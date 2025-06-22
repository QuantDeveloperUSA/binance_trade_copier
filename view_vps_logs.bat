@echo off
echo ============================================
echo    Real-time VPS Python Server Logs
echo ============================================
echo.

echo Connecting to VPS to view Python server logs...
echo Press Ctrl+C to stop monitoring
echo.

echo Method 1: Check Windows Event Logs for Python errors...
ssh Administrator@5.181.5.168 "wevtutil qe Application /c:10 /rd:true /f:text | findstr python"
echo.

echo Method 2: Check if there are any log files in the application directory...
ssh Administrator@5.181.5.168 "cd /d C:\Users\Administrator\binance_trade_copier && dir *.log"
echo.

echo Method 3: Try to see Python output (if running in console)...
echo Note: Since Python runs with 'start /B', output goes to background
echo.

echo Method 4: Check process information...
ssh Administrator@5.181.5.168 "tasklist /fi \"imagename eq python.exe\" /fo table /v"
echo.

echo To see real-time logs, you would need to:
echo 1. RDP to the VPS
echo 2. Stop the current Python process
echo 3. Run: python main.py
echo 4. This will show logs in the console
echo.

pause
