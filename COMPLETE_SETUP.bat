@echo off
REM ============================================================
REM HackNYU - Complete Environment Setup Script
REM This script recreates the entire development environment
REM ============================================================

echo.
echo ============================================================
echo HackNYU - AI Companion Setup (Complete)
echo ============================================================
echo.
echo This will set up:
echo   - Python dependencies (without TTS)
echo   - Qualcomm AI Hub configuration
echo   - Model directories
echo   - Environment verification
echo.
pause

REM ============================================================
REM Step 1: Check Python Version
REM ============================================================
echo.
echo [Step 1/6] Checking Python version...
python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python 3.10+ required!
    echo Current Python version is too old.
    echo.
    echo Please install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo ✓ Python version OK

REM ============================================================
REM Step 2: Install Dependencies (No TTS)
REM ============================================================
echo.
echo [Step 2/6] Installing dependencies (without TTS)...
echo This may take 5-10 minutes depending on your internet...
echo.

echo Installing PyTorch (CPU version)...
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

echo Installing Qualcomm AI Hub...
pip install qai-hub==0.40.0 qai-hub-models==0.17.0

echo Installing Transformers...
pip install transformers==4.35.0

echo Installing Audio processing...
pip install librosa==0.10.1 sounddevice==0.4.6

echo Installing ONNX Runtime...
pip install onnx==1.15.0 onnxruntime==1.16.3

echo Installing utilities...
pip install numpy==1.24.3 requests==2.31.0 python-dotenv==1.0.0

echo.
echo ✓ Dependencies installed

REM ============================================================
REM Step 3: Create Directory Structure
REM ============================================================
echo.
echo [Step 3/6] Creating directory structure...

if not exist "models" mkdir models
if not exist "deployed_models" mkdir deployed_models
if not exist "logs" mkdir logs
if not exist "profiles" mkdir profiles

echo ✓ Directories created

REM ============================================================
REM Step 4: Setup .env File
REM ============================================================
echo.
echo [Step 4/6] Setting up .env configuration...

if exist ".env" (
    echo .env file already exists - skipping creation
) else (
    echo Creating .env file...
    (
        echo # Qualcomm AI Hub Configuration
        echo # Get your API key from: https://app.aihub.qualcomm.com/
        echo QAI_HUB_API_KEY=your_api_key_here
        echo.
        echo # Target Device
        echo TARGET_DEVICE=Samsung Galaxy S24
    ) > .env
    echo ✓ Created .env file - PLEASE EDIT IT WITH YOUR API KEY!
)

REM ============================================================
REM Step 5: Verify Installation
REM ============================================================
echo.
echo [Step 5/6] Verifying installation...

python -c "import torch; print('✓ PyTorch:', torch.__version__)"
python -c "import qai_hub; print('✓ QAI Hub installed')"
python -c "import transformers; print('✓ Transformers:', transformers.__version__)"
python -c "import librosa; print('✓ Librosa installed')"
python -c "import onnxruntime; print('✓ ONNX Runtime installed')"
python -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"

echo.
echo ✓ All packages verified

REM ============================================================
REM Step 6: Display Next Steps
REM ============================================================
echo.
echo [Step 6/6] Setup Complete!
echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo.
echo 1. Edit .env file with your API key:
echo    notepad .env
echo.
echo 2. Get your API key from:
echo    https://app.aihub.qualcomm.com/
echo.
echo 3. Verify connection:
echo    python check_device.py
echo.
echo 4. Convert emotion model:
echo    python convert_emotion_model.py
echo.
echo 5. Deploy to NPU:
echo    python deploy.py --model models/emotion_wav2vec2
echo.
echo ============================================================
echo Optional: Install TTS later
echo ============================================================
echo.
echo If you want Text-to-Speech, you have two options:
echo.
echo Option A: Edge-TTS (lightweight, requires internet)
echo    pip install edge-tts
echo.
echo Option B: Coqui TTS (offline, requires Visual C++ Build Tools)
echo    1. Download Visual C++ Build Tools:
echo       https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo    2. Install "Desktop development with C++" (~6GB)
echo    3. Run: pip install TTS
echo.
echo ============================================================
echo.
pause


