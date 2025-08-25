# Part 1 - Streamlit CivitAI Browser in Cloud Environments - 2. Lightning AI Studios
# Generated for comprehensive CivitAI browser implementation


# lightning_civitai_browser.py
import streamlit as st
import lightning as L
from lightning.app import LightningApp
from lightning.app.frontend import StreamlitFrontend

class CivitAIBrowserComponent(L.LightningWork):
    def __init__(self):
        super().__init__(parallel=True)

    def run(self):
        import subprocess
        subprocess.Popen([
            "streamlit", "run", "civitai_browser.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])

class CivitAIBrowserApp(L.LightningApp):
    def __init__(self):
        super().__init__()
        self.browser = CivitAIBrowserComponent()

    def run(self):
        self.browser.run()

# Run with: lightning run app lightning_civitai_browser.py
