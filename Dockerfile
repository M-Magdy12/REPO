# Multi-stage build for optimized size
FROM python:3.10-slim as base

# Set environment variables to reduce memory usage
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python packages with minimal memory
# Install packages one by one to avoid memory spikes
RUN pip install --no-cache-dir Flask==3.1.2 && \
    pip install --no-cache-dir gunicorn==23.0.0 && \
    pip install --no-cache-dir pillow==12.0.0 && \
    pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir numpy==2.1.3 && \
    pip install --no-cache-dir scikit-learn==1.5.2 && \
    pip install --no-cache-dir streamlit==1.39.0 && \
    pip install --no-cache-dir pymongo==4.10.1 && \
    pip install --no-cache-dir requests==2.32.3

# Copy application files
COPY flask_app.py .
COPY streamlit_app.py .
COPY model.pt .

# Set environment variable for model path
ENV MODEL_PATH=/app/model.pt

# Expose ports
EXPOSE 5000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/')" || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Flask in background with limited workers\n\
gunicorn --bind 0.0.0.0:5000 \
         --workers 1 \
         --threads 2 \
         --worker-class sync \
         --timeout 120 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --preload \
         flask_app:app &\n\
\n\
# Wait for Flask to start\n\
sleep 5\n\
\n\
# Start Streamlit with memory-efficient settings\n\
streamlit run streamlit_app.py \
          --server.port=8501 \
          --server.address=0.0.0.0 \
          --server.headless=true \
          --server.maxUploadSize=10 \
          --server.enableCORS=false \
          --server.enableXsrfProtection=true \
          --browser.gatherUsageStats=false \
          --logger.level=warning\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
