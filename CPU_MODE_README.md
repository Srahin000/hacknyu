# CPU Mode Testing Guide

## Overview

CPU mode allows you to test the complete voice assistant pipeline (Wake Word → Whisper → LLM → TTS) using CPU instead of NPU, perfect for testing while NPU Genie downloads in the background.

## Pipeline Flow (CPU Mode)

1. **Wake Word Detection** (Picovoice) - "Harry Potter"
2. **Speech-to-Text** (Whisper CPU) - Uses existing Whisper Base encoder/decoder ONNX models on CPU
3. **LLM Response** (CPU) - Uses llama.cpp with GGUF model
4. **Text-to-Speech** (pyttsx3) - Offline TTS

## Installation

### Required Dependencies

```powershell
# All dependencies should already be installed:
# - pvporcupine (wake word)
# - llama-cpp-python (CPU LLM)
# - pyttsx3 (TTS)
# - sounddevice (audio capture)
# - onnxruntime (for ONNX models)
# - librosa (for audio preprocessing)
# - tiktoken (for token decoding)

# Make sure you have the Whisper Base models:
# - models/whisper_base2/model.onnx (encoder)
# - models/whisper_base/model.onnx (decoder)
```

## Usage

### Test Mode (Recommended for first run)

Skip wake word detection, use ENTER key to trigger recording:

```powershell
python harry_voice_assistant.py --test --cpu
```

### Full Mode with Wake Word

Listen for "Harry Potter" wake word:

```powershell
python harry_voice_assistant.py --cpu
```

## What CPU Mode Does

- **Whisper**: Uses the same Whisper Base encoder/decoder ONNX models you built, but runs on CPU instead of NPU
- **LLM**: Uses `llama.cpp` with GGUF model (CPU, ~1-2s latency)
- **Skips NPU**: Does not attempt to load NPU Genie or use QNNExecutionProvider for Whisper

## Performance Expectations

- **Wake Word**: ~10-50ms (same as NPU mode)
- **Whisper STT**: ~500-2000ms (CPU, depends on audio length)
- **LLM Response**: ~1000-2000ms (CPU, depends on response length)
- **TTS**: ~100-500ms (same as NPU mode)

## Troubleshooting

### "Encoder/Decoder model not found"
Make sure you have:
- `models/whisper_base2/model.onnx` (encoder)
- `models/whisper_base/model.onnx` (decoder)

These are the same models used for NPU Whisper, just running on CPU.

### "GGUF model not found"
Make sure `models/Llama-3.2-1B-Instruct-Q4_K_M.gguf` exists.

### "Wake word file not found"
Make sure `ppn_files/Harry-Potter_en_windows_v3_0_0.ppn` exists.

## Notes

- CPU mode is perfect for testing the pipeline while NPU Genie downloads
- Uses the same Whisper encoder/decoder models, just on CPU instead of NPU
- Once NPU Genie is ready, remove `--cpu` flag to use NPU acceleration for both Whisper and LLM
- CPU Whisper will be slower than NPU but uses the exact same models
- All processing happens locally, 100% offline

