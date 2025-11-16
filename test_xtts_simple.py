"""
Simple XTTS Voice Cloning Test
Uses WAV sample to avoid FFmpeg dependency issues
"""

import torch
from TTS.api import TTS
import soundfile as sf

print("="*70)
print(" XTTS Voice Cloning Test (Simple) ".center(70))
print("="*70)
print()

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
print()

# Sample file
sample_path = "sound_sample/harry_sample.wav"
print(f"Using sample: {sample_path}")

# Check sample
audio, sr = sf.read(sample_path)
duration = len(audio) / sr
print(f"  Duration: {duration:.1f}s")
print(f"  Sample rate: {sr}Hz")
print()

# Load model with workaround for PyTorch 2.9
print("Loading XTTS model...")
original_torch_load = torch.load
def patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_load

try:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    print("[OK] Model loaded!")
finally:
    torch.load = original_torch_load  # Restore

print()

# Test phrases
phrases = [
    "I solemnly swear that I am up to no good.",
    "Hello! I'm Harry Potter.",
    "That's brilliant!",
]

print(f"Generating {len(phrases)} test clips...")
print()

for i, text in enumerate(phrases, 1):
    output_file = f"xtts_test_{i}.wav"
    print(f"[{i}/{len(phrases)}] \"{text}\"")
    
    try:
        import time
        start = time.time()
        
        tts.tts_to_file(
            text=text,
            speaker_wav=sample_path,
            language="en",
            file_path=output_file
        )
        
        latency = int((time.time() - start) * 1000)
        print(f"  [OK] Saved to {output_file} ({latency}ms)")
        
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
    
    print()

print("="*70)
print("Done! Check the xtts_test_*.wav files")
print("="*70)

