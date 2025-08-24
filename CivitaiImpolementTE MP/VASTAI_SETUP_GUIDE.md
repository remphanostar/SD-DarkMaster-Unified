# Complete Vast.ai Setup Guide for SD-DarkMaster-Pro

## 🚀 Quick Start on Vast.ai

### Step 1: Rent Vast.ai Instance

1. **Visit [vast.ai](https://vast.ai)** and create account
2. **Browse instances** with these recommended specs:
   - **GPU:** RTX 3090, RTX 4090, A100, or similar
   - **VRAM:** 12GB+ (16GB+ recommended for SDXL)
   - **RAM:** 32GB+
   - **Storage:** 100GB+ SSD
   - **Bandwidth:** High up/down speeds

3. **Click "Rent"** on your chosen instance

### Step 2: Deploy Your Application

#### Option A: Quick Docker Deploy
```bash
# SSH into your Vast.ai instance
ssh root@your-vast-ip

# Pull and run the container
docker run -d --gpus all \
  -p 8501:8501 -p 7860:7860 \
  -v /workspace/models:/app/models \
  -v /workspace/downloads:/app/downloads \
  your-dockerhub/sd-darkmaster-pro:vastai
```

#### Option B: Build from Source
```bash
# Clone your repository
git clone https://github.com/your-repo/sd-darkmaster-pro.git
cd sd-darkmaster-pro

# Build Vast.ai optimized image
docker build -f Dockerfile -t sd-darkmaster-pro:vastai .

# Run with GPU support
docker run -d --gpus all \
  -p 8501:8501 -p 7860:7860 \
  -v /workspace:/app/workspace \
  sd-darkmaster-pro:vastai
```

### Step 3: Access Your Application

1. **Find your Vast.ai IP** from the dashboard
2. **Access Streamlit:** `http://YOUR_VAST_IP:8501`
3. **Access WebUI:** `http://YOUR_VAST_IP:7860` (after launching)

## 🎯 Vast.ai Optimizations Included

### GPU Memory Management
- **Automatic GPU detection** and optimization
- **Dynamic VRAM allocation** based on available memory
- **Memory-efficient attention** mechanisms
- **Automatic mixed precision** when beneficial

### Performance Enhancements
- **Concurrent downloads** optimized for Vast.ai bandwidth
- **Model caching** to reduce load times
- **Resource monitoring** to prevent OOM errors
- **Temperature monitoring** to prevent throttling

### User Experience
- **Real-time resource monitoring** in sidebar
- **Vast.ai instance detection** and status
- **Public tunnel creation** for external access
- **Automatic environment setup** and optimization

## 💡 Pro Tips for Vast.ai

### Cost Optimization
- **Use spot instances** for 60-80% cost savings
- **Monitor usage** with built-in resource monitor
- **Auto-shutdown** when idle to save costs
- **Bulk download** models during setup

### Performance Tips
- **Choose instances** with high connectivity scores
- **Use SSD storage** for faster model loading
- **Enable persistent storage** to avoid re-downloads
- **Monitor GPU temperature** to prevent throttling

### Troubleshooting
- **GPU not detected:** Check CUDA installation and drivers
- **Out of memory:** Reduce batch size or enable --medvram
- **Slow downloads:** Check Vast.ai instance location and bandwidth
- **Connection issues:** Verify ports are open in Vast.ai dashboard

## 🔧 Advanced Configuration

### Custom Environment Variables
```bash
export CIVITAI_API_KEY="your_key_here"
export HF_TOKEN="your_token_here"
export VASTAI_OPTIMIZE_MEMORY=true
export WEBUI_ARGS="--xformers --opt-split-attention"
```

### Persistent Storage Setup
```bash
# Create persistent directories
mkdir -p /workspace/{models,downloads,outputs}

# Link to application
ln -sf /workspace/models /app/models
ln -sf /workspace/downloads /app/downloads
```

## 📊 Resource Requirements

| Model Type | Min VRAM | Recommended VRAM | Batch Size |
|------------|----------|------------------|------------|
| SD 1.5     | 6GB      | 8GB+            | 4-8        |
| SDXL       | 8GB      | 12GB+           | 2-4        |
| SDXL + LoRAs | 12GB   | 16GB+           | 1-2        |

## 🛡️ Security Notes

- **Change default passwords** if using authentication
- **Use SSH tunneling** for sensitive operations
- **Enable firewall rules** as needed
- **Backup important data** regularly

## 📞 Support

- **GitHub Issues:** For bugs and feature requests
- **Discord:** Real-time community support
- **Documentation:** Comprehensive guides and tutorials

This Vast.ai integration provides enterprise-grade performance with consumer-friendly simplicity.
