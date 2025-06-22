@echo off
echo ============================================
echo    Automated Deployment Verification
echo ============================================
echo.

echo Testing if automated deployment worked...
echo.

echo 1. Testing web page for rocket emoji...
curl -s http://5.181.5.168:8000 | findstr /C:"🚀"
if errorlevel 1 (
    echo ❌ Rocket emoji NOT found - deployment may have failed
) else (
    echo ✅ Rocket emoji found - deployment successful!
)
echo.

echo 2. Testing navbar title...
curl -s http://5.181.5.168:8000 | findstr /C:"Binance Trade Copier 🚀"
if errorlevel 1 (
    echo ❌ Updated navbar NOT found
) else (
    echo ✅ Updated navbar found!
)
echo.

echo 3. Opening web browser to verify visually...
start http://5.181.5.168:8000
echo.

pause
