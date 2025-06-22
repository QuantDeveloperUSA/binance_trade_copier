@echo off
echo 🧪 Binance Copy Trader Test Suite
echo ================================

REM Install test dependencies
echo Installing test dependencies...
pip install pytest pytest-asyncio httpx

echo.
echo Running Basic System Tests...
python test_system.py

echo.
echo Running Full Test Suite with pytest...
pytest test_system.py -v

echo.
echo Running Integration Tests...
python test_integration.py

echo.
echo Running Performance Tests...
python test_performance.py

echo.
echo 📊 Generating Test Report...
pytest test_system.py --html=reports/test_report.html --self-contained-html

echo.
echo ✅ All tests completed!
echo Check reports/test_report.html for detailed results
pause
