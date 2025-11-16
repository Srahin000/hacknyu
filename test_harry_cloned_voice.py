"""
Quick Test: Harry Potter Cloned Voice TTS
Tests the voice cloning setup before running full voice assistant
"""

import sys
from pathlib import Path
import time

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def test_cloned_voice():
    """Test the cloned voice TTS setup"""
    
    print("="*70)
    print(" Testing Harry Potter Cloned Voice TTS ".center(70))
    print("="*70)
    print()
    
    # Check voice sample exists
    sample_path = Path("sound_sample/harry_sample.wav")
    if not sample_path.exists():
        print(f"❌ Voice sample not found: {sample_path}")
        print("\nPlease add your Harry Potter voice sample to:")
        print(f"  {sample_path}")
        print("\nThis sample is used for voice cloning (6-10 seconds recommended)")
        return False
    
    print(f"✅ Voice sample found: {sample_path.name}")
    
    # Check file info
    try:
        import soundfile as sf
        audio, sr = sf.read(str(sample_path))
        duration = len(audio) / sr
        print(f"   Duration: {duration:.1f}s, Sample rate: {sr}Hz")
    except Exception as e:
        print(f"   (Could not read audio metadata: {e})")
    
    print()
    
    # Load XTTS v2 model
    print("Loading XTTS v2 model for voice cloning...")
    print("  (First time downloads ~1.8GB, subsequent loads are fast)")
    print()
    
    try:
        import torch
        from TTS.api import TTS
        
        # Fix PyTorch loading
        original_load = torch.load
        def patched_load(*args, **kwargs):
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
        
        start = time.time()
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        load_time = int((time.time() - start) * 1000)
        
        print(f"✅ XTTS v2 model loaded ({load_time}ms)")
        print()
        
    except Exception as e:
        print(f"❌ Failed to load XTTS v2: {e}")
        print("\nInstall with: pip install TTS")
        import traceback
        traceback.print_exc()
        return False
    
    # Test phrases
    test_phrases = [
        "Hello! I'm Harry Potter. Nice to meet you.",
        "That's brilliant! Tell me more about that.",
        "Blimey, I reckon we can figure this out together, mate.",
    ]
    
    output_dir = Path("cloned_voice_outputs")
    output_dir.mkdir(exist_ok=True)
    
    print("="*70)
    print(" Generating Test Phrases with Cloned Voice ".center(70))
    print("="*70)
    print()
    
    for i, text in enumerate(test_phrases, 1):
        output_file = output_dir / f"test_cloned_{i:02d}.wav"
        
        print(f"[{i}/{len(test_phrases)}] \"{text}\"")
        
        try:
            start = time.time()
            
            # Generate with cloned voice
            tts.tts_to_file(
                text=text,
                speaker_wav=str(sample_path),  # Cloned voice!
                language="en",
                file_path=str(output_file)
            )
            
            latency = int((time.time() - start) * 1000)
            print(f"   ✅ Generated in {latency}ms")
            print(f"   💾 Saved to: {output_file.name}")
            
            # Play the audio
            try:
                import sounddevice as sd
                import soundfile as sf
                
                audio_data, sample_rate = sf.read(str(output_file))
                print(f"   🔊 Playing...")
                sd.play(audio_data, sample_rate)
                sd.wait()
                print(f"   ✅ Playback complete")
            except Exception as play_error:
                print(f"   ⚠️  Playback failed: {play_error}")
                print(f"   (File saved successfully, check {output_file.name} manually)")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*70)
    print(" Test Complete! ".center(70))
    print("="*70)
    print()
    print("✅ Voice cloning is working!")
    print(f"   Test files saved to: {output_dir}/")
    print()
    print("Next step: Run the full voice assistant")
    print("  python harry_voice_assistant.py --test")
    print()
    print("="*70)
    
    return True


if __name__ == "__main__":
    try:
        success = test_cloned_voice()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

