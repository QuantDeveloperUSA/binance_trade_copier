@echo off
echo Testing VPS Status After Partial Deployment...
echo.

echo The GitHub Actions deployment partially worked:
echo - ✅ SSH connected successfully
echo - ✅ Git pull completed (files updated)
echo - ✅ Old Python process stopped
echo - ❌ Failed at 'timeout' command 
echo - ❌ Python server may not have restarted
echo.

echo We need to manually restart the Python server on the VPS.
echo.

echo Instructions for manual server restart:
echo 1. Connect to VPS via RDP (5.181.5.168)
echo 2. Open PowerShell as Administrator
echo 3. Run: cd C:\Users\Administrator\binance_trade_copier
echo 4. Run: python main.py
echo.

echo After manual restart, you should see the rocket emoji 🚀
echo in the navbar at http://5.181.5.168:8000
echo.

pause
