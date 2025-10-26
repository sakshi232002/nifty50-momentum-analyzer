@echo off
REM NIFTY 50 Momentum Analyzer Setup Script for Windows

echo ======================================
echo NIFTY 50 Momentum Analyzer Setup
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ======================================
echo Setup completed successfully!
echo ======================================
echo.
echo To run the analyzer:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Fetch NIFTY 50 stocks: python scrape_nifty50.py
echo 3. Run momentum analysis: python momentum_analyzer.py
echo.
echo To deactivate: deactivate
echo.
pause