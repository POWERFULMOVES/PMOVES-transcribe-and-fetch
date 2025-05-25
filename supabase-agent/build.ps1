# PowerShell Build Script for Supabase Agent on Windows
# This script builds the Docker image for the Supabase Agent

param(
    [string]$ImageName = "pmoves-supabase-agent",
    [string]$Tag = "latest",
    [switch]$NoBuildCache = $false,
    [switch]$Verbose = $false
)

Write-Host "=== PMOVES Supabase Agent Build Script ===" -ForegroundColor Green
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

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    if (Test-Path "env-template.txt") {
        Write-Host "Found env-template.txt. Please copy it to .env and configure your settings:" -ForegroundColor Yellow
        Write-Host "copy env-template.txt .env" -ForegroundColor Cyan
        Write-Host "Then edit .env with your Supabase credentials" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "Please create a .env file with your configuration" -ForegroundColor Red
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

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
Write-Host "Command: docker $($buildArgs -join ' ')" -ForegroundColor Gray

try {
    & docker $buildArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
        Write-Host "Image: $ImageName`:$Tag" -ForegroundColor Cyan
        
        # Show image size
        $imageInfo = docker images $ImageName --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | Select-Object -Skip 1
        Write-Host "Size: $imageInfo" -ForegroundColor Cyan
        
        Write-Host "`n=== Next Steps ===" -ForegroundColor Green
        Write-Host "1. To run standalone: docker-compose up" -ForegroundColor White
        Write-Host "2. To run with full platform: docker-compose -f ../docker-compose.yml up" -ForegroundColor White
        Write-Host "3. To test the agent: docker run --rm -p 8002:8002 --env-file .env $ImageName`:$Tag" -ForegroundColor White
        Write-Host "4. Health check: curl http://localhost:8002/health" -ForegroundColor White
        
    } else {
        Write-Host "✗ Docker build failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error during Docker build: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Green 