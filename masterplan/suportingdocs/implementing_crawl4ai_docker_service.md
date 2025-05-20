# Implementing the Crawl4AI Docker Service

## Overview
This document outlines the steps to implement and integrate the `crawl4ai` library as a dedicated Docker service within the PMOVES project. Running `crawl4ai` as a shared service allows the backend and various agents to leverage its web crawling and extraction capabilities consistently and scalably.

## Implementation Steps

1.  **Clone `crawl4ai` Repository:** If the `crawl4ai` repository is not already part of the workspace, clone it to access its Docker deployment files (`deploy/docker`).
    **Status:** This step was implicitly handled by referencing files within the cloned `crawl4ai` repository under `docs/crawl4ai/`. **COMPLETED.**

2.  **Adapt Configuration:**
    *   Copy `crawl4ai/deploy/docker/config.yml` to a designated configuration directory in the PMOVES project (e.g., `deployment/crawl4ai/`).
    *   Review and modify `config.yml` to align with PMOVES project standards and environment requirements (e.g., service port, logging levels, security features).
    *   **Crucially, configure the `llm` section in `config.yml` to point `api_base` to your LiteLLM proxy service (e.g., `http://litellm:4000`).** This ensures `crawl4ai` routes its LLM calls through the proxy. You do **not** need to configure individual LLM API keys in `crawl4ai`'s config or environment variables if routing through LiteLLM.
    *   The `crawl4ai/deploy/docker/.llm.env.example` file is **not** needed for the `crawl4ai` service itself when routing via LiteLLM. Your LiteLLM proxy will need access to LLM API keys, typically via its own environment file (e.g., `.env.litellm` as referenced in `docker-compose-core.yml`).
    **Status:** A project-specific `config.yml` was created in `deployment/crawl4ai/` and adapted to point to the LiteLLM proxy. **COMPLETED.**

3.  **Build or Pull Docker Image:**
    *   **Option A: Use Pre-built Image (Recommended):** Pull the latest pre-built `crawl4ai` image from Docker Hub (e.g., `unclecode/crawl4ai:latest` or a specific version tag).
    *   **Option B: Build Locally:** Use the `Dockerfile` and `requirements.txt` located in `crawl4ai/deploy/docker/` to build the Docker image locally. Consider using `docker buildx` for multi-architecture support.
    **Status:** Decision made to use the pre-built `unclecode/crawl4ai:latest` image. **COMPLETED.**

4.  **Integrate into Docker Compose:**
    *   Add a new service definition for `crawl4ai` in your project's main `docker-compose.yml` file.
    *   Specify the chosen Docker image.
    *   Map the service port (default is `11235`) to a host port if needed for external access (though service-to-service communication within Docker Compose usually doesn't require host port mapping).
    *   Mount the adapted `config.yml` and `.llm.env` files as volumes or pass environment variables to the container.
    *   Ensure the `crawl4ai` service is part of the same Docker network as your backend and agents.
    **Status:** A dedicated `docker-compose-crawl4ai.yml` and an updated `docker-compose-core.yml` were created/modified to include the `crawl4ai` service using the pre-built image, mounting the adapted config, and ensuring dependency on LiteLLM. **COMPLETED.**

5.  **Update Backend/Agent Clients:**
    *   Locate the existing `Crawl4aiDockerClient` usage in the backend (e.g., `backend/app/crawl4ai_fetcher.py`) and relevant agent code.
    *   Update the client initialization to connect to the `crawl4ai` service using the service name defined in `docker-compose.yml` (e.g., `http://crawl4ai:11235`).
    *   Ensure the client is configured with any necessary authentication credentials if JWT or other security measures are enabled in `config.yml`.
    **Status:** A new file `backend/app/crawl4ai_docker_fetcher.py` was created containing the refactored logic to use `Crawl4aiDockerClient`. The original `backend/app/crawl4ai_fetcher.py` still exists and needs to be replaced or integrated. **PARTIALLY COMPLETED / IN PROGRESS.**

6.  **Implement Pydantic Controls:**
    *   Define Pydantic models in your project's shared components or in the modules interacting with the `crawl4ai` service.
    *   These models should represent the expected structure and data types for requests sent to the `crawl4ai` API endpoints (e.g., `/crawl`, `/crawl/stream`).
    *   Use these Pydantic models to validate incoming request data within your backend/agents before making calls to the `crawl4ai` service.
    **Status:** This step is pending implementation. It is crucial for robust API interaction. **PENDING.**

7.  **Explore MCP Support:**
    *   Investigate the MCP implementation in `crawl4ai/deploy/docker/mcp_bridge.py` and the relevant sections in `crawl4ai/deploy/docker/README.md`.
    *   Determine if MCP is a suitable protocol for your agent-to-service communication and how it can be integrated with your Pipecat setup.
    *   Adapt or create agent components that communicate with the `crawl4ai` service via MCP if this approach is chosen.
    **Status:** Exploration of MCP support is a potential future enhancement, dependent on decisions about agent communication protocols. **PENDING.**

8.  **Testing:**
    *   Develop unit and integration tests to verify the `crawl4ai` service deployment and its integration with the backend and agents.
    *   Test various scenarios, including successful crawls, LLM-dependent extractions, error handling, and performance under load.
    **Status:** Backend testing for `crawl4ai` integration is partially complete, with some foundational tests passing but key areas (LLM extraction, fetch history status bug) still requiring attention as per the `Project_Status_Synthesis_Report.md`. New integration tests specifically for the Docker service and LLM registry interaction are needed. **IN PROGRESS.**

9.  **Documentation:**
    *   Maintain and expand this document with specific details and code examples as the implementation progresses.
    *   Add cross-references to other relevant project documentation (e.g., LLM configuration, Docker Compose setup).
    **Status:** This document is being updated now to reflect progress. Cross-referencing with `Project_Status_Synthesis_Report.md` and other relevant docs (like the LLM plan) will be important. **IN PROGRESS.**

10. **Implement Orchestrator:** Design and implement the orchestrator service responsible for managing agents, including spawning the default Supabase agent and dynamically selecting agents based on user preferences and available resources (local PC, Jetson nanos, etc.).
    **Status:** The Orchestrator is a separate, significant task in the broader Agent Platform Plan. Its implementation is pending. **PENDING.**

## Next Steps

Based on the current status, the immediate next steps for `crawl4ai` Dockerization and integration are:

1.  **Integrate New Fetcher into Backend:** Modify `backend/app/main.py` to use the newly created `fetch_with_crawl4ai_docker` function from `backend/app/crawl4ai_docker_fetcher.py` for handling `/fetch-content` requests when the `crawl4ai` engine is selected. This will involve updating the endpoint logic to call the new function and handle the streamed responses appropriately.
2.  **Implement Pydantic Controls:** Define and implement Pydantic models for request validation and response structuring when interacting with the `crawl4ai` service, as outlined in Step 6 of the Implementation Steps.
3.  **Address Backend Testing Issues:** Focus on completing the backend testing for `crawl4ai` integration, specifically addressing the LLM extraction strategy verification and resolving the `fetch_history` status bug highlighted in `Project_Status_Synthesis_Report.md`. Create new integration tests for the Docker service setup.
4.  **Update Documentation:** Continue refining this document with specifics as the integration in `main.py` is completed and testing progresses. Ensure accurate cross-referencing.
5.  **Continue Broader Agent/LLM Work:** Note that the `crawl4ai` integration is part of a larger effort involving the dynamic LLM registry and agent platform. Progress on those areas (as detailed in `Project_Status_Synthesis_Report.md` and potentially other masterplan docs) will influence future `crawl4ai` integration work, particularly regarding LLM model selection and agent communication.

## Notes and Considerations

*   **LLM Configuration:** Ensure the LLM providers and API keys are configured for your **LiteLLM proxy**. The `crawl4ai` service will leverage the proxy for LLM access. Configure `crawl4ai`'s `config.yml` to point `api_base` to the LiteLLM service address within the Docker network.
*   **Resource Allocation:** Monitor the resource (CPU, memory) usage of the `crawl4ai` Docker container and adjust resource limits in Docker Compose as needed based on your workload.
*   **Logging and Monitoring:** Integrate the `crawl4ai` service logs into your project's centralized logging system and ensure its metrics (exposed via Prometheus as per `server.py`) are collected by your monitoring stack (Prometheus/Grafana).
*   **Authentication/Authorization:** If you enable JWT or other security features in `config.yml`, ensure your backend and agents are updated to authenticate correctly with the `crawl4ai` service.
*   **Cross-Reference Status:** For detailed status on backend testing and the dynamic LLM management system, refer to [`docs/masterplan/Project_Status_Synthesis_Report.md`](mdc:docs/masterplan/Project_Status_Synthesis_Report.md). 