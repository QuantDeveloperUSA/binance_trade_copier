@echo off
echo Starting Binance Trade Copier Deployment...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the PowerShell deployment script
powershell.exe -ExecutionPolicy Bypass -File "deploy.ps1"

echo.
echo Deployment script completed.
pause
