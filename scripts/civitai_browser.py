#!/usr/bin/env python3
"""
CivitAI Browser Integration
Real working browser with search, preview, and download
"""

import requests
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import time

class CivitAIBrowser:
    """Browse and download models from CivitAI"""
    
    def __init__(self):
        self.api_base = "https://civitai.com/api/v1"
        self.storage_root = Path('/workspace/SD-DarkMaster-Pro/storage')
        self.models_dir = self.storage_root / 'models'
        self.cache_file = Path('/workspace/SD-DarkMaster-Pro/configs/civitai_cache.json')
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load cache
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load search cache"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {'searches': {}, 'models': {}}
    
    def _save_cache(self):
        """Save search cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def search_models(
        self,
        query: str = "",
        types: Optional[List[str]] = None,
        sort: str = "Most Downloaded",
        period: str = "AllTime",
        nsfw: bool = False,
        limit: int = 20
    ) -> List[Dict]:
        """Search CivitAI for models"""
        
        # Build cache key
        cache_key = f"{query}_{types}_{sort}_{period}_{nsfw}_{limit}"
        
        # Check cache (5 minute expiry)
        if cache_key in self.cache['searches']:
            cached = self.cache['searches'][cache_key]
            if time.time() - cached['timestamp'] < 300:  # 5 minutes
                return cached['results']
        
        # Build API parameters
        params = {
            'limit': limit,
            'sort': self._convert_sort(sort),
            'period': period,
            'nsfw': 'true' if nsfw else 'false'
        }
        
        if query:
            params['query'] = query
        
        if types:
            params['types'] = ','.join(types)
        
        try:
            # Make API request
            response = requests.get(
                f"{self.api_base}/models",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for item in data.get('items', []):
                    model_info = self._parse_model_info(item)
                    models.append(model_info)
                    
                    # Cache individual model info
                    self.cache['models'][str(item['id'])] = model_info
                
                # Cache search results
                self.cache['searches'][cache_key] = {
                    'results': models,
                    'timestamp': time.time()
                }
                self._save_cache()
                
                return models
            else:
                print(f"API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _convert_sort(self, sort: str) -> str:
        """Convert UI sort to API sort"""
        mapping = {
            "Most Downloaded": "Most Downloaded",
            "Highest Rated": "Highest Rated",
            "Most Recent": "Newest",
            "Most Liked": "Most Liked"
        }
        return mapping.get(sort, "Most Downloaded")
    
    def _parse_model_info(self, item: Dict) -> Dict:
        """Parse model info from API response"""
        # Get the first model version (usually the latest)
        version = item.get('modelVersions', [{}])[0]
        
        # Get download URL and size
        files = version.get('files', [])
        primary_file = files[0] if files else {}
        
        return {
            'id': item.get('id'),
            'name': item.get('name', 'Unknown'),
            'type': item.get('type', 'Checkpoint'),
            'nsfw': item.get('nsfw', False),
            'tags': item.get('tags', []),
            'creator': item.get('creator', {}).get('username', 'Unknown'),
            'description': item.get('description', ''),
            'download_count': item.get('stats', {}).get('downloadCount', 0),
            'rating': item.get('stats', {}).get('rating', 0),
            'version': {
                'id': version.get('id'),
                'name': version.get('name', 'v1.0'),
                'base_model': version.get('baseModel', 'SD 1.5'),
                'download_url': primary_file.get('downloadUrl', ''),
                'size_kb': primary_file.get('sizeKB', 0),
                'format': primary_file.get('format', 'SafeTensor'),
                'fp': primary_file.get('fp', 'fp16'),
                'hashes': primary_file.get('hashes', {}),
                'images': version.get('images', [])
            }
        }
    
    def download_model(
        self,
        model_info: Dict,
        destination: Optional[Path] = None,
        use_aria2: bool = True
    ) -> bool:
        """Download a model from CivitAI"""
        
        # Determine destination
        if destination is None:
            model_type = model_info.get('type', 'Checkpoint')
            
            if model_type == 'Checkpoint':
                destination = self.models_dir / 'Stable-diffusion'
            elif model_type == 'LORA':
                destination = self.models_dir / 'Lora'
            elif model_type == 'TextualInversion':
                destination = self.models_dir / 'embeddings'
            elif model_type == 'VAE':
                destination = self.models_dir / 'VAE'
            elif model_type == 'Controlnet':
                destination = self.models_dir / 'ControlNet'
            else:
                destination = self.models_dir / 'Other'
        
        destination.mkdir(parents=True, exist_ok=True)
        
        # Get download info
        download_url = model_info['version']['download_url']
        if not download_url:
            print("No download URL available")
            return False
        
        # Generate filename
        model_name = model_info['name'].replace('/', '_').replace('\\', '_')
        version_name = model_info['version']['name']
        format_ext = '.safetensors' if model_info['version']['format'] == 'SafeTensor' else '.ckpt'
        filename = f"{model_name}_{version_name}{format_ext}"
        filepath = destination / filename
        
        # Check if already exists
        if filepath.exists():
            print(f"Model already exists: {filepath}")
            return True
        
        print(f"Downloading {model_name} to {filepath}...")
        
        if use_aria2 and self._check_aria2():
            # Use aria2 for faster downloads
            return self._download_with_aria2(download_url, filepath)
        else:
            # Fallback to requests
            return self._download_with_requests(download_url, filepath)
    
    def _check_aria2(self) -> bool:
        """Check if aria2 is available"""
        try:
            subprocess.run(['aria2c', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _download_with_aria2(self, url: str, filepath: Path) -> bool:
        """Download using aria2 with 16 connections"""
        try:
            cmd = [
                'aria2c',
                '-x', '16',  # 16 connections
                '-s', '16',  # 16 splits
                '--file-allocation=none',
                '--console-log-level=error',
                '--summary-interval=10',
                '-d', str(filepath.parent),
                '-o', filepath.name,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Downloaded successfully: {filepath.name}")
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Aria2 error: {e}")
            return False
    
    def _download_with_requests(self, url: str, filepath: Path) -> bool:
        """Download using requests with progress bar"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Progress: {progress:.1f}%", end='\r')
            
            print(f"\n✅ Downloaded: {filepath.name}")
            return True
            
        except Exception as e:
            print(f"Download error: {e}")
            if filepath.exists():
                filepath.unlink()  # Remove partial download
            return False
    
    def get_model_preview(self, model_id: str) -> Optional[Dict]:
        """Get detailed info and preview images for a model"""
        
        # Check cache first
        if model_id in self.cache['models']:
            return self.cache['models'][model_id]
        
        try:
            response = requests.get(
                f"{self.api_base}/models/{model_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                model_info = self._parse_model_info(data)
                
                # Cache it
                self.cache['models'][model_id] = model_info
                self._save_cache()
                
                return model_info
            
        except Exception as e:
            print(f"Error getting model preview: {e}")
        
        return None
    
    def get_trending_models(self, period: str = "Day", limit: int = 10) -> List[Dict]:
        """Get trending models"""
        return self.search_models(
            query="",
            sort="Most Downloaded",
            period=period,
            limit=limit
        )

# Singleton instance
_browser = None

def get_civitai_browser() -> CivitAIBrowser:
    """Get or create the singleton browser"""
    global _browser
    if _browser is None:
        _browser = CivitAIBrowser()
    return _browser

if __name__ == "__main__":
    # Test the browser
    browser = get_civitai_browser()
    
    print("🔍 Testing CivitAI Browser")
    print("="*50)
    
    # Search for models
    print("\nSearching for 'anime' models...")
    results = browser.search_models(
        query="anime",
        types=["Checkpoint"],
        limit=5
    )
    
    for model in results:
        print(f"\n📦 {model['name']}")
        print(f"   Type: {model['type']}")
        print(f"   Base: {model['version']['base_model']}")
        print(f"   Size: {model['version']['size_kb'] / 1024:.1f} MB")
        print(f"   Downloads: {model['download_count']:,}")
    
    # Get trending
    print("\n🔥 Trending Today")
    print("="*50)
    trending = browser.get_trending_models(period="Day", limit=3)
    
    for model in trending:
        print(f"• {model['name']} ({model['type']})")
        print(f"  Downloads: {model['download_count']:,}")