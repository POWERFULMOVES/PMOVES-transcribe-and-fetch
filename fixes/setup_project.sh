#!/bin/bash
echo "Setting up PMOVES Transcribe and Fetch project..."

# Check if Git LFS is installed
git lfs install
if [ $? -ne 0 ]; then
    echo "Error: Git LFS is not installed. Please install Git LFS and try again."
    echo "Visit https://git-lfs.com for installation instructions."
    exit 1
fi

# Pull LFS content
echo "Pulling LFS content..."
git lfs pull

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    pip install uv
else
    echo "uv is already installed."
fi

# Create virtual environment
echo "Creating Python virtual environment with uv..."
uv venv

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
uv pip install -r requirements.txt

# Create .env file from example
echo "Setting up environment variables..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo ".env file created from example. Please update it with your API keys."
else
    echo ".env file already exists."
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo ""
echo "Setup complete! You can now run:"
echo "- Backend: cd backend && uvicorn app.main:app --reload"
echo "- Frontend: npm run dev"
echo ""
echo "Open http://localhost:3000 in your browser to use the application." 