@echo off
echo Testing direct VPS connection and manual restart...
echo.

echo 1. Quick test - checking VPS connection...
ping -n 1 5.181.5.168
echo.

echo 2. Manual server restart on VPS...
echo Stopping Python process...
ssh trader@5.181.5.168 "taskkill /F /IM python.exe 2>nul || echo No Python process found"
echo.

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting Python server...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && start /B python main.py"
echo.

echo Waiting 5 seconds for server to start...
timeout /t 5 /nobreak >nul

echo Testing web access...
curl -s -m 10 http://5.181.5.168:8000 | findstr /i "title"
echo.

pause
