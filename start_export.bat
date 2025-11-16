@echo off
echo ======================================================================
echo EXPORT LLAMA 3.2 1B FOR NPU (Harry Potter AI)
echo ======================================================================
echo.
echo This will:
echo   1. Install qai-hub-models with Llama dependencies
echo   2. Export Llama 3.2 1B for Snapdragon X Elite NPU
echo   3. Create harry_genie_bundle folder
echo.
echo WARNING: This takes 2-3 HOURS and uses lots of memory!
echo          Let it run and come back later.
echo.
echo ======================================================================
echo.

REM Activate conda environment
echo [1/3] Activating Python environment...
call conda activate hacknyu_offline
if errorlevel 1 (
    echo ERROR: Failed to activate hacknyu_offline environment
    echo Run: conda create -n hacknyu_offline python=3.10 -y
    pause
    exit /b 1
)
echo    ✓ Environment activated
echo.

REM Install dependencies
echo [2/3] Installing qai-hub-models with Llama support...
echo    (This may take 5-10 minutes)
pip install "qai-hub-models[llama-v3-2-1b-instruct]"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    ✓ Dependencies installed
echo.

REM Export model
echo [3/3] Exporting Llama 3.2 1B for Snapdragon X Elite NPU...
echo.
echo Model Details:
echo   - Llama 3.2 1B Instruct
echo   - Pre-quantized (4-bit/8-bit weights)
echo   - Optimized for Snapdragon X Elite
echo   - Output: harry_genie_bundle folder
echo.
echo    ⏳ THIS WILL TAKE 2-3 HOURS! ⏳
echo    You can minimize this window and come back later.
echo.
python -m qai_hub_models.models.llama_v3_2_1b_instruct.export --chipset qualcomm-snapdragon-x-elite --skip-profiling --output-dir harry_genie_bundle

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo ERROR: Export failed!
    echo ======================================================================
    echo.
    echo Common issues:
    echo   1. Need Hugging Face account and Llama 3.2 access
    echo      Visit: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
    echo.
    echo   2. Need to login to Hugging Face:
    echo      pip install -U "huggingface_hub[cli]"
    echo      huggingface-cli login
    echo.
    echo   3. Not enough memory
    echo      Close other programs and try again
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo ✅ SUCCESS! Harry's NPU brain is ready!
echo ======================================================================
echo.
echo Bundle created at: harry_genie_bundle\
echo.
echo Next steps:
echo   1. Make sure QAIRT SDK is installed and configured
echo   2. Run: python harry_npu_genie.py
echo   3. Chat with Harry Potter at ~500ms latency!
echo.
echo ======================================================================
pause

