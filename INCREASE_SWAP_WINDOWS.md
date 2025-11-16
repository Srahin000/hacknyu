# Increase Swap Memory on Windows for LLM Export

## 🎯 Problem
The Llama 3.2 1B NPU export fails because Windows runs out of memory during the compile/link job.

## ✅ Solution: Add 20GB Swap via WSL2

### Step 1: Check if you have WSL2

```powershell
wsl --list --verbose
```

If you don't have WSL2, install it:
```powershell
wsl --install
```

### Step 2: Create WSL Config File

Create or edit `C:\Users\<YourUsername>\.wslconfig`:

```ini
[wsl2]
memory=16GB
swap=20GB
swapfile=C:\\Users\\<YourUsername>\\swap.vhdx
```

**Replace `<YourUsername>` with your actual username** (e.g., `hackuser`)

### Step 3: Restart WSL2

```powershell
wsl --shutdown
wsl
```

### Step 4: Verify Swap is Active

Inside WSL2:
```bash
free -h
```

You should see swap space around 20GB.

### Step 5: Re-run Export

Back in PowerShell (in your project directory):
```powershell
python export_llm_npu.py
```

---

## 🪟 Alternative: Increase Windows Page File (Without WSL2)

If you don't want to use WSL2:

### Step 1: Open System Properties
1. Press `Win + Pause` or right-click "This PC" → Properties
2. Click "Advanced system settings"
3. Under "Performance" click "Settings"
4. Go to "Advanced" tab → Click "Change" under Virtual Memory

### Step 2: Set Custom Page File
1. Uncheck "Automatically manage paging file"
2. Select your C: drive (or drive with most space)
3. Select "Custom size"
4. Set:
   - **Initial size**: 20480 MB (20 GB)
   - **Maximum size**: 40960 MB (40 GB)
5. Click "Set" then "OK"

### Step 3: Restart Computer
```powershell
Restart-Computer
```

### Step 4: Re-run Export
```powershell
python export_llm_npu.py
```

---

## 🐧 Best Option: Use Linux

If you have access to a Linux machine (or VM):

```bash
# Check current swap
free -h

# If swap is < 20GB, add more:
sudo fallocate -l 20G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make it permanent (add to /etc/fstab):
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Run export
python export_llm_npu.py
```

---

## ⏱️ Expected Export Time

With proper swap:
- **Compile jobs**: ~10-20 minutes each (6 jobs total)
- **Link job**: ~5-10 minutes
- **Total**: ~1-2 hours

---

## 🔍 Monitoring Progress

While export is running:

```powershell
# Check memory usage
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 10

# Check Python processes
Get-Process python* | Format-Table Id,ProcessName,WS
```

---

## 💡 Quick Test After Swap Increase

Before running full export, test if swap is working:

```powershell
# Check system info
systeminfo | findstr /C:"Virtual Memory"
```

You should see increased virtual memory available.




