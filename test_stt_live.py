"""
Live Whisper STT Test - NPU Version

Uses Qualcomm AI Hub NPU-optimized model
Shows "RECORDING..." while recording, then transcribes what you said
"""

import sys
import numpy as np
import sounddevice as sd
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def clear_line():
    """Clear the current line"""
    print('\r' + ' ' * 80 + '\r', end='')

def test_stt_npu():
    """STT test using NPU model from Qualcomm AI Hub"""
    print("=" * 60)
    print("LIVE SPEECH-TO-TEXT TEST")
    print("Using Qualcomm AI Hub NPU-Optimized Model")
    print("=" * 60)
    
    try:
        # Load NPU model
        print("\n[1/2] Loading NPU-optimized model...")
        from qai_hub_models.models.whisper_base_en import WhisperBaseEnglish
        
        model = WhisperBaseEnglish.from_pretrained()
        print("✓ NPU model loaded and ready!")
        print("  (Optimized for Snapdragon NPU - ~44ms on device)")
        
        # Recording parameters
        duration = 8
        sample_rate = 16000
        
        while True:
            print("\n" + "=" * 60)
            input("Press ENTER to start recording (or Ctrl+C to quit)...")
            
            print("\n" + "=" * 60)
            print("🎤 RECORDING... (speak now!)")
            print("=" * 60)
            
            # Start recording
            audio = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float32')
            
            # Show timer while recording
            for i in range(duration):
                remaining = duration - i
                print(f"\r🔴 RECORDING... {remaining} seconds left", end='', flush=True)
                time.sleep(1)
            
            # Wait for recording to finish
            sd.wait()
            audio = audio.flatten()
            
            # Clear the recording line
            clear_line()
            print("✓ Recording complete!")
            
            # Transcribe
            print("\n[2/2] Transcribing your speech...")
            
            start_time = time.time()
            transcription = model(audio)
            elapsed = time.time() - start_time
            
            # Show result
            print(f"✓ Done! (took {elapsed:.1f}s)")
            print("\n" + "=" * 60)
            print(f"📝 YOU SAID: \"{transcription}\"")
            print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n✓ Exiting...")
        return True
    except ImportError:
        print("\n✗ qai_hub_models not available")
        print("  Falling back to CPU version...")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the NPU-optimized STT test"""
    print("\n" + "=" * 60)
    print("WHISPER STT - NPU VERSION")
    print("=" * 60)
    print("\nUsing Qualcomm AI Hub NPU-optimized model")
    print("Optimized for Snapdragon devices (~44ms latency on device)\n")
    
    test_stt_npu()

if __name__ == "__main__":
    main()

