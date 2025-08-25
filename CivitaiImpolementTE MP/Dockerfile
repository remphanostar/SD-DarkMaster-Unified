# Vast.ai Optimized Dockerfile for SD-DarkMaster-Pro
FROM nvidia/cuda:11.8-cudnn8-devel-ubuntu22.04

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    unzip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-perftools4 \
    libtcmalloc-minimal4 \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support for Vast.ai GPUs
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install additional AI/ML libraries commonly needed
RUN pip3 install --no-cache-dir \
    xformers \
    accelerate \
    transformers \
    diffusers \
    controlnet_aux \
    opencv-python \
    insightface \
    onnxruntime-gpu

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/models/Stable-diffusion \
    /app/models/VAE \
    /app/models/LoRA \
    /app/models/embeddings \
    /app/models/ControlNet \
    /app/downloads \
    /app/logs \
    /app/temp

# Set permissions
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Expose ports for Streamlit and potential WebUI
EXPOSE 8501 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start script
CMD ["python3", "-m", "streamlit", "run", "sd_darkmaster_streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false"]
