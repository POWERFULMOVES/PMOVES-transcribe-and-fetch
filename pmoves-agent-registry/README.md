# PMOVES Agent Registry Service

A minimal, extensible FastAPI-based service for dynamic agent registration, discovery, and management in the PMOVES platform. Inspired by the LiteLLM registry, this service is designed for easy integration, Dockerization, and future persistence upgrades.

## Features
- REST API for agent registration, update, heartbeat, and discovery
- In-memory agent metadata store (swap for DB later)
- Pydantic schema validation
- Docker-ready
- Designed for orchestrator, UI, and agent integration

## API Endpoints
- `GET /agents` — List all registered agents
- `GET /agents/{agent_id}` — Get details for a specific agent
- `POST /agents/register` — Register or update an agent
- `POST /agents/heartbeat` — Agent health check-in
- `DELETE /agents/{agent_id}` — Deregister an agent

## Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run locally
```bash
uvicorn app.main:app --reload
```

### 3. Build & run with Docker
```bash
docker build -t pmoves-agent-registry .
docker run -p 8000:8000 pmoves-agent-registry
```

## Example: Register an Agent
```bash
curl -X POST http://localhost:8000/agents/register \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": "summarizer-001",
    "name": "SummarizerAgent",
    "description": "Summarizes text content using LLMs.",
    "capabilities": ["summarize", "analyze"],
    "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
    "output_schema": {"type": "object", "properties": {"summary": {"type": "string"}}},
    "status": "active",
    "endpoint": "http://localhost:5001",
    "dependencies": ["llm_registry"],
    "version": "1.0.0",
    "tags": ["text", "llm"],
    "last_heartbeat": "2024-06-01T12:00:00Z",
    "config": {"max_length": 512}
  }'
```

## License
MIT 