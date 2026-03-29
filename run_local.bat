@echo off
chcp 65001 >nul 2>&1
echo ===========================================
echo   Start Bot Locally
echo ===========================================
echo.

REM Check if .env exists
if not exist "src\.env" (
    echo [ERROR] src\.env file not found!
    echo.
    echo Create src\.env file with:
    echo BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
    echo OPENROUTER_API_KEY=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
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

REM Check dependencies
python -c "import telegram, dotenv, openai" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not installed!
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt

    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Dependencies installed
echo.

echo Starting bot...
echo Press Ctrl+C to stop
echo.
python src\bot.py

if errorlevel 1 (
    echo.
    echo [ERROR] Bot stopped with error
    pause
)

echo.
echo Bot stopped. Press any key to close...
pause
