# Part 1 - Streamlit CivitAI Browser in Cloud Environments - 3. Vast.ai Docker Container
# Generated for comprehensive CivitAI browser implementation


# Dockerfile for Vast.ai
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "civitai_browser.py", "--server.port=8501", "--server.address=0.0.0.0"]

# requirements.txt
# streamlit==1.28.0
# requests==2.31.0  
# pillow==10.0.0
# pandas==2.0.3

# Vast.ai setup:
# 1. Create instance with this Docker image
# 2. Port forward 8501
# 3. Access via provided URL
