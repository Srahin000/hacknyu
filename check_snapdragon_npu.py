"""
Comprehensive Snapdragon NPU Diagnostic Tool

Checks:
1. Hardware (Snapdragon X Elite/Plus)
2. Windows version and updates
3. NPU drivers
4. ONNX Runtime QNN support
5. Model compatibility
"""

import sys
import platform
import subprocess
import os
from pathlib import Path

print("="*70)
print(" SNAPDRAGON NPU DIAGNOSTIC ".center(70))
print("="*70)

# 1. Check Hardware & OS
print("\n[1/6] Hardware & OS Check")
print("-"*70)

print(f"  OS: {platform.system()} {platform.release()}")
print(f"  Version: {platform.version()}")
print(f"  Machine: {platform.machine()}")
print(f"  Processor: {platform.processor()}")

is_arm64 = platform.machine().lower() in ['arm64', 'aarch64']
is_windows = platform.system() == "Windows"

if is_arm64:
    print("  [OK] ARM64 architecture detected")
else:
    print(f"  [WARNING] Not ARM64 (detected: {platform.machine()})")
    print("           Snapdragon X Elite/Plus requires ARM64")

if is_windows:
    print("  [OK] Windows detected")
    
    # Check Windows version
    try:
        result = subprocess.run(
            ["wmic", "os", "get", "Caption,Version"],
            capture_output=True,
            text=True
        )
        print(f"  Windows Info:\n{result.stdout}")
    except:
        pass
else:
    print("  [ERROR] Not Windows - QNN EP requires Windows 11")

# 2. Check for Snapdragon NPU
print("\n[2/6] Snapdragon NPU Detection")
print("-"*70)

try:
    # Check CPU info
    result = subprocess.run(
        ["wmic", "cpu", "get", "Name,Description"],
        capture_output=True,
        text=True
    )
    cpu_info = result.stdout
    print(f"  CPU Info:\n{cpu_info}")
    
    if "snapdragon" in cpu_info.lower() or "qualcomm" in cpu_info.lower():
        print("  [OK] Snapdragon processor detected")
    else:
        print("  [WARNING] Snapdragon keyword not found in CPU info")
        print("            Check Device Manager for Hexagon/NPU device")
        
except Exception as e:
    print(f"  [ERROR] Could not query CPU: {e}")

# Check for NPU/Hexagon in Device Manager
print("\n  Checking for NPU drivers...")
try:
    result = subprocess.run(
        ["pnputil", "/enum-devices", "/connected"],
        capture_output=True,
        text=True
    )
    devices = result.stdout.lower()
    
    npu_keywords = ['npu', 'hexagon', 'qnn', 'dsp', 'qualcomm']
    found_npu = any(keyword in devices for keyword in npu_keywords)
    
    if found_npu:
        print("  [OK] NPU-related device found")
    else:
        print("  [WARNING] No NPU device found in connected devices")
        
except Exception as e:
    print(f"  [INFO] Could not enumerate devices: {e}")

# 3. Check ONNX Runtime
print("\n[3/6] ONNX Runtime Check")
print("-"*70)

try:
    import onnxruntime as ort
    print(f"  ONNX Runtime version: {ort.__version__}")
    print(f"  Available providers: {ort.get_available_providers()}")
    
    if 'QNNExecutionProvider' in ort.get_available_providers():
        print("  [SUCCESS] QNNExecutionProvider is AVAILABLE!")
    else:
        print("  [ERROR] QNNExecutionProvider NOT available")
        print("\n  To fix, try:")
        print("    pip uninstall onnxruntime")
        print("    pip install onnxruntime-qnn")
        print("\n  Or use nightly build:")
        print("    pip install ort-nightly-qnn --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ort-qnn-nightly/pypi/simple/")
        
except ImportError:
    print("  [ERROR] onnxruntime not installed")
    print("  Install: pip install onnxruntime-qnn")

# 4. Check QNN DLLs
print("\n[4/6] QNN DLL Check")
print("-"*70)

# Check common locations
qnn_locations = [
    "C:\\Qualcomm\\AIStack\\QAIRT\\2.31.0.250130\\lib\\aarch64-windows-msvc",
    "C:\\Program Files\\Qualcomm\\AIStack",
    os.environ.get('QNN_SDK_ROOT', ''),
]

qnn_dll_found = False
for location in qnn_locations:
    if location and Path(location).exists():
        dll_path = Path(location)
        qnn_dlls = list(dll_path.glob("Qnn*.dll"))
        if qnn_dlls:
            print(f"  [OK] Found QNN DLLs at: {location}")
            print(f"       Count: {len(qnn_dlls)} DLLs")
            qnn_dll_found = True
            
            # Check specifically for QnnHtp.dll (NPU backend)
            if (dll_path / "QnnHtp.dll").exists():
                print(f"  [OK] QnnHtp.dll found (Hexagon/NPU backend)")
            break

if not qnn_dll_found:
    print("  [WARNING] QNN DLLs not found")
    print("            Install QAIRT SDK from:")
    print("            https://qpm.qualcomm.com/#/main/tools/details/qualcomm_ai_engine_direct")

# 5. Check NPU Driver Version
print("\n[5/6] NPU Driver Version Check")
print("-"*70)

print("  Checking for NPU drivers (minimum: 30.0.140.0)...")
try:
    result = subprocess.run(
        ["driverquery", "/v"],
        capture_output=True,
        text=True
    )
    
    # Look for Qualcomm/NPU drivers
    lines = result.stdout.split('\n')
    npu_drivers = [line for line in lines if any(kw in line.lower() for kw in ['qualcomm', 'npu', 'hexagon', 'qnn'])]
    
    if npu_drivers:
        print("  [OK] Found NPU-related drivers:")
        for driver in npu_drivers[:5]:  # Show first 5
            print(f"       {driver.strip()}")
    else:
        print("  [WARNING] No NPU drivers found")
        print("            Update Windows and OEM drivers from:")
        print("            - Windows Update")
        print("            - Device manufacturer's support site")
        
except Exception as e:
    print(f"  [INFO] Could not query drivers: {e}")

# 6. Test Model Loading
print("\n[6/6] Model Compatibility Test")
print("-"*70)

model_path = Path("models/whisper_small_quantized-whispersmalldecoderquantizable-qualcomm_snapdragon_8gen3.onnx")
model_onnx = model_path / "job_jgjeez7e5_optimized_onnx" / "model.onnx"

if model_onnx.exists():
    print(f"  [OK] Model found: {model_onnx}")
    print(f"       Size: {model_onnx.stat().st_size / 1024 / 1024:.1f} MB")
    
    try:
        import onnxruntime as ort
        
        if 'QNNExecutionProvider' in ort.get_available_providers():
            print("\n  Testing model load with QNN...")
            try:
                sess_options = ort.SessionOptions()
                # Disable CPU fallback to force QNN usage
                sess_options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
                
                session = ort.InferenceSession(
                    str(model_onnx),
                    sess_options=sess_options,
                    providers=["QNNExecutionProvider"],
                    provider_options=[{"backend_path": "QnnHtp.dll"}]
                )
                
                print(f"  [SUCCESS] Model loaded with QNN!")
                print(f"  Active provider: {session.get_providers()[0]}")
                
            except Exception as e:
                print(f"  [ERROR] Model load failed: {e}")
                print("          Possible reasons:")
                print("          - Model not compatible with QNN")
                print("          - QnnHtp.dll not found")
                print("          - NPU firmware/driver issue")
        else:
            print("  [SKIP] QNNExecutionProvider not available")
            
    except ImportError:
        print("  [SKIP] onnxruntime not installed")
else:
    print(f"  [INFO] Model not found at: {model_onnx}")

# Summary & Recommendations
print("\n" + "="*70)
print(" SUMMARY & RECOMMENDATIONS ".center(70))
print("="*70)

print("""
Based on the checks above, here's what you need:

REQUIRED:
 [1] ARM64 Windows 11 (latest updates)
 [2] Snapdragon X Elite/Plus with Hexagon NPU
 [3] NPU drivers (version 30.0.140.0+)
 [4] ONNX Runtime with QNNExecutionProvider
 [5] QNN SDK (QAIRT) DLLs
 [6] Compatible quantized model

INSTALLATION COMMANDS:

If QNNExecutionProvider is missing:
  pip uninstall onnxruntime
  pip install onnxruntime-qnn

Or try nightly build:
  pip install ort-nightly-qnn --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ort-qnn-nightly/pypi/simple/

KNOWN ISSUES:
- QNN EP on Windows ARM64 is VERY new (2024-2025)
- Many users report it doesn't work yet on Snapdragon X Elite
- Driver/firmware may not expose NPU for general use
- OEM may restrict NPU to specific apps only

IF NPU DOESN'T WORK:
Use CPU Whisper (works great, ~2-3s latency):
  pip install openai-whisper
  python harry_voice_assistant.py --test

NEXT STEPS:
1. Run: pip install onnxruntime-qnn
2. Run this script again
3. If QNNExecutionProvider appears -> test model loading
4. If not -> use CPU Whisper for now
""")

print("="*70)
