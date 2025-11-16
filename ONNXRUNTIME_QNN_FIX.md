# ONNX Runtime QNN Fix - Corrupted Package Directory

## Problem
Getting error when loading Whisper NPU:
```
ValueError: You're targeting QNN, but have additional onnxruntime packages installed.
```

Even after uninstalling all onnxruntime packages, the error persists.

## Root Cause
A corrupted directory `~nnxruntime` in site-packages is being detected by the verification function. This is likely a remnant from a failed uninstall.

## Solution

### Step 1: Remove corrupted directory
```powershell
Remove-Item -Recurse -Force "C:\Users\hackuser\Miniconda3\Lib\site-packages\~nnxruntime"
```

### Step 2: Remove any existing onnxruntime directories manually
```powershell
Remove-Item -Recurse -Force "C:\Users\hackuser\Miniconda3\Lib\site-packages\onnxruntime" -ErrorAction SilentlyContinue
```

### Step 3: Clean uninstall all onnxruntime packages
```powershell
pip uninstall -y onnxruntime onnxruntime-qnn onnxruntime-gpu
```

### Step 4: Reinstall only onnxruntime-qnn
```powershell
pip install --force-reinstall --no-cache-dir onnxruntime-qnn
```

### Step 5: Verify
```powershell
python -c "from whisper_npu_full import WhisperNPU; model = WhisperNPU(); print('✅ Success')"
```

## Prevention
The `~nnxruntime` directory appears when package uninstallation fails. To prevent:
1. Always use `pip uninstall` instead of manually deleting packages
2. Check for corrupted directories after failed installations:
   ```powershell
   Get-ChildItem "C:\Users\hackuser\Miniconda3\Lib\site-packages" | Where-Object { $_.Name -like "~*" }
   ```

## Status
🔧 **IN PROGRESS**: Removing corrupted directory and reinstalling onnxruntime-qnn

