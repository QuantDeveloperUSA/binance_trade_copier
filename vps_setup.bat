@echo off
REM Binance Trade Copier - VPS Setup Script
REM Run this script on your Windows VPS to prepare for GitHub Actions deployment

echo ============================================
echo  Binance Trade Copier VPS Setup Script
echo ============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Setting up deployment environment...

REM Create deployment directory
set DEPLOY_PATH=C:\trade_copier
if not exist "%DEPLOY_PATH%" (
    echo Creating deployment directory: %DEPLOY_PATH%
    mkdir "%DEPLOY_PATH%"
) else (
    echo Deployment directory already exists: %DEPLOY_PATH%
)

REM Check Python installation
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    python --version
    echo Python is installed correctly
)

REM Check pip
echo.
echo Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
) else (
    echo pip is available
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install curl if not available (for health checks)
echo.
echo Checking curl availability...
curl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: curl is not available
    echo Health checks in deployment may not work
    echo Consider installing curl or using Windows 10/11 which includes it
) else (
    echo curl is available
)

REM Set permissions for deployment directory
echo.
echo Setting permissions for deployment directory...
icacls "%DEPLOY_PATH%" /grant trader:(OI)(CI)F /t >nul 2>&1

REM Create Windows Service (optional)
echo.
echo Do you want to create a Windows Service for the Trade Copier? (y/n)
set /p create_service="Enter choice: "
if /i "%create_service%"=="y" (
    echo.
    echo Creating Windows Service...
    
    REM Create service wrapper script
    echo @echo off > "%DEPLOY_PATH%\service_wrapper.bat"
    echo cd /d "%DEPLOY_PATH%" >> "%DEPLOY_PATH%\service_wrapper.bat"
    echo python main.py >> "%DEPLOY_PATH%\service_wrapper.bat"
    
    REM Install service using sc command
    sc create BinanceTradeCopiersvc binPath= "cmd.exe /c \"%DEPLOY_PATH%\service_wrapper.bat\"" start= auto DisplayName= "Binance Trade Copier Service"
    
    if %errorlevel% equ 0 (
        echo Service created successfully
        echo Service Name: BinanceTradeCopiersvc
        echo You can start/stop it using: sc start/stop BinanceTradeCopiersvc
    ) else (
        echo Failed to create service
        echo You can run the application manually or try creating the service later
    )
) else (
    echo Skipping service creation
    echo You can create it later by running this script again
)

REM Setup firewall rule for web interface (if needed)
echo.
echo Do you want to open firewall port 8000 for the web interface? (y/n)
set /p open_firewall="Enter choice: "
if /i "%open_firewall%"=="y" (
    echo Opening firewall port 8000...
    netsh advfirewall firewall add rule name="Binance Trade Copier" dir=in action=allow protocol=TCP localport=8000
    if %errorlevel% equ 0 (
        echo Firewall rule added successfully
    ) else (
        echo Failed to add firewall rule - you may need to do this manually
    )
) else (
    echo Skipping firewall configuration
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Add your SSH public key to the VPS (for GitHub Actions)
echo 2. Configure GitHub repository secrets:
echo    - VPS_SSH_KEY: Your private SSH key
echo 3. Test the deployment by pushing to main branch
echo.
echo Deployment directory: %DEPLOY_PATH%
echo Service name: BinanceTradeCopiersvc (if created)
echo Web interface: http://localhost:8000 (when running)
echo.
echo To manually start the application:
echo   cd %DEPLOY_PATH%
echo   python main.py
echo.
pause
