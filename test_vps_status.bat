@echo off
echo Testing VPS connectivity and deployment status...
echo.

echo 1. Testing SSH connectivity to VPS...
ssh -o ConnectTimeout=10 trader@5.181.5.168 "echo SSH connection successful"
echo.

echo 2. Checking deployment directory and files...
ssh trader@5.181.5.168 "cd C:\Users\Administrator\binance_trade_copier && dir /b"
echo.

echo 3. Checking git status on VPS...
ssh trader@5.181.5.168 "cd C:\Users\Administrator\binance_trade_copier && git log --oneline -3"
echo.

echo 4. Testing if Python app is running...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo 5. Testing internal web access...
ssh trader@5.181.5.168 "curl -s http://localhost:8000 | findstr title"
echo.

echo 6. Checking firewall rules for port 8000...
ssh trader@5.181.5.168 "netsh advfirewall firewall show rule name=\"Python HTTP\" verbose"
echo.

pause
