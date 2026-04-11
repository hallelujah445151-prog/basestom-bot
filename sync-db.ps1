# Database Synchronization Script (PowerShell) - Fixed Version
$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
Set-Location $scriptDir

Clear-Host

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Database Synchronization" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

$localDbPath = Join-Path -Path $scriptDir -ChildPath "data\orders.db"
$localBackupPath = Join-Path -Path $scriptDir -ChildPath "data\orders.db.server"
$uploadPath = Join-Path -Path $scriptDir -ChildPath "data\orders.db.upload"

Write-Host "Local DB:     $localDbPath" -ForegroundColor Cyan
Write-Host ""

# Check if local database exists
if (-not (Test-Path $localDbPath)) {
    Write-Host "[ERROR] Local database not found!" -ForegroundColor Red
    Write-Host "Path: $localDbPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Please check if the file exists." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "VPS:          31.129.99.125" -ForegroundColor Cyan
Write-Host "VPS User:    root" -ForegroundColor Cyan
Write-Host ""

Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "  Choose direction" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Server -> Local (download)" -ForegroundColor White
Write-Host "2. Local -> Server (upload)" -ForegroundColor White
Write-Host "3. Cancel" -ForegroundColor White
Write-Host ""

Write-Host "Enter your choice (1-3): " -NoNewline -ForegroundColor Cyan
$choice = Read-Host

Write-Host ""

if ($choice -eq "3") {
    Write-Host "" 
    Write-Host "CANCELLED" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 0
}

if ($choice -eq "1") {
    # DOWNLOAD FROM SERVER
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Downloading from Server" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    
    # Create local backup if exists
    if ((Test-Path $localDbPath)) {
        Write-Host "[INFO] Creating local backup..." -ForegroundColor Yellow
        $timestamp = Get-Date -Format "dd.MM.yyyy_HH_mm_ss"
        $backupPath = "$localDbPath.backup_$timestamp"
        Copy-Item $localDbPath $backupPath
        Write-Host "[OK] Backup created: orders.db.backup_$timestamp" -ForegroundColor Green
    }
    
    # Stop bot on server
    Write-Host ""
    Write-Host "[STEP 1] Stopping bot on server..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "supervisorctl stop basestom-bot"
    Write-Host "[OK] Bot stopped" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 2] Downloading database..." -ForegroundColor Yellow
    scp root@31.129.99.125:/opt/basestom-bot/data/orders.db $localBackupPath
    Write-Host "[OK] Database downloaded" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 3] Starting bot on server..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "supervisorctl start basestom-bot"
    Write-Host "[OK] Bot started" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Sync completed!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files:" -ForegroundColor Cyan
    Write-Host "  * Server DB:  $localBackupPath" -ForegroundColor White
    Write-Host "  * Local DB:   $localDbPath" -ForegroundColor White
    Write-Host ""
    Write-Host "To use downloaded database:" -ForegroundColor Yellow
    Write-Host "  1. Close local bot (if running)" -ForegroundColor White
    Write-Host "  2. Replace $localDbPath with $localBackupPath" -ForegroundColor White
    Write-Host "  3. Start bot locally" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

if ($choice -eq "2") {
    # UPLOAD TO SERVER
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Uploading to Server" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "[WARNING] This will replace the server database!" -ForegroundColor Red
    Write-Host ""
    $confirm = Read-Host "Confirm replacement? (yes/no): "
    
    if ($confirm -ne "yes") {
        Write-Host ""
        Write-Host "CANCELLED" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 0
    }
    
    Write-Host ""
    Write-Host "[STEP 1] Creating server backup..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup"
    Write-Host "[OK] Backup created on server" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 2] Stopping bot on server..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "supervisorctl stop basestom-bot"
    Write-Host "[OK] Bot stopped" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 3] Uploading database..." -ForegroundColor Yellow
    scp $localDbPath root@31.129.99.125:/opt/basestom-bot/data/orders.db.new
    Write-Host "[OK] Database uploaded" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 4] Replacing database..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "mv /opt/basestom-bot/data/orders.db.new /opt/basestom-bot/data/orders.db"
    Write-Host "[OK] Database replaced" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[STEP 5] Starting bot on server..." -ForegroundColor Yellow
    ssh root@31.129.99.125 "supervisorctl start basestom-bot"
    Write-Host "[OK] Bot started" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Sync completed!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Database uploaded to server and replaced" -ForegroundColor Green
    Write-Host "Server backup: /opt/basestom-bot/data/orders.db.backup" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "[ERROR] Invalid choice!" -ForegroundColor Red
Read-Host "Press Enter to exit"
exit 1
