@echo off
REM Start Harry Potter Voice Assistant
REM Quick launcher with system check

echo.
echo ========================================
echo   HARRY POTTER VOICE ASSISTANT
echo ========================================
echo.

REM Check if conda env is active
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo.
    echo Please activate your conda environment first:
    echo   conda activate hacknyu_offline
    echo.
    pause
    exit /b 1
)

echo Current environment: %CONDA_DEFAULT_ENV%
echo.

REM Run system check first
echo Running system check...
echo.
python check_voice_assistant_ready.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo System check completed with warnings.
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b
)

echo.
echo ========================================
echo   STARTING VOICE ASSISTANT
echo ========================================
echo.
echo Choose mode:
echo   1. Full Mode (with wake word detection)
echo   2. Test Mode (press ENTER to record)
echo   3. Cancel
echo.

choice /C 123 /N /M "Select mode (1/2/3): "

if errorlevel 3 (
    echo.
    echo Cancelled.
    exit /b 0
)

if errorlevel 2 (
    echo.
    echo Starting TEST MODE...
    echo.
    python harry_voice_assistant.py --test
    exit /b 0
)

if errorlevel 1 (
    echo.
    echo Starting FULL MODE...
    echo.
    echo Say "HARRY POTTER" to activate!
    echo.
    python harry_voice_assistant.py
    exit /b 0
)


