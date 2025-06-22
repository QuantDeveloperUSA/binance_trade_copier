@echo off
echo Building Binance Copy Trader Executable...

REM Install PyInstaller if not already installed
pip install pyinstaller pywin32

REM Clean previous builds
rmdir /s /q build dist 2>nul

REM Create PyInstaller spec file
echo Creating spec file...
pyinstaller --onefile --name BinanceCopyTrader ^
    --add-data "templates;templates" ^
    --hidden-import=sqlalchemy.ext.declarative ^
    --hidden-import=uvicorn.logging ^
    --hidden-import=uvicorn.loops ^
    --hidden-import=uvicorn.protocols ^
    --hidden-import=uvicorn.protocols.http ^
    --hidden-import=uvicorn.protocols.http.h11_impl ^
    --hidden-import=uvicorn.protocols.websockets ^
    --hidden-import=uvicorn.lifespan ^
    --hidden-import=uvicorn.lifespan.on ^
    --hidden-import=binance ^
    --hidden-import=binance.client ^
    --hidden-import=binance.streams ^
    main.py

echo.
echo Build complete! Executable is in dist\BinanceCopyTrader.exe
echo.
echo Installing as Windows Service...
python service_installer.py

pause
