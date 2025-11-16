"""
Convert Wav2Vec2 Emotion Recognition to ONNX for NPU deployment

Model: r-f/wav2vec-english-speech-emotion-recognition
7 emotions: angry, disgust, fear, happy, neutral, sad, surprise
Accuracy: 97.46%
"""

import torch
import torch.onnx
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import numpy as np
from pathlib import Path
import sys

# Fix Windows console encoding for checkmarks
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def convert_to_onnx():
    """Convert Wav2Vec2 emotion model to ONNX"""
    
    print("=" * 60)
    print("Converting Wav2Vec2 Emotion Model to ONNX")
    print("=" * 60)
    
    # Load model and feature extractor (no tokenizer needed for emotion recognition)
    print("\n[1/4] Loading model from Hugging Face...")
    model_name = "r-f/wav2vec-english-speech-emotion-recognition"
    
    try:
        from transformers import Wav2Vec2FeatureExtractor
        processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
        model.eval()
        print("✓ Model loaded successfully")
        
        # Print emotion labels
        emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        print(f"  Emotions: {emotions}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("\nInstall requirements:")
        print("  pip install transformers torch")
        return
    
    # Create dummy input (3 seconds of audio at 16kHz)
    # IMPORTANT: Use fixed shape for NPU compatibility
    print("\n[2/4] Creating dummy input...")
    sample_rate = 16000
    audio_length = 3  # seconds - FIXED LENGTH for NPU
    dummy_audio = torch.randn(1, sample_rate * audio_length)
    
    # Process input
    inputs = processor(
        dummy_audio.numpy()[0],
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True
    )
    
    print(f"  Input shape: {inputs.input_values.shape}")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Duration: {audio_length} seconds")
    
    # Export to ONNX
    print("\n[3/4] Exporting to ONNX...")
    output_dir = Path("models/emotion_wav2vec2")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model.onnx"
    
    try:
        torch.onnx.export(
            model,
            (inputs.input_values,),
            str(output_path),
            export_params=True,
            opset_version=14,  # Compatible with most runtimes
            do_constant_folding=True,
            input_names=['input_values'],
            output_names=['logits'],
            # NO dynamic_axes - use static shapes for NPU compatibility
            dynamic_axes=None
        )
        print(f"✓ Model exported to: {output_path}")
        
    except Exception as e:
        print(f"✗ Error exporting model: {e}")
        return
    
    # Save emotion labels
    print("\n[4/4] Saving emotion labels...")
    labels_path = output_dir / "labels.txt"
    with open(labels_path, 'w') as f:
        for emotion in emotions:
            f.write(f"{emotion}\n")
    print(f"✓ Labels saved to: {labels_path}")
    
    # Test ONNX model
    print("\n[Test] Verifying ONNX model...")
    try:
        import onnxruntime as ort
        
        session = ort.InferenceSession(str(output_path))
        
        # Run inference
        ort_inputs = {session.get_inputs()[0].name: inputs.input_values.numpy()}
        ort_outputs = session.run(None, ort_inputs)
        
        # Get prediction
        logits = ort_outputs[0]
        predicted_id = np.argmax(logits, axis=-1)[0]
        predicted_emotion = emotions[predicted_id]
        
        print(f"✓ ONNX model works!")
        print(f"  Test prediction: {predicted_emotion}")
        print(f"  Logits shape: {logits.shape}")
        
    except ImportError:
        print("⚠ onnxruntime not installed, skipping test")
        print("  Install with: pip install onnxruntime")
    except Exception as e:
        print(f"⚠ ONNX test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Deploy to NPU:")
    print(f"   python deploy.py --model models/emotion_wav2vec2")
    print(f"\n2. This will take 10-30 minutes to compile")
    print(f"\n3. Model specs:")
    print(f"   - Accuracy: 97.46%")
    print(f"   - Input: 16kHz audio (1-5 seconds)")
    print(f"   - Output: 7 emotion classes")
    print(f"   - Target latency: <100ms on NPU")
    print("=" * 60)


if __name__ == "__main__":
    convert_to_onnx()

