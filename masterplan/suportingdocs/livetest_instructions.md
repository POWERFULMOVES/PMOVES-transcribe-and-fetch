**Note:** The tests in this document related to `live_llm_extraction_advanced_tester.py` are being augmented or replaced by the new integration tests (`live_llm_registry_tester.py` and `live_crawl4ai_registry_integration_tester.py`). These new tests provide more focused and robust validation of the LLM integration through the LiteLLM proxy and `LLMRegistryService`.

Here is a recommended testing strategy for the advanced LLMExtractionStrategy parameters using the live_llm_extraction_advanced_tester.py script:

virtual environment must be activated before running commands

.venv\Scripts\activate

## Overall Progress & Recent Updates

Significant progress has been made on backend stability and functionality. Key updates relevant to testing include:

1.  **`fetch_history` Status Bug Resolved:** The previously identified bug affecting status updates within the `fetch_history` mechanism (related to [`backend/app/main.py`](backend/app/main.py:1)) has been successfully fixed. This ensures more accurate tracking of fetch job statuses.
2.  **Comprehensive LLM Logging & Error Handling:** A robust system for logging LLM calls and handling errors has been implemented. This features:
    *   A new `llm_call_logs` database table for persistent storage of LLM call details.
    *   The `log_llm_call` utility function, located in [`backend/app/utils/llm_logging.py`](backend/app/utils/llm_logging.py:1), for standardized logging.
    *   Integration of this logging mechanism into the `/fetch-content` endpoint.
    These improvements provide enhanced visibility into LLM operations and facilitate easier debugging.
3.  **Utility Module Refactoring:** Core utility modules, including [`backend/app/general_utils.py`](backend/app/general_utils.py:1) and the `backend/app/utils/` package, have undergone significant refactoring to improve code organization and maintainability. Detailed documentation of these changes can be found in [`docs/refactoring_utility_modules.md`](docs/refactoring_utility_modules.md).

These updates have been integrated, and the focus now includes ensuring their stability and verifying no regressions were introduced.

## LLMConfig Parameter Handling Tests

These tests (`backend/app/tests/test_crawl4ai_fetcher_llmconfig.py`) specifically verify how the `crawl4ai_fetcher.py` module handles the configuration of `crawl4ai`'s `LLMConfig` when the `LLMExtractionStrategy` is used. They focus on ensuring that the correct parameters (provider, api_token, base_url) are passed to `LLMConfig` based on the input request parameters and environment variables, and that error handling for missing or invalid parameters is functioning as expected.

**Key aspects covered by these tests:**

*   **Provider Parsing:** Verifies that the `llm_model_id_for_extraction` (or the deprecated `llm_provider_model`) from the request is correctly used as the `provider` for `LLMConfig`.
*   **API Token Precedence:** Tests that the `llm_api_token` from the request takes precedence over the `LITELLM_PROXY_API_KEY` environment variable, and that appropriate warnings are logged when no token is explicitly set.
*   **Base URL Handling:** Confirms that the `base_url` for `LLMConfig` is always set to the `LITELLM_PROXY_URL` and that any `llm_base_url` provided in the request is ignored with a warning.
*   **Missing Parameter Handling:** Verifies that the fetcher gracefully handles cases where the LLM provider is missing, yielding an error event.
*   **Default Instruction:** Ensures that a default instruction is used when `llm_instructions` is not provided in the request.
*   **Instantiation Errors:** Tests that exceptions raised during the instantiation of `LLMConfig` or `LLMExtractionStrategy` are caught and handled, resulting in an error event and the `extraction_strategy` not being set on the `CrawlerRunConfig`.

**Note on "UNEXPECTED PASS" Scenarios:** Recent enhancements to `backend/app/crawl4ai_fetcher.py` include more explicit detection and reporting of LLM-specific errors (e.g., when `LLMExtractionStrategy` fails due to invalid configuration, model issues, or provider errors). The fetcher now yields a structured "error" type Server-Sent Event (SSE) with detailed `llm_error` information in such cases. While `test_crawl4ai_fetcher_llmconfig.py` primarily uses mocks, the fetcher logic it tests is now designed to clearly signal these failures. This improved error signaling is crucial for ensuring that tests (including live tests that depend on this fetcher logic) accurately reflect error states, helping to resolve previous "UNEXPECTED PASS" situations where an LLM operation might have failed silently or ambiguously.

**Prerequisites:**

*   Ensure your Python virtual environment is activated.
*   These are unit/integration tests that mock external dependencies like `AsyncWebCrawler` and the LLM registry service. They do **not** require the LiteLLM proxy or the full backend application to be running.

**How to Run:**

Navigate to the project root directory in your terminal and run the following command:

```bash
pytest backend/app/tests/test_crawl4ai_fetcher_llmconfig.py
```

Review the output to ensure all test cases pass, confirming the correct handling of LLM configuration parameters within the `crawl4ai_fetcher`.

**Update (YYYY-MM-DD):** All tests in `test_crawl4ai_fetcher_llmconfig.py` are currently passing after addressing initial issues with mock usage and redundant `LLMConfig` instantiations in the fetcher code, and correcting assertions in the tests.

Overall Rationale:

Isolate Parameter Testing: Each initial batch focuses on a specific group of related parameters.
Progressive Complexity: Start with basic valid cases, then move to defaults, invalid inputs, and combinations.
Clear Debugging: Failures in a batch help narrow down problematic parameters.
Manageable Execution: Batches help manage time, especially for slower tests.
Proposed Test Execution Strategy:

Batch 1: Core llm_extraction_type Functionality (Text & Markdown)

Focus: Basic text/markdown extraction, default/specific models, handling of null/missing type.
Test Cases:
LLMExtract_Type_Text_Google_DefaultInstruction
LLMExtract_Type_Text_SpecificModel_Google
LLMExtract_Type_Markdown_Google
LLMExtract_Type_Null_ShouldDefaultToText_Google
LLMExtract_Type_Missing_ShouldDefaultToText_Google
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_Type_Text_Google_DefaultInstruction" "LLMExtract_Type_Text_SpecificModel_Google" "LLMExtract_Type_Markdown_Google" "LLMExtract_Type_Null_ShouldDefaultToText_Google" "LLMExtract_Type_Missing_ShouldDefaultToText_Google"
```

**Status (2025-05-11):** Batch 1 executed.
*   All 5 tests in Batch 1 passed as expected after fixing the `AttributeError` in `backend/app/crawl4ai_fetcher.py`, correcting SSE error message formatting in `backend/app/main.py`, and changing the URL for relevant tests to `https://www.example.com` to bypass external website issues for testing purposes.

Batch 2: llm_extraction_type - JSON and Schema Handling

Focus: JSON extraction (inferred and schema-defined), invalid schema, schema with non-JSON type.
Test Cases:
LLMExtract_Type_Json_Google_NoSchema
LLMExtract_Type_Json_SpecificModel_WithSchema_Google
LLMExtract_Type_Json_InvalidSchema_Google
LLMExtract_JsonSchema_Provided_But_Type_Not_Json_Google
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_Type_Json_Google_NoSchema" "LLMExtract_Type_Json_SpecificModel_WithSchema_Google" "LLMExtract_Type_Json_InvalidSchema_Google" "LLMExtract_JsonSchema_Provided_But_Type_Not_Json_Google"
```

**Status (2025-05-11):** Batch 2 executed.
*   3 tests passed as expected: `LLMExtract_Type_Json_Google_NoSchema`, `LLMExtract_Type_Json_SpecificModel_WithSchema_Google`, and `LLMExtract_JsonSchema_Provided_But_Type_Not_Json_Google`.
*   `LLMExtract_JsonSchema_Provided_But_Type_Not_Json_Google` passed after changing its URL to `https://www.example.com` to resolve a timeout issue with the previous URL.
*   `LLMExtract_Type_Json_InvalidSchema_Google` unexpectedly passed. This test was expected to fail because it provides an invalid JSON schema. The observed behavior is that the backend/crawl4ai attempts LLM extraction and returns content even with an invalid schema, which the test script interprets as a pass. This indicates that providing an invalid schema does not cause a hard failure in the backend's LLM extraction process.

Batch 3: Invalid llm_extraction_type and llm_provider_model Validation

Focus: Handling invalid llm_extraction_type string and non-existent llm_provider_model.
Test Cases:
LLMExtract_Type_InvalidString_ShouldFailOrHandle
LLMExtract_Model_InvalidNonExistent
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_Type_InvalidString_ShouldFailOrHandle" "LLMExtract_Model_InvalidNonExistent"
```

**Status (2025-05-11):** Batch 3 executed.
*   `LLMExtract_Type_InvalidString_ShouldFailOrHandle_Google`: UNEXPECTED PASS (Expected to fail).
*   `LLMExtract_Model_InvalidNonExistent`: UNEXPECTED PASS (Expected to fail).

Batch 4: llm_instruction Handling

Focus: Behavior when llm_instruction is not provided (default) or is empty.
Test Cases:
LLMExtract_Instruction_NotProvided_ShouldUseDefault
LLMExtract_Instruction_EmptyString
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_Instruction_NotProvided_ShouldUseDefault" "LLMExtract_Instruction_EmptyString"
```

**Status (2025-05-11):** Batch 4 executed.
*   `LLMExtract_Instruction_NotProvided_ShouldUseDefault_Google`: PASS (Expected).
*   `LLMExtract_Instruction_EmptyString_Google`: PASS (Expected).

Batch 5: Override Parameters - llm_context_window_limit_override

Focus: llm_context_window_limit_override (valid, invalid type, zero value).
Test Cases:
LLMExtract_ContextWindowOverride_Valid
LLMExtract_ContextWindowOverride_InvalidType
LLMExtract_ContextWindowOverride_Zero
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_ContextWindowOverride_Valid" "LLMExtract_ContextWindowOverride_InvalidType" "LLMExtract_ContextWindowOverride_Zero"
```

**Status (2025-05-11):** Batch 5 executed.
*   `LLMExtract_ContextWindowOverride_Valid_Google`: PASS (Expected).
*   `LLMExtract_ContextWindowOverride_InvalidType_Google`: UNEXPECTED PASS (Expected to fail).
*   `LLMExtract_ContextWindowOverride_Zero_Google`: UNEXPECTED PASS (Expected to fail).

Batch 6: Override Parameters - llm_max_tokens_override

Focus: llm_max_tokens_override (valid, invalid type, zero value).
Test Cases:
LLMExtract_MaxTokensOverride_Valid
LLMExtract_MaxTokensOverride_InvalidType
LLMExtract_MaxTokensOverride_Zero
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_MaxTokensOverride_Valid" "LLMExtract_MaxTokensOverride_InvalidType" "LLMExtract_MaxTokensOverride_Zero"
```

**Status (2025-05-11):** Batch 6 executed.
*   `LLMExtract_MaxTokensOverride_Valid_Google`: PASS (Expected).
*   `LLMExtract_MaxTokensOverride_InvalidType_Google`: UNEXPECTED PASS (Expected to fail).
*   `LLMExtract_MaxTokensOverride_Zero_Google`: UNEXPECTED PASS (Expected to fail).

Batch 7: Combination and General Default Tests

Focus: Multiple parameters combined and reliance on backend defaults with minimal parameters.
Test Cases:
LLMExtract_MinimalParams_Text_ShouldUseBackendDefaults
LLMExtract_Combination_AllParams_Text_Google
LLMExtract_Combination_AllParams_Json_WithSchema_Google
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_MinimalParams_Text_ShouldUseBackendDefaults" "LLMExtract_Combination_AllParams_Text_Google" "LLMExtract_Combination_AllParams_Json_WithSchema_Google"
```

**Status (2025-05-11):** Batch 7 executed.
*   `LLMExtract_MinimalParams_Text_ShouldUseBackendDefaults`: PASS (Expected).
*   `LLMExtract_Combination_AllParams_Text_Google`: PASS (Expected).
*   `LLMExtract_Combination_AllParams_Json_WithSchema_Google`: PASS (Expected).

Batch 8: Special Configuration & Large Content Tests (Potentially Rate-Limit Sensitive)

Focus: Test requiring user-provided API token and large content tests (potential rate limits).
Test Cases:
LLMExtract_ValidRequestTokenInExtractionConfig (Requires user action: update token in script)
LLMExtract_ContentTooLargeForDefaultContext_NoOverride_Google
LLMExtract_ContentTooLarge_WithSufficientContextOverride_Google
Command:
```bash
python live_llm_extraction_advanced_tester.py -t "LLMExtract_ValidRequestTokenInExtractionConfig" "LLMExtract_ContentTooLargeForDefaultContext_NoOverride_Google" "LLMExtract_ContentTooLarge_WithSufficientContextOverride_Google"
```

**Status (Updated 2025-05-11):**
*   `LLMExtract_ValidRequestTokenInExtractionConfig`:
    *   **Current Status:** Requires review and action.
    *   **Details:** This test is currently **commented out** within the [`live_llm_extraction_advanced_tester.py`](live_llm_extraction_advanced_tester.py:1) script. It was designed as a Groq-specific example to test the `request_token` parameter within `extraction_config`.
    *   **Clarification:** Previous references to a `_Google` suffixed version of this test (e.g., `LLMExtract_ValidRequestTokenInExtractionConfig_Google`) were a misunderstanding. The focus should be on the actual `LLMExtract_ValidRequestTokenInExtractionConfig` test definition as found (and currently commented out) in the script.
    *   **Action Needed:** This test needs to be reviewed. See "Next Steps for Live Testing" for details.
*   `LLMExtract_ContentTooLargeForDefaultContext_NoOverride_Google`: PASS (Expected). This test completed successfully with an increased timeout (600s) as per previous updates.
*   `LLMExtract_ContentTooLarge_WithSufficientContextOverride_Google`: PASS (Expected). This test also completed successfully with the increased timeout.
*   **Context from Previous Updates for Large Content Tests:**
    *   Validation logic in `backend/app/crawl4ai_fetcher.py` was updated.
    *   Timeout for these large content tests in [`live_llm_extraction_advanced_tester.py`](live_llm_extraction_advanced_tester.py:1) was increased from 180s to 600s.
    *   Duration logging was added to `backend/app/crawl4ai_fetcher.py` for LLM extractions.
    *   The increased timeout allows these large content tests to complete. Further optimization for large content handling might still be beneficial.

Note for Batch 8: The script's `SKIP_KNOWN_RATE_LIMIT_SENSITIVE_TESTS` flag (see [`live_llm_extraction_advanced_tester.py`](live_llm_extraction_advanced_tester.py:1)) is `True` by default. To run the large content tests (`LLMExtract_ContentTooLarge...`), ensure this is set to `False` and be mindful of API rate limits. The `LLMExtract_ValidRequestTokenInExtractionConfig` test status is independent of this flag.

## Next Steps for Live Testing

Given the recent backend updates and the current state of test definitions, the following actions are recommended:

1.  **Review and Address `LLMExtract_ValidRequestTokenInExtractionConfig`:**
    *   **Uncomment and Review:** Examine the commented-out `LLMExtract_ValidRequestTokenInExtractionConfig` test in [`live_llm_extraction_advanced_tester.py`](live_llm_extraction_advanced_tester.py:1).
    *   **Assess Relevance:** Determine if this Groq-specific test for `request_token` is still needed or if its purpose is covered elsewhere.
    *   **Adapt or Replace:**
        *   If relevant, adapt it for current API key handling and ensure it can be run (e.g., update placeholder tokens, ensure provider compatibility).
        *   Consider if a Google-specific equivalent (or other provider-specific tests for `request_token`) is necessary and should be created.
    *   **Update Documentation:** Reflect the outcome of this review in this document.

2.  **Regression Testing for Recent Changes:**
    *   **Execute Key Tests:** Run a selection of tests from Batches 1-7 to ensure the `fetch_history` fix, new LLM logging/error handling, and utility module refactoring have not introduced any regressions.
    *   **Focus Areas:**
        *   Tests involving different `llm_extraction_type` values (Batches 1 & 2).
        *   Tests for error conditions and overrides (Batches 3, 5, 6) to verify the new error handling and logging capture issues correctly.
        *   Combination tests (Batch 7) to check overall integration.
    *   **Monitor Logs:** Pay close attention to backend logs and the new `llm_call_logs` table during these tests to verify the logging system is functioning as expected.

3.  **Verify Unexpected Pass Behaviors:**
    *   Re-evaluate tests that previously passed unexpectedly (e.g., `LLMExtract_Type_Json_InvalidSchema_Google` from Batch 2, several tests from Batches 3, 5, 6).
    *   Determine if the backend behavior is now correctly flagging these as errors due to improved validation or if the test expectations need adjustment.

By addressing these items, we can ensure the stability of recent enhancements and maintain comprehensive test coverage.

## Live LLM Registry Service Tests

These tests verify that the backend's `llm_registry_service` can successfully fetch and standardize the list of available LLM models from the LiteLLM proxy, covering different provider types (cloud and local) and specific providers (OpenAI, Groq, Google, Ollama, LLM Studio) as configured in `litellm_proxy_config/config.yaml`.

**Prerequisites:**

*   Ensure your LiteLLM proxy is running and accessible at the URL specified by the `LITELLM_PROXY_URL` environment variable in your `backend/app/.env` file (defaults to `http://localhost:4000`). You can start it using:
    ```bash
    docker-compose -f docker-compose.litellm-proxy.yml up -d
    ```
*   Ensure your `litellm_proxy_config/config.yaml` file is correctly configured with the providers you want to test (OpenAI, Groq, Google, Ollama, LM Studio, etc.) and that the necessary API keys are set in your `backend/app/.env` file and referenced correctly in the `config.yaml` using `os.environ/`.
*   Ensure your Python virtual environment is activated.

**How to Run:**

Navigate to the project root directory in your terminal and run the following command:

```bash
python backend/app/tests/live_llm_registry_tester.py
```

Review the output to ensure all test cases pass, confirming the `llm_registry_service` correctly interacts with the proxy.

## Live Crawl4AI Integration Tests

These tests are designed to perform end-to-end verification of the `crawl4ai` fetching mechanism (`backend/app/crawl4ai_fetcher.py`) when it's integrated with the `LLMRegistryService` and routes its LLM calls through the LiteLLM proxy. These tests cover scenarios where `crawl4ai` uses LLM-dependent features like `LLMExtractionStrategy` with various configurations.

**Key aspects covered by these tests:**

*   **Successful LLM Extraction:** Verifies that content can be extracted using `LLMExtractionStrategy` with different models (text, vision, potentially audio if configured) sourced via the LLM registry and routed through the proxy.
*   **Provider Diversity:** Aims to test with models from different providers (e.g., Groq, OpenAI, Google, local Ollama models) as configured in your LiteLLM proxy.
*   **Parameter Passthrough:** Ensures that LLM-specific parameters (e.g., `llm_model_name`, `extraction_config`, `llm_temperature`) are correctly passed from the `/fetch-content` endpoint request, through `crawl4ai_fetcher.py`, to `crawl4ai`, and ultimately to the LLM via the proxy.
*   **Error Handling:** Validates that if an LLM operation within `crawl4ai` fails (e.g., invalid model, API error from proxy/provider, schema validation error for JSON extraction), the `crawl4ai_fetcher.py` correctly detects this, logs it, updates `fetch_history`, and sends a structured "error" SSE event to the client, including `llm_error` details.

**Prerequisites:**

*   **LiteLLM Proxy:** Ensure your LiteLLM proxy is running and configured with the models you intend to test. Start it using:
    ```bash
    docker-compose -f docker-compose.litellm-proxy.yml up -d
    ```
*   **Backend Service:** The backend FastAPI application must be running, as these tests make live HTTP requests to the `/fetch-content` endpoint. Start it using (ensure it's built with the latest changes):
    ```bash
    docker-compose -f docker-compose.backend.yml up -d --build
    ```
*   **Environment Variables:** Ensure `backend/app/.env` is correctly configured with `LITELLM_PROXY_URL` (pointing to your proxy, e.g., `http://localhost:4000` if testing locally outside Docker, or `http://litellm-proxy:4000` if backend is also in Docker) and `LITELLM_PROXY_API_KEY` (if your proxy is secured with a master key). Provider-specific API keys should also be in this `.env` file for the proxy to use.
*   **Local Models (if testing Ollama):** If you are testing with Ollama models, ensure your Ollama service is running and the models specified in your `litellm_proxy_config/config.yaml` are pulled and available to Ollama. The backend's `ollama_initializer.py` script attempts to load configured Ollama models on startup.
*   **Python Virtual Environment:** Activate your Python virtual environment:
    ```bash
    .venv\\Scripts\\activate
    ```

**How to Run:**

Navigate to the project root directory in your terminal. The test script `live_crawl4ai_registry_integration_tester.py` typically contains various test functions that might be run individually or as a suite.

To run all tests in the file:
```bash
python backend/app/tests/live_crawl4ai_registry_integration_tester.py
```

To run specific test cases (if the script supports `-t` or similar, or by modifying the script's main execution block):
```bash
python backend/app/tests/live_crawl4ai_registry_integration_tester.py -t "TestName1" "TestName2"
```
(Consult the script's internal documentation or argument parser for specific ways to target tests if needed.)

**Expected Outcomes & Verification:**

*   Tests designed for successful LLM extraction should pass, with the backend logs and SSE events showing the expected content.
*   Tests designed to trigger LLM errors (e.g., using an invalid model alias, incorrect schema for JSON extraction) should result in the `/fetch-content` endpoint returning a structured "error" SSE event with `llm_error` details. The `fetch_history` record for such a URL should be marked as "failed" with the corresponding error message.
*   Review backend logs, LiteLLM proxy logs, and the `llm_call_logs` database table (if applicable) to trace the LLM calls and diagnose any issues.

## Live MCP Integration Tests

These tests verify that the LiteLLM proxy correctly exposes configured MCP tools and that a client can list and call these tools via the proxy's MCP endpoint.

**Prerequisites:**

*   Ensure your LiteLLM proxy is running and accessible at the URL specified by the `LITELLM_PROXY_URL` environment variable in your `backend/app/.env` file (defaults to `http://localhost:4000`).
*   Ensure your `litellm_proxy_config/config.yaml` file is correctly configured with the `mcp_servers` section, defining the MCP servers you want to expose.
*   Ensure the configured MCP servers are running and accessible to the LiteLLM proxy.
*   Ensure your Python virtual environment is activated and that the `mcp` library is installed (`pip install mcp`).

**How to Run:**

Navigate to the project root directory in your terminal and run the following command:

```bash
pytest backend/app/tests/live_mcp_integration_tester.py
```

This will execute the test cases defined in the `live_mcp_integration_tester.py` script. Review the output to ensure the tests pass, indicating that the MCP integration via the LiteLLM proxy is functioning as expected.
