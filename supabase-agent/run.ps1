# PowerShell Run Script for Supabase Agent on Windows
# This script runs the Supabase Agent with proper configuration

param(
    [string]$Mode = "standalone", # standalone, platform, test
    [string]$ImageName = "pmoves-supabase-agent",
    [string]$Tag = "latest",
    [switch]$Build = $false,
    [switch]$Detached = $false,
    [switch]$Logs = $false
)

Write-Host "=== PMOVES Supabase Agent Run Script ===" -ForegroundColor Green
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

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    if (Test-Path "env-template.txt") {
        Write-Host "Found env-template.txt. Please copy it to .env and configure your settings:" -ForegroundColor Yellow
        Write-Host "copy env-template.txt .env" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "Please create a .env file with your configuration" -ForegroundColor Red
        exit 1
    }
}

# Create network if it doesn't exist (for standalone mode)
if ($Mode -eq "standalone") {
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
                Write-Host "✓ Supabase Agent is running!" -ForegroundColor Green
                Write-Host "Health check: http://localhost:8002/health" -ForegroundColor Cyan
                Write-Host "API docs: http://localhost:8002/docs" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "✗ Failed to start: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    "platform" {
        Write-Host "Running with full PMOVES platform..." -ForegroundColor Yellow
        Push-Location ..
        try {
            $composeArgs = @("-f", "docker-compose.yml", "up")
            if ($Detached) { $composeArgs += "-d" }
            
            & docker-compose $composeArgs
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Full platform is running!" -ForegroundColor Green
                Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
                Write-Host "Supabase Agent: http://localhost:8002/health" -ForegroundColor Cyan
                Write-Host "LiteLLM Proxy: http://localhost:4000" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "✗ Failed to start platform: $_" -ForegroundColor Red
            exit 1
        } finally {
            Pop-Location
        }
    }
    
    "test" {
        Write-Host "Running test container..." -ForegroundColor Yellow
        $runArgs = @(
            "run", "--rm", 
            "-p", "8002:8002",
            "--env-file", ".env",
            "--network", "pmoves-network",
            "$ImageName`:$Tag"
        )
        
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
        docker-compose logs -f supabase-agent
    } else {
        Push-Location ..
        docker-compose logs -f supabase-agent
        Pop-Location
    }
}

Write-Host "`n=== Agent Started ===" -ForegroundColor Green 