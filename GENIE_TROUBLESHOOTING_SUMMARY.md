# Genie Error 30001 - Complete Troubleshooting Summary

## Current Status

✅ **Fixed Issues:**
- All required DLLs are present
- All model binary files exist
- Config files are present and correctly formatted
- Paths are correctly set (tried both relative and absolute)

❌ **Remaining Issue:**
- Error 30001: "Could not create context from binary for context index = 0"
- This persists even with all files present and correct paths

## Key Findings

### 1. Model Format
- **Format**: Qualcomm AI Hub export format (ctx-bins)
- **Files**: 3 context binaries with AI Hub job-based naming:
  - `job_jp2l424xg_optimized_bin_mq88g90vq.bin` (501 MB)
  - `job_jpek8j87p_optimized_bin_mqko2781n.bin` (238 MB)
  - `job_j5wq8j8z5_optimized_bin_mmxo92pym.bin` (489 MB)

### 2. Configuration
- **Config**: `genie_config.json` correctly references all 3 binaries
- **Tokenizer**: Present and correctly referenced
- **Backend**: QnnHtp with v73 architecture (correct for Snapdragon X Elite)

### 3. QNN SDK Version
- **Installed**: 2.31.0.250130
- **Location**: `C:\Qualcomm\AIStack\QAIRT\2.31.0.250130`
- **Status**: ⚠️ **Version mismatch likely** - Need to verify compilation version

### 4. AI Hub Job IDs
Found 6 unique job IDs from binary filenames:
- `j5wq8j8z5` → https://app.aihub.qualcomm.com/jobs/j5wq8j8z5
- `jp2l424xg` → https://app.aihub.qualcomm.com/jobs/jp2l424xg
- `jpek8j87p` → https://app.aihub.qualcomm.com/jobs/jpek8j87p
- `jp4vmzjqp` → https://app.aihub.qualcomm.com/jobs/jp4vmzjqp
- `jpy6q9nr5` → https://app.aihub.qualcomm.com/jobs/jpy6q9nr5
- `jgzr81wz5` → https://app.aihub.qualcomm.com/jobs/jgzr81wz5

## Root Cause Analysis

Based on the [official tutorial](https://github.com/quic/ai-hub-apps/tree/main/tutorials/llm_on_genie) and error patterns:

**Most Likely Cause: QNN SDK Version Mismatch**

The tutorial explicitly states:
> "We recommend the use of the same version of QAIRT SDK on-target that Qualcomm AI Hub used to compile the assets."

Error 30001 typically indicates:
1. **Version incompatibility** between compilation SDK and runtime SDK
2. **Missing or corrupted binary files** (but we've verified all exist)
3. **Incorrect model format** (but we're using the correct AI Hub export format)

## Solutions

### Solution 1: Check AI Hub Job Pages (CRITICAL)

**Action Required:**
1. Visit the AI Hub job pages listed above
2. Check the "QAIRT Version" or "QNN Version" field in each job
3. Compare with installed version: `2.31.0.250130`

**If versions don't match:**
- Download the matching QAIRT SDK version
- Set `QNN_SDK_ROOT` to the matching version
- OR re-export the model with the current SDK version

### Solution 2: Re-export Model (If Version Mismatch Confirmed)

If the compilation version differs from installed version:

```bash
# Re-export with current SDK version
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export \
    --chipset qualcomm-snapdragon-x-elite \
    --skip-profiling \
    --output-dir genie_bundle_new
```

### Solution 3: Use Official PowerShell Script (After Fixing Config)

The official script expects standard naming. You can either:

**Option A:** Rename files to match template:
- `job_jp2l424xg_optimized_bin_mq88g90vq.bin` → `llama_v3_2_1b_instruct_part_1_of_3.bin`
- `job_jpek8j87p_optimized_bin_mqko2781n.bin` → `llama_v3_2_1b_instruct_part_2_of_3.bin`
- `job_j5wq8j8z5_optimized_bin_mmxo92pym.bin` → `llama_v3_2_1b_instruct_part_3_of_3.bin`

**Option B:** Update the template config to use your actual filenames

### Solution 4: Verify Binary Integrity

Check if binaries are complete and not corrupted:

```powershell
# Verify file sizes match expected ranges
Get-ChildItem genie_bundle\*.bin | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

Expected sizes for Llama 3.2 1B:
- Part 1: ~500 MB
- Part 2: ~500 MB  
- Part 3: ~240 MB

## Diagnostic Tools Created

1. **`diagnose_genie_bundle.py`** - Analyzes bundle structure
2. **`check_genie_version_compatibility.py`** - Checks version compatibility
3. **`fix_genie_config_paths.py`** - Updates config paths
4. **`run_genie_safe.py`** - Safe wrapper with DLL checking

## Next Steps (Priority Order)

1. **IMMEDIATE**: Check AI Hub job pages for QAIRT version
2. **If version mismatch**: Download matching SDK or re-export
3. **If version matches**: Check for other issues (binary integrity, config format)
4. **Last resort**: Re-export model with current SDK

## References

- [Official Tutorial](https://github.com/quic/ai-hub-apps/tree/main/tutorials/llm_on_genie)
- [AI Hub Models](https://github.com/quic/ai-hub-models)
- [QAIRT SDK Download](https://qpm.qualcomm.com/#/main/tools/details/Qualcomm_AI_Runtime_SDK)

## Command to Check Job Versions

You can use the version checker:
```powershell
python check_genie_version_compatibility.py
```

This will show:
- Installed QNN SDK version
- AI Hub job IDs to check
- Recommendations based on findings

