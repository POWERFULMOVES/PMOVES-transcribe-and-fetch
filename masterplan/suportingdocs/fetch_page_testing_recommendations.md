# Fetch Page - Advanced crawl4ai Integration Testing Recommendations

This document outlines recommended testing procedures for the Fetch page's advanced `crawl4ai` integration, particularly focusing on ensuring robust functionality following the resolution of a significant `NotImplementedError` previously encountered on Windows systems.

**Key Update:** The `NotImplementedError` that was blocking `crawl4ai` usage on Windows has been identified as an issue with Uvicorn's `--reload` flag interfering with `asyncio` subprocess management used by `playwright` (a dependency of `crawl4ai`). Running the backend server *without* the `--reload` flag resolves this primary blocker.

The testing recommendations have been updated to reflect this resolution. The focus is now on:
*   Verifying `crawl4ai` functionality on Windows when the development server (e.g., Uvicorn) is run *without* the `--reload` flag.
*   Comprehensive general functionality testing of all Fetch page features integrated with `crawl4ai`.
*   Awareness that if similar `asyncio` subprocess-related errors occur on Windows in the future, development server reload mechanisms (like Uvicorn's `--reload`) should be investigated early.

The following sections detail specific test areas for UI and backend components, originally based on the code verification of May 8, 2025, for features in Section 8.2 of [`docs/fetch_page_enhancement_plan.md`](docs/fetch_page_enhancement_plan.md:1). A relevant tests folder might exist at `docs/crawl4ai/tests`.

## Item 1: UI - Extraction Strategies (`ExtractionStrategyConfigurator.jsx`)

1.  **Conditional Rendering:**
    *   Test that the "crawl4ai - Extraction Strategy" accordion section and the `ExtractionStrategyConfigurator` within it are only visible in `AdvancedFetchOptions.jsx` when `fetchingEngine` prop is set to `'crawl4ai'`.
2.  **Default State:**
    *   Test that `ExtractionStrategyConfigurator` defaults to "None / Default" strategy if no `initialConfig` is provided or if `initialConfig.strategy` is undefined.
3.  **Strategy Selection & Parameter Display:**
    *   For each strategy (None, LLM, JsonCss, Cosine):
        *   Select the strategy.
        *   Verify that the correct set of parameter input fields (or "No specific parameters" message) is displayed.
        *   Verify that the `onCrawl4aiExtractionConfigChange` callback is triggered with the selected strategy and empty/default parameters.
4.  **Parameter Input & State Update:**
    *   For `JsonCssExtractionStrategy`: Enter text into the "Schema (JSON)" textarea. Verify `onCrawl4aiExtractionConfigChange` is called with the updated schema value in `params`.
    *   For `LLMExtractionStrategy`: Enter values into "LLM Instructions", "LLM Provider/Model", "LLM API Token", and "LLM Base URL". Verify `onCrawl4aiExtractionConfigChange` is called with these values correctly placed in `params`.
5.  **Initial Configuration Loading (Re-fetch Scenario):**
    *   Provide a specific `crawl4aiExtractionConfig` prop (e.g., `{ strategy: 'llm', params: { llm_instructions: 'Extract summary', llm_provider_model: 'openai/gpt-4o-mini' } }`).
    *   Verify `ExtractionStrategyConfigurator` initializes with the correct strategy selected and fields pre-filled.
6.  **Dynamic `initialConfig` Update:**
    *   Simulate a change to the `crawl4aiExtractionConfig` prop after initial render.
    *   Verify `ExtractionStrategyConfigurator` updates its UI.
7.  **Tooltip Accessibility:**
    *   Verify tooltips for strategy selection and parameter inputs are present and display help text.

## Item 2: Backend - Extraction Strategies (`crawl4ai_fetcher.py`)

(These are primarily integration tests targeting the API endpoint using `fetch_with_crawl4ai`)

1.  **`LLMExtractionStrategy` Test:**
    *   Send request with `strategy: "LLMExtractionStrategy"` and valid `params` (instructions, provider/model).
    *   Mock `AsyncWebCrawler.arun`, inspect `config` passed. Verify `config.extraction_strategy` is `LLMExtractionStrategy` instance with correct instructions and `llm_config`.
    *   Test with/without optional `llm_api_token`, `llm_base_url`. Test API token precedence (ENV vs. request).
2.  **`JsonCssExtractionStrategy` Test:**
    *   Send request with `strategy: "JsonCssExtractionStrategy"` and valid JSON `schema` string in `params`.
    *   Mock `AsyncWebCrawler.arun`, inspect `config`. Verify `config.extraction_strategy` is `JsonCssExtractionStrategy` instance with correctly parsed schema.
    *   Test with invalid JSON schema string; verify error handling/logging.
3.  **`CosineStrategy` Test:**
    *   Send request with `strategy: "CosineStrategy"`.
    *   Mock `AsyncWebCrawler.arun`, inspect `config`. Verify `config.extraction_strategy` is `CosineStrategy` instance.
4.  **No Strategy / Default Strategy Test:**
    *   Send request with `strategy: "none"` or missing `extraction_config`.
    *   Mock `AsyncWebCrawler.arun`, inspect `config`. Verify `config.extraction_strategy` is `None`.
5.  **Invalid Strategy Name Test:**
    *   Send request with an unknown `strategy` name.
    *   Verify warning logged and `config.extraction_strategy` is `None`.

## Item 3: UI - Advanced Deep Crawling Strategies (`DeepCrawlStrategyConfigurator.jsx`)

1.  **Conditional Rendering:**
    *   Test that the "crawl4ai - Deep Crawl Strategy" accordion section and `DeepCrawlStrategyConfigurator` are only visible when `fetchingEngine` is `'crawl4ai'`.
2.  **Default State:**
    *   Test default strategy is "None / Default".
3.  **Strategy Selection & Parameter Display:**
    *   Select "None": Verify no additional parameters shown.
    *   Select "BFSDeepCrawlStrategy"/"DFSDeepCrawlStrategy": Verify inputs for `max_depth`, `max_pages`, `include_external`, `url_filter_patterns`, `score_threshold` are visible.
    *   Select "BestFirstCrawlingStrategy": Verify inputs for `max_depth`, `max_pages`, `include_external`, `url_filter_patterns`, `url_scorer` are visible. Test conditional display of `scorer_keywords` when `KeywordRelevanceScorer` is selected.
4.  **Parameter Input & `onConfigChange` Callback:**
    *   For each strategy, input valid values. Verify `onCrawl4aiDeepCrawlConfigChange` called with correct `strategy` and `params` object (correct types, nested structure for filters/scorers).
5.  **Initial Configuration Loading (Re-fetch Scenario):**
    *   Provide specific `crawl4aiDeepCrawlConfig` prop. Verify `DeepCrawlStrategyConfigurator` initializes correctly.
6.  **Dynamic `initialConfig` Update:**
    *   Simulate change to `crawl4aiDeepCrawlConfig` prop. Verify UI updates.
7.  **Parameter Reset on Strategy Change:**
    *   Test that strategy-specific parameters (`score_threshold`, `url_scorer`, `scorer_keywords`) are reset in state and `onConfigChange` output when switching strategies.
8.  **Tooltip Accessibility:**
    *   Verify tooltips are present and display help text.

## Item 4: Backend - Advanced Deep Crawling Strategies (`crawl4ai_fetcher.py`)

**(Note: These tests assume the parameter key mismatch identified during verification is fixed)**

1.  **Strategy Instantiation (BFS/DFS/BestFirst):**
    *   Send requests specifying each `strategy_type`. Provide valid direct params (`max_depth`, `max_pages`, `include_external`, `score_threshold` for BFS/DFS).
    *   Mock `AsyncWebCrawler.arun`, verify `config.deep_crawl_strategy` is correct instance with direct params set.
2.  **`FilterChain` Integration Test (After Backend Fix):**
    *   Send request with `deep_crawl_config` including `params: { filter_chain: { URLPatternFilter: ["^https://example.com/blog/.*"] } }`.
    *   Verify `config.deep_crawl_strategy.filter_chain` is `FilterChain` instance with correct `URLPatternFilter`.
3.  **`KeywordRelevanceScorer` Integration Test (After Backend Fix):**
    *   Send request with `strategy: "BestFirstCrawlingStrategy"` and `params: { url_scorer: { KeywordRelevanceScorer: { keywords: ["ai", "test"] } } }`.
    *   Verify `config.deep_crawl_strategy.url_scorer` is `KeywordRelevanceScorer` instance with correct keywords.
4.  **`BestFirstCrawlingStrategy` without Scorer:**
    *   Send request with `strategy: "BestFirstCrawlingStrategy"` but no/invalid `url_scorer`.
    *   Verify warning logged and strategy is instantiated (without scorer).
5.  **"None" Strategy:**
    *   Send request with `strategy: "None"`. Verify `config.deep_crawl_strategy` is `None`.

## Item 5: UI & Backend - Configurable Markdown Generation

1.  **UI Test:**
    *   Verify "Markdown Generator" dropdown exists in `AdvancedFetchOptions.jsx` for `crawl4ai`. Verify "Default" option present. Verify selection updates state via prop.
2.  **Backend/Integration Test:**
    *   Send request with `markdown_generator: "Default"`. Mock `AsyncWebCrawler.arun`, verify `config.markdown_generator` is `DefaultMarkdownGenerator` instance.
    *   Send request with empty/no `markdown_generator`. Verify `config.markdown_generator` is `None`.
    *   Send request with `markdown_generator: "UnknownGenerator"`. Verify warning logged and `config.markdown_generator` is `None`.

## Item 6: UI & Backend - General and Expert `crawl4ai` Options

1.  **UI Tests:**
    *   Verify accordion sections (`crawl4ai-browser-nav`, etc.) exist and contain expected controls.
    *   For sample controls (e.g., User Agent, Enable JS, Target Elements, Scan Full Page, Cache Mode, Capture Screenshot, Respect robots.txt, Verbose Logging, Browser Cookies, Session ID): Verify control exists, linked to state prop, triggers update function.
2.  **Backend/Integration Tests:**
    *   Send requests with various parameter combinations. Mock `AsyncWebCrawler.arun`, inspect `config` (`CrawlerRunConfig`) and `browser_config`.
    *   **BrowserConfig Tests:** Verify boolean flags, string/numeric values, JSON parsing (`cookies`, `headers`).
    *   **CrawlerRunConfig Tests:** Verify boolean flags, string/numeric/float values, list parsing (comma-separated strings).
    *   **Type Conversion Tests:** Test invalid input types; verify graceful handling by helper functions (logging, defaults).

## Item 7: `LLMConfig` End-to-End Robustness

(Backend/Integration Tests)

1.  **Provider Parsing:** Send requests with various `llm_provider_model` strings. Mock `LLMConfig` instantiation, verify `provider` argument matches.
2.  **API Token Precedence:** Test scenarios with/without ENV var and request param token; verify correct token used in `LLMConfig` and warning logged if request token used without ENV var.
3.  **Base URL Handling:** Test with/without `llm_base_url`; verify `LLMConfig` instantiated correctly.
4.  **Missing Provider/Instructions:** Send requests missing `llm_provider_model` or `llm_instructions`. Verify warning logged and `LLMExtractionStrategy` not instantiated.
5.  **Instantiation Errors:** Mock `LLMConfig`/`LLMExtractionStrategy` `__init__` to raise exception. Verify error caught and logged.

## Item 8: Fetch History Refinement for Advanced Strategies

1.  **Backend Test (Once Saving Implemented):**
    *   Perform fetch with `crawl4ai` and configured strategies. Verify `fetch_history` record has `engine_specific_parameters` populated with correct JSON for `crawl4aiExtractionConfig` and `crawl4aiDeepCrawlConfig`.
2.  **Frontend/Integration Test:**
    *   Mock history item with valid `engine_specific_parameters` including strategy configs.
    *   Click "Re-fetch". Verify `formState` in `page.js` updated correctly. Verify `ExtractionStrategyConfigurator` and `DeepCrawlStrategyConfigurator` display pre-filled settings.

## Item 9: `FetchedContentViewer.jsx` Enhancement for Structured Data

1.  **Structured JSON Input (`output_type` hint):** Provide `output_type: 'structured_json'` and valid JSON string/object in `markdownContent`. Verify `JsonView` rendered.
2.  **Structured JSON Input (no `output_type` hint):** Provide valid JSON string/object in `markdownContent`. Verify `JsonView` rendered.
3.  **Invalid JSON Input (`output_type` hint):** Provide `output_type: 'structured_json'` and invalid JSON string. Verify `ReactMarkdown` rendered, displaying the invalid string.
4.  **Plain String/Markdown Input:** Provide `markdownContent: '# Hello'`. Verify `ReactMarkdown` rendered.
5.  **Non-String, Non-JSON Input:** Provide `markdownContent: 123`. Verify `ReactMarkdown` rendered, displaying "123".
6.  **PDF Content:** Provide `pdf_file_path`, `markdownContent: null`. Verify PDF link rendered, no main content viewer.