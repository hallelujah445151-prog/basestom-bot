@echo off
chcp 65001 >nul
setlocal

cls
echo.
echo ==========================================
echo    Database Synchronization
echo ==========================================
echo.

REM Determine script directory
set "SCRIPT_DIR=%~dp0"
set "LOCAL_DB=%SCRIPT_DIR%data\orders.db"
set "LOCAL_BACKUP=%SCRIPT_DIR%data\orders.db.server"
set "TIMESTAMP=%date:~0,2%.%date:~3,2%.%date:~6,4%_%time:~0,2%.%time:~3,2%.%time:~6,2%"

echo Local DB: %LOCAL_DB%
echo.

REM Check if local database exists
if not exist "%LOCAL_DB%" (
    echo [ERROR] Local database not found!
    echo.
    echo Path: %LOCAL_DB%
    echo.
    echo Please check if the file exists.
    pause
    exit /b 1
)

echo [OK] Local database found
echo.
echo ==========================================
echo    VPS Connection Info
echo ==========================================
echo.
echo VPS IP:      31.129.99.125
echo VPS User:    root
echo VPS DB:      /opt/basestom-bot/data/orders.db
echo.

REM Test SSH connection
echo Testing SSH connection...
ssh -o ConnectTimeout=5 root@31.129.99.125 "echo 'SSH connection OK'" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot connect to VPS!
    echo.
    echo Please check:
    echo   - Internet connection
    echo   - VPN is active
    echo   - VPS is running
    echo.
    pause
    exit /b 1
)
echo [OK] SSH connection successful
echo.

REM Check SCP command
echo Checking SCP command...
where scp >nul 2>&1
if errorlevel 1 (
    echo [ERROR] SCP command not found!
    echo.
    echo Please install Git for Windows or OpenSSH for Windows
    echo.
    pause
    exit /b 1
)
echo [OK] SCP command found
echo.

REM Choose direction
echo ==========================================
echo    Choose direction
echo ==========================================
echo.
echo 1. Server -^> Local computer (download)
echo 2. Local computer -^> Server (upload)
echo 3. Cancel
echo.
set /p "direction=Enter your choice (1-3): "

if "%direction%"=="3" (
    echo.
    echo ==========================================
    echo    CANCELLED
    echo ==========================================
    echo.
    pause
    exit /b 0
)

if "%direction%"=="1" goto DOWNLOAD
if "%direction%"=="2" goto UPLOAD

echo [ERROR] Invalid choice!
pause
exit /b 1

:DOWNLOAD
cls
echo.
echo ==========================================
echo    Downloading from Server
echo ==========================================
echo.

REM Create local backup
echo [INFO] Creating local backup...
copy "%LOCAL_DB%" "%LOCAL_DB%.%TIMESTAMP%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create backup!
    pause
    exit /b 1
)
echo [OK] Backup created: orders.db.%TIMESTAMP%
echo.

echo [STEP 1] Stopping bot on server...
ssh root@31.129.99.125 "supervisorctl stop basestom-bot"
if errorlevel 1 (
    echo [ERROR] Failed to stop bot on server
    pause
    exit /b 1
)
echo [OK] Bot stopped
echo.

echo [STEP 2] Downloading database...
scp root@31.129.99.125:/opt/basestom-bot/data/orders.db "%LOCAL_BACKUP%"
if errorlevel 1 (
    echo [ERROR] Failed to download database!
    echo.
    echo Attempting to start bot on server...
    ssh root@31.129.99.125 "supervisorctl start basestom-bot"
    pause
    exit /b 1
)
echo [OK] Database downloaded
echo.

echo [STEP 3] Starting bot on server...
ssh root@31.129.99.125 "supervisorctl start basestom-bot"
if errorlevel 1 (
    echo [WARNING] Failed to start bot on server
    echo Please check logs on server
) else (
    echo [OK] Bot started
)
echo.

cls
echo.
echo ==========================================
echo    Sync completed!
echo ==========================================
echo.
echo Files:
echo   * Server DB:   %LOCAL_BACKUP%
echo   * Local DB:    %LOCAL_DB%
echo.
echo To use downloaded database:
echo   1. Close local bot (if running)
echo   2. Replace %LOCAL_DB% with %LOCAL_BACKUP%
echo   3. Start bot locally
echo.
pause
exit /b 0

:UPLOAD
cls
echo.
echo ==========================================
echo    Uploading to Server
echo ==========================================
echo.

echo [WARNING] This will replace the server database!
echo.
set /p "confirm=Confirm replacement? (yes/no): "

if /i not "%confirm%"=="yes" (
    cls
    echo.
    echo ==========================================
    echo    CANCELLED
    echo ==========================================
    echo.
    pause
    exit /b 0
)

echo.
echo [STEP 1] Creating server backup...
ssh root@31.129.99.125 "cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup"
if errorlevel 1 (
    echo [WARNING] Failed to create backup, continuing...
) else (
    echo [OK] Backup created on server
)
echo.

echo [STEP 2] Stopping bot on server...
ssh root@31.129.99.125 "supervisorctl stop basestom-bot"
if errorlevel 1 (
    echo [ERROR] Failed to stop bot on server
    pause
    exit /b 1
)
echo [OK] Bot stopped
echo.

echo [STEP 3] Uploading database...
scp "%LOCAL_DB%" root@31.129.99.125:/opt/basestom-bot/data/orders.db.upload
if errorlevel 1 (
    echo [ERROR] Failed to upload database!
    echo.
    echo Attempting to start bot on server...
    ssh root@31.129.99.125 "supervisorctl start basestom-bot"
    pause
    exit /b 1
)
echo [OK] Database uploaded
echo.

echo [STEP 4] Replacing database...
ssh root@31.129.99.125 "mv /opt/basestom-bot/data/orders.db.upload /opt/basestom-bot/data/orders.db"
if errorlevel 1 (
    echo [WARNING] Failed to replace database
    echo Database uploaded as: /opt/basestom-bot/data/orders.db.upload
) else (
    echo [OK] Database replaced
)
echo.

echo [STEP 5] Starting bot on server...
ssh root@31.129.99.125 "supervisorctl start basestom-bot"
if errorlevel 1 (
    echo [WARNING] Failed to start bot on server
    echo Please check logs on server
) else (
    echo [OK] Bot started
)
echo.

cls
echo.
echo ==========================================
echo    Sync completed!
echo ==========================================
echo.
echo Database uploaded to server and replaced
echo Server backup: /opt/basestom-bot/data/orders.db.backup
echo.
pause
exit /b 0
