@echo off
title Debug Server Startup
echo === Trade Copier Server Startup Debug ===
echo.

echo Current directory: %CD%
echo Current user: %USERNAME%
echo Current time: %DATE% %TIME%
echo.

echo === CHECKING FILES ===
echo Looking for main files...
if exist main.py (echo ✅ main.py found) else (echo ❌ main.py NOT found)
if exist config.py (echo ✅ config.py found) else (echo ❌ config.py NOT found)
if exist requirements.txt (echo ✅ requirements.txt found) else (echo ❌ requirements.txt NOT found)
echo.

echo === TESTING PYTHON ===
echo Python version:
python --version || (echo ❌ Python not working && pause && exit /b 1)
echo.

echo === TESTING IMPORTS ===
echo Testing critical imports...
python -c "import sys; print('Python path OK')" || echo ❌ Basic Python failed
python -c "import fastapi; print('✅ FastAPI OK')" || echo ❌ FastAPI failed
python -c "import uvicorn; print('✅ Uvicorn OK')" || echo ❌ Uvicorn failed
python -c "import asyncio; print('✅ Asyncio OK')" || echo ❌ Asyncio failed
echo.

echo === TESTING LOG FILE CREATION ===
echo Creating test log files...
echo Test log entry > test_log_creation.log
if exist test_log_creation.log (
    echo ✅ Log file creation works
    del test_log_creation.log
) else (
    echo ❌ Log file creation failed
)
echo.

echo === TESTING PYTHON OUTPUT REDIRECTION ===
echo Testing Python output redirection...
python -c "print('Testing output redirection'); import sys; sys.stdout.flush()" > python_output_test.log 2>&1
if exist python_output_test.log (
    echo ✅ Python output redirection works
    echo Content:
    type python_output_test.log
    del python_output_test.log
) else (
    echo ❌ Python output redirection failed
)
echo.

echo === TESTING MAIN.PY SYNTAX ===
echo Checking main.py syntax...
python -c "import ast; ast.parse(open('main.py').read()); print('✅ Syntax OK')" || (
    echo ❌ Syntax error in main.py
    pause
    exit /b 1
)
echo.

echo === ATTEMPTING DIRECT SERVER START ===
echo WARNING: This will attempt to start the server directly
echo Press Ctrl+C to stop the server when it starts
echo.
pause

echo Starting server with full output...
python main.py

echo.
echo Server stopped or failed to start.
echo.

echo === CHECKING FOR LOG FILES ===
echo Looking for log files created...
if exist server_output.log (
    echo ✅ server_output.log found
    echo Content:
    type server_output.log
) else (
    echo ❌ server_output.log not found
)

if exist binance_trade_copier.log (
    echo ✅ binance_trade_copier.log found  
    echo Content:
    type binance_trade_copier.log
) else (
    echo ❌ binance_trade_copier.log not found
)

echo.
echo === DEBUG COMPLETE ===
pause
