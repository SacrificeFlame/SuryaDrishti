FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal - removed GUI deps to reduce size)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements (try production first, fallback to regular)
COPY requirements*.txt ./

# Install Python dependencies
# Use CPU-only PyTorch to reduce image size from 8GB to ~2GB
RUN pip install --no-cache-dir --upgrade pip && \
    (pip install --no-cache-dir -r requirements-production.txt 2>/dev/null || \
     pip install --no-cache-dir -r requirements.txt) && \
    pip cache purge

# Copy application code (excludes large files via .dockerignore)
COPY . .

# Create directories for data and models
RUN mkdir -p /app/data /app/models

# Clean up Python cache to reduce image size
RUN find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete 2>/dev/null || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

