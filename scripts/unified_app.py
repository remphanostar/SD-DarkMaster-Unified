#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Unified Interface
Single Streamlit app that handles all operations
"""

import streamlit as st
import os
import sys
import json
import subprocess
import time
import threading
import shutil
from pathlib import Path
from datetime import datetime
import psutil
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="SD-DarkMaster-Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'selected_models' not in st.session_state:
    st.session_state.selected_models = []
if 'download_queue' not in st.session_state:
    st.session_state.download_queue = []
if 'webui_process' not in st.session_state:
    st.session_state.webui_process = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Import model data
from scripts._models_data import model_list as sd15_models
from scripts._xl_models_data import model_list as sdxl_models

# Helper functions
def run_command(cmd, stream_output=False):
    """Run a command and optionally stream output"""
    if stream_output:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        output = []
        for line in iter(process.stdout.readline, ''):
            if line:
                output.append(line.strip())
                st.text(line.strip())
        process.wait()
        return process.returncode, '\n'.join(output)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode, result.stdout + result.stderr

def add_log(message, level="info"):
    """Add message to activity log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({
        'time': timestamp,
        'level': level,
        'message': message
    })

# Page Functions
def home_page():
    """Home dashboard"""
    st.title("🎨 SD-DarkMaster-Pro")
    st.markdown("### Unified Interface for Stable Diffusion WebUIs")
    
    # Status cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Setup Status", "✅ Ready" if st.session_state.setup_complete else "❌ Pending")
    with col2:
        st.metric("Selected Models", len(st.session_state.selected_models))
    with col3:
        st.metric("Download Queue", len(st.session_state.download_queue))
    with col4:
        st.metric("WebUI Status", "🟢 Running" if st.session_state.webui_process else "⚫ Stopped")
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Quick Setup", use_container_width=True):
            setup_page()
    
    with col2:
        if st.button("📦 Browse Models", use_container_width=True):
            models_page()
    
    with col3:
        if st.button("🎯 Launch WebUI", use_container_width=True):
            launch_page()
    
    # Activity log
    st.markdown("### Recent Activity")
    if st.session_state.logs:
        for log in st.session_state.logs[-10:]:
            icon = "✅" if log['level'] == "success" else "ℹ️" if log['level'] == "info" else "⚠️"
            st.text(f"[{log['time']}] {icon} {log['message']}")
    else:
        st.info("No recent activity")

def setup_page():
    """Setup and configuration"""
    st.title("⚙️ Setup & Configuration")
    
    # Platform info
    st.markdown("### Platform Information")
    col1, col2, col3, col4 = st.columns(4)
    
    platform = "Colab" if os.path.exists('/content') else "Kaggle" if os.path.exists('/kaggle') else "Local"
    with col1:
        st.info(f"Platform: {platform}")
    with col2:
        st.info(f"Python: {sys.version.split()[0]}")
    with col3:
        gpu_check = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if gpu_check.returncode == 0:
            # Parse GPU name
            gpu_name = "GPU Found"
            for line in gpu_check.stdout.split('\n'):
                if 'NVIDIA' in line and 'Off' not in line:
                    gpu_name = line.split('|')[1].strip().split()[0]
                    break
            st.success(f"GPU: {gpu_name}")
        else:
            st.error("GPU: Not Found")
    with col4:
        st.info(f"RAM: {psutil.virtual_memory().total // (1024**3)} GB")
    
    # Directory structure
    st.markdown("### Directory Structure")
    dirs_status = []
    required_dirs = [
        'configs', 
        'storage/models', 
        'storage/loras', 
        'storage/vae', 
        'storage/controlnet',
        'storage/embeddings',
        'webuis',
        'logs'
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        dirs_status.append({
            'Directory': dir_path,
            'Status': '✅ Exists' if exists else '❌ Missing',
            'Path': str(full_path)
        })
    
    # Display as table
    import pandas as pd
    df = pd.DataFrame(dirs_status)
    st.dataframe(df, use_container_width=True)
    
    # Setup actions
    st.markdown("### Setup Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Create Directories", use_container_width=True):
            for dir_path in required_dirs:
                (project_root / dir_path).mkdir(parents=True, exist_ok=True)
            st.success("✅ All directories created!")
            add_log("Created directory structure", "success")
            st.rerun()
    
    with col2:
        if st.button("📦 Install Dependencies", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            
            deps = {
                'aria2': 'apt-get install -y aria2',
                'wget': 'apt-get install -y wget',
                'git-lfs': 'apt-get install -y git-lfs',
                'streamlit': f'{sys.executable} -m pip install streamlit',
                'gradio': f'{sys.executable} -m pip install gradio',
                'requests': f'{sys.executable} -m pip install requests',
                'beautifulsoup4': f'{sys.executable} -m pip install beautifulsoup4',
                'psutil': f'{sys.executable} -m pip install psutil',
                'humanize': f'{sys.executable} -m pip install humanize'
            }
            
            for i, (dep, cmd) in enumerate(deps.items()):
                status.text(f"Installing {dep}...")
                if 'apt-get' in cmd:
                    subprocess.run(cmd.split(), capture_output=True)
                else:
                    subprocess.run(cmd.split(), capture_output=True)
                progress.progress((i + 1) / len(deps))
            
            status.text("✅ All dependencies installed!")
            add_log("Installed all dependencies", "success")
            st.session_state.setup_complete = True

def models_page():
    """Model selection interface"""
    st.title("📦 Model Selection")
    
    # Model type tabs
    tab1, tab2, tab3 = st.tabs(["SD 1.5", "SDXL", "CivitAI Search"])
    
    with tab1:
        st.markdown("### SD 1.5 Models")
        
        # Model grid
        cols = st.columns(3)
        for idx, (name, info) in enumerate(list(sd15_models.items())[:9]):
            with cols[idx % 3]:
                if st.checkbox(name[:30], key=f"sd15_{name}"):
                    if f"sd15_{name}" not in st.session_state.selected_models:
                        st.session_state.selected_models.append(f"sd15_{name}")
                        add_log(f"Selected model: {name}", "info")
    
    with tab2:
        st.markdown("### SDXL Models")
        
        # Model grid
        cols = st.columns(3)
        for idx, (name, info) in enumerate(list(sdxl_models.items())[:9]):
            with cols[idx % 3]:
                if st.checkbox(name[:30], key=f"sdxl_{name}"):
                    if f"sdxl_{name}" not in st.session_state.selected_models:
                        st.session_state.selected_models.append(f"sdxl_{name}")
                        add_log(f"Selected model: {name}", "info")
    
    with tab3:
        st.markdown("### CivitAI Search")
        
        search_term = st.text_input("Search models on CivitAI")
        if st.button("🔍 Search"):
            st.info("CivitAI search coming soon...")
    
    # Save selections
    if st.button("💾 Save Selections", type="primary"):
        config = {
            'selected_models': st.session_state.selected_models,
            'timestamp': datetime.now().isoformat()
        }
        with open(project_root / 'configs' / 'session.json', 'w') as f:
            json.dump(config, f, indent=2)
        st.success("Selections saved!")
        add_log("Model selections saved", "success")

def downloads_page():
    """Download management"""
    st.title("💾 Downloads")
    
    # Load actual model data for downloads
    all_models = {}
    all_models.update({f"sd15_{k}": v for k, v in sd15_models.items()})
    all_models.update({f"sdxl_{k}": v for k, v in sdxl_models.items()})
    
    # Download queue
    st.markdown("### Download Queue")
    if st.session_state.selected_models:
        total_size = 0
        download_items = []
        
        for model_id in st.session_state.selected_models:
            model_data = all_models.get(model_id, {})
            if isinstance(model_data, dict) and 'link' in model_data:
                url = model_data['link']
                name = model_id.replace('sd15_', '').replace('sdxl_', '')
                size = model_data.get('size', 'Unknown')
                download_items.append({'id': model_id, 'name': name, 'url': url, 'size': size})
                
        # Display download items
        for item in download_items:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.text(item['name'][:40])
            with col2:
                st.text(item['size'])
            with col3:
                st.text("Ready")
            with col4:
                if st.button("❌", key=f"rm_{item['id']}"):
                    st.session_state.selected_models.remove(item['id'])
                    st.rerun()
    else:
        st.info("No models selected for download")
    
    # Download action
    if st.button("⬇️ Start Downloads", type="primary", disabled=not st.session_state.selected_models):
        download_placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create download directory
        download_dir = project_root / 'storage' / 'models'
        download_dir.mkdir(parents=True, exist_ok=True)
        
        total_items = len(download_items)
        for idx, item in enumerate(download_items):
            status_text.text(f"Downloading {item['name']}...")
            
            # Use wget for actual download
            output_path = download_dir / f"{item['name']}.safetensors"
            cmd = f"wget -c -O '{output_path}' '{item['url']}' --progress=bar:force 2>&1"
            
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Show real progress
            for line in process.stdout:
                if '%' in line:
                    try:
                        percent = int(line.split('%')[0].split()[-1])
                        item_progress = (idx + percent/100) / total_items
                        progress_bar.progress(item_progress)
                    except:
                        pass
                        
            process.wait()
            
            if process.returncode == 0:
                add_log(f"Downloaded {item['name']}", "success")
            else:
                add_log(f"Failed to download {item['name']}", "error")
            
            progress_bar.progress((idx + 1) / total_items)
        
        status_text.text("✅ All downloads completed!")
        st.success(f"Downloaded {total_items} models to {download_dir}")

def launch_page():
    """WebUI launcher"""
    st.title("🚀 WebUI Launcher")
    
    # WebUI mapping
    webui_map = {
        "Automatic1111": {
            "repo": "https://github.com/AUTOMATIC1111/stable-diffusion-webui.git",
            "dir": "stable-diffusion-webui",
            "launch_script": "launch.py"
        },
        "Forge": {
            "repo": "https://github.com/lllyasviel/stable-diffusion-webui-forge.git",
            "dir": "stable-diffusion-webui-forge",
            "launch_script": "launch.py"
        },
        "ComfyUI": {
            "repo": "https://github.com/comfyanonymous/ComfyUI.git",
            "dir": "ComfyUI",
            "launch_script": "main.py"
        }
    }
    
    # WebUI selection
    webui_type = st.selectbox(
        "Select WebUI",
        list(webui_map.keys())
    )
    
    # Launch options
    col1, col2 = st.columns(2)
    with col1:
        port = st.number_input("Port", value=7860, min_value=7000, max_value=9000)
    with col2:
        share = st.checkbox("Create public link", value=True)
    
    # Show WebUI status
    webui_info = webui_map[webui_type]
    webui_path = project_root / 'webuis' / webui_info['dir']
    
    if webui_path.exists():
        st.success(f"✅ {webui_type} is installed at {webui_path}")
    else:
        st.info(f"📦 {webui_type} will be installed on first launch")
    
    # Launch button
    if st.button("🚀 Launch WebUI", type="primary"):
        status_placeholder = st.empty()
        log_placeholder = st.empty()
        
        # Create webuis directory
        webuis_dir = project_root / 'webuis'
        webuis_dir.mkdir(exist_ok=True)
        
        # Clone if needed
        if not webui_path.exists():
            status_placeholder.info(f"📥 Cloning {webui_type} repository...")
            cmd = f"cd {webuis_dir} && git clone {webui_info['repo']}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                st.error(f"Failed to clone repository: {result.stderr}")
                return
        
        # Create launch command
        launch_cmd = f"cd {webui_path} && python {webui_info['launch_script']} --port {port}"
        if share:
            launch_cmd += " --share"
        if webui_type == "Forge":
            launch_cmd += " --xformers"
        
        # Launch in background
        status_placeholder.info(f"🚀 Starting {webui_type}...")
        
        # Kill any existing process
        subprocess.run("pkill -f 'stable-diffusion-webui'", shell=True)
        subprocess.run("pkill -f 'ComfyUI'", shell=True)
        time.sleep(2)
        
        # Start the WebUI
        process = subprocess.Popen(
            launch_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Store process
        st.session_state.webui_process = process
        
        # Monitor output
        output_lines = []
        start_time = time.time()
        webui_url = None
        
        while time.time() - start_time < 120:  # 2 minute timeout
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
                # Keep last 10 lines
                if len(output_lines) > 10:
                    output_lines.pop(0)
                
                # Show output
                log_placeholder.code('\n'.join(output_lines))
                
                # Check for URL
                if 'Running on' in line or 'Public URL:' in line:
                    if 'http' in line:
                        webui_url = line.split('http')[1].strip()
                        webui_url = 'http' + webui_url
                        break
            
            if process.poll() is not None:
                st.error("WebUI process terminated unexpectedly")
                break
                
            time.sleep(0.1)
        
        if webui_url:
            status_placeholder.success(f"✅ {webui_type} is running!")
            st.info(f"🌐 Access your WebUI at: {webui_url}")
            add_log(f"Launched {webui_type} at {webui_url}", "success")
        else:
            status_placeholder.warning("WebUI started but URL not detected. Check the logs above.")

def storage_page():
    """Storage management"""
    st.title("🧹 Storage Management")
    
    # Get actual storage stats
    storage_path = project_root / 'storage'
    storage_path.mkdir(exist_ok=True)
    
    def get_dir_size(path):
        """Get directory size in bytes"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry.path)
        except:
            pass
        return total
    
    def format_bytes(bytes):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    # Calculate real sizes
    models_size = get_dir_size(storage_path / 'models')
    loras_size = get_dir_size(storage_path / 'loras')
    vae_size = get_dir_size(storage_path / 'vae')
    controlnet_size = get_dir_size(storage_path / 'controlnet')
    total_size = models_size + loras_size + vae_size + controlnet_size
    
    # Get disk usage
    disk = psutil.disk_usage(str(storage_path))
    
    # Storage stats
    st.markdown("### Storage Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Used", format_bytes(total_size))
    with col2:
        st.metric("Disk Total", format_bytes(disk.total))
    with col3:
        st.metric("Disk Free", format_bytes(disk.free))
    with col4:
        st.metric("Usage", f"{disk.percent:.1f}%")
    
    # Storage breakdown
    st.markdown("### Storage Breakdown")
    
    breakdown = [
        ("Models", models_size),
        ("LoRAs", loras_size),
        ("VAE", vae_size),
        ("ControlNet", controlnet_size)
    ]
    
    for name, size in breakdown:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if total_size > 0:
                st.progress(size / total_size)
            else:
                st.progress(0)
        with col2:
            st.text(name)
        with col3:
            st.text(format_bytes(size))
    
    # File listing
    st.markdown("### Files")
    
    # List actual files
    all_files = []
    for subdir in ['models', 'loras', 'vae', 'controlnet']:
        subpath = storage_path / subdir
        if subpath.exists():
            for file in subpath.glob('*'):
                if file.is_file():
                    all_files.append({
                        'name': file.name,
                        'type': subdir,
                        'size': format_bytes(file.stat().st_size),
                        'path': str(file)
                    })
    
    if all_files:
        for file in all_files:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.text(file['name'][:40])
            with col2:
                st.text(file['type'])
            with col3:
                st.text(file['size'])
            with col4:
                if st.button("🗑️", key=f"del_{file['name']}"):
                    os.remove(file['path'])
                    st.rerun()
    else:
        st.info("No files in storage yet")
    
    # Cleanup actions
    st.markdown("### Cleanup Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Remove All Models"):
            if st.checkbox("Confirm deletion"):
                shutil.rmtree(storage_path / 'models', ignore_errors=True)
                (storage_path / 'models').mkdir(exist_ok=True)
                st.success("Models cleared!")
                st.rerun()
    
    with col2:
        if st.button("🧹 Clear Everything"):
            if st.checkbox("Confirm full clear"):
                for subdir in ['models', 'loras', 'vae', 'controlnet']:
                    shutil.rmtree(storage_path / subdir, ignore_errors=True)
                    (storage_path / subdir).mkdir(exist_ok=True)
                st.success("Storage cleared!")
                st.rerun()
    
    with col3:
        if st.button("📊 Refresh Stats"):
            st.rerun()

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/8B0000/FFFFFF?text=SD-DarkMaster-Pro", use_column_width=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Home", "⚙️ Setup", "📦 Models", "💾 Downloads", "🚀 Launch", "🧹 Storage"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System info
        st.markdown("### System Info")
        st.text(f"CPU: {psutil.cpu_percent()}%")
        st.text(f"RAM: {psutil.virtual_memory().percent}%")
        if st.session_state.webui_process:
            st.text("WebUI: 🟢 Running")
        else:
            st.text("WebUI: ⚫ Stopped")
    
    # Route to pages
    if page == "🏠 Home":
        home_page()
    elif page == "⚙️ Setup":
        setup_page()
    elif page == "📦 Models":
        models_page()
    elif page == "💾 Downloads":
        downloads_page()
    elif page == "🚀 Launch":
        launch_page()
    elif page == "🧹 Storage":
        storage_page()

if __name__ == "__main__":
    main()