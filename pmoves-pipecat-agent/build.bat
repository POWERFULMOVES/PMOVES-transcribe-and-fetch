@echo off
setlocal enabledelayedexpansion

REM Build script for PMOVES Pipecat Agent (Windows)
echo Building PMOVES Pipecat Agent Docker image...

REM Clean up any previous builds
echo Cleaning up previous builds...
docker system prune -f

REM Try building with the main requirements.txt first
echo Attempting build with individual pipecat extras...
docker build -t pmoves-pipecat-agent:latest -f Dockerfile .
if %ERRORLEVEL% equ 0 (
    echo ✅ Build successful with individual pipecat extras!
    goto :success
)

echo ❌ Build failed with individual extras. Trying alternative approach...

REM If that fails, try with the alternative requirements
echo Attempting build with combined pipecat extras...
copy requirements.txt requirements-backup.txt >nul
copy requirements-alternative.txt requirements.txt >nul

docker build -t pmoves-pipecat-agent:latest -f Dockerfile .
if %ERRORLEVEL% equ 0 (
    echo ✅ Build successful with combined pipecat extras!
    echo Note: Using requirements-alternative.txt for successful build
    goto :restore_and_success
) else (
    echo ❌ Build failed with both approaches. Check the logs above.
    REM Restore original requirements
    copy requirements-backup.txt requirements.txt >nul
    del requirements-backup.txt >nul
    exit /b 1
)

:restore_and_success
REM Restore original requirements
copy requirements-backup.txt requirements.txt >nul
del requirements-backup.txt >nul

:success
echo 🎉 Docker image built successfully as 'pmoves-pipecat-agent:latest'
echo.
echo To run the container:
echo   docker run -p 8000:8000 pmoves-pipecat-agent:latest
echo.
echo Or use docker-compose:
echo   docker-compose up
echo.
echo For development with live reload:
echo   docker-compose up --build
pause 