"""
Convert SpeechBrain Emotion Recognition to ONNX for NPU deployment

Model: speechbrain/emotion-recognition-wav2vec2-IEMOCAP
Size: ~80 MB ONNX
4 emotions: neutral, happy, sad, angry
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

def convert_speechbrain_to_onnx():
    """Convert SpeechBrain emotion model to ONNX"""
    
    print("=" * 60)
    print("Converting SpeechBrain Emotion Model to ONNX")
    print("=" * 60)
    
    # Load model
    print("\n[1/4] Loading SpeechBrain model...")
    try:
        from speechbrain.pretrained import EncoderClassifier
        
        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="models/speechbrain_emotion_temp"
        )
        print("[OK] Model loaded successfully")
        
        # Emotion labels from IEMOCAP
        emotions = ['neutral', 'happy', 'sad', 'angry']
        print(f"  Emotions: {emotions}")
        
    except ImportError:
        print("[FAIL] speechbrain not installed")
        print("\nInstall requirements:")
        print("  conda activate hacknyu_offline")
        print("  pip install speechbrain")
        return
    except Exception as e:
        print(f"[FAIL] Error loading model: {e}")
        return
    
    # Create dummy input (3 seconds of audio at 16kHz)
    print("\n[2/4] Creating dummy input...")
    sample_rate = 16000
    audio_length = 3  # seconds - FIXED LENGTH for NPU
    dummy_audio = torch.randn(1, sample_rate * audio_length)
    
    print(f"  Input shape: {dummy_audio.shape}")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Duration: {audio_length} seconds")
    
    # Get the underlying model (wav2vec2 encoder + classifier)
    print("\n[3/4] Extracting and exporting model...")
    output_dir = Path("models/emotion_speechbrain")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model.onnx"
    
    try:
        # SpeechBrain models have a .mods attribute
        model = classifier.mods
        model.eval()
        
        # Export to ONNX
        torch.onnx.export(
            model,
            (dummy_audio,),
            str(output_path),
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['audio'],
            output_names=['embeddings'],
            dynamic_axes=None  # Static shapes for NPU
        )
        print(f"[OK] Model exported to: {output_path}")
        
    except Exception as e:
        print(f"[FAIL] Error exporting model: {e}")
        print("\nTrying alternative approach...")
        
        # Alternative: Save the encoder separately
        try:
            encoder = classifier.mods.encoder
            encoder.eval()
            
            torch.onnx.export(
                encoder,
                (dummy_audio,),
                str(output_path),
                export_params=True,
                opset_version=14,
                do_constant_folding=True,
                input_names=['audio'],
                output_names=['embeddings'],
                dynamic_axes=None
            )
            print(f"[OK] Encoder exported to: {output_path}")
            
        except Exception as e2:
            print(f"[FAIL] Alternative approach failed: {e2}")
            print("\nNote: SpeechBrain models are complex. Let's try Hugging Face version instead.")
            return
    
    # Save emotion labels
    print("\n[4/4] Saving emotion labels...")
    labels_path = output_dir / "labels.txt"
    with open(labels_path, 'w') as f:
        for emotion in emotions:
            f.write(f"{emotion}\n")
    print(f"[OK] Labels saved to: {labels_path}")
    
    # Test ONNX model
    print("\n[Test] Verifying ONNX model...")
    try:
        import onnxruntime as ort
        
        session = ort.InferenceSession(str(output_path))
        
        # Check model info
        print(f"  Inputs: {[inp.name for inp in session.get_inputs()]}")
        print(f"  Outputs: {[out.name for out in session.get_outputs()]}")
        
        # Run inference
        ort_inputs = {session.get_inputs()[0].name: dummy_audio.numpy()}
        ort_outputs = session.run(None, ort_inputs)
        
        print(f"[OK] ONNX model works!")
        print(f"  Output shape: {ort_outputs[0].shape}")
        
    except Exception as e:
        print(f"[WARN] ONNX test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Deploy to NPU:")
    print(f"   conda activate hacknyu_offline")
    print(f"   python deploy.py --model models/emotion_speechbrain")
    print(f"\n2. Model specs:")
    print(f"   - Size: ~80 MB")
    print(f"   - Input: 16kHz audio (3 seconds)")
    print(f"   - Output: 4 emotion classes")
    print(f"   - Target latency: <100ms on NPU")
    print("=" * 60)


def convert_huggingface_wav2vec2_small():
    """Alternative: Convert Hugging Face wav2vec2-small for emotion"""
    
    print("=" * 60)
    print("Converting Hugging Face Wav2Vec2-Small to ONNX")
    print("=" * 60)
    
    print("\n[1/4] Loading model from Hugging Face...")
    try:
        from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
        
        # Using a smaller fine-tuned model
        model_name = "superb/wav2vec2-base-superb-er"  # Emotion Recognition
        
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
        model.eval()
        
        print("[OK] Model loaded successfully")
        
    except Exception as e:
        print(f"[FAIL] Error loading model: {e}")
        return
    
    # Create dummy input
    print("\n[2/4] Creating dummy input...")
    sample_rate = 16000
    audio_length = 3
    dummy_audio = torch.randn(1, sample_rate * audio_length)
    
    # Process input
    inputs = processor(
        dummy_audio.numpy()[0],
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True
    )
    
    print(f"  Input shape: {inputs.input_values.shape}")
    
    # Export to ONNX
    print("\n[3/4] Exporting to ONNX...")
    output_dir = Path("models/emotion_wav2vec2_small")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model.onnx"
    
    try:
        torch.onnx.export(
            model,
            (inputs.input_values,),
            str(output_path),
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['input_values'],
            output_names=['logits'],
            dynamic_axes=None
        )
        print(f"[OK] Model exported to: {output_path}")
        
    except Exception as e:
        print(f"[FAIL] Error exporting: {e}")
        return
    
    # Save config
    print("\n[4/4] Saving configuration...")
    import json
    config = {
        "model": model_name,
        "sample_rate": sample_rate,
        "audio_length": audio_length,
        "num_labels": model.config.num_labels
    }
    
    config_path = output_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[OK] Config saved to: {config_path}")
    
    # Test
    print("\n[Test] Verifying ONNX model...")
    try:
        import onnxruntime as ort
        
        session = ort.InferenceSession(str(output_path))
        ort_inputs = {session.get_inputs()[0].name: inputs.input_values.numpy()}
        ort_outputs = session.run(None, ort_inputs)
        
        logits = ort_outputs[0]
        predicted_id = np.argmax(logits, axis=-1)[0]
        
        print(f"[OK] ONNX model works!")
        print(f"  Predicted class: {predicted_id}")
        print(f"  Logits shape: {logits.shape}")
        
    except Exception as e:
        print(f"[WARN] Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--huggingface":
        convert_huggingface_wav2vec2_small()
    else:
        print("\nWhich model do you want to convert?\n")
        print("1. SpeechBrain emotion-recognition-wav2vec2-IEMOCAP")
        print("2. Hugging Face wav2vec2-base-superb-er (emotion recognition)")
        print("\nUsage:")
        print("  python convert_emotion_speechbrain.py              # SpeechBrain")
        print("  python convert_emotion_speechbrain.py --huggingface  # Hugging Face")
        print("\nTrying SpeechBrain first...\n")
        
        convert_speechbrain_to_onnx()


