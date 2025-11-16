"""
Quick script to check if the Llama 3.2 1B export is running and progressing
"""

import os
import sys
import time
from pathlib import Path

def check_status():
    """Check export status"""
    
    print("="*70)
    print(" LLAMA 3.2 1B EXPORT STATUS CHECK".center(70))
    print("="*70)
    print()
    
    # Check if output directory exists
    output_dir = Path("harry_genie_bundle")
    
    if output_dir.exists():
        print("[1/3] Output directory: EXISTS")
        files = list(output_dir.glob("*"))
        if files:
            print(f"      Files created: {len(files)}")
            for f in files[:5]:  # Show first 5
                print(f"        - {f.name}")
            if len(files) > 5:
                print(f"        ... and {len(files) - 5} more")
        else:
            print("      (Empty - export initializing)")
    else:
        print("[1/3] Output directory: NOT YET CREATED")
        print("      Export is downloading model weights...")
    
    print()
    
    # Check Hugging Face cache (where models download)
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    if hf_cache.exists():
        llama_dirs = list(hf_cache.glob("*llama*3*"))
        if llama_dirs:
            print("[2/3] Hugging Face cache: MODEL DOWNLOADING")
            for d in llama_dirs[:2]:
                print(f"      - {d.name}")
        else:
            print("[2/3] Hugging Face cache: Checking...")
    else:
        print("[2/3] Hugging Face cache: Not found")
    
    print()
    
    # Check if process is running (simplified check)
    print("[3/3] Export process: Should be running in background")
    print("      (Check Task Manager for python.exe if unsure)")
    
    print()
    print("="*70)
    print()
    
    if output_dir.exists() and list(output_dir.glob("*.bin")):
        print("STATUS: Export is PROGRESSING! Models being compiled.")
        print("        This takes 2-3 hours total.")
    elif output_dir.exists():
        print("STATUS: Export STARTED, creating files...")
        print("        Be patient, this takes 2-3 hours.")
    else:
        print("STATUS: Export INITIALIZING, downloading weights...")
        print("        First download takes 10-20 minutes.")
        print("        Then compilation takes 2-3 hours.")
    
    print()
    print("To monitor:")
    print("  - Run this script again: python check_export_status.py")
    print("  - Check Task Manager for python.exe CPU usage")
    print("  - Look for harry_genie_bundle folder creation")
    print()
    
    return output_dir.exists()

if __name__ == "__main__":
    check_status()

