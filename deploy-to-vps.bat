@echo off
echo ===========================================
echo   Auto deploy to VPS
echo ===========================================
echo.

REM Check required commands
where scp >nul 2>&1
if errorlevel 1 (
    echo [ERROR] scp command not found!
    echo.
    echo Install Git for Windows or OpenSSH for Windows
    echo.
    pause
    exit /b 1
)

where ssh >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ssh command not found!
    echo.
    echo Install Git for Windows or OpenSSH for Windows
    echo.
    pause
    exit /b 1
)

echo IP: 31.129.99.125
echo User: root
echo.
echo First connection requires password
echo Password: ^&PJc52K5gNG4
echo.
pause

echo.
echo Checking src\.env file...
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

echo [OK] src\.env file found
echo.

REM Set variables
set VPS_IP=31.129.99.125
set VPS_USER=root
set VPS_PATH=/opt/basestom-bot

echo Deploying to VPS...
echo IP: %VPS_IP%
echo User: %VPS_USER%
echo Enter password: ^&PJc52K5gNG4
echo.

REM Create archive
echo Creating project archive...

REM Change to script directory
cd /d "%~dp0"

echo Current directory: %CD%

REM Using git push and clone on VPS instead of archive
echo Skipping archive creation - will use git clone on VPS

echo [OK] Archive creation skipped

REM Push to GitHub first
echo Pushing latest changes to GitHub...
cd /d "%~dp0"
git add -A
git commit -m "Deploy update - %date% %time%" || echo [INFO] No changes to commit
git push origin master

if errorlevel 1 (
    echo [ERROR] Failed to push to GitHub
    pause
    exit /b 1
)

echo [OK] Code pushed to GitHub
echo.

echo Installing and configuring on VPS...
echo Enter password: ^&PJc52K5gNG4
echo.

REM Execute commands on VPS
echo Step 1: Updating system and installing git...
ssh %VPS_USER%@%VPS_IP% "apt update && apt upgrade -y && apt install -y python3 python3-pip python3-venv git supervisor"

if errorlevel 1 (
    echo [ERROR] Failed to update system
    pause
    exit /b 1
)

echo Step 2: Cloning from GitHub...
ssh %VPS_USER%@%VPS_IP% "rm -rf %VPS_PATH% && git clone https://github.com/hallelujah445151-prog/basestom-bot.git %VPS_PATH%"

if errorlevel 1 (
    echo [ERROR] Failed to clone from GitHub
    pause
    exit /b 1
)

echo Step 3: Creating .env file on VPS...
ssh %VPS_USER%@%VPS_IP% "echo 'BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8' > %VPS_PATH%/src/.env && echo 'OPENROUTER_API_KEY=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' >> %VPS_PATH%/src/.env"

if errorlevel 1 (
    echo [ERROR] Failed to create .env file
    pause
    exit /b 1
)

echo Step 4: Creating virtual environment...
ssh %VPS_USER%@%VPS_IP% "cd %VPS_PATH% && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo Step 5: Configuring Supervisor...
ssh %VPS_USER%@%VPS_IP% "cd %VPS_PATH% && sed 's/your_username/root/g' supervisor.conf > /etc/supervisor/conf.d/basestom-bot.conf && supervisorctl reread && supervisorctl update"

if errorlevel 1 (
    echo [ERROR] Failed to configure Supervisor
    pause
    exit /b 1
)

echo Step 6: Starting bot...
ssh %VPS_USER%@%VPS_IP% "supervisorctl stop basestom-bot 2>nul || true && supervisorctl start basestom-bot && supervisorctl status basestom-bot"

if errorlevel 1 (
    echo [ERROR] Failed to start bot
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   [OK] Deploy completed successfully!
echo ===========================================
echo.
echo Check bot in Telegram:
echo 1. Find bot: @sfdtgafvdba_bot
echo 2. Send: /start
echo.
echo Commands on VPS:
echo   Start:   supervisorctl start basestom-bot
echo   Stop:    supervisorctl stop basestom-bot
echo   Restart: supervisorctl restart basestom-bot
echo   Status:  supervisorctl status basestom-bot
echo   Logs:    supervisorctl tail -f basestom-bot
echo.
echo Connect to VPS:
echo   ssh %VPS_USER%@%VPS_IP%
echo.
pause
