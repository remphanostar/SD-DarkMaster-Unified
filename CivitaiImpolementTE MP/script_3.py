# Part 5 - CivitAI Image Browser with full metadata extraction

part5_examples = {
    "Part 5 - CivitAI Image Browser": {
        "1. Complete Image Browser with Metadata": """
# Comprehensive CivitAI Image Browser with full metadata extraction

import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
from datetime import datetime
import re

class CivitAIImageBrowser:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        
        # Image sort options
        self.sort_options = [
            "Most Reactions", "Most Comments", "Newest"
        ]
        
        self.period_options = [
            "AllTime", "Year", "Month", "Week", "Day"  
        ]
        
        self.nsfw_levels = [
            "None", "Soft", "Mature", "X"
        ]
    
    def get_images(self, limit=20, page=1, sort="Most Reactions", period="AllTime", **filters):
        \"\"\"Get images from CivitAI API\"\"\"
        
        params = {
            "limit": limit,
            "page": page,
            "sort": sort,
            "period": period
        }
        
        # Add optional filters
        if filters.get("modelId"):
            params["modelId"] = filters["modelId"]
        if filters.get("modelVersionId"):
            params["modelVersionId"] = filters["modelVersionId"]
        if filters.get("username"):
            params["username"] = filters["username"]
        if filters.get("postId"):
            params["postId"] = filters["postId"]
        if "nsfw" in filters:
            params["nsfw"] = filters["nsfw"]
        
        # Add auth token
        if self.api_key:
            params["token"] = self.api_key
        
        response = requests.get(f"{self.base_url}/images", params=params)
        return response.json() if response.status_code == 200 else {}
    
    def extract_complete_metadata(self, image_data):
        \"\"\"Extract all available metadata from image\"\"\"
        
        metadata = {
            "basic_info": {
                "id": image_data.get("id"),
                "url": image_data.get("url"),
                "width": image_data.get("width"),
                "height": image_data.get("height"),
                "nsfw": image_data.get("nsfw"),
                "nsfwLevel": image_data.get("nsfwLevel"),
                "createdAt": image_data.get("createdAt"),
                "postId": image_data.get("postId"),
                "hash": image_data.get("hash"),
                "username": image_data.get("username")
            },
            
            "stats": image_data.get("stats", {}),
            
            "generation_params": {},
            "model_info": {},
            "technical_details": {},
            "additional_resources": []
        }
        
        # Extract generation parameters
        meta = image_data.get("meta", {})
        if meta:
            # Basic generation parameters
            generation_params = {
                "prompt": meta.get("prompt", ""),
                "negativePrompt": meta.get("negativePrompt", ""),
                "seed": meta.get("seed"),
                "steps": meta.get("steps"),
                "cfgScale": meta.get("cfgScale"),
                "sampler": meta.get("sampler", ""),
                "scheduler": meta.get("scheduler", ""),
                "size": meta.get("Size", ""),
                "clipSkip": meta.get("Clip skip"),
                "model": meta.get("Model", ""),
                "modelHash": meta.get("Model hash", "")
            }
            
            # Advanced parameters
            advanced_params = {
                "denoisingStrength": meta.get("Denoising strength"),
                "hiresUpscale": meta.get("Hires upscale"),
                "hiresUpscaler": meta.get("Hires upscaler"),
                "hiresSteps": meta.get("Hires steps"),
                "firstPassSize": meta.get("First pass size"),
                "maskBlur": meta.get("Mask blur"),
                "inpaintingFill": meta.get("Inpainting fill"),
                "batchCount": meta.get("Batch count"),
                "batchSize": meta.get("Batch size"),
                "etaDDIM": meta.get("Eta DDIM"),
                "ensd": meta.get("ENSD")
            }
            
            generation_params.update({k: v for k, v in advanced_params.items() if v is not None})
            metadata["generation_params"] = generation_params
            
            # Extract LoRA and additional resources
            resources = meta.get("resources", [])
            if resources:
                for resource in resources:
                    if isinstance(resource, dict):
                        metadata["additional_resources"].append({
                            "name": resource.get("name", ""),
                            "type": resource.get("type", ""),
                            "weight": resource.get("weight"),
                            "hash": resource.get("hash", "")
                        })
            
            # Parse LoRAs from prompt if not in resources
            if not metadata["additional_resources"] and generation_params.get("prompt"):
                loras = self.extract_loras_from_prompt(generation_params["prompt"])
                metadata["additional_resources"].extend(loras)
        
        # Model version IDs (if available)
        if image_data.get("modelVersionIds"):
            metadata["model_info"]["modelVersionIds"] = image_data["modelVersionIds"]
        
        return metadata
    
    def extract_loras_from_prompt(self, prompt):
        \"\"\"Extract LoRA information from prompt text\"\"\"
        
        loras = []
        
        # Pattern for LoRA syntax: <lora:name:weight>
        lora_pattern = r'<lora:([^:>]+):([^>]+)>'
        matches = re.findall(lora_pattern, prompt)
        
        for name, weight in matches:
            loras.append({
                "name": name.strip(),
                "type": "lora",
                "weight": float(weight) if weight.replace('.', '').replace('-', '').isdigit() else weight,
                "hash": ""
            })
        
        # Pattern for embedding syntax: (embedding:weight) or embedding:weight
        embedding_pattern = r'\\b([a-zA-Z0-9_-]+):([0-9.]+)\\b'
        matches = re.findall(embedding_pattern, prompt)
        
        for name, weight in matches:
            if name not in [l["name"] for l in loras]:  # Avoid duplicates
                loras.append({
                    "name": name,
                    "type": "embedding",
                    "weight": float(weight),
                    "hash": ""
                })
        
        return loras
    
    def create_image_browser_interface(self):
        \"\"\"Create the main image browser interface\"\"\"
        
        st.title("🖼️ CivitAI Image Browser")
        
        # Search and filter controls
        with st.sidebar:
            st.header("🔧 Image Filters")
            
            # API Key
            api_key = st.text_input("CivitAI API Key", type="password")
            if api_key:
                self.api_key = api_key
            
            # Basic filters
            sort_by = st.selectbox("Sort By", self.sort_options)
            period = st.selectbox("Time Period", self.period_options)
            limit = st.slider("Images per page", 10, 100, 20)
            
            # Advanced filters
            st.subheader("Advanced Filters")
            
            model_id = st.number_input("Model ID (optional)", value=0, min_value=0)
            username_filter = st.text_input("Creator Username")
            
            # NSFW filter
            nsfw_filter = st.radio("Content Filter", ["All", "Safe Only", "NSFW Only"])
            
            # Apply NSFW setting
            nsfw_param = None
            if nsfw_filter == "Safe Only":
                nsfw_param = False
            elif nsfw_filter == "NSFW Only":
                nsfw_param = True
        
        # Search execution
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("🔍 Image Search Results")
        
        with col2:
            if st.button("🔍 Search Images", type="primary"):
                self.execute_image_search(
                    sort=sort_by,
                    period=period,
                    limit=limit,
                    model_id=model_id if model_id > 0 else None,
                    username=username_filter if username_filter else None,
                    nsfw=nsfw_param
                )
    
    def execute_image_search(self, **params):
        \"\"\"Execute image search and display results\"\"\"
        
        filters = {k: v for k, v in params.items() if v is not None}
        
        with st.spinner("Searching images..."):
            images_data = self.get_images(**filters)
        
        if not images_data.get("items"):
            st.warning("No images found matching your criteria")
            return
        
        st.success(f"Found {len(images_data['items'])} images")
        
        # Display pagination info
        metadata = images_data.get("metadata", {})
        if metadata:
            st.info(f"Showing results from cursor: {metadata.get('nextCursor', 'N/A')}")
        
        # Display images in grid
        self.display_image_grid(images_data["items"])
    
    def display_image_grid(self, images):
        \"\"\"Display images in a responsive grid\"\"\"
        
        # Grid layout
        cols_per_row = 3
        
        for i in range(0, len(images), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(images):
                    with col:
                        self.display_single_image(images[i + j], i + j)
    
    def display_single_image(self, image_data, index):
        \"\"\"Display a single image with metadata\"\"\"
        
        # Display image
        try:
            st.image(image_data["url"], use_column_width=True)
        except:
            st.error("Failed to load image")
            return
        
        # Image info
        st.write(f"**ID:** {image_data['id']}")
        st.write(f"**Size:** {image_data['width']}x{image_data['height']}")
        
        if image_data.get("username"):
            st.write(f"**Creator:** {image_data['username']}")
        
        # Stats
        stats = image_data.get("stats", {})
        if stats:
            st.write(f"👍 {stats.get('likeCount', 0)} | "
                    f"💬 {stats.get('commentCount', 0)} | "
                    f"❤️ {stats.get('heartCount', 0)}")
        
        # Metadata expansion
        if st.button(f"📋 View Details", key=f"details_{image_data['id']}"):
            self.show_detailed_metadata(image_data)
        
        # Download options  
        if st.button(f"💾 Download Options", key=f"download_{image_data['id']}"):
            self.show_download_options(image_data)
    
    def show_detailed_metadata(self, image_data):
        \"\"\"Show detailed metadata in modal-like expander\"\"\"
        
        metadata = self.extract_complete_metadata(image_data)
        
        with st.expander(f"🔍 Full Metadata - Image {image_data['id']}", expanded=True):
            
            # Tabs for different metadata sections
            tab1, tab2, tab3, tab4 = st.tabs(["🎨 Generation", "📊 Stats", "🔧 Technical", "📁 Resources"])
            
            with tab1:
                st.subheader("Generation Parameters")
                gen_params = metadata["generation_params"]
                
                if gen_params.get("prompt"):
                    st.text_area("Positive Prompt", gen_params["prompt"], height=100)
                
                if gen_params.get("negativePrompt"):
                    st.text_area("Negative Prompt", gen_params["negativePrompt"], height=80)
                
                # Key parameters in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if gen_params.get("seed"):
                        st.write(f"**Seed:** {gen_params['seed']}")
                    if gen_params.get("steps"):
                        st.write(f"**Steps:** {gen_params['steps']}")
                    if gen_params.get("cfgScale"):
                        st.write(f"**CFG Scale:** {gen_params['cfgScale']}")
                
                with col2:
                    if gen_params.get("sampler"):
                        st.write(f"**Sampler:** {gen_params['sampler']}")
                    if gen_params.get("scheduler"):
                        st.write(f"**Scheduler:** {gen_params['scheduler']}")
                    if gen_params.get("clipSkip"):
                        st.write(f"**Clip Skip:** {gen_params['clipSkip']}")
                
                with col3:
                    if gen_params.get("size"):
                        st.write(f"**Size:** {gen_params['size']}")
                    if gen_params.get("model"):
                        st.write(f"**Model:** {gen_params['model']}")
                    if gen_params.get("modelHash"):
                        st.write(f"**Model Hash:** {gen_params['modelHash'][:8]}...")
            
            with tab2:
                st.subheader("Image Statistics")
                basic_info = metadata["basic_info"]
                stats = metadata.get("stats", {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json({
                        "Image ID": basic_info["id"],
                        "Dimensions": f"{basic_info['width']}x{basic_info['height']}",
                        "NSFW Level": basic_info.get("nsfwLevel", "None"),
                        "Created": basic_info.get("createdAt", "Unknown")
                    })
                
                with col2:
                    st.json({
                        "Likes": stats.get("likeCount", 0),
                        "Hearts": stats.get("heartCount", 0),
                        "Comments": stats.get("commentCount", 0),
                        "Reactions": stats.get("cryCount", 0) + stats.get("laughCount", 0)
                    })
            
            with tab3:
                st.subheader("Technical Details")
                
                # Advanced generation parameters
                gen_params = metadata["generation_params"]
                technical_params = {
                    k: v for k, v in gen_params.items() 
                    if k in ["denoisingStrength", "hiresUpscale", "hiresUpscaler", 
                            "hiresSteps", "etaDDIM", "ensd", "maskBlur", "batchSize"]
                    and v is not None
                }
                
                if technical_params:
                    st.json(technical_params)
                else:
                    st.info("No additional technical parameters available")
            
            with tab4:
                st.subheader("Additional Resources")
                
                resources = metadata["additional_resources"]
                if resources:
                    for resource in resources:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.write(f"**{resource['name']}**")
                            
                            with col2:
                                st.write(f"Type: {resource['type']}")
                            
                            with col3:
                                if resource.get('weight'):
                                    st.write(f"Weight: {resource['weight']}")
                else:
                    st.info("No additional resources detected")
                
                # Model version info
                if metadata["model_info"].get("modelVersionIds"):
                    st.subheader("Associated Models")
                    for version_id in metadata["model_info"]["modelVersionIds"]:
                        st.write(f"- Model Version ID: {version_id}")
    
    def show_download_options(self, image_data):
        \"\"\"Show download and export options\"\"\"
        
        with st.expander(f"💾 Download Options - Image {image_data['id']}", expanded=True):
            
            metadata = self.extract_complete_metadata(image_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🖼️ Image Download")
                
                # Direct image download
                if st.button("Download Original Image", key=f"dl_img_{image_data['id']}"):
                    st.info(f"Download URL: {image_data['url']}")
                
                # Different resolutions (if available)
                st.info("💡 Use browser's 'Save Image As' for direct download")
            
            with col2:
                st.subheader("📄 Metadata Export")
                
                # Export metadata as JSON
                metadata_json = json.dumps(metadata, indent=2, default=str)
                
                st.download_button(
                    "Download Metadata (JSON)",
                    metadata_json,
                    f"image_{image_data['id']}_metadata.json",
                    "application/json",
                    key=f"dl_json_{image_data['id']}"
                )
                
                # Export A1111 compatible prompt
                a1111_prompt = self.generate_a1111_prompt(metadata)
                
                st.download_button(
                    "Download A1111 Prompt",
                    a1111_prompt,
                    f"image_{image_data['id']}_prompt.txt",
                    "text/plain",
                    key=f"dl_prompt_{image_data['id']}"
                )
            
            # Model download suggestions
            st.subheader("📦 Related Model Downloads")
            
            gen_params = metadata["generation_params"]
            
            if gen_params.get("model") or gen_params.get("modelHash"):
                st.info(f"🎯 **Main Model:** {gen_params.get('model', 'Unknown')}")
                if gen_params.get("modelHash"):
                    st.code(f"Model Hash: {gen_params['modelHash']}")
            
            # LoRA suggestions
            resources = metadata["additional_resources"]
            loras = [r for r in resources if r["type"] == "lora"]
            
            if loras:
                st.info("🎨 **LoRAs used:**")
                for lora in loras:
                    st.write(f"- {lora['name']} (weight: {lora['weight']})")
    
    def generate_a1111_prompt(self, metadata):
        \"\"\"Generate A1111 compatible prompt file\"\"\"
        
        gen_params = metadata["generation_params"]
        
        prompt_lines = []
        
        # Positive prompt
        if gen_params.get("prompt"):
            prompt_lines.append("Positive prompt:")
            prompt_lines.append(gen_params["prompt"])
            prompt_lines.append("")
        
        # Negative prompt
        if gen_params.get("negativePrompt"):
            prompt_lines.append("Negative prompt:")
            prompt_lines.append(gen_params["negativePrompt"])
            prompt_lines.append("")
        
        # Parameters
        params_line = []
        
        if gen_params.get("steps"):
            params_line.append(f"Steps: {gen_params['steps']}")
        
        if gen_params.get("sampler"):
            params_line.append(f"Sampler: {gen_params['sampler']}")
        
        if gen_params.get("cfgScale"):
            params_line.append(f"CFG scale: {gen_params['cfgScale']}")
        
        if gen_params.get("seed"):
            params_line.append(f"Seed: {gen_params['seed']}")
        
        if gen_params.get("size"):
            params_line.append(f"Size: {gen_params['size']}")
        
        if gen_params.get("model"):
            params_line.append(f"Model: {gen_params['model']}")
        
        if gen_params.get("modelHash"):
            params_line.append(f"Model hash: {gen_params['modelHash']}")
        
        if gen_params.get("clipSkip"):
            params_line.append(f"Clip skip: {gen_params['clipSkip']}")
        
        if params_line:
            prompt_lines.append(", ".join(params_line))
        
        return "\\n".join(prompt_lines)

# Main application
def main():
    st.set_page_config(
        page_title="CivitAI Image Browser",
        page_icon="🖼️",
        layout="wide"
    )
    
    browser = CivitAIImageBrowser()
    browser.create_image_browser_interface()

if __name__ == "__main__":
    main()
""",

        "2. Batch Image Downloader": """
# Batch image downloader with model file collection

import streamlit as st
import requests
import asyncio
import aiohttp
import zipfile
import os
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor
import time

class BatchImageDownloader:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        self.download_queue = []
        self.model_queue = []
        
    def create_batch_interface(self):
        \"\"\"Create batch download interface\"\"\"
        
        st.title("📦 Batch Image & Model Downloader")
        
        # Download queue management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Download Queue")
            
            # Input methods
            input_method = st.radio("Add items to queue:", 
                                   ["Image URLs", "Model ID", "Search Results"])
            
            if input_method == "Image URLs":
                urls_input = st.text_area("Image URLs (one per line)", 
                                         placeholder="https://civitai.com/images/123456\\nhttps://civitai.com/images/789012")
                
                if st.button("Add Images to Queue"):
                    urls = [url.strip() for url in urls_input.split('\\n') if url.strip()]
                    self.add_images_to_queue(urls)
            
            elif input_method == "Model ID":
                model_id = st.number_input("Model ID", min_value=1)
                include_images = st.checkbox("Include model preview images", value=True)
                include_files = st.checkbox("Include model files", value=True)
                
                if st.button("Add Model to Queue"):
                    self.add_model_to_queue(model_id, include_images, include_files)
            
            elif input_method == "Search Results":
                st.info("Use the search interface below to add images to queue")
        
        with col2:
            st.subheader("⚙️ Download Settings")
            
            # Download directory
            download_dir = st.text_input("Download Directory", value="./downloads")
            
            # Organization options
            organize_by = st.selectbox("Organize files by:", 
                                     ["None", "Model", "Creator", "Date"])
            
            # Include metadata
            include_metadata = st.checkbox("Include metadata files", value=True)
            include_prompts = st.checkbox("Include A1111 prompt files", value=True)
            
            # Concurrent downloads
            max_concurrent = st.slider("Max concurrent downloads", 1, 10, 3)
        
        # Queue display
        self.display_download_queue()
        
        # Batch download execution
        if st.button("🚀 Start Batch Download", type="primary"):
            self.execute_batch_download(
                download_dir=download_dir,
                organize_by=organize_by,
                include_metadata=include_metadata,
                include_prompts=include_prompts,
                max_concurrent=max_concurrent
            )
    
    def add_images_to_queue(self, urls):
        \"\"\"Add image URLs to download queue\"\"\"
        
        for url in urls:
            # Extract image ID from URL
            if "civitai.com/images/" in url:
                try:
                    image_id = url.split("/images/")[1].split("?")[0]
                    
                    # Get image metadata
                    image_data = self.get_image_metadata(image_id)
                    if image_data:
                        self.download_queue.append({
                            "type": "image",
                            "id": image_id,
                            "url": url,
                            "data": image_data,
                            "status": "queued"
                        })
                        
                except Exception as e:
                    st.error(f"Failed to process URL {url}: {e}")
        
        st.success(f"Added {len(urls)} images to queue")
    
    def add_model_to_queue(self, model_id, include_images=True, include_files=True):
        \"\"\"Add model and its assets to download queue\"\"\"
        
        try:
            # Get model data
            model_data = self.get_model_metadata(model_id)
            if not model_data:
                st.error(f"Could not fetch model {model_id}")
                return
            
            # Add model info to queue
            queue_item = {
                "type": "model",
                "id": model_id,
                "data": model_data,
                "include_images": include_images,
                "include_files": include_files,
                "status": "queued"
            }
            
            self.model_queue.append(queue_item)
            
            # Add individual images to download queue
            if include_images:
                for version in model_data.get("modelVersions", []):
                    for image in version.get("images", []):
                        self.download_queue.append({
                            "type": "model_image",
                            "id": image.get("id") or f"model_{model_id}_img",
                            "url": image["url"],
                            "data": image,
                            "model_id": model_id,
                            "status": "queued"
                        })
            
            st.success(f"Added model {model_id} to queue")
            
        except Exception as e:
            st.error(f"Failed to add model {model_id}: {e}")
    
    def get_image_metadata(self, image_id):
        \"\"\"Get metadata for a specific image\"\"\"
        
        # This would require getting the image from the images API
        # For now, return minimal data
        return {
            "id": image_id,
            "url": f"https://civitai.com/images/{image_id}",
            "meta": {}
        }
    
    def get_model_metadata(self, model_id):
        \"\"\"Get complete model metadata\"\"\"
        
        params = {}
        if self.api_key:
            params["token"] = self.api_key
        
        response = requests.get(f"{self.base_url}/models/{model_id}", params=params)
        return response.json() if response.status_code == 200 else None
    
    def display_download_queue(self):
        \"\"\"Display current download queue\"\"\"
        
        if not self.download_queue and not self.model_queue:
            st.info("Download queue is empty")
            return
        
        st.subheader(f"📋 Queue ({len(self.download_queue)} images, {len(self.model_queue)} models)")
        
        # Images queue
        if self.download_queue:
            with st.expander(f"Images ({len(self.download_queue)})"):
                for i, item in enumerate(self.download_queue):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"Image {item['id']}")
                    
                    with col2:
                        st.write(item['type'])
                    
                    with col3:
                        st.write(item['status'])
                    
                    with col4:
                        if st.button("🗑️", key=f"del_img_{i}"):
                            self.download_queue.pop(i)
                            st.rerun()
        
        # Models queue
        if self.model_queue:
            with st.expander(f"Models ({len(self.model_queue)})"):
                for i, item in enumerate(self.model_queue):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        model_name = item['data'].get('name', f"Model {item['id']}")
                        st.write(model_name[:30])
                    
                    with col2:
                        files_count = sum(len(v.get('files', [])) for v in item['data'].get('modelVersions', []))
                        st.write(f"{files_count} files")
                    
                    with col3:
                        st.write(item['status'])
                    
                    with col4:
                        if st.button("🗑️", key=f"del_model_{i}"):
                            self.model_queue.pop(i)
                            st.rerun()
        
        # Clear queue
        if st.button("🗑️ Clear All"):
            self.download_queue.clear()
            self.model_queue.clear()
            st.rerun()
    
    def execute_batch_download(self, download_dir, organize_by, include_metadata, 
                             include_prompts, max_concurrent):
        \"\"\"Execute the batch download\"\"\"
        
        if not self.download_queue and not self.model_queue:
            st.warning("No items in download queue")
            return
        
        # Create download directory
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        # Progress tracking
        total_items = len(self.download_queue) + len(self.model_queue)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        completed = 0
        
        try:
            # Download images
            for item in self.download_queue:
                status_text.text(f"Downloading image {item['id']}...")
                
                success = self.download_single_image(
                    item, download_dir, organize_by, 
                    include_metadata, include_prompts
                )
                
                if success:
                    item['status'] = 'completed'
                else:
                    item['status'] = 'failed'
                
                completed += 1
                progress_bar.progress(completed / total_items)
                
                time.sleep(0.1)  # Rate limiting
            
            # Download models
            for item in self.model_queue:
                status_text.text(f"Downloading model {item['id']}...")
                
                success = self.download_single_model(
                    item, download_dir, organize_by
                )
                
                if success:
                    item['status'] = 'completed'
                else:
                    item['status'] = 'failed'
                
                completed += 1
                progress_bar.progress(completed / total_items)
                
                time.sleep(0.5)  # Rate limiting for models
            
            # Create download summary
            self.create_download_summary(download_dir)
            
            st.success(f"Batch download completed! Files saved to {download_dir}")
            
        except Exception as e:
            st.error(f"Batch download failed: {e}")
    
    def download_single_image(self, item, download_dir, organize_by, 
                            include_metadata, include_prompts):
        \"\"\"Download a single image with metadata\"\"\"
        
        try:
            # Determine download path
            if organize_by == "Model" and item.get('model_id'):
                subfolder = f"model_{item['model_id']}"
            elif organize_by == "Creator" and item['data'].get('username'):
                subfolder = item['data']['username']
            elif organize_by == "Date":
                subfolder = datetime.now().strftime("%Y-%m-%d")
            else:
                subfolder = "images"
            
            download_path = Path(download_dir) / subfolder
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Download image
            image_url = item['data'].get('url', item['url'])
            response = requests.get(image_url)
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # Default
            
            # Save image
            image_filename = f"image_{item['id']}{ext}"
            image_path = download_path / image_filename
            
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Save metadata
            if include_metadata:
                metadata_path = download_path / f"image_{item['id']}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(item['data'], f, indent=2, default=str)
            
            # Save A1111 prompt
            if include_prompts and item['data'].get('meta'):
                prompt_content = self.generate_a1111_prompt(item['data']['meta'])
                prompt_path = download_path / f"image_{item['id']}_prompt.txt"
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to download image {item['id']}: {e}")
            return False
    
    def download_single_model(self, item, download_dir, organize_by):
        \"\"\"Download model files\"\"\"
        
        try:
            model_data = item['data']
            model_name = model_data.get('name', f"model_{item['id']}")
            
            # Create model folder
            safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            model_folder = Path(download_dir) / "models" / safe_name
            model_folder.mkdir(parents=True, exist_ok=True)
            
            # Save model metadata
            with open(model_folder / "model_info.json", 'w') as f:
                json.dump(model_data, f, indent=2, default=str)
            
            # Download model files
            if item.get('include_files'):
                for version in model_data.get('modelVersions', []):
                    version_folder = model_folder / f"version_{version['id']}"
                    version_folder.mkdir(exist_ok=True)
                    
                    for file_info in version.get('files', []):
                        if file_info.get('downloadUrl'):
                            # Download model file
                            file_response = requests.get(
                                file_info['downloadUrl'],
                                headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
                            )
                            
                            filename = file_info.get('name', f"file_{file_info['id']}")
                            file_path = version_folder / filename
                            
                            with open(file_path, 'wb') as f:
                                f.write(file_response.content)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to download model {item['id']}: {e}")
            return False
    
    def generate_a1111_prompt(self, meta_data):
        \"\"\"Generate A1111 compatible prompt from metadata\"\"\"
        
        lines = []
        
        if meta_data.get('prompt'):
            lines.append(meta_data['prompt'])
        
        if meta_data.get('negativePrompt'):
            lines.append(f"Negative prompt: {meta_data['negativePrompt']}")
        
        # Parameters
        params = []
        if meta_data.get('steps'):
            params.append(f"Steps: {meta_data['steps']}")
        if meta_data.get('sampler'):
            params.append(f"Sampler: {meta_data['sampler']}")
        if meta_data.get('cfgScale'):
            params.append(f"CFG scale: {meta_data['cfgScale']}")
        if meta_data.get('seed'):
            params.append(f"Seed: {meta_data['seed']}")
        
        if params:
            lines.append(", ".join(params))
        
        return "\\n".join(lines)
    
    def create_download_summary(self, download_dir):
        \"\"\"Create a summary of downloaded files\"\"\"
        
        summary = {
            "download_date": datetime.now().isoformat(),
            "total_images": len(self.download_queue),
            "total_models": len(self.model_queue),
            "completed_images": len([i for i in self.download_queue if i['status'] == 'completed']),
            "completed_models": len([i for i in self.model_queue if i['status'] == 'completed']),
            "failed_images": len([i for i in self.download_queue if i['status'] == 'failed']),
            "failed_models": len([i for i in self.model_queue if i['status'] == 'failed'])
        }
        
        summary_path = Path(download_dir) / "download_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

def main():
    st.set_page_config(
        page_title="Batch Downloader",
        page_icon="📦",
        layout="wide"
    )
    
    downloader = BatchImageDownloader()
    downloader.create_batch_interface()

if __name__ == "__main__":
    main()
""",

        "3. Advanced Image Search with Prompt Analysis": """
# Advanced image search with prompt analysis and filtering

import streamlit as st
import requests
import re
from collections import Counter
import pandas as pd
from textstat import flesch_reading_ease
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')  
except LookupError:
    nltk.download('stopwords')

class AdvancedImageSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        self.stop_words = set(stopwords.words('english'))
    
    def create_advanced_search_interface(self):
        \"\"\"Create advanced image search with prompt analysis\"\"\"
        
        st.title("🔍 Advanced Image Search & Analysis")
        
        # Search configuration
        with st.sidebar:
            st.header("🔧 Search Configuration")
            
            # API Key
            api_key = st.text_input("CivitAI API Key", type="password")
            if api_key:
                self.api_key = api_key
            
            # Basic search parameters
            st.subheader("Basic Parameters")
            sort_by = st.selectbox("Sort By", ["Most Reactions", "Most Comments", "Newest"])
            limit = st.slider("Results per search", 20, 200, 100)
            
            # Prompt analysis filters
            st.subheader("Prompt Analysis")
            
            min_prompt_length = st.slider("Min prompt length", 0, 500, 0)
            max_prompt_length = st.slider("Max prompt length", 100, 2000, 2000)
            
            # Keyword filtering
            required_keywords = st.text_input("Required keywords (comma-separated)")
            excluded_keywords = st.text_input("Excluded keywords (comma-separated)")
            
            # Style analysis
            style_categories = st.multiselect("Style Categories", [
                "Photography", "Anime", "Realistic", "Artistic", "Abstract",
                "Portrait", "Landscape", "Character", "Fantasy", "Sci-fi"
            ])
            
            # Technical parameters
            st.subheader("Technical Filters")
            
            min_resolution = st.selectbox("Minimum Resolution", [
                "Any", "512x512", "768x768", "1024x1024", "1536x1536"
            ])
            
            aspect_ratios = st.multiselect("Aspect Ratios", [
                "Square (1:1)", "Portrait (3:4)", "Landscape (4:3)", 
                "Wide (16:9)", "Ultra-wide (21:9)"
            ])
        
        # Main search interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Smart Search")
            
            search_mode = st.radio("Search Mode", [
                "Prompt Keywords", "Style Similarity", "Technical Parameters", "Advanced Query"
            ])
            
            if search_mode == "Prompt Keywords":
                search_query = st.text_input("Search in prompts", 
                                           placeholder="beautiful landscape, sunset, detailed")
                
            elif search_mode == "Style Similarity":
                reference_prompt = st.text_area("Reference prompt for style matching",
                                               placeholder="Paste a prompt to find similar styles")
                
            elif search_mode == "Technical Parameters":
                st.write("Use the sidebar filters for technical parameter search")
                search_query = ""
                
            elif search_mode == "Advanced Query":
                search_query = st.text_area("Advanced search query",
                                          placeholder="Complex search with AND/OR operators")
        
        with col2:
            if st.button("🔍 Execute Search", type="primary"):
                self.execute_advanced_search(
                    search_mode=search_mode,
                    query=locals().get('search_query', '') or locals().get('reference_prompt', ''),
                    sort_by=sort_by,
                    limit=limit,
                    filters={
                        'min_prompt_length': min_prompt_length,
                        'max_prompt_length': max_prompt_length,
                        'required_keywords': required_keywords,
                        'excluded_keywords': excluded_keywords,
                        'style_categories': style_categories,
                        'min_resolution': min_resolution,
                        'aspect_ratios': aspect_ratios
                    }
                )
        
        # Analysis tools
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Analyze Current Results"):
                self.analyze_search_results()
        
        with col2:
            if st.button("🏷️ Extract Popular Tags"):
                self.extract_trending_tags()
    
    def execute_advanced_search(self, search_mode, query, sort_by, limit, filters):
        \"\"\"Execute advanced search with filtering\"\"\"
        
        # Get images from API
        with st.spinner("Searching images..."):
            raw_results = self.get_images_batch(sort_by, limit)
        
        if not raw_results:
            st.error("No images found or API error")
            return
        
        # Apply advanced filters
        filtered_results = self.apply_advanced_filters(raw_results, search_mode, query, filters)
        
        # Display results
        st.success(f"Found {len(filtered_results)} images matching criteria")
        
        # Store results for analysis
        st.session_state.current_results = filtered_results
        
        # Display images
        self.display_filtered_results(filtered_results)
    
    def get_images_batch(self, sort_by, limit):
        \"\"\"Get batch of images from API\"\"\"
        
        params = {
            "limit": min(limit, 200),  # API limit
            "sort": sort_by
        }
        
        if self.api_key:
            params["token"] = self.api_key
        
        response = requests.get(f"{self.base_url}/images", params=params)
        
        if response.status_code == 200:
            return response.json().get("items", [])
        
        return []
    
    def apply_advanced_filters(self, images, search_mode, query, filters):
        \"\"\"Apply advanced filtering to image results\"\"\"
        
        filtered = []
        
        for image in images:
            if self.passes_filters(image, search_mode, query, filters):
                filtered.append(image)
        
        return filtered
    
    def passes_filters(self, image, search_mode, query, filters):
        \"\"\"Check if image passes all filters\"\"\"
        
        meta = image.get('meta', {})
        prompt = meta.get('prompt', '').lower()
        negative_prompt = meta.get('negativePrompt', '').lower()
        
        # Prompt length filter
        prompt_length = len(prompt)
        if prompt_length < filters['min_prompt_length'] or prompt_length > filters['max_prompt_length']:
            return False
        
        # Required keywords
        if filters['required_keywords']:
            required = [kw.strip().lower() for kw in filters['required_keywords'].split(',')]
            if not all(kw in prompt for kw in required):
                return False
        
        # Excluded keywords
        if filters['excluded_keywords']:
            excluded = [kw.strip().lower() for kw in filters['excluded_keywords'].split(',')]
            if any(kw in prompt for kw in excluded):
                return False
        
        # Resolution filter
        if filters['min_resolution'] != "Any":
            min_res = int(filters['min_resolution'].split('x')[0])
            if image.get('width', 0) < min_res or image.get('height', 0) < min_res:
                return False
        
        # Aspect ratio filter
        if filters['aspect_ratios']:
            image_ratio = self.get_aspect_ratio_category(image.get('width', 1), image.get('height', 1))
            if image_ratio not in filters['aspect_ratios']:
                return False
        
        # Style category filter
        if filters['style_categories']:
            image_style = self.categorize_image_style(prompt)
            if not any(style.lower() in image_style.lower() for style in filters['style_categories']):
                return False
        
        # Search mode specific filtering
        if search_mode == "Prompt Keywords" and query:
            query_words = query.lower().split()
            if not any(word in prompt for word in query_words):
                return False
        
        elif search_mode == "Style Similarity" and query:
            similarity_score = self.calculate_style_similarity(prompt, query.lower())
            if similarity_score < 0.3:  # Threshold
                return False
        
        return True
    
    def get_aspect_ratio_category(self, width, height):
        \"\"\"Categorize aspect ratio\"\"\"
        
        if width == 0 or height == 0:
            return "Unknown"
        
        ratio = width / height
        
        if 0.95 <= ratio <= 1.05:
            return "Square (1:1)"
        elif ratio < 0.95:
            return "Portrait (3:4)"
        elif 1.25 <= ratio <= 1.45:
            return "Landscape (4:3)"
        elif 1.7 <= ratio <= 1.9:
            return "Wide (16:9)"
        elif ratio > 2.0:
            return "Ultra-wide (21:9)"
        else:
            return "Other"
    
    def categorize_image_style(self, prompt):
        \"\"\"Categorize image style based on prompt\"\"\"
        
        style_keywords = {
            "Photography": ["photo", "photograph", "realistic", "photorealistic", "camera", "lens"],
            "Anime": ["anime", "manga", "cel shading", "kawaii", "chibi", "otaku"],
            "Realistic": ["realistic", "photorealistic", "lifelike", "detailed", "high resolution"],
            "Artistic": ["painting", "artwork", "artistic", "brush strokes", "canvas"],
            "Abstract": ["abstract", "surreal", "conceptual", "experimental"],
            "Portrait": ["portrait", "face", "headshot", "close-up"],
            "Landscape": ["landscape", "scenery", "nature", "outdoor", "vista"],
            "Character": ["character", "person", "figure", "human"],
            "Fantasy": ["fantasy", "magical", "dragon", "wizard", "mythical"],
            "Sci-fi": ["sci-fi", "futuristic", "cyberpunk", "space", "robot"]
        }
        
        detected_styles = []
        prompt_lower = prompt.lower()
        
        for style, keywords in style_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_styles.append(style)
        
        return ", ".join(detected_styles) if detected_styles else "General"
    
    def calculate_style_similarity(self, prompt1, prompt2):
        \"\"\"Calculate style similarity between two prompts\"\"\"
        
        # Simple word overlap similarity
        words1 = set(word_tokenize(prompt1.lower())) - self.stop_words
        words2 = set(word_tokenize(prompt2.lower())) - self.stop_words
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
    
    def display_filtered_results(self, images):
        \"\"\"Display filtered search results\"\"\"
        
        # Display options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            display_mode = st.selectbox("Display Mode", ["Grid", "List", "Detailed"])
        
        with col2:
            sort_results = st.selectbox("Sort Results", ["Relevance", "Resolution", "Prompt Length"])
        
        with col3:
            images_per_page = st.selectbox("Images per page", [10, 20, 50])
        
        # Sort results
        if sort_results == "Resolution":
            images = sorted(images, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
        elif sort_results == "Prompt Length":
            images = sorted(images, key=lambda x: len(x.get('meta', {}).get('prompt', '')), reverse=True)
        
        # Pagination
        total_pages = (len(images) - 1) // images_per_page + 1
        page = st.selectbox("Page", range(1, total_pages + 1))
        
        start_idx = (page - 1) * images_per_page
        end_idx = start_idx + images_per_page
        page_images = images[start_idx:end_idx]
        
        # Display based on mode
        if display_mode == "Grid":
            self.display_image_grid(page_images)
        elif display_mode == "List":
            self.display_image_list(page_images)
        else:
            self.display_detailed_view(page_images)
    
    def display_image_grid(self, images):
        \"\"\"Display images in grid format\"\"\"
        
        cols = st.columns(3)
        
        for i, image in enumerate(images):
            with cols[i % 3]:
                st.image(image['url'], use_column_width=True)
                
                # Basic info
                st.write(f"**{image['width']}x{image['height']}**")
                
                # Prompt preview
                prompt = image.get('meta', {}).get('prompt', '')
                if prompt:
                    st.write(f"*{prompt[:50]}...*" if len(prompt) > 50 else f"*{prompt}*")
                
                # Metadata button
                if st.button(f"Details", key=f"details_{image['id']}"):
                    st.session_state.selected_image = image
    
    def analyze_search_results(self):
        \"\"\"Analyze current search results\"\"\"
        
        if 'current_results' not in st.session_state:
            st.warning("No search results to analyze")
            return
        
        images = st.session_state.current_results
        
        st.subheader("📊 Search Results Analysis")
        
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Images", len(images))
        
        with col2:
            avg_resolution = sum(img.get('width', 0) * img.get('height', 0) for img in images) / len(images)
            st.metric("Avg Resolution", f"{avg_resolution/1000000:.1f}MP")
        
        with col3:
            avg_prompt_length = sum(len(img.get('meta', {}).get('prompt', '')) for img in images) / len(images)
            st.metric("Avg Prompt Length", f"{avg_prompt_length:.0f}")
        
        with col4:
            nsfw_count = sum(1 for img in images if img.get('nsfw', False))
            st.metric("NSFW Images", f"{nsfw_count}/{len(images)}")
        
        # Prompt analysis
        st.subheader("🏷️ Prompt Analysis")
        
        all_prompts = [img.get('meta', {}).get('prompt', '') for img in images]
        all_words = []
        
        for prompt in all_prompts:
            words = word_tokenize(prompt.lower())
            all_words.extend([word for word in words if word.isalpha() and word not in self.stop_words])
        
        # Most common words
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(20)
        
        if top_words:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Common Words:**")
                for word, count in top_words[:10]:
                    st.write(f"• {word}: {count}")
            
            with col2:
                # Word frequency chart
                words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                st.bar_chart(words_df.set_index('Word'))
        
        # Style distribution
        st.subheader("🎨 Style Distribution")
        
        styles = [self.categorize_image_style(img.get('meta', {}).get('prompt', '')) for img in images]
        style_counter = Counter([style for style_list in styles for style in style_list.split(', ')])
        
        if style_counter:
            style_df = pd.DataFrame(style_counter.most_common(), columns=['Style', 'Count'])
            st.bar_chart(style_df.set_index('Style'))
    
    def extract_trending_tags(self):
        \"\"\"Extract and display trending tags\"\"\"
        
        if 'current_results' not in st.session_state:
            st.warning("No search results available")
            return
        
        st.subheader("🏷️ Trending Tags & Patterns")
        
        images = st.session_state.current_results
        
        # Extract all prompts
        prompts = [img.get('meta', {}).get('prompt', '') for img in images if img.get('meta', {}).get('prompt')]
        
        # Tag extraction patterns
        tag_patterns = [
            (r'\\b(\\w+)\\s+style\\b', 'Style Tags'),
            (r'\\b(\\w+)\\s+art\\b', 'Art Tags'),
            (r'\\b(beautiful|gorgeous|stunning|amazing)\\s+(\\w+)\\b', 'Quality Tags'),
            (r'\\((\\w+):[0-9.]+\\)', 'Weighted Tags'),
            (r'<lora:([^:>]+):', 'LoRA Tags')
        ]
        
        for pattern, category in tag_patterns:
            st.write(f"**{category}:**")
            
            matches = []
            for prompt in prompts:
                matches.extend(re.findall(pattern, prompt, re.IGNORECASE))
            
            if matches:
                # Flatten tuples if necessary
                flat_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        flat_matches.extend(match)
                    else:
                        flat_matches.append(match)
                
                tag_counter = Counter(flat_matches)
                top_tags = tag_counter.most_common(10)
                
                for tag, count in top_tags:
                    st.write(f"• {tag}: {count}")
            else:
                st.write("No matches found")
            
            st.write("")

def main():
    st.set_page_config(
        page_title="Advanced Image Search",
        page_icon="🔍",
        layout="wide"
    )
    
    search_engine = AdvancedImageSearch()
    search_engine.create_advanced_search_interface()

if __name__ == "__main__":
    main()
"""
    }
}

# Continue creating files for Part 5
for part, examples in part5_examples.items():
    for example_name, code in examples.items():
        filename = f"civitai_browser_examples/{part.replace(' ', '_').replace('-', '_').lower()}_{example_name.replace(' ', '_').replace('.', '').lower()}.py"
        with open(filename, 'w') as f:
            f.write(f"# {part} - {example_name}\n")
            f.write(f"# Generated for comprehensive CivitAI browser implementation\n\n")
            f.write(code)

print("Created Part 5 examples - CivitAI Image Browser with full metadata extraction")