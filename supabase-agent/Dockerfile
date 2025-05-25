# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed by some Python packages
# Including curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app /app/app
COPY ./cli.py /app/

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
# This should match AGENT_PORT from .env, default is 8002
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

# Define the command to run the application
# The .env file should be loaded by the application itself (python-dotenv)
# For production, consider managing secrets/env vars via Docker Compose, Kubernetes secrets, etc.
# The PYTHONPATH is set to /app so that `from app.utils...` works if main.py is in /app
# However, our main.py is in app/main.py, and it uses `from .utils.agent_framework import AgentFramework`
# which should work correctly with `uvicorn app.main:app` when run from /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
