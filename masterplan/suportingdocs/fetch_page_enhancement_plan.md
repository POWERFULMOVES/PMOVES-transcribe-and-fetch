# Fetch Page UI/UX Enhancement Plan

**Version:** 1.3
**Date:** May 8, 2025
**Author:** Roo, Architect Mode

## 1. Introduction & Goals

This document outlines the plan for enhancing the User Interface (UI) and User Experience (UX) of the "Fetch" page ([`src/app/fetch/page.js`](../../src/app/fetch/page.js)) within the PMOVES platform. The primary goal is to modernize the interface, simplify the content fetching workflow, provide better feedback to the user, and introduce capabilities for managing fetched content, aligning with the overall strategic UI enhancement goals ([`docs/ui_enhancement_plan.md`](../../docs/ui_enhancement_plan.md)).

This revision (v1.3) significantly expands upon previous versions by incorporating the comprehensive findings and recommendations from a detailed Researcher's report. The focus shifts from basic parameter mapping for `crawl4ai` to a strategic and deep integration of its advanced features. This plan now details the ambition to fully leverage `crawl4ai`'s sophisticated extraction strategies, deep crawling capabilities, and other advanced functionalities to provide users with a powerful and flexible content fetching tool. It outlines the necessary UI enhancements, backend modifications, and a revised roadmap to achieve this advanced integration.

**Key Objectives:**
*   Simplify the form for initiating fetch requests.
*   Enhance fetching engine selection with advanced `crawl4ai` strategy configuration.
*   Implement advanced `crawl4ai` capabilities, including selectable extraction and deep crawling strategies with granular configuration.
*   Improve visualization of fetching progress and logs, considering features from `crawl4ai`.
*   Introduce an interface for managing previously fetched content.
*   Strategically leverage existing UI components and Supabase UI where beneficial.
*   Ensure the design adheres to the guiding principles: User-Centricity, Consistency, Modularity, Performance, and Accessibility.

### 1.1. Implementation Review Summary (as of May 7, 2025 - Maintained for Context)

A review by Roo Sr. (Senior Mode) indicated significant progress on foundational features. Core aspects like dual fetch engine support (Jina and `crawl4ai`) at a basic level, real-time progress updates via SSE, and UI for basic/advanced options and history management were substantially built.

However, key areas requiring attention (many of which are now being addressed by this expanded plan) included:
*   **`crawl4ai` Backend Integration:** Many advanced `crawl4ai` options configured in the UI were not mapped to the `crawl4ai` library in the backend ([`backend/app/crawl4ai_fetcher.py`](../../backend/app/crawl4ai_fetcher.py:1)), rendering them ineffective. This plan now details a much deeper integration requiring more sophisticated backend mapping.
*   **Fetch History Actions:** "View Content" and "Delete" were not fully functional. "Copy URL/Markdown" was not implemented.
*   **Fetch History Table:** Lacked filtering, searching, and sorting capabilities. The data fetching mechanism was due for an update.
*   **Structured Data Display:** No explicit capability in [`FetchedContentViewer.jsx`](../../src/components/fetch/FetchedContentViewer.jsx:1) for structured data (e.g., JSON from `crawl4ai`).

This updated plan (v1.3) details these points and incorporates recommendations for completion, including the integration of the `use-infinite-query` hook for fetch history, and now focuses on the comprehensive integration of advanced `crawl4ai` features.

## 2. Current State Analysis

The current "Fetch" page ([`src/app/fetch/page.js`](../../src/app/fetch/page.js)) provides functionality to fetch web content with numerous advanced options, primarily leveraging a Jina AI-based backend.
The introduction of `crawl4ai` presents an opportunity to offer more advanced and potentially higher-fidelity content extraction.

**Key Characteristics (Current Jina AI based):**
*   **Form Inputs:** A primary URL input field. An extensive set of advanced options are grouped within an accordion.
*   **Fetching Mechanism:** Submits a GET request to the `/fetch-content` backend API.
*   **Feedback:** Displays a "Fetching..." loading state and error messages.
*   **Results Display:** Uses tabs for Markdown and PDF; displays metadata and links.
*   **Component Usage:** Leverages existing Shadcn/ui components.

**Areas for Improvement (and `crawl4ai` consideration):**
*   **Form Complexity:** The sheer number of advanced options can be overwhelming. `crawl4ai` *offers a rich ecosystem of configurable strategies and parameters* that this plan now aims to fully integrate, necessitating careful organization and a more guided user experience.
*   **Fetching Engine Choice & Configuration:** Users need not only a choice of engine but also the ability to configure advanced strategies within `crawl4ai`.
*   **Progress Indication:** Lacks detailed progress feedback. `crawl4ai`'s async nature and potential for hooks could significantly improve this.
*   **Content Management:** No interface exists to view or manage a history of fetched items. The existing history display requires refactoring for data fetching.
*   **Workflow Clarity:** The workflow could be more guided, especially with the introduction of complex `crawl4ai` strategies.

## 3. Proposed Enhancements & Design

### 3.1. Simplified Fetch Form & Workflow with Advanced `crawl4ai` Integration

**Goal:** Make it easier for users to initiate a fetch request, offer a choice of fetching engines, and provide access to basic and advanced options (including sophisticated `crawl4ai` strategies) in a structured, intuitive manner.

**Proposed Changes:**

*   **Fetching Engine Selection (New):** `[STATUS: Fully Implemented (Base Selection)]`
    *   Allow users to choose between "Standard Fetch" (current Jina AI based) and "Advanced Crawl (`crawl4ai`)" (or similar naming). This choice will dynamically influence available subsequent options, especially the advanced strategy configurations for `crawl4ai`.
*   **Two-Tiered Options:**
    *   **Basic Options (Visible by Default):** `[STATUS: Fully Implemented]`
        *   `URL`: The primary input.
        *   `Fetching Engine`: Dropdown to select.
        *   *(Initial `Fetch Depth` and `Target Content Area` will be refined/absorbed into the new `crawl4ai` strategy sections below).*
    *   **Advanced Options Toggle & Structure:** `[STATUS: Fully Implemented]`
    *   **Advanced Options (Initially Collapsed/Modal, context-aware based on selected engine):**
        *   **Common Advanced Options (Jina & General):** `[STATUS: Fully Implemented]`
            *   Retain relevant existing advanced options (markdown flavor, image handling, etc.) but ensure clear labeling and tooltips.
        *   **`crawl4ai` Specific Advanced Options (Visible if `crawl4ai` is selected):** `[STATUS: Planning for Advanced Strategies; Basic Parameter UI Exists but Backend Mapping Incomplete]`
            *   *(These options are derived from the comprehensive parameter list in [`docs/crawl4ai_parameters.md`](../../docs/crawl4ai_parameters.md) and the Researcher's report. They aim to expose relevant `BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, and various strategy configurations. The backend mapping in [`backend/app/crawl4ai_fetcher.py`](../../backend/app/crawl4ai_fetcher.py:1) will require significant updates to dynamically instantiate and configure these strategies.)*

            *   **A. Selectable Extraction Strategies:**
                *   **UI Goal:** Allow users to choose an extraction strategy and configure its specific parameters.
                *   **Selection:** Dropdown/Radio group for:
                    *   `LLMExtractionStrategy`
                    *   `JsonCssExtractionStrategy`
                    *   `CosineStrategy`
                    *   (Default/None: `crawl4ai`'s standard content extraction)
                *   **Strategy-Specific Parameters (Dynamic UI):**
                    *   **For `JsonCssExtractionStrategy`:**
                        *   `Schema`: Text area for JSON schema definition.
                    *   **For `LLMExtractionStrategy`:**
                        *   `LLM Instructions/Prompt`: Text area for detailed instructions.
                        *   **`LLMConfig` (Contextual):** These options become particularly relevant here.
                            *   `LLM Provider/Model`: Flexible text input (e.g., "openai/gpt-4o-mini", "groq/llama3-70b", "ollama/mistral", "lmstudio/local-model", "google/gemini-1.5-pro"). Include help text/examples.
                            *   `LLM API Token`: Secure input or note about using environment variables.
                            *   `LLM Base URL (Custom Endpoint)`: Text input.
                *   **Backend Impact:** Backend must instantiate the chosen strategy with its parameters and the `LLMConfig` if applicable.

            *   **B. Advanced Deep Crawling Strategies:**
                *   **UI Goal:** Allow selection and configuration of deep crawling behavior, replacing/enhancing the simple "Fetch Depth" concept.
                *   **Strategy Selection:** Dropdown/Radio group for:
                    *   `BFSDeepCrawlStrategy` (Breadth-First)
                    *   `DFSDeepCrawlStrategy` (Depth-First)
                    *   `BestFirstCrawlingStrategy`
                *   **Common Deep Crawl Parameters:**
                    *   `Max Depth`: Number input (replaces old "Fetch Depth").
                    *   `Include External Links (`include_external`)`: Switch, with clear tooltip about behavior during deep crawls.
                *   **Strategy-Specific Parameters (Dynamic UI):**
                    *   **For `BestFirstCrawlingStrategy`:**
                        *   `URL Scorer`: Dropdown (e.g., `KeywordRelevanceScorer`).
                        *   `Scorer Parameters`: Conditional inputs (e.g., text input for keywords if `KeywordRelevanceScorer` is chosen).
                    *   `Filter Chain`: UI mechanism to define a chain of URL filters (e.g., regex filters, domain filters). This might start simple (e.g., list of regex patterns) and evolve.
                *   **Backend Impact:** Backend must instantiate the chosen deep crawl strategy with its specific configuration.

            *   **C. Configurable Markdown Generation:**
                *   **UI Goal:** Allow users to influence the final Markdown output.
                *   **Options:**
                    *   `Markdown Generator`: Dropdown for known `crawl4ai` markdown generators or a text input for custom ones.
                *   **Backend Impact:** Pass selected generator to `CrawlerRunConfig.markdown_generator`.

            *   **D. General `crawl4ai` Configuration (Browser, Content, Caching, etc.):**
                *   This section will house many of the previously listed `BrowserConfig` and `CrawlerRunConfig` parameters that are generally applicable.
                *   **Browser & Navigation Settings (Primarily `BrowserConfig` & `CrawlerRunConfig`):**
                    *   `User Agent`, `Viewport Size`, `Proxy URL`, `Page Load Wait Condition`, `Page Timeout (ms)`, `Wait For Element/JS Condition`, `Enable JavaScript`, `Ignore HTTPS Errors`, `Light Mode`, `Text Mode`.
                *   **Content Extraction & Processing (`CrawlerRunConfig`):**
                    *   `Target Elements (CSS Selectors)`, `Excluded Elements (CSS Selector)`, `Excluded Tags`, `Extract Only Text Content`, `Process iFrames Content`, `Word Count Threshold`, `Remove Forms`, `Keep Data Attributes`.
                *   **Page Interaction & Automation (`CrawlerRunConfig`):**
                    *   `Execute JavaScript on Page Load`, `Scan Full Page`, `Scroll Delay`, `Attempt to Remove Overlay Elements`, `Simulate User Behavior`, `Enable "Magic"`, `Override Navigator Properties`.
                *   **Caching (`CrawlerRunConfig`):**
                    *   `Cache Mode`.
                *   **Media Handling (`CrawlerRunConfig`):**
                    *   `Capture Screenshot`, `Generate PDF`, `Capture MHTML`, `Exclude External Images`, `Image Alt Text Min Word Count`, `Image Relevance Score Threshold`.
                *   **Link & Domain Filtering (`CrawlerRunConfig` - general, distinct from deep crawl filters):**
                    *   `Exclude External Links`, `Exclude Social Media Links`, `Custom Excluded Domains`.
                *   **Compliance (`CrawlerRunConfig`):**
                    *   `Respect robots.txt Rules`.
                *   **Debugging & Logging (`CrawlerRunConfig`):**
                    *   `Verbose Logging`, `Log Page Console Output`.

            *   **E. Expert `crawl4ai` Options (Potentially a separate, clearly marked subsection):**
                *   **UI Goal:** Expose highly technical or less frequently used parameters for expert users.
                *   **Parameters:**
                    *   `BrowserConfig`: `cookies` (e.g., JSON input), `headers` (e.g., JSON input), `persistent_context` (toggle).
                    *   `CrawlerRunConfig`: `session_id` (text input), `css_selector` (if a global one is needed beyond target_elements).

        *   **Jina.ai Specific Options (Visible if "Standard Fetch" is selected and still relevant):** `[STATUS: Fully Implemented]`
            *   Review existing Jina.ai options.

*   **Layout:** `[STATUS: Fully Implemented (Base Structure)]`
    *   The main card will feature the URL input and Fetching Engine selection prominently.
    *   A clear "Fetch" button.
    *   A toggle or link to reveal "Advanced Options," which will then present the structured `crawl4ai` configurations.

**User Flow for Submitting a Fetch Request:** (Conceptual update for `crawl4ai` path)

```mermaid
graph TD
    A[User lands on Fetch Page] --> B{Enters URL};
    B --> BA{Selects Fetching Engine (Standard/crawl4ai)};
    BA -- crawl4ai --> BC[Configure Basic crawl4ai settings (e.g., Max Depth)];
    BC --> E{Clicks "Fetch"};
    BA -- Standard --> SC[Configure Standard Fetch options];
    SC --> E;
    
    BA --> G{Wants Advanced Options?};
    G -- Yes & crawl4ai --> H_crawl4ai[Expands Advanced Options];
    H_crawl4ai --> H1[Selects Extraction Strategy & Configures];
    H1 --> H2[Selects Deep Crawling Strategy & Configures];
    H2 --> H3[Configures Markdown Generation];
    H3 --> H4[Configures General/Expert crawl4ai Settings];
    H4 --> E;

    G -- Yes & Standard --> H_standard[Expands Standard Advanced Options];
    H_standard --> I_standard[Configures Standard Settings];
    I_standard --> E;

    G -- No --> E;
    E --> F[Request Sent to Backend (with engine choice & all configs)];
```

### 3.2. Improved Progress & Log Visualization
`[STATUS: Fully Implemented (Base Structure)]`
*   Maintain dedicated progress section, progress bar, status updates/logs (SSE), and cancellable action.
*   Ensure logs can reflect detailed stages from `crawl4ai`'s advanced strategies.

### 3.3. Fetched Content Management Interface
`[STATUS: Partially Implemented - Key data fetching and action items pending as noted in v1.2]`
*   **New Tab or Section:** "Fetch History". `[STATUS: Fully Implemented]`
*   **Data Table/List ([`FetchHistoryTable.jsx`](../../src/components/fetch/FetchHistoryTable.jsx:1)):** `[STATUS: Partially Implemented - Data fetching and pagination to be refactored using the \`use-infinite-query\` hook. Current implementation lacks filtering by engine/status, searching by URL/Title, and sorting by date.]`
    *   Continue with `use-infinite-query` integration plan.
    *   Ensure history items store and can display the chosen `crawl4ai` strategies and key parameters.
*   **Actions per Item:**
    *   `View Content`: `[STATUS: Partially Implemented - Actual fetched content is not re-loaded or displayed from history. Needs to handle structured JSON from \`JsonCssExtractionStrategy\`.]`
    *   `Re-fetch`: `[STATUS: Fully Implemented (Base). Needs to correctly pre-fill advanced strategy configurations.]`
    *   `Delete`: `[STATUS: Partially Implemented - Handler is a stub; no backend delete endpoint.]`
    *   `Copy URL/Markdown`: `[STATUS: Not Implemented]`
*   **Data Persistence:** `[STATUS: Fully Implemented (Base Schema)]`
    *   The `engine_specific_parameters` JSONB column is critical for storing detailed `crawl4ai` strategy configurations.
    *   `output_type` column (e.g., 'markdown', 'structured_json') becomes more important.

### 3.4. Leveraging Existing & New Components
*   **Existing Shadcn/ui Components:** `[STATUS: Fully Implemented]`
*   **New Custom Components (Conceptual):**
    *   `FetchProgressDisplay.jsx` `[STATUS: Implemented]`
    *   `FetchHistoryItem.jsx` (Implicitly part of `FetchHistoryTable.jsx`)
    *   `FetchJobCard.jsx` (Implicitly part of `FetchForm.jsx` and progress display)
    *   **`ExtractionStrategyConfigurator.jsx` (New Conceptual):** Dynamic UI for selecting and configuring `LLMExtractionStrategy`, `JsonCssExtractionStrategy`, etc., including their specific parameters (schema, LLM instructions, `LLMConfig`).
    *   **`DeepCrawlStrategyConfigurator.jsx` (New Conceptual):** Dynamic UI for selecting and configuring `BFS/DFS/BestFirst` strategies, scorers, filters.
    *   [`FetchedContentViewer.jsx`](../../src/components/fetch/FetchedContentViewer.jsx:1): `[STATUS: Implemented, but capability for structured data (e.g., JSON from \`JsonCssExtractionStrategy\`) needs explicit implementation/verification.]`

## 4. Alignment with Guiding Principles
*   **User-Centricity:** Advanced `crawl4ai` strategies empower expert users while basic options remain accessible. Structured configuration prevents overwhelm.
*   *(Other principles remain largely the same as v1.2)*

## 5. Component Breakdown (New/Modified)

*   **Modified:** `[STATUS: Significantly updated as per the plan, further changes for advanced strategies]`
    *   [`src/app/fetch/page.js`](../../src/app/fetch/page.js): Will need to manage state for the new dynamic `crawl4ai` strategy configurations.
    *   [`src/components/fetch/FetchForm.jsx`](../../src/components/fetch/FetchForm.jsx): To host the new strategy configurator components.
    *   [`src/components/fetch/AdvancedFetchOptions.jsx`](../../src/components/fetch/AdvancedFetchOptions.jsx): To be restructured to include the new strategy-based organization.
*   **New Components (Conceptual):**
    *   `FetchProgressTracker.jsx`: `[STATUS: Implemented]`
    *   `FetchHistoryTable.jsx`: `[STATUS: Implemented, but data fetching and pagination will be refactored using \`use-infinite-query\` as noted in 3.3. Currently missing features like advanced filtering/sorting.]`
    *   [`FetchedContentViewer.jsx`](../../src/components/fetch/FetchedContentViewer.jsx:1): `[STATUS: Implemented, but capability for structured data (e.g., JSON from \`crawl4ai\`) is not explicitly present/verified.]`
    *   `ExtractionStrategyConfigurator.jsx`: For selecting and configuring extraction strategies.
    *   `DeepCrawlStrategyConfigurator.jsx`: For selecting and configuring deep crawling strategies.

## 6. Backend Considerations

*   **API for Fetching (`/fetch-content`):** `[STATUS: Partially Implemented - Base engine selection exists. Major work needed for advanced \`crawl4ai\` strategy mapping.]`
    *   The backend ([`backend/app/crawl4ai_fetcher.py`](../../backend/app/crawl4ai_fetcher.py:1)) must be significantly updated to:
        *   Receive parameters indicating chosen extraction and deep crawling strategies and their configurations.
        *   **Dynamically instantiate and configure** the selected `crawl4ai` extraction strategies (e.g., `LLMExtractionStrategy` with its prompt, `JsonCssExtractionStrategy` with its schema).
        *   **Dynamically instantiate and configure** the selected `crawl4ai` deep crawling strategies (e.g., `BestFirstCrawlingStrategy` with its scorer).
        *   Correctly assemble `BrowserConfig`, `CrawlerRunConfig`, and `LLMConfig` objects based on all incoming parameters.
*   **`LLMConfig` Handling:**
    *   The backend must robustly parse the `LLM Provider/Model` string (e.g., "openai/gpt-4o-mini", "ollama/mistral") to correctly instantiate `LLMConfig` for `crawl4ai`, accommodating diverse local and cloud providers. This may involve a mapping or flexible parsing strategy.
    *   Ensure secure handling of API keys, potentially prioritizing environment variables on the backend.
*   **SSE for Progress:** `[STATUS: Fully Implemented]`
    *   Ensure SSE can relay progress/logs from the more complex, multi-stage `crawl4ai` operations.
*   **API for Fetch History:** `[STATUS: Fully Implemented (POST and GET) - NOTE: Backend delete endpoint for history items is missing. Data fetching will now primarily be handled client-side via \`use-infinite-query\` directly interacting with Supabase, though API might still be used for writes or specific actions.]`
    *   Ensure `engine_specific_parameters` correctly stores the full configuration of chosen strategies for accurate "Re-fetch".
*   **Database Schema:** `[STATUS: Assumed Fully Implemented by review.]`
    *   The `fetch_history` table's `engine_specific_parameters` (JSONB) and `output_type` columns are crucial.
*   **Error Handling:** `[STATUS: Fully Implemented]`
    *   Adapt to handle errors arising from misconfiguration or failure of advanced `crawl4ai` strategies.

## 7. Future Considerations

*   **Visual Selector for `crawl4ai`:** (Remains relevant)
*   **`crawl4ai` Presets:** Develop presets for common advanced `crawl4ai` configurations (e.g., "Extract structured data with LLM", "Deep crawl for blog posts").
*   **Interactive Filter Chain Builder:** For `filter_chain` in deep crawling, a more visual or interactive builder.
*   **Advanced `BrowserConfig` UI:** If not fully covered in "Expert Options," consider more granular UI for cookies, headers.
*   **Comparative Analysis & Guidance:** (Remains relevant)
*   **Batch Fetching with `crawl4ai`:** (Remains relevant)

## 8. Current Implementation Status, Remaining Work & Recommendations (Post-Researcher Report)

This section outlines the path forward, focusing on integrating the advanced `crawl4ai` capabilities identified by the Researcher.

### 8.1. Status of Previously Identified Issues (from v1.2):

*   **Incomplete `crawl4ai` Parameter Mapping:** Now part of the larger "Advanced `crawl4ai` Integration" phase, requiring comprehensive backend work for strategy instantiation.
*   **Incomplete Fetch History Actions:**
    *   `View Content from History`: Still needs robust implementation, especially for structured data.
    *   `Delete History Item`: Backend endpoint still needed.
    *   `Copy URL/Markdown from History`: Still not implemented.
*   **Missing Fetch History Filtering and Sorting:** Still pending.
*   **Potential Gap for Structured Data Display:** Now a higher priority with `JsonCssExtractionStrategy`.
*   **`use-infinite-query` Hook Integration:** Assumed to be proceeding as a separate but related task. Its completion will simplify history display.

### 8.2. New Phase: Advanced `crawl4ai` Integration (Prioritized Work Items)

This new phase focuses on implementing the deep `crawl4ai` integration:

1.  **UI - Extraction Strategies:**
    *   **Action:** Design and implement frontend components ([`ExtractionStrategyConfigurator.jsx`](../../src/components/fetch/ExtractionStrategyConfigurator.jsx:1)) for selecting and configuring `LLMExtractionStrategy`, `JsonCssExtractionStrategy`, `CosineStrategy`. This includes UI for their specific parameters (JSON schema, LLM instructions) and contextual `LLMConfig` inputs (Provider/Model, API Key, Base URL with flexible provider format support). [STATUS: Verified Implemented]
    *   **Goal:** Allow users to define sophisticated content extraction methods.

2.  **Backend - Extraction Strategies:**
    *   **Action:** Update [`backend/app/crawl4ai_fetcher.py`](../../backend/app/crawl4ai_fetcher.py:1) to dynamically instantiate and use the selected extraction strategy (`LLMExtractionStrategy`, `JsonCssExtractionStrategy`, etc.) with its full configuration, including the parsed `LLMConfig`. [STATUS: Verified Implemented]
    *   **Goal:** Make UI-selected extraction strategies functional.

3.  **UI - Advanced Deep Crawling Strategies:**
    *   **Action:** Design and implement frontend components ([`DeepCrawlStrategyConfigurator.jsx`](../../src/components/fetch/DeepCrawlStrategyConfigurator.jsx:1)) for selecting `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, `BestFirstCrawlingStrategy`. Include UI for `max_depth`, `include_external`, and strategy-specific parameters like `url_scorer` (with its own config, e.g., keywords) and `filter_chain` capabilities. [STATUS: Verified Implemented]
    *   **Goal:** Provide fine-grained control over crawling behavior.

4.  **Backend - Advanced Deep Crawling Strategies:**
    *   **Action:** Update [`backend/app/crawl4ai_fetcher.py`](../../backend/app/crawl4ai_fetcher.py:1) to dynamically instantiate and use the selected deep crawling strategy with its specific configuration. [STATUS: Partially Implemented - Filter/Scorer instantiation needs review due to potential parameter key mismatch.]
    *   **Goal:** Enable advanced, configurable multi-page crawling.

5.  **UI & Backend - Configurable Markdown Generation:**
    *   **Action:** Implement UI options for `CrawlerRunConfig.markdown_generator` and ensure the backend correctly passes this to `crawl4ai`. [STATUS: Verified Implemented]
    *   **Goal:** Allow user control over Markdown output format.

6.  **UI & Backend - General and Expert `crawl4ai` Options:**
    *   **Action:** Implement UI for the general `BrowserConfig` / `CrawlerRunConfig` parameters (as listed in 3.1.D) and the "Expert Options" (cookies, headers, persistent context, session_id, css_selector from 3.1.E). Ensure backend maps these to `crawl4ai`. [STATUS: Verified Implemented]
    *   **Goal:** Expose remaining useful `crawl4ai` parameters.

7.  **`LLMConfig` End-to-End Robustness:**
    *   **Action:** Thoroughly test the pipeline for `LLMConfig` (provider string parsing, API key handling, base URL) from frontend to backend and into `crawl4ai`'s LLM-dependent strategies, ensuring it works for various specified providers (OpenAI, Groq, Ollama, LMStudio, Google). [STATUS: Verified Implemented (Static Analysis)]
    *   **Goal:** Reliable and secure LLM integration for `crawl4ai`.

8.  **Fetch History Refinement for Advanced Strategies:**
    *   **Action:** Ensure that the chosen advanced `crawl4ai` strategies and their full configurations are correctly saved in the `fetch_history` table (within `engine_specific_parameters`) and accurately pre-filled when using the "Re-fetch" action. [STATUS: Partially Implemented - Frontend pre-fill logic exists, but backend saving of parameters appears missing.]
    *   **Goal:** Maintain fidelity for re-fetching complex configurations.

9.  **`FetchedContentViewer.jsx` Enhancement for Structured Data:**
    *   **Action:** Explicitly add and verify the capability in [`FetchedContentViewer.jsx`](../../src/components/fetch/FetchedContentViewer.jsx:1) to display structured JSON output (e.g., from `JsonCssExtractionStrategy`), potentially using a JSON tree viewer or formatted table. [STATUS: Verified Implemented]
    *   **Goal:** Properly display all types of `crawl4ai` output.

10. **Documentation & Tooltips:**
    *   **Action:** Update all relevant UI tooltips and any internal/user-facing documentation to explain the new advanced `crawl4ai` options and strategies. [STATUS: Verified Implemented (In-code Tooltips)]
    *   **Goal:** Ensure users understand how to use the new powerful features.

### 8.3 Current Status and Resolved Issues

The feature implementation for the 'Advanced `crawl4ai` Integration' phase (Section 8.2) is largely complete based on code review.

**Resolved Blocker: `NotImplementedError` on Windows for `crawl4ai`**

Previously, `crawl4ai`-based fetches were non-functional on Windows environments due to a persistent `NotImplementedError`. This error originated from an incompatibility between Uvicorn's `--reload` flag and the `asyncio.WindowsProactorEventLoopPolicy` required by `playwright` (a dependency of `crawl4ai`) for subprocess handling.

*   **Cause:** Uvicorn's `--reload` functionality interfered with the necessary `asyncio` event loop policy on Windows.
*   **Solution:** The issue has been resolved by running the Uvicorn server without the `--reload` flag during development on Windows systems. This allows `crawl4ai` to function correctly. (Refer to [`docs/CONTEXT_README.md`](../../docs/CONTEXT_README.md:1) for more details on the development environment setup).

With this blocker resolved, `crawl4ai`-based fetches are now functional on Windows, significantly improving the development and testing workflow for this integration.

**Remaining Considerations:**
Verification had previously identified potential issues with backend handling of deep crawl filter/scorer parameters and missing backend logic for saving detailed strategy configurations to fetch history. These items should be re-evaluated now that the primary Windows blocker is resolved.

This comprehensive plan for advanced `crawl4ai` integration aims to transform the Fetch page into a highly capable tool for diverse web content acquisition tasks. The focus is on leveraging `crawl4ai`'s underlying power through a well-structured and configurable UI, supported by a robust backend implementation.