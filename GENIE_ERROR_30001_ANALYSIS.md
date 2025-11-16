# Genie Error 30001 Analysis & Solution

## Current Status

### ✅ What's Working
- DLLs are present (all required Windows DLLs copied successfully)
- All 3 ctx-bins referenced in config exist:
  - `job_jp2l424xg_optimized_bin_mq88g90vq.bin` (501.04 MB)
  - `job_jpek8j87p_optimized_bin_mqko2781n.bin` (237.65 MB)
  - `job_j5wq8j8z5_optimized_bin_mmxo92pym.bin` (489.00 MB)
- Tokenizer exists (`tokenizer.json`)
- Config files exist (`genie_config.json`, `htp_backend_ext_config.json`)
- Genie executable present (`genie-t2t-run.exe`)

### ❌ The Problem
**Error 30001: "Could not create context from binary for context index = 0"**

This error occurs when Genie tries to load the model binaries but fails.

## Root Cause Analysis

Based on your explanation, error 30001 typically means missing:
- `contexts.bin` OR
- `model.hpm` OR  
- `model.dlc`

However, your bundle uses **Qualcomm AI Hub export format** with `ctx-bins` (context binaries), which should be compatible.

### Most Likely Causes:

1. **QNN SDK Version Mismatch** ⚠️ **MOST LIKELY**
   - Model compiled with: Unknown (need to check AI Hub job)
   - QNN SDK installed: `2.31.0.250130`
   - **Solution**: Check AI Hub job page for QAIRT version used, ensure SDK matches

2. **Missing Metadata/Index File**
   - AI Hub exports might need an additional index or metadata file
   - The ctx-bins might need to be in a specific order or format

3. **Path Issues in Config**
   - Paths in `genie_config.json` are relative - might need absolute paths
   - Or paths need to be Windows-style with backslashes

4. **Model Architecture Mismatch**
   - Model compiled for wrong chipset/architecture
   - Should be: Snapdragon X Elite (soc_model: 60, dsp_arch: v73)
   - Current config shows: soc_model: 60, dsp_arch: v73 ✅ (correct)

## Diagnostic Information

### Bundle Structure
```
genie_bundle/
├── genie-t2t-run.exe ✅
├── genie_config.json ✅
├── htp_backend_ext_config.json ✅
├── tokenizer.json ✅
├── job_jp2l424xg_optimized_bin_mq88g90vq.bin ✅ (501 MB)
├── job_jpek8j87p_optimized_bin_mqko2781n.bin ✅ (238 MB)
├── job_j5wq8j8z5_optimized_bin_mmxo92pym.bin ✅ (489 MB)
├── [3 other .bin files - not referenced in config]
└── [DLLs and .so files] ✅
```

### Config Analysis
- **Model type**: `binary` (using ctx-bins)
- **ctx-bins**: 3 files (all exist)
- **Tokenizer**: `tokenizer.json` (exists)
- **Backend**: QnnHtp with v73 architecture ✅

## Solutions to Try

### Solution 1: Check QNN SDK Version Compatibility

**Step 1**: Find the QAIRT version used to compile your model
- Go to Qualcomm AI Hub
- Find the export job that created these binaries
- Check the "QAIRT Version" or "QNN Version" in the job details

**Step 2**: Verify/Update QNN SDK
```powershell
# Check current SDK version
$env:QNN_SDK_ROOT = "C:\Qualcomm\AIStack\QAIRT\2.31.0.250130"
# If model was compiled with different version, download matching SDK
```

### Solution 2: Try Absolute Paths in Config

The config uses relative paths. Try updating to absolute paths:

```python
# Update genie_config.json paths to absolute
import json
from pathlib import Path

bundle_dir = Path("genie_bundle").absolute()
config_path = bundle_dir / "genie_config.json"

with open(config_path, 'r') as f:
    config = json.load(f)

# Update ctx-bins to absolute paths
ctx_bins = config['dialog']['engine']['model']['binary']['ctx-bins']
config['dialog']['engine']['model']['binary']['ctx-bins'] = [
    str(bundle_dir / bin_name) for bin_name in ctx_bins
]

# Update tokenizer path
config['dialog']['tokenizer']['path'] = str(bundle_dir / "tokenizer.json")

# Update extensions path
config['dialog']['engine']['backend']['extensions'] = str(bundle_dir / "htp_backend_ext_config.json")

with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)
```

### Solution 3: Verify Model Export

Check if the export completed successfully:
- Look for any error messages in the export log
- Verify all expected files were created
- Check if model was exported for correct chipset

### Solution 4: Re-export Model (Last Resort)

If version mismatch is confirmed:
```bash
# Re-export with explicit version matching
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \
    --chipset qualcomm-snapdragon-x-elite \
    --skip-profiling \
    --output-dir genie_bundle_new
```

## Next Steps

1. **Check AI Hub Job**: Find the export job and note the QAIRT version
2. **Compare Versions**: Ensure QNN SDK matches compilation version
3. **Try Absolute Paths**: Update genie_config.json with absolute paths
4. **Test Again**: Run `python run_genie_safe.py "test"`

## Files to Check

Please provide:
1. **AI Hub Job Details**: QAIRT version used for compilation
2. **Export Log**: Any warnings/errors from the export process
3. **QNN SDK Version**: Confirm installed version matches compilation version

## Alternative: Use Pre-compiled Genie Models

If compatibility issues persist, consider using pre-compiled Genie models that are guaranteed to work with genie-t2t-run.

