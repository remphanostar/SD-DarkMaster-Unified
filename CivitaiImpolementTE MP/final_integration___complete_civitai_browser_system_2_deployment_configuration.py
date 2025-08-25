# Final Integration - Complete CivitAI Browser System - 2. Deployment Configuration
# Generated for comprehensive CivitAI browser implementation


# Complete deployment configuration for all cloud platforms

# requirements.txt for the complete application
requirements_txt = '''
# Core dependencies
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.3
numpy>=1.24.0
pillow>=10.0.0

# API clients
huggingface_hub>=0.17.0
transformers>=4.30.0

# Data processing
nltk>=3.8
textstat>=0.7.0

# Visualization
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Async and utilities
aiohttp>=3.8.0
asyncio
concurrent.futures
pathlib
json
re
datetime
time
base64
io
zipfile
os
hashlib

# Optional dependencies for advanced features
sentence-transformers>=2.2.0
opencv-python>=4.8.0
scikit-learn>=1.3.0
'''

# Docker configuration
dockerfile_content = '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "master_browser.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''

# Docker Compose for local development
docker_compose_content = '''
version: '3.8'

services:
  civitai-browser:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./downloads:/app/downloads
      - ./cache:/app/.streamlit/cache
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - civitai-browser
    restart: unless-stopped

volumes:
  downloads:
  cache:
'''

# Nginx configuration
nginx_conf = '''
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server civitai-browser:8501;
    }

    server {
        listen 80;
        server_name localhost;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name localhost;

        # SSL configuration (add your certificates)
        # ssl_certificate /etc/nginx/ssl/cert.pem;
        # ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Streamlit specific configuration
        location / {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_read_timeout 86400;
        }

        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://streamlit;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''

# Kubernetes deployment
k8s_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civitai-browser
  labels:
    app: civitai-browser
spec:
  replicas: 3
  selector:
    matchLabels:
      app: civitai-browser
  template:
    metadata:
      labels:
        app: civitai-browser
    spec:
      containers:
      - name: civitai-browser
        image: civitai-browser:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_HEADLESS
          value: "true"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: downloads
          mountPath: /app/downloads
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: downloads
        persistentVolumeClaim:
          claimName: civitai-downloads-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: civitai-browser-service
spec:
  selector:
    app: civitai-browser
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: civitai-downloads-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
'''

# Heroku Procfile and configuration
procfile = '''
web: streamlit run master_browser.py --server.port=$PORT --server.address=0.0.0.0
'''

heroku_runtime = '''
python-3.9.18
'''

# Railway deployment
railway_config = '''
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run master_browser.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health"
  }
}
'''

# Streamlit Cloud config
streamlit_config = '''
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
'''

# Environment variables template
env_template = '''
# CivitAI Configuration
CIVITAI_API_KEY=your_civitai_api_key_here
CIVITAI_BASE_URL=https://civitai.com/api/v1

# Hugging Face Configuration  
HF_TOKEN=your_huggingface_token_here
HF_BASE_URL=https://huggingface.co/api

# Application Settings
DEFAULT_DOWNLOAD_DIR=./downloads
MAX_CONCURRENT_DOWNLOADS=5
CACHE_TTL=3600

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=your_secret_key_here

# Performance
MAX_UPLOAD_SIZE=200
TIMEOUT_SECONDS=30
'''

# Installation scripts
install_script_unix = '''#!/bin/bash

echo "🚀 Installing CivitAI Master Browser..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv civitai_browser_env
source civitai_browser_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create directories
mkdir -p downloads
mkdir -p cache
mkdir -p logs

# Set permissions
chmod +x run.sh

echo "✅ Installation complete!"
echo "🚀 Run './run.sh' to start the application"
'''

install_script_windows = '''@echo off
echo 🚀 Installing CivitAI Master Browser...

:: Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv civitai_browser_env
call civitai_browser_env\Scripts\activate.bat

:: Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Download NLTK data
echo 📚 Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

:: Create directories
if not exist downloads mkdir downloads
if not exist cache mkdir cache
if not exist logs mkdir logs

echo ✅ Installation complete!
echo 🚀 Run 'run.bat' to start the application
pause
'''

# Run scripts
run_script_unix = '''#!/bin/bash

# Activate virtual environment
source civitai_browser_env/bin/activate

# Set environment variables
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false

# Start the application
echo "🚀 Starting CivitAI Master Browser..."
echo "📱 Open http://localhost:8501 in your browser"
streamlit run master_browser.py
'''

run_script_windows = '''@echo off
call civitai_browser_env\Scripts\activate.bat

set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_ENABLE_CORS=false

echo 🚀 Starting CivitAI Master Browser...
echo 📱 Open http://localhost:8501 in your browser
streamlit run master_browser.py
'''

# Write all configuration files
deployment_files = {
    "requirements.txt": requirements_txt,
    "Dockerfile": dockerfile_content,
    "docker-compose.yml": docker_compose_content,
    "nginx.conf": nginx_conf,
    "k8s-deployment.yaml": k8s_deployment,
    "Procfile": procfile,
    "runtime.txt": heroku_runtime,
    "railway.json": railway_config,
    ".streamlit/config.toml": streamlit_config,
    ".env.template": env_template,
    "install.sh": install_script_unix,
    "install.bat": install_script_windows,
    "run.sh": run_script_unix,
    "run.bat": run_script_windows
}

# Create deployment directory structure
import os
deployment_dir = "deployment_configs"
os.makedirs(deployment_dir, exist_ok=True)
os.makedirs(f"{deployment_dir}/.streamlit", exist_ok=True)

for filename, content in deployment_files.items():
    filepath = os.path.join(deployment_dir, filename)

    # Create subdirectories if needed
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

print("✅ Created comprehensive deployment configurations:")
for filename in deployment_files.keys():
    print(f"  📁 {filename}")

print("\n🚀 Ready for deployment on:")
print("  • 🐳 Docker & Docker Compose")
print("  • ☸️ Kubernetes")
print("  • 🟣 Heroku")
print("  • 🚂 Railway")
print("  • ☁️ Streamlit Cloud")
print("  • 💻 Local installation (Windows/Unix)")

