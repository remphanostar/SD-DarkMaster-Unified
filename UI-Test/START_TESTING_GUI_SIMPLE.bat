@echo off
title CivitAI Testing Suite - GUI Launcher
color 0A

echo.
echo ==========================================================================
echo                   CivitAI Testing Suite - GUI Launcher
echo                        Professional Testing Interface
echo ==========================================================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not found in PATH
    echo.
    echo SOLUTION:
    echo    1. Download Python from: https://python.org
    echo    2. During installation, CHECK "Add Python to PATH"
    echo    3. Restart this script after installation
    echo.
    echo Opening Python download page...
    start https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%

REM Check if Streamlit is installed
echo Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit not found. Installing...
    python -m pip install streamlit --quiet
    if %errorlevel% neq 0 (
        echo Failed to install Streamlit
        pause
        exit /b 1
    )
    echo Streamlit installed successfully
) else (
    echo Streamlit is already installed
)

REM Check if testing_launcher.py exists
if not exist "testing_launcher.py" (
    echo.
    echo ERROR: testing_launcher.py not found in current directory
    echo.
    echo SOLUTION:
    echo    Make sure you're running this from the UI-Test folder
    echo    that contains all the testing files.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting CivitAI Testing Suite GUI...
echo ====================================
echo.
echo What you'll get:
echo    - Professional testing interface
echo    - Environment validation tools
echo    - Test script launcher and monitor
echo    - Real-time process monitoring
echo    - File browser and results viewer
echo    - Dark Mode Pro theme
echo.
echo Interface will open at: http://localhost:8502
echo Press Ctrl+C in this window to stop the server
echo.

REM Set UTF-8 encoding for better Unicode support
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

REM Launch the testing GUI
echo Launching GUI interface...
start http://localhost:8502
streamlit run testing_launcher.py --server.port 8502 --server.headless true

echo.
echo Testing GUI session ended.
pause