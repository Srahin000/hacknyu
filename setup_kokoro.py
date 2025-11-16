"""
Download Kokoro TTS voice models
"""

import urllib.request
from pathlib import Path
import sys

# Kokoro voice model URLs  
MODELS = {
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
    "kokoro-v0_19.onnx": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro.onnx",
}

def download_file(url, dest):
    """Download file with progress bar"""
    print(f"Downloading: {Path(dest).name}")
    print(f"  From: {url}")
    print()
    
    try:
        def progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 // total_size)
                bar_len = 50
                filled = int(bar_len * percent / 100)
                bar = '=' * filled + '-' * (bar_len - filled)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r  [{bar}] {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
            else:
                print(".", end='', flush=True)
        
        urllib.request.urlretrieve(url, dest, progress)
        print()  # New line after progress
        print("  [OK] Download complete!")
        print()
        return True
    except Exception as e:
        print()
        print(f"  [ERROR] Failed: {e}")
        print()
        return False


def main():
    print("="*70)
    print(" Kokoro TTS Voice Model Setup ".center(70))
    print("="*70)
    print()
    
    # Find kokoro package location
    try:
        import kokoro_onnx
        kokoro_path = Path(kokoro_onnx.__file__).parent
        print(f"Kokoro package location: {kokoro_path}")
        print()
    except ImportError:
        print("[ERROR] kokoro-onnx not installed!")
        print("  Run: pip install kokoro-onnx")
        print()
        return False
    
    # Download voice models
    success_count = 0
    
    for filename, url in MODELS.items():
        dest = kokoro_path / filename
        
        if dest.exists():
            file_size_mb = dest.stat().st_size / (1024 * 1024)
            print(f"[OK] {filename} already exists ({file_size_mb:.1f} MB)")
            print()
            success_count += 1
        else:
            print(f"Downloading {filename}...")
            if download_file(url, dest):
                success_count += 1
    
    print("="*70)
    print(" Setup Complete! ".center(70))
    print("="*70)
    print()
    
    if success_count == len(MODELS):
        print("[OK] All voice models ready!")
        print()
        print("Next step:")
        print("  python test_kokoro_harry.py")
        print()
        return True
    else:
        print(f"[WARNING] {success_count}/{len(MODELS)} models downloaded")
        print()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

