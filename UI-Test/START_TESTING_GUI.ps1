# CivitAI Testing Suite - GUI Launcher (PowerShell)
# Professional testing interface with Dark Mode Pro theme

Write-Host ""
Write-Host " ████████╗███████╗███████╗████████╗██╗███╗   ██╗ ██████╗      ██████╗ ██╗   ██╗██╗" -ForegroundColor Green
Write-Host " ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝     ██╔════╝ ██║   ██║██║" -ForegroundColor Green
Write-Host "    ██║   █████╗  ███████╗   ██║   ██║██╔██╗ ██║██║  ███╗    ██║  ███╗██║   ██║██║" -ForegroundColor Green
Write-Host "    ██║   ██╔══╝  ╚════██║   ██║   ██║██║╚██╗██║██║   ██║    ██║   ██║██║   ██║██║" -ForegroundColor Green
Write-Host "    ██║   ███████╗███████║   ██║   ██║██║ ╚████║╚██████╔╝    ╚██████╔╝╚██████╔╝██║" -ForegroundColor Green
Write-Host "    ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝      ╚═════╝  ╚═════╝ ╚═╝" -ForegroundColor Green
Write-Host ""
Write-Host "                          🧪 CivitAI Testing Suite - GUI Launcher 🧪" -ForegroundColor Cyan
Write-Host "                                   Professional Testing Interface" -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================================================================" -ForegroundColor DarkGray
Write-Host ""

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Python is not installed or not found in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 SOLUTION:" -ForegroundColor Yellow
    Write-Host "   1. Download Python from: https://python.org" -ForegroundColor White
    Write-Host "   2. During installation, CHECK 'Add Python to PATH'" -ForegroundColor White
    Write-Host "   3. Restart this script after installation" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Opening Python download page..." -ForegroundColor Cyan
    Start-Process "https://python.org/downloads/"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Streamlit installation
Write-Host "🔍 Checking Streamlit installation..." -ForegroundColor Yellow

try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Streamlit is already installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Streamlit not found. Installing..." -ForegroundColor Yellow
        python -m pip install streamlit --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Streamlit installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install Streamlit" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
} catch {
    Write-Host "❌ Error checking Streamlit installation" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if testing_launcher.py exists
if (-not (Test-Path "testing_launcher.py")) {
    Write-Host ""
    Write-Host "❌ ERROR: testing_launcher.py not found in current directory" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 SOLUTION:" -ForegroundColor Yellow
    Write-Host "   Make sure you're running this from the UI-Test folder" -ForegroundColor White
    Write-Host "   that contains all the testing files." -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting CivitAI Testing Suite GUI..." -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📋 What you'll get:" -ForegroundColor Cyan
Write-Host "   ✅ Professional testing interface" -ForegroundColor White
Write-Host "   ✅ Environment validation tools" -ForegroundColor White
Write-Host "   ✅ Test script launcher and monitor" -ForegroundColor White
Write-Host "   ✅ Real-time process monitoring" -ForegroundColor White
Write-Host "   ✅ File browser and results viewer" -ForegroundColor White
Write-Host "   ✅ Dark Mode Pro theme" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Interface will open at: http://localhost:8502" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C in this window to stop the server" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 3

# Launch the testing GUI
Write-Host "🎨 Launching GUI interface..." -ForegroundColor Green

try {
    # Open browser
    Start-Process "http://localhost:8502"
    
    # Start Streamlit
    streamlit run testing_launcher.py --server.port 8502 --server.headless true
} catch {
    Write-Host "❌ Error launching testing GUI: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "🏁 Testing GUI session ended." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}