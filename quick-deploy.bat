@echo off
echo Starting deployment using PowerShell...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"
