# Stage 1: Builder
# Use an NVIDIA CUDA image with Python
# Choose an appropriate image based on your CUDA version (e.g., 12.1 as requested) and Python version (3.12)
# Note: Finding an exact match for Python 3.12 on a CUDA 12.1 image might require checking NVIDIA's or PyTorch's specific images.
# This example uses a general CUDA devel image and installs Python 3.12
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 AS builder

# Install Python 3.12 and essential build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.12 python3.12-venv python3.12-distutils curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as the default python
RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python3.12 1 --force && \
    update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3.12 1 --force

# Install uv
RUN pip install uv

# Set the working directory in the builder container
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies with uv, including the specific PyTorch version for CUDA
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Stage 2: Final image
# Use an NVIDIA CUDA runtime image with Python
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 AS final

# Install Python 3.12 and necessary runtime libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.12 python3.12-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as the default python
RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python3.12 1 --force

# Set the working directory in the final container
WORKDIR /usr/src/app

# Copy installed Python packages from the builder stage
# This copies the site-packages directory for Python 3.12
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/lib/python3/dist-packages/ /usr/lib/python3.12/dist-packages/ # Copy system-installed packages if any

# Copy the application code
COPY ./app /usr/src/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the Python path
ENV PYTHONPATH=/usr/src

# Run uvicorn server when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
