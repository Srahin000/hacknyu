# Quick Fix Guide - Genie Error 30001

## ✅ Problem Identified

**Version Mismatch:**
- Model compiled with: **QAIRT 2.37.1**
- Your SDK: **QAIRT 2.31.0.250130**
- **Result:** Error 30001 - Binaries incompatible

## 🎯 Solution Options

### Option 1: Download Matching SDK (Recommended)

**Step 1:** Download QAIRT SDK 2.37.1
- **QPM Website:** https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK
- **Or use QPM CLI:** `qpm install qualcomm_ai_runtime_sdk --version 2.37.1`
- **Install location:** `C:\Qualcomm\AIStack\QAIRT\`

**Step 2:** Run the fix script
```powershell
.\fix_qnn_sdk_version.ps1
```

**Step 3:** Test Genie
```powershell
python run_genie_safe.py "Hello, my name is Harry Potter"
```

### Option 2: Re-export Model with Current SDK

If you can't download SDK 2.37.1, re-export the model with your current SDK (2.31.0):

```bash
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \
    --chipset qualcomm-snapdragon-x-elite \
    --skip-profiling \
    --output-dir genie_bundle_v2_31
```

**Note:** 
- Takes 1-2 hours
- Requires ~20GB memory (including swap)
- Will create new binaries compatible with SDK 2.31.0

## 📋 Current Status

✅ **Fixed:**
- All DLLs present
- All model files exist
- Config files correct
- Paths configured

❌ **Remaining Issue:**
- SDK version mismatch (2.31.0 vs 2.37.1)

## 🔍 Verification

After installing SDK 2.37.1, verify:
```powershell
# Check if SDK is detected
.\fix_qnn_sdk_version.ps1

# Should show:
# ✅ Found matching version: 2.37.1.xxxxx
# ✅ DLLs copied successfully
```

## 📚 Reference

- [Official Tutorial](https://github.com/quic/ai-hub-apps/tree/main/tutorials/llm_on_genie)
- [QAIRT SDK Download](https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK)
- [QPM Installation Guide](https://docs.qualcomm.com/bundle/publicresource/topics/80-88500-5/install_qualcomm_package_manager_qpm.html)

