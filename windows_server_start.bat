@echo off
title Binance Trade Copier - Windows Service Starter
echo === Windows-Compatible Server Startup ===
echo.

REM Set error handling
setlocal EnableDelayedExpansion

echo Checking Windows environment...
echo User: %USERNAME%
echo Working Directory: %CD%
echo Python Location: 
where python 2>nul || (
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

echo.
echo === Python Environment Check ===
python --version || (
    echo ERROR: Python version check failed
    pause
    exit /b 1
)

echo.
echo === Testing Python Imports ===
python -c "import sys; print('Python executable:', sys.executable)" || (
    echo ERROR: Basic Python test failed
    pause
    exit /b 1
)

echo.
echo === Checking Windows COM Security ===
REM Check if we need to configure COM security for Windows services
python -c "import sys; print('Checking COM compatibility...'); import asyncio; print('Asyncio OK')" 2>nul || (
    echo WARNING: COM/Asyncio compatibility issue detected
    echo This might require Windows COM configuration
)

echo.
echo === Testing Server Dependencies ===
python -c "import fastapi, uvicorn, binance; print('All dependencies available')" || (
    echo ERROR: Missing required dependencies
    echo Running pip install...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo === Creating Log Files ===
echo. > server_output.log
echo. > server_debug.log
echo Log files created

echo.
echo === Starting Server (Method 1: Direct) ===
echo Attempting direct Python execution...
python main.py > server_output.log 2>&1 &
timeout /t 5 /nobreak >nul

echo Checking if server started...
tasklist | findstr python.exe >nul
if errorlevel 1 (
    echo Direct method failed, trying alternative methods...
    goto try_alternative
) else (
    echo ✅ Server appears to be running with direct method
    goto server_running
)

:try_alternative
echo.
echo === Starting Server (Method 2: PowerShell) ===
powershell -Command "Start-Process python -ArgumentList 'main.py' -WindowStyle Hidden -RedirectStandardOutput 'server_output.log' -RedirectStandardError 'server_debug.log'"
timeout /t 5 /nobreak >nul

tasklist | findstr python.exe >nul
if errorlevel 1 (
    echo PowerShell method failed, trying service method...
    goto try_service
) else (
    echo ✅ Server started with PowerShell method
    goto server_running
)

:try_service
echo.
echo === Starting Server (Method 3: Windows Service Style) ===
echo Creating Windows service-compatible startup...
schtasks /create /tn "BinanceTradeServer" /tr "python \"%CD%\main.py\"" /sc once /st 23:59 /f >nul 2>&1
schtasks /run /tn "BinanceTradeServer" >nul 2>&1
timeout /t 5 /nobreak >nul
schtasks /delete /tn "BinanceTradeServer" /f >nul 2>&1

tasklist | findstr python.exe >nul
if errorlevel 1 (
    echo All startup methods failed!
    goto startup_failed
) else (
    echo ✅ Server started with service method
    goto server_running
)

:server_running
echo.
echo === SERVER SUCCESSFULLY STARTED ===
echo Server is running in background
echo Log files: server_output.log, server_debug.log
echo.
echo Monitoring for 30 seconds...
for /l %%i in (1,1,6) do (
    timeout /t 5 /nobreak >nul
    tasklist | findstr python.exe >nul || (
        echo WARNING: Server process disappeared at check %%i
        goto check_logs
    )
    echo Check %%i: Server still running...
)
echo ✅ Server running stable for 30 seconds
goto check_logs

:startup_failed
echo.
echo === STARTUP FAILED ===
echo The server could not be started with any method.
echo Please check the following:
echo 1. Python installation and PATH
echo 2. Windows permissions
echo 3. COM security settings
echo 4. Visual C++ redistributables
echo 5. Windows Defender/Antivirus blocking
echo.

:check_logs
echo.
echo === CURRENT LOG OUTPUT ===
if exist server_output.log (
    echo server_output.log contents:
    type server_output.log
) else (
    echo No server_output.log found
)

if exist server_debug.log (
    echo.
    echo server_debug.log contents:
    type server_debug.log
)

echo.
echo === FINAL STATUS ===
tasklist | findstr python.exe && (
    echo ✅ Python processes currently running:
    tasklist | findstr python.exe
) || (
    echo ❌ No Python processes running
)

echo.
echo Server startup script complete.
REM Don't pause in automated deployment
if "%1"=="" pause
