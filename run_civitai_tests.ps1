# CivitAI Test Suite Runner (PowerShell)
Write-Host "🎨 CivitAI Test Suite Runner (PowerShell)" -ForegroundColor Cyan
Write-Host "=========================================="

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "💡 Install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip is available: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip is not installed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install required packages
Write-Host ""
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
pip install requests streamlit

# Check if files exist
$requiredFiles = @("civitai_manual_test.py", "civitai_test_basic.py", "validate_setup.py")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file found" -ForegroundColor Green
    } else {
        Write-Host "❌ $file not found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Run validation first
Write-Host ""
Write-Host "🔍 Running setup validation..." -ForegroundColor Cyan
Write-Host "==============================="
python validate_setup.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Validation passed!" -ForegroundColor Green
    
    # Ask user what they want to do
    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host "1. Run manual tests (recommended first)" -ForegroundColor White
    Write-Host "2. Launch Streamlit app directly" -ForegroundColor White
    Write-Host "3. Exit" -ForegroundColor White
    
    $choice = Read-Host "Enter choice (1-3)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "🧪 Running manual tests..." -ForegroundColor Cyan
            Write-Host "============================"
            python civitai_manual_test.py
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✅ Manual tests completed successfully!" -ForegroundColor Green
                $launchStreamlit = Read-Host "Launch Streamlit app now? (y/n)"
                
                if ($launchStreamlit -eq "y" -or $launchStreamlit -eq "Y") {
                    Write-Host ""
                    Write-Host "🚀 Launching Streamlit app..." -ForegroundColor Cyan
                    Write-Host "App will be available at: http://localhost:8501" -ForegroundColor Yellow
                    streamlit run civitai_test_basic.py
                }
            } else {
                Write-Host "❌ Manual tests failed. Check the output above." -ForegroundColor Red
                Read-Host "Press Enter to exit"
            }
        }
        "2" {
            Write-Host ""
            Write-Host "🚀 Launching Streamlit app..." -ForegroundColor Cyan
            Write-Host "App will be available at: http://localhost:8501" -ForegroundColor Yellow
            streamlit run civitai_test_basic.py
        }
        "3" {
            Write-Host "👋 Goodbye!" -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Host "Invalid choice. Exiting." -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ Validation failed. Fix the issues above before proceeding." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}