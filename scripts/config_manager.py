#!/usr/bin/env python3
"""
Configuration Manager for SD-DarkMaster-Pro Unified
Handles saving/loading of UI settings, API keys, and preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

class ConfigManager:
    """Manages configuration for SD-DarkMaster-Pro"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize config manager"""
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent / "configs"
        else:
            self.config_dir = config_dir
            
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "unified_config.json"
        
        # Default configuration
        self.default_config = {
            "ui_settings": {
                "selected_webui": "Forge",
                "auto_update_webui": True,
                "auto_update_extensions": True,
                "verbose_downloads": False,
                "gpu_optimization": True
            },
            "api_keys": {
                "huggingface_token": "",
                "civitai_api_key": "",
                "ngrok_auth_token": ""
            },
            "launch_args": {
                "default_args": "--xformers --medvram",
                "forge_args": "--xformers",
                "a1111_args": "--medvram --xformers",
                "comfyui_args": "--auto-launch",
                "custom_args": ""
            },
            "paths": {
                "models_dir": "storage/models",
                "loras_dir": "storage/loras", 
                "vae_dir": "storage/vae",
                "controlnet_dir": "storage/controlnet",
                "webuis_dir": "webuis"
            },
            "download_settings": {
                "concurrent_downloads": 3,
                "retry_attempts": 3,
                "chunk_size": "1M",
                "use_aria2c": True
            },
            "model_selections": {
                "selected_sd15": [],
                "selected_sdxl": [],
                "selected_loras": [],
                "selected_vae": [],
                "selected_controlnet": []
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Merge with defaults to ensure all keys exist
                merged_config = self._merge_configs(self.default_config, config)
                return merged_config
            else:
                # Create default config file
                self.save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge configurations"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def update_from_session_state(self) -> bool:
        """Update config from Streamlit session state"""
        try:
            config = self.load_config()
            
            # Update UI settings from session state
            if hasattr(st.session_state, 'webui_selector'):
                config['ui_settings']['selected_webui'] = st.session_state.webui_selector
                
            if hasattr(st.session_state, 'auto_update_webui'):
                config['ui_settings']['auto_update_webui'] = st.session_state.auto_update_webui
                
            if hasattr(st.session_state, 'auto_update_extensions'):
                config['ui_settings']['auto_update_extensions'] = st.session_state.auto_update_extensions
                
            if hasattr(st.session_state, 'verbose_downloads'):
                config['ui_settings']['verbose_downloads'] = st.session_state.verbose_downloads
                
            if hasattr(st.session_state, 'gpu_optimization'):
                config['ui_settings']['gpu_optimization'] = st.session_state.gpu_optimization
            
            # Update model selections
            if hasattr(st.session_state, 'selected_models'):
                config['model_selections']['selected_models'] = st.session_state.selected_models
            
            return self.save_config(config)
            
        except Exception as e:
            print(f"Error updating config from session state: {e}")
            return False
    
    def load_to_session_state(self) -> bool:
        """Load config to Streamlit session state"""
        try:
            config = self.load_config()
            
            # Load UI settings to session state
            ui_settings = config.get('ui_settings', {})
            for key, value in ui_settings.items():
                if f"config_{key}" not in st.session_state:
                    st.session_state[f"config_{key}"] = value
            
            # Load model selections
            model_selections = config.get('model_selections', {})
            if 'selected_models' not in st.session_state:
                st.session_state.selected_models = model_selections.get('selected_models', [])
            
            return True
            
        except Exception as e:
            print(f"Error loading config to session state: {e}")
            return False
    
    def get_launch_args(self, webui_type: str) -> str:
        """Get launch arguments for specific WebUI"""
        config = self.load_config()
        launch_args = config.get('launch_args', {})
        
        webui_key = f"{webui_type.lower()}_args"
        if webui_key in launch_args:
            return launch_args[webui_key]
        else:
            return launch_args.get('default_args', '--xformers')
    
    def get_api_key(self, service: str) -> str:
        """Get API key for service"""
        config = self.load_config()
        api_keys = config.get('api_keys', {})
        return api_keys.get(f"{service}_api_key", "")
    
    def set_api_key(self, service: str, key: str) -> bool:
        """Set API key for service"""
        config = self.load_config()
        if 'api_keys' not in config:
            config['api_keys'] = {}
        config['api_keys'][f"{service}_api_key"] = key
        return self.save_config(config)
    
    def export_config(self) -> str:
        """Export configuration as JSON string"""
        config = self.load_config()
        return json.dumps(config, indent=2)
    
    def import_config(self, config_json: str) -> bool:
        """Import configuration from JSON string"""
        try:
            config = json.loads(config_json)
            return self.save_config(config)
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

# Global config manager instance
config_manager = ConfigManager()