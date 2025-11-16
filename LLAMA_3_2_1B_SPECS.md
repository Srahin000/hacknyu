# Llama 3.2 1B Instruct - Harry Potter NPU Model

## 📊 Model Specifications

**Model:** Llama 3.2 1B Instruct  
**Source:** https://aihub.qualcomm.com/models/llama_v3_2_1b_instruct  
**Quantization:** Pre-quantized to w4 (4-bit) and w8 (8-bit) weights  
**Status:** ✅ Production-ready for on-device deployment

---

## ⚡ Performance on Snapdragon X Elite

**Expected Latency:**
- Time to first token: ~100-200ms (prompt processing)
- Time per additional token: ~50-100ms (token generation)
- **Total for short response (5-10 tokens): ~500ms-1s**

**Memory Requirements:**
- Model size: ~1-2GB (quantized)
- Runtime memory: ~3-4GB
- Your device: ✅ Has 12GB+ (plenty!)

---

## 🔧 Requirements

**Python Version:** 3.10 to 3.13
- ✅ Your `hacknyu_offline` environment: Python 3.10 (perfect!)

**QAIRT SDK:** v2.29.0+
- ⚠️ Need to download: https://softwarecenter.qualcomm.com/catalog/item/Qualcomm_AI_Runtime_Community

**Device:** Snapdragon X Elite
- ✅ Your device matches!

---

## 🚀 Quick Start

### Step 1: Install Dependencies (5 min)

```powershell
conda activate hacknyu_offline
pip install "qai-hub-models[llama-v3-2-1b-instruct]"
```

**Note:** GPU not required for export! (but 2-3 hours of time is)

---

### Step 2: Get Hugging Face Access (5 min)

**Required for Llama models:**

1. Create free Hugging Face account: https://huggingface.co/join
2. Accept Llama 3.2 license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
3. Login via CLI:
   ```bash
   pip install -U "huggingface_hub[cli]"
   huggingface-cli login
   ```

---

### Step 3: Export Model (2-3 hours, automated)

**Option A - Use batch file:**
```powershell
start_export.bat
```

**Option B - Manual command:**
```powershell
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export --chipset qualcomm-snapdragon-x-elite --skip-profiling --output-dir harry_genie_bundle
```

**What happens:**
- Downloads Llama 3.2 1B weights from Hugging Face
- Compiles for Snapdragon X Elite NPU
- Exports to `harry_genie_bundle` folder
- Creates `genie_config.json` and all required files

**Time:** 2-3 hours (let it run, minimize window)

---

### Step 4: Chat with Harry! (After export)

```powershell
python harry_npu_genie.py
```

**Expected:**
- Response time: ~500ms-1s
- Running on: NPU (Snapdragon X Elite)
- Quality: Much better than TinyLlama!

---

## 📁 What Gets Created

After export completes, you'll have:

```
harry_genie_bundle/
├── genie_config.json           # Genie runtime configuration
├── Llama-3-2-1B-Instruct-PromptProcessor-Quantized.bin
├── Llama-3-2-1B-Instruct-TokenGenerator-Quantized.bin
├── tokenizer.json              # Tokenizer
└── ... (other files)
```

---

## 🎯 Why This Model?

| Feature | Llama 3.2 1B | TinyLlama 1.1B (CPU) |
|---------|--------------|----------------------|
| **Latency** | ~500ms (NPU) | ~6-7s (CPU) |
| **Quality** | State-of-the-art | Basic |
| **Hardware** | NPU-optimized | CPU only |
| **Quantization** | Pre-quantized (4/8-bit) | FP32 |
| **Size** | ~1-2GB | ~4GB |
| **Speed vs Quality** | Best balance | Slow + basic |

**Winner:** Llama 3.2 1B on NPU! 🏆

---

## ⚠️ Troubleshooting

### "Need Hugging Face token"
```bash
pip install -U "huggingface_hub[cli]"
huggingface-cli login
```
Accept Llama license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct

### "QAIRT SDK not found"
- Download: https://softwarecenter.qualcomm.com/catalog/item/Qualcomm_AI_Runtime_Community
- Set environment variables (see tutorial)

### "Export takes forever"
- Normal! 2-3 hours is expected
- Requires significant memory (16GB+ RAM recommended)
- Let it run overnight if needed

### "Out of memory during export"
- Close other programs
- Use `--context-length 1024` for smaller context (faster, less memory)

---

## 🎬 Demo Before Export

Want to test the model on CPU first?

```bash
python -m qai_hub_models.models.llama_v3_2_1b_instruct.demo
```

This runs on CPU (slower) but lets you verify:
- Model downloads correctly
- Hugging Face access works
- Model quality is good

---

## 📚 Official Resources

- **Model Card:** https://aihub.qualcomm.com/models/llama_v3_2_1b_instruct
- **Tutorial:** https://github.com/quic/ai-hub-apps/tree/main/tutorials/llm_on_genie
- **Source:** https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- **Qualcomm AI Hub:** https://aihub.qualcomm.com/

---

## ✅ Checklist

Before starting export:

- [ ] Python 3.10 environment (`hacknyu_offline`)
- [ ] Hugging Face account created
- [ ] Llama 3.2 license accepted
- [ ] `huggingface-cli login` completed
- [ ] Dependencies installed: `pip install "qai-hub-models[llama-v3-2-1b-instruct]"`
- [ ] 16GB+ RAM available
- [ ] 2-3 hours of time available

After export:

- [ ] QAIRT SDK downloaded and installed
- [ ] Environment variables set (`$env:QAIRT_HOME`, etc.)
- [ ] `harry_genie_bundle` folder exists
- [ ] Run `python harry_npu_genie.py`
- [ ] Enjoy fast Harry responses! 🚀

---

## 🎯 Next Steps

**Right now:**
1. Create Hugging Face account
2. Accept Llama 3.2 license
3. Run `start_export.bat`
4. Go get coffee ☕ (it'll take 2-3 hours)

**After export:**
1. Download QAIRT SDK
2. Configure environment
3. Chat with Harry at NPU speed!

This is the production-ready solution! 🎉

