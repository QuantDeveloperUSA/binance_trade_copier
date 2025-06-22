@echo off
echo Quick manual deployment of rocket emoji...
echo.

echo This will manually apply the latest changes on the VPS
echo including the rocket emoji in the navbar.
echo.

echo Instructions:
echo 1. Connect to VPS via RDP
echo 2. Open PowerShell as Administrator  
echo 3. Run these commands:
echo.
echo    cd C:\Users\Administrator\binance_trade_copier
echo    git pull origin main
echo    taskkill /F /IM python.exe
echo    python main.py
echo.
echo After running these commands, refresh http://5.181.5.168:8000
echo and you should see "Binance Trade Copier 🚀" in the navbar.
echo.

pause
