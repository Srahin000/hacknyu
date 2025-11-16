"""
Generate pre-recorded Harry Potter phrases with DIA
Run this in dia_tts environment ONLY!

Usage:
    conda activate dia_tts
    python generate_harry_phrases.py
"""

from dia.model import Dia
import soundfile as sf
from pathlib import Path
import sys

def main():
    print("="*70)
    print(" DIA Harry Potter Phrase Generator ".center(70))
    print("="*70)
    print()
    print("⚠️  Make sure you're in the dia_tts environment!")
    print("   Run: conda activate dia_tts")
    print()
    
    # Load model
    print("Loading DIA model (this may take a minute on first run)...")
    print("  Model: Dia-1.6B-0626 (~1.6GB)")
    print()
    
    try:
        model = Dia.from_pretrained()
        print("✅ Model loaded successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to load DIA model: {e}")
        print()
        print("Make sure DIA is installed:")
        print("  pip install git+https://github.com/nari-labs/dia.git")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path("dia_generated")
    output_dir.mkdir(exist_ok=True)
    
    # Harry Potter phrases with emotion/sounds
    harry_phrases = {
        # Greetings
        "greeting": "[S1] Hello! I'm Harry Potter. How can I help you?",
        "greeting_friendly": "[S1] Hey there! (smiling) It's good to see you!",
        
        # Emotions
        "excited": "[S1] Wow! That's brilliant! (laughs)",
        "very_excited": "[S1] That's amazing! (excited) I can't believe it!",
        "happy": "[S1] That's great! I'm really happy to hear that!",
        "laugh": "[S1] (laughs) That's quite funny!",
        "surprise": "[S1] Blimey! I didn't expect that!",
        
        # Thinking/Uncertain
        "thinking": "[S1] Hmm, let me think about that...",
        "confused": "[S1] I'm not quite sure I understand. Can you explain?",
        "maybe": "[S1] Maybe... I'm not entirely sure.",
        
        # Concern/Worry
        "concerned": "[S1] Are you alright? (worried tone)",
        "worried": "[S1] I'm a bit worried about that... (concerned)",
        
        # Encouragement
        "encouragement": "[S1] You can do it! Don't give up!",
        "brave": "[S1] Be brave! You're stronger than you think!",
        "support": "[S1] I believe in you! You've got this!",
        
        # Farewells
        "goodbye": "[S1] Goodbye! Stay brave and be careful!",
        "see_you": "[S1] See you soon! Take care!",
        
        # Spells (iconic Harry moments)
        "expelliarmus": "[S1] Expelliarmus! (casting spell)",
        "lumos": "[S1] Lumos! (whispering)",
        "expecto_patronum": "[S1] Expecto Patronum! (determined)",
        
        # Common responses
        "yes": "[S1] Yes, absolutely!",
        "yes_excited": "[S1] Yes! (enthusiastic) Definitely!",
        "no": "[S1] No, I don't think so.",
        "not_sure": "[S1] I'm not sure about that...",
        "sorry": "[S1] I'm sorry, I didn't quite catch that.",
        "sorry_cant_help": "[S1] I'm sorry, I don't think I can help with that.",
        "thanks": "[S1] Thank you so much!",
        "welcome": "[S1] You're very welcome!",
        
        # Questions
        "what_mean": "[S1] What do you mean?",
        "can_you_repeat": "[S1] Could you repeat that, please?",
        "anything_else": "[S1] Is there anything else I can help you with?",
        
        # Understanding
        "i_see": "[S1] I see. That makes sense.",
        "interesting": "[S1] That's quite interesting!",
        "tell_me_more": "[S1] Tell me more about that!",
    }
    
    print(f"Generating {len(harry_phrases)} Harry Potter phrases...")
    print(f"This will take about {len(harry_phrases) * 7 // 60} minutes...\n")
    print("Output directory: dia_generated/")
    print()
    
    successful = 0
    failed = 0
    
    for i, (key, text) in enumerate(harry_phrases.items(), 1):
        print(f"[{i}/{len(harry_phrases)}] {key}")
        print(f"  Text: {text}")
        
        try:
            # Generate audio
            audio = model.generate(text)
            
            # Save to file
            output_file = output_dir / f"{key}.mp3"
            sf.write(str(output_file), audio, 44100)
            
            print(f"  ✅ Saved to: {output_file}")
            successful += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            failed += 1
        
        print()
    
    # Summary
    print("="*70)
    print(f"✅ Generation complete!")
    print(f"   Successful: {successful}/{len(harry_phrases)}")
    if failed > 0:
        print(f"   Failed: {failed}/{len(harry_phrases)}")
    print(f"   Output directory: {output_dir.absolute()}")
    print("="*70)
    print()
    
    print("📝 Next steps:")
    print("  1. Switch to main environment: conda activate hacknyu_offline")
    print("  2. Copy audio files to your project")
    print("  3. Use them in your voice assistant!")
    print()
    print("Audio files are in MP3 format (44.1kHz, stereo)")
    print("Total size: ~" + str(len(list(output_dir.glob("*.mp3"))) * 200) + "KB")
    print()

if __name__ == "__main__":
    main()

