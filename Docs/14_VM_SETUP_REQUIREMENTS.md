# VM Setup Requirements for SD-DarkMaster-Pro Unified
**For AI Agents and Cloud Platform VMs**  
**Last Updated:** 2025-01-24 22:20 UTC  
**Version:** 1.0.0

---

## 🚀 **QUICK VM SETUP CHECKLIST**

### **Essential Pre-Requirements:**
```bash
# 1. Python 3.8+ (Recommended: Python 3.10)
python3 --version

# 2. Git (for repository cloning)
git --version

# 3. Pip (Python package manager)
pip --version

# 4. Basic system tools
which curl wget
```

---

## 🖥️ **Platform-Specific Setup Commands**

### **Google Colab** (Usually Pre-configured)
```python
# Check if pre-installed
import sys
print(f"Python: {sys.version}")

# Install missing dependencies if needed
!pip install --upgrade pip
!pip install streamlit pyngrok aria2c-python
```

### **Kaggle** (Usually Pre-configured)
```python
# Kaggle typically has most requirements
# Just ensure Streamlit is available
!pip install streamlit>=1.29.0 pyngrok
```

### **Linux VMs (Ubuntu/Debian)**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10 if not available
sudo apt install python3.10 python3.10-pip python3.10-venv -y

# Install system dependencies
sudo apt install git curl wget aria2 -y

# Install Python packages
pip3 install --upgrade pip
pip3 install streamlit>=1.29.0 pyngrok aria2c-python
```

### **Windows VMs**
```powershell
# Install Python 3.10+ from python.org
# Then install dependencies
pip install --upgrade pip
pip install streamlit>=1.29.0 pyngrok aria2c-python

# Install Git for Windows if needed
# Install aria2 manually or via chocolatey
```

### **macOS VMs**
```bash
# Install Homebrew if not available
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python@3.10 git aria2
pip3 install --upgrade pip
pip3 install streamlit>=1.29.0 pyngrok aria2c-python
```

---

## 📦 **Core Dependencies Required**

### **COMPLETE Installation Stack (From Proven OlDocs)**
**Based on successful installation log - these EXACT versions work:**

#### **Core ML Stack (CPU Versions for Testing)**
```bash
# PyTorch CPU stack - Essential for ML operations and testing
pip install torch==2.8.0+cpu torchvision==0.23.0+cpu torchaudio==2.8.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Hugging Face ecosystem - Required for model loading and processing
pip install diffusers==0.35.0 transformers==4.55.2 accelerate==1.10.0
pip install huggingface_hub==0.34.4 safetensors==0.6.2

# Image processing - Required for SD image operations
pip install opencv-python-headless==4.12.0.88 pillow==11.0.0 imageio==2.37.0
pip install numpy==2.3.2 matplotlib==3.10.5
```

#### **Notebook Development Tools**
```bash
# Jupyter ecosystem - Essential for notebook development and testing
pip install jupyterlab==4.4.6 nbformat==5.10.4 jupytext==1.17.2
pip install py2nb==1.1.1 ipywidgets==8.1.7 nbconvert==7.16.6

# Data processing - Required for model metadata and configuration handling
pip install pandas==2.3.1 pyarrow==21.0.0 pyyaml==6.0.2
pip install requests==2.32.5 tqdm==4.67.1
```

#### **UI Framework Dependencies**
```bash
# Web frameworks - Required for Streamlit interface and fallbacks
pip install streamlit==1.48.1 gradio==5.42.0 fastapi==0.116.1
pip install uvicorn==0.35.0 flask==3.1.1 dash==3.2.0

# Development tools - Code quality and testing
pip install black==25.1.0 isort==6.0.1 pytest==8.4.1
```

### **Python Packages (Essential Minimum)**
```txt
streamlit>=1.29.0              # Main UI framework
pyngrok>=6.0.0                 # Tunnel creation
aria2c-python>=2.0.0           # Fast downloads
requests>=2.31.0               # HTTP requests
pathlib                        # File path handling (built-in Python 3.4+)
json                           # JSON handling (built-in)
subprocess                     # Process execution (built-in)
threading                      # Multi-threading (built-in)
asyncio                        # Async operations (built-in Python 3.7+)
```

### **System Tools Required**
```bash
git                            # Repository cloning
curl                           # HTTP requests
wget                           # File downloads (backup to aria2)
aria2c                         # High-speed downloads
python3                        # Python interpreter (3.8+)
pip3                           # Python package manager
```

### **Optional Enhancements**
```txt
# Enhanced UI Components (install via streamlit_components_requirements.txt)
streamlit-option-menu>=0.3.6   # Better navigation
streamlit-antd-components>=0.3.0 # Ant Design components
streamlit-extras>=0.3.6        # Additional UI elements
streamlit-aggrid>=0.3.4        # Advanced data grids
```

---

## 🔧 **Complete VM Setup Script**

### **One-Command Setup (Linux/macOS)**
```bash
#!/bin/bash
# SD-DarkMaster-Pro VM Setup Script

echo "🚀 Setting up VM for SD-DarkMaster-Pro Unified..."

# Update system (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3.10 python3.10-pip python3.10-venv git curl wget aria2 -y
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with Homebrew
    brew install python@3.10 git aria2
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install streamlit>=1.29.0 pyngrok aria2c-python requests

# Verify installation
echo "✅ Verifying installation..."
python3 --version
pip3 --version
git --version
streamlit --version

echo "🎉 VM setup complete! Ready for SD-DarkMaster-Pro Unified"
```

### **Windows PowerShell Setup**
```powershell
# SD-DarkMaster-Pro VM Setup Script (Windows)
Write-Host "🚀 Setting up Windows VM for SD-DarkMaster-Pro Unified..."

# Check Python installation
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "❌ Python not found. Please install Python 3.10+ from python.org"
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install streamlit pyngrok aria2c-python requests

# Verify installation
Write-Host "✅ Verifying installation..."
python --version
pip --version
git --version
streamlit --version

Write-Host "🎉 Windows VM setup complete!"
```

---

## 🌐 **Platform-Specific Optimizations**

### **Google Colab Optimizations**
```python
# Install Colab-specific tunneling
!pip install pyngrok

# Configure for Colab filesystem
import os
os.environ['COLAB_WORKSPACE'] = '/content'
```

### **Kaggle Optimizations**
```python
# Kaggle workspace configuration
import os
os.environ['KAGGLE_WORKSPACE'] = '/kaggle/working'

# Enable internet access (if needed)
# Note: Some Kaggle competitions disable internet
```

### **Cloud VM Optimizations**
```bash
# For AWS/GCP/Azure VMs
# Ensure ports 8501 (Streamlit) and 4040 (ngrok) are open
sudo ufw allow 8501
sudo ufw allow 4040

# For better performance
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
```

---

## 🚨 **Troubleshooting Common Issues**

### **Python Version Issues**
```bash
# If Python 3.10 not available, minimum Python 3.8
python3.8 --version
pip3.8 install streamlit pyngrok

# Create virtual environment for isolation
python3 -m venv sd-darkmaster-env
source sd-darkmaster-env/bin/activate  # Linux/macOS
# sd-darkmaster-env\Scripts\activate   # Windows
```

### **Permission Issues**
```bash
# Linux/macOS permission fixes
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.py

# Windows: Run PowerShell as Administrator
```

### **Network/Firewall Issues**
```bash
# Check if required ports are accessible
curl -I http://localhost:8501
curl -I http://localhost:4040

# Test internet connectivity
curl -I https://github.com
curl -I https://civitai.com
```

### **Memory/Storage Issues**
```bash
# Check available space (need ~10GB minimum)
df -h

# Check memory (recommend 8GB+ RAM)
free -h

# Clear package cache if needed
pip cache purge
```

---

## ⚠️ **CRITICAL: Installation Issues & Solutions**
**Based on OlDocs installation log - Common problems and proven fixes:**

### **Python 3.13 Compatibility Issues**
**Problem:** pandas==2.2.2 fails to compile with Python 3.13
```
Error: 'maybe_unused' attribute cannot be applied to types
```
**Solution:** Use pandas==2.3.1 (pre-compiled binary)
```bash
pip install pandas==2.3.1
```

### **Externally Managed Environment**
**Problem:** System Python is externally managed
**Solution:** Create virtual environment
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# Required system packages for Ubuntu/Debian
sudo apt install python3-venv python3-full python3-pip
```

### **Gradio Dependencies Partial Install**
**Problem:** Gradio installed without full dependencies due to pandas conflicts
- Missing: aiofiles, audioop-lts, brotli, ffmpy, gradio-client
- Missing: orjson, pydub, python-multipart, ruff, safehttpx

**Impact:** Basic gradio functionality available, some features limited
**Workaround:** Use Streamlit as primary, Gradio as fallback

### **Complex UI Frameworks Skipped**
- **taipy==4.0.2** - Skipped due to compilation issues with Python 3.13
- **marimo==0.14.17** - Skipped due to dependency conflicts  
- **panel==1.7.5** - Skipped due to size and complexity

**Alternative:** Current stack (Streamlit + basic Gradio) covers all core UI needs

### **Virtual Environment Performance**
- **Total Install Time:** ~15 minutes  
- **Disk Usage:** ~2.1GB in virtual environment  
- **Memory:** Works with 4GB RAM minimum
- **Status:** ✅ Ready for ML development and UI creation

---

## ✅ **Verification Checklist**

Before running SD-DarkMaster-Pro Unified, verify:

- [ ] **Python 3.8+** installed and accessible
- [ ] **Git** installed and working
- [ ] **Streamlit** installed (`streamlit --version`)
- [ ] **Pyngrok** installed (`python -c "import pyngrok"`)
- [ ] **Aria2** available (`aria2c --version`)
- [ ] **Internet access** working (for model downloads)
- [ ] **Sufficient storage** (10GB+ free space)
- [ ] **Port access** (8501 for Streamlit, 4040 for tunnels)

### **Quick Test Command**
```bash
# Test if everything is working
python3 -c "
import streamlit
import pyngrok
import aria2p
print('✅ All core dependencies available!')
print(f'Streamlit: {streamlit.__version__}')
print(f'Pyngrok: {pyngrok.__version__}')
"
```

---

## 🎯 **After Setup: Running SD-DarkMaster-Pro**

Once your VM is properly configured:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/SD-DarkMaster-Pro-Unified.git
   cd SD-DarkMaster-Pro-Unified
   ```

2. **Run the single cell** in `notebook/SD-DarkMaster-Pro-Unified.ipynb`

3. **Access via public URL** (automatically generated)

4. **Start creating AI art!**

---

## 📝 **Notes for AI Agents**

When setting up VMs for users:

- **Always show full command output** (follow user rules for transparency)
- **Check each dependency** individually with verification
- **Provide fallback options** if primary installation methods fail
- **Test the setup** before declaring completion
- **Update this document** if new dependencies are discovered

---

**This document ensures any VM or cloud environment can quickly be prepared for SD-DarkMaster-Pro Unified development and usage.**
