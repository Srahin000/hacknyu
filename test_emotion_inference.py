"""
Test emotion recognition inference

Tests the converted ONNX model with sample audio
"""

import numpy as np
import onnxruntime as ort
from pathlib import Path
import wave
import struct

def create_test_audio(filename="test_audio.wav", duration=3, sample_rate=16000):
    """Create a simple test audio file"""
    
    # Generate a simple sine wave (440 Hz - A note)
    samples = []
    for i in range(int(sample_rate * duration)):
        value = np.sin(2 * np.pi * 440 * i / sample_rate)
        samples.append(int(value * 32767))
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f'{len(samples)}h', *samples))
    
    return filename

def test_emotion_model():
    """Test the emotion recognition ONNX model"""
    
    print("=" * 60)
    print("Testing Emotion Recognition Model")
    print("=" * 60)
    
    # Check if model exists
    model_path = Path("models/emotion_wav2vec2/model.onnx")
    labels_path = Path("models/emotion_wav2vec2/labels.txt")
    
    if not model_path.exists():
        print(f"✗ Model not found: {model_path}")
        print("\nRun first:")
        print("  python convert_emotion_model.py")
        return
    
    # Load emotion labels
    emotions = []
    if labels_path.exists():
        with open(labels_path, 'r') as f:
            emotions = [line.strip() for line in f.readlines()]
    else:
        emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    
    print(f"\n[1/4] Model found: {model_path}")
    print(f"  Emotions: {emotions}")
    
    # Load ONNX model
    print("\n[2/4] Loading ONNX model...")
    try:
        session = ort.InferenceSession(str(model_path))
        print("✓ Model loaded")
        
        # Print model info
        input_info = session.get_inputs()[0]
        output_info = session.get_outputs()[0]
        print(f"  Input: {input_info.name}, shape: {input_info.shape}, dtype: {input_info.type}")
        print(f"  Output: {output_info.name}, shape: {output_info.shape}, dtype: {output_info.type}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    # Create test audio
    print("\n[3/4] Creating test audio...")
    audio_file = create_test_audio()
    print(f"✓ Created: {audio_file}")
    
    # Prepare input
    print("\n[4/4] Running inference...")
    
    # Load audio (simplified - in real use, use librosa)
    sample_rate = 16000
    duration = 3
    audio_data = np.random.randn(1, sample_rate * duration).astype(np.float32)
    
    try:
        # Run inference
        ort_inputs = {session.get_inputs()[0].name: audio_data}
        ort_outputs = session.run(None, ort_inputs)
        
        # Process output
        logits = ort_outputs[0]
        predicted_id = np.argmax(logits, axis=-1)[0]
        predicted_emotion = emotions[predicted_id]
        confidence = np.exp(logits[0]) / np.sum(np.exp(logits[0]))
        
        print("✓ Inference successful!")
        print(f"\nResults:")
        print(f"  Predicted emotion: {predicted_emotion}")
        print(f"  Confidence: {confidence[predicted_id]:.2%}")
        print(f"\nAll probabilities:")
        for i, emotion in enumerate(emotions):
            bar = "█" * int(confidence[i] * 50)
            print(f"  {emotion:12s} {confidence[i]:6.2%} {bar}")
        
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext: Deploy to NPU for faster inference")
    print("  python deploy.py --model models/emotion_wav2vec2")
    print("=" * 60)


if __name__ == "__main__":
    test_emotion_model()

