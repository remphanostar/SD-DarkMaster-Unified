# Bonus - Hugging Face Integration - 1. Hugging Face Model Browser
# Generated for comprehensive CivitAI browser implementation


# Hugging Face model browser similar to CivitAI implementation

import streamlit as st
import requests
import json
from huggingface_hub import HfApi, list_models, list_datasets
import pandas as pd

class HuggingFaceModelBrowser:
    def __init__(self, hf_token=None):
        self.hf_token = hf_token
        self.api = HfApi(token=hf_token)
        self.base_url = "https://huggingface.co/api"

        # Available model categories
        self.model_tasks = [
            "text-classification", "token-classification", "table-question-answering",
            "question-answering", "zero-shot-classification", "translation",
            "summarization", "feature-extraction", "text-generation",
            "text2text-generation", "fill-mask", "sentence-similarity",
            "text-to-image", "image-to-text", "image-classification",
            "image-segmentation", "object-detection", "depth-estimation",
            "automatic-speech-recognition", "audio-classification"
        ]

        self.libraries = [
            "pytorch", "tensorflow", "jax", "transformers", "datasets",
            "tokenizers", "onnx", "safetensors", "diffusers", "timm"
        ]

        self.sort_options = [
            "downloads", "likes", "created_at", "modified", "author"
        ]

    def create_hf_browser_interface(self):
        """Create Hugging Face model browser interface"""

        st.title("🤗 Hugging Face Model Browser")

        # Configuration sidebar
        with st.sidebar:
            st.header("🔧 Search Configuration")

            # Authentication
            hf_token = st.text_input("HF Token (optional)", type="password")
            if hf_token:
                self.hf_token = hf_token
                self.api = HfApi(token=hf_token)

            # Search parameters
            search_query = st.text_input("Search Query", placeholder="bert, gpt, stable-diffusion")

            # Filters
            st.subheader("Filters")

            model_tasks = st.multiselect("Tasks", self.model_tasks)
            libraries = st.multiselect("Libraries", self.libraries) 

            # Author filter
            author_filter = st.text_input("Author/Organization", placeholder="microsoft, google, openai")

            # Sort and limit
            sort_by = st.selectbox("Sort By", self.sort_options)
            direction = st.radio("Direction", ["Descending", "Ascending"])
            limit = st.slider("Results Limit", 10, 100, 20)

        # Main interface
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("🔍 Model Search")

            search_mode = st.radio("Search Mode", [
                "Models", "Datasets", "Spaces"
            ])

        with col2:
            if st.button("🔍 Search", type="primary"):
                self.execute_hf_search(
                    search_mode=search_mode,
                    query=search_query,
                    tasks=model_tasks,
                    libraries=libraries,
                    author=author_filter,
                    sort=sort_by,
                    direction=-1 if direction == "Descending" else 1,
                    limit=limit
                )

        # Quick access buttons
        st.subheader("🚀 Quick Access")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🖼️ Text-to-Image Models"):
                self.quick_search("text-to-image", "diffusers")

        with col2:
            if st.button("💬 Language Models"):
                self.quick_search("text-generation", "transformers")

        with col3:
            if st.button("🖥️ Vision Models"):
                self.quick_search("image-classification", "timm")

        with col4:
            if st.button("🎵 Audio Models"):
                self.quick_search("automatic-speech-recognition", "transformers")

    def execute_hf_search(self, search_mode, query, tasks, libraries, author, sort, direction, limit):
        """Execute Hugging Face search"""

        try:
            with st.spinner(f"Searching {search_mode.lower()}..."):

                if search_mode == "Models":
                    results = self.search_models(query, tasks, libraries, author, sort, direction, limit)
                    self.display_model_results(results)

                elif search_mode == "Datasets":
                    results = self.search_datasets(query, author, sort, direction, limit)
                    self.display_dataset_results(results)

                elif search_mode == "Spaces":
                    results = self.search_spaces(query, author, sort, direction, limit)
                    self.display_space_results(results)

        except Exception as e:
            st.error(f"Search failed: {e}")

    def search_models(self, query, tasks, libraries, author, sort, direction, limit):
        """Search HuggingFace models"""

        # Build filter string
        filters = []
        if tasks:
            for task in tasks:
                filters.append(f"task:{task}")
        if libraries:
            for library in libraries:
                filters.append(f"library:{library}")

        filter_str = ",".join(filters) if filters else None

        # Execute search
        models = list_models(
            search=query if query else None,
            author=author if author else None,
            filter=filter_str,
            sort=sort,
            direction=direction,
            limit=limit,
            full=True
        )

        return list(models)

    def search_datasets(self, query, author, sort, direction, limit):
        """Search HuggingFace datasets"""

        datasets = list_datasets(
            search=query if query else None,
            author=author if author else None,
            sort=sort,
            direction=direction,
            limit=limit,
            full=True
        )

        return list(datasets)

    def search_spaces(self, query, author, sort, direction, limit):
        """Search HuggingFace Spaces"""

        # Spaces search via API
        params = {
            "limit": limit,
            "sort": sort,
            "direction": direction
        }

        if query:
            params["search"] = query
        if author:
            params["author"] = author

        response = requests.get(f"{self.base_url}/spaces", params=params)

        if response.status_code == 200:
            return response.json()

        return []

    def display_model_results(self, models):
        """Display model search results"""

        if not models:
            st.warning("No models found")
            return

        st.success(f"Found {len(models)} models")

        for i, model in enumerate(models):
            with st.expander(f"{model.modelId} - {getattr(model, 'pipeline_tag', 'Unknown')}", expanded=i < 3):

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Model ID:** {model.modelId}")
                    st.write(f"**Author:** {model.author or 'Unknown'}")

                    if hasattr(model, 'pipeline_tag') and model.pipeline_tag:
                        st.write(f"**Task:** {model.pipeline_tag}")

                    if hasattr(model, 'library_name') and model.library_name:
                        st.write(f"**Library:** {model.library_name}")

                    if hasattr(model, 'downloads') and model.downloads:
                        st.write(f"**Downloads:** {model.downloads:,}")

                    if hasattr(model, 'likes') and model.likes:
                        st.write(f"**Likes:** {model.likes:,}")

                    if hasattr(model, 'tags') and model.tags:
                        st.write(f"**Tags:** {', '.join(model.tags[:5])}")

                with col2:
                    # Action buttons
                    model_url = f"https://huggingface.co/{model.modelId}"

                    if st.button(f"🔗 View on HF", key=f"view_{model.modelId}"):
                        st.markdown(f"[Open Model]({model_url})")

                    if st.button(f"📋 Copy Model ID", key=f"copy_{model.modelId}"):
                        st.code(model.modelId)

                    if st.button(f"💾 Download Info", key=f"dl_{model.modelId}"):
                        self.show_download_info(model)

    def display_dataset_results(self, datasets):
        """Display dataset search results"""

        if not datasets:
            st.warning("No datasets found")
            return

        st.success(f"Found {len(datasets)} datasets")

        for dataset in datasets:
            with st.expander(f"{dataset.id}"):
                st.write(f"**Dataset ID:** {dataset.id}")
                st.write(f"**Author:** {dataset.author or 'Unknown'}")

                if hasattr(dataset, 'downloads') and dataset.downloads:
                    st.write(f"**Downloads:** {dataset.downloads:,}")

                if hasattr(dataset, 'tags') and dataset.tags:
                    st.write(f"**Tags:** {', '.join(dataset.tags[:5])}")

                dataset_url = f"https://huggingface.co/datasets/{dataset.id}"
                st.markdown(f"[View Dataset]({dataset_url})")

    def display_space_results(self, spaces):
        """Display Spaces search results"""

        if not spaces:
            st.warning("No Spaces found")
            return

        st.success(f"Found {len(spaces)} Spaces")

        # Note: This would need proper Space object handling
        for space in spaces:
            with st.expander(f"Space: {space.get('id', 'Unknown')}"):
                st.write(f"**Space ID:** {space.get('id')}")
                st.write(f"**Author:** {space.get('author', 'Unknown')}")

                space_url = f"https://huggingface.co/spaces/{space.get('id')}"
                st.markdown(f"[View Space]({space_url})")

    def show_download_info(self, model):
        """Show model download information"""

        with st.expander(f"📦 Download Info - {model.modelId}", expanded=True):

            st.subheader("🐍 Using transformers")
            st.code(f'''
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("{model.modelId}")
tokenizer = AutoTokenizer.from_pretrained("{model.modelId}")
            ''')

            st.subheader("🤗 Using huggingface_hub")
            st.code(f'''
from huggingface_hub import hf_hub_download

# Download specific file
file_path = hf_hub_download(
    repo_id="{model.modelId}",
    filename="pytorch_model.bin"
)
            ''')

            if hasattr(model, 'pipeline_tag') and model.pipeline_tag:
                st.subheader("🔧 Using pipeline")
                st.code(f'''
from transformers import pipeline

pipe = pipeline("{model.pipeline_tag}", model="{model.modelId}")
                ''')

            # Model files info
            try:
                model_info = self.api.model_info(model.modelId)
                if hasattr(model_info, 'siblings') and model_info.siblings:
                    st.subheader("📁 Available Files")

                    files_data = []
                    for sibling in model_info.siblings[:10]:  # Limit to first 10 files
                        files_data.append({
                            "Filename": sibling.rfilename,
                            "Size": f"{sibling.size / 1024 / 1024:.1f} MB" if sibling.size else "Unknown"
                        })

                    if files_data:
                        st.dataframe(pd.DataFrame(files_data))

            except Exception as e:
                st.info("Could not fetch file information")

    def quick_search(self, task, library):
        """Execute quick search for specific category"""

        st.subheader(f"🎯 {task.replace('-', ' ').title()} Models")

        try:
            models = list_models(
                filter=f"task:{task},library:{library}",
                sort="downloads",
                direction=-1,
                limit=10,
                full=True
            )

            models_list = list(models)

            if models_list:
                for model in models_list:
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**{model.modelId}**")

                    with col2:
                        if hasattr(model, 'downloads'):
                            st.write(f"{model.downloads:,} downloads")

                    with col3:
                        model_url = f"https://huggingface.co/{model.modelId}"
                        st.markdown(f"[View]({model_url})")
            else:
                st.info("No models found for this category")

        except Exception as e:
            st.error(f"Quick search failed: {e}")

def main():
    st.set_page_config(
        page_title="Hugging Face Browser", 
        page_icon="🤗",
        layout="wide"
    )

    browser = HuggingFaceModelBrowser()
    browser.create_hf_browser_interface()

if __name__ == "__main__":
    main()
