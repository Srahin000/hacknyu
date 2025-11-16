# Re-export Solution for Error 5005

## Problem

Error 5005 indicates binary format incompatibility between compilation and runtime SDK versions:
- **Model compiled with:** 2.37.1.250807093845_124904
- **Your SDK:** 2.37.1.250807
- **Issue:** Even minor sub-version differences can cause incompatibility

## Solution: Re-export Model

Re-exporting the model with your current SDK ensures 100% compatibility.

### Option 1: Automated Script

```bash
python reexport_model_for_sdk_2_37.py
```

This script will:
- Check requirements
- Export Llama 3.2 1B for your exact SDK version
- Log progress
- Take 1-2 hours

### Option 2: Manual Export

```bash
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \
    --chipset qualcomm-snapdragon-x-elite \
    --skip-profiling \
    --output-dir genie_bundle_v2_37
```

## After Export

1. **Backup old bundle:**
   ```powershell
   Rename-Item genie_bundle genie_bundle_old
   ```

2. **Use new bundle:**
   ```powershell
   Rename-Item genie_bundle_v2_37 genie_bundle
   ```

3. **Test Genie:**
   ```powershell
   python run_genie_safe.py "Hello, my name is Harry Potter"
   ```

## Why This Works

- Creates binaries with your exact SDK version (2.37.1.250807)
- Eliminates any sub-version compatibility issues
- Guaranteed to work with your runtime environment

## Requirements

- QAIRT SDK 2.37.1.250807 (already installed ✅)
- qai-hub-models Python package
- QAI Hub API key (optional, for direct download)
- ~20GB memory (RAM + swap)
- 1-2 hours time

## Status

Your SDK is correctly set to 2.37. The only remaining step is re-exporting the model binaries.

