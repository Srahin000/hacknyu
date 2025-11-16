# Download NPU Model - Do This Now

## Step 1: Open Browser

**Go to:** https://aihub.qualcomm.com/models

## Step 2: Find Llama Model

In the **search box** at the top, type: **`Llama`**

You'll see several models. Look for:
- **Llama-v3.2-1B-Instruct** ⭐ (RECOMMENDED - smallest, fastest)
- Llama-v3-8B-Chat (larger, slower)
- Llama-v2-7B-Chat (older)

## Step 3: Download

1. **Click on:** "Llama-v3.2-1B-Instruct"
2. **Click:** The "Download" button
3. **Select format:** 
   - Choose **ONNX** (NOT PyTorch)
   - Click download
4. **Save location:** 
   - Download to: `C:\Users\hackuser\Downloads\`
   - File will be named something like: `llama_v3_2_1b.onnx` or `model.onnx`

**Download size:** ~1-2GB (may take 5-10 minutes depending on internet)

---

## Step 4: Move Model to Project

Once download completes:

```powershell
# Create directory
cd C:\Users\hackuser\Documents\HackNYU
mkdir models\llama_npu

# Move the downloaded file
# (Adjust the filename if different)
move C:\Users\hackuser\Downloads\llama_v3_2_1b.onnx models\llama_npu\model.onnx
```

Or just:
1. Open File Explorer
2. Go to Downloads folder
3. Copy the `.onnx` file
4. Paste into: `C:\Users\hackuser\Documents\HackNYU\models\llama_npu\`
5. Rename to: `model.onnx`

---

## Step 5: Deploy to NPU

```powershell
cd C:\Users\hackuser\Documents\HackNYU
python deploy_fixed.py --model models\llama_npu\model.onnx
```

**What this does:**
- Uploads model to Qualcomm cloud
- Compiles for your Snapdragon device
- Optimizes for NPU
- Downloads compiled binary

**Time:** 10-30 minutes (be patient!)

**You'll see:**
```
✓ Model uploaded
✓ Compile job submitted
  Compiling... (this takes time)
✓ Compilation completed
✓ Profile results downloaded
```

---

## Step 6: Test Harry with NPU!

Once deployment completes:

```powershell
python talk_to_harry_npu.py
```

(I'll create this script once your model is deployed)

**Expected speed:** ~500ms per response (12x faster!)

---

## Troubleshooting

### Can't find Llama on AI Hub?
Try these searches:
- "Llama-3.2"
- "Llama quantized"
- Just browse "Natural Language" category

### Download not ONNX format?
- Make sure you select "ONNX" in the format dropdown
- NOT "PyTorch" or "TorchScript"

### File is a .zip?
- Extract the zip file
- Look inside for `model.onnx` or similar
- Copy that file to `models\llama_npu\`

---

## Let Me Know When:

✅ **Download started** - I'll prepare next scripts
✅ **Download complete** - I'll help you deploy
✅ **Deployment running** - I'll create the final chat script
✅ **Deployment done** - We'll test Harry at 10x speed!

---

**Start the download now, then tell me when it's done!** 🚀

