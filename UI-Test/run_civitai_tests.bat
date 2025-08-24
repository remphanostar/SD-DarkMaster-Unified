@echo off
echo 🎨 CivitAI Test Suite Runner (Windows)
echo =====================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is available

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed
    pause
    exit /b 1
)

echo ✅ pip is available

REM Install required packages
echo.
echo 📦 Installing required packages...
pip install requests streamlit

REM Check if files exist
if not exist "civitai_manual_test.py" (
    echo ❌ civitai_manual_test.py not found
    pause
    exit /b 1
)

if not exist "civitai_test_basic.py" (
    echo ❌ civitai_test_basic.py not found
    pause
    exit /b 1
)

echo ✅ All test files found

REM Run manual test first
echo.
echo 🧪 Running manual tests first...
echo ================================
python civitai_manual_test.py

REM Check if manual tests passed
if %errorlevel% equ 0 (
    echo.
    echo ✅ Manual tests completed!
    echo.
    echo 🚀 Now you can run the Streamlit app:
    echo    streamlit run civitai_test_basic.py
    echo.
    echo 🌐 The app will be available at: http://localhost:8501
    echo.
    echo Press any key to launch Streamlit app...
    pause >nul
    streamlit run civitai_test_basic.py
) else (
    echo ❌ Manual tests failed. Fix issues before running Streamlit app.
    pause
)