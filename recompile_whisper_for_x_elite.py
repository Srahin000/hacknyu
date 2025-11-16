"""
Recompile Whisper for Snapdragon X Elite/Plus

This will compile Whisper specifically for your PC's NPU (not Samsung S24)
"""

import subprocess
import sys

print("="*70)
print("Recompiling Whisper for Snapdragon X Elite/Plus NPU")
print("="*70)

print("\n[INFO] Your current model is compiled for Samsung S24 (8 Gen 3)")
print("[INFO] You need a model compiled for Snapdragon X Elite/Plus")
print("\n[1/2] Attempting to compile via qai-hub...")

target_device = "Qualcomm Snapdragon X Elite CRD"

# Try to run qai-hub command
print(f"\nDevice: {target_device}")
print("Model: Whisper Base (quantized)")
print("\nStarting compilation (this takes 10-20 minutes)...\n")

try:
    cmd = [
        "qai-hub",
        "models",
        "whisper-base-en",
        "--device", target_device,
        "--target-runtime", "qnn",
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("[SUCCESS] Whisper compiled for Snapdragon X Elite!")
        print("="*70)
        print("""
The compiled model should now be in your working directory.
Look for a folder like: whisper_base_en_quantized_*/

Next steps:
1. Find the downloaded model folder
2. Update test_npu_whisper.py to point to new model
3. Run: python test_npu_whisper.py
4. Should now work without Error 5005!
""")
    else:
        print(f"\n[ERROR] Command failed with exit code: {result.returncode}")
        raise Exception("qai-hub command failed")
        
except FileNotFoundError:
    print("[ERROR] qai-hub command not found")
    print("\nInstall it with:")
    print("  pip install qai-hub-models[whisper_base_en]")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n" + "="*70)
    print("MANUAL COMPILATION INSTRUCTIONS")
    print("="*70)
    print(f"""
If automatic compilation failed, compile manually:

METHOD 1: Via Command Line
---------------------------
Run this command:

qai-hub models whisper-base-en \\
  --device "Qualcomm Snapdragon X Elite CRD" \\
  --target-runtime qnn

METHOD 2: Via Python
--------------------
python -m qai_hub_models.models.whisper_base_en.export \\
  --device "Qualcomm Snapdragon X Elite CRD" \\
  --target-runtime qnn

METHOD 3: Via Web UI  
--------------------
1. Go to: https://app.aihub.qualcomm.com
2. Select "Whisper Base" model
3. Choose device: "Snapdragon X Elite CRD"
4. Click "Deploy"
5. Download compiled model

METHOD 4: Use CPU (Works NOW)
-----------------------------
For immediate testing, use CPU Whisper:

pip install openai-whisper
python harry_voice_assistant.py --test

CPU latency (~2-3s) is perfectly fine for voice conversation!

IMPORTANT:
----------
Error 5005 means device mismatch. You MUST compile for X Elite,
not for Samsung S24 (8 Gen 3).
""")
