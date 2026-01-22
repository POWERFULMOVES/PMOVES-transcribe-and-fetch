# PMOVES-transcribe-and-fetch Development Guidelines

This repository follows the **PMOVES.AI-Edition-Hardened** patterns for security, networking, and deployment.

## Architecture Overview

### Network Tiers
| Tier | Network | Subnet | Services |
|------|---------|--------|----------|
| API | transcribe_api | 172.31.1.0/24 | backend, frontend |
| Application | transcribe_app | 172.31.2.0/24 | litellm-proxy, crawl4ai, pipecat, supabase-agent |

### Deployment Modes
| Mode | DB_BACKEND | DOCKED_MODE | Use Case |
|------|------------|-------------|----------|
| Standalone | sqlite | false | Local development, testing |
| Docked | supabase | true | Integration with parent PMOVES.AI |
| Dual-write | supabase | true | Migration from SQLite to Supabase |

## Quick Start

```bash
# Standalone mode (default)
make up

# With all services
make up-full

# With security hardening
make up-hardened

# Docked to PMOVES.AI
make up-docked
```

## Environment Configuration

### Tier-Based Environment Files
```
env.shared           # Common config (git-tracked, no secrets)
env.tier-api         # API tier credentials (Supabase)
env.tier-worker      # Worker tier config
env.tier-llm         # LLM provider API keys
env.tier-media       # Whisper/transcription config
.env.local           # Host overrides (git-ignored)
secrets/             # Docker secrets (git-ignored)
```

### Service Tier Assignment
| Service | Tier | env_file Pattern |
|---------|------|------------------|
| backend | API | env.shared + env.tier-api |
| frontend | API | env.shared + env.tier-api |
| litellm-proxy | LLM | env.shared + env.tier-llm |
| crawl4ai | Worker | env.shared + env.tier-worker |
| pipecat | Media | env.shared + env.tier-media |
| supabase-agent | Worker | env.shared + env.tier-worker |

## Security Hardening

When deploying with `docker-compose.hardened.yml`:

- **Non-root user**: All services run as UID 65532
- **Read-only filesystem**: Transient writes via tmpfs
- **Capabilities dropped**: `cap_drop: ["ALL"]`
- **No privilege escalation**: `no-new-privileges:true`
- **Docker secrets**: Credentials mounted from `secrets/` directory

### Setting Up Secrets

```bash
make secrets-init
# Then create secret files:
echo "your-key" > secrets/supabase_service_key
echo "your-key" > secrets/supabase_jwt_secret
echo "your-key" > secrets/openai_api_key
echo "your-key" > secrets/anthropic_api_key
```

## Key Documentation

- `masterplan/PMOVES_AGENT_PLATFORM_PLAN.md` – Master plan for agent platform
- `PIPECAT_ARCHITECTURE.md` – Pipecat architecture overview
- `docs/pipecatdocs/` – Pipecat component reference
- `pmoves-pipecat/main.py` – Core Pipecat service
- `pmoves-pipecat-agent/minimal_agent.py` – Supabase Realtime agent example

## Development

### Testing
```bash
pytest -q                    # Run tests
make health                  # Check health endpoints
make config                  # Validate compose config
```

### Building
```bash
make build                   # Build all images
make build-no-cache          # Rebuild without cache
```

### Debugging
```bash
make shell-backend           # Shell into backend
make shell-frontend          # Shell into frontend
make logs                    # Tail all logs
```

## Pull Requests

- Reference affected services (backend, frontend, crawl4ai, etc.)
- Note deployment mode changes (standalone vs docked)
- Include security considerations for hardened deployments
- Run `make config` to validate compose before submitting

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic health check |
| `/healthz` | Kubernetes liveness probe |
| `/ready` | Kubernetes readiness probe (checks dependencies) |
