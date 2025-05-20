# PMOVES Project Architecture and Dependencies

## Overview
This document outlines the high-level architecture, key dependencies, dependency management strategies, containerization approach for agents, and the observability stack used in the PMOVES project. It serves as a central reference point for understanding the technical foundation of the project.

## Project Structure
The project follows a monorepo structure with key components organized into top-level directories:
- `backend/`: Contains the backend FastAPI application.
- `src/`: Likely contains the frontend application (Node.js/React/Next.js).
- `pmoves-pipecat/`: Houses components related to the Pipecat communication layer.
- `pmoves-agent-registry/`: Contains the agent registry service.
- `pmoves-ottomator-agents/`: Likely contains specific agent implementations.
- `docs/`: Project documentation.
- `tests/`: Project tests.
- `litellm_proxy_config/`: Configuration for the LiteLLM proxy.
- `migrations/`: Database migration scripts.
- Other directories for temporary files, configuration, and historical data.

## Core Dependencies

### Python Dependencies
Python dependencies are managed using `uv` and defined in `pyproject.toml` and `uv.lock`. Key libraries include:
- Web frameworks (`fastapi`, `uvicorn`, `starlette`)
- LLM interactions (`litellm`, `openai`, `groq`)
- Data handling and database interaction (`pydantic`, `pandas`, `numpy`, `asyncpg`, `supabase`, `postgrest`, `realtime`, `storage3`)
- Content processing (`yt-dlp`, `playwright`, `beautifulsoup4`, `lxml`, `weasyprint`, `pdfkit`, `markdown`, `markdown2`, `python-frontmatter`, `pydub`, `mutagen`, `av`, `ctranslate2`, `onnxruntime`, `faster-whisper`, `torch`, `torchaudio`, `torchvision`, `nltk`, `scikit-learn`, `tokenizers`)
- Testing frameworks (`pytest`, `pytest-asyncio`, etc.)
- Custom/project-specific libraries (`crawl4ai`, `tf-playwright-stealth`, `rank-bm25`, `supafunc`)

For a comprehensive list and exact versions, refer to [`pyproject.toml`](mdc:pyproject.toml) and [`uv.lock`](mdc:uv.lock).

### Node.js/Frontend Dependencies
The frontend is built using Node.js, React, and Next.js. Dependencies are managed via npm or yarn, defined in `package.json` and `package-lock.json`.

For a detailed list of frontend dependencies, refer to [`package.json`](mdc:package.json).

### Database
The project utilizes **Supabase** for its database (PostgreSQL), authentication, and real-time features. Database schema setup is managed via SQL scripts like [`supabase_tables_setup.sql`](mdc:supabase_tables_setup.sql) and potentially migrations.

### Containerization
**Docker** and **Docker Compose** are used to containerize and orchestrate various services, including the backend, LiteLLM proxy, and agents. Refer to the `docker-compose.*.yml` files for service definitions and configurations:
- [`docker-compose.yml`](mdc:docker-compose.yml): Main compose file (may include all services or orchestrate others).
- [`docker-compose.backend.yml`](mdc:docker-compose.backend.yml): Defines the backend service container.
- [`docker-compose.litellm-proxy.yml`](mdc:docker-compose.litellm-proxy.yml): Defines the LiteLLM proxy service container.
- [`docker-compose.pipecat.yml`](mdc:docker-compose.pipecat.yml): Defines the Pipecat service container (if separate).

## Dependency Management

- **Python:** `uv` is the primary tool for managing Python dependencies. It is used to install packages based on `pyproject.toml` and manage the `uv.lock` file for reproducible builds.
- **Node.js:** Dependencies are managed using npm or yarn, based on the `package.json` file.

## Agent Containerization and Deployment
Agents within the PMOVES platform are designed to run as containerized microservices.
- Specific agent implementations (e.g., in `pmoves-ottomator-agents/`) are intended to be built into Docker images.
- Docker Compose files orchestrate the deployment of these agent containers alongside other services like the backend and LiteLLM proxy.
- This containerized approach facilitates scalability, isolation, and easier deployment.

## Observability Stack
The project incorporates an observability stack for monitoring and debugging:
- **OpenTelemetry (Otel):** Used for instrumenting the application to collect traces, metrics, and logs.
- **Prometheus & Grafana:** Likely used for collecting and visualizing metrics.
- **Supabase:** Used for centralized logging and potentially storing other monitoring data (leveraging LiteLLM's Supabase logging callback).

## Shared Services
In addition to the core backend and frontend, key functionalities are being designed as shared services that can be consumed by multiple parts of the application, including the main backend and various agents.

### Crawl4AI Service
The `crawl4ai` library, a powerful web crawling and extraction tool, is planned to run as a dedicated Docker service. This approach offers several advantages:
- **Modularity:** Encapsulates crawling logic in an independent service.
- **Reusability:** A single service instance can be shared by the backend and multiple agents.
- **Scalability:** The service can be scaled independently based on demand.
- **Technology Isolation:** Manages its own dependencies within its container.
- **Enhanced Capabilities:** Provides advanced crawling and extraction features to the entire platform.
- **UI Modularization:** Supports building modular UIs based on agent capabilities that utilize the crawling service.

The `crawl4ai` Docker service is integrated with the **LiteLLM proxy** to route its LLM calls. This leverages the centralized LLM management and configuration provided by the proxy.

The backend and agents will interact with the `crawl4ai` service via its client library and API.

### Agent Registry
A central **Agent Registry** is being developed to manage the dynamic discovery, registration, and management of all agents and potentially other services within the PMOVES platform. This registry will play a key role in enabling the orchestrator and other components to find and utilize available capabilities, including potentially providing information about shared services like `crawl4ai`.

## References to Other Documentation
- **Project Overview:** [`docs/project_overview.md`](mdc:docs/project_overview.md)
- **Project Structure Details:** [`docs/project_structure.md`](mdc:docs/project_structure.md)
- **Agent Platform Plan:** [`docs/masterplan/PMOVES_AGENT_PLATFORM_PLAN.md`](mdc:docs/masterplan/PMOVES_AGENT_PLATFORM_PLAN.md)
- **Agent LLM Plan:** [`docs/masterplan/agent_llm_plan.md`](mdc:docs/masterplan/agent_llm_plan.md)
- **Agent Registry Schema:** [`docs/masterplan/PMOVES_AGENT_REGISTRY_SCHEMA.md`](mdc:docs/masterplan/PMOVES_AGENT_REGISTRY_SCHEMA.md)
- **Backend Testing Plan:** [`docs/new_test_plan.md`](mdc:docs/new_test_plan.md)
- **Live Test Instructions:** [`docs/livetest_instructions.md`](mdc:docs/livetest_instructions.md)
- **API LLM Endpoints:** [`docs/api_llm_endpoints.md`](mdc:docs/api_llm_endpoints.md)
- **LiteLLM Proxy Setup:** [`docs/litellm/LiteLLM Proxy Setup and Initial Configuration.md`](mdc:docs/litellm/LiteLLM%20Proxy%20Setup%20and%20Initial%20Configuration.md) 