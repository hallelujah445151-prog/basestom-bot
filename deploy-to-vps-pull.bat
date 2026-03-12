@echo off
chcp 65001 >nul 2>&1
echo ===========================================
echo   Deploy to VPS - Git Pull
echo ===========================================
echo.

echo Pulling latest code from GitHub...
echo.

cd /d "%~dp0"
git pull origin master

if errorlevel 1 (
    echo [ERROR] Failed to pull from GitHub
    echo.
    pause
    exit /b 1
)

echo [OK] Code updated from GitHub
echo.

echo Restarting bot on VPS...
echo.

ssh root@31.129.99.125 "cd /opt/basestom-bot && git pull origin master && supervisorctl restart basestom-bot"

if errorlevel 1 (
    echo [ERROR] Failed to restart bot
    echo.
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   Deployment completed!
echo ===========================================
echo.
echo Check bot in Telegram:
echo 1. Find bot: @sfdtgafvdba_bot
echo 2. Send: /start
echo.
pause
