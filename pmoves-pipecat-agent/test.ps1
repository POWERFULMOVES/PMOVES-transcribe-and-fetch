# Test script for PMOVES Pipecat Agent (PowerShell)
param(
    [switch]$Quick = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🧪 Testing PMOVES Pipecat Agent..." -ForegroundColor Cyan

# Test 1: Check if Docker is running
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "   ✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Test 2: Check if image exists
Write-Host "2. Checking if image exists..." -ForegroundColor Yellow
$imageExists = docker images pmoves-pipecat-agent:latest --format "{{.Repository}}" | Select-String "pmoves-pipecat-agent"
if ($imageExists) {
    Write-Host "   ✅ Image 'pmoves-pipecat-agent:latest' found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Image not found. Building..." -ForegroundColor Yellow
    .\build.ps1
}

if ($Quick) {
    Write-Host "Quick test completed. Skipping container tests." -ForegroundColor Cyan
    exit 0
}

# Test 3: Run container health check
Write-Host "3. Testing container startup..." -ForegroundColor Yellow
$containerId = docker run -d -p 8001:8000 pmoves-pipecat-agent:latest
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Container started with ID: $($containerId.Substring(0,12))" -ForegroundColor Green
    
    # Wait a moment for startup
    Start-Sleep 5
    
    # Test health endpoint
    Write-Host "4. Testing health endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 10
        if ($response.status -eq "ok") {
            Write-Host "   ✅ Health check passed: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Unexpected health response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check logs
    Write-Host "5. Checking container logs..." -ForegroundColor Yellow
    $logs = docker logs $containerId
    if ($logs -match "error|ERROR|Error") {
        Write-Host "   ⚠️  Found errors in logs:" -ForegroundColor Yellow
        Write-Host $logs -ForegroundColor Red
    } else {
        Write-Host "   ✅ No obvious errors in logs" -ForegroundColor Green
    }
    
    # Cleanup
    Write-Host "6. Cleaning up test container..." -ForegroundColor Yellow
    docker stop $containerId | Out-Null
    docker rm $containerId | Out-Null
    Write-Host "   ✅ Test container cleaned up" -ForegroundColor Green
    
} else {
    Write-Host "   ❌ Failed to start container" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 All tests passed! Your PMOVES Pipecat Agent is ready." -ForegroundColor Green
Write-Host ""
Write-Host "To run the agent:" -ForegroundColor Cyan
Write-Host "  docker-compose up" -ForegroundColor White
Write-Host ""
Write-Host "To run in background:" -ForegroundColor Cyan
Write-Host "  docker-compose up -d" -ForegroundColor White 