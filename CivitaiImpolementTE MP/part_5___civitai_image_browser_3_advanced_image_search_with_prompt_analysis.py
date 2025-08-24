# Part 5 - CivitAI Image Browser - 3. Advanced Image Search with Prompt Analysis
# Generated for comprehensive CivitAI browser implementation


# Advanced image search with prompt analysis and filtering

import streamlit as st
import requests
import re
from collections import Counter
import pandas as pd
from textstat import flesch_reading_ease
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')  
except LookupError:
    nltk.download('stopwords')

class AdvancedImageSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        self.stop_words = set(stopwords.words('english'))

    def create_advanced_search_interface(self):
        """Create advanced image search with prompt analysis"""

        st.title("🔍 Advanced Image Search & Analysis")

        # Search configuration
        with st.sidebar:
            st.header("🔧 Search Configuration")

            # API Key
            api_key = st.text_input("CivitAI API Key", type="password")
            if api_key:
                self.api_key = api_key

            # Basic search parameters
            st.subheader("Basic Parameters")
            sort_by = st.selectbox("Sort By", ["Most Reactions", "Most Comments", "Newest"])
            limit = st.slider("Results per search", 20, 200, 100)

            # Prompt analysis filters
            st.subheader("Prompt Analysis")

            min_prompt_length = st.slider("Min prompt length", 0, 500, 0)
            max_prompt_length = st.slider("Max prompt length", 100, 2000, 2000)

            # Keyword filtering
            required_keywords = st.text_input("Required keywords (comma-separated)")
            excluded_keywords = st.text_input("Excluded keywords (comma-separated)")

            # Style analysis
            style_categories = st.multiselect("Style Categories", [
                "Photography", "Anime", "Realistic", "Artistic", "Abstract",
                "Portrait", "Landscape", "Character", "Fantasy", "Sci-fi"
            ])

            # Technical parameters
            st.subheader("Technical Filters")

            min_resolution = st.selectbox("Minimum Resolution", [
                "Any", "512x512", "768x768", "1024x1024", "1536x1536"
            ])

            aspect_ratios = st.multiselect("Aspect Ratios", [
                "Square (1:1)", "Portrait (3:4)", "Landscape (4:3)", 
                "Wide (16:9)", "Ultra-wide (21:9)"
            ])

        # Main search interface
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🎯 Smart Search")

            search_mode = st.radio("Search Mode", [
                "Prompt Keywords", "Style Similarity", "Technical Parameters", "Advanced Query"
            ])

            if search_mode == "Prompt Keywords":
                search_query = st.text_input("Search in prompts", 
                                           placeholder="beautiful landscape, sunset, detailed")

            elif search_mode == "Style Similarity":
                reference_prompt = st.text_area("Reference prompt for style matching",
                                               placeholder="Paste a prompt to find similar styles")

            elif search_mode == "Technical Parameters":
                st.write("Use the sidebar filters for technical parameter search")
                search_query = ""

            elif search_mode == "Advanced Query":
                search_query = st.text_area("Advanced search query",
                                          placeholder="Complex search with AND/OR operators")

        with col2:
            if st.button("🔍 Execute Search", type="primary"):
                self.execute_advanced_search(
                    search_mode=search_mode,
                    query=locals().get('search_query', '') or locals().get('reference_prompt', ''),
                    sort_by=sort_by,
                    limit=limit,
                    filters={
                        'min_prompt_length': min_prompt_length,
                        'max_prompt_length': max_prompt_length,
                        'required_keywords': required_keywords,
                        'excluded_keywords': excluded_keywords,
                        'style_categories': style_categories,
                        'min_resolution': min_resolution,
                        'aspect_ratios': aspect_ratios
                    }
                )

        # Analysis tools
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Analyze Current Results"):
                self.analyze_search_results()

        with col2:
            if st.button("🏷️ Extract Popular Tags"):
                self.extract_trending_tags()

    def execute_advanced_search(self, search_mode, query, sort_by, limit, filters):
        """Execute advanced search with filtering"""

        # Get images from API
        with st.spinner("Searching images..."):
            raw_results = self.get_images_batch(sort_by, limit)

        if not raw_results:
            st.error("No images found or API error")
            return

        # Apply advanced filters
        filtered_results = self.apply_advanced_filters(raw_results, search_mode, query, filters)

        # Display results
        st.success(f"Found {len(filtered_results)} images matching criteria")

        # Store results for analysis
        st.session_state.current_results = filtered_results

        # Display images
        self.display_filtered_results(filtered_results)

    def get_images_batch(self, sort_by, limit):
        """Get batch of images from API"""

        params = {
            "limit": min(limit, 200),  # API limit
            "sort": sort_by
        }

        if self.api_key:
            params["token"] = self.api_key

        response = requests.get(f"{self.base_url}/images", params=params)

        if response.status_code == 200:
            return response.json().get("items", [])

        return []

    def apply_advanced_filters(self, images, search_mode, query, filters):
        """Apply advanced filtering to image results"""

        filtered = []

        for image in images:
            if self.passes_filters(image, search_mode, query, filters):
                filtered.append(image)

        return filtered

    def passes_filters(self, image, search_mode, query, filters):
        """Check if image passes all filters"""

        meta = image.get('meta', {})
        prompt = meta.get('prompt', '').lower()
        negative_prompt = meta.get('negativePrompt', '').lower()

        # Prompt length filter
        prompt_length = len(prompt)
        if prompt_length < filters['min_prompt_length'] or prompt_length > filters['max_prompt_length']:
            return False

        # Required keywords
        if filters['required_keywords']:
            required = [kw.strip().lower() for kw in filters['required_keywords'].split(',')]
            if not all(kw in prompt for kw in required):
                return False

        # Excluded keywords
        if filters['excluded_keywords']:
            excluded = [kw.strip().lower() for kw in filters['excluded_keywords'].split(',')]
            if any(kw in prompt for kw in excluded):
                return False

        # Resolution filter
        if filters['min_resolution'] != "Any":
            min_res = int(filters['min_resolution'].split('x')[0])
            if image.get('width', 0) < min_res or image.get('height', 0) < min_res:
                return False

        # Aspect ratio filter
        if filters['aspect_ratios']:
            image_ratio = self.get_aspect_ratio_category(image.get('width', 1), image.get('height', 1))
            if image_ratio not in filters['aspect_ratios']:
                return False

        # Style category filter
        if filters['style_categories']:
            image_style = self.categorize_image_style(prompt)
            if not any(style.lower() in image_style.lower() for style in filters['style_categories']):
                return False

        # Search mode specific filtering
        if search_mode == "Prompt Keywords" and query:
            query_words = query.lower().split()
            if not any(word in prompt for word in query_words):
                return False

        elif search_mode == "Style Similarity" and query:
            similarity_score = self.calculate_style_similarity(prompt, query.lower())
            if similarity_score < 0.3:  # Threshold
                return False

        return True

    def get_aspect_ratio_category(self, width, height):
        """Categorize aspect ratio"""

        if width == 0 or height == 0:
            return "Unknown"

        ratio = width / height

        if 0.95 <= ratio <= 1.05:
            return "Square (1:1)"
        elif ratio < 0.95:
            return "Portrait (3:4)"
        elif 1.25 <= ratio <= 1.45:
            return "Landscape (4:3)"
        elif 1.7 <= ratio <= 1.9:
            return "Wide (16:9)"
        elif ratio > 2.0:
            return "Ultra-wide (21:9)"
        else:
            return "Other"

    def categorize_image_style(self, prompt):
        """Categorize image style based on prompt"""

        style_keywords = {
            "Photography": ["photo", "photograph", "realistic", "photorealistic", "camera", "lens"],
            "Anime": ["anime", "manga", "cel shading", "kawaii", "chibi", "otaku"],
            "Realistic": ["realistic", "photorealistic", "lifelike", "detailed", "high resolution"],
            "Artistic": ["painting", "artwork", "artistic", "brush strokes", "canvas"],
            "Abstract": ["abstract", "surreal", "conceptual", "experimental"],
            "Portrait": ["portrait", "face", "headshot", "close-up"],
            "Landscape": ["landscape", "scenery", "nature", "outdoor", "vista"],
            "Character": ["character", "person", "figure", "human"],
            "Fantasy": ["fantasy", "magical", "dragon", "wizard", "mythical"],
            "Sci-fi": ["sci-fi", "futuristic", "cyberpunk", "space", "robot"]
        }

        detected_styles = []
        prompt_lower = prompt.lower()

        for style, keywords in style_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_styles.append(style)

        return ", ".join(detected_styles) if detected_styles else "General"

    def calculate_style_similarity(self, prompt1, prompt2):
        """Calculate style similarity between two prompts"""

        # Simple word overlap similarity
        words1 = set(word_tokenize(prompt1.lower())) - self.stop_words
        words2 = set(word_tokenize(prompt2.lower())) - self.stop_words

        if not words1 or not words2:
            return 0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0

    def display_filtered_results(self, images):
        """Display filtered search results"""

        # Display options
        col1, col2, col3 = st.columns(3)

        with col1:
            display_mode = st.selectbox("Display Mode", ["Grid", "List", "Detailed"])

        with col2:
            sort_results = st.selectbox("Sort Results", ["Relevance", "Resolution", "Prompt Length"])

        with col3:
            images_per_page = st.selectbox("Images per page", [10, 20, 50])

        # Sort results
        if sort_results == "Resolution":
            images = sorted(images, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
        elif sort_results == "Prompt Length":
            images = sorted(images, key=lambda x: len(x.get('meta', {}).get('prompt', '')), reverse=True)

        # Pagination
        total_pages = (len(images) - 1) // images_per_page + 1
        page = st.selectbox("Page", range(1, total_pages + 1))

        start_idx = (page - 1) * images_per_page
        end_idx = start_idx + images_per_page
        page_images = images[start_idx:end_idx]

        # Display based on mode
        if display_mode == "Grid":
            self.display_image_grid(page_images)
        elif display_mode == "List":
            self.display_image_list(page_images)
        else:
            self.display_detailed_view(page_images)

    def display_image_grid(self, images):
        """Display images in grid format"""

        cols = st.columns(3)

        for i, image in enumerate(images):
            with cols[i % 3]:
                st.image(image['url'], use_column_width=True)

                # Basic info
                st.write(f"**{image['width']}x{image['height']}**")

                # Prompt preview
                prompt = image.get('meta', {}).get('prompt', '')
                if prompt:
                    st.write(f"*{prompt[:50]}...*" if len(prompt) > 50 else f"*{prompt}*")

                # Metadata button
                if st.button(f"Details", key=f"details_{image['id']}"):
                    st.session_state.selected_image = image

    def analyze_search_results(self):
        """Analyze current search results"""

        if 'current_results' not in st.session_state:
            st.warning("No search results to analyze")
            return

        images = st.session_state.current_results

        st.subheader("📊 Search Results Analysis")

        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Images", len(images))

        with col2:
            avg_resolution = sum(img.get('width', 0) * img.get('height', 0) for img in images) / len(images)
            st.metric("Avg Resolution", f"{avg_resolution/1000000:.1f}MP")

        with col3:
            avg_prompt_length = sum(len(img.get('meta', {}).get('prompt', '')) for img in images) / len(images)
            st.metric("Avg Prompt Length", f"{avg_prompt_length:.0f}")

        with col4:
            nsfw_count = sum(1 for img in images if img.get('nsfw', False))
            st.metric("NSFW Images", f"{nsfw_count}/{len(images)}")

        # Prompt analysis
        st.subheader("🏷️ Prompt Analysis")

        all_prompts = [img.get('meta', {}).get('prompt', '') for img in images]
        all_words = []

        for prompt in all_prompts:
            words = word_tokenize(prompt.lower())
            all_words.extend([word for word in words if word.isalpha() and word not in self.stop_words])

        # Most common words
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(20)

        if top_words:
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Most Common Words:**")
                for word, count in top_words[:10]:
                    st.write(f"• {word}: {count}")

            with col2:
                # Word frequency chart
                words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                st.bar_chart(words_df.set_index('Word'))

        # Style distribution
        st.subheader("🎨 Style Distribution")

        styles = [self.categorize_image_style(img.get('meta', {}).get('prompt', '')) for img in images]
        style_counter = Counter([style for style_list in styles for style in style_list.split(', ')])

        if style_counter:
            style_df = pd.DataFrame(style_counter.most_common(), columns=['Style', 'Count'])
            st.bar_chart(style_df.set_index('Style'))

    def extract_trending_tags(self):
        """Extract and display trending tags"""

        if 'current_results' not in st.session_state:
            st.warning("No search results available")
            return

        st.subheader("🏷️ Trending Tags & Patterns")

        images = st.session_state.current_results

        # Extract all prompts
        prompts = [img.get('meta', {}).get('prompt', '') for img in images if img.get('meta', {}).get('prompt')]

        # Tag extraction patterns
        tag_patterns = [
            (r'\b(\w+)\s+style\b', 'Style Tags'),
            (r'\b(\w+)\s+art\b', 'Art Tags'),
            (r'\b(beautiful|gorgeous|stunning|amazing)\s+(\w+)\b', 'Quality Tags'),
            (r'\((\w+):[0-9.]+\)', 'Weighted Tags'),
            (r'<lora:([^:>]+):', 'LoRA Tags')
        ]

        for pattern, category in tag_patterns:
            st.write(f"**{category}:**")

            matches = []
            for prompt in prompts:
                matches.extend(re.findall(pattern, prompt, re.IGNORECASE))

            if matches:
                # Flatten tuples if necessary
                flat_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        flat_matches.extend(match)
                    else:
                        flat_matches.append(match)

                tag_counter = Counter(flat_matches)
                top_tags = tag_counter.most_common(10)

                for tag, count in top_tags:
                    st.write(f"• {tag}: {count}")
            else:
                st.write("No matches found")

            st.write("")

def main():
    st.set_page_config(
        page_title="Advanced Image Search",
        page_icon="🔍",
        layout="wide"
    )

    search_engine = AdvancedImageSearch()
    search_engine.create_advanced_search_interface()

if __name__ == "__main__":
    main()
