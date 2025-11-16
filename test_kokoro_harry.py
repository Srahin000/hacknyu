"""
Test Kokoro TTS for Harry Potter Voice
Kokoro is a lightweight 82M parameter TTS with high quality voices
"""

from kokoro_onnx import Kokoro
import time
from pathlib import Path

# Test phrases
TEST_PHRASES = [
    "I solemnly swear that I am up to no good.",
    "Hello! I'm Harry Potter. How can I help you today?",
    "That's brilliant! Tell me more about that.",
    "Expecto Patronum!",
    "Don't worry, we'll figure this out together.",
    "Bloody brilliant!",
]

def test_kokoro():
    """Test Kokoro TTS with different voices"""
    print("="*70)
    print(" Kokoro TTS - Harry Potter Voice Test ".center(70))
    print("="*70)
    print()
    
    # Create output directory
    output_dir = Path("kokoro_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Kokoro
    print("Loading Kokoro TTS...")
    print("  Model: Kokoro-82M")
    print()
    
    try:
        start = time.time()
        # British Female - Emma (good for younger Harry Potter voice)
        # Find the voices file path
        import kokoro_onnx
        from pathlib import Path as PathLib
        kokoro_pkg_path = PathLib(kokoro_onnx.__file__).parent
        voices_path = str(kokoro_pkg_path / "voices-v1.0.bin")
        
        kokoro = Kokoro("bf_emma", voices_path)
        load_time = int((time.time() - start) * 1000)
        print(f"[OK] Model loaded (bf_emma - British Female) in {load_time}ms")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to load Kokoro: {e}")
        print()
        print("Available voices:")
        try:
            import kokoro_onnx
            # List available voices if possible
            print("  Check: https://github.com/thewh1teagle/kokoro-onnx")
        except:
            pass
        return
    
    print("="*70)
    print(" Generating Test Clips ".center(70))
    print("="*70)
    print()
    
    successful = 0
    failed = 0
    total_latency = 0
    
    for i, phrase in enumerate(TEST_PHRASES, 1):
        output_file = output_dir / f"harry_{i:02d}.wav"
        
        print(f"[{i}/{len(TEST_PHRASES)}] \"{phrase[:50]}\"")
        
        try:
            start = time.time()
            
            # Generate audio
            samples, sample_rate = kokoro.create(phrase)
            
            # Save to WAV file
            import wave
            import numpy as np
            
            with wave.open(str(output_file), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Convert float32 samples to int16
                audio_int16 = (samples * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
            
            latency = int((time.time() - start) * 1000)
            total_latency += latency
            
            print(f"   [OK] Saved to {output_file.name} ({latency}ms)")
            successful += 1
            
        except Exception as e:
            print(f"   [ERROR] {e}")
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
        print(f"[OK] Generated voices saved to: {output_dir}/")
        print()
        print("Quality notes:")
        print("  - Kokoro uses British English (en_gb)")
        print("  - 82M parameter model for high quality")
        print("  - Runs fully offline")
        print("  - Fast inference on CPU")
        print()
        print("To use different voices:")
        print("  - bf_emma (British Female - Emma)")
        print("  - bf_isabella (British Female - Isabella)")
        print("  - bm_george (British Male - George)")
        print("  - bm_lewis (British Male - Lewis)")
        print()
    else:
        print("[ERROR] All generations failed. Check errors above.")
    
    print("="*70)


def list_available_voices():
    """List all available Kokoro voices"""
    print("Checking available Kokoro voices...")
    print()
    
    try:
        from kokoro_onnx import Kokoro
        # Available Kokoro voices
        voices = [
            ("bf_emma", "British Female - Emma (good for Harry)"),
            ("bf_isabella", "British Female - Isabella"),
            ("bm_george", "British Male - George"),
            ("bm_lewis", "British Male - Lewis"),
        ]
        
        print("Available voices:")
        for voice_id, description in voices:
            print(f"  - {voice_id}: {description}")
        print()
        
    except Exception as e:
        print(f"Could not list voices: {e}")
        print()


if __name__ == "__main__":
    try:
        # list_available_voices()
        test_kokoro()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

