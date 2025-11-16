# Version Mismatch Solution

## Problem Identified ✅

**Root Cause:** QNN SDK version mismatch causing Error 30001

- **Model compiled with:** QAIRT `2.37.1.250807093845_124904`
- **Currently installed:** QAIRT `2.31.0.250130`
- **AI Hub version:** `aihub-2025.11.03.0`

## Solution

You need to download and install QAIRT SDK version **2.37.1** to match the compilation version.

### Option 1: Download from Qualcomm Package Manager (QPM)

1. **Install QPM** (if not already installed):
   ```powershell
   # Download QPM from: https://qpm.qualcomm.com/
   ```

2. **Install QAIRT SDK 2.37.1**:
   ```powershell
   qpm install qualcomm_ai_runtime_sdk --version 2.37.1
   ```

3. **Install to default location**: `C:\Qualcomm\AIStack\QAIRT\`

### Option 2: Download Directly

1. Visit: https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK
2. Download QAIRT SDK version 2.37.1
3. Extract to: `C:\Qualcomm\AIStack\QAIRT\2.37.1.xxxxx` (version number will be in the folder name)

### After Installation

1. **Run the fix script**:
   ```powershell
   .\fix_qnn_sdk_version.ps1
   ```

   This will:
   - Detect the new SDK version
   - Set `QNN_SDK_ROOT` environment variable
   - Copy matching DLLs to `genie_bundle`
   - Update your system environment

2. **Restart PowerShell** (or set environment variable):
   ```powershell
   $env:QNN_SDK_ROOT = "C:\Qualcomm\AIStack\QAIRT\2.37.1.xxxxx"
   ```

3. **Test Genie**:
   ```powershell
   python run_genie_safe.py "Hello, my name is Harry Potter"
   ```

## Why This Fixes Error 30001

Error 30001 ("Could not create context from binary") occurs when:
- The runtime SDK version doesn't match the compilation SDK version
- Binary format or API changes between versions cause incompatibility
- The model binaries were compiled with a newer SDK than the runtime

By matching the SDK versions, the runtime will be able to properly load and execute the compiled model binaries.

## Verification

After installing the correct SDK version, you should see:
- ✅ Genie loads successfully
- ✅ No Error 30001
- ✅ Model responds to prompts

## Alternative: Re-export Model

If you cannot download SDK 2.37.1, you can re-export the model with your current SDK (2.31.0):

```bash
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \
    --chipset qualcomm-snapdragon-x-elite \
    --skip-profiling \
    --output-dir genie_bundle_new
```

**Note:** This will take 1-2 hours and requires significant memory.

## Files Created

- `fix_qnn_sdk_version.ps1` - Automatically detects and configures matching SDK version
- `check_genie_version_compatibility.py` - Checks version compatibility
- `VERSION_MISMATCH_SOLUTION.md` - This document

