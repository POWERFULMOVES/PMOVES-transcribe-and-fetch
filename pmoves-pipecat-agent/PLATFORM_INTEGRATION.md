# PMOVES Platform Integration Guide

This guide explains how to integrate the Pipecat Agent with the full PMOVES platform.

## Quick Start

### 1. Build the Agent (from this directory)
```powershell
# PowerShell (recommended)
.\build.ps1 -Platform

# Or Command Prompt
build.bat
```

### 2. Run with Platform (from project root)
```bash
# Change to project root
cd ..

# Start just the pipecat agent with dependencies
docker-compose up pmoves-pipecat-agent

# Or start the entire platform
docker-compose up
```

## Platform Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │ Pipecat Agent   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (This Agent)   │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│  LiteLLM Proxy  │◄─────────────┘
                        │   Port: 4000    │
                        └─────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │    Supabase     │    │     MinIO       │
                    │   (Database)    │    │  (S3 Storage)   │
                    │                 │    │  Ports: 9000/1  │
                    └─────────────────┘    └─────────────────┘
```

## Service Communication

### Internal URLs (within Docker network)
- **LiteLLM Proxy**: `http://litellm-proxy:4000`
- **Backend API**: `http://pmoves-backend:8000`
- **Agent Registry**: `http://pmoves-backend:8000/agents`
- **MinIO**: `http://minio:9000`
- **Crawl4AI**: `http://crawl4ai:11235`

### External URLs (from host)
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Pipecat Agent**: `http://localhost:8001`
- **LiteLLM Proxy**: `http://localhost:4000`
- **MinIO Console**: `http://localhost:9001`
- **Crawl4AI**: `http://localhost:11235`

## Environment Variables

The agent automatically receives configuration from the platform's `.env` file:

### Required Platform Variables
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_ID=your_project_id
SUPABASE_KEY=your_service_key

# LiteLLM
LITELLM_MASTER_KEY=your_master_key

# AI Services (fallback)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# MinIO
MINIO_USER=your_minio_user
MINIO_PASSWORD=your_minio_password
```

## Agent Registration Flow

1. **Agent Startup**: Agent starts and reads configuration
2. **Registry Registration**: Agent registers with platform registry
3. **Health Check**: Platform monitors agent health
4. **Service Discovery**: Agent discovers other platform services
5. **Realtime Connection**: Agent connects to Supabase Realtime
6. **Ready State**: Agent is ready to process commands

## Testing Platform Integration

### 1. Check Services
```bash
# From project root
docker-compose ps

# Should show all services running
```

### 2. Test Agent Health
```bash
# Agent health check
curl http://localhost:8001/health

# Platform health check
curl http://localhost:8000/health

# LiteLLM health check
curl http://localhost:4000/health
```

### 3. Check Logs
```bash
# Agent logs
docker-compose logs pmoves-pipecat-agent

# Platform logs
docker-compose logs pmoves-backend
docker-compose logs litellm-proxy
```

## Troubleshooting

### Common Issues

1. **Agent can't connect to LiteLLM**
   ```bash
   # Check LiteLLM proxy is running
   docker-compose logs litellm-proxy
   curl http://localhost:4000/health
   ```

2. **Agent can't register with platform**
   ```bash
   # Check backend is running
   docker-compose logs pmoves-backend
   curl http://localhost:8000/health
   ```

3. **Network issues**
   ```bash
   # Check network exists
   docker network ls | grep pmoves
   
   # Create if missing
   docker network create pmoves-network
   ```

### Debug Commands

```bash
# Check all containers
docker-compose ps

# Check specific service
docker-compose logs -f pmoves-pipecat-agent

# Restart specific service
docker-compose restart pmoves-pipecat-agent

# Rebuild and restart
docker-compose up --build pmoves-pipecat-agent

# Enter container for debugging
docker-compose exec pmoves-pipecat-agent /bin/bash
```

## Development Workflow

### 1. Code Changes
```bash
# Make changes to agent code
# Then rebuild and restart
docker-compose up --build pmoves-pipecat-agent
```

### 2. Configuration Changes
```bash
# Update .env in project root
# Restart services
docker-compose restart pmoves-pipecat-agent
```

### 3. Platform Updates
```bash
# Pull latest platform changes
git pull

# Rebuild everything
docker-compose down
docker-compose up --build
```

## Integration Points

### With Backend API
- Agent registration and heartbeat
- Supabase proxy requests
- File upload/download coordination

### With LiteLLM Proxy
- Model selection and routing
- Streaming LLM responses
- Function call processing

### With Supabase Realtime
- Chat message processing
- Real-time communication
- User presence tracking

### With MinIO
- File storage and retrieval
- Media processing
- Backup coordination

This integration ensures the Pipecat Agent works seamlessly with your PMOVES platform architecture! 