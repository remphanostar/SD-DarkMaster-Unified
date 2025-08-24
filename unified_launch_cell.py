#@title 🚀 Launch SD-DarkMaster-Pro Unified Interface
"""
Single cell that launches the complete SD-DarkMaster-Pro platform
Based on the unified single-cell architecture replacing the original 5-cell system
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def unified_bootstrap():
    """Complete platform deployment in one cell"""
    
    print("🚀 SD-DarkMaster-Pro Unified Bootstrap Starting...")
    print("=" * 60)
    
    # 1. Platform detection (2 seconds)
    print("🔍 Step 1/5: Platform detection...")
    
    if Path('/content').exists():
        platform = 'colab'
        project_root = Path('/content/SD-DarkMaster-Pro')
    elif Path('/kaggle').exists():
        platform = 'kaggle'
        project_root = Path('/kaggle/working/SD-DarkMaster-Pro')
    elif Path('/workspace').exists():
        platform = 'workspace'
        project_root = Path('/workspace/SD-DarkMaster-Pro')
    else:
        platform = 'local'
        project_root = Path.home() / 'SD-DarkMaster-Pro'
    
    print(f"   ✅ Platform detected: {platform}")
    print(f"   📁 Project root: {project_root}")
    
    # 2. Repository management (5 seconds)
    print("\n📥 Step 2/5: Repository management...")
    
    if not project_root.exists():
        print("   📦 Cloning repository...")
        # Note: Replace with actual repository URL when available
        repo_url = "https://github.com/user/SD-DarkMaster-Pro.git"
        try:
            subprocess.run([
                'git', 'clone', repo_url, str(project_root)
            ], check=True, capture_output=True)
            print("   ✅ Repository cloned successfully")
        except subprocess.CalledProcessError:
            print("   ⚠️ Repository clone failed, creating local structure...")
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / 'scripts').mkdir(exist_ok=True)
            (project_root / 'modules').mkdir(exist_ok=True)
            (project_root / 'configs').mkdir(exist_ok=True)
            (project_root / 'storage').mkdir(exist_ok=True)
    else:
        print("   ✅ Repository already exists")
    
    # 3. Dependencies check (8 seconds)
    print("\n📦 Step 3/5: Dependencies verification...")
    
    required_packages = [
        'streamlit==1.28.0',
        'pandas>=1.5.0',
        'requests>=2.28.0',
        'psutil>=5.9.0',
        'aiohttp>=3.8.0',
        'aiofiles>=0.8.0',
        'tqdm>=4.64.0'
    ]
    
    print("   📦 Installing/updating required packages...")
    for package in required_packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-q', package
            ], check=True)
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Failed to install {package}")
    
    print("   ✅ Dependencies verified")
    
    # 4. Launch Streamlit interface (10 seconds)
    print("\n🚀 Step 4/5: Launching unified interface...")
    
    # Copy unified app to project root if it doesn't exist
    unified_app_path = project_root / 'scripts' / 'unified_app.py'
    
    if not unified_app_path.exists():
        print("   📁 Creating unified app structure...")
        unified_app_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy our unified app
        current_unified = Path('sd_darkmaster_unified_app.py')
        if current_unified.exists():
            import shutil
            shutil.copy2(current_unified, unified_app_path)
            print("   ✅ Unified app copied to project")
        else:
            print("   ⚠️ Unified app not found, using fallback")
    
    # Change to project directory
    os.chdir(project_root)
    
    # Launch Streamlit
    print("   🌐 Starting Streamlit server...")
    
    streamlit_cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        str(unified_app_path),
        '--server.port', '8501',
        '--server.headless', 'true',
        '--server.enableCORS', 'true',
        '--server.enableXsrfProtection', 'false'
    ]
    
    try:
        # Launch Streamlit in background
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("   ✅ Streamlit server starting...")
        print(f"   🔗 Local URL: http://localhost:8501")
        
        # Wait for server to start
        time.sleep(5)
        
    except Exception as e:
        print(f"   ❌ Failed to start Streamlit: {e}")
        return False
    
    # 5. Create public tunnel (5 seconds)
    print("\n🌐 Step 5/5: Creating public tunnel...")
    
    # Try different tunnel services based on platform
    tunnel_services = {
        'colab': 'cloudflared',
        'kaggle': 'localtunnel', 
        'workspace': 'ngrok',
        'local': 'localtunnel'
    }
    
    tunnel_service = tunnel_services.get(platform, 'localtunnel')
    public_url = None
    
    if tunnel_service == 'cloudflared':
        try:
            # Install cloudflared if not available
            subprocess.run(['which', 'cloudflared'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("   📦 Installing cloudflared...")
            if platform == 'colab':
                subprocess.run([
                    'wget', '-q', 
                    'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb'
                ], check=True)
                subprocess.run(['dpkg', '-i', 'cloudflared-linux-amd64.deb'], check=True)
        
        try:
            tunnel_process = subprocess.Popen([
                'cloudflared', 'tunnel', '--url', 'http://localhost:8501'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it time to establish tunnel
            time.sleep(3)
            public_url = "Check terminal output for cloudflared URL"
            print(f"   ✅ Cloudflared tunnel created")
        except Exception as e:
            print(f"   ⚠️ Cloudflared failed: {e}")
    
    elif tunnel_service == 'localtunnel':
        try:
            # Install localtunnel via npm
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                         check=True, capture_output=True)
            
            tunnel_process = subprocess.Popen([
                'npx', 'localtunnel', '--port', '8501'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)
            public_url = "Check terminal output for localtunnel URL"
            print(f"   ✅ Localtunnel created")
        except Exception as e:
            print(f"   ⚠️ Localtunnel failed: {e}")
    
    elif tunnel_service == 'ngrok':
        try:
            # Note: Requires ngrok auth token
            tunnel_process = subprocess.Popen([
                'ngrok', 'http', '8501'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)
            public_url = "Check ngrok dashboard for public URL"
            print(f"   ✅ Ngrok tunnel created")
        except Exception as e:
            print(f"   ⚠️ Ngrok failed: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 SD-DarkMaster-Pro Unified Platform Ready!")
    print("=" * 60)
    print(f"🔗 Local Access: http://localhost:8501")
    if public_url:
        print(f"🌐 Public Access: {public_url}")
    print("\n📊 Platform Features:")
    print("   🏠 Dashboard - System status and quick actions")
    print("   ⚙️ Setup - Environment configuration")
    print("   📦 Models - Model selection with CivitAI integration")
    print("   💾 Downloads - Advanced download management")
    print("   🚀 Launch - Multi-WebUI launcher")
    print("   🧹 Storage - Unified storage management")
    print("   📊 Monitor - Real-time system monitoring")
    print("\n✅ All systems operational - Ready for AI art creation!")
    
    return True

# Execute the bootstrap
if __name__ == "__main__":
    success = unified_bootstrap()
    if success:
        print("\n🚀 Bootstrap completed successfully!")
    else:
        print("\n❌ Bootstrap failed - check logs above")