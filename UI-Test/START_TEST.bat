@echo off
title CivitAI UI Test Launcher
echo.
echo 🎨 CivitAI UI Test Launcher
echo ==========================
echo.
echo This will start the CivitAI testing suite.
echo.
echo Prerequisites:
echo  ✅ Python 3.7+ installed
echo  ✅ Internet connection active
echo  ✅ ~1GB free space for test files
echo.
pause

echo.
echo 🚀 Starting test suite...
echo.

REM Check if PowerShell is available and run the PowerShell script
where powershell >nul 2>nul
if %errorlevel% equ 0 (
    echo 💪 Using PowerShell for better experience...
    powershell -ExecutionPolicy Bypass -File "run_civitai_tests.ps1"
) else (
    echo 📝 Using Command Prompt...
    call run_civitai_tests.bat
)

echo.
echo 🏁 Test session completed.
pause