"""
Test XTTS Voice Cloning with Harry Potter Sample

This script tests voice cloning using XTTS v2 with your Harry Potter sample.
If it works well, we can integrate it into the main voice assistant!
"""

import torch
from TTS.api import TTS
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# --- Configuration ---
SOUND_SAMPLE_DIR = Path("sound_sample")
OUTPUT_FILE = "output_cloned_voice.wav"

# Test phrases
TEST_PHRASES = [
    "I solemnly swear that I am up to no good.",
    "Hello! I'm Harry Potter. How can I help you today?",
    "That's brilliant! Tell me more about that.",
    "Expecto Patronum!",
    "Don't worry, we'll figure this out together."
]

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"


def find_sample_file():
    """Find the Harry Potter sample in sound_sample folder"""
    
    if not SOUND_SAMPLE_DIR.exists():
        print(f"[ERROR] sound_sample directory not found!")
        return None
    
    # Look for audio files
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(SOUND_SAMPLE_DIR.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"[ERROR] No audio files found in sound_sample/")
        print(f"   Supported formats: {', '.join(audio_extensions)}")
        return None
    
    # Use first audio file found
    sample_file = audio_files[0]
    print(f"[OK] Found sample: {sample_file.name}")
    return sample_file


def main():
    print("="*70)
    print(" XTTS Voice Cloning Test ".center(70))
    print("="*70)
    print()
    
    # Import torch at the top
    import torch
    
    # 1. Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Device] Running on: {device}")
    
    if device == "cuda":
        print(f"[GPU] {torch.cuda.get_device_name(0)}")
        print(f"[VRAM] {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print(f"[Note] No GPU detected, using CPU (slower but works!)")
    
    print()
    
    # 2. Find sample file
    print("[1/3] Looking for Harry Potter sample...")
    sample_path = find_sample_file()
    
    if not sample_path:
        print()
        print("="*70)
        print("Please add a Harry Potter voice sample to the sound_sample/ folder")
        print("Supported formats: .wav, .mp3, .flac, .ogg")
        print("Ideal: 6-10 seconds, clear voice, no background noise")
        print("="*70)
        return
    
    # Check file size
    file_size_mb = sample_path.stat().st_size / (1024 * 1024)
    print(f"   File size: {file_size_mb:.2f} MB")
    
    # Try to get duration
    try:
        import soundfile as sf
        audio, sr = sf.read(str(sample_path))
        duration = len(audio) / sr
        print(f"   Duration: {duration:.1f} seconds")
        
        if duration < 3:
            print(f"   [WARNING] Sample is short (<3s). Longer samples work better!")
        elif duration > 15:
            print(f"   [WARNING] Sample is long (>15s). Shorter samples are faster!")
        else:
            print(f"   [OK] Good duration for voice cloning!")
    except Exception as e:
        print(f"   [WARNING] Could not read audio: {e}")
    
    print()
    
    # 3. Load XTTS model
    print("[2/3] Loading XTTS model...")
    print("   This downloads ~1.8GB on first run (takes a few minutes)")
    print("   After first time, it's cached and loads quickly!")
    print()
    
    try:
        # Fix PyTorch 2.9 weights_only issue
        import torch
        if hasattr(torch, 'serialization'):
            # Allow TTS config classes to be loaded
            try:
                from TTS.tts.configs.xtts_config import XttsConfig
                torch.serialization.add_safe_globals([XttsConfig])
            except:
                pass
        
        tts = TTS(MODEL_NAME).to(device)
        print("   [OK] Model loaded successfully!")
    except Exception as e:
        print(f"   [ERROR] Failed to load model: {e}")
        print()
        print("Trying workaround...")
        # Try with weights_only=False workaround
        try:
            # Monkey-patch torch.load temporarily
            original_torch_load = torch.load
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_torch_load(*args, **kwargs)
            torch.load = patched_load
            
            tts = TTS(MODEL_NAME).to(device)
            torch.load = original_torch_load  # Restore
            print("   [OK] Model loaded with workaround!")
        except Exception as e2:
            torch.load = original_torch_load  # Restore even on failure
            print(f"   [ERROR] Workaround failed: {e2}")
            print()
            print("Try:")
            print("   pip install torch==2.1.0  # Or another compatible version")
            return
    
    print()
    
    # 4. Run inference on test phrases
    print("[3/3] Generating test audio clips...")
    print(f"   Testing {len(TEST_PHRASES)} phrases")
    print()
    
    output_dir = Path("xtts_test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    successful = 0
    failed = 0
    
    for i, text in enumerate(TEST_PHRASES, 1):
        print(f"   [{i}/{len(TEST_PHRASES)}] \"{text[:50]}...\"")
        
        output_file = output_dir / f"test_{i:02d}.wav"
        
        try:
            import time
            start = time.time()
            
            tts.tts_to_file(
                text=text,
                speaker_wav=str(sample_path),
                language="en",
                file_path=str(output_file)
            )
            
            latency = int((time.time() - start) * 1000)
            print(f"        [OK] Saved to: {output_file.name} ({latency}ms)")
            successful += 1
            
        except Exception as e:
            print(f"        [ERROR] Failed: {e}")
            failed += 1
        
        print()
    
    # Summary
    print()
    print("="*70)
    print(" Test Complete! ".center(70))
    print("="*70)
    print()
    print(f"Results:")
    print(f"   Successful: {successful}/{len(TEST_PHRASES)}")
    print(f"   Failed: {failed}/{len(TEST_PHRASES)}")
    print()
    
    if successful > 0:
        print(f"[OK] Output files saved to: {output_dir}/")
        print()
        print("Listen to the test files and check quality!")
        print()
        print("Next steps:")
        print("  1. Listen to test_01.wav, test_02.wav, etc.")
        print("  2. If quality is good, we can integrate into voice assistant!")
        print("  3. If quality is bad, try a different sample (clearer, 6-10s)")
        print()
        print("To integrate into Harry:")
        print("  python integrate_xtts_cloning.py")
    else:
        print("[ERROR] All generations failed. Check errors above.")
    
    print("="*70)


if __name__ == "__main__":
    main()

