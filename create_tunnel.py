#!/usr/bin/env python3
"""
Create public tunnel for SD-DarkMaster-Pro Dashboard
"""

from pyngrok import ngrok
import time
import subprocess
import sys

def create_tunnel():
    """Create a public tunnel to the Streamlit dashboard"""
    try:
        # Kill any existing tunnels
        ngrok.kill()
        
        # Create tunnel on port 8501
        print("🌐 Creating public tunnel for SD-DarkMaster-Pro Dashboard...")
        tunnel = ngrok.connect(8501)
        
        print(f"✅ Dashboard is now accessible at: {tunnel.public_url}")
        print("🎯 Features available:")
        print("   • Environment Info (Platform, Hardware, GPU detection)")
        print("   • WebUI Selector & Launch Controls")
        print("   • Real-time Output Console")
        print("   • Model Selection (SD1.5, SDXL with original data sources)")
        print("   • Configuration Panel (Tokens, API Keys, Launch Args)")
        print("   • Toggle Controls (Auto-updates, Verbose logging)")
        print("")
        print("📊 Dashboard Status: ENHANCED with your proposed UI design!")
        print("🎨 Theme: Dark Mode Pro with red accent borders")
        print("")
        print("Press Ctrl+C to stop the tunnel...")
        
        # Keep tunnel alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping tunnel...")
            ngrok.disconnect(tunnel.public_url)
            ngrok.kill()
            print("✅ Tunnel stopped")
            
    except Exception as e:
        print(f"❌ Error creating tunnel: {e}")
        print("💡 Make sure Streamlit is running on port 8501")
        return False
    
    return True

if __name__ == "__main__":
    create_tunnel()