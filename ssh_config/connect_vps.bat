@echo off
REM Quick SSH connection script for VPS
REM Usage: connect_vps.bat

echo Connecting to VPS (trader@5.181.5.168)...
echo.

REM Try using SSH config first
ssh vps

REM If that fails, fall back to direct connection
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo SSH config failed, trying direct connection...
    ssh -i %USERPROFILE%\.ssh\vps_key trader@5.181.5.168
)

pause
