@echo off
echo Configuring Windows Firewall for external web access...
echo.

echo Adding inbound rule for port 8000...
netsh advfirewall firewall add rule name="Binance Trade Copier Web" dir=in action=allow protocol=TCP localport=8000
echo.

echo Adding outbound rule for port 8000...
netsh advfirewall firewall add rule name="Binance Trade Copier Web Out" dir=out action=allow protocol=TCP localport=8000
echo.

echo Showing current firewall rules for port 8000...
netsh advfirewall firewall show rule name="Binance Trade Copier Web" verbose
echo.

echo Testing if port is now accessible...
telnet 127.0.0.1 8000
echo.

pause
