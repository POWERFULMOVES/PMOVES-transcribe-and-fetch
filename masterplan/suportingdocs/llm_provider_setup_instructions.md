# LLM Provider Setup Instructions

This document provides instructions for setting up and configuring LLM providers for use with the PMOVES backend, particularly focusing on local models via Ollama and integration with the LiteLLM proxy, as well as cloud providers like Groq, Google, and OpenAI.

## Centralized LLM Management

The PMOVES backend uses a centralized system for managing LLM models, leveraging a LiteLLM proxy. The LiteLLM proxy acts as a single gateway to various LLM providers (cloud and local), and the backend's `llm_registry_service` fetches available models from the proxy on startup.

Configuration for which models are available is primarily done in the LiteLLM proxy's `config.yaml` file (`litellm_proxy_config/config.yaml`).

## Setting up Ollama (Local Models)

Ollama allows you to run open-source LLMs locally. The PMOVES backend includes an initializer script (`backend/app/ollama_initializer.py`) to help ensure that a selected Ollama model is available when the backend starts.

**Prerequisites:**

1.  **Install Ollama:** Download and install Ollama from the official website: [https://ollama.com/](https://ollama.com/)
2.  **Run Ollama Server:** Ensure the Ollama server is running in the background on your system.

**How `ollama_initializer.py` Works:**

-   During the backend application's startup sequence (`backend/app/main.py`), the `ensure_ollama_model_loaded` function from `ollama_initializer.py` is called.
-   This function checks the `LLM_MODEL` environment variable configured for the backend.
-   If the selected model is identified as an Ollama model (based on the `AVAILABLE_MODELS` configuration in `app_config.py`), the script attempts to ensure this model is loaded in your local Ollama instance.
-   It uses the Ollama API (`http://localhost:11434` by default, configurable via `OLLAMA_BASE_URL` in `.env`) to:
    -   Check the list of currently available models (`/api/tags`).
    -   If the required model is not found, it initiates a model pull (`/api/pull`) to download and load the model.
-   This process runs asynchronously during startup and should not block the backend indefinitely, although downloading a large model may take time.

**Configuration:**

1.  **Specify Ollama Model:** Set the `LLM_MODEL` environment variable in your backend's `.env` file (`backend/app/.env`) to the alias of the Ollama model you want to use (e.g., `LLM_MODEL=ollama/llama2`). The alias must match an entry in `backend/app/app_config.py` that has `"provider_group": "Ollama (Local)"`.
2.  **LiteLLM Proxy Configuration:** Ensure your LiteLLM proxy's `config.yaml` (`litellm_proxy_config/config.yaml`) is configured to connect to your local Ollama instance and expose the desired Ollama models. Refer to the LiteLLM documentation for details on configuring the Ollama provider in `config.yaml`.
3.  **Ollama Base URL (Optional):** If your Ollama server is not running on the default `http://localhost:11434`, you can specify its URL using the `OLLAMA_BASE_URL` environment variable in `backend/app/.env`.

**Troubleshooting:**

-   If the backend fails to start or reports errors related to Ollama initialization, check the backend logs for messages from `ollama_initializer.py`.
-   Ensure your local Ollama server is running.
-   Verify that the `LLM_MODEL` environment variable is set correctly and corresponds to a valid Ollama model alias configured in `app_config.py` and `litellm_proxy_config/config.yaml`.
-   Check the LiteLLM proxy logs to see if it can connect to your Ollama instance and list the models.

## Setting up Cloud Providers (Groq, Google, OpenAI)

Integrating cloud-based LLM providers is primarily done by configuring the LiteLLM proxy with your API keys.

**General Configuration Steps:**

1.  **Obtain API Keys:** Get API keys from the respective provider's platform:
    *   **Groq:** [https://console.groq.com/keys](https://console.groq.com/keys)
    *   **Google AI (Gemini):** [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) or Google Cloud Platform.
    *   **OpenAI:** [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2.  **Add API Keys to Environment Variables:** Add your API keys to the `.env` file used by the LiteLLM proxy container. This is typically `backend/app/.env` as configured in `docker-compose.litellm-proxy.yml`. Use the variable names expected by LiteLLM (e.g., `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`).
3.  **Configure LiteLLM Proxy `config.yaml`:** Modify `litellm_proxy_config/config.yaml` to include configurations for the desired providers.

**Provider-Specific Configuration in `config.yaml`:**

Refer to the official LiteLLM documentation for the most up-to-date and detailed configuration options for each provider: `docs/litellm/docs/my-website/docs/providers/`.

Here are examples of how to configure common providers in `config.yaml`:

```yaml
model_list:
  # Example Groq Configuration
  - model_name: groq/llama3-8b-8192 # Alias used by the backend
    litellm_params:
      model: groq/llama3-8b-8192 # Provider's model ID
      api_key: os.environ/GROQ_API_KEY # Source API key from environment variable

  - model_name: groq/llama3-70b-8192
    litellm_params:
      model: groq/llama3-70b-8192
      api_key: os.environ/GROQ_API_KEY

  # Example Google AI (Gemini) Configuration
  # Note: Google models support various capabilities like vision, tool calling
  - model_name: google/gemini-1.5-pro-latest # Alias
    litellm_params:
      model: gemini/gemini-1.5-pro-latest # Provider's model ID
      api_key: os.environ/GEMINI_API_KEY # Source API key

  - model_name: google/gemini-1.0-pro
    litellm_params:
      model: gemini/gemini-1.0-pro
      api_key: os.environ/GEMINI_API_KEY

  # Example OpenAI Configuration
  # Note: OpenAI models support various capabilities like vision, function calling, audio
  - model_name: openai/gpt-4o # Alias
    litellm_params:
      model: gpt-4o # Provider's model ID
      api_key: os.environ/OPENAI_API_KEY # Source API key

  - model_name: openai/gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY

# Ensure dynamic discovery is enabled
litellm_settings:
  check_provider_endpoint: true
  # Add other settings like callbacks here if needed
  # callbacks: ["supabase"] # Example if Supabase logging is configured

# Ensure environment variables are loaded by the proxy container
# This is handled by the docker-compose.litellm-proxy.yml file using --env-file

```

**After Configuration:**

-   Restart the LiteLLM proxy Docker container to load the updated `config.yaml` and environment variables.
-   Restart the backend application. The `llm_registry_service` will fetch the newly configured models from the proxy's `/models` endpoint on startup.

By configuring your desired providers and their API keys in the LiteLLM proxy's environment and `config.yaml`, you make them available for use by the PMOVES backend.
