# Dia-1.6B NPU Deployment Guide

## Overview

[Dia-1.6B](https://huggingface.co/nari-labs/Dia-1.6B) is a 1.6B parameter text-to-speech model that generates realistic dialogue. This guide covers deploying it to Qualcomm NPU.

## Model Information

- **Parameters**: 1.6B
- **VRAM Required**: ~10GB (GPU)
- **Current Support**: GPU only (CUDA 12.6, PyTorch 2.0+)
- **CPU Support**: Coming soon
- **License**: Apache 2.0

## Features

- ✅ Dialogue generation with `[S1]` and `[S2]` tags
- ✅ Non-verbal sounds: `(laughs)`, `(coughs)`, `(sighs)`, etc.
- ✅ Voice cloning support
- ✅ Emotion and tone control

## ⚠️ Dependency Conflicts

**IMPORTANT**: Installing Dia causes dependency conflicts with existing packages:

- **numpy**: Dia requires 2.2.6, but TTS needs 1.22.0
- **protobuf**: Dia requires 3.19.6, but qai-hub needs >=3.20.2
- **torch**: Dia requires 2.6.0, but torchvision needs 2.4.1

**Solutions**:
1. **Use separate environment** for Dia testing (recommended)
2. **Fix conflicts** (may break existing TTS/Whisper setup)
3. **Use Dia only** if you're willing to replace XTTS v2

## Challenges for NPU Deployment

1. **Model Size**: 1.6B parameters (~10GB) may exceed NPU memory
2. **Architecture**: Complex multi-component model (encoder + decoder + vocoder)
3. **Quantization**: Likely required for NPU deployment
4. **ONNX Conversion**: May need custom export logic
5. **GPU-Only**: Currently requires GPU for inference
6. **Dependency Conflicts**: Incompatible with current environment setup

## Deployment Steps

### Step 1: Test Locally

```powershell
conda activate hacknyu_offline
python test_dia_local.py
```

This will:
- Install Dia package (if needed)
- Load the model
- Generate test audio files
- Save outputs to `dia_test_outputs/`

### Step 2: Export to ONNX

```powershell
python export_dia_npu.py
```

**Note**: Direct ONNX export may be challenging due to:
- Complex model architecture
- Custom operations
- Multiple components (encoder, decoder, vocoder)

**Alternative approaches**:
1. Use `torch.onnx.export()`` with proper input/output specs
2. Export components separately (encoder, decoder, vocoder)
3. Use Qualcomm's model export utilities
4. Convert via TorchScript intermediate format

### Step 3: Deploy to NPU

```powershell
python export_dia_npu.py
# Select option 2: Deploy to NPU
```

**Requirements**:
- ONNX model file
- Qualcomm AI Hub API key
- Target device (e.g., Snapdragon X Elite)
- Input/output specifications

## Recommended Approach

Given the complexity, consider:

1. **Start with smaller TTS models** that are already NPU-compatible
2. **Use XTTS v2** (current implementation) which works well
3. **Wait for Dia quantization** or smaller variants
4. **Use GPU locally** for Dia if you have the hardware

## Alternative: Use Dia Locally with GPU

If you have GPU access, you can use Dia locally:

```python
from dia.model import Dia
import soundfile as sf

model = Dia.from_pretrained("nari-labs/Dia-1.6B")
text = "[S1] I solemnly swear that I am up to no good. [S2] That's amazing!"
output = model.generate(text)
sf.write("output.mp3", output, 44100)
```

Then integrate with your voice assistant pipeline.

## Resources

- [Dia-1.6B on Hugging Face](https://huggingface.co/nari-labs/Dia-1.6B)
- [Dia GitHub Repository](https://github.com/nari-labs/dia)
- [Qualcomm AI Hub](https://app.aihub.qualcomm.com/)
- [Qualcomm AI Hub Documentation](https://app.aihub.qualcomm.com/docs/)

## Status

⚠️ **NPU deployment is experimental** - Dia-1.6B was not designed for NPU deployment. The model may require:
- Significant quantization
- Architecture modifications
- Custom ONNX export logic
- Memory optimization

Consider using XTTS v2 (current implementation) which is more suitable for CPU/GPU deployment.

