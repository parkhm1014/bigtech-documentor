#!/bin/bash
# BigTech Retriever - Manual Setup Script
# For users not using DevContainer

set -e  # Exit on error

echo "=========================================="
echo "BigTech Retriever - Setup Script"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠ Warning: Running as root. Consider using a virtual environment."
fi

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.12"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "✗ Python $REQUIRED_VERSION required, but found $PYTHON_VERSION"
    echo "Please install Python 3.12"
    exit 1
else
    echo "✓ Python $PYTHON_VERSION found"
fi

# Check CUDA
echo ""
echo "Checking CUDA..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep -oP 'release \K[0-9.]+')
    echo "✓ CUDA $CUDA_VERSION found"
else
    echo "✗ CUDA not found. Please install CUDA 12.8"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Check Ubuntu version and Python availability
echo ""
echo "Checking system..."
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
echo "Ubuntu version: $UBUNTU_VERSION"

# Handle PEP 668 for Ubuntu 24.04
if [ "$UBUNTU_VERSION" = "24.04" ]; then
    echo "⚠ Ubuntu 24.04 detected - virtual environment recommended for PEP 668"
fi

# Upgrade pip
echo ""
echo "Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# Install packaging and ninja (required for flash-attn)
echo ""
echo "Installing build dependencies (packaging, ninja)..."
pip install packaging ninja

# Install PyTorch with CUDA 12.8
echo ""
echo "Installing PyTorch with CUDA 12.8..."
echo "This may take several minutes..."
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

# Verify PyTorch CUDA
echo ""
echo "Verifying PyTorch CUDA support..."
python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA not available in PyTorch'; print('✓ PyTorch CUDA support confirmed')"

# Install flash-attention from source
echo ""
echo "Building flash-attention from source..."
echo "This will take 5-15 minutes depending on your CPU..."
echo "Using MAX_JOBS=4 to limit memory usage"
MAX_JOBS=4 pip install flash-attn==2.8.3 --no-build-isolation

# Verify flash-attention
echo ""
echo "Verifying flash-attention..."
python3 -c "import flash_attn; print(f'✓ flash-attn {flash_attn.__version__} installed')"

# Install remaining requirements
echo ""
echo "Installing remaining requirements..."
pip install -r requirements.txt

# Create directories
echo ""
echo "Creating project directories..."
mkdir -p origin images temp_crops figures data ocr_output
echo "✓ Directories created"

# Create .env if not exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env created. Please edit it and add your API keys."
else
    echo "⚠ .env already exists. Skipping."
fi

# Run verification
echo ""
echo "Running installation verification..."
python3 scripts/verify_installation.py

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run Jupyter: jupyter notebook Figure_Extraction_and_QA.ipynb"
echo ""
