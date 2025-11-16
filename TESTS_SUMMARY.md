# Test Files Summary

## Available Test Scripts

### 1. ✅ `test_stt_live.py` - NPU Speech-to-Text
**NPU-Optimized Whisper STT Test**

```powershell
python test_stt_live.py
```

**Features:**
- Uses Qualcomm AI Hub NPU-optimized model
- Shows clear "🔴 RECORDING..." countdown
- 8-second recording window
- Displays transcription immediately
- Press ENTER to record again, Ctrl+C to quit

**Example output:**
```
🔴 RECORDING... 5 seconds left
✓ Recording complete!
Transcribing your speech...
✓ Done! (took 1.2s)
============================================================
📝 YOU SAID: "Hello, this is a test of the speech recognition"
============================================================
```

**Performance:**
- Current (CPU emulation): ~1-2s
- On Snapdragon device: ~44ms (45x faster!)

---

### 2. ✅ `test_tts_simple.py` - Text-to-Speech
**pyttsx3 TTS Test**

```powershell
python test_tts_simple.py
```

**Features:**
- Tests pyttsx3 offline TTS
- Speaks 4 test phrases
- Shows available voices
- 100% offline, instant response

**Voices available:**
- Microsoft David (Male, English US)
- Microsoft Zira (Female, English US)
- Microsoft Sabina (Female, Spanish MX)

---

### 3. ✅ `test_emotion_inference.py` - Emotion Recognition
**Test ONNX Emotion Model**

```powershell
python test_emotion_inference.py
```

**Features:**
- Tests emotion detection model
- Uses ONNX model from `models/emotion_*/`
- Detects 7 emotions
- Shows confidence scores

---

## Quick Test All Components

```powershell
# 1. Test STT (Whisper NPU)
python test_stt_live.py

# 2. Test TTS (pyttsx3)
python test_tts_simple.py

# 3. Test Emotion
python test_emotion_inference.py

# 4. Check device connection
python check_device.py
```

## Deleted Files (Cleaned Up)

- ❌ `test_stt_tts.py` - Old comprehensive test
- ❌ `test_whisper_simple.py` - CPU-based test
- ❌ `test_whisper_interactive.py` - Replaced by test_stt_live.py
- ❌ `test_npu_stt.py` - Merged into test_stt_live.py

## Current Stack

```
✅ Wake Word - Picovoice (.ppn file ready)
✅ STT - Whisper NPU (test_stt_live.py)
⚠️ Emotion - Need smaller model for NPU
✅ TTS - pyttsx3 (test_tts_simple.py)
```

## Next Steps

1. **Test the pipeline:**
   ```powershell
   python test_stt_live.py
   ```

2. **Deploy smaller emotion model:**
   ```powershell
   python convert_emotion_small.py
   python deploy_fixed.py --model models/emotion_small/model.onnx
   ```

3. **Build full integration:**
   - Wake word detection
   - STT → Emotion → LLM → TTS
   - Unity avatar

See **GUIDE.md** for complete integration examples!

