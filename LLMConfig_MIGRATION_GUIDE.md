# LLMConfig Migration & Integration Guide

## Context

- The PMOVES platform uses Crawl4AI and Pipecat for agent orchestration, multimodal communication, and LLM-backed capabilities.
- LLMs are served via LiteLLM proxy, but all agent and orchestrator logic must use the correct parameter for model selection in Crawl4AI's `LLMConfig`.

## Required Change

- **All instantiations of `LLMConfig` for Crawl4AI must use the `provider` parameter to specify the model.**
    - Example: `LLMConfig(provider="openai/gpt-4o", api_token="...")`
- Do **not** use `model` or `engine` as a parameter for Crawl4AI's LLMConfig.

## Model Mapping

- Use the `id` field from `backend/app/app_config.py's `AVAILABLE_MODELS` mapping as the value for `provider`.
    - Example: `"id": "openai/gpt-4o"` → `provider="openai/gpt-4o"`

## Registry/Orchestrator Integration

- When dynamically spawning LLM-backed agents, ensure the agent receives the correct `provider` string.
- If the registry or orchestrator logic passes model info, update it to use the `provider` key and value.

## Pipecat & Tool-Calling

- Pipecat's LLM-backed agents must also use `provider` for LLMConfig.
- Tool-calling and multimodal features depend on correct LLMConfig instantiation.

## Implementation Instructions

1. **Search the codebase for all usages of `LLMConfig` and ensure the model is passed as `provider=...`.**
2. **Update any code that uses `model` or `engine` as a parameter for LLMConfig to use `provider` instead.**
3. **If you find any agent registry, orchestrator, or dynamic agent spawning logic that passes model info, ensure it uses the `provider` string from the model mapping.**
4. **Test all LLM-backed features (fetching, chat, tool-calling, multimodal) to confirm correct model selection and no TypeError or misconfiguration.**
5. **If you add new agent types or LLM-backed features in the future, follow this pattern.**

## Checklist for Implementation

- [ ] Update all backend code to use `provider` for LLMConfig.
- [ ] Update any agent registry/orchestrator logic to use the `provider` string from the model mapping.
- [ ] Ensure all Pipecat agent instantiations use the correct LLMConfig.
- [ ] Test agent spawning, registry lookups, and LLM-backed features to confirm correct model selection.
- [ ] Document any new patterns or exceptions in this file for future agents.

## Additional Migration Note: CrawlerRunConfig Content Flags

- The parameters `keep_html`, `keep_text`, `keep_markdown`, and `keep_screenshots` are **not valid** for `CrawlerRunConfig` in Crawl4AI v0.5.0+.
- Similarly, `screenshots_dir` is **not a valid parameter** for `CrawlerRunConfig` to specify an output directory for screenshots.
- To enable screenshot capture, use the boolean parameter `screenshot=True`. The actual storage/handling of the captured screenshot (e.g., if saved to a file or returned in the result object) is managed by the crawler's implementation details, not by a `screenshots_dir` parameter in `CrawlerRunConfig`.
- Use only the documented parameters for content selection and output (e.g., `only_text`, `markdown_generator`, `target_elements`, `screenshot`, etc.).
- If you find these or similar legacy flags in backend code, **remove them** and use the correct documented options.
- See [Crawl4AI Content Selection](https://github.com/unclecode/crawl4ai/blob/main/docs/md_v2/core/content-selection.md) and [API Parameters](https://github.com/unclecode/crawl4ai/blob/main/docs/md_v2/api/parameters.md) for up-to-date config options.

### Checklist for Next Agent

- [ ] Search for and remove any use of `keep_html`, `keep_text`, `keep_markdown`, `keep_screenshots`, or `screenshots_dir` in backend code related to `CrawlerRunConfig`.
- [ ] Use only valid parameters from the Crawl4AI documentation for `CrawlerRunConfig`.
- [ ] If screenshot capture is needed, use the `screenshot: bool` parameter.

---

**No additional custom logic was found that would override this requirement, but always check for new agent types or orchestrator features that may introduce new LLMConfig instantiations.**

## Analysis of `main.py` and Fetcher Parameter Handling (October 2023)

A review of `backend/app/main.py` (specifically the `/fetch-content` endpoint) and the associated fetcher modules (`crawl4ai_docker_fetcher.py`, `crawl4ai_fetcher.py`) revealed the following points regarding configuration parameter consistency:

### 1. Crawl4AI API Token (`CRAWL4AI_API_TOKEN`)

*   **Observation**:
    *   The `/fetch-content` endpoint in `main.py` does not accept the Crawl4AI API token as a query parameter. Both fetcher modules rely on `os.getenv('CRAWL4AI_API_TOKEN')`.
    *   `crawl4ai_docker_fetcher.py`: Correctly initializes `Crawl4aiDockerClient` with the token from the environment variable and calls `await crawl4ai_client.authenticate()`.
    *   `crawl4ai_fetcher.py`: Previously, it was noted that this file retrieved the token but didn't pass it or authenticate. **[RESOLVED]** This has been corrected; `crawl4ai_fetcher.py` now correctly passes the token to `Crawl4aiDockerClient` and calls `await client.authenticate()` if the token is present.
*   **Recommendation**:
    *   **Consistent Token Usage**: **[COMPLETED]** Both fetchers now consistently use the `CRAWL4AI_API_TOKEN` and handle authentication.

### 2. LLM Base URL Parameter Mapping

*   **Observation (Chain of Mismatches)**:
    1.  **Frontend to `main.py`**:
        *   The frontend (`src/app/fetch/page.js`) sends the LLM base URL as a query parameter named `llm_base_url`.
        *   The `/fetch-content` endpoint in `main.py` defines its FastAPI query parameter for this as `crawl4ai_llm_base_url: Optional[str]`.
        *   **Result**: The value sent by the frontend as `llm_base_url` will likely not be correctly received by the `crawl4ai_llm_base_url` variable in the `main.py` endpoint due to the name mismatch.
    2.  **`main.py` to `crawl4ai_docker_fetcher.py`**:
        *   If `main.py` *were* to receive the LLM base URL correctly under the variable `crawl4ai_llm_base_url`, this would be passed to the fetchers within a dictionary (e.g., `shared_params`).
        *   `crawl4ai_docker_fetcher.py` then attempts to retrieve this value using `params.get("llm_api_base")`.
        *   **Result**: This is a name mismatch. `crawl4ai_docker_fetcher.py` will not find `llm_api_base` in the parameters passed from `main.py` if `main.py` is using `crawl4ai_llm_base_url` as the key.
    3.  **`main.py` to `crawl4ai_fetcher.py`**:
        *   `crawl4ai_fetcher.py` correctly expects `params.get("crawl4ai_llm_base_url")`, which would align with the `main.py` query parameter definition if the frontend sent the correctly named parameter.

*   **Recommendation**:
    *   **Standardize Parameter Names**:
        *   **Option A (Recommended for clarity):**
            1.  Update the frontend (`src/app/fetch/page.js`) to send the parameter as `crawl4ai_llm_base_url` to match the `main.py` endpoint definition.
            2.  Modify `crawl4ai_docker_fetcher.py` to expect `params.get("crawl4ai_llm_base_url")` instead of `params.get("llm_api_base")` for consistency with `crawl4ai_fetcher.py` and the `main.py` query parameter.
        *   **Option B (Requires careful mapping in `main.py`):**
            1.  Keep frontend sending `llm_base_url`.
    *   **Verify Logic**: After standardizing, thoroughly test the LLM base URL functionality when direct LLM configuration is used (not via LiteLLM proxy or registry) for both fetcher paths.

By addressing these inconsistencies, the robustness and reliability of LLM configurations and Crawl4AI service authentication will be improved. 

*   **Standardize Parameter Names**: **[COMPLETED]**
    *   **Option A (Recommended for clarity) was implemented:**
        1.  **[DONE]** The frontend (`src/app/fetch/page.js`) has been updated to send the parameter as `crawl4ai_llm_base_url`.
        2.  **[DONE]** `crawl4ai_docker_fetcher.py` has been modified to expect `params.get("crawl4ai_llm_base_url")`.
        (No changes were needed in `main.py` as its query parameter `crawl4ai_llm_base_url` already matched the intended standardized name).
    *   ~~**Option B (Requires careful mapping in `main.py`):**~~
        ~~1.  Keep frontend sending `llm_base_url`.~~ 

### 3. CrawlerRunConfig `page_timeout`

*   **Observation**:
    *   The backend fetcher scripts (`crawl4ai_docker_fetcher.py` and `crawl4ai_fetcher.py`) were previously using an incorrect `max_timeout` parameter for `CrawlerRunConfig`.
*   **Resolution**:
    *   **[COMPLETED]** This has been corrected. Both fetchers now use the valid `page_timeout` parameter for `CrawlerRunConfig`.
    *   The value for `page_timeout` is sourced from the `timeout` request parameter (which originates from `formState.timeout` in the frontend, is passed as `crawl4ai_timeout_seconds` by `main.py`) and is correctly converted from seconds to milliseconds. 