# CRITICAL: Genie Runtime Version Mismatch

## Root Cause Identified ✅

**TWO incompatibilities exist:**

| Component | Model Requires | You Have | Status |
|-----------|---------------|----------|--------|
| QAIRT SDK | 2.37.1.250807093845_124904 | 2.37.1.250807 | ❌ Mismatch |
| **Genie Runtime** | **≥ 1.13** | **1.11.0** | **❌ TOO OLD** |

## The Problem

Your log shows:
```
Using libGenie.so version 1.11.0
```

But AI Hub-generated ctx binaries for Llama 3.2 (X Elite) require:
```
Genie 1.13 or newer
```

## Why This Matters

- Error 30001 → 5005 was progress (SDK version closer)
- But Genie 1.11.0 cannot load binaries compiled for Genie 1.13+
- This explains why error 5005 persists even with SDK 2.37

## Solution Options

### Option 1: Download Newer QAIRT SDK (RECOMMENDED)

You need a QAIRT SDK that includes Genie 1.13 or newer.

**Check available versions:**
- QAIRT 2.38+ likely includes Genie 1.13+
- QAIRT 2.39+ definitely includes Genie 1.13+

**Download:**
1. Visit: https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK
2. Look for version 2.38, 2.39, or newer
3. Check release notes for Genie version
4. Install to: `C:\Qualcomm\AIStack\QAIRT\`

**After installation:**
```powershell
.\fix_qnn_sdk_version.ps1
python run_genie_safe.py "test"
```

### Option 2: Re-export with Current SDK (Fallback)

If you can't get a newer SDK, re-export the model:

```bash
python reexport_model_for_sdk_2_37.py
```

**But note:** This will create binaries for Genie 1.11, which may have limitations or compatibility issues with newer AI Hub features.

### Option 3: Check AI Hub Model Cards

Some AI Hub model cards specify minimum QAIRT versions. Check:
- https://aihub.qualcomm.com/models/llama_v3_2_1b_instruct

Look for "Minimum QAIRT SDK Version" requirements.

## How to Check Genie Version in SDK

```powershell
# Check what Genie version is in a SDK
$sdk = "C:\Qualcomm\AIStack\QAIRT\<version>"
& "$sdk\bin\aarch64-windows-msvc\genie-t2t-run.exe" --version
```

Or check DLL version:
```powershell
$dll = "$sdk\lib\aarch64-windows-msvc\Genie.dll"
(Get-Item $dll).VersionInfo.FileVersion
```

## Current Status

- ✅ SDK 2.37.1.250807 installed
- ❌ Genie 1.11.0 (too old)
- 🎯 Need: Genie 1.13+ (in newer SDK)

## Next Steps

1. **Find SDK with Genie 1.13+:**
   - Try QAIRT 2.38, 2.39, or newer
   - Check QPM for latest versions

2. **Install newer SDK:**
   ```powershell
   # After installation
   .\fix_qnn_sdk_version.ps1
   ```

3. **Test:**
   ```powershell
   python run_genie_safe.py "Hello, my name is Harry Potter"
   ```

## Why This Explains Everything

- **Error 30001** (SDK 2.31): Wrong SDK major version
- **Error 5005** (SDK 2.37): Right SDK, but Genie runtime too old
- **Solution**: Need SDK with both correct version AND Genie 1.13+

