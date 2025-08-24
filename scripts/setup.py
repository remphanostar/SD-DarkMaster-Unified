#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Setup Script
Handles environment initialization and dependency installation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import platform as platform_module

# Platform detection
def detect_platform():
    """Detect the current runtime platform"""
    if 'google.colab' in sys.modules:
        return 'colab'
    elif os.path.exists('/kaggle'):
        return 'kaggle'
    elif os.path.exists('/workspace'):
        return 'workspace'
    else:
        return 'local'

# Get project root
try:
    project_root = Path(__file__).parent.parent
except NameError:
    # When run from notebook
    platform = detect_platform()
    if platform == 'colab':
        project_root = Path('/content/SD-DarkMaster-Pro')
    elif platform == 'kaggle':
        project_root = Path('/kaggle/working/SD-DarkMaster-Pro')
    elif platform == 'workspace':
        project_root = Path('/workspace/SD-DarkMaster-Pro')
    else:
        project_root = Path.home() / 'SD-DarkMaster-Pro'

# Create necessary directories
directories = [
    project_root / 'configs',
    project_root / 'storage',
    project_root / 'storage/models',
    project_root / 'storage/loras',
    project_root / 'storage/vae',
    project_root / 'storage/controlnet',
    project_root / 'storage/embeddings',
    project_root / 'logs'
]

print("📁 Creating directory structure...")
for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ {directory}")

# Platform-specific setup
platform = detect_platform()
print(f"\n🖥️ Detected platform: {platform}")

# Install requirements based on platform
if platform == 'colab':
    print("\n📦 Installing Colab-specific dependencies (verbose mode)...")
    print("-" * 60)
    
    # Core dependencies
    deps = [
        'streamlit',
        'aria2p',
        'gdown',
        'psutil',
        'requests',
        'beautifulsoup4',
        'tqdm',
        'pyngrok',
        'ipywidgets'
    ]
    
    for dep in deps:
        print(f"\n🔧 Installing {dep}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', dep, '-v'],
            capture_output=False,  # Show all output
            text=True
        )
        print(f"✅ {dep} installation completed with exit code: {result.returncode}")
    
    print("-" * 60)
    
    # Enable Colab widgets
    print("\n🎛️ Enabling Colab widgets extension...")
    subprocess.run(['jupyter', 'nbextension', 'enable', '--py', 'widgetsnbextension'], 
                   capture_output=False)
    
elif platform == 'kaggle':
    print("\n📦 Installing Kaggle dependencies (verbose mode)...")
    print("-" * 60)
    
    # Kaggle often has most packages pre-installed
    deps = ['aria2p', 'pyngrok']
    
    for dep in deps:
        print(f"\n🔧 Installing {dep}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', dep, '-v'],
            capture_output=False,
            text=True
        )
        print(f"✅ {dep} installation completed with exit code: {result.returncode}")
    
    print("-" * 60)

else:
    print("\n📦 Installing general dependencies (verbose mode)...")
    print("-" * 60)
    
    # Try to install from requirements.txt if it exists
    req_file = project_root / 'scripts/requirements.txt'
    if req_file.exists():
        print(f"📋 Installing from {req_file}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(req_file), '-v'],
            capture_output=False,
            text=True
        )
        print(f"✅ Requirements installation completed with exit code: {result.returncode}")
    else:
        # Fallback to essential packages
        deps = [
            'streamlit',
            'aria2p',
            'requests',
            'psutil',
            'tqdm',
            'ipywidgets'
        ]
        
        for dep in deps:
            print(f"\n🔧 Installing {dep}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep, '-v'],
                capture_output=False,
                text=True
            )
            print(f"✅ {dep} installation completed with exit code: {result.returncode}")
    
    print("-" * 60)

# Create default configuration
config_file = project_root / 'configs/environment.json'
if not config_file.exists():
    print("\n📝 Creating default configuration...")
    default_config = {
        'platform': platform,
        'project_root': str(project_root),
        'storage_path': str(project_root / 'storage'),
        'aria2_enabled': True,
        'concurrent_downloads': 3,
        'theme': 'dark'
    }
    
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"✅ Configuration saved to: {config_file}")

# Check if aria2c is available
print("\n🔍 Checking for aria2c...")
try:
    result = subprocess.run(['aria2c', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ aria2c is available")
    else:
        print("❌ aria2c not found, trying to install...")
        if platform == 'colab':
            subprocess.run(['apt-get', 'update'], capture_output=False)
            subprocess.run(['apt-get', 'install', '-y', 'aria2'], capture_output=False)
        else:
            print("⚠️ Please install aria2 manually for faster downloads")
except FileNotFoundError:
    print("❌ aria2c not found")
    if platform == 'colab':
        print("📦 Installing aria2 on Colab...")
        subprocess.run(['apt-get', 'update'], capture_output=False)
        subprocess.run(['apt-get', 'install', '-y', 'aria2'], capture_output=False)

print("\n✅ Setup complete!")
print(f"📂 Project root: {project_root}")
print(f"💾 Storage path: {project_root / 'storage'}")
print(f"🖥️ Platform: {platform}")

# Set environment variables
os.environ['SD_DARKMASTER_ROOT'] = str(project_root)
os.environ['SD_DARKMASTER_PLATFORM'] = platform

print("\n🚀 Ready to run Cell 2!")