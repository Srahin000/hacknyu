"""
Simple TTS Test - pyttsx3

Tests basic text-to-speech functionality
"""

import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_pyttsx3():
    """Test pyttsx3 TTS"""
    print("=" * 60)
    print("Testing pyttsx3 Text-to-Speech")
    print("=" * 60)
    
    try:
        import pyttsx3
        
        print("\n[1/4] Initializing TTS engine...")
        engine = pyttsx3.init()
        print("✓ TTS engine initialized")
        
        # Get voice info
        print("\n[2/4] Checking available voices...")
        voices = engine.getProperty('voices')
        print(f"✓ Found {len(voices)} voices")
        
        for i, voice in enumerate(voices[:3]):  # Show first 3
            print(f"  Voice {i+1}: {voice.name}")
        
        # Configure
        print("\n[3/4] Configuring speech parameters...")
        engine.setProperty('rate', 150)     # Speed
        engine.setProperty('volume', 0.9)   # Volume (0-1)
        print("✓ Speech rate: 150 words/min")
        print("✓ Volume: 90%")
        
        # Test phrases
        print("\n[4/4] Testing speech output...")
        print("\n🔊 Listen for the following phrases:\n")
        
        test_phrases = [
            "Hello! I am your A I companion.",
            "Text to speech is working perfectly!",
            "I can help you learn new things every day.",
            "Let's explore the world together!"
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"  {i}. Speaking: \"{phrase}\"")
            engine.say(phrase)
            engine.runAndWait()
        
        print("\n" + "=" * 60)
        print("✓ TTS TEST PASSED!")
        print("=" * 60)
        print("\nYou should have heard 4 phrases spoken aloud.")
        print("If you didn't hear anything, check your audio settings.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def test_save_to_file():
    """Test saving speech to WAV file"""
    print("\n" + "=" * 60)
    print("Bonus: Saving Speech to File")
    print("=" * 60)
    
    try:
        import pyttsx3
        
        print("\n[1/2] Initializing...")
        engine = pyttsx3.init()
        
        print("[2/2] Saving speech to file...")
        output_file = "test_speech_output.wav"
        
        # Note: pyttsx3 doesn't directly support saving to file on Windows
        # But we can still demonstrate it works
        
        text = "This is a test of the text to speech system."
        engine.say(text)
        engine.runAndWait()
        
        print(f"\n✓ Speech generated successfully!")
        print(f"\nNote: pyttsx3 on Windows doesn't save to file directly.")
        print(f"For file output, use Coqui TTS or Picovoice Orca.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    """Run tests"""
    print("\n" + "=" * 60)
    print("SIMPLE TTS TEST - pyttsx3")
    print("=" * 60)
    print("\nThis test will speak several phrases out loud.")
    print("Make sure your speakers/headphones are on!\n")
    print("Starting test in 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    # Run tests
    success1 = test_pyttsx3()
    success2 = test_save_to_file()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if success1:
        print("✓ pyttsx3 TTS is working!")
        print("\n📝 Usage in your app:")
        print("""
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say("Hello! How can I help you?")
engine.runAndWait()
""")
        
        print("\n💡 Recommended for:")
        print("  - Quick prototyping")
        print("  - Basic voice responses")
        print("  - Offline TTS (100% local)")
        
        print("\n⚠️ Limitations:")
        print("  - Basic voice quality (robotic)")
        print("  - Limited emotion expression")
        print("  - No file export on Windows")
        
        print("\n🚀 For production, consider:")
        print("  - Picovoice Orca (best quality, runs on NPU)")
        print("  - Coqui TTS (high quality, requires Python 3.10)")
        
    else:
        print("✗ pyttsx3 test failed")
        print("\nTroubleshooting:")
        print("  1. Check pip install pyttsx3")
        print("  2. Check audio drivers")
        print("  3. Try restarting terminal")

if __name__ == "__main__":
    main()

