# Harry Potter Voice Assistant - Complete Guide

## 🎯 What This Does

A **complete voice-to-voice AI assistant** that:

1. 👂 **Listens** for wake word ("Harry Potter")
2. 🎤 **Records** your question (8 seconds)
3. 📝 **Transcribes** with Whisper STT
4. 🧠 **Generates** response with Llama 3.2 (CPU)
5. 🔊 **Speaks** back the answer with TTS

---

## 🚀 Quick Start

### Prerequisites

Make sure you have:
- ✅ Microphone connected and working
- ✅ Speakers/headphones connected
- ✅ Llama model downloaded (`models/Llama-3.2-1B-Instruct-Q4_K_M.gguf`)
- ✅ Picovoice access key in `.env` file
- ✅ Wake word file (`ppn_files/Harry-Potter_en_windows_v3_0_0.ppn`)

### Install Dependencies

```bash
pip install llama-cpp-python pvporcupine sounddevice openai-whisper pyttsx3 python-dotenv numpy
```

Or use faster-whisper (recommended):
```bash
pip install faster-whisper
```

---

## 🎮 Usage

### Full Mode (with Wake Word)

```bash
python harry_voice_assistant.py
```

**How it works:**
1. Wait for "🟢 Listening for wake word..."
2. Say: **"Harry Potter"**
3. When you hear the beep, ask your question (you have 8 seconds)
4. Harry will transcribe, think, and respond with voice!

### Test Mode (Skip Wake Word)

```bash
python harry_voice_assistant.py --test
```

**How it works:**
1. Press ENTER when ready
2. Record your question (6 seconds)
3. Harry responds with voice
4. Repeat!

---

## 📊 Component Status

When you start the assistant, you'll see initialization status:

```
⚡ HARRY POTTER VOICE ASSISTANT ⚡

🔊 [1/4] Initializing Wake Word Detection...
  ✅ Wake word ready: 'Harry Potter'

🎤 [2/4] Initializing Speech-to-Text...
  ✅ Using faster-whisper (optimized)

🧠 [3/4] Initializing Harry Potter AI...
  ✅ Harry Potter AI loaded (llama.cpp)

🔊 [4/4] Initializing Text-to-Speech...
  ✅ Text-to-Speech ready

✅ ALL SYSTEMS READY!
```

---

## 🎯 Example Conversation

```
🟢 Listening for wake word...

✨ WAKE WORD DETECTED! (#1)
======================================================================

🎤 LISTENING... (speak now!)
======================================================================
🔴 Recording... 8 seconds left
✅ Recording complete!

✅ Transcribed!

💬 You said: "What's your favorite spell?"

🧠 Harry is thinking...
✅ Response ready! (1247ms)

🔊 Harry speaks: "Expecto Patronum! It's saved me more times than I can count. Plus, it's brilliant seeing my stag patronus."

======================================================================
```

---

## ⚙️ Configuration

### Adjust Recording Duration

In `harry_voice_assistant.py`, change:

```python
audio, sample_rate = self.record_audio(duration=8)  # Change 8 to your preference
```

### Change TTS Voice Speed

```python
self.tts_engine.setProperty('rate', 160)  # Lower = slower, Higher = faster
```

### Change Harry's Personality

Edit `harry_llama_cpp.py`, line 77-83:

```python
self.system_prompt = """You are Harry Potter from the books.

Personality: [Your custom personality]
Speech: [Your custom speech style]

Keep responses SHORT (1-2 sentences).
"""
```

---

## 🐛 Troubleshooting

### Wake Word Not Detected

**Problem:** Assistant keeps listening, doesn't detect "Harry Potter"

**Solutions:**
1. Check microphone is working:
   - Windows: Settings → Sound → Test your microphone
2. Speak clearly: **"HARRY POTTER"** (emphasize both words)
3. Check `.env` has valid `PICOVOICE_ACCESS_KEY`
4. Verify wake word file exists: `ppn_files/Harry-Potter_en_windows_v3_0_0.ppn`

### No Audio Recorded

**Problem:** "No speech detected" after recording

**Solutions:**
1. Check microphone permissions
2. Speak louder and closer to microphone
3. Use test mode first: `python harry_voice_assistant.py --test`
4. Increase recording duration (see Configuration above)

### Harry Doesn't Speak

**Problem:** Response shows but no voice output

**Solutions:**
1. Check speakers/headphones are connected
2. Check volume is up
3. Install pyttsx3: `pip install pyttsx3`
4. Test TTS separately: `python test_tts_simple.py`

### Slow Responses

**Problem:** Takes 5+ seconds to respond

**Solutions:**
1. ✅ **You're already using the fast version!** (llama.cpp)
2. Expected latency: ~1-2 seconds
3. For even faster: Wait for NPU deployment (will be ~500ms)
4. Use shorter questions
5. Reduce `max_tokens` in `harry_llama_cpp.py` line 107

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'xyz'`

**Solutions:**
```bash
# Core dependencies
pip install llama-cpp-python
pip install pvporcupine
pip install sounddevice
pip install openai-whisper
pip install pyttsx3
pip install python-dotenv
pip install numpy

# Optional (faster STT)
pip install faster-whisper
```

---

## 📦 File Structure

```
HackNYU/
├── harry_voice_assistant.py        # Main voice assistant
├── harry_llama_cpp.py              # LLM backend (CPU)
├── ppn_files/
│   └── Harry-Potter_en_windows_v3_0_0.ppn  # Wake word model
├── models/
│   └── Llama-3.2-1B-Instruct-Q4_K_M.gguf   # LLM model
└── .env                             # API keys
```

---

## 🎓 How It Works

### Architecture

```
┌─────────────────┐
│  Wake Word      │  Picovoice Porcupine
│  "Harry Potter" │  (~50ms latency)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Record Audio   │  sounddevice
│  (8 seconds)    │  16kHz mono
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Transcribe     │  Whisper Base EN
│  Speech-to-Text │  (~2-3s on CPU)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  LLM Response   │  Llama 3.2 1B (GGUF)
│  Generate Text  │  (~1-2s on CPU)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Speak Response │  pyttsx3
│  Text-to-Speech │  (instant)
└─────────────────┘
```

### Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Wake Word Detection | ~50ms | NPU-optimized |
| Audio Recording | 8 seconds | User configurable |
| Speech-to-Text | ~2-3s | CPU (Whisper Base) |
| LLM Generation | ~1-2s | CPU (Llama.cpp) |
| Text-to-Speech | ~500ms | Windows SAPI |
| **Total (after wake word)** | **~12-14s** | End-to-end |

### Future Optimizations

🚀 **After NPU deployment:**
- STT: 2-3s → ~200ms (15x faster)
- LLM: 1-2s → ~500ms (3x faster)
- **Total: ~12s → ~2s** (6x faster!)

---

## 🎨 Customization Ideas

### 1. Different Character Personalities

Edit the system prompt in `harry_llama_cpp.py`:

```python
# Hermione mode
self.system_prompt = """You are Hermione Granger.
Personality: Intelligent, bookish, rule-following but brave.
Always cite facts and explain things thoroughly."""

# Ron mode  
self.system_prompt = """You are Ron Weasley.
Personality: Loyal, funny, loves food, sometimes insecure.
Use British slang and be casual."""
```

### 2. Multi-Wake-Word Support

Add different wake words for different characters:
- "Harry Potter" → Harry personality
- "Hermione Granger" → Hermione personality
- "Ron Weasley" → Ron personality

### 3. Emotion Detection

Add emotion recognition to audio:
- Use your `test_emotion_inference.py` model
- Adjust Harry's tone based on user emotion
- More empathetic responses

### 4. Context Memory

Harry already has context! Enhance it:
- Remember previous conversations
- Reference past topics
- Build longer-term memory

---

## 🏆 Production Ready Checklist

- [x] Wake word detection working
- [x] Audio recording working
- [x] Speech-to-text working
- [x] LLM response generation working
- [x] Text-to-speech working
- [x] Error handling for each component
- [x] User-friendly status messages
- [ ] NPU optimization (in progress)
- [ ] Emotion detection integration
- [ ] Multi-language support
- [ ] Cloud deployment option

---

## 💡 Tips for Best Results

### For Wake Word:
- Speak clearly and distinctly: "HARRY POTTER"
- Don't rush the words together
- Moderate volume (don't whisper, don't shout)
- Quiet environment helps

### For Questions:
- Speak naturally
- Keep questions clear and specific
- Don't rush (you have 8 seconds!)
- Ask one question at a time

### For Best Responses:
- Harry works best with Harry Potter universe questions
- Keep questions conversational
- Give context if needed: "What happened when..." vs just "What?"

---

## 🔗 Related Files

- `test_wake_word.py` - Test wake word detection only
- `test_stt_live.py` - Test speech-to-text only
- `test_tts_simple.py` - Test text-to-speech only
- `harry_llama_cpp.py` - Test LLM only (text chat)
- `VOICE_ASSISTANT_GUIDE.md` - This file!

---

## 📝 License & Credits

- **Picovoice Porcupine**: Wake word detection
- **OpenAI Whisper**: Speech-to-text
- **Meta Llama 3.2**: Language model
- **llama.cpp**: Fast CPU inference
- **pyttsx3**: Text-to-speech

---

## 🎉 You Did It!

You now have a complete, working voice assistant that can:
- ✅ Detect wake words
- ✅ Listen to questions
- ✅ Understand speech
- ✅ Generate intelligent responses
- ✅ Speak back to you

**This is a fully functional AI voice assistant!** 🎊

Next steps: Deploy to NPU for 6x faster responses! 🚀


