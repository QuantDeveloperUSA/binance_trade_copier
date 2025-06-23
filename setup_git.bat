@echo off
title Git Setup for Trade Copier Deployment
echo === Git Configuration Helper ===
echo.

echo Checking current Git installation...
git --version 2>nul && (
    echo ✅ Git is already installed
    git --version
    goto configure_git
) || (
    echo ❌ Git not found
    goto install_git
)

:install_git
echo.
echo === Installing Git ===
echo Attempting automatic Git installation...

echo Trying winget...
winget --version 2>nul && (
    echo Installing Git via winget...
    winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo Winget installation failed, trying chocolatey...
        goto try_choco
    ) else (
        echo ✅ Git installed via winget
        goto verify_git
    )
) || (
    echo Winget not available, trying chocolatey...
    goto try_choco
)

:try_choco
choco --version 2>nul && (
    echo Installing Git via chocolatey...
    choco install git -y
    if errorlevel 1 (
        echo Chocolatey installation failed
        goto manual_install
    ) else (
        echo ✅ Git installed via chocolatey
        goto verify_git
    )
) || (
    echo Chocolatey not available
    goto manual_install
)

:manual_install
echo.
echo === Manual Installation Required ===
echo Automatic installation failed. Please:
echo 1. Download Git from: https://git-scm.com/download/win
echo 2. Install Git with default settings
echo 3. Restart this script or deployment
echo.
pause
exit /b 1

:verify_git
echo.
echo Refreshing PATH environment...
call refreshenv 2>nul || echo PATH refresh failed - may need to restart command prompt
timeout /t 2 /nobreak >nul

echo Verifying Git installation...
git --version 2>nul && (
    echo ✅ Git verification successful
    goto configure_git
) || (
    echo ❌ Git still not accessible - may need to restart command prompt
    echo Please restart this script in a new command prompt
    pause
    exit /b 1
)

:configure_git
echo.
echo === Git Configuration ===
echo Current Git configuration:
git config --global user.name 2>nul || echo No global user name set
git config --global user.email 2>nul || echo No global user email set

echo.
echo Setting basic Git configuration...
git config --global user.name "TradeServer" 2>nul || echo Failed to set user name
git config --global user.email "trade@server.local" 2>nul || echo Failed to set user email
git config --global init.defaultBranch main 2>nul || echo Failed to set default branch

echo.
echo === Testing Git Clone ===
echo Testing GitHub connectivity...
cd /d C:\
git ls-remote https://github.com/QuantDeveloperUSA/binance_trade_copier.git HEAD 2>nul && (
    echo ✅ GitHub connectivity successful
) || (
    echo ❌ GitHub connectivity failed
    echo This might be due to:
    echo - Firewall blocking Git
    echo - Network connectivity issues
    echo - Repository access permissions
)

echo.
echo === Git Setup Complete ===
echo Git should now be ready for deployment use.
echo The deployment workflow will use Git to:
echo - Pull latest changes
echo - Remove deleted files automatically
echo - Maintain clean repository state
echo.
pause
