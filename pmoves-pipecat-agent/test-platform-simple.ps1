# Simple Platform Integration Test - Connect to Host Services
Write-Host "=== PMOVES Pipecat Agent Platform Integration Test ===" -ForegroundColor Green

# Check if platform services are running on host
Write-Host "Checking platform services..." -ForegroundColor Yellow

# Check LiteLLM proxy
try {
    $litellmResponse = Invoke-WebRequest -Uri "http://localhost:4000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ LiteLLM proxy running on host:4000" -ForegroundColor Green
} catch {
    Write-Host "✗ LiteLLM proxy not accessible on host:4000" -ForegroundColor Red
    exit 1
}

# Check backend
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend running on host:8000" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backend not accessible on host:8000 (may be normal)" -ForegroundColor Yellow
}

# Run agent with host service URLs
Write-Host "Starting agent with platform integration..." -ForegroundColor Yellow
$containerId = docker run --rm -d `
    --name pmoves-pipecat-agent-platform `
    -p 8001:8000 `
    --network pmoves-network `
    --add-host host.docker.internal:host-gateway `
    --env-file ../backend/app/.env `
    -e PLATFORM_MODE=true `
    -e LITELLM_PROXY_URL=http://host.docker.internal:4000 `
    -e AGENT_REGISTRY_URL=http://host.docker.internal:8000 `
    -e SUPABASE_BACKEND_URL=http://host.docker.internal:8000 `
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
        
        # Test platform connectivity
        Write-Host "`nTesting platform connectivity..." -ForegroundColor Yellow
        try {
            $configResponse = Invoke-WebRequest -Uri "http://localhost:8001/config" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✓ Agent can access configuration" -ForegroundColor Green
        } catch {
            Write-Host "⚠ Config endpoint requires authentication (expected)" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "✗ Agent health check failed: $_" -ForegroundColor Red
        Write-Host "`nAgent logs:" -ForegroundColor Yellow
        docker logs $containerId --tail 20
    }
    
    Write-Host "`n=== Agent is running in platform mode ===" -ForegroundColor Green
    Write-Host "Agent Health: http://localhost:8001/health" -ForegroundColor Cyan
    Write-Host "Platform LiteLLM: http://localhost:4000" -ForegroundColor Cyan
    Write-Host "Platform Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "`nTo stop: docker stop $containerId" -ForegroundColor Yellow
    
} else {
    Write-Host "✗ Failed to start agent container" -ForegroundColor Red
    exit 1
} 