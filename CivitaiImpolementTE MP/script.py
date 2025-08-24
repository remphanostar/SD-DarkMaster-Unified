# Let me create comprehensive code examples for each part of the CivitAI browser implementation

civitai_examples = {
    "Part 1 - Streamlit CivitAI Browser in Cloud Environments": {
        "1. Google Colab with ngrok": """
# Google Colab Implementation with ngrok tunneling
import streamlit as st
import requests
import json
import pandas as pd
from io import BytesIO
from PIL import Image
import os

class CivitAIBrowser:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        
    def get_models(self, limit=20, page=1, sort="Highest Rated", 
                   types=None, nsfw=False, **filters):
        params = {
            "limit": limit,
            "page": page, 
            "sort": sort,
            "nsfw": nsfw
        }
        
        if types:
            params["types"] = types
        if self.api_key:
            params["token"] = self.api_key
            
        # Add additional filters
        params.update(filters)
        
        response = requests.get(f"{self.base_url}/models", params=params)
        return response.json() if response.status_code == 200 else {}
    
    def get_images(self, limit=20, model_id=None, sort="Most Reactions", **filters):
        params = {
            "limit": limit,
            "sort": sort
        }
        
        if model_id:
            params["modelId"] = model_id
        if self.api_key:
            params["token"] = self.api_key
            
        params.update(filters)
        
        response = requests.get(f"{self.base_url}/images", params=params)
        return response.json() if response.status_code == 200 else {}

def main():
    st.set_page_config(page_title="CivitAI Browser", layout="wide")
    st.title("🎨 CivitAI Model & Image Browser")
    
    # Initialize browser
    api_key = st.sidebar.text_input("CivitAI API Key (optional)", type="password")
    browser = CivitAIBrowser(api_key)
    
    # Model browser section
    st.header("Model Browser")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        model_types = st.multiselect("Model Types", 
            ["Checkpoint", "LORA", "TextualInversion", "Hypernetwork", "AestheticGradient"])
    with col2:
        sort_by = st.selectbox("Sort By", ["Highest Rated", "Most Downloaded", "Newest"])
    with col3:
        limit = st.slider("Results per page", 10, 100, 20)
    
    if st.button("Search Models"):
        with st.spinner("Fetching models..."):
            models_data = browser.get_models(
                limit=limit, 
                sort=sort_by, 
                types=model_types if model_types else None
            )
            
        if models_data.get("items"):
            for model in models_data["items"]:
                with st.expander(f"{model['name']} - {model['type']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Creator:** {model['creator']['username']}")
                        st.write(f"**Downloads:** {model['stats']['downloadCount']:,}")
                        st.write(f"**Rating:** {model['stats']['rating']:.2f}/5")
                        
                        # Model versions
                        if model.get("modelVersions"):
                            version = model["modelVersions"][0]
                            st.write(f"**Latest Version:** {version['name']}")
                            st.write(f"**Download URL:** {version.get('downloadUrl', 'N/A')}")
                    
                    with col2:
                        if model["modelVersions"] and model["modelVersions"][0].get("images"):
                            try:
                                img_url = model["modelVersions"][0]["images"][0]["url"]
                                st.image(img_url, width=200)
                            except:
                                st.write("No preview available")

if __name__ == "__main__":
    main()

# Colab setup cell:
# !pip install streamlit pyngrok
# from pyngrok import ngrok
# ngrok.set_auth_token("YOUR_NGROK_TOKEN")
# public_url = ngrok.connect(port="8501")
# print(public_url)
# !streamlit run civitai_browser.py
""",

        "2. Lightning AI Studios": """
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
""",

        "3. Vast.ai Docker Container": """
# Dockerfile for Vast.ai
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "civitai_browser.py", "--server.port=8501", "--server.address=0.0.0.0"]

# requirements.txt
# streamlit==1.28.0
# requests==2.31.0  
# pillow==10.0.0
# pandas==2.0.3

# Vast.ai setup:
# 1. Create instance with this Docker image
# 2. Port forward 8501
# 3. Access via provided URL
""",

        "4. Hugging Face Spaces": """
# For Hugging Face Spaces deployment
# Create app.py in your Space repository

import streamlit as st
import requests
import json
from PIL import Image
import io

# Same CivitAIBrowser class as above...

def main():
    st.set_page_config(
        page_title="CivitAI Browser", 
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 CivitAI Model Browser")
    st.markdown("Browse and download models from CivitAI")
    
    # Implementation continues...

if __name__ == "__main__":
    main()

# requirements.txt for HF Spaces:
# streamlit
# requests  
# pillow
# pandas
""",

        "5. Local Tunnel Alternative": """
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
"""
    },
    
    "Part 2 - Model Card Fields from API": {
        "Complete Model Card Fields": """
# Comprehensive model card field extraction

class ModelCardExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
    
    def extract_all_model_fields(self, model_id):
        \"\"\"Extract all available fields from a model card\"\"\"
        
        url = f"{self.base_url}/models/{model_id}"
        params = {"token": self.api_key} if self.api_key else {}
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {}
            
        model_data = response.json()
        
        # Basic model information
        basic_fields = {
            "id": model_data.get("id"),
            "name": model_data.get("name"),
            "description": model_data.get("description"),
            "type": model_data.get("type"),  # Checkpoint, LORA, etc.
            "nsfw": model_data.get("nsfw"),
            "tags": model_data.get("tags", []),
            "mode": model_data.get("mode"),  # Archived, TakenDown, None
            "poi": model_data.get("poi"),  # Person of Interest flag
            "allowNoCredit": model_data.get("allowNoCredit"),
            "allowCommercialUse": model_data.get("allowCommercialUse"),
            "allowDerivatives": model_data.get("allowDerivatives"),
            "allowDifferentLicense": model_data.get("allowDifferentLicense")
        }
        
        # Creator information
        creator_info = {}
        if model_data.get("creator"):
            creator_info = {
                "creator_username": model_data["creator"].get("username"),
                "creator_image": model_data["creator"].get("image")
            }
        
        # Statistics
        stats = {}
        if model_data.get("stats"):
            stats = {
                "downloadCount": model_data["stats"].get("downloadCount"),
                "favoriteCount": model_data["stats"].get("favoriteCount"),
                "commentCount": model_data["stats"].get("commentCount"),
                "ratingCount": model_data["stats"].get("ratingCount"),
                "rating": model_data["stats"].get("rating")
            }
        
        # Model versions
        versions = []
        for version in model_data.get("modelVersions", []):
            version_data = {
                "id": version.get("id"),
                "name": version.get("name"),
                "description": version.get("description"),
                "createdAt": version.get("createdAt"),
                "downloadUrl": version.get("downloadUrl"),
                "trainedWords": version.get("trainedWords", []),
                "baseModel": version.get("baseModel"),
                "earlyAccessTimeFrame": version.get("earlyAccessTimeFrame"),
                "stats": version.get("stats", {})
            }
            
            # File information
            files = []
            for file_info in version.get("files", []):
                file_data = {
                    "name": file_info.get("name"),
                    "id": file_info.get("id"),
                    "sizeKB": file_info.get("sizeKB"),
                    "type": file_info.get("type"),
                    "pickleScanResult": file_info.get("pickleScanResult"),
                    "virusScanResult": file_info.get("virusScanResult"),
                    "scannedAt": file_info.get("scannedAt"),
                    "primary": file_info.get("primary"),
                    "downloadUrl": file_info.get("downloadUrl"),
                    "hashes": file_info.get("hashes", {}),
                    "metadata": {
                        "fp": file_info.get("metadata", {}).get("fp"),
                        "size": file_info.get("metadata", {}).get("size"),
                        "format": file_info.get("metadata", {}).get("format")
                    }
                }
                files.append(file_data)
            
            version_data["files"] = files
            
            # Images
            images = []
            for image in version.get("images", []):
                image_data = {
                    "url": image.get("url"),
                    "nsfw": image.get("nsfw"),
                    "width": image.get("width"),
                    "height": image.get("height"),
                    "hash": image.get("hash"),
                    "meta": image.get("meta")  # Generation parameters
                }
                images.append(image_data)
            
            version_data["images"] = images
            versions.append(version_data)
        
        return {
            **basic_fields,
            **creator_info,
            **stats,
            "modelVersions": versions
        }
    
    def detect_model_type(self, model_data):
        \"\"\"Detect if model is SDXL, SD1.5, LORA, Checkpoint, etc.\"\"\"
        
        model_type = model_data.get("type", "")
        
        # Check base model from versions
        base_models = []
        for version in model_data.get("modelVersions", []):
            if version.get("baseModel"):
                base_models.append(version["baseModel"])
        
        classification = {
            "primary_type": model_type,
            "base_models": list(set(base_models)),
            "is_checkpoint": model_type == "Checkpoint",
            "is_lora": model_type == "LORA", 
            "is_textual_inversion": model_type == "TextualInversion",
            "is_vae": model_type == "VAE",
            "supports_sdxl": any("SDXL" in bm for bm in base_models),
            "supports_sd15": any("SD 1.5" in bm for bm in base_models),
            "supports_sd21": any("SD 2.1" in bm for bm in base_models)
        }
        
        return classification

# Usage example
extractor = ModelCardExtractor(api_key="your_api_key")
model_data = extractor.extract_all_model_fields(model_id=123456)
model_classification = extractor.detect_model_type(model_data)
print(json.dumps(model_data, indent=2))
"""
    }
}

# Save examples to files for better organization
import os
os.makedirs("civitai_browser_examples", exist_ok=True)

for part, examples in civitai_examples.items():
    for example_name, code in examples.items():
        filename = f"civitai_browser_examples/{part.replace(' ', '_').replace('-', '_').lower()}_{example_name.replace(' ', '_').replace('.', '').lower()}.py"
        with open(filename, 'w') as f:
            f.write(f"# {part} - {example_name}\n")
            f.write(f"# Generated for comprehensive CivitAI browser implementation\n\n")
            f.write(code)

print("Created comprehensive code examples for CivitAI browser implementation:")
for part in civitai_examples.keys():
    print(f"- {part}")