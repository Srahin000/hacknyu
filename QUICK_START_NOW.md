# Test Harry NOW (While NPU Export Runs)

## 🎯 Two-Track Approach

**Track 1: Fast CPU Version (Ready in 10 minutes)**
- Uses llama.cpp with GGUF quantization
- ~1-2s response time (vs 6-7s with TinyLlama!)
- Test Harry's personality immediately

**Track 2: NPU Version (Ready in 3 hours)**
- Official Qualcomm export (already set up)
- ~500ms response time
- Production-ready

---

## 🚀 Track 1: Test Harry NOW (10 minutes)

### Step 1: Install llama-cpp-python

```powershell
conda activate hacknyu_offline

# Install with CPU support (fast precompiled wheels)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

---

### Step 2: Download GGUF Model

**Go to:** https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/tree/main

**Download file:** `Llama-3.2-1B-Instruct-Q4_K_M.gguf`
- Size: ~700MB
- Click filename → "Download" button

**Save to:** `C:\Users\hackuser\Documents\HackNYU\`

---

### Step 3: Chat with Harry!

```powershell
python harry_llama_cpp.py
```

**Expected:**
- Response time: ~1-2s (much better than 6-7s!)
- Runs on CPU (optimized with llama.cpp)
- Same Harry personality
- Test immediately!

---

## ⚡ Track 2: NPU Version (Start in parallel)

While testing the CPU version, start the NPU export:

### Step 1: Hugging Face Access

```powershell
# Get access to Llama 3.2
# 1. Go to: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
# 2. Click "Agree and access repository"
# 3. Get token: https://huggingface.co/settings/tokens

# Login
pip install -U "huggingface_hub[cli]"
huggingface-cli login
```

---

### Step 2: Start Export (Runs for 2-3 hours)

```powershell
# Automated script
start_export.bat

# Or manual
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export --chipset qualcomm-snapdragon-x-elite --skip-profiling --output-dir harry_genie_bundle
```

**Let this run!** Minimize the window and test the CPU version meanwhile.

---

### Step 3: After Export (in ~3 hours)

1. **Install QAIRT SDK:** https://softwarecenter.qualcomm.com/catalog/item/Qualcomm_AI_Runtime_Community
2. **Set environment variables** (see `HARRY_NPU_SIMPLE_SETUP.md`)
3. **Run NPU version:**
   ```powershell
   python harry_npu_genie.py
   ```

**Result:** ~500ms responses! 🚀

---

## 📊 Performance Comparison

| Version | Hardware | Latency | Setup Time |
|---------|----------|---------|------------|
| **TinyLlama (old)** | CPU | 6-7s | 5 min |
| **Llama.cpp (Track 1)** | CPU | 1-2s | 10 min |
| **Genie NPU (Track 2)** | NPU | ~500ms | 3 hours |

---

## 🎯 What to Do Right Now

### Immediate (10 min):
```powershell
# 1. Install llama-cpp
conda activate hacknyu_offline
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 2. Download GGUF
# → https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF
# → Save: Llama-3.2-1B-Instruct-Q4_K_M.gguf

# 3. Test!
python harry_llama_cpp.py
```

### In Parallel (2-3 hours):
```powershell
# 1. Get Hugging Face access
# → https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct

# 2. Login
huggingface-cli login

# 3. Start export (then minimize)
start_export.bat
```

---

## 🎬 Timeline

**Now → 10 min:**
- Install llama-cpp
- Download GGUF model
- Test Harry on CPU (~1-2s)

**10 min → 3 hours:**
- CPU version works!
- NPU export runs in background
- Test Harry's personality
- Refine responses

**After 3 hours:**
- Download QAIRT SDK
- Configure environment
- Switch to NPU version (~500ms!)

---

## 💡 Why This Approach?

✅ **Test immediately** with CPU version
✅ **NPU export runs in parallel** (no wasted time)
✅ **Same code structure** (easy to switch)
✅ **Verify Harry's personality** before NPU deploy

---

## Summary

**Start both tracks NOW:**

1. **Track 1 (CPU):** Test in 10 minutes
2. **Track 2 (NPU):** Ready in 3 hours

**Best of both worlds!** 🎉

---

## Quick Commands

```powershell
# Track 1 - CPU (10 min)
conda activate hacknyu_offline
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
# Download GGUF from: https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF
python harry_llama_cpp.py

# Track 2 - NPU (3 hours)
huggingface-cli login
start_export.bat
```

Get started! 🚀

