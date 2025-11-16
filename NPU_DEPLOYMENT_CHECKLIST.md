# NPU Deployment Checklist

## 📋 Your To-Do List

### ☐ Step 1: Download Model (5-10 minutes)

**Action:** Download Llama-3.2-1B ONNX from Qualcomm AI Hub

1. Open: https://aihub.qualcomm.com/models
2. Search: "Llama-3.2-1B" or "Llama"
3. Click on model
4. Download ONNX format (~1-2GB)
5. Save to: `models\llama_npu\model.onnx`

**Check status:**
```powershell
python check_model_ready.py
```

---

### ☐ Step 2: Deploy to NPU (10-30 minutes)

**Action:** Compile model for Snapdragon NPU

```powershell
python deploy_fixed.py --model models\llama_npu\model.onnx
```

**What happens:**
- Uploads to Qualcomm cloud ✓
- Compiles for NPU (this is slow!) ⏳
- Downloads compiled binary ✓
- Saves to `deployed_models/`

**This takes 10-30 minutes - be patient!**

---

### ☐ Step 3: Test Harry with NPU (instant!)

**Action:** Chat with super-fast Harry

```powershell
python talk_to_harry_npu.py
```

**Expected:**
- Response time: ~300-500ms ⚡
- 10-12x faster than CPU!
- Same Harry personality

---

## 🔍 Check Your Progress

```powershell
# Quick status check
python check_model_ready.py
```

This shows:
- ✅ or ❌ Model downloaded
- ✅ or ⏳ Model deployed
- Next steps

---

## ⏱️ Time Estimate

| Step | Time | What You Do |
|------|------|-------------|
| Download | 5-10 min | Wait for download |
| Deploy | 10-30 min | Run command, wait |
| Test | Instant | Chat with Harry! |
| **TOTAL** | **20-40 min** | Mostly waiting |

---

## 🎯 Current Status

Run this command to see where you are:

```powershell
python check_model_ready.py
```

Output will show:
```
✅ ONNX model downloaded (or ❌ if not)
✅ NPU model deployed (or ⏳ if not)
```

---

## 📁 Expected File Structure

After everything:
```
HackNYU/
├── models/
│   └── llama_npu/
│       └── model.onnx          ← Downloaded from AI Hub
│
├── deployed_models/
│   └── llama_npu/
│       └── compiled_model.onnx ← After deploy_fixed.py
│
└── talk_to_harry_npu.py        ← Your super-fast Harry!
```

---

## 🚀 Quick Reference

```powershell
# 1. Check status
python check_model_ready.py

# 2. Deploy (after download)
python deploy_fixed.py --model models\llama_npu\model.onnx

# 3. Chat with NPU Harry
python talk_to_harry_npu.py
```

---

## ❓ Need Help?

**Model not downloading?**
- Try different search terms: "Llama quantized", "Llama 1B"
- Look in "Natural Language" category
- Make sure you select ONNX format!

**Deployment stuck?**
- This is normal! NPU compilation takes 10-30 minutes
- Don't cancel - let it run
- You can check status on: https://app.aihub.qualcomm.com/

**Deployment failed?**
- Check API key: `python check_device.py`
- Model might be too large - try smaller one
- Check error message for hints

---

## 🎉 When Done

You'll have:
- ✅ Harry responding in ~500ms
- ✅ 12x faster than CPU
- ✅ Ready for full pipeline integration
- ✅ NPU-optimized for your device

**Next:** Integrate with wake word + STT + TTS for full <1s pipeline!

---

**Start now:** Open browser → https://aihub.qualcomm.com/models → Download Llama!

