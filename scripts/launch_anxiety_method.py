#!/usr/bin/env python3
"""
SD-DarkMaster-Pro WebUI Launcher - AnxietySolo Method
Uses pre-configured packages for guaranteed compatibility
"""

import os
import sys
import subprocess
import asyncio
import json
import time
import shutil
import tarfile
import zipfile
import lz4.frame
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
import urllib.request
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
try:
    project_root = Path(__file__).parent.parent
except NameError:
    # When executed from notebook - detect platform
    if os.path.exists('/content'):
        project_root = Path('/content/SD-DarkMaster-Pro')
    elif os.path.exists('/kaggle'):
        project_root = Path('/kaggle/working/SD-DarkMaster-Pro')
    elif os.path.exists('/workspace'):
        project_root = Path('/workspace/SD-DarkMaster-Pro')
    else:
        project_root = Path.home() / 'SD-DarkMaster-Pro'
        
sys.path.insert(0, str(project_root))

# ============================================================================
# PACKAGE CONFIGURATIONS
# ============================================================================

WEBUI_PACKAGES = {
    'A1111': {
        'name': 'AUTOMATIC1111 WebUI',
        'package_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/A1111.zip',
        'venv_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31018-venv-torch260-cu124-C-fca.tar.lz4',
        'venv_name': 'python31018-venv-torch260-cu124',
        'size': '860 MB',
        'launch_script': 'launch.py',
        'default_port': 7860,
        'vram_min': 4,
        'ready': True
    },
    'Forge': {
        'name': 'Stable Diffusion WebUI Forge',
        'package_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/Forge.zip',
        'venv_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31018-venv-torch260-cu124-C-fca.tar.lz4',
        'venv_name': 'python31018-venv-torch260-cu124',
        'size': '1.01 GB',
        'launch_script': 'launch.py',
        'default_port': 7860,
        'vram_min': 4,
        'ready': True,
        'description': 'Optimized for low VRAM, best for 16GB Colab'
    },
    'ReForge': {
        'name': 'Stable Diffusion WebUI reForge',
        'package_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/ReForge.zip',
        'venv_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31018-venv-torch260-cu124-C-fca.tar.lz4',
        'venv_name': 'python31018-venv-torch260-cu124',
        'size': '1.33 GB',
        'launch_script': 'launch.py',
        'default_port': 7860,
        'vram_min': 4,
        'ready': True
    },
    'ComfyUI': {
        'name': 'ComfyUI',
        'package_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/ComfyUI.zip',
        'venv_url': 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31018-venv-torch260-cu124-C-fca.tar.lz4',
        'venv_name': 'python31018-venv-torch260-cu124',
        'size': '1.04 GB',
        'launch_script': 'main.py',
        'default_port': 8188,
        'vram_min': 4,
        'ready': True,
        'description': 'Best for Flux models and complex workflows'
    },
    'Fooocus': {
        'name': 'Fooocus',
        'package_url': None,  # We need to create this
        'venv_url': None,
        'venv_name': 'python310-venv-torch210-fooocus',
        'size': '~900 MB',
        'launch_script': 'launch.py',
        'default_port': 7865,
        'vram_min': 4,
        'ready': False,
        'description': 'Simplified interface, great for beginners'
    },
    'SD-Next': {
        'name': 'SD.Next (Vladmandic)',
        'package_url': None,  # We need to create this
        'venv_url': None,
        'venv_name': 'python310-venv-torch230-sdnext',
        'size': '~1.2 GB',
        'launch_script': 'launch.py',
        'default_port': 7860,
        'vram_min': 6,
        'ready': False,
        'description': 'Advanced features, latest optimizations'
    },
    'InvokeAI': {
        'name': 'InvokeAI',
        'package_url': None,  # We need to create this
        'venv_url': None,
        'venv_name': 'python310-venv-torch210-invoke',
        'size': '~1.5 GB',
        'launch_script': 'invokeai-web',
        'default_port': 9090,
        'vram_min': 6,
        'ready': False,
        'description': 'Professional UI with advanced features'
    }
}

# ============================================================================
# PACKAGE MANAGER
# ============================================================================

class AnxietyPackageManager:
    """Manages pre-configured WebUI packages using AnxietySolo's method"""
    
    def __init__(self):
        self.project_root = project_root
        self.packages_dir = self.project_root / 'packages'
        self.webuis_dir = self.project_root / 'webuis'
        self.venvs_dir = self.project_root / 'venvs'
        self.storage_dir = self.project_root / 'storage'
        
        # Create directories
        for dir_path in [self.packages_dir, self.webuis_dir, self.venvs_dir, self.storage_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create storage subdirectories
        for subdir in ['models', 'loras', 'vae', 'embeddings', 'hypernetworks', 'controlnet']:
            (self.storage_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def download_with_progress(self, url: str, dest_path: Path, description: str = "Downloading"):
        """Download file with progress bar"""
        
        if dest_path.exists():
            logger.info(f"Using cached: {dest_path.name}")
            return dest_path
        
        logger.info(f"Downloading: {url}")
        
        # Get file size
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
        
        # Download with progress
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=description) as pbar:
            def download_hook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if downloaded < total_size:
                    pbar.update(block_size)
            
            urllib.request.urlretrieve(url, dest_path, reporthook=download_hook)
        
        logger.info(f"✅ Downloaded: {dest_path.name}")
        return dest_path
    
    def extract_zip(self, zip_path: Path, extract_to: Path):
        """Extract ZIP archive"""
        logger.info(f"Extracting {zip_path.name}...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get total files for progress
            total_files = len(zip_ref.namelist())
            
            with tqdm(total=total_files, desc="Extracting") as pbar:
                for file in zip_ref.namelist():
                    zip_ref.extract(file, extract_to)
                    pbar.update(1)
        
        logger.info(f"✅ Extracted to {extract_to}")
    
    def extract_lz4(self, lz4_path: Path, extract_to: Path):
        """Extract LZ4 compressed tar archive"""
        logger.info(f"Extracting {lz4_path.name}...")
        
        # First decompress LZ4 to tar
        tar_path = lz4_path.with_suffix('')
        
        with lz4.frame.open(lz4_path, 'rb') as lz4_file:
            with open(tar_path, 'wb') as tar_file:
                shutil.copyfileobj(lz4_file, tar_file)
        
        # Then extract tar
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(extract_to)
        
        # Clean up tar file
        tar_path.unlink()
        
        logger.info(f"✅ Extracted to {extract_to}")
    
    def link_unified_storage(self, webui_path: Path, webui_type: str):
        """Create symbolic links to unified storage"""
        logger.info("Linking unified storage...")
        
        # Storage mapping for different WebUIs
        storage_mappings = {
            'A1111': {
                'models/Stable-diffusion': self.storage_dir / 'models',
                'models/Lora': self.storage_dir / 'loras',
                'models/VAE': self.storage_dir / 'vae',
                'embeddings': self.storage_dir / 'embeddings',
                'models/hypernetworks': self.storage_dir / 'hypernetworks',
                'models/ControlNet': self.storage_dir / 'controlnet'
            },
            'Forge': {
                # Same as A1111
                'models/Stable-diffusion': self.storage_dir / 'models',
                'models/Lora': self.storage_dir / 'loras',
                'models/VAE': self.storage_dir / 'vae',
                'embeddings': self.storage_dir / 'embeddings',
                'models/hypernetworks': self.storage_dir / 'hypernetworks',
                'models/ControlNet': self.storage_dir / 'controlnet'
            },
            'ReForge': {
                # Same as A1111
                'models/Stable-diffusion': self.storage_dir / 'models',
                'models/Lora': self.storage_dir / 'loras',
                'models/VAE': self.storage_dir / 'vae',
                'embeddings': self.storage_dir / 'embeddings',
                'models/hypernetworks': self.storage_dir / 'hypernetworks',
                'models/ControlNet': self.storage_dir / 'controlnet'
            },
            'ComfyUI': {
                'models/checkpoints': self.storage_dir / 'models',
                'models/loras': self.storage_dir / 'loras',
                'models/vae': self.storage_dir / 'vae',
                'models/embeddings': self.storage_dir / 'embeddings',
                'models/controlnet': self.storage_dir / 'controlnet'
            },
            'Fooocus': {
                'models/checkpoints': self.storage_dir / 'models',
                'models/loras': self.storage_dir / 'loras',
                'models/vae': self.storage_dir / 'vae'
            }
        }
        
        # Get mappings for this WebUI type
        mappings = storage_mappings.get(webui_type, storage_mappings['A1111'])
        
        for webui_subpath, storage_path in mappings.items():
            link_path = webui_path / webui_subpath
            
            # Create parent directory if needed
            link_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove existing link or directory
            if link_path.exists() or link_path.is_symlink():
                if link_path.is_symlink():
                    link_path.unlink()
                elif link_path.is_dir():
                    shutil.rmtree(link_path)
            
            # Create symbolic link
            link_path.symlink_to(storage_path)
            logger.info(f"  Linked: {webui_subpath} → {storage_path.name}")
    
    def install_webui(self, webui_type: str) -> bool:
        """Install pre-configured WebUI package"""
        
        config = WEBUI_PACKAGES.get(webui_type)
        if not config:
            logger.error(f"Unknown WebUI type: {webui_type}")
            return False
        
        if not config['ready']:
            logger.error(f"{webui_type} package not yet available. Need to create it first.")
            return False
        
        webui_path = self.webuis_dir / webui_type
        
        # Check if already installed
        if webui_path.exists():
            logger.info(f"{webui_type} already installed at {webui_path}")
            return True
        
        logger.info(f"Installing {config['name']}...")
        
        # Download WebUI package
        package_filename = f"{webui_type}.zip"
        package_path = self.packages_dir / package_filename
        
        if not package_path.exists():
            self.download_with_progress(
                config['package_url'],
                package_path,
                f"Downloading {webui_type} ({config['size']})"
            )
        
        # Extract WebUI
        self.extract_zip(package_path, self.webuis_dir)
        
        # Download and extract venv if needed
        venv_path = self.venvs_dir / config['venv_name']
        
        if not venv_path.exists():
            venv_filename = f"{config['venv_name']}.tar.lz4"
            venv_archive = self.packages_dir / venv_filename
            
            if not venv_archive.exists():
                self.download_with_progress(
                    config['venv_url'],
                    venv_archive,
                    f"Downloading Python environment (5.22 GB)"
                )
            
            self.extract_lz4(venv_archive, self.venvs_dir)
        
        # Link venv to WebUI
        webui_venv = webui_path / 'venv'
        if not webui_venv.exists():
            webui_venv.symlink_to(venv_path)
            logger.info(f"Linked venv: {config['venv_name']}")
        
        # Link unified storage
        self.link_unified_storage(webui_path, webui_type)
        
        logger.info(f"✅ {config['name']} installed successfully!")
        return True
    
    def launch_webui(self, webui_type: str, port: Optional[int] = None, 
                    share: bool = False, api: bool = False) -> subprocess.Popen:
        """Launch WebUI with its specific venv"""
        
        config = WEBUI_PACKAGES.get(webui_type)
        if not config:
            raise ValueError(f"Unknown WebUI type: {webui_type}")
        
        webui_path = self.webuis_dir / webui_type
        if not webui_path.exists():
            raise FileNotFoundError(f"{webui_type} not installed. Run install first.")
        
        # Use venv Python
        venv_python = webui_path / 'venv' / 'bin' / 'python'
        if not venv_python.exists():
            # Windows compatibility
            venv_python = webui_path / 'venv' / 'Scripts' / 'python.exe'
        
        # Build launch command
        cmd = [str(venv_python), config['launch_script']]
        
        # Add port
        if port is None:
            port = config['default_port']
        cmd.extend(['--port', str(port)])
        
        # Add sharing
        if share:
            cmd.append('--share')
        
        # Add API
        if api:
            cmd.append('--api')
        
        # Add optimizations for low VRAM
        if webui_type in ['Forge', 'ReForge']:
            cmd.extend(['--xformers', '--medvram-sdxl'])
        elif webui_type == 'ComfyUI':
            cmd.extend(['--normalvram', '--use-pytorch-cross-attention'])
        
        logger.info(f"Launching {config['name']} on port {port}...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Launch process
        process = subprocess.Popen(
            cmd,
            cwd=webui_path,
            env={
                **os.environ,
                'CUDA_VISIBLE_DEVICES': '0',
                'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512'
            }
        )
        
        logger.info(f"✅ {config['name']} launched! Access at http://localhost:{port}")
        
        return process
    
    def get_installed_webuis(self) -> list:
        """Get list of installed WebUIs"""
        installed = []
        for webui_type in WEBUI_PACKAGES:
            webui_path = self.webuis_dir / webui_type
            if webui_path.exists():
                installed.append(webui_type)
        return installed
    
    def get_storage_usage(self) -> Dict:
        """Get storage usage statistics"""
        stats = {}
        
        for category in ['models', 'loras', 'vae', 'embeddings']:
            category_path = self.storage_dir / category
            if category_path.exists():
                files = list(category_path.glob('*'))
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                stats[category] = {
                    'count': len(files),
                    'size_gb': round(total_size / (1024**3), 2)
                }
        
        return stats

# ============================================================================
# MAIN INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 SD-DarkMaster-Pro WebUI Launcher")
    print("📦 Using AnxietySolo Pre-configured Packages")
    print("="*60 + "\n")
    
    manager = AnxietyPackageManager()
    
    # Try to load from session.json
    session_file = project_root / 'configs' / 'session.json'
    auto_launch = False
    selected_webui = None
    
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_config = json.load(f)
                selected_webui = session_config.get('webui_type', None)
                if selected_webui:
                    print(f"📄 Loaded configuration from session.json")
                    print(f"🎯 Selected WebUI: {selected_webui}")
                    auto_launch = True
        except Exception as e:
            print(f"⚠️ Error loading session config: {e}")
    
    # Show available WebUIs
    print("Available WebUIs:")
    for webui_type, config in WEBUI_PACKAGES.items():
        status = "✅ Ready" if config['ready'] else "❌ Not Available"
        print(f"  {webui_type}: {config['name']} - {status}")
        if config.get('description'):
            print(f"    → {config['description']}")
    
    print("\n" + "-"*60 + "\n")
    
    # Auto-launch if configured
    if auto_launch and selected_webui:
        print(f"\n🚀 Auto-launching {selected_webui}...")
        
        # Check if installed
        webui_path = manager.webuis_dir / selected_webui
        if not webui_path.exists():
            print(f"📦 Installing {selected_webui} first...")
            if not manager.install_webui(selected_webui):
                print("❌ Installation failed, switching to interactive mode")
                auto_launch = False
        
        if auto_launch:
            try:
                # Get port from config
                port = session_config.get('launch_settings', {}).get('port', None)
                process = manager.launch_webui(selected_webui, port)
                print(f"✅ {selected_webui} launched successfully!")
                print(f"🌐 WebUI running with PID: {process.pid}")
                print("\nPress Ctrl+C to stop the WebUI")
                process.wait()
            except KeyboardInterrupt:
                print("\n⏹️ Stopping WebUI...")
                return
            except Exception as e:
                print(f"❌ Launch failed: {e}")
                print("Switching to interactive mode...")
                auto_launch = False
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Install WebUI")
        print("2. Launch WebUI")
        print("3. Show installed")
        print("4. Show storage usage")
        print("5. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            webui_type = input("WebUI to install (Forge/ComfyUI/etc): ").strip()
            if manager.install_webui(webui_type):
                print("Installation complete!")
        
        elif choice == '2':
            webui_type = input("WebUI to launch: ").strip()
            port = input(f"Port (default {WEBUI_PACKAGES[webui_type]['default_port']}): ").strip()
            port = int(port) if port else None
            
            try:
                process = manager.launch_webui(webui_type, port)
                print(f"WebUI running with PID: {process.pid}")
                print("Press Ctrl+C to stop")
                process.wait()
            except KeyboardInterrupt:
                print("\nStopping WebUI...")
                process.terminate()
        
        elif choice == '3':
            installed = manager.get_installed_webuis()
            print(f"Installed WebUIs: {', '.join(installed) if installed else 'None'}")
        
        elif choice == '4':
            stats = manager.get_storage_usage()
            print("Storage Usage:")
            for category, info in stats.items():
                print(f"  {category}: {info['count']} files, {info['size_gb']} GB")
        
        elif choice == '5':
            break

if __name__ == "__main__":
    main()