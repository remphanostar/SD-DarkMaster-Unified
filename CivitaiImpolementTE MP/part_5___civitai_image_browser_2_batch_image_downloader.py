# Part 5 - CivitAI Image Browser - 2. Batch Image Downloader
# Generated for comprehensive CivitAI browser implementation


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
        """Create batch download interface"""

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
                                         placeholder="https://civitai.com/images/123456\nhttps://civitai.com/images/789012")

                if st.button("Add Images to Queue"):
                    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
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
        """Add image URLs to download queue"""

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
        """Add model and its assets to download queue"""

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
        """Get metadata for a specific image"""

        # This would require getting the image from the images API
        # For now, return minimal data
        return {
            "id": image_id,
            "url": f"https://civitai.com/images/{image_id}",
            "meta": {}
        }

    def get_model_metadata(self, model_id):
        """Get complete model metadata"""

        params = {}
        if self.api_key:
            params["token"] = self.api_key

        response = requests.get(f"{self.base_url}/models/{model_id}", params=params)
        return response.json() if response.status_code == 200 else None

    def display_download_queue(self):
        """Display current download queue"""

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
        """Execute the batch download"""

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
        """Download a single image with metadata"""

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
        """Download model files"""

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
        """Generate A1111 compatible prompt from metadata"""

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

        return "\n".join(lines)

    def create_download_summary(self, download_dir):
        """Create a summary of downloaded files"""

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
