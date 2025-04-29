#!/bin/bash
# Test script for backend SSE endpoint

echo "Testing backend SSE endpoint..."
echo "This script will connect to the SSE endpoint and display the events received."
echo "Press Ctrl+C to stop the test."
echo ""

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please install curl and try again."
    exit 1
fi

# Check if the backend server is running
echo "Checking if backend server is running..."

# Try multiple endpoints
endpoints=("http://localhost:8000/api/health" "http://localhost:8000/" "http://localhost:8000/api/search/preset-technical")
backend_running=false

for endpoint in "${endpoints[@]}"; do
    echo "Trying to connect to $endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null)
    if [[ "$response" == "200" || "$response" == "204" || "$response" == "302" ]]; then
        backend_running=true
        echo "Successfully connected to $endpoint"
        break
    fi
done

if [ "$backend_running" = false ]; then
    echo "Backend server might not be running or accessible."
    read -p "Do you want to continue anyway? (y/n): " continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Yy](es)?$ ]]; then
        echo "Error: Backend server is not running. Please start the backend server:"
        echo "cd backend && python -m app.main"
        exit 1
    fi
fi

echo "Backend server is running."
echo "Connecting to SSE endpoint..."
echo ""

# Connect to the SSE endpoint
curl -N -H "Accept: text/event-stream" http://localhost:8000/api/search/preset-technical?shocwave=true&max_results=33&run_analysis=true

echo ""
echo "Test completed."
