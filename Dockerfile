# ----------------------------
# Base Image
# ----------------------------
FROM python:3.11-slim

# ----------------------------
# Environment
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ----------------------------
# Working Directory
# ----------------------------
WORKDIR /app

# ----------------------------
# System Packages
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Install Python Dependencies
# ----------------------------
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ----------------------------
# Copy Project
# ----------------------------
COPY . .

# ----------------------------
# Expose Port
# ----------------------------
EXPOSE 8000

# ----------------------------
# Health Check
# ----------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# ----------------------------
# Start Server
# ----------------------------
CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
    "--proxy-headers",
    "--workers",
    "1"
]