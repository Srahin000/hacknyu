@echo off
echo ============================================================
echo Setting up Offline TTS Environment (Python 3.10)
echo ============================================================

echo.
echo [1/4] Activating hacknyu_offline environment...
call conda activate hacknyu_offline

echo.
echo [2/4] Checking Python version...
python --version

echo.
echo [3/4] Installing core dependencies...
pip install qai-hub>=0.40.0 qai-hub-models>=0.17.0

echo.
echo [4/4] Installing AI/ML packages...
pip install torch transformers librosa sounddevice python-dotenv onnx onnxruntime

echo.
echo [5/5] Installing Coqui TTS (offline)...
pip install TTS

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Environment: hacknyu_offline (Python 3.10)
echo All packages installed including offline TTS
echo.
echo Next steps:
echo   1. Stay in this environment (already activated)
echo   2. Set your API key: $env:QAI_HUB_API_KEY="your_key"
echo   3. Run: python convert_emotion_model.py
echo   4. Run: python deploy.py --model models/emotion_wav2vec2
echo   5. Run: python setup_tts.py
echo.
echo ============================================================

pause

