@echo off
echo ============================================
echo    VPS Deployment Diagnostic Script
echo ============================================
echo.

echo 1. Testing SSH connection to VPS...
ssh -o ConnectTimeout=10 trader@5.181.5.168 "echo SSH connection successful"
if errorlevel 1 (
    echo ERROR: SSH connection failed
    goto :error
)
echo.

echo 2. Checking if deployment directory exists...
ssh trader@5.181.5.168 "if exist C:\Users\Administrator\binance_trade_copier echo Directory exists"
echo.

echo 3. Checking git repository status...
ssh trader@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && git log --oneline -3"
echo.

echo 4. Checking if deployment script exists and running it...
ssh trader@5.181.5.168 "if exist C:\Users\Administrator\binance_trade_copier\deploy_script.bat (echo Deploy script found && C:\Users\Administrator\binance_trade_copier\deploy_script.bat) else (echo Deploy script NOT found)"
echo.

echo 5. Checking if Python application is running...
ssh trader@5.181.5.168 "tasklist | findstr python"
echo.

echo 6. Testing internal web access on VPS...
ssh trader@5.181.5.168 "curl -s -m 5 http://localhost:8000 | findstr /i title"
echo.

echo 7. Checking if port 8000 is listening...
ssh trader@5.181.5.168 "netstat -an | findstr :8000"
echo.

echo 8. Checking firewall rules for port 8000...
ssh trader@5.181.5.168 "netsh advfirewall firewall show rule name=all | findstr /i 8000"
echo.

echo 9. Adding/updating firewall rules for port 8000...
ssh trader@5.181.5.168 "netsh advfirewall firewall delete rule name=\"Binance Trade Copier Web\" protocol=TCP localport=8000 2>nul & netsh advfirewall firewall add rule name=\"Binance Trade Copier Web\" dir=in action=allow protocol=TCP localport=8000"
echo.

echo 10. Final test - checking if web app is accessible...
timeout /t 5 /nobreak >nul
curl -s -m 10 http://5.181.5.168:8000 | findstr /i "binance\|trade\|title"
if errorlevel 1 (
    echo External access still not working - manual intervention required
) else (
    echo SUCCESS: Web application is now accessible externally!
)

goto :end

:error
echo.
echo ERROR: Diagnostic failed. Please check SSH connection and VPS status.

:end
echo.
echo Diagnostic completed.
pause
