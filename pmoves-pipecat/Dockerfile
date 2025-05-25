FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies required for pipecat and audio processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    wget \
    curl \
    git \
    ffmpeg \
    portaudio19-dev \
    libasound2-dev \
    libpulse-dev \
    libsndfile1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install core dependencies first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install with better error handling
COPY requirements.txt .

# Install requirements with retries and better error handling
RUN pip install --no-cache-dir --timeout 300 -r requirements.txt

# Copy service code
COPY . .

# Expose ports for service endpoints
EXPOSE 8080 8081

# Entrypoint: run the core pipecat service
CMD ["python", "main.py"] 