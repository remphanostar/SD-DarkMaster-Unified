# Continue with Part 3 - Multi-category model parsing

part3_examples = {
    "Part 3 - Multi-Category Model Parsing": {
        "1. Advanced Model Parser": """
# Advanced parser for models with multiple categories/versions

class MultiCategoryModelParser:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
    
    def parse_complex_model(self, model_id):
        \"\"\"Parse a model that contains multiple categories like inpainting, VAE, SDXL versions\"\"\"
        
        model_data = self.get_model_data(model_id)
        if not model_data:
            return {}
        
        parsed_categories = {
            "base_model_info": self.extract_base_info(model_data),
            "categories": {},
            "file_matrix": {},
            "compatibility_map": {}
        }
        
        # Parse each version and categorize
        for version in model_data.get("modelVersions", []):
            category_info = self.categorize_version(version)
            
            # Group by category type
            category_key = category_info["category"]
            if category_key not in parsed_categories["categories"]:
                parsed_categories["categories"][category_key] = []
            
            parsed_categories["categories"][category_key].append({
                "version_id": version["id"],
                "version_name": version["name"],
                "base_model": category_info["base_model"],
                "special_type": category_info["special_type"],
                "files": self.parse_version_files(version),
                "metadata": category_info
            })
        
        # Create compatibility matrix
        parsed_categories["compatibility_map"] = self.create_compatibility_map(
            parsed_categories["categories"]
        )
        
        return parsed_categories
    
    def categorize_version(self, version):
        \"\"\"Categorize a model version based on name, base model, and files\"\"\"
        
        version_name = version.get("name", "").lower()
        base_model = version.get("baseModel", "")
        description = version.get("description", "").lower()
        
        # Detect special types
        special_types = []
        
        # Inpainting detection
        if any(term in version_name for term in ["inpaint", "inpainting", "inp"]):
            special_types.append("inpainting")
        
        # VAE detection  
        if any(term in version_name for term in ["vae", "variational"]):
            special_types.append("vae")
        
        # Pruned detection
        if any(term in version_name for term in ["pruned", "pruning"]):
            special_types.append("pruned")
        
        # EMA detection
        if any(term in version_name for term in ["ema", "exponential"]):
            special_types.append("ema")
        
        # FP16 detection
        if any(term in version_name for term in ["fp16", "half", "16bit"]):
            special_types.append("fp16")
        
        # Base model categorization
        category = "standard"
        if "SDXL" in base_model:
            category = "sdxl"
        elif "SD 1.5" in base_model:
            category = "sd15"
        elif "SD 2.1" in base_model:
            category = "sd21"
        elif special_types:
            category = "_".join(special_types)
        
        return {
            "category": category,
            "base_model": base_model,
            "special_type": special_types,
            "version_name": version.get("name"),
            "trained_words": version.get("trainedWords", [])
        }
    
    def parse_version_files(self, version):
        \"\"\"Parse files within a version and categorize them\"\"\"
        
        files_by_type = {
            "primary": [],
            "safetensors": [],
            "pickle": [],
            "config": [],
            "vae": [],
            "other": []
        }
        
        for file_info in version.get("files", []):
            file_name = file_info.get("name", "").lower()
            file_type = file_info.get("type", "")
            format_type = file_info.get("metadata", {}).get("format", "")
            
            # Categorize file
            if file_info.get("primary"):
                files_by_type["primary"].append(file_info)
            elif "safetensors" in file_name or format_type == "SafeTensor":
                files_by_type["safetensors"].append(file_info)
            elif "pickle" in file_name or format_type == "PickleTensor":
                files_by_type["pickle"].append(file_info)
            elif "vae" in file_name:
                files_by_type["vae"].append(file_info)
            elif file_name.endswith((".yaml", ".yml", ".json")):
                files_by_type["config"].append(file_info)
            else:
                files_by_type["other"].append(file_info)
        
        return files_by_type
    
    def create_compatibility_map(self, categories):
        \"\"\"Create a compatibility map between different versions\"\"\"
        
        compatibility = {}
        
        # Map base model compatibility
        base_model_groups = {
            "SD 1.5": ["sd15", "standard"],
            "SDXL": ["sdxl"],
            "SD 2.1": ["sd21"]
        }
        
        for base_model, compatible_categories in base_model_groups.items():
            compatibility[base_model] = {
                "compatible_categories": compatible_categories,
                "available_versions": []
            }
            
            for category in compatible_categories:
                if category in categories:
                    compatibility[base_model]["available_versions"].extend(
                        categories[category]
                    )
        
        return compatibility
    
    def get_recommended_downloads(self, parsed_model, use_case="general"):
        \"\"\"Get recommended files to download based on use case\"\"\"
        
        recommendations = {
            "primary_model": None,
            "vae_file": None,
            "config_files": [],
            "alternatives": []
        }
        
        # Get the most suitable primary model
        if use_case == "sdxl" and "sdxl" in parsed_model["categories"]:
            category_versions = parsed_model["categories"]["sdxl"]
        elif use_case == "inpainting" and "inpainting" in parsed_model["categories"]:
            category_versions = parsed_model["categories"]["inpainting"]  
        else:
            # Default to SD 1.5 or first available
            if "sd15" in parsed_model["categories"]:
                category_versions = parsed_model["categories"]["sd15"]
            else:
                category_versions = list(parsed_model["categories"].values())[0]
        
        if category_versions:
            # Get primary files from the best version
            best_version = category_versions[0]  # Could add ranking logic
            primary_files = best_version["files"]["primary"]
            safetensor_files = best_version["files"]["safetensors"]
            
            if primary_files:
                recommendations["primary_model"] = primary_files[0]
            elif safetensor_files:
                recommendations["primary_model"] = safetensor_files[0]
        
        # Look for VAE files across all categories
        for category_name, versions in parsed_model["categories"].items():
            for version in versions:
                vae_files = version["files"]["vae"]
                if vae_files and not recommendations["vae_file"]:
                    recommendations["vae_file"] = vae_files[0]
                
                # Collect config files
                recommendations["config_files"].extend(
                    version["files"]["config"]
                )
        
        return recommendations

# Example usage
parser = MultiCategoryModelParser(api_key="your_api_key")

# Parse a complex model (example with multiple versions)
complex_model = parser.parse_complex_model(model_id=123456)

# Get recommendations for different use cases
general_recs = parser.get_recommended_downloads(complex_model, "general")
sdxl_recs = parser.get_recommended_downloads(complex_model, "sdxl") 
inpainting_recs = parser.get_recommended_downloads(complex_model, "inpainting")

print("Model Categories Found:")
for category, versions in complex_model["categories"].items():
    print(f"- {category}: {len(versions)} version(s)")

print("\nRecommended Downloads (General Use):")
if general_recs["primary_model"]:
    print(f"Primary: {general_recs['primary_model']['name']}")
if general_recs["vae_file"]:
    print(f"VAE: {general_recs['vae_file']['name']}")
""",

        "2. Category-Specific Browser": """
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
""",

        "3. Batch Model Processor": """
# Batch processor for multiple complex models

class BatchModelProcessor:
    def __init__(self, api_key=None):
        self.parser = MultiCategoryModelParser(api_key)
        self.processed_models = {}
    
    def process_model_list(self, model_ids, max_workers=5):
        \"\"\"Process multiple models concurrently\"\"\"
        
        import concurrent.futures
        import time
        
        results = {}
        
        def process_single_model(model_id):
            try:
                return model_id, self.parser.parse_complex_model(model_id)
            except Exception as e:
                return model_id, {"error": str(e)}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(process_single_model, mid): mid 
                for mid in model_ids
            }
            
            for future in concurrent.futures.as_completed(future_to_id):
                model_id = future_to_id[future]
                try:
                    model_id, result = future.result()
                    results[model_id] = result
                    time.sleep(0.1)  # Rate limiting
                except Exception as e:
                    results[model_id] = {"error": str(e)}
        
        self.processed_models.update(results)
        return results
    
    def create_model_matrix(self):
        \"\"\"Create a matrix of all processed models and their categories\"\"\"
        
        matrix_data = []
        
        for model_id, model_data in self.processed_models.items():
            if "error" in model_data:
                continue
                
            base_info = model_data.get("base_model_info", {})
            categories = model_data.get("categories", {})
            
            row = {
                "model_id": model_id,
                "model_name": base_info.get("name", "Unknown"),
                "model_type": base_info.get("type", "Unknown"),
                "total_versions": len(model_data.get("modelVersions", [])),
                "categories": list(categories.keys()),
                "has_sdxl": "sdxl" in categories,
                "has_sd15": "sd15" in categories, 
                "has_inpainting": "inpainting" in categories,
                "has_vae": any("vae" in cat for cat in categories),
                "download_count": base_info.get("downloadCount", 0),
                "rating": base_info.get("rating", 0)
            }
            
            matrix_data.append(row)
        
        return pd.DataFrame(matrix_data)
    
    def generate_batch_download_script(self, use_case="general"):
        \"\"\"Generate a download script for all recommended files\"\"\"
        
        script_lines = ["#!/bin/bash", "# Auto-generated CivitAI download script", ""]
        
        for model_id, model_data in self.processed_models.items():
            if "error" in model_data:
                continue
            
            recs = self.parser.get_recommended_downloads(model_data, use_case)
            model_name = model_data.get("base_model_info", {}).get("name", f"model_{model_id}")
            
            script_lines.append(f"# Downloads for {model_name}")
            
            if recs["primary_model"]:
                url = recs["primary_model"].get("downloadUrl")
                filename = recs["primary_model"].get("name")
                if url:
                    script_lines.append(f'wget "{url}" -O "{filename}"')
            
            if recs["vae_file"]:
                url = recs["vae_file"].get("downloadUrl") 
                filename = recs["vae_file"].get("name")
                if url:
                    script_lines.append(f'wget "{url}" -O "{filename}"')
            
            script_lines.append("")
        
        return "\n".join(script_lines)

# Streamlit interface for batch processing
def create_batch_processor_ui():
    st.subheader("Batch Model Processor")
    
    # Input model IDs
    model_ids_input = st.text_area(
        "Model IDs (one per line or comma-separated)",
        placeholder="123456\n789012\n345678"
    )
    
    if model_ids_input:
        # Parse model IDs
        model_ids = []
        for line in model_ids_input.strip().split('\n'):
            ids = [id.strip() for id in line.replace(',', ' ').split() if id.strip().isdigit()]
            model_ids.extend([int(id) for id in ids])
        
        st.write(f"Found {len(model_ids)} model IDs to process")
        
        if st.button("Process All Models"):
            processor = BatchModelProcessor(st.session_state.get("api_key"))
            
            with st.spinner("Processing models..."):
                results = processor.process_model_list(model_ids)
            
            # Display results matrix
            matrix_df = processor.create_model_matrix()
            
            if not matrix_df.empty:
                st.subheader("Processing Results")
                st.dataframe(matrix_df)
                
                # Download script generation
                use_case = st.selectbox("Download Script Use Case", ["general", "sdxl", "inpainting"])
                
                if st.button("Generate Download Script"):
                    script = processor.generate_batch_download_script(use_case)
                    
                    st.subheader("Download Script")
                    st.code(script, language="bash")
                    
                    # Offer script download
                    st.download_button(
                        "Download Script",
                        script,
                        file_name=f"civitai_download_{use_case}.sh",
                        mime="text/x-shellscript"
                    )
"""
    }
}

# Continue creating files
for part, examples in part3_examples.items():
    for example_name, code in examples.items():
        filename = f"civitai_browser_examples/{part.replace(' ', '_').replace('-', '_').lower()}_{example_name.replace(' ', '_').replace('.', '').lower()}.py"
        with open(filename, 'w') as f:
            f.write(f"# {part} - {example_name}\n")
            f.write(f"# Generated for comprehensive CivitAI browser implementation\n\n")
            f.write(code)

print("Created Part 3 examples:")
for part in part3_examples.keys():
    print(f"- {part}")