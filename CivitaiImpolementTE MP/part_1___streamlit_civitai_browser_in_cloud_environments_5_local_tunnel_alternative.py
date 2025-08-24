# Part 1 - Streamlit CivitAI Browser in Cloud Environments - 5. Local Tunnel Alternative
# Generated for comprehensive CivitAI browser implementation


# Alternative using localtunnel instead of ngrok
import subprocess
import streamlit as st

def setup_tunnel():
    # Install localtunnel
    subprocess.run(["npm", "install", "-g", "localtunnel"], check=True)

    # Start tunnel
    tunnel = subprocess.Popen([
        "lt", "--port", "8501", "--subdomain", "civitai-browser"
    ])

    return tunnel

# In Colab/Jupyter:
# !npm install -g localtunnel
# !streamlit run app.py &
# !lt --port 8501
