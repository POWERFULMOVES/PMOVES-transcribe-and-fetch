## PMOVES UI Enhancement Strategic Plan

**1. Overall Goal:**
To significantly enhance the user interface (UI) and user experience (UX) of the PMOVES platform by modernizing components, improving workflow clarity, and strategically integrating Supabase UI components where beneficial.

**2. Guiding Principles:**
*   **User-Centricity:** Prioritize ease of use, intuitive navigation, and clear feedback for all user actions.
*   **Consistency:** Maintain a consistent design language and component behavior across all sections of the application.
*   **Modularity:** Develop and enhance reusable components to streamline development and maintenance.
*   **Performance:** Ensure UI enhancements do not negatively impact application speed and responsiveness.
*   **Accessibility:** Adhere to accessibility best practices to make the platform usable for a wider audience.

**3. Review and Analysis Phase:**
*   **Current UI Audit:**
    *   Systematically review each key page:
        *   [`src/app/transcribe/page.js`](src/app/transcribe/page.js)
        *   [`src/app/fetch/page.js`](src/app/fetch/page.js)
        *   [`src/app/download/page.js`](src/app/download/page.js)
        *   [`src/app/upserter/page.js`](src/app/upserter/page.js)
        *   [`src/app/vector-search/page.js`](src/app/vector-search/page.js)
    *   Evaluate existing components in [`src/components/`](src/components/) for:
        *   Visual appeal and modernity.
        *   Ease of use and intuitiveness.
        *   Consistency with the overall application.
        *   Responsiveness across different screen sizes.
        *   Information density and clarity.
*   **User Workflow Analysis:**
    *   Map out the primary user flows for each section (transcription, fetching, etc.).
    *   Identify pain points, areas of confusion, or inefficiencies in the current workflows.
    *   Look for opportunities to simplify steps or provide better guidance.
*   **Supabase UI Component Evaluation (Future Step - for implementation team):**
    *   Research available Supabase UI components (e.g., from libraries like `supabase-ui` or official Supabase examples).
    *   Assess their suitability for PMOVES, considering features, customization options, and ease of integration.
    *   Focus on components that can simplify data display, forms, authentication, and real-time updates.

**4. Key Areas for UI/UX Improvement & Prioritization:**

*   **A. Global Enhancements:**
    *   **Navigation:** Review the main navigation structure ([`src/components/nav-header.js`](src/components/nav-header.js)). Ensure it's intuitive and provides easy access to all key sections. Consider a more modern sidebar or top navigation approach if current is lacking.
    *   **Feedback & Notifications:** Standardize and improve user feedback for actions (success, error, loading). Utilize a consistent toast/notification system (e.g., using [`src/components/hooks/use-toast.js`](src/components/hooks/use-toast.js) and [`src/components/ui/sonner.jsx`](src/components/ui/sonner.jsx) or similar).
    *   **Forms:** Standardize form design and validation across the application. Ensure all input fields ([`src/components/ui/input.jsx`](src/components/ui/input.jsx), [`src/components/ui/textarea.jsx`](src/components/ui/textarea.jsx), [`src/components/ui/select.jsx`](src/components/ui/select.jsx), etc.) are clear and provide good user feedback.
    *   **Data Display:** Improve how lists, tables ([`src/components/ui/table.jsx`](src/components/ui/table.jsx)), and cards ([`src/components/ui/card.jsx`](src/components/ui/card.jsx)) present information. Consider pagination, sorting, and filtering capabilities, potentially leveraging Supabase UI for data grids.
    *   **Theme & Styling:** Review [`src/app/globals.css`](src/app/globals.css) and theme configuration ([`src/components/theme-provider.jsx`](src/components/theme-provider.jsx), [`src/app/theme-config.js`](src/app/theme-config.js)). Ensure a modern, clean, and accessible theme.

*   **B. Page-Specific Enhancements (Prioritized):**

    *   **i. Vector Search (`src/app/vector-search/page.js`):**
        *   **Priority:** High. This is a core feature.
        *   **Status:** Completed (May 7, 2025)
        *   **Current Components:** [`src/components/search/`](src/components/search/) (e.g., [`SearchFlow.jsx`](src/components/search/SearchFlow.jsx:1), [`SearchResultCard.jsx`](src/components/search/SearchResultCard.jsx:1), [`SearchResultsTable.jsx`](src/components/search/SearchResultsTable.jsx:1)).
        *   **Potential Improvements:**
            *   More interactive and visual query building.
            *   Enhanced results display: clearer highlighting of matches, better metadata presentation, options for different views (card, list, table).
            *   Improved filtering and sorting options for search results.
            *   Integration of AI-powered analysis display ([`AnalysisDisplay.jsx`](src/components/search/AnalysisDisplay.jsx:1)) in a more user-friendly manner.
            *   **Supabase UI:** Consider Supabase components for real-time result updates, data tables, or filter controls if they offer advantages over existing custom components.

    *   **ii. Upserter (`src/app/upserter/page.js`):**
        *   **Priority:** High.
        *   **Status:** Largely Completed.
        *   **Summary of Enhancements (as of May 2025):**
            *   Integrated Supabase "File Upload (Dropzone)" component ([`src/components/dropzone.jsx`](src/components/dropzone.jsx:1)) for streamlined file uploads.
            *   Implemented a metadata form to capture essential information alongside file uploads on the [`src/app/upserter/page.js`](src/app/upserter/page.js).
            *   Developed and connected a backend API ([`src/app/api/content/upsert/file/route.js`](src/app/api/content/upsert/file/route.js)) for persisting file information and associated metadata.
        *   **Previously Noted Potential Improvements (Now Addressed or Re-evaluated):**
            *   Streamlined file/content upload process: Addressed with Dropzone integration.
            *   Clearer progress indicators: Addressed with Dropzone features and API feedback mechanisms.
            *   Better management interface for uploaded content: Partially addressed by storing metadata. A dedicated UI for managing all uploaded content could be a future enhancement if deemed necessary.
            *   Improved form for metadata input: Addressed with the new metadata form.
            *   **Supabase UI:** Leveraged for the file upload component. Further Supabase UI components for displaying lists of processed items can be considered if a dedicated management interface is built.

    *   **iii. Transcribe (`src/app/transcribe/page.js`):**
        *   **Priority:** Medium-High. Core transcription functionality.
        *   **Potential Improvements:**
            *   Intuitive interface for selecting processing options (GPU vs. Groq).
            *   Clear display of transcription progress and status (leveraging SSE).
            *   User-friendly way to view and manage completed transcriptions (segmented, full, speaker diarization).
            *   **Supabase UI:** Could be used for displaying transcription jobs, their statuses, and results in a structured table or list.

    *   **iv. Fetch (`src/app/fetch/page.js`):**
        *   **Priority:** Medium. Important for web content.
        *   **Current Status (May 8, 2025):**
            *   Advanced `crawl4ai` integration features for the Fetch page (as detailed in [`docs/fetch_page_enhancement_plan.md`](docs/fetch_page_enhancement_plan.md) Section 8.2) have been implemented, though some backend logic requires further review/completion (see linked plan).
            *   **Known Blocker:** `crawl4ai` functionality on the Fetch page is currently blocked on Windows due to a persistent `NotImplementedError` (asyncio/playwright). Further investigation is needed. Refer to [`docs/fetch_page_enhancement_plan.md`](docs/fetch_page_enhancement_plan.md) for details.
            *   Dynamic LLM model selection from the backend registry has been implemented for the `crawl4ai` engine. Users can choose from available models in the 'Advanced Fetch Options' UI, which utilizes the `useLLMModels` hook.
        *   **Potential Improvements:**
            *   Simplified form for entering URLs and fetch parameters.
            *   Better visualization of fetching progress and logs.
            *   Interface for managing fetched content.
            *   **Supabase UI:** Forms and data display components.

    *   **v. Download (`src/app/download/page.js`):**
        *   **Priority:** Medium. Utility feature.
        *   **Potential Improvements:**
            *   Clearer options for format selection, quality, and other download parameters.
            *   Improved progress tracking for downloads.
            *   **Supabase UI:** Forms and progress indicators.

**5. Suggested New Components or UI Feature Types:**

*   **Advanced Data Table/Grid:** For displaying search results, upserter logs, transcription lists. Should support sorting, filtering, pagination, and potentially inline actions. *Supabase UI might offer good options here.*
*   **Enhanced File Upload Component:** With drag-and-drop, progress bars, and preview capabilities.
*   **Interactive Query Builder:** For vector search, allowing users to construct complex queries more easily.
*   **Status Dashboard/Overview:** A section or component that gives users a quick overview of ongoing processes (transcriptions, fetches, downloads) and their statuses.
*   **Rich Text Editor/Viewer:** For displaying and potentially editing formatted content (e.g., cleaned HTML from fetched pages or formatted transcriptions).
*   **Settings/Configuration Panels:** For user-specific preferences or advanced settings for each module, presented in a clear and organized way.
*   **Onboarding/Help Components:** Tooltips ([`src/components/ui/tooltip.jsx`](src/components/ui/tooltip.jsx)), guided tours, or contextual help sections to improve usability, especially for new users.

**6. Status Update & Next Steps (Focus: Transcribe Page - May 2025):**

The detailed planning and implementation for the "Vector Search" page ([`src/app/vector-search/page.js`](src/app/vector-search/page.js)) enhancements, which were the previous focus of this section, are now complete as of May 7, 2025.

Following the priorities outlined in Section 4.B, the next key area for UI/UX enhancement is the **"Transcribe" page** ([`src/app/transcribe/page.js`](src/app/transcribe/page.js)). This page is designated with a Medium-High priority (see Section 4.B.iii).

The potential improvements for the "Transcribe" page, as noted in Section 4.B.iii, include:
*   Developing a more intuitive interface for selecting processing options (e.g., GPU vs. Groq).
*   Ensuring a clear display of transcription progress and status, leveraging Server-Sent Events (SSE).
*   Providing a user-friendly way to view and manage completed transcriptions, including segmented audio, full transcripts, and speaker diarization information.

Consequently, the next phase of work will concentrate on a detailed review, research, design, and implementation planning specifically for these "Transcribe" page enhancements.