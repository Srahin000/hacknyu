"""
Quick System Check for Harry Potter Voice Assistant

Verifies all components are installed and configured correctly
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_component(name, check_func):
    """Check a component and print status"""
    print(f"\n{'='*60}")
    print(f"Checking: {name}")
    print('='*60)
    
    try:
        result = check_func()
        if result:
            print(f"✅ {name} is READY")
            return True
        else:
            print(f"❌ {name} is NOT READY")
            return False
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")
        return False


def check_picovoice():
    """Check Picovoice wake word"""
    
    # Check import
    print("[1/3] Checking pvporcupine...")
    try:
        import pvporcupine
        print("  ✓ pvporcupine installed")
    except ImportError:
        print("  ✗ pvporcupine not installed")
        print("  Install: pip install pvporcupine")
        return False
    
    # Check access key
    print("[2/3] Checking access key...")
    from dotenv import load_dotenv
    load_dotenv()
    
    access_key = os.getenv('PICOVOICE_ACCESS_KEY')
    if not access_key:
        print("  ✗ PICOVOICE_ACCESS_KEY not in .env")
        print("\n  Get your free key:")
        print("    1. Visit: https://console.picovoice.ai/")
        print("    2. Sign up (free)")
        print("    3. Copy Access Key")
        print("    4. Add to .env file:")
        print("       PICOVOICE_ACCESS_KEY=your_key_here")
        return False
    
    print(f"  ✓ Access key found: {access_key[:15]}...")
    
    # Check wake word file
    print("[3/3] Checking wake word file...")
    ppn_file = Path("ppn_files/Harry-Potter_en_windows_v3_0_0.ppn")
    if not ppn_file.exists():
        print(f"  ✗ Wake word file not found: {ppn_file}")
        return False
    
    print(f"  ✓ Wake word file exists")
    print(f"  Wake word: 'Harry Potter'")
    
    return True


def check_whisper():
    """Check Whisper STT"""
    
    print("[1/2] Checking Whisper installation...")
    
    # Try faster-whisper first
    try:
        import faster_whisper
        print("  ✓ faster-whisper installed (recommended)")
        stt_type = "faster-whisper"
    except ImportError:
        # Try regular whisper
        try:
            import whisper
            print("  ✓ whisper installed (standard)")
            stt_type = "whisper"
        except ImportError:
            print("  ✗ No Whisper installation found")
            print("\n  Install one of:")
            print("    pip install faster-whisper  (recommended)")
            print("    pip install openai-whisper  (standard)")
            return False
    
    # Check sounddevice
    print("[2/2] Checking audio library...")
    try:
        import sounddevice
        print("  ✓ sounddevice installed")
    except ImportError:
        print("  ✗ sounddevice not installed")
        print("  Install: pip install sounddevice")
        return False
    
    return True


def check_llama():
    """Check Llama LLM"""
    
    # Check llama-cpp-python
    print("[1/3] Checking llama-cpp-python...")
    try:
        from llama_cpp import Llama
        print("  ✓ llama-cpp-python installed")
    except ImportError:
        print("  ✗ llama-cpp-python not installed")
        print("\n  Install with:")
        print("    pip install llama-cpp-python")
        print("\n  Or use precompiled wheels:")
        print("    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
        return False
    
    # Check model file
    print("[2/3] Checking model file...")
    model_paths = [
        "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    ]
    
    model_found = False
    for path in model_paths:
        if os.path.exists(path):
            print(f"  ✓ Model found: {path}")
            
            # Check size
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  ✓ Model size: {size_mb:.1f} MB")
            
            model_found = True
            break
    
    if not model_found:
        print("  ✗ Model not found")
        print("\n  Download from:")
        print("    https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF")
        print("\n  Download file: Llama-3.2-1B-Instruct-Q4_K_M.gguf")
        print("  Save to: models/")
        return False
    
    # Check harry_llama_cpp.py exists
    print("[3/3] Checking Harry integration...")
    if not os.path.exists("harry_llama_cpp.py"):
        print("  ✗ harry_llama_cpp.py not found")
        return False
    
    print("  ✓ harry_llama_cpp.py exists")
    
    return True


def check_tts():
    """Check TTS"""
    
    print("[1/1] Checking pyttsx3...")
    try:
        import pyttsx3
        
        # Try to initialize
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"  ✓ pyttsx3 installed")
        print(f"  ✓ Found {len(voices)} voices")
        
        # Show available voices
        if voices:
            print("\n  Available voices:")
            for i, voice in enumerate(voices[:3]):  # Show first 3
                print(f"    {i+1}. {voice.name}")
        
        return True
        
    except ImportError:
        print("  ✗ pyttsx3 not installed")
        print("  Install: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"  ✗ TTS initialization failed: {e}")
        return False


def check_audio_devices():
    """Check audio input/output devices"""
    
    print("[1/1] Checking audio devices...")
    
    try:
        import sounddevice as sd
        
        # Get default devices
        input_device = sd.query_devices(kind='input')
        output_device = sd.query_devices(kind='output')
        
        print(f"\n  ✓ Input device: {input_device['name']}")
        print(f"  ✓ Output device: {output_device['name']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking devices: {e}")
        return False


def main():
    """Run all checks"""
    
    print("\n" + "="*60)
    print(" HARRY POTTER VOICE ASSISTANT - SYSTEM CHECK ".center(60))
    print("="*60)
    
    results = {}
    
    # Check each component
    results['Wake Word (Picovoice)'] = check_component('Wake Word (Picovoice)', check_picovoice)
    results['Speech-to-Text (Whisper)'] = check_component('Speech-to-Text (Whisper)', check_whisper)
    results['LLM (Llama)'] = check_component('LLM (Llama)', check_llama)
    results['Text-to-Speech (pyttsx3)'] = check_component('Text-to-Speech (pyttsx3)', check_tts)
    results['Audio Devices'] = check_component('Audio Devices', check_audio_devices)
    
    # Summary
    print("\n" + "="*60)
    print(" SUMMARY ".center(60))
    print("="*60)
    
    all_ready = True
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")
        if not status:
            all_ready = False
    
    print("\n" + "="*60)
    
    if all_ready:
        print("\n🎉 ALL SYSTEMS GO!")
        print("\nYou're ready to run the voice assistant!")
        print("\nStart with:")
        print("  python harry_voice_assistant.py --test    (test mode)")
        print("  python harry_voice_assistant.py           (full mode)")
    else:
        print("\n⚠️  Some components need attention")
        print("\nFix the issues above, then run this check again:")
        print("  python check_voice_assistant_ready.py")
    
    print()


if __name__ == "__main__":
    main()


