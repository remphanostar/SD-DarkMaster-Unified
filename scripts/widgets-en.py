#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Widgets Dashboard
Enhanced UI with CivitAI integration and model selection
"""

import sys
import os
from pathlib import Path
import streamlit as st
import json
import platform
import subprocess
from datetime import datetime
import psutil
import time

# Add project root to path for imports and handle notebook execution
try:
    # When running as script
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, str(Path(__file__).parent))
except NameError:
    # When executed from notebook - detect platform
    if os.path.exists('/content'):
        project_root = '/content/SD-DarkMaster-Pro'
    elif os.path.exists('/kaggle'):
        project_root = '/kaggle/working/SD-DarkMaster-Pro'
    elif os.path.exists('/workspace'):
        project_root = '/workspace/SD-DarkMaster-Pro'
    else:
        project_root = os.path.join(os.path.expanduser('~'), 'SD-DarkMaster-Pro')
    sys.path.insert(0, os.path.join(project_root, 'scripts'))
        
project_root = Path(project_root)
sys.path.insert(0, str(project_root))

# Suppress warnings after path is set
try:
    from suppress_warnings import suppress_streamlit_warnings
    suppress_streamlit_warnings()
except ImportError:
    pass  # Silently skip if not available

# Import model data
from scripts._models_data import model_list as sd15_models, vae_list as sd15_vae_list, controlnet_list as sd15_controlnet_list, lora_list as sd15_lora_list
from scripts._xl_models_data import model_list as sdxl_models, vae_list as sdxl_vae_list, controlnet_list as sdxl_controlnet_list, lora_list as sdxl_lora_list

# Initialize Streamlit page config
st.set_page_config(
    page_title="SD-DarkMaster-Pro Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the sophisticated dark theme
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.3) 100%);
        border: 2px solid rgba(139, 0, 0, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Title with star */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    /* Info panels */
    .info-panel {
        background: rgba(139, 0, 0, 0.1);
        border: 1px solid rgba(139, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        height: 100%;
    }
    
    /* Console styling */
    .console-output {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 10px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #0f0;
        height: 150px;
        overflow-y: auto;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(139, 0, 0, 0.05);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(139, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(139, 0, 0, 0.5);
    }
    
    /* Model button styling */
    .model-button {
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
        border: 2px solid #333;
        border-radius: 8px;
        padding: 12px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #888;
        text-align: center;
        width: 100%;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .model-button:hover {
        border-color: rgba(139, 0, 0, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(139, 0, 0, 0.3);
    }
    
    .model-button-selected {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.3) 0%, rgba(139, 0, 0, 0.1) 100%);
        border: 2px solid #8B0000;
        color: white !important;
    }
    
    /* Download button styling */
    .download-button {
        background: linear-gradient(135deg, #8B0000 0%, #660000 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .download-button:hover {
        background: linear-gradient(135deg, #A00000 0%, #8B0000 100%);
        transform: scale(1.05);
    }
    
    /* Queue section */
    .queue-section {
        background: rgba(139, 0, 0, 0.05);
        border: 1px solid rgba(139, 0, 0, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8B0000, #FF0000);
    }
    
    /* Selections panel */
    .selections-panel {
        background: rgba(139, 0, 0, 0.1);
        border: 1px solid rgba(139, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        height: 100%;
    }
    
    .selections-panel h4 {
        color: #FFD700;
        margin-bottom: 10px;
    }
    
    .selection-item {
        background: rgba(0, 0, 0, 0.3);
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px 0;
        color: #888;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_models' not in st.session_state:
    st.session_state.selected_models = set()
if 'selected_loras' not in st.session_state:
    st.session_state.selected_loras = set()
if 'selected_vae' not in st.session_state:
    st.session_state.selected_vae = None
if 'selected_controlnet' not in st.session_state:
    st.session_state.selected_controlnet = set()
if 'console_output' not in st.session_state:
    st.session_state.console_output = []
if 'download_queue' not in st.session_state:
    st.session_state.download_queue = []
if 'environment_info' not in st.session_state:
    st.session_state.environment_info = {
        'platform': 'Unknown',
        'gpu': False,
        'hardware': 'Unknown'
    }

# Function to detect environment
def detect_environment():
    """Detect the current running environment"""
    env_info = {
        'platform': 'Local',
        'gpu': False,
        'hardware': platform.machine()
    }
    
    # Check for various cloud platforms
    if os.path.exists('/content'):
        env_info['platform'] = 'Google Colab'
    elif os.path.exists('/kaggle'):
        env_info['platform'] = 'Kaggle'
    elif 'PAPERSPACE' in os.environ:
        env_info['platform'] = 'Paperspace'
    elif 'RUNPOD' in os.environ:
        env_info['platform'] = 'Runpod'
    elif 'VAST' in os.environ:
        env_info['platform'] = 'Vast.ai'
    
    # Check for GPU
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            env_info['gpu'] = True
    except:
        pass
    
    return env_info

# Update environment info
if st.session_state.environment_info['platform'] == 'Unknown':
    st.session_state.environment_info = detect_environment()

# Add to console
def add_console_output(message):
    """Add message to console output"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.console_output.append(f"[{timestamp}] {message}")
    # Keep only last 100 messages
    if len(st.session_state.console_output) > 100:
        st.session_state.console_output = st.session_state.console_output[-100:]

# Toggle model selection
def toggle_model(model_id):
    """Toggle model selection"""
    if model_id in st.session_state.selected_models:
        st.session_state.selected_models.remove(model_id)
        add_console_output(f"Deselected: {model_id}")
    else:
        st.session_state.selected_models.add(model_id)
        add_console_output(f"Selected: {model_id}")

# Toggle LoRA selection
def toggle_lora(lora_id):
    """Toggle LoRA selection"""
    if lora_id in st.session_state.selected_loras:
        st.session_state.selected_loras.remove(lora_id)
        add_console_output(f"Deselected LoRA: {lora_id}")
    else:
        st.session_state.selected_loras.add(lora_id)
        add_console_output(f"Selected LoRA: {lora_id}")

# Toggle ControlNet selection
def toggle_controlnet(cn_id):
    """Toggle ControlNet selection"""
    if cn_id in st.session_state.selected_controlnet:
        st.session_state.selected_controlnet.remove(cn_id)
        add_console_output(f"Deselected ControlNet: {cn_id}")
    else:
        st.session_state.selected_controlnet.add(cn_id)
        add_console_output(f"Selected ControlNet: {cn_id}")

# Main header
st.markdown('<h1 class="main-title">⭐ SD-DarkMaster-Pro Dashboard</h1>', unsafe_allow_html=True)

# Header section with controls
header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col1:
    st.markdown('<div class="info-panel">', unsafe_allow_html=True)
    st.markdown("### Environment Info")
    st.write(f"**Platform:** {st.session_state.environment_info['platform']}")
    st.write(f"**Hardware:** {st.session_state.environment_info['hardware']}")
    st.write(f"**GPU:** {'✅ Yes' if st.session_state.environment_info['gpu'] else '❌ No'}")
    st.markdown('</div>', unsafe_allow_html=True)

with header_col2:
    # WebUI selector and Launch button row
    selector_col, launch_col = st.columns([2, 1])
    
    with selector_col:
        webui_choice = st.selectbox(
            "WebUI Selector",
            ["Automatic1111", "ComfyUI", "Forge", "ReForge"],
            key="webui_selector"
        )
    
    with launch_col:
        if st.button("🚀 Launch WebUI", key="launch_webui", use_container_width=True, type="primary"):
            add_console_output(f"Launching {webui_choice}...")
            st.balloons()
    
    # Console output
    st.markdown("### Output Console")
    console_placeholder = st.empty()
    with console_placeholder.container():
        console_text = "\n".join(st.session_state.console_output[-10:]) if st.session_state.console_output else "System ready..."
        st.code(console_text, language="bash")

with header_col3:
    st.markdown('<div class="selections-panel">', unsafe_allow_html=True)
    st.markdown("### Selections")
    st.markdown("**Pre-installed:** 5")
    st.markdown("**CivitAI:** " + str(len(st.session_state.selected_models)))
    st.markdown("**Queue:** " + str(len(st.session_state.download_queue)))
    st.markdown('</div>', unsafe_allow_html=True)

# Show current selections summary
st.markdown("### 📊 Current Selections")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Models", len(st.session_state.selected_models))
with col2:
    st.metric("LoRAs", len(st.session_state.selected_loras))
with col3:
    st.metric("VAE", "1" if st.session_state.selected_vae else "0")
with col4:
    st.metric("ControlNets", len(st.session_state.selected_controlnet))

# Main content tabs
tab_models, tab_browser, tab_settings = st.tabs(["📦 Models", "🔍 Model Search", "⚙️ Settings"])

with tab_models:
    st.markdown("### Model Selection")
    st.info("Select models, LoRAs, VAEs, and ControlNets to download")
    
    # Model type tabs (using the names you specified)
    model_tabs = st.tabs(["SD1.5", "SDXL", "Pony", "Illustrious", "Misc"])
    
    # SD1.5 Tab
    with model_tabs[0]:
        st.markdown("#### SD 1.5 Models & Components")
        
        # Create expandable sections for better organization
        with st.expander("🎨 SD 1.5 Models", expanded=True):
            st.markdown("Select SD 1.5 checkpoint models")
            
            # Create model grid
            cols = st.columns(3)
            for idx, (model_name, model_info) in enumerate(list(sd15_models.items())[:9]):
                with cols[idx % 3]:
                    model_id = f"sd15_{model_name}"
                    is_selected = model_id in st.session_state.selected_models
                    
                    if st.checkbox(model_name[:30], value=is_selected, key=f"cb_{model_id}"):
                        if not is_selected:
                            st.session_state.selected_models.add(model_id)
                            add_console_output(f"Selected: {model_name}")
                    else:
                        if is_selected:
                            st.session_state.selected_models.remove(model_id)
                            add_console_output(f"Deselected: {model_name}")
        
        with st.expander("🎨 SD 1.5 LoRAs", expanded=False):
            st.markdown("Select SD 1.5 LoRA models")
            
            # Create LoRA grid
            cols = st.columns(2)
            for idx, (lora_name, lora_info) in enumerate(sd15_lora_list.items()):
                with cols[idx % 2]:
                    lora_id = f"sd15_lora_{lora_name}"
                    is_selected = lora_id in st.session_state.selected_loras
                    
                    if st.checkbox(lora_name[:40], value=is_selected, key=f"cb_{lora_id}"):
                        if not is_selected:
                            st.session_state.selected_loras.add(lora_id)
                            add_console_output(f"Selected LoRA: {lora_name}")
                    else:
                        if is_selected:
                            st.session_state.selected_loras.remove(lora_id)
                            add_console_output(f"Deselected LoRA: {lora_name}")
        
        with st.expander("🎭 SD 1.5 VAE", expanded=False):
            st.markdown("Select VAE for SD 1.5 models")
            
            # VAE selection (single choice)
            vae_options = ["None (Use Model VAE)"] + list(sd15_vae_list.keys())
            current_vae = st.session_state.selected_vae if st.session_state.selected_vae in vae_options else "None (Use Model VAE)"
            
            selected_vae = st.radio(
                "Select VAE:",
                vae_options,
                index=vae_options.index(current_vae),
                key="sd15_vae_radio"
            )
            
            if selected_vae != "None (Use Model VAE)":
                st.session_state.selected_vae = selected_vae
                add_console_output(f"Selected VAE: {selected_vae}")
            else:
                st.session_state.selected_vae = None
        
        with st.expander("🎮 SD 1.5 ControlNet", expanded=False):
            st.markdown("Select ControlNet models")
            
            # ControlNet selection
            cols = st.columns(2)
            for idx, (cn_name, cn_info) in enumerate(sd15_controlnet_list.items()):
                with cols[idx % 2]:
                    cn_id = f"sd15_cn_{cn_name}"
                    is_selected = cn_id in st.session_state.selected_controlnet
                    
                    if st.checkbox(cn_name[:40], value=is_selected, key=f"cb_{cn_id}"):
                        if not is_selected:
                            st.session_state.selected_controlnet.add(cn_id)
                            add_console_output(f"Selected ControlNet: {cn_name}")
                    else:
                        if is_selected:
                            st.session_state.selected_controlnet.remove(cn_id)
                            add_console_output(f"Deselected ControlNet: {cn_name}")

    # SDXL Tab
    with model_tabs[1]:
        sdxl_subtabs = st.tabs(["Models", "LoRAs", "VAE", "ControlNet"])
        
        with sdxl_subtabs[0]:  # Models
            st.markdown("### SDXL Models")
            
            # Create model grid
            cols = st.columns(3)
            for idx, (model_name, model_info) in enumerate(list(sdxl_models.items())[:9]):
                with cols[idx % 3]:
                    model_id = f"sdxl_{model_name}"
                    is_selected = model_id in st.session_state.selected_models
                    
                    # Create custom button with HTML
                    button_class = "model-button-selected" if is_selected else "model-button"
                    st.markdown(f"""
                        <div class="{button_class}">
                            {model_name[:30]}...
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Actual button (invisible)
                    if st.button(model_name, key=f"btn_{model_id}", use_container_width=True, help=model_name):
                        toggle_model(model_id)
                        st.rerun()
        
        with sdxl_subtabs[1]:  # LoRAs
            st.markdown("### SDXL LoRAs")
            
            # Create LoRA grid
            cols = st.columns(2)
            for idx, (lora_name, lora_info) in enumerate(sdxl_lora_list.items()):
                with cols[idx % 2]:
                    lora_id = f"sdxl_lora_{lora_name}"
                    is_selected = lora_id in st.session_state.selected_loras
                    
                    # LoRA card with checkbox
                    with st.container():
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.checkbox("", value=is_selected, key=f"lora_{lora_id}"):
                                if not is_selected:
                                    st.session_state.selected_loras.add(lora_id)
                                else:
                                    st.session_state.selected_loras.remove(lora_id)
                                st.rerun()
                        with col2:
                            st.markdown(f"**{lora_name[:40]}...**" if len(lora_name) > 40 else f"**{lora_name}**")
                            if isinstance(lora_info, list) and len(lora_info) > 0:
                                st.caption(f"📦 {lora_info[0].get('name', 'unknown')}")
        
        with sdxl_subtabs[2]:  # VAE
            st.markdown("### SDXL VAEs")
            
            # VAE selector (single select)
            vae_options = ["None (Use Model's VAE)"] + list(sdxl_vae_list.keys())
            selected_vae = st.radio(
                "Select VAE",
                vae_options,
                index=0 if st.session_state.selected_vae is None else (
                    vae_options.index(st.session_state.selected_vae) if st.session_state.selected_vae in vae_options else 0
                ),
                key="sdxl_vae_selector"
            )
            
            if selected_vae != "None (Use Model's VAE)":
                st.session_state.selected_vae = f"sdxl_{selected_vae}"
                vae_info = sdxl_vae_list[selected_vae]
                st.info(f"**Size:** {vae_info.get('name', 'unknown')}")
            else:
                st.session_state.selected_vae = None
        
        with sdxl_subtabs[3]:  # ControlNet
            st.markdown("### SDXL ControlNet Models")
            
            # Create ControlNet grid
            cols = st.columns(2)
            for idx, (cn_name, cn_info) in enumerate(sdxl_controlnet_list.items()):
                with cols[idx % 2]:
                    cn_id = f"sdxl_cn_{cn_name}"
                    is_selected = cn_id in st.session_state.selected_controlnet
                    
                    # ControlNet card with checkbox
                    with st.container():
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.checkbox("", value=is_selected, key=f"cn_{cn_id}"):
                                if not is_selected:
                                    st.session_state.selected_controlnet.add(cn_id)
                                else:
                                    st.session_state.selected_controlnet.remove(cn_id)
                                st.rerun()
                        with col2:
                            st.markdown(f"**{cn_name}**")
                            if isinstance(cn_info, list) and len(cn_info) > 0:
                                st.caption(f"📦 {len(cn_info)} file(s)")
    
    # Pony Tab
    with model_tabs[2]:
        pony_subtabs = st.tabs(["Models", "LoRAs", "VAE"])
        
        with pony_subtabs[0]:
            st.info("Pony models will be displayed here")
        
        with pony_subtabs[1]:
            st.info("Pony LoRAs will be displayed here")
        
        with pony_subtabs[2]:
            st.info("Pony VAEs will be displayed here")
    
    # Illustrious Tab
    with model_tabs[3]:
        illustrious_subtabs = st.tabs(["Models", "LoRAs", "VAE"])
        
        with illustrious_subtabs[0]:
            st.info("Illustrious models will be displayed here")
        
        with illustrious_subtabs[1]:
            st.info("Illustrious LoRAs will be displayed here")
        
        with illustrious_subtabs[2]:
            st.info("Illustrious VAEs will be displayed here")
    
    # Misc Tab
    with model_tabs[4]:
        misc_tabs = st.tabs(["SAM", "ADetailer", "Upscaler", "Reactor", "Other Extensions"])
        
        with misc_tabs[0]:
            st.info("SAM models will be displayed here")
        
        with misc_tabs[1]:
            st.info("ADetailer models will be displayed here")
        
        with misc_tabs[2]:
            st.info("Upscaler models will be displayed here")
        
        with misc_tabs[3]:
            st.info("Reactor models will be displayed here")
        
        with misc_tabs[4]:
            st.info("Other extension models will be displayed here")

with tab_browser:
    st.markdown("### 🔍 CivitAI Model Browser")
    
    # Import CivitAI browser
    try:
        from scripts.civitai_browser import CivitAIBrowser
        browser = CivitAIBrowser()
    except ImportError:
        st.error("CivitAI browser module not found")
        browser = None
    
    # Search bar
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input("Search models...", placeholder="Enter model name or tag", key="civitai_search")
    with search_col2:
        search_button = st.button("Search", use_container_width=True, type="primary")
    
    # Filters
    filter_cols = st.columns(4)
    with filter_cols[0]:
        model_type = st.selectbox("Type", ["All", "Checkpoint", "LoRA", "VAE", "ControlNet"], key="civitai_type")
    with filter_cols[1]:
        base_model = st.selectbox("Base Model", ["All", "SD 1.5", "SDXL", "Pony", "Illustrious"], key="civitai_base")
    with filter_cols[2]:
        sort_by = st.selectbox("Sort By", ["Most Downloaded", "Highest Rated", "Newest"], key="civitai_sort")
    with filter_cols[3]:
        nsfw_filter = st.checkbox("Include NSFW", value=False, key="civitai_nsfw")
    
    # Results area
    if search_button and browser and search_query:
        with st.spinner("Searching CivitAI..."):
            # Map filter values
            types_map = {
                "Checkpoint": ["Checkpoint"],
                "LoRA": ["LORA", "LoCon"],
                "VAE": ["VAE"],
                "ControlNet": ["Controlnet"]
            }
            
            # Perform search
            types = types_map.get(model_type, None) if model_type != "All" else None
            results = browser.search_models(
                query=search_query,
                types=types,
                sort=sort_by,
                nsfw=nsfw_filter,
                limit=12
            )
            
            if results:
                # Display results in grid
                st.markdown(f"Found {len(results)} models")
                
                # Create grid layout
                cols = st.columns(3)
                for idx, model in enumerate(results):
                    with cols[idx % 3]:
                        # Model card
                        with st.container():
                            # Ensure model is a dictionary
                            if isinstance(model, str):
                                st.warning(f"Invalid model data: {model}")
                                continue
                                
                            # Preview image
                            version_info = model.get('version', {})
                            images = version_info.get('images', [])
                            if images and len(images) > 0:
                                st.image(images[0].get('url', ''), use_column_width=True)
                            
                            # Model info
                            st.markdown(f"**{model.get('name', 'Unknown')}**")
                            
                            # Creator is already a string from the API parser
                            creator = model.get('creator', 'Unknown')
                            st.caption(f"by {creator}")
                            
                            # Stats
                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(f"⬇️ {model.get('download_count', 0):,}")
                            with col2:
                                st.caption(f"⭐ {model.get('rating', 0):.1f}")
                            
                            # Download button
                            if st.button("Download", key=f"dl_{model['id']}", use_container_width=True):
                                # Get download info from parsed version
                                version = model.get('version', {})
                                download_url = version.get('download_url', '')
                                filename = version.get('name', f"{model['name']}.safetensors")
                                
                                # Determine storage path based on type
                                model_type = model.get('type', 'Checkpoint')
                                if model_type == 'Checkpoint':
                                    storage_path = 'models/Stable-diffusion'
                                elif model_type in ['LORA', 'LoCon']:
                                    storage_path = 'models/Lora'
                                elif model_type == 'VAE':
                                    storage_path = 'models/VAE'
                                elif model_type == 'Controlnet':
                                    storage_path = 'models/ControlNet'
                                else:
                                    storage_path = 'models/Other'
                                
                                # Add to session state download queue
                                if 'civitai_downloads' not in st.session_state:
                                    st.session_state.civitai_downloads = []
                                
                                if download_url:
                                    st.session_state.civitai_downloads.append({
                                        'name': model['name'],
                                        'url': download_url,
                                        'filename': filename,
                                        'storage_path': storage_path,
                                        'type': model_type
                                    })
                                    
                                    st.success(f"Added {model['name']} to download queue!")
                                    add_console_output(f"Queued download: {model['name']}")
                                else:
                                    st.error("No download URL available for this model")
            else:
                st.info("No models found. Try different search terms.")
    
    # Show download queue
    if 'civitai_downloads' in st.session_state and st.session_state.civitai_downloads:
        st.markdown("### 📥 Download Queue")
        for item in st.session_state.civitai_downloads:
            st.text(f"• {item['name']} → {item['storage_path']}")
        
        if st.button("Clear Queue", key="clear_civitai_queue"):
            st.session_state.civitai_downloads = []
            st.rerun()

with tab_settings:
    st.markdown("### ⚙️ Settings")
    
    settings_tabs = st.tabs(["Paths", "Download", "Advanced", "About"])
    
    with settings_tabs[0]:
        st.markdown("### Storage Paths")
        st.text_input("Models Path", value="/storage/models", key="models_path")
        st.text_input("LoRA Path", value="/storage/loras", key="lora_path")
        st.text_input("VAE Path", value="/storage/vae", key="vae_path")
        st.text_input("ControlNet Path", value="/storage/controlnet", key="controlnet_path")
    
    with settings_tabs[1]:
        st.markdown("### Download Settings")
        st.slider("Parallel Downloads", 1, 16, 4, key="parallel_downloads")
        st.checkbox("Use Aria2c", value=True, key="use_aria2c")
        st.checkbox("Auto-extract ZIP files", value=True, key="auto_extract")
    
    with settings_tabs[2]:
        st.markdown("### Advanced Settings")
        st.checkbox("Enable Debug Mode", value=False, key="debug_mode")
        st.checkbox("Auto-detect Extensions", value=True, key="auto_detect")
        st.number_input("Cache Size (GB)", min_value=1, max_value=100, value=10, key="cache_size")
    
    with settings_tabs[3]:
        st.markdown("### About SD-DarkMaster-Pro")
        st.info("""
        **Version:** 2.0.0  
        **Author:** DarkMaster  
        **License:** MIT  
        
        SD-DarkMaster-Pro is an advanced Stable Diffusion WebUI manager with integrated model management,
        CivitAI browser, and multi-platform support.
        """)

# Download Queue Section (Bottom)
st.markdown("---")
st.markdown("### 📥 Download Queue")

queue_col1, queue_col2, queue_col3 = st.columns([3, 1, 1])

with queue_col1:
    if st.session_state.selected_models:
        # Show progress bar
        progress = st.progress(0, text="Ready to download...")
        
        # Show selected models count by type
        sd15_count = len([m for m in st.session_state.selected_models if m.startswith('sd15_')])
        sdxl_count = len([m for m in st.session_state.selected_models if m.startswith('sdxl_')])
        pony_count = len([m for m in st.session_state.selected_models if m.startswith('pony_')])
        illustrious_count = len([m for m in st.session_state.selected_models if m.startswith('illustrious_')])
        misc_count = len([m for m in st.session_state.selected_models if m.startswith('misc_')])
        
        col_counts = st.columns(5)
        with col_counts[0]:
            st.metric("SD1.5", sd15_count)
        with col_counts[1]:
            st.metric("SDXL", sdxl_count)
        with col_counts[2]:
            st.metric("Pony", pony_count)
        with col_counts[3]:
            st.metric("Illustrious", illustrious_count)
        with col_counts[4]:
            st.metric("Misc", misc_count)
        
        # Sample queue display
        with st.expander("View Queue", expanded=False):
            for model in list(st.session_state.selected_models)[:10]:
                model_type = model.split('_')[0].upper()
                st.markdown(f"- [{model_type}] {model}")
    else:
        st.info("No models selected for download")

with queue_col2:
    # Base Model Lock dropdown
    st.markdown("#### 🔒 Base Model Lock")
    base_model_lock = st.selectbox(
        "Filter models to load",
        ["None (Load All)", "SD 1.5 Only", "SDXL Only", "Pony Only", "Illustrious Only", "Misc Only"],
        key="base_model_lock",
        help="Lock the WebUI to only load models from a specific base architecture. This ensures compatibility and prevents mixing incompatible model types."
    )
    
    # Calculate what will actually be loaded based on the lock
    if base_model_lock != "None (Load All)":
        if "SD 1.5" in base_model_lock:
            filtered_models = [m for m in st.session_state.selected_models if m.startswith('sd15_')]
        elif "SDXL" in base_model_lock:
            filtered_models = [m for m in st.session_state.selected_models if m.startswith('sdxl_')]
        elif "Pony" in base_model_lock:
            filtered_models = [m for m in st.session_state.selected_models if m.startswith('pony_')]
        elif "Illustrious" in base_model_lock:
            filtered_models = [m for m in st.session_state.selected_models if m.startswith('illustrious_')]
        elif "Misc" in base_model_lock:
            filtered_models = [m for m in st.session_state.selected_models if m.startswith('misc_')]
        else:
            filtered_models = list(st.session_state.selected_models)
        
        if len(filtered_models) != len(st.session_state.selected_models):
            st.caption(f"⚠️ Will load {len(filtered_models)} of {len(st.session_state.selected_models)} selected")
    else:
        filtered_models = list(st.session_state.selected_models)

with queue_col3:
    # Determine button text based on lock
    if base_model_lock != "None (Load All)" and filtered_models:
        button_text = f"⬇️ Download {base_model_lock.replace(' Only', '')}"
        models_to_download = len(filtered_models)
    else:
        button_text = "⬇️ Download All"
        models_to_download = len(st.session_state.selected_models)
    
    if st.button(button_text, key="download_all", use_container_width=True, type="primary", 
                 disabled=len(st.session_state.selected_models) == 0):
        if base_model_lock != "None (Load All)":
            add_console_output(f"Starting download of {models_to_download} {base_model_lock.replace(' Only', '')} models...")
            add_console_output(f"Base Model Lock active: {base_model_lock}")
        else:
            add_console_output(f"Starting download of {models_to_download} models (all types)...")
        
        with st.spinner("Downloading..."):
            time.sleep(2)  # Simulate download
        st.success(f"Download started for {models_to_download} models!")

# Add initialization message
if len(st.session_state.console_output) == 0:
    add_console_output("SD-DarkMaster-Pro initialized successfully")
    add_console_output(f"Platform detected: {st.session_state.environment_info['platform']}")
    add_console_output("Ready for model selection...")

# Add Save Configuration Button at the bottom
st.markdown("---")
st.markdown("## 💾 Save Configuration")
st.info("Configure your installation preferences and save all selections for the next steps")

save_col1, save_col2, save_col3 = st.columns([2, 1, 1])

with save_col1:
    st.markdown("### 💾 Save Configuration")
    st.caption("Save your selections for Cell 3 (Downloads) and Cell 4 (Launch)")
    
    # Installation method selection
    install_method = st.radio(
        "Installation Method",
        ["Package Method (Fast)", "Git Clone (Standard)"],
        index=0,
        help="""
        **Package Method**: Uses AnxietySolo's pre-configured packages (5-10 min setup, 5.2GB shared venv)
        **Git Clone**: Standard git installation (30-45 min setup, creates new venv)
        """,
        horizontal=True
    )

with save_col2:
    # WebUI selection for launch config
    webui_type = st.selectbox(
        "WebUI Type",
        ["Forge", "ComfyUI", "A1111", "ReForge", "SD-Next"],
        key="webui_type_selection",
        help="Select which WebUI to launch in Cell 4"
    )
    
    # Show package availability
    if install_method == "Package Method (Fast)":
        package_available = webui_type in ["Forge", "ComfyUI", "A1111", "ReForge"]
        if package_available:
            st.success("✅ Package available")
        else:
            st.warning("⚠️ Package not ready, will use git clone")

with save_col3:
    st.markdown("### ")  # Add spacing
    if st.button("💾 Save All Settings", type="primary", use_container_width=True, help="Click to save all your selections and settings to session.json"):
        # Prepare configuration data
        config = {
            "timestamp": datetime.now().isoformat(),
            "platform": st.session_state.environment_info['platform'],
            "install_method": "package" if "Package" in install_method else "git",
            "selected_models": list(st.session_state.selected_models),
            "selected_loras": list(st.session_state.selected_loras),
            "selected_vae": st.session_state.selected_vae,  # This is already a string or None
            "selected_controlnet": list(st.session_state.selected_controlnet),
            "base_model_lock": base_model_lock,
            "webui_type": webui_type,
            "civitai_downloads": st.session_state.get('civitai_downloads', []),
            "download_settings": {
                "use_aria2c": True,
                "parallel_downloads": 4,
                "resume_downloads": True
            },
            "launch_settings": {
                "port": 7860,
                "share": False,
                "api": True,
                "tunnel": "none",
                "theme": "dark",
                "use_anxiety_launcher": install_method == "Package Method (Fast)"
            }
        }
        
        # Save to session.json
        config_file = Path(project_root) / 'configs' / 'session.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            st.success("✅ Configuration saved successfully!")
            add_console_output(f"Configuration saved to: {config_file}")
            vae_count = 1 if config['selected_vae'] else 0
            add_console_output(f"Models: {len(config['selected_models'])}, LoRAs: {len(config['selected_loras'])}, VAE: {vae_count}, ControlNets: {len(config['selected_controlnet'])}")
            add_console_output(f"WebUI: {webui_type}, Method: {install_method}, Base Lock: {base_model_lock}")
            
            # Show saved config details
            with st.expander("View Saved Configuration", expanded=True):
                st.json(config)
                
        except Exception as e:
            st.error(f"❌ Failed to save configuration: {str(e)}")
            add_console_output(f"Error saving config: {str(e)}")

# Add info about next steps
st.markdown("---")
st.info("""
**Next Steps:**
1. Click **'💾 Save All Settings'** to save your configuration
2. Run **Cell 3** to download selected models using aria2c
3. Run **Cell 4** to launch your selected WebUI (will use your chosen installation method)
4. Run **Cell 5** for storage management and cleanup

**Installation Methods:**
- **Package Method**: 5-10 min setup, pre-configured with 5.2GB shared venv (recommended)
- **Git Clone**: 30-45 min setup, downloads everything fresh
""")

# Display current session status
if os.path.exists(os.path.join(project_root, 'configs', 'session.json')):
    st.sidebar.markdown("### 📄 Current Session")
    try:
        with open(os.path.join(project_root, 'configs', 'session.json'), 'r') as f:
            session_data = json.load(f)
        st.sidebar.success("Session config loaded")
        st.sidebar.caption(f"Last saved: {session_data.get('timestamp', 'Unknown')}")
    except:
        st.sidebar.warning("Session config exists but couldn't be loaded")
else:
    st.sidebar.info("No saved session config yet")