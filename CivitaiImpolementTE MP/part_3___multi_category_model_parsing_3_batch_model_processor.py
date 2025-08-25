# Part 3 - Multi-Category Model Parsing - 3. Batch Model Processor
# Generated for comprehensive CivitAI browser implementation


# Batch processor for multiple complex models

class BatchModelProcessor:
    def __init__(self, api_key=None):
        self.parser = MultiCategoryModelParser(api_key)
        self.processed_models = {}

    def process_model_list(self, model_ids, max_workers=5):
        """Process multiple models concurrently"""

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
        """Create a matrix of all processed models and their categories"""

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
        """Generate a download script for all recommended files"""

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

        return "
".join(script_lines)

# Streamlit interface for batch processing
def create_batch_processor_ui():
    st.subheader("Batch Model Processor")

    # Input model IDs
    model_ids_input = st.text_area(
        "Model IDs (one per line or comma-separated)",
        placeholder="123456
789012
345678"
    )

    if model_ids_input:
        # Parse model IDs
        model_ids = []
        for line in model_ids_input.strip().split('
'):
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
