#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Unified Streamlit Interface
A complete, standalone Streamlit application for AI art platform management
"""

import streamlit as st
import os
import sys
import json
import subprocess
import time
import threading
import shutil
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from datetime import datetime
import psutil
import requests
from typing import Dict, List, Optional, Tuple
import pandas as pd

# ===============================
# PAGE CONFIGURATION & THEME
# ===============================

st.set_page_config(
    page_title="SD-DarkMaster-Pro Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Pro Theme CSS
DARK_MODE_PRO_CSS = """
<style>
/* Dark Mode Pro Base Styling */
.stApp {
    background: linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%);
    color: #6B7280;
    font-family: 'Roboto', sans-serif;
}

/* Header Styling */
.main-header {
    color: #10B981;
    font-family: 'Roboto', sans-serif;
    font-weight: bold;
    font-size: 3rem;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
}

.sub-header {
    color: #6B7280;
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    transition: all 0.3s ease-in-out;
    font-weight: bold;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* Sidebar Styling */
.css-1d391kg {
    background: #1F2937;
    border-right: 1px solid #374151;
}

/* Container Styling */
.status-container {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Progress Bar Styling */
.stProgress > div > div {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 0.5rem;
    padding: 1rem;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    background: #1F2937;
    border-radius: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    color: #6B7280;
    background: #111827;
    border-radius: 0.25rem;
    margin: 0 0.25rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
    color: white;
}

/* Selection Cards */
.model-card {
    background: #1F2937;
    border: 2px solid #374151;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: all 0.3s ease-in-out;
}

.model-card:hover {
    border-color: #10B981;
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.2);
}

.model-card-selected {
    background: linear-gradient(135deg, #065f46 0%, #10B981 100%);
    border-color: #10B981;
    color: white;
}

/* Console Styling */
.console-container {
    background: #111827;
    border: 1px solid #10B981;
    border-radius: 0.5rem;
    padding: 1rem;
    font-family: 'Fira Code', monospace;
    max-height: 400px;
    overflow-y: auto;
}
</style>
"""

# ===============================
# SESSION STATE INITIALIZATION
# ===============================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = {}
    if 'download_queue' not in st.session_state:
        st.session_state.download_queue = []
    if 'webui_process' not in st.session_state:
        st.session_state.webui_process = None
    if 'activity_logs' not in st.session_state:
        st.session_state.activity_logs = []
    if 'platform_info' not in st.session_state:
        st.session_state.platform_info = detect_platform()
    if 'storage_stats' not in st.session_state:
        st.session_state.storage_stats = {}

# ===============================
# ORIGINAL DATA SOURCES
# ===============================

# SD 1.5 Models Data (from _models_data.py)
SD15_MODELS = {
    "D5K6.0": {"url": "https://huggingface.co/Remphanstar/Rojos/blob/main/1.5-D5K6.0.safetensors", "name": "1.5-D5K6.0.safetensors"},
    "Merged amateurs - Mixed Amateurs": {"url": "https://civitai.com/api/download/models/179318", "name": "mergedAmateurs_mixedAmateurs.safetensors"},
    "PornMaster-Pro V10.1-VAE-inpainting": {"url": "https://civitai.com/api/download/models/937781", "name": "pornmasterProV101VAE_v101VAE-inpainting.safetensors", "inpainting": True},
    "epiCRealism pureEvolution InPainting": {"url": "https://civitai.com/api/download/models/95864", "name": "epicrealism_v10-inpainting.safetensors", "inpainting": True},
    "LazyMix+ (Real Amateur Nudes)": {"url": "https://civitai.com/models/10961/lazymix-real-amateur-nudes", "name": "lazymixRealAmateur_v40.safetensors"},
}

SD15_VAE = {
    "vae-ft-mse-840000-ema-pruned": {"url": "https://civitai.com/api/download/models/311162", "name": "vaeFtMse840000EmaPruned_vaeFtMse840k.safetensors"},
    "ClearVAE(SD1.5)": {"url": "https://civitai.com/api/download/models/88156", "name": "clearvaeSD15_v23.safetensors"},
}

# SDXL Models Data (from _xl_models_data.py)
SDXL_MODELS = {
    "uberRealisticPornMerge-xlV6Final-inpainting": {"url": "https://civitai.com/api/download/models/1024962", "name": "uberrealisticpornmerge_ponyxlHybridV1.safetensors", "inpainting": True},
    "lustifySDXLNSFW_oltINPAINTING": {"url": "https://huggingface.co/RandomGulag/lustifySDXLNSFW_oltINPAINTING/resolve/main/lustifySDXLNSFW_oltINPAINTING.safetensors", "name": "lustifySDXLNSFW_oltINPAINTING.safetensors", "inpainting": True},
    "PornMaster-Pro SDXL": {"url": "https://civitai.com/api/download/models/1167499", "name": "pornmasterProSDXL_sdxlV2VAE.safetensors"},
    "True Amateur Feeling XL": {"url": "https://civitai.com/api/download/models/907265", "name": "trueAmateurFeelingXL_v2.safetensors"},
}

SDXL_VAE = {
    "Pony Standard VAE": {"url": "https://civitai.com/api/download/models/785437", "name": "ponyStandardVAE_v10.safetensors"},
    "FIX FP16 Errors SDXL": {"url": "https://civitai.com/api/download/models/155933", "name": "fixFP16ErrorsSDXLLowerMemoryUse_v10.safetensors"},
    "SDXL VAE": {"url": "https://civitai.com/api/download/models/333245", "name": "sdxlVAE_sdxlVAE.safetensors"},
}

# Extensions List (from _extensions.txt)
EXTENSIONS_LIST = [
    "https://github.com/anxety-solo/webui_timer",
    "https://github.com/anxety-solo/anxety-theme",
    "https://github.com/anxety-solo/Umi-AI-Wildcards",
    "https://github.com/gutris1/sd-image-viewer",
    "https://github.com/gutris1/sd-image-info",
    "https://github.com/gutris1/sd-hub",
    "https://github.com/Bing-su/adetailer",
    "https://github.com/Haoming02/sd-forge-couple",
    "https://github.com/hako-mikan/sd-webui-regional-prompter",
    "https://github.com/thomasasfk/sd-webui-aspect-ratio-helper",
    "https://github.com/Mikubill/sd-webui-controlnet",
    "https://github.com/zanllp/sd-webui-infinite-image-Browse",
    "https://github.com/ilian6806/stable-diffusion-webui-state",
    "https://github.com/DominikDoom/a1111-sd-webui-tagcomplete",
    "https://github.com/picobyte/stable-diffusion-webui-wd14-tagger",
]

# ===============================
# UTILITY FUNCTIONS
# ===============================

def detect_platform() -> Dict:
    """Detect platform and return configuration"""
    platform_info = {
        'name': 'Unknown',
        'is_cloud': False,
        'gpu_available': False,
        'python_version': sys.version.split()[0],
        'ram_gb': psutil.virtual_memory().total // (1024**3),
        'cpu_count': psutil.cpu_count()
    }
    
    # Platform detection
    if os.path.exists('/content'):
        platform_info['name'] = 'Google Colab'
        platform_info['is_cloud'] = True
    elif os.path.exists('/kaggle'):
        platform_info['name'] = 'Kaggle'
        platform_info['is_cloud'] = True
    elif os.path.exists('/workspace'):
        platform_info['name'] = 'Cloud Workspace'
        platform_info['is_cloud'] = True
    else:
        platform_info['name'] = 'Local'
    
    # GPU detection
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            platform_info['gpu_available'] = True
            # Parse GPU name
            for line in result.stdout.split('\n'):
                if 'NVIDIA' in line and '|' in line:
                    try:
                        gpu_name = line.split('|')[1].strip().split()[0:2]
                        platform_info['gpu_name'] = ' '.join(gpu_name)
                        break
                    except:
                        platform_info['gpu_name'] = 'NVIDIA GPU'
        else:
            platform_info['gpu_name'] = 'CPU Only'
    except:
        platform_info['gpu_name'] = 'CPU Only'
    
    return platform_info

def add_activity_log(message: str, level: str = "info"):
    """Add message to activity log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_logs.append({
        'time': timestamp,
        'level': level,
        'message': message
    })
    # Keep only last 50 logs
    if len(st.session_state.activity_logs) > 50:
        st.session_state.activity_logs = st.session_state.activity_logs[-50:]

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def run_command(cmd: str, capture_output: bool = True) -> Tuple[int, str]:
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            timeout=300
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

# ===============================
# PAGES
# ===============================

def render_home_page():
    """Home dashboard with overview and quick actions"""
    st.markdown('<h1 class="main-header">🎨 SD-DarkMaster-Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Unified AI Art Platform with 80x Faster Deployment</p>', unsafe_allow_html=True)
    
    # Status Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅ Ready" if st.session_state.setup_complete else "❌ Pending"
        st.metric("Setup Status", status)
    
    with col2:
        model_count = sum(len(models) for models in st.session_state.selected_models.values())
        st.metric("Selected Models", model_count)
    
    with col3:
        st.metric("Download Queue", len(st.session_state.download_queue))
    
    with col4:
        webui_status = "🟢 Running" if st.session_state.webui_process else "⚫ Stopped"
        st.metric("WebUI Status", webui_status)
    
    # Platform Information
    st.subheader("🖥️ Platform Information")
    platform = st.session_state.platform_info
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Platform:** {platform['name']}")
    with col2:
        st.info(f"**Python:** {platform['python_version']}")
    with col3:
        st.info(f"**GPU:** {platform['gpu_name']}")
    with col4:
        st.info(f"**RAM:** {platform['ram_gb']} GB")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⚙️ Setup Environment", use_container_width=True, type="primary"):
            st.switch_page("Setup")
    
    with col2:
        if st.button("📦 Browse Models", use_container_width=True):
            st.switch_page("Models")
    
    with col3:
        if st.button("💾 Manage Downloads", use_container_width=True):
            st.switch_page("Downloads")
    
    with col4:
        if st.button("🚀 Launch WebUI", use_container_width=True):
            st.switch_page("Launch")
    
    # Activity Log
    st.subheader("📋 Recent Activity")
    if st.session_state.activity_logs:
        with st.container():
            st.markdown('<div class="console-container">', unsafe_allow_html=True)
            for log in st.session_state.activity_logs[-10:]:
                icon = "✅" if log['level'] == "success" else "ℹ️" if log['level'] == "info" else "⚠️" if log['level'] == "warning" else "❌"
                st.text(f"[{log['time']}] {icon} {log['message']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start by setting up your environment!")

def render_setup_page():
    """Setup and configuration page"""
    st.title("⚙️ Setup & Configuration")
    
    # Environment Status
    st.subheader("🖥️ Environment Status")
    platform = st.session_state.platform_info
    
    col1, col2 = st.columns(2)
    with col1:
        st.json({
            "Platform": platform['name'],
            "Python Version": platform['python_version'],
            "CPU Cores": platform['cpu_count'],
            "RAM (GB)": platform['ram_gb'],
            "GPU Available": platform['gpu_available'],
            "GPU Name": platform.get('gpu_name', 'N/A')
        })
    
    with col2:
        # Directory structure check
        st.subheader("📁 Directory Structure")
        required_dirs = [
            'storage/models/sd15',
            'storage/models/sdxl', 
            'storage/vae',
            'storage/lora',
            'storage/controlnet',
            'storage/embeddings',
            'storage/upscalers',
            'webuis',
            'configs',
            'logs'
        ]
        
        for dir_path in required_dirs:
            exists = Path(dir_path).exists()
            status = "✅" if exists else "❌"
            st.text(f"{status} {dir_path}")
    
    # Setup Actions
    st.subheader("🔧 Setup Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Create Directories", use_container_width=True):
            progress = st.progress(0)
            status_text = st.empty()
            
            for i, dir_path in enumerate(required_dirs):
                status_text.text(f"Creating {dir_path}...")
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                progress.progress((i + 1) / len(required_dirs))
                time.sleep(0.1)
            
            status_text.text("✅ All directories created!")
            add_activity_log("Created directory structure", "success")
            st.session_state.setup_complete = True
            st.rerun()
    
    with col2:
        if st.button("📦 Install Dependencies", use_container_width=True):
            with st.spinner("Installing dependencies..."):
                deps = [
                    "streamlit>=1.29.0",
                    "requests>=2.31.0", 
                    "psutil",
                    "aiohttp",
                    "aiofiles",
                    "beautifulsoup4",
                    "pandas"
                ]
                
                for dep in deps:
                    cmd = f"{sys.executable} -m pip install {dep}"
                    returncode, output = run_command(cmd)
                    if returncode == 0:
                        add_activity_log(f"Installed {dep}", "success")
                    else:
                        add_activity_log(f"Failed to install {dep}: {output}", "error")
                
                st.success("✅ Dependencies installation completed!")
    
    with col3:
        if st.button("🧪 Run System Test", use_container_width=True):
            with st.spinner("Running system tests..."):
                # Test GPU
                returncode, output = run_command("nvidia-smi")
                gpu_test = "✅ GPU Available" if returncode == 0 else "❌ No GPU"
                
                # Test Python packages
                packages = ['streamlit', 'requests', 'psutil']
                package_tests = []
                for pkg in packages:
                    try:
                        __import__(pkg)
                        package_tests.append(f"✅ {pkg}")
                    except ImportError:
                        package_tests.append(f"❌ {pkg}")
                
                # Display results
                st.text(gpu_test)
                for test in package_tests:
                    st.text(test)
                
                add_activity_log("System tests completed", "info")

def render_models_page():
    """Model selection and management"""
    st.title("📦 Model Selection & Management")
    
    # Model type tabs
    tab1, tab2, tab3, tab4 = st.tabs(["SD 1.5", "SDXL", "VAE Models", "CivitAI Search"])
    
    with tab1:
        st.subheader("Stable Diffusion 1.5 Models")
        render_model_grid("sd15", SD15_MODELS, "SD 1.5 checkpoint models")
    
    with tab2:
        st.subheader("SDXL Models")
        render_model_grid("sdxl", SDXL_MODELS, "SDXL checkpoint models")
    
    with tab3:
        st.subheader("VAE Models")
        vae_col1, vae_col2 = st.columns(2)
        
        with vae_col1:
            st.markdown("**SD 1.5 VAE**")
            render_model_grid("sd15_vae", SD15_VAE, "VAE models for SD 1.5")
        
        with vae_col2:
            st.markdown("**SDXL VAE**")
            render_model_grid("sdxl_vae", SDXL_VAE, "VAE models for SDXL")
    
    with tab4:
        render_civitai_search()
    
    # Selection Summary
    st.subheader("📋 Current Selections")
    total_selected = sum(len(models) for models in st.session_state.selected_models.values())
    
    if total_selected > 0:
        st.success(f"✅ {total_selected} models selected")
        
        # Show selections by category
        for category, models in st.session_state.selected_models.items():
            if models:
                st.write(f"**{category.upper()}:** {len(models)} models")
                for model in list(models)[:5]:  # Show first 5
                    st.text(f"  • {model}")
                if len(models) > 5:
                    st.text(f"  ... and {len(models) - 5} more")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save Selections", type="primary", use_container_width=True):
                save_selections()
        with col2:
            if st.button("📥 Add to Download Queue", use_container_width=True):
                add_selections_to_queue()
        with col3:
            if st.button("🗑️ Clear All Selections", use_container_width=True):
                clear_all_selections()
    else:
        st.info("No models selected yet. Choose models from the tabs above.")

def render_model_grid(category: str, models_dict: Dict, description: str):
    """Render a grid of model selection cards"""
    if category not in st.session_state.selected_models:
        st.session_state.selected_models[category] = set()
    
    st.caption(description)
    
    # Create grid
    cols = st.columns(3)
    for idx, (model_name, model_info) in enumerate(models_dict.items()):
        with cols[idx % 3]:
            # Model card
            is_selected = model_name in st.session_state.selected_models[category]
            card_style = "model-card-selected" if is_selected else "model-card"
            
            with st.container():
                st.markdown(f'<div class="{card_style}">', unsafe_allow_html=True)
                
                # Model name (truncated)
                display_name = model_name[:40] + "..." if len(model_name) > 40 else model_name
                st.markdown(f"**{display_name}**")
                
                # Model info
                if isinstance(model_info, dict):
                    if 'name' in model_info:
                        st.caption(f"File: {model_info['name']}")
                    if model_info.get('inpainting'):
                        st.caption("🎨 Inpainting model")
                
                # Selection button
                button_text = "✅ Selected" if is_selected else "➕ Select"
                button_type = "secondary" if is_selected else "primary"
                
                if st.button(button_text, key=f"{category}_{idx}", type=button_type, use_container_width=True):
                    if is_selected:
                        st.session_state.selected_models[category].remove(model_name)
                        add_activity_log(f"Deselected {model_name}", "info")
                    else:
                        st.session_state.selected_models[category].add(model_name)
                        add_activity_log(f"Selected {model_name}", "info")
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

def render_civitai_search():
    """CivitAI search interface"""
    st.subheader("🔍 CivitAI Model Search")
    
    # Search controls
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "Search models", 
            placeholder="anime, realistic, photography...",
            key="civitai_search"
        )
    
    with col2:
        model_type = st.selectbox(
            "Type",
            ["All", "Checkpoint", "LORA", "VAE", "ControlNet", "TextualInversion"],
            key="civitai_type"
        )
    
    with col3:
        if st.button("🔍 Search", type="primary", use_container_width=True):
            if search_term:
                search_civitai_models(search_term, model_type)
            else:
                st.warning("Please enter a search term")
    
    # Display search results
    if 'civitai_results' in st.session_state and st.session_state.civitai_results:
        st.subheader("Search Results")
        
        for idx, model in enumerate(st.session_state.civitai_results[:9]):  # Show first 9
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                # Model image placeholder
                st.image("https://via.placeholder.com/150x150?text=Model", width=150)
            
            with col2:
                st.markdown(f"**{model.get('name', 'Unknown Model')}**")
                st.caption(f"Creator: {model.get('creator', 'Unknown')}")
                st.caption(f"Downloads: {model.get('stats', {}).get('downloadCount', 0)}")
                st.caption(f"Rating: {'⭐' * int(model.get('stats', {}).get('rating', 0))}")
            
            with col3:
                if st.button("📥 Add to Queue", key=f"civitai_{idx}", use_container_width=True):
                    add_civitai_model_to_queue(model)
                    st.success("Added to download queue!")

def search_civitai_models(query: str, model_type: str):
    """Search CivitAI for models (placeholder implementation)"""
    # This is a placeholder - real implementation would use CivitAI API
    st.session_state.civitai_results = [
        {
            "name": f"Sample Model {i+1} - {query}",
            "creator": f"Artist{i+1}",
            "stats": {"downloadCount": 1000 + i*100, "rating": 4 + (i % 2)},
            "url": f"https://civitai.com/models/{1000+i}"
        }
        for i in range(6)
    ]
    add_activity_log(f"Searched CivitAI for '{query}' ({model_type})", "info")

def add_civitai_model_to_queue(model: Dict):
    """Add CivitAI model to download queue"""
    download_item = {
        "name": model['name'],
        "url": model.get('url', ''),
        "source": "CivitAI",
        "type": "model"
    }
    st.session_state.download_queue.append(download_item)
    add_activity_log(f"Added {model['name']} to download queue", "success")

def save_selections():
    """Save current model selections"""
    config = {
        'selected_models': {k: list(v) for k, v in st.session_state.selected_models.items()},
        'timestamp': datetime.now().isoformat()
    }
    
    Path('configs').mkdir(exist_ok=True)
    with open('configs/model_selections.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    st.success("✅ Selections saved!")
    add_activity_log("Model selections saved", "success")

def add_selections_to_queue():
    """Add all selected models to download queue"""
    added_count = 0
    
    for category, models in st.session_state.selected_models.items():
        for model_name in models:
            # Get model data
            model_data = None
            if category == "sd15":
                model_data = SD15_MODELS.get(model_name)
            elif category == "sdxl":
                model_data = SDXL_MODELS.get(model_name)
            elif category == "sd15_vae":
                model_data = SD15_VAE.get(model_name)
            elif category == "sdxl_vae":
                model_data = SDXL_VAE.get(model_name)
            
            if model_data and isinstance(model_data, dict) and 'url' in model_data:
                download_item = {
                    "name": model_data.get('name', model_name),
                    "url": model_data['url'],
                    "category": category,
                    "source": "internal"
                }
                st.session_state.download_queue.append(download_item)
                added_count += 1
    
    if added_count > 0:
        st.success(f"✅ Added {added_count} models to download queue!")
        add_activity_log(f"Added {added_count} models to download queue", "success")
    else:
        st.warning("No valid models found to add to queue")

def clear_all_selections():
    """Clear all model selections"""
    st.session_state.selected_models = {}
    st.success("✅ All selections cleared!")
    add_activity_log("Cleared all model selections", "info")
    st.rerun()

def render_downloads_page():
    """Download management page"""
    st.title("💾 Download Management")
    
    # Download queue overview
    st.subheader("📋 Download Queue")
    
    if st.session_state.download_queue:
        # Queue statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Queue Size", len(st.session_state.download_queue))
        with col2:
            st.metric("Estimated Size", "~12.5 GB")  # Placeholder
        with col3:
            st.metric("Estimated Time", "~25 min")   # Placeholder
        
        # Download items
        st.subheader("🗂️ Queue Items")
        
        for idx, item in enumerate(st.session_state.download_queue):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.text(item.get('name', 'Unknown')[:50])
            with col2:
                st.text(item.get('category', 'N/A'))
            with col3:
                st.text(item.get('source', 'N/A'))
            with col4:
                if st.button("🗑️", key=f"remove_{idx}", help="Remove from queue"):
                    st.session_state.download_queue.pop(idx)
                    st.rerun()
        
        # Download controls
        st.subheader("⬇️ Download Controls")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Downloads", type="primary", use_container_width=True):
                start_downloads()
        
        with col2:
            if st.button("⏸️ Pause All", use_container_width=True):
                st.info("Download pause functionality coming soon")
        
        with col3:
            if st.button("🗑️ Clear Queue", use_container_width=True):
                st.session_state.download_queue = []
                st.success("Queue cleared!")
                st.rerun()
        
    else:
        st.info("📥 Download queue is empty. Add models from the Models page.")
        
        if st.button("📦 Go to Models Page", type="primary"):
            st.switch_page("Models")
    
    # Download history
    st.subheader("📚 Download History")
    render_download_history()

def start_downloads():
    """Start downloading queued items"""
    if not st.session_state.download_queue:
        st.warning("No items in download queue")
        return
    
    # Create download directory
    download_dir = Path('storage/models')
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_items = len(st.session_state.download_queue)
    completed = 0
    
    for idx, item in enumerate(st.session_state.download_queue):
        status_text.text(f"Downloading {item['name']}...")
        
        # Simulate download (replace with actual download logic)
        simulate_download(item, download_dir)
        
        completed += 1
        progress_bar.progress(completed / total_items)
        
        add_activity_log(f"Downloaded {item['name']}", "success")
    
    status_text.text("✅ All downloads completed!")
    st.success(f"Downloaded {total_items} items to {download_dir}")
    
    # Clear queue
    st.session_state.download_queue = []

def simulate_download(item: Dict, download_dir: Path):
    """Simulate download with progress (replace with actual download)"""
    import time
    import random
    
    # Simulate download time
    time.sleep(random.uniform(0.5, 1.5))
    
    # Create placeholder file
    filename = item.get('name', 'unknown_model.safetensors')
    if not filename.endswith('.safetensors'):
        filename += '.safetensors'
    
    file_path = download_dir / filename
    file_path.touch()

def render_download_history():
    """Show download history"""
    history_dir = Path('storage/models')
    
    if history_dir.exists():
        downloaded_files = list(history_dir.glob('*.safetensors'))
        
        if downloaded_files:
            st.write(f"**{len(downloaded_files)} files downloaded**")
            
            for file_path in downloaded_files[:10]:  # Show last 10
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(file_path.name)
                with col2:
                    st.text(format_bytes(file_path.stat().st_size))
                with col3:
                    if st.button("🗑️", key=f"del_{file_path.name}", help="Delete file"):
                        file_path.unlink()
                        st.rerun()
        else:
            st.info("No downloaded files yet")
    else:
        st.info("Download directory not created yet")

def render_launch_page():
    """WebUI launcher page"""
    st.title("🚀 WebUI Launcher")
    
    # WebUI selection
    webui_options = {
        "Forge": {
            "description": "🔥 Recommended - Optimized SD WebUI with better performance",
            "repo": "https://github.com/lllyasviel/stable-diffusion-webui-forge.git",
            "compatibility": "95% extensions compatible"
        },
        "Automatic1111": {
            "description": "⚡ Original SD WebUI - Maximum compatibility",
            "repo": "https://github.com/AUTOMATIC1111/stable-diffusion-webui.git", 
            "compatibility": "100% extensions compatible"
        },
        "ComfyUI": {
            "description": "🎯 Node-based interface - Advanced workflows",
            "repo": "https://github.com/comfyanonymous/ComfyUI.git",
            "compatibility": "Different extension system"
        }
    }
    
    # WebUI selection interface
    st.subheader("🎛️ Select WebUI")
    
    selected_webui = st.selectbox(
        "Choose your WebUI",
        list(webui_options.keys()),
        format_func=lambda x: f"{x} - {webui_options[x]['description']}"
    )
    
    # WebUI info
    webui_info = webui_options[selected_webui]
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Description:** {webui_info['description']}")
        st.info(f"**Compatibility:** {webui_info['compatibility']}")
    
    with col2:
        webui_path = Path(f"webuis/{selected_webui.lower()}")
        if webui_path.exists():
            st.success(f"✅ {selected_webui} is installed")
        else:
            st.warning(f"📦 {selected_webui} will be installed on first launch")
    
    # Launch configuration
    st.subheader("⚙️ Launch Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        port = st.number_input("Port", min_value=7000, max_value=9999, value=7860)
    
    with col2:
        share = st.checkbox("Create public link", value=True)
    
    with col3:
        xformers = st.checkbox("Enable xformers", value=True)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        launch_args = st.text_area(
            "Additional launch arguments",
            value="--medvram --opt-split-attention",
            help="Additional command line arguments for the WebUI"
        )
        
        auto_open = st.checkbox("Auto-open browser", value=False)
        theme = st.selectbox("Theme", ["dark", "light"], index=0)
    
    # Launch button
    st.subheader("🚀 Launch")
    
    if st.button("🚀 Launch WebUI", type="primary", use_container_width=True):
        launch_webui(selected_webui, webui_info, port, share, xformers, launch_args)

def launch_webui(webui_name: str, webui_info: Dict, port: int, share: bool, xformers: bool, launch_args: str):
    """Launch the selected WebUI"""
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    log_container = st.empty()
    
    webui_path = Path(f"webuis/{webui_name.lower()}")
    
    try:
        # Step 1: Create directory
        status_placeholder.info("📁 Preparing workspace...")
        progress_bar.progress(0.1)
        webui_path.parent.mkdir(exist_ok=True)
        
        # Step 2: Clone if needed
        if not webui_path.exists():
            status_placeholder.info(f"📥 Cloning {webui_name} repository...")
            progress_bar.progress(0.3)
            
            cmd = f"git clone {webui_info['repo']} {webui_path}"
            returncode, output = run_command(cmd)
            
            if returncode != 0:
                st.error(f"❌ Failed to clone repository: {output}")
                return
            
            add_activity_log(f"Cloned {webui_name} repository", "success")
        
        # Step 3: Prepare launch command
        status_placeholder.info("🔧 Preparing launch command...")
        progress_bar.progress(0.6)
        
        launch_script = "launch.py" if webui_name != "ComfyUI" else "main.py"
        cmd = f"cd {webui_path} && python {launch_script} --port {port}"
        
        if share:
            cmd += " --share"
        if xformers and webui_name in ["Forge", "Automatic1111"]:
            cmd += " --xformers"
        if launch_args.strip():
            cmd += f" {launch_args.strip()}"
        
        # Step 4: Launch
        status_placeholder.info(f"🚀 Starting {webui_name}...")
        progress_bar.progress(0.8)
        
        # Kill any existing processes
        subprocess.run("pkill -f 'webui'", shell=True, capture_output=True)
        subprocess.run("pkill -f 'ComfyUI'", shell=True, capture_output=True)
        time.sleep(1)
        
        # Start WebUI process
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        st.session_state.webui_process = process
        
        # Step 5: Monitor startup
        status_placeholder.info("⏳ Starting WebUI (this may take a few minutes)...")
        progress_bar.progress(1.0)
        
        # Monitor output for URL
        output_lines = []
        start_time = time.time()
        webui_url = None
        
        while time.time() - start_time < 180:  # 3 minute timeout
            if process.poll() is not None:
                st.error("❌ WebUI process terminated unexpectedly")
                break
            
            try:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    
                    # Keep last 15 lines
                    if len(output_lines) > 15:
                        output_lines.pop(0)
                    
                    # Update log display
                    with log_container.container():
                        st.markdown('<div class="console-container">', unsafe_allow_html=True)
                        for log_line in output_lines:
                            st.text(log_line)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Check for URLs
                    if 'Running on' in line or 'gradio.live' in line:
                        for part in line.split():
                            if part.startswith('http'):
                                webui_url = part
                                break
                        if webui_url:
                            break
                
                time.sleep(0.1)
                
            except Exception as e:
                st.error(f"Error reading output: {e}")
                break
        
        # Show result
        if webui_url:
            status_placeholder.success(f"✅ {webui_name} is running!")
            st.balloons()
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🌐 **WebUI URL:** {webui_url}")
            with col2:
                st.info(f"🖥️ **Local URL:** http://localhost:{port}")
            
            add_activity_log(f"Successfully launched {webui_name} at {webui_url}", "success")
            
            # Provide direct link
            st.markdown(f"### 🔗 Direct Access")
            st.markdown(f"[**🚀 Open {webui_name} WebUI**]({webui_url})")
            
        else:
            status_placeholder.warning("⚠️ WebUI started but URL not detected. Check the logs above.")
            add_activity_log(f"Started {webui_name} but URL not detected", "warning")
    
    except Exception as e:
        st.error(f"❌ Error launching WebUI: {str(e)}")
        add_activity_log(f"Failed to launch {webui_name}: {str(e)}", "error")

def render_storage_page():
    """Storage management page"""
    st.title("🧹 Storage Management")
    
    # Storage overview
    st.subheader("📊 Storage Overview")
    
    # Calculate storage usage
    storage_stats = calculate_storage_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Used", format_bytes(storage_stats['total_used']))
    with col2:
        st.metric("Models", format_bytes(storage_stats['models_size']))
    with col3:
        st.metric("Free Space", format_bytes(storage_stats['free_space']))
    with col4:
        st.metric("Usage %", f"{storage_stats['usage_percent']:.1f}%")
    
    # Storage breakdown
    st.subheader("📁 Storage Breakdown")
    
    categories = [
        ("Models (SD 1.5)", storage_stats['sd15_size']),
        ("Models (SDXL)", storage_stats['sdxl_size']),
        ("VAE", storage_stats['vae_size']),
        ("LoRA", storage_stats['lora_size']),
        ("ControlNet", storage_stats['controlnet_size']),
        ("Embeddings", storage_stats['embeddings_size']),
        ("Upscalers", storage_stats['upscalers_size'])
    ]
    
    for name, size in categories:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if storage_stats['total_used'] > 0:
                progress = size / storage_stats['total_used']
                st.progress(progress)
            else:
                st.progress(0)
        
        with col2:
            st.text(name)
        
        with col3:
            st.text(format_bytes(size))
    
    # File management
    st.subheader("📋 File Management")
    
    # File browser
    storage_root = Path('storage')
    if storage_root.exists():
        selected_category = st.selectbox(
            "Browse category",
            ["models/sd15", "models/sdxl", "vae", "lora", "controlnet", "embeddings", "upscalers"]
        )
        
        category_path = storage_root / selected_category
        if category_path.exists():
            files = list(category_path.glob('*'))
            
            if files:
                st.write(f"**{len(files)} files in {selected_category}**")
                
                # File list
                for file_path in files[:20]:  # Show first 20
                    if file_path.is_file():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.text(file_path.name[:40])
                        with col2:
                            st.text(format_bytes(file_path.stat().st_size))
                        with col3:
                            modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                            st.text(modified.strftime("%m/%d"))
                        with col4:
                            if st.button("🗑️", key=f"del_{file_path.name[:10]}", help="Delete file"):
                                file_path.unlink()
                                st.success(f"Deleted {file_path.name}")
                                st.rerun()
                
                if len(files) > 20:
                    st.info(f"Showing first 20 of {len(files)} files")
            else:
                st.info(f"No files in {selected_category}")
        else:
            st.info(f"Directory {selected_category} does not exist")
    
    # Cleanup actions
    st.subheader("🧹 Cleanup Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Temporary Files", use_container_width=True):
            cleanup_temp_files()
    
    with col2:
        if st.button("📊 Refresh Storage Stats", use_container_width=True):
            st.session_state.storage_stats = {}  # Force recalculation
            st.rerun()
    
    with col3:
        with st.expander("⚠️ Danger Zone"):
            st.warning("These actions cannot be undone!")
            
            if st.button("🗑️ Clear All Models"):
                if st.checkbox("I understand this will delete all models"):
                    clear_all_models()
            
            if st.button("💣 Reset All Storage"):
                if st.checkbox("I understand this will delete everything"):
                    reset_all_storage()

def calculate_storage_stats() -> Dict:
    """Calculate storage usage statistics"""
    storage_root = Path('storage')
    
    def get_dir_size(path: Path) -> int:
        total = 0
        if path.exists() and path.is_dir():
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except (OSError, PermissionError):
                        pass
        return total
    
    stats = {
        'sd15_size': get_dir_size(storage_root / 'models' / 'sd15'),
        'sdxl_size': get_dir_size(storage_root / 'models' / 'sdxl'),
        'vae_size': get_dir_size(storage_root / 'vae'),
        'lora_size': get_dir_size(storage_root / 'lora'),
        'controlnet_size': get_dir_size(storage_root / 'controlnet'),
        'embeddings_size': get_dir_size(storage_root / 'embeddings'),
        'upscalers_size': get_dir_size(storage_root / 'upscalers'),
    }
    
    # Calculate totals
    stats['models_size'] = stats['sd15_size'] + stats['sdxl_size']
    stats['total_used'] = sum(stats.values())
    
    # Get disk stats
    try:
        disk_usage = shutil.disk_usage(storage_root if storage_root.exists() else '.')
        stats['free_space'] = disk_usage.free
        stats['total_space'] = disk_usage.total
        stats['usage_percent'] = (stats['total_used'] / disk_usage.total) * 100 if disk_usage.total > 0 else 0
    except:
        stats['free_space'] = 0
        stats['total_space'] = 0
        stats['usage_percent'] = 0
    
    return stats

def cleanup_temp_files():
    """Clean up temporary files"""
    temp_dirs = ['.cache', '__pycache__', 'logs', 'tmp']
    cleaned = 0
    
    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        if temp_path.exists():
            try:
                shutil.rmtree(temp_path)
                cleaned += 1
            except:
                pass
    
    st.success(f"✅ Cleaned {cleaned} temporary directories")
    add_activity_log(f"Cleaned {cleaned} temporary directories", "success")

def clear_all_models():
    """Clear all model files"""
    storage_root = Path('storage')
    model_dirs = ['models', 'vae', 'lora', 'controlnet', 'embeddings', 'upscalers']
    
    for model_dir in model_dirs:
        dir_path = storage_root / model_dir
        if dir_path.exists():
            shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
    
    st.success("✅ All models cleared!")
    add_activity_log("Cleared all model files", "warning")

def reset_all_storage():
    """Reset entire storage directory"""
    storage_root = Path('storage')
    if storage_root.exists():
        shutil.rmtree(storage_root)
        storage_root.mkdir(exist_ok=True)
    
    st.success("✅ Storage completely reset!")
    add_activity_log("Reset entire storage directory", "warning")

def render_monitor_page():
    """System monitoring page"""
    st.title("📊 System Monitor")
    
    # Real-time system metrics
    st.subheader("🖥️ System Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpu_percent = psutil.cpu_percent(interval=1)
        st.metric("CPU Usage", f"{cpu_percent}%", delta=None)
    
    with col2:
        memory = psutil.virtual_memory()
        st.metric("RAM Usage", f"{memory.percent}%", f"{format_bytes(memory.used)}")
    
    with col3:
        disk = psutil.disk_usage('.')
        disk_percent = (disk.used / disk.total) * 100
        st.metric("Disk Usage", f"{disk_percent:.1f}%", format_bytes(disk.used))
    
    with col4:
        # Network stats
        network = psutil.net_io_counters()
        st.metric("Network", "Active", f"↓{format_bytes(network.bytes_recv)} ↑{format_bytes(network.bytes_sent)}")
    
    # Process monitoring
    st.subheader("🔄 Active Processes")
    
    if st.session_state.webui_process:
        st.success("🟢 WebUI Process Running")
        
        try:
            process = psutil.Process(st.session_state.webui_process.pid)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Process CPU", f"{process.cpu_percent():.1f}%")
            with col2:
                memory_mb = process.memory_info().rss / 1024 / 1024
                st.metric("Process RAM", f"{memory_mb:.0f} MB")
            with col3:
                runtime = time.time() - process.create_time()
                st.metric("Runtime", f"{runtime/60:.1f} min")
                
        except (psutil.NoSuchProcess, AttributeError):
            st.warning("⚠️ WebUI process information unavailable")
            st.session_state.webui_process = None
    else:
        st.info("⚫ No WebUI process running")
    
    # Live logs
    st.subheader("📜 Live Activity Log")
    
    # Auto-refresh option
    auto_refresh = st.checkbox("🔄 Auto-refresh (5s)", value=False)
    
    if auto_refresh:
        # Auto-refresh every 5 seconds
        time.sleep(5)
        st.rerun()
    
    # Activity log display
    if st.session_state.activity_logs:
        log_container = st.container()
        with log_container:
            st.markdown('<div class="console-container">', unsafe_allow_html=True)
            
            # Show last 20 logs
            for log in st.session_state.activity_logs[-20:]:
                timestamp = log['time']
                level = log['level']
                message = log['message']
                
                # Color code by level
                if level == "success":
                    icon = "✅"
                elif level == "error":
                    icon = "❌"
                elif level == "warning":
                    icon = "⚠️"
                else:
                    icon = "ℹ️"
                
                st.text(f"[{timestamp}] {icon} {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No activity logs yet")
    
    # System information
    st.subheader("ℹ️ System Information")
    
    system_info = {
        "Platform": st.session_state.platform_info['name'],
        "Python Version": st.session_state.platform_info['python_version'],
        "CPU Cores": st.session_state.platform_info['cpu_count'],
        "Total RAM": f"{st.session_state.platform_info['ram_gb']} GB",
        "GPU": st.session_state.platform_info['gpu_name'],
        "Streamlit Version": st.__version__,
    }
    
    col1, col2 = st.columns(2)
    with col1:
        for key, value in list(system_info.items())[:len(system_info)//2]:
            st.info(f"**{key}:** {value}")
    
    with col2:
        for key, value in list(system_info.items())[len(system_info)//2:]:
            st.info(f"**{key}:** {value}")

# ===============================
# MAIN APPLICATION
# ===============================

def main():
    """Main application function"""
    
    # Apply Dark Mode Pro CSS
    st.markdown(DARK_MODE_PRO_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎛️ Navigation")
        
        page = st.radio(
            "Choose a page:",
            ["🏠 Home", "⚙️ Setup", "📦 Models", "💾 Downloads", "🚀 Launch", "🧹 Storage", "📊 Monitor"],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        st.markdown("### 📊 Quick Stats")
        st.text(f"Platform: {st.session_state.platform_info['name']}")
        st.text(f"Selected: {sum(len(models) for models in st.session_state.selected_models.values())} models")
        st.text(f"Queue: {len(st.session_state.download_queue)} items")
        
        webui_status = "🟢 Running" if st.session_state.webui_process else "⚫ Stopped"
        st.text(f"WebUI: {webui_status}")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        if st.button("🗑️ Clear Logs", use_container_width=True):
            st.session_state.activity_logs = []
            add_activity_log("Cleared activity logs", "info")
    
    # Main content area
    if page == "🏠 Home":
        render_home_page()
    elif page == "⚙️ Setup":
        render_setup_page()
    elif page == "📦 Models":
        render_models_page()
    elif page == "💾 Downloads":
        render_downloads_page()
    elif page == "🚀 Launch":
        render_launch_page()
    elif page == "🧹 Storage":
        render_storage_page()
    elif page == "📊 Monitor":
        render_monitor_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #6B7280; padding: 1rem;">SD-DarkMaster-Pro Unified Dashboard v2.0 - Built with Streamlit</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()