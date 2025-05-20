# Pipecat Agent Service (Supabase Realtime)

This service runs the Pipecat agent as a communications layer, listening to Supabase Realtime channels and exposing HTTP endpoints for integration with other services.

## Features
- Listens to Supabase Realtime `messages` table for new chat/events
- Processes and routes messages (agent-to-agent, agent-to-user, multimodal)
- Exposes a FastAPI HTTP service for health checks and future API integration
- Runs as a Docker container for easy deployment
- Loads all configuration from a unified `.env.yaml` file

## Configuration

### Unified YAML Config
- Place a `.env.yaml` file in the project root (see example below)
- All services (backend, pipecat, litellm) can read from this file
- You can mount it into the container with:
  ```
  docker run -v $(pwd)/.env.yaml:/app/.env.yaml ...
  ```

#### Example `.env.yaml`
```yaml
supabase:
  id: yourprojectref
  key: your-supabase-key
  url: https://yourprojectref.supabase.co

litellm:
  proxy_url: http://litellm-proxy:4000
  config_path: ./litellm_proxy_config/config.yaml
  api_key: your-litellm-proxy-key

pipecat:
  chat_channel: main-room
  call_word: "@SupabaseAgent"
  agent_name: SupabaseAgent
  avatar_url: https://example.com/supabase-agent-avatar.png
  endpoint: http://localhost:8001
  model: openai/gpt-4o

backend:
  port: 8000

api_keys:
  openai: sk-...
  anthropic: ...
  # ...
```

## Model Selection
- The Pipecat agent will use the model specified in `.env.yaml` under `pipecat.model`
- This must match a model available in your LiteLLM proxy config
- To change models, update `.env.yaml` and restart the container

## Usage

### Local (with uv or pip)
```bash
uv pip install -r requirements.txt
python agent.py
```

### Docker
Build and run:
```bash
docker build -t pipecat-agent .
docker run -v $(pwd)/.env.yaml:/app/.env.yaml pipecat-agent
```

### Health Check
The service exposes a health endpoint:
```
GET /health
```

## Integration
- Other services/agents can send messages to the Supabase `messages` table or call HTTP endpoints (future expansion)
- Pipecat can be extended to route/process/respond to messages, or forward to other agents/services

## Extending
- Add more FastAPI endpoints for agent control, message injection, etc.
- Implement advanced message routing, multimodal support, or agent-to-agent protocols

--- 