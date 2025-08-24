#!/usr/bin/env python3
"""
Unified Storage Manager Module
Handles all storage operations and path management across WebUIs
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class UnifiedStorageManager:
    """Universal storage management with symbolic links"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/workspace/SD-DarkMaster-Pro")
        self.storage_root = self.project_root / "storage"
        
        # Define storage structure
        self.storage_paths = {
            'models': {
                'checkpoints': self.storage_root / 'models' / 'Stable-diffusion',
                'vae': self.storage_root / 'models' / 'VAE',
                'lora': self.storage_root / 'models' / 'Lora',
                'lycoris': self.storage_root / 'models' / 'LyCORIS',
                'embeddings': self.storage_root / 'embeddings',
                'hypernetworks': self.storage_root / 'models' / 'hypernetworks',
                'controlnet': self.storage_root / 'models' / 'ControlNet',
                'upscalers': self.storage_root / 'models' / 'ESRGAN',
                'clip': self.storage_root / 'models' / 'CLIP',
                'clip_vision': self.storage_root / 'models' / 'CLIP_vision',
                'diffusers': self.storage_root / 'models' / 'diffusers'
            },
            'outputs': {
                'txt2img': self.storage_root / 'outputs' / 'txt2img-images',
                'img2img': self.storage_root / 'outputs' / 'img2img-images',
                'extras': self.storage_root / 'outputs' / 'extras-images',
                'grids': self.storage_root / 'outputs' / 'txt2img-grids',
                'samples': self.storage_root / 'outputs' / 'samples',
                'temp': self.storage_root / 'outputs' / 'temp'
            },
            'cache': {
                'huggingface': self.storage_root / 'cache' / 'huggingface',
                'clip': self.storage_root / 'cache' / 'clip',
                'torch': self.storage_root / 'cache' / 'torch',
                'transformers': self.storage_root / 'cache' / 'transformers'
            },
            'configs': {
                'webui': self.storage_root / 'configs' / 'webui',
                'models': self.storage_root / 'configs' / 'models',
                'presets': self.storage_root / 'configs' / 'presets'
            }
        }
        
        self.webui_mappings = {
            'A1111': {
                'models': 'models',
                'outputs': 'outputs',
                'embeddings': 'embeddings',
                'extensions': 'extensions'
            },
            'ComfyUI': {
                'models': 'models',
                'output': 'output',
                'input': 'input',
                'custom_nodes': 'custom_nodes'
            },
            'Forge': {
                'models': 'models',
                'outputs': 'outputs',
                'embeddings': 'embeddings',
                'extensions': 'extensions'
            }
        }
        
    def initialize_storage(self) -> bool:
        """Initialize unified storage structure"""
        try:
            logger.info("Initializing unified storage structure...")
            
            # Create all storage directories
            for category, paths in self.storage_paths.items():
                if isinstance(paths, dict):
                    for name, path in paths.items():
                        path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created {category}/{name}: {path}")
                else:
                    paths.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created {category}: {paths}")
            
            # Create metadata file
            self._create_storage_metadata()
            
            # Set environment variables for cache directories
            os.environ['HF_HOME'] = str(self.storage_paths['cache']['huggingface'])
            os.environ['TORCH_HOME'] = str(self.storage_paths['cache']['torch'])
            os.environ['TRANSFORMERS_CACHE'] = str(self.storage_paths['cache']['transformers'])
            
            logger.info("✅ Unified storage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            return False
    
    def _create_storage_metadata(self):
        """Create metadata file for storage tracking"""
        metadata = {
            'version': '1.0.0',
            'created': os.path.getmtime(self.storage_root) if self.storage_root.exists() else None,
            'structure': {
                category: {
                    name: str(path) for name, path in paths.items()
                } if isinstance(paths, dict) else str(paths)
                for category, paths in self.storage_paths.items()
            }
        }
        
        metadata_file = self.storage_root / 'storage_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def link_webui_storage(self, webui_path: Path, webui_type: str = 'A1111') -> bool:
        """Create symbolic links for WebUI compatibility"""
        try:
            logger.info(f"Linking storage for {webui_type} at {webui_path}")
            
            if webui_type not in self.webui_mappings:
                logger.warning(f"Unknown WebUI type: {webui_type}")
                return False
            
            mappings = self.webui_mappings[webui_type]
            
            for webui_dir, storage_key in mappings.items():
                webui_target = webui_path / webui_dir
                
                # Determine source path
                if storage_key == 'models':
                    source_path = self.storage_root / 'models'
                elif storage_key in ['output', 'outputs']:
                    source_path = self.storage_root / 'outputs'
                elif storage_key == 'embeddings':
                    source_path = self.storage_paths['models']['embeddings']
                else:
                    source_path = self.storage_root / storage_key
                
                # Backup existing directory if it exists
                if webui_target.exists() and not webui_target.is_symlink():
                    backup_path = webui_path / f"{webui_dir}_backup"
                    shutil.move(str(webui_target), str(backup_path))
                    logger.info(f"Backed up {webui_target} to {backup_path}")
                
                # Remove existing symlink if present
                if webui_target.is_symlink():
                    webui_target.unlink()
                
                # Create symbolic link
                webui_target.symlink_to(source_path)
                logger.info(f"Linked {webui_target} -> {source_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to link WebUI storage: {e}")
            return False
    
    def get_storage_path(self, asset_type: str, sub_type: str = None) -> Path:
        """Get the appropriate storage path for an asset type"""
        if asset_type in self.storage_paths:
            if sub_type and isinstance(self.storage_paths[asset_type], dict):
                return self.storage_paths[asset_type].get(sub_type, self.storage_root / asset_type)
            return self.storage_paths[asset_type]
        
        # Default fallback
        return self.storage_root / asset_type
    
    def get_storage_usage(self) -> Dict[str, Dict]:
        """Get storage usage statistics"""
        usage = {}
        
        for category, paths in self.storage_paths.items():
            if isinstance(paths, dict):
                usage[category] = {}
                for name, path in paths.items():
                    if path.exists():
                        size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                        count = len(list(path.rglob('*')))
                        usage[category][name] = {
                            'size_bytes': size,
                            'size_mb': size / (1024 * 1024),
                            'size_gb': size / (1024 * 1024 * 1024),
                            'file_count': count
                        }
            else:
                if paths.exists():
                    size = sum(f.stat().st_size for f in paths.rglob('*') if f.is_file())
                    count = len(list(paths.rglob('*')))
                    usage[category] = {
                        'size_bytes': size,
                        'size_mb': size / (1024 * 1024),
                        'size_gb': size / (1024 * 1024 * 1024),
                        'file_count': count
                    }
        
        return usage
    
    def organize_downloads(self, file_path: Path, asset_type: str) -> Path:
        """Organize downloaded file into appropriate storage location"""
        # Determine destination based on file type
        if asset_type == 'checkpoint':
            dest_dir = self.storage_paths['models']['checkpoints']
        elif asset_type == 'lora':
            dest_dir = self.storage_paths['models']['lora']
        elif asset_type == 'vae':
            dest_dir = self.storage_paths['models']['vae']
        elif asset_type == 'embedding':
            dest_dir = self.storage_paths['models']['embeddings']
        elif asset_type == 'controlnet':
            dest_dir = self.storage_paths['models']['controlnet']
        else:
            dest_dir = self.storage_root / 'downloads' / asset_type
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / file_path.name
        
        # Move file to destination
        shutil.move(str(file_path), str(dest_path))
        logger.info(f"Organized {file_path.name} to {dest_path}")
        
        return dest_path
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str = None) -> bool:
        """Verify file integrity using hash"""
        if not file_path.exists():
            return False
        
        if expected_hash:
            # Calculate file hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            calculated_hash = sha256_hash.hexdigest()
            return calculated_hash == expected_hash
        
        # Basic integrity check
        return file_path.stat().st_size > 0
    
    def cleanup_duplicates(self) -> int:
        """Find and remove duplicate files"""
        duplicates = []
        hash_map = {}
        
        for category, paths in self.storage_paths.items():
            if isinstance(paths, dict):
                for name, path in paths.items():
                    if path.exists():
                        for file_path in path.rglob('*'):
                            if file_path.is_file():
                                file_hash = self._get_file_hash(file_path)
                                if file_hash in hash_map:
                                    duplicates.append(file_path)
                                else:
                                    hash_map[file_hash] = file_path
        
        # Remove duplicates
        for dup_path in duplicates:
            dup_path.unlink()
            logger.info(f"Removed duplicate: {dup_path}")
        
        return len(duplicates)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()