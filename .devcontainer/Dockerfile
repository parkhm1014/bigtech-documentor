# BigTech Retriever DevContainer
# CUDA 12.8 + Ubuntu 22.04 + Python 3.12 + Flash Attention

FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set timezone
ENV TZ=UTC

# Add deadsnakes PPA for Python 3.12 (Ubuntu 22.04 default is 3.10)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies
# Optimized order: apt packages rarely change, so cache this layer
RUN apt-get update && apt-get install -y \
    # Python 3.12 from deadsnakes PPA
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    # Build essentials (needed for flash-attn compilation)
    build-essential \
    cmake \
    ninja-build \
    git \
    wget \
    curl \
    # PDF processing
    poppler-utils \
    # Graphics libraries (for matplotlib, PIL, etc.) - Ubuntu 22.04 versions
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Development tools
    vim \
    htop \
    tree \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Create python3 symlink to python3.12
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Install pip for Python 3.12 using get-pip.py (avoids distutils dependency)
RUN wget -q https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# Set working directory
WORKDIR /workspace

# Create directories for data (do this early as it doesn't change)
RUN mkdir -p /workspace/origin \
    /workspace/images \
    /workspace/temp_crops \
    /workspace/figures \
    /workspace/data \
    /workspace/ocr_output

# Upgrade pip, setuptools, wheel
# This layer changes rarely
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install packaging and ninja first (required for flash-attn build)
# Separate layer for build dependencies
RUN pip install --no-cache-dir packaging ninja

# Copy requirements file BEFORE installing PyTorch
# This allows better caching - if requirements.txt doesn't change, skip reinstall
COPY requirements.txt /tmp/requirements.txt

# Install PyTorch with CUDA 12.8 support (install before flash-attn)
# Large download - separate layer for better caching
RUN pip install --no-cache-dir \
    torch==2.7.1 \
    torchvision==0.22.1 \
    torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

# Build and install flash-attention from source
# MAX_JOBS=4 to prevent OOM on systems with <96GB RAM
# This is the slowest step - keep it separate for caching
ENV MAX_JOBS=4
RUN pip install --no-cache-dir flash-attn==2.8.3 --no-build-isolation

# Install remaining requirements
# This layer rebuilds if requirements.txt changes
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Clean up
RUN rm -rf /tmp/* && \
    pip cache purge

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Set Python buffering off for better logging
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["/bin/bash"]
