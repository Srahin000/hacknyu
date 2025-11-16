"""
TTS Testing Script for Harry Potter Voice Assistant

Test different TTS parameters, voices, emotions, speeds, and pitches.
"""

import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_xtts_model():
    """Load XTTS v2 model once (cached) and return it"""
    
    print("Loading XTTS v2 model (using cached model)...")
    print("  ⏳ This may take 30-60 seconds on first load (model is ~1.87GB)")
    print("  💡 Subsequent uses will be much faster!")
    print()
    
    import torch
    from TTS.api import TTS
    
    # Fix for PyTorch 2.6+ weights_only=True default
    original_load = torch.load
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    start_time = time.time()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    load_time = time.time() - start_time
    
    # Restore original torch.load
    torch.load = original_load
    
    print(f"✅ XTTS v2 loaded successfully! ({load_time:.1f}s)")
    print()
    
    # Display available speakers
    if hasattr(tts, 'speakers') and tts.speakers:
        print("Available speakers:")
        if isinstance(tts.speakers, list):
            for i, speaker in enumerate(tts.speakers, 1):
                print(f"  {i}. {speaker}")
        elif isinstance(tts.speakers, dict):
            for key, value in tts.speakers.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {tts.speakers}")
        print()
    else:
        print("⚠️  No speakers list found - using speaker parameter directly")
        print()
    
    return tts


def test_xtts_v2():
    """Test XTTS v2 with various parameters"""
    
    print("=" * 70)
    print(" 🎤 XTTS v2 Testing ".center(70))
    print("=" * 70)
    print()
    
    # Create output directory
    output_dir = Path("tts_test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Load model once (reused for all tests)
        tts = load_xtts_model()
        
        # Test texts
        test_texts = [
            "I solemnly swear that I am up to no good.",
            "I solemnly swear that I am up to no good!",
            "Oh! I solemnly swear that I am up to no good!",
            "Woooow! I solemnly swear that I am up to no good!!!",
        ]
        
        # Default Harry Potter voice parameters
        default_params = {
            "speaker": "male-en-2",
            "emotion": "happy",
            "speed": 1.12,
            "pitch": 1.20
        }
        
        # Test 1: Default parameters
        print("Test 1: Default Harry Potter voice parameters")
        print(f"  Speaker: {default_params['speaker']}")
        print(f"  Emotion: {default_params['emotion']}")
        print(f"  Speed: {default_params['speed']}")
        print(f"  Pitch: {default_params['pitch']}")
        print()
        
        for i, text in enumerate(test_texts):
            output_path = output_dir / f"default_line_{i+1}.wav"
            print(f"  Generating: {text[:50]}...")
            start_time = time.time()
            
            tts.tts_to_file(
                text=text,
                file_path=str(output_path),
                language="en",
                speaker=default_params["speaker"],
                emotion=default_params["emotion"],
                speed=default_params["speed"],
                pitch=default_params["pitch"]
            )
            
            elapsed = (time.time() - start_time) * 1000
            print(f"    ✅ Saved to {output_path} ({elapsed:.0f}ms)")
        
        print()
        
        # Test 2: Different emotions
        print("Test 2: Different emotions (keeping other params same)")
        emotions = ["happy", "sad", "angry", "surprised", "neutral"]
        
        test_text = "I solemnly swear that I am up to no good!"
        
        for emotion in emotions:
            output_path = output_dir / f"emotion_{emotion}.wav"
            print(f"  Testing emotion: {emotion}")
            
            tts.tts_to_file(
                text=test_text,
                file_path=str(output_path),
                language="en",
                speaker=default_params["speaker"],
                emotion=emotion,
                speed=default_params["speed"],
                pitch=default_params["pitch"]
            )
            
            print(f"    ✅ Saved to {output_path}")
        
        print()
        
        # Test 3: Different speeds
        print("Test 3: Different speeds")
        speeds = [0.9, 1.0, 1.12, 1.25, 1.5]
        
        for speed in speeds:
            output_path = output_dir / f"speed_{speed:.2f}.wav"
            print(f"  Testing speed: {speed}")
            
            tts.tts_to_file(
                text=test_text,
                file_path=str(output_path),
                language="en",
                speaker=default_params["speaker"],
                emotion=default_params["emotion"],
                speed=speed,
                pitch=default_params["pitch"]
            )
            
            print(f"    ✅ Saved to {output_path}")
        
        print()
        
        # Test 4: Different pitches
        print("Test 4: Different pitches")
        pitches = [0.9, 1.0, 1.10, 1.20, 1.30]
        
        for pitch in pitches:
            output_path = output_dir / f"pitch_{pitch:.2f}.wav"
            print(f"  Testing pitch: {pitch}")
            
            tts.tts_to_file(
                text=test_text,
                file_path=str(output_path),
                language="en",
                speaker=default_params["speaker"],
                emotion=default_params["emotion"],
                speed=default_params["speed"],
                pitch=pitch
            )
            
            print(f"    ✅ Saved to {output_path}")
        
        print()
        
        # Test 5: Different speakers (if available)
        print("Test 5: Different speakers")
        
        # Get available speakers from model
        if hasattr(tts, 'speakers') and tts.speakers:
            if isinstance(tts.speakers, list):
                speakers_to_test = tts.speakers[:4]  # Test first 4
            elif isinstance(tts.speakers, dict):
                speakers_to_test = list(tts.speakers.keys())[:4]
            else:
                speakers_to_test = ["male-en-1", "male-en-2", "female-en-1", "female-en-2"]
        else:
            # Fallback to common speaker names
            speakers_to_test = ["male-en-1", "male-en-2", "female-en-1", "female-en-2"]
        
        print(f"  Testing {len(speakers_to_test)} speakers...")
        
        for speaker in speakers_to_test:
            output_path = output_dir / f"speaker_{speaker.replace('/', '_')}.wav"
            print(f"  Testing speaker: {speaker}")
            
            try:
                tts.tts_to_file(
                    text=test_text,
                    file_path=str(output_path),
                    language="en",
                    speaker=speaker,
                    emotion=default_params["emotion"],
                    speed=default_params["speed"],
                    pitch=default_params["pitch"]
                )
                print(f"    ✅ Saved to {output_path}")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
        
        print()
        print("=" * 70)
        print(f"✅ All tests complete! Outputs saved to: {output_dir}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ XTTS v2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pyttsx3():
    """Test pyttsx3 fallback"""
    
    print()
    print("=" * 70)
    print(" 🎤 pyttsx3 Fallback Testing ".center(70))
    print("=" * 70)
    print()
    
    try:
        import pyttsx3
        
        print("Initializing pyttsx3...")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.9)
        
        # List available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices):
            print(f"  {i+1}. {voice.name} ({voice.id})")
        
        # Try to find a good voice
        for voice in voices:
            if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                print(f"\nUsing voice: {voice.name}")
                break
        
        test_text = "I solemnly swear that I am up to no good!"
        print(f"\nSpeaking: {test_text}")
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ pyttsx3 test complete!")
        return True
        
    except Exception as e:
        print(f"❌ pyttsx3 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main testing function"""
    
    print("\n" + "=" * 70)
    print(" 🧪 TTS SYSTEM TESTING ".center(70))
    print("=" * 70)
    print()
    print("This script tests the TTS system with various parameters.")
    print("Output files will be saved to: tts_test_outputs/")
    print()
    print("💡 TIP: The model loads once and is reused for all tests.")
    print("   First load takes 30-60s, but subsequent tests are fast!")
    print()
    
    # Test XTTS v2
    xtts_success = test_xtts_v2()
    
    # Test pyttsx3 fallback
    if not xtts_success:
        print("\n⚠️  XTTS v2 failed, testing pyttsx3 fallback...")
        test_pyttsx3()
    
    print("\n" + "=" * 70)
    print(" 🎉 Testing Complete! ".center(70))
    print("=" * 70)
    print()
    print("Listen to the generated files in tts_test_outputs/ to compare:")
    print("  - Different emotions")
    print("  - Different speeds")
    print("  - Different pitches")
    print("  - Different speakers")
    print()
    print("💡 The model is now loaded in memory - you can run this script")
    print("   again and it will be much faster!")
    print()


if __name__ == "__main__":
    main()

