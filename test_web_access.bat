@echo off
echo Testing web application accessibility...
echo.

echo 1. Testing local web access on VPS...
curl -s -m 10 http://localhost:8000
echo.
echo Return code: %ERRORLEVEL%
echo.

echo 2. Testing external web access...
curl -s -m 10 http://5.181.5.168:8000
echo.
echo Return code: %ERRORLEVEL%
echo.

echo 3. Testing if port 8000 is listening...
netstat -an | findstr :8000
echo.

echo 4. Checking firewall rule for port 8000...
netsh advfirewall firewall show rule name="Python HTTP" verbose
echo.

echo 5. Checking if Python application is running...
tasklist | findstr python
echo.

pause
