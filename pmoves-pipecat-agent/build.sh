#!/bin/bash

# Build script for PMOVES Pipecat Agent
set -e

echo "Building PMOVES Pipecat Agent Docker image..."

# Clean up any previous builds
echo "Cleaning up previous builds..."
docker system prune -f

# Try building with the main requirements.txt first
echo "Attempting build with individual pipecat extras..."
if docker build -t pmoves-pipecat-agent:latest -f Dockerfile .; then
    echo "✅ Build successful with individual pipecat extras!"
    exit 0
fi

echo "❌ Build failed with individual extras. Trying alternative approach..."

# If that fails, try with the alternative requirements
echo "Attempting build with combined pipecat extras..."
cp requirements.txt requirements-backup.txt
cp requirements-alternative.txt requirements.txt

if docker build -t pmoves-pipecat-agent:latest -f Dockerfile .; then
    echo "✅ Build successful with combined pipecat extras!"
    echo "Note: Using requirements-alternative.txt for successful build"
else
    echo "❌ Build failed with both approaches. Check the logs above."
    # Restore original requirements
    cp requirements-backup.txt requirements.txt
    rm requirements-backup.txt
    exit 1
fi

# Restore original requirements
cp requirements-backup.txt requirements.txt
rm requirements-backup.txt

echo "🎉 Docker image built successfully as 'pmoves-pipecat-agent:latest'"
echo ""
echo "To run the container:"
echo "  docker run -p 8000:8000 pmoves-pipecat-agent:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up" 