#!/bin/bash

# Run the SSE backend fixes
echo "Running SSE backend fixes..."

echo "1. Applying download status updates fix..."
python fix_sse_backend_simple.py
if [ $? -ne 0 ]; then
    echo "Error applying download status updates fix. Please check the logs."
    exit 1
fi

echo "2. Applying transcription status updates fix..."
python fix_sse_transcription_updates.py
if [ $? -ne 0 ]; then
    echo "Error applying transcription status updates fix. Please check the logs."
    exit 1
fi

echo "All SSE fixes applied successfully!"
echo "Please restart your backend server to apply the changes."
