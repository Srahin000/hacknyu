@echo off
echo ============================================================
echo Fast Dependency Installation (Python 3.10)
echo ============================================================
echo.
echo Press Ctrl+C now if you want to stop pip backtracking first!
timeout /t 5

echo.
echo [Step 1/5] Installing PyTorch (largest package first)...
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

echo.
echo [Step 2/5] Installing Qualcomm AI Hub...
pip install qai-hub==0.40.0 qai-hub-models==0.17.0

echo.
echo [Step 3/5] Installing ML/Audio packages...
pip install transformers==4.35.0 librosa==0.10.1 sounddevice==0.4.6

echo.
echo [Step 4/5] Installing ONNX...
pip install onnx==1.15.0 onnxruntime==1.16.3

echo.
echo [Step 5/5] Installing TTS (this one takes time)...
pip install TTS==0.22.0

echo.
echo [Bonus] Installing utilities...
pip install numpy requests python-dotenv

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Test it:
echo   python -c "from TTS.api import TTS; print('TTS works!')"
echo   python -c "import qai_hub; print('AI Hub works!')"
echo.
pause

