# Picovoice Wake Word Setup

## ✅ Installation Complete

Picovoice Porcupine is installed and ready!

## 🔑 Get Your Access Key (1 minute)

1. **Go to Picovoice Console:**
   - Visit: https://console.picovoice.ai/
   
2. **Sign Up (Free):**
   - Create account with email
   - Verify email
   
3. **Copy Access Key:**
   - Dashboard will show your Access Key
   - Copy the entire key
   
4. **Add to `.env` file:**
   ```bash
   # Open .env file and add:
   PICOVOICE_ACCESS_KEY=your_access_key_here
   ```

Your `.env` file should now have:
```bash
QAI_HUB_API_KEY=your_qualcomm_key
TARGET_DEVICE=Samsung Galaxy S24
PICOVOICE_ACCESS_KEY=your_picovoice_key
```

## 🧪 Test Wake Word Detection

```powershell
python test_wake_word.py
```

This will:
1. Load your `Harry-Potter_en_windows_v3_0_0.ppn` file
2. Listen for "Harry Potter" wake word
3. Print "✓ WAKE WORD DETECTED!" when you say it
4. Keep listening (Ctrl+C to stop)

## 📝 Your Wake Word

- **Wake Phrase:** "Harry Potter"
- **File:** `ppn_files/Harry-Potter_en_windows_v3_0_0.ppn`
- **Language:** English
- **Platform:** Windows
- **Runs:** 100% offline (after initial key validation)

## 🎯 Usage Example

```python
import pvporcupine

# Initialize with your .ppn file
porcupine = pvporcupine.create(
    access_key="your_key_here",
    keyword_paths=["ppn_files/Harry-Potter_en_windows_v3_0_0.ppn"]
)

# In audio callback
keyword_index = porcupine.process(audio_frame)
if keyword_index >= 0:
    print("Wake word detected!")
    # Start recording for STT
```

## 🚀 Full Pipeline

Once wake word is working, integrate with STT:

```
1. Always listening for "Harry Potter"
   ↓
2. Wake word detected → Start recording
   ↓
3. Record speech (8 seconds or until silence)
   ↓
4. Transcribe with Whisper NPU (~44ms)
   ↓
5. Process with emotion detection
   ↓
6. Generate response
   ↓
7. Speak with TTS
   ↓
8. Return to listening for wake word
```

## ⚡ Performance

- **Wake Word Detection:** <50ms latency
- **Always-On:** Low power consumption
- **Offline:** Runs 100% locally
- **No Internet:** Works without connection

## 🆓 Free Tier Limits

Picovoice free tier includes:
- Unlimited on-device inference
- Custom wake words (.ppn files)
- Wake word, STT, and TTS
- Perfect for development and demos

## 🔧 Troubleshooting

### "Access key not found"
```bash
# Add to .env file:
PICOVOICE_ACCESS_KEY=your_key_here
```

### "Cannot open audio stream"
- Check microphone is plugged in
- Set as default device in Windows sound settings
- Close other apps using microphone

### "Invalid access key"
- Get new key from console.picovoice.ai
- Copy entire key (no spaces)
- Restart terminal after adding to .env

## 📚 Resources

- [Picovoice Console](https://console.picovoice.ai/)
- [Porcupine Docs](https://picovoice.ai/docs/porcupine/)
- [Train Custom Wake Words](https://console.picovoice.ai/ppn)

## ✅ Next Steps

1. Get access key from console.picovoice.ai
2. Add to `.env` file
3. Run: `python test_wake_word.py`
4. Say "Harry Potter" to test
5. Build full pipeline!

