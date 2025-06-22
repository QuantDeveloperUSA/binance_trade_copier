@echo off
echo Manually starting the Python server on VPS...
echo.

echo 1. Connecting to VPS and checking current status...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo 2. Changing to application directory and starting server...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && python main.py"

pause
