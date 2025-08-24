# SD-DarkMaster-Pro UI Comprehensive Requirements Document

## Project Overview
SD-DarkMaster-Pro is a unified Stable Diffusion model management system designed to run on Google Colab and other cloud platforms. It provides a dark-themed Streamlit interface for managing, browsing, downloading, and organizing AI models from multiple sources, with automatic WebUI launching capabilities.

## Core Design Principles
1. **Dark Theme**: Entire UI must be dark (#0e0e0e background) with red (#ef4444) accent colors
2. **No Tab Jumping**: All tabs must maintain consistent heights to prevent layout shifts
3. **Toggle Selection**: Models are selected via full-width toggle buttons that change color (dark gray to red) when selected
4. **Single Download Action**: One unified download button for all selected models, no individual download buttons
5. **Persistent State**: All selections must persist during tab navigation
6. **Mobile-Responsive**: UI must work on different screen sizes

## Complete UI Structure

### Top Level - Header
- **Title**: "🌟 SD-DarkMaster-Pro Dashboard" (large, white text)
- **Subtitle**: "Unified Model Management System" (smaller, gray caption)

### Main Navigation - Level 1 Tabs
Two primary tabs that divide the entire functionality:

#### Tab 1: "Models"
**Purpose**: Browse and select pre-configured models from dictionaries and local storage
**Content**: All available models organized by type and category

#### Tab 2: "Model Search"  
**Purpose**: Search, browse, and download new models from external sources
**Content**: Search interfaces for different model repositories

---

## MODELS TAB - Complete Structure

### Level 2 - Model Type Tabs (under Models)
#### Tab: "SDXL"
**Purpose**: Contains all SDXL-based models (excluding Pony/Illustrious variants)

##### Level 3 - SDXL Sub-categories
1. **Tab: "Model"**
   - **Purpose**: SDXL checkpoint files (main model files)
   - **Display**: 2-column grid of toggle buttons
   - **Each button shows**: Model name (truncated to 40 chars) + file size
   - **Interaction**: Click button to toggle selection (gray→red when selected)
   - **Data source**: `_xl_models_data.py` dictionary, filtered for non-pony/illustrious

2. **Tab: "Lora"**
   - **Purpose**: SDXL LoRA files (smaller model modifications)
   - **Display**: Same 2-column toggle button grid
   - **Content**: SDXL-specific LoRA models

3. **Tab: "Etc"**
   - **Purpose**: Additional SDXL model types
   - **Sub-tabs within**:
     - **VAE**: Variational Autoencoder models for SDXL
     - **ControlNet**: Control models for SDXL
     - **Embeddings**: Textual inversion embeddings for SDXL

#### Tab: "etc"
**Purpose**: All other model types not in main SDXL category

##### Level 3 - Other Model Types
1. **Tab: "SD-1.5"**
   - **Sub-tabs**:
     - **Models**: SD 1.5 checkpoint files
     - **Loras**: SD 1.5 LoRA files  
     - **VAE**: SD 1.5 VAE models
     - **ControlNet**: SD 1.5 ControlNet models
   - **Data source**: `_models_data.py` dictionary
   - **Display**: Same 2-column toggle button grid

2. **Tab: "Pony"**
   - **Purpose**: Pony Diffusion models (SDXL-based anime style)
   - **Display**: Toggle buttons for all pony models
   - **Data source**: SDXL dictionary filtered for 'pony' in name

3. **Tab: "Illustrious"**
   - **Purpose**: Illustrious models (SDXL-based anime style)
   - **Display**: Toggle buttons for illustrious models
   - **Data source**: SDXL dictionary filtered for 'illustrious' in name

4. **Tab: "Misc"**
   - **Purpose**: Extension-specific models
   - **Sub-tabs**:
     - **SAM**: Segment Anything models for masking
     - **ADetailer**: Face/hand detection models
     - **Upscaler**: ESRGAN/RealESRGAN upscaling models
     - **Reactor**: Face swap models
   - **Data source**: `MODEL_REGISTRY` from `setup_central_storage.py`

---

## MODEL SEARCH TAB - Complete Structure

### Level 2 - Search Source Tabs (under Model Search)

#### Tab: "CivitAI Search"
**Purpose**: Search and download models from CivitAI.com

##### Level 3 - CivitAI View Modes
1. **Tab: "Model page basic + pic basic"**
   - **Purpose**: Quick search with preview images
   - **Components**:
     - Search input field (placeholder: "anime, realistic, etc...")
     - Type dropdown: ["All", "Checkpoint", "LORA", "VAE", "ControlNet", "TextualInversion"]
     - Search button (triggers API call)
     - Results grid: 3-column layout with:
       - Model preview image
       - Model name
       - Creator name
       - Download count
       - Rating stars
       - Quick "Add to Queue" button

2. **Tab: "Verbose every detail"**
   - **Purpose**: Display COMPLETE information from CivitAI API
   - **Components**:
     - Model ID input field
     - "Load Full Details" button
   - **Display sections** (all expandable):
     - **Statistics Bar**: Downloads, Likes, Rating, Reviews, Comments (metrics display)
     - **Description**: Full markdown description from creator
     - **Tags Section**: All tags as clickable pills
     - **Model Versions**: 
       - Version name
       - Base model (SD1.5/SDXL/etc)
       - Created date
       - Download count per version
       - File size
       - File format (safetensors/ckpt)
       - FP precision (fp16/fp32)
       - Trigger words (for LoRAs)
       - Training details
       - Individual file downloads with hashes
     - **Creator Information**:
       - Avatar image
       - Username
       - Creator stats
       - Link to other models
     - **Metadata**:
       - Model type
       - NSFW flag (with 🔞 icon if true)
       - POI flag (with ⚠️ if true)
       - Commercial use allowed
       - Derivatives allowed
       - License information
     - **Sample Images Gallery**:
       - Up to 20 sample images in grid
       - Each image expandable to show:
         - Full positive prompt
         - Negative prompt
         - Generation settings:
           - Steps
           - Sampler (DPM++, Euler a, etc)
           - CFG Scale
           - Seed
           - Size (dimensions)
           - Model hash
           - Clip skip
           - Any LoRAs used
           - Any embeddings used
     - **Reviews Section**: User reviews and ratings
     - **Discussion/Comments**: User comments thread

3. **Tab: "Download Queue"**
   - **Purpose**: Manage CivitAI-specific download queue
   - **Display**: List of queued items with:
     - Model name
     - Version
     - File size
     - Remove button
     - Reorder drag handles

#### Tab: "HF Search"
**Purpose**: Search and download from HuggingFace
**Components**:
- Search input (placeholder: "stabilityai/stable-diffusion...")
- Repository browser
- File tree viewer
- Multi-select for files
- "Add to Queue" button

#### Tab: "Browse local PC (not colab instance actual PC)"
**Purpose**: Upload models from user's LOCAL computer to Colab
**Important Note**: Must clearly indicate this accesses the user's actual computer, NOT the Colab instance
**Components**:
- File uploader (multi-select enabled)
- Accepted formats: .safetensors, .ckpt, .pt, .bin
- File list showing:
  - Filename
  - File size in MB
  - Upload progress bar per file
  - "Start Upload" button per file
- Clear indication: "This uploads from YOUR computer to the cloud instance"

#### Tab: "Queue"
**Purpose**: Master queue showing ALL selected items from ALL sources
**Sections**:
1. **Summary Cards**:
   - Total selected models (from Models tab)
   - Total queued downloads (from search tabs)
   - Total file size estimate
   - Estimated download time

2. **Selected Models Section**:
   - Header: "Models Selected from Library"
   - List showing:
     - Model type icon (🎨 for checkpoint, 🎭 for LoRA, etc)
     - Full model path/name
     - Size
     - Source (SD1.5/SDXL/Pony/etc)
     - Individual remove button

3. **Download Queue Section**:
   - Header: "Models to Download"
   - List showing:
     - Source icon (CivitAI/HF/Upload)
     - Model name
     - Version (if applicable)
     - File size
     - Download URL/path
     - Individual remove button

4. **Action Buttons**:
   - "Download All" - primary green button
   - "Clear Queue" - secondary button
   - "Export List" - saves queue as JSON

---

## Bottom Control Section (Always Visible)

### Download Control Bar
**Location**: Below all tabs, always visible
**Layout**: 3 columns

#### Column 1 (2 units wide):
- **Download Button**: 
  - Green gradient background (#10b981 to #059669)
  - Text: "📥 Download (X models)" where X is total count
  - Shows sum of selected + queued items
  - Pulses when items are selected

#### Column 2 (6 units wide):
- **Progress Bar**:
  - Shows 0% when idle
  - Green fill (#10b981) during download
  - Caption below: "Ready to download X items" or "Downloading... X%"
  - Shows current file being downloaded

#### Column 3 (2 units wide):
- **Clear All Button**:
  - Text: "🧹 Clear All"
  - Clears both selections and queue
  - Confirmation dialog on click

### Output Console
**Purpose**: Show system activity and logs
**Location**: Bottom of page
**Features**:
- Dark background (#1e1e1e)
- Green text (#10b981) for success
- Red text (#ef4444) for errors  
- Shows last 10 log entries
- Auto-scrolls to bottom
- Monospace font
- Sample messages:
  - "[+] Selected: model_name"
  - "[-] Deselected: model_name"
  - "🚀 Starting download of X models..."
  - "✅ Downloaded: model_name (234.5 MB)"
  - "❌ Error: Failed to download model_name"
  - "📊 Queue updated: X items"

### Statistics Bar
**Location**: Very bottom
**Layout**: 4 equal columns showing metrics:
1. **Selected**: Count of toggle-selected models
2. **Queued**: Count of items in download queue
3. **Downloaded**: Count of successfully downloaded models
4. **Storage**: Total GB used

---

## Visual Design Requirements

### Color Scheme
- **Background**: #0e0e0e (near black)
- **Card/Panel Background**: #1a1a1a (dark gray)
- **Borders**: #2a2a2a (lighter gray)
- **Text Primary**: #ffffff (white)
- **Text Secondary**: #888888 (gray)
- **Accent/Selected**: #ef4444 (red)
- **Success**: #10b981 (green)
- **Warning**: #f59e0b (orange)
- **Error**: #ef4444 (red)

### Button States
- **Default**: Background #1a1a1a, Border #2a2a2a
- **Hover**: Background #2a2a2a, Border #ef4444
- **Selected**: Background #ef4444, Border #dc2626
- **Disabled**: Opacity 0.5

### Typography
- **Title**: 32px, bold
- **Headers**: 20px, semi-bold
- **Tab Labels**: 14px, medium
- **Button Text**: 15px, medium
- **Body Text**: 14px, regular
- **Console Text**: 13px, monospace

### Spacing
- **Tab Height**: Minimum 42px (prevents jumping)
- **Button Padding**: 12px vertical, 20px horizontal
- **Grid Gap**: 12px between items
- **Section Margin**: 20px between major sections

### Responsive Breakpoints
- **Desktop**: >1024px (2-3 column grids)
- **Tablet**: 768-1024px (2 column grids)
- **Mobile**: <768px (single column)

---

## Functional Requirements

### State Management
- All selections persist across tab navigation
- Download queue persists until explicitly cleared
- Search results cache for 5 minutes
- Output log maintains last 100 entries

### API Integration
- CivitAI API v1 for model search and details
- HuggingFace API for repository browsing
- Async downloading with aria2c (16 connections)
- Progress callbacks for real-time updates

### Error Handling
- Network timeouts after 30 seconds
- Retry failed downloads 3 times
- Show clear error messages in output console
- Graceful degradation if APIs unavailable

### Performance
- Lazy load images in galleries
- Paginate search results (20 per page)
- Virtual scrolling for long lists
- Debounce search input (500ms)

---

## Platform-Specific Features

### Google Colab
- Auto-detect Colab environment
- Use ngrok for public URL if needed
- Mount Google Drive for persistent storage
- Show GPU/RAM usage in stats

### Local/Other Platforms
- Detect platform (Kaggle, Paperspace, etc)
- Adjust paths accordingly
- Support local file system browsing
- No ngrok needed for local

---

## Critical Implementation Notes

1. **NO CHECKBOXES** - Only toggle buttons for selection
2. **NO INDIVIDUAL DOWNLOADS** - Single unified download action
3. **CONSISTENT TAB HEIGHTS** - Use CSS min-height to prevent jumping
4. **PERSISTENT COLORS** - Selected items must stay red even after clicking
5. **CLEAR QUEUE INDICATION** - User must always know what will be downloaded
6. **VERBOSE MEANS EVERYTHING** - The verbose tab must show ALL available API data
7. **LOCAL PC CLARITY** - Must be crystal clear that local browse accesses user's computer, not cloud instance

This comprehensive specification defines every element, its purpose, and its behavior in the SD-DarkMaster-Pro UI system.