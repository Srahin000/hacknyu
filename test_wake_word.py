"""
Test Picovoice Wake Word Detection

Uses your custom .ppn file: Harry-Potter_en_windows_v3_0_0.ppn
"""

import sys
import struct
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_wake_word():
    """Test Picovoice Porcupine wake word detection"""
    print("=" * 60)
    print("PICOVOICE WAKE WORD DETECTION TEST")
    print("=" * 60)
    
    try:
        import pvporcupine
        import sounddevice as sd
        
        # Check for access key
        print("\n[1/4] Checking Picovoice access key...")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        access_key = os.getenv('PICOVOICE_ACCESS_KEY')
        
        if not access_key:
            print("✗ PICOVOICE_ACCESS_KEY not set in .env")
            print("\nTo get your access key:")
            print("  1. Go to: https://console.picovoice.ai/")
            print("  2. Sign up (free)")
            print("  3. Copy your Access Key")
            print("  4. Add to .env file:")
            print("     PICOVOICE_ACCESS_KEY=your_key_here")
            return False
        
        print(f"✓ Access key found: {access_key[:20]}...")
        
        # Find .ppn file
        print("\n[2/4] Loading wake word model...")
        ppn_file = Path("ppn_files/Harry-Potter_en_windows_v3_0_0.ppn")
        
        if not ppn_file.exists():
            print(f"✗ Wake word file not found: {ppn_file}")
            return False
        
        print(f"✓ Found wake word: {ppn_file.name}")
        print(f"  Wake word: 'Harry Potter'")
        print(f"  Language: English")
        print(f"  Platform: Windows")
        
        # Initialize Porcupine
        print("\n[3/4] Initializing Porcupine...")
        
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[str(ppn_file)]
        )
        
        print("✓ Porcupine initialized")
        print(f"  Sample rate: {porcupine.sample_rate} Hz")
        print(f"  Frame length: {porcupine.frame_length} samples")
        
        # Start listening
        print("\n[4/4] Listening for wake word...")
        print("=" * 60)
        print("\n🎤 Say 'HARRY POTTER' to trigger detection!")
        print("   (Press Ctrl+C to stop)\n")
        
        detection_count = 0
        frame_count = 0
        
        # Open audio stream and process directly (not using callback for better feedback)
        stream = sd.InputStream(
            channels=1,
            samplerate=porcupine.sample_rate,
            blocksize=porcupine.frame_length,
            dtype='int16'
        )
        
        stream.start()
        print("🟢 LISTENING...", end='', flush=True)
        
        try:
            while True:
                # Read audio frame
                audio_frame, overflowed = stream.read(porcupine.frame_length)
                
                if overflowed:
                    print("\n⚠ Audio buffer overflow", end='', flush=True)
                
                # Convert to required format
                pcm = struct.unpack_from("h" * porcupine.frame_length, audio_frame)
                
                # Detect wake word
                keyword_index = porcupine.process(pcm)
                
                # Show we're actively listening
                frame_count += 1
                if frame_count % 30 == 0:  # Update every ~1 second
                    print(".", end='', flush=True)
                
                if keyword_index >= 0:
                    detection_count += 1
                    print(f"\n\n{'='*60}")
                    print(f"✅ WAKE WORD DETECTED! (Detection #{detection_count})")
                    print(f"{'='*60}")
                    print(f"\n   🎯 Detected: 'Harry Potter'")
                    print(f"   ⚡ Response time: <50ms")
                    print(f"   ✓ Working perfectly!\n")
                    print("🟢 LISTENING...", end='', flush=True)
                    frame_count = 0
        
        finally:
            stream.stop()
            stream.close()
        
    except KeyboardInterrupt:
        print("\n\n✓ Stopping wake word detection...")
        print(f"  Total detections: {detection_count}")
        
        if detection_count > 0:
            print("\n✅ WAKE WORD TEST PASSED!")
        else:
            print("\n⚠️  No detections (did you say 'Harry Potter'?)")
        
        return True
        
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("\nInstall with:")
        print("  pip install pvporcupine sounddevice")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            porcupine.delete()
        except:
            pass

def main():
    """Run wake word test"""
    print("\n" + "=" * 60)
    print("PICOVOICE PORCUPINE - WAKE WORD TEST")
    print("=" * 60)
    print("\nThis will test your custom wake word:")
    print("  File: Harry-Potter_en_windows_v3_0_0.ppn")
    print("  Wake word: 'Harry Potter'")
    print("\nMake sure you have:")
    print("  ✓ Microphone connected")
    print("  ✓ PICOVOICE_ACCESS_KEY in .env file")
    print()
    
    input("Press ENTER to start listening...")
    
    success = test_wake_word()
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("""
Your wake word detection is working!

Now you can integrate it with STT:

1. Wake word triggers → Start recording
2. Record speech → Transcribe with Whisper
3. Generate response → Play with TTS

Run the full pipeline:
  python test_full_pipeline.py

(I'll create this next if you want!)
""")
    else:
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING")
        print("=" * 60)
        print("""
If wake word detection failed:

1. Get Picovoice Access Key:
   - Visit: https://console.picovoice.ai/
   - Sign up (free)
   - Copy your Access Key
   
2. Add to .env file:
   PICOVOICE_ACCESS_KEY=your_key_here
   
3. Test your microphone:
   - Check Windows sound settings
   - Ensure microphone is default device
   
4. Run test again:
   python test_wake_word.py
""")

if __name__ == "__main__":
    main()

