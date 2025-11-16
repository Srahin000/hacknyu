"""
Piper TTS + SoX Kid Voice Filter
Creates a Harry Potter kid voice by pitch-shifting a British adult voice

Requirements:
1. Piper TTS: https://github.com/rhasspy/piper/releases
2. SoX: http://sox.sourceforge.net/
3. British voice model (download links below)
"""

import subprocess
import os
from pathlib import Path

# Configuration
TEXT = "I solemnly swear that I am up to no good."
MODEL_PATH = "en_GB-alba-medium.onnx"
PIPER_EXE = "tools\\piper.exe"  # Downloaded Piper
OUTPUT_RAW = "temp_adult.wav"
OUTPUT_KID = "harry_potter_kid.wav"

# Test phrases
TEST_PHRASES = [
    "I solemnly swear that I am up to no good.",
    "Hello! I'm Harry Potter. How can I help you today?",
    "That's brilliant! Tell me more about that.",
    "Expecto Patronum!",
    "Don't worry, we'll figure this out together.",
]


def check_dependencies():
    """Check if Piper and SoX are installed"""
    print("Checking dependencies...")
    print()
    
    # Check Piper (use local version first)
    piper_path = Path(PIPER_EXE)
    if piper_path.exists():
        print(f"[OK] Piper found: {PIPER_EXE}")
    else:
        try:
            result = subprocess.run(['piper', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"[OK] Piper found in PATH: {result.stdout.strip()}")
        except FileNotFoundError:
            print("[ERROR] Piper not found!")
            print("   Run: python setup_piper.py")
            return False
        except Exception as e:
            print(f"[WARNING] Piper check failed: {e}")
    
    # Check SoX
    try:
        result = subprocess.run(['sox', '--version'], 
                              capture_output=True, text=True, timeout=5)
        print(f"[OK] SoX found: {result.stdout.strip().split()[1]}")
    except FileNotFoundError:
        print("[ERROR] SoX not found!")
        print("   Download from: https://sourceforge.net/projects/sox/files/sox/")
        print("   Get: sox-14.4.2-win32.zip")
        print("   Extract and add to PATH")
        return False
    except Exception as e:
        print(f"[WARNING] SoX check failed: {e}")
    
    print()
    return True


def check_model():
    """Check if Piper model exists"""
    if not Path(MODEL_PATH).exists():
        print(f"[ERROR] Model not found: {MODEL_PATH}")
        print()
        print("Download British voice model:")
        print("  1. Go to: https://github.com/rhasspy/piper/releases/tag/v1.2.0")
        print("  2. Download: en_GB-alba-medium.onnx")
        print("  3. Download: en_GB-alba-medium.onnx.json")
        print("  4. Place both files in this directory")
        print()
        print("Alternative models:")
        print("  - en_GB-jenny_dioco-medium.onnx (Female, expressive)")
        print("  - en_GB-cori-medium.onnx (Male)")
        print()
        return False
    
    # Check for config file
    config_path = MODEL_PATH + ".json"
    if not Path(config_path).exists():
        print(f"[WARNING] Config file missing: {config_path}")
        print("   Model may not work without it!")
        print()
    
    return True


def generate_kid_voice(text, output_file, pitch=350, tempo=1.1):
    """
    Generate kid voice using Piper + SoX
    
    Args:
        text: Text to speak
        pitch: Pitch shift (200-500, higher = younger)
        tempo: Speed multiplier (1.0-1.2, higher = faster)
    
    Returns:
        True if successful
    """
    try:
        # Step 1: Generate base voice with Piper
        print(f"   [1/2] Generating base voice...")
        
        # Use local piper if available, otherwise system piper
        piper_exe = PIPER_EXE if Path(PIPER_EXE).exists() else "piper"
        
        # Piper command: provide text via stdin
        result = subprocess.run(
            [piper_exe, '--model', MODEL_PATH, '--output_file', OUTPUT_RAW],
            input=text,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"   [ERROR] Piper failed: {result.stderr}")
            print(f"   stdout: {result.stdout}")
            return False
        
        if not Path(OUTPUT_RAW).exists():
            print(f"   [ERROR] Piper didn't create output file")
            return False
        
        # Step 2: Apply kid filter with SoX
        print(f"   [2/2] Applying kid filter (pitch={pitch}, tempo={tempo})...")
        
        sox_cmd = f'sox {OUTPUT_RAW} {output_file} pitch {pitch} tempo {tempo}'
        
        result = subprocess.run(sox_cmd, shell=True, capture_output=True,
                              text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"   [ERROR] SoX failed: {result.stderr}")
            return False
        
        # Cleanup
        if Path(OUTPUT_RAW).exists():
            os.remove(OUTPUT_RAW)
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"   [ERROR] Command timed out")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False


def main():
    print("="*70)
    print(" Piper + SoX Harry Potter Voice Generator ".center(70))
    print("="*70)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print()
        print("Please install missing dependencies and try again.")
        return
    
    # Check model
    if not check_model():
        print()
        print("Please download the model and try again.")
        return
    
    print("="*70)
    print(" Generating Test Clips ".center(70))
    print("="*70)
    print()
    
    # Create output directory
    output_dir = Path("piper_outputs")
    output_dir.mkdir(exist_ok=True)
    
    successful = 0
    failed = 0
    
    for i, phrase in enumerate(TEST_PHRASES, 1):
        output_file = output_dir / f"harry_{i:02d}.wav"
        
        print(f"[{i}/{len(TEST_PHRASES)}] \"{phrase[:50]}...\"")
        
        import time
        start = time.time()
        
        if generate_kid_voice(phrase, str(output_file)):
            latency = int((time.time() - start) * 1000)
            print(f"   [OK] Saved to {output_file.name} ({latency}ms)")
            successful += 1
        else:
            print(f"   [FAILED]")
            failed += 1
        
        print()
    
    # Summary
    print("="*70)
    print(" Results ".center(70))
    print("="*70)
    print()
    print(f"Successful: {successful}/{len(TEST_PHRASES)}")
    print(f"Failed: {failed}/{len(TEST_PHRASES)}")
    print()
    
    if successful > 0:
        print(f"[OK] Generated voices saved to: {output_dir}/")
        print()
        print("Listen to the files and check quality!")
        print()
        print("Tuning options:")
        print("  - Increase pitch (400-500) for younger voice")
        print("  - Decrease pitch (250-350) for older voice")
        print("  - Adjust tempo (1.0-1.3) for speed")
        print()
        print("Try different models:")
        print("  - en_GB-jenny_dioco-medium.onnx (more expressive)")
        print("  - en_GB-cori-medium.onnx (male voice)")
    else:
        print("[ERROR] All generations failed. Check errors above.")
    
    print("="*70)


if __name__ == "__main__":
    main()

