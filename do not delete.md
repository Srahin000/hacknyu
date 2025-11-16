# NPU Deployment Fix Instructions - DO NOT DELETE

## 🚨 Critical Issues Preventing NPU Deployment

### Issue #1: Insufficient Memory
```
Recommended memory (RAM + swap): 80 GB (currently 32 GB)
Recommended swap space: 49 GB (currently 0 GB)
```

### Issue #2: Hugging Face Token Permissions
```
403 Forbidden: Please enable access to public gated repositories 
in your fine-grained token settings to view this repository.
```

---

## ✅ Fix Steps (Must Complete IN ORDER)

### Step 1: Fix Hugging Face Access

#### 1a. Accept the Llama Model License
- Go to: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
- Click "Agree and access repository"
- You MUST accept the license agreement to download the model

#### 1b. Update Your Token Permissions
- Go to: https://huggingface.co/settings/tokens
- Edit your existing token OR create a new one
- **CRITICAL**: Enable "Read access to contents of all public gated repos you can access"
- Copy the token

#### 1c. Re-login with Updated Token
```bash
huggingface-cli login --token YOUR_NEW_TOKEN
```

Or interactive login:
```bash
huggingface-cli login
```

---

### Step 2: Increase Swap Space (49 GB Required)

**Official Guide:**
https://github.com/quic/ai-hub-apps/blob/main/tutorials/llm_on_genie/increase_swap.md

#### Windows Steps:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab
3. Click "Settings" under Performance
4. Go to "Advanced" tab in Performance Options
5. Click "Change" under Virtual Memory
6. **Uncheck** "Automatically manage paging file size for all drives"
7. Select your drive (usually C:)
8. Select "Custom size"
9. Set both values:
   - Initial size (MB): `49000`
   - Maximum size (MB): `49000`
10. Click "Set"
11. Click "OK" on all dialogs
12. **RESTART YOUR COMPUTER** (required for changes to take effect)

---

### Step 3: Verify Prerequisites

After completing steps 1 and 2, verify before starting export:

```bash
# Check you're logged in to Hugging Face
huggingface-cli whoami

# Check available memory (after restart)
wmic OS get TotalVisibleMemorySize
```

---

### Step 4: Start NPU Export (2-3 Hours)

Only after completing ALL above steps:

```bash
python -m qai_hub_models.models.llama_v3_2_3b_instruct.export --chipset qualcomm-snapdragon-x-elite --skip-profiling --output-dir genie_bundle
```

---

## ⚠️ Important Notes

1. **Cannot run in parallel until swap is fixed**: The emotion model deployment can run in parallel ONLY after you increase swap space. Otherwise, the system will run out of memory.

2. **Restart is mandatory**: Windows requires a restart for swap space changes to take effect.

3. **Export takes 2-3 hours**: The NPU export happens on Qualcomm's cloud servers. Keep your internet connection stable.

4. **Network stability**: Ensure stable internet for the entire 2-3 hour export process.

---

## 🎯 Quick Checklist

- [ ] Accept Llama 3.2 3B license on Hugging Face
- [ ] Update HF token with gated repo access
- [ ] Re-login with new token (`huggingface-cli login`)
- [ ] Increase swap space to 49 GB
- [ ] Restart computer
- [ ] Verify swap space is active
- [ ] Start NPU export
- [ ] Keep computer running with stable internet for 2-3 hours

---

## 🔧 If Export Still Fails

### Memory Issues:
- Check Task Manager → Performance → Memory to verify swap is active
- Close other memory-intensive applications
- Consider using a smaller model (1B instead of 3B)

### Token Issues:
- Verify you can access https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct in browser
- Try logging out and back in: `huggingface-cli logout` then `huggingface-cli login`
- Check token has "Fine-grained - read" permission for gated repos

### Network Issues:
- Ensure stable internet connection
- Consider running overnight when network is stable
- Check firewall isn't blocking Hugging Face or Qualcomm AI Hub

---

**Last Updated:** 2025-11-16
**Status:** Prerequisites not met - complete steps 1 & 2 before attempting export


