# Part 4 - Advanced Search Filters and Tools - 2. Smart Filter Presets
# Generated for comprehensive CivitAI browser implementation


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
        """Create interface for filter presets"""

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
        """Allow users to save custom presets"""

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
        """Get currently trending tags"""

        # This would require analyzing recent popular models
        # For demo purposes, return common tags
        return [
            "photorealistic", "anime", "realistic", "portrait", "landscape",
            "fantasy", "sci-fi", "character", "style", "concept art","
            "3d", "digital art", "painting", "photography", "cinematic"
        ]

    def suggest_related_filters(self, current_query):
        """Suggest related filters based on current search"""

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
        """Create smart suggestions interface"""

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
        """Save a search configuration"""

        st.session_state.saved_searches[name] = {
            "params": params,
            "saved_at": datetime.now().isoformat(),
            "results_count": results_count
        }

    def create_saved_searches_interface(self):
        """Interface for managing saved searches"""

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
        """Quick save current search"""

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
