@echo off
echo [%DATE% %TIME%] Starting deployment script...

REM Change to deployment directory
cd /d "C:\Users\Administrator\binance_trade_copier"
if errorlevel 1 (
    echo ERROR: Could not change to deployment directory
    exit /b 1
)

echo [%DATE% %TIME%] Current directory: %CD%

REM Pull latest changes from git
echo [%DATE% %TIME%] Pulling latest changes...
git pull origin main
if errorlevel 1 (
    echo ERROR: Git pull failed
    exit /b 1
)

REM Show current commit
echo [%DATE% %TIME%] Current commit:
git log --oneline -1

REM Stop existing Python processes
echo [%DATE% %TIME%] Stopping existing Python processes...
taskkill /F /IM python.exe 2>nul
if errorlevel 1 (
    echo No Python processes were running
) else (
    echo Python processes stopped
)

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start the application
echo [%DATE% %TIME%] Starting application...
start /B python main.py

REM Verify the application started
timeout /t 5 /nobreak >nul
tasklist | findstr python.exe >nul
if errorlevel 1 (
    echo WARNING: Python application may not have started
) else (
    echo SUCCESS: Python application is running
)

echo [%DATE% %TIME%] Deployment completed
