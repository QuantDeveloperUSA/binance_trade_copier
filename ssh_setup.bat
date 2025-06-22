@echo off
REM SSH Key Setup Script for Binance Trade Copier Auto-Deployment
REM Run this script on your LOCAL machine (Windows 11)

echo ============================================
echo SSH Key Setup for Auto-Deployment
echo ============================================
echo.

set SSH_DIR=%USERPROFILE%\.ssh
set KEY_NAME=id_rsa_vps
set VPS_USER=trader
set VPS_HOST=5.181.5.168

echo [1/4] Checking if .ssh directory exists...
if not exist "%SSH_DIR%" (
    echo Creating .ssh directory...
    mkdir "%SSH_DIR%"
    echo ✅ Created: %SSH_DIR%
) else (
    echo ✅ Directory exists: %SSH_DIR%
)
echo.

echo [2/4] Generating SSH key pair...
echo This will create a new SSH key specifically for VPS deployment
echo Key will be saved as: %SSH_DIR%\%KEY_NAME%
echo.
ssh-keygen -t rsa -b 4096 -C "%VPS_USER%@%VPS_HOST%" -f "%SSH_DIR%\%KEY_NAME%" -N ""

if %ERRORLEVEL% EQ 0 (
    echo ✅ SSH key pair generated successfully
) else (
    echo ❌ Failed to generate SSH key pair
    pause
    exit /b 1
)
echo.

echo [3/4] Displaying public key (copy this to your VPS)...
echo ============================================
echo COPY THE FOLLOWING PUBLIC KEY:
echo ============================================
type "%SSH_DIR%\%KEY_NAME%.pub"
echo.
echo ============================================
echo.

echo [4/4] Next steps:
echo.
echo 📋 1. COPY the public key above
echo.
echo 🔑 2. SSH to your VPS and run these commands:
echo    ssh %VPS_USER%@%VPS_HOST%
echo    mkdir C:\Users\%VPS_USER%\.ssh 2^>nul
echo    echo [PASTE_PUBLIC_KEY_HERE] ^>^> C:\Users\%VPS_USER%\.ssh\authorized_keys
echo.
echo 🔧 3. Test SSH key authentication:
echo    ssh -i "%SSH_DIR%\%KEY_NAME%" %VPS_USER%@%VPS_HOST%
echo.
echo 📝 4. Add to GitHub Secrets (copy the private key):
echo    Secret Name: SSH_PRIVATE_KEY
echo    Secret Value: [Content of %SSH_DIR%\%KEY_NAME%]
echo.
echo 📄 5. To get private key content for GitHub:
echo    type "%SSH_DIR%\%KEY_NAME%"
echo.
echo ============================================
echo.

pause

echo.
echo Would you like to see the private key content for GitHub? (y/n)
set /p SHOW_PRIVATE=
if /i "%SHOW_PRIVATE%"=="y" (
    echo.
    echo ============================================
    echo PRIVATE KEY CONTENT FOR GITHUB SECRET:
    echo ============================================
    type "%SSH_DIR%\%KEY_NAME%"
    echo.
    echo ============================================
    echo Copy everything above (including BEGIN and END lines^)
    echo.
)

echo.
echo 🎯 Summary of files created:
echo    Public Key:  %SSH_DIR%\%KEY_NAME%.pub
echo    Private Key: %SSH_DIR%\%KEY_NAME%
echo.
echo 🔐 Security Note: Keep your private key secure and never share it publicly!
echo.
pause
