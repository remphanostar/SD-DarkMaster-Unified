#!/bin/bash

echo "🎨 CivitAI Test Suite Runner"
echo "============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

echo "✅ Python3 and pip3 are available"

# Install required packages
echo ""
echo "📦 Installing required packages..."
pip3 install requests streamlit

# Check if files exist
if [ ! -f "civitai_manual_test.py" ]; then
    echo "❌ civitai_manual_test.py not found"
    exit 1
fi

if [ ! -f "civitai_test_basic.py" ]; then
    echo "❌ civitai_test_basic.py not found"
    exit 1
fi

echo "✅ All test files found"

# Run manual test first
echo ""
echo "🧪 Running manual tests first..."
echo "================================"
python3 civitai_manual_test.py

# Check if manual tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Manual tests completed!"
    echo ""
    echo "🚀 Now you can run the Streamlit app:"
    echo "   streamlit run civitai_test_basic.py"
    echo ""
    echo "🌐 The app will be available at: http://localhost:8501"
else
    echo "❌ Manual tests failed. Fix issues before running Streamlit app."
fi