#!/usr/bin/env python3
"""
SD-DarkMaster-Pro Auto-Cleaner & Storage Manager
Advanced storage management with smart cleanup
"""

import sys
import os
from pathlib import Path
import json
import shutil
import subprocess
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import humanize
import time
import logging
import hashlib

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
        
sys.path.insert(0, str(project_root))

# Suppress warnings after path is set
try:
    from suppress_warnings import suppress_streamlit_warnings
    suppress_streamlit_warnings()
except ImportError:
    pass  # Silently skip if not available

# Import modules
from modules.enterprise.unified_storage_manager import UnifiedStorageManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# STORAGE CLEANER
# ============================================================================

class StorageCleaner:
    """Advanced storage cleanup and optimization"""
    
    def __init__(self):
        self.storage_manager = UnifiedStorageManager()
        self.cleanup_history = []
        self.protected_files = self._load_protected_files()
        
    def _load_protected_files(self) -> List[str]:
        """Load list of protected files that should never be deleted"""
        protected = [
            'config.json',
            'ui-config.json',
            'styles.csv',
            'params.txt',
            'user.css'
        ]
        
        # Add model files from session config
        config_file = project_root / 'configs' / 'session.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'selected_models' in config:
                    protected.extend(config['selected_models'])
        
        return protected
    
    def analyze_storage(self) -> Dict:
        """Analyze storage usage and identify cleanup opportunities"""
        logger.info("Analyzing storage...")
        
        analysis = {
            'total_size': 0,
            'categories': {},
            'duplicates': [],
            'old_files': [],
            'large_files': [],
            'temp_files': [],
            'cache_files': [],
            'cleanup_potential': 0
        }
        
        # Get storage usage by category
        usage = self.storage_manager.get_storage_usage()
        
        for category, data in usage.items():
            if isinstance(data, dict):
                if 'size_gb' in data:
                    analysis['categories'][category] = {
                        'size_gb': data['size_gb'],
                        'file_count': data.get('file_count', 0)
                    }
                    analysis['total_size'] += data['size_gb']
                else:
                    category_total = 0
                    for subcat, subdata in data.items():
                        category_total += subdata.get('size_gb', 0)
                    analysis['categories'][category] = {
                        'size_gb': category_total,
                        'subcategories': data
                    }
                    analysis['total_size'] += category_total
        
        # Find duplicates
        analysis['duplicates'] = self._find_duplicates()
        
        # Find old files (>30 days)
        analysis['old_files'] = self._find_old_files(days=30)
        
        # Find large files (>1GB)
        analysis['large_files'] = self._find_large_files(size_gb=1.0)
        
        # Find temp and cache files
        analysis['temp_files'] = self._find_temp_files()
        analysis['cache_files'] = self._find_cache_files()
        
        # Calculate cleanup potential
        cleanup_size = 0
        cleanup_size += sum(f['size_gb'] for f in analysis['duplicates'])
        cleanup_size += sum(f['size_gb'] for f in analysis['old_files'])
        cleanup_size += sum(f['size_gb'] for f in analysis['temp_files'])
        cleanup_size += sum(f['size_gb'] for f in analysis['cache_files'])
        
        analysis['cleanup_potential'] = cleanup_size
        
        return analysis
    
    def _find_duplicates(self) -> List[Dict]:
        """Find duplicate files"""
        duplicates = []
        hash_map = {}
        
        for category_paths in self.storage_manager.storage_paths.values():
            if isinstance(category_paths, dict):
                paths = category_paths.values()
            else:
                paths = [category_paths]
            
            for path in paths:
                if path.exists():
                    for file_path in path.rglob('*'):
                        if file_path.is_file() and file_path.name not in self.protected_files:
                            file_hash = self._get_file_hash(file_path)
                            
                            if file_hash in hash_map:
                                duplicates.append({
                                    'path': str(file_path),
                                    'duplicate_of': str(hash_map[file_hash]),
                                    'size_gb': file_path.stat().st_size / (1024**3)
                                })
                            else:
                                hash_map[file_hash] = file_path
        
        return duplicates
    
    def _find_old_files(self, days: int = 30) -> List[Dict]:
        """Find files older than specified days"""
        old_files = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        output_paths = self.storage_manager.storage_paths.get('outputs', {})
        if isinstance(output_paths, dict):
            paths = output_paths.values()
        else:
            paths = [output_paths]
        
        for path in paths:
            if path.exists():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime < cutoff_time and file_path.name not in self.protected_files:
                            old_files.append({
                                'path': str(file_path),
                                'age_days': (datetime.now() - mtime).days,
                                'size_gb': file_path.stat().st_size / (1024**3)
                            })
        
        return old_files
    
    def _find_large_files(self, size_gb: float = 1.0) -> List[Dict]:
        """Find files larger than specified size"""
        large_files = []
        
        for category_paths in self.storage_manager.storage_paths.values():
            if isinstance(category_paths, dict):
                paths = category_paths.values()
            else:
                paths = [category_paths]
            
            for path in paths:
                if path.exists():
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            file_size_gb = file_path.stat().st_size / (1024**3)
                            if file_size_gb > size_gb:
                                large_files.append({
                                    'path': str(file_path),
                                    'size_gb': file_size_gb,
                                    'type': file_path.suffix
                                })
        
        return sorted(large_files, key=lambda x: x['size_gb'], reverse=True)
    
    def _find_temp_files(self) -> List[Dict]:
        """Find temporary files"""
        temp_files = []
        temp_patterns = ['*.tmp', '*.temp', '*.cache', '*.bak', '*.backup', '~*']
        
        temp_dir = self.storage_manager.storage_paths['outputs'].get('temp')
        if temp_dir and temp_dir.exists():
            for pattern in temp_patterns:
                for file_path in temp_dir.glob(pattern):
                    if file_path.is_file():
                        temp_files.append({
                            'path': str(file_path),
                            'size_gb': file_path.stat().st_size / (1024**3)
                        })
        
        return temp_files
    
    def _find_cache_files(self) -> List[Dict]:
        """Find cache files"""
        cache_files = []
        
        cache_paths = self.storage_manager.storage_paths.get('cache', {})
        if isinstance(cache_paths, dict):
            for cache_type, cache_path in cache_paths.items():
                if cache_path.exists():
                    for file_path in cache_path.rglob('*'):
                        if file_path.is_file():
                            cache_files.append({
                                'path': str(file_path),
                                'type': cache_type,
                                'size_gb': file_path.stat().st_size / (1024**3)
                            })
        
        return cache_files
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def cleanup_duplicates(self) -> Dict:
        """Remove duplicate files"""
        logger.info("Cleaning up duplicate files...")
        
        duplicates = self._find_duplicates()
        removed_count = 0
        freed_space = 0
        
        for dup in duplicates:
            try:
                file_path = Path(dup['path'])
                if file_path.exists():
                    size = file_path.stat().st_size
                    file_path.unlink()
                    removed_count += 1
                    freed_space += size
                    logger.info(f"Removed duplicate: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to remove {dup['path']}: {e}")
        
        result = {
            'removed_files': removed_count,
            'freed_space_gb': freed_space / (1024**3)
        }
        
        self._log_cleanup_action('duplicates', result)
        return result
    
    def cleanup_old_files(self, days: int = 30) -> Dict:
        """Remove old files"""
        logger.info(f"Cleaning up files older than {days} days...")
        
        old_files = self._find_old_files(days)
        removed_count = 0
        freed_space = 0
        
        for old_file in old_files:
            try:
                file_path = Path(old_file['path'])
                if file_path.exists():
                    size = file_path.stat().st_size
                    file_path.unlink()
                    removed_count += 1
                    freed_space += size
                    logger.info(f"Removed old file: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to remove {old_file['path']}: {e}")
        
        result = {
            'removed_files': removed_count,
            'freed_space_gb': freed_space / (1024**3)
        }
        
        self._log_cleanup_action('old_files', result)
        return result
    
    def cleanup_temp_files(self) -> Dict:
        """Remove temporary files"""
        logger.info("Cleaning up temporary files...")
        
        temp_files = self._find_temp_files()
        removed_count = 0
        freed_space = 0
        
        for temp_file in temp_files:
            try:
                file_path = Path(temp_file['path'])
                if file_path.exists():
                    size = file_path.stat().st_size
                    file_path.unlink()
                    removed_count += 1
                    freed_space += size
                    logger.info(f"Removed temp file: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to remove {temp_file['path']}: {e}")
        
        result = {
            'removed_files': removed_count,
            'freed_space_gb': freed_space / (1024**3)
        }
        
        self._log_cleanup_action('temp_files', result)
        return result
    
    def cleanup_cache(self) -> Dict:
        """Clear cache files"""
        logger.info("Clearing cache...")
        
        cache_files = self._find_cache_files()
        removed_count = 0
        freed_space = 0
        
        for cache_file in cache_files:
            try:
                file_path = Path(cache_file['path'])
                if file_path.exists():
                    size = file_path.stat().st_size
                    file_path.unlink()
                    removed_count += 1
                    freed_space += size
            except Exception as e:
                logger.error(f"Failed to remove cache file: {e}")
        
        result = {
            'removed_files': removed_count,
            'freed_space_gb': freed_space / (1024**3)
        }
        
        self._log_cleanup_action('cache', result)
        return result
    
    def cleanup_all(self) -> Dict:
        """Perform complete cleanup"""
        logger.info("Performing complete cleanup...")
        
        results = {
            'duplicates': self.cleanup_duplicates(),
            'old_files': self.cleanup_old_files(),
            'temp_files': self.cleanup_temp_files(),
            'cache': self.cleanup_cache()
        }
        
        total_freed = sum(r['freed_space_gb'] for r in results.values())
        total_files = sum(r['removed_files'] for r in results.values())
        
        summary = {
            'total_files_removed': total_files,
            'total_space_freed_gb': total_freed,
            'details': results
        }
        
        logger.info(f"✅ Cleanup complete: Removed {total_files} files, freed {total_freed:.2f} GB")
        return summary
    
    def _log_cleanup_action(self, action_type: str, result: Dict):
        """Log cleanup action to history"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action_type,
            'result': result
        }
        
        self.cleanup_history.append(history_entry)
        
        # Save to file
        history_file = project_root / 'configs' / 'cleanup_history.json'
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(history_entry)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

# ============================================================================
# UI INTERFACE
# ============================================================================

def render_cleaner_interface():
    """Render storage cleaner interface"""
    try:
        import streamlit as st
        render_streamlit_interface()
    except:
        render_gradio_interface()

def render_streamlit_interface():
    """Render Streamlit cleaner interface"""
    import streamlit as st
    import plotly.express as px
    import pandas as pd
    
    st.markdown("""
    # 🧹 Advanced Storage Management
    ### Storage visualization and cleanup tools
    """)
    
    cleaner = StorageCleaner()
    
    # Analyze storage
    if st.button("🔍 Analyze Storage", key="analyze"):
        with st.spinner("Analyzing storage..."):
            analysis = cleaner.analyze_storage()
            st.session_state['analysis'] = analysis
    
    # Display analysis results
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Storage", f"{analysis['total_size']:.2f} GB")
        with col2:
            st.metric("Cleanup Potential", f"{analysis['cleanup_potential']:.2f} GB")
        with col3:
            cleanup_percent = (analysis['cleanup_potential'] / analysis['total_size'] * 100) if analysis['total_size'] > 0 else 0
            st.metric("Potential Savings", f"{cleanup_percent:.1f}%")
        
        # Storage breakdown chart
        if analysis['categories']:
            st.markdown("### Storage Breakdown")
            
            # Prepare data for chart
            chart_data = []
            for category, data in analysis['categories'].items():
                if 'subcategories' in data:
                    for subcat, subdata in data['subcategories'].items():
                        chart_data.append({
                            'Category': f"{category}/{subcat}",
                            'Size (GB)': subdata.get('size_gb', 0)
                        })
                else:
                    chart_data.append({
                        'Category': category,
                        'Size (GB)': data.get('size_gb', 0)
                    })
            
            if chart_data:
                df = pd.DataFrame(chart_data)
                fig = px.pie(df, values='Size (GB)', names='Category', 
                           title='Storage Distribution',
                           color_discrete_sequence=['#10B981', '#059669', '#047857'])
                st.plotly_chart(fig)
        
        # Cleanup opportunities
        st.markdown("### Cleanup Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"📁 Duplicate files: {len(analysis['duplicates'])}")
            st.info(f"📅 Old files (>30 days): {len(analysis['old_files'])}")
        
        with col2:
            st.info(f"📦 Large files (>1GB): {len(analysis['large_files'])}")
            st.info(f"🗑️ Temp/Cache files: {len(analysis['temp_files']) + len(analysis['cache_files'])}")
        
        # Cleanup actions
        st.markdown("### Cleanup Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Remove Duplicates", key="remove_dup"):
                with st.spinner("Removing duplicates..."):
                    result = cleaner.cleanup_duplicates()
                    st.success(f"Removed {result['removed_files']} files, freed {result['freed_space_gb']:.2f} GB")
        
        with col2:
            if st.button("📅 Remove Old Files", key="remove_old"):
                with st.spinner("Removing old files..."):
                    result = cleaner.cleanup_old_files()
                    st.success(f"Removed {result['removed_files']} files, freed {result['freed_space_gb']:.2f} GB")
        
        with col3:
            if st.button("🗑️ Clear Temp", key="clear_temp"):
                with st.spinner("Clearing temp files..."):
                    result = cleaner.cleanup_temp_files()
                    st.success(f"Removed {result['removed_files']} files, freed {result['freed_space_gb']:.2f} GB")
        
        with col4:
            if st.button("💾 Clear Cache", key="clear_cache"):
                with st.spinner("Clearing cache..."):
                    result = cleaner.cleanup_cache()
                    st.success(f"Removed {result['removed_files']} files, freed {result['freed_space_gb']:.2f} GB")
        
        # Complete cleanup
        st.markdown("---")
        if st.button("🧹 Complete Cleanup (All)", key="cleanup_all", type="primary"):
            with st.spinner("Performing complete cleanup..."):
                summary = cleaner.cleanup_all()
                st.success(f"✅ Complete! Removed {summary['total_files_removed']} files, freed {summary['total_space_freed_gb']:.2f} GB")
                
                # Show details
                with st.expander("Cleanup Details"):
                    st.json(summary['details'])

def render_gradio_interface():
    """Render Gradio cleaner interface (fallback)"""
    import gradio as gr
    
    cleaner = StorageCleaner()
    
    def analyze():
        analysis = cleaner.analyze_storage()
        return f"""
Storage Analysis:
- Total Size: {analysis['total_size']:.2f} GB
- Cleanup Potential: {analysis['cleanup_potential']:.2f} GB
- Duplicates: {len(analysis['duplicates'])} files
- Old Files: {len(analysis['old_files'])} files
- Large Files: {len(analysis['large_files'])} files
- Temp/Cache: {len(analysis['temp_files']) + len(analysis['cache_files'])} files
"""
    
    def cleanup_all():
        summary = cleaner.cleanup_all()
        return f"✅ Removed {summary['total_files_removed']} files, freed {summary['total_space_freed_gb']:.2f} GB"
    
    with gr.Blocks(title="Storage Cleaner") as interface:
        gr.Markdown("# 🧹 Advanced Storage Management")
        
        analyze_btn = gr.Button("Analyze Storage", variant="primary")
        analysis_output = gr.Textbox(label="Analysis Results", lines=10)
        
        analyze_btn.click(analyze, outputs=analysis_output)
        
        gr.Markdown("### Cleanup Actions")
        
        with gr.Row():
            dup_btn = gr.Button("Remove Duplicates")
            old_btn = gr.Button("Remove Old Files")
            temp_btn = gr.Button("Clear Temp")
            cache_btn = gr.Button("Clear Cache")
        
        cleanup_all_btn = gr.Button("Complete Cleanup", variant="primary")
        cleanup_output = gr.Textbox(label="Cleanup Results", lines=3)
        
        cleanup_all_btn.click(cleanup_all, outputs=cleanup_output)
    
    interface.launch(server_name="0.0.0.0", server_port=7863, share=False)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🧹 SD-DarkMaster-Pro Storage Manager")
    print("🎨 Advanced Cleanup & Optimization")
    print("="*60 + "\n")
    
    # Check if running in notebook
    try:
        get_ipython()  # This exists in Jupyter/Colab
        in_notebook = True
    except NameError:
        in_notebook = False
    
    if in_notebook:
        # For notebook mode, show storage info and options
        print("📊 Storage Analysis")
        print("-" * 40)
        
        # Create cleaner instance
        cleaner = StorageCleaner()
        
        # Get storage info
        usage = cleaner.get_storage_usage()
        print(f"📁 Storage Path: {project_root / 'storage'}")
        print(f"💾 Total Size: {usage['total_human']}")
        print(f"📊 Used: {usage['used_human']} ({usage['percent']}%)")
        print(f"✨ Free: {usage['free_human']}")
        
        # Show breakdown by type
        print("\n📂 Storage Breakdown:")
        print("-" * 40)
        for item_type, data in usage['by_type'].items():
            print(f"{item_type.capitalize():12} {data['size_human']:>10} ({data['count']} files)")
        
        # Show available actions
        print("\n🛠️ Available Actions:")
        print("-" * 40)
        print("1. Remove duplicate files")
        print("2. Clean old downloads (30+ days)")
        print("3. Clear temporary files")
        print("4. Optimize storage paths")
        
        print("\n💡 Tip: To perform cleanup, use the Streamlit UI version of this tool")
        print("   or manually manage files in: " + str(project_root / 'storage'))
        
        # Check for issues
        duplicates = cleaner.find_duplicates()
        if duplicates:
            print(f"\n⚠️ Found {len(duplicates)} duplicate files wasting space")
        
        old_files = cleaner.find_old_files(days=30)
        if old_files:
            print(f"⚠️ Found {len(old_files)} files older than 30 days")
            
    else:
        # For non-notebook environments, use UI
        render_cleaner_interface()

if __name__ == "__main__":
    main()