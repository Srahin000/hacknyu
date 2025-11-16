# Harry Potter Voice Assistant - NPU Edition

**Fully NPU-powered voice assistant featuring Harry Potter as your AI companion!**

---

## 🌟 Key Features

### ⚡ **Full NPU Acceleration**
- **Speech-to-Text**: Whisper model running on Qualcomm NPU
- **LLM**: Llama 3.2 1B via Qualcomm Genie (NPU)
- **Emotion Detection**: Real-time audio emotion analysis
- **No CPU Fallbacks**: Pure NPU performance

### 🧙 **Harry Potter Character**
- Authentic Harry Potter personality from books/movies
- British teenage speech patterns ("bloody hell", "blimey", "reckon", "mate")
- Brave, loyal, kind, occasionally sarcastic
- Natural conversational tone with wizarding world references

### 🧠 **Intelligent Context & Insights**
- **Context Manager**: Loads previous conversation insights for continuity
- **Background Analysis**: Automatically generates insights after each conversation
- **Learning Patterns**: Tracks topics, emotions, breakthroughs, and struggles
- **Personalized Responses**: Harry remembers past conversations and adapts

### 🎤 **Complete Voice Pipeline**
1. Wake word detection ("Harry Potter" or keyboard fallback)
2. 8-second audio recording with auto-gain boost
3. Whisper NPU speech-to-text (~500ms)
4. Emotion detection from audio
5. Genie NPU LLM response (~1-2s)
6. XTTS v2 text-to-speech with Harry's voice
7. Automatic insight generation (background)

---

## 📦 What's Updated

### ✅ **Removed**
- ❌ CPU fallback modes (NPU-only now)
- ❌ `--cpu` command-line flag
- ❌ Conditional fallback logic

### ✅ **Added**
- ✨ Automatic insight generation after each conversation
- ✨ Enhanced Harry Potter character prompt with personality details
- ✨ `--no-insights` flag to disable background analysis
- ✨ NPU-powered conversation analyzer
- ✨ Background threading for non-blocking insight generation

### ✅ **Improved**
- 🎯 Better error messages for NPU component failures
- 🎯 Clearer initialization feedback
- 🎯 Enhanced context integration

---

## 🚀 Quick Start

### **Prerequisites**
1. ✅ Qualcomm Snapdragon X Elite NPU
2. ✅ QAIRT SDK 2.37.1 installed
3. ✅ Genie bundle configured (test with `python run_genie_safe.py "Hello"`)
4. ✅ Whisper NPU models deployed
5. ✅ Python dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

### **Run the Assistant**

**Normal Mode** (with wake word):
```bash
python harry_voice_assistant.py
```

**Test Mode** (keyboard activation):
```bash
python harry_voice_assistant.py --test
```

**Disable Context** (ignore previous conversations):
```bash
python harry_voice_assistant.py --no-context
```

**Disable Insights** (skip background analysis):
```bash
python harry_voice_assistant.py --no-insights
```

---

## 🎯 How It Works

### **1. Wake Word Detection**
- **Primary**: Picovoice "Harry Potter" wake word
- **Fallback**: Press ENTER if Picovoice unavailable

### **2. Audio Recording**
- 8 seconds of audio capture
- Auto-gain boost for quiet microphones
- Real-time countdown feedback

### **3. Speech-to-Text (Whisper NPU)**
- Whisper Base model on NPU
- ~500ms latency
- Automatic preprocessing

### **4. Emotion Detection (NPU)**
- Analyzes user's emotional state from audio
- Detects: Joy, Calm, Neutral, Frustrated, Anxious, Excited, etc.
- Stores emotion data in conversation metadata

### **5. LLM Response (Genie NPU)**
- Llama 3.2 1B Instruct via Qualcomm Genie
- Harry Potter character prompt with personality
- Context from previous conversations (if enabled)
- ~1-2s response time

### **6. Text-to-Speech (XTTS v2)**
- High-quality voice synthesis
- Harry Potter voice parameters:
  - Speaker: `male-en-2`
  - Emotion: `happy`
  - Speed: `1.12` (youthful pacing)
  - Pitch: `1.20` (kid-like pitch)

### **7. Insight Generation (Background)**
- Runs asynchronously after conversation
- Extracts structured insights using Genie NPU:
  - **Topics**: What was discussed
  - **Emotions**: Dominant emotional state
  - **Sentiment**: 0-100 score
  - **Engagement**: low/medium/high
  - **Breakthroughs**: Learning "aha" moments
  - **Attention Flags**: When parent should check in
- Saves insights to `conversations/<date>/conv_XXXX/insights.json`

---

## 📂 File Structure

### **Conversation Storage**
```
conversations/
├── 20251116/
│   ├── conv_0001_143025/
│   │   ├── user_audio.wav          # User's recorded audio
│   │   ├── harry_audio.wav         # Harry's TTS response
│   │   ├── transcript.txt          # Full transcript
│   │   ├── metadata.json           # Metadata (emotion, latency, etc.)
│   │   └── insights.json           # AI-generated insights
│   └── conv_0002_143512/
│       └── ...
└── 20251115/
    └── ...
```

### **TTS Audio Archive**
```
audio/
├── harry_tts_20251116_143025_conv0001.wav
├── harry_tts_20251116_143025_conv0001.txt
└── ...
```

---

## 🧠 Context & Insights System

### **Context Manager** (`context_manager.py`)
- **Reads** recent conversation insights
- **Builds context** for Harry's responses
- Tracks:
  - Recent topics discussed
  - Emotional trends (improving/declining/stable)
  - High-interest topics
  - Learning struggles and breakthroughs
  - Attention flags

### **Conversation Analyzer** (`conversation_analyzer.py`)
- **Generates insights** using Genie NPU
- Runs in **background thread** (non-blocking)
- Extracts:
  - **Topics**: Space, math, friends, art, school, family, etc.
  - **Dominant Emotion**: Joyful, Calm, Frustrated, Anxious, etc.
  - **Sentiment Score**: 0-100 (negative/neutral/positive)
  - **Summary**: 2-3 sentence neutral summary
  - **Key Phrases**: Important de-identified phrases
  - **Engagement Level**: low/medium/high
  - **Question Count**: Number of questions asked
  - **Breakthrough Flag**: "Aha" moment detection
  - **Needs Attention Flag**: Parent check-in recommendation

### **Batch Analysis**
Run insights on all conversations without insights:
```bash
python conversation_analyzer.py --batch
```

---

## 🎨 Harry Potter Character Prompt

### **Personality**
- Brave but humble
- Loyal to friends
- Occasionally sarcastic
- Kind-hearted
- Dislikes showing off

### **Speech Patterns**
- British expressions: "bloody hell", "blimey", "reckon", "mate", "brilliant"
- Natural contractions: "I'm", "don't", "can't", "you're"
- Casual teenager tone: direct, friendly, not overly formal

### **Response Style**
- Short answers (1-3 sentences)
- Helpful and encouraging
- References wizarding world when relevant (but doesn't force it)
- Shows genuine interest
- Occasionally shows modest pride about Hogwarts/friends

### **Example Responses**

**Question**: "What's the most important thing in life?"
**Harry**: "I reckon it's the people you love, mate. My friends saved me more times than I can count. Family isn't always blood - it's the ones who stick by you."

**Question**: "How do I deal with bullies?"
**Harry**: "Stand up for yourself, but don't sink to their level. I dealt with Malfoy for years - sometimes the best thing is to ignore them and focus on your real friends. You're stronger than you think."

**Question**: "Tell me about Quidditch!"
**Harry**: "Bloody brilliant sport! Flying on a broomstick, chasing the Golden Snitch... nothing quite like it. I've been playing Seeker since first year - it's terrifying and amazing at the same time!"

---

## 🛠️ Troubleshooting

### **NPU Components Not Loading**

#### **Whisper NPU Failed**
```bash
❌ NPU Whisper failed
   Make sure Whisper models are deployed to NPU
   See: WHISPER_NPU_FIX.md
```
**Solution**: Deploy Whisper models to NPU (check deployment guides)

#### **Genie LLM Failed**
```bash
❌ Genie LLM failed
   Make sure Genie bundle is properly configured
   Test with: python run_genie_safe.py "Hello"
```
**Solution**: 
1. Test Genie separately: `python run_genie_safe.py "Hello"`
2. Check SDK version: `fix_qnn_sdk_version.ps1`
3. Verify bundle structure: `python diagnose_genie_bundle.py`

#### **Insight Generation Disabled**
```bash
⚠️ Insight generation disabled: [error]
```
**Solution**: This is non-critical. Insights won't be generated, but voice assistant will still work.

### **Wake Word Not Working**
```bash
⚠️ PICOVOICE_ACCESS_KEY not found in .env
   Using keyboard fallback (press ENTER to activate)
```
**Solution**: 
1. Get free API key from https://console.picovoice.ai/
2. Add to `.env` file: `PICOVOICE_ACCESS_KEY=your_key_here`
3. Or use keyboard fallback (press ENTER)

### **No Speech Detected**
```bash
⚠️ No speech detected. Try again!
```
**Solution**: 
- Speak louder during recording
- Check microphone permissions
- Verify microphone is working in Windows settings

---

## 📊 Performance Metrics

### **Latency Breakdown**
- **Wake Word**: Instant (<50ms)
- **Audio Recording**: 8 seconds (user-controlled)
- **Emotion Detection**: ~200-500ms (NPU)
- **Speech-to-Text**: ~500ms (Whisper NPU)
- **LLM Response**: ~1-2s (Genie NPU)
- **Text-to-Speech**: ~2-3s (XTTS v2, varies by response length)
- **Insight Generation**: ~2-5s (background, non-blocking)

### **Total Interaction Time**
- **User speaks**: 8s (recording)
- **Harry responds**: ~4-6s (STT + LLM + TTS)
- **Insights**: Generated in background (doesn't block)

---

## 🎓 Advanced Usage

### **Manual Insight Generation**

**Analyze specific conversation:**
```bash
python conversation_analyzer.py --conv-dir conversations/20251116/conv_0001_143025
```

**Batch analyze all conversations:**
```bash
python conversation_analyzer.py --batch
```

### **Test Context System**
```bash
python context_manager.py
```
Shows:
- Recent insights
- Topic history
- Emotional trends
- Learning context
- Context string for Harry

### **Disable Specific Features**

**No context (fresh start each time):**
```bash
python harry_voice_assistant.py --no-context
```

**No insights (save processing time):**
```bash
python harry_voice_assistant.py --no-insights
```

**Both disabled:**
```bash
python harry_voice_assistant.py --no-context --no-insights
```

---

## 🔧 Configuration

### **TTS Voice Parameters** (`harry_voice_assistant.py`)
```python
self.tts_speaker = "male-en-2"     # Male English voice
self.tts_emotion = "happy"          # Cheerful tone
self.tts_speed = 1.12               # Slightly faster (youthful)
self.tts_pitch = 1.20               # Higher pitch (kid-like)
```

### **Context Window** (`context_manager.py`)
```python
self.max_context = 5  # Number of recent conversations to load
```

### **Recording Duration** (`harry_voice_assistant.py`)
```python
audio, sample_rate = self.record_audio(duration=8)  # 8 seconds
```

---

## 📝 File Dependencies

### **Core Files**
- `harry_voice_assistant.py` - Main voice assistant
- `harry_llm_npu.py` - Genie NPU interface
- `context_manager.py` - Context loading and management
- `conversation_analyzer.py` - Insight generation
- `whisper_npu_full.py` - Whisper NPU interface
- `emotion_npu.py` - Emotion detection
- `run_genie_safe.py` - Genie testing utility

### **Genie Bundle**
- `genie_bundle/genie-t2t-run.exe` - Genie runtime
- `genie_bundle/genie_config.json` - Configuration
- `genie_bundle/*.bin` - Model binaries
- `genie_bundle/tokenizer.json` - Tokenizer
- `genie_bundle/*.dll` - Required libraries

---

## 🚀 Next Steps

1. **Test the Assistant**:
   ```bash
   python harry_voice_assistant.py --test
   ```

2. **Ask Harry a Question**:
   - Press ENTER (test mode)
   - Speak for 8 seconds
   - Wait for Harry's response

3. **Check Generated Insights**:
   ```bash
   cat conversations/20251116/conv_0001_*/insights.json
   ```

4. **View Context in Action**:
   ```bash
   python context_manager.py
   ```

---

## 🎉 Enjoy Your Harry Potter Voice Assistant!

Harry is now fully NPU-powered and ready to be your AI companion. He'll remember your conversations, learn your interests, and respond with authentic Harry Potter personality!

**Have fun chatting with Harry! ⚡**

