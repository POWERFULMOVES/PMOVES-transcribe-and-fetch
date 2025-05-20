### Agent Task Plan: Centralized LLM Model Management and Integration

**Overall Objective:** Implement a robust system for dynamically managing LLM models via a LiteLLM proxy, integrate it into the backend services (like crawl4ai and new agents), add comprehensive testing, and ensure necessary documentation is created/updated. The goal is to enable flexible, centralized LLM usage across the application.

**Guiding Principles & Context:**
*   The LiteLLM proxy acts as the central point for accessing various LLM providers (cloud and local).
*   The `llm_registry_service.py` in the backend is responsible for fetching available models from the proxy's `/models` endpoint, standardizing the data, and serving it to other backend components.
*   API keys and sensitive configurations should primarily be managed via environment variables, especially when using Docker.
*   Testing is critical to ensure functionality across different providers and capabilities (text, vision, audio).
*   The existing `crawl4ai` tests should *not* be modified directly; new tests will be created for integration verification.
*   This plan is designed for agent execution; each section outlines a specific task, necessary context, and actionable steps.

---

#### **Task 1: LiteLLM Proxy Setup and Initial Configuration**

**Objective:** Get the LiteLLM proxy running using Docker and configure it to make models available from key providers via its `/models` endpoint.

**Context:**
*   The LiteLLM proxy handles the connections to individual LLM providers.
*   Configuration is primarily done via `litellm_proxy_config/config.yaml`.
*   Environment variables are the secure way to pass API keys and other secrets.
*   We have created separate docker-compose files for the proxy and backend [1-8].
*   Refer to the LiteLLM documentation for provider-specific configuration details in `docs/litellm/docs/my-website/docs/providers/`.

**Agent Instructions/Steps:**
1.  **Review:** Examine the current `litellm_proxy_config/config.yaml` file to understand its structure and existing configurations.
2.  **Review:** Consult the LiteLLM provider documentation in `docs/litellm/docs/my-website/docs/providers/` for the specific providers intended for initial integration (e.g., Groq, Google, Ollama, OpenAI, LLM Studio) [9-11].
3.  **Modify:** Update `litellm_proxy_config/config.yaml` to include configurations for the desired providers [9, 10].
    *   **Ensure:** For each provider, correctly specify the `model_name` (the alias the backend will use, e.g., `groq/llama3-70b-8192`), the actual `litellm_params.model` (the provider's model ID), and how API keys are sourced (e.g., `os.environ/PROVIDER_API_KEY`) [9].
    *   **Enable:** Ensure `check_provider_endpoint: true` is set to enable model discovery via the `/models` endpoint.
    *   **Include:** Add configurations for key model types needed: chat, vision, and potentially audio models if supported by the provider and LiteLLM.
4.  **Review:** Examine `docker-compose.litellm-proxy.yml` to understand how the `config.yaml` is mounted and how environment variables are passed [5].
5.  **Ensure:** Verify that `docker-compose.litellm-proxy.yml` uses the `--env-file` option to load variables from `backend/app/.env` into the proxy container [5, 12, 13].
6.  **Execute:** Run the LiteLLM proxy using the command `docker-compose -f docker-compose.litellm-proxy.yml up -d` [8].
7.  **Verify:** Check Docker container status to confirm the proxy is running.

**Verification:**
*   Confirm the LiteLLM proxy Docker container is running.
*   Optionally, make a simple GET request to the proxy's `/models` endpoint (e.g., `http://localhost:4000/models` if running locally) to see the list of models exposed by the proxy.

**Status:** [x] COMPLETED

---

#### **Task 2: Implement Dynamic LLM Registry Service**

**Objective:** Develop the backend service responsible for fetching models from the LiteLLM proxy and providing a standardized interface to other application components.

**Context:**
*   The `llm_registry_service.py` file within `backend/app/utils/` is the place to implement this service [13-15].
*   It should fetch model information from the LiteLLM proxy's `/models` endpoint.
*   The service should ideally load and cache model information on application startup [16, 17].
*   It needs to handle standardizing model information received from the proxy for consistent internal use.

**Agent Instructions/Steps:**
1.  **Locate:** Find or create the file `backend/app/utils/llm_registry_service.py` [14, 15].
2.  **Implement:** Write the core logic for the `LLMRegistryService` class.
    *   **Add:** A method to fetch models from the configured LiteLLM proxy `/models` endpoint.
    *   **Add:** Logic to parse the response from the proxy and standardize the model data structure internally.
    *   **Implement:** Logic to load and cache the model list, potentially during the backend application's startup [16, 17].
3.  **Integrate:** Modify `backend/app/app_config.py` or `backend/app/main.py` (or an appropriate startup logic location) to initialize the `LLMRegistryService` instance and trigger the initial model fetching and caching when the backend starts [16-20].
4.  **Review:** Ensure the service handles potential errors during fetching (e.g., proxy not available) gracefully.

**Verification:**
*   Restart the backend application (e.g., using `docker-compose -f docker-compose.backend.yml up --build -d` after ensuring the proxy is running).
*   Access the debug endpoint `/debug/llm-registry-status` to verify that the service is initialized and has fetched models [21]. The output should list the models retrieved from the proxy.

**Status:** [x] COMPLETED

---

#### **Task 3: Create and Run LLM Registry Service Tests**

**Objective:** Write and execute specific tests to verify that the `llm_registry_service` correctly interacts with the LiteLLM proxy and handles models from different providers.

**Context:**
*   These tests are distinct from the end-to-end `crawl4ai` integration tests [22].
*   They should focus solely on the `llm_registry_service`'s ability to fetch and process data from the proxy's `/models` endpoint [23-26].
*   Tests need to cover different configured providers: Groq, Google, Ollama, LLM Studio, etc., including both cloud and local providers [23, 25, 26].
*   A new test file should be created for these tests [27].

**Agent Instructions/Steps:**
1.  **Create:** Create a new test file, for example, `backend/app/tests/live_llm_registry_tester.py` [27].
2.  **Implement:** Write test cases within this file.
    *   **Add:** A test function to verify that the `llm_registry_service` can be initialized and successfully fetches models from the proxy.
    *   **Add:** Test cases to check that models from each configured provider (Groq, Google, Ollama, LLM Studio) are present in the fetched list (assuming they are configured in `config.yaml`) [23, 25, 26].
    *   **Add:** Test cases to verify that the structure and key information (like model name, capabilities) of the fetched models are standardized correctly by the `llm_registry_service`.
    *   **Note:** These tests will require the LiteLLM proxy and the backend application (with the registry service initialized) to be running [28].
3.  **Update Documentation:** Add instructions to `docs/livetest_instructions.md` on how to run the `live_llm_registry_tester.py` script [27-29].
4.  **Execute:** Run the newly created test script (`live_llm_registry_tester.py`).

**Verification:**
*   All tests in `live_llm_registry_tester.py` should pass.
*   The `docs/livetest_instructions.md` file should contain clear instructions for running these specific tests [28].

**Status:** [x] COMPLETED

---

#### **Task 4: Integrate LLM Registry into Consumers (Crawl4AI, etc.)**

**Objective:** Modify backend components that use LLMs (starting with `crawl4ai_fetcher.py`) to obtain model information and configuration from the `llm_registry_service` instead of relying on hardcoded values or direct LLM provider calls.

**Context:**
*   `crawl4ai_fetcher.py` and potentially `psearchworking.py` are key consumers [9, 14, 15].
*   They need to access the `LLMRegistryService` instance to select and configure the correct models based on aliases or requirements.
*   This step ensures that these components route their LLM calls through the LiteLLM proxy via the registry service.

**Agent Instructions/Steps:**
1.  **Locate:** Find the relevant files that make direct LLM calls or configure LLMs, such as `backend/app/crawl4ai_fetcher.py` and `backend/app/psearchworking.py`.
2.  **Refactor:** Modify these files to obtain the `LLMRegistryService` instance (assuming it's initialized during app startup and accessible).
3.  **Update LLM Configuration:** Change how LLM models are configured within these components. Instead of setting provider-specific configurations directly, look up the required model details from the `LLMRegistryService` using the model aliases defined in `config.yaml` [30].
    *   **Ensure:** LLM calls within these components are now directed to the LiteLLM proxy's endpoint, using the model alias, and relying on the proxy to handle provider routing and authentication.
    *   **Consider:** How model capabilities (text, vision, audio) are checked or utilized based on the information from the registry.
4.  **Review:** Ensure that error handling related to LLM calls is still robust when routing through the registry and proxy [31].

**Verification:**
*   The code should compile and the backend should start without errors after modifications.
*   The application logs should indicate LLM calls being routed through the LiteLLM proxy address.
*   Basic manual tests (e.g., triggering a crawl that uses LLM extraction) should function correctly. Comprehensive testing is covered in the next task.

**Status:** [x] COMPLETED

---

#### **Implemented Endpoints Analysis**

**Objective:** Analyze the currently implemented LLM endpoints in the backend and compare them against the capabilities of the integrated LiteLLM providers.

**Context:**
* The primary LLM interaction endpoint currently implemented is in `backend/app/routes/llm_routes.py`.
* The `LLMRegistryService` in `backend/app/utils/llm_registry_service.py` is used to manage model access.
* LiteLLM supports various capabilities beyond basic chat completion, including embeddings, completions, vision, tool calling, etc., depending on the provider.

**Analysis:**
* The current implementation in `llm_routes.py` primarily exposes a generic `/chat/completions` endpoint.
* This endpoint effectively utilizes the `LLMRegistryService` to route chat requests to different providers based on the selected model alias.
* However, the current structure does not fully expose the broader capabilities offered by many LLM providers integrated via LiteLLM.

#### **Provider Capability Analysis**

**Objective:** Summarize the capabilities of the LiteLLM providers intended for integration (Groq, Google, Ollama, OpenAI, LLM Studio) based on their documentation.

**Context:**
* Refer to the LiteLLM provider documentation in `docs/litellm/docs/my-website/docs/providers/` for detailed capabilities.

**Capabilities Summary:**
*   **Groq:** Primarily focused on high-speed text generation (`/chat/completions`, `/completions`).
*   **Google (Gemini):** Supports `/chat/completions`, `/embeddings`, `/completions`, vision, tool calling (including Google Search and Code Execution tools), file handling (inline, https, gs://), context caching, and image generation.
*   **Ollama:** Supports `/chat/completions`, `/embeddings`, `/completions`, tool calling, and vision.
*   **OpenAI:** Supports `/chat/completions`, `/embeddings`, `/completions`, vision, function calling, fine-tuned models, audio transcription, and various advanced settings.
*   **LLM Studio:** Supports `/chat/completions`, `/embeddings`, and `/completions`. It is noted as being OpenAI-compatible.

**Comparison:**
* The current `/chat/completions` endpoint aligns with the core chat capabilities of all providers.
* Capabilities like embeddings, vision, tool/function calling, file handling, audio transcription, and image generation are not currently exposed by dedicated backend endpoints, despite being supported by several integrated providers.

#### **Refactoring Proposal: Expanding Backend LLM Endpoints**

**Objective:** Propose changes to the backend endpoint structure to better expose the diverse capabilities of the integrated LLM providers.

**Context:**
* The goal is to make the full range of LLM functionalities accessible to other backend services and future agents.
* This requires either adding new endpoints or enhancing existing ones to handle different types of LLM interactions.

**Proposal:**
To fully leverage the capabilities of the integrated LLM providers, the endpoint structure in `backend/app/routes/llm_routes.py` should be expanded. Two main approaches are possible:

1.  **Dedicated Endpoints:** Add new, specific endpoints for each major LLM capability.
    *   Examples: `/llm/embeddings`, `/llm/vision-analyze`, `/llm/transcribe-audio`, `/llm/generate-image`, `/llm/tool-call`.
    *   **Pros:** Clear separation of concerns, easier to understand and document each capability.
    *   **Cons:** Can lead to a large number of endpoints as more capabilities are added.

2.  **Enhanced Generic Endpoint:** Enhance the existing `/llm/chat/completions` endpoint (or a similar generic endpoint) to accept additional parameters or input structures that indicate the desired capability (e.g., including image data for vision, tool definitions for tool calling). LiteLLM can often handle routing these complex requests to the correct provider functionality.
    *   **Pros:** Fewer top-level endpoints, potentially simpler for consumers if the input structure is well-defined.
    *   **Cons:** The endpoint logic can become more complex, and documentation needs to clearly explain how to trigger different capabilities via the generic endpoint.

**Recommendation:**
A hybrid approach might be most effective. Maintain `/llm/chat/completions` for standard conversational interactions. Add dedicated endpoints for distinct modalities or complex operations like `/llm/embeddings`, `/llm/vision-analyze`, `/llm/transcribe-audio`, and `/llm/generate-image`. Tool/Function calling could potentially be integrated into the `/llm/chat/completions` endpoint as it's often part of a conversational flow, or a dedicated `/llm/tool-call` endpoint could be added if needed for more direct tool execution scenarios.

**Implications for `LLMRegistryService`:**
The `LLMRegistryService` will need to be updated to support these new endpoints and capabilities. This involves:
*   Fetching and storing more detailed capability information for each model from the LiteLLM `/models` endpoint.
*   Providing methods for consumers to query models based on required capabilities (e.g., `get_model_for_embeddings()`, `get_model_for_vision()`).
*   Potentially adding methods to directly call LiteLLM functions for embeddings, vision, etc., via the service, abstracting the direct LiteLLM calls away from the endpoint handlers.

**Testing Note:**
Implementing these new endpoints and updating the `LLMRegistryService` will require comprehensive testing to ensure each capability functions correctly with the configured providers. This will involve creating new test cases similar to those outlined in Task 5, specifically targeting the new endpoints and their interactions with different model types and capabilities.

---

#### **Task 4b: Enhance Backend LLM Endpoints for Full Capability Exposure (Refined Architecture)**

**Objective:** Refactor backend API endpoints in `backend/app/routes/` to directly call the LiteLLM proxy's data plane endpoints, leveraging the `LLMRegistryService` for model information, and expose the full range of LLM capabilities supported by integrated providers.

**Context:**
*   The LiteLLM proxy acts as the central gateway to various LLM providers.
*   The `LLMRegistryService` in `backend/app/utils/llm_registry_service.py` is responsible for fetching and providing standardized model *information* from the proxy's `/model/info` endpoint.
*   Backend endpoints in `backend/app/routes/llm_routes.py` need to be refactored to obtain model details from the registry and then make direct HTTP calls to the LiteLLM proxy's data plane endpoints (`/v1/chat/completions`, `/v1/embeddings`, etc.).
*   The goal is to expose the full range of LLM functionalities (including tool calling, diverse file types, provider-specific parameters) through these endpoints.

**Agent Instructions/Steps:**
1.  **Refactor `llm_routes.py` Endpoints:**
    *   Modify the endpoint functions (`/llm/chat`, `/llm/embeddings`, `/llm/generate-image`, `/llm/text-completion`, `/llm/transcribe-audio`, `/llm/text-to-speech`, `/llm/vision-analyze`) to obtain the `LLMRegistryService` instance using `get_llm_registry_service`.
    *   Use the registry instance to retrieve model details (e.g., using `get_model_details` or `get_available_models`) based on the requested `model_alias`.
    *   Construct the appropriate request payload for the LiteLLM proxy's data plane endpoint (`/v1/chat/completions`, `/v1/embeddings`, etc.). This includes mapping the incoming request body parameters (messages with multimodal content, tools, temperature, max_tokens, safety_settings, thinking, reasoning_effort, cache_control, extra_body, user, etc.) to the format expected by the LiteLLM proxy's data plane API.
    *   Make an asynchronous HTTP POST request directly to the LiteLLM proxy's relevant data plane endpoint (e.g., `LITELLM_PROXY_URL/v1/chat/completions`) using a library like `httpx`. Include the necessary headers, particularly the Authorization header with the `LITELLM_PROXY_API_KEY`.
    *   Process the HTTP response received from the proxy and map it to the appropriate Pydantic response model (`ChatCompletionResponse`, `EmbeddingResponse`, etc.). Handle potential errors from the proxy.
2.  **Keep `llm_registry_service.py` Focused:** Ensure `llm_registry_service.py` remains focused on fetching and providing model metadata from the proxy's `/model/info` endpoint. The existing functions for fetching and caching models (`_fetch_models_from_litellm_proxy`, `refresh_available_models`, `get_available_models`, `get_model_details`, `get_cache_status`, `initialize_llm_registry`) are suitable for this role and should be retained. The task-specific functions like `generate_embedding`, `transcribe_audio`, etc., that currently make HTTP calls to the proxy's data plane can be kept as helper functions within `llm_registry_service.py` (to be called by the refactored routes) or moved entirely into the route handlers if that simplifies the architecture. Keeping them as helper functions in `llm_registry_service.py` is recommended for cleaner route handlers.
3.  **Update Documentation:** Revise the API documentation file (`docs/api_llm_endpoints.md`) to accurately describe this interaction pattern, explaining that the backend endpoints call the LiteLLM proxy's data plane endpoints and how to use the various capabilities (tool calling, file types, parameters).

**Verification:**
*   Verify that the endpoint logic in `llm_routes.py` is refactored to call the LiteLLM proxy directly using `httpx`.
*   Confirm that the correct request payloads are constructed and sent to the proxy for each endpoint.
*   Verify that the responses from the proxy are correctly processed and mapped to the backend's response models.
*   Ensure the `LLMRegistryService` remains focused on providing model information.
*   Ensure the API documentation (`docs/api_llm_endpoints.md`) is updated to reflect the new interaction pattern and capabilities.
*   Basic manual tests or new targeted tests should confirm that the newly exposed capabilities function correctly by routing through the LiteLLM proxy.

**Status:** [x] COMPLETED

---

#### **Task 5: Create and Run New Crawl4AI Integration Tests**

**Objective:** Create *new* tests specifically to verify the end-to-end integration of `crawl4ai` using the `llm_registry_service` and routing calls through the LiteLLM proxy.

**Context:**
*   **Crucially, do NOT modify the existing `live_llm_extraction_advanced_tester.py` or other existing tests** [32-36]. Create entirely new test file(s).
*   These tests must cover different scenarios: text extraction, vision analysis, and audio transcription (if applicable and configured via the proxy) [34, 36].
*   Tests should use models from both cloud (Groq, Google, OpenAI) and local (Ollama, LLM Studio) providers configured in `config.yaml` [34, 36].
*   Refer to `docs/crawl4ai/docs/` for context on crawl4ai functionality, but the tests should focus on the integration with the new LLM infrastructure [33].

**Agent Instructions/Steps:**
1.  **Create:** Create a new test file, for example, `backend/app/tests/live_crawl4ai_registry_integration_tester.py` [35, 37].
2.  **Implement:** Write test cases within this file.
    *   **Add:** Test functions for basic crawl operations that *do* involve LLM calls via the registry and proxy.
    *   **Create Test Cases:** Define test cases that use models specified by their aliases from `config.yaml`, covering:
        *   Text extraction using a configured text model (e.g., from Groq, Google, Ollama).
        *   Vision analysis using a configured vision model (e.g., from Google, OpenAI, LLM Studio).
        *   Audio transcription using a configured audio model (if applicable) [34, 36].
    *   **Ensure:** The tests obtain model details from the `llm_registry_service` using model aliases before initiating crawl/extraction operations, mimicking how consumers will use the registry [30].
    *   **Include:** Cover both cloud and local model scenarios [34, 36].
    *   **Note:** These tests require the LiteLLM proxy, the backend application (with registry and integrated consumers), and any necessary local models (like Ollama) to be running.
3.  **Update Documentation:** Add instructions to `docs/livetest_instructions.md` on how to run the `live_crawl4ai_registry_integration_tester.py` script [37-39]. Include specific instructions on using `docker-compose -f docker-compose.litellm-proxy.yml up -d` to start *just* the proxy before running these tests [38, 39].
4.  **Execute:** Run the newly created test script (`live_crawl4ai_registry_integration_tester.py`).

**Verification:**
*   All tests in `live_crawl4ai_registry_integration_tester.py` should pass for correctly configured providers and running local models.
*   The `docs/livetest_instructions.md` file should contain clear instructions for running these specific tests, including launching the proxy independently [38, 39].

**Status:** [x] COMPLETED

---

#### **Task 6: Enhance and Integrate Ollama Initialization Script**

**Objective:** Modify the existing `backend/app/ollama_initializer.py` script to robustly check if a selected Ollama model is loaded and load it via Ollama if necessary, and integrate this script into the backend startup process in `backend/app/main.py`.

**Context:**
*   The existing `backend/app/ollama_initializer.py` script provides a starting point for identifying Ollama models and initiating loading.
*   The script should only attempt to load an Ollama model if an Ollama model alias is selected in the backend configuration (`app_config`).
*   The script needs a more reliable way to check if an Ollama model is loaded and to initiate the loading process if needed, preferably using the Ollama API or a more robust subprocess command, handling potential errors gracefully.
*   The script must be executed during the backend application's startup sequence in `backend/app/main.py`, ideally before the LLM registry attempts to fetch models from the LiteLLM proxy.
*   The LiteLLM proxy will then connect to the running Ollama instance to serve the model.

**Agent Instructions/Steps:**

1.  **Review:** Re-examine the existing `backend/app/ollama_initializer.py` script to fully understand its current implementation.
2.  **Enhance Ollama Check/Load Logic:** Modify `backend/app/ollama_initializer.py` to improve the robustness of checking if an Ollama model is loaded and loading it.
    *   **Option A (Preferred):** Use the Ollama API (via `httpx`) to check for loaded models (`/api/tags`) and initiate pulls (`/api/pull`). Implement error handling for server not running or API errors.
    *   **Option B (Alternative):** If using subprocess, improve the logic to check `ollama list` first and only run `ollama run` if the model is not listed, adding timeouts and handling potential interactive prompts or errors.
    *   **Ensure:** The script logs informative messages about the process and handles errors gracefully without blocking backend startup indefinitely.
3.  **Integrate into Backend Startup:** Modify `backend/app/main.py` to call the `initialize_ollama_model` function from `ollama_initializer.py` within the `@app.on_event("startup")` event handler.
    *   **Ensure:** The call to `initialize_ollama_model` happens *before* the call to `initialize_llm_registry`.
4.  **Update Documentation:** Add instructions to `docs/llm_provider_setup_instructions.md` (or a relevant documentation file) explaining the purpose of `ollama_initializer.py` and how it works, including any necessary Ollama setup steps for the user.

**Verification:**
*   Configure an Ollama model alias in your backend's environment variables (`LLM_MODEL`) and LiteLLM proxy config (`config.yaml`).
*   Ensure the Ollama server is running locally.
*   Start the backend application.
*   Check the backend logs to confirm that `ollama_initializer.py` ran, identified the Ollama model, and attempted to load it if necessary.
*   Verify that the LiteLLM proxy can successfully connect to and serve the Ollama model.

**Status:** [x] COMPLETED

---

#### **Task 7: Implement LiteLLM Proxy Enhancements (Logging, Discovery Robustness)**

**Objective:** Enhance the LiteLLM proxy configuration to include improved logging (OpenTelemetry, raw requests) and ensure the dynamic discovery setup is robust.

**Context:**
*   Review of LiteLLM documentation identified potential enhancements like callbacks for logging and `log_raw_request_response` [11, 42].
*   OpenTelemetry (`otel`) is a suitable callback for integrating with monitoring stacks like Prometheus and Grafana.
*   Ensuring robust dynamic discovery configuration is key for easily adding/updating models via `config.yaml`.

**Agent Instructions/Steps:**
1.  **Review:** Examine the updated `litellm_proxy_config/config.yaml` file.
2.  **Modify:** Update `litellm_proxy_config/config.yaml` to implement the enhancements:
    *   **Add:** Include `log_raw_request_response: true` under `litellm_settings` to enable logging of raw requests and responses [45, 46].
    *   **Configure Callback:** Add `otel` to the `callbacks` list under `litellm_settings`.
    *   **Remove:** Remove any `callback_vars` section previously added for other callbacks (like Supabase).
    *   **Review:** Double-check the provider configurations to ensure `check_provider_endpoint: true` is consistently set and that the model aliases (`model_name`) and actual provider model IDs (`litellm_params.model`) are correct based on documentation review.
3.  **Restart:** Restart the LiteLLM proxy container using `docker-compose -f docker-compose.litellm-proxy.yml down` followed by `docker-compose -f docker-compose.litellm-proxy.yml up -d` to apply the configuration changes.

**Verification:**
*   Check the proxy container logs to confirm successful startup without the previous `FileNotFoundError`.
*   Make some LLM calls through the proxy (e.g., via the debug endpoint or by running the test scripts).
*   **Note:** Verifying that telemetry data is received by Prometheus and visualized in Grafana requires additional configuration of an OpenTelemetry collector and your monitoring stack, which is outside the scope of this specific LiteLLM configuration task but is necessary for end-to-end monitoring.

**Status:** [x] COMPLETED

---

#### **Task 7b: Implement and Test MCP Integration**

**Objective:** Configure the LiteLLM proxy to expose MCP tools and verify that backend services or external clients can list and call these tools through the proxy.

**Context:**
*   The LiteLLM proxy supports defining and exposing MCP servers and their tools via the `/mcp/tools/list` and `/mcp/tools/call` endpoints.
*   The `docs/litellm/docs/my-website/docs/mcp.md` document provides details on configuring `mcp_servers` in `config.yaml` and using the LiteLLM Python SDK as an MCP client bridge.
*   This task builds upon the functional LiteLLM proxy setup and aims to extend its capabilities to include MCP tool management.

**Agent Instructions/Steps:**
1.  **Review:** Examine the `docs/litellm/docs/my-website/docs/mcp.md` document to understand the configuration and usage of MCP with LiteLLM.
2.  **Modify `litellm_proxy_config/config.yaml`:** Add or update the `mcp_servers` section in `config.yaml` to define the MCP servers that the proxy should connect to and expose.
    *   **Ensure:** The `url` for each MCP server is correctly specified.
3.  **Restart LiteLLM Proxy:** Restart the LiteLLM proxy container to apply the `mcp_servers` configuration.
4.  **Implement Verification:** Write or adapt a script (potentially a new test file like `backend/app/tests/live_mcp_integration_tester.py`) to verify the MCP integration.
    *   **Add:** Logic to connect to the LiteLLM proxy's MCP endpoint (e.g., `http://localhost:4000/mcp/`).
    *   **Add:** A test case to list the available MCP tools via the proxy's `/mcp/tools/list` endpoint.
    *   **Add:** Test cases to call a sample MCP tool via the proxy's `/mcp/tools/call` endpoint, ensuring the call is routed correctly to the underlying MCP server and the result is received.
    *   **Note:** This requires the configured MCP servers to be running and accessible to the LiteLLM proxy.
5.  **Update Documentation:** Add instructions to `docs/livetest_instructions.md` on how to run the new MCP integration test script and any necessary setup steps for the MCP servers.

**Verification:**
*   The LiteLLM proxy container should restart successfully with the new `mcp_servers` configuration.
*   The MCP integration test script (`live_mcp_integration_tester.py`) should successfully list and call the configured MCP tools via the LiteLLM proxy.
*   The `docs/livetest_instructions.md` file should contain clear instructions for running these tests and setting up required MCP servers.

**Status:** [ ] PENDING

---

#### **Task 8: Update Documentation**

**Objective:** Ensure the project documentation reflects the new LLM management system, including setup, configuration, testing, and how to use the new features.

**Context:**
*   The `docs/livetest_instructions.md` file needs updates for running the new test scripts and launching the proxy [27-29, 37-39].
*   General project documentation (potentially a new file like `docs/llm_model_management.md`) is needed to explain the system architecture and how to configure providers via the proxy [47-49].
*   Instructions for running the separate Docker Compose files should be included [8].

**Agent Instructions/Steps:**
1.  **Update `docs/livetest_instructions.md`:**
    *   **Add:** A section with instructions for running `live_llm_registry_tester.py` [27-29].
    *   **Add:** A section with instructions for running `live_crawl4ai_registry_integration_tester.py` [37-39].
    *   **Include:** In both new sections, provide the command `docker-compose -f docker-compose.litellm-proxy.yml up -d` and emphasize that the proxy must be running before executing the tests [38, 39].
    *   **Clarify:** Note that the existing `live_llm_extraction_advanced_tester.py` tests are being replaced or augmented by the new integration tests [32-36].
2.  **Create/Update LLM Management Documentation:**
    *   **Determine:** Decide if a new file (`docs/llm_model_management.md`) is best, or if integration into an existing overview document is preferable [47-49].
    *   **Document:** Explain the centralized LLM model management system: the role of the LiteLLM proxy, the `llm_registry_service`, and how consumers interact with it.
    *   **Provide:** Instructions on how to configure new LLM providers by modifying `litellm_proxy_config/config.yaml`, referencing the LiteLLM provider documentation.
    *   **Explain:** How API keys are handled securely via environment variables and `--env-file`.
    *   **Include:** Instructions for running the LiteLLM proxy and backend services using the separate Docker Compose files (`docker-compose.litellm-proxy.yml` and `docker-compose.backend.yml`) [8].
3.  **Review:** Read through the updated/new documentation to ensure clarity, accuracy, and completeness.

**Verification:**
*   The `docs/livetest_instructions.md` file accurately reflects how to run the new tests.
*   New or updated documentation clearly explains the LLM system and configuration process.
*   Docker instructions are updated to reference the separate compose files [50].

**Status:** [ ] PENDING

---

#### **Task 9: Address Pending Backend Test Fixes (Cross-Reference)**

**Objective:** Review `docs/new_test_plan.md` to identify any other pending test fixes or issues related to the `/fetch-content` endpoint and crawl4ai integration that were not covered by the `test_crawl4ai_fetcher_llmconfig.py` work. Address these as per the workflow in that document.

**Context:**
*   This task ensures all known issues from `new_test_plan.md` related to the `/fetch-content` endpoint's LLM functionalities (especially `LLMExtractionStrategy`) are resolved.
*   Focus areas include:
    *   Ensuring correct `fetch_history` status updates, especially for terminal states like "failed" or "success" when LLM errors occur or client cancels.
    *   Improving how LLM-specific errors from `LLMExtractionStrategy` in `crawl4ai_fetcher.py` are reported back through SSE events (e.g., ensuring a clear "error" type event with structured error details, rather than embedding errors in "completed" events).
    *   Verifying that fixes allow previously "UNEXPECTED PASS" test cases in `test_crawl4ai_fetcher_llmconfig.py` (as detailed in `new_test_plan.md`) to behave as expected (i.e., correctly identify and report failure conditions).
*   Work involved changes to `backend/app/main.py` (SSE handling, `terminal_status_written_to_db` logic) and `backend/app/crawl4ai_fetcher.py` (explicit LLM error detection and SSE event generation).

**Agent Instructions/Steps:**
1.  **Review `docs/new_test_plan.md`:** Identify all outstanding issues related to `/fetch-content`, `crawl4ai_fetcher.py` LLM usage, and associated tests.
2.  **Implement Fixes:**
    *   **Fetch History Status:** Modify `backend/app/main.py` in the `/fetch-content` endpoint to ensure `terminal_status_written_to_db` is correctly set when an LLM error (propagated from `crawl4ai_fetcher.py`) or client cancellation leads to a "failed" status update in `fetch_history`.
    *   **LLM Error Reporting:** Modify `backend/app/crawl4ai_fetcher.py` (`fetch_with_crawl4ai` generator) to explicitly detect if `LLMExtractionStrategy` was used and failed (e.g., `result.error` is set, or `result.extracted_content` is missing when it shouldn't be). If so, construct and `yield` a dedicated SSE event of `type: "error"` with a structured `llm_error` field, and then `return` from the generator to prevent sending a subsequent "completed" event.
3.  **Verify:**
    *   Confirm that the "UNEXPECTED PASS" test cases from `docs/new_test_plan.md` now behave as expected (e.g., tests designed to fail due to invalid LLM configs now correctly show as failing, or appropriately signal the error if the test asserts an error state).
    *   Manually test scenarios if necessary to confirm robust error handling and status updates.

**Status:** [x] COMPLETED

---

#### **Task 9a: LLMConfig Parameter Handling and Proxy Routing**

**Objective:** Review `docs/new_test_plan.md` to identify any other pending test fixes or issues related to the `/fetch-content` endpoint and crawl4ai integration that were not covered by the `test_crawl4ai_fetcher_llmconfig.py` work. Address these as per the workflow in that document.

**Context:**
*   This task ensures all known issues from `new_test_plan.md` related to the `/fetch-content` endpoint's LLM functionalities (especially `LLMExtractionStrategy`) are resolved.
*   Focus areas include:
    *   Ensuring correct `fetch_history` status updates, especially for terminal states like "failed" or "success" when LLM errors occur or client cancels.
    *   Improving how LLM-specific errors from `LLMExtractionStrategy` in `crawl4ai_fetcher.py` are reported back through SSE events (e.g., ensuring a clear "error" type event with structured error details, rather than embedding errors in "completed" events).
    *   Verifying that fixes allow previously "UNEXPECTED PASS" test cases in `test_crawl4ai_fetcher_llmconfig.py` (as detailed in `new_test_plan.md`) to behave as expected (i.e., correctly identify and report failure conditions).
*   Work involved changes to `backend/app/main.py` (SSE handling, `terminal_status_written_to_db` logic) and `backend/app/crawl4ai_fetcher.py` (explicit LLM error detection and SSE event generation).

**Agent Instructions/Steps:**
1.  **Review `docs/new_test_plan.md`:** Identify all outstanding issues related to `/fetch-content`, `crawl4ai_fetcher.py` LLM usage, and associated tests.
2.  **Implement Fixes:**
    *   **Fetch History Status:** Modify `backend/app/main.py` in the `/fetch-content` endpoint to ensure `terminal_status_written_to_db` is correctly set when an LLM error (propagated from `crawl4ai_fetcher.py`) or client cancellation leads to a "failed" status update in `fetch_history`.
    *   **LLM Error Reporting:** Modify `backend/app/crawl4ai_fetcher.py` (`fetch_with_crawl4ai` generator) to explicitly detect if `LLMExtractionStrategy` was used and failed (e.g., `result.error` is set, or `result.extracted_content` is missing when it shouldn't be). If so, construct and `yield` a dedicated SSE event of `type: "error"` with a structured `llm_error` field, and then `return` from the generator to prevent sending a subsequent "completed" event.
3.  **Verify:**
    *   Confirm that the "UNEXPECTED PASS" test cases from `docs/new_test_plan.md` now behave as expected (e.g., tests designed to fail due to invalid LLM configs now correctly show as failing, or appropriately signal the error if the test asserts an error state).
    *   Manually test scenarios if necessary to confirm robust error handling and status updates.

**Status:** [x] COMPLETED

---

#### **Task 10: Docker Compose and Environment Variable Hardening for Backend**

**Objective:** Ensure the backend services are robustly configured and tested with Docker Compose and environment variable hardening.

**Context:**
*   This task ensures that the backend services are correctly configured and tested with Docker Compose.
*   It also includes hardening environment variables to ensure security and reliability.

**Agent Instructions/Steps:**
1.  **Review:** Examine the `docker-compose.backend.yml` file to ensure all services are correctly configured.
2.  **Verify:** Run the backend services using `docker-compose -f docker-compose.backend.yml up --build -d`.
3.  **Ensure:** Verify that all services start without errors.
4.  **Hardening:** Implement environment variable hardening for sensitive configurations.

**Verification:**
*   Confirm that the backend services start successfully.
*   Ensure that sensitive configurations are not exposed in environment variables.

**Status:** [x] COMPLETED

---

#### **Deliverables:**

*   An updated `litellm_proxy_config/config.yaml`