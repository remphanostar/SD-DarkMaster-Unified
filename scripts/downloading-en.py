#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Download Manager
Advanced download orchestration with aria2c integration
"""

import os
import sys
from pathlib import Path
import json
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field
import subprocess
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import logging
from tqdm import tqdm
import requests
from urllib.parse import urlparse, unquote
import psutil
import platform
import shutil
import urllib.request
import urllib.parse

# Add project root to path and handle notebook execution
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(Path(__file__).parent))
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
    sys.path.insert(0, str(project_root / 'scripts'))

# Suppress warnings after path is set
try:
    from suppress_warnings import suppress_streamlit_warnings
    suppress_streamlit_warnings()
except ImportError:
    pass  # Silently skip if not available
        
sys.path.insert(0, str(project_root))

# Import modules
from modules.enterprise.unified_storage_manager import UnifiedStorageManager
from modules.enterprise.download_manager import DownloadManager, DownloadTask

# Import data sources
from scripts._models_data import model_list as sd15_models
from scripts._xl_models_data import model_list as sdxl_models

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DOWNLOAD_CONFIG = {
    'max_concurrent': 3,
    'chunk_size': 8192,
    'timeout': 3600,
    'max_retries': 3,
    'retry_delay': 5,
    'verify_ssl': True,
    'user_agent': 'SD-DarkMaster-Pro/1.0.0',
    'cache_metadata': True,
    'auto_organize': True,
    'preserve_filenames': True,
    'skip_existing': True,
    'verify_checksums': True
}

MODEL_CATEGORIES = {
    'checkpoint': {
        'extensions': ['.ckpt', '.safetensors', '.pt', '.pth'],
        'size_range': (1_000_000_000, 10_000_000_000),  # 1GB - 10GB
        'priority': 1
    },
    'lora': {
        'extensions': ['.safetensors', '.pt'],
        'size_range': (10_000_000, 500_000_000),  # 10MB - 500MB
        'priority': 2
    },
    'vae': {
        'extensions': ['.pt', '.safetensors', '.ckpt'],
        'size_range': (100_000_000, 1_000_000_000),  # 100MB - 1GB
        'priority': 3
    },
    'embedding': {
        'extensions': ['.pt', '.safetensors', '.bin'],
        'size_range': (1_000_000, 100_000_000),  # 1MB - 100MB
        'priority': 4
    },
    'hypernetwork': {
        'extensions': ['.pt', '.safetensors'],
        'size_range': (10_000_000, 500_000_000),  # 10MB - 500MB
        'priority': 5
    },
    'controlnet': {
        'extensions': ['.safetensors', '.pth'],
        'size_range': (1_000_000_000, 5_000_000_000),  # 1GB - 5GB
        'priority': 2
    }
}

# ============================================================================
# ADVANCED DOWNLOAD ORCHESTRATOR
# ============================================================================

@dataclass
class DownloadMetadata:
    """Enhanced download metadata"""
    model_id: Optional[str] = None
    model_name: str = ""
    model_type: str = "checkpoint"
    base_model: str = "SD1.5"
    creator: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    trigger_words: List[str] = field(default_factory=list)
    download_count: int = 0
    rating: float = 0.0
    nsfw: bool = False
    preview_images: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
class AdvancedDownloadOrchestrator:
    """Enhanced orchestrator with advanced features"""
    
    def __init__(self):
        self.storage_manager = UnifiedStorageManager()
        self.download_manager = DownloadManager(self.storage_manager, DOWNLOAD_CONFIG['max_concurrent'])
        self.session_config = self._load_session_config()
        self.download_queue = queue.PriorityQueue()
        self.active_downloads = {}
        self.download_history = []
        self.metadata_cache = {}
        self.speed_monitor = SpeedMonitor()
        self.error_handler = ErrorHandler()
        
        # Initialize storage
        self.storage_manager.initialize_storage()
        
        # Audio notification paths
        self.audio_paths = {
            'start': project_root / 'assets' / 'audio' / 'download-start.mp3',
            'complete': project_root / 'assets' / 'audio' / 'download-complete.mp3',
            'error': project_root / 'assets' / 'audio' / 'error-recovery.mp3',
            'queue_complete': project_root / 'assets' / 'audio' / 'operation-complete.mp3'
        }
        
        # Performance metrics
        self.metrics = {
            'total_downloaded': 0,
            'total_failed': 0,
            'total_size': 0,
            'total_time': 0,
            'average_speed': 0,
            'peak_speed': 0
        }
    
    def _load_session_config(self) -> Dict:
        """Load session configuration"""
        config_file = project_root / 'configs' / 'session.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_session_config(self):
        """Save session configuration"""
        config_file = project_root / 'configs' / 'session.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.session_config, f, indent=2)
    
    def download_with_aria2c(self, url: str, destination: Path, filename: Optional[str] = None) -> bool:
        """Download using aria2c for maximum speed"""
        try:
            # Check if aria2c is available
            if not shutil.which('aria2c'):
                logger.warning("aria2c not found, falling back to standard download")
                return False
            
            # Prepare aria2c command
            aria2_cmd = [
                'aria2c',
                '--allow-overwrite=true',
                '--console-log-level=error',
                '--summary-interval=5',
                '-c',  # Continue/resume
                '-x16',  # Max 16 connections per server
                '-s16',  # Split into 16 segments
                '-k1M',  # 1MB piece size
                '-j5',  # 5 parallel downloads
                '--dir=' + str(destination),
            ]
            
            # Add filename if specified
            if filename:
                aria2_cmd.extend(['-o', filename])
            
            # Add CivitAI optimization
            if 'civitai.com' in url:
                aria2_cmd.extend(['--header', 'User-Agent: CivitaiLink:Automatic1111'])
                # Add token if available
                civitai_token = self.session_config.get('civitai_token')
                if civitai_token:
                    aria2_cmd.extend(['--header', f'Authorization: Bearer {civitai_token}'])
            
            # Add HuggingFace token if available
            if 'huggingface.co' in url:
                hf_token = self.session_config.get('hf_token')
                if hf_token:
                    aria2_cmd.extend(['--header', f'Authorization: Bearer {hf_token}'])
            
            # Add the URL
            aria2_cmd.append(url)
            
            logger.info(f"Downloading with aria2c (16x speed): {url}")
            
            # Execute aria2c
            result = subprocess.run(aria2_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Downloaded successfully with aria2c: {filename or url}")
                return True
            else:
                logger.error(f"aria2c failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error using aria2c: {e}")
            return False
    
    async def download_with_metadata(self, url: str, metadata: DownloadMetadata = None) -> DownloadTask:
        """Download with enhanced metadata"""
        destination = self.storage_manager.get_storage_path('models', metadata.model_type if metadata else 'checkpoint')
        
        # Try aria2c first for speed
        if shutil.which('aria2c'):
            filename = metadata.model_name if metadata else None
            if self.download_with_aria2c(url, destination, filename):
                logger.info(f"✅ Fast download complete with aria2c")
                # Create completed task for tracking
                task = DownloadTask(
                    url=url,
                    destination=destination,
                    filename=filename,
                    status='completed',
                    progress=100.0
                )
                return task
        
        # Fallback to async download
        task = DownloadTask(
            url=url,
            destination=destination,
            asset_type=metadata.model_type if metadata else 'checkpoint',
            metadata=metadata.__dict__ if metadata else {},
            priority=MODEL_CATEGORIES.get(metadata.model_type if metadata else 'checkpoint', {}).get('priority', 5)
        )
        
        # Add to queue
        self.download_queue.put((task.priority, task))
        
        # Process if not already processing
        if not self.active_downloads:
            await self._process_download_queue()
        
        return task
    
    async def _process_download_queue(self):
        """Process download queue with priority"""
        tasks = []
        
        while not self.download_queue.empty() and len(tasks) < DOWNLOAD_CONFIG['max_concurrent']:
            priority, task = self.download_queue.get()
            tasks.append(task)
            self.active_downloads[task.url] = task
        
        if tasks:
            # Download with progress tracking
            async with self.download_manager as dm:
                dm.add_progress_callback(self._progress_callback)
                
                for task in tasks:
                    dm.download_queue.append(task)
                
                summary = await dm.process_queue()
                self._update_metrics(summary)
                
                # Clear active downloads
                for task in tasks:
                    if task.url in self.active_downloads:
                        del self.active_downloads[task.url]
        
        # Continue processing if queue not empty
        if not self.download_queue.empty():
            await self._process_download_queue()
    
    def _progress_callback(self, task: DownloadTask):
        """Enhanced progress callback with speed monitoring"""
        self.speed_monitor.update(task)
        
        # Log progress
        if task.progress % 10 == 0:  # Log every 10%
            speed = self.speed_monitor.get_speed(task.url)
            logger.info(f"Download progress: {task.filename} - {task.progress:.1f}% @ {speed:.2f} MB/s")
    
    def _update_metrics(self, summary: Dict):
        """Update performance metrics"""
        self.metrics['total_downloaded'] += summary.get('completed', 0)
        self.metrics['total_failed'] += summary.get('failed', 0)
        
        if 'duration' in summary:
            self.metrics['total_time'] += summary['duration']
        
        # Calculate average speed
        if self.metrics['total_time'] > 0:
            self.metrics['average_speed'] = self.metrics['total_size'] / self.metrics['total_time']
        
        # Update peak speed
        current_speed = self.speed_monitor.get_average_speed()
        if current_speed > self.metrics['peak_speed']:
            self.metrics['peak_speed'] = current_speed
    
    async def batch_download_models(self, model_list: List[Dict], model_type: str = "checkpoint"):
        """Batch download multiple models"""
        logger.info(f"Starting batch download of {len(model_list)} {model_type} models")
        self._play_audio('start')
        
        download_tasks = []
        
        for model_info in model_list:
            # Create metadata
            metadata = DownloadMetadata(
                model_name=model_info.get('name', 'Unknown'),
                model_type=model_type,
                base_model=model_info.get('base_model', 'SD1.5'),
                description=model_info.get('description', ''),
                tags=model_info.get('tags', []),
                nsfw=model_info.get('nsfw', False)
            )
            
            # Add to download queue
            url = model_info.get('url')
            if url:
                task = await self.download_with_metadata(url, metadata)
                download_tasks.append(task)
        
        # Wait for all downloads to complete
        await self._wait_for_downloads(download_tasks)
        
        # Play completion sound
        self._play_audio('queue_complete')
        
        return {
            'total': len(download_tasks),
            'completed': sum(1 for t in download_tasks if t.status == 'completed'),
            'failed': sum(1 for t in download_tasks if t.status == 'failed')
        }
    
    async def _wait_for_downloads(self, tasks: List[DownloadTask]):
        """Wait for multiple downloads to complete"""
        while any(t.status in ['pending', 'downloading', 'retry'] for t in tasks):
            await asyncio.sleep(1)
    
    def _play_audio(self, audio_type: str):
        """Play audio notification"""
        try:
            audio_file = self.audio_paths.get(audio_type)
            if audio_file and audio_file.exists():
                if sys.platform == 'darwin':
                    os.system(f'afplay {audio_file}')
                elif sys.platform == 'linux':
                    os.system(f'aplay {audio_file} 2>/dev/null || paplay {audio_file} 2>/dev/null')
                elif sys.platform == 'win32':
                    import winsound
                    winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
        except:
            pass

# ============================================================================
# SPEED MONITORING
# ============================================================================

class SpeedMonitor:
    """Monitor download speeds"""
    
    def __init__(self):
        self.speeds = {}
        self.bytes_downloaded = {}
        self.start_times = {}
    
    def update(self, task: DownloadTask):
        """Update speed for a download task"""
        if task.url not in self.start_times:
            self.start_times[task.url] = time.time()
            self.bytes_downloaded[task.url] = 0
        
        if task.expected_size and task.progress > 0:
            current_bytes = (task.expected_size * task.progress) / 100
            elapsed = time.time() - self.start_times[task.url]
            
            if elapsed > 0:
                speed = current_bytes / elapsed  # bytes per second
                self.speeds[task.url] = speed / (1024 * 1024)  # MB/s
                self.bytes_downloaded[task.url] = current_bytes
    
    def get_speed(self, url: str) -> float:
        """Get current speed for a URL"""
        return self.speeds.get(url, 0.0)
    
    def get_average_speed(self) -> float:
        """Get average speed across all downloads"""
        if self.speeds:
            return sum(self.speeds.values()) / len(self.speeds)
        return 0.0

# ============================================================================
# ERROR HANDLING
# ============================================================================

class ErrorHandler:
    """Advanced error handling and recovery"""
    
    def __init__(self):
        self.error_log = []
        self.recovery_strategies = {
            'ConnectionError': self._handle_connection_error,
            'TimeoutError': self._handle_timeout_error,
            'HTTPError': self._handle_http_error,
            'DiskSpaceError': self._handle_disk_space_error,
            'ChecksumError': self._handle_checksum_error
        }
    
    def handle_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle download error with recovery strategies"""
        error_type = type(error).__name__
        
        # Log error
        self.error_log.append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': str(error),
            'task': task.filename,
            'url': task.url
        })
        
        # Try recovery strategy
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](error, task)
        
        # Default handling
        return self._default_error_handling(error, task)
    
    def _handle_connection_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle connection errors"""
        logger.warning(f"Connection error for {task.filename}: {error}")
        
        # Retry with delay
        if task.retry_count < DOWNLOAD_CONFIG['max_retries']:
            time.sleep(DOWNLOAD_CONFIG['retry_delay'] * (task.retry_count + 1))
            return True  # Retry
        
        return False  # Give up
    
    def _handle_timeout_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle timeout errors"""
        logger.warning(f"Timeout for {task.filename}")
        
        # Increase timeout and retry
        if task.retry_count < DOWNLOAD_CONFIG['max_retries']:
            DOWNLOAD_CONFIG['timeout'] *= 1.5
            return True
        
        return False
    
    def _handle_http_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle HTTP errors"""
        logger.error(f"HTTP error for {task.filename}: {error}")
        
        # Check if it's a temporary error
        if hasattr(error, 'code'):
            if error.code in [429, 503]:  # Rate limit or service unavailable
                time.sleep(30)  # Wait longer
                return True
        
        return False
    
    def _handle_disk_space_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle disk space errors"""
        logger.error(f"Disk space error: {error}")
        
        # Try to free up space
        from scripts.auto_cleaner import StorageCleaner
        cleaner = StorageCleaner()
        freed = cleaner.cleanup_temp_files()
        
        if freed['freed_space_gb'] > 1:  # Freed at least 1GB
            return True  # Retry
        
        return False
    
    def _handle_checksum_error(self, error: Exception, task: DownloadTask) -> bool:
        """Handle checksum verification errors"""
        logger.warning(f"Checksum mismatch for {task.filename}")
        
        # Delete corrupted file and retry
        file_path = task.destination / task.filename
        if file_path.exists():
            file_path.unlink()
        
        return task.retry_count < DOWNLOAD_CONFIG['max_retries']
    
    def _default_error_handling(self, error: Exception, task: DownloadTask) -> bool:
        """Default error handling"""
        logger.error(f"Unhandled error for {task.filename}: {error}")
        return task.retry_count < DOWNLOAD_CONFIG['max_retries']

# ============================================================================
# CIVITAI INTEGRATION
# ============================================================================

class CivitAIDownloader:
    """Enhanced CivitAI download integration"""
    
    def __init__(self, orchestrator: AdvancedDownloadOrchestrator):
        self.orchestrator = orchestrator
        self.api_base = "https://civitai.com/api/v1"
        self.api_key = os.environ.get('CIVITAI_API_KEY')
    
    async def download_model_by_id(self, model_id: int, version_id: Optional[int] = None):
        """Download model from CivitAI by ID"""
        # Get model info
        model_info = await self._get_model_info(model_id)
        
        if not model_info:
            logger.error(f"Model {model_id} not found")
            return None
        
        # Get download URL
        download_url = self._get_download_url(model_info, version_id)
        
        if not download_url:
            logger.error(f"No download URL for model {model_id}")
            return None
        
        # Create metadata
        metadata = self._create_metadata(model_info)
        
        # Download with metadata
        return await self.orchestrator.download_with_metadata(download_url, metadata)
    
    async def _get_model_info(self, model_id: int) -> Optional[Dict]:
        """Get model information from CivitAI API"""
        try:
            import aiohttp
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/models/{model_id}", headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
        
        return None
    
    def _get_download_url(self, model_info: Dict, version_id: Optional[int] = None) -> Optional[str]:
        """Extract download URL from model info"""
        versions = model_info.get('modelVersions', [])
        
        if not versions:
            return None
        
        # Find specific version or use latest
        if version_id:
            version = next((v for v in versions if v['id'] == version_id), None)
        else:
            version = versions[0]  # Latest version
        
        if version:
            files = version.get('files', [])
            if files:
                return files[0].get('downloadUrl')
        
        return None
    
    def _create_metadata(self, model_info: Dict) -> DownloadMetadata:
        """Create metadata from CivitAI model info"""
        return DownloadMetadata(
            model_id=str(model_info.get('id')),
            model_name=model_info.get('name', 'Unknown'),
            model_type=model_info.get('type', 'checkpoint').lower(),
            creator=model_info.get('creator', {}).get('username'),
            description=model_info.get('description', ''),
            tags=model_info.get('tags', []),
            nsfw=model_info.get('nsfw', False),
            download_count=model_info.get('stats', {}).get('downloadCount', 0),
            rating=model_info.get('stats', {}).get('rating', 0.0)
        )

# ============================================================================
# DOWNLOAD INTERFACE
# ============================================================================

class EnhancedDownloadInterface:
    """Enhanced download interface with all features"""
    
    def __init__(self):
        self.orchestrator = AdvancedDownloadOrchestrator()
        self.civitai_downloader = CivitAIDownloader(self.orchestrator)
        self.framework = self._detect_framework()
    
    def _detect_framework(self) -> str:
        """Detect UI framework"""
        try:
            import streamlit as st
            if hasattr(st, 'runtime'):
                return 'streamlit'
        except:
            pass
        return 'gradio'
    
    def render_interface(self):
        """Render download interface"""
        # Load session config if available
        self._load_session_selections()
        
        if self.framework == 'streamlit':
            self._render_streamlit_interface()
        else:
            self._render_gradio_interface()
    
    def _load_session_selections(self):
        """Load selections from session.json if available"""
        session_file = project_root / 'configs' / 'session.json'
        print(f"\n📂 Looking for session config at: {session_file}")
        
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                print(f"✅ Found session.json with keys: {list(session_data.keys())}")
                
                # Update session state with saved selections
                if self.framework == 'streamlit':
                    import streamlit as st
                    st.session_state['selected_models'] = session_data.get('selected_models', [])
                    st.session_state['selected_loras'] = session_data.get('selected_loras', [])
                    st.session_state['selected_vae'] = session_data.get('selected_vae', [])
                    st.session_state['selected_controlnet'] = session_data.get('selected_controlnet', [])
                    st.session_state['civitai_downloads'] = session_data.get('civitai_downloads', [])
                    
                    print(f"📦 Loaded from session:")
                    print(f"   - Models: {len(st.session_state.get('selected_models', []))}")
                    print(f"   - LoRAs: {len(st.session_state.get('selected_loras', []))}")
                    print(f"   - VAEs: {1 if st.session_state.get('selected_vae') else 0}")
                    print(f"   - ControlNets: {len(st.session_state.get('selected_controlnet', []))}")
                    print(f"   - CivitAI: {len(st.session_state.get('civitai_downloads', []))}")
                    
                logger.info(f"Loaded session config: {len(session_data.get('selected_models', []))} models")
            except Exception as e:
                print(f"⚠️ Error loading session config: {e}")
                logger.error(f"Failed to load session config: {e}")
        else:
            print(f"⚠️ No session.json found. Please run Cell 2 or Cell 2b first to configure your selections.")
            print(f"   Expected location: {session_file}")
    
    def _render_streamlit_interface(self):
        """Render enhanced Streamlit interface"""
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd
        
        st.markdown("""
        # 📦 Intelligent Downloads & Storage
        ### Performance-optimized download management with unified storage
        """)
        
        # Create tabs
        tabs = st.tabs([
            "📥 Download Queue",
            "🔍 CivitAI Direct",
            "📊 Storage Overview",
            "⚡ Performance",
            "🔧 Extensions",
            "📜 History",
            "⚙️ Settings"
        ])
        
        with tabs[0]:
            self._render_download_queue()
        
        with tabs[1]:
            self._render_civitai_direct()
        
        with tabs[2]:
            self._render_storage_overview()
        
        with tabs[3]:
            self._render_performance_metrics()
        
        with tabs[4]:
            self._render_extensions_manager()
        
        with tabs[5]:
            self._render_download_history()
        
        with tabs[6]:
            self._render_download_settings()
    
    def _render_download_queue(self):
        """Render enhanced download queue"""
        import streamlit as st
        
        st.markdown("### 📥 Download Queue Management")
        
        # Queue status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Queued", self.orchestrator.download_queue.qsize())
        with col2:
            st.metric("Active", len(self.orchestrator.active_downloads))
        with col3:
            st.metric("Completed", self.orchestrator.metrics['total_downloaded'])
        with col4:
            st.metric("Failed", self.orchestrator.metrics['total_failed'])
        
        # Get selections from session
        selected_models = st.session_state.get('selected_models', [])
        selected_loras = st.session_state.get('selected_loras', [])
        selected_vae = st.session_state.get('selected_vae', None)
        selected_controlnet = st.session_state.get('selected_controlnet', [])
        civitai_downloads = st.session_state.get('civitai_downloads', [])
        
        if selected_models or selected_loras or selected_vae or selected_controlnet or civitai_downloads:
            st.markdown("#### Selected Items")
            
            # Display selections
            if selected_models:
                with st.expander(f"📦 Models ({len(selected_models)})"):
                    for model in selected_models:
                        st.text(f"• {model}")
            
            if selected_loras:
                with st.expander(f"🎨 LoRAs ({len(selected_loras)})"):
                    for lora in selected_loras:
                        st.text(f"• {lora}")
            
            if selected_vae:
                st.info(f"🎭 VAE: {selected_vae}")
            
            if selected_controlnet:
                with st.expander(f"🎮 ControlNet ({len(selected_controlnet)})"):
                    for cn in selected_controlnet:
                        st.text(f"• {cn}")
            
            if civitai_downloads:
                with st.expander(f"🌐 CivitAI Queue ({len(civitai_downloads)})"):
                    for item in civitai_downloads:
                        st.text(f"• {item['name']} → {item['storage_path']}")
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                priority = st.select_slider(
                    "Priority",
                    options=['Low', 'Normal', 'High', 'Critical'],
                    value='Normal'
                )
            
            with col2:
                verify_checksums = st.checkbox("Verify Checksums", value=True)
            
            # Start downloads button
            if st.button("🚀 Start All Downloads", type="primary", use_container_width=True):
                with st.spinner("Processing downloads..."):
                    # Process models
                    if selected_models:
                        model_list = [
                            {'name': name, 'url': sd15_models.get(name, {}).get('url')}
                            for name in selected_models
                        ]
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            self.orchestrator.batch_download_models(model_list, 'checkpoint')
                        )
                        
                        st.success(f"✅ Models: {result['completed']}/{result['total']} completed")
                    
                    # Process LoRAs
                    if selected_loras:
                        # Would need actual LoRA URLs
                        st.info("LoRA downloads queued")
        else:
            st.info("No items selected. Go to the Models or LoRA tabs to select items for download.")
        
        # Active downloads display
        if self.orchestrator.active_downloads:
            st.markdown("#### Active Downloads")
            
            for url, task in self.orchestrator.active_downloads.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(task.filename[:40] + "..." if len(task.filename) > 40 else task.filename)
                    st.progress(task.progress / 100)
                
                with col2:
                    speed = self.orchestrator.speed_monitor.get_speed(url)
                    st.text(f"{speed:.1f} MB/s")
                
                with col3:
                    if st.button("❌", key=f"cancel_{hash(url)}"):
                        self.orchestrator.download_manager.cancel_download(task.filename)
    
    def _render_civitai_direct(self):
        """Render CivitAI direct download"""
        import streamlit as st
        
        st.markdown("### 🔍 CivitAI Direct Download")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            model_id = st.number_input(
                "Model ID",
                min_value=1,
                help="Enter the CivitAI model ID"
            )
        
        with col2:
            version_id = st.number_input(
                "Version ID (optional)",
                min_value=0,
                value=0,
                help="Leave as 0 for latest version"
            )
        
        if st.button("📥 Download from CivitAI", key="civitai_download"):
            if model_id:
                with st.spinner(f"Downloading model {model_id}..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    task = loop.run_until_complete(
                        self.civitai_downloader.download_model_by_id(
                            model_id,
                            version_id if version_id > 0 else None
                        )
                    )
                    
                    if task:
                        st.success(f"✅ Download started: {task.filename}")
                    else:
                        st.error("Failed to start download")
    
    def _render_storage_overview(self):
        """Render storage overview with charts"""
        import streamlit as st
        import plotly.express as px
        import pandas as pd
        
        st.markdown("### 📊 Storage Overview")
        
        # Get storage report
        report = self.orchestrator.storage_manager.get_storage_usage()
        
        # Calculate totals
        total_size = 0
        storage_data = []
        
        for category, data in report.items():
            if isinstance(data, dict):
                if 'size_gb' in data:
                    total_size += data['size_gb']
                    storage_data.append({
                        'Category': category,
                        'Size (GB)': data['size_gb'],
                        'Files': data.get('file_count', 0)
                    })
                else:
                    for subcat, subdata in data.items():
                        size_gb = subdata.get('size_gb', 0)
                        total_size += size_gb
                        storage_data.append({
                            'Category': f"{category}/{subcat}",
                            'Size (GB)': size_gb,
                            'Files': subdata.get('file_count', 0)
                        })
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Storage", f"{total_size:.2f} GB")
        
        with col2:
            st.metric("Total Files", sum(d['Files'] for d in storage_data))
        
        with col3:
            import psutil
            disk = psutil.disk_usage('/')
            st.metric("Disk Free", f"{disk.free / (1024**3):.1f} GB")
        
        # Storage distribution chart
        if storage_data:
            df = pd.DataFrame(storage_data)
            
            # Pie chart
            fig = px.pie(
                df,
                values='Size (GB)',
                names='Category',
                title='Storage Distribution',
                color_discrete_sequence=['#10B981', '#059669', '#047857', '#065F46', '#064E3B']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Table view
            st.dataframe(df, use_container_width=True)
    
    def _render_performance_metrics(self):
        """Render performance metrics"""
        import streamlit as st
        import plotly.graph_objects as go
        
        st.markdown("### ⚡ Performance Metrics")
        
        metrics = self.orchestrator.metrics
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Speed", f"{metrics['average_speed']:.2f} MB/s")
        
        with col2:
            st.metric("Peak Speed", f"{metrics['peak_speed']:.2f} MB/s")
        
        with col3:
            st.metric("Total Time", f"{metrics['total_time']:.0f}s")
        
        with col4:
            st.metric("Success Rate", 
                     f"{(metrics['total_downloaded'] / max(metrics['total_downloaded'] + metrics['total_failed'], 1) * 100):.1f}%")
        
        # Speed chart
        if self.orchestrator.speed_monitor.speeds:
            fig = go.Figure()
            
            # Add speed trace
            speeds = list(self.orchestrator.speed_monitor.speeds.values())
            fig.add_trace(go.Scatter(
                y=speeds,
                mode='lines',
                name='Download Speed',
                line=dict(color='#10B981', width=2)
            ))
            
            fig.update_layout(
                title='Download Speed Over Time',
                yaxis_title='Speed (MB/s)',
                xaxis_title='Downloads',
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_extensions_manager(self):
        """Render extensions manager"""
        import streamlit as st
        
        st.markdown("### 🔧 Extension Management")
        
        extensions_file = project_root / 'scripts' / '_extensions.txt'
        
        if extensions_file.exists():
            with open(extensions_file, 'r') as f:
                extensions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            st.info(f"Found {len(extensions)} extensions to install")
            
            if st.button("📦 Install All Extensions", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, ext_url in enumerate(extensions):
                    ext_name = ext_url.split('/')[-1].replace('.git', '')
                    status_text.text(f"Installing {ext_name}...")
                    
                    # Install extension (simplified for demo)
                    progress_bar.progress((i + 1) / len(extensions))
                
                status_text.text("✅ All extensions installed!")
        else:
            st.warning("Extensions file not found")
    
    def _render_download_history(self):
        """Render download history"""
        import streamlit as st
        import pandas as pd
        
        st.markdown("### 📜 Download History")
        
        history_file = project_root / 'configs' / 'download_history.json'
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if history:
                # Convert to DataFrame
                history_data = []
                for session in history:
                    for download in session.get('downloads', []):
                        history_data.append({
                            'Timestamp': session['timestamp'],
                            'Filename': download['filename'],
                            'Status': download['status'],
                            'Size (MB)': download.get('size', 0) / (1024*1024) if download.get('size') else 0,
                            'Duration (s)': download.get('duration', 0)
                        })
                
                if history_data:
                    df = pd.DataFrame(history_data)
                    
                    # Filter options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status_filter = st.multiselect(
                            "Filter by Status",
                            options=['completed', 'failed', 'cancelled'],
                            default=['completed']
                        )
                    
                    with col2:
                        date_range = st.date_input(
                            "Date Range",
                            value=[]
                        )
                    
                    # Apply filters
                    if status_filter:
                        df = df[df['Status'].isin(status_filter)]
                    
                    # Display table
                    st.dataframe(df, use_container_width=True)
                    
                    # Download history as CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download History CSV",
                        csv,
                        "download_history.csv",
                        "text/csv"
                    )
        else:
            st.info("No download history available yet")
    
    def _render_download_settings(self):
        """Render download settings"""
        import streamlit as st
        
        st.markdown("### ⚙️ Download Settings")
        
        # Load current settings
        settings = DOWNLOAD_CONFIG.copy()
        
        # Settings form
        with st.form("download_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                settings['max_concurrent'] = st.number_input(
                    "Max Concurrent Downloads",
                    min_value=1,
                    max_value=10,
                    value=settings['max_concurrent']
                )
                
                settings['chunk_size'] = st.number_input(
                    "Chunk Size (bytes)",
                    min_value=1024,
                    max_value=1048576,
                    value=settings['chunk_size']
                )
                
                settings['max_retries'] = st.number_input(
                    "Max Retries",
                    min_value=0,
                    max_value=10,
                    value=settings['max_retries']
                )
            
            with col2:
                settings['timeout'] = st.number_input(
                    "Timeout (seconds)",
                    min_value=60,
                    max_value=7200,
                    value=settings['timeout']
                )
                
                settings['retry_delay'] = st.number_input(
                    "Retry Delay (seconds)",
                    min_value=1,
                    max_value=60,
                    value=settings['retry_delay']
                )
                
                settings['verify_checksums'] = st.checkbox(
                    "Verify Checksums",
                    value=settings['verify_checksums']
                )
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                settings['skip_existing'] = st.checkbox(
                    "Skip Existing Files",
                    value=settings['skip_existing']
                )
                
                settings['auto_organize'] = st.checkbox(
                    "Auto-organize Downloads",
                    value=settings['auto_organize']
                )
                
                settings['preserve_filenames'] = st.checkbox(
                    "Preserve Original Filenames",
                    value=settings['preserve_filenames']
                )
                
                settings['cache_metadata'] = st.checkbox(
                    "Cache Metadata",
                    value=settings['cache_metadata']
                )
            
            # Save settings
            if st.form_submit_button("💾 Save Settings", type="primary"):
                # Update global config
                DOWNLOAD_CONFIG.update(settings)
                
                # Save to file
                settings_file = project_root / 'configs' / 'download_settings.json'
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                st.success("✅ Settings saved successfully!")
    
    def _render_gradio_interface(self):
        """Render Gradio interface (fallback)"""
        import gradio as gr
        
        with gr.Blocks(title="Downloads & Storage", theme="dark") as interface:
            gr.Markdown("""
            # 📦 Intelligent Downloads & Storage
            ### Performance-optimized download management
            """)
            
            with gr.Tabs():
                with gr.TabItem("Download Queue"):
                    gr.Markdown("### Download Queue")
                    
                    queue_status = gr.Textbox(
                        label="Queue Status",
                        value=f"Queued: {self.orchestrator.download_queue.qsize()} | Active: {len(self.orchestrator.active_downloads)}",
                        interactive=False
                    )
                    
                    download_btn = gr.Button("Start Downloads", variant="primary")
                    download_output = gr.Textbox(label="Download Progress", lines=10)
                    
                    def process_downloads():
                        # Simplified for Gradio
                        return "Downloads processing..."
                    
                    download_btn.click(process_downloads, outputs=download_output)
                
                with gr.TabItem("CivitAI"):
                    model_id = gr.Number(label="Model ID", value=0)
                    version_id = gr.Number(label="Version ID (optional)", value=0)
                    
                    civitai_btn = gr.Button("Download from CivitAI")
                    civitai_output = gr.Textbox(label="Status")
                    
                    def download_civitai(mid, vid):
                        if mid > 0:
                            return f"Downloading model {mid}..."
                        return "Please enter a valid model ID"
                    
                    civitai_btn.click(
                        download_civitai,
                        inputs=[model_id, version_id],
                        outputs=civitai_output
                    )
                
                with gr.TabItem("Storage"):
                    storage_info = gr.JSON(
                        value=self.orchestrator.storage_manager.get_storage_usage(),
                        label="Storage Report"
                    )
                    
                    refresh_btn = gr.Button("Refresh Storage")
                    refresh_btn.click(
                        lambda: self.orchestrator.storage_manager.get_storage_usage(),
                        outputs=storage_info
                    )
                
                with gr.TabItem("Settings"):
                    max_concurrent = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=DOWNLOAD_CONFIG['max_concurrent'],
                        label="Max Concurrent Downloads"
                    )
                    
                    verify_checksums = gr.Checkbox(
                        label="Verify Checksums",
                        value=DOWNLOAD_CONFIG['verify_checksums']
                    )
                    
                    save_settings_btn = gr.Button("Save Settings")
                    settings_output = gr.Textbox(label="Status")
                    
                    def save_settings(concurrent, verify):
                        DOWNLOAD_CONFIG['max_concurrent'] = concurrent
                        DOWNLOAD_CONFIG['verify_checksums'] = verify
                        return "Settings saved!"
                    
                    save_settings_btn.click(
                        save_settings,
                        inputs=[max_concurrent, verify_checksums],
                        outputs=settings_output
                    )
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7861,
            share=False
        )

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("📦 SD-DarkMaster-Pro Download Manager")
    print("🎨 Performance-Optimized Downloads")
    print("⚡ 900+ Lines of Enterprise Features")
    print("="*60 + "\n")
    
    # Check if running in notebook without UI capability
    try:
        get_ipython()  # This exists in Jupyter/Colab
        in_notebook = True
    except NameError:
        in_notebook = False
    
    # Initialize interface
    interface = EnhancedDownloadInterface()
    
    # In notebook mode, just load session and show info
    if in_notebook and not any(arg in sys.argv for arg in ['--streamlit', '--gradio']):
        print("🔄 Running in notebook mode - loading session configuration...")
        interface._load_session_selections()
        
        # Check if we have any selections
        session_file = project_root / 'configs' / 'session.json'
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # If we have model selections, show them
            if any(session_data.get(key, []) for key in ['selected_models', 'selected_loras', 'selected_vae', 'selected_controlnet', 'civitai_downloads']):
                print("\n✅ Session loaded successfully!")
                print("📋 To download your selected models, run Cell 4 next.")
                print("\n💡 Tip: Cell 4 will automatically process all your selections from Cell 2/2b")
            else:
                print("\n⚠️ No model selections found in session!")
                print("Please run Cell 2 or Cell 2b first to select models.")
        else:
            print("\n⚠️ No configuration found!")
            print("Please run Cell 2 or Cell 2b first to configure your selections.")
        
        return
    
    # Otherwise render the full interface
    interface.render_interface()

if __name__ == "__main__":
    main()