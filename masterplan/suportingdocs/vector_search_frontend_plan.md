# Frontend Implementation Plan: Vector Search Page Enhancements

**Overall Goal:** Implement a two-column layout for the Vector Search page, featuring a comprehensive filter panel and an enhanced results display area, ensuring tight integration with backend search capabilities.

**Legend for Backend Alignment:**
*   🟢 **Directly Supported:** Backend has clear parameters/fields for this.
*   🟡 **Partially Supported/Indirect:** Backend has related fields, but direct filtering/control might require frontend logic or minor backend adaptation.
*   🔴 **Not Directly Supported:** Requires significant client-side logic or a dedicated backend enhancement.

---

## Phase 1: Core Structure and Search Parameter Integration

**Sub-task 1.1: Implement Two-Column Layout**
*   **Description:** Establish the main page structure with a left-hand filter panel (fixed or collapsible) and a right-hand results area.
*   **Key `shadcn/ui` Components:** CSS Grid/Flexbox, [`Resizable`](https://ui.shadcn.com/docs/components/resizable), [`Card`](src/components/ui/card.jsx:1).
*   **Dependencies:** None.
*   **Backend Alignment:** N/A.
*   **Refactoring Notes:** Foundational change to [`src/app/vector-search/page.js`](src/app/vector-search/page.js).

**Sub-task 1.2: Refine Search Input and Parameter Controls**
*   **Description:** Integrate existing search input and parameter accordion into the new layout. Improve UI clarity for parameter descriptions.
*   **Key `shadcn/ui` Components:** [`Input`](src/components/ui/input.jsx:1), [`Button`](src/components/ui/button.jsx:1), [`Accordion`](src/components/ui/accordion.jsx:1), [`Slider`](src/components/ui/slider.jsx:1), [`Label`](src/components/ui/label.jsx:1), [`Select`](src/components/ui/select.jsx:1), [`Switch`](src/components/ui/switch.jsx:1).
*   **Dependencies:** Sub-task 1.1.
*   **Backend Alignment:** 🟢 Maps to `query`, tier-specific parameters (`similarity_threshold`, `content_weight`, `max_results`), `preset`, and `run_analysis` in `SearchParameters.update_from_frontend` ([`backend/app/psearchworking.py:611`](backend/app/psearchworking.py:611)).
*   **Refactoring Notes:** Adapt existing parameter logic in [`src/app/vector-search/page.js`](src/app/vector-search/page.js).

---

## Phase 2: Filter Panel Implementation

**Sub-task 2.1: Filter Panel Shell**
*   **Description:** Create the container for the filter panel.
*   **Key `shadcn/ui` Components:** [`Card`](src/components/ui/card.jsx:1), [`ScrollArea`](src/components/ui/scroll-area.jsx:1).
*   **Dependencies:** Sub-task 1.1.
*   **Backend Alignment:** N/A.
*   **Refactoring Notes:** New component structure.

**Sub-task 2.2: "Document Type" Filter**
*   **Description:** Implement filter for "Document Type" (e.g., Transcript, Webpage).
*   **Key `shadcn/ui` Components:** [`Checkbox`](src/components/ui/checkbox.jsx:1), [`Label`](src/components/ui/label.jsx:1).
*   **Dependencies:** Sub-task 2.1.
*   **Backend Alignment:** 🟡 `SearchResult.content_type` ([`backend/app/psearchworking.py:310`](backend/app/psearchworking.py:310)) exists. 🔴 Direct backend filtering not supported; likely client-side.
*   **Refactoring Notes:** New filter component and state management.

**Sub-task 2.3: "Source" Filter**
*   **Description:** Implement filter for "Source" (e.g., `video_transcriptions`, `document_embeddings`).
*   **Key `shadcn/ui` Components:** [`Checkbox`](src/components/ui/checkbox.jsx:1), [`Label`](src/components/ui/label.jsx:1).
*   **Dependencies:** Sub-task 2.1.
*   **Backend Alignment:** 🟡 `SearchResult.source` ([`backend/app/psearchworking.py:298`](backend/app/psearchworking.py:298)) exists. 🔴 Direct backend filtering not supported; likely client-side.
*   **Refactoring Notes:** New filter component and state management.

**Sub-task 2.4: "Score Range" Filter**
*   **Description:** Implement filter for similarity score range.
*   **Key `shadcn/ui` Components:** [`Slider`](src/components/ui/slider.jsx:1) (range), [`Label`](src/components/ui/label.jsx:1).
*   **Dependencies:** Sub-task 2.1.
*   **Backend Alignment:** 🟢 Can partially map to `similarity_threshold` per tier. 🟡 Full range filtering likely client-side.
*   **Refactoring Notes:** New filter component. Interaction with backend thresholds needs careful design.

**Sub-task 2.5: "Date Range" Filter**
*   **Description:** Implement filter for a date range.
*   **Key `shadcn/ui` Components:** [`DatePicker`](https://ui.shadcn.com/docs/components/date-picker), [`Label`](src/components/ui/label.jsx:1).
*   **Dependencies:** Sub-task 2.1.
*   **Backend Alignment:** 🔴 No standardized date field in `SearchResult` ([`backend/app/psearchworking.py:292`](backend/app/psearchworking.py:292)). Almost certainly client-side unless backend is enhanced.
*   **Refactoring Notes:** New filter component.

---

## Phase 3: Active Filters and Results Area Enhancements

**Sub-task 3.1: Active Filter Display**
*   **Description:** Display currently applied filters with options to remove.
*   **Key `shadcn/ui` Components:** [`Badge`](https://ui.shadcn.com/docs/components/badge), [`Button`](src/components/ui/button.jsx:1).
*   **Dependencies:** Sub-tasks 2.2, 2.3, 2.4, 2.5.
*   **Backend Alignment:** N/A.
*   **Refactoring Notes:** New component.

**Sub-task 3.2: Results Area Shell and View Switcher**
*   **Description:** Create results container with "Table View" / "Card View" switcher.
*   **Key `shadcn/ui` Components:** [`Tabs`](src/components/ui/tabs.jsx:1).
*   **Dependencies:** Sub-task 1.1.
*   **Backend Alignment:** N/A.
*   **Refactoring Notes:** Structures conditional rendering of [`SearchResultsTable.jsx`](src/components/search/SearchResultsTable.jsx:1) and `SearchResultCard` mapping.

**Sub-task 3.3: Global Sort Control**
*   **Description:** Implement dropdown to sort results (Relevance, Date, Title).
*   **Key `shadcn/ui` Components:** [`Select`](src/components/ui/select.jsx:1).
*   **Dependencies:** Sub-task 3.2.
*   **Backend Alignment:** 🟡 Sorting by `similarity` is direct. 🔴 Others (Title, Date) are client-side.
*   **Refactoring Notes:** New component; sorting logic on `results` array.

**Sub-task 3.4: Pagination / Load More**
*   **Description:** Implement pagination or "Load More" for results.
*   **Key `shadcn/ui` Components:** [`Pagination`](https://ui.shadcn.com/docs/components/pagination), [`Button`](src/components/ui/button.jsx:1).
*   **Dependencies:** Sub-task 3.2.
*   **Backend Alignment:** 🟡 Backend `max_results` controls initial fetch. 🔴 True server-side pagination not directly supported by current SSE. Client-side pagination on a larger fetched set is recommended.
*   **Refactoring Notes:** Significant logic change for results display.

**Sub-task 3.5: Enhanced `SearchResultCard` Component**
*   **Description:** Refactor [`src/components/search/SearchResultCard.jsx`](src/components/search/SearchResultCard.jsx:1) to display all relevant fields from `SearchResult.to_dict()` ([`backend/app/psearchworking.py:445`](backend/app/psearchworking.py:445)).
*   **Key `shadcn/ui` Components:** [`Card`](src/components/ui/card.jsx:1), [`Badge`](https://ui.shadcn.com/docs/components/badge).
*   **Dependencies:** Sub-task 3.2.
*   **Backend Alignment:** 🟢 Directly maps to `SearchResult.to_dict()` fields.
*   **Refactoring Notes:** Major refactor of [`src/components/search/SearchResultCard.jsx`](src/components/search/SearchResultCard.jsx:1).

**Sub-task 3.6: Enhanced `SearchResultsTable` Component**
*   **Description:** Refactor [`src/components/search/SearchResultsTable.jsx`](src/components/search/SearchResultsTable.jsx:1) to include key `SearchResult` fields.
*   **Key `shadcn/ui` Components:** [`Table`](src/components/ui/table.jsx:1).
*   **Dependencies:** Sub-task 3.2.
*   **Backend Alignment:** 🟢 Directly maps to `SearchResult.to_dict()` fields.
*   **Refactoring Notes:** Major refactor of [`src/components/search/SearchResultsTable.jsx`](src/components/search/SearchResultsTable.jsx:1).

**Sub-task 3.7: Integration of `AnalysisDisplay`**
*   **Description:** Integrate [`src/components/search/AnalysisDisplay.jsx`](src/components/search/AnalysisDisplay.jsx:1) into the new results layout.
*   **Key `shadcn/ui` Components:** [`TabsContent`](src/components/ui/tabs.jsx:1), [`Accordion`](src/components/ui/accordion.jsx:1).
*   **Dependencies:** Sub-task 3.2.
*   **Backend Alignment:** 🟢 Displays fetched analysis strings.
*   **Refactoring Notes:** Layout integration for [`AnalysisDisplay.jsx`](src/components/search/AnalysisDisplay.jsx:1).

---

## Phase 4: State Management and API Integration

**Sub-task 4.1: Centralized State Management for Filters**
*   **Description:** Implement state in [`src/app/vector-search/page.js`](src/app/vector-search/page.js) for all new filters.
*   **Key `shadcn/ui` Components:** N/A (React state).
*   **Dependencies:** Sub-tasks 2.2, 2.3, 2.4, 2.5.
*   **Backend Alignment:** N/A.
*   **Refactoring Notes:** New state variables in [`src/app/vector-search/page.js`](src/app/vector-search/page.js).

**Sub-task 4.2: Apply Filters to Results**
*   **Description:** Implement client-side logic to filter `results` array based on active filters.
*   **Key `shadcn/ui` Components:** N/A.
*   **Dependencies:** Sub-task 4.1.
*   **Backend Alignment:** Client-side handling for filters marked 🟡 or 🔴.
*   **Refactoring Notes:** New filtering functions in [`src/app/vector-search/page.js`](src/app/vector-search/page.js).

**Sub-task 4.3: API Call Adjustments for Score Range (if applicable)**
*   **Description:** Modify `handleSearch` if "Score Range" filter influences backend `similarity_thresholds`.
*   **Key `shadcn/ui` Components:** N/A.
*   **Dependencies:** Sub-task 2.4.
*   **Backend Alignment:** 🟢 (If mapping to backend thresholds).
*   **Refactoring Notes:** Modification to `handleSearch` in [`src/app/vector-search/page.js`](src/app/vector-search/page.js).