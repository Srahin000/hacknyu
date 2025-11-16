# Fix LLM NPU Export - Quick Action Guide

## 🔴 The Problem

Your Llama 3.2 1B export failed with:
```
qai_hub.client.UserError: Model passed in was 'None' 
(make sure this is not the target of a failed compile job)
```

**Root Cause**: Insufficient memory/swap during compile/link jobs

---

## ✅ Solution Options (Pick One)

### Option 1: Increase Swap on Windows (RECOMMENDED)

**Time**: 5 minutes + 1-2 hour export

**Steps**:
1. Create `C:\Users\hackuser\.wslconfig`:
```ini
[wsl2]
memory=16GB
swap=20GB
swapfile=C:\\Users\\hackuser\\swap.vhdx
```

2. Restart WSL2:
```powershell
wsl --shutdown
```

3. Re-run export with improved script:
```powershell
python export_llm_npu_improved.py
```

📖 **Full guide**: `INCREASE_SWAP_WINDOWS.md`

---

### Option 2: Use Your Working CPU Setup (FASTEST)

**Time**: 0 minutes (already working!)

Your voice assistant **already works perfectly** with CPU:

```powershell
python harry_voice_assistant.py --cpu
```

**Performance**:
- Whisper STT: ~2-3 seconds (CPU)
- Llama LLM: ~1-2 seconds (llama.cpp)
- XTTS TTS: ~1-2 seconds

**Total**: ~5 seconds per conversation - **totally fine for voice assistant!**

✅ **This is the easiest option** - no export needed!

---

### Option 3: Download Prebuilt Model (IF AVAILABLE)

**Time**: 10-30 minutes (download only)

Check if Qualcomm has prebuilt Llama 3.2 for X Elite:

1. Visit: https://aihub.qualcomm.com/compute/models
2. Search for "Llama 3.2 1B"
3. Filter by "Snapdragon X Elite"
4. Download precompiled bundle

📁 Place in: `genie_bundle/`

---

### Option 4: Use Linux for Export

**Time**: 1-2 hours

If you have Linux machine or VM:

```bash
# Add swap
sudo fallocate -l 20G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Run export
python export_llm_npu_improved.py
```

---

## 🎯 My Recommendation

### For HACKATHON / DEMO:
→ **Use Option 2** (CPU mode)
- Works NOW
- No waiting for export
- Already fast enough
- 100% reliable

### For PRODUCTION / OPTIMIZATION LATER:
→ **Use Option 1** (Increase swap + export)
- NPU will be faster (~500ms vs 1-2s)
- Worth it after you have everything else working

---

## 📊 Performance Comparison

| Component | CPU Mode | NPU Mode |
|-----------|----------|----------|
| **Whisper** | 2-3s | ~1s (when working) |
| **Llama** | 1-2s | ~500ms (theoretical) |
| **Total** | ~5s | ~3s |
| **Setup Time** | ✅ 0 min | ❌ 2+ hours |
| **Reliability** | ✅✅✅ High | ⚠️ Experimental |

---

## 🚀 Quick Start Commands

### Run Voice Assistant (CPU Mode) - WORKS NOW:
```powershell
python harry_voice_assistant.py --cpu
```

### Test Mode (No Wake Word):
```powershell
python harry_voice_assistant.py --cpu --test
```

### Check Audio Files:
```powershell
Get-ChildItem audio
```

### Export to NPU (After Increasing Swap):
```powershell
python export_llm_npu_improved.py
```

### Test NPU LLM (After Export):
```powershell
python test_npu_llm.py
```

---

## 💡 Bottom Line

**Your voice assistant is READY TO USE right now with CPU mode!**

The NPU export is a nice optimization for later, but not required for a great demo. Focus on:
1. ✅ Getting wake word working (or use keyboard fallback)
2. ✅ Recording good conversations
3. ✅ Testing Harry's personality
4. ✅ Saving all audio files (already done!)

**Save NPU optimization for after your demo works!** 🎉

---

## 🆘 If You Still Want NPU

Follow these steps IN ORDER:

1. ✅ Read `INCREASE_SWAP_WINDOWS.md`
2. ✅ Increase swap to 20GB
3. ✅ Run `python export_llm_npu_improved.py`
4. ✅ Wait 1-2 hours
5. ✅ Test with `python test_npu_llm.py`
6. ✅ Run voice assistant (NPU auto-detected)

Need help? Check the logs in `llm_export.log`









