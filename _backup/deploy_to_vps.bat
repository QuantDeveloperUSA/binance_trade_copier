@echo off
echo VPS Deployment Package Builder
echo ==============================

REM Build the executable
call build_exe.bat

REM Create deployment folder
mkdir deployment 2>nul
copy dist\BinanceCopyTrader.exe deployment\
copy config.py deployment\
copy service_installer.py deployment\

REM Create deployment instructions
echo Creating deployment instructions...
(
echo Binance Copy Trader VPS Deployment Instructions
echo ================================================
echo.
echo 1. Copy the deployment folder to your VPS
echo.
echo 2. On the VPS, run Command Prompt as Administrator
echo.
echo 3. Navigate to the deployment folder and run:
echo    python service_installer.py
echo.
echo 4. The service will start automatically and run on system boot
echo.
echo 5. Access the web interface at http://VPS_IP:8000
echo.
echo 6. Default admin password: admin123 (change in config.py)
echo.
echo Service Management Commands:
echo - Stop:    net stop BinanceCopyTrader
echo - Start:   net start BinanceCopyTrader  
echo - Status:  sc query BinanceCopyTrader
echo - Remove:  BinanceCopyTrader.exe remove
echo.
echo The service runs as LocalSystem and starts before user login.
) > deployment\README.txt

echo.
echo Deployment package created in 'deployment' folder
echo Copy this folder to your VPS and follow README.txt
pause
