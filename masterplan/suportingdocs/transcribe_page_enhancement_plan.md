# Detailed Plan: "Transcribe" Page UI/UX Enhancement

**Date:** May 7, 2025
**Version:** 1.0
**Author:** Roo (Architect AI)

## 1. Introduction

This document outlines the detailed plan for enhancing the User Interface (UI) and User Experience (UX) of the "Transcribe" page (currently part of [`src/app/page.js`](src/app/page.js:1)) within the PMOVES platform. The plan is based on the objectives set forth in the [`docs/ui_enhancement_plan.md`](docs/ui_enhancement_plan.md:1), focusing on intuitive processing options, clear progress display, and user-friendly results management.

## 2. Guiding Principles Recap

All enhancements will adhere to the PMOVES guiding principles:
*   **User-Centricity:** Prioritize ease of use, intuitive navigation, and clear feedback.
*   **Consistency:** Maintain a consistent design language.
*   **Modularity:** Develop reusable components.
*   **Performance:** Ensure UI enhancements do not negatively impact speed.
*   **Accessibility:** Adhere to accessibility best practices.

## 3. Current State Analysis

The "Transcribe" functionality currently resides within a tab in [`src/app/page.js`](src/app/page.js:1060-1239). It includes:
*   Input fields for YouTube URL and save directory.
*   A dropdown for selecting the transcription model (Faster Whisper vs. Groq).
*   A "Process Video" button to initiate transcription.
*   A visual step-progress indicator.
*   A "Status Updates" panel showing log-like messages.
*   A "Live Transcription" panel displaying segments as they arrive via SSE.

While functional, there are opportunities for improvement in clarity, workflow, and management of completed transcriptions.

## 4. Detailed Enhancement Plan

### 4.1. Intuitive Processing Options

**Goal:** Design an interface for users to easily select and understand processing options (e.g., GPU vs. Groq).

**Current:** A simple dropdown menu ([`src/app/page.js`](src/app/page.js:1069-1080)) for model selection.

**Proposed Enhancements:**

*   **Component:** `ProcessingOptionsSelector` (New or Enhanced `Select` component)
    *   **Visual Distinction:** Instead of a plain dropdown, consider using visually distinct cards or radio buttons with icons and brief descriptions for each option (GPU/Local vs. Groq/Cloud). This leverages the existing `TRANSCRIPTION_STYLES` constants ([`src/app/page.js`](src/app/page.js:65-90)) for icons (☁️ for Groq, 💻 for Local).
        *   **Example:**
            *   Card 1: "💻 Local GPU (Faster Whisper)" - "High-speed transcription using your local GPU. Best for privacy and no external API calls."
            *   Card 2: "☁️ Cloud AI (Groq)" - "Fast transcription using Groq's cloud API. May be quicker for some, offloads GPU work. Requires backend API key."
    *   **Information Tooltips:** Add tooltips ([`src/components/ui/tooltip.jsx`](src/components/ui/tooltip.jsx:1)) to each option explaining its benefits, requirements (e.g., "GPU required," "API key configured on backend"), and potential costs or speed implications.
    *   **Default Selection:** Maintain the current logic for default selection or make it configurable if needed.
    *   **Layout:** Integrate this selector clearly within the "Video Transcription Setup" card ([`src/app/page.js`](src/app/page.js:1061-1150)).

*   **User Flow:**
    1.  User navigates to the "Transcription" tab.
    2.  User sees clear, visually distinct options for processing.
    3.  User can hover or click for more information (tooltips).
    4.  User selects an option. The UI might subtly update to reflect the choice (e.g., changing an icon next to the "Process Video" button).

### 4.2. Clear Progress Display

**Goal:** Plan for a clear and informative display of transcription progress and status, effectively utilizing Server-Sent Events (SSE).

**Current:**
*   A visual step-progress indicator ([`src/app/page.js`](src/app/page.js:1010-1048)).
*   A "Status Updates" panel ([`src/app/page.js`](src/app/page.js:1154-1177)) showing text logs.
*   A "Live Transcription" panel ([`src/app/page.js`](src/app/page.js:1179-1237)) showing incoming segments.
*   Timer for elapsed time ([`src/app/page.js`](src/app/page.js:397-448), displayed at line 1203).

**Proposed Enhancements:**

*   **Component:** `MasterProgressIndicator` (Enhance existing step progress)
    *   **Refine Steps:** The current steps are 'Enter YouTube URL', 'Process Video', 'Transcribe Audio', 'Transcription Complete'. These are good. Ensure they accurately reflect backend stages.
    *   **Sub-Status within Steps:** For longer steps like "Transcribe Audio," provide more granular feedback within the "Status Updates" panel, linked to the active step. For example, "Downloading audio...", "Preparing model...", "Transcribing chunk 1/10...".
    *   **Visual Feedback:**
        *   The existing progress bar and step highlighting are good.
        *   Consider adding subtle animations or icons to the active step in the `MasterProgressIndicator`.
        *   The "Status Updates" panel ([`src/app/page.js`](src/app/page.js:1172)) should remain, but its content should be more curated and less like a raw log if possible. Focus on user-understandable messages.
        *   The "Live Transcription" panel ([`src/app/page.js`](src/app/page.js:1210)) is effective for real-time segment display. Ensure smooth scrolling and clear demarcation of segments. The existing `TranscriptionSegment` component ([`src/app/page.js`](src/app/page.js:308-369)) is well-styled.

*   **Component:** `TranscriptionJobSummary` (New Component, displayed above or integrated with results)
    *   **Content:** Once processing starts, display a small summary:
        *   Video Title (if fetched from metadata).
        *   Selected Model (e.g., "Processing with Groq ☁️").
        *   Overall Status (e.g., "In Progress," "Completed," "Failed").
        *   Elapsed Time (already present, ensure it's clearly associated with the current job).
        *   Estimated time remaining (if backend can provide this via SSE).

*   **SSE Utilization:**
    *   Continue using SSE for real-time updates to status messages and transcription segments.
    *   Backend should send distinct event types for:
        *   Overall job status changes (e.g., `job_started`, `audio_downloaded`, `transcription_progress`, `job_completed`, `job_failed`).
        *   Detailed status messages.
        *   Transcription segments.
        *   Speaker diarization info (when available).
    *   The frontend reducer ([`src/app/reducers/transcriptionReducer.js`](src/app/reducers/transcriptionReducer.js:1)) should handle these events to update the UI components.

*   **Error Handling Display:**
    *   The current error display ([`src/app/page.js`](src/app/page.js:1321-1326)) is good. Ensure errors from SSE are also channeled here clearly.

### 4.3. User-Friendly Results Management

**Goal:** Design a system for users to view and manage completed transcriptions, including segmented audio, full transcripts, and speaker diarization information.

**Current:** Primarily shows live transcription. No dedicated area for managing/viewing *completed* jobs or detailed results beyond the concatenated live transcript.

**Proposed Enhancements:**

*   **Component:** `CompletedTranscriptionView` (New Component)
    *   **Layout:** This view would appear once a transcription is complete, potentially replacing or augmenting the "Live Transcription" panel for that job, or as a new section/tab.
    *   **Tabs within Results:** Use tabs ([`src/components/ui/tabs.jsx`](src/components/ui/tabs.jsx:1)) for different views of the result:
        *   **Segmented Transcript:**
            *   Similar to the current live view but for a completed job.
            *   Each segment ([`TranscriptionSegment`](src/app/page.js:308)) should still link to the YouTube timestamp if available.
            *   **Speaker Labels:** If speaker diarization is available from the backend, display speaker labels for each segment (e.g., "Speaker A:", "Speaker B:"). This will require modifications to the `TranscriptionSegment` component and the data structure.
            *   **Search/Filter:** Add a small search bar to filter segments within the completed transcript.
        *   **Full Transcript:**
            *   A view of the entire transcript as a single block of text.
            *   Option to "Copy to Clipboard" ([`Button`](src/components/ui/button.jsx:1)).
        *   **Download Options:**
            *   Buttons to download the transcript in various formats (e.g., TXT, SRT, VTT, JSON). This will require backend support to generate these formats.
            *   Leverage existing [`Button`](src/components/ui/button.jsx:1) components.
        *   **Audio Playback (Optional Advanced Feature):**
            *   If feasible, embed a simple audio player that can play back the original audio, with the transcript segments highlighting as the audio plays. This is a more complex addition.

*   **Component:** `TranscriptionHistory` (New Component - for managing multiple jobs)
    *   **Concept:** If users are expected to run multiple transcriptions, a history list/table would be beneficial. This might be a larger effort and could be a future iteration if not immediately feasible.
    *   **Display:** A table ([`src/components/ui/table.jsx`](src/components/ui/table.jsx:1)) listing past transcription jobs.
        *   Columns: Video Title/URL, Date, Model Used, Status (Completed, Failed), Actions (View, Delete).
        *   "View" action would load the `CompletedTranscriptionView` for that job.
    *   **Storage:** This would require backend persistence of job metadata and results. Supabase could be leveraged here.

*   **User Flow for Results:**
    1.  Transcription completes. The `MasterProgressIndicator` shows "Transcription Complete."
    2.  The "Live Transcription" panel might transition to the `CompletedTranscriptionView`, or a "View Results" button appears.
    3.  User interacts with the `CompletedTranscriptionView`:
        *   Switches between segmented, full transcript, and download tabs.
        *   Copies text or downloads files.
        *   Views speaker labels if available.
    4.  (If `TranscriptionHistory` is implemented) User can see a list of past jobs and revisit their results.

## 5. Component Strategy

*   **Leverage Existing `src/components/ui/`:**
    *   [`Tabs`](src/components/ui/tabs.jsx:1), [`Card`](src/components/ui/card.jsx:1), [`Button`](src/components/ui/button.jsx:1), [`Input`](src/components/ui/input.jsx:1), [`Label`](src/components/ui/label.jsx:1), [`Select`](src/components/ui/select.jsx:1), [`ScrollArea`](src/components/ui/scroll-area.jsx:1), [`Accordion`](src/components/ui/accordion.jsx:1), [`Tooltip`](src/components/ui/tooltip.jsx:1) (if added for processing options), [`Table`](src/components/ui/table.jsx:1) (for history).
    *   The existing `TranscriptionSegment` component ([`src/app/page.js`](src/app/page.js:308)) is a good base but will need modification for speaker labels.

*   **New Components to Create:**
    *   `ProcessingOptionsSelector` (or enhanced `Select` usage): For GPU vs. Groq choice.
    *   `TranscriptionJobSummary`: Small panel for ongoing job details.
    *   `CompletedTranscriptionView`: Main component for displaying finished transcript results with internal tabs.
    *   `TranscriptionHistory` (Potentially V2): For listing multiple past jobs.

*   **Modifications to Existing Components:**
    *   [`src/app/page.js`](src/app/page.js:1): Refactor to incorporate the new components and layout changes for the "Transcription" tab.
    *   `transcriptionReducer` ([`src/app/reducers/transcriptionReducer.js`](src/app/reducers/transcriptionReducer.js:1)): Update to handle new state related to completed job display, speaker diarization, and potentially history.
    *   `TranscriptionSegment` ([`src/app/page.js`](src/app/page.js:308)): Add support for displaying speaker labels.

## 6. Alignment with Guiding Principles

*   **User-Centricity:**
    *   Clearer processing options and progress feedback.
    *   Dedicated views for completed results make them easier to use.
    *   Tooltips and descriptive text aid understanding.
*   **Consistency:**
    *   Utilize existing UI components from `src/components/ui/` for a consistent look and feel.
    *   Follow established patterns for layout and interaction.
*   **Modularity:**
    *   New features like `CompletedTranscriptionView` and `ProcessingOptionsSelector` will be designed as reusable components.
*   **Performance:**
    *   Continue efficient use of SSE.
    *   Virtualization for long lists/transcripts if performance becomes an issue (though `ScrollArea` should handle typical cases).
*   **Accessibility:**
    *   Ensure all new interactive elements are keyboard navigable.
    *   Use appropriate ARIA attributes.
    *   Maintain good color contrast.
    *   Leverage semantic HTML and accessible components from `src/components/ui/`.

## 7. Visual Design & Layout Sketch (Mermaid Diagram)

```mermaid
graph TD
    A[Transcribe Page Tab] --> B{Transcription Setup};
    B -- Model Selection --> B1[ProcessingOptionsSelector: Local GPU vs. Cloud AI];
    B -- Inputs --> B2[YouTube URL Input];
    B -- Inputs --> B3[Save Directory Input];
    B -- Action --> B4[Process Video Button];

    A --> C[MasterProgressIndicator: Steps 1-4];

    A --> D{Ongoing Transcription Display};
    D --> D1[TranscriptionJobSummary: Title, Model, Time];
    D --> D2[Status Updates Panel (Scrollable)];
    D --> D3[Live Transcription Panel (Scrollable Segments)];

    A --> E{Completed Transcription View (Appears on Completion)};
    E --> E1[Tabs: Segmented | Full Text | Downloads];
    E1 -- Segmented --> E1a[Segmented List with Speaker Labels & Timestamps];
    E1 -- Full Text --> E1b[Full Transcript Block + Copy Button];
    E1 -- Downloads --> E1c[Download Buttons: TXT, SRT, JSON];

    A --> F[Error Display Panel (If Errors Occur)];

    %% Styling for clarity
    classDef card fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef newComp fill:#e6ffed,stroke:#28a745,stroke-width:2px;
    classDef enhanceComp fill:#ffe6e6,stroke:#dc3545,stroke-width:2px;

    class B,D,E,F card;
    class B1,D1,E1,E1a,E1b,E1c newComp;
    class C enhanceComp;
```

## 8. Next Steps for Development Team

1.  **Review this plan.**
2.  **Component Breakdown & Task Creation:** Decompose the proposed components and enhancements into smaller development tasks.
3.  **Backend Liaison:** Confirm backend capabilities for providing speaker diarization, different download formats, and any new SSE event types required.
4.  **Iterative Implementation:**
    *   Start with `ProcessingOptionsSelector`.
    *   Enhance progress display and `TranscriptionJobSummary`.
    *   Develop the `CompletedTranscriptionView` with its internal tabs.
    *   Consider `TranscriptionHistory` as a follow-up.
5.  **Testing:** Thoroughly test UI interactions, SSE updates, and results display.

This plan provides a comprehensive guide for the development team to enhance the "Transcribe" page, aligning with the project's overall UI/UX goals.