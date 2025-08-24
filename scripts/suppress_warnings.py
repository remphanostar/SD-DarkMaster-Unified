"""
Utility to suppress Streamlit warnings when running from notebooks
"""

import os
import warnings
import logging
import sys
from contextlib import contextmanager

def suppress_streamlit_warnings():
    """Suppress all Streamlit warnings when running from notebook"""
    # General warnings
    warnings.filterwarnings('ignore')
    
    # Environment variables
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Logging suppression
    try:
        # Suppress specific Streamlit loggers
        loggers = [
            'streamlit.runtime.scriptrunner_utils.script_run_context',
            'streamlit.runtime.state.session_state_proxy',
            'streamlit.runtime.scriptrunner',
            'streamlit.runtime.caching',
            'streamlit.runtime.legacy_caching',
            'streamlit.runtime.stats',
            'streamlit.config',
            'streamlit.watcher.path_watcher',
            'streamlit.delta_generator',
            'streamlit'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.ERROR)
            logger.disabled = True
    except:
        pass
    
    # Redirect stderr to suppress print warnings
    class SuppressStreamlitOutput:
        def write(self, msg):
            # Only suppress Streamlit-specific warnings
            if 'ScriptRunContext' not in msg and 'streamlit' not in msg.lower():
                sys.__stderr__.write(msg)
        
        def flush(self):
            pass
    
    # Only redirect if we're in a notebook environment
    if 'ipykernel' in sys.modules or 'google.colab' in sys.modules:
        sys.stderr = SuppressStreamlitOutput()

@contextmanager
def quiet_streamlit():
    """Context manager to temporarily suppress Streamlit output"""
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr

# Auto-suppress when imported
suppress_streamlit_warnings()