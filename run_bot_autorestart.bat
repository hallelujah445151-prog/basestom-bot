@echo off
REM Auto-restart bot script for Windows
REM This will restart the bot if it crashes

echo Basestom Bot Auto-Restart Script
echo ==================================
echo.

:LOOP
echo Starting bot...
echo.

python src\bot.py

echo.
echo Bot stopped or crashed!
echo Restarting in 10 seconds...
echo.

timeout /t 10 /nobreak > nul

echo.
goto LOOP
