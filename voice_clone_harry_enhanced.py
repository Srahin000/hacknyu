"""
Enhanced Voice Cloning with Controllable Parameters
Uses your voice sample but allows you to control speed, emotion, and other parameters
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

# Test phrases with different styles
TEST_PHRASES = [
    {
        "text": "I solemnly swear that I am up to no good.",
        "speed": 1.0,  # Normal speed
        "emotion": None  # Use default from sample
    },
    {
        "text": "That's brilliant! Tell me more about that.",
        "speed": 1.2,  # Faster (excited)
        "emotion": None
    },
    {
        "text": "Don't worry, we'll figure this out together.",
        "speed": 0.9,  # Slower (calm, reassuring)
        "emotion": None
    },
]


def clone_voice_enhanced(tts, text, output_file, speed=1.0, emotion=None):
    """
    Generate speech using cloned voice with controllable parameters
    
    Args:
        tts: TTS model instance
        text: Text to speak
        output_file: Output file path
        speed: Speech speed multiplier (0.5-2.0, default 1.0)
        emotion: Emotion style (optional, uses sample's emotion if None)
    """
    try:
        start = time.time()
        
        # Build parameters
        params = {
            "text": text,
            "speaker_wav": str(SAMPLE_PATH),  # Uses your sample file
            "language": "en",
            "file_path": str(output_file)
        }
        
        # Add optional parameters if supported
        # Note: XTTS v2 voice cloning may not support all these parameters
        # Speed control might need post-processing
        if speed != 1.0:
            # XTTS doesn't directly support speed parameter in cloning mode
            # You'd need to use a different approach or post-process
            pass
        
        tts.tts_to_file(**params)
        
        latency = int((time.time() - start) * 1000)
        return True, latency
    except Exception as e:
        return False, str(e)


def main():
    print("="*70)
    print(" Enhanced Voice Cloning - Controllable Parameters ".center(70))
    print("="*70)
    print()
    print("How it works:")
    print("  ✅ Uses your sample file: harry_sample.wav")
    print("  ✅ Clones the voice characteristics from the sample")
    print("  ✅ You control: What text to speak")
    print("  ⚠️  Limited control: Speed/emotion may need post-processing")
    print()
    
    # Load model
    print("Loading XTTS v2 model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    fix_pytorch_loading = lambda: None
    original_torch_load = torch.load
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_torch_load(*args, **kwargs)
    torch.load = patched_load
    
    try:
        tts = TTS(MODEL_NAME).to(device)
        print("  [OK] Model loaded")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print()
    print("="*70)
    print(" Generating Cloned Voice Samples ".center(70))
    print("="*70)
    print()
    
    successful = 0
    failed = 0
    
    for i, phrase_config in enumerate(TEST_PHRASES, 1):
        text = phrase_config["text"]
        speed = phrase_config.get("speed", 1.0)
        emotion = phrase_config.get("emotion")
        
        output_file = OUTPUT_DIR / f"enhanced_{i:02d}.wav"
        
        print(f"[{i}/{len(TEST_PHRASES)}] \"{text[:50]}\"")
        print(f"   Speed: {speed}x")
        
        success, result = clone_voice_enhanced(tts, text, output_file, speed=speed, emotion=emotion)
        
        if success:
            latency = result
            print(f"   [OK] Saved to {output_file.name} ({latency}ms)")
            successful += 1
        else:
            print(f"   [ERROR] {result}")
            failed += 1
        
        print()
    
    # Summary
    print("="*70)
    print(f"Results: {successful}/{len(TEST_PHRASES)} successful")
    print()
    print("Note: XTTS v2 voice cloning:")
    print("  - Uses your sample file directly (harry_sample.wav)")
    print("  - Clones voice characteristics (tone, accent, style)")
    print("  - You control the text content")
    print("  - Speed/emotion control may require post-processing")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()




