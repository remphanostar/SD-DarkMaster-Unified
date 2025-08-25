# Create the bonus Hugging Face implementation and final integrated examples

bonus_and_final = {
    "Bonus - Hugging Face Integration": {
        "1. Hugging Face Model Browser": """
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
        \"\"\"Create Hugging Face model browser interface\"\"\"
        
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
        \"\"\"Execute Hugging Face search\"\"\"
        
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
        \"\"\"Search HuggingFace models\"\"\"
        
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
        \"\"\"Search HuggingFace datasets\"\"\"
        
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
        \"\"\"Search HuggingFace Spaces\"\"\"
        
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
        \"\"\"Display model search results\"\"\"
        
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
        \"\"\"Display dataset search results\"\"\"
        
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
        \"\"\"Display Spaces search results\"\"\"
        
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
        \"\"\"Show model download information\"\"\"
        
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
        \"\"\"Execute quick search for specific category\"\"\"
        
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
""",

        "2. Unified Model Browser (CivitAI + HF)": """
# Unified browser for both CivitAI and Hugging Face models

import streamlit as st
import requests
from huggingface_hub import HfApi, list_models
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

class UnifiedModelBrowser:
    def __init__(self, civitai_key=None, hf_token=None):
        self.civitai_key = civitai_key
        self.hf_token = hf_token
        self.hf_api = HfApi(token=hf_token)
        
        # Platform configurations
        self.platforms = {
            "CivitAI": {
                "base_url": "https://civitai.com/api/v1",
                "types": ["Checkpoint", "LORA", "TextualInversion", "Hypernetwork", "AestheticGradient", "Controlnet"],
                "icon": "🎨"
            },
            "Hugging Face": {
                "base_url": "https://huggingface.co/api",
                "types": ["text-to-image", "text-generation", "image-classification", "object-detection"],
                "icon": "🤗"
            }
        }
    
    def create_unified_interface(self):
        \"\"\"Create unified search interface\"\"\"
        
        st.title("🌐 Unified AI Model Browser")
        st.markdown("Search across CivitAI and Hugging Face simultaneously")
        
        # Platform selection
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            platforms = st.multiselect(
                "Select Platforms",
                options=list(self.platforms.keys()),
                default=list(self.platforms.keys()),
                format_func=lambda x: f"{self.platforms[x]['icon']} {x}"
            )
        
        if not platforms:
            st.warning("Please select at least one platform to search")
            return
        
        # Authentication
        with st.sidebar:
            st.header("🔐 Authentication")
            
            if "CivitAI" in platforms:
                civitai_key = st.text_input("CivitAI API Key", type="password")
                if civitai_key:
                    self.civitai_key = civitai_key
            
            if "Hugging Face" in platforms:
                hf_token = st.text_input("HF Token", type="password")
                if hf_token:
                    self.hf_token = hf_token
                    self.hf_api = HfApi(token=hf_token)
        
        # Search configuration
        st.subheader("🔍 Search Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_query = st.text_input("Search Query", placeholder="stable diffusion, bert, anime")
            search_mode = st.radio("Search Mode", ["General", "Specific Type", "Cross-Platform"])
        
        with col2:
            # Common filters
            sort_by = st.selectbox("Sort By", ["Relevance", "Downloads", "Recent", "Rating"])
            limit_per_platform = st.slider("Results per platform", 5, 50, 10)
        
        # Platform-specific filters
        platform_filters = {}
        
        if len(platforms) > 1:
            st.subheader("🔧 Platform-Specific Filters")
            
            filter_tabs = st.tabs([f"{self.platforms[p]['icon']} {p}" for p in platforms])
            
            for i, platform in enumerate(platforms):
                with filter_tabs[i]:
                    platform_filters[platform] = self.create_platform_filters(platform)
        
        # Execute search
        if st.button("🚀 Search All Platforms", type="primary"):
            self.execute_unified_search(
                platforms=platforms,
                query=search_query,
                search_mode=search_mode,
                sort_by=sort_by,
                limit_per_platform=limit_per_platform,
                platform_filters=platform_filters
            )
    
    def create_platform_filters(self, platform):
        \"\"\"Create platform-specific filter interface\"\"\"
        
        filters = {}
        
        if platform == "CivitAI":
            model_types = st.multiselect("Model Types", self.platforms[platform]["types"])
            base_models = st.multiselect("Base Models", ["SD 1.5", "SDXL 1.0", "SD 2.1"])
            nsfw_filter = st.radio("Content Filter", ["All", "Safe Only", "NSFW Only"])
            
            filters = {
                "types": model_types,
                "baseModels": base_models,
                "nsfw": None if nsfw_filter == "All" else (False if nsfw_filter == "Safe Only" else True)
            }
        
        elif platform == "Hugging Face":
            tasks = st.multiselect("Tasks", self.platforms[platform]["types"])
            libraries = st.multiselect("Libraries", ["transformers", "diffusers", "timm", "sentence-transformers"])
            author = st.text_input("Author/Organization")
            
            filters = {
                "tasks": tasks,
                "libraries": libraries,
                "author": author
            }
        
        return filters
    
    def execute_unified_search(self, platforms, query, search_mode, sort_by, limit_per_platform, platform_filters):
        \"\"\"Execute search across all selected platforms\"\"\"
        
        results = {}
        
        # Create progress tracking
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            futures = {}
            
            for i, platform in enumerate(platforms):
                status_text.text(f"Searching {platform}...")
                
                future = executor.submit(
                    self.search_platform,
                    platform,
                    query,
                    sort_by,
                    limit_per_platform,
                    platform_filters.get(platform, {})
                )
                
                futures[platform] = future
                progress_bar.progress((i + 0.5) / len(platforms))
            
            # Collect results
            for i, (platform, future) in enumerate(futures.items()):
                try:
                    results[platform] = future.result(timeout=30)
                    status_text.text(f"Completed {platform}")
                except Exception as e:
                    results[platform] = {"error": str(e)}
                    st.error(f"Failed to search {platform}: {e}")
                
                progress_bar.progress((i + 1) / len(platforms))
        
        progress_container.empty()
        
        # Display results
        self.display_unified_results(results, search_mode)
    
    def search_platform(self, platform, query, sort_by, limit, filters):
        \"\"\"Search a specific platform\"\"\"
        
        if platform == "CivitAI":
            return self.search_civitai(query, sort_by, limit, filters)
        elif platform == "Hugging Face":
            return self.search_huggingface(query, sort_by, limit, filters)
        
        return {"error": "Unknown platform"}
    
    def search_civitai(self, query, sort_by, limit, filters):
        \"\"\"Search CivitAI models\"\"\"
        
        params = {
            "limit": limit,
            "query": query if query else None,
            "sort": "Highest Rated" if sort_by == "Rating" else "Most Downloaded"
        }
        
        # Apply filters
        if filters.get("types"):
            params["types"] = filters["types"]
        if filters.get("baseModels"):
            params["baseModels"] = filters["baseModels"]
        if filters.get("nsfw") is not None:
            params["nsfw"] = filters["nsfw"]
        
        # Add auth
        if self.civitai_key:
            params["token"] = self.civitai_key
        
        try:
            response = requests.get(f"{self.platforms['CivitAI']['base_url']}/models", params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "items": data.get("items", []),
                    "total": len(data.get("items", [])),
                    "platform": "CivitAI"
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def search_huggingface(self, query, sort_by, limit, filters):
        \"\"\"Search Hugging Face models\"\"\"
        
        try:
            # Build filter string
            filter_parts = []
            if filters.get("tasks"):
                for task in filters["tasks"]:
                    filter_parts.append(f"task:{task}")
            if filters.get("libraries"):
                for lib in filters["libraries"]:
                    filter_parts.append(f"library:{lib}")
            
            filter_str = ",".join(filter_parts) if filter_parts else None
            
            # Map sort options
            hf_sort = "downloads" if sort_by in ["Downloads", "Relevance"] else "created_at"
            
            models = list_models(
                search=query if query else None,
                author=filters.get("author") if filters.get("author") else None,
                filter=filter_str,
                sort=hf_sort,
                direction=-1,
                limit=limit,
                full=True
            )
            
            models_list = list(models)
            
            return {
                "items": models_list,
                "total": len(models_list),
                "platform": "Hugging Face"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def display_unified_results(self, results, search_mode):
        \"\"\"Display results from all platforms\"\"\"
        
        # Summary metrics
        st.subheader("📊 Search Summary")
        
        cols = st.columns(len(results))
        
        for i, (platform, result) in enumerate(results.items()):
            with cols[i]:
                icon = self.platforms[platform]["icon"]
                
                if "error" in result:
                    st.error(f"{icon} {platform}\\nError: {result['error']}")
                else:
                    count = result.get("total", 0)
                    st.success(f"{icon} {platform}\\n{count} results")
        
        # Display mode selection
        display_mode = st.radio("Display Mode", ["Separate Tabs", "Unified List", "Side by Side"])
        
        if display_mode == "Separate Tabs":
            self.display_separate_tabs(results)
        elif display_mode == "Unified List":
            self.display_unified_list(results)
        else:
            self.display_side_by_side(results)
    
    def display_separate_tabs(self, results):
        \"\"\"Display results in separate tabs\"\"\"
        
        valid_results = {k: v for k, v in results.items() if "error" not in v}
        
        if not valid_results:
            st.error("No valid results from any platform")
            return
        
        tabs = st.tabs([f"{self.platforms[p]['icon']} {p} ({r['total']})" for p, r in valid_results.items()])
        
        for i, (platform, result) in enumerate(valid_results.items()):
            with tabs[i]:
                self.display_platform_results(platform, result["items"])
    
    def display_unified_list(self, results):
        \"\"\"Display all results in a unified list\"\"\"
        
        st.subheader("🔄 Unified Results")
        
        all_items = []
        
        for platform, result in results.items():
            if "error" not in result:
                for item in result["items"]:
                    all_items.append({
                        "platform": platform,
                        "data": item
                    })
        
        if not all_items:
            st.warning("No results to display")
            return
        
        # Sort by platform priority or relevance
        for item in all_items:
            platform = item["platform"]
            data = item["data"]
            
            with st.expander(f"{self.platforms[platform]['icon']} {self.get_item_title(platform, data)}"):
                self.display_single_item(platform, data)
    
    def display_side_by_side(self, results):
        \"\"\"Display results side by side\"\"\"
        
        valid_results = {k: v for k, v in results.items() if "error" not in v}
        
        if len(valid_results) < 2:
            st.warning("Need at least 2 platforms with results for side-by-side view")
            self.display_separate_tabs(results)
            return
        
        cols = st.columns(len(valid_results))
        
        for i, (platform, result) in enumerate(valid_results.items()):
            with cols[i]:
                st.subheader(f"{self.platforms[platform]['icon']} {platform}")
                self.display_platform_results(platform, result["items"][:5])  # Limit for space
    
    def display_platform_results(self, platform, items):
        \"\"\"Display results for a specific platform\"\"\"
        
        if not items:
            st.info("No results found")
            return
        
        for item in items:
            with st.expander(self.get_item_title(platform, item)):
                self.display_single_item(platform, item)
    
    def get_item_title(self, platform, item):
        \"\"\"Get display title for an item\"\"\"
        
        if platform == "CivitAI":
            return f"{item.get('name', 'Unknown')} - {item.get('type', 'Model')}"
        elif platform == "Hugging Face":
            return f"{item.modelId} - {getattr(item, 'pipeline_tag', 'Model')}"
        
        return "Unknown Item"
    
    def display_single_item(self, platform, item):
        \"\"\"Display a single item\"\"\"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if platform == "CivitAI":
                st.write(f"**Creator:** {item.get('creator', {}).get('username', 'Unknown')}")
                st.write(f"**Type:** {item.get('type', 'Unknown')}")
                st.write(f"**Downloads:** {item.get('stats', {}).get('downloadCount', 0):,}")
                st.write(f"**Rating:** {item.get('stats', {}).get('rating', 0):.2f}/5")
                
                if item.get('tags'):
                    st.write(f"**Tags:** {', '.join(item['tags'][:5])}")
                    
            elif platform == "Hugging Face":
                st.write(f"**Model ID:** {item.modelId}")
                st.write(f"**Author:** {getattr(item, 'author', 'Unknown')}")
                
                if hasattr(item, 'pipeline_tag'):
                    st.write(f"**Task:** {item.pipeline_tag}")
                
                if hasattr(item, 'downloads') and item.downloads:
                    st.write(f"**Downloads:** {item.downloads:,}")
                
                if hasattr(item, 'likes') and item.likes:
                    st.write(f"**Likes:** {item.likes:,}")
        
        with col2:
            # Platform-specific actions
            if platform == "CivitAI":
                model_url = f"https://civitai.com/models/{item.get('id')}"
                st.markdown(f"[🔗 View on CivitAI]({model_url})")
                
            elif platform == "Hugging Face":
                model_url = f"https://huggingface.co/{item.modelId}"
                st.markdown(f"[🔗 View on HF]({model_url})")
                
                st.code(f"# Use with transformers\\nfrom transformers import pipeline\\npipe = pipeline(model='{item.modelId}')")

def main():
    st.set_page_config(
        page_title="Unified Model Browser",
        page_icon="🌐", 
        layout="wide"
    )
    
    browser = UnifiedModelBrowser()
    browser.create_unified_interface()

if __name__ == "__main__":
    main()
"""
    },
    
    "Final Integration - Complete CivitAI Browser System": {
        "1. Master Application": """
# Master CivitAI browser application integrating all components

import streamlit as st
import sys
import importlib.util
from pathlib import Path

# Import all components (assuming they're in the same directory)
class MasterCivitAIBrowser:
    def __init__(self):
        self.components = {
            "Model Browser": "🎨",
            "Image Browser": "🖼️", 
            "Batch Downloader": "📦",
            "Advanced Search": "🔍",
            "Multi-Category Parser": "🔧",
            "Hugging Face Integration": "🤗",
            "Analytics Dashboard": "📊"
        }
        
        # Initialize session state
        if "current_component" not in st.session_state:
            st.session_state.current_component = "Model Browser"
        
        if "global_config" not in st.session_state:
            st.session_state.global_config = {
                "civitai_api_key": "",
                "hf_token": "",
                "download_dir": "./downloads",
                "theme": "dark"
            }
    
    def create_master_interface(self):
        \"\"\"Create the master interface\"\"\"
        
        # Page configuration
        st.set_page_config(
            page_title="CivitAI Master Browser",
            page_icon="🎨",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown(\"\"\"
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .component-card {
            padding: 1rem;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .component-card:hover {
            border-color: #4ecdc4;
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
        }
        
        .stats-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
        }
        </style>
        \"\"\", unsafe_allow_html=True)
        
        # Main header
        st.markdown('<h1 class="main-header">🎨 CivitAI Master Browser Suite</h1>', unsafe_allow_html=True)
        
        # Global configuration sidebar
        self.create_global_sidebar()
        
        # Component navigation
        self.create_component_navigation()
        
        # Main content area
        self.render_current_component()
        
        # Footer
        self.create_footer()
    
    def create_global_sidebar(self):
        \"\"\"Create global configuration sidebar\"\"\"
        
        with st.sidebar:
            st.header("🔧 Global Configuration")
            
            # API Keys
            st.subheader("🔐 Authentication")
            
            civitai_key = st.text_input(
                "CivitAI API Key",
                value=st.session_state.global_config["civitai_api_key"],
                type="password",
                help="Get your API key from civitai.com/user/account"
            )
            
            hf_token = st.text_input(
                "Hugging Face Token",
                value=st.session_state.global_config["hf_token"], 
                type="password",
                help="Get your token from huggingface.co/settings/tokens"
            )
            
            # Update session state
            st.session_state.global_config["civitai_api_key"] = civitai_key
            st.session_state.global_config["hf_token"] = hf_token
            
            st.divider()
            
            # Global settings
            st.subheader("⚙️ Global Settings")
            
            download_dir = st.text_input(
                "Download Directory",
                value=st.session_state.global_config["download_dir"]
            )
            st.session_state.global_config["download_dir"] = download_dir
            
            theme = st.selectbox(
                "Theme",
                ["dark", "light"],
                index=0 if st.session_state.global_config["theme"] == "dark" else 1
            )
            st.session_state.global_config["theme"] = theme
            
            st.divider()
            
            # Quick stats
            self.display_quick_stats()
            
            st.divider()
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Cache cleared!")
    
    def display_quick_stats(self):
        \"\"\"Display quick statistics\"\"\"
        
        st.subheader("📊 Quick Stats")
        
        # Mock statistics (in real app, these would come from actual data)
        stats = {
            "Searches Today": 0,
            "Downloads": 0,
            "Bookmarks": 0,
            "Cache Size": "0 MB"
        }
        
        # Update with session state data if available
        if hasattr(st.session_state, 'search_history'):
            stats["Searches Today"] = len(st.session_state.search_history)
        
        if hasattr(st.session_state, 'download_queue'):
            stats["Downloads"] = len(st.session_state.download_queue)
        
        for key, value in stats.items():
            st.metric(key, value)
    
    def create_component_navigation(self):
        \"\"\"Create component navigation\"\"\"
        
        st.subheader("🧭 Navigation")
        
        # Component selector
        cols = st.columns(len(self.components))
        
        for i, (component, icon) in enumerate(self.components.items()):
            with cols[i]:
                if st.button(
                    f"{icon}\\n{component}", 
                    key=f"nav_{component}",
                    use_container_width=True
                ):
                    st.session_state.current_component = component
                    st.rerun()
        
        # Current component indicator
        current = st.session_state.current_component
        icon = self.components[current]
        
        st.info(f"Current: {icon} **{current}**")
    
    def render_current_component(self):
        \"\"\"Render the currently selected component\"\"\"
        
        current = st.session_state.current_component
        
        st.divider()
        
        # Component header
        icon = self.components[current]
        st.subheader(f"{icon} {current}")
        
        # Render component based on selection
        if current == "Model Browser":
            self.render_model_browser()
        elif current == "Image Browser":
            self.render_image_browser()
        elif current == "Batch Downloader":
            self.render_batch_downloader()
        elif current == "Advanced Search":
            self.render_advanced_search()
        elif current == "Multi-Category Parser":
            self.render_multi_category_parser()
        elif current == "Hugging Face Integration":
            self.render_hf_integration()
        elif current == "Analytics Dashboard":
            self.render_analytics_dashboard()
    
    def render_model_browser(self):
        \"\"\"Render model browser component\"\"\"
        
        st.markdown("**🎨 Browse and search CivitAI models with advanced filtering**")
        
        # Quick demo of model browser
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Search Models", placeholder="anime, photorealistic, LORA...")
            model_types = st.multiselect("Model Types", ["Checkpoint", "LORA", "TextualInversion"])
        
        with col2:
            sort_by = st.selectbox("Sort By", ["Highest Rated", "Most Downloaded", "Newest"])
            limit = st.slider("Results", 10, 100, 20)
        
        if st.button("🔍 Search Models", type="primary"):
            st.info("Model search would execute here with real CivitAI API integration")
            
            # Mock results display
            with st.expander("Example Model Result"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Example SDXL Model**")
                    st.write("Creator: ExampleArtist")
                    st.write("Downloads: 50,000")
                    st.write("Rating: 4.8/5")
                
                with col2:
                    st.info("Preview image would appear here")
    
    def render_image_browser(self):
        \"\"\"Render image browser component\"\"\"
        
        st.markdown("**🖼️ Browse CivitAI images with metadata extraction and batch download**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Sort Images", ["Most Reactions", "Most Comments", "Newest"])
            st.selectbox("Time Period", ["AllTime", "Month", "Week", "Day"])
        
        with col2:
            st.selectbox("Content Filter", ["All", "Safe Only", "NSFW Only"])
            st.slider("Images per page", 10, 50, 20)
        
        if st.button("🔍 Browse Images", type="primary"):
            st.info("Image browser would display grid of images with metadata")
        
        # Metadata extraction demo
        with st.expander("🔍 Metadata Extraction Example"):
            st.json({
                "prompt": "masterpiece, best quality, 1girl, anime style",
                "negative_prompt": "worst quality, low quality",
                "seed": 1234567890,
                "steps": 30,
                "cfg_scale": 7,
                "sampler": "DPM++ 2M Karras",
                "model": "animePastelDream_softBakedVAE.safetensors",
                "loras": [
                    {"name": "character_style", "weight": 0.8}
                ]
            })
    
    def render_batch_downloader(self):
        \"\"\"Render batch downloader component\"\"\"
        
        st.markdown("**📦 Batch download images and models with organization**")
        
        # Download queue simulation
        st.subheader("📋 Download Queue")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Images Queued", "0")
        
        with col2:
            st.metric("Models Queued", "0")
        
        with col3:
            st.metric("Total Size", "0 GB")
        
        # Add to queue controls
        st.subheader("➕ Add to Queue")
        
        input_method = st.radio("Input Method", ["URLs", "Model ID", "Search Results"])
        
        if input_method == "URLs":
            urls = st.text_area("Image URLs (one per line)")
            if st.button("Add URLs to Queue"):
                st.success("URLs would be added to download queue")
        
        elif input_method == "Model ID":
            model_id = st.number_input("Model ID", min_value=1)
            include_images = st.checkbox("Include preview images", True)
            include_files = st.checkbox("Include model files", True)
            
            if st.button("Add Model to Queue"):
                st.success(f"Model {model_id} would be added to queue")
        
        # Download settings
        with st.expander("⚙️ Download Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Download Directory", value=st.session_state.global_config["download_dir"])
                st.selectbox("Organize By", ["None", "Model", "Creator", "Date"])
            
            with col2:
                st.checkbox("Include metadata files", True)
                st.checkbox("Include A1111 prompt files", True)
                st.slider("Max concurrent downloads", 1, 10, 3)
    
    def render_advanced_search(self):
        \"\"\"Render advanced search component\"\"\"
        
        st.markdown("**🔍 Advanced search with filters, presets, and analytics**")
        
        # Search presets
        st.subheader("🎯 Search Presets")
        
        presets = [
            "Photography Models", "Anime LoRAs", "Character Models",
            "SDXL Checkpoints", "Inpainting Models", "Style LoRAs"
        ]
        
        cols = st.columns(3)
        for i, preset in enumerate(presets):
            with cols[i % 3]:
                if st.button(preset, key=f"preset_{i}"):
                    st.success(f"Applied preset: {preset}")
        
        # Advanced filters
        st.subheader("🔧 Advanced Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.multiselect("Model Types", ["Checkpoint", "LORA", "TextualInversion"])
            st.multiselect("Base Models", ["SD 1.5", "SDXL 1.0", "SD 2.1"])
        
        with col2:
            st.text_input("Creator Username")
            st.selectbox("Commercial Use", ["Any", "Allowed", "Not Allowed"])
        
        with col3:
            st.slider("Min Downloads", 0, 100000, 0)
            st.slider("Min Rating", 0.0, 5.0, 0.0)
        
        # Smart suggestions
        with st.expander("💡 Smart Suggestions"):
            st.info("Based on your search: 'anime' - Try these filters:")
            st.write("• Model Types: LORA, Checkpoint")
            st.write("• Base Models: SD 1.5")
            st.write("• Tags: manga, 2d, cel-shading")
    
    def render_multi_category_parser(self):
        \"\"\"Render multi-category parser component\"\"\"
        
        st.markdown("**🔧 Parse models with multiple categories and versions**")
        
        model_id = st.number_input("Model ID to Parse", min_value=1, value=123456)
        
        if st.button("🔍 Analyze Model Categories"):
            st.success("Model analysis would display here")
            
            # Mock category analysis
            st.subheader("📊 Model Categories Found")
            
            categories = {
                "SD 1.5 Standard": 2,
                "SDXL Version": 1,
                "Inpainting": 1,
                "VAE": 1
            }
            
            for category, count in categories.items():
                st.write(f"• **{category}**: {count} version(s)")
            
            # Recommendations
            st.subheader("💡 Download Recommendations")
            
            use_case = st.selectbox("Use Case", ["General", "SDXL", "Inpainting"])
            
            if st.button("Get Recommendations"):
                st.json({
                    "primary_model": "model_v2_sdxl.safetensors",
                    "vae_file": "vae-ft-mse-840000-ema-pruned.ckpt",
                    "config_files": ["config.yaml"],
                    "total_size": "6.2 GB"
                })
    
    def render_hf_integration(self):
        \"\"\"Render Hugging Face integration component\"\"\"
        
        st.markdown("**🤗 Search and browse Hugging Face models**")
        
        # Platform comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 CivitAI")
            st.write("• AI Art Models")
            st.write("• Stable Diffusion")
            st.write("• LoRAs & Checkpoints")
            st.write("• Community Generated")
        
        with col2:
            st.subheader("🤗 Hugging Face")
            st.write("• NLP Models")
            st.write("• Computer Vision")
            st.write("• Audio Processing")
            st.write("• Research & Production")
        
        # Unified search
        st.subheader("🌐 Unified Search")
        
        platforms = st.multiselect("Search Platforms", ["CivitAI", "Hugging Face"], default=["CivitAI", "Hugging Face"])
        search_query = st.text_input("Search Query", placeholder="stable diffusion, bert, image classification")
        
        if st.button("🔍 Search Both Platforms"):
            st.success("Unified search would execute across selected platforms")
            
            # Mock results
            tab1, tab2 = st.tabs(["🎨 CivitAI Results", "🤗 HuggingFace Results"])
            
            with tab1:
                st.info("CivitAI models matching query would appear here")
            
            with tab2:
                st.info("HuggingFace models matching query would appear here")
    
    def render_analytics_dashboard(self):
        \"\"\"Render analytics dashboard component\"\"\"
        
        st.markdown("**📊 Search analytics and usage insights**")
        
        # Mock analytics data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Searches", "0", "0")
        
        with col2:
            st.metric("Avg Results", "0", "0")
        
        with col3:
            st.metric("Success Rate", "0%", "0%")
        
        with col4:
            st.metric("Total Downloads", "0", "0")
        
        # Charts placeholder
        st.subheader("📈 Usage Trends")
        
        chart_type = st.selectbox("Chart Type", ["Searches Over Time", "Popular Search Terms", "Model Type Distribution"])
        
        st.info(f"{chart_type} chart would be displayed here with real usage data")
        
        # Search history
        st.subheader("🔍 Recent Searches")
        
        if st.button("📥 Export Search History"):
            st.success("Search history would be exported as CSV")
    
    def create_footer(self):
        \"\"\"Create application footer\"\"\"
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎨 CivitAI Master Browser**")
            st.markdown("Comprehensive AI model management")
        
        with col2:
            st.markdown("**🔗 Links**")
            st.markdown("[CivitAI](https://civitai.com) | [Hugging Face](https://huggingface.co)")
        
        with col3:
            st.markdown("**ℹ️ Version**")
            st.markdown("v1.0.0 - Complete Suite")

def main():
    app = MasterCivitAIBrowser()
    app.create_master_interface()

if __name__ == "__main__":
    main()
""",

        "2. Deployment Configuration": """
# Complete deployment configuration for all cloud platforms

# requirements.txt for the complete application
requirements_txt = '''
# Core dependencies
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.3
numpy>=1.24.0
pillow>=10.0.0

# API clients
huggingface_hub>=0.17.0
transformers>=4.30.0

# Data processing
nltk>=3.8
textstat>=0.7.0

# Visualization
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Async and utilities
aiohttp>=3.8.0
asyncio
concurrent.futures
pathlib
json
re
datetime
time
base64
io
zipfile
os
hashlib

# Optional dependencies for advanced features
sentence-transformers>=2.2.0
opencv-python>=4.8.0
scikit-learn>=1.3.0
'''

# Docker configuration
dockerfile_content = '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "master_browser.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''

# Docker Compose for local development
docker_compose_content = '''
version: '3.8'

services:
  civitai-browser:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./downloads:/app/downloads
      - ./cache:/app/.streamlit/cache
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - civitai-browser
    restart: unless-stopped

volumes:
  downloads:
  cache:
'''

# Nginx configuration
nginx_conf = '''
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server civitai-browser:8501;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name localhost;
        
        # SSL configuration (add your certificates)
        # ssl_certificate /etc/nginx/ssl/cert.pem;
        # ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Streamlit specific configuration
        location / {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_read_timeout 86400;
        }
        
        # Static files caching
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://streamlit;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''

# Kubernetes deployment
k8s_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civitai-browser
  labels:
    app: civitai-browser
spec:
  replicas: 3
  selector:
    matchLabels:
      app: civitai-browser
  template:
    metadata:
      labels:
        app: civitai-browser
    spec:
      containers:
      - name: civitai-browser
        image: civitai-browser:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_HEADLESS
          value: "true"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: downloads
          mountPath: /app/downloads
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: downloads
        persistentVolumeClaim:
          claimName: civitai-downloads-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: civitai-browser-service
spec:
  selector:
    app: civitai-browser
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: civitai-downloads-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
'''

# Heroku Procfile and configuration
procfile = '''
web: streamlit run master_browser.py --server.port=$PORT --server.address=0.0.0.0
'''

heroku_runtime = '''
python-3.9.18
'''

# Railway deployment
railway_config = '''
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run master_browser.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health"
  }
}
'''

# Streamlit Cloud config
streamlit_config = '''
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
'''

# Environment variables template
env_template = '''
# CivitAI Configuration
CIVITAI_API_KEY=your_civitai_api_key_here
CIVITAI_BASE_URL=https://civitai.com/api/v1

# Hugging Face Configuration  
HF_TOKEN=your_huggingface_token_here
HF_BASE_URL=https://huggingface.co/api

# Application Settings
DEFAULT_DOWNLOAD_DIR=./downloads
MAX_CONCURRENT_DOWNLOADS=5
CACHE_TTL=3600

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=your_secret_key_here

# Performance
MAX_UPLOAD_SIZE=200
TIMEOUT_SECONDS=30
'''

# Installation scripts
install_script_unix = '''#!/bin/bash

echo "🚀 Installing CivitAI Master Browser..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv civitai_browser_env
source civitai_browser_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create directories
mkdir -p downloads
mkdir -p cache
mkdir -p logs

# Set permissions
chmod +x run.sh

echo "✅ Installation complete!"
echo "🚀 Run './run.sh' to start the application"
'''

install_script_windows = '''@echo off
echo 🚀 Installing CivitAI Master Browser...

:: Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv civitai_browser_env
call civitai_browser_env\\Scripts\\activate.bat

:: Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Download NLTK data
echo 📚 Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

:: Create directories
if not exist downloads mkdir downloads
if not exist cache mkdir cache
if not exist logs mkdir logs

echo ✅ Installation complete!
echo 🚀 Run 'run.bat' to start the application
pause
'''

# Run scripts
run_script_unix = '''#!/bin/bash

# Activate virtual environment
source civitai_browser_env/bin/activate

# Set environment variables
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false

# Start the application
echo "🚀 Starting CivitAI Master Browser..."
echo "📱 Open http://localhost:8501 in your browser"
streamlit run master_browser.py
'''

run_script_windows = '''@echo off
call civitai_browser_env\\Scripts\\activate.bat

set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_ENABLE_CORS=false

echo 🚀 Starting CivitAI Master Browser...
echo 📱 Open http://localhost:8501 in your browser
streamlit run master_browser.py
'''

# Write all configuration files
deployment_files = {
    "requirements.txt": requirements_txt,
    "Dockerfile": dockerfile_content,
    "docker-compose.yml": docker_compose_content,
    "nginx.conf": nginx_conf,
    "k8s-deployment.yaml": k8s_deployment,
    "Procfile": procfile,
    "runtime.txt": heroku_runtime,
    "railway.json": railway_config,
    ".streamlit/config.toml": streamlit_config,
    ".env.template": env_template,
    "install.sh": install_script_unix,
    "install.bat": install_script_windows,
    "run.sh": run_script_unix,
    "run.bat": run_script_windows
}

# Create deployment directory structure
import os
deployment_dir = "deployment_configs"
os.makedirs(deployment_dir, exist_ok=True)
os.makedirs(f"{deployment_dir}/.streamlit", exist_ok=True)

for filename, content in deployment_files.items():
    filepath = os.path.join(deployment_dir, filename)
    
    # Create subdirectories if needed
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

print("✅ Created comprehensive deployment configurations:")
for filename in deployment_files.keys():
    print(f"  📁 {filename}")

print("\\n🚀 Ready for deployment on:")
print("  • 🐳 Docker & Docker Compose")
print("  • ☸️ Kubernetes")
print("  • 🟣 Heroku")
print("  • 🚂 Railway")
print("  • ☁️ Streamlit Cloud")
print("  • 💻 Local installation (Windows/Unix)")

"""
    }
}

# Create the final files
for part, examples in bonus_and_final.items():
    for example_name, code in examples.items():
        filename = f"civitai_browser_examples/{part.replace(' ', '_').replace('-', '_').lower()}_{example_name.replace(' ', '_').replace('.', '').lower()}.py"
        with open(filename, 'w') as f:
            f.write(f"# {part} - {example_name}\n")
            f.write(f"# Generated for comprehensive CivitAI browser implementation\n\n")
            f.write(code)

print("✅ Created final integration examples and deployment configurations!")
print("\n📋 Complete implementation includes:")
print("- Part 1: Cloud deployment methods (5 variations)")
print("- Part 2: Model card field extraction")  
print("- Part 3: Multi-category model parsing (3 variations)")
print("- Part 4: Advanced search filters (3 variations)")
print("- Part 5: Image browser with metadata (3 variations)")
print("- Bonus: Hugging Face integration (2 variations)")
print("- Final: Master application + deployment configs (2 variations)")
print("\n🎯 Total: 19 complete code examples covering all requested features!")