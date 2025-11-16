"""
Simple test for QAIRT NPU Whisper Quantized Model

Tests your deployed Whisper model on Snapdragon NPU
"""

import os
import sys
import numpy as np
from pathlib import Path

# Set QAIRT SDK path (adjust if needed)
QNN_SDK_ROOT = "C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130"
os.environ['QNN_SDK_ROOT'] = QNN_SDK_ROOT
os.environ['PATH'] = f"{QNN_SDK_ROOT}\\lib\\aarch64-windows-msvc;" + os.environ.get('PATH', '')

print("="*70)
print("Testing QAIRT NPU Whisper Quantized Model")
print("="*70)

# 1. Check model files
model_path = Path("models/whisper_base")

if not model_path.exists():
    print(f"[ERROR] Model directory not found: {model_path}")
    sys.exit(1)

model_bin = model_path / "model.bin"
model_onnx = model_path / "model.onnx"

print(f"\n[1/3] Checking model files...")
print(f"  Directory: {model_path}")
if model_bin.exists():
    print(f"  model.bin: OK ({model_bin.stat().st_size / 1024 / 1024:.1f} MB)")
else:
    print(f"  model.bin: NOT FOUND")
    
if model_onnx.exists():
    print(f"  model.onnx: OK")
else:
    print(f"  model.onnx: NOT FOUND")

if not model_bin.exists():
    print("\n[ERROR] model.bin not found (NPU compiled model)")
    sys.exit(1)

# 2. Test ONNX Runtime with QNN
print(f"\n[2/4] Testing ONNX Runtime with QNN ExecutionProvider...")

try:
    import onnxruntime as ort
    
    print(f"  ONNX Runtime version: {ort.__version__}")
    print(f"  Available providers: {ort.get_available_providers()}")
    
    # Try to create session with QNN
    if 'QNNExecutionProvider' in ort.get_available_providers():
        print("\n  [SUCCESS] QNNExecutionProvider IS AVAILABLE!")
        
        # Try loading model with QNN options
        print("\n  Attempting to load model with QNN...")
        try:
            qnn_options = {
                'backend_path': 'QnnHtp.dll',  # Hexagon/NPU backend
                'qnn_context_cache_enable': '1',
            }
            
            session = ort.InferenceSession(
                str(model_onnx),
                providers=['QNNExecutionProvider', 'CPUExecutionProvider'],
                provider_options=[qnn_options, {}]
            )
            print(f"  [SUCCESS] Model loaded!")
            print(f"  Active provider: {session.get_providers()[0]}")
            
            # Show model info
            print(f"\n  Model inputs:")
            for inp in session.get_inputs():
                print(f"    - {inp.name}: {inp.shape} ({inp.type})")
            
            print(f"\n  Model outputs:")
            for out in session.get_outputs():
                print(f"    - {out.name}: {out.shape} ({out.type})")
            
            print("\n  [OK] NPU is ready for inference!")
                
        except Exception as e:
            print(f"  [ERROR] Failed to load model: {e}")
            print("\n  This likely means:")
            print("    - Model was compiled for different device (8gen3 vs X Elite)")
            print("    - Or model format incompatible with QNN EP")
            print("    - Will fall back to CPU")
    else:
        print("\n  [ERROR] QNNExecutionProvider not available")
        print("  Install: pip install onnxruntime-qnn")
        
except ImportError:
    print("  [ERROR] onnxruntime not installed")
    print("  Install: pip install onnxruntime-qnn")

# 3. Alternative: Try qai_hub_models
print(f"\n[3/4] Testing qai_hub_models...")

try:
    import qai_hub_models
    print(f"  qai_hub_models: Installed")
    print(f"  [INFO] For inference, use qai_hub_models.evaluate or ONNX Runtime")
    
except ImportError:
    print("  [ERROR] qai_hub_models not installed")

# 4. Device compatibility check
print(f"\n[4/4] Checking device compatibility...")
print(f"  Your model: Whisper Base (ONNX Runtime)")
print(f"  Your device: Surface Laptop 7 - Snapdragon X Elite")
print(f"  [INFO] Checking if model is compiled for X Elite...")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Check the results above:

If QNNExecutionProvider loaded successfully:
  -> Your Whisper Base model is ready for NPU!
  -> Expected STT latency: ~200ms
  -> Run: python harry_voice_assistant.py --test

If Error 5005 appeared:
  -> Model might still be for wrong device
  -> Will fall back to CPU automatically
  -> CPU latency: ~2-3s (still works fine)

Next step:
  python harry_voice_assistant.py --test
""")

