# LLM System Configuration Guide

This document provides a comprehensive guide to configuring the centralized LLM (Large Language Model) management system used in this project. This system leverages LiteLLM as a proxy to interface with various LLM providers, and an `LLMRegistryService` in the backend to manage and serve model information.

## Core Components

1.  **LiteLLM Proxy:**
    *   Acts as the central gateway for all LLM API calls.
    *   Configured via `litellm_proxy_config/config.yaml`.
    *   Handles routing requests to the appropriate LLM provider (e.g., OpenAI, Groq, Google, Ollama).
    *   Manages API keys for different providers.
    *   Exposes a unified API endpoint (e.g., `/v1/chat/completions`, `/v1/embeddings`) that backend services use.

2.  **`LLMRegistryService` (`backend/app/utils/llm_registry_service.py`):**
    *   A backend service that queries the LiteLLM proxy's `/models` or `/model/info` endpoint on startup and periodically.
    *   Fetches the list of available models configured in the proxy.
    *   Standardizes model information (name, provider, capabilities).
    *   Provides this information to other backend components (like `crawl4ai_fetcher.py` or API route handlers) so they know which models are available and how to call them via the proxy.

3.  **Backend Consumers (e.g., `crawl4ai_fetcher.py`, `llm_routes.py`):**
    *   These components no longer directly call LLM provider APIs.
    *   They obtain model information from the `LLMRegistryService`.
    *   They construct API requests (e.g., for chat completion, embeddings) and send them to the LiteLLM proxy's data plane endpoints.
    *   The proxy URL and master API key for the proxy itself are configured via environment variables for the backend.

## Configuration Flow

### 1. LiteLLM Proxy Configuration (`litellm_proxy_config/config.yaml`)

This is the primary file for defining which LLM providers and models are accessible through the proxy.

*   **`model_list`:** Defines the models available. Each entry specifies:
    *   `model_name`: An alias used internally by the backend and requested by clients (e.g., `groq/llama3-70b-8192`, `openai/gpt-4o`, `google/gemini-1.5-pro-latest`). This is the ID that will appear in the `/models` endpoint of the proxy.
    *   `litellm_params`:
        *   `model`: The actual model ID as recognized by the provider (e.g., `llama3-70b-8192` for Groq, `gpt-4o` for OpenAI).
        *   `api_key`: Crucially, this should point to an environment variable that holds the actual API key (e.g., `os.environ/GROQ_API_KEY`, `os.environ/OPENAI_API_KEY`). **Do not hardcode API keys here.**
        *   Other provider-specific parameters can be added here (e.g., `api_base` for self-hosted models).
    *   `check_provider_endpoint: true`: (Recommended) Allows LiteLLM to verify model availability.

*   **`litellm_settings`:** General settings for the proxy.
    *   `master_key`: (Optional but recommended for securing proxy endpoints) An API key that clients (like our backend) must use to authenticate with the proxy itself. This is set via the `LITELLM_PROXY_API_KEY` environment variable when running the proxy.
    *   `callbacks`: Can be configured for logging, telemetry (e.g., `otel`), etc.
    *   `log_raw_request_response: true`: Useful for debugging, logs full request/response data.

*   **`environment_variables`:** (Optional) Can define default values for environment variables if they are not set in the Docker environment. However, it's generally better to manage these externally.

**Example `config.yaml` snippet:**

'''yaml
model_list:
  - model_name: groq/llama3-70b-8192
    litellm_params:
      model: llama3-70b-8192
      api_key: os.environ/GROQ_API_KEY
    check_provider_endpoint: true
  - model_name: openai/gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY
  - model_name: ollama/pmoves-phi3-custom # Alias for a local Ollama model
    litellm_params:
      model: ollama/pmoves-phi3-custom # Tells LiteLLM to use its Ollama integration
      # No api_key needed for local Ollama by default
      api_base: http://host.docker.internal:11434 # If backend is in Docker, proxy needs to reach Ollama host

litellm_settings:
  # master_key: os.environ/LITELLM_PROXY_API_KEY # If you set a master key for the proxy
  health_check_models: ["groq/llama3-70b-8192"] # Optional: for /health/models endpoint
  callbacks: ["otel"] # Example: OpenTelemetry
  log_raw_request_response: true

# general_settings: # Deprecated in favor of litellm_settings
  # master_key: os.environ/LITELLM_MASTER_KEY # Old way
'''

### 2. API Key Management

*   **Provider API Keys:** (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`)
    *   These are specific to each LLM provider.
    *   They should be set as environment variables for the **LiteLLM proxy container**.
    *   When using `docker-compose.litellm-proxy.yml`, these are typically loaded from the `backend/app/.env` file via the `--env-file` option.
*   **LiteLLM Proxy Master API Key (`LITELLM_PROXY_API_KEY`):**
    *   This is a *single* API key used to protect the LiteLLM proxy itself.
    *   If set in `litellm_settings.master_key` (e.g., `os.environ/LITELLM_PROXY_API_KEY`), then the proxy will require this key for all incoming requests.
    *   The `LITELLM_PROXY_API_KEY` environment variable must be set for the **LiteLLM proxy container** (e.g., in `backend/app/.env`).
    *   The **backend application** also needs this key as an environment variable (`LITELLM_PROXY_API_KEY`) so it can authenticate its requests *to* the proxy.

### 3. Backend Configuration (Environment Variables for `backend/app/.env`)

The backend application needs the following key environment variables:

*   `LITELLM_PROXY_URL`: The full URL of the running LiteLLM proxy (e.g., `http://litellm-proxy:4000` if running in Docker Compose network, or `http://localhost:4000` if running locally).
*   `LITELLM_PROXY_API_KEY`: The master API key for the LiteLLM proxy. This *must* match the key the proxy is configured to expect (if `master_key` is set in `config.yaml`).
*   `DEFAULT_EMBEDDING_MODEL_ID`: (Optional) The default model alias (from `config.yaml`) to use for embeddings if not specified by the caller (e.g., `openai/text-embedding-ada-002`).

### 4. Request Flow for an LLM Call (e.g., from `crawl4ai_fetcher.py`)

1.  **Request Initiated:** A component like `crawl4ai` needs to make an LLM call (e.g., for `LLMExtractionStrategy`).
2.  **LLMConfig Population:**
    *   The `LLMConfig` object for `crawl4ai` is populated.
    *   `api_base`: This is **always** set to the `LITELLM_PROXY_URL` (from the backend's environment variables).
    *   `api_key`: This is set to the `LITELLM_PROXY_API_KEY` (from the backend's environment variables). This is the key for the *proxy*, not a specific provider.
    *   `model`: The `model_name` (alias) from `litellm_proxy_config/config.yaml` is used (e.g., `groq/llama3-70b-8192`). This alias might be hardcoded, come from request parameters, or be determined via the `LLMRegistryService`.
3.  **Call to LiteLLM Proxy:** `crawl4ai` (or any other backend component using LiteLLM's Python library or making direct HTTP calls) sends the request to the `LITELLM_PROXY_URL` (e.g., `http://litellm-proxy:4000/v1/chat/completions`).
    *   The request includes the `model` alias.
    *   The `Authorization: Bearer <LITELLM_PROXY_API_KEY>` header is set.
4.  **Proxy Handles the Request:**
    *   The LiteLLM proxy receives the request.
    *   It authenticates the request using its master key (if configured).
    *   It looks up the `model` alias in its `config.yaml`.
    *   It identifies the target provider and the actual provider model ID.
    *   It retrieves the provider-specific API key (e.g., `GROQ_API_KEY`) from its own environment variables.
    *   It forwards the request to the actual LLM provider (e.g., Groq API).
5.  **Response Relayed:** The provider's response is sent back to the proxy, which then relays it to the backend component (`crawl4ai_fetcher`).

### 5. Embedding Generation (`get_embedding_with_registry` in `main.py`)

*   The helper function `get_embedding_with_registry` is used to generate embeddings.
*   It takes a `model_id` (which should be an alias from `config.yaml`, e.g., `openai/text-embedding-ada-002`).
*   It calls the `generate_embedding` method of the `LLMRegistryService` instance.
*   The `LLMRegistryService.generate_embedding` method then makes an HTTP request to the LiteLLM proxy's `/v1/embeddings` endpoint, providing the `model_id` (alias) and the `LITELLM_PROXY_API_KEY`.
*   The proxy routes this to the appropriate embedding provider.

## Docker Compose Setup

*   **`docker-compose.litellm-proxy.yml`:**
    *   Runs the LiteLLM proxy service.
    *   Mounts `litellm_proxy_config/config.yaml` into the container.
    *   Uses `--env-file backend/app/.env` to load provider API keys and the `LITELLM_PROXY_API_KEY` for the proxy itself.
*   **`docker-compose.backend.yml`:**
    *   Runs the backend FastAPI application.
    *   Also uses `--env-file backend/app/.env` to load `LITELLM_PROXY_URL` and `LITELLM_PROXY_API_KEY` (for the backend to *use* when calling the proxy).

Ensure that network configurations in Docker Compose allow the backend container to reach the LiteLLM proxy container (e.g., by using the proxy's service name as the hostname in `LITELLM_PROXY_URL`).

This consolidated system provides flexibility in adding/changing LLM providers, centralizes API key management for providers within the proxy's environment, and simplifies LLM integration for backend services. 