@echo off
echo ============================================================
echo MINIMAL Install (Skip TTS for now - install it later)
echo ============================================================

echo.
echo [1/4] PyTorch...
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

echo.
echo [2/4] Qualcomm AI Hub...
pip install qai-hub qai-hub-models

echo.
echo [3/4] ML packages...
pip install transformers librosa sounddevice onnxruntime python-dotenv

echo.
echo [4/4] Done! TTS skipped for now.
echo.
echo You can install TTS later when needed:
echo   pip install TTS
echo.
echo ============================================================
pause

