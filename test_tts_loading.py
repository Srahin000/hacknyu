"""Quick test to see if TTS loads with voice cloning"""
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("="*70)
print(" Testing TTS Voice Cloning Load ".center(70))
print("="*70)
print()

try:
    print("Step 1: Importing torch...")
    import torch
    print("  [OK] torch imported")
    print()
    
    print("Step 2: Importing TTS...")
    from TTS.api import TTS
    print("  [OK] TTS imported")
    print()
    
    print("Step 3: Loading XTTS v2 model...")
    # Fix PyTorch loading
    original_load = torch.load
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    print("  [OK] XTTS v2 model loaded")
    print()
    
    print("="*70)
    print(" SUCCESS! TTS is working ".center(70))
    print("="*70)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

