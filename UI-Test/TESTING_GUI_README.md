# 🧪 CivitAI Testing Suite - GUI Launcher

## 🎯 What This Is

A **professional testing interface** that provides a comprehensive GUI for managing, launching, and monitoring all your CivitAI integration tests. Built with the same Dark Mode Pro theme as the main SD-DarkMaster-Pro application.

## 🚀 Super Quick Start

### **🖱️ Just Want the GUI?**
1. **Double-click** `START_TESTING_GUI.bat` (Windows Command Prompt)
   
   **OR**
   
2. **Right-click** folder → **"Open PowerShell here"** → `.\START_TESTING_GUI.ps1`

**That's it!** The GUI opens at http://localhost:8502

## 🎨 What You Get

### 📊 **Professional Interface**
- **Dark Mode Pro theme** - Same styling as main app
- **Real-time monitoring** - Live process tracking
- **Comprehensive dashboard** - Overview of all tests
- **Interactive controls** - Launch, stop, monitor tests

### 🧪 **Complete Test Management**
- **Environment validation** - Check Python, packages, API access
- **Script launcher** - One-click test execution
- **Process monitoring** - Real-time CPU/RAM usage
- **Results tracking** - Success/failure history with detailed output

### 📁 **File Management**
- **File browser** - View all test scripts and configs
- **Content viewer** - Read files with syntax highlighting
- **Disk usage** - Monitor storage usage
- **Cleanup tools** - Remove temporary files

## 🖥️ Interface Overview

### **🏠 Overview Page**
- **Quick status** - Environment, running tests, results
- **Quick actions** - Validate, launch UI test, run manual test
- **Environment status** - Python, packages, files, API access
- **Activity log** - Real-time activity monitoring

### **📜 Test Scripts Page**
- **Script cards** - Detailed info for each test
- **Filter & sort** - Find scripts by type, availability
- **Launch controls** - Start, stop, monitor individual tests
- **Status tracking** - Running, success, failed states

### **📊 Results Page**
- **Active processes** - Monitor running tests with CPU/RAM usage
- **Results history** - Complete success/failure tracking
- **Detailed output** - Full command output and error logs
- **Process management** - Stop running tests

### **📁 File Browser Page**
- **File listing** - All scripts, configs, documentation
- **Content viewer** - View files with syntax highlighting
- **File operations** - Refresh, disk usage, cleanup
- **File details** - Size, modification date, type

## 🔧 Available Test Scripts

### **🔍 Environment Validation**
- **File:** `validate_setup.py`
- **Purpose:** Check Python, packages, API access, file permissions
- **Time:** ~30 seconds
- **Output:** Complete environment status report

### **⚙️ Manual Functionality Test**
- **File:** `civitai_manual_test.py`
- **Purpose:** Test CivitAI search, details, download functionality
- **Time:** 2-5 minutes
- **Output:** API responses, download verification

### **🎨 Streamlit UI Test**
- **File:** `civitai_test_basic.py`
- **Purpose:** Interactive web interface for CivitAI integration
- **Time:** Interactive (runs until stopped)
- **Output:** Web interface at localhost:8501

### **🖥️ Windows Automation**
- **Files:** `run_civitai_tests.bat`, `run_civitai_tests.ps1`
- **Purpose:** Run complete test suite automatically
- **Time:** 5-10 minutes
- **Output:** Full automation with progress reporting

### **🚀 Quick Install & Test**
- **File:** `INSTALL_AND_TEST.bat`
- **Purpose:** One-click setup and complete testing
- **Time:** 3-8 minutes
- **Output:** Complete environment + testing

## 💻 System Requirements

### **✅ Minimum:**
- **Windows 10/11**
- **Python 3.7+**
- **4GB RAM**
- **Internet connection**

### **✅ Recommended:**
- **Windows 11**
- **Python 3.9+**
- **8GB+ RAM**
- **Fast internet**

## 🎮 How to Use

### **Step 1: Launch GUI**
```cmd
# Double-click one of these:
START_TESTING_GUI.bat      # Command Prompt version
START_TESTING_GUI.ps1      # PowerShell version (recommended)
```

### **Step 2: Validate Environment**
1. Go to **🏠 Overview** page
2. Click **🔍 Validate Environment**
3. Check that all items show ✅

### **Step 3: Run Tests**
1. Go to **📜 Test Scripts** page
2. Click **🚀 Launch** on any test
3. Monitor progress in **📊 Results** page

### **Step 4: View Results**
1. Check **📊 Results** page for success/failure
2. View detailed output for any issues
3. Use **📁 File Browser** to examine files

## 🔍 Troubleshooting

### **❌ "Python not found"**
1. Install Python from https://python.org
2. ✅ **Check "Add Python to PATH"** during install
3. Restart the launcher

### **❌ "Streamlit not found"**
- The launcher auto-installs Streamlit
- If it fails, run: `pip install streamlit`

### **❌ "testing_launcher.py not found"**
- Make sure you're in the `UI-Test` folder
- All files should be in the same directory

### **❌ "Port 8502 already in use"**
1. Close any existing Streamlit instances
2. Or change port in the launcher script

## 🎯 Success Criteria

### **✅ Environment Ready:**
- Python 3.7+ installed ✅
- All required packages installed ✅
- CivitAI API accessible ✅
- All test files present ✅

### **✅ Tests Working:**
- Environment validation passes ✅
- Manual test completes successfully ✅
- UI test loads and responds ✅
- Downloads work correctly ✅

### **✅ GUI Functional:**
- Interface loads at localhost:8502 ✅
- All pages navigate correctly ✅
- Tests launch and monitor properly ✅
- Results display with details ✅

## 🌟 Pro Tips

### **⚡ Quick Testing Workflow:**
1. **START_TESTING_GUI.bat** → Launch interface
2. **🔍 Validate Environment** → Check everything works
3. **⚙️ Manual Test** → Verify functionality
4. **🎨 UI Test** → Test interactive interface
5. **📊 Monitor Results** → Check success/failure

### **🎨 Interface Features:**
- **Auto-refresh** available on monitor page
- **Real-time logs** in console container
- **Process monitoring** with CPU/RAM usage
- **File viewer** with syntax highlighting
- **Dark theme** matches main application

### **🔧 Advanced Usage:**
- **Filter scripts** by type or availability
- **Monitor multiple** tests simultaneously
- **View detailed output** for debugging
- **Clean temp files** to free space
- **Export results** for documentation

---

## 🎉 Ready to Test!

**🚀 Launch the GUI: Double-click `START_TESTING_GUI.bat`**

**🌐 Access at: http://localhost:8502**

**📖 Full docs: See other README files in this folder**

---

**Happy Testing! 🧪✨**