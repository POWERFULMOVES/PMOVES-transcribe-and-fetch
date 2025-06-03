# Fetch Component Updates & Roadmap

This document outlines recent changes to the content fetching UI (`src/app/fetch/page.js` and `src/components/fetch/AdvancedFetchOptions.js`), their alignment with overall project goals, and pending work.

## Recent Work Done (October 2024)

### 1. Dynamic Model Loading & Selection (`page.js`, `AdvancedFetchOptions.js`)
- **Backend Integration:**
    - The `FetchContentPage` (`page.js`) now dynamically fetches a list of available LLM models from the backend API endpoint (`/api/v1/models`) on component mount.
    - This list is used to populate a `<Select>` dropdown in `AdvancedFetchOptions.js`.
- **State Management:**
    - `page.js` manages an `availableModels` state.
    - The selected model (its `model_alias` or `id`) is stored in the `llmProvider` field of the `formState`.
- **UI Update:**
    - `AdvancedFetchOptions.js` now renders a dynamic dropdown for LLM selection instead of a static input field.
    - Props `llmProvider`, `setLlmProvider`, and `availableModels` are passed from `page.js` to `AdvancedFetchOptions.js`.
- **CORS & Backend Endpoint:**
    - Reviewed backend CORS configuration in `main.py` to ensure it allows requests from the frontend (typically `http://localhost:3000`).
    - Identified and utilized the `/api/v1/models` (from `llm_routes.py`) endpoint in the backend to serve the list of models. This endpoint leverages the `LLMRegistryService` which caches model details.

### 2. SSE (Server-Sent Events) Handling Consolidation (`page.js`)
- **Issue Identified:** A build error (`cannot reassign to a variable declared with const`) was occurring due to a redundant `useEffect` hook in `page.js` that was incorrectly attempting to manage an SSE connection using `useState` for the `EventSource` object. This conflicted with the primary SSE handling logic within the `handleFetchContent` function.
- **Resolution:** The problematic `useEffect` hook (responsible for the `sseClient` state) was identified and recommended for removal/commenting out.
- **Correct Implementation:** The `handleFetchContent` function correctly manages the SSE connection lifecycle using an `eventSourceRef.current` to store the `EventSource` instance. This ensures a single, robust mechanism for handling real-time progress updates from the `/fetch-content` backend endpoint.

### 3. Crawl4AI Strategy Configurators (`AdvancedFetchOptions.js`)
- **Missing Components:** The `ExtractionStrategyConfigurator.jsx` and `DeepCrawlStrategyConfigurator.jsx` components were previously causing "Module not found" or "ReferenceError" issues due to incorrect import paths or them not being properly rendered.
- **Restoration & UI Integration:**
    - Verified the correct import paths for these configurator components within `AdvancedFetchOptions.js`.
    - Wrapped each configurator (`ExtractionStrategyConfigurator` and `DeepCrawlStrategyConfigurator`) within its own `AccordionItem` in the JSX. This ensures they are displayed consistently with other advanced options when `fetchingEngine` is set to `'crawl4ai'`.
    - Ensured necessary props (`crawl4aiExtractionConfig`, `onCrawl4aiExtractionConfigChange`, `crawl4aiDeepCrawlConfig`, `onCrawl4aiDeepCrawlConfigChange`) are passed from `page.js` to `AdvancedFetchOptions.js` and then to these configurators.

## Alignment with Project Goals

These changes directly support several key project objectives:

- **Hybrid Local/Cloud App:** Dynamic model loading allows the frontend to adapt to various backend configurations, including locally served models (e.g., via Ollama managed by LiteLLM) and different cloud providers. The `llmBaseUrl` and `llmApiToken` fields further support this by allowing users to specify custom endpoints and credentials.
- **Enhanced User Experience:**
    - Providing a dropdown for model selection is more user-friendly than requiring manual input of model names.
    - Centralized and corrected SSE handling provides reliable real-time feedback during fetch operations.
    - Properly integrated strategy configurators allow users to fine-tune Crawl4AI behavior directly from the UI.
- **Modular Frontend Components:** Refinements to `AdvancedFetchOptions.js` and `page.js` maintain a separation of concerns, where `page.js` handles data fetching and state management, and `AdvancedFetchOptions.js` focuses on presenting configuration options.
- **Pipecat Communication Layer (Future):** While these changes primarily affect direct backend-frontend communication for the fetch page, the standardized model information and a robust fetching UI lay groundwork for future integration with Pipecat agents that might orchestrate or utilize these fetching capabilities. The dynamic model list could eventually be sourced via a Pipecat agent/service that interacts with the LiteLLM registry.

## Outstanding Work & Next Steps

- **Manual SSE Fix Verification:** confirm that the redundant `useEffect` hook in `src/app/fetch/page.js` has been manually commented out or removed to fully resolve the SSE-related build error.
- **Comprehensive Testing of Model Selection:**
    - Test with various backend model configurations (OpenAI, Groq, Ollama via LiteLLM).
    - Ensure the selected `llmProvider`, `llmApiToken`, and `llmBaseUrl` are correctly passed to the backend when `fetchingEngine` is `crawl4ai` (and potentially for other engines if LLM features are used).
- **Strategy Configurator State Management:**
    - Verify that changes made within `ExtractionStrategyConfigurator` and `DeepCrawlStrategyConfigurator` are correctly updating the `formState` in `page.js` via the `onCrawl4aiExtractionConfigChange` and `onCrawl4aiDeepCrawlConfigChange` handlers.
    - Ensure these configurations are correctly stringified and passed as URL parameters to the `/fetch-content` backend endpoint.
- **Error Handling for Model Loading:**
    - Enhance error display if the `/api/v1/models` endpoint fails or returns an unexpected format.
- **Default Model Selection (Optional):** Consider automatically selecting the first model in the list as the default if `llmProvider` is initially empty, or provide a "None" option. (Currently, it defaults to an empty selection).
- **UI Polish for Strategy Configurators:** Review the layout and usability of the strategy configurators now that they are correctly rendered.
- **Backend Parameter Alignment:**
    - Double-check that all frontend parameters for `crawl4ai` in `page.js` (`handleFetchContent` function) correctly map to the backend API parameters in `main.py` for the `/fetch-content` endpoint, especially for boolean values and JSON stringified objects.
- **State Synchronization for `useAdvancedSettings`:** The `useAdvancedSettings` hook in `page.js` initializes many Crawl4AI-specific parts of `formState`. Ensure that when `AdvancedFetchOptions` updates these (e.g., `crawl4aiUserAgent`), the main `formState` in `page.js` is the single source of truth and is updated correctly. (This seems to be handled by passing individual setters like `setCrawl4aiUserAgentHandler`).

This document should be updated as further enhancements are made to the fetch functionality. 