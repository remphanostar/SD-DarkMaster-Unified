#!/usr/bin/env python3
"""
🧪 CivitAI Testing Suite Launcher
A comprehensive GUI for managing and launching CivitAI integration tests
"""

import streamlit as st
import os
import sys
import json
import subprocess
import time
import threading
import shutil
import requests
from pathlib import Path
from datetime import datetime
import psutil
from typing import Dict, List, Optional, Tuple
import pandas as pd

# ===============================
# PAGE CONFIGURATION & THEME
# ===============================

st.set_page_config(
    page_title="🧪 CivitAI Testing Suite",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Pro Theme CSS (from app.py)
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

/* Test Card Styling */
.test-card {
    background: #1F2937;
    border: 2px solid #374151;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.3s ease-in-out;
}

.test-card:hover {
    border-color: #10B981;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.test-card-success {
    border-color: #10B981;
    background: linear-gradient(135deg, #065f46 0%, #1F2937 100%);
}

.test-card-warning {
    border-color: #F59E0B;
    background: linear-gradient(135deg, #92400e 0%, #1F2937 100%);
}

.test-card-error {
    border-color: #EF4444;
    background: linear-gradient(135deg, #991b1b 0%, #1F2937 100%);
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
    color: #E5E7EB;
}

/* Status Indicators */
.status-running {
    color: #10B981;
    font-weight: bold;
}

.status-stopped {
    color: #6B7280;
}

.status-error {
    color: #EF4444;
    font-weight: bold;
}

/* Progress Bars */
.stProgress > div > div {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

/* Metrics */
div[data-testid="metric-container"] {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 0.5rem;
    padding: 1rem;
}

/* Tabs */
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
</style>
"""

# ===============================
# SESSION STATE INITIALIZATION
# ===============================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'test_processes' not in st.session_state:
        st.session_state.test_processes = {}
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    if 'activity_logs' not in st.session_state:
        st.session_state.activity_logs = []
    if 'environment_status' not in st.session_state:
        st.session_state.environment_status = None
    if 'last_validation' not in st.session_state:
        st.session_state.last_validation = None

# ===============================
# TEST CONFIGURATION
# ===============================

TEST_SCRIPTS = {
    "validation": {
        "name": "🔍 Environment Validation",
        "file": "validate_setup.py",
        "description": "Validates Python installation, required packages, CivitAI API access, and file permissions",
        "type": "validation",
        "estimated_time": "30 seconds",
        "requirements": ["Python 3.7+", "Internet connection"],
        "outputs": ["Environment status report", "Package verification", "API connectivity test"],
        "command": "python validate_setup.py"
    },
    "manual_test": {
        "name": "⚙️ Manual Functionality Test", 
        "file": "civitai_manual_test.py",
        "description": "Command-line test of core CivitAI functionality: search, model details, and file download",
        "type": "functionality",
        "estimated_time": "2-5 minutes",
        "requirements": ["Valid environment", "~100MB free space"],
        "outputs": ["API response data", "Download verification", "File organization test"],
        "command": "python civitai_manual_test.py"
    },
    "streamlit_ui": {
        "name": "🎨 Streamlit UI Test",
        "file": "civitai_test_basic.py", 
        "description": "Interactive Streamlit interface for CivitAI search, browse, and download functionality",
        "type": "ui",
        "estimated_time": "Interactive",
        "requirements": ["Streamlit installed", "Port 8501 available"],
        "outputs": ["Web interface at localhost:8501", "Interactive model browser", "Download interface"],
        "command": "streamlit run civitai_test_basic.py --server.port 8501"
    },
    "batch_windows": {
        "name": "🖥️ Windows Batch Runner",
        "file": "run_civitai_tests.bat",
        "description": "Automated Windows batch script that runs all tests in sequence",
        "type": "automation",
        "estimated_time": "5-10 minutes", 
        "requirements": ["Windows OS", "Command Prompt"],
        "outputs": ["Complete test suite results", "Environment setup", "Functionality verification"],
        "command": "run_civitai_tests.bat"
    },
    "powershell": {
        "name": "💻 PowerShell Runner",
        "file": "run_civitai_tests.ps1", 
        "description": "Enhanced PowerShell script with better error handling and progress reporting",
        "type": "automation",
        "estimated_time": "5-10 minutes",
        "requirements": ["Windows PowerShell", "Execution policy enabled"],
        "outputs": ["Detailed progress reports", "Error handling", "Success verification"],
        "command": "powershell -ExecutionPolicy Bypass -File run_civitai_tests.ps1"
    },
    "quick_install": {
        "name": "🚀 Quick Install & Test",
        "file": "INSTALL_AND_TEST.bat",
        "description": "One-click installer that sets up everything and runs the complete test suite",
        "type": "installer",
        "estimated_time": "3-8 minutes",
        "requirements": ["Windows OS", "Internet connection"],
        "outputs": ["Complete environment setup", "Package installation", "Full test execution"],
        "command": "INSTALL_AND_TEST.bat"
    }
}

# ===============================
# UTILITY FUNCTIONS
# ===============================

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

def run_command(cmd: str, capture_output: bool = True, timeout: int = 300) -> Tuple[int, str]:
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

def check_file_exists(filename: str) -> bool:
    """Check if test file exists"""
    return Path(filename).exists()

def get_file_size(filename: str) -> str:
    """Get formatted file size"""
    try:
        size = Path(filename).stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def check_python_version() -> Tuple[bool, str]:
    """Check Python version"""
    try:
        version = sys.version.split()[0]
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 7:
            return True, version
        else:
            return False, version
    except:
        return False, "Unknown"

def check_package_installed(package: str) -> bool:
    """Check if Python package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def validate_environment() -> Dict:
    """Validate complete environment"""
    results = {
        'python': check_python_version(),
        'packages': {},
        'files': {},
        'api_access': False,
        'overall': False
    }
    
    # Check required packages
    required_packages = ['requests', 'streamlit', 'pandas', 'pathlib']
    for package in required_packages:
        results['packages'][package] = check_package_installed(package)
    
    # Check test files
    for script_id, script_info in TEST_SCRIPTS.items():
        filename = script_info['file']
        results['files'][filename] = check_file_exists(filename)
    
    # Check CivitAI API access
    try:
        response = requests.get('https://civitai.com/api/v1/models', timeout=10)
        results['api_access'] = response.status_code == 200
    except:
        results['api_access'] = False
    
    # Overall status
    results['overall'] = (
        results['python'][0] and
        all(results['packages'].values()) and
        any(results['files'].values()) and
        results['api_access']
    )
    
    return results

# ===============================
# PAGE RENDERERS
# ===============================

def render_overview_page():
    """Main overview and dashboard"""
    st.markdown('<h1 class="main-header">🧪 CivitAI Testing Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comprehensive Testing Environment for CivitAI Integration</p>', unsafe_allow_html=True)
    
    # Quick status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        running_tests = len([p for p in st.session_state.test_processes.values() if p and p.poll() is None])
        st.metric("Running Tests", running_tests)
    
    with col2:
        completed_tests = len(st.session_state.test_results)
        st.metric("Completed Tests", completed_tests)
    
    with col3:
        if st.session_state.environment_status:
            env_status = "✅ Ready" if st.session_state.environment_status['overall'] else "❌ Issues"
        else:
            env_status = "❓ Unknown"
        st.metric("Environment", env_status)
    
    with col4:
        total_scripts = len(TEST_SCRIPTS)
        available_scripts = sum(1 for script in TEST_SCRIPTS.values() if check_file_exists(script['file']))
        st.metric("Available Scripts", f"{available_scripts}/{total_scripts}")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Validate Environment", type="primary", use_container_width=True):
            with st.spinner("Validating environment..."):
                st.session_state.environment_status = validate_environment()
                st.session_state.last_validation = datetime.now()
                add_activity_log("Environment validation completed", "info")
            st.rerun()
    
    with col2:
        if st.button("🎨 Launch UI Test", use_container_width=True):
            if check_file_exists("civitai_test_basic.py"):
                launch_test("streamlit_ui")
            else:
                st.error("civitai_test_basic.py not found!")
    
    with col3:
        if st.button("⚙️ Run Manual Test", use_container_width=True):
            if check_file_exists("civitai_manual_test.py"):
                launch_test("manual_test")
            else:
                st.error("civitai_manual_test.py not found!")
    
    with col4:
        if st.button("🚀 Quick Install", use_container_width=True):
            if check_file_exists("INSTALL_AND_TEST.bat"):
                launch_test("quick_install")
            else:
                st.error("INSTALL_AND_TEST.bat not found!")
    
    # Environment Status Display
    if st.session_state.environment_status:
        st.subheader("🖥️ Environment Status")
        env = st.session_state.environment_status
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🐍 Python Environment**")
            python_ok, python_version = env['python']
            python_status = "✅" if python_ok else "❌"
            st.text(f"{python_status} Python {python_version}")
            
            st.markdown("**📦 Required Packages**")
            for package, installed in env['packages'].items():
                status = "✅" if installed else "❌"
                st.text(f"{status} {package}")
        
        with col2:
            st.markdown("**📄 Test Files**")
            for filename, exists in env['files'].items():
                status = "✅" if exists else "❌"
                st.text(f"{status} {filename}")
            
            st.markdown("**🌐 External Access**")
            api_status = "✅" if env['api_access'] else "❌"
            st.text(f"{api_status} CivitAI API")
        
        if st.session_state.last_validation:
            st.caption(f"Last validated: {st.session_state.last_validation.strftime('%H:%M:%S')}")
    
    # Recent Activity
    st.subheader("📋 Recent Activity")
    if st.session_state.activity_logs:
        with st.container():
            st.markdown('<div class="console-container">', unsafe_allow_html=True)
            for log in st.session_state.activity_logs[-8:]:
                icon = "✅" if log['level'] == "success" else "ℹ️" if log['level'] == "info" else "⚠️" if log['level'] == "warning" else "❌"
                st.text(f"[{log['time']}] {icon} {log['message']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start by validating your environment!")

def render_test_scripts_page():
    """Individual test script management"""
    st.title("📜 Test Scripts Manager")
    
    st.markdown("Manage and launch individual test scripts with detailed information and controls.")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox(
            "Filter by type:",
            ["All", "validation", "functionality", "ui", "automation", "installer"]
        )
    
    with col2:
        show_only_available = st.checkbox("Show only available scripts", value=False)
    
    with col3:
        sort_by = st.selectbox("Sort by:", ["name", "type", "estimated_time"])
    
    # Script cards
    for script_id, script_info in TEST_SCRIPTS.items():
        # Apply filters
        if filter_type != "All" and script_info['type'] != filter_type:
            continue
        
        if show_only_available and not check_file_exists(script_info['file']):
            continue
        
        # Determine card style based on status
        file_exists = check_file_exists(script_info['file'])
        is_running = script_id in st.session_state.test_processes and st.session_state.test_processes[script_id] and st.session_state.test_processes[script_id].poll() is None
        has_results = script_id in st.session_state.test_results
        
        if not file_exists:
            card_class = "test-card-error"
        elif is_running:
            card_class = "test-card-warning" 
        elif has_results:
            card_class = "test-card-success"
        else:
            card_class = "test-card"
        
        # Render script card
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {script_info['name']}")
            st.markdown(script_info['description'])
            
            # Script details
            st.markdown(f"**📄 File:** `{script_info['file']}`")
            st.markdown(f"**⏱️ Estimated Time:** {script_info['estimated_time']}")
            st.markdown(f"**🏷️ Type:** {script_info['type']}")
            
            # Requirements
            with st.expander("📋 Requirements & Details"):
                st.markdown("**Requirements:**")
                for req in script_info['requirements']:
                    st.markdown(f"• {req}")
                
                st.markdown("**Expected Outputs:**")
                for output in script_info['outputs']:
                    st.markdown(f"• {output}")
                
                st.markdown(f"**Command:** `{script_info['command']}`")
        
        with col2:
            # File info
            if file_exists:
                st.success("✅ Available")
                file_size = get_file_size(script_info['file'])
                st.caption(f"Size: {file_size}")
            else:
                st.error("❌ Missing")
            
            # Process status
            if is_running:
                st.warning("🟡 Running")
            elif has_results:
                result = st.session_state.test_results[script_id]
                if result.get('success', False):
                    st.success("🟢 Success")
                else:
                    st.error("🔴 Failed")
            else:
                st.info("⚫ Ready")
        
        with col3:
            # Action buttons
            if is_running:
                if st.button(f"⏹️ Stop", key=f"stop_{script_id}", use_container_width=True):
                    stop_test(script_id)
                
                if st.button(f"📊 Monitor", key=f"monitor_{script_id}", use_container_width=True):
                    st.session_state.monitoring_test = script_id
            
            elif file_exists:
                if st.button(f"🚀 Launch", key=f"launch_{script_id}", type="primary", use_container_width=True):
                    launch_test(script_id)
                
                if st.button(f"📝 View File", key=f"view_{script_id}", use_container_width=True):
                    st.session_state.viewing_file = script_info['file']
            
            else:
                st.button("❌ Unavailable", disabled=True, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def render_test_results_page():
    """Test results and monitoring"""
    st.title("📊 Test Results & Monitoring")
    
    # Active processes monitoring
    st.subheader("🔄 Active Processes")
    
    active_processes = [(script_id, process) for script_id, process in st.session_state.test_processes.items() 
                       if process and process.poll() is None]
    
    if active_processes:
        for script_id, process in active_processes:
            script_info = TEST_SCRIPTS[script_id]
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{script_info['name']}**")
                st.caption(f"PID: {process.pid}")
            
            with col2:
                try:
                    ps_process = psutil.Process(process.pid)
                    cpu_percent = ps_process.cpu_percent()
                    st.metric("CPU", f"{cpu_percent:.1f}%")
                except:
                    st.text("CPU: N/A")
            
            with col3:
                try:
                    ps_process = psutil.Process(process.pid)
                    memory_mb = ps_process.memory_info().rss / 1024 / 1024
                    st.metric("RAM", f"{memory_mb:.0f}MB")
                except:
                    st.text("RAM: N/A")
            
            with col4:
                if st.button(f"⏹️ Stop", key=f"stop_monitor_{script_id}"):
                    stop_test(script_id)
                    st.rerun()
    else:
        st.info("No active test processes")
    
    # Test results history
    st.subheader("📋 Test Results History")
    
    if st.session_state.test_results:
        results_data = []
        for script_id, result in st.session_state.test_results.items():
            script_info = TEST_SCRIPTS.get(script_id, {})
            results_data.append({
                'Test': script_info.get('name', script_id),
                'Type': script_info.get('type', 'unknown'),
                'Status': '✅ Success' if result.get('success', False) else '❌ Failed',
                'Duration': result.get('duration', 'N/A'),
                'Timestamp': result.get('timestamp', 'N/A'),
                'Exit Code': result.get('exit_code', 'N/A')
            })
        
        df = pd.DataFrame(results_data)
        st.dataframe(df, use_container_width=True)
        
        # Detailed results
        st.subheader("🔍 Detailed Results")
        
        selected_test = st.selectbox(
            "Select test for detailed view:",
            list(st.session_state.test_results.keys()),
            format_func=lambda x: TEST_SCRIPTS.get(x, {}).get('name', x)
        )
        
        if selected_test:
            result = st.session_state.test_results[selected_test]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.json({
                    'success': result.get('success', False),
                    'exit_code': result.get('exit_code', 'N/A'),
                    'duration': result.get('duration', 'N/A'),
                    'timestamp': result.get('timestamp', 'N/A')
                })
            
            with col2:
                if 'output' in result:
                    st.markdown("**Output:**")
                    st.markdown('<div class="console-container">', unsafe_allow_html=True)
                    st.text(result['output'][:1000] + ('...' if len(result['output']) > 1000 else ''))
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No test results yet. Run some tests to see results here!")
    
    # Clear results
    if st.session_state.test_results:
        if st.button("🗑️ Clear All Results", type="secondary"):
            st.session_state.test_results = {}
            add_activity_log("Cleared all test results", "info")
            st.rerun()

def render_file_browser_page():
    """File browser and editor"""
    st.title("📁 File Browser & Manager")
    
    # File listing
    st.subheader("📄 Available Files")
    
    files_info = []
    for script_id, script_info in TEST_SCRIPTS.items():
        filename = script_info['file']
        if check_file_exists(filename):
            file_path = Path(filename)
            files_info.append({
                'Filename': filename,
                'Type': script_info['type'],
                'Description': script_info['description'][:60] + '...',
                'Size': get_file_size(filename),
                'Modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
    
    # Add other files
    other_files = [
        'civitai_requirements.txt',
        'README.md',
        'WINDOWS_QUICK_START.md',
        'CIVITAI_TEST_README.md',
        'DOWNLOAD_INSTRUCTIONS.txt'
    ]
    
    for filename in other_files:
        if check_file_exists(filename):
            file_path = Path(filename)
            files_info.append({
                'Filename': filename,
                'Type': 'documentation' if filename.endswith('.md') or filename.endswith('.txt') else 'config',
                'Description': 'Documentation or configuration file',
                'Size': get_file_size(filename),
                'Modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
    
    if files_info:
        df = pd.DataFrame(files_info)
        st.dataframe(df, use_container_width=True)
        
        # File viewer
        st.subheader("👁️ File Viewer")
        
        selected_file = st.selectbox(
            "Select file to view:",
            [info['Filename'] for info in files_info]
        )
        
        if selected_file and st.button("📖 View File Content"):
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine language for syntax highlighting
                if selected_file.endswith('.py'):
                    st.code(content, language='python')
                elif selected_file.endswith('.bat'):
                    st.code(content, language='batch')
                elif selected_file.endswith('.ps1'):
                    st.code(content, language='powershell')
                elif selected_file.endswith('.md'):
                    st.markdown(content)
                else:
                    st.text(content)
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    else:
        st.warning("No files found in current directory")
    
    # File operations
    st.subheader("🔧 File Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh File List", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 Show Disk Usage", use_container_width=True):
            show_disk_usage()
    
    with col3:
        if st.button("🧹 Clean Temp Files", use_container_width=True):
            clean_temp_files()

def show_disk_usage():
    """Show disk usage information"""
    try:
        total, used, free = shutil.disk_usage('.')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Space", f"{total // (1024**3)} GB")
        with col2:
            st.metric("Used Space", f"{used // (1024**3)} GB")
        with col3:
            st.metric("Free Space", f"{free // (1024**3)} GB")
        
        usage_percent = (used / total) * 100
        st.progress(usage_percent / 100)
        st.caption(f"Disk usage: {usage_percent:.1f}%")
        
    except Exception as e:
        st.error(f"Error getting disk usage: {e}")

def clean_temp_files():
    """Clean temporary files"""
    temp_patterns = ['*.tmp', '*.log', '__pycache__', '*.pyc']
    cleaned = 0
    
    try:
        for pattern in temp_patterns:
            for file_path in Path('.').glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        cleaned += 1
                except:
                    pass
        
        st.success(f"✅ Cleaned {cleaned} temporary files")
        add_activity_log(f"Cleaned {cleaned} temporary files", "success")
        
    except Exception as e:
        st.error(f"Error cleaning files: {e}")

# ===============================
# TEST MANAGEMENT FUNCTIONS
# ===============================

def launch_test(script_id: str):
    """Launch a test script"""
    script_info = TEST_SCRIPTS[script_id]
    
    if not check_file_exists(script_info['file']):
        st.error(f"File {script_info['file']} not found!")
        return
    
    try:
        # Kill any existing process for this script
        if script_id in st.session_state.test_processes and st.session_state.test_processes[script_id]:
            try:
                st.session_state.test_processes[script_id].terminate()
            except:
                pass
        
        # Launch new process
        cmd = script_info['command']
        
        if script_info['type'] == 'ui':  # Streamlit UI
            process = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            st.session_state.test_processes[script_id] = process
            add_activity_log(f"Launched {script_info['name']} (PID: {process.pid})", "success")
            
            # For UI tests, show the URL
            time.sleep(2)  # Give it time to start
            st.success(f"✅ {script_info['name']} launched!")
            st.info("🌐 **Access URL:** http://localhost:8501")
            st.markdown("[🚀 **Open in Browser**](http://localhost:8501)")
            
        else:  # Other types
            start_time = time.time()
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )
            end_time = time.time()
            
            # Store results
            st.session_state.test_results[script_id] = {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'output': result.stdout + result.stderr,
                'duration': f"{end_time - start_time:.1f}s",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if result.returncode == 0:
                st.success(f"✅ {script_info['name']} completed successfully!")
                add_activity_log(f"{script_info['name']} completed successfully", "success")
            else:
                st.error(f"❌ {script_info['name']} failed with exit code {result.returncode}")
                add_activity_log(f"{script_info['name']} failed", "error")
                
                # Show error output
                with st.expander("🔍 Error Details"):
                    st.text(result.stdout + result.stderr)
    
    except Exception as e:
        st.error(f"Failed to launch {script_info['name']}: {str(e)}")
        add_activity_log(f"Failed to launch {script_info['name']}: {str(e)}", "error")

def stop_test(script_id: str):
    """Stop a running test"""
    if script_id in st.session_state.test_processes and st.session_state.test_processes[script_id]:
        try:
            process = st.session_state.test_processes[script_id]
            process.terminate()
            process.wait(timeout=5)
            
            script_name = TEST_SCRIPTS[script_id]['name']
            st.success(f"⏹️ Stopped {script_name}")
            add_activity_log(f"Stopped {script_name}", "info")
            
            del st.session_state.test_processes[script_id]
            
        except Exception as e:
            st.error(f"Error stopping test: {e}")

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
        st.markdown("### 🧪 Testing Suite")
        
        page = st.radio(
            "Choose a page:",
            ["🏠 Overview", "📜 Test Scripts", "📊 Results", "📁 File Browser"],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        running_tests = len([p for p in st.session_state.test_processes.values() if p and p.poll() is None])
        st.text(f"Running: {running_tests}")
        st.text(f"Results: {len(st.session_state.test_results)}")
        
        available_scripts = sum(1 for script in TEST_SCRIPTS.values() if check_file_exists(script['file']))
        st.text(f"Available: {available_scripts}/{len(TEST_SCRIPTS)}")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        if st.button("🧹 Clear Logs", use_container_width=True):
            st.session_state.activity_logs = []
            add_activity_log("Cleared activity logs", "info")
        
        if st.button("⏹️ Stop All Tests", use_container_width=True):
            for script_id in list(st.session_state.test_processes.keys()):
                stop_test(script_id)
            st.rerun()
    
    # Main content area
    if page == "🏠 Overview":
        render_overview_page()
    elif page == "📜 Test Scripts":
        render_test_scripts_page()
    elif page == "📊 Results":
        render_test_results_page()
    elif page == "📁 File Browser":
        render_file_browser_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #6B7280; padding: 1rem;">🧪 CivitAI Testing Suite v1.0 - Built with Streamlit</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()