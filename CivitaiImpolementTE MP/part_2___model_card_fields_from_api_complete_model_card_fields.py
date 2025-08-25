# Part 2 - Model Card Fields from API - Complete Model Card Fields
# Generated for comprehensive CivitAI browser implementation


# Comprehensive model card field extraction

class ModelCardExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"

    def extract_all_model_fields(self, model_id):
        """Extract all available fields from a model card"""

        url = f"{self.base_url}/models/{model_id}"
        params = {"token": self.api_key} if self.api_key else {}

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {}

        model_data = response.json()

        # Basic model information
        basic_fields = {
            "id": model_data.get("id"),
            "name": model_data.get("name"),
            "description": model_data.get("description"),
            "type": model_data.get("type"),  # Checkpoint, LORA, etc.
            "nsfw": model_data.get("nsfw"),
            "tags": model_data.get("tags", []),
            "mode": model_data.get("mode"),  # Archived, TakenDown, None
            "poi": model_data.get("poi"),  # Person of Interest flag
            "allowNoCredit": model_data.get("allowNoCredit"),
            "allowCommercialUse": model_data.get("allowCommercialUse"),
            "allowDerivatives": model_data.get("allowDerivatives"),
            "allowDifferentLicense": model_data.get("allowDifferentLicense")
        }

        # Creator information
        creator_info = {}
        if model_data.get("creator"):
            creator_info = {
                "creator_username": model_data["creator"].get("username"),
                "creator_image": model_data["creator"].get("image")
            }

        # Statistics
        stats = {}
        if model_data.get("stats"):
            stats = {
                "downloadCount": model_data["stats"].get("downloadCount"),
                "favoriteCount": model_data["stats"].get("favoriteCount"),
                "commentCount": model_data["stats"].get("commentCount"),
                "ratingCount": model_data["stats"].get("ratingCount"),
                "rating": model_data["stats"].get("rating")
            }

        # Model versions
        versions = []
        for version in model_data.get("modelVersions", []):
            version_data = {
                "id": version.get("id"),
                "name": version.get("name"),
                "description": version.get("description"),
                "createdAt": version.get("createdAt"),
                "downloadUrl": version.get("downloadUrl"),
                "trainedWords": version.get("trainedWords", []),
                "baseModel": version.get("baseModel"),
                "earlyAccessTimeFrame": version.get("earlyAccessTimeFrame"),
                "stats": version.get("stats", {})
            }

            # File information
            files = []
            for file_info in version.get("files", []):
                file_data = {
                    "name": file_info.get("name"),
                    "id": file_info.get("id"),
                    "sizeKB": file_info.get("sizeKB"),
                    "type": file_info.get("type"),
                    "pickleScanResult": file_info.get("pickleScanResult"),
                    "virusScanResult": file_info.get("virusScanResult"),
                    "scannedAt": file_info.get("scannedAt"),
                    "primary": file_info.get("primary"),
                    "downloadUrl": file_info.get("downloadUrl"),
                    "hashes": file_info.get("hashes", {}),
                    "metadata": {
                        "fp": file_info.get("metadata", {}).get("fp"),
                        "size": file_info.get("metadata", {}).get("size"),
                        "format": file_info.get("metadata", {}).get("format")
                    }
                }
                files.append(file_data)

            version_data["files"] = files

            # Images
            images = []
            for image in version.get("images", []):
                image_data = {
                    "url": image.get("url"),
                    "nsfw": image.get("nsfw"),
                    "width": image.get("width"),
                    "height": image.get("height"),
                    "hash": image.get("hash"),
                    "meta": image.get("meta")  # Generation parameters
                }
                images.append(image_data)

            version_data["images"] = images
            versions.append(version_data)

        return {
            **basic_fields,
            **creator_info,
            **stats,
            "modelVersions": versions
        }

    def detect_model_type(self, model_data):
        """Detect if model is SDXL, SD1.5, LORA, Checkpoint, etc."""

        model_type = model_data.get("type", "")

        # Check base model from versions
        base_models = []
        for version in model_data.get("modelVersions", []):
            if version.get("baseModel"):
                base_models.append(version["baseModel"])

        classification = {
            "primary_type": model_type,
            "base_models": list(set(base_models)),
            "is_checkpoint": model_type == "Checkpoint",
            "is_lora": model_type == "LORA", 
            "is_textual_inversion": model_type == "TextualInversion",
            "is_vae": model_type == "VAE",
            "supports_sdxl": any("SDXL" in bm for bm in base_models),
            "supports_sd15": any("SD 1.5" in bm for bm in base_models),
            "supports_sd21": any("SD 2.1" in bm for bm in base_models)
        }

        return classification

# Usage example
extractor = ModelCardExtractor(api_key="your_api_key")
model_data = extractor.extract_all_model_fields(model_id=123456)
model_classification = extractor.detect_model_type(model_data)
print(json.dumps(model_data, indent=2))
