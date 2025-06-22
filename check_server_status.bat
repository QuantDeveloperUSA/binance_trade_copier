@echo off
echo Checking server status on VPS...
echo.

echo 1. Checking if Python processes are running...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo 2. Checking if port 8000 is listening...
ssh trader@5.181.5.168 "netstat -an | findstr :8000"
echo.

echo 3. Testing internal web access...
ssh trader@5.181.5.168 "curl -s -m 5 http://localhost:8000"
echo.

echo 4. Testing external web access...
curl -s -m 10 http://5.181.5.168:8000
echo.

pause
