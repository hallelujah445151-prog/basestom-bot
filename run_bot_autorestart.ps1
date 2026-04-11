# Auto-restart bot script for PowerShell
# This will restart the bot if it crashes

Write-Host "Basestom Bot Auto-Restart Script" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

while ($true) {
    Write-Host "Starting bot..." -ForegroundColor Cyan
    Write-Host ""

    try {
        python src\bot.py
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Bot stopped or crashed!" -ForegroundColor Yellow
    Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
    Write-Host ""

    Start-Sleep -Seconds 10

    Write-Host ""
}
