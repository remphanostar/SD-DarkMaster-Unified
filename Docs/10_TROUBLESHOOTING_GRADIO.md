# Gradio Link Stability Guide for SD-DarkMaster-Pro

## Overview
This guide provides comprehensive solutions for ensuring stable Gradio links in multi-platform environments, particularly for Google Colab, Kaggle, and cloud platforms where link stability is critical for WebUI access.

## Common Gradio Link Issues

### 1. Link Expiration
**Problem**: Gradio links expire after a certain time period
**Impact**: Users lose access to WebUI interface
**Solution**: Implement persistent link generation with automatic refresh

### 2. Platform-Specific Issues
**Problem**: Different platforms handle Gradio differently
**Impact**: Inconsistent behavior across Colab/Kaggle/Cloud
**Solution**: Platform-specific configuration and fallback systems

### 3. Port Conflicts
**Problem**: Multiple WebUIs trying to use same port
**Impact**: Launch failures and connection errors
**Solution**: Dynamic port allocation and conflict resolution

## Implementation Solutions

### 1. Persistent Link Generation

```python
import gradio as gr
import threading
import time
import requests
from pathlib import Path

class StableGradioLauncher:
    def __init__(self):
        self.current_port = None
        self.current_link = None
        self.link_thread = None
        
    def launch_with_stable_link(self, webui_path, port=None):
        """Launch WebUI with stable link generation"""
        
        # Dynamic port allocation
        if port is None:
            port = self.find_available_port()
        
        # Launch WebUI
        webui_process = self.launch_webui(webui_path, port)
        
        # Generate stable link
        stable_link = self.generate_stable_link(port)
        
        # Start link monitoring
        self.start_link_monitoring(port, stable_link)
        
        return stable_link, webui_process
    
    def find_available_port(self, start_port=7860):
        """Find available port starting from start_port"""
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    def generate_stable_link(self, port):
        """Generate stable public link using ngrok or similar"""
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(port)
            return public_url
        except Exception as e:
            # Fallback to local link
            return f"http://localhost:{port}"
    
    def start_link_monitoring(self, port, link):
        """Monitor link health and regenerate if needed"""
        def monitor():
            while True:
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=5)
                    if response.status_code != 200:
                        # Regenerate link
                        new_link = self.generate_stable_link(port)
                        print(f"Link regenerated: {new_link}")
                except:
                    # Link is down, attempt to restart
                    print("Link down, attempting restart...")
                    self.restart_webui(port)
                time.sleep(30)  # Check every 30 seconds
        
        self.link_thread = threading.Thread(target=monitor, daemon=True)
        self.link_thread.start()
```

### 2. Platform-Specific Configuration

```python
import sys
import os

def get_platform_gradio_config():
    """Get platform-specific Gradio configuration"""
    
    if 'google.colab' in sys.modules:
        # Colab-specific settings
        return {
            'server_name': '0.0.0.0',
            'server_port': 7860,
            'share': True,  # Use Gradio's built-in sharing
            'inbrowser': False,
            'quiet': False,
            'show_error': True,
            'enable_queue': True,
            'max_threads': 40
        }
    
    elif os.path.exists('/kaggle'):
        # Kaggle-specific settings
        return {
            'server_name': '0.0.0.0',
            'server_port': 7860,
            'share': False,  # Kaggle handles sharing
            'inbrowser': False,
            'quiet': False,
            'show_error': True,
            'enable_queue': True,
            'max_threads': 20
        }
    
    elif os.path.exists('/workspace'):
        # Workspace/Cloud settings
        return {
            'server_name': '0.0.0.0',
            'server_port': 7860,
            'share': True,
            'inbrowser': False,
            'quiet': False,
            'show_error': True,
            'enable_queue': True,
            'max_threads': 30
        }
    
    else:
        # Local development
        return {
            'server_name': '127.0.0.1',
            'server_port': 7860,
            'share': False,
            'inbrowser': True,
            'quiet': False,
            'show_error': True,
            'enable_queue': True,
            'max_threads': 10
        }
```

### 3. Multi-Tunnel System

```python
import subprocess

class MultiTunnelSystem:
    """Multiple tunnel options for maximum link stability"""
    
    def __init__(self):
        self.tunnels = []
        self.current_tunnel = None
        
    def create_tunnels(self, port):
        """Create multiple tunnel options"""
        
        tunnels = []
        
        # Option 1: ngrok
        try:
            from pyngrok import ngrok
            ngrok_url = ngrok.connect(port)
            tunnels.append(('ngrok', ngrok_url))
        except Exception as e:
            print(f"ngrok failed: {e}")
        
        # Option 2: localtunnel
        try:
            import subprocess
            result = subprocess.run([
                'npx', 'localtunnel', '--port', str(port)
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lt_url = result.stdout.strip()
                tunnels.append(('localtunnel', lt_url))
        except Exception as e:
            print(f"localtunnel failed: {e}")
        
        # Option 3: serveo
        try:
            import subprocess
            result = subprocess.run([
                'ssh', '-o', 'StrictHostKeyChecking=no', 
                '-R', f'80:localhost:{port}', 'serveo.net'
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                serveo_url = f"https://{result.stdout.strip()}"
                tunnels.append(('serveo', serveo_url))
        except Exception as e:
            print(f"serveo failed: {e}")
        
        self.tunnels = tunnels
        return tunnels
    
    def get_best_tunnel(self):
        """Get the most stable tunnel"""
        if not self.tunnels:
            return None
        
        # Test each tunnel
        for name, url in self.tunnels:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.current_tunnel = (name, url)
                    return url
            except:
                continue
        
        # Fallback to first available
        if self.tunnels:
            return self.tunnels[0][1]
        
        return None
```

### 4. Link Health Monitoring

```python
import threading
import time
import requests

class LinkHealthMonitor:
    """Monitor and maintain link health"""
    
    def __init__(self):
        self.health_checks = []
        self.auto_restart = True
        
    def add_health_check(self, url, check_interval=30):
        """Add a URL to monitor"""
        self.health_checks.append({
            'url': url,
            'interval': check_interval,
            'last_check': time.time(),
            'status': 'unknown'
        })
    
    def start_monitoring(self):
        """Start health monitoring"""
        def monitor():
            while True:
                for check in self.health_checks:
                    if time.time() - check['last_check'] >= check['interval']:
                        self.check_url_health(check)
                time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def check_url_health(self, check):
        """Check if a URL is healthy"""
        try:
            response = requests.get(check['url'], timeout=10)
            check['status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            check['status'] = 'unhealthy'
        
        check['last_check'] = time.time()
        
        # Auto-restart if unhealthy
        if check['status'] == 'unhealthy' and self.auto_restart:
            self.restart_webui()
    
    def restart_webui(self):
        """Restart WebUI if link becomes unhealthy"""
        print("Link unhealthy, restarting WebUI...")
        # Implementation depends on WebUI type
        pass
```

## Integration with SD-DarkMaster-Pro

### 1. Launch Script Integration

```python
# In launch.py
def launch_webui_with_stable_links(webui_type, config):
    """Launch WebUI with stable link generation"""
    
    # Initialize stable launcher
    launcher = StableGradioLauncher()
    
    # Get platform-specific config
    gradio_config = get_platform_gradio_config()
    
    # Launch with stable links
    stable_link, process = launcher.launch_with_stable_link(
        webui_path=config['webui_path'],
        port=gradio_config['server_port']
    )
    
    # Initialize health monitoring
    monitor = LinkHealthMonitor()
    monitor.add_health_check(stable_link)
    monitor.start_monitoring()
    
    return {
        'link': stable_link,
        'process': process,
        'monitor': monitor
    }
```

### 2. User Interface Integration

```python
# In widgets-en.py
def display_stable_links(links_info):
    """Display stable links in the UI"""
    
    st.subheader("🌐 Stable WebUI Links")
    
    for webui_name, info in links_info.items():
        with st.expander(f"{webui_name} Links"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Primary Link:** {info['link']}")
                if info.get('backup_link'):
                    st.markdown(f"**Backup Link:** {info['backup_link']}")
                
                # Link status indicator
                status = "🟢 Healthy" if info.get('status') == 'healthy' else "🔴 Unhealthy"
                st.markdown(f"**Status:** {status}")
            
            with col2:
                if st.button(f"Copy {webui_name} Link"):
                    st.write("Link copied to clipboard!")
                
                if st.button(f"Test {webui_name} Link"):
                    # Test link health
                    pass
```

## Best Practices

### 1. Always Use Multiple Tunnel Options
- Primary: ngrok (most reliable)
- Backup: localtunnel or serveo
- Fallback: Local access

### 2. Implement Health Monitoring
- Regular health checks (every 30 seconds)
- Automatic restart on failure
- User notification of link status

### 3. Platform-Specific Optimization
- Colab: Use Gradio's built-in sharing
- Kaggle: Leverage Kaggle's proxy system
- Cloud: Use ngrok with authentication

### 4. User Experience
- Display multiple link options
- Show link health status
- Provide copy-to-clipboard functionality
- Auto-refresh links when needed

## Troubleshooting

### Common Issues and Solutions

1. **Link Expires Quickly**
   - Solution: Implement automatic link regeneration
   - Use multiple tunnel providers

2. **Port Already in Use**
   - Solution: Dynamic port allocation
   - Kill conflicting processes

3. **Platform-Specific Failures**
   - Solution: Platform-specific configurations
   - Fallback mechanisms

4. **Slow Link Generation**
   - Solution: Pre-warm tunnel connections
   - Cache successful configurations

This guide ensures maximum link stability across all platforms while providing users with reliable access to their WebUI interfaces.
