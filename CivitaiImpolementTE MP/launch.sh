#!/bin/bash
# Vast.ai Launch Script for SD-DarkMaster-Pro

echo "🚀 Starting SD-DarkMaster-Pro on Vast.ai..."

# Set Vast.ai environment variables
export CUDA_VISIBLE_DEVICES=0
export TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8

# Create necessary directories
mkdir -p /app/models/{Stable-diffusion,VAE,Lora,embeddings,ControlNet}
mkdir -p /app/{downloads,outputs,logs}

# Check GPU
nvidia-smi

# Start Streamlit application
python3 -m streamlit run vastai_optimized_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
