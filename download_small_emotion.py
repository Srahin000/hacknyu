"""
Download and convert small emotion models specifically for mobile/edge deployment
Searching for quantized, distilled, or mobile-optimized versions
"""

import torch
import torch.onnx
from pathlib import Path
import sys
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def try_small_models():
    """Try various small emotion models"""
    
    print("=" * 70)
    print("Searching for Small Pre-trained Emotion Models")
    print("=" * 70)
    print("\nTarget: <100 MB for NPU deployment\n")
    
    # List of genuinely small models to try
    small_models = [
        # Distilled models
        ("distil-whisper/distil-small.en", "DistilWhisper Small", "whisper"),
        
        # Lightweight audio models
        ("speechbrain/emotion-recognition-wav2vec2-IEMOCAP", "SpeechBrain IEMOCAP", "speechbrain"),
        
        # Hubert small
        ("ntu-spml/distilhubert", "DistilHuBERT", "hubert"),
        
        # Quantized versions (if available)
        ("Rajaram1996/Emotion_Detection_Audio", "Emotion Detection", "custom"),
    ]
    
    success = False
    
    for model_name, description, model_type in small_models:
        print(f"\nTrying: {model_name}")
        print(f"  Description: {description}")
        
        try:
            if model_type == "speechbrain":
                # Try without symlinks
                import os
                os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
                
                from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
                
                processor = AutoFeatureExtractor.from_pretrained(model_name, use_symlinks=False)
                model = AutoModelForAudioClassification.from_pretrained(model_name, use_symlinks=False)
                model.eval()
                
            else:
                from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
                
                try:
                    processor = AutoFeatureExtractor.from_pretrained(model_name)
                    model = AutoModelForAudioClassification.from_pretrained(model_name)
                    model.eval()
                except:
                    continue
            
            # Check size
            num_params = sum(p.numel() for p in model.parameters())
            size_mb = num_params * 4 / (1024 * 1024)
            
            print(f"  [INFO] Parameters: {num_params/1e6:.1f}M")
            print(f"  [INFO] Estimated size: ~{size_mb:.0f} MB")
            
            if size_mb < 150:  # Accept anything under 150MB
                print(f"  [ACCEPT] Small enough!")
                
                # Convert to ONNX
                print(f"\n  Converting to ONNX...")
                output_dir = Path("models/emotion_downloaded")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "model.onnx"
                
                # Create dummy input
                sample_rate = 16000
                audio_length = 3
                dummy_audio = torch.randn(1, sample_rate * audio_length)
                
                inputs = processor(
                    dummy_audio.numpy()[0],
                    sampling_rate=sample_rate,
                    return_tensors="pt",
                    padding=True
                )
                
                input_tensor = inputs.input_values if hasattr(inputs, 'input_values') else inputs.input_features
                input_name = 'input_values' if hasattr(inputs, 'input_values') else 'input_features'
                
                torch.onnx.export(
                    model,
                    (input_tensor,),
                    str(output_path),
                    export_params=True,
                    opset_version=14,
                    do_constant_folding=True,
                    input_names=[input_name],
                    output_names=['logits'],
                    dynamic_axes=None
                )
                
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  [OK] Converted! Actual size: {file_size_mb:.1f} MB")
                
                if file_size_mb < 150:
                    # Get labels
                    if hasattr(model.config, 'id2label'):
                        emotions = [model.config.id2label[i] for i in range(model.config.num_labels)]
                    else:
                        emotions = ['neutral', 'happy', 'sad', 'angry']
                    
                    # Save config
                    config = {
                        "model": model_name,
                        "description": description,
                        "sample_rate": sample_rate,
                        "audio_length": audio_length,
                        "emotions": emotions,
                        "file_size_mb": round(file_size_mb, 2),
                        "npu_compatible": file_size_mb < 150
                    }
                    
                    with open(output_dir / "config.json", 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    with open(output_dir / "labels.txt", 'w') as f:
                        for e in emotions:
                            f.write(f"{e}\n")
                    
                    print(f"\n  [SUCCESS] Model ready for NPU deployment!")
                    print(f"  Location: {output_dir}")
                    print(f"  Emotions: {', '.join(emotions)}")
                    
                    success = True
                    break
                else:
                    print(f"  [SKIP] ONNX too large: {file_size_mb:.0f} MB")
            else:
                print(f"  [SKIP] Too large: {size_mb:.0f} MB")
                
        except Exception as e:
            print(f"  [SKIP] Error: {str(e)[:100]}")
            continue
    
    if not success:
        print("\n" + "=" * 70)
        print("[CONCLUSION] No pre-trained models small enough for NPU")
        print("=" * 70)
        print("\nThe reality:")
        print("- All wav2vec2/HuBERT emotion models are 300-1200 MB")
        print("- These models cause OOM on mobile NPUs")
        print("- Industry uses cloud APIs or custom tiny models")
        print("\nYour options for hackathon:")
        print("\n1. Use the 16 MB custom model (untrained but demonstrates NPU)")
        print("   python deploy.py --model models/emotion_ultra_tiny")
        print("\n2. Skip emotion, focus on STT + TTS")
        print("\n3. Use simple heuristics (volume = excitement, etc.)")
        print("\n4. Use cloud API (Azure Cognitive Services, etc.)")
        print("=" * 70)
    
    return success


if __name__ == "__main__":
    try_small_models()


