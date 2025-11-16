"""
Convert TINY Emotion Recognition Model to ONNX (~20-50 MB)

For NPU deployment - must be small to avoid OOM errors!
Using DistilHuBERT or similar lightweight models
"""

import torch
import torch.onnx
import numpy as np
from pathlib import Path
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def convert_tiny_emotion_model():
    """Convert tiny emotion model to ONNX"""
    
    print("=" * 70)
    print("Converting TINY Emotion Model to ONNX for NPU")
    print("=" * 70)
    print("\n[CRITICAL] NPU has limited memory!")
    print("Previous 1.2GB model FAILED with OOM error")
    print("Target: <100 MB for NPU deployment")
    print()
    
    # Try tiny models only
    tiny_models = [
        ("MIT/ast-finetuned-speech-commands-v2", "Audio Spectrogram Transformer"),
        ("facebook/wav2vec2-base", "Wav2Vec2 Base (smaller)"),
        ("anton-l/wav2vec2-base-speech-emotion-recognition-feat", "Wav2Vec2 Base Emotion"),
    ]
    
    print("[1/5] Trying TINY models...")
    
    model = None
    processor = None
    model_name = None
    model_desc = None
    
    for name, desc in tiny_models:
        try:
            print(f"\n  Trying: {name}")
            from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
            
            processor = AutoFeatureExtractor.from_pretrained(name)
            model = AutoModelForAudioClassification.from_pretrained(name)
            model.eval()
            
            # Check model size
            num_params = sum(p.numel() for p in model.parameters())
            size_mb = num_params * 4 / (1024 * 1024)  # Rough estimate in MB
            
            print(f"  [OK] Loaded: {desc}")
            print(f"  Parameters: {num_params/1e6:.1f}M")
            print(f"  Estimated size: ~{size_mb:.0f} MB")
            
            if size_mb < 300:  # Only accept models < 300MB
                model_name = name
                model_desc = desc
                print(f"  [ACCEPT] Model is small enough for NPU!")
                break
            else:
                print(f"  [SKIP] Still too large (>{size_mb:.0f} MB)")
                model = None
                continue
                
        except Exception as e:
            print(f"  [SKIP] Failed: {str(e)[:80]}")
            continue
    
    if model is None:
        print("\n[FAIL] No tiny models available")
        print("\n=== ALTERNATIVE SOLUTION ===")
        print("For your hackathon, consider:")
        print("1. Skip emotion detection entirely (focus on STT + TTS)")
        print("2. Use cloud-based emotion API (OpenAI Whisper has emotion)")
        print("3. Use simple audio features (volume, pitch) instead of ML")
        print("\nThe 1.2GB wav2vec2 models are TOO LARGE for mobile NPU!")
        print("=" * 70)
        return
    
    # Create dummy input
    print("\n[2/5] Creating dummy input...")
    sample_rate = 16000
    audio_length = 3  # seconds
    dummy_audio = torch.randn(1, sample_rate * audio_length)
    
    # Process input
    inputs = processor(
        dummy_audio.numpy()[0],
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True
    )
    
    # Get the actual input tensor
    if hasattr(inputs, 'input_values'):
        input_tensor = inputs.input_values
        input_name = 'input_values'
    elif hasattr(inputs, 'input_features'):
        input_tensor = inputs.input_features
        input_name = 'input_features'
    else:
        input_tensor = list(inputs.values())[0]
        input_name = list(inputs.keys())[0]
    
    print(f"  Input shape: {input_tensor.shape}")
    print(f"  Input name: {input_name}")
    
    # Export to ONNX
    print("\n[3/5] Exporting to ONNX...")
    output_dir = Path("models/emotion_tiny")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model.onnx"
    
    try:
        torch.onnx.export(
            model,
            (input_tensor,),
            str(output_path),
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=[input_name],
            output_names=['logits'],
            dynamic_axes=None  # Static shapes for NPU
        )
        print(f"[OK] Model exported to: {output_path}")
        
    except Exception as e:
        print(f"[FAIL] Error exporting: {e}")
        return
    
    # Check actual file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Actual file size: {file_size_mb:.1f} MB")
    
    if file_size_mb > 300:
        print(f"  [ERROR] Model STILL too large! {file_size_mb:.0f} MB > 300 MB")
        print(f"  This will likely FAIL on NPU with OOM error!")
        print(f"\n  Recommendation: Skip emotion detection for hackathon")
        return
    elif file_size_mb > 100:
        print(f"  [WARN] Model is large ({file_size_mb:.0f} MB). May work but risky.")
    else:
        print(f"  [OK] Model size is good for NPU!")
    
    # Save config
    print("\n[4/5] Saving configuration...")
    
    # Get emotion labels
    if hasattr(model.config, 'id2label'):
        emotions = [model.config.id2label[i] for i in range(model.config.num_labels)]
    else:
        emotions = [f"emotion_{i}" for i in range(model.config.num_labels)]
    
    labels_path = output_dir / "labels.txt"
    with open(labels_path, 'w') as f:
        for emotion in emotions:
            f.write(f"{emotion}\n")
    print(f"[OK] Labels saved: {emotions}")
    
    import json
    config = {
        "model": model_name,
        "description": model_desc,
        "sample_rate": sample_rate,
        "audio_length": audio_length,
        "num_labels": len(emotions),
        "emotions": emotions,
        "file_size_mb": round(file_size_mb, 2),
        "npu_compatible": file_size_mb < 300
    }
    
    config_path = output_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"[OK] Config saved")
    
    # Test ONNX model
    print("\n[5/5] Testing ONNX model...")
    try:
        import onnxruntime as ort
        
        session = ort.InferenceSession(str(output_path))
        ort_inputs = {session.get_inputs()[0].name: input_tensor.numpy()}
        ort_outputs = session.run(None, ort_inputs)
        
        logits = ort_outputs[0]
        predicted_id = np.argmax(logits, axis=-1)[0]
        predicted_emotion = emotions[predicted_id] if predicted_id < len(emotions) else f"id_{predicted_id}"
        
        print(f"[OK] ONNX model works!")
        print(f"  Test prediction: {predicted_emotion}")
        print(f"  Logits shape: {logits.shape}")
        
    except Exception as e:
        print(f"[WARN] ONNX test failed: {e}")
    
    # Final verdict
    print("\n" + "=" * 70)
    print("Model Analysis for NPU Deployment")
    print("=" * 70)
    print(f"Previous deployment:   1200 MB - FAILED (OOM)")
    print(f"This model:            {file_size_mb:4.0f} MB - {'OK' if file_size_mb < 100 else 'RISKY' if file_size_mb < 300 else 'WILL FAIL'}")
    print(f"Memory saved:          {1200 - file_size_mb:.0f} MB ({(1 - file_size_mb/1200)*100:.0f}% reduction)")
    print()
    
    if file_size_mb < 100:
        print("[SUCCESS] This model should work on NPU!")
        print("\nNext steps:")
        print("  conda activate hacknyu_offline")
        print("  python deploy.py --model models/emotion_tiny")
    elif file_size_mb < 300:
        print("[WARNING] This model MIGHT work, but could still hit OOM")
        print("\nYou can try deploying, but be prepared for failure.")
        print("  conda activate hacknyu_offline")
        print("  python deploy.py --model models/emotion_tiny")
    else:
        print("[FAIL] This model will likely FAIL with OOM on NPU")
        print("\nRecommendation: Skip emotion detection for hackathon")
    
    print("=" * 70)


def create_simple_emotion_classifier():
    """Create a VERY simple emotion classifier from scratch (<10 MB)"""
    
    print("=" * 70)
    print("Creating Ultra-Tiny Custom Emotion Classifier")
    print("=" * 70)
    print("\nThis will be a simple CNN model (<10 MB)")
    print("Good enough for demo purposes!\n")
    
    import torch.nn as nn
    
    class TinyEmotionCNN(nn.Module):
        def __init__(self, num_emotions=4):
            super().__init__()
            # Simple CNN for mel spectrogram input
            self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
            self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
            self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
            self.pool = nn.MaxPool2d(2, 2)
            self.fc1 = nn.Linear(128 * 10 * 25, 128)  # Adjusted for 80x200 mel spec
            self.fc2 = nn.Linear(128, num_emotions)
            self.relu = nn.ReLU()
            
        def forward(self, x):
            # x: (batch, 1, 80, 200) - mel spectrogram
            x = self.pool(self.relu(self.conv1(x)))  # -> (batch, 32, 40, 100)
            x = self.pool(self.relu(self.conv2(x)))  # -> (batch, 64, 20, 50)
            x = self.pool(self.relu(self.conv3(x)))  # -> (batch, 128, 10, 25)
            x = x.view(x.size(0), -1)  # Flatten
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    print("[1/4] Creating tiny CNN model...")
    model = TinyEmotionCNN(num_emotions=4)
    model.eval()
    
    num_params = sum(p.numel() for p in model.parameters())
    size_mb = num_params * 4 / (1024 * 1024)
    print(f"[OK] Model created")
    print(f"  Parameters: {num_params/1e6:.2f}M")
    print(f"  Estimated size: ~{size_mb:.1f} MB")
    
    print("\n[2/4] Exporting to ONNX...")
    output_dir = Path("models/emotion_ultra_tiny")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model.onnx"
    
    # Dummy input: mel spectrogram (80 mel bins, 200 time frames ~ 3 sec)
    dummy_input = torch.randn(1, 1, 80, 200)
    
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['mel_spectrogram'],
        output_names=['logits'],
        dynamic_axes=None
    )
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Model exported: {file_size_mb:.1f} MB")
    
    print("\n[3/4] Saving configuration...")
    emotions = ['neutral', 'happy', 'sad', 'angry']
    
    labels_path = output_dir / "labels.txt"
    with open(labels_path, 'w') as f:
        for emotion in emotions:
            f.write(f"{emotion}\n")
    
    import json
    config = {
        "model": "custom_tiny_cnn",
        "description": "Ultra-lightweight CNN for emotion recognition",
        "input_type": "mel_spectrogram",
        "input_shape": [1, 1, 80, 200],
        "sample_rate": 16000,
        "num_labels": 4,
        "emotions": emotions,
        "file_size_mb": round(file_size_mb, 2),
        "note": "Untrained model - for demo/structure only. Needs training!"
    }
    
    config_path = output_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[OK] Config saved")
    
    print("\n[4/4] Testing...")
    import onnxruntime as ort
    session = ort.InferenceSession(str(output_path))
    ort_outputs = session.run(None, {'mel_spectrogram': dummy_input.numpy()})
    print(f"[OK] Model works! Output shape: {ort_outputs[0].shape}")
    
    print("\n" + "=" * 70)
    print(f"[SUCCESS] Ultra-tiny model created: {file_size_mb:.1f} MB")
    print("=" * 70)
    print("\nNOTE: This is an UNTRAINED model (random weights)")
    print("It will give random predictions, but demonstrates the structure.")
    print("\nFor hackathon demo:")
    print("1. Deploy this tiny model to NPU (won't OOM!)")
    print("2. Show the fast inference time")
    print("3. Mention it would be trained on real emotion data")
    print("\nDeploy with:")
    print("  conda activate hacknyu_offline")
    print("  python deploy.py --model models/emotion_ultra_tiny")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    print("\nEmotion Model Converter for NPU")
    print("Previous deployment FAILED with OOM error (1.2GB model too large)\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--custom":
        print("Creating custom ultra-tiny model...\n")
        create_simple_emotion_classifier()
    else:
        print("Searching for small pre-trained models...\n")
        convert_tiny_emotion_model()
        
        print("\n\nAlternative: Create custom tiny model (untrained but <10 MB)")
        print("Run: python convert_emotion_tiny.py --custom")


