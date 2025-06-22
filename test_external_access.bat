@echo off
echo Testing external web access to Binance Trade Copier...
echo.

REM Test from local machine
echo Testing from local machine...
curl -s -m 10 http://5.181.5.168:8000 > temp_response.txt 2>&1

if exist temp_response.txt (
    echo Response received:
    type temp_response.txt | findstr /i "binance\|trade\|copier\|html\|<!DOCTYPE"
    del temp_response.txt
) else (
    echo No response received
)

echo.
echo Testing with telnet...
echo quit | telnet 5.181.5.168 8000

echo.
pause
