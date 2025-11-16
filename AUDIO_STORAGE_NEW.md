# Audio Storage System - UPDATED

## 📁 New Organization (November 2025)

The voice assistant now uses a **clean separation** between TTS responses and user recordings:

```
audio/                                    ← TTS RESPONSES ONLY (Harry's voice)
├── harry_tts_20251116_203045_conv0001.wav
├── harry_tts_20251116_203045_conv0001.txt
├── harry_tts_20251116_203152_conv0002.wav
├── harry_tts_20251116_203152_conv0002.txt
└── ...

conversations/                            ← FULL CONVERSATIONS (organized)
├── 20251116/                             ← Date folder
│   ├── conv_0001_203045/                 ← Conversation #1
│   │   ├── user_audio.wav                ← Your voice recording
│   │   ├── harry_audio.wav               ← Harry's TTS response
│   │   ├── transcript.txt                ← Full conversation + emotion
│   │   ├── harry_response.txt            ← Just Harry's text
│   │   └── metadata.json                 ← Complete metadata + emotion data
│   │
│   ├── conv_0002_203152/                 ← Conversation #2
│   │   ├── user_audio.wav
│   │   ├── harry_audio.wav
│   │   ├── transcript.txt
│   │   ├── harry_response.txt
│   │   └── metadata.json
│   └── ...
└── ...
```

## 🎯 Key Changes

### Before (Confusing):
- ❌ Both user audio AND TTS audio in `audio/` folder
- ❌ Hard to tell which files are which
- ❌ No emotion detection

### After (Clean):
- ✅ `audio/` folder = **TTS responses ONLY** (Harry's voice)
- ✅ `conversations/` folder = **Complete conversations** (user + Harry + emotion)
- ✅ **Emotion detection** integrated (NPU-accelerated)

## 📝 File Naming

### TTS Audio (in `audio/` folder):
```
harry_tts_YYYYMMDD_HHMMSS_conv####.wav
harry_tts_YYYYMMDD_HHMMSS_conv####.txt
```

Example:
- `harry_tts_20251116_203045_conv0001.wav` = Harry's TTS voice, Nov 16 2025, 8:30:45 PM
- `harry_tts_20251116_203045_conv0001.txt` = What Harry said (text)

### Conversation Files (in `conversations/YYYYMMDD/conv_####_HHMMSS/`):
```
user_audio.wav        ← Your voice recording
harry_audio.wav       ← Harry's TTS response (copy from audio/)
transcript.txt        ← Full conversation with emotion
harry_response.txt    ← Just Harry's response text
metadata.json         ← Complete conversation metadata
```

## 😊 Emotion Detection

Every conversation now includes **emotion detection** on your voice!

### In `transcript.txt`:
```
Conversation #1
Timestamp: 2025-11-16 20:30:45
======================================================================

EMOTION: HAPPY (85% confidence)

USER:
Hello Harry, how are you?

HARRY:
Hello! I'm doing great, thanks for asking!
```

### In `metadata.json`:
```json
{
  "conversation_id": 1,
  "timestamp": "2025-11-16T20:30:45.123456",
  "user_query": "Hello Harry, how are you?",
  "harry_response": "Hello! I'm doing great, thanks for asking!",
  "emotion_type": "npu",
  "emotion": {
    "detected": "happy",
    "confidence": 0.85,
    "latency_ms": 42,
    "all_scores": {
      "happy": 0.85,
      "neutral": 0.08,
      "sad": 0.03,
      "angry": 0.02,
      "fear": 0.01,
      "disgust": 0.01,
      "surprise": 0.00
    }
  }
}
```

## 🎤 Supported Emotions

The NPU emotion model detects 7 emotions:
1. **Happy** 😊
2. **Sad** 😢
3. **Angry** 😠
4. **Fear** 😨
5. **Disgust** 🤢
6. **Surprise** 😲
7. **Neutral** 😐

## 💾 What Gets Saved

### For EVERY Conversation:

| Content | audio/ folder | conversations/ folder |
|---------|--------------|----------------------|
| **Your voice** | ❌ | ✅ `user_audio.wav` |
| **Harry's voice** | ✅ `harry_tts_*.wav` | ✅ `harry_audio.wav` (copy) |
| **Transcripts** | ✅ `harry_tts_*.txt` | ✅ `transcript.txt` + `harry_response.txt` |
| **Emotion data** | ❌ | ✅ In `transcript.txt` + `metadata.json` |
| **Metadata** | ❌ | ✅ `metadata.json` |

## 🚀 Usage Examples

### Get All TTS Audio Files
```powershell
# All Harry's voice responses
Get-ChildItem audio\harry_tts_*.wav

# Export for training
Copy-Item audio\harry_tts_*.wav -Destination D:\TTS_Training\
```

### Review a Conversation
```powershell
# View transcript with emotion
Get-Content conversations\20251116\conv_0001_203045\transcript.txt

# Play user audio
Start-Process conversations\20251116\conv_0001_203045\user_audio.wav

# Play Harry's response
Start-Process conversations\20251116\conv_0001_203045\harry_audio.wav

# Check metadata
Get-Content conversations\20251116\conv_0001_203045\metadata.json | ConvertFrom-Json
```

### Find Conversations by Emotion
```python
import json
from pathlib import Path

def find_by_emotion(target_emotion):
    """Find all conversations with a specific emotion"""
    results = []
    
    for metadata_file in Path("conversations").rglob("metadata.json"):
        with open(metadata_file) as f:
            data = json.load(f)
        
        if "emotion" in data and data["emotion"]["detected"] == target_emotion:
            results.append({
                "conversation": data["conversation_id"],
                "timestamp": data["timestamp"],
                "user_query": data["user_query"],
                "emotion_confidence": data["emotion"]["confidence"]
            })
    
    return results

# Find all happy conversations
happy_convos = find_by_emotion("happy")
for convo in happy_convos:
    print(f"Conv #{convo['conversation']}: {convo['user_query']}")
    print(f"  Confidence: {convo['emotion_confidence']*100:.0f}%")
```

## 📊 Storage Details

### Audio Quality:
- **User audio**: 16kHz mono WAV (Whisper input format)
- **Harry's audio**: 22kHz stereo WAV (XTTS v2 output)

### Disk Space (per conversation):
- User recording (8 sec): ~250 KB
- Harry's audio (varies): ~200-500 KB per response
- Metadata + text: ~5 KB

### Example Session (10 conversations):
- TTS audio in `audio/`: ~3-5 MB
- Full conversations: ~8-12 MB (includes user audio + TTS copies + metadata)

## ⚙️ Model Performance

### Emotion Detection:
- **NPU mode**: ~40-80ms latency per audio sample
- **Accuracy**: 97.46% on test dataset (Wav2Vec2)
- **Works offline**: No internet needed

### When Does Emotion Detection Run?
- After you finish speaking
- Before transcription starts
- Runs in parallel with Whisper STT (if on NPU)

## 🔧 Troubleshooting

### Emotion detection not working?
```bash
# Test emotion model directly
python emotion_npu.py

# Check if model exists
ls models/emotion_wav2vec2/
```

### Clean up old audio files?
```powershell
# Remove old user audio files from audio/ folder (if you have any from before)
Remove-Item audio\user_*.wav
Remove-Item audio\user_*.txt
```

## 📚 Related Files

- `harry_voice_assistant.py` - Main voice assistant with emotion integration
- `emotion_npu.py` - Emotion detection NPU wrapper
- `VOICE_ASSISTANT_GUIDE.md` - Complete voice assistant guide
- `README.md` - Project overview

