# Part 3 - Multi-Category Model Parsing - 1. Advanced Model Parser
# Generated for comprehensive CivitAI browser implementation


# Advanced parser for models with multiple categories/versions

class MultiCategoryModelParser:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"

    def parse_complex_model(self, model_id):
        """Parse a model that contains multiple categories like inpainting, VAE, SDXL versions"""

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
        """Categorize a model version based on name, base model, and files"""

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
        """Parse files within a version and categorize them"""

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
        """Create a compatibility map between different versions"""

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
        """Get recommended files to download based on use case"""

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

print("
Recommended Downloads (General Use):")
if general_recs["primary_model"]:
    print(f"Primary: {general_recs['primary_model']['name']}")
if general_recs["vae_file"]:
    print(f"VAE: {general_recs['vae_file']['name']}")
