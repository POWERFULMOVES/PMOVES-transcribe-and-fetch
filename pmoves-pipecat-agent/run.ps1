# PowerShell Run Script for PMOVES Pipecat Agent on Windows
# This script runs the Pipecat Agent with proper configuration

param(
    [string]$Mode = "standalone", # standalone, platform, test
    [string]$ImageName = "pmoves-pipecat-agent",
    [string]$Tag = "latest",
    [switch]$Build = $false,
    [switch]$Detached = $false,
    [switch]$Logs = $false
)

Write-Host "=== PMOVES Pipecat Agent Run Script ===" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Cyan

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

# Build if requested
if ($Build) {
    Write-Host "Building image first..." -ForegroundColor Yellow
    & .\build.ps1 -ImageName $ImageName -Tag $Tag
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Build failed" -ForegroundColor Red
        exit 1
    }
}

# Check for environment files
$envPath = "..\backend\app\.env"
$localEnvPath = ".env"

Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path $envPath) {
    Write-Host "✓ Found environment file at: $envPath" -ForegroundColor Green
    $useEnvFile = $envPath
} elseif (Test-Path $localEnvPath) {
    Write-Host "✓ Found local environment file: $localEnvPath" -ForegroundColor Green
    $useEnvFile = $localEnvPath
} else {
    Write-Host "⚠ Warning: No .env file found" -ForegroundColor Yellow
    $useEnvFile = $null
}

# Create network if it doesn't exist (for standalone and test modes)
if ($Mode -eq "standalone" -or $Mode -eq "test") {
    Write-Host "Checking for pmoves-network..." -ForegroundColor Yellow
    $networkExists = docker network ls --filter name=pmoves-network --format "{{.Name}}" | Where-Object { $_ -eq "pmoves-network" }
    if (-not $networkExists) {
        Write-Host "Creating pmoves-network..." -ForegroundColor Yellow
        docker network create pmoves-network
        Write-Host "✓ Network created" -ForegroundColor Green
    } else {
        Write-Host "✓ Network exists" -ForegroundColor Green
    }
}

# Run based on mode
switch ($Mode) {
    "standalone" {
        Write-Host "Running in standalone mode..." -ForegroundColor Yellow
        $composeArgs = @("up")
        if ($Detached) { $composeArgs += "-d" }
        
        try {
            & docker-compose $composeArgs
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Pipecat Agent is running!" -ForegroundColor Green
                Write-Host "Health check: http://localhost:8001/health" -ForegroundColor Cyan
                Write-Host "WebSocket: ws://localhost:8001/ws" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "✗ Failed to start: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    "platform" {
        Write-Host "Running with PMOVES platform integration..." -ForegroundColor Yellow
        Write-Host "Connecting to existing pmoves-network and platform services..." -ForegroundColor Cyan
        
        # Check if pmoves-network exists (should be created by platform)
        $networkExists = docker network ls --filter name=pmoves-network --format "{{.Name}}" | Where-Object { $_ -eq "pmoves-network" }
        if (-not $networkExists) {
            Write-Host "⚠ Warning: pmoves-network not found. Creating it..." -ForegroundColor Yellow
            docker network create pmoves-network
        }
        
        try {
            $composeArgs = @("-f", "docker-compose.yml", "-f", "docker-compose.platform.yml", "up")
            if ($Detached) { $composeArgs += "-d" }
            
            & docker-compose $composeArgs pmoves-pipecat-agent
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Pipecat Agent connected to platform!" -ForegroundColor Green
                Write-Host "Agent Health: http://localhost:8001/health" -ForegroundColor Cyan
                Write-Host "Platform Backend: http://localhost:8000" -ForegroundColor Cyan
                Write-Host "Platform LiteLLM: http://localhost:4000" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "✗ Failed to start agent: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    "test" {
        Write-Host "Running test container..." -ForegroundColor Yellow
        $runArgs = @(
            "run", "--rm", 
            "-p", "8001:8000",
            "--network", "pmoves-network"
        )
        
        # Add environment file if available
        if ($useEnvFile) {
            $runArgs += "--env-file"
            $runArgs += $useEnvFile
        }
        
        $runArgs += "$ImageName`:$Tag"
        
        Write-Host "Command: docker $($runArgs -join ' ')" -ForegroundColor Gray
        & docker $runArgs
    }
    
    default {
        Write-Host "Invalid mode: $Mode" -ForegroundColor Red
        Write-Host "Valid modes: standalone, platform, test" -ForegroundColor Yellow
        exit 1
    }
}

if ($Logs -and $Mode -ne "test") {
    Write-Host "`nShowing logs..." -ForegroundColor Yellow
    Start-Sleep 2
    if ($Mode -eq "standalone") {
        docker-compose logs -f pipecat-agent
    } else {
        Push-Location ..
        docker-compose logs -f pipecat-agent
        Pop-Location
    }
}

Write-Host "`n=== Agent Started ===" -ForegroundColor Green 