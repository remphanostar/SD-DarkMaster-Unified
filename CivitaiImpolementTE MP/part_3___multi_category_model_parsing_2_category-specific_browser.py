# Part 3 - Multi-Category Model Parsing - 2. Category-Specific Browser
# Generated for comprehensive CivitAI browser implementation


# Streamlit component for browsing multi-category models

import streamlit as st
import pandas as pd

def create_category_browser():
    st.subheader("Multi-Category Model Browser")

    # Model selection
    model_id = st.number_input("Model ID", value=123456)

    if st.button("Analyze Model Categories"):
        parser = MultiCategoryModelParser(st.session_state.get("api_key"))
        parsed_model = parser.parse_complex_model(model_id)

        if parsed_model.get("categories"):
            st.success(f"Found {len(parsed_model['categories'])} categories")

            # Display categories in tabs
            category_names = list(parsed_model["categories"].keys())
            tabs = st.tabs(category_names)

            for i, (category, versions) in enumerate(parsed_model["categories"].items()):
                with tabs[i]:
                    st.write(f"**{category.upper()} Category**")

                    for version in versions:
                        with st.expander(f"{version['version_name']}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write("**Version Info:**")
                                st.json({
                                    "Base Model": version["base_model"],
                                    "Special Types": version["special_type"],
                                    "Trained Words": version["trained_words"]
                                })

                            with col2:
                                st.write("**Available Files:**")
                                for file_type, files in version["files"].items():
                                    if files:
                                        st.write(f"*{file_type.title()}:* {len(files)} file(s)")
                                        for file_info in files:
                                            if st.button(f"Download {file_info['name']}", key=f"dl_{file_info['id']}"):
                                                st.info(f"Download URL: {file_info.get('downloadUrl', 'N/A')}")

            # Recommendations section
            st.subheader("Download Recommendations")

            use_case = st.selectbox("Use Case", ["general", "sdxl", "inpainting", "sd15"])

            if st.button("Get Recommendations"):
                recs = parser.get_recommended_downloads(parsed_model, use_case)

                if recs["primary_model"]:
                    st.success("**Recommended Primary Model:**")
                    st.json({
                        "File": recs["primary_model"]["name"],
                        "Size": f"{recs['primary_model']['sizeKB']/1024:.1f} MB",
                        "Format": recs["primary_model"].get("metadata", {}).get("format"),
                        "Download URL": recs["primary_model"].get("downloadUrl")
                    })

                if recs["vae_file"]:
                    st.info("**Recommended VAE:**")
                    st.json({
                        "File": recs["vae_file"]["name"],
                        "Size": f"{recs['vae_file']['sizeKB']/1024:.1f} MB"
                    })

        else:
            st.error("Could not parse model or no versions found")

# Integration with main app
def main():
    st.title("Advanced CivitAI Model Parser")
    create_category_browser()

if __name__ == "__main__":
    main()
