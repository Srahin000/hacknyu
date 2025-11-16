# Emotion Detection on Snapdragon NPU

## 🎭 Overview

The voice assistant now includes **real-time emotion detection** that analyzes your voice and detects your emotional state using a Wav2Vec2 model running on the Snapdragon NPU.

## ✨ Features

- **7 Emotions Detected**: Happy, Sad, Angry, Fear, Disgust, Surprise, Neutral
- **NPU Accelerated**: ~40-80ms latency on Snapdragon X Elite
- **Offline**: No internet connection needed
- **Automatic Logging**: Emotion data saved in conversation metadata

## 🚀 Quick Start

### Test Emotion Detection

```powershell
# Test on existing audio files
python test_emotion_detection.py

# Or use the voice assistant (includes emotion detection)
python harry_voice_assistant.py --test
```

### See Results

After a conversation, check the transcript:

```powershell
# View latest conversation
$latest = Get-ChildItem conversations\*\conv_* | Sort-Object LastWriteTime | Select-Object -Last 1
Get-Content $latest\transcript.txt
```

Example output:
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

## 📊 Supported Emotions

| Emotion | Emoji | Common Triggers |
|---------|-------|-----------------|
| **Happy** | 😊 | Excited speech, upbeat tone |
| **Sad** | 😢 | Low energy, slower speech |
| **Angry** | 😠 | Loud, harsh tone |
| **Fear** | 😨 | Tense, uncertain voice |
| **Disgust** | 🤢 | Negative reactions |
| **Surprise** | 😲 | Sudden pitch changes |
| **Neutral** | 😐 | Normal conversation |

## 🔧 How It Works

### Processing Pipeline

1. **Audio Recording** → 8 seconds of your voice
2. **Emotion Detection** → NPU processes audio (~40-80ms)
3. **Speech-to-Text** → Whisper transcribes (parallel)
4. **LLM Response** → Harry generates reply
5. **Text-to-Speech** → Harry speaks

### Model Details

- **Architecture**: Wav2Vec2 (fine-tuned for emotion)
- **Input**: 16kHz mono audio, 3 seconds
- **Output**: 7 emotion probabilities + confidence scores
- **Accuracy**: 97.46% on test dataset
- **Latency**: 
  - NPU: 40-80ms
  - CPU fallback: 100-200ms

## 📁 Where Emotion Data is Saved

### 1. Transcript Files (`transcript.txt`)
```
EMOTION: HAPPY (85% confidence)

USER:
Hello Harry!
```

### 2. Metadata Files (`metadata.json`)
```json
{
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

## 💡 Use Cases

### 1. Educational AI
- Adapt responses based on student emotion
- Detect frustration → provide more help
- Detect happiness → encourage progress

### 2. Mental Health Monitoring
- Track emotional patterns over time
- Identify trends in mood
- Provide supportive responses

### 3. Customer Service
- Detect customer frustration
- Escalate to human agent if angry
- Provide empathetic responses

### 4. Research & Analysis
- Study emotional patterns in conversations
- Analyze emotion distribution
- Correlate emotions with topics

## 📈 Analyzing Emotion Data

### Python Script Example

```python
import json
from pathlib import Path
from collections import Counter

def analyze_emotions():
    """Analyze emotions from all conversations"""
    
    emotions = []
    
    # Load all metadata files
    for metadata_file in Path("conversations").rglob("metadata.json"):
        with open(metadata_file) as f:
            data = json.load(f)
        
        if "emotion" in data:
            emotions.append({
                "emotion": data["emotion"]["detected"],
                "confidence": data["emotion"]["confidence"],
                "timestamp": data["timestamp"],
                "query": data["user_query"]
            })
    
    # Count emotions
    emotion_counts = Counter(e["emotion"] for e in emotions)
    
    print(f"Total conversations: {len(emotions)}")
    print("\nEmotion Distribution:")
    for emotion, count in emotion_counts.most_common():
        percentage = (count / len(emotions)) * 100
        print(f"  {emotion:10s}: {count:3d} ({percentage:5.1f}%)")
    
    # Average confidence
    avg_confidence = sum(e["confidence"] for e in emotions) / len(emotions)
    print(f"\nAverage confidence: {avg_confidence*100:.1f}%")
    
    # Most confident predictions
    print("\nMost Confident Detections:")
    for e in sorted(emotions, key=lambda x: x["confidence"], reverse=True)[:5]:
        print(f"  {e['emotion']:10s} ({e['confidence']*100:.0f}%) - \"{e['query'][:50]}...\"")

if __name__ == "__main__":
    analyze_emotions()
```

### PowerShell Script Example

```powershell
# Count emotions in all conversations
$conversations = Get-ChildItem conversations\*\conv_*\metadata.json

$emotions = @()
foreach ($file in $conversations) {
    $data = Get-Content $file | ConvertFrom-Json
    if ($data.emotion) {
        $emotions += $data.emotion.detected
    }
}

# Show distribution
$emotions | Group-Object | Sort-Object Count -Descending | Format-Table Name, Count
```

## 🧪 Model Information

### Model Files
```
models/emotion_wav2vec2/
├── model.onnx       # ONNX model for NPU/CPU
├── labels.txt       # Emotion labels
└── config.json      # Model configuration
```

### Alternative Models

The project includes several emotion models:
- `emotion_wav2vec2/` - **Recommended** (best accuracy, NPU-optimized)
- `emotion_small/` - Smaller model (faster, lower accuracy)
- `emotion_ultra_tiny/` - Tiny model (very fast, basic accuracy)

To switch models, edit `emotion_npu.py`:
```python
detector = EmotionNPU(model_path="models/emotion_small/model.onnx")
```

## ⚙️ Configuration

### Disable Emotion Detection

If you don't want emotion detection, it will automatically skip if the model isn't available:

```python
# Emotion detection is optional
# If it fails to load, the assistant continues without it
```

### Adjust Audio Length

The emotion detector uses 3 seconds of audio by default. To change:

```python
# In emotion_npu.py
emotion_data = detector.detect_emotion(audio, sample_rate, target_length=5.0)
```

## 🐛 Troubleshooting

### "Emotion model not found"
```bash
# Check if model exists
ls models/emotion_wav2vec2/

# If missing, the model should already be there
# Check README.md for deployment instructions
```

### Emotion detection is slow
```python
# Check if using NPU
python test_emotion_detection.py

# Should show: inference_type="npu"
# If showing "cpu", the QNN provider isn't working
```

### Low confidence scores
- Short audio clips may have low confidence
- Background noise affects accuracy
- Clear speech gives best results

## 📚 Technical Details

### Audio Preprocessing
1. Resample to 16kHz (Wav2Vec2 requirement)
2. Pad or trim to target length (default: 3 seconds)
3. Normalize to [-1, 1] range
4. Add batch dimension

### Inference Process
1. Input: `(1, 48000)` float32 array (3s @ 16kHz)
2. Wav2Vec2 feature extraction
3. Emotion classification head
4. Softmax → 7 emotion probabilities
5. Return top emotion + confidence

### Performance Optimization
- **NPU Execution**: QNNExecutionProvider for hardware acceleration
- **Parallel Processing**: Emotion detection can run alongside STT
- **Caching**: Audio preprocessing optimized for speed

## 🔮 Future Enhancements

Potential improvements:
- [ ] Emotion-aware TTS (adjust Harry's voice based on user emotion)
- [ ] Multi-modal emotion (combine audio + text analysis)
- [ ] Real-time emotion tracking (continuous monitoring)
- [ ] Emotion history visualization (charts/graphs)
- [ ] Personalized emotion models (adapt to individual users)

## 📖 References

- **Wav2Vec2**: [Facebook AI Research](https://ai.facebook.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)
- **Emotion Recognition**: [RAVDESS Dataset](https://zenodo.org/record/1188976)
- **ONNX Runtime**: [Microsoft ONNX Runtime](https://onnxruntime.ai/)
- **QNN Provider**: [Qualcomm Neural Network SDK](https://developer.qualcomm.com/software/qualcomm-neural-processing-sdk)

---

**Questions or issues?** Check the main [README.md](README.md) or [VOICE_ASSISTANT_GUIDE.md](VOICE_ASSISTANT_GUIDE.md).

