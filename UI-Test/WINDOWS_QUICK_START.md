# 🎨 CivitAI UI Test - Windows Quick Start

## 📋 Overview

This folder contains all the files needed to test CivitAI functionality on Windows. Test the UI here, then deploy the actual implementation on Linux cloud platforms (Vast.ai, Lightning AI, Colab).

## 📁 What's in This Folder

```
UI-Test/
├── civitai_test_basic.py           # Main Streamlit UI for testing
├── civitai_manual_test.py          # Command-line functionality test
├── validate_setup.py               # Setup validation script
├── run_civitai_tests.bat          # Windows batch file runner
├── run_civitai_tests.ps1          # PowerShell runner (recommended)
├── civitai_requirements.txt        # Python packages needed
├── CIVITAI_TEST_README.md         # Detailed instructions
└── WINDOWS_QUICK_START.md         # This file
```

## 🚀 Super Quick Start (3 Steps)

### Option 1: PowerShell (Recommended)
```powershell
# 1. Open PowerShell in this folder
# 2. Run the test suite
.\run_civitai_tests.ps1

# 3. Follow the prompts!
```

### Option 2: Command Prompt
```cmd
# 1. Open Command Prompt in this folder
# 2. Run the batch file
run_civitai_tests.bat

# 3. Follow the prompts!
```

### Option 3: Manual Step-by-Step
```cmd
# 1. Install requirements
pip install -r civitai_requirements.txt

# 2. Validate setup
python validate_setup.py

# 3. Test functionality
python civitai_manual_test.py

# 4. Launch UI
streamlit run civitai_test_basic.py
```

## 🎯 What You'll Test

### 1. 🔍 **Search Interface**
- Search CivitAI models by keywords
- Filter by type (Checkpoint, LoRA, VAE, etc.)
- Sort by rating, downloads, date

### 2. 📖 **Model Details**
- View complete model information
- See all available versions
- Browse downloadable files

### 3. 📥 **Download System**
- Download model files with progress
- Organize files by type
- Verify downloads completed

### 4. 🎨 **UI Components**
- Streamlit interface testing
- Button functionality
- Progress bars and status

## 💻 Windows Requirements

### Prerequisites
- **Windows 10/11**
- **Python 3.7+** (Get from https://python.org)
- **Internet connection** for CivitAI API
- **~1GB free space** for test downloads

### Python Installation Check
```cmd
python --version
pip --version
```

If these commands don't work:
1. Install Python from https://python.org
2. ✅ Check "Add Python to PATH" during installation
3. Restart Command Prompt/PowerShell

## 🎮 How to Use

### Step 1: Download & Extract
1. Download this entire `UI-Test` folder
2. Extract to your desired location (e.g., `C:\CivitAI-Test\`)
3. Open folder in Windows Explorer

### Step 2: Run Tests
**Right-click in folder → "Open PowerShell window here"**
```powershell
.\run_civitai_tests.ps1
```

**Or use Command Prompt:**
```cmd
run_civitai_tests.bat
```

### Step 3: Follow Prompts
The script will:
1. ✅ Check Python installation
2. 📦 Install required packages
3. 🔍 Validate setup
4. 🧪 Run functionality tests
5. 🚀 Launch Streamlit UI

### Step 4: Test in Browser
- UI opens at: **http://localhost:8501**
- Test search, view models, try downloads
- Verify everything works as expected

## 🔧 Troubleshooting

### Common Windows Issues

**❌ "python is not recognized"**
```cmd
# Add Python to PATH or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe
```

**❌ "pip install fails"**
```cmd
# Try with --user flag
pip install --user -r civitai_requirements.txt
```

**❌ "PowerShell execution policy"**
```powershell
# Run as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**❌ "Port 8501 already in use"**
```cmd
# Kill any existing Streamlit processes
taskkill /f /im python.exe
# Or use different port
streamlit run civitai_test_basic.py --server.port 8502
```

**❌ "CivitAI API not accessible"**
- Check firewall/antivirus
- Try with VPN if region-restricted
- Verify internet connection

### Performance Tips
- Close other browsers tabs
- Disable antivirus real-time scanning temporarily
- Use wired internet connection for better download speeds
- Don't download huge files during testing

## 📊 Expected Results

### Successful Setup:
```
✅ Python 3.x.x - OK
✅ requests - OK
✅ streamlit - OK
✅ CivitAI API accessible
🎉 ALL CHECKS PASSED!
```

### Successful Test:
```
✅ Found 5 models
✅ Model details retrieved!
✅ Download successful: model.safetensors
📊 Results: 4/4 tests passed
🎉 ALL TESTS PASSED!
```

### Working Streamlit UI:
- Search bar with filters
- Model cards with images
- Download buttons that work
- Progress bars during downloads
- File verification messages

## 🔑 API Key (Optional)

For better performance and access:
1. Go to: https://civitai.com/user/account
2. Generate API key (free)
3. Enter in Streamlit UI when prompted
4. Enjoy higher rate limits and NSFW access

## 🎯 Success Criteria

### ✅ Ready for Linux Deployment When:
1. All validation checks pass
2. Can search and find models
3. Model details load correctly
4. At least one file downloads successfully
5. Streamlit UI is responsive and functional

### 🚀 Next Steps:
Once Windows testing passes:
1. Deploy to Linux cloud platform (Vast.ai/Colab)
2. Integrate with main SD-DarkMaster-Pro
3. Add advanced features (image browsing, metadata)
4. Scale up for production use

## 📞 Need Help?

If you encounter issues:
1. **Check console output** - detailed error messages
2. **Run validation first** - `python validate_setup.py`
3. **Try manual test** - `python civitai_manual_test.py`
4. **Check Windows firewall/antivirus settings**

---

**🎮 Ready to test? Right-click → PowerShell → `.\run_civitai_tests.ps1`**