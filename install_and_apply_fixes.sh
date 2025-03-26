#!/bin/bash

echo "==================================="
echo "PMOVES SSE Fixes Installation Script"
echo "==================================="
echo ""

# Check for Node.js
echo "Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed or not in PATH."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check for Python
echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo ""

echo "Installing Node.js dependencies..."
npm install --no-fund --no-audit --loglevel=error axios eventsource fs-extra chalk

echo ""
echo "Installing Python dependencies..."
python3 -m pip install rich

echo ""
echo "==================================="
echo "Dependencies installed successfully!"
echo "==================================="
echo ""

# Ask to apply fixes
read -p "Do you want to apply the fixes now? (y/n) " APPLY_FIXES

if [[ $APPLY_FIXES =~ ^[Yy]$ ]]; then
    echo ""
    echo "Applying fixes..."
    echo ""
    
    echo "1. Applying backend fixes..."
    python3 fix_sse_v6.py
    
    echo ""
    echo "2. Applying frontend fixes..."
    node apply_sse_frontend_fixes.js
    
    echo ""
    echo "3. Fixing SVG viewBox issues..."
    node fix_svg_viewbox.js
    
    echo ""
    echo "==================================="
    echo "All fixes have been applied!"
    echo "==================================="
else
    echo ""
    echo "You can apply the fixes later by running:"
    echo ""
    echo "python3 fix_sse_v6.py"
    echo "node apply_sse_frontend_fixes.js"
    echo "node fix_svg_viewbox.js"
    echo ""
    echo "Or by running:"
    echo ""
    echo "npm run fix-all"
fi

# Ask to test SSE implementation
read -p "Do you want to test the SSE implementation now? (y/n) " TEST_SSE

if [[ $TEST_SSE =~ ^[Yy]$ ]]; then
    echo ""
    echo "Testing SSE implementation..."
    echo ""
    node test_sse_implementation.js
else
    echo ""
    echo "You can test the SSE implementation later by running:"
    echo ""
    echo "node test_sse_implementation.js"
    echo ""
    echo "Or by running:"
    echo ""
    echo "npm run test"
fi

echo ""
echo "==================================="
echo "Installation complete!"
echo "==================================="
echo ""
echo "For more information, please read README_SSE_FIXES.md"
echo ""
