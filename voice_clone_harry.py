"""
Voice Cloning from Harry Potter Sample
Uses Coqui TTS XTTS v2 to clone your voice sample into a TTS system
"""

import torch
from TTS.api import TTS
import os
import sys
from pathlib import Path
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuration
SAMPLE_PATH = Path("sound_sample/harry_sample.wav")
OUTPUT_DIR = Path("cloned_voice_outputs")
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

# Test phrases
TEST_PHRASES = [
    "I solemnly swear that I am up to no good.",
    "Hello! I'm Harry Potter. How can I help you today?",
    "That's brilliant! Tell me more about that.",
    "Expecto Patronum!",
    "Don't worry, we'll figure this out together.",
    "Bloody brilliant!",
    "The wand chooses the wizard, you know.",
]

def check_sample():
    """Check if voice sample exists and is valid"""
    print("Checking voice sample...")
    
    if not SAMPLE_PATH.exists():
        print(f"[ERROR] Voice sample not found: {SAMPLE_PATH}")
        print()
        print("Please add your voice sample to:")
        print(f"  {SAMPLE_PATH}")
        print()
        print("Supported formats: .wav, .mp3, .flac")
        print("Ideal: 6-10 seconds, clear voice, minimal background noise")
        return False
    
    # Check file size
    file_size_mb = SAMPLE_PATH.stat().st_size / (1024 * 1024)
    print(f"  [OK] Sample found: {SAMPLE_PATH.name} ({file_size_mb:.2f} MB)")
    
    # Try to get duration
    try:
        import soundfile as sf
        audio, sr = sf.read(str(SAMPLE_PATH))
        duration = len(audio) / sr
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Sample rate: {sr} Hz")
        
        if duration < 3:
            print(f"  [WARNING] Sample is short (<3s). Longer samples work better!")
        elif duration > 15:
            print(f"  [WARNING] Sample is long (>15s). Shorter samples are faster!")
        else:
            print(f"  [OK] Good duration for voice cloning!")
    except Exception as e:
        print(f"  [WARNING] Could not read audio: {e}")
        print(f"  Will try anyway...")
    
    print()
    return True


def fix_pytorch_loading():
    """Fix PyTorch 2.9 weights_only issue"""
    original_torch_load = torch.load
    
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_torch_load(*args, **kwargs)
    
    torch.load = patched_load


def load_xtts_model():
    """Load XTTS v2 model for voice cloning"""
    print("Loading XTTS v2 model...")
    print("  This downloads ~1.8GB on first run (takes a few minutes)")
    print("  After first time, it's cached and loads quickly!")
    print()
    
    # Fix PyTorch loading issue
    fix_pytorch_loading()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")
    
    try:
        start = time.time()
        tts = TTS(MODEL_NAME).to(device)
        load_time = int((time.time() - start) * 1000)
        print(f"  [OK] Model loaded in {load_time}ms")
        print()
        return tts
    except Exception as e:
        print(f"  [ERROR] Failed to load model: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check internet connection (first download)")
        print("  2. Ensure enough disk space (~2GB)")
        print("  3. Try: pip install --upgrade TTS")
        return None


def clone_voice(tts, text, output_file):
    """Generate speech using cloned voice"""
    try:
        start = time.time()
        
        # Try to work around torchcodec by using soundfile to load audio first
        # and passing it as numpy array if possible
        try:
            import soundfile as sf
            import numpy as np
            
            # Load audio with soundfile (bypasses torchcodec)
            audio_data, sample_rate = sf.read(str(SAMPLE_PATH))
            
            # XTTS expects speaker_wav as file path, but let's try passing the data
            # Actually, XTTS API requires file path, so we'll just use the path
            # The issue is in XTTS's internal audio loading
            tts.tts_to_file(
                text=text,
                speaker_wav=str(SAMPLE_PATH),
                language="en",
                file_path=str(output_file)
            )
        except Exception as inner_e:
            # If that fails, try the original way
            if "torchcodec" in str(inner_e).lower() or "libtorchcodec" in str(inner_e).lower():
                # torchcodec issue - try to use a workaround
                # Convert WAV to a format that doesn't need torchcodec
                import tempfile
                import subprocess
                
                # Use ffmpeg to convert to a simpler format if needed
                # Actually, let's just try the direct call and see what happens
                raise inner_e
            else:
                raise inner_e
        
        latency = int((time.time() - start) * 1000)
        return True, latency
    except Exception as e:
        error_msg = str(e)
        if "torchcodec" in error_msg.lower() or "libtorchcodec" in error_msg.lower():
            return False, "torchcodec DLL issue - PyTorch 2.9.1 may be incompatible. Try: pip install torchcodec --upgrade or use PyTorch 2.0-2.1"
        return False, error_msg


def main():
    print("="*70)
    print(" Voice Cloning from Harry Potter Sample ".center(70))
    print("="*70)
    print()
    
    # Check sample
    if not check_sample():
        return
    
    # Load model
    tts = load_xtts_model()
    if not tts:
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("="*70)
    print(" Generating Cloned Voice Samples ".center(70))
    print("="*70)
    print()
    
    successful = 0
    failed = 0
    total_latency = 0
    
    for i, text in enumerate(TEST_PHRASES, 1):
        output_file = OUTPUT_DIR / f"cloned_{i:02d}.wav"
        
        print(f"[{i}/{len(TEST_PHRASES)}] \"{text[:50]}\"")
        
        success, result = clone_voice(tts, text, output_file)
        
        if success:
            latency = result
            total_latency += latency
            print(f"   [OK] Saved to {output_file.name} ({latency}ms)")
            successful += 1
        else:
            print(f"   [ERROR] {result}")
            failed += 1
        
        print()
    
    # Summary
    print("="*70)
    print(" Results ".center(70))
    print("="*70)
    print()
    print(f"Successful: {successful}/{len(TEST_PHRASES)}")
    print(f"Failed: {failed}/{len(TEST_PHRASES)}")
    
    if successful > 0:
        avg_latency = total_latency // successful
        print(f"Average latency: {avg_latency}ms per phrase")
        print()
        print(f"[OK] Cloned voice samples saved to: {OUTPUT_DIR}/")
        print()
        print("Listen to the files and check quality!")
        print()
        print("Quality tips:")
        print("  - If quality is good: Ready to integrate!")
        print("  - If quality is bad: Try a clearer sample (6-10s, no background noise)")
        print("  - If voice doesn't match: Sample might be too short or unclear")
        print()
        print("Next step: Integrate into harry_voice_assistant.py")
    else:
        print("[ERROR] All generations failed. Check errors above.")
    
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVoice cloning cancelled.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

