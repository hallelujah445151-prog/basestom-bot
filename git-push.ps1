# Git Push Script (PowerShell) - UTF-8 Encoded
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Git Push Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Set-Location basestom

Write-Host "[INFO] Running git commands..." -ForegroundColor Yellow

try {
    # Add file
    $addResult = & git add src/services/reminder_service.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Git add failed!" -ForegroundColor Red
        Write-Host $addResult -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] File staged" -ForegroundColor Green

    # Commit
    $commitResult = & git commit -m "Fix reminder - send 1 day before deadline" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Git commit failed!" -ForegroundColor Red
        Write-Host $commitResult -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Changes committed" -ForegroundColor Green

    # Push
    Write-Host "[INFO] Pushing to GitHub..." -ForegroundColor Yellow
    $pushResult = & git push 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Git push failed!" -ForegroundColor Red
        Write-Host $pushResult -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Pushed to GitHub" -ForegroundColor Green

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Success!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green

} catch {
    Write-Host "[ERROR] Error: $_" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Read-Host "Press Enter to exit"
