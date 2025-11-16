"""
Quick setup script for Piper TTS + SoX

Downloads and extracts:
1. Piper TTS (Windows)
2. SoX audio tool
3. British voice model for Harry Potter
"""

import urllib.request
import zipfile
import shutil
from pathlib import Path
import sys

PIPER_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alba/medium/en_GB-alba-medium.onnx"
CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json"

def download_file(url, dest):
    """Download file with progress"""
    print(f"Downloading: {Path(dest).name}")
    print(f"  From: {url}")
    
    try:
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 // total_size)
            bar_len = 40
            filled = int(bar_len * percent / 100)
            bar = '=' * filled + '-' * (bar_len - filled)
            print(f"\r  [{bar}] {percent}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, dest, progress)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n  [ERROR] Failed: {e}")
        return False


def main():
    print("="*70)
    print(" Piper TTS + SoX Setup ".center(70))
    print("="*70)
    print()
    
    # Create directories
    tools_dir = Path("tools")
    tools_dir.mkdir(exist_ok=True)
    
    # 1. Download Piper
    print("[1/3] Setting up Piper TTS...")
    print()
    
    piper_zip = tools_dir / "piper.zip"
    
    if not (tools_dir / "piper.exe").exists():
        if download_file(PIPER_URL, piper_zip):
            print("  Extracting...")
            with zipfile.ZipFile(piper_zip, 'r') as zip_ref:
                zip_ref.extractall(tools_dir)
            
            # Move piper.exe to tools root
            piper_src = tools_dir / "piper" / "piper.exe"
            if piper_src.exists():
                shutil.move(str(piper_src), str(tools_dir / "piper.exe"))
            
            piper_zip.unlink()  # Delete zip
            print("  [OK] Piper installed!")
        else:
            print("  [FAILED] Could not download Piper")
            return False
    else:
        print("  [OK] Piper already installed")
    
    print()
    
    # 2. Download voice model
    print("[2/3] Downloading British voice model...")
    print()
    
    model_path = Path("en_GB-alba-medium.onnx")
    config_path = Path("en_GB-alba-medium.onnx.json")
    
    if not model_path.exists():
        if not download_file(MODEL_URL, model_path):
            print("  [FAILED] Could not download model")
            return False
    else:
        print("  [OK] Model already downloaded")
    
    if not config_path.exists():
        if not download_file(CONFIG_URL, config_path):
            print("  [FAILED] Could not download config")
            return False
    else:
        print("  [OK] Config already downloaded")
    
    print()
    
    # 3. SoX instructions
    print("[3/3] SoX Audio Tool")
    print()
    print("  SoX must be installed separately:")
    print("  1. Download from: https://sourceforge.net/projects/sox/files/sox/14.4.2/")
    print("  2. Get: sox-14.4.2-win32.zip")
    print("  3. Extract and add to PATH")
    print()
    print("  OR use Chocolatey: choco install sox")
    print()
    
    # Summary
    print("="*70)
    print(" Setup Complete! ".center(70))
    print("="*70)
    print()
    print("[OK] Piper TTS installed: tools/piper.exe")
    print(f"[OK] Voice model: {model_path}")
    print("[TODO] Install SoX (see instructions above)")
    print()
    print("Once SoX is installed, run:")
    print("  python test_piper_harry.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)

