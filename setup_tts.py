"""
Setup Coqui TTS for local inference

Model: xtts_v2 (multilingual, expressive)
Can adjust enthusiasm through text punctuation
"""

import sys
from pathlib import Path

def setup_tts():
    """Install and configure Coqui TTS"""
    
    print("=" * 60)
    print("Setting up Coqui TTS (XTTS_v2)")
    print("=" * 60)
    
    # Check if TTS is installed
    try:
        from TTS.api import TTS
        print("✓ TTS already installed")
    except ImportError:
        print("\n[1/3] Installing TTS...")
        print("Run: pip install TTS")
        return
    
    print("\n[2/3] Downloading XTTS_v2 model...")
    try:
        # Initialize TTS (will download model if not cached)
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("✓ Model downloaded and ready")
        
        # Get model info
        print(f"\nModel info:")
        print(f"  - Type: XTTS_v2 (Expressive TTS)")
        print(f"  - Languages: Multilingual (English supported)")
        print(f"  - Voice cloning: Supported")
        print(f"  - Inference: CPU (can be fast on modern CPUs)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    print("\n[3/3] Testing TTS with different enthusiasm levels...")
    
    # Create test outputs
    test_texts = [
        ("Normal", "Hello! I'm ready to help you learn."),
        ("Excited", "WOW! That's such a great question!"),
        ("Enthusiastic", "Oh! I love talking about this topic!"),
        ("Very excited", "AMAZING! You're doing so well!")
    ]
    
    output_dir = Path("tts_samples")
    output_dir.mkdir(exist_ok=True)
    
    for level, text in test_texts:
        try:
            output_path = output_dir / f"{level.lower().replace(' ', '_')}.wav"
            tts.tts_to_file(
                text=text,
                file_path=str(output_path),
                language="en"
            )
            print(f"✓ Created: {level} - '{text[:30]}...'")
        except Exception as e:
            print(f"✗ Failed {level}: {e}")
    
    print("\n" + "=" * 60)
    print("TTS Setup Complete!")
    print("=" * 60)
    print("\nTest samples saved to: tts_samples/")
    print("\nUsage in your app:")
    print("""
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

# Generate speech
tts.tts_to_file(
    text="Hello! How can I help you?",
    file_path="output.wav",
    language="en"
)
    """)
    
    print("\n💡 Tips for expressive speech:")
    print("  - Use exclamation marks: 'Wow! That's cool!'")
    print("  - Add interjections: 'Oh! I see what you mean!'")
    print("  - Use capitals: 'AMAZING work!'")
    print("  - Question marks for curious tone: 'Really?'")
    
    print("\n⚡ Performance notes:")
    print("  - First inference: ~2-5 seconds (model loading)")
    print("  - Subsequent: ~0.5-2 seconds per sentence")
    print("  - Can run in background thread")
    print("  - Consider caching common phrases")
    
    print("\n🎯 NPU Optimization:")
    print("  - TTS runs best on CPU (large model, sequential)")
    print("  - Keep STT + Emotion on NPU (parallel, low latency)")
    print("  - TTS can be async (generate while avatar animates)")
    print("=" * 60)


if __name__ == "__main__":
    setup_tts()

