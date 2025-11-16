# Dia-1.6B Environment Setup Guide

## ⚠️ Dependency Conflicts Warning

Dia-1.6B has dependency conflicts with the current voice assistant environment:

| Package | Dia Requires | Current Needs | Conflict |
|---------|--------------|---------------|----------|
| numpy | 2.2.6 | 1.22.0 (TTS) | ❌ Breaks TTS |
| protobuf | 3.19.6 | >=3.20.2 (qai-hub) | ❌ Breaks qai-hub |
| torch | 2.6.0 | 2.4.1 (torchvision) | ⚠️ Minor |

## Recommended: Separate Environment

Create a separate conda environment for Dia testing:

```powershell
# Create new environment for Dia
conda create -n dia_test python=3.10 -y
conda activate dia_test

# Install Dia
pip install git+https://github.com/nari-labs/dia.git

# Test Dia
python test_dia_local.py
```

## Alternative: Fix Conflicts (Risky)

If you want to use Dia in the same environment, you'll need to:

1. **Accept breaking TTS**: Dia's numpy 2.2.6 will break XTTS v2
2. **Fix protobuf**: Upgrade to >=3.20.2 (may break Dia)
3. **Accept torch mismatch**: torchvision may not work

**Not recommended** - will break existing voice assistant setup.

## Current Status

- ✅ Dia package installed
- ✅ Can import `from dia.model import Dia`
- ⚠️ Dependency conflicts present
- ❌ Will break XTTS v2 (numpy conflict)
- ❌ May break qai-hub (protobuf conflict)

## Recommendation

**For NPU deployment**: Stick with XTTS v2 (current setup) which:
- Works with current dependencies
- Works on CPU (no GPU required)
- Has pyttsx3 fallback
- Is already integrated

**For Dia testing**: Use separate environment to avoid breaking existing setup.

