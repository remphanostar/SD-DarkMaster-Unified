# Part 1 - Streamlit CivitAI Browser in Cloud Environments - 1. Google Colab with ngrok
# Generated for comprehensive CivitAI browser implementation


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
