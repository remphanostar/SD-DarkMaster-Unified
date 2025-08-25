# Part 5 - CivitAI Image Browser - 1. Complete Image Browser with Metadata
# Generated for comprehensive CivitAI browser implementation


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
        """Get images from CivitAI API"""

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
        """Extract all available metadata from image"""

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
        """Extract LoRA information from prompt text"""

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
        embedding_pattern = r'\b([a-zA-Z0-9_-]+):([0-9.]+)\b'
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
        """Create the main image browser interface"""

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
        """Execute image search and display results"""

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
        """Display images in a responsive grid"""

        # Grid layout
        cols_per_row = 3

        for i in range(0, len(images), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < len(images):
                    with col:
                        self.display_single_image(images[i + j], i + j)

    def display_single_image(self, image_data, index):
        """Display a single image with metadata"""

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
        """Show detailed metadata in modal-like expander"""

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
        """Show download and export options"""

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
        """Generate A1111 compatible prompt file"""

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

        return "\n".join(prompt_lines)

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
