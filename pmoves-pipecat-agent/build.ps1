# PowerShell Build Script for PMOVES Pipecat Agent on Windows
# This script builds the Docker image for the Pipecat Agent with proper dependencies

param(
    [string]$ImageName = "pmoves-pipecat-agent",
    [string]$Tag = "latest",
    [switch]$NoBuildCache = $false,
    [switch]$Verbose = $false
)

Write-Host "=== PMOVES Pipecat Agent Build Script ===" -ForegroundColor Green
Write-Host "Building Docker image: $ImageName`:$Tag" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Red
    exit 1
}

# Check for environment file in the backend directory
$envPath = "..\backend\app\.env"
$localEnvPath = ".env"

Write-Host "Checking for environment configuration..." -ForegroundColor Yellow
if (Test-Path $envPath) {
    Write-Host "✓ Found environment file at: $envPath" -ForegroundColor Green
} elseif (Test-Path $localEnvPath) {
    Write-Host "✓ Found local environment file: $localEnvPath" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: No .env file found" -ForegroundColor Yellow
    Write-Host "Expected locations:" -ForegroundColor Yellow
    Write-Host "  - $envPath (recommended)" -ForegroundColor Gray
    Write-Host "  - $localEnvPath (local)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "You can continue building, but you'll need to provide environment variables at runtime." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Build command preparation
$buildArgs = @("build", "-t", "$ImageName`:$Tag", ".")

if ($NoBuildCache) {
    $buildArgs += "--no-cache"
    Write-Host "Building without cache..." -ForegroundColor Yellow
}

if ($Verbose) {
    $buildArgs += "--progress=plain"
}

Write-Host "Building PMOVES Pipecat Agent Docker image..." -ForegroundColor Yellow
Write-Host "Command: docker $($buildArgs -join ' ')" -ForegroundColor Gray

try {
    & docker $buildArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
        Write-Host "Image: $ImageName`:$Tag" -ForegroundColor Cyan
        
        # Show image size
        $imageInfo = docker images $ImageName --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | Select-Object -Skip 1
        if ($imageInfo) {
            Write-Host "Size: $imageInfo" -ForegroundColor Cyan
        }
        
        Write-Host "`n=== Next Steps ===" -ForegroundColor Green
        Write-Host "1. To run standalone: .\run.ps1 -Mode standalone" -ForegroundColor White
        Write-Host "2. To run with platform: .\run.ps1 -Mode platform" -ForegroundColor White
        Write-Host "3. To test the agent: .\run.ps1 -Mode test" -ForegroundColor White
        Write-Host "4. Health check: curl http://localhost:8001/health" -ForegroundColor White
        
    } else {
        Write-Host "✗ Docker build failed" -ForegroundColor Red
        Write-Host "Check the error messages above for details" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error during Docker build: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Green 