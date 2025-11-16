# Model Setup Instructions

This project requires large model files that are **not stored in Git** due to size limitations.

## 📦 Required Models

### 1. Llama 3.2 1B Instruct (GGUF) - 770 MB

**What it does:** Harry Potter personality AI (LLM for text generation)

**Download from:** https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF

**File:** `Llama-3.2-1B-Instruct-Q4_K_M.gguf`

**Save to:** `models/Llama-3.2-1B-Instruct-Q4_K_M.gguf`

```powershell
# Quick download with wget or curl
curl -L -o models/Llama-3.2-1B-Instruct-Q4_K_M.gguf https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

---

### 2. Whisper Base Models (NPU) - ~290 MB total

**What it does:** Speech-to-text on Qualcomm Snapdragon X Elite NPU

**Method 1: Export from Qualcomm AI Hub** (Recommended)

```powershell
# Export Whisper models for Snapdragon X Elite
python -m qai_hub_models.models.whisper_base.export --target-runtime precompiled_qnn_onnx --device "Snapdragon X Elite CRD"

# Extract and organize files
Expand-Archive -Path .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\Whisper-Base_HfWhisperEncoder_float.onnx.zip -DestinationPath .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite

mv .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\job*optimized_onnx .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\HfWhisperEncoder

Expand-Archive -Path .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\Whisper-Base_HfWhisperDecoder_float.onnx.zip -DestinationPath .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite

mv .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\job*optimized_onnx .\build\whisper_base_float\precompiled\qualcomm-snapdragon-x-elite\HfWhisperDecoder
```

**Method 2: CPU Fallback** (No download needed)

The project automatically falls back to CPU-based OpenAI Whisper if NPU models aren't available:

```powershell
pip install openai-whisper
```

---

### 3. Genie Bundle (NPU Runtime) - Optional

**What it does:** Qualcomm Genie runtime for LLM inference on NPU

**Required for:** Running Llama on NPU (currently uses CPU fallback)

**Setup:**
```powershell
python setup_genie_bundle.py
```

This downloads and extracts the Genie runtime to `genie_bundle/`.

---

## 🚀 Quick Start

### Option A: CPU Mode (Easiest)

Use CPU for everything while testing:

```powershell
# Install CPU Whisper
pip install openai-whisper

# Run in CPU mode
python harry_voice_assistant.py --cpu
```

### Option B: NPU Mode (Best Performance)

Download models and run on NPU:

1. Download Llama GGUF (see above)
2. Export Whisper NPU models (see above)
3. Run normally:

```powershell
python harry_voice_assistant.py
```

---

## 📂 Expected Directory Structure

```
models/
├── Llama-3.2-1B-Instruct-Q4_K_M.gguf         # 770 MB
├── whisper_base-hfwhisperencoder-qualcomm_snapdragon_x_elite.bin  # 145 MB
├── whisper_base-hfwhisperdecoder-qualcomm_snapdragon_x_elite.bin  # 145 MB
└── ...

build/
└── whisper_base_float/
    └── precompiled/
        └── qualcomm-snapdragon-x-elite/
            ├── HfWhisperEncoder/
            │   └── model.onnx
            └── HfWhisperDecoder/
                └── model.onnx

genie_bundle/                                  # Optional - for NPU LLM
├── genie-t2t-run.exe
├── genie_config.json
└── ...
```

---

## ❓ Troubleshooting

**Q: Why aren't models in the repository?**
- GitHub has a 100 MB file size limit
- These models are 145-770 MB each
- Users must download them separately

**Q: Can I use smaller models?**
- Yes! For Llama, try Q3 or Q2 quantizations (smaller but lower quality)
- For Whisper, use `whisper-tiny` (39 MB) or `whisper-small` (244 MB)

**Q: Do I need NPU models?**
- No! CPU mode works fine for testing
- NPU provides better performance but requires more setup

---

## 📝 Notes

- All model files are in `.gitignore` to keep the repository small
- Models are downloaded/cached locally on each developer's machine
- For production deployment, consider hosting models separately (S3, etc.)

