# Bonus - Hugging Face Integration - 2. Unified Model Browser (CivitAI + HF)
# Generated for comprehensive CivitAI browser implementation


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
        """Create unified search interface"""

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
        """Create platform-specific filter interface"""

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
        """Execute search across all selected platforms"""

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
        """Search a specific platform"""

        if platform == "CivitAI":
            return self.search_civitai(query, sort_by, limit, filters)
        elif platform == "Hugging Face":
            return self.search_huggingface(query, sort_by, limit, filters)

        return {"error": "Unknown platform"}

    def search_civitai(self, query, sort_by, limit, filters):
        """Search CivitAI models"""

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
        """Search Hugging Face models"""

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
        """Display results from all platforms"""

        # Summary metrics
        st.subheader("📊 Search Summary")

        cols = st.columns(len(results))

        for i, (platform, result) in enumerate(results.items()):
            with cols[i]:
                icon = self.platforms[platform]["icon"]

                if "error" in result:
                    st.error(f"{icon} {platform}\nError: {result['error']}")
                else:
                    count = result.get("total", 0)
                    st.success(f"{icon} {platform}\n{count} results")

        # Display mode selection
        display_mode = st.radio("Display Mode", ["Separate Tabs", "Unified List", "Side by Side"])

        if display_mode == "Separate Tabs":
            self.display_separate_tabs(results)
        elif display_mode == "Unified List":
            self.display_unified_list(results)
        else:
            self.display_side_by_side(results)

    def display_separate_tabs(self, results):
        """Display results in separate tabs"""

        valid_results = {k: v for k, v in results.items() if "error" not in v}

        if not valid_results:
            st.error("No valid results from any platform")
            return

        tabs = st.tabs([f"{self.platforms[p]['icon']} {p} ({r['total']})" for p, r in valid_results.items()])

        for i, (platform, result) in enumerate(valid_results.items()):
            with tabs[i]:
                self.display_platform_results(platform, result["items"])

    def display_unified_list(self, results):
        """Display all results in a unified list"""

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
        """Display results side by side"""

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
        """Display results for a specific platform"""

        if not items:
            st.info("No results found")
            return

        for item in items:
            with st.expander(self.get_item_title(platform, item)):
                self.display_single_item(platform, item)

    def get_item_title(self, platform, item):
        """Get display title for an item"""

        if platform == "CivitAI":
            return f"{item.get('name', 'Unknown')} - {item.get('type', 'Model')}"
        elif platform == "Hugging Face":
            return f"{item.modelId} - {getattr(item, 'pipeline_tag', 'Model')}"

        return "Unknown Item"

    def display_single_item(self, platform, item):
        """Display a single item"""

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

                st.code(f"# Use with transformers\nfrom transformers import pipeline\npipe = pipeline(model='{item.modelId}')")

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
