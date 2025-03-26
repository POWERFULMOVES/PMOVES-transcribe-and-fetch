@echo off
echo ===================================
echo PMOVES SSE Fixes Installation Script
echo ===================================
echo.

echo Checking for Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

echo Checking for Python...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    exit /b 1
)

echo.
echo Installing dependencies...
echo.

echo Installing Node.js dependencies...
npm install --no-fund --no-audit --loglevel=error axios eventsource fs-extra chalk

echo.
echo Installing Python dependencies...
pip install rich

echo.
echo ===================================
echo Dependencies installed successfully!
echo ===================================
echo.

echo Do you want to apply the fixes now? (Y/N)
set /p APPLY_FIXES=

if /i "%APPLY_FIXES%"=="Y" (
    echo.
    echo Applying fixes...
    echo.
    
    echo 1. Applying backend fixes...
    python fix_sse_v6.py
    
    echo.
    echo 2. Applying frontend fixes...
    node apply_sse_frontend_fixes.js
    
    echo.
    echo 3. Fixing SVG viewBox issues...
    node fix_svg_viewbox.js
    
    echo.
    echo ===================================
    echo All fixes have been applied!
    echo ===================================
) else (
    echo.
    echo You can apply the fixes later by running:
    echo.
    echo python fix_sse_v6.py
    echo node apply_sse_frontend_fixes.js
    echo node fix_svg_viewbox.js
    echo.
    echo Or by running:
    echo.
    echo npm run fix-all
)

echo.
echo Do you want to test the SSE implementation now? (Y/N)
set /p TEST_SSE=

if /i "%TEST_SSE%"=="Y" (
    echo.
    echo Testing SSE implementation...
    echo.
    node test_sse_implementation.js
) else (
    echo.
    echo You can test the SSE implementation later by running:
    echo.
    echo node test_sse_implementation.js
    echo.
    echo Or by running:
    echo.
    echo npm run test
)

echo.
echo ===================================
echo Installation complete!
echo ===================================
echo.
echo For more information, please read README_SSE_FIXES.md
echo.
pause
