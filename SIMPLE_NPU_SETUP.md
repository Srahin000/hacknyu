# Simple NPU Setup for Harry's LLM

## Current Situation:
- ❌ qai_hub_models doesn't have ready Llama loaders
- ✅ You need to download ONNX from Qualcomm website
- ✅ Then deploy with deploy_fixed.py

---

## Step-by-Step (15 minutes)

### Step 1: Download Model (5 min)

**Go to:** https://aihub.qualcomm.com/models

**In search box, type:** `Llama`

**You'll see:**
- Llama-v3.2-1B-Instruct (BEST FOR YOU - smallest/fastest)
- Llama-v3-8B-Chat  
- Llama-v2-7B-Chat

**Click on:** Llama-v3.2-1B-Instruct

**Click:** "Download" button

**Select format:** ONNX (not PyTorch)

**Save to:** `C:\Users\hackuser\Documents\HackNYU\models\llama_3_2_1b\`

---

### Step 2: Deploy to NPU (10 min compile time)

```powershell
cd C:\Users\hackuser\Documents\HackNYU
python deploy_fixed.py --model models/llama_3_2_1b/model.onnx
```

This will:
- Upload to Qualcomm cloud
- Compile for Snapdragon NPU
- Download optimized binary

**Time:** 10-30 minutes (runs in cloud, you can wait)

---

### Step 3: Use NPU Model

I'll create a script that uses the deployed model.

---

## Alternative: Use Current Model with Quantization (2 min)

While waiting for NPU download/deploy, use 4-bit quantization:

**Already installed:** bitsandbytes ✅

**Update harry_llm.py to use quantization** → Will make it 2-3x faster

---

## What Should You Do Right Now?

### Option A: Get NPU Model (Best, but takes time)
1. Open browser: https://aihub.qualcomm.com/models
2. Download Llama-3.2-1B ONNX (~1GB)
3. Deploy with deploy_fixed.py (10-30 min)
4. Result: ~500ms responses ⚡

### Option B: Use Quantization (Quick fix)
1. I'll update harry_llm.py to use 4-bit
2. Test immediately
3. Result: ~2-3s responses (vs current 6-7s)

---

## Which Do You Want?

**A) I'll start downloading NPU model now** (tell me when done)
- Best: 10x faster (~500ms)
- Takes: 15 min setup + 30 min deploy

**B) Use quantization while I download** (fastest to test)
- Good: 2-3x faster (~2-3s)  
- Takes: 2 minutes

**C) Both** (quantization now, NPU later)
- Use quantization immediately
- Deploy NPU in background
- Switch when ready

Which option?

