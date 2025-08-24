#!/usr/bin/env python3
"""
Dark Mode Pro Theme Engine
Comprehensive theming system for all interfaces
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DarkProThemeEngine:
    """Dark Mode Pro theme engine for consistent styling"""
    
    # Core color palette
    COLORS = {
        'primary': '#111827',      # Deep black
        'accent': '#10B981',       # Electric green
        'text': '#6B7280',         # Cool gray
        'surface': '#1F2937',      # Elevated surfaces
        'border': '#374151',       # Subtle borders
        'success': '#10B981',      # Green
        'warning': '#F59E0B',      # Amber
        'error': '#EF4444',        # Red
        'info': '#3B82F6',         # Blue
        'text_primary': '#F3F4F6',
        'text_secondary': '#9CA3AF',
        'hover': '#374151',
        'active': '#4B5563'
    }
    
    # Gradients
    GRADIENTS = {
        'primary': 'linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%)',
        'accent': 'linear-gradient(90deg, #10B981 0%, #059669 100%)',
        'dark': 'linear-gradient(180deg, #111827 0%, #1F2937 100%)',
        'surface': 'linear-gradient(135deg, #1F2937 0%, #374151 100%)'
    }
    
    # Typography
    TYPOGRAPHY = {
        'font_header': "'Roboto', sans-serif",
        'font_body': "'Roboto', sans-serif",
        'font_code': "'Fira Code', monospace",
        'size_xs': '0.75rem',
        'size_sm': '0.875rem',
        'size_base': '1rem',
        'size_lg': '1.125rem',
        'size_xl': '1.25rem',
        'size_2xl': '1.5rem',
        'size_3xl': '1.875rem',
        'weight_normal': '400',
        'weight_medium': '500',
        'weight_semibold': '600',
        'weight_bold': '700'
    }
    
    # Spacing
    SPACING = {
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
        '3xl': '4rem'
    }
    
    # Animations
    ANIMATIONS = {
        'transition_fast': '0.15s ease-in-out',
        'transition_normal': '0.3s ease-in-out',
        'transition_slow': '0.5s ease-in-out',
        'hover_scale': 'scale(1.02)',
        'active_scale': 'scale(0.98)'
    }
    
    def __init__(self):
        self.custom_colors = {}
        self.theme_config = self._create_theme_config()
    
    def _create_theme_config(self) -> Dict[str, Any]:
        """Create comprehensive theme configuration"""
        return {
            'colors': self.COLORS,
            'gradients': self.GRADIENTS,
            'typography': self.TYPOGRAPHY,
            'spacing': self.SPACING,
            'animations': self.ANIMATIONS,
            'shadows': {
                'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                'glow': '0 0 20px rgba(16, 185, 129, 0.3)'
            },
            'borders': {
                'radius_sm': '0.25rem',
                'radius_md': '0.5rem',
                'radius_lg': '0.75rem',
                'radius_xl': '1rem',
                'width': '1px'
            }
        }
    
    def get_css_variables(self) -> str:
        """Generate CSS custom properties"""
        css = ":root {\n"
        
        # Colors
        for key, value in self.COLORS.items():
            css += f"  --darkpro-{key}: {value};\n"
        
        # Gradients
        for key, value in self.GRADIENTS.items():
            css += f"  --darkpro-gradient-{key}: {value};\n"
        
        # Typography
        for key, value in self.TYPOGRAPHY.items():
            css += f"  --darkpro-{key.replace('_', '-')}: {value};\n"
        
        # Spacing
        for key, value in self.SPACING.items():
            css += f"  --darkpro-spacing-{key}: {value};\n"
        
        # Animations
        for key, value in self.ANIMATIONS.items():
            css += f"  --darkpro-{key.replace('_', '-')}: {value};\n"
        
        css += "}\n"
        return css
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit theme configuration"""
        return {
            'primaryColor': self.COLORS['accent'],
            'backgroundColor': self.COLORS['primary'],
            'secondaryBackgroundColor': self.COLORS['surface'],
            'textColor': self.COLORS['text'],
            'font': 'sans serif'
        }
    
    def get_streamlit_css(self) -> str:
        """Get complete Streamlit CSS"""
        return f"""
        {self.get_css_variables()}
        
        /* Streamlit Dark Mode Pro Theme */
        .stApp {{
            background: var(--darkpro-primary);
            color: var(--darkpro-text);
            font-family: var(--darkpro-font-body);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: var(--darkpro-gradient-primary);
            color: white;
            border: none;
            border-radius: var(--darkpro-radius-md);
            padding: var(--darkpro-spacing-sm) var(--darkpro-spacing-md);
            font-weight: var(--darkpro-weight-semibold);
            transition: var(--darkpro-transition-normal);
        }}
        
        .stButton > button:hover {{
            transform: var(--darkpro-hover-scale);
            box-shadow: var(--darkpro-shadow-glow);
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {{
            background: var(--darkpro-surface);
            border: 1px solid var(--darkpro-border);
            color: var(--darkpro-text);
            border-radius: var(--darkpro-radius-md);
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background: var(--darkpro-surface);
        }}
        
        /* Metrics */
        [data-testid="metric-container"] {{
            background: var(--darkpro-surface);
            border: 1px solid var(--darkpro-border);
            border-radius: var(--darkpro-radius-lg);
            padding: var(--darkpro-spacing-md);
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: var(--darkpro-surface);
            border: 1px solid var(--darkpro-border);
            border-radius: var(--darkpro-radius-md);
        }}
        
        /* Code blocks */
        .stCodeBlock {{
            background: var(--darkpro-surface);
            border: 1px solid var(--darkpro-border);
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--darkpro-surface);
            border-radius: var(--darkpro-radius-md);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: var(--darkpro-text);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--darkpro-accent);
            color: white;
        }}
        """
    
    def get_gradio_theme(self):
        """Get Gradio theme object"""
        try:
            import gradio as gr
            
            return gr.themes.Base().set(
                body_background_fill=self.COLORS['primary'],
                body_text_color=self.COLORS['text'],
                button_primary_background_fill=self.COLORS['accent'],
                button_primary_background_fill_hover=self.COLORS['success'],
                button_primary_text_color='white',
                block_background_fill=self.COLORS['surface'],
                block_border_color=self.COLORS['border'],
                block_border_width='1px',
                block_title_text_color=self.COLORS['accent'],
                block_title_text_weight='600',
                input_background_fill=self.COLORS['surface'],
                input_border_color=self.COLORS['border'],
                input_text_color=self.COLORS['text'],
                panel_background_fill=self.COLORS['surface'],
                panel_border_color=self.COLORS['border'],
                section_header_text_color=self.COLORS['accent'],
                section_header_text_weight='700'
            )
        except ImportError:
            logger.warning("Gradio not available for theme generation")
            return None
    
    def get_gradio_css(self) -> str:
        """Get Gradio custom CSS"""
        return f"""
        {self.get_css_variables()}
        
        /* Gradio Dark Mode Pro Theme */
        .gradio-container {{
            background: var(--darkpro-primary) !important;
            color: var(--darkpro-text) !important;
            font-family: var(--darkpro-font-body) !important;
        }}
        
        .gr-button-primary {{
            background: var(--darkpro-gradient-accent) !important;
            border: none !important;
            color: white !important;
            font-weight: var(--darkpro-weight-semibold) !important;
        }}
        
        .gr-button-primary:hover {{
            transform: var(--darkpro-hover-scale) !important;
            box-shadow: var(--darkpro-shadow-glow) !important;
        }}
        
        .gr-input, .gr-dropdown {{
            background: var(--darkpro-surface) !important;
            border: 1px solid var(--darkpro-border) !important;
            color: var(--darkpro-text) !important;
        }}
        
        .gr-panel {{
            background: var(--darkpro-surface) !important;
            border: 1px solid var(--darkpro-border) !important;
            border-radius: var(--darkpro-radius-lg) !important;
        }}
        
        .gr-box {{
            background: var(--darkpro-surface) !important;
            border-color: var(--darkpro-border) !important;
        }}
        
        .gr-check-radio {{
            background: var(--darkpro-surface) !important;
        }}
        
        .gr-check-radio:checked {{
            background: var(--darkpro-accent) !important;
        }}
        """
    
    def save_theme_config(self, path: Path):
        """Save theme configuration to file"""
        config_file = path / 'darkpro_theme.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(self.theme_config, f, indent=2)
        
        logger.info(f"Theme configuration saved to {config_file}")
    
    def load_custom_theme(self, config_path: Path) -> bool:
        """Load custom theme configuration"""
        if not config_path.exists():
            logger.warning(f"Theme config not found: {config_path}")
            return False
        
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
            
            # Merge custom config with default
            if 'colors' in custom_config:
                self.COLORS.update(custom_config['colors'])
            if 'gradients' in custom_config:
                self.GRADIENTS.update(custom_config['gradients'])
            if 'typography' in custom_config:
                self.TYPOGRAPHY.update(custom_config['typography'])
            
            self.theme_config = self._create_theme_config()
            logger.info("Custom theme loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load custom theme: {e}")
            return False
    
    def get_component_style(self, component: str) -> Dict[str, str]:
        """Get style for specific component"""
        styles = {
            'card': {
                'background': self.COLORS['surface'],
                'border': f"1px solid {self.COLORS['border']}",
                'border-radius': '0.75rem',
                'padding': '1rem',
                'box-shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            },
            'button': {
                'background': self.GRADIENTS['accent'],
                'color': 'white',
                'border': 'none',
                'border-radius': '0.5rem',
                'padding': '0.5rem 1rem',
                'font-weight': '600',
                'cursor': 'pointer',
                'transition': self.ANIMATIONS['transition_normal']
            },
            'input': {
                'background': self.COLORS['surface'],
                'border': f"1px solid {self.COLORS['border']}",
                'color': self.COLORS['text'],
                'border-radius': '0.5rem',
                'padding': '0.5rem',
                'width': '100%'
            },
            'badge': {
                'background': self.COLORS['accent'],
                'color': 'white',
                'padding': '0.25rem 0.5rem',
                'border-radius': '0.25rem',
                'font-size': '0.875rem',
                'font-weight': '500'
            }
        }
        
        return styles.get(component, {})