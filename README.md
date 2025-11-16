# Offline AI Companion - Snapdragon NPU Deployment

Educational AI companion for children that runs 100% offline using Snapdragon NPU acceleration.

## 🎉 NEW: Complete Voice Assistant!

**Harry Potter Voice Assistant** - Full voice-to-voice conversation pipeline:
- Wake word detection → Speech recognition → AI response → Voice output
- Run it now: `python harry_voice_assistant.py --test`
- Full guide: [VOICE_ASSISTANT_GUIDE.md](VOICE_ASSISTANT_GUIDE.md)

## Features

- **Voice Assistant** - Complete voice-to-voice AI conversation
- Speech-to-Text (Whisper) on NPU (~44ms latency)
- Emotion Recognition (Wav2Vec2) on NPU (97.46% accuracy)
- Text-to-Speech with pyttsx3 (offline)
- Custom wake word detection ("Harry Potter")
- LLM responses with Llama 3.2 (CPU-optimized)
- Real-time Unity avatar integration
- Local storage with Snowflake sync

## Quick Start

### 🎤 Voice Assistant (Ready Now!)

```powershell
# 1. Check system readiness
python check_voice_assistant_ready.py

# 2. Run in test mode (recommended first time)
python harry_voice_assistant.py --test

# 3. Run with wake word
python harry_voice_assistant.py

# Or use the launcher
start_harry_voice.bat
```

See [VOICE_ASSISTANT_GUIDE.md](VOICE_ASSISTANT_GUIDE.md) for complete setup!

### 🚀 NPU Deployment (Advanced)

#### Prerequisites

- Python 3.10 (required for some TTS options)
- Qualcomm AI Hub API Key ([get one here](https://app.aihub.qualcomm.com/))
- Snapdragon NPU-enabled device (e.g., Samsung Galaxy S24)

#### Installation

```powershell
# Create Python 3.10 environment
conda create -n hacknyu_offline python=3.10 -y
conda activate hacknyu_offline

# Install dependencies
pip install -r requirements.txt

# Set up API key in .env file
QAI_HUB_API_KEY=your_api_key_here
TARGET_DEVICE=Samsung Galaxy S24
```

### Deploy Models

```powershell
# 1. Convert emotion model
python convert_emotion_model.py

# 2. Deploy to NPU (takes 10-30 min)
python deploy_fixed.py --model models/emotion_wav2vec2/model.onnx

# 3. Test everything
python test_emotion_inference.py
python check_device.py
```

## Project Structure

```
HackNYU/
├── deploy_fixed.py          # Model deployment (corrected SDK API)
├── deploy.py                # Original deployment script
├── config.py                # Configuration
├── convert_emotion_model.py # Convert Wav2Vec2 to ONNX
├── check_device.py          # Verify device connection
├── test_emotion_inference.py # Test emotion model
├── requirements.txt         # Python dependencies
├── .env                     # API keys (create this)
├── models/                  # ONNX models
├── deployed_models/         # Compiled NPU models
└── ppn_files/              # Picovoice wake word files
```

## Documentation

See **[GUIDE.md](GUIDE.md)** for complete documentation including:
- Detailed setup instructions
- Model deployment workflow
- NPU compilation guide
- Performance optimization
- Troubleshooting
- Full system architecture

## Performance

| Component | Device | Latency | Offline |
|-----------|--------|---------|---------|
| Wake Word | NPU | <50ms | ✅ |
| STT (Whisper) | NPU | ~44ms | ✅ |
| Emotion (Wav2Vec2) | NPU | ~80ms | ✅ |
| TTS (Picovoice Orca) | CPU | ~500ms | ✅ |
| **Total Pipeline** | Mixed | **<1s** | **✅** |

## Support

- **Qualcomm AI Hub**: [Documentation](https://app.aihub.qualcomm.com/docs/index.html)
- **Full Guide**: See [GUIDE.md](GUIDE.md)
- **Issues**: Check troubleshooting section in GUIDE.md

## License

Educational and development purposes. See individual model licenses for commercial use.
