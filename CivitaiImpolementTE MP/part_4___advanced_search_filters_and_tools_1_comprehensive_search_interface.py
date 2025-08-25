# Part 4 - Advanced Search Filters and Tools - 1. Comprehensive Search Interface
# Generated for comprehensive CivitAI browser implementation


# Advanced search interface with all available filters

import streamlit as st
import requests
from datetime import datetime, timedelta

class AdvancedCivitAISearch:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"

        # Available filter options from CivitAI API
        self.model_types = [
            "Checkpoint", "TextualInversion", "Hypernetwork", 
            "AestheticGradient", "LORA", "Controlnet", "Poses"
        ]

        self.sort_options = [
            "Highest Rated", "Most Downloaded", "Newest"
        ]

        self.period_options = [
            "AllTime", "Year", "Month", "Week", "Day"
        ]

        self.base_models = [
            "SD 1.4", "SD 1.5", "SD 2.0", "SD 2.1", "SDXL 0.9", "SDXL 1.0",
            "Pony", "SD 3", "FLUX.1 D", "FLUX.1 S"
        ]

        self.commercial_use_options = [
            "None", "Image", "Rent", "Sell"
        ]

        # Image sort options
        self.image_sort_options = [
            "Most Reactions", "Most Comments", "Newest"
        ]

        self.nsfw_levels = [
            "None", "Soft", "Mature", "X"
        ]

    def create_search_interface(self):
        """Create comprehensive search interface"""

        st.title("🔍 Advanced CivitAI Search")

        # API Key input
        api_key = st.sidebar.text_input("CivitAI API Key", type="password")
        if api_key:
            self.api_key = api_key

        # Search tabs
        search_tab, filter_tab, advanced_tab = st.tabs(["🔍 Search", "🔧 Filters", "⚙️ Advanced"])

        with search_tab:
            search_params = self.create_basic_search()

        with filter_tab:
            filter_params = self.create_filter_interface()

        with advanced_tab:
            advanced_params = self.create_advanced_interface()

        # Combine all parameters
        all_params = {**search_params, **filter_params, **advanced_params}

        # Search execution
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Search Models", type="primary"):
                self.execute_model_search(all_params)

        with col2:
            if st.button("🖼️ Search Images", type="secondary"):
                self.execute_image_search(all_params)

        return all_params

    def create_basic_search(self):
        """Basic search parameters"""

        params = {}

        st.subheader("Basic Search")

        col1, col2 = st.columns(2)

        with col1:
            search_query = st.text_input("🔍 Search Query", placeholder="Enter keywords...")
            if search_query:
                params["query"] = search_query

            search_by = st.selectbox("Search By", ["Query", "Tag", "User name", "Model URL"])
            params["search_type"] = search_by

        with col2:
            sort_by = st.selectbox("Sort By", self.sort_options)
            params["sort"] = sort_by

            time_period = st.selectbox("Time Period", self.period_options)
            params["period"] = time_period

        # Results per page
        limit = st.slider("Results per page", 10, 100, 20)
        params["limit"] = limit

        return params

    def create_filter_interface(self):
        """Advanced filtering options"""

        params = {}

        st.subheader("Content Filters")

        # Model type filters
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Model Types:**")
            selected_types = []
            for model_type in self.model_types:
                if st.checkbox(model_type, key=f"type_{model_type}"):
                    selected_types.append(model_type)

            if selected_types:
                params["types"] = selected_types

        with col2:
            st.write("**Base Models:**")
            selected_base_models = st.multiselect("Base Models", self.base_models)
            if selected_base_models:
                params["baseModels"] = selected_base_models

        # Creator and licensing filters
        st.subheader("Creator & Licensing")

        col1, col2 = st.columns(2)

        with col1:
            username_filter = st.text_input("Creator Username")
            if username_filter:
                params["username"] = username_filter

            allow_no_credit = st.checkbox("Allow No Credit Required")
            if allow_no_credit:
                params["allowNoCredit"] = True

        with col2:
            commercial_use = st.selectbox("Commercial Use", ["Any"] + self.commercial_use_options)
            if commercial_use != "Any":
                params["allowCommercialUse"] = commercial_use

            allow_derivatives = st.checkbox("Allow Derivatives")
            if allow_derivatives:
                params["allowDerivatives"] = True

        # Content rating
        st.subheader("Content Rating")

        nsfw_filter = st.radio("NSFW Content", ["Include All", "Safe Only", "NSFW Only"])
        if nsfw_filter == "Safe Only":
            params["nsfw"] = False
        elif nsfw_filter == "NSFW Only":
            params["nsfw"] = True

        return params

    def create_advanced_interface(self):
        """Advanced search options"""

        params = {}

        st.subheader("Advanced Options")

        col1, col2 = st.columns(2)

        with col1:
            # Favorites and hidden (requires auth)
            if self.api_key:
                favorites_only = st.checkbox("My Favorites Only")
                if favorites_only:
                    params["favorites"] = True

                include_hidden = st.checkbox("Include Hidden Models")
                if include_hidden:
                    params["hidden"] = True

            # File options
            primary_file_only = st.checkbox("Primary File Only")
            if primary_file_only:
                params["primaryFileOnly"] = True

        with col2:
            # Generation support
            supports_generation = st.checkbox("Supports Generation")
            if supports_generation:
                params["supportsGeneration"] = True

            # Specific model IDs
            model_ids_input = st.text_input("Specific Model IDs (comma-separated)")
            if model_ids_input:
                try:
                    model_ids = [int(id.strip()) for id in model_ids_input.split(",")]
                    params["ids"] = model_ids
                except ValueError:
                    st.error("Invalid model IDs format")

        # Custom tags
        st.subheader("Tag Filters")

        custom_tags = st.text_input("Custom Tags (comma-separated)", 
                                   placeholder="anime, realistic, portrait")
        if custom_tags:
            tag_list = [tag.strip() for tag in custom_tags.split(",")]
            params["custom_tags"] = tag_list

        return params

    def execute_model_search(self, params):
        """Execute model search with all parameters"""

        # Build API parameters
        api_params = {
            "limit": params.get("limit", 20),
            "sort": params.get("sort", "Highest Rated"),
            "period": params.get("period", "AllTime")
        }

        # Add search query
        search_type = params.get("search_type", "Query")
        query = params.get("query", "")

        if query:
            if search_type == "Query":
                api_params["query"] = query
            elif search_type == "Tag":
                api_params["tag"] = query
            elif search_type == "User name":
                api_params["username"] = query
            elif search_type == "Model URL" and "models/" in query:
                # Extract model ID from URL
                import re
                match = re.search(r'models/(\d+)', query)
                if match:
                    api_params["ids"] = [int(match.group(1))]

        # Add filters
        if params.get("types"):
            api_params["types"] = params["types"]

        if params.get("baseModels"):
            api_params["baseModels"] = params["baseModels"]

        if params.get("username"):
            api_params["username"] = params["username"]

        if "nsfw" in params:
            api_params["nsfw"] = params["nsfw"]

        if params.get("favorites"):
            api_params["favorites"] = True

        if params.get("allowCommercialUse"):
            api_params["allowCommercialUse"] = params["allowCommercialUse"]

        # Add auth token
        if self.api_key:
            api_params["token"] = self.api_key

        # Execute search
        with st.spinner("Searching models..."):
            response = requests.get(f"{self.base_url}/models", params=api_params)

        if response.status_code == 200:
            data = response.json()
            self.display_model_results(data)
        else:
            st.error(f"Search failed: {response.status_code}")

    def execute_image_search(self, params):
        """Execute image search"""

        api_params = {
            "limit": params.get("limit", 20),
            "sort": "Most Reactions"
        }

        # Add search parameters
        if params.get("query"):
            # For images, we search by prompt content
            st.info("Image search by prompt keywords not directly supported by API. Showing recent images instead.")

        if "nsfw" in params:
            api_params["nsfw"] = params["nsfw"]

        if self.api_key:
            api_params["token"] = self.api_key

        # Execute search
        with st.spinner("Searching images..."):
            response = requests.get(f"{self.base_url}/images", params=api_params)

        if response.status_code == 200:
            data = response.json()
            self.display_image_results(data)
        else:
            st.error(f"Image search failed: {response.status_code}")

    def display_model_results(self, data):
        """Display model search results"""

        if not data.get("items"):
            st.warning("No models found matching your criteria")
            return

        st.success(f"Found {len(data['items'])} models")

        # Display pagination info
        metadata = data.get("metadata", {})
        if metadata:
            st.info(f"Page {metadata.get('currentPage', 1)} of {metadata.get('totalPages', '?')} "
                   f"({metadata.get('totalItems', '?')} total items)")

        # Display results
        for i, model in enumerate(data["items"]):
            with st.expander(f"{model['name']} - {model['type']}", expanded=i < 3):
                self.display_model_card(model)

    def display_image_results(self, data):
        """Display image search results"""

        if not data.get("items"):
            st.warning("No images found")
            return

        st.success(f"Found {len(data['items'])} images")

        # Display in grid
        cols = st.columns(3)

        for i, image in enumerate(data["items"]):
            with cols[i % 3]:
                st.image(image["url"], caption=f"Image {image['id']}")

                if image.get("meta"):
                    with st.expander("Generation Info"):
                        st.json(image["meta"])

    def display_model_card(self, model):
        """Display individual model card"""

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**Creator:** {model['creator']['username']}")
            st.write(f"**Type:** {model['type']}")
            st.write(f"**Downloads:** {model['stats']['downloadCount']:,}")
            st.write(f"**Rating:** {model['stats']['rating']:.2f}/5 ({model['stats']['ratingCount']} ratings)")

            if model.get("tags"):
                st.write(f"**Tags:** {', '.join(model['tags'])}")

        with col2:
            # Display preview image
            if model.get("modelVersions") and model["modelVersions"][0].get("images"):
                try:
                    img_url = model["modelVersions"][0]["images"][0]["url"]
                    st.image(img_url, width=200)
                except:
                    st.write("No preview available")

        # Model versions
        if model.get("modelVersions"):
            st.write("**Available Versions:**")
            for version in model["modelVersions"][:3]:  # Show first 3 versions
                st.write(f"- {version['name']} ({len(version.get('files', []))} files)")

# Main app
def main():
    search_engine = AdvancedCivitAISearch()
    search_params = search_engine.create_search_interface()

if __name__ == "__main__":
    main()
