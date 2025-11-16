# Whisper NPU Encoder/Decoder Fix Documentation

## Problem
The NPU Whisper encoder/decoder was failing with the error:
```
qai_hub_models not properly installed: numpy.core.multiarray failed to import
```

This error occurred when trying to load the Whisper models using `qai_hub_models` with the QNN runtime.

## Root Cause
The issue was caused by an incompatible NumPy version. The system had NumPy 2.2.6 installed, but:
1. `qai_hub_models` and related packages require NumPy 1.x (specifically 1.22.0 for Python 3.10)
2. NumPy 2.x has breaking changes that break compatibility with older packages
3. The `numpy.core.multiarray` module structure changed in NumPy 2.x

## Solution

### Step 1: Identify the Required NumPy Version
- TTS library requires: `numpy==1.22.0` for Python 3.10
- `qai_hub_models` and ONNX Runtime work with NumPy 1.x
- Checked package requirements to determine compatible version

### Step 2: Reinstall NumPy 1.22.0
```powershell
conda activate hacknyu_offline
pip install "numpy==1.22.0"
```

This downgrades NumPy from 2.2.6 to 1.22.0, restoring compatibility with:
- `qai_hub_models` (Qualcomm AI Hub Models)
- `onnxruntime-qnn` (QNN Runtime)
- `TTS` (Coqui TTS library)
- Other dependencies that rely on NumPy 1.x

### Step 3: Verify the Fix
Test that the NPU Whisper can now load:
```python
from whisper_npu_full import WhisperNPU
model = WhisperNPU()
# Should load successfully without numpy.core.multiarray errors
```

## Technical Details

### Why NumPy 2.x Breaks Things
1. **Module Structure Changes**: NumPy 2.0 removed `numpy.core.multiarray` as a public API
2. **C API Changes**: Many compiled extensions (like ONNX Runtime, PyTorch) were built against NumPy 1.x C API
3. **Import Path Changes**: Internal module paths changed, breaking dynamic imports

### Compatible Versions
- **NumPy**: 1.22.0 (required by TTS for Python 3.10)
- **ONNX Runtime**: Works with NumPy 1.19.0 - 1.26.x
- **PyTorch**: Compatible with NumPy 1.19.0+
- **qai_hub_models**: Requires NumPy 1.x

## Files Affected
- `whisper_npu_full.py`: NPU Whisper implementation using `HfWhisperApp`
- `harry_voice_assistant.py`: Main voice assistant that initializes Whisper

## Prevention
To avoid this issue in the future:
1. **Pin NumPy version** in `requirements.txt`:
   ```
   numpy==1.22.0
   ```
2. **Check compatibility** before upgrading NumPy
3. **Test NPU components** after any NumPy changes

## Verification Commands
```powershell
# Check NumPy version
python -c "import numpy; print(numpy.__version__)"

# Test qai_hub_models import
python -c "from qai_hub_models.models._shared.hf_whisper.app import HfWhisperApp; print('OK')"

# Test NPU Whisper loading
python -c "from whisper_npu_full import WhisperNPU; model = WhisperNPU(); print('OK')"
```

## Status
✅ **FIXED**: NumPy 1.22.0 installed, NPU Whisper should now load correctly

