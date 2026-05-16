# PowerShell deployment script for VPS (Windows compatible)

$ErrorActionPreference = "Stop"

# Configuration
$VPS_IP = "31.129.99.125"
$VPS_USER = "root"
$VPS_PATH = "/opt/basestom-bot"
$ARCHIVE_NAME = "basestom-bot-deploy.zip"
$LOCAL_PATH = "C:\Users\crush\AppData\Roaming\projects\basestom"

Write-Host "========================================="
Write-Host "Deploy script for VPS (PowerShell)"
Write-Host "========================================="
Write-Host ""

try {
    # Step 1: Create archive
    Write-Host "Step 1: Creating archive..."
    Write-Host ""

    Set-Location $LOCAL_PATH

    # Create ZIP archive
    Compress-Archive -Path @(
        "requirements.txt",
        "DEPLOY_COMMANDS.md",
        "supervisor.conf",
        "src",
        "data/references.json",
        "src/.env"
    ) -DestinationPath $ARCHIVE_NAME -Force

    Write-Host "Archive created: $ARCHIVE_NAME"
    Write-Host ""

    # Step 2: Upload archive to VPS
    Write-Host "Step 2: Uploading archive to VPS ($VPS_IP)..."
    Write-Host "Enter password for ${VPS_USER}@${VPS_IP}"
    Write-Host ""

    # Use scp from Git Bash or PowerShell
    $scpCommand = "scp $ARCHIVE_NAME ${VPS_USER}@${VPS_IP}:/tmp/"

    try {
        Invoke-Expression $scpCommand
    } catch {
        Write-Host "ERROR: scp command failed. Trying with pscp (PuTTY)..."
        Write-Host "Please install Git for Windows or use PuTTY's pscp"
        Write-Host "Manual upload required:"
        Write-Host "  scp $ARCHIVE_NAME ${VPS_USER}@${VPS_IP}:/tmp/"
        pause
        exit 1
    }

    Write-Host "Archive uploaded successfully"
    Write-Host ""

    # Step 3: Install on VPS via SSH
    Write-Host "Step 3: Installing on VPS..."
    Write-Host "Enter password for ${VPS_USER}@${VPS_IP}"
    Write-Host ""

    $sshCommand = "ssh ${VPS_USER}@${VPS_IP} `"cd ${VPS_PATH} && unzip -o /tmp/${ARCHIVE_NAME} -d ${VPS_PATH} && rm /tmp/${ARCHIVE_NAME} && source venv/bin/activate && pip install -r requirements.txt && supervisorctl restart basestom-bot && supervisorctl status basestom-bot`""

    try {
        Invoke-Expression $sshCommand
    } catch {
        Write-Host "ERROR: SSH command failed. Please run manually:"
        Write-Host "  ssh ${VPS_USER}@${VPS_IP} `"cd ${VPS_PATH} && unzip -o /tmp/${ARCHIVE_NAME} -d ${VPS_PATH} && rm /tmp/${ARCHIVE_NAME} && source venv/bin/activate && pip install -r requirements.txt && supervisorctl restart basestom-bot`""
        pause
        exit 1
    }

    # Cleanup
    Write-Host ""
    Write-Host "Cleaning up local archive..."
    Remove-Item $ARCHIVE_NAME -Force

    Write-Host ""
    Write-Host "========================================="
    Write-Host "Deployment completed successfully!"
    Write-Host "========================================="
    Write-Host ""
    Write-Host "Check bot in Telegram:"
    Write-Host "1. Find bot: @sfdtgafvdba_bot"
    Write-Host "2. Send: /start"
    Write-Host ""
    Write-Host "To manage bot:"
    Write-Host "  Status:  ssh ${VPS_USER}@${VPS_IP} supervisorctl status basestom-bot"
    Write-Host "  Logs:    ssh ${VPS_USER}@${VPS_IP} supervisorctl tail -f basestom-bot"
    Write-Host ""
    pause

} catch {
    Write-Host ""
    Write-Host "ERROR: Deployment failed"
    Write-Host $_.Exception.Message
    Write-Host ""
    pause
    exit 1
}
