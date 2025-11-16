"""
Configuration file for Qualcomm AI Hub model deployment
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Qualcomm AI Hub API Configuration
# Priority: 1) .env file, 2) Environment variable, 3) Default value
# Get your API key from: https://app.aihub.qualcomm.com/
QAI_HUB_API_KEY = os.getenv("QAI_HUB_API_KEY", "")
QAI_HUB_API_URL = "https://app.aihub.qualcomm.com"

# Target Device Configuration
# Available devices: "Samsung Galaxy S24", "Samsung Galaxy S23", etc.
# Device names use title case with spaces (not hyphens)
# Check https://aihub.qualcomm.com for available devices
# Run: python check_device.py to see all available devices
TARGET_DEVICE = os.getenv("TARGET_DEVICE", "Samsung Galaxy S24")

# Model Configuration
MODELS = {
    "stt": {
        "name": "whisper_small_quantized",
        "model_class": "WhisperSmallQuantized",
        "input_shape": (1, 80, 3000),  # (batch, mel_bins, time_frames)
        "input_dtype": "float32",
        "max_latency_ms": 200,
    },
    "emotion": {
        "name": "audio_emotion_recognition",
        "model_class": "AudioEmotionModel",
        "input_shape": (1, 1, 16000),  # (batch, channels, samples) - 1 second @ 16kHz
        "input_dtype": "float32",
        "max_latency_ms": 100,  # Real-time requirement
        "max_size_mb": 50,  # Adjust X as needed
    },
    "tts": {
        "name": "text_to_speech",
        "model_class": "TTSModel",
        "input_shape": (1, 512),  # (batch, text_embedding)
        "input_dtype": "int32",
        "max_latency_ms": 200,
    }
}

# Deployment Settings
DEPLOYMENT_SETTINGS = {
    "compilation_timeout": 3600,  # 1 hour
    "profile_timeout": 600,  # 10 minutes
    "validation_tolerance": 1e-3,  # Max difference for output validation
    "enable_quantization": True,
    "optimization_level": "high",
}

# Output Directories
OUTPUT_DIR = "deployed_models"
LOGS_DIR = "logs"
PROFILES_DIR = "profiles"

