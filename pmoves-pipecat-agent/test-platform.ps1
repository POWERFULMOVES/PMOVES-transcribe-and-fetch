# Simple Platform Integration Test
Write-Host "=== PMOVES Pipecat Agent Platform Test ===" -ForegroundColor Green

# Check if pmoves-network exists
Write-Host "Checking pmoves-network..." -ForegroundColor Yellow
$networkExists = docker network ls --filter name=pmoves-network --format "{{.Name}}" | Where-Object { $_ -eq "pmoves-network" }
if ($networkExists) {
    Write-Host "✓ pmoves-network found" -ForegroundColor Green
} else {
    Write-Host "✗ pmoves-network not found" -ForegroundColor Red
    exit 1
}

# Check if LiteLLM proxy is running on platform
Write-Host "Checking platform LiteLLM proxy..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Platform LiteLLM proxy is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Platform LiteLLM proxy not accessible: $_" -ForegroundColor Red
    exit 1
}

# Run agent in platform mode
Write-Host "Starting agent in platform mode..." -ForegroundColor Yellow
$containerId = docker run --rm -d `
    --name pmoves-pipecat-agent-platform `
    -p 8001:8000 `
    --network pmoves-network `
    --env-file ../backend/app/.env `
    -e PLATFORM_MODE=true `
    -e LITELLM_PROXY_URL=http://litellm-proxy:4000 `
    -e AGENT_REGISTRY_URL=http://pmoves-backend:8000 `
    pmoves-pipecat-agent:latest

if ($containerId) {
    Write-Host "✓ Agent container started: $containerId" -ForegroundColor Green
    
    # Wait for startup
    Write-Host "Waiting for agent to start..." -ForegroundColor Yellow
    Start-Sleep 10
    
    # Test health endpoint
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 10 -ErrorAction Stop
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "✓ Agent health check passed" -ForegroundColor Green
        Write-Host "  Status: $($healthData.status)" -ForegroundColor Cyan
        Write-Host "  Type: $($healthData.agent_type)" -ForegroundColor Cyan
        Write-Host "  Capabilities: $($healthData.capabilities -join ', ')" -ForegroundColor Cyan
    } catch {
        Write-Host "✗ Agent health check failed: $_" -ForegroundColor Red
    }
    
    # Show logs
    Write-Host "`nAgent logs:" -ForegroundColor Yellow
    docker logs $containerId --tail 20
    
    # Cleanup
    Write-Host "`nStopping test container..." -ForegroundColor Yellow
    docker stop $containerId | Out-Null
    Write-Host "✓ Test complete" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start agent container" -ForegroundColor Red
    exit 1
} 