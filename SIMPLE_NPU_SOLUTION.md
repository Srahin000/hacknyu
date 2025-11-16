# Simple Solution: Get Whisper Working on NPU

## Problem Summary
- ✅ Your hardware: Snapdragon X Elite (has NPU)
- ✅ Your software: QNNExecutionProvider available
- ❌ Your model: Compiled for Samsung S24 (wrong device)
- ❌ Your auth: API token not configured

**Error 5005 = Device mismatch**

## Three Options (Pick ONE):

---

### Option 1: Use CPU Whisper (EASIEST - Works Now!)

**Time: 1 minute**

```bash
# Install CPU Whisper
pip install openai-whisper

# Test voice assistant
python harry_voice_assistant.py --test
```

**Performance:**
- STT: ~2-3 seconds (vs ~200ms on NPU)
- Total: ~4-6 seconds per response
- **Perfectly fine for conversation!**

**✅ RECOMMENDED** for immediate use and demos

---

### Option 2: Compile via Web UI (EASIER)

**Time: 15-20 minutes**

**Steps:**

1. **Login to AI Hub:**
   - Go to: https://app.aihub.qualcomm.com
   - Sign in with your account

2. **Find Whisper Model:**
   - Go to "Models" or "Model Zoo"
   - Search for "Whisper Base" or "Whisper Small"

3. **Deploy to Your Device:**
   - Click on Whisper model
   - Click "Deploy" or "Compile"
   - **Device:** Select "Qualcomm Snapdragon X Elite CRD"
   - **Runtime:** QNN
   - **Quantization:** INT8
   - Click "Submit"

4. **Wait for Compilation:**
   - Takes 10-20 minutes
   - Shows progress in "Jobs" tab

5. **Download Model:**
   - When done, click "Download"
   - Extract to: `models/whisper_x_elite/`

6. **Update test script:**
   ```python
   # In test_npu_whisper.py, line 22:
   model_path = Path("models/whisper_x_elite")
   ```

7. **Test:**
   ```bash
   python test_npu_whisper.py
   ```

---

### Option 3: Fix CLI Authentication (HARDER)

**Time: 5 minutes + 15-20 minutes compilation**

**Steps:**

1. **Get API Token:**
   - Go to: https://app.aihub.qualcomm.com/account/
   - Copy your API token

2. **Configure qai-hub:**
   ```bash
   qai-hub configure --api_token YOUR_TOKEN_HERE
   ```

3. **Compile via CLI:**
   ```bash
   qai-hub submit-compile-job \
     --model-id whisper-base-en \
     --device "Qualcomm Snapdragon X Elite CRD" \
     --target-runtime qnn
   ```

4. **Wait and download** (similar to Option 2)

---

## My Recommendation

### For Hackathon/Demo THIS WEEKEND:
**Use Option 1 (CPU)** - it works perfectly and 2-3s latency is fine for conversation.

### For Production/Optimization LATER:
**Use Option 2 (Web UI)** - easiest way to get NPU model without CLI headaches.

---

## Quick Test Right Now

Let's verify CPU Whisper works:

```bash
# 1. Install
pip install openai-whisper

# 2. Quick test
python -c "import whisper; print('Whisper ready!')"

# 3. Run voice assistant
python harry_voice_assistant.py --test
```

**Expected output:**
```
Harry Potter Voice Assistant
[1/4] Wake Word ready
[2/4] STT ready (CPU Whisper)
[3/4] LLM ready (Harry llama.cpp)
[4/4] TTS ready

Press ENTER to record...
```

---

## Performance Comparison

| Solution | STT Latency | Setup Time | Complexity |
|----------|-------------|------------|------------|
| **CPU Whisper** | **2-3s** | **1 min** | ⭐ Easy |
| NPU (Web UI) | 200ms | 20 min | ⭐⭐ Medium |
| NPU (CLI) | 200ms | 25 min | ⭐⭐⭐ Hard |

---

## Bottom Line

**Your NPU hardware is perfect and ready.**

You just need the right model binary. For now:
- CPU works great (2-3s is fine)
- NPU optimization can wait
- Focus on making the voice assistant functional!

**Next command:**
```bash
pip install openai-whisper
python harry_voice_assistant.py --test
```

Let's get Harry talking! 🎙️✨

