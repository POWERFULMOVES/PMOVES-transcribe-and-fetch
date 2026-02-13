#!/bin/bash
# Post-sync script to install PyTorch with CUDA 12.4 support (RTX 5090/Blackwell compatible)
# Run this after `uv sync` to replace CPU torch with CUDA version
uv pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 torchaudio==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
