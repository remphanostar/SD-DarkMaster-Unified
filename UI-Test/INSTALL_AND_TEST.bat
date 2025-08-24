@echo off
title CivitAI Test Suite - Auto Installer
color 0A

echo.
echo  ██████╗██╗██╗   ██╗██╗████████╗ █████╗ ██╗    ████████╗███████╗███████╗████████╗
echo ██╔════╝██║██║   ██║██║╚══██╔══╝██╔══██╗██║    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
echo ██║     ██║██║   ██║██║   ██║   ███████║██║       ██║   █████╗  ███████╗   ██║   
echo ██║     ██║╚██╗ ██╔╝██║   ██║   ██╔══██║██║       ██║   ██╔══╝  ╚════██║   ██║   
echo ╚██████╗██║ ╚████╔╝ ██║   ██║   ██║  ██║██║       ██║   ███████╗███████║   ██║   
echo  ╚═════╝╚═╝  ╚═══╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   
echo.
echo                           🎨 CivitAI Integration Test Suite 🎨
echo                                  Auto-Installer for Windows
echo.
echo ==================================================================================
echo.

REM Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Python is not installed or not found in PATH
    echo.
    echo 💡 SOLUTION:
    echo    1. Download Python from: https://python.org
    echo    2. During installation, CHECK "Add Python to PATH"
    echo    3. Restart this script after installation
    echo.
    echo 🌐 Opening Python download page...
    start https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found: %PYTHON_VERSION%

REM Check pip
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: pip is not available
    echo 💡 Reinstall Python with pip included
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('pip --version 2^>^&1') do set PIP_VERSION=%%i
echo ✅ Found: %PIP_VERSION%

echo.
echo 📦 Installing required Python packages...
echo ============================================
echo.

REM Install packages one by one with progress
echo 🔄 Installing requests...
pip install requests --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ❌ Failed to install requests
    pause
    exit /b 1
)
echo ✅ requests installed

echo 🔄 Installing streamlit...
pip install streamlit --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ❌ Failed to install streamlit
    pause
    exit /b 1
)
echo ✅ streamlit installed

echo 🔄 Installing additional packages...
pip install pathlib pandas --quiet --disable-pip-version-check
echo ✅ Additional packages installed

echo.
echo 🧪 Running setup validation...
echo ==============================
python validate_setup.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉 INSTALLATION SUCCESSFUL!
    echo ===========================
    echo.
    echo ✅ Python: Ready
    echo ✅ Packages: Installed  
    echo ✅ CivitAI API: Accessible
    echo ✅ Test Files: Available
    echo.
    echo 🚀 What's next?
    echo ===============
    echo.
    echo 1️⃣  Test functionality: python civitai_manual_test.py
    echo 2️⃣  Launch UI:           streamlit run civitai_test_basic.py
    echo 3️⃣  Auto-run everything: START_TEST.bat
    echo.
    
    set /p choice="🎮 Launch Streamlit UI now? (Y/N): "
    if /i "%choice%"=="Y" (
        echo.
        echo 🚀 Launching Streamlit UI...
        echo 🌐 Opening browser to: http://localhost:8501
        echo 🛑 Press Ctrl+C in this window to stop the server
        echo.
        timeout /t 3 >nul
        start http://localhost:8501
        streamlit run civitai_test_basic.py
    ) else (
        echo.
        echo 👋 Setup complete! Run START_TEST.bat when ready to test.
    )
) else (
    echo.
    echo ❌ INSTALLATION FAILED
    echo =====================
    echo.
    echo 🔧 Please check the error messages above and:
    echo    1. Ensure stable internet connection
    echo    2. Check Windows firewall settings
    echo    3. Try running as Administrator
    echo    4. Temporarily disable antivirus
    echo.
)

echo.
pause