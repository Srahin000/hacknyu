"""
Emotion Detection on Snapdragon NPU
Uses Wav2Vec2 emotion recognition model on QNN NPU
"""

import numpy as np
import onnxruntime as ort
import librosa
from pathlib import Path
import time


class EmotionNPU:
    """Emotion detection using Wav2Vec2 on Snapdragon NPU"""
    
    def __init__(self, model_path=None):
        """
        Initialize emotion detection model
        
        Args:
            model_path: Path to ONNX model (default: models/emotion_wav2vec2/model.onnx)
        """
        if model_path is None:
            model_path = Path("models/emotion_wav2vec2/model.onnx")
        else:
            model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Emotion model not found: {model_path}")
        
        # Load emotion labels
        labels_path = model_path.parent / "labels.txt"
        if labels_path.exists():
            with open(labels_path, 'r') as f:
                self.labels = [line.strip() for line in f if line.strip()]
        else:
            # Default labels
            self.labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        
        print(f"  Loading emotion model from: {model_path}")
        
        # Try QNN NPU provider first, fallback to CPU
        self.inference_type = None
        
        try:
            # Try QNN NPU execution provider
            providers = ['QNNExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(
                str(model_path),
                providers=providers
            )
            
            # Check which provider is actually being used
            actual_providers = self.session.get_providers()
            if 'QNNExecutionProvider' in actual_providers:
                self.inference_type = "npu"
                print(f"  ✅ Emotion model loaded on NPU")
            else:
                self.inference_type = "cpu"
                print(f"  ⚠️  QNN NPU not available, using CPU")
                
        except Exception as e:
            print(f"  ⚠️  NPU initialization failed, using CPU: {e}")
            self.session = ort.InferenceSession(
                str(model_path),
                providers=['CPUExecutionProvider']
            )
            self.inference_type = "cpu"
        
        # Get input details
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        
        print(f"  Model input: {self.input_name}, shape: {self.input_shape}")
        print(f"  Emotion labels: {', '.join(self.labels)}")
    
    def preprocess_audio(self, audio, sample_rate, target_length=3.0):
        """
        Preprocess audio for emotion detection
        
        Args:
            audio: Audio array (numpy array, float32)
            sample_rate: Original sample rate
            target_length: Target audio length in seconds (default: 3.0)
        
        Returns:
            Preprocessed audio tensor
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Resample to 16kHz if needed (Wav2Vec2 expects 16kHz)
        if sample_rate != 16000:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000
        
        # Calculate target samples
        target_samples = int(target_length * sample_rate)
        
        # Pad or trim to target length
        if len(audio) < target_samples:
            # Pad with zeros
            padding = target_samples - len(audio)
            audio = np.pad(audio, (0, padding), mode='constant')
        else:
            # Trim to target length
            audio = audio[:target_samples]
        
        # Normalize to [-1, 1]
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
        
        # Add batch dimension: (1, samples)
        audio = audio.reshape(1, -1)
        
        return audio.astype(np.float32)
    
    def detect_emotion(self, audio, sample_rate):
        """
        Detect emotion from audio
        
        Args:
            audio: Audio array (numpy array, float32)
            sample_rate: Sample rate (Hz)
        
        Returns:
            tuple: (emotion_label, confidence, latency_ms, all_scores)
        """
        start_time = time.time()
        
        try:
            # Preprocess audio
            processed_audio = self.preprocess_audio(audio, sample_rate)
            
            # Run inference
            outputs = self.session.run(None, {self.input_name: processed_audio})
            
            # Get predictions (softmax probabilities)
            logits = outputs[0]  # Shape: (1, num_classes)
            
            # Apply softmax if needed
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / exp_logits.sum(axis=-1, keepdims=True)
            
            # Get top prediction
            predicted_idx = np.argmax(probs[0])
            confidence = float(probs[0][predicted_idx])
            emotion = self.labels[predicted_idx]
            
            # Get all scores
            all_scores = {self.labels[i]: float(probs[0][i]) for i in range(len(self.labels))}
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return emotion, confidence, latency_ms, all_scores
            
        except Exception as e:
            print(f"  [ERROR] Emotion detection error: {e}")
            import traceback
            traceback.print_exc()
            return "unknown", 0.0, 0, {}
    
    def __repr__(self):
        return f"EmotionNPU(inference_type={self.inference_type}, labels={len(self.labels)})"


# Fallback CPU version
class EmotionCPU:
    """CPU fallback for emotion detection - simple energy-based heuristic"""
    
    def __init__(self):
        self.inference_type = "cpu-heuristic"
        self.labels = ['angry', 'happy', 'neutral', 'sad']
        print("  ⚠️  Using simple energy-based emotion heuristic (CPU)")
    
    def detect_emotion(self, audio, sample_rate):
        """Simple heuristic based on audio energy and pitch"""
        start_time = time.time()
        
        try:
            # Calculate energy
            energy = np.mean(audio ** 2)
            
            # Simple heuristic
            if energy > 0.1:
                emotion = "angry"
                confidence = 0.6
            elif energy > 0.05:
                emotion = "happy"
                confidence = 0.5
            elif energy > 0.01:
                emotion = "neutral"
                confidence = 0.5
            else:
                emotion = "sad"
                confidence = 0.4
            
            all_scores = {label: 0.25 for label in self.labels}
            all_scores[emotion] = confidence
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return emotion, confidence, latency_ms, all_scores
            
        except Exception as e:
            print(f"  [ERROR] Emotion detection error: {e}")
            return "unknown", 0.0, 0, {}


if __name__ == "__main__":
    """Test emotion detection"""
    import soundfile as sf
    
    print("="*70)
    print(" Testing Emotion Detection ".center(70))
    print("="*70)
    print()
    
    # Initialize model
    try:
        detector = EmotionNPU()
    except Exception as e:
        print(f"NPU initialization failed: {e}")
        print("Using CPU fallback...")
        detector = EmotionCPU()
    
    print()
    print("Detector:", detector)
    print()
    
    # Test with sample audio if available
    audio_files = [
        "audio/user_*.wav",
        "conversations/*/conv_*/user_audio.wav"
    ]
    
    from glob import glob
    
    found_audio = False
    for pattern in audio_files:
        files = glob(pattern)
        if files:
            test_file = files[0]
            print(f"Testing with: {test_file}")
            print()
            
            # Load audio
            audio, sr = sf.read(test_file)
            
            # Detect emotion
            emotion, confidence, latency, scores = detector.detect_emotion(audio, sr)
            
            print(f"Detected Emotion: {emotion.upper()} ({confidence*100:.1f}% confidence)")
            print(f"Latency: {latency}ms on {detector.inference_type}")
            print()
            print("All scores:")
            for label, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {label:10s}: {score*100:5.1f}%")
            
            found_audio = True
            break
    
    if not found_audio:
        print("No audio files found for testing.")
        print("Record some audio first with: python harry_voice_assistant.py --test")
    
    print()
    print("="*70)

