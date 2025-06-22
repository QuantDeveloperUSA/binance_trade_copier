@echo off
echo Installing type checking tools...
echo pyright was installed in the requirements.txt... pip install pyright mypy pylint pylint-html

REM Create reports directory
mkdir reports 2>nul

echo.
echo Running Pyright (Pylance CLI)...
pyright --outputjson > reports\pyright_report.json
pyright > reports\pyright_report.txt

echo.
echo Running MyPy type checker...
mypy . --ignore-missing-imports > reports\mypy_report.txt 2>&1

echo.
echo Running Pylint...
pylint *.py --output-format=text > reports\pylint_report.txt 2>&1
pylint *.py --output-format=json > reports\pylint_report.json 2>&1

echo.
echo Type checking complete!
echo.
echo Reports saved to:
echo   reports\pyright_report.txt
echo   reports\pyright_report.json
echo   reports\mypy_report.txt
echo   reports\pylint_report.txt
echo   reports\pylint_report.json
echo.
pause
