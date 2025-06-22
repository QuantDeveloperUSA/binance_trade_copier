@echo off
echo Starting Binance Copy Trader...
cd /d "%~dp0"
echo Running database migration...
python migrate_db.py
if %errorlevel% neq 0 (
    echo Migration failed!
    pause
    exit /b 1
)
echo Starting main application...
python main.py
pause
