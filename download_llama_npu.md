# Download Llama for NPU - Step by Step

## Get NPU-Optimized Llama Model from Qualcomm AI Hub

### Step 1: Visit Qualcomm AI Hub

Go to: **https://aihub.qualcomm.com/models**

### Step 2: Search for Llama

In the search box, type: **"Llama"**

### Step 3: Select a Model

**Recommended:** Llama-v3-8B-Chat-quantized
- Best balance of speed and quality
- Pre-optimized for Snapdragon NPU
- ~4GB download

**Alternative (Smaller/Faster):** Llama-v2-7B-Chat-quantized
- Slightly older but works great
- ~3.5GB download

### Step 4: Download

1. Click on the model
2. Click "Download" button
3. Select format: **ONNX** (not PyTorch)
4. Download to: `C:\Users\hackuser\Documents\HackNYU\models\`
5. Rename folder to: `llama_npu`

Your structure should be:
```
HackNYU/
  models/
    llama_npu/
      model.onnx          ← The main model file
      config.json
      (other files)
```

### Step 5: Deploy to NPU

```powershell
cd C:\Users\hackuser\Documents\HackNYU
python deploy_fixed.py --model models/llama_npu/model.onnx
```

This will:
- Upload to Qualcomm cloud
- Compile for your Snapdragon device
- Takes 10-30 minutes
- Downloads optimized binary

### Step 6: Test Harry with NPU

```powershell
python harry_llm_npu.py
```

It will automatically detect and use the NPU model!

---

## Alternative: Use AI Hub Models Directly

If models are available through Python API:

```powershell
# Try to see available models
python -c "from qai_hub_models import models; print(dir(models))"
```

Look for:
- `llama_v3_8b_chat_quantized`
- `llama_v2_7b_chat_quantized`

If found, they work directly without manual download!

---

## What if AI Hub doesn't have ONNX downloads?

Use the model browser API:

```powershell
python list_ai_hub_models.py
```

(I'll create this script if needed)

---

## Expected Performance After NPU Deployment

| Stage | Before (CPU) | After (NPU) | Improvement |
|-------|--------------|-------------|-------------|
| Harry's response | 6-7s | 500ms | **12x faster!** |
| Total pipeline | N/A | <1s | **Real-time!** |

---

## Need Help?

1. Can't find download? → Let me create a script to browse available models
2. Download too big? → Use smaller Llama-v2-7B
3. Want to test NPU readiness? → Run `python check_device.py`

Let me know where you're stuck!

