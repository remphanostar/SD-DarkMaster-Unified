# 🎨 CivitAI Basic Search & Download Test

## 📋 Overview

This is **Step 1** of implementing CivitAI integration into SD-DarkMaster-Pro. We're starting with basic search and download functionality to ensure everything works before moving to the next step.

## 🗂️ Files Created

### Core Test Files
- **`civitai_test_basic.py`** - Streamlit interface for testing CivitAI functionality
- **`civitai_manual_test.py`** - Command-line test script for systematic testing
- **`validate_setup.py`** - Setup validation script

### Helper Files
- **`run_civitai_tests.sh`** - Automated test runner script
- **`civitai_requirements.txt`** - Required Python packages
- **`CIVITAI_TEST_README.md`** - This instruction file

## 🚀 Quick Start

### Option 1: Automated Testing
```bash
# Run all validations and tests
./run_civitai_tests.sh
```

### Option 2: Manual Step-by-Step
```bash
# 1. Validate setup
python3 validate_setup.py

# 2. Run manual tests
python3 civitai_manual_test.py

# 3. Run Streamlit interface
streamlit run civitai_test_basic.py
```

## 🧪 What Gets Tested

### 1. API Connection ✅
- Tests connection to CivitAI API
- Validates response format
- Checks rate limiting

### 2. Basic Search ✅
- Search for models by query
- Filter by model type (Checkpoint, LoRA, VAE, etc.)
- Sort results by rating/downloads

### 3. Model Details ✅
- Retrieve detailed model information
- Get model versions and files
- Extract download URLs

### 4. File Download ✅
- Download model files
- Progress tracking
- File verification

### 5. File Organization ✅
- Create download directories
- Verify file integrity
- Check file permissions

## 🎯 Expected Results

### Successful Test Run Should Show:
```
✅ CivitAI API accessible - Status: 200
✅ Found X models
✅ Model details retrieved!
✅ Download successful: filename.safetensors
📊 Results: 4/4 tests passed
🎉 ALL TESTS PASSED! Ready for integration.
```

### Streamlit App Should Display:
- 🔑 API Key input (optional)
- 🔍 Search interface with filters
- 📋 Search results with model cards
- 📖 Detailed model information
- 📥 Download buttons for files
- 📂 Downloaded files list

## 🔧 Troubleshooting

### Common Issues & Solutions

**❌ "requests module not found"**
```bash
pip3 install requests streamlit
```

**❌ "CivitAI API not accessible"**
- Check internet connection
- Verify firewall settings
- Try with VPN if region-blocked

**❌ "Permission denied on downloads"**
```bash
chmod 755 .
mkdir -p downloads test_downloads
```

**❌ "Streamlit won't start"**
```bash
# Kill existing processes
pkill -f streamlit
# Restart
streamlit run civitai_test_basic.py --server.port 8501
```

### Rate Limiting
- CivitAI has rate limits for unauthenticated requests
- Get API key from: https://civitai.com/user/account
- Enter in Streamlit interface or set in manual test

## 📊 Test Data

### Default Test Searches:
1. **"realistic"** - Checkpoint models
2. **"anime"** - Checkpoint models  
3. **"lora"** - LoRA models
4. **""** (empty) - VAE models
5. **"portrait"** - Any type

### File Size Limits:
- Manual test: Prefers files < 50MB
- Streamlit: User chooses what to download
- Large files show warning and confirmation

## 🔐 API Key (Optional)

### Without API Key:
- ✅ Basic search works
- ✅ Model details work
- ❌ May hit rate limits
- ❌ No NSFW content access

### With API Key:
- ✅ Higher rate limits
- ✅ NSFW content access
- ✅ Better performance
- ✅ More detailed metadata

Get your free API key: https://civitai.com/user/account

## 📁 Directory Structure After Testing

```
/workspace/
├── civitai_test_basic.py         # Streamlit app
├── civitai_manual_test.py        # Manual tests
├── validate_setup.py             # Setup validator
├── run_civitai_tests.sh          # Test runner
├── downloads/                    # Streamlit downloads
│   └── civitai/
├── test_downloads/               # Manual test downloads
└── CIVITAI_TEST_README.md        # This file
```

## 🎯 Success Criteria

### For Moving to Next Step:
1. ✅ All validation checks pass
2. ✅ Manual tests complete successfully
3. ✅ Streamlit app loads and functions
4. ✅ Can search and view models
5. ✅ Can download at least one file
6. ✅ Downloaded files are verified

### Next Step Will Be:
- Enhanced search filters (tags, NSFW, sorting)
- Image browsing functionality
- Metadata extraction
- Integration with main SD-DarkMaster-Pro app

## 🚨 Important Notes

### Before Testing:
- Ensure stable internet connection
- Have ~1GB free space for test downloads
- Close other applications using port 8501

### During Testing:
- Don't download huge files (>500MB) unless necessary
- Be patient with API responses (can take 5-10 seconds)
- Check console output for detailed error messages

### After Testing:
- Clean up test downloads if not needed:
  ```bash
  rm -rf test_downloads downloads/civitai
  ```

## 📞 Support

If tests fail or you encounter issues:

1. **Check the console output** - detailed error messages
2. **Run validation again** - `python3 validate_setup.py`
3. **Try manual test** - `python3 civitai_manual_test.py`
4. **Check internet connection** - API may be temporarily down

---

**Ready to test? Run: `./run_civitai_tests.sh` or `python3 validate_setup.py`**