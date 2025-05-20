# Using Crawl4AI with the Backend Fetch Service

This document explains how the `crawl4ai` library is integrated into the backend's `/fetch-content` endpoint, particularly focusing on its interaction with the centralized LLM management system via the LiteLLM proxy.

## Overview

The backend service (specifically `backend/app/crawl4ai_fetcher.py`) utilizes `crawl4ai` to fetch and process web content. When LLM-dependent features of `crawl4ai` are used (e.g., `LLMExtractionStrategy`, image captioning), all LLM calls are routed through the LiteLLM proxy.

## Key Integration Points

### 1. Invocation via `/fetch-content` Endpoint

The `/fetch-content` endpoint in `backend/app/main.py` is the primary way to trigger a crawl using `crawl4ai`. When the `engine` parameter is set to `crawl4ai`, the request is routed to the `fetch_with_crawl4ai` generator in `backend/app/crawl4ai_fetcher.py`.

This generator handles:
*   Parsing request parameters relevant to `crawl4ai` (browser settings, crawl configurations, extraction strategies).
*   Setting up the `CrawlerRunConfig`, `BrowserConfig`, and `LLMConfig` for `crawl4ai`.
*   Executing the crawl using `AsyncWebCrawler.arun()`.
*   Streaming progress, logs, and results (or errors) back to the client via Server-Sent Events (SSE).

### 2. `LLMConfig` Population for LiteLLM Proxy

When an LLM-dependent feature is requested (e.g., `extraction_strategy: "llm"` or `image_captioning: true`), `crawl4ai_fetcher.py` configures the `LLMConfig` for `crawl4ai` to use the LiteLLM proxy:

*   **`api_base`**: This is **always** set to the `LITELLM_PROXY_URL` obtained from the backend's environment variables (e.g., `http://litellm-proxy:4000`). `crawl4ai` will send all its LLM requests to this proxy URL.
*   **`api_key`**: This is set to the `LITELLM_PROXY_API_KEY` obtained from the backend's environment variables. This key is used to authenticate the backend's requests *to* the LiteLLM proxy (it's the proxy's master key, not a provider-specific key).
*   **`model`**: The `model_name` (alias) for the desired LLM is passed here. This alias should correspond to a model defined in the LiteLLM proxy's `config.yaml` (e.g., `groq/llama3-70b-8192`, `openai/gpt-4o`). The backend may derive this from request parameters like `llm_model_name` or use a default.
    *   The `llm_provider` parameter from the request is used to help construct this model alias if it's not a fully qualified one (e.g., if `llm_provider` is "openai" and `llm_model_name` is "gpt-3.5-turbo", the fetcher might form "openai/gpt-3.5-turbo").
*   Other LLM parameters like `temperature` (`llm_temperature`) and `max_tokens` (`llm_max_tokens`) are also passed from the request to `LLMConfig`.

Refer to `docs/llm_configuration.md` for more details on the overall LLM system and proxy setup.

### 3. `ExtractionStrategy` Configuration

The `/fetch-content` endpoint accepts an `extraction_config` parameter (as a JSON string) which allows for detailed configuration of `crawl4ai`'s extraction strategies, including `LLMExtractionStrategy`.

**Example for `LLMExtractionStrategy`:**

If you pass `extraction_strategy: "llm"` and provide relevant `extraction_config`:

'''json
// In the query parameters for /fetch-content:
// extraction_strategy=llm
// llm_model_name=groq/llama3-8b-8192  // Or any model alias from your proxy config
// extraction_config='{"type": "json", "schema_json": {"type": "object", "properties": {"event_name": {"type": "string"}, "date": {"type": "string"}}}}'
'''

`crawl4ai_fetcher.py` will parse `extraction_config` and instantiate `LLMExtractionStrategy` accordingly. The `LLMConfig` (as described above) will ensure that the strategy's LLM calls go through the proxy.

### 4. Handling of LLM-Specific Errors

The `crawl4ai_fetcher.py` module has specific logic to detect and report errors that occur within `crawl4ai`'s LLM-dependent strategies, especially `LLMExtractionStrategy`.

*   If `LLMExtractionStrategy` is used and it encounters an error (e.g., the LLM provider returns an error, the model is invalid, rate limits are hit, or the output doesn't conform to a requested JSON schema), this error is caught.
*   Instead of potentially being hidden or causing the fetch to silently fail to extract LLM content, `crawl4ai_fetcher.py` will:
    1.  Construct a structured `llm_error` dictionary containing details about the failure (e.g., error message, type, model used, related parameters).
    2.  Yield an SSE event of `type: "error"` to the client. This event will include the `llm_error` dictionary.
    3.  Terminate the fetch process for that URL to prevent sending a misleading "completed" event.

This explicit error reporting helps in diagnosing issues with LLM configurations or provider problems when using `crawl4ai` through the backend.

**Example SSE Error Event for LLM Failure:**

'''json
{
  "type": "error",
  "timestamp": "2023-10-27T10:20:30.123Z",
  "id": "1698391230.123",
  "message": "LLM extraction strategy failed for model: non_existent_model_alias",
  "llm_error": {
    "error_type": "APIError", // Or ModelNotFound, ConfigurationError, etc.
    "message": "The model `non_existent_model_alias` does not exist or you do not have access to it.",
    "model_used": "non_existent_model_alias",
    "strategy_params": {
      "extraction_type": "markdown"
      // ... other relevant strategy parameters
    },
    "raw_provider_error": "Details from LiteLLM/Provider..." // Optional
  }
}
'''

### 5. Fetch History Integration

All fetch attempts, including those using `crawl4ai`, are logged in the `fetch_history` database table.
*   The initial status is "pending".
*   If an LLM error (as described above) or any other critical error occurs during the `crawl4ai` process, the status in `fetch_history` will be updated to "failed", and the error message (including structured LLM error details if applicable) will be logged.
*   On successful completion, the status is updated to "success", and a summary of the content along with paths to any generated artifacts (like PDFs) are stored.

## Request Parameters

Many parameters for the `/fetch-content` endpoint directly map to `crawl4ai`'s `BrowserConfig` and `CrawlerRunConfig`. Refer to the API documentation for `/fetch-content` (and `docs/api_reference.md` or similar) and the `crawl4ai` library's own documentation for details on each parameter's effect.

Key parameters related to LLM usage include:
*   `engine: "crawl4ai"`
*   `extraction_strategy`: (e.g., "markdown", "llm")
*   `extraction_config`: JSON string for detailed strategy configuration.
*   `llm_model_name`: Alias of the LLM model to be used (e.g., `openai/gpt-4o`, `groq/llama3-70b-8192`).
*   `llm_provider`: (Optional, can help form the model alias if `llm_model_name` isn't fully qualified like `provider/model`).
*   `llm_temperature`, `llm_max_tokens`: Standard LLM sampling parameters.
*   `image_captioning`: Boolean, if true, enables image captioning which uses an LLM.

By routing `crawl4ai`'s LLM needs through the centralized LiteLLM proxy and `LLMRegistryService`, the backend maintains a consistent and configurable approach to LLM usage across different tools and services. 