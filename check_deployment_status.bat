@echo off
echo ============================================
echo    VPS Status Check After Deployment #13
echo ============================================
echo.

echo 1. Checking if our verification file exists on VPS...
ssh trader@5.181.5.168 "if exist C:\Users\Administrator\binance_trade_copier\deployment_fix_verification.txt (echo FOUND: deployment_fix_verification.txt) else (echo NOT FOUND: deployment_fix_verification.txt)"
echo.

echo 2. Checking current git commit on VPS...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && git log --oneline -1"
echo.

echo 3. Checking current HTML title in templates/index.html...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && findstr /n \"<title>\" templates\index.html"
echo.

echo 4. Checking if Python process is running...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo 5. Testing internal web access on VPS...
ssh trader@5.181.5.168 "curl -s http://localhost:8000 | findstr /i \"<title>\""
echo.

echo 6. Checking main.py FastAPI title...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && findstr /n \"FastAPI\" main.py"
echo.

pause
