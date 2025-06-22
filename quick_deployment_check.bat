@echo off
echo ============================================
echo    Quick Deployment Status Check
echo ============================================
echo.

echo 1. Testing if web application is responding...
curl -s -m 10 http://5.181.5.168:8000 > nul
if errorlevel 1 (
    echo ❌ Web application is not responding
    goto end
) else (
    echo ✅ Web application is responding
)
echo.

echo 2. Checking for updated title "Binance Trade Copier"...
curl -s -m 10 http://5.181.5.168:8000 | findstr "Binance Trade Copier" > nul
if errorlevel 1 (
    echo ❌ Title not updated
) else (
    echo ✅ Title updated to "Binance Trade Copier"
)
echo.

echo 3. Checking for rocket emoji (previous deployment test)...
curl -s -m 10 http://5.181.5.168:8000 | findstr "🚀" > nul
if errorlevel 1 (
    echo ❌ Rocket emoji not found
) else (
    echo ✅ Rocket emoji found
)
echo.

echo 4. Checking for checkmark emoji (latest deployment test)...
curl -s -m 10 http://5.181.5.168:8000 | findstr "✅" > nul
if errorlevel 1 (
    echo ❌ Latest changes not deployed yet
) else (
    echo ✅ Latest changes are live!
)
echo.

echo 5. GitHub Actions Status:
echo    Check: https://github.com/QuantDeveloperUSA/binance_trade_copier/actions
echo.

:end
echo ============================================
pause
