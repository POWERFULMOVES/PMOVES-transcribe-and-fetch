# =============================================================================
# PMOVES-transcribe-and-fetch Makefile
# =============================================================================
# Deployment targets following PMOVES.AI-Edition-Hardened patterns.
#
# Usage:
#   make env-bootstrap   # Copy credentials from parent PMOVES.AI
#   make up              # Standalone mode (default)
#   make up-docked       # Docked to PMOVES.AI
#   make up-hardened     # With security overlay
#   make up-full         # All services with all profiles
# =============================================================================

PROJECT := pmoves-transcribe
COMPOSE := docker compose -p $(PROJECT)

# Environment defaults
DOCKED_MODE ?= false
DB_BACKEND ?= sqlite
SUPABASE_DUAL_WRITE ?= false
AGENT_ZERO_MCP_ENABLED ?= false

# =============================================================================
# Environment Bootstrap (aligned with PMOVES-DoX pattern)
# =============================================================================

.PHONY: env-bootstrap
env-bootstrap: ## Copy credentials from parent PMOVES.AI
	@echo "Bootstrapping environment from parent PMOVES.AI..."
	@chmod +x ./scripts/bootstrap_env.sh 2>/dev/null || true
	@./scripts/bootstrap_env.sh

.PHONY: ensure-standalone-networks
ensure-standalone-networks: ## Create external networks for standalone mode
	@echo "Ensuring external networks exist for standalone mode..."
	@for network in pmoves_api pmoves_app pmoves_bus pmoves_data transcribe_api transcribe_app; do \
		docker network inspect $$network >/dev/null 2>&1 || { \
			echo "  Creating network: $$network"; \
			docker network create $$network >/dev/null; \
		}; \
	done
	@echo "External networks ready"

# =============================================================================
# Core Targets
# =============================================================================

.PHONY: up
up: ## Start core services (backend, frontend)
	$(COMPOSE) up -d

.PHONY: down
down: ## Stop all services
	$(COMPOSE) down

.PHONY: logs
logs: ## Tail logs from all services
	$(COMPOSE) logs -f

.PHONY: ps
ps: ## Show running services
	$(COMPOSE) ps

# =============================================================================
# Deployment Mode Targets
# =============================================================================

.PHONY: up-standalone
up-standalone: ensure-standalone-networks ## Start in standalone mode (SQLite, local services)
	DOCKED_MODE=false DB_BACKEND=sqlite $(COMPOSE) up -d

.PHONY: up-docked
up-docked: ## Start in docked mode (Supabase, parent network)
	DOCKED_MODE=true DB_BACKEND=supabase AGENT_ZERO_MCP_ENABLED=true $(COMPOSE) up -d

.PHONY: up-dual-write
up-dual-write: ## Start with dual-write migration mode
	DOCKED_MODE=true DB_BACKEND=supabase SUPABASE_DUAL_WRITE=true $(COMPOSE) up -d

.PHONY: up-hardened
up-hardened: ## Start with security hardening overlay
	$(COMPOSE) -f docker-compose.yml -f docker-compose.hardened.yml up -d

.PHONY: up-hardened-docked
up-hardened-docked: ## Start hardened + docked mode
	DOCKED_MODE=true DB_BACKEND=supabase AGENT_ZERO_MCP_ENABLED=true \
	$(COMPOSE) -f docker-compose.yml -f docker-compose.hardened.yml up -d

# =============================================================================
# Profile Targets
# =============================================================================

.PHONY: up-llm
up-llm: ## Start with LiteLLM proxy
	$(COMPOSE) --profile llm up -d

.PHONY: up-crawl
up-crawl: ## Start with Crawl4AI
	$(COMPOSE) --profile crawl up -d

.PHONY: up-voice
up-voice: ## Start with Pipecat (voice processing)
	$(COMPOSE) --profile voice up -d

.PHONY: up-agents
up-agents: ## Start with Supabase agent
	$(COMPOSE) --profile agents up -d

.PHONY: up-full
up-full: ## Start all services (all profiles)
	$(COMPOSE) --profile llm --profile crawl --profile voice --profile agents up -d

.PHONY: up-full-hardened
up-full-hardened: ## Start all services with hardening
	$(COMPOSE) -f docker-compose.yml -f docker-compose.hardened.yml \
	--profile llm --profile crawl --profile voice --profile agents up -d

# =============================================================================
# Health & Diagnostics
# =============================================================================

.PHONY: health
health: ## Check health endpoints
	@echo "Checking backend health..."
	@curl -sf http://localhost:$${TRANSCRIBE_BACKEND_HOST_PORT:-8000}/healthz && echo " OK" || echo " FAIL"
	@echo "Checking backend readiness..."
	@curl -sf http://localhost:$${TRANSCRIBE_BACKEND_HOST_PORT:-8000}/ready && echo " OK" || echo " FAIL"
	@echo "Checking frontend..."
	@curl -sf http://localhost:$${TRANSCRIBE_FRONTEND_HOST_PORT:-448}/ >/dev/null && echo " OK" || echo " FAIL"

.PHONY: config
config: ## Validate compose configuration
	$(COMPOSE) config

.PHONY: config-hardened
config-hardened: ## Validate hardened compose configuration
	$(COMPOSE) -f docker-compose.yml -f docker-compose.hardened.yml config

# =============================================================================
# Development
# =============================================================================

.PHONY: build
build: ## Build all images
	$(COMPOSE) build

.PHONY: build-no-cache
build-no-cache: ## Build all images without cache
	$(COMPOSE) build --no-cache

.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	$(COMPOSE) exec backend /bin/sh

.PHONY: shell-frontend
shell-frontend: ## Open shell in frontend container
	$(COMPOSE) exec frontend /bin/sh

# =============================================================================
# Secrets Management
# =============================================================================

.PHONY: secrets-init
secrets-init: ## Initialize secrets directory
	@mkdir -p secrets
	@touch secrets/.gitkeep
	@echo "Created secrets/ directory"
	@echo "Add secret files:"
	@echo "  secrets/supabase_service_key"
	@echo "  secrets/supabase_jwt_secret"
	@echo "  secrets/openai_api_key"
	@echo "  secrets/anthropic_api_key"

.PHONY: secrets-from-gh
secrets-from-gh: ## Populate secrets/ from GitHub Secrets
	@mkdir -p secrets
	@echo "Populating secrets from GitHub..."
	@gh secret view CI_SUPABASE_SERVICE_KEY --json value -q '.value' > secrets/supabase_service_key 2>/dev/null && echo "  supabase_service_key OK" || echo "  supabase_service_key MISSING"
	@gh secret view CI_SUPABASE_SERVICE_KEY --json value -q '.value' > secrets/supabase_jwt_secret 2>/dev/null && echo "  supabase_jwt_secret OK" || echo "  supabase_jwt_secret MISSING"
	@gh secret view OPENAI_API_KEY --json value -q '.value' > secrets/openai_api_key 2>/dev/null && echo "  openai_api_key OK" || echo "  openai_api_key MISSING"
	@gh secret view ANTHROPIC_API_KEY --json value -q '.value' > secrets/anthropic_api_key 2>/dev/null && echo "  anthropic_api_key OK" || echo "  anthropic_api_key MISSING"
	@chmod 600 secrets/* 2>/dev/null || true
	@echo "Secrets populated in secrets/"

.PHONY: env-from-gh
env-from-gh: ## Populate .env.local from GitHub Secrets (standalone mode)
	@echo "Populating .env.local from GitHub Secrets..."
	@echo "# Generated from GitHub Secrets" > .env.local
	@echo "# Standalone mode" >> .env.local
	@echo "DOCKED_MODE=false" >> .env.local
	@echo "DB_BACKEND=sqlite" >> .env.local
	@echo "" >> .env.local
	@echo "# LLM Provider Keys" >> .env.local
	@echo "OPENAI_API_KEY=$$(gh secret view OPENAI_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "ANTHROPIC_API_KEY=$$(gh secret view ANTHROPIC_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "GROQ_API_KEY=$$(gh secret view GROQ_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "GEMINI_API_KEY=$$(gh secret view GEMINI_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "GOOGLE_API_KEY=$$(gh secret view GOOGLE_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "DEEPSEEK_API_KEY=$$(gh secret view DEEPSEEK_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "MISTRAL_API_KEY=$$(gh secret view MISTRAL_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "PERPLEXITYAI_API_KEY=$$(gh secret view PERPLEXITYAI_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "TOGETHER_AI_API_KEY=$$(gh secret view TOGETHER_AI_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "COHERE_API_KEY=$$(gh secret view COHERE_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "FIREWORKS_AI_API_KEY=$$(gh secret view FIREWORKS_AI_API_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "" >> .env.local
	@echo "# Supabase" >> .env.local
	@echo "SUPABASE_URL=$$(gh secret view CI_SUPABASE_URL --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "SUPABASE_ANON_KEY=$$(gh secret view CI_SUPABASE_ANON_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "SUPABASE_SERVICE_KEY=$$(gh secret view CI_SUPABASE_SERVICE_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "NEXT_PUBLIC_SUPABASE_URL=$$(gh secret view CI_SUPABASE_URL --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=$$(gh secret view CI_SUPABASE_ANON_KEY --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo "" >> .env.local
	@echo "# Hugging Face" >> .env.local
	@echo "HF_TOKEN=$$(gh secret view HF_TOKEN --json value -q '.value' 2>/dev/null)" >> .env.local
	@echo ".env.local populated from GitHub Secrets"

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean
clean: ## Remove containers and networks
	$(COMPOSE) down -v --remove-orphans

.PHONY: clean-images
clean-images: ## Remove built images
	$(COMPOSE) down --rmi local

.PHONY: prune
prune: ## Prune unused Docker resources
	docker system prune -f

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
