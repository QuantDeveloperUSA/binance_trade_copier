@echo off
echo ============================================
echo    VPS Logs and Status Monitor
echo ============================================
echo.

echo 1. Checking GitHub Actions deployment logs...
echo    (You can also check: https://github.com/QuantDeveloperUSA/binance_trade_copier/actions)
echo.

echo 2. Checking if Python server is running on VPS...
ssh Administrator@5.181.5.168 "tasklist | findstr python"
if errorlevel 1 (
    echo ❌ Python server not running
) else (
    echo ✅ Python server is running
)
echo.

echo 3. Checking Python server process details...
ssh Administrator@5.181.5.168 "wmic process where \"name='python.exe'\" get ProcessId,CreationDate,CommandLine /format:table"
echo.

echo 4. Checking current git status on VPS...
ssh Administrator@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && git log --oneline -3"
echo.

echo 5. Checking if server is responding...
curl -s -m 5 http://5.181.5.168:8000 | findstr "title"
echo.

echo 6. Testing for the latest change (checkmark emoji)...
curl -s http://5.181.5.168:8000 | findstr "✅"
if errorlevel 1 (
    echo ❌ Latest changes not deployed yet
) else (
    echo ✅ Latest changes are live!
)
echo.

pause
