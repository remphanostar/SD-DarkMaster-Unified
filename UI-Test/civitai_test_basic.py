#!/usr/bin/env python3
"""
CivitAI Basic Search and Download - Test Implementation
Step 1: Simple search functionality with download capability
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path
from datetime import datetime
import time

# ===============================
# BASIC CIVITAI API CLASS
# ===============================

class CivitAIBasic:
    def __init__(self, api_key=None):
        # Use hardcoded API key if none provided
        self.api_key = api_key or "ff14ef326fa02885e8202e4d44fc9a13"
        self.base_url = "https://civitai.com/api/v1"
        self.headers = {}
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def search_models(self, query="", limit=50, sort="Highest Rated", model_type=None):
        """Basic model search"""
        
        params = {
            'limit': min(limit, 100),  # CivitAI max is usually 100
            'sort': sort,
            'nsfw': 'true'  # Include NSFW results for broader search
        }
        
        if query and query.strip():
            params['query'] = query.strip()
            
        if model_type and model_type != "All":
            params['types'] = [model_type]
            
        if self.api_key:
            params['token'] = self.api_key
        
        try:
            print(f"🔍 Searching CivitAI with params: {params}")
            
            response = requests.get(
                f"{self.base_url}/models",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('items', []))} models")
                return data.get('items', [])
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def get_model_details(self, model_id):
        """Get detailed model information"""
        
        params = {}
        if self.api_key:
            params['token'] = self.api_key
            
        try:
            response = requests.get(
                f"{self.base_url}/models/{model_id}",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get model details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting model details: {e}")
            return None
    
    def download_model_file(self, download_url, filename, download_dir="downloads"):
        """Download a model file"""
        
        # Create download directory
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        file_path = download_path / filename
        
        try:
            print(f"📥 Starting download: {filename}")
            print(f"🔗 URL: {download_url}")
            
            # Stream download with progress
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"📊 Progress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)")
            
            print(f"✅ Download complete: {file_path}")
            return str(file_path)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"❌ Download failed: Unauthorized (401)")
                print(f"💡 This model requires a CivitAI API key for download")
                print(f"🔑 Get your free API key at: https://civitai.com/user/account")
                print(f"📝 Some models may be NSFW-gated or creator-restricted")
            else:
                print(f"❌ Download failed: HTTP {e.response.status_code} - {e}")
            return None
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

# ===============================
# STREAMLIT INTERFACE
# ===============================

def main():
    st.set_page_config(
        page_title="CivitAI Basic Test",
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 CivitAI Basic Search & Download Test")
    st.markdown("**Step 1:** Testing basic CivitAI search and download functionality")
    
    # Initialize session state
    if 'civitai_api' not in st.session_state:
        # Auto-initialize with hardcoded API key for seamless testing
        st.session_state.civitai_api = CivitAIBasic()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    
    # API Key input
    st.subheader("🔑 API Configuration")
    api_key = st.text_input(
        "CivitAI API Key (pre-filled for testing)", 
        value="ff14ef326fa02885e8202e4d44fc9a13",
        type="password",
        help="API key is pre-configured for testing. Get your own at https://civitai.com/user/account"
    )
    
    if st.button("🔌 Re-initialize API") or api_key != st.session_state.civitai_api.api_key:
        st.session_state.civitai_api = CivitAIBasic(api_key)
        st.success("✅ CivitAI API updated!")
    
    # Show current API status
    st.info(f"🔌 **API Status:** Ready with key: ...{st.session_state.civitai_api.api_key[-8:]}")
    
    # Search Interface
    st.subheader("🔍 Model Search")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Query", 
            placeholder="Enter model name or keywords...",
            value="realistic"
        )
    
    with col2:
        model_type = st.selectbox(
            "Model Type",
            ["All", "Checkpoint", "LORA", "TextualInversion", "Hypernetwork", "VAE"]
        )
    
    with col3:
        limit = st.slider("Results", 10, 100, 50)
    
    # Search button
    if st.button("🔍 Search Models"):
        with st.spinner("Searching CivitAI..."):
            
            search_type = None if model_type == "All" else model_type
            
            results = st.session_state.civitai_api.search_models(
                query=search_query,
                limit=limit,
                model_type=search_type
            )
            
            st.session_state.search_results = results
            
            if results:
                st.success(f"✅ Found {len(results)} models!")
            else:
                st.error("❌ No models found or search failed")
    
    # Display Results
    if st.session_state.search_results:
        st.subheader("📋 Search Results")
        
        for i, model in enumerate(st.session_state.search_results):
            with st.expander(f"🎨 {model.get('name', 'Unknown')} - {model.get('type', 'Unknown')}", expanded=i < 3):
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Creator:** {model.get('creator', {}).get('username', 'Unknown')}")
                    st.write(f"**Type:** {model.get('type', 'Unknown')}")
                    st.write(f"**NSFW:** {'Yes' if model.get('nsfw', False) else 'No'}")
                    
                    if model.get('description'):
                        st.write(f"**Description:** {model['description'][:200]}...")
                    
                    if model.get('tags'):
                        st.write(f"**Tags:** {', '.join(model['tags'][:5])}")
                
                with col2:
                    # Stats
                    stats = model.get('stats', {})
                    st.metric("Downloads", f"{stats.get('downloadCount', 0):,}")
                    st.metric("Rating", f"{stats.get('rating', 0):.1f}/5")
                    st.metric("Favorites", f"{stats.get('favoriteCount', 0):,}")
                
                with col3:
                    # Actions
                    if st.button(f"📖 View Details", key=f"details_{model['id']}"):
                        st.session_state.selected_model = model
                        st.rerun()
                    
                    if st.button(f"🔗 Open on CivitAI", key=f"open_{model['id']}"):
                        model_url = f"https://civitai.com/models/{model['id']}"
                        st.markdown(f"[🔗 Open Model]({model_url})")
    
    # Model Details and Download
    if st.session_state.selected_model:
        model = st.session_state.selected_model
        
        st.subheader(f"📖 Model Details: {model['name']}")
        
        with st.spinner("Loading model details..."):
            model_details = st.session_state.civitai_api.get_model_details(model['id'])
        
        if model_details:
            # Display model versions
            versions = model_details.get('modelVersions', [])
            
            if versions:
                st.write(f"**Available Versions:** {len(versions)}")
                
                for version_idx, version in enumerate(versions):
                    with st.expander(f"📦 Version: {version.get('name', f'Version {version_idx + 1}')}", expanded=version_idx == 0):
                        
                        # Version info
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Base Model:** {version.get('baseModel', 'Unknown')}")
                            st.write(f"**Created:** {version.get('createdAt', 'Unknown')}")
                            
                            if version.get('description'):
                                st.write(f"**Description:** {version['description'][:200]}...")
                        
                        with col2:
                            # Version stats
                            version_stats = version.get('stats', {})
                            st.metric("Downloads", f"{version_stats.get('downloadCount', 0):,}")
                        
                        # Files
                        files = version.get('files', [])
                        if files:
                            st.write(f"**Available Files ({len(files)}):**")
                            
                            for file_info in files:
                                file_col1, file_col2, file_col3 = st.columns([3, 1, 1])
                                
                                with file_col1:
                                    st.text(f"📄 {file_info.get('name', 'Unknown')}")
                                    
                                    # File size
                                    size_kb = file_info.get('sizeKB', 0)
                                    if size_kb > 0:
                                        if size_kb > 1024 * 1024:  # > 1GB
                                            size_str = f"{size_kb / (1024 * 1024):.1f} GB"
                                        elif size_kb > 1024:  # > 1MB
                                            size_str = f"{size_kb / 1024:.1f} MB"
                                        else:
                                            size_str = f"{size_kb} KB"
                                        st.caption(f"Size: {size_str}")
                                
                                with file_col2:
                                    file_type = file_info.get('type', 'Model')
                                    st.text(f"Type: {file_type}")
                                
                                with file_col3:
                                    download_url = file_info.get('downloadUrl')
                                    
                                    if download_url and st.button(f"📥 Download", key=f"download_{file_info.get('id', 'unknown')}"):
                                        
                                        # Start download
                                        with st.spinner(f"Downloading {file_info['name']}..."):
                                            
                                            filename = file_info['name']
                                            download_result = st.session_state.civitai_api.download_model_file(
                                                download_url=download_url,
                                                filename=filename,
                                                download_dir="downloads/civitai"
                                            )
                                            
                                            if download_result:
                                                st.success(f"✅ Downloaded: {filename}")
                                                st.info(f"📁 Location: {download_result}")
                                            else:
                                                st.error("❌ Download failed!")
            else:
                st.warning("No versions available for this model")
        else:
            st.error("Failed to load model details")
    
    # Download status
    st.subheader("📁 Downloads")
    download_dir = Path("downloads/civitai")
    
    if download_dir.exists():
        downloaded_files = list(download_dir.glob("*"))
        
        if downloaded_files:
            st.write(f"**Downloaded Files ({len(downloaded_files)}):**")
            
            for file_path in downloaded_files:
                file_size = file_path.stat().st_size
                size_mb = file_size / (1024 * 1024)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(f"📄 {file_path.name}")
                
                with col2:
                    st.text(f"{size_mb:.1f} MB")
                
                with col3:
                    if st.button(f"🗑️", key=f"delete_{file_path.name}"):
                        file_path.unlink()
                        st.rerun()
        else:
            st.info("No files downloaded yet")
    else:
        st.info("Download directory not created yet")

if __name__ == "__main__":
    main()