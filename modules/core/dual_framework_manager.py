#!/usr/bin/env python3
"""
Dual Framework Manager
Intelligent Streamlit/Gradio failover system
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import importlib.util

logger = logging.getLogger(__name__)

class DualFrameworkManager:
    """Manage dual framework (Streamlit/Gradio) with intelligent failover"""
    
    def __init__(self):
        self.primary_framework = 'streamlit'
        self.fallback_framework = 'gradio'
        self.current_framework = None
        self.framework_status = {
            'streamlit': {'available': False, 'healthy': False, 'error': None},
            'gradio': {'available': False, 'healthy': False, 'error': None}
        }
        self._check_frameworks()
    
    def _check_frameworks(self):
        """Check availability of both frameworks"""
        # Check Streamlit
        try:
            import streamlit as st
            self.framework_status['streamlit']['available'] = True
            
            # Check if Streamlit runtime is available
            if hasattr(st, 'runtime') and hasattr(st.runtime, 'exists'):
                self.framework_status['streamlit']['healthy'] = st.runtime.exists()
            else:
                # Try to detect if we're in a Streamlit environment
                self.framework_status['streamlit']['healthy'] = (
                    'streamlit' in sys.modules and
                    os.environ.get('STREAMLIT_SERVER_PORT') is not None
                )
        except ImportError as e:
            self.framework_status['streamlit']['error'] = str(e)
            logger.warning(f"Streamlit not available: {e}")
        except Exception as e:
            self.framework_status['streamlit']['error'] = str(e)
            logger.error(f"Streamlit check failed: {e}")
        
        # Check Gradio
        try:
            import gradio as gr
            self.framework_status['gradio']['available'] = True
            self.framework_status['gradio']['healthy'] = True  # Gradio is generally more reliable
        except ImportError as e:
            self.framework_status['gradio']['error'] = str(e)
            logger.warning(f"Gradio not available: {e}")
        except Exception as e:
            self.framework_status['gradio']['error'] = str(e)
            logger.error(f"Gradio check failed: {e}")
    
    def select_framework(self, prefer_primary: bool = True) -> str:
        """Select the best available framework"""
        if prefer_primary:
            # Try primary framework first
            if self.framework_status[self.primary_framework]['available']:
                if self.framework_status[self.primary_framework]['healthy']:
                    self.current_framework = self.primary_framework
                    logger.info(f"Selected primary framework: {self.primary_framework}")
                    return self.primary_framework
                else:
                    logger.warning(f"Primary framework {self.primary_framework} not healthy")
            
            # Fallback to secondary
            if self.framework_status[self.fallback_framework]['available']:
                self.current_framework = self.fallback_framework
                logger.info(f"Using fallback framework: {self.fallback_framework}")
                return self.fallback_framework
        else:
            # Prefer fallback (more stable)
            if self.framework_status[self.fallback_framework]['available']:
                self.current_framework = self.fallback_framework
                return self.fallback_framework
            
            if self.framework_status[self.primary_framework]['available']:
                self.current_framework = self.primary_framework
                return self.primary_framework
        
        # No framework available
        logger.error("No UI framework available!")
        raise RuntimeError("Neither Streamlit nor Gradio is available")
    
    def launch_interface(self, interface_func: Callable, **kwargs):
        """Launch interface with selected framework"""
        framework = self.select_framework()
        
        if framework == 'streamlit':
            return self._launch_streamlit(interface_func, **kwargs)
        else:
            return self._launch_gradio(interface_func, **kwargs)
    
    def _launch_streamlit(self, interface_func: Callable, **kwargs):
        """Launch Streamlit interface"""
        import streamlit as st
        
        # Configure Streamlit
        st.set_page_config(
            page_title=kwargs.get('title', 'SD-DarkMaster-Pro'),
            page_icon=kwargs.get('icon', '🌟'),
            layout=kwargs.get('layout', 'wide'),
            initial_sidebar_state=kwargs.get('sidebar', 'expanded')
        )
        
        # Apply Dark Mode Pro theme
        self._apply_streamlit_theme()
        
        # Run interface function
        return interface_func(framework='streamlit', **kwargs)
    
    def _launch_gradio(self, interface_func: Callable, **kwargs):
        """Launch Gradio interface"""
        import gradio as gr
        
        # Create Gradio interface
        interface = interface_func(framework='gradio', **kwargs)
        
        if isinstance(interface, gr.Blocks):
            # Apply Dark Mode Pro theme
            interface.theme = self._get_gradio_theme()
            
            # Launch
            interface.launch(
                server_name=kwargs.get('server_name', '0.0.0.0'),
                server_port=kwargs.get('server_port', 7860),
                share=kwargs.get('share', False),
                quiet=kwargs.get('quiet', False)
            )
        
        return interface
    
    def _apply_streamlit_theme(self):
        """Apply Dark Mode Pro theme to Streamlit"""
        import streamlit as st
        
        dark_css = """
        <style>
        :root {
            --darkpro-primary: #111827;
            --darkpro-accent: #10B981;
            --darkpro-text: #6B7280;
            --darkpro-surface: #1F2937;
            --darkpro-border: #374151;
        }
        
        .stApp {
            background: var(--darkpro-primary);
            color: var(--darkpro-text);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%);
            color: white;
            border: none;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)
    
    def _get_gradio_theme(self):
        """Get Dark Mode Pro theme for Gradio"""
        import gradio as gr
        
        return gr.themes.Base().set(
            body_background_fill="#111827",
            body_text_color="#6B7280",
            button_primary_background_fill="#10B981",
            button_primary_background_fill_hover="#059669",
            block_background_fill="#1F2937",
            block_border_color="#374151",
            block_title_text_color="#10B981"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get framework status"""
        return {
            'current': self.current_framework,
            'status': self.framework_status,
            'primary': self.primary_framework,
            'fallback': self.fallback_framework
        }
    
    def switch_framework(self, force_fallback: bool = False):
        """Switch to alternate framework"""
        if force_fallback or self.current_framework == self.primary_framework:
            self.current_framework = self.fallback_framework
        else:
            self.current_framework = self.primary_framework
        
        logger.info(f"Switched to {self.current_framework} framework")
        return self.current_framework