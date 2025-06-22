@echo off
echo Testing SSH Key Authentication...
echo.

echo 1. Testing SSH connection with verbose output...
ssh -v trader@5.181.5.168 "echo SSH key authentication working"
echo.

echo 2. If the above failed, test with key file explicitly...
ssh -i C:\Users\Administrator\.ssh\github_deploy trader@5.181.5.168 "echo SSH key authentication working with explicit key"
echo.

echo 3. Check if SSH service is running on VPS...
telnet 5.181.5.168 22
echo.

pause
