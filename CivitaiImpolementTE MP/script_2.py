# Part 4 - Search Filters and Tools

part4_examples = {
    "Part 4 - Advanced Search Filters and Tools": {
        "1. Comprehensive Search Interface": """
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
        \"\"\"Create comprehensive search interface\"\"\"
        
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
        \"\"\"Basic search parameters\"\"\"
        
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
        \"\"\"Advanced filtering options\"\"\"
        
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
        \"\"\"Advanced search options\"\"\"
        
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
        \"\"\"Execute model search with all parameters\"\"\"
        
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
                match = re.search(r'models/(\\d+)', query)
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
        \"\"\"Execute image search\"\"\"
        
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
        \"\"\"Display model search results\"\"\"
        
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
        \"\"\"Display image search results\"\"\"
        
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
        \"\"\"Display individual model card\"\"\"
        
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
""",

        "2. Smart Filter Presets": """
# Pre-configured filter presets for common use cases

class FilterPresets:
    def __init__(self):
        self.presets = {
            "Photography Models": {
                "types": ["Checkpoint"],
                "baseModels": ["SDXL 1.0", "SD 1.5"],
                "tags": ["photorealistic", "photography", "realistic"],
                "sort": "Highest Rated",
                "nsfw": False
            },
            
            "Anime/Manga Models": {
                "types": ["Checkpoint", "LORA"],
                "baseModels": ["SD 1.5", "SDXL 1.0"],
                "tags": ["anime", "manga", "cartoon"],
                "sort": "Most Downloaded",
                "nsfw": "any"
            },
            
            "Character LoRAs": {
                "types": ["LORA"],
                "tags": ["character", "person", "celebrity"],
                "sort": "Most Downloaded",
                "period": "Month"
            },
            
            "Style LoRAs": {
                "types": ["LORA"],
                "tags": ["style", "art", "artistic"],
                "sort": "Highest Rated",
                "period": "Week"
            },
            
            "SDXL Models": {
                "baseModels": ["SDXL 1.0", "SDXL 0.9"],
                "sort": "Newest",
                "supportsGeneration": True
            },
            
            "Commercial Safe": {
                "allowCommercialUse": "Sell",
                "allowDerivatives": True,
                "allowNoCredit": False,
                "nsfw": False
            },
            
            "Inpainting Models": {
                "tags": ["inpainting", "inpaint"],
                "types": ["Checkpoint"],
                "sort": "Highest Rated"
            },
            
            "ControlNet Models": {
                "types": ["Controlnet"],
                "sort": "Most Downloaded",
                "period": "AllTime"
            },
            
            "Textual Inversions": {
                "types": ["TextualInversion"],
                "sort": "Highest Rated",
                "baseModels": ["SD 1.5"]
            },
            
            "Popular This Week": {
                "sort": "Most Downloaded",
                "period": "Week",
                "limit": 50
            }
        }
    
    def create_preset_interface(self):
        \"\"\"Create interface for filter presets\"\"\"
        
        st.subheader("🎯 Search Presets")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_preset = st.selectbox("Choose a preset", list(self.presets.keys()))
        
        with col2:
            if st.button("Apply Preset"):
                return self.presets[selected_preset]
        
        # Show preset details
        if selected_preset:
            with st.expander("Preset Details"):
                st.json(self.presets[selected_preset])
        
        return {}
    
    def create_custom_preset(self, current_params):
        \"\"\"Allow users to save custom presets\"\"\"
        
        st.subheader("💾 Save Custom Preset")
        
        preset_name = st.text_input("Preset Name")
        
        if st.button("Save Current Filters as Preset") and preset_name:
            # Filter out empty parameters
            clean_params = {k: v for k, v in current_params.items() if v}
            
            if "custom_presets" not in st.session_state:
                st.session_state.custom_presets = {}
            
            st.session_state.custom_presets[preset_name] = clean_params
            st.success(f"Preset '{preset_name}' saved!")
        
        # Show saved custom presets
        if hasattr(st.session_state, "custom_presets") and st.session_state.custom_presets:
            st.subheader("My Custom Presets")
            
            for name, params in st.session_state.custom_presets.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{name}**")
                
                with col2:
                    if st.button("Load", key=f"load_{name}"):
                        return params
                
                with col3:
                    if st.button("Delete", key=f"del_{name}"):
                        del st.session_state.custom_presets[name]
                        st.rerun()
        
        return {}

# Dynamic filter suggestions
class SmartFilterSuggestions:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
    
    def get_trending_tags(self, limit=20):
        \"\"\"Get currently trending tags\"\"\"
        
        # This would require analyzing recent popular models
        # For demo purposes, return common tags
        return [
            "photorealistic", "anime", "realistic", "portrait", "landscape",
            "fantasy", "sci-fi", "character", "style", "concept art","
            "3d", "digital art", "painting", "photography", "cinematic"
        ]
    
    def suggest_related_filters(self, current_query):
        \"\"\"Suggest related filters based on current search\"\"\"
        
        suggestions = {}
        
        if not current_query:
            return suggestions
        
        query_lower = current_query.lower()
        
        # Model type suggestions
        if any(term in query_lower for term in ["anime", "manga", "cartoon"]):
            suggestions["recommended_types"] = ["LORA", "Checkpoint"]
            suggestions["recommended_base_models"] = ["SD 1.5"]
        
        elif any(term in query_lower for term in ["photo", "realistic", "portrait"]):
            suggestions["recommended_types"] = ["Checkpoint"]
            suggestions["recommended_base_models"] = ["SDXL 1.0", "SD 1.5"]
        
        elif any(term in query_lower for term in ["style", "art"]):
            suggestions["recommended_types"] = ["LORA", "TextualInversion"]
        
        # Tag suggestions
        tag_associations = {
            "anime": ["manga", "cartoon", "2d", "cel shading"],
            "realistic": ["photorealistic", "photography", "detailed"],
            "portrait": ["face", "person", "character", "headshot"],
            "landscape": ["scenery", "environment", "nature", "outdoor"],
            "fantasy": ["magic", "medieval", "dragon", "mythical"]
        }
        
        for key, related_tags in tag_associations.items():
            if key in query_lower:
                suggestions["recommended_tags"] = related_tags
                break
        
        return suggestions
    
    def create_suggestions_interface(self, current_query=""):
        \"\"\"Create smart suggestions interface\"\"\"
        
        st.subheader("💡 Smart Suggestions")
        
        # Trending tags
        trending_tags = self.get_trending_tags()
        
        st.write("**Trending Tags:**")
        tag_cols = st.columns(5)
        
        for i, tag in enumerate(trending_tags[:10]):
            with tag_cols[i % 5]:
                if st.button(f"#{tag}", key=f"trend_{tag}"):
                    return {"suggested_tag": tag}
        
        # Query-based suggestions
        if current_query:
            suggestions = self.suggest_related_filters(current_query)
            
            if suggestions:
                st.write("**Suggestions based on your search:**")
                
                if suggestions.get("recommended_types"):
                    st.info(f"💡 Try these model types: {', '.join(suggestions['recommended_types'])}")
                
                if suggestions.get("recommended_base_models"):
                    st.info(f"💡 Recommended base models: {', '.join(suggestions['recommended_base_models'])}")
                
                if suggestions.get("recommended_tags"):
                    st.info(f"💡 Related tags: {', '.join(suggestions['recommended_tags'])}")
        
        return {}

# Saved searches functionality
class SavedSearches:
    def __init__(self):
        if "saved_searches" not in st.session_state:
            st.session_state.saved_searches = {}
    
    def save_search(self, name, params, results_count=0):
        \"\"\"Save a search configuration\"\"\"
        
        st.session_state.saved_searches[name] = {
            "params": params,
            "saved_at": datetime.now().isoformat(),
            "results_count": results_count
        }
    
    def create_saved_searches_interface(self):
        \"\"\"Interface for managing saved searches\"\"\"
        
        st.subheader("💾 Saved Searches")
        
        if not st.session_state.saved_searches:
            st.info("No saved searches yet. Run a search and save it!")
            return {}
        
        # Display saved searches
        for name, search_data in st.session_state.saved_searches.items():
            with st.expander(f"{name} ({search_data['results_count']} results)"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    saved_date = datetime.fromisoformat(search_data["saved_at"])
                    st.write(f"Saved: {saved_date.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show key parameters
                    params = search_data["params"]
                    if params.get("query"):
                        st.write(f"Query: {params['query']}")
                    if params.get("types"):
                        st.write(f"Types: {', '.join(params['types'])}")
                
                with col2:
                    if st.button("Load", key=f"load_search_{name}"):
                        return search_data["params"]
                
                with col3:
                    if st.button("Delete", key=f"del_search_{name}"):
                        del st.session_state.saved_searches[name]
                        st.rerun()
        
        return {}
    
    def quick_save_interface(self, current_params, results_count=0):
        \"\"\"Quick save current search\"\"\"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            save_name = st.text_input("Save current search as:", placeholder="My search")
        
        with col2:
            if st.button("💾 Save") and save_name:
                self.save_search(save_name, current_params, results_count)
                st.success("Search saved!")

# Main enhanced search app
def create_enhanced_search_app():
    st.title("🚀 Enhanced CivitAI Browser")
    
    # Initialize components
    search_engine = AdvancedCivitAISearch()
    presets = FilterPresets()
    suggestions = SmartFilterSuggestions()
    saved_searches = SavedSearches()
    
    # Sidebar for presets and saved searches
    with st.sidebar:
        st.header("Quick Access")
        
        # Presets
        preset_params = presets.create_preset_interface()
        
        st.divider()
        
        # Saved searches
        saved_params = saved_searches.create_saved_searches_interface()
        
        # Apply preset or saved search
        if preset_params or saved_params:
            st.session_state.applied_params = preset_params or saved_params
    
    # Main search interface
    search_params = search_engine.create_search_interface()
    
    # Apply any loaded parameters
    if hasattr(st.session_state, "applied_params"):
        search_params.update(st.session_state.applied_params)
        del st.session_state.applied_params
    
    # Smart suggestions
    suggestion_params = suggestions.create_suggestions_interface(
        search_params.get("query", "")
    )
    
    if suggestion_params:
        search_params.update(suggestion_params)
    
    # Quick save
    saved_searches.quick_save_interface(search_params)
    
    # Custom preset creation
    presets.create_custom_preset(search_params)
    
    return search_params

if __name__ == "__main__":
    create_enhanced_search_app()
""",

        "3. Advanced Search Analytics": """
# Search analytics and insights

import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd

class SearchAnalytics:
    def __init__(self):
        if "search_history" not in st.session_state:
            st.session_state.search_history = []
    
    def log_search(self, params, results_count, execution_time):
        \"\"\"Log search for analytics\"\"\"
        
        search_log = {
            "timestamp": datetime.now().isoformat(),
            "params": params,
            "results_count": results_count,
            "execution_time": execution_time,
            "search_type": "model" if "types" in params else "general"
        }
        
        st.session_state.search_history.append(search_log)
        
        # Keep only last 100 searches
        if len(st.session_state.search_history) > 100:
            st.session_state.search_history = st.session_state.search_history[-100:]
    
    def create_analytics_dashboard(self):
        \"\"\"Create analytics dashboard\"\"\"
        
        if not st.session_state.search_history:
            st.info("No search history available yet.")
            return
        
        st.subheader("📊 Search Analytics")
        
        history = st.session_state.search_history
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Searches", len(history))
        
        with col2:
            avg_results = sum(h['results_count'] for h in history) / len(history)
            st.metric("Avg Results", f"{avg_results:.1f}")
        
        with col3:
            avg_time = sum(h['execution_time'] for h in history) / len(history)
            st.metric("Avg Time", f"{avg_time:.2f}s")
        
        with col4:
            success_rate = len([h for h in history if h['results_count'] > 0]) / len(history) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Searches over time
            daily_searches = df.groupby('date').size()
            
            fig = px.line(
                x=daily_searches.index, 
                y=daily_searches.values,
                title="Searches Over Time",
                labels={'x': 'Date', 'y': 'Number of Searches'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Search types distribution
            search_types = Counter(h['search_type'] for h in history)
            
            fig = px.pie(
                values=list(search_types.values()),
                names=list(search_types.keys()),
                title="Search Types Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Popular search terms
        st.subheader("📈 Popular Search Terms")
        
        all_queries = [h['params'].get('query', '') for h in history if h['params'].get('query')]
        query_words = []
        
        for query in all_queries:
            query_words.extend(query.lower().split())
        
        if query_words:
            word_counts = Counter(query_words)
            popular_words = word_counts.most_common(10)
            
            fig = px.bar(
                x=[word for word, count in popular_words],
                y=[count for word, count in popular_words],
                title="Most Searched Terms",
                labels={'x': 'Search Terms', 'y': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Filter usage
        st.subheader("🔧 Filter Usage")
        
        filter_usage = Counter()
        
        for search in history:
            params = search['params']
            if params.get('types'):
                for model_type in params['types']:
                    filter_usage[f"Type: {model_type}"] += 1
            if params.get('baseModels'):
                for base_model in params['baseModels']:
                    filter_usage[f"Base: {base_model}"] += 1
            if params.get('sort'):
                filter_usage[f"Sort: {params['sort']}"] += 1
        
        if filter_usage:
            most_used_filters = filter_usage.most_common(10)
            
            fig = px.bar(
                x=[count for filter_name, count in most_used_filters],
                y=[filter_name for filter_name, count in most_used_filters],
                orientation='h',
                title="Most Used Filters",
                labels={'x': 'Usage Count', 'y': 'Filter'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Export search history
        if st.button("📥 Export Search History"):
            csv_data = pd.DataFrame(history).to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                "civitai_search_history.csv",
                "text/csv"
            )

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_timing(self):
        self.start_time = time.time()
    
    def end_timing(self, operation_name):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics[operation_name] = duration
            return duration
        return 0
    
    def create_performance_display(self):
        \"\"\"Display performance metrics\"\"\"
        
        if not self.metrics:
            return
        
        st.subheader("⚡ Performance Metrics")
        
        for operation, duration in self.metrics.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{operation}**")
            
            with col2:
                st.write(f"{duration:.2f}s")
            
            with col3:
                # Performance indicator
                if duration < 1.0:
                    st.success("Fast")
                elif duration < 3.0:
                    st.warning("Moderate")
                else:
                    st.error("Slow")

# Integrated advanced search with analytics
def create_analytics_enhanced_search():
    st.title("📊 CivitAI Browser with Analytics")
    
    # Initialize components
    search_engine = AdvancedCivitAISearch()
    analytics = SearchAnalytics()
    performance = PerformanceMonitor()
    
    # Analytics dashboard in expander
    with st.expander("📊 View Analytics Dashboard"):
        analytics.create_analytics_dashboard()
    
    # Main search interface
    search_params = search_engine.create_search_interface()
    
    # Override search execution to include analytics
    if st.button("🔍 Search with Analytics", type="primary"):
        performance.start_timing()
        
        # Execute search (simplified for demo)
        with st.spinner("Searching..."):
            time.sleep(1)  # Simulate API call
            results_count = 42  # Mock results
        
        execution_time = performance.end_timing("Model Search")
        
        # Log search
        analytics.log_search(search_params, results_count, execution_time)
        
        # Display results
        st.success(f"Found {results_count} results in {execution_time:.2f}s")
        
        # Show performance metrics
        performance.create_performance_display()

if __name__ == "__main__":
    create_analytics_enhanced_search()
"""
    }
}

# Continue creating files for Part 4
for part, examples in part4_examples.items():
    for example_name, code in examples.items():
        filename = f"civitai_browser_examples/{part.replace(' ', '_').replace('-', '_').lower()}_{example_name.replace(' ', '_').replace('.', '').lower()}.py"
        with open(filename, 'w') as f:
            f.write(f"# {part} - {example_name}\n")
            f.write(f"# Generated for comprehensive CivitAI browser implementation\n\n")
            f.write(code)

print("Created Part 4 examples - Advanced Search Filters and Tools")