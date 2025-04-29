@echo off
echo Running SSE backend fixes...

echo 1. Applying download status updates fix...
python fix_sse_backend_simple.py
if %ERRORLEVEL% NEQ 0 (
    echo Error applying download status updates fix. Please check the logs.
    exit /b 1
)

echo 2. Applying transcription status updates fix...
python fix_sse_transcription_updates.py
if %ERRORLEVEL% NEQ 0 (
    echo Error applying transcription status updates fix. Please check the logs.
    exit /b 1
)

echo All SSE fixes applied successfully!
echo Please restart your backend server to apply the changes.
