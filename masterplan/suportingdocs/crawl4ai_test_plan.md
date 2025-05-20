# Test Plan: Fetch Page - Advanced crawl4ai Integration

## 1. Introduction

This test plan outlines the testing strategy for the advanced `crawl4ai` integration on the Fetch page. It is based on the recommendations in [`docs/fetch_page_testing_recommendations.md`](docs/fetch_page_testing_recommendations.md:1) and aims to ensure robust functionality, particularly after resolving the `NotImplementedError` on Windows systems. The plan identifies key test areas, components involved, and dependencies to guide the testing process and facilitate delegation of specific testing subtasks.

## 2. General Prerequisites & Assumptions

*   **Windows Environment:** All tests, especially those involving `crawl4ai`, must be conducted with the backend development server (e.g., Uvicorn) running *without* the `--reload` flag. This is crucial to avoid `asyncio` subprocess management issues with `playwright` (a `crawl4ai` dependency).
*   **Backend Fixes:**
    *   **Item 4 (Backend - Advanced Deep Crawling Strategies):** Tests for `FilterChain` (Test 4.2) and `KeywordRelevanceScorer` (Test 4.3) assume that the parameter key mismatch identified during the May 8, 2025 verification (mentioned in the source document) has been resolved in [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1).
*   **Feature Implementation:**
    *   **Item 8 (Fetch History Refinement):** Backend tests (Test 8.1) related to saving `engine_specific_parameters` to `fetch_history` can only be performed once the saving mechanism is fully implemented.

## 3. Pre-existing Tests Assessment

*   The document [`docs/fetch_page_testing_recommendations.md`](docs/fetch_page_testing_recommendations.md:1) mentions: "A relevant tests folder might exist at `docs/crawl4ai/tests`."
*   It has been confirmed that the directory `docs/crawl4ai/tests` **does exist** and contains a comprehensive suite of Python-based tests. These tests are designed to validate the functionality, robustness, and various operational aspects of the `crawl4ai` library itself (e.g., its core crawling strategies, CLI, Docker integration, browser automation, content processing, performance, and error handling).
*   While these existing `crawl4ai` library tests are crucial for ensuring the reliability of the `crawl4ai` dependency, they **do not cover the PMOVES application-specific integration logic**. This includes:
    *   The PMOVES React UI components and their behavior related to `crawl4ai` configuration.
    *   The PMOVES backend API logic in [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1) responsible for mapping frontend requests to `crawl4ai` configurations and handling responses.
    *   End-to-end workflows within the PMOVES application that utilize `crawl4ai`.
*   Therefore, new tests specifically designed for the PMOVES application, as detailed in subsequent sections of this plan, are essential to ensure the `crawl4ai` integration is functioning correctly within the PMOVES context. The `crawl4ai` library's tests can, however, serve as valuable references for understanding expected library behavior and for inspiring additional integration test scenarios (see Section 5).

## 4. Test Areas and Specific Items

As established in Section 3, the tests in this area are specific to the PMOVES application and require new test development, as the `crawl4ai` library's own tests do not cover this integration layer.

### Area A: UI Component Tests (Client-Side)

This area focuses on testing the user interface components related to `crawl4ai` configuration on the Fetch page.
*   **Type:** Component-level UI testing (React components). Involves checking conditional rendering, default states, user interactions (selections, input), prop handling, callback invocations, and tooltip accessibility.

**Item 1: UI - Extraction Strategies**
*   **Component:** [`src/components/fetch/ExtractionStrategyConfigurator.jsx`](src/components/fetch/ExtractionStrategyConfigurator.jsx)
*   **Context Component:** [`src/components/fetch/AdvancedFetchOptions.jsx`](src/components/fetch/AdvancedFetchOptions.jsx)
*   **Key Tests:**
    1.  `[COMPLETED]` Conditional rendering based on `fetchingEngine` prop.
    2.  `[COMPLETED]` Default state ("None / Default").
    3.  `[COMPLETED]` Strategy selection (None, LLM, JsonCss, Cosine) and correct parameter field display.
    4.  `[COMPLETED]` `onCrawl4aiExtractionConfigChange` callback triggered with correct data.
    5.  `[COMPLETED]` Parameter input for `JsonCssExtractionStrategy` (schema) and `LLMExtractionStrategy` (instructions, provider, token, URL) updates state.
    6.  `[COMPLETED]` Initial configuration loading via `crawl4aiExtractionConfig` prop.
    7.  `[COMPLETED]` Dynamic updates when `initialConfig` prop changes.
    8.  `[COMPLETED]` Tooltip presence and content.

**Item 3: UI - Advanced Deep Crawling Strategies**
*   **Component:** [`src/components/fetch/DeepCrawlStrategyConfigurator.jsx`](src/components/fetch/DeepCrawlStrategyConfigurator.jsx)
*   **Context Component:** [`src/components/fetch/AdvancedFetchOptions.jsx`](src/components/fetch/AdvancedFetchOptions.jsx)
*   **Key Tests:**
    1.  `[COMPLETED]` Conditional rendering based on `fetchingEngine` prop.
    2.  `[COMPLETED]` Default state ("None / Default").
    3.  `[COMPLETED]` Strategy selection (None, BFS, DFS, BestFirst) and correct parameter field display (including conditional display for `scorer_keywords`).
    4.  `[COMPLETED]` `onCrawl4aiDeepCrawlConfigChange` callback triggered with correct data (types, structure).
    5.  `[COMPLETED]` Initial configuration loading via `crawl4aiDeepCrawlConfig` prop.
    6.  [COMPLETED] Dynamic updates when `initialConfig` prop changes.
    7.  [COMPLETED] Parameter reset when switching strategies.
    8.  [COMPLETED] Tooltip presence and content.

**Item 5 (UI Part): UI - Configurable Markdown Generation**
*   **Component:** Controls within [`src/components/fetch/AdvancedFetchOptions.jsx`](src/components/fetch/AdvancedFetchOptions.jsx)
*   **Key Tests:**
    1.  [COMPLETED] "Markdown Generator" dropdown existence for `crawl4ai`.
    2.  [COMPLETED] "Default" option presence.
    3.  [COMPLETED] Selection updates state via prop.

**Item 6 (UI Part): UI - General and Expert `crawl4ai` Options**
*   **Components:** Accordion sections and controls within [`src/components/fetch/AdvancedFetchOptions.jsx`](src/components/fetch/AdvancedFetchOptions.jsx) (e.g., `crawl4ai-browser-nav`).
*   **Key Tests:**
    1.  [COMPLETED] Existence of accordion sections and expected controls (User Agent, Enable JS, Target Elements, etc.).
    2.  [COMPLETED] Controls linked to state props and trigger update functions correctly.

**Item 9: `FetchedContentViewer.jsx` Enhancement for Structured Data**
*   **Component:** [`src/components/fetch/FetchedContentViewer.jsx`](src/components/fetch/FetchedContentViewer.jsx)
*   **Key Tests:**
    1.  [COMPLETED] Render `JsonView` with `output_type: 'structured_json'` and valid JSON.
    2.  [COMPLETED] Render `JsonView` with valid JSON and no `output_type` hint.
    3.  [COMPLETED] Render `ReactMarkdown` with `output_type: 'structured_json'` and invalid JSON.
    4.  [COMPLETED] Render `ReactMarkdown` with plain string/Markdown.
    5.  [COMPLETED] Render `ReactMarkdown` with non-string, non-JSON input (e.g., number).
    6.  [COMPLETED] Render PDF link correctly when `pdf_file_path` is provided.

### Area B: Backend API & Integration Tests (Server-Side)

This area focuses on testing the backend API endpoints and logic in [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1) that handle `crawl4ai` requests. As established in Section 3, these tests are specific to the PMOVES application and require new test development.
*   **Type:** API integration testing. Involves sending HTTP requests to the backend, mocking external dependencies (like `AsyncWebCrawler.arun`, `LLMConfig`), and verifying the internal `config` objects passed to `crawl4ai` and error/warning logging.

**Item 2: Backend - Extraction Strategies**
*   **File:** [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1) (function: `fetch_with_crawl4ai`)
*   **Key Tests:**
    1.  [COMPLETED] `LLMExtractionStrategy`: Valid params, mock `arun`, inspect `config.extraction_strategy`. Test with/without optional LLM params and API token precedence.
    2.  [COMPLETED] `JsonCssExtractionStrategy`: Valid JSON schema, mock `arun`, inspect `config.extraction_strategy`. Test invalid JSON schema for error handling.
    3.  [COMPLETED] `CosineStrategy`: Mock `arun`, inspect `config.extraction_strategy`.
    4.  [COMPLETED] No Strategy / Default: `strategy: "none"` or missing config, mock `arun`, verify `config.extraction_strategy` is `None`.
    5.  [COMPLETED] Invalid Strategy Name: Verify warning logged and `config.extraction_strategy` is `None`.

**Item 4: Backend - Advanced Deep Crawling Strategies**
*   **File:** [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1)
*   **Prerequisite:** Assumes backend fix for parameter key mismatch is in place.
*   **Key Tests:**
    1.  [COMPLETED] Strategy Instantiation (BFS/DFS/BestFirst): Send requests, mock `arun`, verify `config.deep_crawl_strategy` instance and params.
    2.  [COMPLETED] `FilterChain` Integration (After Backend Fix): Send request with `filter_chain` params, verify `config.deep_crawl_strategy.filter_chain` instance.
    3.  [COMPLETED] `KeywordRelevanceScorer` Integration (After Backend Fix): Send request with `url_scorer` params, verify `config.deep_crawl_strategy.url_scorer` instance.
    4.  [COMPLETED] `BestFirstCrawlingStrategy` without Scorer: Verify warning logged and strategy instantiated.
    5.  [COMPLETED] "None" Strategy: Verify `config.deep_crawl_strategy` is `None`.

**Item 5 (Backend Part): Backend - Configurable Markdown Generation**
*   **File:** [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1)
*   **Key Tests:**
    1.  [COMPLETED] `markdown_generator: "Default"`: Mock `arun`, verify `config.markdown_generator` is `DefaultMarkdownGenerator`.
    2.  [COMPLETED] Empty/no `markdown_generator`: Verify `config.markdown_generator` is `None`.
    3.  [COMPLETED] `markdown_generator: "UnknownGenerator"`: Verify warning logged and `config.markdown_generator` is `None`.

**Item 6 (Backend Part): Backend - General and Expert `crawl4ai` Options**
*   **File:** [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1)
*   **Key Tests:**
    1.  [COMPLETED] Send requests with various parameter combinations. Mock `arun`, inspect `config` (`CrawlerRunConfig`) and `browser_config`.
    2.  [COMPLETED] `BrowserConfig` Tests: Boolean flags, string/numeric values, JSON parsing (`cookies`, `headers`).
    3.  [COMPLETED] `CrawlerRunConfig` Tests: Boolean flags, string/numeric/float values, list parsing.
    4.  [COMPLETED] Type Conversion Tests: Invalid input types; verify graceful handling (logging, defaults).

**Item 7: `LLMConfig` End-to-End Robustness**
*   **File:** [`backend/app/crawl4ai_fetcher.py`](backend/app/crawl4ai_fetcher.py:1) (logic related to `LLMConfig` within `LLMExtractionStrategy`)
*   **Key Tests:**
    1.  [COMPLETED] Provider Parsing: Various `llm_provider_model` strings, mock `LLMConfig`, verify `provider`.
    2.  [COMPLETED] API Token Precedence: ENV var vs. request param token, verify correct token used and warnings.
    3.  [COMPLETED] Base URL Handling: With/without `llm_base_url`, verify `LLMConfig`.
    4.  [COMPLETED] Missing Provider/Instructions: Verify warning logged and strategy not instantiated.
    5.  [COMPLETED] Instantiation Errors: Mock `LLMConfig`/`LLMExtractionStrategy` `__init__` to raise exception, verify error caught/logged.

### Area C: End-to-End Feature Tests (UI & Backend Interaction)

This area focuses on testing the complete workflow from UI interaction through backend processing and back to the UI, particularly for features involving state persistence or complex data flow. As established in Section 3, these tests are specific to the PMOVES application and require new test development.
*   **Type:** End-to-end integration testing.

**Item 8: Fetch History Refinement for Advanced Strategies**
*   **Backend Component:** Fetch history saving mechanism (database interaction).
*   **Frontend Components:** [`src/app/fetch/page.js`](src/app/fetch/page.js) (`formState`), [`src/components/fetch/ExtractionStrategyConfigurator.jsx`](src/components/fetch/ExtractionStrategyConfigurator.jsx), [`src/components/fetch/DeepCrawlStrategyConfigurator.jsx`](src/components/fetch/DeepCrawlStrategyConfigurator.jsx).
*   **Prerequisite:** Fetch history saving mechanism must be implemented.
*   **Key Tests:**
    1.  [COMPLETED] **Backend:** Perform fetch with `crawl4ai` and configured strategies. Verify `fetch_history` record has `engine_specific_parameters` populated correctly.
    2.  [COMPLETED] **Frontend/Integration:** Mock history item with valid `engine_specific_parameters`. Click "Re-fetch". Verify `formState` in [`src/app/fetch/page.js`](src/app/fetch/page.js:1) updated. Verify UI configurators (`ExtractionStrategyConfigurator`, `DeepCrawlStrategyConfigurator`) display pre-filled settings.

## 5. Additional Testing Considerations (Inspired by `crawl4ai` Library Tests)

The comprehensive test suite found in `docs/crawl4ai/tests` for the `crawl4ai` library itself highlights several areas of testing that would be beneficial to incorporate into this plan to ensure a more robust and reliable integration of `crawl4ai` within the PMOVES application. These include:

*   **5.1. Performance & Benchmarking:**
    *   **Objective:** To measure the performance characteristics of `crawl4ai` operations when invoked via the PMOVES backend API.
    *   **Considerations:** Test response times for typical fetch scenarios (simple URL, small deep crawl), identify potential overhead from the PMOVES integration layer, and establish performance baselines.
    *   **Inspired by:** `crawl4ai/tests/async/test_performance.py`, `crawl4ai/tests/memory/run_benchmark.py`.

*   **5.2. Stress & Load Testing:**
    *   **Objective:** To assess the stability and resource utilization of the PMOVES backend when handling multiple concurrent `crawl4ai` requests.
    *   **Considerations:** Simulate concurrent user requests for `crawl4ai` fetches, monitor server resource usage (CPU, memory), and identify breaking points or degradation in performance under load.
    *   **Inspired by:** `crawl4ai/tests/memory/test_stress_api.py`, `crawl4ai/tests/memory/test_dispatcher_stress.py`.

*   **5.3. Enhanced Error Handling Scenarios:**
    *   **Objective:** To ensure the PMOVES integration gracefully handles a wider range of error conditions that may arise from `crawl4ai` operations or network issues.
    *   **Considerations:** Test PMOVES's behavior with network failures during crawls, unexpected exceptions from the `crawl4ai` library, operation timeouts, and ensure errors are appropriately logged and communicated to the UI.
    *   **Inspired by:** `crawl4ai/tests/async/test_error_handling.py`.

*   **5.4. Caching Implications (If Applicable):**
    *   **Objective:** To verify the correct behavior of any caching mechanisms implemented within PMOVES related to `crawl4ai` calls, or to understand the impact of `crawl4ai`'s internal caching on PMOVES.
    *   **Considerations:** If PMOVES caches `crawl4ai` results, test cache hits, misses, and invalidation. If relying on `crawl4ai`'s cache, test how re-fetch scenarios behave.
    *   **Inspired by:** `crawl4ai/tests/async/test_caching.py`, `crawl4ai/tests/general/test_cache_context.py`.

*   **5.5. Memory Usage Monitoring:**
    *   **Objective:** To monitor and manage the memory footprint of the PMOVES backend process during potentially resource-intensive `crawl4ai` operations.
    *   **Considerations:** Track memory usage during deep crawls or fetches of large sites to identify potential memory leaks or excessive consumption attributable to the integration.
    *   **Inspired by:** `crawl4ai/tests/memory/test_crawler_monitor.py`.

*   **5.6. Dockerized `crawl4ai` Interaction (Conditional):**
    *   **Objective:** If PMOVES intends to interact with `crawl4ai` running as a separate Dockerized service, test this specific deployment and communication model.
    *   **Considerations:** This would only be relevant if the integration architecture changes from using `crawl4ai` as a direct Python library. Tests would cover API communication with the `crawl4ai` Docker service, deployment, and configuration.
    *   **Inspired by:** `crawl4ai/tests/docker/test_server.py`, `crawl4ai/tests/docker/test_rest_api_deep_crawl.py`.

Incorporating these additional testing areas will contribute to a more resilient and well-understood `crawl4ai` integration.

## 6. Test Execution Notes

*   **Environment:** As stated in prerequisites, ensure the backend server is run without the `--reload` flag on Windows for all `crawl4ai` related tests.
*   **Sequence:**
    1.  It's recommended to start with **Area A (UI Component Tests)** to ensure individual UI parts are functioning correctly.
    2.  Proceed to **Area B (Backend API & Integration Tests)**, ensuring prerequisites (backend fixes) are met.
    3.  Finally, conduct **Area C (End-to-End Feature Tests)** once dependent features like history saving are implemented.
*   **Delegation:** Each numbered sub-test within Items 1-9 (and considerations in Section 5) can be considered a distinct subtask for delegation.

This plan provides a structured approach to testing the `crawl4ai` integration.
## 7. Running the Tests

### Prerequisites

*   **Frontend (Jest):** Ensure Node.js and npm are installed. Navigate to the project root directory (`c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch`) in your terminal and run `npm install` to install necessary dependencies defined in [`package.json`](package.json).
*   **Backend (Pytest):** Ensure Python and pip are installed. It's recommended to use a virtual environment. Navigate to the `backend` directory (`c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch/backend`) and install dependencies using `pip install -r requirements.txt`. This should include `pytest`. If `pytest` is not included, install it separately (`pip install pytest`).
*   **Backend Server (for some tests):** As noted in Section 2, for tests involving actual `crawl4ai` execution (though many backend tests mock this), the backend server must be running *without* the `--reload` flag on Windows.

### Frontend Tests (Jest)

*   **Location:** Frontend tests (React components and integration) are located primarily within `__tests__` subdirectories under [`src/components/fetch/`](src/components/fetch/) and [`src/app/fetch/`](src/app/fetch/).
*   **Command:** Navigate to the project root directory (`c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch`) in your terminal.
    *   To run all frontend tests:
        ```bash
        npm test
        ```
    *   To run tests within a specific directory (e.g., all tests in `src/app/fetch/`):
        ```bash
        npm test src/app/fetch/
        ```
    *   To run a specific test file (e.g., `page.test.js` within `src/app/fetch/__tests__/`):
        ```bash
        npm test src/app/fetch/__tests__/page.test.js
        ```

### Backend Tests (Pytest)

*   **Location:** Backend tests (API and integration) are located in [`backend/app/tests/`](backend/app/tests/).
*   **Command:** Navigate to the project root directory (`c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch`) in your terminal and run:
    ```bash
    pytest backend/app/tests/
    ```
    Alternatively, navigate to the `backend` directory and run `pytest app/tests/`. Pytest will discover and run all tests within the specified directory.