@echo off
echo Starting Python server in background on VPS...
echo.

echo Stopping any existing Python processes...
ssh trader@5.181.5.168 "taskkill /F /IM python.exe 2>nul"
echo.

echo Starting server in background...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && start /B python main.py"
echo.

echo Waiting 5 seconds for server to start...
timeout /t 5 /nobreak >nul

echo Checking if Python process is running...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo Testing local web access on VPS...
ssh trader@5.181.5.168 "curl -s -m 5 http://localhost:8000 | findstr /i title"
echo.

echo Testing external web access...
timeout /t 2 /nobreak >nul
curl -s -m 10 http://5.181.5.168:8000 | findstr /i "binance\|trade\|title"

echo.
pause
