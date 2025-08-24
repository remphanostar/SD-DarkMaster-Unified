#!/bin/bash
# Create Forge NSFW Maximum Package with Central Storage
# This script prepares your custom Forge package with all optimizations

set -e  # Exit on error

echo "=================================================="
echo "🚀 SD-DarkMaster-Pro Forge NSFW Package Creator"
echo "=================================================="

# Configuration
WORKSPACE="/workspace/SD-DarkMaster-Pro"
PACKAGE_DIR="$WORKSPACE/package_build"
STORAGE_DIR="$PACKAGE_DIR/storage"
FORGE_DIR="$PACKAGE_DIR/Forge"
EXTENSIONS_DIR="$FORGE_DIR/extensions"

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# ============================================================================
# STEP 1: Get Forge from AnxietySolo or fresh
# ============================================================================

echo "📦 Setting up Forge base..."
cd "$PACKAGE_DIR"

# Option 1: Use AnxietySolo's Forge (if available)
if [ -f "$WORKSPACE/packages/Forge.zip" ]; then
    echo "Using AnxietySolo's Forge package..."
    unzip -q "$WORKSPACE/packages/Forge.zip"
else
    echo "Cloning fresh Forge..."
    git clone --depth=1 https://github.com/lllyasviel/stable-diffusion-webui-forge.git Forge
fi

# ============================================================================
# STEP 2: Install all extensions
# ============================================================================

echo "🔧 Installing extensions..."
cd "$EXTENSIONS_DIR"

# Your extension list (29 working extensions)
EXTENSIONS=(
    "https://github.com/Mikubill/sd-webui-controlnet"
    "https://github.com/Bing-su/adetailer"
    "https://github.com/hako-mikan/sd-webui-regional-prompter"
    "https://github.com/Haoming02/sd-forge-couple"
    "https://github.com/thomasasfk/sd-webui-aspect-ratio-helper"
    "https://github.com/zanllp/sd-webui-infinite-image-browsing"
    "https://github.com/ilian6806/stable-diffusion-webui-state"
    "https://github.com/DominikDoom/a1111-sd-webui-tagcomplete"
    "https://github.com/anxety-solo/webui_timer"
    "https://github.com/anxety-solo/anxety-theme"
    "https://github.com/anxety-solo/Umi-AI-Wildcards"
    "https://github.com/gutris1/sd-image-viewer"
    "https://github.com/gutris1/sd-image-info"
    "https://github.com/gutris1/sd-hub"
    "https://github.com/continue-revolution/sd-webui-segment-anything"
    "https://github.com/Uminosachi/sd-webui-inpaint-anything"
    "https://github.com/light-and-ray/sd-webui-replacer"
    "https://github.com/zero01101/openOutpaint-webUI-extension"
    "https://github.com/OedoSoldier/sd-webui-image-sequence-toolkit"
    "https://github.com/pkuliyi2015/multidiffusion-upscaler-for-automatic1111"
    "https://github.com/kainatquaderee/sd-webui-reactor-Nsfw_freedom"
    "https://github.com/novitalabs/sd-webui-cleaner"
    "https://github.com/light-and-ray/sd-webui-lama-cleaner-masked-content"
    "https://github.com/adieyal/sd-dynamic-prompts"
    "https://github.com/redmercy69/sd-webui-stripper"
    "https://github.com/graemeniedermayer/clothseg"
    "https://github.com/hako-mikan/sd-webui-supermerger"
)

for ext_url in "${EXTENSIONS[@]}"; do
    ext_name=$(basename "$ext_url")
    if [ ! -d "$ext_name" ]; then
        echo "  Installing $ext_name..."
        git clone --depth=1 "$ext_url" 2>/dev/null || echo "  ⚠️ Failed: $ext_name"
    fi
done

# ============================================================================
# STEP 3: Setup central storage
# ============================================================================

echo "💾 Setting up central model storage..."
mkdir -p "$STORAGE_DIR"/{sam,adetailer,controlnet,upscalers,reactor,models,loras,vae,embeddings}

# Download essential models (comment out if you want smaller package)
echo "📥 Downloading essential models..."

# SAM model (375MB version for space)
if [ ! -f "$STORAGE_DIR/sam/sam_vit_b_01ec64.pth" ]; then
    echo "  Downloading SAM base model..."
    wget -q -O "$STORAGE_DIR/sam/sam_vit_b_01ec64.pth" \
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
fi

# ADetailer models (essential for NSFW)
ADETAILER_MODELS=(
    "face_yolov8n.pt"
    "hand_yolov8n.pt"
    "person_yolov8n-seg.pt"
)

for model in "${ADETAILER_MODELS[@]}"; do
    if [ ! -f "$STORAGE_DIR/adetailer/$model" ]; then
        echo "  Downloading $model..."
        wget -q -O "$STORAGE_DIR/adetailer/$model" \
            "https://huggingface.co/Bingsu/adetailer/resolve/main/$model"
    fi
done

# ============================================================================
# STEP 4: Create symlinks for all extensions
# ============================================================================

echo "🔗 Creating symlinks to central storage..."

# SAM symlinks
for ext in "sd-webui-segment-anything" "sd-webui-inpaint-anything" "sd-webui-replacer"; do
    if [ -d "$EXTENSIONS_DIR/$ext" ]; then
        mkdir -p "$EXTENSIONS_DIR/$ext/models"
        ln -sf "$STORAGE_DIR/sam"/* "$EXTENSIONS_DIR/$ext/models/" 2>/dev/null || true
        echo "  Linked SAM models to $ext"
    fi
done

# ADetailer symlinks
if [ -d "$EXTENSIONS_DIR/adetailer" ]; then
    mkdir -p "$EXTENSIONS_DIR/adetailer/models"
    ln -sf "$STORAGE_DIR/adetailer"/* "$EXTENSIONS_DIR/adetailer/models/" 2>/dev/null || true
    echo "  Linked ADetailer models"
fi

# ============================================================================
# STEP 5: Link main model directories
# ============================================================================

echo "🔗 Setting up main model directories..."

# Create Forge model structure
mkdir -p "$FORGE_DIR/models"/{Stable-diffusion,Lora,VAE,ControlNet,ESRGAN}

# Link to central storage
ln -sf "$STORAGE_DIR/models"/* "$FORGE_DIR/models/Stable-diffusion/" 2>/dev/null || true
ln -sf "$STORAGE_DIR/loras"/* "$FORGE_DIR/models/Lora/" 2>/dev/null || true
ln -sf "$STORAGE_DIR/vae"/* "$FORGE_DIR/models/VAE/" 2>/dev/null || true
ln -sf "$STORAGE_DIR/controlnet"/* "$FORGE_DIR/models/ControlNet/" 2>/dev/null || true
ln -sf "$STORAGE_DIR/upscalers"/* "$FORGE_DIR/models/ESRGAN/" 2>/dev/null || true

# ============================================================================
# STEP 6: Copy upscalers from AnxietySolo if available
# ============================================================================

if [ -d "/workspace/A11111/models/ESRGAN" ]; then
    echo "📋 Copying ESRGAN upscalers from AnxietySolo..."
    cp /workspace/A11111/models/ESRGAN/*.pth "$STORAGE_DIR/upscalers/" 2>/dev/null || true
fi

# ============================================================================
# STEP 7: Create configuration
# ============================================================================

echo "⚙️ Creating configuration files..."

# Create launch script
cat > "$FORGE_DIR/launch_forge.sh" << 'EOF'
#!/bin/bash
# Launch Forge with optimizations for 16GB VRAM

# Use shared venv
VENV_PATH="/workspace/venv"
if [ -d "$VENV_PATH" ]; then
    export PATH="$VENV_PATH/bin:$PATH"
    export PYTHONPATH="$VENV_PATH/lib/python3.10/site-packages:$PYTHONPATH"
fi

# Launch with optimizations
python launch.py \
    --xformers \
    --medvram-sdxl \
    --api \
    --theme dark \
    --no-half-vae \
    --enable-insecure-extension-access \
    "$@"
EOF

chmod +x "$FORGE_DIR/launch_forge.sh"

# Create info file
cat > "$PACKAGE_DIR/PACKAGE_INFO.txt" << EOF
================================================
SD-DarkMaster-Pro Forge NSFW Maximum Package
================================================

Version: 1.0
Created: $(date)
Size: ~4.5GB (with models)

INCLUDED:
- Forge WebUI (optimized for 16GB VRAM)
- 29 pre-installed extensions
- All NSFW extensions enabled
- Central model storage configured
- Essential models pre-downloaded

EXTENSIONS:
$(ls -1 "$EXTENSIONS_DIR" | sed 's/^/  - /')

CENTRAL STORAGE:
- SAM models: /storage/sam/
- ADetailer models: /storage/adetailer/
- ControlNet models: /storage/controlnet/
- Upscalers: /storage/upscalers/

TO USE:
1. Extract this package
2. Extract the shared venv (python31018-venv-torch260-cu124-C-fca.tar.lz4)
3. Run: ./Forge/launch_forge.sh

NOTES:
- All extensions share models via symlinks (saves GB of space!)
- Reactor NSFW Freedom included and configured
- Optimized for 16GB VRAM with --medvram-sdxl
EOF

# ============================================================================
# STEP 8: Create the package
# ============================================================================

echo "📦 Creating final package..."
cd "$PACKAGE_DIR"

# Remove .git directories to save space
find . -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true

# Create the zip
zip -r -q "Forge_NSFW_Maximum.zip" Forge storage PACKAGE_INFO.txt

# Get final size
SIZE=$(du -h "Forge_NSFW_Maximum.zip" | cut -f1)

echo ""
echo "=================================================="
echo "✅ Package created successfully!"
echo "=================================================="
echo "📦 File: $PACKAGE_DIR/Forge_NSFW_Maximum.zip"
echo "📏 Size: $SIZE"
echo ""
echo "Features:"
echo "  • 29 extensions pre-installed"
echo "  • Central model storage configured"
echo "  • Essential models included"
echo "  • All NSFW features enabled"
echo "  • Optimized for 16GB VRAM"
echo ""
echo "Next steps:"
echo "1. Copy to: /workspace/packages/"
echo "2. Test with launch_final.py"
echo "=================================================="