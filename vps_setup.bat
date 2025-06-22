@echo off
REM Initial VPS Setup Script for Binance Trade Copier
REM Run this script on your VPS (trader@5.181.5.168) before first deployment

echo ============================================
echo Binance Trade Copier - VPS Setup Script
echo ============================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/windows/
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python is installed
)
echo.

REM Check if Git is installed
echo [2/6] Checking Git installation...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    git --version
    echo ✅ Git is installed
)
echo.

REM Check if pip is working
echo [3/6] Checking pip installation...
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip is not working
    echo Please ensure Python and pip are properly installed
    pause
    exit /b 1
) else (
    pip --version
    echo ✅ pip is working
)
echo.

REM Create deployment directory
echo [4/6] Creating deployment directory...
set DEPLOY_DIR=C:\Users\trader\binance_trade_copier
if not exist "%DEPLOY_DIR%" (
    mkdir "%DEPLOY_DIR%"
    echo ✅ Created directory: %DEPLOY_DIR%
) else (
    echo ✅ Directory already exists: %DEPLOY_DIR%
)
echo.

REM Create data directories
echo [5/6] Creating data directories...
cd /d "%DEPLOY_DIR%"
if not exist "data" mkdir "data"
if not exist "templates" mkdir "templates"
if not exist "logs" mkdir "logs"
echo ✅ Data directories created
echo.

REM Configure Git (optional)
echo [6/6] Git configuration...
git config --global user.name >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git user not configured. Please configure:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
) else (
    echo ✅ Git user already configured
    echo User: 
    git config --global user.name
    echo Email: 
    git config --global user.email
)
echo.

echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo Next steps:
echo 1. Configure GitHub secrets in your repository:
echo    - VPS_HOST: 5.181.5.168
echo    - VPS_USERNAME: trader
echo    - VPS_PASSWORD: your_password
echo.
echo 2. Update the GitHub repository URL in .github/workflows/deploy.yml
echo.
echo 3. Push your code to the main branch to trigger auto-deployment
echo.
echo 4. Monitor deployment at: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
echo.
echo Application will be available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo.
pause
