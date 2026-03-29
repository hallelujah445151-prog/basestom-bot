@echo off
chcp 65001 >nul 2>&1
echo ===========================================
echo   Test Bot - Simple Version
echo ===========================================
echo.

echo [OK] .env file found
echo.

echo Starting test bot...
echo Press Ctrl+C to stop
echo.

python src\test_bot.py

if errorlevel 1 (
    echo.
    echo [ERROR] Bot stopped with error
    pause
)
