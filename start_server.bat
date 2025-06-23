@echo off
title Binance Trade Copier Server
echo === Binance Trade Copier Server Wrapper ===
echo Starting server with enhanced monitoring and auto-restart...
echo.

:start_server
echo [%date% %time%] Starting server with monitor...
python server_monitor.py >> server_output.log 2>&1

echo [%date% %time%] Server monitor stopped. Exit code: %errorlevel%

if %errorlevel% equ 0 (
    echo Server stopped normally.
) else (
    echo Server monitor crashed with error code %errorlevel%
    echo Waiting 10 seconds before restart...
    timeout /t 10 /nobreak >nul
    echo Restarting server monitor...
    goto start_server
)

echo Server shutdown complete.
pause
