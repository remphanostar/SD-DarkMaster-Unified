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
    page_title="SD-DarkMaster-Pro Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
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

# Import configuration manager
try:
    from scripts.config_manager import config_manager
except ImportError:
    print("⚠️ Config manager not found, using basic config")
    config_manager = None

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

# Enhanced Dashboard Functions
def render_environment_info():
    """Environment Info Panel (Top-Left)"""
    platform = "Colab" if os.path.exists('/content') else "Kaggle" if os.path.exists('/kaggle') else "Vast" if os.path.exists('/workspace') else "Local"
    
    # GPU Detection
    gpu_check = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    gpu_status = "Yes" if gpu_check.returncode == 0 else "No"
    
    # Hardware info
    ram_gb = psutil.virtual_memory().total // (1024**3)
    cpu_count = psutil.cpu_count()
    
    st.markdown("""
    <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
        <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Environment Info</h3>
        <p style='color: #F3F4F6; margin: 5px 0;'><strong>Platform:</strong> {}</p>
        <p style='color: #F3F4F6; margin: 5px 0;'><strong>Hardware:</strong> {} CPU, {} GB RAM</p>
        <p style='color: #F3F4F6; margin: 5px 0;'><strong>GPU:</strong> {}</p>
    </div>
    """.format(platform, cpu_count, ram_gb, gpu_status), unsafe_allow_html=True)

def render_webui_controls():
    """WebUI Selector and Launch Controls (Top-Center/Right)"""
    webui_options = ["Forge", "A1111", "ComfyUI", "SD.Next"]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
            <h3 style='color: #EF4444; margin: 0 0 10px 0;'>WebUI Selector</h3>
        </div>
        """, unsafe_allow_html=True)
        
        selected_webui = st.selectbox("Choose WebUI", webui_options, key="webui_selector")
        
    with col2:
        st.markdown("""
        <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
            <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Launch WebUI</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch WebUI", use_container_width=True, type="primary"):
            st.success(f"Launching {selected_webui}...")
            add_log(f"Starting {selected_webui} WebUI", "info")

def render_output_console():
    """Output Console (Center)"""
    st.markdown("""
    <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
        <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Output Console</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Console content
    console_container = st.container()
    with console_container:
        if st.session_state.logs:
            log_text = "\n".join([f"[{log['time']}] {log['message']}" for log in st.session_state.logs[-10:]])
            st.code(log_text, language="bash", wrap_lines=True)
        else:
            st.code("No activity yet. Select models and launch WebUI to see logs here.", language="bash")

def render_selections_panel():
    """Selections Panel (Right Side)"""
    st.markdown("""
    <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
        <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Selections:</h3>
        <h4 style='color: #F3F4F6; margin: 5px 0;'>Pre-installed models</h4>
        <h4 style='color: #F3F4F6; margin: 5px 0;'>CivitAI Downloaded</h4>
        <h4 style='color: #F3F4F6; margin: 5px 0;'>Models</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Model selections summary
    if st.session_state.selected_models:
        st.write(f"Selected: {len(st.session_state.selected_models)} models")
        for model in st.session_state.selected_models[:5]:  # Show first 5
            st.text(f"• {model}")
        if len(st.session_state.selected_models) > 5:
            st.text(f"... and {len(st.session_state.selected_models) - 5} more")
    else:
        st.info("No models selected yet")

def render_model_selection_tabs():
    """Model Selection Tabs (Center-Bottom)"""
    st.markdown("### Model Selection")
    
    # Main model type tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Models", "🔍 Model Search", "🎯 SDXL", "⚙️ etc"])
    
    with tab1:
        # Sub-tabs for models
        subtab1, subtab2, subtab3 = st.tabs(["SD1.5", "Lora", "Etc"])
        
        with subtab1:
            st.markdown("#### SD 1.5 Models")
            if sd15_models:
                for i, (model_id, model_info) in enumerate(list(sd15_models.items())[:10]):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(f"{model_id[:40]}...")
                    with col2:
                        if st.checkbox("Select", key=f"sd15_{i}"):
                            if f"sd15_{model_id}" not in st.session_state.selected_models:
                                st.session_state.selected_models.append(f"sd15_{model_id}")
    
    with tab2:
        st.markdown("#### CivitAI Search")
        search_term = st.text_input("Search models on CivitAI", placeholder="anime, realistic, etc...")
        if st.button("🔍 Search CivitAI"):
            st.info("CivitAI integration coming soon...")
    
    with tab3:
        st.markdown("#### SDXL Models")
        if sdxl_models:
            for i, (model_id, model_info) in enumerate(list(sdxl_models.items())[:10]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{model_id[:40]}...")
                with col2:
                    if st.checkbox("Select", key=f"sdxl_{i}"):
                        if f"sdxl_{model_id}" not in st.session_state.selected_models:
                            st.session_state.selected_models.append(f"sdxl_{model_id}")
    
    with tab4:
        st.markdown("#### Other Model Types")
        st.info("VAE, ControlNet, and other model types coming soon...")

def render_config_panel():
    """Configuration Panel - Tokens/API Keys (Bottom-Left)"""
    st.markdown("""
    <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
        <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Tokens/API Keys</h3>
        <p style='color: #F3F4F6; margin: 5px 0;'>Launch args</p>
        <p style='color: #F3F4F6; margin: 5px 0;'>Import/export settings</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load current config
    current_config = {}
    if config_manager:
        current_config = config_manager.load_config()
        api_keys = current_config.get('api_keys', {})
        launch_args = current_config.get('launch_args', {})
    
    # Configuration inputs with current values
    hf_token = st.text_input(
        "HuggingFace Token", 
        value=api_keys.get('huggingface_token', '') if config_manager else '',
        placeholder="hf_...", 
        type="password",
        key="hf_token_input"
    )
    
    civitai_key = st.text_input(
        "CivitAI API Key", 
        value=api_keys.get('civitai_api_key', '') if config_manager else '',
        placeholder="Enter API key", 
        type="password",
        key="civitai_key_input"
    )
    
    # WebUI-specific launch args
    webui_type = st.session_state.get('webui_selector', 'Forge')
    current_args = launch_args.get(f'{webui_type.lower()}_args', '--xformers') if config_manager else '--xformers'
    
    launch_args_input = st.text_area(
        f"Launch Arguments ({webui_type})", 
        value=current_args,
        placeholder="--xformers --medvram", 
        height=60,
        key="launch_args_input"
    )
    
    # Save/Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Config", key="save_config_btn"):
            if config_manager:
                # Update config with new values
                config = config_manager.load_config()
                config['api_keys']['huggingface_token'] = hf_token
                config['api_keys']['civitai_api_key'] = civitai_key
                config['launch_args'][f'{webui_type.lower()}_args'] = launch_args_input
                
                if config_manager.save_config(config):
                    st.success("✅ Configuration saved!")
                    add_log("Configuration saved successfully", "success")
                else:
                    st.error("❌ Failed to save configuration")
            else:
                st.warning("Config manager not available")
    
    with col2:
        if st.button("📤 Export Config", key="export_config_btn"):
            if config_manager:
                config_json = config_manager.export_config()
                st.download_button(
                    label="⬇️ Download Config",
                    data=config_json,
                    file_name="sd_darkmaster_config.json",
                    mime="application/json"
                )
                st.success("✅ Config ready for download!")
            else:
                st.warning("Config manager not available")
    
    # Import config
    st.markdown("#### Import Configuration")
    uploaded_file = st.file_uploader("Upload config file", type="json", key="config_upload")
    if uploaded_file and config_manager:
        try:
            config_data = json.load(uploaded_file)
            if config_manager.save_config(config_data):
                st.success("✅ Configuration imported!")
                st.rerun()
            else:
                st.error("❌ Failed to import configuration")
        except Exception as e:
            st.error(f"❌ Invalid config file: {str(e)}")

def render_toggles_panel():
    """Toggles Panel (Bottom-Right)"""
    st.markdown("""
    <div style='background: #1F2937; border: 2px solid #EF4444; border-radius: 10px; padding: 15px; margin: 10px 0;'>
        <h3 style='color: #EF4444; margin: 0 0 10px 0;'>Toggles:</h3>
        <p style='color: #F3F4F6; margin: 5px 0;'>WebUI Updater</p>
        <p style='color: #F3F4F6; margin: 5px 0;'>Extensions updater</p>
        <p style='color: #F3F4F6; margin: 5px 0;'>Verbose Download</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load current settings from config
    current_settings = {}
    if config_manager:
        config = config_manager.load_config()
        current_settings = config.get('ui_settings', {})
    
    # Toggle controls with config integration
    auto_update_webui = st.checkbox(
        "Auto-update WebUI", 
        value=current_settings.get('auto_update_webui', True),
        key="auto_update_webui"
    )
    
    auto_update_extensions = st.checkbox(
        "Auto-update Extensions", 
        value=current_settings.get('auto_update_extensions', True),
        key="auto_update_extensions"
    )
    
    verbose_downloads = st.checkbox(
        "Verbose Download Logs", 
        value=current_settings.get('verbose_downloads', False),
        key="verbose_downloads"
    )
    
    gpu_optimization = st.checkbox(
        "Enable GPU Optimization", 
        value=current_settings.get('gpu_optimization', True),
        key="gpu_optimization"
    )
    
    # Auto-save toggle changes to config
    if config_manager:
        # Update config when toggles change
        config = config_manager.load_config()
        config['ui_settings']['auto_update_webui'] = auto_update_webui
        config['ui_settings']['auto_update_extensions'] = auto_update_extensions  
        config['ui_settings']['verbose_downloads'] = verbose_downloads
        config['ui_settings']['gpu_optimization'] = gpu_optimization
        
        # Save updated config
        config_manager.save_config(config)
    
    # Status indicator
    st.markdown("#### Settings Status")
    col1, col2 = st.columns(2)
    with col1:
        status = "🟢 Saved" if config_manager else "🟡 No Config"
        st.text(f"Config: {status}")
    with col2:
        gpu_status = "🟢 Enabled" if gpu_optimization else "🔴 Disabled"
        st.text(f"GPU: {gpu_status}")

# Enhanced Main Dashboard
def main():
    # Apply Dark Mode Pro CSS
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%);
    }
    .stTitle {
        color: #F3F4F6 !important;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 0 !important;
    }
    .stMarkdown h1 {
        color: #F3F4F6 !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main Title
    st.markdown("# ⭐ SD-DarkMaster-Pro Dashboard")
    
    # Top Row - Environment Info, WebUI Controls
    top_row = st.columns([2, 4, 3])
    
    with top_row[0]:
        render_environment_info()
        
    with top_row[1]:
        render_webui_controls()
        
    with top_row[2]:
        render_selections_panel()
    
    # Middle Row - Output Console (Full Width)
    st.markdown("---")
    render_output_console()
    
    # Model Selection Area
    st.markdown("---")
    render_model_selection_tabs()
    
    # Bottom Row - Configuration and Toggles
    st.markdown("---")
    bottom_row = st.columns([3, 2])
    
    with bottom_row[0]:
        render_config_panel()
        
    with bottom_row[1]:
        render_toggles_panel()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6B7280;'>SD-DarkMaster-Pro Unified Dashboard v2.0</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()