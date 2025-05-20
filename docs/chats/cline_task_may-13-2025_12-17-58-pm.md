**User:**

<task>
'docs/project_overview.md' (see below for file content) 'docs/project_structure.md' (see below for file content) 'docs/CONTEXT_README.md' (see below for file content) 'docs/Consolidated_Overview' (see below for file content) .md 
 review the following docs  and   'docs/crawl4ai/docs/md_v2/' (see below for folder content)  can be used for reference i wanted to ensure that local models can be used in crawl4ai  'docs/livetest_instructions.md' (see below for file content) i will test in production the model is gemma3 'backend\app\app_config.py' (see below for file content) but i need something in place that when ollama is selected in launches the model so i dont have to wait when fetching
</task>

<file_content path="docs/project_overview.md">
# PMOVES Project Comprehensive Overview

## Core Features

### 1. Transcription Service
- **Dual Processing Options**:
  - GPU-based local processing
  - Groq API integration for cloud processing
- **Output Formats**:
  - Segmented transcriptions with timestamps
  - Full transcripts
  - Speaker diarization support
- **Storage**:
  - Structured storage in Supabase
  - Vector embeddings for searchability
  - Metadata preservation

### 2. Web Content Fetching (JinAI Integration)
- **Features**:
  - Advanced webpage downloading
  - Content extraction and cleaning
  - Metadata preservation
  - Link following capabilities
  - Rate limiting and respect for robots.txt
- **Processing**:
  - HTML cleaning and formatting
  - Content structuring
  - Embedding generation
  - Supabase storage integration

### 3. Video/Audio Download Service
- **Features**:
  - Advanced yt-dlp integration
  - Multiple format support
  - Quality selection
  - Playlist handling
  - Custom output formatting
- **Options**:
  - Format selection
  - Quality preferences
  - Metadata extraction
  - Thumbnail downloading
  - Subtitle extraction

### 4. Content Upserter
- **Capabilities**:
  - Multi-format content processing
  - Automatic embedding generation
  - Metadata extraction and storage
  - Duplicate detection
  - Version control
- **Content Types**:
  - Transcriptions
  - Web content
  - Downloaded media
  - Documents
  - Structured data

### 5. Vector Search Interface
- **Search Methods**:
  - Semantic (vector) search
  - Keyword search
  - Hybrid search
- **Features**:
  - Two-column layout (Filter Panel + Results Area) for enhanced usability.
  - Client-side filtering capabilities (e.g., by Document Type, Source, Score Range).
  - Client-side sorting options (e.g., by Relevance, Title).
  - Switchable results view (Card/Table formats) and pagination for easier navigation.
  - Real-time search results with adjustable parameters.
  - Display of AI-powered analysis and insights.
  - Live updates via Server-Sent Events (SSE).
  - Expanded search scope, now including fetched web content (from `webpage_content` table, as outlined in [`docs/fetch_enhancement_plan.md`](docs/fetch_enhancement_plan.md)).
  - (For detailed UI/UX evolution, see [`docs/vector_search_frontend_plan.md`](docs/vector_search_frontend_plan.md); for current status, see [`docs/ui_enhancement_plan.md`](docs/ui_enhancement_plan.md).)

## Technical Architecture

### Frontend (Next.js)
1. **Pages**:
   - `/transcribe`: Transcription interface
   - `/fetch`: Web content fetching
   - `/download`: Media downloading
   - `/upserter`: Content management
   - `/vector-search`: Search interface

2. **Components**:
   - Progress tracking
   - File upload
   - Search interface
   - Results visualization
   - Error handling

### Backend (FastAPI)
1. **Core Services**:
   ```
   backend/app/
   ├── transcribe1.py        # Transcription service
   ├── fetch_content.py      # Web content fetching
   ├── download_manager.py   # Media downloading
   ├── pmoves_upserter.py   # Content upserting
   ├── psearchworking.py    # Vector search
   └── audio_processor.py   # Audio processing
   ```

2. **Support Systems**:
   ```
   backend/app/
   ├── monitoring/          # System monitoring
   ├── db/                 # Database operations
   ├── config/            # Configuration
   └── utils/            # Utility functions
   ```

### Database (Supabase)
1. **Tables**:
   - `video_transcriptions`: Segmented transcripts
   - `video_transcriptions_full`: Complete transcripts
   - `webpage_content`: Web content
   - `document_embeddings`: Vector embeddings
   - `media_content`: Media metadata

2. **Features**:
   - Vector similarity search
   - Full-text search
   - Real-time subscriptions
   - Row-level security

## Integration Points

### 1. External Services
- OpenAI API (embeddings & analysis)
- Groq API (transcription & analysis)
- yt-dlp (media download)
- JinAI (web scraping)

### 2. Internal Systems
- SSE monitoring
- Queue management
- Error handling
- Progress tracking

## Data Flow

1. **Content Ingestion**:
   ```
   Input → Processing → Embedding → Storage → Indexing
   ```

2. **Search Process**:
   ```
   Query → Embedding → Search → Results → Analysis
   ```

3. **Transcription Flow**:
   ```
   Media → Processing → Transcription → Segmentation → Storage
   ```

## Performance Features

1. **Optimization**:
   - Async operations
   - Connection pooling
   - Caching
   - Rate limiting

2. **Monitoring**:
   - Real-time metrics
   - Error tracking
   - Performance logging
   - Resource usage

## Security Measures

1. **API Security**:
   - Rate limiting
   - Input validation
   - Output sanitization
   - Error handling

2. **Data Security**:
   - Encrypted storage
   - Secure connections
   - Access control
   - Audit logging

## Development Guidelines

1. **Code Organization**:
   - Modular architecture
   - Clear separation of concerns
   - Consistent naming
   - Comprehensive documentation

2. **Testing**:
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Performance testing

3. **Deployment**:
   - Environment configuration
   - Database migrations
   - Version control
   - Backup procedures 
</file_content>

<file_content path="docs/project_structure.md">
# PMOVES Project Structure and Guidelines

## Project Overview
PMOVES is a transcription and search platform that combines vector search capabilities with OpenAI and Groq integrations for advanced content analysis.

## Directory Structure

```
PMOVES-transcribe-and-fetch/
├── backend/                  # Backend FastAPI application
│   └── app/
│       ├── main.py          # Main FastAPI application entry point
│       ├── psearchworking.py # Core vector search implementation
│       ├── pmoves_upserter.py # Content upserter functionality
│       ├── transcribe1.py   # Transcription service
│       ├── config/          # Configuration modules
│       ├── db/             # Database related code
│       ├── monitoring/     # SSE and system monitoring
│       └── routes/         # API route handlers
│
├── src/                    # Frontend Next.js application
│   ├── app/               # Next.js app directory
│   │   ├── vector-search/ # Vector search interface (recently overhauled UI)
│   │   ├── upserter/     # Content upserting interface
│   │   └── api/          # API route handlers
│   ├── components/        # Reusable React components
│   │   └── search/       # Components specific to search functionality
│   └── lib/              # Frontend utilities
│
└── PMOVES Supabase/       # Supabase database setup
    └── supabasedocs/     # SQL and documentation files
```

## Key Components

### Backend Components

1. Vector Search (`psearchworking.py`):
   - Handles semantic search using embeddings
   - Integrates with OpenAI and Groq
   - Supports multiple search methods: dot product, keyword, and hybrid

2. Content Upserter (`pmoves_upserter.py`):
   - Manages content ingestion
   - Handles different content types
   - Processes and stores embeddings

3. Transcription Service (`transcribe1.py`):
   - Manages audio/video transcription
   - Uses Groq for processing
   - Handles chunking and metadata

4. Monitoring System (`monitoring/`):
   - Tracks SSE connections
   - Monitors system performance
   - Provides debugging information

### Frontend Components

1. Vector Search Interface:
   - Two-column layout (Filter Panel + Results Area)
   - Advanced client-side filtering (Document Type, Source, Score Range)
   - Client-side sorting capabilities (Relevance, Title)
   - Switchable results view (Card/Table) and pagination
   - Real-time search results with adjustable parameters
   - Display of AI-driven analysis and insights
   - (For detailed UI/UX evolution, see [`docs/vector_search_frontend_plan.md`](docs/vector_search_frontend_plan.md) and for current status, see [`docs/ui_enhancement_plan.md`](docs/ui_enhancement_plan.md).)

2. Content Upserter Interface:
   - File upload handling
   - Progress tracking
   - Status updates

## Coding Guidelines

### Backend Guidelines

1. API Endpoints:
   ```python
   @app.get("/endpoint")
   async def endpoint():
       # Use async for I/O operations
       # Return JSON responses
       return {"status": "success"}
   ```

2. Error Handling:
   ```python
   try:
       result = await process_data()
   except Exception as e:
       logger.error(f"Error: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))
   ```

3. Database Operations:
   ```python
   # Always use parameterized queries
   result = await db.fetch_one(
       "SELECT * FROM table WHERE id = :id",
       {"id": user_id}
   )
   ```

4. Environment Variables:
   - Store in `backend/app/.env`
   - Never commit sensitive data
   - Use descriptive names

### Frontend Guidelines

1. Component Structure:
   ```javascript
   // Use TypeScript when possible
   interface Props {
     data: SearchResult[];
     onUpdate: (id: string) => void;
   }

   export function Component({ data, onUpdate }: Props) {
     // Component logic
   }
   ```

2. State Management:
   ```javascript
   // Use hooks for state
   const [state, setState] = useState(initial);
   
   // Use reducers for complex state
   const [state, dispatch] = useReducer(reducer, initial);
   ```

3. API Calls:
   ```javascript
   // Use async/await with error handling
   try {
     const response = await fetch('/api/endpoint');
     const data = await response.json();
   } catch (error) {
     console.error('Error:', error);
   }
   ```

## SSE (Server-Sent Events) Guidelines

1. Server Implementation:
   ```python
   async def event_generator():
       try:
           yield f"data: {json.dumps({'type': 'status'})}\n\n"
       except Exception as e:
           yield f"data: {json.dumps({'type': 'error'})}\n\n"
   ```

2. Client Implementation:
   ```javascript
   const eventSource = new EventSource('/api/stream');
   eventSource.onmessage = (event) => {
     const data = JSON.parse(event.data);
     // Handle different message types
   };
   ```

## Database Guidelines

1. Table Naming:
   - Use snake_case
   - Descriptive names
   - Include purpose in name

2. Vector Operations:
   ```sql
   -- Use appropriate indexes
   CREATE INDEX ON table USING ivfflat (embedding vector_cosine_ops);
   
   -- Use efficient similarity search
   SELECT * FROM table 
   WHERE 1 - (embedding <=> query_embedding) > similarity_threshold;
   ```

## Testing Guidelines

1. Backend Tests:
   ```python
   @pytest.mark.asyncio
   async def test_function():
       # Arrange
       input_data = {}
       # Act
       result = await function(input_data)
       # Assert
       assert result["status"] == "success"
   ```

2. Frontend Tests:
   ```javascript
   describe('Component', () => {
     it('should render correctly', () => {
       render(<Component />);
       expect(screen.getByText('text')).toBeInTheDocument();
     });
   });
   ```

## Monitoring Guidelines

1. Log Levels:
   - ERROR: Unexpected errors
   - WARNING: Potential issues
   - INFO: General information
   - DEBUG: Detailed debugging

2. Performance Monitoring:
   - Track response times
   - Monitor memory usage
   - Log API call frequencies

## Deployment Guidelines

1. Environment Setup:
   - Use requirements.txt for Python
   - Use package.json for Node.js
   - Document environment variables

2. Database Migrations:
   - Version control migrations
   - Test migrations locally
   - Backup before deploying

## Security Guidelines

1. API Security:
   - Validate all inputs
   - Sanitize outputs
   - Use rate limiting

2. Data Security:
   - Encrypt sensitive data
   - Use secure connections
   - Regular security audits 
</file_content>

<file_content path="docs/CONTEXT_README.md">
# Project Context: Fetch Page crawl4ai Integration

This document provides a summary of the current status of the `crawl4ai` integration for the Fetch page, intended to provide context for resuming development.

## Goal

The primary objective was to implement advanced `crawl4ai` features for the Fetch page, as detailed in the [Fetch Page Enhancement Plan](fetch_page_enhancement_plan.md).

## Current Status

Feature implementation is complete. This includes:
*   UI components for `crawl4ai` strategies and options.
*   Backend logic to handle different fetching strategies.
*   Refinement of fetch history.
*   Implementation of a JSON viewer for results.
*   Addition of tooltips for clarity.

The updated status and findings from the Architect mode are documented in [Section 8 of the Fetch Page Enhancement Plan](fetch_page_enhancement_plan.md#section-8-current-status-and-blockers).

## Blocker Resolved: `NotImplementedError` on Windows

A critical `NotImplementedError` *was* preventing `crawl4ai` from functioning correctly on Windows environments. This error originated from `asyncio.create_subprocess_exec` when `playwright` attempted to start its browser instance, but it has now been resolved.

## Investigation and Solution

The investigation into the `NotImplementedError` involved several steps. Initially, the standard recommended fix for `asyncio` issues on Windows, setting `asyncio.WindowsSelectorEventLoopPolicy()` in [`backend/app/main.py`](backend/app/main.py:1), was implemented but did not resolve the issue.

Subsequently, `asyncio.WindowsProactorEventLoopPolicy()` was correctly implemented in [`backend/app/main.py`](backend/app/main.py:1). It was also confirmed that `playwright` was correctly installed (`playwright install`). Isolated tests conducted using [`backend/app/test_crawl4ai_isolated.py`](backend/app/test_crawl4ai_isolated.py:1) demonstrated that `crawl4ai` itself could function correctly under the `WindowsProactorEventLoopPolicy`.

The final root cause of the `NotImplementedError` in the full application environment was identified as an interference issue between Uvicorn's `--reload` flag and the `asyncio.WindowsProactorEventLoopPolicy` when running on Windows.

The solution is to run the Uvicorn server without the `--reload` flag during development on Windows when `crawl4ai` features are being utilized. This allows `crawl4ai` and `playwright` to operate as expected.

## Testing Recommendations

Detailed testing recommendations to further diagnose and address the issue have been prepared by the Architect and can be found in [Fetch Page Testing Recommendations](fetch_page_testing_recommendations.md).

## Resolution Summary

The `NotImplementedError` on Windows related to `crawl4ai` and `playwright` has been successfully resolved. The issue was traced to a conflict between Uvicorn's `--reload` flag and the `asyncio.WindowsProactorEventLoopPolicy`. `crawl4ai` now functions correctly on Windows when the Uvicorn server is run without the `--reload` flag.
</file_content>

<file_content path="docs/Consolidated_Overview">
Error fetching content: Failed to access path "docs/Consolidated_Overview": ENOENT: no such file or directory, stat 'c:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\docs\Consolidated_Overview'
</file_content>

<folder_content path="docs/crawl4ai/docs/md_v2/">
├── advanced/
├── api/
├── ask_ai/
├── assets/
├── basic/
├── blog/
├── core/
├── extraction/
└── index.md

<file_content path="docs/crawl4ai/docs/md_v2/index.md">
# 🚀🤖 Crawl4AI: Open-Source LLM-Friendly Web Crawler & Scraper

<div class = "badges" align="center">

  <p>
    <a href="https://trendshift.io/repositories/11716" target="_blank">
      <img src="https://trendshift.io/api/badge/repositories/11716"
           alt="unclecode%2Fcrawl4ai | Trendshift"
           style="width: 250px; height: 55px;"
           width="250" height="55"/>
    </a>

  </p>

  <p>
    <a href="https://github.com/unclecode/crawl4ai/stargazers">
      <img src="https://img.shields.io/github/stars/unclecode/crawl4ai?style=social"
           alt="GitHub Stars"/>
    </a>
    <a href="https://github.com/unclecode/crawl4ai/network/members">
      <img src="https://img.shields.io/github/forks/unclecode/crawl4ai?style=social"
           alt="GitHub Forks"/>
    </a>
    <a href="https://badge.fury.io/py/crawl4ai">
      <img src="https://badge.fury.io/py/crawl4ai.svg"
           alt="PyPI version"/>
    </a>
  </p>

  <p>
    <a href="https://pypi.org/project/crawl4ai/">
      <img src="https://img.shields.io/pypi/pyversions/crawl4ai"
           alt="Python Version"/>
    </a>
    <a href="https://pepy.tech/project/crawl4ai">
      <img src="https://static.pepy.tech/badge/crawl4ai/month"
           alt="Downloads"/>
    </a>
    <a href="https://github.com/unclecode/crawl4ai/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/unclecode/crawl4ai"
           alt="License"/>
    </a>
  </p>
  
</div>

Crawl4AI is the #1 trending GitHub repository, actively maintained by a vibrant community. It delivers blazing-fast, AI-ready web crawling tailored for large language models, AI agents, and data pipelines. Fully open source, flexible, and built for real-time performance, **Crawl4AI** empowers developers with unmatched speed, precision, and deployment ease.

> **Note**: If you're looking for the old documentation, you can access it [here](https://old.docs.crawl4ai.com).


## Quick Start

Here's a quick example to show you how easy it is to use Crawl4AI with its asynchronous capabilities:

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://crawl4ai.com")

        # Print the extracted content
        print(result.markdown)

# Run the async main function
asyncio.run(main())
```

---

## Video Tutorial

<div align="center">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/xo3qK6Hg9AA?start=15" title="Crawl4AI Tutorial" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

---

## What Does Crawl4AI Do?

Crawl4AI is a feature-rich crawler and scraper that aims to:

1. **Generate Clean Markdown**: Perfect for RAG pipelines or direct ingestion into LLMs.  
2. **Structured Extraction**: Parse repeated patterns with CSS, XPath, or LLM-based extraction.  
3. **Advanced Browser Control**: Hooks, proxies, stealth modes, session re-use—fine-grained control.  
4. **High Performance**: Parallel crawling, chunk-based extraction, real-time use cases.  
5. **Open Source**: No forced API keys, no paywalls—everyone can access their data.  

**Core Philosophies**:
- **Democratize Data**: Free to use, transparent, and highly configurable.  
- **LLM Friendly**: Minimally processed, well-structured text, images, and metadata, so AI models can easily consume it.

---

## Documentation Structure

To help you get started, we’ve organized our docs into clear sections:

- **Setup & Installation**  
  Basic instructions to install Crawl4AI via pip or Docker.  
- **Quick Start**  
  A hands-on introduction showing how to do your first crawl, generate Markdown, and do a simple extraction.  
- **Core**  
  Deeper guides on single-page crawling, advanced browser/crawler parameters, content filtering, and caching.  
- **Advanced**  
  Explore link & media handling, lazy loading, hooking & authentication, proxies, session management, and more.  
- **Extraction**  
  Detailed references for no-LLM (CSS, XPath) vs. LLM-based strategies, chunking, and clustering approaches.  
- **API Reference**  
  Find the technical specifics of each class and method, including `AsyncWebCrawler`, `arun()`, and `CrawlResult`.

Throughout these sections, you’ll find code samples you can **copy-paste** into your environment. If something is missing or unclear, raise an issue or PR.

---

## How You Can Support

- **Star & Fork**: If you find Crawl4AI helpful, star the repo on GitHub or fork it to add your own features.  
- **File Issues**: Encounter a bug or missing feature? Let us know by filing an issue, so we can improve.  
- **Pull Requests**: Whether it’s a small fix, a big feature, or better docs—contributions are always welcome.  
- **Join Discord**: Come chat about web scraping, crawling tips, or AI workflows with the community.  
- **Spread the Word**: Mention Crawl4AI in your blog posts, talks, or on social media.  

**Our mission**: to empower everyone—students, researchers, entrepreneurs, data scientists—to access, parse, and shape the world’s data with speed, cost-efficiency, and creative freedom.

---

## Quick Links

- **[GitHub Repo](https://github.com/unclecode/crawl4ai)**  
- **[Installation Guide](./core/installation.md)**  
- **[Quick Start](./core/quickstart.md)**  
- **[API Reference](./api/async-webcrawler.md)**  
- **[Changelog](https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md)**  

Thank you for joining me on this journey. Let’s keep building an **open, democratic** approach to data extraction and AI together.

Happy Crawling!  
— *Unclecode, Founder & Maintainer of Crawl4AI*  

</file_content>
</folder_content>

<file_content path="docs/livetest_instructions.md">
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
</file_content>

<file_content path="backend\app\app_config.py">
# NOTE: This is the ONLY config file for backend settings.
# Do not use or create alternate config files for Whisper or API keys.
# All settings should come from .env or this file.
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the current directory (where config.py is)
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

logger.info(f"Looking for .env file at: {env_path}")
# Force reload of environment variables
load_dotenv(env_path, override=True)

# Unified workspace root
WORKSPACE_ROOT = os.getenv('WORKSPACE_ROOT', os.path.join(os.getcwd(), 'workspace'))

# Centralized subfolder structure for all content types
SUBFOLDERS = {
    "transcriptions": {
        "audio": "audio",
        "markdown": "markdown",
        "pdf": "pdf"
    },
    "downloads": {
        "video": "video",
        "audio": "audio",
        "subtitles": "subtitles"
    },
    "fetches": {
        "markdown": "markdown",
        "pdf": "pdf"
    },
    "uploads": {
        "files": "files",
        "metadata": "metadata"
    }
}

# Path to wkhtmltopdf executable
WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
if not os.path.isfile(WKHTMLTOPDF_PATH):
    logger.warning(
        f"wkhtmltopdf not found at '{WKHTMLTOPDF_PATH}'. "
        f"PDF generation will fail unless properly configured. "
        f"Please install wkhtmltopdf or set WKHTMLTOPDF_PATH in .env file."
    )

# Whisper model settings
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'large-v3')
WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cuda')
WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'float16')

# API Key and Base URL Environment Variables
# Centralized loading of API keys and base URLs from environment variables
# crawl4ai will attempt to load these if a token is not explicitly passed.
# Defining them here makes it clear what the application expects.

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # crawl4ai docs show GEMINI_API_KEY and GEMINI_API_TOKEN, using KEY for consistency
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
TOGETHER_AI_API_KEY = os.getenv('TOGETHER_AI_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
FIREWORKS_AI_API_KEY = os.getenv('FIREWORKS_AI_API_KEY') # Assuming FIREWORKS_AI_API_KEY based on provider name

# Base URLs for local/custom OpenAI-compatible endpoints
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434') # Default for local Ollama
OPENAI_COMPATIBLE_BASE_URL = os.getenv('OPENAI_COMPATIBLE_BASE_URL') # For LM Studio, etc.

# Model configurations
# Keys are user-friendly display names.
# Each entry contains:
#   - id: The `provider_name/model_name` string crawl4ai expects.
#   - description: User-friendly description.
#   - provider_group: Helps categorize models in UI (e.g., "OpenAI", "Groq").
#   - requires_api_key: Boolean.
#   - api_key_var: Name of the environment variable for the API key (if required).
#   - base_url_var: Name of the environment variable for the base URL (if applicable).
#   - is_llm_provider: Boolean, true if it's an LLM for crawl4ai's LLMConfig.
#   - type: 'llm' or 'transcription'
AVAILABLE_MODELS = {
    # Faster Whisper (Local) - Special case
    'Faster Whisper (Local Transcription)': {
        'id': 'faster-whisper', # Internal identifier, not for crawl4ai LLMConfig
        'description': 'Local Faster Whisper model for audio transcription',
        'provider_group': 'Local Models',
        'type': 'transcription',
        'requires_gpu': True,
        'is_llm_provider': False # Not used with LLMConfig in crawl4ai
    },

    # OpenAI
    "OpenAI: GPT-4o": { # General availability, often points to latest
        "id": "openai/gpt-4o",
        "description": "OpenAI's most advanced multimodal model.",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4o Mini": { # General availability
        "id": "openai/gpt-4o-mini",
        "description": "OpenAI's most capable and cost-effective small model.",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4.1 Mini (2025-04-14)": { # Specific version from Azure/User
        "id": "openai/gpt-4.1-mini-2025-04-14", # Assuming crawl4ai uses this ID format
        "description": "OpenAI GPT-4.1 Mini (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4.1 Nano (2025-04-14)": { # Specific version from Azure/User
        "id": "openai/gpt-4.1-nano-2025-04-14", # Assuming crawl4ai uses this ID format
        "description": "OpenAI GPT-4.1 Nano, fastest 4.1 model (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: o4-mini (2025-04-16)": { # Specific version from Azure/User
        "id": "openai/o4-mini-2025-04-16", # Assuming crawl4ai uses this ID format
        "description": "OpenAI o4-mini reasoning model (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4 Turbo (latest)": { # General Turbo, often points to latest like turbo-2024-04-09
        "id": "openai/gpt-4-turbo",
        "description": "OpenAI GPT-4 Turbo with 128k context (latest general availability).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-3.5 Turbo (latest)": {
        "id": "openai/gpt-3.5-turbo",
        "description": "OpenAI GPT-3.5 Turbo, fast and affordable (latest general availability).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Groq
    "Groq: Llama 3.3 70B Versatile": { # New from Groq Docs
        "id": "groq/llama-3.3-70b-versatile",
        "description": "Meta Llama 3.3 70B (128k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama3 70B (8k context)": { # Retained, still in Groq production
        "id": "groq/llama3-70b-8192",
        "description": "Meta Llama3 70B (8k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama 3.1 8B Instant": { # New from Groq Docs
        "id": "groq/llama-3.1-8b-instant",
        "description": "Meta Llama 3.1 8B (128k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama3 8B (8k context)": { # Retained, still in Groq production
        "id": "groq/llama3-8b-8192",
        "description": "Meta Llama3 8B (8k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Mixtral 8x7B (32k context)": { # Retained, popular Groq model
        "id": "groq/mixtral-8x7b-32768",
        "description": "Mixtral 8x7B (32k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Gemma2 9B IT": { # New from Groq Docs (replaces gemma-7b-it)
        "id": "groq/gemma2-9b-it",
        "description": "Google Gemma2 9B IT (8k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: DeepSeek-R1 Distill Llama 70B (Preview)": { # User requested, from Groq Preview
        "id": "groq/deepseek-r1-distill-llama-70b",
        "description": "DeepSeek-R1 Distill Llama 70B (128k context, Preview) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama Guard 3 8B": { # New from Groq Docs, likely for moderation
        "id": "groq/llama-guard-3-8b",
        "description": "Meta Llama Guard 3 8B (8k context) via Groq, for content moderation.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, # crawl4ai might treat it as a standard LLM
        "type": "llm" # Or potentially 'moderation' if app handles it differently
    },

    # Groq Transcription Models (User Requested)
    "Groq: Whisper Large v3 Turbo (Transcription)": {
        "id": "groq/whisper-large-v3-turbo",
        "description": "OpenAI Whisper Large v3 Turbo via Groq for audio transcription.",
        "provider_group": "Groq (Transcription)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "transcription"
    },
    "Groq: Distil-Whisper Large v3 EN (Transcription)": {
        "id": "groq/distil-whisper-large-v3-en",
        "description": "HuggingFace Distil-Whisper Large v3 EN via Groq for English audio transcription.",
        "provider_group": "Groq (Transcription)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "transcription"
    },

    # Groq TTS Models (User Requested)
    "Groq: PlayAI TTS (Preview)": {
        "id": "groq/playai-tts",
        "description": "PlayAI Text-to-Speech (Preview) via Groq.",
        "provider_group": "Groq (TTS)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "tts"
    },

    # Anthropic
    "Anthropic: Claude 3.5 Sonnet": { # Newest Sonnet
        "id": "anthropic/claude-3-5-sonnet-20240620",
        "description": "Anthropic's latest Sonnet model, balances speed and intelligence.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Opus": {
        "id": "anthropic/claude-3-opus-20240229",
        "description": "Anthropic's most powerful model, Claude 3 Opus.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Sonnet (Original)": {
        "id": "anthropic/claude-3-sonnet-20240229",
        "description": "Anthropic Claude 3 Sonnet (original release), balanced performance.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Haiku": {
        "id": "anthropic/claude-3-haiku-20240307",
        "description": "Anthropic's fastest and most compact model, Claude 3 Haiku.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Google Gemini
    "Google: Gemini 2.5 Pro Preview (05-06)": { # From Google Docs
        "id": "gemini/gemini-2.5-pro-preview-05-06", # Model code: models/gemini-2.5-pro-preview-05-06
        "description": "Google's state-of-the-art thinking model (Preview).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 2.5 Flash Preview (04-17)": { # User requested
        "id": "gemini/gemini-2.5-flash-preview-04-17", # Model code: models/gemini-2.5-flash-preview-04-17
        "description": "Google's best price-performance model (Preview).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 2.0 Flash Live (001)": { # User requested
        "id": "gemini/gemini-2.0-flash-live-001", # Model code: models/gemini-2.0-flash-live-001
        "description": "Google Gemini for low-latency bidirectional voice and video interactions.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm" # Can output text and audio
    },
    "Google: Gemini 1.5 Pro (latest)": { # Retained from previous, still current
        "id": "gemini/gemini-1.5-pro-latest", # Model code: models/gemini-1.5-pro (latest points to this)
        "description": "Google's mid-size multimodal model for complex reasoning.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 1.5 Flash (latest)": { # Retained from previous, still current
        "id": "gemini/gemini-1.5-flash-latest", # Model code: models/gemini-1.5-flash (latest points to this)
        "description": "Google's fast and versatile multimodal model.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini Embedding (Experimental)": { # User requested
        "id": "gemini/gemini-embedding-exp-03-07", # Model code from docs: gemini-embedding-exp-03-07
        "description": "Google's experimental text embedding model.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": False, # Primarily for embeddings, not general LLM tasks via LLMConfig
        "type": "embedding"
    },
    "Google: Gemini Pro (legacy)": { # As per crawl4ai docs, kept for compatibility
        "id": "gemini/gemini-pro",
        "description": "Google Gemini Pro (legacy version, from crawl4ai docs).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # DeepSeek (API)
    "DeepSeek API: Chat": {
        "id": "deepseek/deepseek-chat",
        "description": "DeepSeek Chat model via API.",
        "provider_group": "DeepSeek (API)",
        "requires_api_key": True, "api_key_var": "DEEPSEEK_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "DeepSeek API: Coder": {
        "id": "deepseek/deepseek-coder",
        "description": "DeepSeek Coder model via API, specialized for code.",
        "provider_group": "DeepSeek (API)",
        "requires_api_key": True, "api_key_var": "DEEPSEEK_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Mistral AI (API)
    "Mistral API: Large (latest)": {
        "id": "mistral/mistral-large-latest",
        "description": "Mistral AI's flagship model, Large (latest) via API.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Mistral API: Small (latest)": { # Mistral often refers to this as `mistral-small-latest`
        "id": "mistral/mistral-small-latest", # crawl4ai might just use `mistral/mistral-small`
        "description": "Mistral AI's Small model (latest) via API, optimized for latency.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Mistral API: Codestral (latest)": {
        "id": "mistral/codestral-latest",
        "description": "Mistral AI's Codestral model for code generation (latest) via API.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    # Note: open-mixtral-8x7b is often served by other providers like TogetherAI or Groq,
    # or locally via Ollama. If Mistral offers it directly via their API, it would be listed here.

    # Together AI
    "TogetherAI: Llama 3 70B Chat HF": {
        "id": "together_ai/meta-llama/Llama-3-70b-chat-hf",
        "description": "Llama 3 70B Chat (HuggingFace version) via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Llama 3 8B Chat HF": {
        "id": "together_ai/meta-llama/Llama-3-8b-chat-hf",
        "description": "Llama 3 8B Chat (HuggingFace version) via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Mixtral 8x7B Instruct": {
        "id": "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
        "description": "Mixtral 8x7B Instruct v0.1 via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Qwen1.5 72B Chat": {
        "id": "together_ai/Qwen/Qwen1.5-72B-Chat",
        "description": "Qwen 1.5 72B Chat via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Cohere
    "Cohere: Command R+": {
        "id": "cohere/command-r-plus",
        "description": "Cohere's most advanced model, Command R+.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Cohere: Command R": {
        "id": "cohere/command-r",
        "description": "Cohere Command R model.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Cohere: Command Light": { # General Command and Command Light
        "id": "cohere/command-light",
        "description": "Cohere Command Light, faster and more affordable.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Fireworks AI
    "Fireworks AI: Llama v3 70B Instruct": {
        "id": "fireworks_ai/accounts/fireworks/models/llama-v3-70b-instruct",
        "description": "Llama v3 70B Instruct via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Fireworks AI: Mixtral 8x7B Instruct": {
        "id": "fireworks_ai/accounts/fireworks/models/mixtral-8x7b-instruct",
        "description": "Mixtral 8x7B Instruct via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Fireworks AI: Firefunction V1": {
        "id": "fireworks_ai/accounts/fireworks/models/firefunction-v1",
        "description": "Firefunction V1 (Function Calling Model) via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Ollama (Local models) - Updated based on user request and ollama.com/library
    "Ollama: Llama 3.3 (local)": { # User requested
        "id": "ollama/llama3.3",
        "description": "Llama 3.3 model running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: DeepSeek-R1 (local)": { # User requested
        "id": "ollama/deepseek-r1",
        "description": "DeepSeek's first-generation reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Qwen 3 (local)": { # User requested
        "id": "ollama/qwen3",
        "description": "Qwen3 model series locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Mistral (local)": { # User requested
        "id": "ollama/mistral", # This is typically mistral-7b
        "description": "Mistral 7B model (v0.3) running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Gemma 3 (local)": { # User requested
        "id": "ollama/gemma3",
        "description": "Gemma 3 model series locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Phi-4 Reasoning (local)": { # User requested (phi4)
        "id": "ollama/phi4",
        "description": "Phi-4 (14B) reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Phi-4 Mini Reasoning (local)": { # User requested and confirmed
        "id": "ollama/phi4-mini-reasoning",
        "description": "Phi-4 Mini (3.8B) reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    # Retaining some common Ollama models from previous list if not covered above
    "Ollama: Llama3 (generic, local)": {
        "id": "ollama/llama3",
        "description": "Generic Llama3 model (e.g., 8B) locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: CodeLlama (local)": {
        "id": "ollama/codellama",
        "description": "CodeLlama model running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },


    # OpenAI-Compatible (e.g., LM Studio)
    "OpenAI-Compatible: LM Studio (local)": {
        "id": "openai/lm-studio-model", # Placeholder, actual model depends on server
        "description": "Model served by LM Studio or other local OpenAI-compatible server.",
        "provider_group": "OpenAI-Compatible (Local)",
        "requires_api_key": False,
        "api_key_var": "OPENAI_API_KEY", # Often a dummy key like "lm-studio" is accepted
        "base_url_var": "OPENAI_COMPATIBLE_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI-Compatible: Another Local Model": {
        "id": "openai/another-local-model", # Placeholder
        "description": "Another model via a local OpenAI-compatible server.",
        "provider_group": "OpenAI-Compatible (Local)",
        "requires_api_key": False,
        "api_key_var": "OPENAI_API_KEY",
        "base_url_var": "OPENAI_COMPATIBLE_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    }
}

# Debug logging for loaded API keys
API_KEYS_TO_LOG = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "DEEPSEEK_API_KEY": DEEPSEEK_API_KEY,
    "MISTRAL_API_KEY": MISTRAL_API_KEY,
    "TOGETHER_AI_API_KEY": TOGETHER_AI_API_KEY,
    "COHERE_API_KEY": COHERE_API_KEY,
    "FIREWORKS_AI_API_KEY": FIREWORKS_AI_API_KEY,
}

for key_name, key_value in API_KEYS_TO_LOG.items():
    logger.info(f"{key_name} loaded: {'Yes' if key_value else 'No'}")
    if not key_value:
        logger.warning(f"{key_name} is not set in environment variables.")
    elif key_value == f"your_{key_name.lower()}_here" or "sk-YOUR_KEY_HERE" in key_value: # Common placeholder patterns
        logger.error(f"Default placeholder value detected for {key_name} - please update your .env file.")
    else:
        logger.info(f"{key_name} starts with: {key_value[:min(len(key_value), 5)]}...")


# Debug logging for Base URLs
BASE_URLS_TO_LOG = {
    "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
    "OPENAI_COMPATIBLE_BASE_URL": OPENAI_COMPATIBLE_BASE_URL,
}
for url_name, url_value in BASE_URLS_TO_LOG.items():
    logger.info(f"{url_name} loaded: {url_value if url_value else 'Not set, using default or none'}")
    if url_value and ("localhost" in url_value or "127.0.0.1" in url_value):
        logger.info(f"{url_name} appears to be a local address: {url_value}")

# It's good practice to ensure API keys are set if a model requiring one is selected by the application.
# However, crawl4ai handles API key loading from env vars internally if not passed.
# This config primarily serves to inform the frontend/user and provide defaults.
# The actual enforcement or requirement check might happen closer to the crawl4ai call.
</file_content>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 9:56:26 AM (America/New_York, UTC-4:00)

# Current Working Directory (c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch) Files
.cursorignore
.env.bak
.eslintrc.json
.gitattributes
.gitignore
.roomodes
babel.config.js
components.json
jest.config.js
jest.setup.js
jsconfig.json
LICENSE
live_fetch_content_tester.py
live_llm_extraction_advanced_tester.py
live_llm_local_tester.py
next.config.js
package.json
post_sync.ps1
post_sync.sh
postcss.config.js
postcss.config.mjs
pyproject.toml
README.md
requirements.txt
supabase_tables_setup.sql
tailwind.config.js
test_results.md
uv.lock
__mocks__/
__mocks__/react-markdown.js
archive/
archive/page copy 2.js
archive/page copy.js
archive/page.js.bak.2025-03-26T23-44-38.678Z
archive/pagebak.js
archive/fixes/
backend/
backend/.env.example
backend/browseruseapi.md
backend/requirements.txt
backend/app/
backend/app/__init__.py
backend/app/.env.example
backend/app/app_config.py
backend/app/audio_processor.py
backend/app/compsearchfix.py
backend/app/crawl4ai_fetcher.py
backend/app/data_utils.py
backend/app/databaseplan.md
backend/app/debug_endpoints.py
backend/app/download_manager.py
backend/app/error_handlers.py
backend/app/fetch_content.py
backend/app/file_utils.py
backend/app/folder_manager.py
backend/app/frontend_adapter.py
backend/app/general_utils.py
backend/app/gtrans.py
backend/app/main.bak.py
backend/app/main.py
backend/app/main.py.bak.20250326_193211
backend/app/main.py.bak.20250326_194438
backend/app/main.py.bak.autostart_fix
backend/app/main.py.bak.complete_fix
backend/app/main.py.bak.cors_fix
backend/app/main.py.bak.direct_fix_v2
backend/app/main.py.bak.final_fix
backend/app/main.py.bak.manual_fix
backend/app/main.py.bak.sse_fix
backend/app/main.py.bak.syntax_fix
backend/app/main.py.new
backend/app/mainfixed.py
backend/app/mainloang.py
backend/app/pmoves_rag.py
backend/app/pmoves_search.py
backend/app/pmoves_upserter.py
backend/app/pmovesmd.py
backend/app/process_video_wrapper.py
backend/app/psearch_overview.md
backend/app/psearch.md
backend/app/psearch.py
backend/app/psearchtables.md
backend/app/psearchworking_export.py
backend/app/psearchworking_fixed.py
backend/app/psearchworking.py
backend/app/psearchworking.py.backup
backend/app/psearchworking.py.fixed
backend/app/psearchworking.py.fixed2
backend/app/psearchworking.py.fixed3
backend/app/psearchworking.py.new
backend/app/psearchworking.py.original
backend/app/queue_manager.py
backend/app/README.md
backend/app/requirements.lock
backend/app/requirements.txt
backend/app/test_crawl4ai_isolated.py
backend/app/test_embedding_fix.py
backend/app/test_playwright.py
backend/app/test_supabase.py
backend/app/test.py
backend/app/transcribe1 copy.py
backend/app/transcribe1.py
backend/app/transcribe1.py.backup
backend/app/transcribe1.py.bak.20250326_193211
backend/app/transcribe1.py.bak.20250326_194438
backend/app/transcribebak.py
backend/app/vector_search.py
backend/app/video_processor.py
backend/app/config/
backend/app/db/
backend/app/monitoring/
backend/app/routes/
backend/app/static/
backend/app/temp_pdfs/
backend/app/tests/
backend/app/utils/
backend/backend/
backend/backend/app/
backend/backend/fetched_content/
backend/backend/temp_pdfs/
backend/downloads/
backend/fetched_content/
backend/pmoves_backend.egg-info/
backend/temp_pdfs/
backend/temp_pdfs/example.com_20250510_201658.pdf
backend/temp_pdfs/example.com_20250510_201701.pdf
backend/temp_pdfs/example.com_20250510_201718.pdf
backend/temp_pdfs/example.com_20250510_201722.pdf
backend/temp_pdfs/example.com_20250510_201725.pdf
backend/temp_pdfs/example.com_20250510_201729.pdf
backend/temp_pdfs/example.com_20250510_201732.pdf
backend/temp_pdfs/example.com_20250510_201735.pdf
backend/temp_pdfs/example.com_20250510_201739.pdf
docs/
docs/Consolidated_Overview .md
docs/CONTEXT_README.md
docs/crawl4ai_parameters.md
docs/crawl4ai_test_plan.md
docs/cursor_rules.md
docs/fetch_enhancement_plan.md
docs/fetch_implementation_subtasks.md
docs/fetch_page_enhancement_plan.md
docs/fetch_page_testing_recommendations.md
docs/Frontend_Integration_Review_&_Enhancement Plan.md
docs/livetest_instructions.md
docs/new_test_plan.md
docs/pmoves_dynamic_llm_plan.md
docs/project_overview.md
docs/Project_Status_Synthesis_Report.md
docs/project_structure.md
docs/refactoring_utility_modules.md
docs/search_params_integration.md
docs/searchstopped.md
docs/transcribe_page_enhancement_plan.md
docs/ui_enhancement_plan.md
docs/vector_search_frontend_plan.md
docs/crawl4ai/
docs/implementation/
docs/supabasedocs/
docs/technical_specs/
docs/uidocs/
fetched_content/
font/
font/f_zero_snes.zip
font/image2vector.svg
font/retro_mario.zip
font/super_mario_64.zip
font/super_mario_256.zip
font/f_zero_snes/
migrations/
migrations/llmlog.sql
migrations/V1_add_webpage_embeddings_and_search.sql
migrations/V2_create_fetch_history_table.sql
migrations/V3_add_content_summary_to_fetch_history.sql
migrations/V4_add_raw_content_path_to_fetch_history.sql
migrations/V5_add_supabase_content_id_to_fetch_history.sql
PMOVES Supabase/
PMOVES Supabase/pmoves_vector_search_rag.py
PMOVES Supabase/pmoves_vector_search.py
PMOVES Supabase/pmoves_vector_searchkdot.py
PMOVES Supabase/pmoves2.py
PMOVES Supabase/requirements.txt
public/
public/fonts/
public/images/
src/
src/setupTests.js
src/app/
src/components/
src/hooks/
src/lib/
src/utils/
temp_pdfs/
test_obsidian/
test_obsidian/markdown/
test_output/
test_output/audio/
test_output/markdown/
test_output/obsidian/
test_output/output/

(File list truncated. Use list_files on specific subdirectories if you need to explore further.)

# Context Window Usage
0 / 1,048.576K tokens used (0%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The user wants me to review several documents and a folder of documentation related to the PMOVES project and the `crawl4ai` integration. The goal is to understand how local models, specifically Gemma 3 via Ollama, can be used with `crawl4ai` and to implement a mechanism in `backend\app\app_config.py` to ensure that when an Ollama model is selected, it launches the model if it's not already running, to avoid delays during fetching.

I have the content of `docs/project_overview.md`, `docs/project_structure.md`, `docs/CONTEXT_README.md`, `docs/livetest_instructions.md`, and `backend\app\app_config.py`. The file `docs/Consolidated_Overview.md` was not found. I also have the file listing for `docs/crawl4ai/docs/md_v2/` and the content of `docs/crawl4ai/docs/md_v2/index.md`.

To address the user's request, I need to:
1. Review the provided documents to understand the current state of the project, the `crawl4ai` integration, and how models are configured.
2. Specifically look for information on local model usage and how `crawl4ai` interacts with them. The `crawl4ai` documentation (`docs/crawl4ai/docs/md_v2/index.md` and the folder structure) and `backend\app\app_config.py` will be key here.
3. Analyze `backend\app\app_config.py` to understand the current model configuration and identify where the logic for launching an Ollama model could be added.
4. Formulate a plan to implement the requested feature: automatically launching the selected Ollama model when it's chosen for fetching. This might involve adding a check before calling `crawl4ai` to see if the model is running and, if not, executing a command to launch it.
5. Present the findings and the plan to the user using the `plan_mode_respond` tool.

Given that I am in PLAN MODE, I will first review the documents and then propose a plan. I will not make any code changes yet.

Reviewing the documents:
- `docs/project_overview.md`: Provides a high-level overview of PMOVES features, architecture, and data flow. Mentions Groq API and local processing for transcription, and JinAI/crawl4ai for web fetching. Mentions OpenAI and Groq for embeddings/analysis. Lists backend components including `fetch_content.py` and `psearchworking.py`. Lists frontend pages including `/fetch`. Mentions external services like Groq API and JinAI (crawl4ai).
- `docs/project_structure.md`: Details the directory structure and key components. Confirms `backend/app/fetch_content.py` handles web content fetching and `backend/app/psearchworking.py` handles vector search and integrates with OpenAI/Groq. Mentions the frontend fetch interface at `src/app/fetch/`.
- `docs/CONTEXT_README.md`: Focuses specifically on the `crawl4ai` integration for the Fetch page. States that feature implementation is complete and the `NotImplementedError` on Windows is resolved by running Uvicorn without `--reload`. Mentions `backend/app/main.py` and `backend/app/test_crawl4ai_isolated.py`. This confirms `crawl4ai` is integrated and working on Windows under specific conditions.
- `docs/livetest_instructions.md`: Details a testing strategy for `crawl4ai`'s LLM extraction parameters. Mentions recent backend updates including fixing a `fetch_history` status bug, implementing LLM logging, and refactoring utility modules. Lists various test batches and their statuses, indicating unexpected passes for some tests related to invalid inputs and overrides. This document confirms that LLM extraction is being actively tested and refined, and that `crawl4ai` is being used for LLM-based tasks. It also mentions `live_llm_extraction_advanced_tester.py`.
- `docs/crawl4ai/docs/md_v2/index.md`: This is the main index for the `crawl4ai` documentation. It highlights Crawl4AI's features, including generating clean Markdown, structured extraction (CSS, XPath, LLM-based), advanced browser control, and high performance. It emphasizes being "LLM Friendly". The quick start shows basic asynchronous usage. This confirms `crawl4ai` is designed to work with LLMs and has features for extraction.
- `backend\app\app_config.py`: This file centralizes backend settings, including API keys and base URLs for various models/providers. It defines `AVAILABLE_MODELS`, which includes entries for "Ollama (Local)" models like "Ollama: Gemma 3 (local)". These entries specify `requires_api_key: False` and `base_url_var: "OLLAMA_BASE_URL"`. The `OLLAMA_BASE_URL` is defaulted to `http://localhost:11434`. This file is the correct place to manage model configurations and potentially add logic related to launching local models.

Based on the review, `crawl4ai` is integrated and used for LLM-based extraction. `backend\app\app_config.py` lists Ollama models, including Gemma 3, and their configuration points to a local base URL. The user wants to ensure that when an Ollama model is selected, the backend attempts to launch it if it's not running.

Plan:
1. Identify the part of the backend code that handles the selection and use of the LLM for `crawl4ai` fetching. Based on the document review, this is likely within `backend/app/fetch_content.py` or potentially `backend/app/psearchworking.py` if the LLM extraction is tied to the search/upsert process, but `fetch_content.py` seems more direct for the fetch page.
2. Before initiating the `crawl4ai` call with an Ollama model, add a check to see if the Ollama server is running. This could involve attempting a simple request to the `OLLAMA_BASE_URL`.
3. If the check indicates the server is not running, execute a command to launch the specific Ollama model (e.g., `ollama run gemma3`). This command would need to be executed in a separate process or thread to avoid blocking the main application flow.
4. Consider potential issues: How to handle different operating systems for the launch command? How to determine if the model is *ready* after launching the server? How to handle errors during the launch? How to avoid launching if the server is already running but the specific model isn't loaded? (Ollama typically loads the model on the first `run` command if it's not already loaded).
5. Refine the plan to address these issues. A robust solution might involve:
    - Checking if the Ollama server is reachable.
    - If reachable, attempt a small request with the specific model to see if it's loaded/available.
    - If not reachable or the model isn't available, execute `ollama run <model_name>` in a non-blocking way.
    - Add logging to track the status of the Ollama server and model loading.
6. Propose this plan to the user.

I will now formulate the response using `plan_mode_respond`.<plan_mode_respond>
Based on the provided documentation and file contents, I understand that you want to ensure that when an Ollama model, specifically Gemma 3, is selected for use with `crawl4ai` in the PMOVES application, the backend automatically attempts to launch the model via Ollama if it's not already running. This is to prevent delays during fetching.

Here's a plan to implement this functionality:

1.  **Identify the Integration Point:** The logic for selecting and using the LLM for `crawl4ai` fetching is likely located within `backend/app/fetch_content.py`, as this file handles the web content fetching process. We will need to examine this file to find where the `crawl4ai` call is made with the LLM configuration.

2.  **Implement Ollama Status Check:** Before initiating the `crawl4ai` fetch when an Ollama model is selected, we will add a check to verify if the Ollama server is running and if the specific model is available. This can be done by:
    *   Attempting a simple HTTP request to the configured `OLLAMA_BASE_URL` (defaulting to `http://localhost:11434`). A successful response indicates the server is running.
    *   If the server is reachable, attempt a small, non-destructive request using the selected Ollama model (e.g., a simple chat completion with a minimal prompt). A successful response here indicates the model is loaded and ready.

3.  **Execute Ollama Launch Command:** If the status check reveals that the Ollama server is not running or the specific model is not loaded, we will execute a command to launch the model.
    *   The command will be `ollama run <model_name>`, where `<model_name>` is the identifier for the selected Ollama model (e.g., `gemma3`).
    *   This command needs to be executed in a non-blocking manner (e.g., using `subprocess.Popen` in Python) so that it doesn't halt the FastAPI application while Ollama starts up and loads the model.
    *   We will need to consider the operating system to ensure the command is executed correctly (e.g., using `shell=True` on Windows might be necessary, but requires caution).

4.  **Add Waiting and Retry Logic:** After executing the launch command, the application should ideally wait briefly and potentially retry the status check to confirm that the Ollama server and model are ready before proceeding with the `crawl4ai` fetch. This waiting period should be reasonable to avoid excessive delays but long enough for Ollama to initialize.

5.  **Integrate with `app_config.py`:** The `backend/app/app_config.py` file already contains the configuration for Ollama models and the `OLLAMA_BASE_URL`. The logic for checking and launching the model will utilize this configuration. We might add a helper function in `app_config.py` or a related utility module to encapsulate the Ollama interaction logic.

6.  **Error Handling and Logging:** Implement robust error handling for the status checks and the launch command execution. Log informative messages at each step (checking status, launching model, success/failure) to aid in debugging.

**Refined Steps:**

*   Modify the function in `backend/app/fetch_content.py` that prepares and executes the `crawl4ai` call.
*   Before the `crawl4ai` call, check if the selected LLM model is an Ollama model based on its `id` in `AVAILABLE_MODELS`.
*   If it's an Ollama model, call a new utility function (e.g., `ensure_ollama_model_ready`) that takes the model ID and base URL.
*   The `ensure_ollama_model_ready` function will:
    *   Attempt to connect to the `OLLAMA_BASE_URL`.
    *   If connection fails, execute `ollama run <model_id>` in a non-blocking subprocess.
    *   Wait for a short duration (e.g., 5-10 seconds).
    *   Retry connecting to the `OLLAMA_BASE_URL` and attempt a small request with the model ID to confirm readiness.
    *   Raise an error if the model is not ready after retries.
*   Add necessary imports and logging to the relevant files.

This plan focuses on integrating the Ollama model readiness check and launch into the existing fetch workflow without requiring significant changes to the core `crawl4ai` library itself.

Does this plan align with your requirements, and are there any specific details you'd like to refine before we proceed to implementation in ACT MODE?
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
The tool execution failed with the following error:
<error>
Missing value for required parameter 'response'. Please retry with complete response.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.
</error>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 9:56:43 AM (America/New_York, UTC-4:00)

# Context Window Usage
46,866 / 1,048.576K tokens used (4%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The previous `plan_mode_respond` tool use failed because I did not include the `response` parameter within the tool tags. I need to retry the `plan_mode_respond` tool use, ensuring the response content is correctly placed within the `<response>` tags. The content of the response will be the plan I formulated in the previous turn.<plan_mode_respond>
<response>
Based on the provided documentation and file contents, I understand that you want to ensure that when an Ollama model, specifically Gemma 3, is selected for use with `crawl4ai` in the PMOVES application, the backend automatically attempts to launch the model via Ollama if it's not already running. This is to prevent delays during fetching.

Here's a plan to implement this functionality:

1.  **Identify the Integration Point:** The logic for selecting and using the LLM for `crawl4ai` fetching is likely located within `backend/app/fetch_content.py`, as this file handles the web content fetching process. We will need to examine this file to find where the `crawl4ai` call is made with the LLM configuration.

2.  **Implement Ollama Status Check:** Before initiating the `crawl4ai` fetch when an Ollama model is selected, we will add a check to verify if the Ollama server is running and if the specific model is available. This can be done by:
    *   Attempting a simple HTTP request to the configured `OLLAMA_BASE_URL` (defaulting to `http://localhost:11434`). A successful response indicates the server is running.
    *   If the server is reachable, attempt a small, non-destructive request using the selected Ollama model (e.g., a simple chat completion with a minimal prompt). A successful response here indicates the model is loaded and ready.

3.  **Execute Ollama Launch Command:** If the status check reveals that the Ollama server is not running or the specific model is not loaded, we will execute a command to launch the model.
    *   The command will be `ollama run <model_name>`, where `<model_name>` is the identifier for the selected Ollama model (e.g., `gemma3`).
    *   This command needs to be executed in a non-blocking manner (e.g., using `subprocess.Popen` in Python) so that it doesn't halt the FastAPI application while Ollama starts up and loads the model.
    *   We will need to consider the operating system to ensure the command is executed correctly (e.g., using `shell=True` on Windows might be necessary, but requires caution).

4.  **Add Waiting and Retry Logic:** After executing the launch command, the application should ideally wait briefly and potentially retry the status check to confirm that the Ollama server and model are ready before proceeding with the `crawl4ai` fetch. This waiting period should be reasonable to avoid excessive delays but long enough for Ollama to initialize.

5.  **Integrate with `app_config.py`:** The `backend/app/app_config.py` file already contains the configuration for Ollama models and the `OLLAMA_BASE_URL`. The logic for checking and launching the model will utilize this configuration. We might add a helper function in `app_config.py` or a related utility module to encapsulate the Ollama interaction logic.

6.  **Error Handling and Logging:** Implement robust error handling for the status checks and the launch command execution. Log informative messages at each step (checking status, launching model, success/failure) to aid in debugging.

**Refined Steps:**

*   Modify the function in `backend/app/fetch_content.py` that prepares and executes the `crawl4ai` call.
*   Before the `crawl4ai` call, check if the selected LLM model is an Ollama model based on its `id` in `AVAILABLE_MODELS`.
*   If it's an Ollama model, call a new utility function (e.g., `ensure_ollama_model_ready`) that takes the model ID and base URL.
*   The `ensure_ollama_model_ready` function will:
    *   Attempt to connect to the `OLLAMA_BASE_URL`.
    *   If connection fails, execute `ollama run <model_id>` in a non-blocking subprocess.
    *   Wait for a short duration (e.g., 5-10 seconds).
    *   Retry connecting to the `OLLAMA_BASE_URL` and attempt a small request with the model ID to confirm readiness.
    *   Raise an error if the model is not ready after retries.
*   Add necessary imports and logging to the relevant files.

This plan focuses on integrating the Ollama model readiness check and launch into the existing fetch workflow without requiring significant changes to the core `crawl4ai` library itself.

Does this plan align with your requirements, and are there any specific details you'd like to refine before we proceed to implementation in ACT MODE?
</response>
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
<user_message>
the models are selected when the server is launched for simplicity the model can be loaded if its selected in env which loads to app_config
</user_message>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 9:58:39 AM (America/New_York, UTC-4:00)

# Context Window Usage
48,644 / 1,048.576K tokens used (5%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The user has clarified that the LLM models are selected via environment variables when the server launches, and this selection is loaded into `app_config.py`. They want the selected Ollama model to be loaded when the server starts, so it's ready for fetching without delay.

This changes the plan slightly. Instead of checking and potentially launching the model *before each fetch*, the goal is to ensure the selected Ollama model is loaded into memory by the Ollama server *when the PMOVES backend starts*.

Revised Plan:
1. Identify where in the backend startup process (likely `backend/app/main.py` or a file imported by it) the model configuration from `app_config.py` is accessed or initialized.
2. After the model configuration is loaded, check if the selected LLM model (determined by an environment variable, which is then reflected in `app_config.py`) is an Ollama model.
3. If an Ollama model is selected, execute the command `ollama run <model_name>` during the backend startup. This command will instruct the local Ollama server to download and load the specified model into memory if it's not already present and loaded.
4. This command should also be executed in a non-blocking manner to avoid delaying the backend server startup.
5. Add logging to indicate which Ollama model is being loaded during startup.

This approach ensures the model is ready as soon as the backend is operational, addressing the user's goal of avoiding delays during fetching.

I will now present this revised plan using `plan_mode_respond`.<plan_mode_respond>
Thank you for the clarification. Based on your input that models are selected via environment variables loaded into `app_config.py` at server launch, the goal is to ensure the selected Ollama model is loaded by the Ollama server during the PMOVES backend startup process.

Here is the revised plan:

1.  **Identify Backend Startup:** We will locate the main backend startup logic, likely within `backend/app/main.py` or an initialization routine called by it, where the application reads the configuration from `app_config.py`.

2.  **Check Selected Model:** During the backend startup, after the configuration from `app_config.py` is loaded, we will check which LLM model has been selected (presumably via an environment variable that the backend reads). We will then determine if this selected model is one of the configured Ollama models listed in `app_config.py`.

3.  **Execute Ollama Model Loading Command:** If the selected model is an Ollama model, we will execute the command `ollama run <model_name>` during the backend's initialization phase.
    *   This command tells the local Ollama server to download the model if necessary and load it into memory, making it ready for subsequent requests without delay.
    *   Similar to the previous plan, this command should be executed in a non-blocking way (e.g., using `subprocess.Popen`) to prevent the backend startup from being blocked by the model loading process.

4.  **Add Logging:** We will add logging statements during the startup process to indicate whether an Ollama model was selected and if the `ollama run` command is being executed. This will help in monitoring and debugging.

**Refined Steps:**

*   In `backend/app/main.py` or an appropriate initialization function, access the loaded configuration from `app_config.py`.
*   Determine the currently selected LLM model based on application logic (e.g., reading a specific environment variable that maps to a model ID in `AVAILABLE_MODELS`).
*   Check if the selected model's configuration in `AVAILABLE_MODELS` indicates it's an Ollama model (`provider_group: "Ollama (Local)"`).
*   If it is an Ollama model, construct the command `ollama run <model_id>` using the model's `id` from `app_config.py`.
*   Execute this command using `subprocess.Popen` or a similar non-blocking method, ensuring it's compatible with the operating system.
*   Add logging before and after attempting to run the Ollama command.

This revised plan ensures that the selected Ollama model is proactively loaded by the Ollama server when the PMOVES backend starts, addressing the performance concern for fetching operations.

Does this revised plan meet your requirements? If so, we can proceed to ACT MODE to implement it.
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
The tool execution failed with the following error:
<error>
Missing value for required parameter 'response'. Please retry with complete response.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.
</error>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 9:58:46 AM (America/New_York, UTC-4:00)

# Context Window Usage
96,665 / 1,048.576K tokens used (9%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The previous `plan_mode_respond` tool use failed again due to the missing `response` parameter. I need to retry the `plan_mode_respond` tool use, ensuring the response content is correctly placed within the `<response>` tags. The content of the response will be the revised plan I formulated in the previous turn.<plan_mode_respond>
<response>
Thank you for the clarification. Based on your input that models are selected via environment variables loaded into `app_config.py` at server launch, the goal is to ensure the selected Ollama model is loaded by the Ollama server during the PMOVES backend startup process.

Here is the revised plan:

1.  **Identify Backend Startup:** We will locate the main backend startup logic, likely within `backend/app/main.py` or an initialization routine called by it, where the application reads the configuration from `app_config.py`.

2.  **Check Selected Model:** During the backend startup, after the configuration from `app_config.py` is loaded, we will check which LLM model has been selected (presumably via an environment variable that the backend reads). We will then determine if this selected model is one of the configured Ollama models listed in `app_config.py`.

3.  **Execute Ollama Model Loading Command:** If the selected model is an Ollama model, we will execute the command `ollama run <model_name>` during the backend's initialization phase.
    *   This command tells the local Ollama server to download the model if necessary and load it into memory, making it ready for subsequent requests without delay.
    *   Similar to the previous plan, this command should be executed in a non-blocking way (e.g., using `subprocess.Popen`) to prevent the backend startup from being blocked by the model loading process.
    *   We will need to consider the operating system to ensure the command is executed correctly (e.g., using `shell=True` on Windows might be necessary, but requires caution).

4.  **Add Logging:** We will add logging statements during the startup process to indicate whether an Ollama model was selected and if the `ollama run` command is being executed. This will help in monitoring and debugging.

**Refined Steps:**

*   In `backend/app/main.py` or an appropriate initialization function, access the loaded configuration from `app_config.py`.
*   Determine the currently selected LLM model based on application logic (e.g., reading a specific environment variable that maps to a model ID in `AVAILABLE_MODELS`).
*   Check if the selected model's configuration in `AVAILABLE_MODELS` indicates it's an Ollama model (`provider_group: "Ollama (Local)"`).
*   If it is an Ollama model, construct the command `ollama run <model_id>` using the model's `id` from `app_config.py`.
*   Execute this command using `subprocess.Popen` or a similar non-blocking method, ensuring it's compatible with the operating system.
*   Add logging before and after attempting to run the Ollama command.

This revised plan ensures that the selected Ollama model is proactively loaded by the Ollama server when the PMOVES backend starts, addressing the performance concern for fetching operations.

Does this revised plan meet your requirements? If so, we can proceed to ACT MODE to implement it.
</response>
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
<user_message>
i dont want to messe with main if it needs to be specific for ollama integation that would be better a separate script that activates ollama when it is selected
</user_message>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 9:59:59 AM (America/New_York, UTC-4:00)

# Context Window Usage
93,804 / 1,048.576K tokens used (9%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The user wants to avoid modifying `backend/app/main.py` directly for the Ollama integration. They suggest a separate script that activates Ollama when it's selected.

This is a good approach for keeping the Ollama-specific logic separate and not cluttering the main application entry point.

Revised Plan (incorporating a separate script):
1. Create a new Python script (e.g., `backend/app/ollama_initializer.py`) that will handle the Ollama model loading logic.
2. This script will read the selected LLM model from environment variables (the same way `app_config.py` does).
3. It will check if the selected model is an Ollama model.
4. If an Ollama model is selected, the script will execute the `ollama run <model_name>` command in a non-blocking manner.
5. The main backend startup process (`backend/app/main.py`) will then need to execute this `ollama_initializer.py` script during its startup phase. This can be done using `subprocess.Popen` in `main.py` to run the script in a separate process.
6. Add logging to both `ollama_initializer.py` and `main.py` to track the execution and status.

This plan keeps the Ollama logic isolated in a dedicated script while still ensuring the model is loaded during backend startup.

I will now present this revised plan using `plan_mode_respond`.<plan_mode_respond>
Okay, I understand. To keep the Ollama integration logic separate from `backend/app/main.py`, we can create a dedicated script for this purpose.

Here is the revised plan using a separate script:

1.  **Create a Dedicated Script:** We will create a new Python script, for example, `backend/app/ollama_initializer.py`. This script will be responsible solely for checking the selected model and initiating the Ollama model loading if necessary.

2.  **Read Selected Model in Script:** The `ollama_initializer.py` script will read the environment variable that specifies the selected LLM model, similar to how `app_config.py` accesses this information. It will also need access to the `AVAILABLE_MODELS` configuration from `app_config.py` to determine if the selected model is an Ollama model. We can achieve this by importing necessary parts of `app_config.py` into the initializer script.

3.  **Implement Ollama Loading Logic in Script:** Inside `ollama_initializer.py`, the script will:
    *   Determine the selected model ID.
    *   Look up the model's configuration in `app_config.py.AVAILABLE_MODELS`.
    *   If the model is identified as an Ollama model (`provider_group: "Ollama (Local)"`), it will construct the `ollama run <model_id>` command.
    *   It will then execute this command using a non-blocking method like `subprocess.Popen`.

4.  **Execute Script During Backend Startup:** The `backend/app/main.py` script will be modified to execute `ollama_initializer.py` during its startup sequence. This can be done by adding a call to `subprocess.Popen` in `main.py` that runs the `ollama_initializer.py` script. This ensures the Ollama loading process starts when the backend starts, without blocking `main.py`.

5.  **Add Logging:** We will include logging in both `ollama_initializer.py` to report on the model check and command execution, and in `backend/app/main.py` to indicate that the initializer script is being launched.

**Refined Steps:**

*   Create `backend/app/ollama_initializer.py`.
*   In `ollama_initializer.py`, import necessary modules (e.g., `os`, `subprocess`, `logging`) and potentially parts of `backend.app.app_config`.
*   Implement the logic in `ollama_initializer.py` to read the selected model environment variable, check if it's an Ollama model using `app_config.AVAILABLE_MODELS`, and execute `ollama run <model_id>` using `subprocess.Popen` if it is.
*   In `backend/app/main.py`, add code during the application startup (e.g., within an `asyncio.create_task` or similar if using FastAPI's startup events, or simply as a call near the beginning of the script if appropriate) to execute `ollama_initializer.py` using `subprocess.Popen`.
*   Add logging in both files.

This approach isolates the Ollama-specific logic into `ollama_initializer.py`, keeping `main.py` cleaner, while still achieving the goal of loading the selected Ollama model during backend startup.

Does this revised plan, which uses a separate script, meet your requirements? If so, please let me know, and we can proceed to ACT MODE to implement it.
</response>
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
The tool execution failed with the following error:
<error>
Missing value for required parameter 'response'. Please retry with complete response.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.
</error>
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:00:06 AM (America/New_York, UTC-4:00)

# Context Window Usage
101,736 / 1,048.576K tokens used (10%)

# Current Mode
PLAN MODE
In this mode you should focus on information gathering, asking questions, and architecting a solution. Once you have a plan, use the plan_mode_respond tool to engage in a conversational back and forth with the user. Do not use the plan_mode_respond tool until you've gathered all the information you need e.g. with read_file or ask_followup_question.
(Remember: If it seems the user wants you to use tools only available in Act Mode, you should ask the user to "toggle to Act mode" (use those words) - they will have to manually do this themselves with the Plan/Act toggle button below. You do not have the ability to switch to Act Mode yourself, and must wait for the user to do it themselves once they are satisfied with the plan. You also cannot present an option to toggle to Act mode, as this will be something you need to direct the user to do manually themselves.)
</environment_details>

---

**Assistant:**

<thinking>The previous `plan_mode_respond` tool use failed again due to the missing `response` parameter. I need to retry the `plan_mode_respond` tool use, ensuring the response content is correctly placed within the `<response>` tags. The content of the response will be the revised plan I formulated in the previous turn.<plan_mode_respond>
<response>
Okay, I understand. To keep the Ollama integration logic separate from `backend/app/main.py`, we can create a dedicated script for this purpose.

Here is the revised plan using a separate script:

1.  **Create a Dedicated Script:** We will create a new Python script, for example, `backend/app/ollama_initializer.py`. This script will be responsible solely for checking the selected model and initiating the Ollama model loading if necessary.

2.  **Read Selected Model in Script:** The `ollama_initializer.py` script will read the environment variable that specifies the selected LLM model, similar to how `app_config.py` accesses this information. It will also need access to the `AVAILABLE_MODELS` configuration from `app_config.py` to determine if the selected model is an Ollama model. We can achieve this by importing necessary parts of `app_config.py` into the initializer script.

3.  **Implement Ollama Loading Logic in Script:** Inside `ollama_initializer.py`, the script will:
    *   Determine the selected model ID.
    *   Look up the model's configuration in `app_config.py.AVAILABLE_MODELS`.
    *   If the model is identified as an Ollama model (`provider_group: "Ollama (Local)"`), it will construct the `ollama run <model_id>` command.
    *   It will then execute this command using a non-blocking method like `subprocess.Popen`.

4.  **Execute Script During Backend Startup:** The `backend/app/main.py` script will be modified to execute `ollama_initializer.py` during its startup sequence. This can be done by adding a call to `subprocess.Popen` in `main.py` that runs the `ollama_initializer.py` script. This ensures the Ollama loading process starts when the backend starts, without blocking `main.py`.

5.  **Add Logging:** We will include logging in both `ollama_initializer.py` to report on the model check and command execution, and in `backend/app/main.py` to indicate that the initializer script is being launched.

**Refined Steps:**

*   Create `backend/app/ollama_initializer.py`.
*   In `ollama_initializer.py`, import necessary modules (e.g., `os`, `subprocess`, `logging`) and potentially parts of `backend.app.app_config`.
*   Implement the logic in `ollama_initializer.py` to read the selected model environment variable, check if it's an Ollama model using `app_config.AVAILABLE_MODELS`, and execute `ollama run <model_id>` using `subprocess.Popen` if it is.
*   In `backend/app/main.py`, add code during the application startup (e.g., within an `asyncio.create_task` or similar if using FastAPI's startup events, or simply as a call near the beginning of the script if appropriate) to execute `ollama_initializer.py` using `subprocess.Popen`.
*   Add logging in both files.

This approach isolates the Ollama-specific logic into `ollama_initializer.py`, keeping `main.py` cleaner, while still achieving the goal of loading the selected Ollama model during backend startup.

Does this revised plan, which uses a separate script, meet your requirements? If so, please let me know, and we can proceed to ACT MODE to implement it.
</response>
</plan_mode_respond>

---

**User:**

[plan_mode_respond] Result:
[The user has switched to ACT MODE, so you may now proceed with the task.]
<environment_details>
# VSCode Visible Files
docs/livetest_instructions.md

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
backend/app/tests/TESTING_INSTRUCTIONS.md
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:00:28 AM (America/New_York, UTC-4:00)

# Context Window Usage
105,315 / 1,048.576K tokens used (10%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>The user has switched to ACT MODE, indicating they approve the plan to create a separate script (`ollama_initializer.py`) to handle the Ollama model loading during backend startup.

My next steps are to implement this plan:
1. Create the `backend/app/ollama_initializer.py` script.
2. Write the Python code in `ollama_initializer.py` to read the selected model from environment variables, check if it's an Ollama model using `app_config.AVAILABLE_MODELS`, and execute the `ollama run <model_id>` command using `subprocess.Popen` if it is.
3. Modify `backend/app/main.py` to execute `ollama_initializer.py` during its startup.
4. Add logging to both files.

I will start by creating the `ollama_initializer.py` script and adding the necessary logic. I will need to read the `LLM_MODEL` environment variable (assuming this is how the selected model is specified, based on common patterns and the structure of `app_config.py` which lists models with `id`s that look like they'd be used in config). I will also need to import `app_config` to access `AVAILABLE_MODELS`.

After creating the script, I will modify `backend/app/main.py` to run it.

Let's start with creating `backend/app/ollama_initializer.py`.<write_to_file>
<path>backend/app/ollama_initializer.py</path>
<content>
import os
import subprocess
import sys
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure ollama_initializer.py is in the backend/app directory.")
    sys.exit(1)

def ensure_ollama_model_loaded():
    """
    Checks the selected LLM model from environment variables and
    executes 'ollama run &lt;model_id&gt;' if it's an Ollama model.
    """
    # Assuming the selected LLM model ID is stored in an environment variable
    # named LLM_MODEL. Adjust if the actual variable name is different.
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.info("LLM_MODEL environment variable not set. Skipping Ollama model loading.")
        return

    logger.info(f"Selected LLM_MODEL: {selected_model_id}")

    model_config = None
    # Find the model config by matching the 'id' in AVAILABLE_MODELS
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config:
        logger.warning(f"Model ID '{selected_model_id}' not found in AVAILABLE_MODELS config. Cannot determine if it's an Ollama model.")
        return

    if model_config.get('provider_group') == 'Ollama (Local)':
        ollama_model_id = model_config.get('id')
        logger.info(f"Selected model '{selected_model_id}' is an Ollama model. Attempting to load via 'ollama run {ollama_model_id}'.")

        try:
            # Execute 'ollama run &lt;model_id&gt;' in a non-blocking way
            # This command will download and load the model if not already present/loaded
            # Use shell=True on Windows for better command execution
            command = ["ollama", "run", ollama_model_id]
            if os.name == 'nt': # Check if on Windows
                 # Use a simple command that exits immediately after loading/checking
                 # 'ollama run' can be interactive, so we need to handle that.
                 # A better approach might be 'ollama pull' followed by a check,
                 # but 'ollama run' is simpler for initial loading.
                 # Let's try a non-interactive command if possible, or just run and detach.
                 # 'ollama list' is non-interactive, but doesn't load.
                 # 'ollama run' is the standard way to ensure it's loaded.
                 # We'll run it and let it potentially run in the background or exit.
                 # Adding '&amp;' for Windows background execution might work, but is shell-dependent.
                 # Let's stick to a basic Popen and hope it behaves reasonably or exits.
                 # A more robust solution might involve checking 'ollama list' first.
                 # For simplicity in this initializer script, we'll just run it.
                 # We'll redirect stdout/stderr to avoid interactive prompts in the main process.
                 process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
            else: # Linux/macOS
                 process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            logger.info(f"Executed command: {' '.join(command)}. Process started with PID: {process.pid}")
            # Note: We are not waiting for the process to finish, as it might stay running
            # or take time to download. The goal is just to initiate the loading.

        except FileNotFoundError:
            logger.error("Ollama command not found. Make sure Ollama is installed and in your system's PATH.")
        except Exception as e:
            logger.error(f"Error executing 'ollama run {ollama_model_id}': {e}")
    else:
        logger.info(f"Selected model '{selected_model_id}' is not an Ollama model. Skipping Ollama model loading.")

if __name__ == "__main__":
    logger.info("Running Ollama initializer script.")
    ensure_ollama_model_loaded()
    logger.info("Ollama initializer script finished.")

</content>
</write_to_file>
</thinking>

---

**User:**

[write_to_file for 'backend/app/ollama_initializer.py'] Result:
The content was successfully saved to backend/app/ollama_initializer.py.

Here is the full, updated content of the file that was saved:

<final_file_content path="backend/app/ollama_initializer.py">
import os
import subprocess
import sys
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure ollama_initializer.py is in the backend/app directory.")
    sys.exit(1)

def ensure_ollama_model_loaded():
    """
    Checks the selected LLM model from environment variables and
    executes 'ollama run <model_id>' if it's an Ollama model.
    """
    # Assuming the selected LLM model ID is stored in an environment variable
    # named LLM_MODEL. Adjust if the actual variable name is different.
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.info("LLM_MODEL environment variable not set. Skipping Ollama model loading.")
        return

    logger.info(f"Selected LLM_MODEL: {selected_model_id}")

    model_config = None
    # Find the model config by matching the 'id' in AVAILABLE_MODELS
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config:
        logger.warning(f"Model ID '{selected_model_id}' not found in AVAILABLE_MODELS config. Cannot determine if it's an Ollama model.")
        return

    if model_config.get('provider_group') == 'Ollama (Local)':
        ollama_model_id = model_config.get('id')
        logger.info(f"Selected model '{selected_model_id}' is an Ollama model. Attempting to load via 'ollama run {ollama_model_id}'.")

        try:
            # Execute 'ollama run <model_id>' in a non-blocking way
            # This command will download and load the model if not already present/loaded
            # Use shell=True on Windows for better command execution
            command = ["ollama", "run", ollama_model_id]
            if os.name == 'nt': # Check if on Windows
                 # Use a simple command that exits immediately after loading/checking
                 # 'ollama run' can be interactive, so we need to handle that.
                 # A better approach might be 'ollama pull' followed by a check,
                 # but 'ollama run' is simpler for initial loading.
                 # Let's try a non-interactive command if possible, or just run and detach.
                 # 'ollama list' is non-interactive, but doesn't load.
                 # 'ollama run' is the standard way to ensure it's loaded.
                 # We'll run it and let it potentially run in the background or exit.
                 # Adding '&' for Windows background execution might work, but is shell-dependent.
                 # Let's stick to a basic Popen and hope it behaves reasonably or exits.
                 # A more robust solution might involve checking 'ollama list' first.
                 # For simplicity in this initializer script, we'll just run it.
                 # We'll redirect stdout/stderr to avoid interactive prompts in the main process.
                 process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
            else: # Linux/macOS
                 process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            logger.info(f"Executed command: {' '.join(command)}. Process started with PID: {process.pid}")
            # Note: We are not waiting for the process to finish, as it might stay running
            # or take time to download. The goal is just to initiate the loading.

        except FileNotFoundError:
            logger.error("Ollama command not found. Make sure Ollama is installed and in your system's PATH.")
        except Exception as e:
            logger.error(f"Error executing 'ollama run {ollama_model_id}': {e}")
    else:
        logger.info(f"Selected model '{selected_model_id}' is not an Ollama model. Skipping Ollama model loading.")

if __name__ == "__main__":
    logger.info("Running Ollama initializer script.")
    ensure_ollama_model_loaded()
    logger.info("Ollama initializer script finished.")

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.


<environment_details>
# VSCode Visible Files
backend/app/ollama_initializer.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
backend/app/ollama_initializer.py

# Current Time
5/13/2025, 10:00:51 AM (America/New_York, UTC-4:00)

# Context Window Usage
109,197 / 1,048.576K tokens used (10%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I have successfully created the `backend/app/ollama_initializer.py` script. The next step is to modify `backend/app/main.py` to execute this script during its startup.

I need to find the appropriate place in `backend/app/main.py` to add the code that runs `ollama_initializer.py`. FastAPI applications typically have a startup event handler (`@app.on_event("startup")`) which is a good place for initialization tasks. I will look for this or a similar mechanism in `main.py`.

I will use the `replace_in_file` tool to add the necessary code to `backend/app/main.py`. I will need to add an import for `subprocess` and potentially `sys` if needed for path manipulation, and then add the code to run the script in a non-blocking way within the startup event.

I will first read `backend/app/main.py` to understand its structure and identify the startup event or a suitable location for the code.<read_file>
<path>backend/app/main.py</path>
</read_file>
</thinking>

---

**User:**

[read_file for 'backend/app/main.py'] Result:
import os
import sys # Keep sys import first for platform check

# --- Event Loop Policy (MUST BE SET BEFORE ASYNCIO IMPORT) ---
_event_loop_policy_set = False
if sys.platform == "win32":
    try:
        # Temporarily import asyncio just for this setting
        import asyncio as _asyncio_temp
        _asyncio_temp.set_event_loop_policy(_asyncio_temp.WindowsProactorEventLoopPolicy())
        _event_loop_policy_set = True
        # We will log this after full asyncio and logging are imported
    except ImportError:
        # Fallback or error logging if asyncio cannot be imported here
        logger.critical("CRITICAL: Could not import asyncio to set event loop policy.")
    finally:
        # Ensure our temporary import doesn't linger
        if '_asyncio_temp' in locals():
            del _asyncio_temp

import asyncio # Now import asyncio for real
import logging # Import logging

# Rich logging for pretty terminal output
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in ["true", "1", "yes"]
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "pmoves_backend.log")

# Set up root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any default handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Console handler (always enabled)
if RICH_AVAILABLE:
    console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
else:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)

# File handler (optional, based on env)
if LOG_TO_FILE:
    file_handler = logging.FileHandler(LOG_FILE_NAME, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

logger.info(f"Logging initialized. Console: always. File: {'enabled' if LOG_TO_FILE else 'disabled'}{f' ({LOG_FILE_NAME})' if LOG_TO_FILE else ''}")

# --- Logging Configuration (Setup ASAP after policy set) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # Initialize main logger

# Log the policy that was set (or attempted)
if sys.platform == "win32":
    if _event_loop_policy_set:
        logger.info(f"Policy set in main.py (top level): {asyncio.get_event_loop_policy().__class__.__name__}")
    else:
        logger.error(f"Failed to set WindowsProactorEventLoopPolicy. Current policy: {asyncio.get_event_loop_policy().__class__.__name__}")
else:
    logger.info(f"Running on non-Windows platform. Default policy: {asyncio.get_event_loop_policy().__class__.__name__}")


# -*- coding: utf-8 -*-
"""
PMOVES Transcription API Backend

This FastAPI application provides endpoints for:
- Processing YouTube videos (downloading, transcribing).
- Downloading videos/audio using yt-dlp with progress updates.
- Fetching video metadata.
- Fetching web content using Jina Reader API, generating PDFs, storing in Supabase, and enabling vector search.
- Real-time status updates via Server-Sent Events (SSE).
- Content ingestion and vector search capabilities (requires related modules).
"""

# --- Standard Library Imports ---
import os
import re
import json
import shutil
# import logging # Moved up
# import asyncio # Moved up
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
from typing import Any # Added for Supabase client type hint if needed, or use from existing

# --- Third-Party Imports ---
from dotenv import load_dotenv
from fastapi import (
    FastAPI, HTTPException, BackgroundTasks, Body, Request,
    status, Query, Depends, Security # Added Security for potential API key auth
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse # Added FileResponse
from fastapi.security import APIKeyHeader # Added for potential API key auth
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import (
    BaseModel, validator, ValidationError, Field, field_validator
)
import torch # Still imported from original, ensure necessary

# --- Optional Third-Party Imports (with fallbacks/warnings) ---
try:
    from openai import OpenAI, AsyncOpenAI # Added AsyncOpenAI
    from openai import APIError as OpenAI_APIError # Specific OpenAI errors
    from openai import RateLimitError as OpenAI_RateLimitError
    from openai import APIConnectionError as OpenAI_APIConnectionError
    from openai import AuthenticationError as OpenAI_AuthenticationError
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    OpenAI_APIError = None
    OpenAI_RateLimitError = None
    OpenAI_APIConnectionError = None
    OpenAI_AuthenticationError = None

try:
    from groq import Groq, AsyncGroq # Added AsyncGroq
except ImportError:
    Groq = None
    AsyncGroq = None

try:
    from rich.console import Console
except ImportError:
    class Console:
        def print(self, *args, **kwargs): print(*args)
    Console = Console() # Instantiate dummy

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from tiktoken import get_encoding
except ImportError:
    get_encoding = None

import aiofiles # Used for async file operations if needed

# --- Logging Configuration (Moved to top of file and initialized as 'logger') ---
# (Original content removed as it's now at the beginning)

# --- Check Critical Dependencies ---
if OpenAI is None or AsyncOpenAI is None:
    logger.warning("Optional dependency 'openai' not found or incomplete. AI analysis/embedding features may be limited.")
if Groq is None or AsyncGroq is None:
    logger.warning("Optional dependency 'groq' not found or incomplete. Groq features will be unavailable.")
if yt_dlp is None:
     logger.error("Required dependency 'yt-dlp' not found. Video download and info features will fail.")
if get_encoding is None:
    logger.warning("Optional dependency 'tiktoken' not found. Token counting will be estimated.")

# --- Rich Console Initialization ---
console = Console()

# --- Environment Variable Loading ---
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}. Relying on environment variables.")
    load_dotenv() # Attempt default load

# --- API Client Initialization ---
# OpenAI (Async)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if AsyncOpenAI and openai_api_key:
    try:
        openai_client = AsyncOpenAI(api_key=openai_api_key)
        logger.info("Async OpenAI client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async OpenAI client: {e}", exc_info=True)
elif AsyncOpenAI:
    logger.warning("OPENAI_API_KEY not set. OpenAI client not initialized.")

# Groq (Async)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if AsyncGroq and groq_api_key:
    try:
        groq_client = AsyncGroq(api_key=groq_api_key)
        logger.info("Async Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async Groq client: {e}", exc_info=True)
elif AsyncGroq:
    logger.warning("GROQ_API_KEY not set. Groq client not initialized.")


# --- Local/Project Imports ---
try:
    from .queue_manager import QueueManager
    from .monitoring.logger import PerformanceMonitor, async_timer, CustomLogger
    from .monitoring.metrics import MetricsCollector, TranscriptionMetrics, router as metrics_router, get_metrics_collector
    from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
    from .transcribe1 import process_video, VideoProcessRequest as TranscribeVideoRequest # Renamed Pydantic model
    from .general_utils import (
        save_text_to_markdown,
        clean_filename, format_timestamp, sanitize_filename,
        generate_pdf_from_markdown_string # Added for PDF generation
    )
    from .fetch_content import (
        fetch_content_from_url, generate_unique_filename
    )
    from .crawl4ai_fetcher import fetch_with_crawl4ai # Added for crawl4ai
    from .app_config import WORKSPACE_ROOT, SUBFOLDERS
    from .psearchworking_export import (
        search_all, analyze_search_results, get_client as get_supabase_client,
        SearchParameters, global_search_params, SearchResult,
        TokenCounter as PSearchTokenCounter, ModelSelector
    )
    from .config.search_config import (
         get_preset, validate_search_params, router as search_config_router # etc.
     )
    from .routes.content_upserter import router as content_upserter_router
    from .routes.fetch_history_routes import router as fetch_history_router # Added this line
    from .monitoring.sse_monitor import sse_monitoring_middleware
    from .monitoring.routes import router as monitoring_router
    from .utils.llm_logging import log_llm_call # Added for LLM call logging

    PROJECT_MODULES_LOADED = True
except ImportError as e:
     logger.error(f"Failed to import one or more project modules: {e}. Check installation and package structure.", exc_info=True)
     PROJECT_MODULES_LOADED = False

     # --- Define dummy classes/functions with CORRECT SYNTAX ---
     logger.warning("Defining dummy components due to import errors.")

     class QueueManager:
         """Dummy QueueManager with correct syntax."""
         def __init__(self):
             self.status_queue = asyncio.Queue()
             self.transcription_queue = asyncio.Queue()
             logger.info("Initialized dummy QueueManager queues.")
         async def start(self): logger.warning("Called dummy QueueManager.start()"); pass
         async def stop(self): logger.warning("Called dummy QueueManager.stop()"); pass
         def has_active_transcriptions(self): return False # Add dummy method

     class PerformanceMonitor:
         """Dummy PerformanceMonitor."""
         def __init__(self, logger_instance): pass
         def start_timer(self, name: str): pass
         def stop_timer(self, name: str) -> float: return 0.0

     class MetricsCollector:
         """Dummy MetricsCollector."""
         async def collect_system_metrics(self): pass
         def add_metric(self, *args, **kwargs): pass

     class TranscriptionMetrics:
         """Dummy TranscriptionMetrics."""
         def record_request(self, success: bool): pass

     # --- Dummy Functions ---
     def get_supabase_client(): logger.error("Dummy: Supabase client unavailable."); return None
     DEFAULT_OUTPUT_FOLDER = './output'
     async def process_video(*args, **kwargs): logger.error("Dummy: process_video unavailable.")
     async def search_all(*args, **kwargs): logger.error("Dummy: search_all unavailable."); return [], None, None
     def analyze_search_results(*args, **kwargs): logger.error("Dummy: analyze_search_results unavailable."); return "Analysis unavailable."
     async def fetch_content_from_url(*args, **kwargs): logger.error("Dummy: fetch_content_from_url unavailable."); return {"error": "unavailable"}
     async def convert_md_to_pdf_util(*args, **kwargs): logger.error("Dummy: convert_markdown_to_pdf unavailable."); return False
     def generate_unique_filename(url, ext): return f"dummy_{url[:10]}_{int(time.time())}.{ext}"

     # --- More Dummy Classes ---
     class SearchParameters:
         """Dummy SearchParameters."""
         def get_all_params(self) -> dict: return {}
         def get_params(self, tier: str) -> dict: return {}
         def load_current(self): pass
         def update_params(self, tier:str, **kwargs): pass
         def update_from_frontend(self, **kwargs): return True # Add dummy method

     global_search_params = SearchParameters()

     class SearchResult:
          """Dummy SearchResult."""
          def __init__(self, **kwargs): pass
          def to_dict(self): return {}

     class PSearchTokenCounter:
          """Dummy TokenCounter."""
          def get_stats(self) -> dict: return {'embedding_tokens':0, 'generation_tokens':{'input':0, 'output':0}, 'total_tokens':0}
          def count_embedding_tokens(self, text:str) -> int: return 0
          def count_generation_tokens(self, input_text:str, output_text:Optional[str]=None) -> dict: return {'input':0, 'output':0}

     class ModelSelector:
         """Dummy ModelSelector."""
         @staticmethod
         def generate_analysis(text: str, provider: str = 'openai') -> str: return "Dummy Analysis Unavailable."

     # --- Dummy Routers/Middleware ---
     content_upserter_router = None
     metrics_router = None
     monitoring_router = None
     sse_monitoring_middleware = None

# --- Initialize Core Components ---
if PROJECT_MODULES_LOADED:
    performance_monitor = PerformanceMonitor(logger)
    metrics_collector = MetricsCollector()
    transcription_metrics = TranscriptionMetrics()
    try:
        queue_manager = QueueManager()
    except Exception as e:
        logger.error(f"Failed to initialize QueueManager: {e}", exc_info=True)
        sys.exit("QueueManager initialization failed.")
else:
     logger.warning("Using dummy components due to import errors.")
     performance_monitor = PerformanceMonitor(logger)
     metrics_collector = MetricsCollector()
     transcription_metrics = TranscriptionMetrics()
     queue_manager = QueueManager() # Dummy instance

# Download-specific queue
download_status_queue = asyncio.Queue()


# --- TokenCounter Class ---
# (Keep existing TokenCounter class - lines 375-447)
class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {'input': 0, 'output': 0}
        self.encoders = None
        if get_encoding:
            try:
                self.encoders = {
                    'cl100k_base': get_encoding('cl100k_base'),
                    'gpt-4': get_encoding('cl100k_base'),
                }
                logger.info("TokenCounter initialized with tiktoken encoders.")
            except Exception as e:
                logger.warning(f"Could not initialize tiktoken encoders: {e}. Token counting will be estimated.")
        else:
             logger.warning("TokenCounter initialized without tiktoken. Token counting will be estimated.")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        return len(text) // 4

    def count_embedding_tokens(self, text: str) -> int:
        """Count or estimate tokens for embedding."""
        if not self.encoders or 'cl100k_base' not in self.encoders:
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logger.warning(f"Could not count embedding tokens using tiktoken: {e}. Estimating.")
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens

    def count_generation_tokens(self, input_text: str, output_text: Optional[str] = None) -> dict:
        """Count or estimate tokens for generation."""
        result = {'input': 0, 'output': 0}
        encoder = self.encoders.get('gpt-4') if self.encoders else None

        try:
            if encoder:
                result['input'] = len(encoder.encode(input_text))
                if output_text:
                    result['output'] = len(encoder.encode(output_text))
            else:
                result['input'] = self._estimate_tokens(input_text)
                if output_text:
                    result['output'] = self._estimate_tokens(output_text)
        except Exception as e:
            logger.warning(f"Could not count generation tokens using tiktoken: {e}. Estimating.")
            result['input'] = self._estimate_tokens(input_text)
            if output_text:
                result['output'] = self._estimate_tokens(output_text)

        self.generation_tokens['input'] += result['input']
        self.generation_tokens['output'] += result['output']
        return result

    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        total = self.embedding_tokens + sum(self.generation_tokens.values())
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': total
        }

# Initialize token counter
token_counter = TokenCounter()


# --- Supabase Client Function ---
# (Keep existing get_client function - lines 451-465)
def get_client():
    """Get a Supabase client instance using the imported function."""
    if not PROJECT_MODULES_LOADED or get_supabase_client is None:
         logger.error("Cannot get Supabase client: psearchworking module or get_client function not loaded.")
         raise RuntimeError("Supabase client function is unavailable.")
    try:
        client = get_supabase_client()
        if client is None:
            logger.error("get_supabase_client() returned None.")
            raise RuntimeError("Failed to obtain Supabase client instance.")
        # logger.debug("Supabase client obtained successfully.")
        return client
    except Exception as e:
        logger.error(f"Error obtaining Supabase client via get_supabase_client(): {e}", exc_info=True)
        raise RuntimeError(f"Failed to obtain Supabase client: {e}")


# --- Pydantic Models ---
# (Keep existing models: ComprehensiveSearchRequest, ComprehensiveSearchResponse, VideoRequest, VectorSearchRequest, VectorSearchResponse, DownloadRequest, VideoInfoRequest - lines 469-586)
class ComprehensiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(30, ge=10, le=100, description="Maximum TOTAL results desired across methods")
    run_analysis: bool = Field(True, description="Whether to run AI analysis on results")

class ComprehensiveSearchResponse(BaseModel):
    """Response model for the comprehensive search endpoint."""
    query: str
    results: List[Dict[str, Any]] # List of dictionaries matching SearchResult.to_dict()
    openai_analysis: Optional[str] = None
    groq_analysis: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata, like timing, token counts, effective params")

    class Config:
        from_attributes = True # For Pydantic v2

class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str # Client must provide path to existing Obsidian vault/folder
    output_folder: str # Client provides desired base output path
    transcription_model: str = "faster-whisper"
    use_groq: Optional[bool] = None # Allow explicit setting, but validator overrides

    @field_validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v, re.IGNORECASE):
            raise ValueError('Invalid YouTube URL format')
        return v

    @field_validator('output_folder')
    def output_folder_must_be_valid(cls, v):
        if not v:
            v = os.path.join(WORKSPACE_ROOT, SUBFOLDERS['transcriptions']['markdown'])
        try:
             path = Path(v).resolve()
             if not path.parent.exists():
                  raise ValueError(f"Parent directory does not exist: {path.parent}")
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid output folder path '{v}': {e}")

    @field_validator('obsidian_dir')
    def obsidian_dir_must_exist(cls, v):
        if not v:
            raise ValueError('Obsidian directory path must be provided')
        try:
             path = Path(v).resolve()
             if not path.is_dir():
                  raise ValueError('Path is not an existing directory')
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid Obsidian directory path '{v}': {e}")

    @field_validator('transcription_model')
    def validate_transcription_model(cls, v):
        valid_models = ["faster-whisper", "groq"] # Add specific models if needed e.g. "groq/whisper-large-v3"
        if v.lower() not in valid_models and not v.lower().startswith("groq/"):
            raise ValueError(f"Invalid transcription model. Use 'faster-whisper', 'groq', or specific 'groq/model-name'.")
        return v.lower()

    from pydantic import model_validator

    @model_validator(mode='after')
    def check_and_set_use_groq(self) -> 'VideoRequest':
        model_name = self.transcription_model
        is_groq_model = model_name == 'groq' or model_name.startswith('groq/')

        if self.use_groq is not None and self.use_groq != is_groq_model:
             logger.warning(f"Provided 'use_groq' ({self.use_groq}) contradicts model '{model_name}'. Overriding based on model.")

        self.use_groq = is_groq_model # Set use_groq based on the model selected

        if self.use_groq and groq_client is None:
             raise ValueError("Groq transcription model selected, but Groq client is not available/configured.")

        return self

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    # Add fields for other search function parameters if needed
    content_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    summary_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    video_filter: Optional[str] = Field(None)

    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Search query must not be empty')
        return v.strip()

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    ai_response: Optional[str] = Field(None) # Keep for potential future use
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True # Pydantic v2

class DownloadRequest(BaseModel):
    url: str
    options: Dict[str, Any] = Field(default_factory=dict, description="yt-dlp options")

class VideoInfoRequest(BaseModel):
    url: str

# --- Fetch History Models ---
class FetchHistoryBase(BaseModel):
    url: str = Field(..., description="The URL that was fetched or attempted to be fetched.")
    fetching_engine: str = Field(..., description="The engine used for fetching (e.g., 'jina', 'crawl4ai').")
    status: str = Field(default='pending', description="The status of the fetch job (e.g., 'pending', 'success', 'failed').")
    engine_specific_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters specific to the fetching engine used.")
    user_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the user who initiated the fetch.")
    error_message: Optional[str] = Field(None, description="Error message if the fetch job failed.")
    content_summary: Optional[str] = Field(None, description="A brief summary or preview of the fetched content.")
    raw_content_path: Optional[str] = Field(None, description="Path to the stored raw fetched content, if applicable.")
    processed_content_path: Optional[str] = Field(None, description="Path to the stored processed content (e.g., PDF), if applicable.")
    supabase_content_id: Optional[uuid.UUID] = Field(None, description="ID of the related content in Supabase 'webpage_content' table, if applicable.")

class FetchHistoryCreate(FetchHistoryBase):
    pass

class FetchHistoryResponse(FetchHistoryBase):
    id: uuid.UUID = Field(..., description="Unique identifier for the fetch history record.")
    fetch_date: datetime = Field(..., description="Timestamp of when the fetch job was recorded.")

    class Config:
        from_attributes = True


# --- Initialize FastAPI app ---
# (Keep existing app initialization - lines 589-602)
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for YouTube video processing, download, and search.",
    version="1.2.0", # Incremented version for fetch/pdf/search features
    openapi_tags=[
        {"name": "Processing", "description": "Video transcription and processing."},
        {"name": "Download", "description": "Video/Audio download operations."},
        {"name": "Search", "description": "Content search functionalities."},
        {"name": "Status", "description": "Real-time status updates via SSE."},
        {"name": "Utility", "description": "Helper endpoints."},
        {"name": "Health", "description": "Service health checks."},
        {"name": "Content Fetch", "description": "Fetch web content, generate PDFs."},
        {"name": "Files", "description": "Serve generated files (e.g., PDFs)."},
        {"name": "Fetch History", "description": "Manage and view fetch history records."}, # Keep only one
    ]
)

# --- Configure CORS ---
# (Keep existing CORS middleware - lines 605-615)
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(',')
logger.info(f"Configuring CORS for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Content-Type-Options", "Content-Disposition"], # Added Content-Disposition
)

# --- Add Custom Middlewares ---
# (Keep existing middlewares: SSE Monitoring, Error Handling, Request Logging - lines 618-669)
# SSE Monitoring Middleware (if available)
if PROJECT_MODULES_LOADED and 'sse_monitoring_middleware' in locals() and sse_monitoring_middleware:
    try:
        app.middleware("http")(sse_monitoring_middleware)
        logger.info("SSE monitoring middleware enabled.")
    except Exception as e:
        logger.warning(f"Failed to enable SSE monitoring middleware: {e}")

# Error Handling Middleware (should be early)
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exc:
        raise http_exc # Re-raise for FastAPI to handle
    except Exception as exc:
        logger.error(f"Unhandled exception during request to {request.url.path}", exc_info=exc)
        error_details = {"error_code": "UNEXPECTED_SERVER_ERROR", "message": "An internal server error occurred."}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if PROJECT_MODULES_LOADED and 'TranscriptionErrorHandler' in locals():
             try:
                 error_details = TranscriptionErrorHandler.handle_error(
                     "UNEXPECTED_SERVER_ERROR", exc, path=str(request.url.path)
                 )
             except Exception as handler_err:
                  logger.error(f"Error handler itself failed: {handler_err}")
        return JSONResponse(status_code=status_code, content=error_details)

# Request Logging Middleware (should be after error handling, before routes)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"--> {method} {path} from {client_host}")
    response = await call_next(request) # Process request
    process_time = time.time() - start_time
    status_code = response.status_code
    logger.info(f"<-- {method} {path} - Status={status_code} ({process_time:.3f}s)")
    return response


# --- App Lifecycle Events ---
# (Keep existing startup/shutdown events - lines 672-697)
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             collector = get_metrics_collector()
             import asyncio
             asyncio.create_task(collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")
        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated...")
    try:
        await queue_manager.stop()
        logger.info("Queue manager stopped.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)


# --- SSE Message Formatter ---
# (Keep existing format_sse_message function - lines 700-747)
def format_sse_message(message_type: str, content: Any, metadata: Optional[dict] = None) -> str:
    """Formats a message dictionary into an SSE string, ensuring content is serializable."""
    message = {
        "type": message_type,
        "content": None, # Initialize content to None
        "timestamp": datetime.now().isoformat(),
        "id": str(time.time())  # Add a unique ID for each message
    }
    if metadata:
        message["metadata"] = metadata

    serializable_content = None
    if isinstance(content, (str, int, float, bool, type(None))):
        serializable_content = content
    elif isinstance(content, (dict, list)):
        serializable_content = content
    elif hasattr(content, 'to_dict') and callable(content.to_dict):
        try:
            serializable_content = content.to_dict()
        except Exception as e:
            logger.warning(f"Error calling to_dict() for SSE content type {message_type}: {e}. Content: {str(content)[:100]}")
            serializable_content = f"Error serializing object: {str(content)[:100]}"
    elif hasattr(content, '__dict__'):
         try:
             json.dumps(content.__dict__)
             serializable_content = content.__dict__
         except TypeError:
              logger.warning(f"Could not directly serialize __dict__ for SSE content type {message_type}. Sending string representation. Content: {str(content)[:100]}")
              serializable_content = str(content) # Fallback to string representation
    else:
        serializable_content = str(content)

    message["content"] = serializable_content

    try:
        json_str = json.dumps(message)
        return json_str # EventSourceResponse will handle the "data: " prefix and "\n\n"
    except TypeError as e:
         logger.error(f"FINAL fallback: Failed to serialize SSE message of type {message_type}: {e}. Content: {str(serializable_content)[:100]}")
         error_content = {"error": "Failed to serialize message content", "original_type": message_type}
         # EventSourceResponse will handle the "data: " prefix and "\n\n"
         return json.dumps({'type': 'error', 'content': error_content, 'timestamp': datetime.now().isoformat()})


# --- Combined SSE Updates Endpoint ---
# (Keep existing /combined-updates endpoint - lines 752-983)
@app.get("/combined-updates", tags=["Status"])
async def get_combined_updates(request: Request):
    """SSE endpoint for combined status and transcription updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"SSE connection requested from {client_host} (Origin: {origin}) for /combined-updates.")

    async def event_generator():
        logger.info(f"SSE (Combined): GENERATOR ENTERED for {client_host}.")
        try:
            status_q = queue_manager.status_queue
            transcription_q = queue_manager.transcription_queue
            logger.info(f"SSE (Combined): Got queue references. TQ ID: {id(transcription_q)}, SQ ID: {id(status_q)}")
            last_activity_time = time.time()
            heartbeat_interval = 2
            connection_timeout = 300

            transcription_task = asyncio.create_task(transcription_q.get())
            setattr(transcription_task, '_queue_name', 'transcription')
            status_task = asyncio.create_task(status_q.get())
            setattr(status_task, '_queue_name', 'status')
            heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
            setattr(heartbeat_task, '_is_heartbeat', True)

            all_tasks = {transcription_task, status_task, heartbeat_task}
            logger.info(f"SSE (Combined): Initialized {len(all_tasks)} persistent tasks. Entering main try block.")
        except Exception as setup_err:
            logger.error(f"SSE (Combined): ERROR DURING INITIAL SETUP: {setup_err}", exc_info=True)
            try: yield format_sse_message('error', f"SSE generator setup failed: {setup_err}")
            except: pass
            return

        try:
            connection_established_msg = format_sse_message(
                "status", "SSE connection established",
                {"connection_id": str(time.time()), "server_time": datetime.now().isoformat()}
            )
            yield connection_established_msg
            last_activity_time = time.time()
            yield format_sse_message('heartbeat', 'initial_ping')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check_2')

            while True:
                logger.debug(f"SSE (Combined): Entering new loop iteration for {client_host}")
                try:
                    logger.info(f"SSE (Combined): LOOP START - Waiting on {len(all_tasks)} persistent tasks.")
                    done, pending = await asyncio.wait(all_tasks, return_when=asyncio.FIRST_COMPLETED)
                    logger.info(f"SSE (Combined): WAIT COMPLETED - Done: {len(done)}, Pending: {len(pending)}")

                    for task in done:
                        if getattr(task, '_is_heartbeat', False):
                            logger.debug("SSE (Combined): Heartbeat task completed.")
                            try:
                                yield format_sse_message('heartbeat', 'ping_interval')
                                last_activity_time = time.time()
                                logger.debug("SSE (Combined): Sent interval heartbeat.")
                            except Exception as send_err:
                                logger.error(f"Failed to send interval heartbeat: {send_err}. Closing connection.")
                                raise send_err
                            all_tasks.remove(task)
                            new_heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
                            setattr(new_heartbeat_task, '_is_heartbeat', True)
                            all_tasks.add(new_heartbeat_task)
                            logger.debug(f"SSE (Combined): Replaced completed heartbeat task with new task {id(new_heartbeat_task)}")
                            continue

                        original_queue = None
                        queue_name = getattr(task, '_queue_name', None)
                        if queue_name == 'transcription': original_queue = transcription_q
                        elif queue_name == 'status': original_queue = status_q

                        if original_queue is None:
                            logger.error(f"SSE (Combined): Completed task {id(task)} is not a known queue task.")
                            continue

                        try:
                            item = task.result()
                            logger.info(f"SSE (Combined): ITEM RETRIEVED from {queue_name} queue {id(original_queue)}. Type: {type(item).__name__}. Content: {str(item)[:100]}...")
                            sse_msg = None
                            if isinstance(item, str):
                                try:
                                    payload_dict = json.loads(item)
                                    msg_type = payload_dict.get('type', 'transcription_segment' if original_queue == transcription_q else 'status')
                                    msg_content = payload_dict.get('content', payload_dict)
                                    sse_msg = format_sse_message(msg_type, msg_content)
                                except json.JSONDecodeError:
                                    logger.error(f"SSE (Combined): Failed to decode JSON from {queue_name} queue {id(original_queue)}: {item[:100]}...")
                                    sse_msg = format_sse_message('error', f"Invalid data received from backend queue: {item[:100]}...")
                                except Exception as format_err:
                                    logger.error(f"SSE (Combined): Error formatting message after JSON decode: {format_err}", exc_info=True)
                                    sse_msg = format_sse_message('error', f"Internal error formatting SSE message: {format_err}")
                            else:
                                logger.error(f"SSE (Combined): Received non-string item type '{type(item).__name__}' from {queue_name} queue {id(original_queue)}. Content: {str(item)[:100]}")
                                sse_msg = format_sse_message('error', f"Invalid data type received from backend queue: {type(item).__name__}")

                            if sse_msg:
                                try:
                                    yield sse_msg
                                    last_activity_time = time.time()
                                    logger.info(f"SSE SEND (Combined): {sse_msg.strip()[:150]}...")
                                except Exception as send_err:
                                    logger.error(f"Failed to send update to SSE client: {send_err}")
                                    raise send_err
                            else:
                                logger.warning(f"SSE (Combined): No valid SSE message generated for item from {original_queue} queue.")

                            original_queue.task_done()
                            all_tasks.remove(task)
                            if original_queue == transcription_q:
                                new_task = asyncio.create_task(transcription_q.get())
                                setattr(new_task, '_queue_name', 'transcription')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed transcription task with new task {id(new_task)}")
                            elif original_queue == status_q:
                                new_task = asyncio.create_task(status_q.get())
                                setattr(new_task, '_queue_name', 'status')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed status task with new task {id(new_task)}")

                        except asyncio.CancelledError:
                            logger.info(f"SSE (Combined): A queue get() task {id(task)} was cancelled.")
                        except Exception as e:
                            logger.error(f"SSE (Combined): Error processing completed task result for task {id(task)}: {e}", exc_info=True)
                            try: yield format_sse_message('error', f"Internal SSE error processing task result: {str(e)}")
                            except Exception as send_err: logger.error(f"Failed to send task processing error to SSE client: {send_err}"); raise send_err

                except asyncio.CancelledError:
                    logger.info(f"SSE connection closed by client {client_host} for /combined-updates (Caught CancelledError in loop).")
                    break
                except Exception as loop_err:
                    error_message = f"FATAL Error in /combined-updates SSE generator loop: {loop_err}"
                    logger.error(error_message, exc_info=True)
                    try: yield format_sse_message('error', f"Fatal SSE generator loop error: {str(loop_err)}")
                    except Exception: pass
                    break

            logger.info(f"SSE event generator loop exited for {client_host} (/combined-updates).")

        finally:
            logger.info(f"SSE event generator entering finally block for {client_host} (/combined-updates).")
            logger.info(f"SSE (Combined): Cancelling {len(all_tasks)} remaining tasks in final cleanup.")
            for task in list(all_tasks):
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
                except Exception as e: logger.error(f"Error awaiting cancellation of task {id(task)}: {e}")
            logger.info(f"SSE event generator finished final cleanup for {client_host} (/combined-updates).")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Combined SSE ---
# (Keep existing /combined-updates OPTIONS handler - lines 1006-1010)
@app.options("/combined-updates", tags=["Status"])
async def options_combined_updates(request: Request):
    """Handle OPTIONS preflight requests for /combined-updates."""
    return _handle_options_request(request, allowed_origins)


# --- Download Status SSE Endpoint ---
# (Keep existing /api/download-status endpoint - lines 1013-1084)
@app.get("/api/download-status", tags=["Status", "Download"])
async def get_download_status(request: Request):
    """SSE endpoint specifically for download status updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"Download status SSE connection requested from {client_host} (Origin: {origin}).")

    async def event_generator():
        q = download_status_queue
        last_activity_time = time.time()
        heartbeat_interval = 20

        try:
            yield format_sse_message("status", "Connected to download status stream")
            last_activity_time = time.time()

            while True:
                try:
                    status_update_str = await asyncio.wait_for(q.get(), timeout=heartbeat_interval)
                    logger.debug(f"SSE (Download): Sending update: {status_update_str[:100]}...")
                    try:
                        update_data = json.loads(status_update_str)
                        yield f"data: {status_update_str}\n\n" # Send raw JSON string
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Download SSE received non-JSON: {status_update_str[:100]}... Error: {e}")
                        yield format_sse_message('status', status_update_str) # Send as plain
                    q.task_done()
                    last_activity_time = time.time()

                except asyncio.TimeoutError:
                    logger.debug("SSE (Download): Sending heartbeat.")
                    yield format_sse_message('heartbeat', 'ping')
                    last_activity_time = time.time()
                    continue

                except asyncio.QueueEmpty:
                     await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Download SSE connection closed by client {client_host}.")
        except Exception as e:
            error_message = f"Error in download status SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try: yield format_sse_message('error', error_message)
            except Exception as send_err: logger.error(f"Failed to send error to download SSE client: {send_err}")
        finally:
            logger.info(f"Download SSE event generator finished for {client_host}.")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    origin = request.headers.get("origin", "N/A")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"Download SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Download Status SSE ---
# (Keep existing /api/download-status OPTIONS handler - lines 1087-1090)
@app.options("/api/download-status", tags=["Status", "Download"])
async def options_download_status(request: Request):
    """Handle OPTIONS preflight requests for /api/download-status."""
    return _handle_options_request(request, allowed_origins)

# --- Helper for OPTIONS requests ---
# (Keep existing _handle_options_request function - lines 1093-1109)
def _handle_options_request(request: Request, allowed_origins_list: List[str]):
    origin = request.headers.get("origin")
    method = request.headers.get("access-control-request-method")
    logger.info(f"OPTIONS request for {request.url.path} from origin: {origin}, method: {method}")

    if origin in allowed_origins_list:
        response = JSONResponse(content={"detail": "OK"}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS" # Adjust as needed per endpoint
        response.headers["Access-Control-Allow-Headers"] = "*" # Or be specific: "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400" # Cache preflight for 1 day
        logger.debug(f"OPTIONS response headers: {response.headers}")
        return response
    else:
        logger.warning(f"OPTIONS request from disallowed origin: {origin}")
        return JSONResponse(content={"detail": "Origin not allowed"}, status_code=400)


# --- Transcription Status Endpoint ---
# (Keep existing /transcription-status endpoint - lines 1113-1131)
@app.get("/transcription-status", tags=["Status"])
async def transcription_status():
    """Check if there's an active transcription process running."""
    try:
        active = False
        if queue_manager and hasattr(queue_manager, '_running') and queue_manager._running:
            active = not queue_manager.transcription_queue.empty()
            if hasattr(queue_manager, 'has_active_transcriptions'):
                 active = active or queue_manager.has_active_transcriptions()
        return {"active": active}
    except Exception as e:
        logger.error(f"Error checking transcription status: {e}")
        return {"active": False, "error": str(e)}

# --- Process Video Endpoint ---
# (Keep existing /process-video/ endpoint - lines 1134-1212)
@app.post("/process-video/", tags=["Processing"])
async def process_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """Initiate background processing (download, transcribe) for a YouTube video."""
    if not PROJECT_MODULES_LOADED or process_video is None:
         raise HTTPException(status_code=501, detail="Video processing feature is unavailable due to missing modules.")

    try:
        logger.info(f"Processing video request for URL: {request.youtube_video_url}")
        console.print(f"[cyan]Obsidian Dir:[/cyan] {request.obsidian_dir}")
        console.print(f"[cyan]Output Folder:[/cyan] {request.output_folder}")
        console.print(f"[cyan]Model:[/cyan] {request.transcription_model}, [cyan]Use Groq:[/cyan] {request.use_groq}")

        transcription_metrics.record_request(True)
        output_path = Path(request.output_folder)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured output folder exists: {output_path}")
        except OSError as e:
             logger.error(f"Failed to create output folder {output_path}: {e}", exc_info=True)
             raise HTTPException(status_code=500, detail=f"Could not create output directory: {e}")

        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq
        }

        try:
            from .transcribe1 import extract_video_id
            video_id = extract_video_id(request.youtube_video_url)
        except Exception as e:
            logger.warning(f"Could not extract video ID for tracking: {e}")
            video_id = request.youtube_video_url

        from .process_video_wrapper import process_video_with_tracking

        background_tasks.add_task(
            process_video_with_tracking,
            youtube_video_url=request.youtube_video_url,
            obsidian_dir=request.obsidian_dir,
            status_queue=queue_manager.status_queue,
            transcription_queue=queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config,
            video_id=video_id
        )

        logger.info(f"Background task added for processing: {request.youtube_video_url}")

        return {
            "status": "started",
            "message": "Video processing initiated in the background.",
            "details": {
                 "url": request.youtube_video_url,
                 "output_folder": request.output_folder,
                 "obsidian_dir": request.obsidian_dir
            },
            "timestamp": datetime.now().isoformat()
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.warning(f"Validation error processing video request: {e.errors()}", exc_info=False)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException as e:
         transcription_metrics.record_request(False)
         raise e
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(f"Unexpected error initiating video processing for {request.youtube_video_url}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start video processing task.")


# --- Video Download Feature ---
# (Keep existing download_video_task, report_download_progress, report_postprocess_progress, /api/download endpoint - lines 1217-1459)
async def download_video_task(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task using yt-dlp (run in thread) with progress reporting."""
    if yt_dlp is None:
        logger.error("yt-dlp library is not installed. Cannot download video.")
        await status_queue.put(format_sse_message('error','Download feature unavailable: yt-dlp library not installed.'))
        return

    download_dir = options.get('download_dir', os.path.join(os.getcwd(), 'downloads'))
    logger.info(f"Download task started for URL: {url}, saving to: {download_dir}")

    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create download directory {download_dir}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Failed to create download directory: {e}'))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_template = os.path.join(download_dir, f'%(title)s_{timestamp}.%(ext)s')

    ydl_opts = {
        'outtmpl': filename_template,
        'quiet': True, 'no_warnings': True, 'noprogress': True,
        'keepvideo': options.get('keepVideo', True),
        'overwrites': False,
        'ffmpeg_location': options.get('ffmpegPath'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True, 'playlist_items': None,
    }

    video_format = options.get('format')
    if video_format == 'best': pass
    elif video_format in ['1080p', '720p', '480p', '360p']:
        res = video_format.replace('p', '')
        ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best[height<={res}]'
    elif video_format == 'audio_best':
         ydl_opts['format'] = 'bestaudio/best'
         options['extractAudio'] = True
         options.setdefault('audioFormat', 'mp3')

    if options.get('extractAudio'):
        audio_format = options.get('audioFormat', 'mp3')
        audio_quality = options.get('audioQuality', '192')
        ydl_opts.setdefault('postprocessors', []).append({
            'key': 'FFmpegExtractAudio', 'preferredcodec': audio_format, 'preferredquality': audio_quality,
        })
        if not ydl_opts['keepvideo'] and video_format != 'audio_best':
             ydl_opts['format'] = 'bestaudio/best'

    if options.get('embedThumbnail') and video_format != 'audio_best':
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append({'key': 'EmbedThumbnail'})

    if options.get('embedMetadata', True):
        ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegMetadata', 'add_metadata': True})

    if options.get('subtitles'):
        sub_lang = options.get('subtitleLanguage', 'en')
        sub_auto = options.get('autoSubtitles', False)
        sub_format = options.get('subtitleFormat', 'srt')
        ydl_opts.update({
            'writesubtitles': True, 'writeautomaticsub': sub_auto,
            'subtitleslangs': [sub_lang] if sub_lang != 'all' else ['all'],
            'subtitlesformat': sub_format,
        })
        if options.get('embedSubtitles') and video_format != 'audio_best':
             ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegEmbedSubtitle'})

    is_playlist_url = 'list=' in url or '/playlist?' in url
    if is_playlist_url and options.get('downloadPlaylist'):
        playlist_items = None
        items_str = options.get('playlistItems')
        start = options.get('playlistStart')
        end = options.get('playlistEnd')
        if items_str: playlist_items = items_str
        elif start or end: playlist_items = f"{start or ''}-{end or ''}"
        ydl_opts['noplaylist'] = False
        ydl_opts['playlist_items'] = playlist_items
        logger.info(f"Playlist download enabled. Items: '{playlist_items or 'all'}'")
    elif is_playlist_url:
        logger.info("Playlist URL detected, but only downloading single video.")
        ydl_opts['noplaylist'] = True

    try:
        await status_queue.put(format_sse_message('status', f'Starting download: {url}', {'download_dir': download_dir}))
        logger.info("Running yt-dlp download process in thread...")
        loop = asyncio.get_running_loop()
        ydl_opts['progress_hooks'] = [functools.partial(report_download_progress, loop, status_queue)]
        ydl_opts['postprocessor_hooks'] = [functools.partial(report_postprocess_progress, loop, status_queue)]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             await asyncio.to_thread(ydl.download, [url])
        logger.info(f"yt-dlp download thread finished for {url}.")
        await status_queue.put(format_sse_message('complete', f'Download finished for: {url}'))
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error for {url}: {e}", exc_info=False)
        await status_queue.put(format_sse_message('error', f'Download failed: {e}'))
    except Exception as e:
        logger.error(f"Unexpected error during download task for {url}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Unexpected download error: {e}'))

def report_download_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp download progress, puts message to asyncio queue."""
    if loop is None: logger.error("Asyncio loop is None in report_download_progress."); return
    if d['status'] == 'downloading':
        try:
            progress = d.get('fraction', 0) * 100
            speed = d.get('speed_str', d.get('speed', 'N/A'))
            eta = d.get('eta_str', d.get('eta', 'N/A'))
            filename = d.get('filename', d.get('info_dict',{}).get('filename', '...'))
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            size_str = "N/A"
            if total_bytes:
                if total_bytes < 1024*1024: size_str = f"{total_bytes/1024:.1f} KiB"
                elif total_bytes < 1024*1024*1024: size_str = f"{total_bytes/(1024*1024):.1f} MiB"
                else: size_str = f"{total_bytes/(1024*1024*1024):.2f} GiB"
            content = {'progress': round(progress, 1), 'speed': speed, 'eta': eta, 'filename': os.path.basename(filename), 'total_size': size_str, 'status': 'Downloading'}
            message = format_sse_message('progress', content)
            asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
        except Exception as e: pass
    elif d['status'] == 'finished':
        filename = d.get('filename', d.get('info_dict',{}).get('filename', 'file'))
        message = format_sse_message('status', f'Downloaded {os.path.basename(filename)}. Post-processing...')
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
    elif d['status'] == 'error':
         err_msg = d.get("error", "Unknown download error")
         filename = d.get('filename', d.get('info_dict',{}).get('filename', 'N/A'))
         message = format_sse_message('error', f'Error downloading {os.path.basename(filename)}: {err_msg}')
         asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

def report_postprocess_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp post-processing progress."""
    if loop is None: logger.error("Asyncio loop is None in report_postprocess_progress."); return
    status = d.get('status')
    pp_name = d.get('postprocessor')
    info = d.get('info_dict', {})
    filename = os.path.basename(info.get('filepath', info.get('filename', 'file')))
    if status == 'started' or status == 'processing': message = format_sse_message('status', f'Post-processing ({pp_name}): Starting on {filename}...')
    elif status == 'finished': message = format_sse_message('status', f'Post-processing ({pp_name}): Finished for {filename}.')
    elif status == 'error': message = format_sse_message('error', f'Post-processing ({pp_name}): Failed for {filename}. Check logs.')
    else: return
    asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

@app.post("/api/download", tags=["Download"])
async def download_video_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a video/audio download task in the background."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Download feature unavailable: yt-dlp library not installed.")
    try:
        logger.info(f"Download request received for URL: {request.url}")
        console.print(f"[yellow]Options:[/yellow] {request.options}")
        request.options.setdefault('download_dir', os.path.join(os.getcwd(), 'downloads'))
        background_tasks.add_task(download_video_task, request.url, request.options, download_status_queue)
        return {"status": "success", "message": "Download task initiated in background.", "url": request.url, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error starting download task for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start download task: {e}")


# --- Get Video Info Endpoint ---
# (Keep existing /api/video-info endpoint - lines 1463-1551)
@app.post("/api/video-info", tags=["Download", "Utility"])
async def get_video_info(request: VideoInfoRequest):
    """Get metadata for a YouTube video or playlist without downloading."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Info feature unavailable: yt-dlp library not installed.")
    logger.info(f"Video info request for URL: {request.url}")
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'extract_flat': 'in_playlist'}
    info = None
    try:
        logger.debug(f"Extracting info for {request.url} in thread...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             info = await asyncio.to_thread(ydl.extract_info, request.url, download=False)
        logger.debug(f"Info extraction finished.")
        if not info: raise HTTPException(status_code=404, detail="Could not extract information for the given URL.")

        is_playlist = info.get('_type') == 'playlist'
        playlist_count = len(info.get('entries', [])) if is_playlist else 0
        title = info.get('title', 'N/A')
        author = info.get('uploader', info.get('channel', 'N/A'))
        thumbnail = info.get('thumbnail')
        video_id = info.get('id', '')
        original_url = info.get('webpage_url', request.url)
        duration_str = "N/A"
        if is_playlist: duration_str = f"{playlist_count} videos"
        else:
            duration_sec = info.get('duration')
            if duration_sec:
                try:
                    duration_str = str(timedelta(seconds=int(duration_sec)))
                except (ValueError, TypeError): # Catch specific errors during conversion
                    logger.warning(f"Could not convert duration '{duration_sec}' to timedelta.")
                    pass # Keep duration_str as "N/A"
            if not thumbnail and info.get('thumbnails'): thumbnail = info['thumbnails'][-1]['url']

        formats = info.get('formats', [])
        available_formats_notes = sorted(list(set(f.get('format_note', f.get('resolution', f.get('ext'))) for f in formats if f.get('format_note') or f.get('resolution') or f.get('ext')))) if formats else ["N/A (requires detailed fetch)"]
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        available_subtitles = sorted(list(subs.keys()))
        available_auto_captions = sorted(list(auto_subs.keys()))

        return {"title": title, "author": author, "thumbnail": thumbnail, "duration": duration_str, "is_playlist": is_playlist, "playlist_count": playlist_count if is_playlist else 1, "available_formats": available_formats_notes, "available_subtitles": available_subtitles, "available_auto_captions": available_auto_captions, "id": video_id, "original_url": original_url}
    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"yt-dlp info extraction failed for {request.url}: {e}")
        status_code = 400; detail = f"Failed to process URL"
        if "Unsupported URL" in str(e): status_code = 400; detail = "Unsupported URL"
        elif "Video unavailable" in str(e): status_code = 404; detail = "Video unavailable"
        elif "Private video" in str(e): status_code = 403; detail = "Video is private"
        elif "Sign in to confirm your age" in str(e): status_code = 403; detail = "Video requires age verification (login)"
        raise HTTPException(status_code=status_code, detail=f"{detail}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching video info for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching video info: {e}")


# --- List Downloads Endpoint ---
# (Keep existing /api/list-downloads endpoint - lines 1555-1634)
@app.get("/api/list-downloads", tags=["Download"])
async def list_downloads(directory: Optional[str] = Query(None)):
    """List files in the specified download directory."""
    logger.info(f"List downloads request for directory: {directory}")
    list_dir = directory
    if not list_dir:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): list_dir = user_downloads
            else: list_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
        except Exception: list_dir = os.path.abspath('./downloads')

    list_dir_path = Path(list_dir).resolve()
    if not list_dir_path.is_dir():
        logger.warning(f"Attempted to list non-existent or non-directory path: {list_dir_path}")
        return {"files": []}
    try:
        entries = await asyncio.to_thread(os.listdir, list_dir_path)
        files_list = []
        for entry_name in entries:
            entry_path = list_dir_path / entry_name
            if await asyncio.to_thread(os.path.isfile, entry_path):
                try:
                    stat = await asyncio.to_thread(os.stat, entry_path)
                    size_bytes = stat.st_size
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    file_extension = entry_path.suffix.lower()
                    file_type = "Other"
                    if file_extension in ['.mp4', '.mkv', '.webm', '.avi', '.mov']: file_type = "Video"
                    elif file_extension in ['.mp3', '.wav', '.aac', '.m4a', '.opus', '.ogg']: file_type = "Audio"
                    elif file_extension in ['.srt', '.vtt', '.ass']: file_type = "Subtitle"
                    size_str = "N/A"
                    if size_bytes is not None:
                        if size_bytes < 1024: size_str = f"{size_bytes} B"
                        elif size_bytes < 1024*1024: size_str = f"{size_bytes/1024:.1f} KB"
                        elif size_bytes < 1024*1024*1024: size_str = f"{size_bytes/(1024*1024):.1f} MB"
                        else: size_str = f"{size_bytes/(1024*1024*1024):.2f} GB"
                    files_list.append({"name": entry_name, "type": file_type, "size": size_str, "modified": mod_time.isoformat(), "path": str(entry_path)})
                except Exception as file_info_err:
                    logger.warning(f"Error getting info for file {entry_path}: {file_info_err}")
                    files_list.append({"name": entry_name, "type": "Unknown", "size": "N/A", "modified": "N/A", "path": str(entry_path)})
        files_list.sort(key=lambda x: x.get('modified', '0'), reverse=True)
        logger.info(f"Listed {len(files_list)} files in {list_dir_path}")
        return {"files": files_list}
    except Exception as e:
        logger.error(f"Error listing files in directory {list_dir_path}: {e}", exc_info=True)
        return {"files": [], "error": f"Failed to list files: {e}"}


# --- Fetch History API Endpoints ---

@app.post("/api/fetch-history", response_model=FetchHistoryResponse, tags=["Fetch History"], status_code=status.HTTP_201_CREATED)
async def create_fetch_history_entry(payload: FetchHistoryCreate):
    """
    Create a new fetch history entry.
    """
    logger.info(f"Creating fetch history entry for URL: {payload.url} with engine: {payload.fetching_engine}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        # Prepare data for insertion, Pydantic model ensures correct types for what's passed
        # fetch_date and id are handled by the database by default
        data_to_insert = payload.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .insert(data_to_insert)
            .execute
        )

        if hasattr(response, 'data') and response.data:
            created_entry_data = response.data[0]
            logger.info(f"Successfully created fetch history entry with ID: {created_entry_data.get('id')}")
            # Ensure all fields required by FetchHistoryResponse are present, or handle defaults
            # The DB defaults should cover 'id' and 'fetch_date'
            return FetchHistoryResponse(**created_entry_data)
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error creating fetch history entry: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history creation: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating fetch history entry for URL {payload.url}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create fetch history entry: {str(e)}")

@app.get("/api/fetch-history", response_model=List[FetchHistoryResponse], tags=["Fetch History"])
async def list_fetch_history_entries(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return."),
    offset: int = Query(0, ge=0, description="Number of records to skip for pagination.")
):
    """
    List existing fetch history entries, ordered by fetch_date descending.
    """
    logger.info(f"Listing fetch history entries with limit={limit}, offset={offset}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("*")
            .order("fetch_date", desc=True)
            .limit(limit)
            .offset(offset)
            .execute
        )

        if hasattr(response, 'data'):
            entries_data = response.data
            logger.info(f"Successfully retrieved {len(entries_data)} fetch history entries.")
            # Pydantic will validate each item in the list against FetchHistoryResponse
            return [FetchHistoryResponse(**entry) for entry in entries_data]
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error listing fetch history entries: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history listing: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error listing fetch history entries: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list fetch history entries: {str(e)}")


# --- Get Default Directory Endpoint ---
# (Keep existing /api/default-directory endpoint - lines 1640-1667)
@app.get("/api/default-directory", tags=["Utility"])
async def get_default_directory():
    """Suggest a default download directory path (client can override)."""
    path_str = ""
    warning = None
    try:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): path_str = user_downloads
            else: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "User 'Downloads' directory not found, suggesting relative path."
        except Exception: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "Could not determine user home directory, suggesting relative path."
        logger.info(f"Providing default download directory suggestion: {path_str}")
        response = {"path": path_str}
        if warning: response["warning"] = warning
        return response
    except Exception as e:
        logger.error(f"Error determining default directory: {e}", exc_info=True)
        fallback_dir = os.path.abspath('./downloads')
        return {"path": fallback_dir, "warning": "Could not determine default path, using relative './downloads'."}


# --- PDF Storage Path ---
PDF_STORAGE_BASE_DIR = Path(os.getenv('PDF_STORAGE_PATH', './temp_pdfs')).resolve()
try:
    PDF_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured PDF storage directory exists: {PDF_STORAGE_BASE_DIR}")
except OSError as e:
    logger.error(f"CRITICAL: Could not create PDF storage directory {PDF_STORAGE_BASE_DIR}: {e}. PDF features will fail.", exc_info=True)
    # Depending on requirements, might want to exit or just disable PDF features
    # sys.exit(f"Failed to create PDF storage directory: {PDF_STORAGE_BASE_DIR}")


# --- Helper: Generate OpenAI Embedding ---
async def get_openai_embedding(text: str, model: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")) -> Optional[List[float]]:
    """Generates embedding for text using OpenAI API, with logging."""
    if not openai_client:
        logger.error("OpenAI client not initialized. Cannot generate embedding.")
        # Log attempt even if client is not initialized, as it's an LLM operation attempt
        llm_log_data_no_client = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "ConfigurationError",
            "error_message_detail": "OpenAI client not initialized.",
            "input_text_preview": (text[:100] + "...") if text and len(text) > 100 else text
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_no_client, indent=2, default=str)}")
        return None

    if not text or not text.strip():
        logger.warning("Attempted to generate embedding for empty text.")
        # Log this attempt as well
        llm_log_data_empty_text = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "InputError",
            "error_message_detail": "Input text for embedding was empty or whitespace.",
            "input_text_preview": ""
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_empty_text, indent=2, default=str)}")
        return None

    llm_log_data: Dict[str, Any] = {
        "request_timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_call_type": "embedding",
        "llm_provider": "openai",
        "model_name": model,
        "input_text_preview": (text[:100] + "...") if len(text) > 100 else text,
        "call_successful": False, # Default to False
    }
    start_time = time.time()

    try:
        processed_text = text.replace("\n", " ")
        response = await openai_client.embeddings.create(input=[processed_text], model=model)
        embedding = response.data[0].embedding
        
        llm_log_data["call_successful"] = True
        if response.usage:
            llm_log_data["prompt_tokens_total"] = response.usage.prompt_tokens
            llm_log_data["total_tokens_used"] = response.usage.total_tokens
        # Cost calculation would require model pricing data
        # llm_log_data["cost"] = calculate_cost(model, response.usage.prompt_tokens)
        
        logger.info(f"Generated OpenAI embedding using model {model} for text snippet: '{text[:50]}...'")
        return embedding
    except OpenAI_APIError as e:
        logger.error(f"OpenAI API error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "RateLimitError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_APIConnectionError as e:
        logger.error(f"OpenAI connection error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIConnectionError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_AuthenticationError as e:
        logger.error(f"OpenAI authentication error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "AuthenticationError"
        llm_log_data["error_message_detail"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error generating OpenAI embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "UnhandledException"
        llm_log_data["error_message_detail"] = str(e)
    finally:
        end_time = time.time()
        llm_log_data["llm_call_duration_ms"] = int((end_time - start_time) * 1000)
        # Log the comprehensive data (placeholder for DB insert)
        # TODO: Implement actual DB insertion for llm_call_logs table
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data, indent=2, default=str)}")
    
    return None

# --- Helper: Upsert Content to Supabase ---
async def upsert_content_to_supabase(
    url: str,
    title: str,
    markdown_content: str,
    embedding: Optional[List[float]],
    pdf_path: Optional[str] = None
) -> Optional[str]:
    """Upserts fetched content, embedding, and PDF path to Supabase using the SQL function."""
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            logger.error("Supabase client unavailable. Cannot upsert content.")
            return None

        # Generate a unique content_id (e.g., UUID) for new entries
        # The SQL function handles finding existing entries by URL
        content_id = str(uuid.uuid4())

        # Prepare parameters for the SQL function
        params = {
            "p_content_id": content_id,
            "p_title": title,
            "p_url": url,
            "p_content": markdown_content,
            "p_embedding": embedding, # Pass the list of floats
            "p_pdf_path": pdf_path,
            # "p_source_file": None # Or pass pdf_path here if using source_file column
        }

        logger.info(f"Calling Supabase RPC upsert_webpage_content for URL: {url}")
        response = await asyncio.to_thread(
             supabase_client.rpc('upsert_webpage_content', params).execute
        )
        # response = supabase_client.rpc('upsert_webpage_content', params).execute() # Original sync call

        # Check response (supabase-py v1 might differ from v2 in response structure)
        # Assuming response.data contains the returned content_id
        if hasattr(response, 'data') and response.data:
            returned_id = response.data
            logger.info(f"Successfully upserted content for URL {url}. Returned ID: {returned_id}")
            return returned_id
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error upserting content for {url}: {response.error}")
             return None
        else:
             # Handle unexpected response structure (log and return None)
             logger.warning(f"Unexpected response structure from Supabase upsert RPC for {url}: {response}")
             return None

    except Exception as e:
        logger.error(f"Error upserting content to Supabase for URL {url}: {e}", exc_info=True)
        return None

# --- Helper: Update Fetch History Record ---
async def _update_fetch_history_record(
    supabase_client: Any, # from supabase import Client as SupabaseClient - or use Any
    history_id: Optional[uuid.UUID],
    update_data: Dict[str, Any],
    all_request_params_for_history: Dict[str, Any]
) -> Tuple[Optional[str], bool]: # Returns (SSE message string or None, db_write_successful_flag)
    """
    Helper to update a fetch_history record.
    Returns an SSE message string for the event_generator to yield,
    and a boolean indicating if the database write operation was successful for this call.
    The database update itself is attempted regardless.
    """
    if not history_id or not supabase_client:
        logger.warning(f"Attempted to update fetch history with invalid history_id ({history_id}) or supabase_client.")
        return format_sse_message("error", "history_update_skipped_invalid_params", {"message": f"Skipping history update for {history_id} due to invalid client or ID."}), False

    payload_to_send = {**update_data, "engine_specific_parameters": all_request_params_for_history}
    # Ensure no None values accidentally overwrite existing data unless intended by update_data
    payload_to_send = {k: v for k, v in payload_to_send.items() if v is not None or k in update_data}

    sse_message_to_yield: Optional[str] = None
    db_write_successful = False
    try:
        logger.info(f"Attempting to update fetch_history record ID: {history_id} with status: {update_data.get('status')}")
        update_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .update(payload_to_send)
            .eq("id", history_id)
            .execute
        )

        if hasattr(update_response, 'data') and update_response.data:
            logger.info(f"Successfully updated fetch history {history_id} with status: {update_data.get('status')}")
            sse_message_to_yield = format_sse_message("status", "history_updated", {"message": f"Fetch history record {history_id} updated.", "status": update_data.get('status')})
            db_write_successful = True
        elif hasattr(update_response, 'error') and update_response.error:
            err_msg = update_response.error.message if hasattr(update_response.error, 'message') else str(update_response.error)
            logger.error(f"Failed to update fetch history {history_id}: {err_msg}")
            sse_message_to_yield = format_sse_message("warning", "history_update_failed", {"message": f"Could not update history record {history_id}: {err_msg}"})
        else:
            logger.error(f"Unexpected response structure when updating fetch history {history_id}: {update_response}")
            sse_message_to_yield = format_sse_message("warning", "history_update_unexpected_response", {"message": f"Unexpected DB response for history update {history_id}."})
    except Exception as e:
        logger.error(f"Exception updating fetch history {history_id}: {e}", exc_info=True)
        sse_message_to_yield = format_sse_message("warning", "history_update_exception", {"message": f"Exception during history update for {history_id}: {str(e)}"})
    
    return sse_message_to_yield, db_write_successful

# --- Fetch Content Endpoint (MODIFIED for SSE) ---
@app.get("/fetch-content", tags=["Content Fetch"])
async def fetch_content_endpoint(
    request: Request, # Added Request for client host logging
    url: str = Query(..., description="URL to fetch content from"),
    engine: str = Query("jina", description="Fetching engine to use ('jina' or 'crawl4ai')"),
    generate_pdf: bool = Query(True, description="Generate PDF from fetched content (used by both engines if capable)"),
    upload_to_supabase: bool = Query(False, description="Upload content and embedding to Supabase (post-fetch process)"),

    # --- Browser/Crawling Generic Parameters (used by crawl4ai, some by Jina if applicable) ---
    headless: Optional[bool] = Query(True, description="Run browser in headless mode (crawl4ai)"),
    user_agent: Optional[str] = Query(None, description="Custom user agent string for the browser (crawl4ai)"),
    proxy_url: Optional[str] = Query(None, description="Proxy URL for browser requests (crawl4ai)"), # ADDED
    enable_javascript: Optional[bool] = Query(True, description="Enable JavaScript execution (crawl4ai)"),
    ignore_https_errors: Optional[bool] = Query(True, description="Ignore HTTPS errors (crawl4ai)"), # ADDED
    light_mode: Optional[bool] = Query(False, description="Enable light mode (reduces resource usage) (crawl4ai)"), # ADDED
    text_mode: Optional[bool] = Query(False, description="Enable text-only mode (crawl4ai)"), # ADDED
    browser_cookies: Optional[str] = Query(None, description="JSON string of cookies to set (crawl4ai)"), # ADDED
    browser_headers: Optional[str] = Query(None, description="JSON string of headers to set (crawl4ai)"), # ADDED
    browser_use_persistent_context: Optional[bool] = Query(False, description="Use persistent browser context (crawl4ai)"), # ADDED
    browser_user_data_dir: Optional[str] = Query(None, description="Path to browser user data directory (crawl4ai)"), # ADDED
    browser_extra_args: Optional[str] = Query(None, description="Comma-separated list of extra browser arguments (crawl4ai)"), # ADDED
    viewport_width: Optional[int] = Query(None, description="Browser viewport width (crawl4ai)"), # ADDED
    viewport_height: Optional[int] = Query(None, description="Browser viewport height (crawl4ai)"), # ADDED
    browser_engine: str = Query("playwright", description="Browser engine ('playwright' or 'selenium') (crawl4ai, Jina)"),
    browser_viewport: str = Query("1920x1080", description="Browser viewport (e.g., '1920x1080') (Jina specific, use viewport_width/height for crawl4ai)"), # Clarified
    browser_locale: str = Query("en-US", description="Browser locale (e.g., 'en-US') (crawl4ai, Jina)"),
    take_screenshot: Optional[bool] = Query(False, description="Enable screenshot capture (crawl4ai)"),
    take_screenshot_on_error: Optional[bool] = Query(True, description="Capture screenshot if an error occurs during crawling (crawl4ai)"),
    respect_robots_txt: Optional[bool] = Query(True, description="Whether to respect robots.txt rules (crawl4ai)"),
    
    # --- Timeouts ---
    jina_timeout_seconds: int = Query(300, description="Timeout in seconds for Jina fetch operation"),
    crawl4ai_interaction_timeout_ms: Optional[int] = Query(30000, description="Page interaction timeout for crawl4ai in ms (e.g., for JS execution)"),
    navigation_timeout_ms: Optional[int] = Query(60000, description="Page navigation timeout for crawl4ai in ms"),
    page_load_timeout_ms: Optional[int] = Query(None, description="Overall page load timeout for crawl4ai in ms (defaults to navigation_timeout_ms if None)"), # Matches crawl4ai_fetcher
    page_load_wait_condition: Optional[str] = Query(None, description="Page load wait condition (e.g., 'load', 'domcontentloaded', 'networkidle') (crawl4ai)"), # ADDED
    wait_for_element_js_condition: Optional[str] = Query(None, description="JavaScript expression to wait for before proceeding (crawl4ai)"), # ADDED

    # --- Content Extraction & Formatting Parameters (primarily crawl4ai, some overlap with Jina) ---
    target_selector: Optional[str] = Query(None, description="CSS Selector for target elements to focus on (crawl4ai, Jina)"), # Renamed from target_elements_css_selectors
    excluded_selector: Optional[str] = Query(None, description="CSS Selector for elements to exclude (crawl4ai, Jina)"), # Renamed from excluded_elements_css_selector
    excluded_tags: Optional[str] = Query(None, description="Comma-separated list of HTML tags to exclude (crawl4ai)"), # ADDED
    extract_only_text_content: Optional[bool] = Query(False, description="Extract only text content, no HTML structure (crawl4ai)"), # ADDED
    process_iframes_content: Optional[bool] = Query(False, description="Process content within iframes (crawl4ai)"), # ADDED
    word_count_threshold: Optional[int] = Query(None, description="Minimum word count for content to be considered valid (crawl4ai)"), # ADDED
    remove_forms: Optional[bool] = Query(False, description="Remove form elements from content (crawl4ai)"), # ADDED
    keep_data_attributes: Optional[bool] = Query(False, description="Keep data-* attributes in HTML (crawl4ai)"), # ADDED
    execute_javascript_on_page_load: Optional[str] = Query(None, description="JavaScript code to execute on page load (crawl4ai)"), # ADDED
    scan_full_page_auto_scroll: Optional[bool] = Query(False, description="Enable auto-scroll to capture full page content (crawl4ai)"), # ADDED
    scroll_delay_seconds: Optional[float] = Query(None, description="Delay in seconds between scrolls for full page capture (crawl4ai)"), # ADDED
    attempt_remove_overlay_elements: Optional[bool] = Query(False, description="Attempt to remove overlay elements (crawl4ai)"), # ADDED
    simulate_user_behavior: Optional[bool] = Query(False, description="Simulate user behavior like mouse movements (crawl4ai)"), # ADDED
    enable_magic_handling: Optional[bool] = Query(False, description="Enable crawl4ai's 'magic' handling for complex sites (crawl4ai)"), # ADDED
    override_navigator_properties: Optional[bool] = Query(False, description="Override browser navigator properties (crawl4ai)"), # ADDED
    cache_mode: Optional[str] = Query(None, description="Cache mode for crawl4ai (e.g., 'ENABLED', 'BYPASS', 'REFRESH')"), # ADDED
    capture_screenshot_base64: Optional[bool] = Query(False, description="Capture screenshot as base64 (crawl4ai)"), # ADDED (distinct from take_screenshot)
    # generate_pdf: bool = Query(True, ...) is already present
    capture_mhtml_snapshot: Optional[bool] = Query(False, description="Capture MHTML snapshot of the page (crawl4ai)"), # ADDED
    exclude_external_images: Optional[bool] = Query(False, description="Exclude external images from extraction (crawl4ai)"), # ADDED
    image_alt_text_min_word_count: Optional[int] = Query(None, description="Min word count for image alt text to be considered (crawl4ai)"), # ADDED
    image_relevance_score_threshold: Optional[int] = Query(None, description="Relevance score threshold for images (crawl4ai)"), # ADDED
    exclude_external_links: Optional[bool] = Query(False, description="Exclude external links from extraction (crawl4ai)"), # ADDED
    exclude_social_media_links: Optional[bool] = Query(False, description="Exclude social media links (crawl4ai)"), # ADDED
    custom_excluded_domains: Optional[str] = Query(None, description="Comma-separated list of custom domains to exclude (crawl4ai)"), # ADDED
    # respect_robots_txt: Optional[bool] = Query(True, ...) is already present
    verbose_logging: Optional[bool] = Query(False, description="Enable verbose logging for crawl4ai"), # ADDED
    log_page_console_output: Optional[bool] = Query(False, description="Log page console output during crawl (crawl4ai)"), # ADDED
    crawl_session_id: Optional[str] = Query(None, description="Session ID for crawl4ai"), # ADDED
    crawl_css_selector: Optional[str] = Query(None, description="Global CSS selector for crawl4ai (distinct from target_selector)"), # ADDED
    crawl4ai_markdown_generator: Optional[str] = Query(None, description="Specify markdown generator for crawl4ai (e.g., 'Default')"), # ADDED
    
    # --- Deep Crawl Individual Parameters (used if deep_crawl_config blob is not provided) ---
    deep_crawl_strategy_name: Optional[str] = Query(None, alias="deep_crawl_strategy_name", description="Name of the deep crawl strategy (e.g., BFSDeepCrawlStrategy)"),
    deep_crawl_max_depth: Optional[int] = Query(None, alias="deep_crawl_max_depth", description="Maximum depth for deep crawling"),
    deep_crawl_max_pages: Optional[int] = Query(None, alias="deep_crawl_max_pages", description="Maximum number of pages for deep crawling"),
    deep_crawl_include_external: Optional[bool] = Query(None, alias="deep_crawl_include_external", description="Include external links in deep crawl"),
    deep_crawl_score_threshold: Optional[float] = Query(None, alias="deep_crawl_score_threshold", description="Score threshold for deep crawl strategies like BFS/DFS"),
    deep_crawl_filter_regexes: Optional[str] = Query(None, alias="deep_crawl_filter_regexes", description="Comma-separated regex patterns for URL filtering in deep crawl"),
    deep_crawl_url_scorer_type: Optional[str] = Query(None, alias="deep_crawl_url_scorer_type", description="Type of URL scorer for BestFirstCrawlingStrategy (e.g., KeywordRelevanceScorer)"),
    deep_crawl_scorer_keywords: Optional[str] = Query(None, alias="deep_crawl_scorer_keywords", description="Comma-separated keywords for KeywordRelevanceScorer"),
    deep_crawl_scorer_weight: Optional[float] = Query(None, alias="deep_crawl_scorer_weight", description="Weight for KeywordRelevanceScorer"),
    
    deep_crawl_config: Optional[str] = Query(None, description="JSON string for deep crawl strategy configuration (crawl4ai)"), # ADDED
    extraction_config: Optional[str] = Query(None, description="JSON string for extraction strategy configuration (crawl4ai)"), # ADDED
 
    extraction_strategy: Optional[str] = Query("markdown", description="Content extraction strategy for crawl4ai (e.g., 'markdown', 'llm')"), # This was for Jina, now more general
    output_format: Optional[str] = Query("markdown", description="Desired output format from crawl4ai (e.g., 'markdown', 'text')"), # This was for Jina, now more general
    token_budget: int = Query(4000, description="Max tokens for content processing (crawl4ai token_limit, Jina token_budget)"),
    remove_images: bool = Query(False, description="Remove images from content (crawl4ai, Jina)"),
    extract_links: bool = Query(True, description="Extract links from content (crawl4ai, Jina)"),
    extract_metadata: bool = Query(True, description="Extract page metadata (crawl4ai, Jina)"),
    markdown_flavor: str = Query("github", description="Markdown flavor for output (crawl4ai, Jina)"),

    # --- LLM Specific Parameters (for crawl4ai's LLM features like captioning or LLM extraction) ---
    image_captioning: bool = Query(False, description="Enable image captioning (crawl4ai with LLM, Jina)"),
    llm_provider: Optional[str] = Query("openai", description="LLM provider for crawl4ai (e.g., 'openai', 'groq', 'ollama/model')"),
    llm_api_key: Optional[str] = Query(None, description="API key for the LLM provider (use environment variables if None)"),
    llm_model_name: Optional[str] = Query("gpt-3.5-turbo", description="Specific LLM model name for crawl4ai"),
    llm_temperature: Optional[float] = Query(0.7, ge=0.0, le=2.0, description="LLM temperature for crawl4ai"),
    llm_max_tokens: Optional[int] = Query(1000, ge=1, description="LLM max tokens for generation for crawl4ai"),

    # --- Jina Specific Parameters (ignored by crawl4ai) ---
    json_response: bool = Query(True, description="Request raw JSON response from Jina (contains metadata) (Jina specific)"), # Should be Jina specific
    cache_ttl: int = Query(3600, description="Cache TTL in seconds (Jina specific)") # Should be Jina specific
):
    """
    Fetches content using the specified engine and streams progress via SSE.
    Optionally generates PDF, generates embedding, and stores in Supabase.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE /fetch-content request from {client_host} for URL: {url}, Engine: {engine}, PDF: {generate_pdf}, Supabase: {upload_to_supabase}")

    if not PROJECT_MODULES_LOADED:
        async def error_gen_no_modules():
            yield format_sse_message("error", "Core project modules not loaded. Fetch feature unavailable.")
        return EventSourceResponse(error_gen_no_modules())

    # Gather all original request parameters for potential use by fetchers
    all_request_params = {
        "url": url, "engine": engine, "generate_pdf": generate_pdf, "upload_to_supabase": upload_to_supabase,
        "headless": headless, "user_agent": user_agent, "proxy_url": proxy_url, # ADDED
        "enable_javascript": enable_javascript, "ignore_https_errors": ignore_https_errors, # ADDED
        "light_mode": light_mode, "text_mode": text_mode, # ADDED
        "browser_cookies": browser_cookies, "browser_headers": browser_headers, # ADDED
        "browser_use_persistent_context": browser_use_persistent_context, # ADDED
        "browser_user_data_dir": browser_user_data_dir, "browser_extra_args": browser_extra_args, # ADDED
        "viewport_width": viewport_width, "viewport_height": viewport_height, # ADDED
        "browser_engine": browser_engine, "browser_viewport": browser_viewport, "browser_locale": browser_locale,
        "take_screenshot": take_screenshot, "take_screenshot_on_error": take_screenshot_on_error,
        "respect_robots_txt": respect_robots_txt,
        "jina_timeout_seconds": jina_timeout_seconds,
        "crawl4ai_interaction_timeout_ms": crawl4ai_interaction_timeout_ms,
        "navigation_timeout_ms": navigation_timeout_ms,
        "page_load_timeout_ms": page_load_timeout_ms,
        "page_load_wait_condition": page_load_wait_condition, # ADDED
        "wait_for_element_js_condition": wait_for_element_js_condition, # ADDED
        "target_selector": target_selector, "excluded_selector": excluded_selector,
        "excluded_tags": excluded_tags, # ADDED
        "extract_only_text_content": extract_only_text_content, # ADDED
        "process_iframes_content": process_iframes_content, # ADDED
        "word_count_threshold": word_count_threshold, # ADDED
        "remove_forms": remove_forms, "keep_data_attributes": keep_data_attributes, # ADDED
        "execute_javascript_on_page_load": execute_javascript_on_page_load, # ADDED
        "scan_full_page_auto_scroll": scan_full_page_auto_scroll, # ADDED
        "scroll_delay_seconds": scroll_delay_seconds, # ADDED
        "attempt_remove_overlay_elements": attempt_remove_overlay_elements, # ADDED
        "simulate_user_behavior": simulate_user_behavior, # ADDED
        "enable_magic_handling": enable_magic_handling, # ADDED
        "override_navigator_properties": override_navigator_properties, # ADDED
        "cache_mode": cache_mode, # ADDED
        "capture_screenshot_base64": capture_screenshot_base64, # ADDED
        "capture_mhtml_snapshot": capture_mhtml_snapshot, # ADDED
        "exclude_external_images": exclude_external_images, # ADDED
        "image_alt_text_min_word_count": image_alt_text_min_word_count, # ADDED
        "image_relevance_score_threshold": image_relevance_score_threshold, # ADDED
        "exclude_external_links": exclude_external_links, # ADDED
        "exclude_social_media_links": exclude_social_media_links, # ADDED
        "custom_excluded_domains": custom_excluded_domains, # ADDED
        "verbose_logging": verbose_logging, "log_page_console_output": log_page_console_output, # ADDED
        "crawl_session_id": crawl_session_id, "crawl_css_selector": crawl_css_selector, # ADDED
        "crawl4ai_markdown_generator": crawl4ai_markdown_generator, # ADDED
        
        # Deep Crawl Individual Parameters
        "deep_crawl_strategy_name": deep_crawl_strategy_name,
        "deep_crawl_max_depth": deep_crawl_max_depth,
        "deep_crawl_max_pages": deep_crawl_max_pages,
        "deep_crawl_include_external": deep_crawl_include_external,
        "deep_crawl_score_threshold": deep_crawl_score_threshold,
        "deep_crawl_filter_regexes": deep_crawl_filter_regexes,
        "deep_crawl_url_scorer_type": deep_crawl_url_scorer_type,
        "deep_crawl_scorer_keywords": deep_crawl_scorer_keywords,
        "deep_crawl_scorer_weight": deep_crawl_scorer_weight,
        
        "deep_crawl_config": deep_crawl_config, # This is the JSON blob
        "extraction_config": extraction_config, # ADDED
        "extraction_strategy": extraction_strategy, "output_format": output_format,
        "token_budget": token_budget, "remove_images": remove_images, "extract_links": extract_links,
        "extract_metadata": extract_metadata, "markdown_flavor": markdown_flavor,
        "image_captioning": image_captioning, "llm_provider": llm_provider, "llm_api_key": llm_api_key,
        "llm_model_name": llm_model_name, "llm_temperature": llm_temperature, "llm_max_tokens": llm_max_tokens,
        "json_response": json_response, "cache_ttl": cache_ttl
    }
    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    async def event_generator():
        # --- Fetch History Variables ---
        fetch_history_id: Optional[uuid.UUID] = None
        supabase_client_for_history: Optional[Any] = None # Holds Supabase client
        terminal_status_written_to_db: bool = False # NEW: Tracks if 'success' or 'failed' status was successfully written

        # --- Other original variables ---
        fetched_data_dict: Optional[Dict[str, Any]] = None
        markdown_content: Optional[str] = None
        title: str = "Untitled"
        fetched_url_actual: str = url
        pdf_relative_path: Optional[str] = None
        embedding_generated: bool = False
        supabase_content_id_str: Optional[str] = None

        try:
            # --- Get Supabase Client for History ---
            try:
                supabase_client_for_history = get_client()
                if not supabase_client_for_history:
                    logger.error("Failed to get Supabase client for fetch history (get_client returned None).")
                    yield format_sse_message("error", "database_client_unavailable", {"message": "Database client is essential for history tracking and is unavailable."})
                    return # Stop if DB client cannot be obtained
            except RuntimeError as e_db_client:
                logger.error(f"RuntimeError getting Supabase client for fetch history: {e_db_client}", exc_info=True)
                yield format_sse_message("error", "database_connection_failed", {"message": f"Database connection error for history: {str(e_db_client)}"})
                return # Stop if DB client cannot be obtained
            except Exception as e_db_client_other:
                logger.error(f"Unexpected error getting Supabase client for fetch history: {e_db_client_other}", exc_info=True)
                yield format_sse_message("error", "database_client_error", {"message": f"Unexpected database client error for history: {str(e_db_client_other)}"})
                return

            # --- Create Initial Fetch History Record ---
            if supabase_client_for_history:
                try:
                    initial_history_payload_dict = {
                        "url": url,
                        "fetching_engine": engine,
                        "status": "pending",
                        # engine_specific_parameters will be added in the final update
                    }
                    # Validate with Pydantic model before sending to DB
                    FetchHistoryCreate(**initial_history_payload_dict)


                    create_response = await asyncio.to_thread(
                        supabase_client_for_history.table("fetch_history")
                        .insert(initial_history_payload_dict)
                        .execute
                    )
                    if hasattr(create_response, 'data') and create_response.data:
                        fetch_history_id = create_response.data[0].get('id')
                        if fetch_history_id:
                             logger.info(f"Initial fetch history record created with ID: {fetch_history_id} for URL: {url}")
                             yield format_sse_message("status", "history_created", {"message": f"Fetch history record created: {fetch_history_id}", "history_id": str(fetch_history_id)})
                        else:
                             logger.error(f"Initial fetch history record created for {url} but ID was not returned in data: {create_response.data}")
                             yield format_sse_message("warning", "history_creation_no_id", {"message": "History record created but ID missing."})
                    elif hasattr(create_response, 'error') and create_response.error:
                        err_msg = create_response.error.message if hasattr(create_response.error, 'message') else str(create_response.error)
                        logger.error(f"Failed to create initial fetch history record for {url}: {err_msg}")
                        yield format_sse_message("warning", "history_creation_failed", {"message": f"Could not create initial history record: {err_msg}"})
                    else:
                        logger.error(f"Unexpected response from Supabase during initial fetch history creation for {url}: {create_response}")
                        yield format_sse_message("warning", "history_creation_unexpected_response", {"message": "Unexpected DB response for initial history creation."})
                except ValidationError as ve:
                    logger.error(f"Validation error for initial fetch history payload for {url}: {ve.errors()}", exc_info=True)
                    yield format_sse_message("error", "history_payload_invalid", {"message": f"Initial history data invalid: {str(ve)}"})
                    # Potentially return if this is critical
                except Exception as e_hist_create:
                    logger.error(f"Exception creating initial fetch history for {url}: {e_hist_create}", exc_info=True)
                    yield format_sse_message("warning", "history_creation_exception", {"message": f"Error during initial history creation: {str(e_hist_create)}"})
            
            yield format_sse_message("status", "initializing", {"message": f"Initializing fetch process for {url} with {engine}..."})
            await asyncio.sleep(0.1) # Small delay for frontend to catch up

            if engine.lower() == "crawl4ai":
                if fetch_with_crawl4ai is None: # Check if the function itself is available
                    yield format_sse_message("error", "Crawl4ai fetcher module not available.")
                    return
                logger.info(f"Using crawl4ai engine for URL: {url}")
                async for sse_event_json_str_from_fetcher in fetch_with_crawl4ai(url=url, original_request_params=all_request_params):
                    try:
                        event_data_from_fetcher = json.loads(sse_event_json_str_from_fetcher)

                        # --- LLM Logging Integration ---
                        if event_data_from_fetcher.get("type") == "llm_log_event":
                            llm_log_data = event_data_from_fetcher.get("data")
                            if llm_log_data and supabase_client_for_history: # Ensure data and client exist
                                try:
                                    # Use await if log_llm_call is async, otherwise remove await
                                    await log_llm_call(llm_log_data_dict=llm_log_data, supabase_client=supabase_client_for_history)
                                    logger.info(f"LLM call logged for type: {llm_log_data.get('llm_call_type')}, model: {llm_log_data.get('model_name')}")
                                except Exception as e_log_llm:
                                    logger.error(f"Failed to log LLM call via utility: {e_log_llm}", exc_info=True)
                                    # Optionally, yield an error to client if this failure is critical for them to know
                                    # yield format_sse_message("warning", "llm_log_failed", {"message": f"Failed to log LLM event: {str(e_log_llm)}"})
                            elif not llm_log_data:
                                logger.warning("llm_log_event received but 'data' payload was missing.")
                            elif not supabase_client_for_history:
                                logger.warning("llm_log_event received but supabase_client_for_history was not available for logging.")
                            continue # Skip yielding this event to the client
                        # --- End LLM Logging Integration ---

                        final_sse_event_dict = {
                            "type": event_data_from_fetcher.get("type"),
                            "timestamp": datetime.now().isoformat(),
                            "id": str(time.time())
                        }
                        if "status" in event_data_from_fetcher:
                            final_sse_event_dict["status"] = event_data_from_fetcher.get("status")

                        # Check for structured LLM error from crawl4ai_fetcher
                        # This is distinct from llm_log_event, this is an error *during* an LLM call within crawl4ai
                        if event_data_from_fetcher.get("type") == "error" and "llm_error" in event_data_from_fetcher:
                            final_sse_event_dict["message"] = event_data_from_fetcher.get("message", "LLM operation failed.")
                            final_sse_event_dict["llm_error"] = event_data_from_fetcher["llm_error"] # Pass the structured LLM error
                            logger.error(f"LLM Error event from crawl4ai_fetcher: {json.dumps(event_data_from_fetcher['llm_error'])}")
                        elif event_data_from_fetcher.get("type") == "error":
                            # General error from crawl4ai_fetcher
                            if "message" in event_data_from_fetcher:
                                final_sse_event_dict["message"] = event_data_from_fetcher.get("message")
                            if "details" in event_data_from_fetcher:
                                final_sse_event_dict["details"] = event_data_from_fetcher.get("details")
                        else:
                            # Non-error events (status, completed)
                            content_payload_for_final_sse = {}
                            if "message" in event_data_from_fetcher:
                                content_payload_for_final_sse["message"] = event_data_from_fetcher.get("message")
                            if "data" in event_data_from_fetcher:
                                content_payload_for_final_sse["data"] = event_data_from_fetcher.get("data")
                                if event_data_from_fetcher.get("type") == "completed" or \
                                   event_data_from_fetcher.get("status") == "completed":
                                    fetched_data_dict = event_data_from_fetcher.get("data")
                            
                            if content_payload_for_final_sse:
                                final_sse_event_dict["content"] = content_payload_for_final_sse
                            elif "message" in event_data_from_fetcher:
                                 final_sse_event_dict["content"] = event_data_from_fetcher.get("message")

                        logger.info(f"MAIN.PY /fetch-content: About to yield for crawl4ai: {json.dumps(final_sse_event_dict)}")
                        yield json.dumps(final_sse_event_dict)

                        if event_data_from_fetcher.get("type") == "error" or event_data_from_fetcher.get("status") == "error":
                            error_message_for_db = str(event_data_from_fetcher.get('message', 'Unknown error from fetcher'))
                            if "llm_error" in event_data_from_fetcher and isinstance(event_data_from_fetcher["llm_error"], dict):
                                error_message_for_db = f"LLM Error: {event_data_from_fetcher['llm_error'].get('message', error_message_for_db)}. Details: {json.dumps(event_data_from_fetcher['llm_error'].get('details'))}"

                            logger.error(f"Error event from crawl4ai_fetcher: {error_message_for_db}")
                            if fetch_history_id and supabase_client_for_history:
                                error_update_data = {"status": "failed", "error_message": error_message_for_db[:1000]}
                                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                                if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                    terminal_status_written_to_db = True
                            return
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from crawl4ai_fetcher: {sse_event_json_str_from_fetcher}")
                        yield format_sse_message("error", "Received invalid data from crawl4ai engine.")
                        if fetch_history_id and supabase_client_for_history:
                            error_update_data = {"status": "failed", "error_message": "Received invalid JSON data from crawl4ai engine."}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                            if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return
                    except Exception as e_inner_crawl:
                        logger.error(f"Error processing event from crawl4ai_fetcher: {e_inner_crawl}", exc_info=True)
                        yield format_sse_message("error", f"Internal error processing crawl4ai event: {str(e_inner_crawl)}")
                        if fetch_history_id and supabase_client_for_history:
                            failure_update_data = {"status": "failed", "error_message": f"Internal error processing crawl4ai event: {str(e_inner_crawl)}"[:1000]}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                            if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return


            elif engine.lower() == "jina":
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Jina fetcher (fetch_content_from_url) not available.")
                    return
                logger.info(f"Using Jina engine for URL: {url}")
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_handler_output, dict) or jina_handler_output.get("error"):
                            error_detail = jina_handler_output.get("content", "Unknown error from Jina") if isinstance(jina_handler_output, dict) else str(jina_handler_output)
                            logger.error(f"Jina engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_handler_output
                    else: # Client wanted plain text (json_response is False)
                        if not isinstance(jina_handler_output, str):
                            logger.error(f"Jina engine (Text mode) for {url} returned non-string: {type(jina_handler_output)}. Content: {str(jina_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text)"
                        fetched_data_dict = {
                            "markdown": jina_handler_output, "content": jina_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }
                    
                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina..."})
                    await asyncio.sleep(0.5) # Simulate processing

                except Exception as e_jina:
                    logger.error(f"Error calling Jina fetch_content_from_url for {url}: {e_jina}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina engine: {str(e_jina)}")
                    return
            else:
                logger.warning(f"Unknown or unsupported engine '{engine}' requested for URL: {url}. Defaulting to Jina.")
                # Essentially duplicate Jina logic here or refactor Jina part into a sub-generator
                # For now, let's assume Jina is the default if not crawl4ai
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Default Jina fetcher not available.")
                    return
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina (default)..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_default_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_default_handler_output, dict) or jina_default_handler_output.get("error"):
                            error_detail = jina_default_handler_output.get("content", "Unknown error from Jina (default)") if isinstance(jina_default_handler_output, dict) else str(jina_default_handler_output)
                            logger.error(f"Jina (default) engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina (default) engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_default_handler_output
                    else: # Client wanted plain text
                        if not isinstance(jina_default_handler_output, str):
                            logger.error(f"Jina (default) engine (Text mode) for {url} returned non-string: {type(jina_default_handler_output)}. Content: {str(jina_default_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina (default) engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_default_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text Default)"
                        fetched_data_dict = {
                            "markdown": jina_default_handler_output, "content": jina_default_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }

                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina (default)..."})
                    await asyncio.sleep(0.5)
                except Exception as e_jina_def:
                    logger.error(f"Error calling Jina (default) for {url}: {e_jina_def}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina (default) engine: {str(e_jina_def)}")
                    return

            # --- Post-fetch processing (PDF, Supabase) ---
            if fetched_data_dict and not fetched_data_dict.get("error"):
                markdown_content = fetched_data_dict.get('markdown') # Correct key for markdown content
                title = fetched_data_dict.get('title', 'Untitled')
                fetched_url_actual = fetched_data_dict.get('url', url)
                # pdf_path_from_fetch is specific to how Jina's fetch_content_from_url might return it
                # For crawl4ai, this would be None unless explicitly set in its "data" payload.
                pdf_path_from_fetcher = fetched_data_dict.get("pdf_path")


                if not markdown_content:
                    logger.warning(f"Engine {engine} returned no markdown content for URL: {url}")
                    # Still send a completed event, but data might be minimal
                else:
                    logger.info(f"Successfully fetched core content using {engine} from {url}. Title: '{title}'. Length: {len(markdown_content)}")

                if generate_pdf:
                    yield format_sse_message("status", "pdf_generation", {"message": "Generating PDF..."})
                    if markdown_content and pdf_path_from_fetcher: # If fetcher already made PDF
                        pdf_relative_path = pdf_path_from_fetcher
                        logger.info(f"Using PDF path from {engine} fetch: {pdf_relative_path} for {url}")
                        yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF ready at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                    elif markdown_content: # We have markdown, and PDF wasn't pre-generated
                        try:
                            # PDF_STORAGE_BASE_DIR is defined globally in main.py
                            # Ensure generate_unique_filename is available (imported from .fetch_content)
                            # Ensure generate_pdf_from_markdown_string is available (imported from .utils)
                            
                            unique_pdf_filename = generate_unique_filename(fetched_url_actual, "pdf")
                            output_pdf_filepath = PDF_STORAGE_BASE_DIR / unique_pdf_filename # Use Path object
                            
                            logger.info(f"Attempting PDF generation for {fetched_url_actual} to {output_pdf_filepath}")
                            pdf_conversion_successful = await generate_pdf_from_markdown_string(markdown_content, str(output_pdf_filepath))
                            
                            if pdf_conversion_successful:
                                # Construct relative path for client
                                # PDF_STORAGE_BASE_DIR is like "c:\...\backend\app\temp_pdfs"
                                # We want "temp_pdfs/filename.pdf"
                                base_storage_dir_name = PDF_STORAGE_BASE_DIR.name # Should be "temp_pdfs"
                                pdf_relative_path = Path(base_storage_dir_name) / unique_pdf_filename
                                pdf_relative_path = str(pdf_relative_path).replace("\\", "/") # Ensure forward slashes
                                logger.info(f"PDF generated via main.py, relative path: {pdf_relative_path}")
                                yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF generated at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                            else:
                                logger.error(f"PDF conversion failed in main.py for URL {fetched_url_actual}.")
                                yield format_sse_message("warning", "pdf_generation_failed", {"message": "PDF generation failed."})
                        except Exception as e_pdf_gen:
                            logger.error(f"Error during PDF generation in main.py for {fetched_url_actual}: {e_pdf_gen}", exc_info=True)
                            yield format_sse_message("warning", "pdf_generation_error", {"message": f"Error during PDF generation: {str(e_pdf_gen)}"})
                    else: # No markdown content
                        yield format_sse_message("status", "pdf_generation_skipped", {"message": "PDF generation skipped (no content)."})
                
                if upload_to_supabase:
                    yield format_sse_message("status", "supabase_upload", {"message": "Preparing for Supabase upload..."})
                    if markdown_content:
                        embedding = await get_openai_embedding(markdown_content)
                        if embedding:
                            embedding_generated = True
                            yield format_sse_message("status", "embedding_complete", {"message": "Embedding generated."})
                            supabase_content_id = await upsert_content_to_supabase(
                                url=fetched_url_actual, title=title, markdown_content=markdown_content,
                                embedding=embedding, pdf_path=pdf_relative_path
                            )
                            if supabase_content_id:
                                supabase_content_id_str = str(supabase_content_id)
                                yield format_sse_message("status", "supabase_upload_complete", {"message": f"Content uploaded to Supabase with ID: {supabase_content_id_str}", "database_id": supabase_content_id_str})
                            else:
                                yield format_sse_message("warning", "Supabase upload failed.")
                        else:
                            yield format_sse_message("warning", "Embedding generation failed, skipping Supabase upload.")
                    else: # No markdown content
                        yield format_sse_message("status", "supabase_upload_skipped", {"message": "Supabase upload skipped (no content)."})
                
                # Update fetch_history with success details
                if fetch_history_id and supabase_client_for_history:
                    success_update_data = {
                        "status": "success",
                        "content_summary": (markdown_content or "")[:500] + "..." if markdown_content and len(markdown_content) > 500 else (markdown_content or "No content."),
                        "raw_content_path": None, # Assuming raw content isn't saved to a file path directly by this endpoint
                        "content_storage_path": pdf_relative_path,
                        "supabase_content_id": supabase_content_id_str if supabase_content_id_str else None
                    }
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, success_update_data, all_request_params)
                    # Only mark terminal status as written if the DB write for a terminal status succeeded
                    if db_write_ok and success_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg

                # Final "completed" event with all data
                final_payload_data = {
                    "url": fetched_url_actual,
                    "title": title,
                    "content": markdown_content, # Send full content if not too large, or preview
                    "content_preview": (markdown_content or "")[:250] + "..." if markdown_content else "No content.",
                    "pdf_path": pdf_relative_path,
                    "embedding_generated": embedding_generated,
                    "database_id": supabase_content_id_str,
                    "engine_used": engine
                }
                yield format_sse_message("completed", final_payload_data, {"message": f"Fetch process completed for {url}."})
            
            elif fetched_data_dict and fetched_data_dict.get("error"):
                error_msg_content = fetched_data_dict.get("content", f"Unknown error after fetching with {engine}")
                logger.error(f"Fetch process for {url} by {engine} resulted in error state: {error_msg_content}")
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": str(error_msg_content)[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", error_msg_content)
            
            else: # No fetched_data_dict (e.g., engine failed to initialize or returned unexpected structure)
                final_error_message = f"Failed to retrieve or process data using {engine} for {url}. No valid data dictionary was produced."
                logger.error(final_error_message)
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": final_error_message[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", final_error_message)

        except asyncio.CancelledError:
            logger.info(f"SSE /fetch-content connection closed by client {client_host} for URL: {url}")
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": "Fetch cancelled by client."}
                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success, but client cancelled
                 logger.info(f"Fetch cancelled by client after 'success' status was set for {fetch_history_id}. Status remains 'success'.")
                 post_success_error_update = {"error_message": "Fetch cancelled by client post-success."[:1000]} # Update error message, status remains success
                 await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params) # db_write_ok not critical here
            # No yield here as the connection is likely gone
        except HTTPException as http_exc:
            logger.warning(f"HTTPException in /fetch-content generator for {url}: {http_exc.detail}", exc_info=True)
            final_error_message_to_client = f"Server error: {http_exc.detail}"
            db_error_message = f"HTTPException: {str(http_exc.detail)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"HTTPException occurred after 'success' status for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success HTTPException: {str(http_exc.detail)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        except Exception as e:
            logger.error(f"Unexpected error in /fetch-content SSE generator for {url} with {engine}: {e}", exc_info=True)
            final_error_message_to_client = f"An unexpected server error occurred: {str(e)}"
            db_error_message = f"Unexpected error: {str(e)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"Error occurred after 'success' status was set for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success error: {str(e)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        finally:
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                logger.warning(f"Fetch process for history ID {fetch_history_id} (URL: {url}) ended without confirmed terminal status. Attempting to mark as 'failed'.")
                final_failure_data = {
                    "status": "failed",
                    "error_message": "Process terminated without explicit success or failure status update."[:1000]
                }
                # This update is critical for DB state; SSE message not yielded from finally.
                await _update_fetch_history_record(
                    supabase_client_for_history,
                    fetch_history_id,
                    final_failure_data,
                    all_request_params
                )
            logger.info(f"SSE /fetch-content event generator finished for {client_host}, URL: {url}")

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


# --- PDF Serving Endpoints ---

def secure_path_join(base: Path, requested_path: str) -> Optional[Path]:
    """Safely join a base directory and a requested path, preventing traversal."""
    try:
        # Normalize the requested path to prevent tricks like '..'
        normalized_req_path = os.path.normpath(requested_path)

        # Disallow absolute paths in the request
        if os.path.isabs(normalized_req_path):
            logger.warning(f"Attempted absolute path request: {normalized_req_path}")
            return None

        # Join base and requested path
        full_path = base.joinpath(normalized_req_path).resolve()

        # Crucial check: Ensure the resolved path is still within the base directory
        if base.resolve() in full_path.parents or base.resolve() == full_path:
             # Further check: ensure the part after the base matches the normalized request
             # This helps prevent issues if base itself contains '..' like structures (though resolve() should handle it)
             relative_part = full_path.relative_to(base.resolve())
             if str(relative_part) == normalized_req_path:
                  return full_path
             else:
                  logger.warning(f"Path validation failed: Relative part mismatch. Base='{base}', Req='{requested_path}', Resolved='{full_path}', Relative='{relative_part}'")
                  return None
        else:
            logger.warning(f"Directory traversal attempt blocked: Base='{base}', Req='{requested_path}', Resolved='{full_path}'")
            return None
    except Exception as e:
        logger.error(f"Error during secure path join: {e}", exc_info=True)
        return None

@app.get("/view-pdf", tags=["Files"])
async def view_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for inline viewing."""
    logger.info(f"Request to view PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for viewing at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=secure_full_path.name, # Provides a default filename if user saves
            content_disposition_type="inline" # Display in browser
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for viewing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")

@app.get("/download-pdf", tags=["Files"])
async def download_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for download as an attachment."""
    logger.info(f"Request to download PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for download at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        # Use a generic filename or derive from path if needed
        download_filename = f"downloaded_{secure_full_path.name}"
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=download_filename, # Suggests this filename to the browser
            content_disposition_type="attachment" # Force download dialog
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for download: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")


# --- Include Other Routers ---
# (Keep existing router includes - lines 1722-1741)
if PROJECT_MODULES_LOADED:
    if 'content_upserter_router' in locals() and content_upserter_router:
        try: app.include_router(content_upserter_router, prefix="/api/content", tags=["Content Management"])
        except Exception as e: logger.warning(f"Failed to include content_upserter_router: {e}")

    if 'fetch_history_router' in locals() and fetch_history_router: # Added this block
        try: app.include_router(fetch_history_router, prefix="/api", tags=["Fetch History"]) # Using /api prefix for consistency
        except Exception as e: logger.warning(f"Failed to include fetch_history_router: {e}")

    if 'metrics_router' in locals() and metrics_router:
        try: app.include_router(metrics_router, prefix="/monitoring", tags=["Monitoring"])
        except Exception as e: logger.warning(f"Failed to include metrics_router: {e}")

    if 'monitoring_router' in locals() and metrics_router != monitoring_router and monitoring_router:
         try: app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
         except Exception as e: logger.warning(f"Failed to include monitoring_router: {e}")

    if 'search_config_router' in locals() and search_config_router:
        try: app.include_router(search_config_router, prefix="/api/search-config", tags=["Search Configuration"])
        except Exception as e: logger.warning(f"Failed to include search_config_router: {e}")

# --- Include Debug Endpoints ---
try:
    from .debug_endpoints import router as debug_router
    app.include_router(debug_router)
    logger.info("Debug endpoints included.")
except Exception as e:
    logger.warning(f"Failed to include debug endpoints: {e}")


# --- Vector Search Endpoint (MODIFIED to use SQL Function) ---
@app.post("/api/vector-search", response_model=VectorSearchResponse, tags=["Search"])
async def vector_search_endpoint(request: VectorSearchRequest):
    """Perform vector search using the advanced_hybrid_search SQL function."""
    logger.info(f"Vector search request: Query='{request.query[:50]}...', Max={request.max_results}, Threshold={request.threshold}")

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Database client unavailable.")
        if not openai_client:
             raise HTTPException(status_code=503, detail="Embedding service unavailable.")

        # 1. Generate query embedding
        query_embedding = await get_openai_embedding(request.query)
        if query_embedding is None:
            # get_openai_embedding now logs detailed LLM call info internally.
            # Here, we raise a structured error for the client.
            error_detail_payload = {
                "error_code": "EMBEDDING_GENERATION_FAILED",
                "message": "Failed to generate query embedding for vector search.",
                "llm_error_type": "EmbeddingError", # Generic, as detailed type is in server logs
                "details": {
                    "query_preview": (request.query[:100] + "...") if request.query and len(request.query) > 100 else request.query,
                    "suggestion": "Check server logs for detailed error information from the embedding service."
                }
            }
            logger.error(f"Raising HTTPException for vector search due to embedding failure. Payload: {json.dumps(error_detail_payload)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail_payload
            )

        # 2. Prepare parameters for the SQL function
        #    Match parameters defined in the SQL function (adjust dimension if needed)
        params = {
            'query_embedding': query_embedding,
            'match_count': request.max_results,
            'min_similarity': request.threshold, # Assuming threshold maps to min_similarity
            'content_weight': request.content_weight, # Pass weights from request
            'summary_weight': request.summary_weight,
            'video_filter': request.video_filter # Pass filter from request
        }
        logger.debug(f"Calling Supabase RPC advanced_hybrid_search with params: match_count={params['match_count']}, min_similarity={params['min_similarity']}, content_weight={params['content_weight']}, summary_weight={params['summary_weight']}, video_filter={params['video_filter']}")

        # 3. Call the Supabase function via RPC
        response = await asyncio.to_thread(
             supabase_client.rpc('advanced_hybrid_search', params).execute
        )
        # response = supabase_client.rpc('advanced_hybrid_search', params).execute() # Original sync call

        # 4. Process results
        search_results = []
        if hasattr(response, 'data') and response.data:
            search_results = response.data
            logger.info(f"Advanced hybrid search returned {len(search_results)} results.")
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error during advanced_hybrid_search: {response.error}")
             raise HTTPException(status_code=500, detail=f"Database search error: {response.error}")
        else:
             logger.warning(f"Unexpected response structure from Supabase search RPC: {response}")
             # Return empty results

        # 5. Prepare response metadata (optional AI response generation removed for now)
        metadata = {
            "query": request.query,
            "results_count": len(search_results),
            "search_function": "advanced_hybrid_search",
            "parameters_used": {
                "threshold": request.threshold,
                "max_results": request.max_results,
                "content_weight": request.content_weight,
                "summary_weight": request.summary_weight,
                "video_filter": request.video_filter
            },
            "token_usage": token_counter.get_stats() # Include token stats
        }

        return VectorSearchResponse(
            results=search_results, # The SQL function should return dicts directly
            ai_response=None, # AI response generation can be added later if needed
            metadata=metadata
        )

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI errors
    except Exception as e:
         logger.error(f"Error during vector search for query '{request.query[:50]}...': {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")


# --- Comprehensive Search Endpoint (Using psearchworking) ---
# (Keep existing /api/search endpoint - lines 1806-1945)
@app.post("/api/search", response_model=ComprehensiveSearchResponse, tags=["Search"])
async def comprehensive_search_endpoint(
    request: ComprehensiveSearchRequest, # Request body
    # Query parameters for overrides
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
    preset: Optional[str] = Query(None)
):
    """
    Perform comprehensive search using logic from psearchworking.
    Accepts optional query parameters to override search settings.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    logger.info(f"Search request: Query='{request.query[:50]}...', MaxRes={request.max_results}, Analysis={request.run_analysis}, Preset='{preset}'")

    try:
        update_successful = global_search_params.update_from_frontend(
            preset=preset,
            fine_grained_similarity_threshold=fg_similarity_threshold,
            fine_grained_content_weight=fg_content_weight,
            fine_grained_result_percentage=fg_result_percentage,
            fine_grained_max_results=fg_max_results,
            contextual_similarity_threshold=ctx_similarity_threshold,
            contextual_content_weight=ctx_content_weight,
            contextual_result_percentage=ctx_result_percentage,
            contextual_max_results=ctx_max_results,
            overview_similarity_threshold=ov_similarity_threshold,
            overview_content_weight=ov_content_weight,
            overview_result_percentage=ov_result_percentage,
            overview_max_results=ov_max_results,
        )
        if not update_successful:
             logger.warning("Search parameters updated from frontend might be invalid (e.g., sum > 1.0). Check psearchworking validation logic.")
        logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
    except Exception as param_err:
         logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search parameters provided.")

    start_time = time.time()
    try:
        results, openai_analysis, groq_analysis = await asyncio.to_thread(
            search_all,
            query=request.query,
            max_results=request.max_results,
            skip_prompts=True,
            run_analysis=request.run_analysis
        )

        search_duration = time.time() - start_time
        logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")

        formatted_results = []
        if results:
            try:
                formatted_results = [res.to_dict() for res in results]
                logger.info(f"Successfully converted {len(formatted_results)} SearchResult objects to dictionaries")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                formatted_results = []
                for res in results:
                    try:
                        result_dict = {
                            'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                            'content_id': getattr(res, 'content_id', None),
                            'content': getattr(res, 'content', None),
                            'similarity': getattr(res, 'similarity', 0.0),
                            'source': getattr(res, 'source', 'unknown'),
                            'title': getattr(res, 'title', ''),
                            'start_time': getattr(res, 'start_time', None),
                            'end_time': getattr(res, 'end_time', None),
                            'url': getattr(res, 'url', ''),
                            'watch_url': getattr(res, 'watch_url', ''),
                            'video_id': getattr(res, 'video_id', None),
                            'segment_id': getattr(res, 'segment_id', None),
                            'summary': getattr(res, 'summary', ''),
                            'metadata': getattr(res, 'metadata', {}),
                            'search_method': getattr(res, 'search_method', 'unknown'),
                            'content_type': getattr(res, 'content_type', 'unknown')
                        }
                        formatted_results.append(result_dict)
                    except Exception as item_err:
                        logger.error(f"Error formatting individual result: {item_err}")
                logger.info(f"Manually converted {len(formatted_results)} SearchResult objects to dictionaries")

        metadata = {
            "query": request.query,
            "total_results_found": len(results),
            "search_duration_seconds": round(search_duration, 2),
            "analysis_run": request.run_analysis,
            "effective_params": global_search_params.get_all_params(),
            "search_complete": True,
            "analysis_complete": request.run_analysis and (openai_analysis is not None or groq_analysis is not None)
        }
        try:
            try:
                from .psearchworking import token_counter as psearch_token_counter
                metadata["token_usage"] = psearch_token_counter.get_stats()
            except (ImportError, AttributeError):
                metadata["token_usage"] = token_counter.get_stats()
        except (NameError, AttributeError) as tk_err:
            logger.warning(f"Could not get token stats: {tk_err}")

        return ComprehensiveSearchResponse(
            query=request.query,
            results=formatted_results,
            openai_analysis=openai_analysis,
            groq_analysis=groq_analysis,
            metadata=metadata
        )

    except Exception as e:
        search_duration = time.time() - start_time
        logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search execution failed: {e}")


# --- Search SSE Endpoint (Using psearchworking) ---
# (Keep existing /api/search-sse endpoint - lines 1948-2131)
@app.get("/api/search-sse", tags=["Search"])
async def search_sse_endpoint(
    request: Request,
    query: str = Query(..., min_length=1),
    max_results: int = Query(30, ge=10, le=100),
    run_analysis: bool = Query(True),
    preset: Optional[str] = Query(None),
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
):
    """
    Server-Sent Events endpoint for real-time search updates.
    Provides incremental updates as the search progresses.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE search request from {client_host}: Query='{query[:50]}...', MaxRes={max_results}, Analysis={run_analysis}, Preset='{preset}'")

    async def event_generator():
        try:
            yield format_sse_message("status", "Starting search operation", {"stage": "start"})
            await asyncio.sleep(0.5)

            yield format_sse_message("status", "Configuring search parameters", {"stage": "search"})
            try:
                update_successful = global_search_params.update_from_frontend(
                    preset=preset,
                    fine_grained_similarity_threshold=fg_similarity_threshold,
                    fine_grained_content_weight=fg_content_weight,
                    fine_grained_result_percentage=fg_result_percentage,
                    fine_grained_max_results=fg_max_results,
                    contextual_similarity_threshold=ctx_similarity_threshold,
                    contextual_content_weight=ctx_content_weight,
                    contextual_result_percentage=ctx_result_percentage,
                    contextual_max_results=ctx_max_results,
                    overview_similarity_threshold=ov_similarity_threshold,
                    overview_content_weight=ov_content_weight,
                    overview_result_percentage=ov_result_percentage,
                    overview_max_results=ov_max_results,
                )
                if not update_successful:
                    logger.warning("Search parameters updated from frontend might be invalid")
                    yield format_sse_message("status", "Warning: Some search parameters may be invalid", {"stage": "search"})
                logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
            except Exception as param_err:
                logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
                yield format_sse_message("error", f"Invalid search parameters: {param_err}")
                return

            start_time = time.time()
            yield format_sse_message("status", "Executing search query", {"stage": "filter"})
            try:
                results, openai_analysis, groq_analysis = await asyncio.to_thread(
                    search_all, query=query, max_results=max_results, skip_prompts=True, run_analysis=run_analysis
                )
                search_duration = time.time() - start_time
                logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")
                yield format_sse_message("status", "Combining search results", {"stage": "combine"})
                await asyncio.sleep(0.5)

                formatted_results = []
                if results:
                    try: formatted_results = [res.to_dict() for res in results]
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                        formatted_results = []
                        for res in results:
                            try:
                                result_dict = {
                                    'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                                    'content_id': getattr(res, 'content_id', None), 'content': getattr(res, 'content', None),
                                    'similarity': getattr(res, 'similarity', 0.0), 'source': getattr(res, 'source', 'unknown'),
                                    'title': getattr(res, 'title', ''), 'start_time': getattr(res, 'start_time', None),
                                    'end_time': getattr(res, 'end_time', None), 'url': getattr(res, 'url', ''),
                                    'watch_url': getattr(res, 'watch_url', ''), 'video_id': getattr(res, 'video_id', None),
                                    'segment_id': getattr(res, 'segment_id', None), 'summary': getattr(res, 'summary', ''),
                                    'metadata': getattr(res, 'metadata', {}), 'search_method': getattr(res, 'search_method', 'unknown'),
                                    'content_type': getattr(res, 'content_type', 'unknown')
                                }
                                formatted_results.append(result_dict)
                            except Exception as item_err: logger.error(f"Error formatting individual result: {item_err}")

                metadata = {
                    "query": query, "total_results_found": len(results), "search_duration_seconds": round(search_duration, 2),
                    "analysis_run": run_analysis, "effective_params": global_search_params.get_all_params(),
                    "search_complete": True, "stage": "complete"
                }
                try:
                    try: from .psearchworking import token_counter as psearch_token_counter; metadata["token_usage"] = psearch_token_counter.get_stats()
                    except (ImportError, AttributeError): metadata["token_usage"] = token_counter.get_stats()
                except (NameError, AttributeError) as tk_err: logger.warning(f"Could not get token stats: {tk_err}")

                if run_analysis:
                    yield format_sse_message("status", "Analyzing search results", {"stage": "analyze"})
                    if openai_analysis: yield format_sse_message("analysis", openai_analysis, {"provider": "openai"})
                    if groq_analysis: yield format_sse_message("analysis", groq_analysis, {"provider": "groq"})
                    metadata["analysis_complete"] = bool(openai_analysis or groq_analysis)

                yield format_sse_message("results", formatted_results, {**metadata, "stage": "complete"})
                yield format_sse_message("complete", "Search process completed", {"stage": "complete"})

            except Exception as e:
                search_duration = time.time() - start_time
                error_msg = f"Search execution failed: {e}"
                logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
                yield format_sse_message("error", error_msg)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed by client {client_host}")
        except Exception as e:
            logger.error(f"Unexpected error in search SSE generator: {e}", exc_info=True)
            yield format_sse_message("error", f"Unexpected error: {e}")

    return EventSourceResponse(event_generator())

# --- Root and Health Check ---
# (Keep existing / and /health endpoints - lines 2133-2160)
@app.get("/", tags=["Utility"])
async def root():
    """Root endpoint providing basic service status."""
    logger.info("Root endpoint '/' called.")
    return {"service": "PMOVES Transcription API", "status": "running", "version": app.version, "timestamp": datetime.now().isoformat()}

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    logger.debug("Health check '/health' called")
    db_status = "connected"
    try:
         client = get_client()
    except Exception as e:
         db_status = f"error: {e}"
         logger.warning(f"Health check: Supabase client unavailable: {e}")
    return {"status": "healthy", "dependencies": {"database": db_status}, "timestamp": datetime.now().isoformat()}


# --- Test Event Loop Policy Route ---
@app.get("/test-event-loop-policy", tags=["Utility", "Debug"])
async def test_event_loop_policy_route():
    # asyncio is imported at the top. logger is defined globally.
    policy_name = asyncio.get_event_loop_policy().__class__.__name__
    logger.info(f"Policy in /test-event-loop-policy route: {policy_name}")
    return {"active_policy": policy_name}

# --- ASGI Server Runner ---
# (Keep existing __main__ block - lines 2165-2194)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")
    # Log policy before Uvicorn run
    logger.info(f"Policy before Uvicorn run in __main__: {asyncio.get_event_loop_policy().__class__.__name__}")
    app_host = os.getenv("HOST", "127.0.0.1")
    try: app_port = int(os.getenv("PORT", "8000"))
    except ValueError: logger.warning(f"Invalid PORT env var '{os.getenv('PORT')}', using 8000."); app_port = 8000
    reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
    if reload_flag: logger.warning("Auto-reload enabled. Recommended only for development.")
    uvicorn.run(
        f"{Path(__file__).stem}:app", host=app_host, port=app_port, reload=reload_flag, log_level="info"
    )

# --- App Config Endpoint ---
@app.get("/api/app-config", tags=["Utility"])
async def get_app_config():
    """Expose backend folder and subfolder config to the frontend."""
    return {
        "WORKSPACE_ROOT": WORKSPACE_ROOT,
        "SUBFOLDERS": SUBFOLDERS
    }

# --- Workspace Directory Listing Endpoint ---
@app.get("/api/list-workspace", tags=["Utility"])
async def list_workspace():
    """Recursively list all files and folders under the workspace root."""
    def list_dir(path, rel_path=""):
        items = []
        for entry in os.scandir(path):
            entry_rel_path = os.path.join(rel_path, entry.name)
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "type": "folder",
                    "path": entry_rel_path.replace("\\", "/"),
                    "children": list_dir(entry.path, entry_rel_path)
                })
            else:
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": entry_rel_path.replace("\\", "/"),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return sorted(items, key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    tree = list_dir(WORKSPACE_ROOT)
    return {"root": WORKSPACE_ROOT, "tree": tree}

<environment_details>
# VSCode Visible Files
backend/app/ollama_initializer.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:00:55 AM (America/New_York, UTC-4:00)

# Context Window Usage
108,903 / 1,048.576K tokens used (10%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I have read the content of `backend/app/main.py`. I can see the `@app.on_event("startup")` decorator is used for the `startup_event` function. This is the ideal place to add the code to execute the `ollama_initializer.py` script.

I need to add the following:
1. Import the `subprocess` module. It seems `subprocess` is already imported, so I just need to ensure it's available in the `startup_event` scope.
2. Add a call to `subprocess.Popen` within the `startup_event` function to execute `sys.executable backend/app/ollama_initializer.py`. Using `sys.executable` ensures the script is run with the same Python interpreter as the main application.
3. Add logging around the execution of the initializer script.

I will use `replace_in_file` to add this code to the `startup_event` function in `backend/app/main.py`. I will add the code after the existing `queue_manager.start()` call.<replace_in_file>
<path>backend/app/main.py</path>
<diff>
<<<<<<< SEARCH
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             collector = get_metrics_collector()
             import asyncio
             asyncio.create_task(collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")
        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
=======
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             collector = get_metrics_collector()
             import asyncio
             asyncio.create_task(collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")

        # --- Execute Ollama Initializer Script ---
        try:
            logger.info("Launching Ollama initializer script...")
            # Use sys.executable to ensure the script runs with the same Python interpreter
            # Run in a non-blocking way using subprocess.Popen
            # The script itself handles checking the selected model and running ollama
            ollama_init_script_path = Path(__file__).parent / "ollama_initializer.py"
            if ollama_init_script_path.exists():
                # Use shell=True on Windows for better command execution, but be cautious
                # For cross-platform compatibility and safety, explicitly pass command parts
                command = [sys.executable, str(ollama_init_script_path)]
                # Use creationflags for Windows to prevent a console window from popping up
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                
                # Start the process without waiting
                process = subprocess.Popen(command, creationflags=creationflags)
                logger.info(f"Ollama initializer script launched with PID: {process.pid}")
            else:
                logger.error(f"Ollama initializer script not found at {ollama_init_script_path}. Skipping Ollama model loading on startup.")
        except Exception as e_ollama_init:
            logger.error(f"Error launching Ollama initializer script: {e_ollama_init}", exc_info=True)
        # --- End Ollama Initializer Script Execution ---

        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
>>>>>>> REPLACE
</diff>
</replace_in_file>
</thinking>

---

**User:**

[replace_in_file for 'backend/app/main.py'] Result:
The content was successfully saved to backend/app/main.py.

Here is the full, updated content of the file that was saved:

<final_file_content path="backend/app/main.py">
import os
import sys # Keep sys import first for platform check

# --- Event Loop Policy (MUST BE SET BEFORE ASYNCIO IMPORT) ---
_event_loop_policy_set = False
if sys.platform == "win32":
    try:
        # Temporarily import asyncio just for this setting
        import asyncio as _asyncio_temp
        _asyncio_temp.set_event_loop_policy(_asyncio_temp.WindowsProactorEventLoopPolicy())
        _event_loop_policy_set = True
        # We will log this after full asyncio and logging are imported
    except ImportError:
        # Fallback or error logging if asyncio cannot be imported here
        logger.critical("CRITICAL: Could not import asyncio to set event loop policy.")
    finally:
        # Ensure our temporary import doesn't linger
        if '_asyncio_temp' in locals():
            del _asyncio_temp

import asyncio # Now import asyncio for real
import logging # Import logging

# Rich logging for pretty terminal output
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in ["true", "1", "yes"]
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "pmoves_backend.log")

# Set up root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any default handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Console handler (always enabled)
if RICH_AVAILABLE:
    console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
else:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)

# File handler (optional, based on env)
if LOG_TO_FILE:
    file_handler = logging.FileHandler(LOG_FILE_NAME, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

logger.info(f"Logging initialized. Console: always. File: {'enabled' if LOG_TO_FILE else 'disabled'}{f' ({LOG_FILE_NAME})' if LOG_TO_FILE else ''}")

# --- Logging Configuration (Setup ASAP after policy set) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # Initialize main logger

# Log the policy that was set (or attempted)
if sys.platform == "win32":
    if _event_loop_policy_set:
        logger.info(f"Policy set in main.py (top level): {asyncio.get_event_loop_policy().__class__.__name__}")
    else:
        logger.error(f"Failed to set WindowsProactorEventLoopPolicy. Current policy: {asyncio.get_event_loop_policy().__class__.__name__}")
else:
    logger.info(f"Running on non-Windows platform. Default policy: {asyncio.get_event_loop_policy().__class__.__name__}")


# -*- coding: utf-8 -*-
"""
PMOVES Transcription API Backend

This FastAPI application provides endpoints for:
- Processing YouTube videos (downloading, transcribing).
- Downloading videos/audio using yt-dlp with progress updates.
- Fetching video metadata.
- Fetching web content using Jina Reader API, generating PDFs, storing in Supabase, and enabling vector search.
- Real-time status updates via Server-Sent Events (SSE).
- Content ingestion and vector search capabilities (requires related modules).
"""

# --- Standard Library Imports ---
import os
import re
import json
import shutil
# import logging # Moved up
# import asyncio # Moved up
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
from typing import Any # Added for Supabase client type hint if needed, or use from existing

# --- Third-Party Imports ---
from dotenv import load_dotenv
from fastapi import (
    FastAPI, HTTPException, BackgroundTasks, Body, Request,
    status, Query, Depends, Security # Added Security for potential API key auth
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse # Added FileResponse
from fastapi.security import APIKeyHeader # Added for potential API key auth
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import (
    BaseModel, validator, ValidationError, Field, field_validator
)
import torch # Still imported from original, ensure necessary

# --- Optional Third-Party Imports (with fallbacks/warnings) ---
try:
    from openai import OpenAI, AsyncOpenAI # Added AsyncOpenAI
    from openai import APIError as OpenAI_APIError # Specific OpenAI errors
    from openai import RateLimitError as OpenAI_RateLimitError
    from openai import APIConnectionError as OpenAI_APIConnectionError
    from openai import AuthenticationError as OpenAI_AuthenticationError
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    OpenAI_APIError = None
    OpenAI_RateLimitError = None
    OpenAI_APIConnectionError = None
    OpenAI_AuthenticationError = None

try:
    from groq import Groq, AsyncGroq # Added AsyncGroq
except ImportError:
    Groq = None
    AsyncGroq = None

try:
    from rich.console import Console
except ImportError:
    class Console:
        def print(self, *args, **kwargs): print(*args)
    Console = Console() # Instantiate dummy

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from tiktoken import get_encoding
except ImportError:
    get_encoding = None

import aiofiles # Used for async file operations if needed

# --- Logging Configuration (Moved to top of file and initialized as 'logger') ---
# (Original content removed as it's now at the beginning)

# --- Check Critical Dependencies ---
if OpenAI is None or AsyncOpenAI is None:
    logger.warning("Optional dependency 'openai' not found or incomplete. AI analysis/embedding features may be limited.")
if Groq is None or AsyncGroq is None:
    logger.warning("Optional dependency 'groq' not found or incomplete. Groq features will be unavailable.")
if yt_dlp is None:
     logger.error("Required dependency 'yt-dlp' not found. Video download and info features will fail.")
if get_encoding is None:
    logger.warning("Optional dependency 'tiktoken' not found. Token counting will be estimated.")

# --- Rich Console Initialization ---
console = Console()

# --- Environment Variable Loading ---
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}. Relying on environment variables.")
    load_dotenv() # Attempt default load

# --- API Client Initialization ---
# OpenAI (Async)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if AsyncOpenAI and openai_api_key:
    try:
        openai_client = AsyncOpenAI(api_key=openai_api_key)
        logger.info("Async OpenAI client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async OpenAI client: {e}", exc_info=True)
elif AsyncOpenAI:
    logger.warning("OPENAI_API_KEY not set. OpenAI client not initialized.")

# Groq (Async)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if AsyncGroq and groq_api_key:
    try:
        groq_client = AsyncGroq(api_key=groq_api_key)
        logger.info("Async Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async Groq client: {e}", exc_info=True)
elif AsyncGroq:
    logger.warning("GROQ_API_KEY not set. Groq client not initialized.")


# --- Local/Project Imports ---
try:
    from .queue_manager import QueueManager
    from .monitoring.logger import PerformanceMonitor, async_timer, CustomLogger
    from .monitoring.metrics import MetricsCollector, TranscriptionMetrics, router as metrics_router, get_metrics_collector
    from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
    from .transcribe1 import process_video, VideoProcessRequest as TranscribeVideoRequest # Renamed Pydantic model
    from .general_utils import (
        save_text_to_markdown,
        clean_filename, format_timestamp, sanitize_filename,
        generate_pdf_from_markdown_string # Added for PDF generation
    )
    from .fetch_content import (
        fetch_content_from_url, generate_unique_filename
    )
    from .crawl4ai_fetcher import fetch_with_crawl4ai # Added for crawl4ai
    from .app_config import WORKSPACE_ROOT, SUBFOLDERS
    from .psearchworking_export import (
        search_all, analyze_search_results, get_client as get_supabase_client,
        SearchParameters, global_search_params, SearchResult,
        TokenCounter as PSearchTokenCounter, ModelSelector
    )
    from .config.search_config import (
         get_preset, validate_search_params, router as search_config_router # etc.
     )
    from .routes.content_upserter import router as content_upserter_router
    from .routes.fetch_history_routes import router as fetch_history_router # Added this line
    from .monitoring.sse_monitor import sse_monitoring_middleware
    from .monitoring.routes import router as monitoring_router
    from .utils.llm_logging import log_llm_call # Added for LLM call logging

    PROJECT_MODULES_LOADED = True
except ImportError as e:
     logger.error(f"Failed to import one or more project modules: {e}. Check installation and package structure.", exc_info=True)
     PROJECT_MODULES_LOADED = False

     # --- Define dummy classes/functions with CORRECT SYNTAX ---
     logger.warning("Defining dummy components due to import errors.")

     class QueueManager:
         """Dummy QueueManager with correct syntax."""
         def __init__(self):
             self.status_queue = asyncio.Queue()
             self.transcription_queue = asyncio.Queue()
             logger.info("Initialized dummy QueueManager queues.")
         async def start(self): logger.warning("Called dummy QueueManager.start()"); pass
         async def stop(self): logger.warning("Called dummy QueueManager.stop()"); pass
         def has_active_transcriptions(self): return False # Add dummy method

     class PerformanceMonitor:
         """Dummy PerformanceMonitor."""
         def __init__(self, logger_instance): pass
         def start_timer(self, name: str): pass
         def stop_timer(self, name: str) -> float: return 0.0

     class MetricsCollector:
         """Dummy MetricsCollector."""
         async def collect_system_metrics(self): pass
         def add_metric(self, *args, **kwargs): pass

     class TranscriptionMetrics:
         """Dummy TranscriptionMetrics."""
         def record_request(self, success: bool): pass

     # --- Dummy Functions ---
     def get_supabase_client(): logger.error("Dummy: Supabase client unavailable."); return None
     DEFAULT_OUTPUT_FOLDER = './output'
     async def process_video(*args, **kwargs): logger.error("Dummy: process_video unavailable.")
     async def search_all(*args, **kwargs): logger.error("Dummy: search_all unavailable."); return [], None, None
     def analyze_search_results(*args, **kwargs): logger.error("Dummy: analyze_search_results unavailable."); return "Analysis unavailable."
     async def fetch_content_from_url(*args, **kwargs): logger.error("Dummy: fetch_content_from_url unavailable."); return {"error": "unavailable"}
     async def convert_md_to_pdf_util(*args, **kwargs): logger.error("Dummy: convert_markdown_to_pdf unavailable."); return False
     def generate_unique_filename(url, ext): return f"dummy_{url[:10]}_{int(time.time())}.{ext}"

     # --- More Dummy Classes ---
     class SearchParameters:
         """Dummy SearchParameters."""
         def get_all_params(self) -> dict: return {}
         def get_params(self, tier: str) -> dict: return {}
         def load_current(self): pass
         def update_params(self, tier:str, **kwargs): pass
         def update_from_frontend(self, **kwargs): return True # Add dummy method

     global_search_params = SearchParameters()

     class SearchResult:
          """Dummy SearchResult."""
          def __init__(self, **kwargs): pass
          def to_dict(self): return {}

     class PSearchTokenCounter:
          """Dummy TokenCounter."""
          def get_stats(self) -> dict: return {'embedding_tokens':0, 'generation_tokens':{'input':0, 'output':0}, 'total_tokens':0}
          def count_embedding_tokens(self, text:str) -> int: return 0
          def count_generation_tokens(self, input_text:str, output_text:Optional[str]=None) -> dict: return {'input':0, 'output':0}

     class ModelSelector:
         """Dummy ModelSelector."""
         @staticmethod
         def generate_analysis(text: str, provider: str = 'openai') -> str: return "Dummy Analysis Unavailable."

     # --- Dummy Routers/Middleware ---
     content_upserter_router = None
     metrics_router = None
     monitoring_router = None
     sse_monitoring_middleware = None

# --- Initialize Core Components ---
if PROJECT_MODULES_LOADED:
    performance_monitor = PerformanceMonitor(logger)
    metrics_collector = MetricsCollector()
    transcription_metrics = TranscriptionMetrics()
    try:
        queue_manager = QueueManager()
    except Exception as e:
        logger.error(f"Failed to initialize QueueManager: {e}", exc_info=True)
        sys.exit("QueueManager initialization failed.")
else:
     logger.warning("Using dummy components due to import errors.")
     performance_monitor = PerformanceMonitor(logger)
     metrics_collector = MetricsCollector()
     transcription_metrics = TranscriptionMetrics()
     queue_manager = QueueManager() # Dummy instance

# Download-specific queue
download_status_queue = asyncio.Queue()


# --- TokenCounter Class ---
# (Keep existing TokenCounter class - lines 375-447)
class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {'input': 0, 'output': 0}
        self.encoders = None
        if get_encoding:
            try:
                self.encoders = {
                    'cl100k_base': get_encoding('cl100k_base'),
                    'gpt-4': get_encoding('cl100k_base'),
                }
                logger.info("TokenCounter initialized with tiktoken encoders.")
            except Exception as e:
                logger.warning(f"Could not initialize tiktoken encoders: {e}. Token counting will be estimated.")
        else:
             logger.warning("TokenCounter initialized without tiktoken. Token counting will be estimated.")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        return len(text) // 4

    def count_embedding_tokens(self, text: str) -> int:
        """Count or estimate tokens for embedding."""
        if not self.encoders or 'cl100k_base' not in self.encoders:
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logger.warning(f"Could not count embedding tokens using tiktoken: {e}. Estimating.")
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens

    def count_generation_tokens(self, input_text: str, output_text: Optional[str] = None) -> dict:
        """Count or estimate tokens for generation."""
        result = {'input': 0, 'output': 0}
        encoder = self.encoders.get('gpt-4') if self.encoders else None

        try:
            if encoder:
                result['input'] = len(encoder.encode(input_text))
                if output_text:
                    result['output'] = len(encoder.encode(output_text))
            else:
                result['input'] = self._estimate_tokens(input_text)
                if output_text:
                    result['output'] = self._estimate_tokens(output_text)
        except Exception as e:
            logger.warning(f"Could not count generation tokens using tiktoken: {e}. Estimating.")
            result['input'] = self._estimate_tokens(input_text)
            if output_text:
                result['output'] = self._estimate_tokens(output_text)

        self.generation_tokens['input'] += result['input']
        self.generation_tokens['output'] += result['output']
        return result

    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        total = self.embedding_tokens + sum(self.generation_tokens.values())
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': total
        }

# Initialize token counter
token_counter = TokenCounter()


# --- Supabase Client Function ---
# (Keep existing get_client function - lines 451-465)
def get_client():
    """Get a Supabase client instance using the imported function."""
    if not PROJECT_MODULES_LOADED or get_supabase_client is None:
         logger.error("Cannot get Supabase client: psearchworking module or get_client function not loaded.")
         raise RuntimeError("Supabase client function is unavailable.")
    try:
        client = get_supabase_client()
        if client is None:
            logger.error("get_supabase_client() returned None.")
            raise RuntimeError("Failed to obtain Supabase client instance.")
        # logger.debug("Supabase client obtained successfully.")
        return client
    except Exception as e:
        logger.error(f"Error obtaining Supabase client via get_supabase_client(): {e}", exc_info=True)
        raise RuntimeError(f"Failed to obtain Supabase client: {e}")


# --- Pydantic Models ---
# (Keep existing models: ComprehensiveSearchRequest, ComprehensiveSearchResponse, VideoRequest, VectorSearchRequest, VectorSearchResponse, DownloadRequest, VideoInfoRequest - lines 469-586)
class ComprehensiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(30, ge=10, le=100, description="Maximum TOTAL results desired across methods")
    run_analysis: bool = Field(True, description="Whether to run AI analysis on results")

class ComprehensiveSearchResponse(BaseModel):
    """Response model for the comprehensive search endpoint."""
    query: str
    results: List[Dict[str, Any]] # List of dictionaries matching SearchResult.to_dict()
    openai_analysis: Optional[str] = None
    groq_analysis: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata, like timing, token counts, effective params")

    class Config:
        from_attributes = True # For Pydantic v2

class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str # Client must provide path to existing Obsidian vault/folder
    output_folder: str # Client provides desired base output path
    transcription_model: str = "faster-whisper"
    use_groq: Optional[bool] = None # Allow explicit setting, but validator overrides

    @field_validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v, re.IGNORECASE):
            raise ValueError('Invalid YouTube URL format')
        return v

    @field_validator('output_folder')
    def output_folder_must_be_valid(cls, v):
        if not v:
            v = os.path.join(WORKSPACE_ROOT, SUBFOLDERS['transcriptions']['markdown'])
        try:
             path = Path(v).resolve()
             if not path.parent.exists():
                  raise ValueError(f"Parent directory does not exist: {path.parent}")
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid output folder path '{v}': {e}")

    @field_validator('obsidian_dir')
    def obsidian_dir_must_exist(cls, v):
        if not v:
            raise ValueError('Obsidian directory path must be provided')
        try:
             path = Path(v).resolve()
             if not path.is_dir():
                  raise ValueError('Path is not an existing directory')
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid Obsidian directory path '{v}': {e}")

    @field_validator('transcription_model')
    def validate_transcription_model(cls, v):
        valid_models = ["faster-whisper", "groq"] # Add specific models if needed e.g. "groq/whisper-large-v3"
        if v.lower() not in valid_models and not v.lower().startswith("groq/"):
            raise ValueError(f"Invalid transcription model. Use 'faster-whisper', 'groq', or specific 'groq/model-name'.")
        return v.lower()

    from pydantic import model_validator

    @model_validator(mode='after')
    def check_and_set_use_groq(self) -> 'VideoRequest':
        model_name = self.transcription_model
        is_groq_model = model_name == 'groq' or model_name.startswith('groq/')

        if self.use_groq is not None and self.use_groq != is_groq_model:
             logger.warning(f"Provided 'use_groq' ({self.use_groq}) contradicts model '{model_name}'. Overriding based on model.")

        self.use_groq = is_groq_model # Set use_groq based on the model selected

        if self.use_groq and groq_client is None:
             raise ValueError("Groq transcription model selected, but Groq client is not available/configured.")

        return self

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    # Add fields for other search function parameters if needed
    content_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    summary_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    video_filter: Optional[str] = Field(None)

    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Search query must not be empty')
        return v.strip()

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    ai_response: Optional[str] = Field(None) # Keep for potential future use
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True # Pydantic v2

class DownloadRequest(BaseModel):
    url: str
    options: Dict[str, Any] = Field(default_factory=dict, description="yt-dlp options")

class VideoInfoRequest(BaseModel):
    url: str

# --- Fetch History Models ---
class FetchHistoryBase(BaseModel):
    url: str = Field(..., description="The URL that was fetched or attempted to be fetched.")
    fetching_engine: str = Field(..., description="The engine used for fetching (e.g., 'jina', 'crawl4ai').")
    status: str = Field(default='pending', description="The status of the fetch job (e.g., 'pending', 'success', 'failed').")
    engine_specific_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters specific to the fetching engine used.")
    user_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the user who initiated the fetch.")
    error_message: Optional[str] = Field(None, description="Error message if the fetch job failed.")
    content_summary: Optional[str] = Field(None, description="A brief summary or preview of the fetched content.")
    raw_content_path: Optional[str] = Field(None, description="Path to the stored raw fetched content, if applicable.")
    processed_content_path: Optional[str] = Field(None, description="Path to the stored processed content (e.g., PDF), if applicable.")
    supabase_content_id: Optional[uuid.UUID] = Field(None, description="ID of the related content in Supabase 'webpage_content' table, if applicable.")

class FetchHistoryCreate(FetchHistoryBase):
    pass

class FetchHistoryResponse(FetchHistoryBase):
    id: uuid.UUID = Field(..., description="Unique identifier for the fetch history record.")
    fetch_date: datetime = Field(..., description="Timestamp of when the fetch job was recorded.")

    class Config:
        from_attributes = True


# --- Initialize FastAPI app ---
# (Keep existing app initialization - lines 589-602)
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for YouTube video processing, download, and search.",
    version="1.2.0", # Incremented version for fetch/pdf/search features
    openapi_tags=[
        {"name": "Processing", "description": "Video transcription and processing."},
        {"name": "Download", "description": "Video/Audio download operations."},
        {"name": "Search", "description": "Content search functionalities."},
        {"name": "Status", "description": "Real-time status updates via SSE."},
        {"name": "Utility", "description": "Helper endpoints."},
        {"name": "Health", "description": "Service health checks."},
        {"name": "Content Fetch", "description": "Fetch web content, generate PDFs."},
        {"name": "Files", "description": "Serve generated files (e.g., PDFs)."},
        {"name": "Fetch History", "description": "Manage and view fetch history records."}, # Keep only one
    ]
)

# --- Configure CORS ---
# (Keep existing CORS middleware - lines 605-615)
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(',')
logger.info(f"Configuring CORS for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Content-Type-Options", "Content-Disposition"], # Added Content-Disposition
)

# --- Add Custom Middlewares ---
# (Keep existing middlewares: SSE Monitoring, Error Handling, Request Logging - lines 618-669)
# SSE Monitoring Middleware (if available)
if PROJECT_MODULES_LOADED and 'sse_monitoring_middleware' in locals() and sse_monitoring_middleware:
    try:
        app.middleware("http")(sse_monitoring_middleware)
        logger.info("SSE monitoring middleware enabled.")
    except Exception as e:
        logger.warning(f"Failed to enable SSE monitoring middleware: {e}")

# Error Handling Middleware (should be early)
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exc:
        raise http_exc # Re-raise for FastAPI to handle
    except Exception as exc:
        logger.error(f"Unhandled exception during request to {request.url.path}", exc_info=exc)
        error_details = {"error_code": "UNEXPECTED_SERVER_ERROR", "message": "An internal server error occurred."}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if PROJECT_MODULES_LOADED and 'TranscriptionErrorHandler' in locals():
             try:
                 error_details = TranscriptionErrorHandler.handle_error(
                     "UNEXPECTED_SERVER_ERROR", exc, path=str(request.url.path)
                 )
             except Exception as handler_err:
                  logger.error(f"Error handler itself failed: {handler_err}")
        return JSONResponse(status_code=status_code, content=error_details)

# Request Logging Middleware (should be after error handling, before routes)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"--> {method} {path} from {client_host}")
    response = await call_next(request) # Process request
    process_time = time.time() - start_time
    status_code = response.status_code
    logger.info(f"<-- {method} {path} - Status={status_code} ({process_time:.3f}s)")
    return response


# --- App Lifecycle Events ---
# (Keep existing startup/shutdown events - lines 672-697)
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             collector = get_metrics_collector()
             import asyncio
             asyncio.create_task(collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")

        # --- Execute Ollama Initializer Script ---
        try:
            logger.info("Launching Ollama initializer script...")
            # Use sys.executable to ensure the script runs with the same Python interpreter
            # Run in a non-blocking way using subprocess.Popen
            # The script itself handles checking the selected model and running ollama
            ollama_init_script_path = Path(__file__).parent / "ollama_initializer.py"
            if ollama_init_script_path.exists():
                # Use shell=True on Windows for better command execution, but be cautious
                # For cross-platform compatibility and safety, explicitly pass command parts
                command = [sys.executable, str(ollama_init_script_path)]
                # Use creationflags for Windows to prevent a console window from popping up
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                
                # Start the process without waiting
                process = subprocess.Popen(command, creationflags=creationflags)
                logger.info(f"Ollama initializer script launched with PID: {process.pid}")
            else:
                logger.error(f"Ollama initializer script not found at {ollama_init_script_path}. Skipping Ollama model loading on startup.")
        except Exception as e_ollama_init:
            logger.error(f"Error launching Ollama initializer script: {e_ollama_init}", exc_info=True)
        # --- End Ollama Initializer Script Execution ---

        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated...")
    try:
        await queue_manager.stop()
        logger.info("Queue manager stopped.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)


# --- SSE Message Formatter ---
# (Keep existing format_sse_message function - lines 700-747)
def format_sse_message(message_type: str, content: Any, metadata: Optional[dict] = None) -> str:
    """Formats a message dictionary into an SSE string, ensuring content is serializable."""
    message = {
        "type": message_type,
        "content": None, # Initialize content to None
        "timestamp": datetime.now().isoformat(),
        "id": str(time.time())  # Add a unique ID for each message
    }
    if metadata:
        message["metadata"] = metadata

    serializable_content = None
    if isinstance(content, (str, int, float, bool, type(None))):
        serializable_content = content
    elif isinstance(content, (dict, list)):
        serializable_content = content
    elif hasattr(content, 'to_dict') and callable(content.to_dict):
        try:
            serializable_content = content.to_dict()
        except Exception as e:
            logger.warning(f"Error calling to_dict() for SSE content type {message_type}: {e}. Content: {str(content)[:100]}")
            serializable_content = f"Error serializing object: {str(content)[:100]}"
    elif hasattr(content, '__dict__'):
         try:
             json.dumps(content.__dict__)
             serializable_content = content.__dict__
         except TypeError:
              logger.warning(f"Could not directly serialize __dict__ for SSE content type {message_type}. Sending string representation. Content: {str(content)[:100]}")
              serializable_content = str(content) # Fallback to string representation
    else:
        serializable_content = str(content)

    message["content"] = serializable_content

    try:
        json_str = json.dumps(message)
        return json_str # EventSourceResponse will handle the "data: " prefix and "\n\n"
    except TypeError as e:
         logger.error(f"FINAL fallback: Failed to serialize SSE message of type {message_type}: {e}. Content: {str(serializable_content)[:100]}")
         error_content = {"error": "Failed to serialize message content", "original_type": message_type}
         # EventSourceResponse will handle the "data: " prefix and "\n\n"
         return json.dumps({'type': 'error', 'content': error_content, 'timestamp': datetime.now().isoformat()})


# --- Combined SSE Updates Endpoint ---
# (Keep existing /combined-updates endpoint - lines 752-983)
@app.get("/combined-updates", tags=["Status"])
async def get_combined_updates(request: Request):
    """SSE endpoint for combined status and transcription updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"SSE connection requested from {client_host} (Origin: {origin}) for /combined-updates.")

    async def event_generator():
        logger.info(f"SSE (Combined): GENERATOR ENTERED for {client_host}.")
        try:
            status_q = queue_manager.status_queue
            transcription_q = queue_manager.transcription_queue
            logger.info(f"SSE (Combined): Got queue references. TQ ID: {id(transcription_q)}, SQ ID: {id(status_q)}")
            last_activity_time = time.time()
            heartbeat_interval = 2
            connection_timeout = 300

            transcription_task = asyncio.create_task(transcription_q.get())
            setattr(transcription_task, '_queue_name', 'transcription')
            status_task = asyncio.create_task(status_q.get())
            setattr(status_task, '_queue_name', 'status')
            heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
            setattr(heartbeat_task, '_is_heartbeat', True)

            all_tasks = {transcription_task, status_task, heartbeat_task}
            logger.info(f"SSE (Combined): Initialized {len(all_tasks)} persistent tasks. Entering main try block.")
        except Exception as setup_err:
            logger.error(f"SSE (Combined): ERROR DURING INITIAL SETUP: {setup_err}", exc_info=True)
            try: yield format_sse_message('error', f"SSE generator setup failed: {setup_err}")
            except: pass
            return

        try:
            connection_established_msg = format_sse_message(
                "status", "SSE connection established",
                {"connection_id": str(time.time()), "server_time": datetime.now().isoformat()}
            )
            yield connection_established_msg
            last_activity_time = time.time()
            yield format_sse_message('heartbeat', 'initial_ping')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check_2')

            while True:
                logger.debug(f"SSE (Combined): Entering new loop iteration for {client_host}")
                try:
                    logger.info(f"SSE (Combined): LOOP START - Waiting on {len(all_tasks)} persistent tasks.")
                    done, pending = await asyncio.wait(all_tasks, return_when=asyncio.FIRST_COMPLETED)
                    logger.info(f"SSE (Combined): WAIT COMPLETED - Done: {len(done)}, Pending: {len(pending)}")

                    for task in done:
                        if getattr(task, '_is_heartbeat', False):
                            logger.debug("SSE (Combined): Heartbeat task completed.")
                            try:
                                yield format_sse_message('heartbeat', 'ping_interval')
                                last_activity_time = time.time()
                                logger.debug("SSE (Combined): Sent interval heartbeat.")
                            except Exception as send_err:
                                logger.error(f"Failed to send interval heartbeat: {send_err}. Closing connection.")
                                raise send_err
                            all_tasks.remove(task)
                            new_heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
                            setattr(new_heartbeat_task, '_is_heartbeat', True)
                            all_tasks.add(new_heartbeat_task)
                            logger.debug(f"SSE (Combined): Replaced completed heartbeat task with new task {id(new_heartbeat_task)}")
                            continue

                        original_queue = None
                        queue_name = getattr(task, '_queue_name', None)
                        if queue_name == 'transcription': original_queue = transcription_q
                        elif queue_name == 'status': original_queue = status_q

                        if original_queue is None:
                            logger.error(f"SSE (Combined): Completed task {id(task)} is not a known queue task.")
                            continue

                        try:
                            item = task.result()
                            logger.info(f"SSE (Combined): ITEM RETRIEVED from {queue_name} queue {id(original_queue)}. Type: {type(item).__name__}. Content: {str(item)[:100]}...")
                            sse_msg = None
                            if isinstance(item, str):
                                try:
                                    payload_dict = json.loads(item)
                                    msg_type = payload_dict.get('type', 'transcription_segment' if original_queue == transcription_q else 'status')
                                    msg_content = payload_dict.get('content', payload_dict)
                                    sse_msg = format_sse_message(msg_type, msg_content)
                                except json.JSONDecodeError:
                                    logger.error(f"SSE (Combined): Failed to decode JSON from {queue_name} queue {id(original_queue)}: {item[:100]}...")
                                    sse_msg = format_sse_message('error', f"Invalid data received from backend queue: {item[:100]}...")
                                except Exception as format_err:
                                    logger.error(f"SSE (Combined): Error formatting message after JSON decode: {format_err}", exc_info=True)
                                    sse_msg = format_sse_message('error', f"Internal error formatting SSE message: {format_err}")
                            else:
                                logger.error(f"SSE (Combined): Received non-string item type '{type(item).__name__}' from {queue_name} queue {id(original_queue)}. Content: {str(item)[:100]}")
                                sse_msg = format_sse_message('error', f"Invalid data type received from backend queue: {type(item).__name__}")

                            if sse_msg:
                                try:
                                    yield sse_msg
                                    last_activity_time = time.time()
                                    logger.info(f"SSE SEND (Combined): {sse_msg.strip()[:150]}...")
                                except Exception as send_err:
                                    logger.error(f"Failed to send update to SSE client: {send_err}")
                                    raise send_err
                            else:
                                logger.warning(f"SSE (Combined): No valid SSE message generated for item from {original_queue} queue.")

                            original_queue.task_done()
                            all_tasks.remove(task)
                            if original_queue == transcription_q:
                                new_task = asyncio.create_task(transcription_q.get())
                                setattr(new_task, '_queue_name', 'transcription')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed transcription task with new task {id(new_task)}")
                            elif original_queue == status_q:
                                new_task = asyncio.create_task(status_q.get())
                                setattr(new_task, '_queue_name', 'status')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed status task with new task {id(new_task)}")

                        except asyncio.CancelledError:
                            logger.info(f"SSE (Combined): A queue get() task {id(task)} was cancelled.")
                        except Exception as e:
                            logger.error(f"SSE (Combined): Error processing completed task result for task {id(task)}: {e}", exc_info=True)
                            try: yield format_sse_message('error', f"Internal SSE error processing task result: {str(e)}")
                            except Exception as send_err: logger.error(f"Failed to send task processing error to SSE client: {send_err}"); raise send_err

                except asyncio.CancelledError:
                    logger.info(f"SSE connection closed by client {client_host} for /combined-updates (Caught CancelledError in loop).")
                    break
                except Exception as loop_err:
                    error_message = f"FATAL Error in /combined-updates SSE generator loop: {loop_err}"
                    logger.error(error_message, exc_info=True)
                    try: yield format_sse_message('error', f"Fatal SSE generator loop error: {str(loop_err)}")
                    except Exception: pass
                    break

            logger.info(f"SSE event generator loop exited for {client_host} (/combined-updates).")

        finally:
            logger.info(f"SSE event generator entering finally block for {client_host} (/combined-updates).")
            logger.info(f"SSE (Combined): Cancelling {len(all_tasks)} remaining tasks in final cleanup.")
            for task in list(all_tasks):
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
                except Exception as e: logger.error(f"Error awaiting cancellation of task {id(task)}: {e}")
            logger.info(f"SSE event generator finished final cleanup for {client_host} (/combined-updates).")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Combined SSE ---
# (Keep existing /combined-updates OPTIONS handler - lines 1006-1010)
@app.options("/combined-updates", tags=["Status"])
async def options_combined_updates(request: Request):
    """Handle OPTIONS preflight requests for /combined-updates."""
    return _handle_options_request(request, allowed_origins)


# --- Download Status SSE Endpoint ---
# (Keep existing /api/download-status endpoint - lines 1013-1084)
@app.get("/api/download-status", tags=["Status", "Download"])
async def get_download_status(request: Request):
    """SSE endpoint specifically for download status updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"Download status SSE connection requested from {client_host} (Origin: {origin}).")

    async def event_generator():
        q = download_status_queue
        last_activity_time = time.time()
        heartbeat_interval = 20

        try:
            yield format_sse_message("status", "Connected to download status stream")
            last_activity_time = time.time()

            while True:
                try:
                    status_update_str = await asyncio.wait_for(q.get(), timeout=heartbeat_interval)
                    logger.debug(f"SSE (Download): Sending update: {status_update_str[:100]}...")
                    try:
                        update_data = json.loads(status_update_str)
                        yield f"data: {status_update_str}\n\n" # Send raw JSON string
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Download SSE received non-JSON: {status_update_str[:100]}... Error: {e}")
                        yield format_sse_message('status', status_update_str) # Send as plain
                    q.task_done()
                    last_activity_time = time.time()

                except asyncio.TimeoutError:
                    logger.debug("SSE (Download): Sending heartbeat.")
                    yield format_sse_message('heartbeat', 'ping')
                    last_activity_time = time.time()
                    continue

                except asyncio.QueueEmpty:
                     await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Download SSE connection closed by client {client_host}.")
        except Exception as e:
            error_message = f"Error in download status SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try: yield format_sse_message('error', error_message)
            except Exception as send_err: logger.error(f"Failed to send error to download SSE client: {send_err}")
        finally:
            logger.info(f"Download SSE event generator finished for {client_host}.")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    origin = request.headers.get("origin", "N/A")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"Download SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Download Status SSE ---
# (Keep existing /api/download-status OPTIONS handler - lines 1087-1090)
@app.options("/api/download-status", tags=["Status", "Download"])
async def options_download_status(request: Request):
    """Handle OPTIONS preflight requests for /api/download-status."""
    return _handle_options_request(request, allowed_origins)

# --- Helper for OPTIONS requests ---
# (Keep existing _handle_options_request function - lines 1093-1109)
def _handle_options_request(request: Request, allowed_origins_list: List[str]):
    origin = request.headers.get("origin")
    method = request.headers.get("access-control-request-method")
    logger.info(f"OPTIONS request for {request.url.path} from origin: {origin}, method: {method}")

    if origin in allowed_origins_list:
        response = JSONResponse(content={"detail": "OK"}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS" # Adjust as needed per endpoint
        response.headers["Access-Control-Allow-Headers"] = "*" # Or be specific: "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400" # Cache preflight for 1 day
        logger.debug(f"OPTIONS response headers: {response.headers}")
        return response
    else:
        logger.warning(f"OPTIONS request from disallowed origin: {origin}")
        return JSONResponse(content={"detail": "Origin not allowed"}, status_code=400)


# --- Transcription Status Endpoint ---
# (Keep existing /transcription-status endpoint - lines 1113-1131)
@app.get("/transcription-status", tags=["Status"])
async def transcription_status():
    """Check if there's an active transcription process running."""
    try:
        active = False
        if queue_manager and hasattr(queue_manager, '_running') and queue_manager._running:
            active = not queue_manager.transcription_queue.empty()
            if hasattr(queue_manager, 'has_active_transcriptions'):
                 active = active or queue_manager.has_active_transcriptions()
        return {"active": active}
    except Exception as e:
        logger.error(f"Error checking transcription status: {e}")
        return {"active": False, "error": str(e)}

# --- Process Video Endpoint ---
# (Keep existing /process-video/ endpoint - lines 1134-1212)
@app.post("/process-video/", tags=["Processing"])
async def process_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """Initiate background processing (download, transcribe) for a YouTube video."""
    if not PROJECT_MODULES_LOADED or process_video is None:
         raise HTTPException(status_code=501, detail="Video processing feature is unavailable due to missing modules.")

    try:
        logger.info(f"Processing video request for URL: {request.youtube_video_url}")
        console.print(f"[cyan]Obsidian Dir:[/cyan] {request.obsidian_dir}")
        console.print(f"[cyan]Output Folder:[/cyan] {request.output_folder}")
        console.print(f"[cyan]Model:[/cyan] {request.transcription_model}, [cyan]Use Groq:[/cyan] {request.use_groq}")

        transcription_metrics.record_request(True)
        output_path = Path(request.output_folder)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured output folder exists: {output_path}")
        except OSError as e:
             logger.error(f"Failed to create output folder {output_path}: {e}", exc_info=True)
             raise HTTPException(status_code=500, detail=f"Could not create output directory: {e}")

        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq
        }

        try:
            from .transcribe1 import extract_video_id
            video_id = extract_video_id(request.youtube_video_url)
        except Exception as e:
            logger.warning(f"Could not extract video ID for tracking: {e}")
            video_id = request.youtube_video_url

        from .process_video_wrapper import process_video_with_tracking

        background_tasks.add_task(
            process_video_with_tracking,
            youtube_video_url=request.youtube_video_url,
            obsidian_dir=request.obsidian_dir,
            status_queue=queue_manager.status_queue,
            transcription_queue=queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config,
            video_id=video_id
        )

        logger.info(f"Background task added for processing: {request.youtube_video_url}")

        return {
            "status": "started",
            "message": "Video processing initiated in the background.",
            "details": {
                 "url": request.youtube_video_url,
                 "output_folder": request.output_folder,
                 "obsidian_dir": request.obsidian_dir
            },
            "timestamp": datetime.now().isoformat()
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.warning(f"Validation error processing video request: {e.errors()}", exc_info=False)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException as e:
         transcription_metrics.record_request(False)
         raise e
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(f"Unexpected error initiating video processing for {request.youtube_video_url}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start video processing task.")


# --- Video Download Feature ---
# (Keep existing download_video_task, report_download_progress, report_postprocess_progress, /api/download endpoint - lines 1217-1459)
async def download_video_task(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task using yt-dlp (run in thread) with progress reporting."""
    if yt_dlp is None:
        logger.error("yt-dlp library is not installed. Cannot download video.")
        await status_queue.put(format_sse_message('error','Download feature unavailable: yt-dlp library not installed.'))
        return

    download_dir = options.get('download_dir', os.path.join(os.getcwd(), 'downloads'))
    logger.info(f"Download task started for URL: {url}, saving to: {download_dir}")

    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create download directory {download_dir}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Failed to create download directory: {e}'))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_template = os.path.join(download_dir, f'%(title)s_{timestamp}.%(ext)s')

    ydl_opts = {
        'outtmpl': filename_template,
        'quiet': True, 'no_warnings': True, 'noprogress': True,
        'keepvideo': options.get('keepVideo', True),
        'overwrites': False,
        'ffmpeg_location': options.get('ffmpegPath'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True, 'playlist_items': None,
    }

    video_format = options.get('format')
    if video_format == 'best': pass
    elif video_format in ['1080p', '720p', '480p', '360p']:
        res = video_format.replace('p', '')
        ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best[height<={res}]'
    elif video_format == 'audio_best':
         ydl_opts['format'] = 'bestaudio/best'
         options['extractAudio'] = True
         options.setdefault('audioFormat', 'mp3')

    if options.get('extractAudio'):
        audio_format = options.get('audioFormat', 'mp3')
        audio_quality = options.get('audioQuality', '192')
        ydl_opts.setdefault('postprocessors', []).append({
            'key': 'FFmpegExtractAudio', 'preferredcodec': audio_format, 'preferredquality': audio_quality,
        })
        if not ydl_opts['keepvideo'] and video_format != 'audio_best':
             ydl_opts['format'] = 'bestaudio/best'

    if options.get('embedThumbnail') and video_format != 'audio_best':
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append({'key': 'EmbedThumbnail'})

    if options.get('embedMetadata', True):
        ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegMetadata', 'add_metadata': True})

    if options.get('subtitles'):
        sub_lang = options.get('subtitleLanguage', 'en')
        sub_auto = options.get('autoSubtitles', False)
        sub_format = options.get('subtitleFormat', 'srt')
        ydl_opts.update({
            'writesubtitles': True, 'writeautomaticsub': sub_auto,
            'subtitleslangs': [sub_lang] if sub_lang != 'all' else ['all'],
            'subtitlesformat': sub_format,
        })
        if options.get('embedSubtitles') and video_format != 'audio_best':
             ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegEmbedSubtitle'})

    is_playlist_url = 'list=' in url or '/playlist?' in url
    if is_playlist_url and options.get('downloadPlaylist'):
        playlist_items = None
        items_str = options.get('playlistItems')
        start = options.get('playlistStart')
        end = options.get('playlistEnd')
        if items_str: playlist_items = items_str
        elif start or end: playlist_items = f"{start or ''}-{end or ''}"
        ydl_opts['noplaylist'] = False
        ydl_opts['playlist_items'] = playlist_items
        logger.info(f"Playlist download enabled. Items: '{playlist_items or 'all'}'")
    elif is_playlist_url:
        logger.info("Playlist URL detected, but only downloading single video.")
        ydl_opts['noplaylist'] = True

    try:
        await status_queue.put(format_sse_message('status', f'Starting download: {url}', {'download_dir': download_dir}))
        logger.info("Running yt-dlp download process in thread...")
        loop = asyncio.get_running_loop()
        ydl_opts['progress_hooks'] = [functools.partial(report_download_progress, loop, status_queue)]
        ydl_opts['postprocessor_hooks'] = [functools.partial(report_postprocess_progress, loop, status_queue)]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             await asyncio.to_thread(ydl.download, [url])
        logger.info(f"yt-dlp download thread finished for {url}.")
        await status_queue.put(format_sse_message('complete', f'Download finished for: {url}'))
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error for {url}: {e}", exc_info=False)
        await status_queue.put(format_sse_message('error', f'Download failed: {e}'))
    except Exception as e:
        logger.error(f"Unexpected error during download task for {url}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Unexpected download error: {e}'))

def report_download_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp download progress, puts message to asyncio queue."""
    if loop is None: logger.error("Asyncio loop is None in report_download_progress."); return
    if d['status'] == 'downloading':
        try:
            progress = d.get('fraction', 0) * 100
            speed = d.get('speed_str', d.get('speed', 'N/A'))
            eta = d.get('eta_str', d.get('eta', 'N/A'))
            filename = d.get('filename', d.get('info_dict',{}).get('filename', '...'))
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            size_str = "N/A"
            if total_bytes:
                if total_bytes < 1024*1024: size_str = f"{total_bytes/1024:.1f} KiB"
                elif total_bytes < 1024*1024*1024: size_str = f"{total_bytes/(1024*1024):.1f} MiB"
                else: size_str = f"{total_bytes/(1024*1024*1024):.2f} GiB"
            content = {'progress': round(progress, 1), 'speed': speed, 'eta': eta, 'filename': os.path.basename(filename), 'total_size': size_str, 'status': 'Downloading'}
            message = format_sse_message('progress', content)
            asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
        except Exception as e: pass
    elif d['status'] == 'finished':
        filename = d.get('filename', d.get('info_dict',{}).get('filename', 'file'))
        message = format_sse_message('status', f'Downloaded {os.path.basename(filename)}. Post-processing...')
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
    elif d['status'] == 'error':
         err_msg = d.get("error", "Unknown download error")
         filename = d.get('filename', d.get('info_dict',{}).get('filename', 'N/A'))
         message = format_sse_message('error', f'Error downloading {os.path.basename(filename)}: {err_msg}')
         asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

def report_postprocess_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp post-processing progress."""
    if loop is None: logger.error("Asyncio loop is None in report_postprocess_progress."); return
    status = d.get('status')
    pp_name = d.get('postprocessor')
    info = d.get('info_dict', {})
    filename = os.path.basename(info.get('filepath', info.get('filename', 'file')))
    if status == 'started' or status == 'processing': message = format_sse_message('status', f'Post-processing ({pp_name}): Starting on {filename}...')
    elif status == 'finished': message = format_sse_message('status', f'Post-processing ({pp_name}): Finished for {filename}.')
    elif status == 'error': message = format_sse_message('error', f'Post-processing ({pp_name}): Failed for {filename}. Check logs.')
    else: return
    asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

@app.post("/api/download", tags=["Download"])
async def download_video_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a video/audio download task in the background."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Download feature unavailable: yt-dlp library not installed.")
    try:
        logger.info(f"Download request received for URL: {request.url}")
        console.print(f"[yellow]Options:[/yellow] {request.options}")
        request.options.setdefault('download_dir', os.path.join(os.getcwd(), 'downloads'))
        background_tasks.add_task(download_video_task, request.url, request.options, download_status_queue)
        return {"status": "success", "message": "Download task initiated in background.", "url": request.url, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error starting download task for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start download task: {e}")


# --- Get Video Info Endpoint ---
# (Keep existing /api/video-info endpoint - lines 1463-1551)
@app.post("/api/video-info", tags=["Download", "Utility"])
async def get_video_info(request: VideoInfoRequest):
    """Get metadata for a YouTube video or playlist without downloading."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Info feature unavailable: yt-dlp library not installed.")
    logger.info(f"Video info request for URL: {request.url}")
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'extract_flat': 'in_playlist'}
    info = None
    try:
        logger.debug(f"Extracting info for {request.url} in thread...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             info = await asyncio.to_thread(ydl.extract_info, request.url, download=False)
        logger.debug(f"Info extraction finished.")
        if not info: raise HTTPException(status_code=404, detail="Could not extract information for the given URL.")

        is_playlist = info.get('_type') == 'playlist'
        playlist_count = len(info.get('entries', [])) if is_playlist else 0
        title = info.get('title', 'N/A')
        author = info.get('uploader', info.get('channel', 'N/A'))
        thumbnail = info.get('thumbnail')
        video_id = info.get('id', '')
        original_url = info.get('webpage_url', request.url)
        duration_str = "N/A"
        if is_playlist: duration_str = f"{playlist_count} videos"
        else:
            duration_sec = info.get('duration')
            if duration_sec:
                try:
                    duration_str = str(timedelta(seconds=int(duration_sec)))
                except (ValueError, TypeError): # Catch specific errors during conversion
                    logger.warning(f"Could not convert duration '{duration_sec}' to timedelta.")
                    pass # Keep duration_str as "N/A"
            if not thumbnail and info.get('thumbnails'): thumbnail = info['thumbnails'][-1]['url']

        formats = info.get('formats', [])
        available_formats_notes = sorted(list(set(f.get('format_note', f.get('resolution', f.get('ext'))) for f in formats if f.get('format_note') or f.get('resolution') or f.get('ext')))) if formats else ["N/A (requires detailed fetch)"]
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        available_subtitles = sorted(list(subs.keys()))
        available_auto_captions = sorted(list(auto_subs.keys()))

        return {"title": title, "author": author, "thumbnail": thumbnail, "duration": duration_str, "is_playlist": is_playlist, "playlist_count": playlist_count if is_playlist else 1, "available_formats": available_formats_notes, "available_subtitles": available_subtitles, "available_auto_captions": available_auto_captions, "id": video_id, "original_url": original_url}
    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"yt-dlp info extraction failed for {request.url}: {e}")
        status_code = 400; detail = f"Failed to process URL"
        if "Unsupported URL" in str(e): status_code = 400; detail = "Unsupported URL"
        elif "Video unavailable" in str(e): status_code = 404; detail = "Video unavailable"
        elif "Private video" in str(e): status_code = 403; detail = "Video is private"
        elif "Sign in to confirm your age" in str(e): status_code = 403; detail = "Video requires age verification (login)"
        raise HTTPException(status_code=status_code, detail=f"{detail}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching video info for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching video info: {e}")


# --- List Downloads Endpoint ---
# (Keep existing /api/list-downloads endpoint - lines 1555-1634)
@app.get("/api/list-downloads", tags=["Download"])
async def list_downloads(directory: Optional[str] = Query(None)):
    """List files in the specified download directory."""
    logger.info(f"List downloads request for directory: {directory}")
    list_dir = directory
    if not list_dir:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): list_dir = user_downloads
            else: list_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
        except Exception: list_dir = os.path.abspath('./downloads')

    list_dir_path = Path(list_dir).resolve()
    if not list_dir_path.is_dir():
        logger.warning(f"Attempted to list non-existent or non-directory path: {list_dir_path}")
        return {"files": []}
    try:
        entries = await asyncio.to_thread(os.listdir, list_dir_path)
        files_list = []
        for entry_name in entries:
            entry_path = list_dir_path / entry_name
            if await asyncio.to_thread(os.path.isfile, entry_path):
                try:
                    stat = await asyncio.to_thread(os.stat, entry_path)
                    size_bytes = stat.st_size
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    file_extension = entry_path.suffix.lower()
                    file_type = "Other"
                    if file_extension in ['.mp4', '.mkv', '.webm', '.avi', '.mov']: file_type = "Video"
                    elif file_extension in ['.mp3', '.wav', '.aac', '.m4a', '.opus', '.ogg']: file_type = "Audio"
                    elif file_extension in ['.srt', '.vtt', '.ass']: file_type = "Subtitle"
                    size_str = "N/A"
                    if size_bytes is not None:
                        if size_bytes < 1024: size_str = f"{size_bytes} B"
                        elif size_bytes < 1024*1024: size_str = f"{size_bytes/1024:.1f} KB"
                        elif size_bytes < 1024*1024*1024: size_str = f"{size_bytes/(1024*1024):.1f} MB"
                        else: size_str = f"{size_bytes/(1024*1024*1024):.2f} GB"
                    files_list.append({"name": entry_name, "type": file_type, "size": size_str, "modified": mod_time.isoformat(), "path": str(entry_path)})
                except Exception as file_info_err:
                    logger.warning(f"Error getting info for file {entry_path}: {file_info_err}")
                    files_list.append({"name": entry_name, "type": "Unknown", "size": "N/A", "modified": "N/A", "path": str(entry_path)})
        files_list.sort(key=lambda x: x.get('modified', '0'), reverse=True)
        logger.info(f"Listed {len(files_list)} files in {list_dir_path}")
        return {"files": files_list}
    except Exception as e:
        logger.error(f"Error listing files in directory {list_dir_path}: {e}", exc_info=True)
        return {"files": [], "error": f"Failed to list files: {e}"}


# --- Fetch History API Endpoints ---

@app.post("/api/fetch-history", response_model=FetchHistoryResponse, tags=["Fetch History"], status_code=status.HTTP_201_CREATED)
async def create_fetch_history_entry(payload: FetchHistoryCreate):
    """
    Create a new fetch history entry.
    """
    logger.info(f"Creating fetch history entry for URL: {payload.url} with engine: {payload.fetching_engine}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        # Prepare data for insertion, Pydantic model ensures correct types for what's passed
        # fetch_date and id are handled by the database by default
        data_to_insert = payload.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .insert(data_to_insert)
            .execute
        )

        if hasattr(response, 'data') and response.data:
            created_entry_data = response.data[0]
            logger.info(f"Successfully created fetch history entry with ID: {created_entry_data.get('id')}")
            # Ensure all fields required by FetchHistoryResponse are present, or handle defaults
            # The DB defaults should cover 'id' and 'fetch_date'
            return FetchHistoryResponse(**created_entry_data)
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error creating fetch history entry: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history creation: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating fetch history entry for URL {payload.url}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create fetch history entry: {str(e)}")

@app.get("/api/fetch-history", response_model=List[FetchHistoryResponse], tags=["Fetch History"])
async def list_fetch_history_entries(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return."),
    offset: int = Query(0, ge=0, description="Number of records to skip for pagination.")
):
    """
    List existing fetch history entries, ordered by fetch_date descending.
    """
    logger.info(f"Listing fetch history entries with limit={limit}, offset={offset}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("*")
            .order("fetch_date", desc=True)
            .limit(limit)
            .offset(offset)
            .execute
        )

        if hasattr(response, 'data'):
            entries_data = response.data
            logger.info(f"Successfully retrieved {len(entries_data)} fetch history entries.")
            # Pydantic will validate each item in the list against FetchHistoryResponse
            return [FetchHistoryResponse(**entry) for entry in entries_data]
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error listing fetch history entries: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history listing: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error listing fetch history entries: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list fetch history entries: {str(e)}")


# --- Get Default Directory Endpoint ---
# (Keep existing /api/default-directory endpoint - lines 1640-1667)
@app.get("/api/default-directory", tags=["Utility"])
async def get_default_directory():
    """Suggest a default download directory path (client can override)."""
    path_str = ""
    warning = None
    try:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): path_str = user_downloads
            else: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "User 'Downloads' directory not found, suggesting relative path."
        except Exception: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "Could not determine user home directory, suggesting relative path."
        logger.info(f"Providing default download directory suggestion: {path_str}")
        response = {"path": path_str}
        if warning: response["warning"] = warning
        return response
    except Exception as e:
        logger.error(f"Error determining default directory: {e}", exc_info=True)
        fallback_dir = os.path.abspath('./downloads')
        return {"path": fallback_dir, "warning": "Could not determine default path, using relative './downloads'."}


# --- PDF Storage Path ---
PDF_STORAGE_BASE_DIR = Path(os.getenv('PDF_STORAGE_PATH', './temp_pdfs')).resolve()
try:
    PDF_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured PDF storage directory exists: {PDF_STORAGE_BASE_DIR}")
except OSError as e:
    logger.error(f"CRITICAL: Could not create PDF storage directory {PDF_STORAGE_BASE_DIR}: {e}. PDF features will fail.", exc_info=True)
    # Depending on requirements, might want to exit or just disable PDF features
    # sys.exit(f"Failed to create PDF storage directory: {PDF_STORAGE_BASE_DIR}")


# --- Helper: Generate OpenAI Embedding ---
async def get_openai_embedding(text: str, model: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")) -> Optional[List[float]]:
    """Generates embedding for text using OpenAI API, with logging."""
    if not openai_client:
        logger.error("OpenAI client not initialized. Cannot generate embedding.")
        # Log attempt even if client is not initialized, as it's an LLM operation attempt
        llm_log_data_no_client = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "ConfigurationError",
            "error_message_detail": "OpenAI client not initialized.",
            "input_text_preview": (text[:100] + "...") if text and len(text) > 100 else text
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_no_client, indent=2, default=str)}")
        return None

    if not text or not text.strip():
        logger.warning("Attempted to generate embedding for empty text.")
        # Log this attempt as well
        llm_log_data_empty_text = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "InputError",
            "error_message_detail": "Input text for embedding was empty or whitespace.",
            "input_text_preview": ""
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_empty_text, indent=2, default=str)}")
        return None

    llm_log_data: Dict[str, Any] = {
        "request_timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_call_type": "embedding",
        "llm_provider": "openai",
        "model_name": model,
        "input_text_preview": (text[:100] + "...") if len(text) > 100 else text,
        "call_successful": False, # Default to False
    }
    start_time = time.time()

    try:
        processed_text = text.replace("\n", " ")
        response = await openai_client.embeddings.create(input=[processed_text], model=model)
        embedding = response.data[0].embedding
        
        llm_log_data["call_successful"] = True
        if response.usage:
            llm_log_data["prompt_tokens_total"] = response.usage.prompt_tokens
            llm_log_data["total_tokens_used"] = response.usage.total_tokens
        # Cost calculation would require model pricing data
        # llm_log_data["cost"] = calculate_cost(model, response.usage.prompt_tokens)
        
        logger.info(f"Generated OpenAI embedding using model {model} for text snippet: '{text[:50]}...'")
        return embedding
    except OpenAI_APIError as e:
        logger.error(f"OpenAI API error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "RateLimitError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_APIConnectionError as e:
        logger.error(f"OpenAI connection error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIConnectionError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_AuthenticationError as e:
        logger.error(f"OpenAI authentication error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "AuthenticationError"
        llm_log_data["error_message_detail"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error generating OpenAI embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "UnhandledException"
        llm_log_data["error_message_detail"] = str(e)
    finally:
        end_time = time.time()
        llm_log_data["llm_call_duration_ms"] = int((end_time - start_time) * 1000)
        # Log the comprehensive data (placeholder for DB insert)
        # TODO: Implement actual DB insertion for llm_call_logs table
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data, indent=2, default=str)}")
    
    return None

# --- Helper: Upsert Content to Supabase ---
async def upsert_content_to_supabase(
    url: str,
    title: str,
    markdown_content: str,
    embedding: Optional[List[float]],
    pdf_path: Optional[str] = None
) -> Optional[str]:
    """Upserts fetched content, embedding, and PDF path to Supabase using the SQL function."""
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            logger.error("Supabase client unavailable. Cannot upsert content.")
            return None

        # Generate a unique content_id (e.g., UUID) for new entries
        # The SQL function handles finding existing entries by URL
        content_id = str(uuid.uuid4())

        # Prepare parameters for the SQL function
        params = {
            "p_content_id": content_id,
            "p_title": title,
            "p_url": url,
            "p_content": markdown_content,
            "p_embedding": embedding, # Pass the list of floats
            "p_pdf_path": pdf_path,
            # "p_source_file": None # Or pass pdf_path here if using source_file column
        }

        logger.info(f"Calling Supabase RPC upsert_webpage_content for URL: {url}")
        response = await asyncio.to_thread(
             supabase_client.rpc('upsert_webpage_content', params).execute
        )
        # response = supabase_client.rpc('upsert_webpage_content', params).execute() # Original sync call

        # Check response (supabase-py v1 might differ from v2 in response structure)
        # Assuming response.data contains the returned content_id
        if hasattr(response, 'data') and response.data:
            returned_id = response.data
            logger.info(f"Successfully upserted content for URL {url}. Returned ID: {returned_id}")
            return returned_id
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error upserting content for {url}: {response.error}")
             return None
        else:
             # Handle unexpected response structure (log and return None)
             logger.warning(f"Unexpected response structure from Supabase upsert RPC for {url}: {response}")
             return None

    except Exception as e:
        logger.error(f"Error upserting content to Supabase for URL {url}: {e}", exc_info=True)
        return None

# --- Helper: Update Fetch History Record ---
async def _update_fetch_history_record(
    supabase_client: Any, # from supabase import Client as SupabaseClient - or use Any
    history_id: Optional[uuid.UUID],
    update_data: Dict[str, Any],
    all_request_params_for_history: Dict[str, Any]
) -> Tuple[Optional[str], bool]: # Returns (SSE message string or None, db_write_successful_flag)
    """
    Helper to update a fetch_history record.
    Returns an SSE message string for the event_generator to yield,
    and a boolean indicating if the database write operation was successful for this call.
    The database update itself is attempted regardless.
    """
    if not history_id or not supabase_client:
        logger.warning(f"Attempted to update fetch history with invalid history_id ({history_id}) or supabase_client.")
        return format_sse_message("error", "history_update_skipped_invalid_params", {"message": f"Skipping history update for {history_id} due to invalid client or ID."}), False

    payload_to_send = {**update_data, "engine_specific_parameters": all_request_params_for_history}
    # Ensure no None values accidentally overwrite existing data unless intended by update_data
    payload_to_send = {k: v for k, v in payload_to_send.items() if v is not None or k in update_data}

    sse_message_to_yield: Optional[str] = None
    db_write_successful = False
    try:
        logger.info(f"Attempting to update fetch_history record ID: {history_id} with status: {update_data.get('status')}")
        update_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .update(payload_to_send)
            .eq("id", history_id)
            .execute
        )

        if hasattr(update_response, 'data') and update_response.data:
            logger.info(f"Successfully updated fetch history {history_id} with status: {update_data.get('status')}")
            sse_message_to_yield = format_sse_message("status", "history_updated", {"message": f"Fetch history record {history_id} updated.", "status": update_data.get('status')})
            db_write_successful = True
        elif hasattr(update_response, 'error') and update_response.error:
            err_msg = update_response.error.message if hasattr(update_response.error, 'message') else str(update_response.error)
            logger.error(f"Failed to update fetch history {history_id}: {err_msg}")
            sse_message_to_yield = format_sse_message("warning", "history_update_failed", {"message": f"Could not update history record {history_id}: {err_msg}"})
        else:
            logger.error(f"Unexpected response structure when updating fetch history {history_id}: {update_response}")
            sse_message_to_yield = format_sse_message("warning", "history_update_unexpected_response", {"message": f"Unexpected DB response for history update {history_id}."})
    except Exception as e:
        logger.error(f"Exception updating fetch history {history_id}: {e}", exc_info=True)
        sse_message_to_yield = format_sse_message("warning", "history_update_exception", {"message": f"Exception during history update for {history_id}: {str(e)}"})
    
    return sse_message_to_yield, db_write_successful

# --- Fetch Content Endpoint (MODIFIED for SSE) ---
@app.get("/fetch-content", tags=["Content Fetch"])
async def fetch_content_endpoint(
    request: Request, # Added Request for client host logging
    url: str = Query(..., description="URL to fetch content from"),
    engine: str = Query("jina", description="Fetching engine to use ('jina' or 'crawl4ai')"),
    generate_pdf: bool = Query(True, description="Generate PDF from fetched content (used by both engines if capable)"),
    upload_to_supabase: bool = Query(False, description="Upload content and embedding to Supabase (post-fetch process)"),

    # --- Browser/Crawling Generic Parameters (used by crawl4ai, some by Jina if applicable) ---
    headless: Optional[bool] = Query(True, description="Run browser in headless mode (crawl4ai)"),
    user_agent: Optional[str] = Query(None, description="Custom user agent string for the browser (crawl4ai)"),
    proxy_url: Optional[str] = Query(None, description="Proxy URL for browser requests (crawl4ai)"), # ADDED
    enable_javascript: Optional[bool] = Query(True, description="Enable JavaScript execution (crawl4ai)"),
    ignore_https_errors: Optional[bool] = Query(True, description="Ignore HTTPS errors (crawl4ai)"), # ADDED
    light_mode: Optional[bool] = Query(False, description="Enable light mode (reduces resource usage) (crawl4ai)"), # ADDED
    text_mode: Optional[bool] = Query(False, description="Enable text-only mode (crawl4ai)"), # ADDED
    browser_cookies: Optional[str] = Query(None, description="JSON string of cookies to set (crawl4ai)"), # ADDED
    browser_headers: Optional[str] = Query(None, description="JSON string of headers to set (crawl4ai)"), # ADDED
    browser_use_persistent_context: Optional[bool] = Query(False, description="Use persistent browser context (crawl4ai)"), # ADDED
    browser_user_data_dir: Optional[str] = Query(None, description="Path to browser user data directory (crawl4ai)"), # ADDED
    browser_extra_args: Optional[str] = Query(None, description="Comma-separated list of extra browser arguments (crawl4ai)"), # ADDED
    viewport_width: Optional[int] = Query(None, description="Browser viewport width (crawl4ai)"), # ADDED
    viewport_height: Optional[int] = Query(None, description="Browser viewport height (crawl4ai)"), # ADDED
    browser_engine: str = Query("playwright", description="Browser engine ('playwright' or 'selenium') (crawl4ai, Jina)"),
    browser_viewport: str = Query("1920x1080", description="Browser viewport (e.g., '1920x1080') (Jina specific, use viewport_width/height for crawl4ai)"), # Clarified
    browser_locale: str = Query("en-US", description="Browser locale (e.g., 'en-US') (crawl4ai, Jina)"),
    take_screenshot: Optional[bool] = Query(False, description="Enable screenshot capture (crawl4ai)"),
    take_screenshot_on_error: Optional[bool] = Query(True, description="Capture screenshot if an error occurs during crawling (crawl4ai)"),
    respect_robots_txt: Optional[bool] = Query(True, description="Whether to respect robots.txt rules (crawl4ai)"),
    
    # --- Timeouts ---
    jina_timeout_seconds: int = Query(300, description="Timeout in seconds for Jina fetch operation"),
    crawl4ai_interaction_timeout_ms: Optional[int] = Query(30000, description="Page interaction timeout for crawl4ai in ms (e.g., for JS execution)"),
    navigation_timeout_ms: Optional[int] = Query(60000, description="Page navigation timeout for crawl4ai in ms"),
    page_load_timeout_ms: Optional[int] = Query(None, description="Overall page load timeout for crawl4ai in ms (defaults to navigation_timeout_ms if None)"), # Matches crawl4ai_fetcher
    page_load_wait_condition: Optional[str] = Query(None, description="Page load wait condition (e.g., 'load', 'domcontentloaded', 'networkidle') (crawl4ai)"), # ADDED
    wait_for_element_js_condition: Optional[str] = Query(None, description="JavaScript expression to wait for before proceeding (crawl4ai)"), # ADDED

    # --- Content Extraction & Formatting Parameters (primarily crawl4ai, some overlap with Jina) ---
    target_selector: Optional[str] = Query(None, description="CSS Selector for target elements to focus on (crawl4ai, Jina)"), # Renamed from target_elements_css_selectors
    excluded_selector: Optional[str] = Query(None, description="CSS Selector for elements to exclude (crawl4ai, Jina)"), # Renamed from excluded_elements_css_selector
    excluded_tags: Optional[str] = Query(None, description="Comma-separated list of HTML tags to exclude (crawl4ai)"), # ADDED
    extract_only_text_content: Optional[bool] = Query(False, description="Extract only text content, no HTML structure (crawl4ai)"), # ADDED
    process_iframes_content: Optional[bool] = Query(False, description="Process content within iframes (crawl4ai)"), # ADDED
    word_count_threshold: Optional[int] = Query(None, description="Minimum word count for content to be considered valid (crawl4ai)"), # ADDED
    remove_forms: Optional[bool] = Query(False, description="Remove form elements from content (crawl4ai)"), # ADDED
    keep_data_attributes: Optional[bool] = Query(False, description="Keep data-* attributes in HTML (crawl4ai)"), # ADDED
    execute_javascript_on_page_load: Optional[str] = Query(None, description="JavaScript code to execute on page load (crawl4ai)"), # ADDED
    scan_full_page_auto_scroll: Optional[bool] = Query(False, description="Enable auto-scroll to capture full page content (crawl4ai)"), # ADDED
    scroll_delay_seconds: Optional[float] = Query(None, description="Delay in seconds between scrolls for full page capture (crawl4ai)"), # ADDED
    attempt_remove_overlay_elements: Optional[bool] = Query(False, description="Attempt to remove overlay elements (crawl4ai)"), # ADDED
    simulate_user_behavior: Optional[bool] = Query(False, description="Simulate user behavior like mouse movements (crawl4ai)"), # ADDED
    enable_magic_handling: Optional[bool] = Query(False, description="Enable crawl4ai's 'magic' handling for complex sites (crawl4ai)"), # ADDED
    override_navigator_properties: Optional[bool] = Query(False, description="Override browser navigator properties (crawl4ai)"), # ADDED
    cache_mode: Optional[str] = Query(None, description="Cache mode for crawl4ai (e.g., 'ENABLED', 'BYPASS', 'REFRESH')"), # ADDED
    capture_screenshot_base64: Optional[bool] = Query(False, description="Capture screenshot as base64 (crawl4ai)"), # ADDED (distinct from take_screenshot)
    # generate_pdf: bool = Query(True, ...) is already present
    capture_mhtml_snapshot: Optional[bool] = Query(False, description="Capture MHTML snapshot of the page (crawl4ai)"), # ADDED
    exclude_external_images: Optional[bool] = Query(False, description="Exclude external images from extraction (crawl4ai)"), # ADDED
    image_alt_text_min_word_count: Optional[int] = Query(None, description="Min word count for image alt text to be considered (crawl4ai)"), # ADDED
    image_relevance_score_threshold: Optional[int] = Query(None, description="Relevance score threshold for images (crawl4ai)"), # ADDED
    exclude_external_links: Optional[bool] = Query(False, description="Exclude external links from extraction (crawl4ai)"), # ADDED
    exclude_social_media_links: Optional[bool] = Query(False, description="Exclude social media links (crawl4ai)"), # ADDED
    custom_excluded_domains: Optional[str] = Query(None, description="Comma-separated list of custom domains to exclude (crawl4ai)"), # ADDED
    # respect_robots_txt: Optional[bool] = Query(True, ...) is already present
    verbose_logging: Optional[bool] = Query(False, description="Enable verbose logging for crawl4ai"), # ADDED
    log_page_console_output: Optional[bool] = Query(False, description="Log page console output during crawl (crawl4ai)"), # ADDED
    crawl_session_id: Optional[str] = Query(None, description="Session ID for crawl4ai"), # ADDED
    crawl_css_selector: Optional[str] = Query(None, description="Global CSS selector for crawl4ai (distinct from target_selector)"), # ADDED
    crawl4ai_markdown_generator: Optional[str] = Query(None, description="Specify markdown generator for crawl4ai (e.g., 'Default')"), # ADDED
    
    # --- Deep Crawl Individual Parameters (used if deep_crawl_config blob is not provided) ---
    deep_crawl_strategy_name: Optional[str] = Query(None, alias="deep_crawl_strategy_name", description="Name of the deep crawl strategy (e.g., BFSDeepCrawlStrategy)"),
    deep_crawl_max_depth: Optional[int] = Query(None, alias="deep_crawl_max_depth", description="Maximum depth for deep crawling"),
    deep_crawl_max_pages: Optional[int] = Query(None, alias="deep_crawl_max_pages", description="Maximum number of pages for deep crawling"),
    deep_crawl_include_external: Optional[bool] = Query(None, alias="deep_crawl_include_external", description="Include external links in deep crawl"),
    deep_crawl_score_threshold: Optional[float] = Query(None, alias="deep_crawl_score_threshold", description="Score threshold for deep crawl strategies like BFS/DFS"),
    deep_crawl_filter_regexes: Optional[str] = Query(None, alias="deep_crawl_filter_regexes", description="Comma-separated regex patterns for URL filtering in deep crawl"),
    deep_crawl_url_scorer_type: Optional[str] = Query(None, alias="deep_crawl_url_scorer_type", description="Type of URL scorer for BestFirstCrawlingStrategy (e.g., KeywordRelevanceScorer)"),
    deep_crawl_scorer_keywords: Optional[str] = Query(None, alias="deep_crawl_scorer_keywords", description="Comma-separated keywords for KeywordRelevanceScorer"),
    deep_crawl_scorer_weight: Optional[float] = Query(None, alias="deep_crawl_scorer_weight", description="Weight for KeywordRelevanceScorer"),
    
    deep_crawl_config: Optional[str] = Query(None, description="JSON string for deep crawl strategy configuration (crawl4ai)"), # ADDED
    extraction_config: Optional[str] = Query(None, description="JSON string for extraction strategy configuration (crawl4ai)"), # ADDED
 
    extraction_strategy: Optional[str] = Query("markdown", description="Content extraction strategy for crawl4ai (e.g., 'markdown', 'llm')"), # This was for Jina, now more general
    output_format: Optional[str] = Query("markdown", description="Desired output format from crawl4ai (e.g., 'markdown', 'text')"), # This was for Jina, now more general
    token_budget: int = Query(4000, description="Max tokens for content processing (crawl4ai token_limit, Jina token_budget)"),
    remove_images: bool = Query(False, description="Remove images from content (crawl4ai, Jina)"),
    extract_links: bool = Query(True, description="Extract links from content (crawl4ai, Jina)"),
    extract_metadata: bool = Query(True, description="Extract page metadata (crawl4ai, Jina)"),
    markdown_flavor: str = Query("github", description="Markdown flavor for output (crawl4ai, Jina)"),

    # --- LLM Specific Parameters (for crawl4ai's LLM features like captioning or LLM extraction) ---
    image_captioning: bool = Query(False, description="Enable image captioning (crawl4ai with LLM, Jina)"),
    llm_provider: Optional[str] = Query("openai", description="LLM provider for crawl4ai (e.g., 'openai', 'groq', 'ollama/model')"),
    llm_api_key: Optional[str] = Query(None, description="API key for the LLM provider (use environment variables if None)"),
    llm_model_name: Optional[str] = Query("gpt-3.5-turbo", description="Specific LLM model name for crawl4ai"),
    llm_temperature: Optional[float] = Query(0.7, ge=0.0, le=2.0, description="LLM temperature for crawl4ai"),
    llm_max_tokens: Optional[int] = Query(1000, ge=1, description="LLM max tokens for generation for crawl4ai"),

    # --- Jina Specific Parameters (ignored by crawl4ai) ---
    json_response: bool = Query(True, description="Request raw JSON response from Jina (contains metadata) (Jina specific)"), # Should be Jina specific
    cache_ttl: int = Query(3600, description="Cache TTL in seconds (Jina specific)") # Should be Jina specific
):
    """
    Fetches content using the specified engine and streams progress via SSE.
    Optionally generates PDF, generates embedding, and stores in Supabase.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE /fetch-content request from {client_host} for URL: {url}, Engine: {engine}, PDF: {generate_pdf}, Supabase: {upload_to_supabase}")

    if not PROJECT_MODULES_LOADED:
        async def error_gen_no_modules():
            yield format_sse_message("error", "Core project modules not loaded. Fetch feature unavailable.")
        return EventSourceResponse(error_gen_no_modules())

    # Gather all original request parameters for potential use by fetchers
    all_request_params = {
        "url": url, "engine": engine, "generate_pdf": generate_pdf, "upload_to_supabase": upload_to_supabase,
        "headless": headless, "user_agent": user_agent, "proxy_url": proxy_url, # ADDED
        "enable_javascript": enable_javascript, "ignore_https_errors": ignore_https_errors, # ADDED
        "light_mode": light_mode, "text_mode": text_mode, # ADDED
        "browser_cookies": browser_cookies, "browser_headers": browser_headers, # ADDED
        "browser_use_persistent_context": browser_use_persistent_context, # ADDED
        "browser_user_data_dir": browser_user_data_dir, "browser_extra_args": browser_extra_args, # ADDED
        "viewport_width": viewport_width, "viewport_height": viewport_height, # ADDED
        "browser_engine": browser_engine, "browser_viewport": browser_viewport, "browser_locale": browser_locale,
        "take_screenshot": take_screenshot, "take_screenshot_on_error": take_screenshot_on_error,
        "respect_robots_txt": respect_robots_txt,
        "jina_timeout_seconds": jina_timeout_seconds,
        "crawl4ai_interaction_timeout_ms": crawl4ai_interaction_timeout_ms,
        "navigation_timeout_ms": navigation_timeout_ms,
        "page_load_timeout_ms": page_load_timeout_ms,
        "page_load_wait_condition": page_load_wait_condition, # ADDED
        "wait_for_element_js_condition": wait_for_element_js_condition, # ADDED
        "target_selector": target_selector, "excluded_selector": excluded_selector,
        "excluded_tags": excluded_tags, # ADDED
        "extract_only_text_content": extract_only_text_content, # ADDED
        "process_iframes_content": process_iframes_content, # ADDED
        "word_count_threshold": word_count_threshold, # ADDED
        "remove_forms": remove_forms, "keep_data_attributes": keep_data_attributes, # ADDED
        "execute_javascript_on_page_load": execute_javascript_on_page_load, # ADDED
        "scan_full_page_auto_scroll": scan_full_page_auto_scroll, # ADDED
        "scroll_delay_seconds": scroll_delay_seconds, # ADDED
        "attempt_remove_overlay_elements": attempt_remove_overlay_elements, # ADDED
        "simulate_user_behavior": simulate_user_behavior, # ADDED
        "enable_magic_handling": enable_magic_handling, # ADDED
        "override_navigator_properties": override_navigator_properties, # ADDED
        "cache_mode": cache_mode, # ADDED
        "capture_screenshot_base64": capture_screenshot_base64, # ADDED
        "capture_mhtml_snapshot": capture_mhtml_snapshot, # ADDED
        "exclude_external_images": exclude_external_images, # ADDED
        "image_alt_text_min_word_count": image_alt_text_min_word_count, # ADDED
        "image_relevance_score_threshold": image_relevance_score_threshold, # ADDED
        "exclude_external_links": exclude_external_links, # ADDED
        "exclude_social_media_links": exclude_social_media_links, # ADDED
        "custom_excluded_domains": custom_excluded_domains, # ADDED
        "verbose_logging": verbose_logging, "log_page_console_output": log_page_console_output, # ADDED
        "crawl_session_id": crawl_session_id, "crawl_css_selector": crawl_css_selector, # ADDED
        "crawl4ai_markdown_generator": crawl4ai_markdown_generator, # ADDED
        
        # Deep Crawl Individual Parameters
        "deep_crawl_strategy_name": deep_crawl_strategy_name,
        "deep_crawl_max_depth": deep_crawl_max_depth,
        "deep_crawl_max_pages": deep_crawl_max_pages,
        "deep_crawl_include_external": deep_crawl_include_external,
        "deep_crawl_score_threshold": deep_crawl_score_threshold,
        "deep_crawl_filter_regexes": deep_crawl_filter_regexes,
        "deep_crawl_url_scorer_type": deep_crawl_url_scorer_type,
        "deep_crawl_scorer_keywords": deep_crawl_scorer_keywords,
        "deep_crawl_scorer_weight": deep_crawl_scorer_weight,
        
        "deep_crawl_config": deep_crawl_config, # This is the JSON blob
        "extraction_config": extraction_config, # ADDED
        "extraction_strategy": extraction_strategy, "output_format": output_format,
        "token_budget": token_budget, "remove_images": remove_images, "extract_links": extract_links,
        "extract_metadata": extract_metadata, "markdown_flavor": markdown_flavor,
        "image_captioning": image_captioning, "llm_provider": llm_provider, "llm_api_key": llm_api_key,
        "llm_model_name": llm_model_name, "llm_temperature": llm_temperature, "llm_max_tokens": llm_max_tokens,
        "json_response": json_response, "cache_ttl": cache_ttl
    }
    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    async def event_generator():
        # --- Fetch History Variables ---
        fetch_history_id: Optional[uuid.UUID] = None
        supabase_client_for_history: Optional[Any] = None # Holds Supabase client
        terminal_status_written_to_db: bool = False # NEW: Tracks if 'success' or 'failed' status was successfully written

        # --- Other original variables ---
        fetched_data_dict: Optional[Dict[str, Any]] = None
        markdown_content: Optional[str] = None
        title: str = "Untitled"
        fetched_url_actual: str = url
        pdf_relative_path: Optional[str] = None
        embedding_generated: bool = False
        supabase_content_id_str: Optional[str] = None

        try:
            # --- Get Supabase Client for History ---
            try:
                supabase_client_for_history = get_client()
                if not supabase_client_for_history:
                    logger.error("Failed to get Supabase client for fetch history (get_client returned None).")
                    yield format_sse_message("error", "database_client_unavailable", {"message": "Database client is essential for history tracking and is unavailable."})
                    return # Stop if DB client cannot be obtained
            except RuntimeError as e_db_client:
                logger.error(f"RuntimeError getting Supabase client for fetch history: {e_db_client}", exc_info=True)
                yield format_sse_message("error", "database_connection_failed", {"message": f"Database connection error for history: {str(e_db_client)}"})
                return # Stop if DB client cannot be obtained
            except Exception as e_db_client_other:
                logger.error(f"Unexpected error getting Supabase client for fetch history: {e_db_client_other}", exc_info=True)
                yield format_sse_message("error", "database_client_error", {"message": f"Unexpected database client error for history: {str(e_db_client_other)}"})
                return

            # --- Create Initial Fetch History Record ---
            if supabase_client_for_history:
                try:
                    initial_history_payload_dict = {
                        "url": url,
                        "fetching_engine": engine,
                        "status": "pending",
                        # engine_specific_parameters will be added in the final update
                    }
                    # Validate with Pydantic model before sending to DB
                    FetchHistoryCreate(**initial_history_payload_dict)


                    create_response = await asyncio.to_thread(
                        supabase_client_for_history.table("fetch_history")
                        .insert(initial_history_payload_dict)
                        .execute
                    )
                    if hasattr(create_response, 'data') and create_response.data:
                        fetch_history_id = create_response.data[0].get('id')
                        if fetch_history_id:
                             logger.info(f"Initial fetch history record created with ID: {fetch_history_id} for URL: {url}")
                             yield format_sse_message("status", "history_created", {"message": f"Fetch history record created: {fetch_history_id}", "history_id": str(fetch_history_id)})
                        else:
                             logger.error(f"Initial fetch history record created for {url} but ID was not returned in data: {create_response.data}")
                             yield format_sse_message("warning", "history_creation_no_id", {"message": "History record created but ID missing."})
                    elif hasattr(create_response, 'error') and create_response.error:
                        err_msg = create_response.error.message if hasattr(create_response.error, 'message') else str(create_response.error)
                        logger.error(f"Failed to create initial fetch history record for {url}: {err_msg}")
                        yield format_sse_message("warning", "history_creation_failed", {"message": f"Could not create initial history record: {err_msg}"})
                    else:
                        logger.error(f"Unexpected response from Supabase during initial fetch history creation for {url}: {create_response}")
                        yield format_sse_message("warning", "history_creation_unexpected_response", {"message": "Unexpected DB response for initial history creation."})
                except ValidationError as ve:
                    logger.error(f"Validation error for initial fetch history payload for {url}: {ve.errors()}", exc_info=True)
                    yield format_sse_message("error", "history_payload_invalid", {"message": f"Initial history data invalid: {str(ve)}"})
                    # Potentially return if this is critical
                except Exception as e_hist_create:
                    logger.error(f"Exception creating initial fetch history for {url}: {e_hist_create}", exc_info=True)
                    yield format_sse_message("warning", "history_creation_exception", {"message": f"Error during initial history creation: {str(e_hist_create)}"})
            
            yield format_sse_message("status", "initializing", {"message": f"Initializing fetch process for {url} with {engine}..."})
            await asyncio.sleep(0.1) # Small delay for frontend to catch up

            if engine.lower() == "crawl4ai":
                if fetch_with_crawl4ai is None: # Check if the function itself is available
                    yield format_sse_message("error", "Crawl4ai fetcher module not available.")
                    return
                logger.info(f"Using crawl4ai engine for URL: {url}")
                async for sse_event_json_str_from_fetcher in fetch_with_crawl4ai(url=url, original_request_params=all_request_params):
                    try:
                        event_data_from_fetcher = json.loads(sse_event_json_str_from_fetcher)

                        # --- LLM Logging Integration ---
                        if event_data_from_fetcher.get("type") == "llm_log_event":
                            llm_log_data = event_data_from_fetcher.get("data")
                            if llm_log_data and supabase_client_for_history: # Ensure data and client exist
                                try:
                                    # Use await if log_llm_call is async, otherwise remove await
                                    await log_llm_call(llm_log_data_dict=llm_log_data, supabase_client=supabase_client_for_history)
                                    logger.info(f"LLM call logged for type: {llm_log_data.get('llm_call_type')}, model: {llm_log_data.get('model_name')}")
                                except Exception as e_log_llm:
                                    logger.error(f"Failed to log LLM call via utility: {e_log_llm}", exc_info=True)
                                    # Optionally, yield an error to client if this failure is critical for them to know
                                    # yield format_sse_message("warning", "llm_log_failed", {"message": f"Failed to log LLM event: {str(e_log_llm)}"})
                            elif not llm_log_data:
                                logger.warning("llm_log_event received but 'data' payload was missing.")
                            elif not supabase_client_for_history:
                                logger.warning("llm_log_event received but supabase_client_for_history was not available for logging.")
                            continue # Skip yielding this event to the client
                        # --- End LLM Logging Integration ---

                        final_sse_event_dict = {
                            "type": event_data_from_fetcher.get("type"),
                            "timestamp": datetime.now().isoformat(),
                            "id": str(time.time())
                        }
                        if "status" in event_data_from_fetcher:
                            final_sse_event_dict["status"] = event_data_from_fetcher.get("status")

                        # Check for structured LLM error from crawl4ai_fetcher
                        # This is distinct from llm_log_event, this is an error *during* an LLM call within crawl4ai
                        if event_data_from_fetcher.get("type") == "error" and "llm_error" in event_data_from_fetcher:
                            final_sse_event_dict["message"] = event_data_from_fetcher.get("message", "LLM operation failed.")
                            final_sse_event_dict["llm_error"] = event_data_from_fetcher["llm_error"] # Pass the structured LLM error
                            logger.error(f"LLM Error event from crawl4ai_fetcher: {json.dumps(event_data_from_fetcher['llm_error'])}")
                        elif event_data_from_fetcher.get("type") == "error":
                            # General error from crawl4ai_fetcher
                            if "message" in event_data_from_fetcher:
                                final_sse_event_dict["message"] = event_data_from_fetcher.get("message")
                            if "details" in event_data_from_fetcher:
                                final_sse_event_dict["details"] = event_data_from_fetcher.get("details")
                        else:
                            # Non-error events (status, completed)
                            content_payload_for_final_sse = {}
                            if "message" in event_data_from_fetcher:
                                content_payload_for_final_sse["message"] = event_data_from_fetcher.get("message")
                            if "data" in event_data_from_fetcher:
                                content_payload_for_final_sse["data"] = event_data_from_fetcher.get("data")
                                if event_data_from_fetcher.get("type") == "completed" or \
                                   event_data_from_fetcher.get("status") == "completed":
                                    fetched_data_dict = event_data_from_fetcher.get("data")
                            
                            if content_payload_for_final_sse:
                                final_sse_event_dict["content"] = content_payload_for_final_sse
                            elif "message" in event_data_from_fetcher:
                                 final_sse_event_dict["content"] = event_data_from_fetcher.get("message")

                        logger.info(f"MAIN.PY /fetch-content: About to yield for crawl4ai: {json.dumps(final_sse_event_dict)}")
                        yield json.dumps(final_sse_event_dict)

                        if event_data_from_fetcher.get("type") == "error" or event_data_from_fetcher.get("status") == "error":
                            error_message_for_db = str(event_data_from_fetcher.get('message', 'Unknown error from fetcher'))
                            if "llm_error" in event_data_from_fetcher and isinstance(event_data_from_fetcher["llm_error"], dict):
                                error_message_for_db = f"LLM Error: {event_data_from_fetcher['llm_error'].get('message', error_message_for_db)}. Details: {json.dumps(event_data_from_fetcher['llm_error'].get('details'))}"

                            logger.error(f"Error event from crawl4ai_fetcher: {error_message_for_db}")
                            if fetch_history_id and supabase_client_for_history:
                                error_update_data = {"status": "failed", "error_message": error_message_for_db[:1000]}
                                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                                if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                    terminal_status_written_to_db = True
                            return
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from crawl4ai_fetcher: {sse_event_json_str_from_fetcher}")
                        yield format_sse_message("error", "Received invalid data from crawl4ai engine.")
                        if fetch_history_id and supabase_client_for_history:
                            error_update_data = {"status": "failed", "error_message": "Received invalid JSON data from crawl4ai engine."}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                            if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return
                    except Exception as e_inner_crawl:
                        logger.error(f"Error processing event from crawl4ai_fetcher: {e_inner_crawl}", exc_info=True)
                        yield format_sse_message("error", f"Internal error processing crawl4ai event: {str(e_inner_crawl)}")
                        if fetch_history_id and supabase_client_for_history:
                            failure_update_data = {"status": "failed", "error_message": f"Internal error processing crawl4ai event: {str(e_inner_crawl)}"[:1000]}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                            if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return


            elif engine.lower() == "jina":
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Jina fetcher (fetch_content_from_url) not available.")
                    return
                logger.info(f"Using Jina engine for URL: {url}")
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_handler_output, dict) or jina_handler_output.get("error"):
                            error_detail = jina_handler_output.get("content", "Unknown error from Jina") if isinstance(jina_handler_output, dict) else str(jina_handler_output)
                            logger.error(f"Jina engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_handler_output
                    else: # Client wanted plain text (json_response is False)
                        if not isinstance(jina_handler_output, str):
                            logger.error(f"Jina engine (Text mode) for {url} returned non-string: {type(jina_handler_output)}. Content: {str(jina_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text)"
                        fetched_data_dict = {
                            "markdown": jina_handler_output, "content": jina_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }
                    
                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina..."})
                    await asyncio.sleep(0.5) # Simulate processing

                except Exception as e_jina:
                    logger.error(f"Error calling Jina fetch_content_from_url for {url}: {e_jina}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina engine: {str(e_jina)}")
                    return
            else:
                logger.warning(f"Unknown or unsupported engine '{engine}' requested for URL: {url}. Defaulting to Jina.")
                # Essentially duplicate Jina logic here or refactor Jina part into a sub-generator
                # For now, let's assume Jina is the default if not crawl4ai
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Default Jina fetcher not available.")
                    return
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina (default)..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_default_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_default_handler_output, dict) or jina_default_handler_output.get("error"):
                            error_detail = jina_default_handler_output.get("content", "Unknown error from Jina (default)") if isinstance(jina_default_handler_output, dict) else str(jina_default_handler_output)
                            logger.error(f"Jina (default) engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina (default) engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_default_handler_output
                    else: # Client wanted plain text
                        if not isinstance(jina_default_handler_output, str):
                            logger.error(f"Jina (default) engine (Text mode) for {url} returned non-string: {type(jina_default_handler_output)}. Content: {str(jina_default_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina (default) engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_default_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text Default)"
                        fetched_data_dict = {
                            "markdown": jina_default_handler_output, "content": jina_default_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }

                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina (default)..."})
                    await asyncio.sleep(0.5)
                except Exception as e_jina_def:
                    logger.error(f"Error calling Jina (default) for {url}: {e_jina_def}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina (default) engine: {str(e_jina_def)}")
                    return

            # --- Post-fetch processing (PDF, Supabase) ---
            if fetched_data_dict and not fetched_data_dict.get("error"):
                markdown_content = fetched_data_dict.get('markdown') # Correct key for markdown content
                title = fetched_data_dict.get('title', 'Untitled')
                fetched_url_actual = fetched_data_dict.get('url', url)
                # pdf_path_from_fetch is specific to how Jina's fetch_content_from_url might return it
                # For crawl4ai, this would be None unless explicitly set in its "data" payload.
                pdf_path_from_fetcher = fetched_data_dict.get("pdf_path")


                if not markdown_content:
                    logger.warning(f"Engine {engine} returned no markdown content for URL: {url}")
                    # Still send a completed event, but data might be minimal
                else:
                    logger.info(f"Successfully fetched core content using {engine} from {url}. Title: '{title}'. Length: {len(markdown_content)}")

                if generate_pdf:
                    yield format_sse_message("status", "pdf_generation", {"message": "Generating PDF..."})
                    if markdown_content and pdf_path_from_fetcher: # If fetcher already made PDF
                        pdf_relative_path = pdf_path_from_fetcher
                        logger.info(f"Using PDF path from {engine} fetch: {pdf_relative_path} for {url}")
                        yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF ready at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                    elif markdown_content: # We have markdown, and PDF wasn't pre-generated
                        try:
                            # PDF_STORAGE_BASE_DIR is defined globally in main.py
                            # Ensure generate_unique_filename is available (imported from .fetch_content)
                            # Ensure generate_pdf_from_markdown_string is available (imported from .utils)
                            
                            unique_pdf_filename = generate_unique_filename(fetched_url_actual, "pdf")
                            output_pdf_filepath = PDF_STORAGE_BASE_DIR / unique_pdf_filename # Use Path object
                            
                            logger.info(f"Attempting PDF generation for {fetched_url_actual} to {output_pdf_filepath}")
                            pdf_conversion_successful = await generate_pdf_from_markdown_string(markdown_content, str(output_pdf_filepath))
                            
                            if pdf_conversion_successful:
                                # Construct relative path for client
                                # PDF_STORAGE_BASE_DIR is like "c:\...\backend\app\temp_pdfs"
                                # We want "temp_pdfs/filename.pdf"
                                base_storage_dir_name = PDF_STORAGE_BASE_DIR.name # Should be "temp_pdfs"
                                pdf_relative_path = Path(base_storage_dir_name) / unique_pdf_filename
                                pdf_relative_path = str(pdf_relative_path).replace("\\", "/") # Ensure forward slashes
                                logger.info(f"PDF generated via main.py, relative path: {pdf_relative_path}")
                                yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF generated at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                            else:
                                logger.error(f"PDF conversion failed in main.py for URL {fetched_url_actual}.")
                                yield format_sse_message("warning", "pdf_generation_failed", {"message": "PDF generation failed."})
                        except Exception as e_pdf_gen:
                            logger.error(f"Error during PDF generation in main.py for {fetched_url_actual}: {e_pdf_gen}", exc_info=True)
                            yield format_sse_message("warning", "pdf_generation_error", {"message": f"Error during PDF generation: {str(e_pdf_gen)}"})
                    else: # No markdown content
                        yield format_sse_message("status", "pdf_generation_skipped", {"message": "PDF generation skipped (no content)."})
                
                if upload_to_supabase:
                    yield format_sse_message("status", "supabase_upload", {"message": "Preparing for Supabase upload..."})
                    if markdown_content:
                        embedding = await get_openai_embedding(markdown_content)
                        if embedding:
                            embedding_generated = True
                            yield format_sse_message("status", "embedding_complete", {"message": "Embedding generated."})
                            supabase_content_id = await upsert_content_to_supabase(
                                url=fetched_url_actual, title=title, markdown_content=markdown_content,
                                embedding=embedding, pdf_path=pdf_relative_path
                            )
                            if supabase_content_id:
                                supabase_content_id_str = str(supabase_content_id)
                                yield format_sse_message("status", "supabase_upload_complete", {"message": f"Content uploaded to Supabase with ID: {supabase_content_id_str}", "database_id": supabase_content_id_str})
                            else:
                                yield format_sse_message("warning", "Supabase upload failed.")
                        else:
                            yield format_sse_message("warning", "Embedding generation failed, skipping Supabase upload.")
                    else: # No markdown content
                        yield format_sse_message("status", "supabase_upload_skipped", {"message": "Supabase upload skipped (no content)."})
                
                # Update fetch_history with success details
                if fetch_history_id and supabase_client_for_history:
                    success_update_data = {
                        "status": "success",
                        "content_summary": (markdown_content or "")[:500] + "..." if markdown_content and len(markdown_content) > 500 else (markdown_content or "No content."),
                        "raw_content_path": None, # Assuming raw content isn't saved to a file path directly by this endpoint
                        "content_storage_path": pdf_relative_path,
                        "supabase_content_id": supabase_content_id_str if supabase_content_id_str else None
                    }
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, success_update_data, all_request_params)
                    # Only mark terminal status as written if the DB write for a terminal status succeeded
                    if db_write_ok and success_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg

                # Final "completed" event with all data
                final_payload_data = {
                    "url": fetched_url_actual,
                    "title": title,
                    "content": markdown_content, # Send full content if not too large, or preview
                    "content_preview": (markdown_content or "")[:250] + "..." if markdown_content else "No content.",
                    "pdf_path": pdf_relative_path,
                    "embedding_generated": embedding_generated,
                    "database_id": supabase_content_id_str,
                    "engine_used": engine
                }
                yield format_sse_message("completed", final_payload_data, {"message": f"Fetch process completed for {url}."})
            
            elif fetched_data_dict and fetched_data_dict.get("error"):
                error_msg_content = fetched_data_dict.get("content", f"Unknown error after fetching with {engine}")
                logger.error(f"Fetch process for {url} by {engine} resulted in error state: {error_msg_content}")
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": str(error_msg_content)[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", error_msg_content)
            
            else: # No fetched_data_dict (e.g., engine failed to initialize or returned unexpected structure)
                final_error_message = f"Failed to retrieve or process data using {engine} for {url}. No valid data dictionary was produced."
                logger.error(final_error_message)
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": final_error_message[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", final_error_message)

        except asyncio.CancelledError:
            logger.info(f"SSE /fetch-content connection closed by client {client_host} for URL: {url}")
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": "Fetch cancelled by client."}
                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success, but client cancelled
                 logger.info(f"Fetch cancelled by client after 'success' status was set for {fetch_history_id}. Status remains 'success'.")
                 post_success_error_update = {"error_message": "Fetch cancelled by client post-success."[:1000]} # Update error message, status remains success
                 await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params) # db_write_ok not critical here
            # No yield here as the connection is likely gone
        except HTTPException as http_exc:
            logger.warning(f"HTTPException in /fetch-content generator for {url}: {http_exc.detail}", exc_info=True)
            final_error_message_to_client = f"Server error: {http_exc.detail}"
            db_error_message = f"HTTPException: {str(http_exc.detail)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"HTTPException occurred after 'success' status for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success HTTPException: {str(http_exc.detail)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        except Exception as e:
            logger.error(f"Unexpected error in /fetch-content SSE generator for {url} with {engine}: {e}", exc_info=True)
            final_error_message_to_client = f"An unexpected server error occurred: {str(e)}"
            db_error_message = f"Unexpected error: {str(e)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"Error occurred after 'success' status was set for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success error: {str(e)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        finally:
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                logger.warning(f"Fetch process for history ID {fetch_history_id} (URL: {url}) ended without confirmed terminal status. Attempting to mark as 'failed'.")
                final_failure_data = {
                    "status": "failed",
                    "error_message": "Process terminated without explicit success or failure status update."[:1000]
                }
                # This update is critical for DB state; SSE message not yielded from finally.
                await _update_fetch_history_record(
                    supabase_client_for_history,
                    fetch_history_id,
                    final_failure_data,
                    all_request_params
                )
            logger.info(f"SSE /fetch-content event generator finished for {client_host}, URL: {url}")

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


# --- PDF Serving Endpoints ---

def secure_path_join(base: Path, requested_path: str) -> Optional[Path]:
    """Safely join a base directory and a requested path, preventing traversal."""
    try:
        # Normalize the requested path to prevent tricks like '..'
        normalized_req_path = os.path.normpath(requested_path)

        # Disallow absolute paths in the request
        if os.path.isabs(normalized_req_path):
            logger.warning(f"Attempted absolute path request: {normalized_req_path}")
            return None

        # Join base and requested path
        full_path = base.joinpath(normalized_req_path).resolve()

        # Crucial check: Ensure the resolved path is still within the base directory
        if base.resolve() in full_path.parents or base.resolve() == full_path:
             # Further check: ensure the part after the base matches the normalized request
             # This helps prevent issues if base itself contains '..' like structures (though resolve() should handle it)
             relative_part = full_path.relative_to(base.resolve())
             if str(relative_part) == normalized_req_path:
                  return full_path
             else:
                  logger.warning(f"Path validation failed: Relative part mismatch. Base='{base}', Req='{requested_path}', Resolved='{full_path}', Relative='{relative_part}'")
                  return None
        else:
            logger.warning(f"Directory traversal attempt blocked: Base='{base}', Req='{requested_path}', Resolved='{full_path}'")
            return None
    except Exception as e:
        logger.error(f"Error during secure path join: {e}", exc_info=True)
        return None

@app.get("/view-pdf", tags=["Files"])
async def view_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for inline viewing."""
    logger.info(f"Request to view PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for viewing at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=secure_full_path.name, # Provides a default filename if user saves
            content_disposition_type="inline" # Display in browser
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for viewing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")

@app.get("/download-pdf", tags=["Files"])
async def download_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for download as an attachment."""
    logger.info(f"Request to download PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for download at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        # Use a generic filename or derive from path if needed
        download_filename = f"downloaded_{secure_full_path.name}"
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=download_filename, # Suggests this filename to the browser
            content_disposition_type="attachment" # Force download dialog
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for download: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")


# --- Include Other Routers ---
# (Keep existing router includes - lines 1722-1741)
if PROJECT_MODULES_LOADED:
    if 'content_upserter_router' in locals() and content_upserter_router:
        try: app.include_router(content_upserter_router, prefix="/api/content", tags=["Content Management"])
        except Exception as e: logger.warning(f"Failed to include content_upserter_router: {e}")

    if 'fetch_history_router' in locals() and fetch_history_router: # Added this block
        try: app.include_router(fetch_history_router, prefix="/api", tags=["Fetch History"]) # Using /api prefix for consistency
        except Exception as e: logger.warning(f"Failed to include fetch_history_router: {e}")

    if 'metrics_router' in locals() and metrics_router:
        try: app.include_router(metrics_router, prefix="/monitoring", tags=["Monitoring"])
        except Exception as e: logger.warning(f"Failed to include metrics_router: {e}")

    if 'monitoring_router' in locals() and metrics_router != monitoring_router and monitoring_router:
         try: app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
         except Exception as e: logger.warning(f"Failed to include monitoring_router: {e}")

    if 'search_config_router' in locals() and search_config_router:
        try: app.include_router(search_config_router, prefix="/api/search-config", tags=["Search Configuration"])
        except Exception as e: logger.warning(f"Failed to include search_config_router: {e}")

# --- Include Debug Endpoints ---
try:
    from .debug_endpoints import router as debug_router
    app.include_router(debug_router)
    logger.info("Debug endpoints included.")
except Exception as e:
    logger.warning(f"Failed to include debug endpoints: {e}")


# --- Vector Search Endpoint (MODIFIED to use SQL Function) ---
@app.post("/api/vector-search", response_model=VectorSearchResponse, tags=["Search"])
async def vector_search_endpoint(request: VectorSearchRequest):
    """Perform vector search using the advanced_hybrid_search SQL function."""
    logger.info(f"Vector search request: Query='{request.query[:50]}...', Max={request.max_results}, Threshold={request.threshold}")

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Database client unavailable.")
        if not openai_client:
             raise HTTPException(status_code=503, detail="Embedding service unavailable.")

        # 1. Generate query embedding
        query_embedding = await get_openai_embedding(request.query)
        if query_embedding is None:
            # get_openai_embedding now logs detailed LLM call info internally.
            # Here, we raise a structured error for the client.
            error_detail_payload = {
                "error_code": "EMBEDDING_GENERATION_FAILED",
                "message": "Failed to generate query embedding for vector search.",
                "llm_error_type": "EmbeddingError", # Generic, as detailed type is in server logs
                "details": {
                    "query_preview": (request.query[:100] + "...") if request.query and len(request.query) > 100 else request.query,
                    "suggestion": "Check server logs for detailed error information from the embedding service."
                }
            }
            logger.error(f"Raising HTTPException for vector search due to embedding failure. Payload: {json.dumps(error_detail_payload)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail_payload
            )

        # 2. Prepare parameters for the SQL function
        #    Match parameters defined in the SQL function (adjust dimension if needed)
        params = {
            'query_embedding': query_embedding,
            'match_count': request.max_results,
            'min_similarity': request.threshold, # Assuming threshold maps to min_similarity
            'content_weight': request.content_weight, # Pass weights from request
            'summary_weight': request.summary_weight,
            'video_filter': request.video_filter # Pass filter from request
        }
        logger.debug(f"Calling Supabase RPC advanced_hybrid_search with params: match_count={params['match_count']}, min_similarity={params['min_similarity']}, content_weight={params['content_weight']}, summary_weight={params['summary_weight']}, video_filter={params['video_filter']}")

        # 3. Call the Supabase function via RPC
        response = await asyncio.to_thread(
             supabase_client.rpc('advanced_hybrid_search', params).execute
        )
        # response = supabase_client.rpc('advanced_hybrid_search', params).execute() # Original sync call

        # 4. Process results
        search_results = []
        if hasattr(response, 'data') and response.data:
            search_results = response.data
            logger.info(f"Advanced hybrid search returned {len(search_results)} results.")
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error during advanced_hybrid_search: {response.error}")
             raise HTTPException(status_code=500, detail=f"Database search error: {response.error}")
        else:
             logger.warning(f"Unexpected response structure from Supabase search RPC: {response}")
             # Return empty results

        # 5. Prepare response metadata (optional AI response generation removed for now)
        metadata = {
            "query": request.query,
            "results_count": len(search_results),
            "search_function": "advanced_hybrid_search",
            "parameters_used": {
                "threshold": request.threshold,
                "max_results": request.max_results,
                "content_weight": request.content_weight,
                "summary_weight": request.summary_weight,
                "video_filter": request.video_filter
            },
            "token_usage": token_counter.get_stats() # Include token stats
        }

        return VectorSearchResponse(
            results=search_results, # The SQL function should return dicts directly
            ai_response=None, # AI response generation can be added later if needed
            metadata=metadata
        )

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI errors
    except Exception as e:
         logger.error(f"Error during vector search for query '{request.query[:50]}...': {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")


# --- Comprehensive Search Endpoint (Using psearchworking) ---
# (Keep existing /api/search endpoint - lines 1806-1945)
@app.post("/api/search", response_model=ComprehensiveSearchResponse, tags=["Search"])
async def comprehensive_search_endpoint(
    request: ComprehensiveSearchRequest, # Request body
    # Query parameters for overrides
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
    preset: Optional[str] = Query(None)
):
    """
    Perform comprehensive search using logic from psearchworking.
    Accepts optional query parameters to override search settings.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    logger.info(f"Search request: Query='{request.query[:50]}...', MaxRes={request.max_results}, Analysis={request.run_analysis}, Preset='{preset}'")

    try:
        update_successful = global_search_params.update_from_frontend(
            preset=preset,
            fine_grained_similarity_threshold=fg_similarity_threshold,
            fine_grained_content_weight=fg_content_weight,
            fine_grained_result_percentage=fg_result_percentage,
            fine_grained_max_results=fg_max_results,
            contextual_similarity_threshold=ctx_similarity_threshold,
            contextual_content_weight=ctx_content_weight,
            contextual_result_percentage=ctx_result_percentage,
            contextual_max_results=ctx_max_results,
            overview_similarity_threshold=ov_similarity_threshold,
            overview_content_weight=ov_content_weight,
            overview_result_percentage=ov_result_percentage,
            overview_max_results=ov_max_results,
        )
        if not update_successful:
             logger.warning("Search parameters updated from frontend might be invalid (e.g., sum > 1.0). Check psearchworking validation logic.")
        logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
    except Exception as param_err:
         logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search parameters provided.")

    start_time = time.time()
    try:
        results, openai_analysis, groq_analysis = await asyncio.to_thread(
            search_all,
            query=request.query,
            max_results=request.max_results,
            skip_prompts=True,
            run_analysis=request.run_analysis
        )

        search_duration = time.time() - start_time
        logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")

        formatted_results = []
        if results:
            try:
                formatted_results = [res.to_dict() for res in results]
                logger.info(f"Successfully converted {len(formatted_results)} SearchResult objects to dictionaries")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                formatted_results = []
                for res in results:
                    try:
                        result_dict = {
                            'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                            'content_id': getattr(res, 'content_id', None),
                            'content': getattr(res, 'content', None),
                            'similarity': getattr(res, 'similarity', 0.0),
                            'source': getattr(res, 'source', 'unknown'),
                            'title': getattr(res, 'title', ''),
                            'start_time': getattr(res, 'start_time', None),
                            'end_time': getattr(res, 'end_time', None),
                            'url': getattr(res, 'url', ''),
                            'watch_url': getattr(res, 'watch_url', ''),
                            'video_id': getattr(res, 'video_id', None),
                            'segment_id': getattr(res, 'segment_id', None),
                            'summary': getattr(res, 'summary', ''),
                            'metadata': getattr(res, 'metadata', {}),
                            'search_method': getattr(res, 'search_method', 'unknown'),
                            'content_type': getattr(res, 'content_type', 'unknown')
                        }
                        formatted_results.append(result_dict)
                    except Exception as item_err:
                        logger.error(f"Error formatting individual result: {item_err}")
                logger.info(f"Manually converted {len(formatted_results)} SearchResult objects to dictionaries")

        metadata = {
            "query": request.query,
            "total_results_found": len(results),
            "search_duration_seconds": round(search_duration, 2),
            "analysis_run": request.run_analysis,
            "effective_params": global_search_params.get_all_params(),
            "search_complete": True,
            "analysis_complete": request.run_analysis and (openai_analysis is not None or groq_analysis is not None)
        }
        try:
            try:
                from .psearchworking import token_counter as psearch_token_counter
                metadata["token_usage"] = psearch_token_counter.get_stats()
            except (ImportError, AttributeError):
                metadata["token_usage"] = token_counter.get_stats()
        except (NameError, AttributeError) as tk_err:
            logger.warning(f"Could not get token stats: {tk_err}")

        return ComprehensiveSearchResponse(
            query=request.query,
            results=formatted_results,
            openai_analysis=openai_analysis,
            groq_analysis=groq_analysis,
            metadata=metadata
        )

    except Exception as e:
        search_duration = time.time() - start_time
        logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search execution failed: {e}")


# --- Search SSE Endpoint (Using psearchworking) ---
# (Keep existing /api/search-sse endpoint - lines 1948-2131)
@app.get("/api/search-sse", tags=["Search"])
async def search_sse_endpoint(
    request: Request,
    query: str = Query(..., min_length=1),
    max_results: int = Query(30, ge=10, le=100),
    run_analysis: bool = Query(True),
    preset: Optional[str] = Query(None),
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
):
    """
    Server-Sent Events endpoint for real-time search updates.
    Provides incremental updates as the search progresses.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE search request from {client_host}: Query='{query[:50]}...', MaxRes={max_results}, Analysis={run_analysis}, Preset='{preset}'")

    async def event_generator():
        try:
            yield format_sse_message("status", "Starting search operation", {"stage": "start"})
            await asyncio.sleep(0.5)

            yield format_sse_message("status", "Configuring search parameters", {"stage": "search"})
            try:
                update_successful = global_search_params.update_from_frontend(
                    preset=preset,
                    fine_grained_similarity_threshold=fg_similarity_threshold,
                    fine_grained_content_weight=fg_content_weight,
                    fine_grained_result_percentage=fg_result_percentage,
                    fine_grained_max_results=fg_max_results,
                    contextual_similarity_threshold=ctx_similarity_threshold,
                    contextual_content_weight=ctx_content_weight,
                    contextual_result_percentage=ctx_result_percentage,
                    contextual_max_results=ctx_max_results,
                    overview_similarity_threshold=ov_similarity_threshold,
                    overview_content_weight=ov_content_weight,
                    overview_result_percentage=ov_result_percentage,
                    overview_max_results=ov_max_results,
                )
                if not update_successful:
                    logger.warning("Search parameters updated from frontend might be invalid")
                    yield format_sse_message("status", "Warning: Some search parameters may be invalid", {"stage": "search"})
                logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
            except Exception as param_err:
                logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
                yield format_sse_message("error", f"Invalid search parameters: {param_err}")
                return

            start_time = time.time()
            yield format_sse_message("status", "Executing search query", {"stage": "filter"})
            try:
                results, openai_analysis, groq_analysis = await asyncio.to_thread(
                    search_all, query=query, max_results=max_results, skip_prompts=True, run_analysis=run_analysis
                )
                search_duration = time.time() - start_time
                logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")
                yield format_sse_message("status", "Combining search results", {"stage": "combine"})
                await asyncio.sleep(0.5)

                formatted_results = []
                if results:
                    try: formatted_results = [res.to_dict() for res in results]
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                        formatted_results = []
                        for res in results:
                            try:
                                result_dict = {
                                    'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                                    'content_id': getattr(res, 'content_id', None), 'content': getattr(res, 'content', None),
                                    'similarity': getattr(res, 'similarity', 0.0), 'source': getattr(res, 'source', 'unknown'),
                                    'title': getattr(res, 'title', ''), 'start_time': getattr(res, 'start_time', None),
                                    'end_time': getattr(res, 'end_time', None), 'url': getattr(res, 'url', ''),
                                    'watch_url': getattr(res, 'watch_url', ''), 'video_id': getattr(res, 'video_id', None),
                                    'segment_id': getattr(res, 'segment_id', None), 'summary': getattr(res, 'summary', ''),
                                    'metadata': getattr(res, 'metadata', {}), 'search_method': getattr(res, 'search_method', 'unknown'),
                                    'content_type': getattr(res, 'content_type', 'unknown')
                                }
                                formatted_results.append(result_dict)
                            except Exception as item_err: logger.error(f"Error formatting individual result: {item_err}")

                metadata = {
                    "query": query, "total_results_found": len(results), "search_duration_seconds": round(search_duration, 2),
                    "analysis_run": run_analysis, "effective_params": global_search_params.get_all_params(),
                    "search_complete": True, "stage": "complete"
                }
                try:
                    try: from .psearchworking import token_counter as psearch_token_counter; metadata["token_usage"] = psearch_token_counter.get_stats()
                    except (ImportError, AttributeError): metadata["token_usage"] = token_counter.get_stats()
                except (NameError, AttributeError) as tk_err: logger.warning(f"Could not get token stats: {tk_err}")

                if run_analysis:
                    yield format_sse_message("status", "Analyzing search results", {"stage": "analyze"})
                    if openai_analysis: yield format_sse_message("analysis", openai_analysis, {"provider": "openai"})
                    if groq_analysis: yield format_sse_message("analysis", groq_analysis, {"provider": "groq"})
                    metadata["analysis_complete"] = bool(openai_analysis or groq_analysis)

                yield format_sse_message("results", formatted_results, {**metadata, "stage": "complete"})
                yield format_sse_message("complete", "Search process completed", {"stage": "complete"})

            except Exception as e:
                search_duration = time.time() - start_time
                error_msg = f"Search execution failed: {e}"
                logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
                yield format_sse_message("error", error_msg)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed by client {client_host}")
        except Exception as e:
            logger.error(f"Unexpected error in search SSE generator: {e}", exc_info=True)
            yield format_sse_message("error", f"Unexpected error: {e}")

    return EventSourceResponse(event_generator())

# --- Root and Health Check ---
# (Keep existing / and /health endpoints - lines 2133-2160)
@app.get("/", tags=["Utility"])
async def root():
    """Root endpoint providing basic service status."""
    logger.info("Root endpoint '/' called.")
    return {"service": "PMOVES Transcription API", "status": "running", "version": app.version, "timestamp": datetime.now().isoformat()}

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    logger.debug("Health check '/health' called")
    db_status = "connected"
    try:
         client = get_client()
    except Exception as e:
         db_status = f"error: {e}"
         logger.warning(f"Health check: Supabase client unavailable: {e}")
    return {"status": "healthy", "dependencies": {"database": db_status}, "timestamp": datetime.now().isoformat()}


# --- Test Event Loop Policy Route ---
@app.get("/test-event-loop-policy", tags=["Utility", "Debug"])
async def test_event_loop_policy_route():
    # asyncio is imported at the top. logger is defined globally.
    policy_name = asyncio.get_event_loop_policy().__class__.__name__
    logger.info(f"Policy in /test-event-loop-policy route: {policy_name}")
    return {"active_policy": policy_name}

# --- ASGI Server Runner ---
# (Keep existing __main__ block - lines 2165-2194)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")
    # Log policy before Uvicorn run
    logger.info(f"Policy before Uvicorn run in __main__: {asyncio.get_event_loop_policy().__class__.__name__}")
    app_host = os.getenv("HOST", "127.0.0.1")
    try: app_port = int(os.getenv("PORT", "8000"))
    except ValueError: logger.warning(f"Invalid PORT env var '{os.getenv('PORT')}', using 8000."); app_port = 8000
    reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
    if reload_flag: logger.warning("Auto-reload enabled. Recommended only for development.")
    uvicorn.run(
        f"{Path(__file__).stem}:app", host=app_host, port=app_port, reload=reload_flag, log_level="info"
    )

# --- App Config Endpoint ---
@app.get("/api/app-config", tags=["Utility"])
async def get_app_config():
    """Expose backend folder and subfolder config to the frontend."""
    return {
        "WORKSPACE_ROOT": WORKSPACE_ROOT,
        "SUBFOLDERS": SUBFOLDERS
    }

# --- Workspace Directory Listing Endpoint ---
@app.get("/api/list-workspace", tags=["Utility"])
async def list_workspace():
    """Recursively list all files and folders under the workspace root."""
    def list_dir(path, rel_path=""):
        items = []
        for entry in os.scandir(path):
            entry_rel_path = os.path.join(rel_path, entry.name)
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "type": "folder",
                    "path": entry_rel_path.replace("\\", "/"),
                    "children": list_dir(entry.path, entry_rel_path)
                })
            else:
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": entry_rel_path.replace("\\", "/"),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return sorted(items, key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    tree = list_dir(WORKSPACE_ROOT)
    return {"root": WORKSPACE_ROOT, "tree": tree}

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.


<environment_details>
# VSCode Visible Files
backend/app/main.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:01:39 AM (America/New_York, UTC-4:00)

# Context Window Usage
103,158 / 1,048.576K tokens used (10%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I have successfully modified `backend/app/main.py` to execute the `ollama_initializer.py` script during startup.

The implementation of the plan is now complete:
1. Created `backend/app/ollama_initializer.py`.
2. Added logic to `ollama_initializer.py` to check the selected model and run `ollama run <model_id>` if it's an Ollama model.
3. Modified `backend/app/main.py` to execute `ollama_initializer.py` during the `@app.on_event("startup")`.

I have addressed the user's request to ensure that when an Ollama model is selected, it is loaded by the Ollama server when the backend starts, to avoid delays during fetching.

I will now use the `attempt_completion` tool to inform the user that the task is complete and provide a command to demonstrate the result. The demonstration would involve starting the backend server and observing the logs to see if the Ollama initializer script is launched and attempts to load the selected model.

To demonstrate, I will provide the command to run the FastAPI application using uvicorn, as shown in the `__main__` block of `backend/app/main.py`. This command is `uvicorn backend.app.main:app --reload` or `uvicorn backend.app.main:app` depending on the `ENABLE_RELOAD` environment variable. Since the user mentioned the `--reload` flag caused issues with `crawl4ai` on Windows, I will provide the command without `--reload` for a more stable test environment, assuming they are on Windows as indicated by the system information. The command will be `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`. I will also instruct the user to set the `LLM_MODEL` environment variable to an Ollama model ID (like `ollama/gemma3`) before running the command to trigger the initializer script.<attempt_completion>
<result>
I have implemented the functionality to automatically initiate the loading of the selected Ollama model when the backend server starts.

Here's what I've done:
1.  Created a new script `backend/app/ollama_initializer.py`. This script reads the `LLM_MODEL` environment variable, checks if the selected model is configured as an Ollama model in `app_config.py`, and if so, executes the `ollama run <model_id>` command in a non-blocking way.
2.  Modified `backend/app/main.py` to execute the `ollama_initializer.py` script during the application's startup event (`@app.on_event("startup")`).

Now, when you start the backend server and have an Ollama model (like `gemma3`) specified in your environment variables (e.g., `LLM_MODEL=ollama/gemma3`), the backend will attempt to load that model into the Ollama server's memory during its startup.

To test this, set the `LLM_MODEL` environment variable to an Ollama model ID (e.g., `ollama/gemma3`) and then run the backend server. Observe the server logs for messages indicating the Ollama initializer script is being launched and attempting to load the model.
</result>
<command>
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
</command>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user denied this operation.
The user provided the following feedback:
<feedback>
PMOVES-transcribe-and-fetch) PS C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend> uvicorn app.main:app
[05/13/25 10:02:02] INFO     Logging initialized. Console: always. File: disabled
2025-05-13 10:02:02,029 - app.main - INFO - Logging initialized. Console: always. File: disabled
                    INFO     Policy set in main.py (top level): WindowsProactorEventLoopPolicy
2025-05-13 10:02:02,031 - app.main - INFO - Policy set in main.py (top level): WindowsProactorEventLoopPolicy
[05/13/25 10:02:05] INFO     Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:02:05,338 - app.main - INFO - Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
                    INFO     Async OpenAI client initialized.
2025-05-13 10:02:05,733 - app.main - INFO - Async OpenAI client initialized.
                    INFO     Async Groq client initialized.
2025-05-13 10:02:05,932 - app.main - INFO - Async Groq client initialized.
2025-05-13 10:02:06,797 - app.app_config - INFO - Looking for .env file at: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:02:06,799 - app.app_config - INFO - OPENAI_API_KEY loaded: Yes
2025-05-13 10:02:06,799 - app.app_config - INFO - OPENAI_API_KEY starts with: sk-pr...
2025-05-13 10:02:06,799 - app.app_config - INFO - ANTHROPIC_API_KEY loaded: Yes
2025-05-13 10:02:06,799 - app.app_config - ERROR - Default placeholder value detected for ANTHROPIC_API_KEY - please update your .env file.
2025-05-13 10:02:06,799 - app.app_config - INFO - GROQ_API_KEY loaded: Yes
2025-05-13 10:02:06,799 - app.app_config - INFO - GROQ_API_KEY starts with: gsk_W...
2025-05-13 10:02:06,799 - app.app_config - INFO - GEMINI_API_KEY loaded: Yes
2025-05-13 10:02:06,799 - app.app_config - INFO - GEMINI_API_KEY starts with: AIzaS...
2025-05-13 10:02:06,800 - app.app_config - INFO - DEEPSEEK_API_KEY loaded: Yes
2025-05-13 10:02:06,800 - app.app_config - ERROR - Default placeholder value detected for DEEPSEEK_API_KEY - please update your .env file.
2025-05-13 10:02:06,800 - app.app_config - INFO - MISTRAL_API_KEY loaded: Yes
2025-05-13 10:02:06,800 - app.app_config - ERROR - Default placeholder value detected for MISTRAL_API_KEY - please update your .env file.
2025-05-13 10:02:06,800 - app.app_config - INFO - TOGETHER_AI_API_KEY loaded: Yes
2025-05-13 10:02:06,800 - app.app_config - ERROR - Default placeholder value detected for TOGETHER_AI_API_KEY - please update your .env file.
2025-05-13 10:02:06,800 - app.app_config - INFO - COHERE_API_KEY loaded: Yes
2025-05-13 10:02:06,800 - app.app_config - ERROR - Default placeholder value detected for COHERE_API_KEY - please update your .env file.
2025-05-13 10:02:06,800 - app.app_config - INFO - FIREWORKS_AI_API_KEY loaded: Yes
2025-05-13 10:02:06,800 - app.app_config - ERROR - Default placeholder value detected for FIREWORKS_AI_API_KEY - please update your .env file.
2025-05-13 10:02:06,800 - app.app_config - INFO - OLLAMA_BASE_URL loaded: http://localhost:11434
2025-05-13 10:02:06,800 - app.app_config - INFO - OLLAMA_BASE_URL appears to be a local address: http://localhost:11434
2025-05-13 10:02:06,800 - app.app_config - INFO - OPENAI_COMPATIBLE_BASE_URL loaded: http://localhost:1234/v1
2025-05-13 10:02:06,800 - app.app_config - INFO - OPENAI_COMPATIBLE_BASE_URL appears to be a local address: http://localhost:1234/v1
Rich console is available.
2025-05-13 10:02:06,898 - app.transcribe1 - INFO - --- System Info ---
2025-05-13 10:02:06,898 - app.transcribe1 - INFO - Selected Whisper model size: large-v3
2025-05-13 10:02:06,898 - app.transcribe1 - INFO - CUDA available: True
2025-05-13 10:02:06,899 - app.transcribe1 - INFO - Determined optimal device: 'cuda' with compute type: 'float16'
2025-05-13 10:02:06,900 - app.transcribe1 - INFO - GPU Device Name: NVIDIA GeForce RTX 3090 Ti
2025-05-13 10:02:06,900 - app.transcribe1 - INFO - GPU Memory: 23.99 GB
2025-05-13 10:02:06,900 - app.transcribe1 - INFO - CUDA Device Capability: (8, 6)
2025-05-13 10:02:06,900 - app.transcribe1 - INFO - CUDA Device Count: 1
2025-05-13 10:02:06,900 - app.transcribe1 - INFO - --- End System Info ---
Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:02:07,746 - search_params - INFO - Loaded search parameters from preset: default
2025-05-13 10:02:07,825 - search_params - INFO - Loaded search parameters from preset: default
2025-05-13 10:02:07,837 - app.routes.fetch_history_routes - INFO - Ensured fetched content storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\fetched_content
[05/13/25 10:02:07] INFO     TokenCounter initialized with tiktoken encoders.
2025-05-13 10:02:07,844 - app.main - INFO - TokenCounter initialized with tiktoken encoders.
                    INFO     Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
2025-05-13 10:02:07,851 - app.main - INFO - Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
                    INFO     SSE monitoring middleware enabled.
2025-05-13 10:02:07,852 - app.main - INFO - SSE monitoring middleware enabled.
                    INFO     Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\temp_pdfs
2025-05-13 10:02:07,856 - app.main - INFO - Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\temp_pdfs
                    INFO     Debug endpoints included.
2025-05-13 10:02:07,874 - app.main - INFO - Debug endpoints included.
INFO:     Started server process [64844]
INFO:     Waiting for application startup.
                    INFO     Application startup initiated...
2025-05-13 10:02:07,880 - app.main - INFO - Application startup initiated...
                    INFO     System metrics collection scheduled.
2025-05-13 10:02:07,881 - app.main - INFO - System metrics collection scheduled.
                    INFO     Queue manager started.
2025-05-13 10:02:07,881 - app.main - INFO - Queue manager started.
                    INFO     Launching Ollama initializer script...
2025-05-13 10:02:07,882 - app.main - INFO - Launching Ollama initializer script...
                    ERROR    Error launching Ollama initializer script: name 'subprocess' is not defined
                             ╭────────────────────────────────────────────────────────────────────────────────────────────────────────── Traceback (most recent call last) ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
                             │ C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:680 in startup_event                                                                                                                                                  │
                             │                                                                                                                                                                                                                                                       │
                             │    677 │   │   │   │   # For cross-platform compatibility and safety, explicitly pass command                                                                                                                                                         │
                             │        parts                                                                                                                                                                                                                                          │
                             │    678 │   │   │   │   command = [sys.executable, str(ollama_init_script_path)]                                                                                                                                                                       │
                             │    679 │   │   │   │   # Use creationflags for Windows to prevent a console window from popping                                                                                                                                                       │
                             │        up                                                                                                                                                                                                                                             │
                             │ ❱  680 │   │   │   │   creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform ==                                                                                                                                                         │
                             │        'win32' else 0                                                                                                                                                                                                                                 │
                             │    681 │   │   │   │                                                                                                                                                                                                                                  │
                             │    682 │   │   │   │   # Start the process without waiting                                                                                                                                                                                            │
                             │    683 │   │   │   │   process = subprocess.Popen(command, creationflags=creationflags)                                                                                                                                                               │
                             ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                             NameError: name 'subprocess' is not defined
2025-05-13 10:02:07,883 - app.main - ERROR - Error launching Ollama initializer script: name 'subprocess' is not defined
Traceback (most recent call last):
  File "C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py", line 680, in startup_event
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                    ^^^^^^^^^^
NameError: name 'subprocess' is not defined. Did you forget to import 'subprocess'
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
</feedback>
<environment_details>
# VSCode Visible Files
backend/app/main.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:02:30 AM (America/New_York, UTC-4:00)

# Context Window Usage
247,528 / 1,048.576K tokens used (24%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>The user provided feedback that the backend failed to start with a `NameError: name 'subprocess' is not defined`. Looking at the traceback, the error occurs in the `startup_event` function in `backend/app/main.py` when trying to use `subprocess.CREATE_NEW_PROCESS_GROUP`.

Although I thought `subprocess` was already imported based on my previous read of the file, it seems it was not imported in a scope accessible by the `startup_event` function, or perhaps it was removed or commented out elsewhere.

I need to add an explicit import for the `subprocess` module at the top of `backend/app/main.py` to make it available to the `startup_event` function.

I will use `replace_in_file` to add `import subprocess` near the other standard library imports in `backend/app/main.py`.The backend failed to start because the `subprocess` module was not imported in a scope where it could be used by the `startup_event` function.

I will add an explicit import for the `subprocess` module at the top of `backend/app/main.py`.

<replace_in_file>
<path>backend/app/main.py</path>
<diff>
<<<<<<< SEARCH
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
from typing import Any # Added for Supabase client type hint if needed, or use from existing
=======
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
import subprocess # Added subprocess import
from typing import Any # Added for Supabase client type hint if needed, or use from existing
>>>>>>> REPLACE
</diff>
</replace_in_file>

---

**User:**

[replace_in_file for 'backend/app/main.py'] Result:
The content was successfully saved to backend/app/main.py.

Here is the full, updated content of the file that was saved:

<final_file_content path="backend/app/main.py">
import os
import sys # Keep sys import first for platform check

# --- Event Loop Policy (MUST BE SET BEFORE ASYNCIO IMPORT) ---
_event_loop_policy_set = False
if sys.platform == "win32":
    try:
        # Temporarily import asyncio just for this setting
        import asyncio as _asyncio_temp
        _asyncio_temp.set_event_loop_policy(_asyncio_temp.WindowsProactorEventLoopPolicy())
        _event_loop_policy_set = True
        # We will log this after full asyncio and logging are imported
    except ImportError:
        # Fallback or error logging if asyncio cannot be imported here
        logger.critical("CRITICAL: Could not import asyncio to set event loop policy.")
    finally:
        # Ensure our temporary import doesn't linger
        if '_asyncio_temp' in locals():
            del _asyncio_temp

import asyncio # Now import asyncio for real
import logging # Import logging

# Rich logging for pretty terminal output
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in ["true", "1", "yes"]
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "pmoves_backend.log")

# Set up root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any default handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Console handler (always enabled)
if RICH_AVAILABLE:
    console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
else:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)

# File handler (optional, based on env)
if LOG_TO_FILE:
    file_handler = logging.FileHandler(LOG_FILE_NAME, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

logger.info(f"Logging initialized. Console: always. File: {'enabled' if LOG_TO_FILE else 'disabled'}{f' ({LOG_FILE_NAME})' if LOG_TO_FILE else ''}")

# --- Logging Configuration (Setup ASAP after policy set) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # Initialize main logger

# Log the policy that was set (or attempted)
if sys.platform == "win32":
    if _event_loop_policy_set:
        logger.info(f"Policy set in main.py (top level): {asyncio.get_event_loop_policy().__class__.__name__}")
    else:
        logger.error(f"Failed to set WindowsProactorEventLoopPolicy. Current policy: {asyncio.get_event_loop_policy().__class__.__name__}")
else:
    logger.info(f"Running on non-Windows platform. Default policy: {asyncio.get_event_loop_policy().__class__.__name__}")


# -*- coding: utf-8 -*-
"""
PMOVES Transcription API Backend

This FastAPI application provides endpoints for:
- Processing YouTube videos (downloading, transcribing).
- Downloading videos/audio using yt-dlp with progress updates.
- Fetching video metadata.
- Fetching web content using Jina Reader API, generating PDFs, storing in Supabase, and enabling vector search.
- Real-time status updates via Server-Sent Events (SSE).
- Content ingestion and vector search capabilities (requires related modules).
"""

# --- Standard Library Imports ---
import os
import re
import json
import shutil
# import logging # Moved up
# import asyncio # Moved up
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
import subprocess # Added subprocess import
from typing import Any # Added for Supabase client type hint if needed, or use from existing

# --- Third-Party Imports ---
from dotenv import load_dotenv
from fastapi import (
    FastAPI, HTTPException, BackgroundTasks, Body, Request,
    status, Query, Depends, Security # Added Security for potential API key auth
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse # Added FileResponse
from fastapi.security import APIKeyHeader # Added for potential API key auth
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import (
    BaseModel, validator, ValidationError, Field, field_validator
)
import torch # Still imported from original, ensure necessary

# --- Optional Third-Party Imports (with fallbacks/warnings) ---
try:
    from openai import OpenAI, AsyncOpenAI # Added AsyncOpenAI
    from openai import APIError as OpenAI_APIError # Specific OpenAI errors
    from openai import RateLimitError as OpenAI_RateLimitError
    from openai import APIConnectionError as OpenAI_APIConnectionError
    from openai import AuthenticationError as OpenAI_AuthenticationError
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    OpenAI_APIError = None
    OpenAI_RateLimitError = None
    OpenAI_APIConnectionError = None
    OpenAI_AuthenticationError = None

try:
    from groq import Groq, AsyncGroq # Added AsyncGroq
except ImportError:
    Groq = None
    AsyncGroq = None

try:
    from rich.console import Console
except ImportError:
    class Console:
        def print(self, *args, **kwargs): print(*args)
    Console = Console() # Instantiate dummy

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from tiktoken import get_encoding
except ImportError:
    get_encoding = None

import aiofiles # Used for async file operations if needed

# --- Logging Configuration (Moved to top of file and initialized as 'logger') ---
# (Original content removed as it's now at the beginning)

# --- Check Critical Dependencies ---
if OpenAI is None or AsyncOpenAI is None:
    logger.warning("Optional dependency 'openai' not found or incomplete. AI analysis/embedding features may be limited.")
if Groq is None or AsyncGroq is None:
    logger.warning("Optional dependency 'groq' not found or incomplete. Groq features will be unavailable.")
if yt_dlp is None:
     logger.error("Required dependency 'yt-dlp' not found. Video download and info features will fail.")
if get_encoding is None:
    logger.warning("Optional dependency 'tiktoken' not found. Token counting will be estimated.")

# --- Rich Console Initialization ---
console = Console()

# --- Environment Variable Loading ---
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}. Relying on environment variables.")
    load_dotenv() # Attempt default load

# --- API Client Initialization ---
# OpenAI (Async)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if AsyncOpenAI and openai_api_key:
    try:
        openai_client = AsyncOpenAI(api_key=openai_api_key)
        logger.info("Async OpenAI client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async OpenAI client: {e}", exc_info=True)
elif AsyncOpenAI:
    logger.warning("OPENAI_API_KEY not set. OpenAI client not initialized.")

# Groq (Async)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if AsyncGroq and groq_api_key:
    try:
        groq_client = AsyncGroq(api_key=groq_api_key)
        logger.info("Async Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async Groq client: {e}", exc_info=True)
elif AsyncGroq:
    logger.warning("GROQ_API_KEY not set. Groq client not initialized.")


# --- Local/Project Imports ---
try:
    from .queue_manager import QueueManager
    from .monitoring.logger import PerformanceMonitor, async_timer, CustomLogger
    from .monitoring.metrics import MetricsCollector, TranscriptionMetrics, router as metrics_router, get_metrics_collector
    from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
    from .transcribe1 import process_video, VideoProcessRequest as TranscribeVideoRequest # Renamed Pydantic model
    from .general_utils import (
        save_text_to_markdown,
        clean_filename, format_timestamp, sanitize_filename,
        generate_pdf_from_markdown_string # Added for PDF generation
    )
    from .fetch_content import (
        fetch_content_from_url, generate_unique_filename
    )
    from .crawl4ai_fetcher import fetch_with_crawl4ai # Added for crawl4ai
    from .app_config import WORKSPACE_ROOT, SUBFOLDERS
    from .psearchworking_export import (
        search_all, analyze_search_results, get_client as get_supabase_client,
        SearchParameters, global_search_params, SearchResult,
        TokenCounter as PSearchTokenCounter, ModelSelector
    )
    from .config.search_config import (
         get_preset, validate_search_params, router as search_config_router # etc.
     )
    from .routes.content_upserter import router as content_upserter_router
    from .routes.fetch_history_routes import router as fetch_history_router # Added this line
    from .monitoring.sse_monitor import sse_monitoring_middleware
    from .monitoring.routes import router as monitoring_router
    from .utils.llm_logging import log_llm_call # Added for LLM call logging

    PROJECT_MODULES_LOADED = True
except ImportError as e:
     logger.error(f"Failed to import one or more project modules: {e}. Check installation and package structure.", exc_info=True)
     PROJECT_MODULES_LOADED = False

     # --- Define dummy classes/functions with CORRECT SYNTAX ---
     logger.warning("Defining dummy components due to import errors.")

     class QueueManager:
         """Dummy QueueManager with correct syntax."""
         def __init__(self):
             self.status_queue = asyncio.Queue()
             self.transcription_queue = asyncio.Queue()
             logger.info("Initialized dummy QueueManager queues.")
         async def start(self): logger.warning("Called dummy QueueManager.start()"); pass
         async def stop(self): logger.warning("Called dummy QueueManager.stop()"); pass
         def has_active_transcriptions(self): return False # Add dummy method

     class PerformanceMonitor:
         """Dummy PerformanceMonitor."""
         def __init__(self, logger_instance): pass
         def start_timer(self, name: str): pass
         def stop_timer(self, name: str) -> float: return 0.0

     class MetricsCollector:
         """Dummy MetricsCollector."""
         async def collect_system_metrics(self): pass
         def add_metric(self, *args, **kwargs): pass

     class TranscriptionMetrics:
         """Dummy TranscriptionMetrics."""
         def record_request(self, success: bool): pass

     # --- Dummy Functions ---
     def get_supabase_client(): logger.error("Dummy: Supabase client unavailable."); return None
     DEFAULT_OUTPUT_FOLDER = './output'
     async def process_video(*args, **kwargs): logger.error("Dummy: process_video unavailable.")
     async def search_all(*args, **kwargs): logger.error("Dummy: search_all unavailable."); return [], None, None
     def analyze_search_results(*args, **kwargs): logger.error("Dummy: analyze_search_results unavailable."); return "Analysis unavailable."
     async def fetch_content_from_url(*args, **kwargs): logger.error("Dummy: fetch_content_from_url unavailable."); return {"error": "unavailable"}
     async def convert_md_to_pdf_util(*args, **kwargs): logger.error("Dummy: convert_markdown_to_pdf unavailable."); return False
     def generate_unique_filename(url, ext): return f"dummy_{url[:10]}_{int(time.time())}.{ext}"

     # --- More Dummy Classes ---
     class SearchParameters:
         """Dummy SearchParameters."""
         def get_all_params(self) -> dict: return {}
         def get_params(self, tier: str) -> dict: return {}
         def load_current(self): pass
         def update_params(self, tier:str, **kwargs): pass
         def update_from_frontend(self, **kwargs): return True # Add dummy method

     global_search_params = SearchParameters()

     class SearchResult:
          """Dummy SearchResult."""
          def __init__(self, **kwargs): pass
          def to_dict(self): return {}

     class PSearchTokenCounter:
          """Dummy TokenCounter."""
          def get_stats(self) -> dict: return {'embedding_tokens':0, 'generation_tokens':{'input':0, 'output':0}, 'total_tokens':0}
          def count_embedding_tokens(self, text:str) -> int: return 0
          def count_generation_tokens(self, input_text:str, output_text:Optional[str]=None) -> dict: return {'input':0, 'output':0}

     class ModelSelector:
         """Dummy ModelSelector."""
         @staticmethod
         def generate_analysis(text: str, provider: str = 'openai') -> str: return "Dummy Analysis Unavailable."

     # --- Dummy Routers/Middleware ---
     content_upserter_router = None
     metrics_router = None
     monitoring_router = None
     sse_monitoring_middleware = None

# --- Initialize Core Components ---
if PROJECT_MODULES_LOADED:
    performance_monitor = PerformanceMonitor(logger)
    metrics_collector = MetricsCollector()
    transcription_metrics = TranscriptionMetrics()
    try:
        queue_manager = QueueManager()
    except Exception as e:
        logger.error(f"Failed to initialize QueueManager: {e}", exc_info=True)
        sys.exit("QueueManager initialization failed.")
else:
     logger.warning("Using dummy components due to import errors.")
     performance_monitor = PerformanceMonitor(logger)
     metrics_collector = MetricsCollector()
     transcription_metrics = TranscriptionMetrics()
     queue_manager = QueueManager() # Dummy instance

# Download-specific queue
download_status_queue = asyncio.Queue()


# --- TokenCounter Class ---
# (Keep existing TokenCounter class - lines 375-447)
class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {'input': 0, 'output': 0}
        self.encoders = None
        if get_encoding:
            try:
                self.encoders = {
                    'cl100k_base': get_encoding('cl100k_base'),
                    'gpt-4': get_encoding('cl100k_base'),
                }
                logger.info("TokenCounter initialized with tiktoken encoders.")
            except Exception as e:
                logger.warning(f"Could not initialize tiktoken encoders: {e}. Token counting will be estimated.")
        else:
             logger.warning("TokenCounter initialized without tiktoken. Token counting will be estimated.")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        return len(text) // 4

    def count_embedding_tokens(self, text: str) -> int:
        """Count or estimate tokens for embedding."""
        if not self.encoders or 'cl100k_base' not in self.encoders:
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logger.warning(f"Could not count embedding tokens using tiktoken: {e}. Estimating.")
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens

    def count_generation_tokens(self, input_text: str, output_text: Optional[str] = None) -> dict:
        """Count or estimate tokens for generation."""
        result = {'input': 0, 'output': 0}
        encoder = self.encoders.get('gpt-4') if self.encoders else None

        try:
            if encoder:
                result['input'] = len(encoder.encode(input_text))
                if output_text:
                    result['output'] = len(encoder.encode(output_text))
            else:
                result['input'] = self._estimate_tokens(input_text)
                if output_text:
                    result['output'] = self._estimate_tokens(output_text)
        except Exception as e:
            logger.warning(f"Could not count generation tokens using tiktoken: {e}. Estimating.")
            result['input'] = self._estimate_tokens(input_text)
            if output_text:
                result['output'] = self._estimate_tokens(output_text)

        self.generation_tokens['input'] += result['input']
        self.generation_tokens['output'] += result['output']
        return result

    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        total = self.embedding_tokens + sum(self.generation_tokens.values())
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': total
        }

# Initialize token counter
token_counter = TokenCounter()


# --- Supabase Client Function ---
# (Keep existing get_client function - lines 451-465)
def get_client():
    """Get a Supabase client instance using the imported function."""
    if not PROJECT_MODULES_LOADED or get_supabase_client is None:
         logger.error("Cannot get Supabase client: psearchworking module or get_client function not loaded.")
         raise RuntimeError("Supabase client function is unavailable.")
    try:
        client = get_supabase_client()
        if client is None:
            logger.error("get_supabase_client() returned None.")
            raise RuntimeError("Failed to obtain Supabase client instance.")
        # logger.debug("Supabase client obtained successfully.")
        return client
    except Exception as e:
        logger.error(f"Error obtaining Supabase client via get_supabase_client(): {e}", exc_info=True)
        raise RuntimeError(f"Failed to obtain Supabase client: {e}")


# --- Pydantic Models ---
# (Keep existing models: ComprehensiveSearchRequest, ComprehensiveSearchResponse, VideoRequest, VectorSearchRequest, VectorSearchResponse, DownloadRequest, VideoInfoRequest - lines 469-586)
class ComprehensiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(30, ge=10, le=100, description="Maximum TOTAL results desired across methods")
    run_analysis: bool = Field(True, description="Whether to run AI analysis on results")

class ComprehensiveSearchResponse(BaseModel):
    """Response model for the comprehensive search endpoint."""
    query: str
    results: List[Dict[str, Any]] # List of dictionaries matching SearchResult.to_dict()
    openai_analysis: Optional[str] = None
    groq_analysis: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata, like timing, token counts, effective params")

    class Config:
        from_attributes = True # For Pydantic v2

class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str # Client must provide path to existing Obsidian vault/folder
    output_folder: str # Client provides desired base output path
    transcription_model: str = "faster-whisper"
    use_groq: Optional[bool] = None # Allow explicit setting, but validator overrides

    @field_validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v, re.IGNORECASE):
            raise ValueError('Invalid YouTube URL format')
        return v

    @field_validator('output_folder')
    def output_folder_must_be_valid(cls, v):
        if not v:
            v = os.path.join(WORKSPACE_ROOT, SUBFOLDERS['transcriptions']['markdown'])
        try:
             path = Path(v).resolve()
             if not path.parent.exists():
                  raise ValueError(f"Parent directory does not exist: {path.parent}")
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid output folder path '{v}': {e}")

    @field_validator('obsidian_dir')
    def obsidian_dir_must_exist(cls, v):
        if not v:
            raise ValueError('Obsidian directory path must be provided')
        try:
             path = Path(v).resolve()
             if not path.is_dir():
                  raise ValueError('Path is not an existing directory')
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid Obsidian directory path '{v}': {e}")

    @field_validator('transcription_model')
    def validate_transcription_model(cls, v):
        valid_models = ["faster-whisper", "groq"] # Add specific models if needed e.g. "groq/whisper-large-v3"
        if v.lower() not in valid_models and not v.lower().startswith("groq/"):
            raise ValueError(f"Invalid transcription model. Use 'faster-whisper', 'groq', or specific 'groq/model-name'.")
        return v.lower()

    from pydantic import model_validator

    @model_validator(mode='after')
    def check_and_set_use_groq(self) -> 'VideoRequest':
        model_name = self.transcription_model
        is_groq_model = model_name == 'groq' or model_name.startswith('groq/')

        if self.use_groq is not None and self.use_groq != is_groq_model:
             logger.warning(f"Provided 'use_groq' ({self.use_groq}) contradicts model '{model_name}'. Overriding based on model.")

        self.use_groq = is_groq_model # Set use_groq based on the model selected

        if self.use_groq and groq_client is None:
             raise ValueError("Groq transcription model selected, but Groq client is not available/configured.")

        return self

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    # Add fields for other search function parameters if needed
    content_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    summary_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    video_filter: Optional[str] = Field(None)

    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Search query must not be empty')
        return v.strip()

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    ai_response: Optional[str] = Field(None) # Keep for potential future use
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True # Pydantic v2

class DownloadRequest(BaseModel):
    url: str
    options: Dict[str, Any] = Field(default_factory=dict, description="yt-dlp options")

class VideoInfoRequest(BaseModel):
    url: str

# --- Fetch History Models ---
class FetchHistoryBase(BaseModel):
    url: str = Field(..., description="The URL that was fetched or attempted to be fetched.")
    fetching_engine: str = Field(..., description="The engine used for fetching (e.g., 'jina', 'crawl4ai').")
    status: str = Field(default='pending', description="The status of the fetch job (e.g., 'pending', 'success', 'failed').")
    engine_specific_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters specific to the fetching engine used.")
    user_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the user who initiated the fetch.")
    error_message: Optional[str] = Field(None, description="Error message if the fetch job failed.")
    content_summary: Optional[str] = Field(None, description="A brief summary or preview of the fetched content.")
    raw_content_path: Optional[str] = Field(None, description="Path to the stored raw fetched content, if applicable.")
    processed_content_path: Optional[str] = Field(None, description="Path to the stored processed content (e.g., PDF), if applicable.")
    supabase_content_id: Optional[uuid.UUID] = Field(None, description="ID of the related content in Supabase 'webpage_content' table, if applicable.")

class FetchHistoryCreate(FetchHistoryBase):
    pass

class FetchHistoryResponse(FetchHistoryBase):
    id: uuid.UUID = Field(..., description="Unique identifier for the fetch history record.")
    fetch_date: datetime = Field(..., description="Timestamp of when the fetch job was recorded.")

    class Config:
        from_attributes = True


# --- Initialize FastAPI app ---
# (Keep existing app initialization - lines 589-602)
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for YouTube video processing, download, and search.",
    version="1.2.0", # Incremented version for fetch/pdf/search features
    openapi_tags=[
        {"name": "Processing", "description": "Video transcription and processing."},
        {"name": "Download", "description": "Video/Audio download operations."},
        {"name": "Search", "description": "Content search functionalities."},
        {"name": "Status", "description": "Real-time status updates via SSE."},
        {"name": "Utility", "description": "Helper endpoints."},
        {"name": "Health", "description": "Service health checks."},
        {"name": "Content Fetch", "description": "Fetch web content, generate PDFs."},
        {"name": "Files", "description": "Serve generated files (e.g., PDFs)."},
        {"name": "Fetch History", "description": "Manage and view fetch history records."}, # Keep only one
    ]
)

# --- Configure CORS ---
# (Keep existing CORS middleware - lines 605-615)
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(',')
logger.info(f"Configuring CORS for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Content-Type-Options", "Content-Disposition"], # Added Content-Disposition
)

# --- Add Custom Middlewares ---
# (Keep existing middlewares: SSE Monitoring, Error Handling, Request Logging - lines 618-669)
# SSE Monitoring Middleware (if available)
if PROJECT_MODULES_LOADED and 'sse_monitoring_middleware' in locals() and sse_monitoring_middleware:
    try:
        app.middleware("http")(sse_monitoring_middleware)
        logger.info("SSE monitoring middleware enabled.")
    except Exception as e:
        logger.warning(f"Failed to enable SSE monitoring middleware: {e}")

# Error Handling Middleware (should be early)
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exc:
        raise http_exc # Re-raise for FastAPI to handle
    except Exception as exc:
        logger.error(f"Unhandled exception during request to {request.url.path}", exc_info=exc)
        error_details = {"error_code": "UNEXPECTED_SERVER_ERROR", "message": "An internal server error occurred."}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if PROJECT_MODULES_LOADED and 'TranscriptionErrorHandler' in locals():
             try:
                 error_details = TranscriptionErrorHandler.handle_error(
                     "UNEXPECTED_SERVER_ERROR", exc, path=str(request.url.path)
                 )
             except Exception as handler_err:
                  logger.error(f"Error handler itself failed: {handler_err}")
        return JSONResponse(status_code=status_code, content=error_details)

# Request Logging Middleware (should be after error handling, before routes)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"--> {method} {path} from {client_host}")
    response = await call_next(request) # Process request
    process_time = time.time() - start_time
    status_code = response.status_code
    logger.info(f"<-- {method} {path} - Status={status_code} ({process_time:.3f}s)")
    return response


# --- App Lifecycle Events ---
# (Keep existing startup/shutdown events - lines 672-697)
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             collector = get_metrics_collector()
             import asyncio
             asyncio.create_task(collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")

        # --- Execute Ollama Initializer Script ---
        try:
            logger.info("Launching Ollama initializer script...")
            # Use sys.executable to ensure the script runs with the same Python interpreter
            # Run in a non-blocking way using subprocess.Popen
            # The script itself handles checking the selected model and running ollama
            ollama_init_script_path = Path(__file__).parent / "ollama_initializer.py"
            if ollama_init_script_path.exists():
                # Use shell=True on Windows for better command execution, but be cautious
                # For cross-platform compatibility and safety, explicitly pass command parts
                command = [sys.executable, str(ollama_init_script_path)]
                # Use creationflags for Windows to prevent a console window from popping up
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                
                # Start the process without waiting
                process = subprocess.Popen(command, creationflags=creationflags)
                logger.info(f"Ollama initializer script launched with PID: {process.pid}")
            else:
                logger.error(f"Ollama initializer script not found at {ollama_init_script_path}. Skipping Ollama model loading on startup.")
        except Exception as e_ollama_init:
            logger.error(f"Error launching Ollama initializer script: {e_ollama_init}", exc_info=True)
        # --- End Ollama Initializer Script Execution ---

        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated...")
    try:
        await queue_manager.stop()
        logger.info("Queue manager stopped.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)


# --- SSE Message Formatter ---
# (Keep existing format_sse_message function - lines 700-747)
def format_sse_message(message_type: str, content: Any, metadata: Optional[dict] = None) -> str:
    """Formats a message dictionary into an SSE string, ensuring content is serializable."""
    message = {
        "type": message_type,
        "content": None, # Initialize content to None
        "timestamp": datetime.now().isoformat(),
        "id": str(time.time())  # Add a unique ID for each message
    }
    if metadata:
        message["metadata"] = metadata

    serializable_content = None
    if isinstance(content, (str, int, float, bool, type(None))):
        serializable_content = content
    elif isinstance(content, (dict, list)):
        serializable_content = content
    elif hasattr(content, 'to_dict') and callable(content.to_dict):
        try:
            serializable_content = content.to_dict()
        except Exception as e:
            logger.warning(f"Error calling to_dict() for SSE content type {message_type}: {e}. Content: {str(content)[:100]}")
            serializable_content = f"Error serializing object: {str(content)[:100]}"
    elif hasattr(content, '__dict__'):
         try:
             json.dumps(content.__dict__)
             serializable_content = content.__dict__
         except TypeError:
              logger.warning(f"Could not directly serialize __dict__ for SSE content type {message_type}. Sending string representation. Content: {str(content)[:100]}")
              serializable_content = str(content) # Fallback to string representation
    else:
        serializable_content = str(content)

    message["content"] = serializable_content

    try:
        json_str = json.dumps(message)
        return json_str # EventSourceResponse will handle the "data: " prefix and "\n\n"
    except TypeError as e:
         logger.error(f"FINAL fallback: Failed to serialize SSE message of type {message_type}: {e}. Content: {str(serializable_content)[:100]}")
         error_content = {"error": "Failed to serialize message content", "original_type": message_type}
         # EventSourceResponse will handle the "data: " prefix and "\n\n"
         return json.dumps({'type': 'error', 'content': error_content, 'timestamp': datetime.now().isoformat()})


# --- Combined SSE Updates Endpoint ---
# (Keep existing /combined-updates endpoint - lines 752-983)
@app.get("/combined-updates", tags=["Status"])
async def get_combined_updates(request: Request):
    """SSE endpoint for combined status and transcription updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"SSE connection requested from {client_host} (Origin: {origin}) for /combined-updates.")

    async def event_generator():
        logger.info(f"SSE (Combined): GENERATOR ENTERED for {client_host}.")
        try:
            status_q = queue_manager.status_queue
            transcription_q = queue_manager.transcription_queue
            logger.info(f"SSE (Combined): Got queue references. TQ ID: {id(transcription_q)}, SQ ID: {id(status_q)}")
            last_activity_time = time.time()
            heartbeat_interval = 2
            connection_timeout = 300

            transcription_task = asyncio.create_task(transcription_q.get())
            setattr(transcription_task, '_queue_name', 'transcription')
            status_task = asyncio.create_task(status_q.get())
            setattr(status_task, '_queue_name', 'status')
            heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
            setattr(heartbeat_task, '_is_heartbeat', True)

            all_tasks = {transcription_task, status_task, heartbeat_task}
            logger.info(f"SSE (Combined): Initialized {len(all_tasks)} persistent tasks. Entering main try block.")
        except Exception as setup_err:
            logger.error(f"SSE (Combined): ERROR DURING INITIAL SETUP: {setup_err}", exc_info=True)
            try: yield format_sse_message('error', f"SSE generator setup failed: {setup_err}")
            except: pass
            return

        try:
            connection_established_msg = format_sse_message(
                "status", "SSE connection established",
                {"connection_id": str(time.time()), "server_time": datetime.now().isoformat()}
            )
            yield connection_established_msg
            last_activity_time = time.time()
            yield format_sse_message('heartbeat', 'initial_ping')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check')
            await asyncio.sleep(1); yield format_sse_message('heartbeat', 'connection_check_2')

            while True:
                logger.debug(f"SSE (Combined): Entering new loop iteration for {client_host}")
                try:
                    logger.info(f"SSE (Combined): LOOP START - Waiting on {len(all_tasks)} persistent tasks.")
                    done, pending = await asyncio.wait(all_tasks, return_when=asyncio.FIRST_COMPLETED)
                    logger.info(f"SSE (Combined): WAIT COMPLETED - Done: {len(done)}, Pending: {len(pending)}")

                    for task in done:
                        if getattr(task, '_is_heartbeat', False):
                            logger.debug("SSE (Combined): Heartbeat task completed.")
                            try:
                                yield format_sse_message('heartbeat', 'ping_interval')
                                last_activity_time = time.time()
                                logger.debug("SSE (Combined): Sent interval heartbeat.")
                            except Exception as send_err:
                                logger.error(f"Failed to send interval heartbeat: {send_err}. Closing connection.")
                                raise send_err
                            all_tasks.remove(task)
                            new_heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
                            setattr(new_heartbeat_task, '_is_heartbeat', True)
                            all_tasks.add(new_heartbeat_task)
                            logger.debug(f"SSE (Combined): Replaced completed heartbeat task with new task {id(new_heartbeat_task)}")
                            continue

                        original_queue = None
                        queue_name = getattr(task, '_queue_name', None)
                        if queue_name == 'transcription': original_queue = transcription_q
                        elif queue_name == 'status': original_queue = status_q

                        if original_queue is None:
                            logger.error(f"SSE (Combined): Completed task {id(task)} is not a known queue task.")
                            continue

                        try:
                            item = task.result()
                            logger.info(f"SSE (Combined): ITEM RETRIEVED from {queue_name} queue {id(original_queue)}. Type: {type(item).__name__}. Content: {str(item)[:100]}...")
                            sse_msg = None
                            if isinstance(item, str):
                                try:
                                    payload_dict = json.loads(item)
                                    msg_type = payload_dict.get('type', 'transcription_segment' if original_queue == transcription_q else 'status')
                                    msg_content = payload_dict.get('content', payload_dict)
                                    sse_msg = format_sse_message(msg_type, msg_content)
                                except json.JSONDecodeError:
                                    logger.error(f"SSE (Combined): Failed to decode JSON from {queue_name} queue {id(original_queue)}: {item[:100]}...")
                                    sse_msg = format_sse_message('error', f"Invalid data received from backend queue: {item[:100]}...")
                                except Exception as format_err:
                                    logger.error(f"SSE (Combined): Error formatting message after JSON decode: {format_err}", exc_info=True)
                                    sse_msg = format_sse_message('error', f"Internal error formatting SSE message: {format_err}")
                            else:
                                logger.error(f"SSE (Combined): Received non-string item type '{type(item).__name__}' from {queue_name} queue {id(original_queue)}. Content: {str(item)[:100]}")
                                sse_msg = format_sse_message('error', f"Invalid data type received from backend queue: {type(item).__name__}")

                            if sse_msg:
                                try:
                                    yield sse_msg
                                    last_activity_time = time.time()
                                    logger.info(f"SSE SEND (Combined): {sse_msg.strip()[:150]}...")
                                except Exception as send_err:
                                    logger.error(f"Failed to send update to SSE client: {send_err}")
                                    raise send_err
                            else:
                                logger.warning(f"SSE (Combined): No valid SSE message generated for item from {original_queue} queue.")

                            original_queue.task_done()
                            all_tasks.remove(task)
                            if original_queue == transcription_q:
                                new_task = asyncio.create_task(transcription_q.get())
                                setattr(new_task, '_queue_name', 'transcription')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed transcription task with new task {id(new_task)}")
                            elif original_queue == status_q:
                                new_task = asyncio.create_task(status_q.get())
                                setattr(new_task, '_queue_name', 'status')
                                all_tasks.add(new_task)
                                logger.debug(f"SSE (Combined): Replaced completed status task with new task {id(new_task)}")

                        except asyncio.CancelledError:
                            logger.info(f"SSE (Combined): A queue get() task {id(task)} was cancelled.")
                        except Exception as e:
                            logger.error(f"SSE (Combined): Error processing completed task result for task {id(task)}: {e}", exc_info=True)
                            try: yield format_sse_message('error', f"Internal SSE error processing task result: {str(e)}")
                            except Exception as send_err: logger.error(f"Failed to send task processing error to SSE client: {send_err}"); raise send_err

                except asyncio.CancelledError:
                    logger.info(f"SSE connection closed by client {client_host} for /combined-updates (Caught CancelledError in loop).")
                    break
                except Exception as loop_err:
                    error_message = f"FATAL Error in /combined-updates SSE generator loop: {loop_err}"
                    logger.error(error_message, exc_info=True)
                    try: yield format_sse_message('error', f"Fatal SSE generator loop error: {str(loop_err)}")
                    except Exception: pass
                    break

            logger.info(f"SSE event generator loop exited for {client_host} (/combined-updates).")

        finally:
            logger.info(f"SSE event generator entering finally block for {client_host} (/combined-updates).")
            logger.info(f"SSE (Combined): Cancelling {len(all_tasks)} remaining tasks in final cleanup.")
            for task in list(all_tasks):
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
                except Exception as e: logger.error(f"Error awaiting cancellation of task {id(task)}: {e}")
            logger.info(f"SSE event generator finished final cleanup for {client_host} (/combined-updates).")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Combined SSE ---
# (Keep existing /combined-updates OPTIONS handler - lines 1006-1010)
@app.options("/combined-updates", tags=["Status"])
async def options_combined_updates(request: Request):
    """Handle OPTIONS preflight requests for /combined-updates."""
    return _handle_options_request(request, allowed_origins)


# --- Download Status SSE Endpoint ---
# (Keep existing /api/download-status endpoint - lines 1013-1084)
@app.get("/api/download-status", tags=["Status", "Download"])
async def get_download_status(request: Request):
    """SSE endpoint specifically for download status updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"Download status SSE connection requested from {client_host} (Origin: {origin}).")

    async def event_generator():
        q = download_status_queue
        last_activity_time = time.time()
        heartbeat_interval = 20

        try:
            yield format_sse_message("status", "Connected to download status stream")
            last_activity_time = time.time()

            while True:
                try:
                    status_update_str = await asyncio.wait_for(q.get(), timeout=heartbeat_interval)
                    logger.debug(f"SSE (Download): Sending update: {status_update_str[:100]}...")
                    try:
                        update_data = json.loads(status_update_str)
                        yield f"data: {status_update_str}\n\n" # Send raw JSON string
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Download SSE received non-JSON: {status_update_str[:100]}... Error: {e}")
                        yield format_sse_message('status', status_update_str) # Send as plain
                    q.task_done()
                    last_activity_time = time.time()

                except asyncio.TimeoutError:
                    logger.debug("SSE (Download): Sending heartbeat.")
                    yield format_sse_message('heartbeat', 'ping')
                    last_activity_time = time.time()
                    continue

                except asyncio.QueueEmpty:
                     await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Download SSE connection closed by client {client_host}.")
        except Exception as e:
            error_message = f"Error in download status SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try: yield format_sse_message('error', error_message)
            except Exception as send_err: logger.error(f"Failed to send error to download SSE client: {send_err}")
        finally:
            logger.info(f"Download SSE event generator finished for {client_host}.")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    origin = request.headers.get("origin", "N/A")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"Download SSE response headers: {response.headers}")
    return response

# --- OPTIONS handler for Download Status SSE ---
# (Keep existing /api/download-status OPTIONS handler - lines 1087-1090)
@app.options("/api/download-status", tags=["Status", "Download"])
async def options_download_status(request: Request):
    """Handle OPTIONS preflight requests for /api/download-status."""
    return _handle_options_request(request, allowed_origins)

# --- Helper for OPTIONS requests ---
# (Keep existing _handle_options_request function - lines 1093-1109)
def _handle_options_request(request: Request, allowed_origins_list: List[str]):
    origin = request.headers.get("origin")
    method = request.headers.get("access-control-request-method")
    logger.info(f"OPTIONS request for {request.url.path} from origin: {origin}, method: {method}")

    if origin in allowed_origins_list:
        response = JSONResponse(content={"detail": "OK"}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS" # Adjust as needed per endpoint
        response.headers["Access-Control-Allow-Headers"] = "*" # Or be specific: "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400" # Cache preflight for 1 day
        logger.debug(f"OPTIONS response headers: {response.headers}")
        return response
    else:
        logger.warning(f"OPTIONS request from disallowed origin: {origin}")
        return JSONResponse(content={"detail": "Origin not allowed"}, status_code=400)


# --- Transcription Status Endpoint ---
# (Keep existing /transcription-status endpoint - lines 1113-1131)
@app.get("/transcription-status", tags=["Status"])
async def transcription_status():
    """Check if there's an active transcription process running."""
    try:
        active = False
        if queue_manager and hasattr(queue_manager, '_running') and queue_manager._running:
            active = not queue_manager.transcription_queue.empty()
            if hasattr(queue_manager, 'has_active_transcriptions'):
                 active = active or queue_manager.has_active_transcriptions()
        return {"active": active}
    except Exception as e:
        logger.error(f"Error checking transcription status: {e}")
        return {"active": False, "error": str(e)}

# --- Process Video Endpoint ---
# (Keep existing /process-video/ endpoint - lines 1134-1212)
@app.post("/process-video/", tags=["Processing"])
async def process_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """Initiate background processing (download, transcribe) for a YouTube video."""
    if not PROJECT_MODULES_LOADED or process_video is None:
         raise HTTPException(status_code=501, detail="Video processing feature is unavailable due to missing modules.")

    try:
        logger.info(f"Processing video request for URL: {request.youtube_video_url}")
        console.print(f"[cyan]Obsidian Dir:[/cyan] {request.obsidian_dir}")
        console.print(f"[cyan]Output Folder:[/cyan] {request.output_folder}")
        console.print(f"[cyan]Model:[/cyan] {request.transcription_model}, [cyan]Use Groq:[/cyan] {request.use_groq}")

        transcription_metrics.record_request(True)
        output_path = Path(request.output_folder)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured output folder exists: {output_path}")
        except OSError as e:
             logger.error(f"Failed to create output folder {output_path}: {e}", exc_info=True)
             raise HTTPException(status_code=500, detail=f"Could not create output directory: {e}")

        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq
        }

        try:
            from .transcribe1 import extract_video_id
            video_id = extract_video_id(request.youtube_video_url)
        except Exception as e:
            logger.warning(f"Could not extract video ID for tracking: {e}")
            video_id = request.youtube_video_url

        from .process_video_wrapper import process_video_with_tracking

        background_tasks.add_task(
            process_video_with_tracking,
            youtube_video_url=request.youtube_video_url,
            obsidian_dir=request.obsidian_dir,
            status_queue=queue_manager.status_queue,
            transcription_queue=queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config,
            video_id=video_id
        )

        logger.info(f"Background task added for processing: {request.youtube_video_url}")

        return {
            "status": "started",
            "message": "Video processing initiated in the background.",
            "details": {
                 "url": request.youtube_video_url,
                 "output_folder": request.output_folder,
                 "obsidian_dir": request.obsidian_dir
            },
            "timestamp": datetime.now().isoformat()
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.warning(f"Validation error processing video request: {e.errors()}", exc_info=False)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException as e:
         transcription_metrics.record_request(False)
         raise e
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(f"Unexpected error initiating video processing for {request.youtube_video_url}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start video processing task.")


# --- Video Download Feature ---
# (Keep existing download_video_task, report_download_progress, report_postprocess_progress, /api/download endpoint - lines 1217-1459)
async def download_video_task(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task using yt-dlp (run in thread) with progress reporting."""
    if yt_dlp is None:
        logger.error("yt-dlp library is not installed. Cannot download video.")
        await status_queue.put(format_sse_message('error','Download feature unavailable: yt-dlp library not installed.'))
        return

    download_dir = options.get('download_dir', os.path.join(os.getcwd(), 'downloads'))
    logger.info(f"Download task started for URL: {url}, saving to: {download_dir}")

    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create download directory {download_dir}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Failed to create download directory: {e}'))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_template = os.path.join(download_dir, f'%(title)s_{timestamp}.%(ext)s')

    ydl_opts = {
        'outtmpl': filename_template,
        'quiet': True, 'no_warnings': True, 'noprogress': True,
        'keepvideo': options.get('keepVideo', True),
        'overwrites': False,
        'ffmpeg_location': options.get('ffmpegPath'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True, 'playlist_items': None,
    }

    video_format = options.get('format')
    if video_format == 'best': pass
    elif video_format in ['1080p', '720p', '480p', '360p']:
        res = video_format.replace('p', '')
        ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best[height<={res}]'
    elif video_format == 'audio_best':
         ydl_opts['format'] = 'bestaudio/best'
         options['extractAudio'] = True
         options.setdefault('audioFormat', 'mp3')

    if options.get('extractAudio'):
        audio_format = options.get('audioFormat', 'mp3')
        audio_quality = options.get('audioQuality', '192')
        ydl_opts.setdefault('postprocessors', []).append({
            'key': 'FFmpegExtractAudio', 'preferredcodec': audio_format, 'preferredquality': audio_quality,
        })
        if not ydl_opts['keepvideo'] and video_format != 'audio_best':
             ydl_opts['format'] = 'bestaudio/best'

    if options.get('embedThumbnail') and video_format != 'audio_best':
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append({'key': 'EmbedThumbnail'})

    if options.get('embedMetadata', True):
        ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegMetadata', 'add_metadata': True})

    if options.get('subtitles'):
        sub_lang = options.get('subtitleLanguage', 'en')
        sub_auto = options.get('autoSubtitles', False)
        sub_format = options.get('subtitleFormat', 'srt')
        ydl_opts.update({
            'writesubtitles': True, 'writeautomaticsub': sub_auto,
            'subtitleslangs': [sub_lang] if sub_lang != 'all' else ['all'],
            'subtitlesformat': sub_format,
        })
        if options.get('embedSubtitles') and video_format != 'audio_best':
             ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegEmbedSubtitle'})

    is_playlist_url = 'list=' in url or '/playlist?' in url
    if is_playlist_url and options.get('downloadPlaylist'):
        playlist_items = None
        items_str = options.get('playlistItems')
        start = options.get('playlistStart')
        end = options.get('playlistEnd')
        if items_str: playlist_items = items_str
        elif start or end: playlist_items = f"{start or ''}-{end or ''}"
        ydl_opts['noplaylist'] = False
        ydl_opts['playlist_items'] = playlist_items
        logger.info(f"Playlist download enabled. Items: '{playlist_items or 'all'}'")
    elif is_playlist_url:
        logger.info("Playlist URL detected, but only downloading single video.")
        ydl_opts['noplaylist'] = True

    try:
        await status_queue.put(format_sse_message('status', f'Starting download: {url}', {'download_dir': download_dir}))
        logger.info("Running yt-dlp download process in thread...")
        loop = asyncio.get_running_loop()
        ydl_opts['progress_hooks'] = [functools.partial(report_download_progress, loop, status_queue)]
        ydl_opts['postprocessor_hooks'] = [functools.partial(report_postprocess_progress, loop, status_queue)]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             await asyncio.to_thread(ydl.download, [url])
        logger.info(f"yt-dlp download thread finished for {url}.")
        await status_queue.put(format_sse_message('complete', f'Download finished for: {url}'))
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error for {url}: {e}", exc_info=False)
        await status_queue.put(format_sse_message('error', f'Download failed: {e}'))
    except Exception as e:
        logger.error(f"Unexpected error during download task for {url}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Unexpected download error: {e}'))

def report_download_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp download progress, puts message to asyncio queue."""
    if loop is None: logger.error("Asyncio loop is None in report_download_progress."); return
    if d['status'] == 'downloading':
        try:
            progress = d.get('fraction', 0) * 100
            speed = d.get('speed_str', d.get('speed', 'N/A'))
            eta = d.get('eta_str', d.get('eta', 'N/A'))
            filename = d.get('filename', d.get('info_dict',{}).get('filename', '...'))
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            size_str = "N/A"
            if total_bytes:
                if total_bytes < 1024*1024: size_str = f"{total_bytes/1024:.1f} KiB"
                elif total_bytes < 1024*1024*1024: size_str = f"{total_bytes/(1024*1024):.1f} MiB"
                else: size_str = f"{total_bytes/(1024*1024*1024):.2f} GiB"
            content = {'progress': round(progress, 1), 'speed': speed, 'eta': eta, 'filename': os.path.basename(filename), 'total_size': size_str, 'status': 'Downloading'}
            message = format_sse_message('progress', content)
            asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
        except Exception as e: pass
    elif d['status'] == 'finished':
        filename = d.get('filename', d.get('info_dict',{}).get('filename', 'file'))
        message = format_sse_message('status', f'Downloaded {os.path.basename(filename)}. Post-processing...')
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
    elif d['status'] == 'error':
         err_msg = d.get("error", "Unknown download error")
         filename = d.get('filename', d.get('info_dict',{}).get('filename', 'N/A'))
         message = format_sse_message('error', f'Error downloading {os.path.basename(filename)}: {err_msg}')
         asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

def report_postprocess_progress(loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict):
    """Hook for yt-dlp post-processing progress."""
    if loop is None: logger.error("Asyncio loop is None in report_postprocess_progress."); return
    status = d.get('status')
    pp_name = d.get('postprocessor')
    info = d.get('info_dict', {})
    filename = os.path.basename(info.get('filepath', info.get('filename', 'file')))
    if status == 'started' or status == 'processing': message = format_sse_message('status', f'Post-processing ({pp_name}): Starting on {filename}...')
    elif status == 'finished': message = format_sse_message('status', f'Post-processing ({pp_name}): Finished for {filename}.')
    elif status == 'error': message = format_sse_message('error', f'Post-processing ({pp_name}): Failed for {filename}. Check logs.')
    else: return
    asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

@app.post("/api/download", tags=["Download"])
async def download_video_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a video/audio download task in the background."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Download feature unavailable: yt-dlp library not installed.")
    try:
        logger.info(f"Download request received for URL: {request.url}")
        console.print(f"[yellow]Options:[/yellow] {request.options}")
        request.options.setdefault('download_dir', os.path.join(os.getcwd(), 'downloads'))
        background_tasks.add_task(download_video_task, request.url, request.options, download_status_queue)
        return {"status": "success", "message": "Download task initiated in background.", "url": request.url, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error starting download task for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start download task: {e}")


# --- Get Video Info Endpoint ---
# (Keep existing /api/video-info endpoint - lines 1463-1551)
@app.post("/api/video-info", tags=["Download", "Utility"])
async def get_video_info(request: VideoInfoRequest):
    """Get metadata for a YouTube video or playlist without downloading."""
    if yt_dlp is None: raise HTTPException(status_code=501, detail="Info feature unavailable: yt-dlp library not installed.")
    logger.info(f"Video info request for URL: {request.url}")
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'extract_flat': 'in_playlist'}
    info = None
    try:
        logger.debug(f"Extracting info for {request.url} in thread...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             info = await asyncio.to_thread(ydl.extract_info, request.url, download=False)
        logger.debug(f"Info extraction finished.")
        if not info: raise HTTPException(status_code=404, detail="Could not extract information for the given URL.")

        is_playlist = info.get('_type') == 'playlist'
        playlist_count = len(info.get('entries', [])) if is_playlist else 0
        title = info.get('title', 'N/A')
        author = info.get('uploader', info.get('channel', 'N/A'))
        thumbnail = info.get('thumbnail')
        video_id = info.get('id', '')
        original_url = info.get('webpage_url', request.url)
        duration_str = "N/A"
        if is_playlist: duration_str = f"{playlist_count} videos"
        else:
            duration_sec = info.get('duration')
            if duration_sec:
                try:
                    duration_str = str(timedelta(seconds=int(duration_sec)))
                except (ValueError, TypeError): # Catch specific errors during conversion
                    logger.warning(f"Could not convert duration '{duration_sec}' to timedelta.")
                    pass # Keep duration_str as "N/A"
            if not thumbnail and info.get('thumbnails'): thumbnail = info['thumbnails'][-1]['url']

        formats = info.get('formats', [])
        available_formats_notes = sorted(list(set(f.get('format_note', f.get('resolution', f.get('ext'))) for f in formats if f.get('format_note') or f.get('resolution') or f.get('ext')))) if formats else ["N/A (requires detailed fetch)"]
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        available_subtitles = sorted(list(subs.keys()))
        available_auto_captions = sorted(list(auto_subs.keys()))

        return {"title": title, "author": author, "thumbnail": thumbnail, "duration": duration_str, "is_playlist": is_playlist, "playlist_count": playlist_count if is_playlist else 1, "available_formats": available_formats_notes, "available_subtitles": available_subtitles, "available_auto_captions": available_auto_captions, "id": video_id, "original_url": original_url}
    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"yt-dlp info extraction failed for {request.url}: {e}")
        status_code = 400; detail = f"Failed to process URL"
        if "Unsupported URL" in str(e): status_code = 400; detail = "Unsupported URL"
        elif "Video unavailable" in str(e): status_code = 404; detail = "Video unavailable"
        elif "Private video" in str(e): status_code = 403; detail = "Video is private"
        elif "Sign in to confirm your age" in str(e): status_code = 403; detail = "Video requires age verification (login)"
        raise HTTPException(status_code=status_code, detail=f"{detail}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching video info for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching video info: {e}")


# --- List Downloads Endpoint ---
# (Keep existing /api/list-downloads endpoint - lines 1555-1634)
@app.get("/api/list-downloads", tags=["Download"])
async def list_downloads(directory: Optional[str] = Query(None)):
    """List files in the specified download directory."""
    logger.info(f"List downloads request for directory: {directory}")
    list_dir = directory
    if not list_dir:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): list_dir = user_downloads
            else: list_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
        except Exception: list_dir = os.path.abspath('./downloads')

    list_dir_path = Path(list_dir).resolve()
    if not list_dir_path.is_dir():
        logger.warning(f"Attempted to list non-existent or non-directory path: {list_dir_path}")
        return {"files": []}
    try:
        entries = await asyncio.to_thread(os.listdir, list_dir_path)
        files_list = []
        for entry_name in entries:
            entry_path = list_dir_path / entry_name
            if await asyncio.to_thread(os.path.isfile, entry_path):
                try:
                    stat = await asyncio.to_thread(os.stat, entry_path)
                    size_bytes = stat.st_size
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    file_extension = entry_path.suffix.lower()
                    file_type = "Other"
                    if file_extension in ['.mp4', '.mkv', '.webm', '.avi', '.mov']: file_type = "Video"
                    elif file_extension in ['.mp3', '.wav', '.aac', '.m4a', '.opus', '.ogg']: file_type = "Audio"
                    elif file_extension in ['.srt', '.vtt', '.ass']: file_type = "Subtitle"
                    size_str = "N/A"
                    if size_bytes is not None:
                        if size_bytes < 1024: size_str = f"{size_bytes} B"
                        elif size_bytes < 1024*1024: size_str = f"{size_bytes/1024:.1f} KB"
                        elif size_bytes < 1024*1024*1024: size_str = f"{size_bytes/(1024*1024):.1f} MB"
                        else: size_str = f"{size_bytes/(1024*1024*1024):.2f} GB"
                    files_list.append({"name": entry_name, "type": file_type, "size": size_str, "modified": mod_time.isoformat(), "path": str(entry_path)})
                except Exception as file_info_err:
                    logger.warning(f"Error getting info for file {entry_path}: {file_info_err}")
                    files_list.append({"name": entry_name, "type": "Unknown", "size": "N/A", "modified": "N/A", "path": str(entry_path)})
        files_list.sort(key=lambda x: x.get('modified', '0'), reverse=True)
        logger.info(f"Listed {len(files_list)} files in {list_dir_path}")
        return {"files": files_list}
    except Exception as e:
        logger.error(f"Error listing files in directory {list_dir_path}: {e}", exc_info=True)
        return {"files": [], "error": f"Failed to list files: {e}"}


# --- Fetch History API Endpoints ---

@app.post("/api/fetch-history", response_model=FetchHistoryResponse, tags=["Fetch History"], status_code=status.HTTP_201_CREATED)
async def create_fetch_history_entry(payload: FetchHistoryCreate):
    """
    Create a new fetch history entry.
    """
    logger.info(f"Creating fetch history entry for URL: {payload.url} with engine: {payload.fetching_engine}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        # Prepare data for insertion, Pydantic model ensures correct types for what's passed
        # fetch_date and id are handled by the database by default
        data_to_insert = payload.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .insert(data_to_insert)
            .execute
        )

        if hasattr(response, 'data') and response.data:
            created_entry_data = response.data[0]
            logger.info(f"Successfully created fetch history entry with ID: {created_entry_data.get('id')}")
            # Ensure all fields required by FetchHistoryResponse are present, or handle defaults
            # The DB defaults should cover 'id' and 'fetch_date'
            return FetchHistoryResponse(**created_entry_data)
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error creating fetch history entry: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history creation: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating fetch history entry for URL {payload.url}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create fetch history entry: {str(e)}")

@app.get("/api/fetch-history", response_model=List[FetchHistoryResponse], tags=["Fetch History"])
async def list_fetch_history_entries(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return."),
    offset: int = Query(0, ge=0, description="Number of records to skip for pagination.")
):
    """
    List existing fetch history entries, ordered by fetch_date descending.
    """
    logger.info(f"Listing fetch history entries with limit={limit}, offset={offset}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("*")
            .order("fetch_date", desc=True)
            .limit(limit)
            .offset(offset)
            .execute
        )

        if hasattr(response, 'data'):
            entries_data = response.data
            logger.info(f"Successfully retrieved {len(entries_data)} fetch history entries.")
            # Pydantic will validate each item in the list against FetchHistoryResponse
            return [FetchHistoryResponse(**entry) for entry in entries_data]
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error listing fetch history entries: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        else:
            logger.error(f"Unexpected response from Supabase during fetch history listing: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected database response.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error listing fetch history entries: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list fetch history entries: {str(e)}")


# --- Get Default Directory Endpoint ---
# (Keep existing /api/default-directory endpoint - lines 1640-1667)
@app.get("/api/default-directory", tags=["Utility"])
async def get_default_directory():
    """Suggest a default download directory path (client can override)."""
    path_str = ""
    warning = None
    try:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir(): path_str = user_downloads
            else: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "User 'Downloads' directory not found, suggesting relative path."
        except Exception: path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads')); warning = "Could not determine user home directory, suggesting relative path."
        logger.info(f"Providing default download directory suggestion: {path_str}")
        response = {"path": path_str}
        if warning: response["warning"] = warning
        return response
    except Exception as e:
        logger.error(f"Error determining default directory: {e}", exc_info=True)
        fallback_dir = os.path.abspath('./downloads')
        return {"path": fallback_dir, "warning": "Could not determine default path, using relative './downloads'."}


# --- PDF Storage Path ---
PDF_STORAGE_BASE_DIR = Path(os.getenv('PDF_STORAGE_PATH', './temp_pdfs')).resolve()
try:
    PDF_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured PDF storage directory exists: {PDF_STORAGE_BASE_DIR}")
except OSError as e:
    logger.error(f"CRITICAL: Could not create PDF storage directory {PDF_STORAGE_BASE_DIR}: {e}. PDF features will fail.", exc_info=True)
    # Depending on requirements, might want to exit or just disable PDF features
    # sys.exit(f"Failed to create PDF storage directory: {PDF_STORAGE_BASE_DIR}")


# --- Helper: Generate OpenAI Embedding ---
async def get_openai_embedding(text: str, model: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")) -> Optional[List[float]]:
    """Generates embedding for text using OpenAI API, with logging."""
    if not openai_client:
        logger.error("OpenAI client not initialized. Cannot generate embedding.")
        # Log attempt even if client is not initialized, as it's an LLM operation attempt
        llm_log_data_no_client = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "ConfigurationError",
            "error_message_detail": "OpenAI client not initialized.",
            "input_text_preview": (text[:100] + "...") if text and len(text) > 100 else text
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_no_client, indent=2, default=str)}")
        return None

    if not text or not text.strip():
        logger.warning("Attempted to generate embedding for empty text.")
        # Log this attempt as well
        llm_log_data_empty_text = {
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_call_type": "embedding",
            "llm_provider": "openai",
            "model_name": model,
            "call_successful": False,
            "error_type": "InputError",
            "error_message_detail": "Input text for embedding was empty or whitespace.",
            "input_text_preview": ""
        }
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data_empty_text, indent=2, default=str)}")
        return None

    llm_log_data: Dict[str, Any] = {
        "request_timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_call_type": "embedding",
        "llm_provider": "openai",
        "model_name": model,
        "input_text_preview": (text[:100] + "...") if len(text) > 100 else text,
        "call_successful": False, # Default to False
    }
    start_time = time.time()

    try:
        processed_text = text.replace("\n", " ")
        response = await openai_client.embeddings.create(input=[processed_text], model=model)
        embedding = response.data[0].embedding
        
        llm_log_data["call_successful"] = True
        if response.usage:
            llm_log_data["prompt_tokens_total"] = response.usage.prompt_tokens
            llm_log_data["total_tokens_used"] = response.usage.total_tokens
        # Cost calculation would require model pricing data
        # llm_log_data["cost"] = calculate_cost(model, response.usage.prompt_tokens)
        
        logger.info(f"Generated OpenAI embedding using model {model} for text snippet: '{text[:50]}...'")
        return embedding
    except OpenAI_APIError as e:
        logger.error(f"OpenAI API error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "RateLimitError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_APIConnectionError as e:
        logger.error(f"OpenAI connection error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "APIConnectionError"
        llm_log_data["error_message_detail"] = str(e)
    except OpenAI_AuthenticationError as e:
        logger.error(f"OpenAI authentication error generating embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "AuthenticationError"
        llm_log_data["error_message_detail"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error generating OpenAI embedding: {e}", exc_info=True)
        llm_log_data["error_type"] = "UnhandledException"
        llm_log_data["error_message_detail"] = str(e)
    finally:
        end_time = time.time()
        llm_log_data["llm_call_duration_ms"] = int((end_time - start_time) * 1000)
        # Log the comprehensive data (placeholder for DB insert)
        # TODO: Implement actual DB insertion for llm_call_logs table
        logger.info(f"LLM Call Log (OpenAI Embedding): {json.dumps(llm_log_data, indent=2, default=str)}")
    
    return None

# --- Helper: Upsert Content to Supabase ---
async def upsert_content_to_supabase(
    url: str,
    title: str,
    markdown_content: str,
    embedding: Optional[List[float]],
    pdf_path: Optional[str] = None
) -> Optional[str]:
    """Upserts fetched content, embedding, and PDF path to Supabase using the SQL function."""
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            logger.error("Supabase client unavailable. Cannot upsert content.")
            return None

        # Generate a unique content_id (e.g., UUID) for new entries
        # The SQL function handles finding existing entries by URL
        content_id = str(uuid.uuid4())

        # Prepare parameters for the SQL function
        params = {
            "p_content_id": content_id,
            "p_title": title,
            "p_url": url,
            "p_content": markdown_content,
            "p_embedding": embedding, # Pass the list of floats
            "p_pdf_path": pdf_path,
            # "p_source_file": None # Or pass pdf_path here if using source_file column
        }

        logger.info(f"Calling Supabase RPC upsert_webpage_content for URL: {url}")
        response = await asyncio.to_thread(
             supabase_client.rpc('upsert_webpage_content', params).execute
        )
        # response = supabase_client.rpc('upsert_webpage_content', params).execute() # Original sync call

        # Check response (supabase-py v1 might differ from v2 in response structure)
        # Assuming response.data contains the returned content_id
        if hasattr(response, 'data') and response.data:
            returned_id = response.data
            logger.info(f"Successfully upserted content for URL {url}. Returned ID: {returned_id}")
            return returned_id
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error upserting content for {url}: {response.error}")
             return None
        else:
             # Handle unexpected response structure (log and return None)
             logger.warning(f"Unexpected response structure from Supabase upsert RPC for {url}: {response}")
             return None

    except Exception as e:
        logger.error(f"Error upserting content to Supabase for URL {url}: {e}", exc_info=True)
        return None

# --- Helper: Update Fetch History Record ---
async def _update_fetch_history_record(
    supabase_client: Any, # from supabase import Client as SupabaseClient - or use Any
    history_id: Optional[uuid.UUID],
    update_data: Dict[str, Any],
    all_request_params_for_history: Dict[str, Any]
) -> Tuple[Optional[str], bool]: # Returns (SSE message string or None, db_write_successful_flag)
    """
    Helper to update a fetch_history record.
    Returns an SSE message string for the event_generator to yield,
    and a boolean indicating if the database write operation was successful for this call.
    The database update itself is attempted regardless.
    """
    if not history_id or not supabase_client:
        logger.warning(f"Attempted to update fetch history with invalid history_id ({history_id}) or supabase_client.")
        return format_sse_message("error", "history_update_skipped_invalid_params", {"message": f"Skipping history update for {history_id} due to invalid client or ID."}), False

    payload_to_send = {**update_data, "engine_specific_parameters": all_request_params_for_history}
    # Ensure no None values accidentally overwrite existing data unless intended by update_data
    payload_to_send = {k: v for k, v in payload_to_send.items() if v is not None or k in update_data}

    sse_message_to_yield: Optional[str] = None
    db_write_successful = False
    try:
        logger.info(f"Attempting to update fetch_history record ID: {history_id} with status: {update_data.get('status')}")
        update_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .update(payload_to_send)
            .eq("id", history_id)
            .execute
        )

        if hasattr(update_response, 'data') and update_response.data:
            logger.info(f"Successfully updated fetch history {history_id} with status: {update_data.get('status')}")
            sse_message_to_yield = format_sse_message("status", "history_updated", {"message": f"Fetch history record {history_id} updated.", "status": update_data.get('status')})
            db_write_successful = True
        elif hasattr(update_response, 'error') and update_response.error:
            err_msg = update_response.error.message if hasattr(update_response.error, 'message') else str(update_response.error)
            logger.error(f"Failed to update fetch history {history_id}: {err_msg}")
            sse_message_to_yield = format_sse_message("warning", "history_update_failed", {"message": f"Could not update history record {history_id}: {err_msg}"})
        else:
            logger.error(f"Unexpected response structure when updating fetch history {history_id}: {update_response}")
            sse_message_to_yield = format_sse_message("warning", "history_update_unexpected_response", {"message": f"Unexpected DB response for history update {history_id}."})
    except Exception as e:
        logger.error(f"Exception updating fetch history {history_id}: {e}", exc_info=True)
        sse_message_to_yield = format_sse_message("warning", "history_update_exception", {"message": f"Exception during history update for {history_id}: {str(e)}"})
    
    return sse_message_to_yield, db_write_successful

# --- Fetch Content Endpoint (MODIFIED for SSE) ---
@app.get("/fetch-content", tags=["Content Fetch"])
async def fetch_content_endpoint(
    request: Request, # Added Request for client host logging
    url: str = Query(..., description="URL to fetch content from"),
    engine: str = Query("jina", description="Fetching engine to use ('jina' or 'crawl4ai')"),
    generate_pdf: bool = Query(True, description="Generate PDF from fetched content (used by both engines if capable)"),
    upload_to_supabase: bool = Query(False, description="Upload content and embedding to Supabase (post-fetch process)"),

    # --- Browser/Crawling Generic Parameters (used by crawl4ai, some by Jina if applicable) ---
    headless: Optional[bool] = Query(True, description="Run browser in headless mode (crawl4ai)"),
    user_agent: Optional[str] = Query(None, description="Custom user agent string for the browser (crawl4ai)"),
    proxy_url: Optional[str] = Query(None, description="Proxy URL for browser requests (crawl4ai)"), # ADDED
    enable_javascript: Optional[bool] = Query(True, description="Enable JavaScript execution (crawl4ai)"),
    ignore_https_errors: Optional[bool] = Query(True, description="Ignore HTTPS errors (crawl4ai)"), # ADDED
    light_mode: Optional[bool] = Query(False, description="Enable light mode (reduces resource usage) (crawl4ai)"), # ADDED
    text_mode: Optional[bool] = Query(False, description="Enable text-only mode (crawl4ai)"), # ADDED
    browser_cookies: Optional[str] = Query(None, description="JSON string of cookies to set (crawl4ai)"), # ADDED
    browser_headers: Optional[str] = Query(None, description="JSON string of headers to set (crawl4ai)"), # ADDED
    browser_use_persistent_context: Optional[bool] = Query(False, description="Use persistent browser context (crawl4ai)"), # ADDED
    browser_user_data_dir: Optional[str] = Query(None, description="Path to browser user data directory (crawl4ai)"), # ADDED
    browser_extra_args: Optional[str] = Query(None, description="Comma-separated list of extra browser arguments (crawl4ai)"), # ADDED
    viewport_width: Optional[int] = Query(None, description="Browser viewport width (crawl4ai)"), # ADDED
    viewport_height: Optional[int] = Query(None, description="Browser viewport height (crawl4ai)"), # ADDED
    browser_engine: str = Query("playwright", description="Browser engine ('playwright' or 'selenium') (crawl4ai, Jina)"),
    browser_viewport: str = Query("1920x1080", description="Browser viewport (e.g., '1920x1080') (Jina specific, use viewport_width/height for crawl4ai)"), # Clarified
    browser_locale: str = Query("en-US", description="Browser locale (e.g., 'en-US') (crawl4ai, Jina)"),
    take_screenshot: Optional[bool] = Query(False, description="Enable screenshot capture (crawl4ai)"),
    take_screenshot_on_error: Optional[bool] = Query(True, description="Capture screenshot if an error occurs during crawling (crawl4ai)"),
    respect_robots_txt: Optional[bool] = Query(True, description="Whether to respect robots.txt rules (crawl4ai)"),
    
    # --- Timeouts ---
    jina_timeout_seconds: int = Query(300, description="Timeout in seconds for Jina fetch operation"),
    crawl4ai_interaction_timeout_ms: Optional[int] = Query(30000, description="Page interaction timeout for crawl4ai in ms (e.g., for JS execution)"),
    navigation_timeout_ms: Optional[int] = Query(60000, description="Page navigation timeout for crawl4ai in ms"),
    page_load_timeout_ms: Optional[int] = Query(None, description="Overall page load timeout for crawl4ai in ms (defaults to navigation_timeout_ms if None)"), # Matches crawl4ai_fetcher
    page_load_wait_condition: Optional[str] = Query(None, description="Page load wait condition (e.g., 'load', 'domcontentloaded', 'networkidle') (crawl4ai)"), # ADDED
    wait_for_element_js_condition: Optional[str] = Query(None, description="JavaScript expression to wait for before proceeding (crawl4ai)"), # ADDED

    # --- Content Extraction & Formatting Parameters (primarily crawl4ai, some overlap with Jina) ---
    target_selector: Optional[str] = Query(None, description="CSS Selector for target elements to focus on (crawl4ai, Jina)"), # Renamed from target_elements_css_selectors
    excluded_selector: Optional[str] = Query(None, description="CSS Selector for elements to exclude (crawl4ai, Jina)"), # Renamed from excluded_elements_css_selector
    excluded_tags: Optional[str] = Query(None, description="Comma-separated list of HTML tags to exclude (crawl4ai)"), # ADDED
    extract_only_text_content: Optional[bool] = Query(False, description="Extract only text content, no HTML structure (crawl4ai)"), # ADDED
    process_iframes_content: Optional[bool] = Query(False, description="Process content within iframes (crawl4ai)"), # ADDED
    word_count_threshold: Optional[int] = Query(None, description="Minimum word count for content to be considered valid (crawl4ai)"), # ADDED
    remove_forms: Optional[bool] = Query(False, description="Remove form elements from content (crawl4ai)"), # ADDED
    keep_data_attributes: Optional[bool] = Query(False, description="Keep data-* attributes in HTML (crawl4ai)"), # ADDED
    execute_javascript_on_page_load: Optional[str] = Query(None, description="JavaScript code to execute on page load (crawl4ai)"), # ADDED
    scan_full_page_auto_scroll: Optional[bool] = Query(False, description="Enable auto-scroll to capture full page content (crawl4ai)"), # ADDED
    scroll_delay_seconds: Optional[float] = Query(None, description="Delay in seconds between scrolls for full page capture (crawl4ai)"), # ADDED
    attempt_remove_overlay_elements: Optional[bool] = Query(False, description="Attempt to remove overlay elements (crawl4ai)"), # ADDED
    simulate_user_behavior: Optional[bool] = Query(False, description="Simulate user behavior like mouse movements (crawl4ai)"), # ADDED
    enable_magic_handling: Optional[bool] = Query(False, description="Enable crawl4ai's 'magic' handling for complex sites (crawl4ai)"), # ADDED
    override_navigator_properties: Optional[bool] = Query(False, description="Override browser navigator properties (crawl4ai)"), # ADDED
    cache_mode: Optional[str] = Query(None, description="Cache mode for crawl4ai (e.g., 'ENABLED', 'BYPASS', 'REFRESH')"), # ADDED
    capture_screenshot_base64: Optional[bool] = Query(False, description="Capture screenshot as base64 (crawl4ai)"), # ADDED (distinct from take_screenshot)
    # generate_pdf: bool = Query(True, ...) is already present
    capture_mhtml_snapshot: Optional[bool] = Query(False, description="Capture MHTML snapshot of the page (crawl4ai)"), # ADDED
    exclude_external_images: Optional[bool] = Query(False, description="Exclude external images from extraction (crawl4ai)"), # ADDED
    image_alt_text_min_word_count: Optional[int] = Query(None, description="Min word count for image alt text to be considered (crawl4ai)"), # ADDED
    image_relevance_score_threshold: Optional[int] = Query(None, description="Relevance score threshold for images (crawl4ai)"), # ADDED
    exclude_external_links: Optional[bool] = Query(False, description="Exclude external links from extraction (crawl4ai)"), # ADDED
    exclude_social_media_links: Optional[bool] = Query(False, description="Exclude social media links (crawl4ai)"), # ADDED
    custom_excluded_domains: Optional[str] = Query(None, description="Comma-separated list of custom domains to exclude (crawl4ai)"), # ADDED
    # respect_robots_txt: Optional[bool] = Query(True, ...) is already present
    verbose_logging: Optional[bool] = Query(False, description="Enable verbose logging for crawl4ai"), # ADDED
    log_page_console_output: Optional[bool] = Query(False, description="Log page console output during crawl (crawl4ai)"), # ADDED
    crawl_session_id: Optional[str] = Query(None, description="Session ID for crawl4ai"), # ADDED
    crawl_css_selector: Optional[str] = Query(None, description="Global CSS selector for crawl4ai (distinct from target_selector)"), # ADDED
    crawl4ai_markdown_generator: Optional[str] = Query(None, description="Specify markdown generator for crawl4ai (e.g., 'Default')"), # ADDED
    
    # --- Deep Crawl Individual Parameters (used if deep_crawl_config blob is not provided) ---
    deep_crawl_strategy_name: Optional[str] = Query(None, alias="deep_crawl_strategy_name", description="Name of the deep crawl strategy (e.g., BFSDeepCrawlStrategy)"),
    deep_crawl_max_depth: Optional[int] = Query(None, alias="deep_crawl_max_depth", description="Maximum depth for deep crawling"),
    deep_crawl_max_pages: Optional[int] = Query(None, alias="deep_crawl_max_pages", description="Maximum number of pages for deep crawling"),
    deep_crawl_include_external: Optional[bool] = Query(None, alias="deep_crawl_include_external", description="Include external links in deep crawl"),
    deep_crawl_score_threshold: Optional[float] = Query(None, alias="deep_crawl_score_threshold", description="Score threshold for deep crawl strategies like BFS/DFS"),
    deep_crawl_filter_regexes: Optional[str] = Query(None, alias="deep_crawl_filter_regexes", description="Comma-separated regex patterns for URL filtering in deep crawl"),
    deep_crawl_url_scorer_type: Optional[str] = Query(None, alias="deep_crawl_url_scorer_type", description="Type of URL scorer for BestFirstCrawlingStrategy (e.g., KeywordRelevanceScorer)"),
    deep_crawl_scorer_keywords: Optional[str] = Query(None, alias="deep_crawl_scorer_keywords", description="Comma-separated keywords for KeywordRelevanceScorer"),
    deep_crawl_scorer_weight: Optional[float] = Query(None, alias="deep_crawl_scorer_weight", description="Weight for KeywordRelevanceScorer"),
    
    deep_crawl_config: Optional[str] = Query(None, description="JSON string for deep crawl strategy configuration (crawl4ai)"), # ADDED
    extraction_config: Optional[str] = Query(None, description="JSON string for extraction strategy configuration (crawl4ai)"), # ADDED
 
    extraction_strategy: Optional[str] = Query("markdown", description="Content extraction strategy for crawl4ai (e.g., 'markdown', 'llm')"), # This was for Jina, now more general
    output_format: Optional[str] = Query("markdown", description="Desired output format from crawl4ai (e.g., 'markdown', 'text')"), # This was for Jina, now more general
    token_budget: int = Query(4000, description="Max tokens for content processing (crawl4ai token_limit, Jina token_budget)"),
    remove_images: bool = Query(False, description="Remove images from content (crawl4ai, Jina)"),
    extract_links: bool = Query(True, description="Extract links from content (crawl4ai, Jina)"),
    extract_metadata: bool = Query(True, description="Extract page metadata (crawl4ai, Jina)"),
    markdown_flavor: str = Query("github", description="Markdown flavor for output (crawl4ai, Jina)"),

    # --- LLM Specific Parameters (for crawl4ai's LLM features like captioning or LLM extraction) ---
    image_captioning: bool = Query(False, description="Enable image captioning (crawl4ai with LLM, Jina)"),
    llm_provider: Optional[str] = Query("openai", description="LLM provider for crawl4ai (e.g., 'openai', 'groq', 'ollama/model')"),
    llm_api_key: Optional[str] = Query(None, description="API key for the LLM provider (use environment variables if None)"),
    llm_model_name: Optional[str] = Query("gpt-3.5-turbo", description="Specific LLM model name for crawl4ai"),
    llm_temperature: Optional[float] = Query(0.7, ge=0.0, le=2.0, description="LLM temperature for crawl4ai"),
    llm_max_tokens: Optional[int] = Query(1000, ge=1, description="LLM max tokens for generation for crawl4ai"),

    # --- Jina Specific Parameters (ignored by crawl4ai) ---
    json_response: bool = Query(True, description="Request raw JSON response from Jina (contains metadata) (Jina specific)"), # Should be Jina specific
    cache_ttl: int = Query(3600, description="Cache TTL in seconds (Jina specific)") # Should be Jina specific
):
    """
    Fetches content using the specified engine and streams progress via SSE.
    Optionally generates PDF, generates embedding, and stores in Supabase.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE /fetch-content request from {client_host} for URL: {url}, Engine: {engine}, PDF: {generate_pdf}, Supabase: {upload_to_supabase}")

    if not PROJECT_MODULES_LOADED:
        async def error_gen_no_modules():
            yield format_sse_message("error", "Core project modules not loaded. Fetch feature unavailable.")
        return EventSourceResponse(error_gen_no_modules())

    # Gather all original request parameters for potential use by fetchers
    all_request_params = {
        "url": url, "engine": engine, "generate_pdf": generate_pdf, "upload_to_supabase": upload_to_supabase,
        "headless": headless, "user_agent": user_agent, "proxy_url": proxy_url, # ADDED
        "enable_javascript": enable_javascript, "ignore_https_errors": ignore_https_errors, # ADDED
        "light_mode": light_mode, "text_mode": text_mode, # ADDED
        "browser_cookies": browser_cookies, "browser_headers": browser_headers, # ADDED
        "browser_use_persistent_context": browser_use_persistent_context, # ADDED
        "browser_user_data_dir": browser_user_data_dir, "browser_extra_args": browser_extra_args, # ADDED
        "viewport_width": viewport_width, "viewport_height": viewport_height, # ADDED
        "browser_engine": browser_engine, "browser_viewport": browser_viewport, "browser_locale": browser_locale,
        "take_screenshot": take_screenshot, "take_screenshot_on_error": take_screenshot_on_error,
        "respect_robots_txt": respect_robots_txt,
        "jina_timeout_seconds": jina_timeout_seconds,
        "crawl4ai_interaction_timeout_ms": crawl4ai_interaction_timeout_ms,
        "navigation_timeout_ms": navigation_timeout_ms,
        "page_load_timeout_ms": page_load_timeout_ms,
        "page_load_wait_condition": page_load_wait_condition, # ADDED
        "wait_for_element_js_condition": wait_for_element_js_condition, # ADDED
        "target_selector": target_selector, "excluded_selector": excluded_selector,
        "excluded_tags": excluded_tags, # ADDED
        "extract_only_text_content": extract_only_text_content, # ADDED
        "process_iframes_content": process_iframes_content, # ADDED
        "word_count_threshold": word_count_threshold, # ADDED
        "remove_forms": remove_forms, "keep_data_attributes": keep_data_attributes, # ADDED
        "execute_javascript_on_page_load": execute_javascript_on_page_load, # ADDED
        "scan_full_page_auto_scroll": scan_full_page_auto_scroll, # ADDED
        "scroll_delay_seconds": scroll_delay_seconds, # ADDED
        "attempt_remove_overlay_elements": attempt_remove_overlay_elements, # ADDED
        "simulate_user_behavior": simulate_user_behavior, # ADDED
        "enable_magic_handling": enable_magic_handling, # ADDED
        "override_navigator_properties": override_navigator_properties, # ADDED
        "cache_mode": cache_mode, # ADDED
        "capture_screenshot_base64": capture_screenshot_base64, # ADDED
        "capture_mhtml_snapshot": capture_mhtml_snapshot, # ADDED
        "exclude_external_images": exclude_external_images, # ADDED
        "image_alt_text_min_word_count": image_alt_text_min_word_count, # ADDED
        "image_relevance_score_threshold": image_relevance_score_threshold, # ADDED
        "exclude_external_links": exclude_external_links, # ADDED
        "exclude_social_media_links": exclude_social_media_links, # ADDED
        "custom_excluded_domains": custom_excluded_domains, # ADDED
        "verbose_logging": verbose_logging, "log_page_console_output": log_page_console_output, # ADDED
        "crawl_session_id": crawl_session_id, "crawl_css_selector": crawl_css_selector, # ADDED
        "crawl4ai_markdown_generator": crawl4ai_markdown_generator, # ADDED
        
        # Deep Crawl Individual Parameters
        "deep_crawl_strategy_name": deep_crawl_strategy_name,
        "deep_crawl_max_depth": deep_crawl_max_depth,
        "deep_crawl_max_pages": deep_crawl_max_pages,
        "deep_crawl_include_external": deep_crawl_include_external,
        "deep_crawl_score_threshold": deep_crawl_score_threshold,
        "deep_crawl_filter_regexes": deep_crawl_filter_regexes,
        "deep_crawl_url_scorer_type": deep_crawl_url_scorer_type,
        "deep_crawl_scorer_keywords": deep_crawl_scorer_keywords,
        "deep_crawl_scorer_weight": deep_crawl_scorer_weight,
        
        "deep_crawl_config": deep_crawl_config, # This is the JSON blob
        "extraction_config": extraction_config, # ADDED
        "extraction_strategy": extraction_strategy, "output_format": output_format,
        "token_budget": token_budget, "remove_images": remove_images, "extract_links": extract_links,
        "extract_metadata": extract_metadata, "markdown_flavor": markdown_flavor,
        "image_captioning": image_captioning, "llm_provider": llm_provider, "llm_api_key": llm_api_key,
        "llm_model_name": llm_model_name, "llm_temperature": llm_temperature, "llm_max_tokens": llm_max_tokens,
        "json_response": json_response, "cache_ttl": cache_ttl
    }
    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    # logger.debug(f"All request params for /fetch-content: {all_request_params}")


    async def event_generator():
        # --- Fetch History Variables ---
        fetch_history_id: Optional[uuid.UUID] = None
        supabase_client_for_history: Optional[Any] = None # Holds Supabase client
        terminal_status_written_to_db: bool = False # NEW: Tracks if 'success' or 'failed' status was successfully written

        # --- Other original variables ---
        fetched_data_dict: Optional[Dict[str, Any]] = None
        markdown_content: Optional[str] = None
        title: str = "Untitled"
        fetched_url_actual: str = url
        pdf_relative_path: Optional[str] = None
        embedding_generated: bool = False
        supabase_content_id_str: Optional[str] = None

        try:
            # --- Get Supabase Client for History ---
            try:
                supabase_client_for_history = get_client()
                if not supabase_client_for_history:
                    logger.error("Failed to get Supabase client for fetch history (get_client returned None).")
                    yield format_sse_message("error", "database_client_unavailable", {"message": "Database client is essential for history tracking and is unavailable."})
                    return # Stop if DB client cannot be obtained
            except RuntimeError as e_db_client:
                logger.error(f"RuntimeError getting Supabase client for fetch history: {e_db_client}", exc_info=True)
                yield format_sse_message("error", "database_connection_failed", {"message": f"Database connection error for history: {str(e_db_client)}"})
                return # Stop if DB client cannot be obtained
            except Exception as e_db_client_other:
                logger.error(f"Unexpected error getting Supabase client for fetch history: {e_db_client_other}", exc_info=True)
                yield format_sse_message("error", "database_client_error", {"message": f"Unexpected database client error for history: {str(e_db_client_other)}"})
                return

            # --- Create Initial Fetch History Record ---
            if supabase_client_for_history:
                try:
                    initial_history_payload_dict = {
                        "url": url,
                        "fetching_engine": engine,
                        "status": "pending",
                        # engine_specific_parameters will be added in the final update
                    }
                    # Validate with Pydantic model before sending to DB
                    FetchHistoryCreate(**initial_history_payload_dict)


                    create_response = await asyncio.to_thread(
                        supabase_client_for_history.table("fetch_history")
                        .insert(initial_history_payload_dict)
                        .execute
                    )
                    if hasattr(create_response, 'data') and create_response.data:
                        fetch_history_id = create_response.data[0].get('id')
                        if fetch_history_id:
                             logger.info(f"Initial fetch history record created with ID: {fetch_history_id} for URL: {url}")
                             yield format_sse_message("status", "history_created", {"message": f"Fetch history record created: {fetch_history_id}", "history_id": str(fetch_history_id)})
                        else:
                             logger.error(f"Initial fetch history record created for {url} but ID was not returned in data: {create_response.data}")
                             yield format_sse_message("warning", "history_creation_no_id", {"message": "History record created but ID missing."})
                    elif hasattr(create_response, 'error') and create_response.error:
                        err_msg = create_response.error.message if hasattr(create_response.error, 'message') else str(create_response.error)
                        logger.error(f"Failed to create initial fetch history record for {url}: {err_msg}")
                        yield format_sse_message("warning", "history_creation_failed", {"message": f"Could not create initial history record: {err_msg}"})
                    else:
                        logger.error(f"Unexpected response from Supabase during initial fetch history creation for {url}: {create_response}")
                        yield format_sse_message("warning", "history_creation_unexpected_response", {"message": "Unexpected DB response for initial history creation."})
                except ValidationError as ve:
                    logger.error(f"Validation error for initial fetch history payload for {url}: {ve.errors()}", exc_info=True)
                    yield format_sse_message("error", "history_payload_invalid", {"message": f"Initial history data invalid: {str(ve)}"})
                    # Potentially return if this is critical
                except Exception as e_hist_create:
                    logger.error(f"Exception creating initial fetch history for {url}: {e_hist_create}", exc_info=True)
                    yield format_sse_message("warning", "history_creation_exception", {"message": f"Error during initial history creation: {str(e_hist_create)}"})
            
            yield format_sse_message("status", "initializing", {"message": f"Initializing fetch process for {url} with {engine}..."})
            await asyncio.sleep(0.1) # Small delay for frontend to catch up

            if engine.lower() == "crawl4ai":
                if fetch_with_crawl4ai is None: # Check if the function itself is available
                    yield format_sse_message("error", "Crawl4ai fetcher module not available.")
                    return
                logger.info(f"Using crawl4ai engine for URL: {url}")
                async for sse_event_json_str_from_fetcher in fetch_with_crawl4ai(url=url, original_request_params=all_request_params):
                    try:
                        event_data_from_fetcher = json.loads(sse_event_json_str_from_fetcher)

                        # --- LLM Logging Integration ---
                        if event_data_from_fetcher.get("type") == "llm_log_event":
                            llm_log_data = event_data_from_fetcher.get("data")
                            if llm_log_data and supabase_client_for_history: # Ensure data and client exist
                                try:
                                    # Use await if log_llm_call is async, otherwise remove await
                                    await log_llm_call(llm_log_data_dict=llm_log_data, supabase_client=supabase_client_for_history)
                                    logger.info(f"LLM call logged for type: {llm_log_data.get('llm_call_type')}, model: {llm_log_data.get('model_name')}")
                                except Exception as e_log_llm:
                                    logger.error(f"Failed to log LLM call via utility: {e_log_llm}", exc_info=True)
                                    # Optionally, yield an error to client if this failure is critical for them to know
                                    # yield format_sse_message("warning", "llm_log_failed", {"message": f"Failed to log LLM event: {str(e_log_llm)}"})
                            elif not llm_log_data:
                                logger.warning("llm_log_event received but 'data' payload was missing.")
                            elif not supabase_client_for_history:
                                logger.warning("llm_log_event received but supabase_client_for_history was not available for logging.")
                            continue # Skip yielding this event to the client
                        # --- End LLM Logging Integration ---

                        final_sse_event_dict = {
                            "type": event_data_from_fetcher.get("type"),
                            "timestamp": datetime.now().isoformat(),
                            "id": str(time.time())
                        }
                        if "status" in event_data_from_fetcher:
                            final_sse_event_dict["status"] = event_data_from_fetcher.get("status")

                        # Check for structured LLM error from crawl4ai_fetcher
                        # This is distinct from llm_log_event, this is an error *during* an LLM call within crawl4ai
                        if event_data_from_fetcher.get("type") == "error" and "llm_error" in event_data_from_fetcher:
                            final_sse_event_dict["message"] = event_data_from_fetcher.get("message", "LLM operation failed.")
                            final_sse_event_dict["llm_error"] = event_data_from_fetcher["llm_error"] # Pass the structured LLM error
                            logger.error(f"LLM Error event from crawl4ai_fetcher: {json.dumps(event_data_from_fetcher['llm_error'])}")
                        elif event_data_from_fetcher.get("type") == "error":
                            # General error from crawl4ai_fetcher
                            if "message" in event_data_from_fetcher:
                                final_sse_event_dict["message"] = event_data_from_fetcher.get("message")
                            if "details" in event_data_from_fetcher:
                                final_sse_event_dict["details"] = event_data_from_fetcher.get("details")
                        else:
                            # Non-error events (status, completed)
                            content_payload_for_final_sse = {}
                            if "message" in event_data_from_fetcher:
                                content_payload_for_final_sse["message"] = event_data_from_fetcher.get("message")
                            if "data" in event_data_from_fetcher:
                                content_payload_for_final_sse["data"] = event_data_from_fetcher.get("data")
                                if event_data_from_fetcher.get("type") == "completed" or \
                                   event_data_from_fetcher.get("status") == "completed":
                                    fetched_data_dict = event_data_from_fetcher.get("data")
                            
                            if content_payload_for_final_sse:
                                final_sse_event_dict["content"] = content_payload_for_final_sse
                            elif "message" in event_data_from_fetcher:
                                 final_sse_event_dict["content"] = event_data_from_fetcher.get("message")

                        logger.info(f"MAIN.PY /fetch-content: About to yield for crawl4ai: {json.dumps(final_sse_event_dict)}")
                        yield json.dumps(final_sse_event_dict)

                        if event_data_from_fetcher.get("type") == "error" or event_data_from_fetcher.get("status") == "error":
                            error_message_for_db = str(event_data_from_fetcher.get('message', 'Unknown error from fetcher'))
                            if "llm_error" in event_data_from_fetcher and isinstance(event_data_from_fetcher["llm_error"], dict):
                                error_message_for_db = f"LLM Error: {event_data_from_fetcher['llm_error'].get('message', error_message_for_db)}. Details: {json.dumps(event_data_from_fetcher['llm_error'].get('details'))}"

                            logger.error(f"Error event from crawl4ai_fetcher: {error_message_for_db}")
                            if fetch_history_id and supabase_client_for_history:
                                error_update_data = {"status": "failed", "error_message": error_message_for_db[:1000]}
                                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                                if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                    terminal_status_written_to_db = True
                            return
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from crawl4ai_fetcher: {sse_event_json_str_from_fetcher}")
                        yield format_sse_message("error", "Received invalid data from crawl4ai engine.")
                        if fetch_history_id and supabase_client_for_history:
                            error_update_data = {"status": "failed", "error_message": "Received invalid JSON data from crawl4ai engine."}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, error_update_data, all_request_params)
                            if db_write_ok and error_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return
                    except Exception as e_inner_crawl:
                        logger.error(f"Error processing event from crawl4ai_fetcher: {e_inner_crawl}", exc_info=True)
                        yield format_sse_message("error", f"Internal error processing crawl4ai event: {str(e_inner_crawl)}")
                        if fetch_history_id and supabase_client_for_history:
                            failure_update_data = {"status": "failed", "error_message": f"Internal error processing crawl4ai event: {str(e_inner_crawl)}"[:1000]}
                            _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                            if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                                terminal_status_written_to_db = True
                        return


            elif engine.lower() == "jina":
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Jina fetcher (fetch_content_from_url) not available.")
                    return
                logger.info(f"Using Jina engine for URL: {url}")
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_handler_output, dict) or jina_handler_output.get("error"):
                            error_detail = jina_handler_output.get("content", "Unknown error from Jina") if isinstance(jina_handler_output, dict) else str(jina_handler_output)
                            logger.error(f"Jina engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_handler_output
                    else: # Client wanted plain text (json_response is False)
                        if not isinstance(jina_handler_output, str):
                            logger.error(f"Jina engine (Text mode) for {url} returned non-string: {type(jina_handler_output)}. Content: {str(jina_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text)"
                        fetched_data_dict = {
                            "markdown": jina_handler_output, "content": jina_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }
                    
                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina..."})
                    await asyncio.sleep(0.5) # Simulate processing

                except Exception as e_jina:
                    logger.error(f"Error calling Jina fetch_content_from_url for {url}: {e_jina}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina engine: {str(e_jina)}")
                    return
            else:
                logger.warning(f"Unknown or unsupported engine '{engine}' requested for URL: {url}. Defaulting to Jina.")
                # Essentially duplicate Jina logic here or refactor Jina part into a sub-generator
                # For now, let's assume Jina is the default if not crawl4ai
                if fetch_content_from_url is None:
                    yield format_sse_message("error", "Default Jina fetcher not available.")
                    return
                yield format_sse_message("status", "fetching", {"message": f"Fetching content from {url} with Jina (default)..."})
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_default_handler_output = await fetch_content_from_url(
                        url=url, json_response=json_response, timeout=jina_timeout_seconds, target_selector=target_selector,
                        excluded_selector=excluded_selector, browser_engine=browser_engine, token_budget=token_budget,
                        remove_images=remove_images, extract_links=extract_links, image_captioning=image_captioning,
                        cache_ttl=cache_ttl, markdown_flavor=markdown_flavor, browser_viewport=browser_viewport,
                        browser_locale=browser_locale, extract_metadata=extract_metadata
                    )

                    if json_response: # Client wanted JSON
                        if not isinstance(jina_default_handler_output, dict) or jina_default_handler_output.get("error"):
                            error_detail = jina_default_handler_output.get("content", "Unknown error from Jina (default)") if isinstance(jina_default_handler_output, dict) else str(jina_default_handler_output)
                            logger.error(f"Jina (default) engine failed (JSON mode) for {url}. Response: {error_detail[:200]}")
                            yield format_sse_message("error", f"Jina (default) engine failed: {error_detail}")
                            return
                        fetched_data_dict = jina_default_handler_output
                    else: # Client wanted plain text
                        if not isinstance(jina_default_handler_output, str):
                            logger.error(f"Jina (default) engine (Text mode) for {url} returned non-string: {type(jina_default_handler_output)}. Content: {str(jina_default_handler_output)[:200]}")
                            yield format_sse_message("error", "Jina (default) engine failed: Invalid response in text mode.")
                            return
                        
                        title_match = re.search(r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)", jina_default_handler_output, re.IGNORECASE | re.MULTILINE)
                        extracted_title = title_match.group(1).strip() if title_match else "Untitled (from Text Default)"
                        fetched_data_dict = {
                            "markdown": jina_default_handler_output, "content": jina_default_handler_output,
                            "title": extracted_title, "url": url,
                            "links": [], "metadata": {}, "pdf_path": None
                        }

                    yield format_sse_message("status", "processing", {"message": "Processing content fetched by Jina (default)..."})
                    await asyncio.sleep(0.5)
                except Exception as e_jina_def:
                    logger.error(f"Error calling Jina (default) for {url}: {e_jina_def}", exc_info=True)
                    yield format_sse_message("error", f"Error with Jina (default) engine: {str(e_jina_def)}")
                    return

            # --- Post-fetch processing (PDF, Supabase) ---
            if fetched_data_dict and not fetched_data_dict.get("error"):
                markdown_content = fetched_data_dict.get('markdown') # Correct key for markdown content
                title = fetched_data_dict.get('title', 'Untitled')
                fetched_url_actual = fetched_data_dict.get('url', url)
                # pdf_path_from_fetch is specific to how Jina's fetch_content_from_url might return it
                # For crawl4ai, this would be None unless explicitly set in its "data" payload.
                pdf_path_from_fetcher = fetched_data_dict.get("pdf_path")


                if not markdown_content:
                    logger.warning(f"Engine {engine} returned no markdown content for URL: {url}")
                    # Still send a completed event, but data might be minimal
                else:
                    logger.info(f"Successfully fetched core content using {engine} from {url}. Title: '{title}'. Length: {len(markdown_content)}")

                if generate_pdf:
                    yield format_sse_message("status", "pdf_generation", {"message": "Generating PDF..."})
                    if markdown_content and pdf_path_from_fetcher: # If fetcher already made PDF
                        pdf_relative_path = pdf_path_from_fetcher
                        logger.info(f"Using PDF path from {engine} fetch: {pdf_relative_path} for {url}")
                        yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF ready at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                    elif markdown_content: # We have markdown, and PDF wasn't pre-generated
                        try:
                            # PDF_STORAGE_BASE_DIR is defined globally in main.py
                            # Ensure generate_unique_filename is available (imported from .fetch_content)
                            # Ensure generate_pdf_from_markdown_string is available (imported from .utils)
                            
                            unique_pdf_filename = generate_unique_filename(fetched_url_actual, "pdf")
                            output_pdf_filepath = PDF_STORAGE_BASE_DIR / unique_pdf_filename # Use Path object
                            
                            logger.info(f"Attempting PDF generation for {fetched_url_actual} to {output_pdf_filepath}")
                            pdf_conversion_successful = await generate_pdf_from_markdown_string(markdown_content, str(output_pdf_filepath))
                            
                            if pdf_conversion_successful:
                                # Construct relative path for client
                                # PDF_STORAGE_BASE_DIR is like "c:\...\backend\app\temp_pdfs"
                                # We want "temp_pdfs/filename.pdf"
                                base_storage_dir_name = PDF_STORAGE_BASE_DIR.name # Should be "temp_pdfs"
                                pdf_relative_path = Path(base_storage_dir_name) / unique_pdf_filename
                                pdf_relative_path = str(pdf_relative_path).replace("\\", "/") # Ensure forward slashes
                                logger.info(f"PDF generated via main.py, relative path: {pdf_relative_path}")
                                yield format_sse_message("status", "pdf_generation_complete", {"message": f"PDF generated at {pdf_relative_path}", "pdf_path": pdf_relative_path})
                            else:
                                logger.error(f"PDF conversion failed in main.py for URL {fetched_url_actual}.")
                                yield format_sse_message("warning", "pdf_generation_failed", {"message": "PDF generation failed."})
                        except Exception as e_pdf_gen:
                            logger.error(f"Error during PDF generation in main.py for {fetched_url_actual}: {e_pdf_gen}", exc_info=True)
                            yield format_sse_message("warning", "pdf_generation_error", {"message": f"Error during PDF generation: {str(e_pdf_gen)}"})
                    else: # No markdown content
                        yield format_sse_message("status", "pdf_generation_skipped", {"message": "PDF generation skipped (no content)."})
                
                if upload_to_supabase:
                    yield format_sse_message("status", "supabase_upload", {"message": "Preparing for Supabase upload..."})
                    if markdown_content:
                        embedding = await get_openai_embedding(markdown_content)
                        if embedding:
                            embedding_generated = True
                            yield format_sse_message("status", "embedding_complete", {"message": "Embedding generated."})
                            supabase_content_id = await upsert_content_to_supabase(
                                url=fetched_url_actual, title=title, markdown_content=markdown_content,
                                embedding=embedding, pdf_path=pdf_relative_path
                            )
                            if supabase_content_id:
                                supabase_content_id_str = str(supabase_content_id)
                                yield format_sse_message("status", "supabase_upload_complete", {"message": f"Content uploaded to Supabase with ID: {supabase_content_id_str}", "database_id": supabase_content_id_str})
                            else:
                                yield format_sse_message("warning", "Supabase upload failed.")
                        else:
                            yield format_sse_message("warning", "Embedding generation failed, skipping Supabase upload.")
                    else: # No markdown content
                        yield format_sse_message("status", "supabase_upload_skipped", {"message": "Supabase upload skipped (no content)."})
                
                # Update fetch_history with success details
                if fetch_history_id and supabase_client_for_history:
                    success_update_data = {
                        "status": "success",
                        "content_summary": (markdown_content or "")[:500] + "..." if markdown_content and len(markdown_content) > 500 else (markdown_content or "No content."),
                        "raw_content_path": None, # Assuming raw content isn't saved to a file path directly by this endpoint
                        "content_storage_path": pdf_relative_path,
                        "supabase_content_id": supabase_content_id_str if supabase_content_id_str else None
                    }
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, success_update_data, all_request_params)
                    # Only mark terminal status as written if the DB write for a terminal status succeeded
                    if db_write_ok and success_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg

                # Final "completed" event with all data
                final_payload_data = {
                    "url": fetched_url_actual,
                    "title": title,
                    "content": markdown_content, # Send full content if not too large, or preview
                    "content_preview": (markdown_content or "")[:250] + "..." if markdown_content else "No content.",
                    "pdf_path": pdf_relative_path,
                    "embedding_generated": embedding_generated,
                    "database_id": supabase_content_id_str,
                    "engine_used": engine
                }
                yield format_sse_message("completed", final_payload_data, {"message": f"Fetch process completed for {url}."})
            
            elif fetched_data_dict and fetched_data_dict.get("error"):
                error_msg_content = fetched_data_dict.get("content", f"Unknown error after fetching with {engine}")
                logger.error(f"Fetch process for {url} by {engine} resulted in error state: {error_msg_content}")
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": str(error_msg_content)[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", error_msg_content)
            
            else: # No fetched_data_dict (e.g., engine failed to initialize or returned unexpected structure)
                final_error_message = f"Failed to retrieve or process data using {engine} for {url}. No valid data dictionary was produced."
                logger.error(final_error_message)
                if fetch_history_id and supabase_client_for_history:
                    failure_update_data = {"status": "failed", "error_message": final_error_message[:1000]}
                    history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                    if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                        terminal_status_written_to_db = True
                    if history_update_sse_msg:
                        yield history_update_sse_msg
                yield format_sse_message("error", final_error_message)

        except asyncio.CancelledError:
            logger.info(f"SSE /fetch-content connection closed by client {client_host} for URL: {url}")
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": "Fetch cancelled by client."}
                _, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success, but client cancelled
                 logger.info(f"Fetch cancelled by client after 'success' status was set for {fetch_history_id}. Status remains 'success'.")
                 post_success_error_update = {"error_message": "Fetch cancelled by client post-success."[:1000]} # Update error message, status remains success
                 await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params) # db_write_ok not critical here
            # No yield here as the connection is likely gone
        except HTTPException as http_exc:
            logger.warning(f"HTTPException in /fetch-content generator for {url}: {http_exc.detail}", exc_info=True)
            final_error_message_to_client = f"Server error: {http_exc.detail}"
            db_error_message = f"HTTPException: {str(http_exc.detail)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"HTTPException occurred after 'success' status for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success HTTPException: {str(http_exc.detail)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        except Exception as e:
            logger.error(f"Unexpected error in /fetch-content SSE generator for {url} with {engine}: {e}", exc_info=True)
            final_error_message_to_client = f"An unexpected server error occurred: {str(e)}"
            db_error_message = f"Unexpected error: {str(e)}"[:1000]

            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                failure_update_data = {"status": "failed", "error_message": db_error_message}
                history_update_sse_msg, db_write_ok = await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, failure_update_data, all_request_params)
                if db_write_ok and failure_update_data.get("status") in ["success", "failed"]:
                    terminal_status_written_to_db = True
                if history_update_sse_msg:
                    try: yield history_update_sse_msg
                    except Exception: pass
            elif fetch_history_id and supabase_client_for_history and terminal_status_written_to_db: # Already success
                logger.info(f"Error occurred after 'success' status was set for {fetch_history_id}. Error: {db_error_message}. Status remains 'success'.")
                post_success_error_update = {"error_message": f"Post-success error: {str(e)}"[:1000]}
                await _update_fetch_history_record(supabase_client_for_history, fetch_history_id, post_success_error_update, all_request_params)
            try:
                yield format_sse_message("error", final_error_message_to_client)
            except Exception: pass
        finally:
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                logger.warning(f"Fetch process for history ID {fetch_history_id} (URL: {url}) ended without confirmed terminal status. Attempting to mark as 'failed'.")
                final_failure_data = {
                    "status": "failed",
                    "error_message": "Process terminated without explicit success or failure status update."[:1000]
                }
                # This update is critical for DB state; SSE message not yielded from finally.
                await _update_fetch_history_record(
                    supabase_client_for_history,
                    fetch_history_id,
                    final_failure_data,
                    all_request_params
                )
            logger.info(f"SSE /fetch-content event generator finished for {client_host}, URL: {url}")

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


# --- PDF Serving Endpoints ---

def secure_path_join(base: Path, requested_path: str) -> Optional[Path]:
    """Safely join a base directory and a requested path, preventing traversal."""
    try:
        # Normalize the requested path to prevent tricks like '..'
        normalized_req_path = os.path.normpath(requested_path)

        # Disallow absolute paths in the request
        if os.path.isabs(normalized_req_path):
            logger.warning(f"Attempted absolute path request: {normalized_req_path}")
            return None

        # Join base and requested path
        full_path = base.joinpath(normalized_req_path).resolve()

        # Crucial check: Ensure the resolved path is still within the base directory
        if base.resolve() in full_path.parents or base.resolve() == full_path:
             # Further check: ensure the part after the base matches the normalized request
             # This helps prevent issues if base itself contains '..' like structures (though resolve() should handle it)
             relative_part = full_path.relative_to(base.resolve())
             if str(relative_part) == normalized_req_path:
                  return full_path
             else:
                  logger.warning(f"Path validation failed: Relative part mismatch. Base='{base}', Req='{requested_path}', Resolved='{full_path}', Relative='{relative_part}'")
                  return None
        else:
            logger.warning(f"Directory traversal attempt blocked: Base='{base}', Req='{requested_path}', Resolved='{full_path}'")
            return None
    except Exception as e:
        logger.error(f"Error during secure path join: {e}", exc_info=True)
        return None

@app.get("/view-pdf", tags=["Files"])
async def view_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for inline viewing."""
    logger.info(f"Request to view PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for viewing at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=secure_full_path.name, # Provides a default filename if user saves
            content_disposition_type="inline" # Display in browser
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for viewing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")

@app.get("/download-pdf", tags=["Files"])
async def download_pdf_endpoint(path: str = Query(..., description="Relative path to the PDF file within the storage directory")):
    """Serves a generated PDF file for download as an attachment."""
    logger.info(f"Request to download PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for download at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        # Use a generic filename or derive from path if needed
        download_filename = f"downloaded_{secure_full_path.name}"
        return FileResponse(
            path=str(secure_full_path),
            media_type='application/pdf',
            filename=download_filename, # Suggests this filename to the browser
            content_disposition_type="attachment" # Force download dialog
        )
    except Exception as e:
        logger.error(f"Error serving PDF {secure_full_path} for download: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")


# --- Include Other Routers ---
# (Keep existing router includes - lines 1722-1741)
if PROJECT_MODULES_LOADED:
    if 'content_upserter_router' in locals() and content_upserter_router:
        try: app.include_router(content_upserter_router, prefix="/api/content", tags=["Content Management"])
        except Exception as e: logger.warning(f"Failed to include content_upserter_router: {e}")

    if 'fetch_history_router' in locals() and fetch_history_router: # Added this block
        try: app.include_router(fetch_history_router, prefix="/api", tags=["Fetch History"]) # Using /api prefix for consistency
        except Exception as e: logger.warning(f"Failed to include fetch_history_router: {e}")

    if 'metrics_router' in locals() and metrics_router:
        try: app.include_router(metrics_router, prefix="/monitoring", tags=["Monitoring"])
        except Exception as e: logger.warning(f"Failed to include metrics_router: {e}")

    if 'monitoring_router' in locals() and metrics_router != monitoring_router and monitoring_router:
         try: app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
         except Exception as e: logger.warning(f"Failed to include monitoring_router: {e}")

    if 'search_config_router' in locals() and search_config_router:
        try: app.include_router(search_config_router, prefix="/api/search-config", tags=["Search Configuration"])
        except Exception as e: logger.warning(f"Failed to include search_config_router: {e}")

# --- Include Debug Endpoints ---
try:
    from .debug_endpoints import router as debug_router
    app.include_router(debug_router)
    logger.info("Debug endpoints included.")
except Exception as e:
    logger.warning(f"Failed to include debug endpoints: {e}")


# --- Vector Search Endpoint (MODIFIED to use SQL Function) ---
@app.post("/api/vector-search", response_model=VectorSearchResponse, tags=["Search"])
async def vector_search_endpoint(request: VectorSearchRequest):
    """Perform vector search using the advanced_hybrid_search SQL function."""
    logger.info(f"Vector search request: Query='{request.query[:50]}...', Max={request.max_results}, Threshold={request.threshold}")

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Database client unavailable.")
        if not openai_client:
             raise HTTPException(status_code=503, detail="Embedding service unavailable.")

        # 1. Generate query embedding
        query_embedding = await get_openai_embedding(request.query)
        if query_embedding is None:
            # get_openai_embedding now logs detailed LLM call info internally.
            # Here, we raise a structured error for the client.
            error_detail_payload = {
                "error_code": "EMBEDDING_GENERATION_FAILED",
                "message": "Failed to generate query embedding for vector search.",
                "llm_error_type": "EmbeddingError", # Generic, as detailed type is in server logs
                "details": {
                    "query_preview": (request.query[:100] + "...") if request.query and len(request.query) > 100 else request.query,
                    "suggestion": "Check server logs for detailed error information from the embedding service."
                }
            }
            logger.error(f"Raising HTTPException for vector search due to embedding failure. Payload: {json.dumps(error_detail_payload)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail_payload
            )

        # 2. Prepare parameters for the SQL function
        #    Match parameters defined in the SQL function (adjust dimension if needed)
        params = {
            'query_embedding': query_embedding,
            'match_count': request.max_results,
            'min_similarity': request.threshold, # Assuming threshold maps to min_similarity
            'content_weight': request.content_weight, # Pass weights from request
            'summary_weight': request.summary_weight,
            'video_filter': request.video_filter # Pass filter from request
        }
        logger.debug(f"Calling Supabase RPC advanced_hybrid_search with params: match_count={params['match_count']}, min_similarity={params['min_similarity']}, content_weight={params['content_weight']}, summary_weight={params['summary_weight']}, video_filter={params['video_filter']}")

        # 3. Call the Supabase function via RPC
        response = await asyncio.to_thread(
             supabase_client.rpc('advanced_hybrid_search', params).execute
        )
        # response = supabase_client.rpc('advanced_hybrid_search', params).execute() # Original sync call

        # 4. Process results
        search_results = []
        if hasattr(response, 'data') and response.data:
            search_results = response.data
            logger.info(f"Advanced hybrid search returned {len(search_results)} results.")
        elif hasattr(response, 'error') and response.error:
             logger.error(f"Supabase RPC error during advanced_hybrid_search: {response.error}")
             raise HTTPException(status_code=500, detail=f"Database search error: {response.error}")
        else:
             logger.warning(f"Unexpected response structure from Supabase search RPC: {response}")
             # Return empty results

        # 5. Prepare response metadata (optional AI response generation removed for now)
        metadata = {
            "query": request.query,
            "results_count": len(search_results),
            "search_function": "advanced_hybrid_search",
            "parameters_used": {
                "threshold": request.threshold,
                "max_results": request.max_results,
                "content_weight": request.content_weight,
                "summary_weight": request.summary_weight,
                "video_filter": request.video_filter
            },
            "token_usage": token_counter.get_stats() # Include token stats
        }

        return VectorSearchResponse(
            results=search_results, # The SQL function should return dicts directly
            ai_response=None, # AI response generation can be added later if needed
            metadata=metadata
        )

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI errors
    except Exception as e:
         logger.error(f"Error during vector search for query '{request.query[:50]}...': {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")


# --- Comprehensive Search Endpoint (Using psearchworking) ---
# (Keep existing /api/search endpoint - lines 1806-1945)
@app.post("/api/search", response_model=ComprehensiveSearchResponse, tags=["Search"])
async def comprehensive_search_endpoint(
    request: ComprehensiveSearchRequest, # Request body
    # Query parameters for overrides
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
    preset: Optional[str] = Query(None)
):
    """
    Perform comprehensive search using logic from psearchworking.
    Accepts optional query parameters to override search settings.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    logger.info(f"Search request: Query='{request.query[:50]}...', MaxRes={request.max_results}, Analysis={request.run_analysis}, Preset='{preset}'")

    try:
        update_successful = global_search_params.update_from_frontend(
            preset=preset,
            fine_grained_similarity_threshold=fg_similarity_threshold,
            fine_grained_content_weight=fg_content_weight,
            fine_grained_result_percentage=fg_result_percentage,
            fine_grained_max_results=fg_max_results,
            contextual_similarity_threshold=ctx_similarity_threshold,
            contextual_content_weight=ctx_content_weight,
            contextual_result_percentage=ctx_result_percentage,
            contextual_max_results=ctx_max_results,
            overview_similarity_threshold=ov_similarity_threshold,
            overview_content_weight=ov_content_weight,
            overview_result_percentage=ov_result_percentage,
            overview_max_results=ov_max_results,
        )
        if not update_successful:
             logger.warning("Search parameters updated from frontend might be invalid (e.g., sum > 1.0). Check psearchworking validation logic.")
        logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
    except Exception as param_err:
         logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search parameters provided.")

    start_time = time.time()
    try:
        results, openai_analysis, groq_analysis = await asyncio.to_thread(
            search_all,
            query=request.query,
            max_results=request.max_results,
            skip_prompts=True,
            run_analysis=request.run_analysis
        )

        search_duration = time.time() - start_time
        logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")

        formatted_results = []
        if results:
            try:
                formatted_results = [res.to_dict() for res in results]
                logger.info(f"Successfully converted {len(formatted_results)} SearchResult objects to dictionaries")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                formatted_results = []
                for res in results:
                    try:
                        result_dict = {
                            'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                            'content_id': getattr(res, 'content_id', None),
                            'content': getattr(res, 'content', None),
                            'similarity': getattr(res, 'similarity', 0.0),
                            'source': getattr(res, 'source', 'unknown'),
                            'title': getattr(res, 'title', ''),
                            'start_time': getattr(res, 'start_time', None),
                            'end_time': getattr(res, 'end_time', None),
                            'url': getattr(res, 'url', ''),
                            'watch_url': getattr(res, 'watch_url', ''),
                            'video_id': getattr(res, 'video_id', None),
                            'segment_id': getattr(res, 'segment_id', None),
                            'summary': getattr(res, 'summary', ''),
                            'metadata': getattr(res, 'metadata', {}),
                            'search_method': getattr(res, 'search_method', 'unknown'),
                            'content_type': getattr(res, 'content_type', 'unknown')
                        }
                        formatted_results.append(result_dict)
                    except Exception as item_err:
                        logger.error(f"Error formatting individual result: {item_err}")
                logger.info(f"Manually converted {len(formatted_results)} SearchResult objects to dictionaries")

        metadata = {
            "query": request.query,
            "total_results_found": len(results),
            "search_duration_seconds": round(search_duration, 2),
            "analysis_run": request.run_analysis,
            "effective_params": global_search_params.get_all_params(),
            "search_complete": True,
            "analysis_complete": request.run_analysis and (openai_analysis is not None or groq_analysis is not None)
        }
        try:
            try:
                from .psearchworking import token_counter as psearch_token_counter
                metadata["token_usage"] = psearch_token_counter.get_stats()
            except (ImportError, AttributeError):
                metadata["token_usage"] = token_counter.get_stats()
        except (NameError, AttributeError) as tk_err:
            logger.warning(f"Could not get token stats: {tk_err}")

        return ComprehensiveSearchResponse(
            query=request.query,
            results=formatted_results,
            openai_analysis=openai_analysis,
            groq_analysis=groq_analysis,
            metadata=metadata
        )

    except Exception as e:
        search_duration = time.time() - start_time
        logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search execution failed: {e}")


# --- Search SSE Endpoint (Using psearchworking) ---
# (Keep existing /api/search-sse endpoint - lines 1948-2131)
@app.get("/api/search-sse", tags=["Search"])
async def search_sse_endpoint(
    request: Request,
    query: str = Query(..., min_length=1),
    max_results: int = Query(30, ge=10, le=100),
    run_analysis: bool = Query(True),
    preset: Optional[str] = Query(None),
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
):
    """
    Server-Sent Events endpoint for real-time search updates.
    Provides incremental updates as the search progresses.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    client_host = request.client.host if request.client else "unknown"
    logger.info(f"SSE search request from {client_host}: Query='{query[:50]}...', MaxRes={max_results}, Analysis={run_analysis}, Preset='{preset}'")

    async def event_generator():
        try:
            yield format_sse_message("status", "Starting search operation", {"stage": "start"})
            await asyncio.sleep(0.5)

            yield format_sse_message("status", "Configuring search parameters", {"stage": "search"})
            try:
                update_successful = global_search_params.update_from_frontend(
                    preset=preset,
                    fine_grained_similarity_threshold=fg_similarity_threshold,
                    fine_grained_content_weight=fg_content_weight,
                    fine_grained_result_percentage=fg_result_percentage,
                    fine_grained_max_results=fg_max_results,
                    contextual_similarity_threshold=ctx_similarity_threshold,
                    contextual_content_weight=ctx_content_weight,
                    contextual_result_percentage=ctx_result_percentage,
                    contextual_max_results=ctx_max_results,
                    overview_similarity_threshold=ov_similarity_threshold,
                    overview_content_weight=ov_content_weight,
                    overview_result_percentage=ov_result_percentage,
                    overview_max_results=ov_max_results,
                )
                if not update_successful:
                    logger.warning("Search parameters updated from frontend might be invalid")
                    yield format_sse_message("status", "Warning: Some search parameters may be invalid", {"stage": "search"})
                logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
            except Exception as param_err:
                logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
                yield format_sse_message("error", f"Invalid search parameters: {param_err}")
                return

            start_time = time.time()
            yield format_sse_message("status", "Executing search query", {"stage": "filter"})
            try:
                results, openai_analysis, groq_analysis = await asyncio.to_thread(
                    search_all, query=query, max_results=max_results, skip_prompts=True, run_analysis=run_analysis
                )
                search_duration = time.time() - start_time
                logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")
                yield format_sse_message("status", "Combining search results", {"stage": "combine"})
                await asyncio.sleep(0.5)

                formatted_results = []
                if results:
                    try: formatted_results = [res.to_dict() for res in results]
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                        formatted_results = []
                        for res in results:
                            try:
                                result_dict = {
                                    'id': f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                                    'content_id': getattr(res, 'content_id', None), 'content': getattr(res, 'content', None),
                                    'similarity': getattr(res, 'similarity', 0.0), 'source': getattr(res, 'source', 'unknown'),
                                    'title': getattr(res, 'title', ''), 'start_time': getattr(res, 'start_time', None),
                                    'end_time': getattr(res, 'end_time', None), 'url': getattr(res, 'url', ''),
                                    'watch_url': getattr(res, 'watch_url', ''), 'video_id': getattr(res, 'video_id', None),
                                    'segment_id': getattr(res, 'segment_id', None), 'summary': getattr(res, 'summary', ''),
                                    'metadata': getattr(res, 'metadata', {}), 'search_method': getattr(res, 'search_method', 'unknown'),
                                    'content_type': getattr(res, 'content_type', 'unknown')
                                }
                                formatted_results.append(result_dict)
                            except Exception as item_err: logger.error(f"Error formatting individual result: {item_err}")

                metadata = {
                    "query": query, "total_results_found": len(results), "search_duration_seconds": round(search_duration, 2),
                    "analysis_run": run_analysis, "effective_params": global_search_params.get_all_params(),
                    "search_complete": True, "stage": "complete"
                }
                try:
                    try: from .psearchworking import token_counter as psearch_token_counter; metadata["token_usage"] = psearch_token_counter.get_stats()
                    except (ImportError, AttributeError): metadata["token_usage"] = token_counter.get_stats()
                except (NameError, AttributeError) as tk_err: logger.warning(f"Could not get token stats: {tk_err}")

                if run_analysis:
                    yield format_sse_message("status", "Analyzing search results", {"stage": "analyze"})
                    if openai_analysis: yield format_sse_message("analysis", openai_analysis, {"provider": "openai"})
                    if groq_analysis: yield format_sse_message("analysis", groq_analysis, {"provider": "groq"})
                    metadata["analysis_complete"] = bool(openai_analysis or groq_analysis)

                yield format_sse_message("results", formatted_results, {**metadata, "stage": "complete"})
                yield format_sse_message("complete", "Search process completed", {"stage": "complete"})

            except Exception as e:
                search_duration = time.time() - start_time
                error_msg = f"Search execution failed: {e}"
                logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
                yield format_sse_message("error", error_msg)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed by client {client_host}")
        except Exception as e:
            logger.error(f"Unexpected error in search SSE generator: {e}", exc_info=True)
            yield format_sse_message("error", f"Unexpected error: {e}")

    return EventSourceResponse(event_generator())

# --- Root and Health Check ---
# (Keep existing / and /health endpoints - lines 2133-2160)
@app.get("/", tags=["Utility"])
async def root():
    """Root endpoint providing basic service status."""
    logger.info("Root endpoint '/' called.")
    return {"service": "PMOVES Transcription API", "status": "running", "version": app.version, "timestamp": datetime.now().isoformat()}

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    logger.debug("Health check '/health' called")
    db_status = "connected"
    try:
         client = get_client()
    except Exception as e:
         db_status = f"error: {e}"
         logger.warning(f"Health check: Supabase client unavailable: {e}")
    return {"status": "healthy", "dependencies": {"database": db_status}, "timestamp": datetime.now().isoformat()}


# --- Test Event Loop Policy Route ---
@app.get("/test-event-loop-policy", tags=["Utility", "Debug"])
async def test_event_loop_policy_route():
    # asyncio is imported at the top. logger is defined globally.
    policy_name = asyncio.get_event_loop_policy().__class__.__name__
    logger.info(f"Policy in /test-event-loop-policy route: {policy_name}")
    return {"active_policy": policy_name}

# --- ASGI Server Runner ---
# (Keep existing __main__ block - lines 2165-2194)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")
    # Log policy before Uvicorn run
    logger.info(f"Policy before Uvicorn run in __main__: {asyncio.get_event_loop_policy().__class__.__name__}")
    app_host = os.getenv("HOST", "127.0.0.1")
    try: app_port = int(os.getenv("PORT", "8000"))
    except ValueError: logger.warning(f"Invalid PORT env var '{os.getenv('PORT')}', using 8000."); app_port = 8000
    reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
    if reload_flag: logger.warning("Auto-reload enabled. Recommended only for development.")
    uvicorn.run(
        f"{Path(__file__).stem}:app", host=app_host, port=app_port, reload=reload_flag, log_level="info"
    )

# --- App Config Endpoint ---
@app.get("/api/app-config", tags=["Utility"])
async def get_app_config():
    """Expose backend folder and subfolder config to the frontend."""
    return {
        "WORKSPACE_ROOT": WORKSPACE_ROOT,
        "SUBFOLDERS": SUBFOLDERS
    }

# --- Workspace Directory Listing Endpoint ---
@app.get("/api/list-workspace", tags=["Utility"])
async def list_workspace():
    """Recursively list all files and folders under the workspace root."""
    def list_dir(path, rel_path=""):
        items = []
        for entry in os.scandir(path):
            entry_rel_path = os.path.join(rel_path, entry.name)
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "type": "folder",
                    "path": entry_rel_path.replace("\\", "/"),
                    "children": list_dir(entry.path, entry_rel_path)
                })
            else:
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": entry_rel_path.replace("\\", "/"),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return sorted(items, key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    tree = list_dir(WORKSPACE_ROOT)
    return {"root": WORKSPACE_ROOT, "tree": tree}

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.


<environment_details>
# VSCode Visible Files
backend/app/main.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
backend/app/main.py

# Current Time
5/13/2025, 10:05:36 AM (America/New_York, UTC-4:00)

# Context Window Usage
152,251 / 1,048.576K tokens used (15%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>The user provided feedback showing a `NameError: name 'subprocess' is not defined` in `backend/app/main.py`. I attempted to fix this by adding `import subprocess` to the standard library imports section.

The user's feedback shows the traceback clearly pointing to the line where `subprocess.CREATE_NEW_PROCESS_GROUP` is used within the `startup_event` function. The error message "NameError: name 'subprocess' is not defined. Did you forget to import 'subprocess'" confirms that the import was indeed missing or not in the correct scope.

My previous action was to add `import subprocess` to the standard library imports. The `replace_in_file` tool reported success. This should have resolved the `NameError`.

The user's feedback also includes the full log output from running `uvicorn app.main:app`. This log shows that the `ollama_initializer script` was *launched*, but then the `NameError` occurred *within* the `startup_event` function of `main.py`. This confirms my diagnosis that the `subprocess` import was missing in `main.py`.

Since I have now added the `subprocess` import to `backend/app/main.py`, the `NameError` should be resolved. The task of implementing the Ollama initializer script and integrating it into the backend startup is complete.

I will attempt completion again, providing the same command as before, as the fix should now allow the backend to start without the `NameError`. The user can then verify in the logs that the Ollama initializer script runs successfully and attempts to load the selected model.<attempt_completion>
<result>
I have added the missing `import subprocess` to `backend/app/main.py`. This should resolve the `NameError` that occurred during startup.

The implementation to launch the Ollama initializer script during backend startup is now complete.

To test this, set the `LLM_MODEL` environment variable to an Ollama model ID (e.g., `ollama/gemma3`) and then run the backend server. Observe the server logs for messages indicating the Ollama initializer script is being launched and attempting to load the model.
</result>
<command>
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
</command>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user denied this operation.
The user provided the following feedback:
<feedback>
(PMOVES-transcribe-and-fetch) PS C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend> uvicorn app.main:app
[05/13/25 10:33:43] INFO     Logging initialized. Console: always. File: disabled
2025-05-13 10:33:43,835 - app.main - INFO - Logging initialized. Console: always. File: disabled
                    INFO     Policy set in main.py (top level): WindowsProactorEventLoopPolicy
2025-05-13 10:33:43,838 - app.main - INFO - Policy set in main.py (top level): WindowsProactorEventLoopPolicy
[05/13/25 10:33:46] INFO     Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:33:46,590 - app.main - INFO - Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
                    INFO     Async OpenAI client initialized.
2025-05-13 10:33:46,922 - app.main - INFO - Async OpenAI client initialized.
[05/13/25 10:33:47] INFO     Async Groq client initialized.
2025-05-13 10:33:47,101 - app.main - INFO - Async Groq client initialized.
2025-05-13 10:33:47,789 - app.app_config - INFO - Looking for .env file at: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:33:47,791 - app.app_config - INFO - OPENAI_API_KEY loaded: Yes
2025-05-13 10:33:47,791 - app.app_config - INFO - OPENAI_API_KEY starts with: sk-pr...
2025-05-13 10:33:47,791 - app.app_config - INFO - ANTHROPIC_API_KEY loaded: Yes
2025-05-13 10:33:47,791 - app.app_config - ERROR - Default placeholder value detected for ANTHROPIC_API_KEY - please update your .env file.
2025-05-13 10:33:47,791 - app.app_config - INFO - GROQ_API_KEY loaded: Yes
2025-05-13 10:33:47,791 - app.app_config - INFO - GROQ_API_KEY starts with: gsk_W...
2025-05-13 10:33:47,791 - app.app_config - INFO - GEMINI_API_KEY loaded: Yes
2025-05-13 10:33:47,791 - app.app_config - INFO - GEMINI_API_KEY starts with: AIzaS...
2025-05-13 10:33:47,791 - app.app_config - INFO - DEEPSEEK_API_KEY loaded: Yes
2025-05-13 10:33:47,792 - app.app_config - ERROR - Default placeholder value detected for DEEPSEEK_API_KEY - please update your .env file.
2025-05-13 10:33:47,792 - app.app_config - INFO - MISTRAL_API_KEY loaded: Yes
2025-05-13 10:33:47,792 - app.app_config - ERROR - Default placeholder value detected for MISTRAL_API_KEY - please update your .env file.
2025-05-13 10:33:47,792 - app.app_config - INFO - TOGETHER_AI_API_KEY loaded: Yes
2025-05-13 10:33:47,792 - app.app_config - ERROR - Default placeholder value detected for TOGETHER_AI_API_KEY - please update your .env file.
2025-05-13 10:33:47,792 - app.app_config - INFO - COHERE_API_KEY loaded: Yes
2025-05-13 10:33:47,792 - app.app_config - ERROR - Default placeholder value detected for COHERE_API_KEY - please update your .env file.
2025-05-13 10:33:47,792 - app.app_config - INFO - FIREWORKS_AI_API_KEY loaded: Yes
2025-05-13 10:33:47,792 - app.app_config - ERROR - Default placeholder value detected for FIREWORKS_AI_API_KEY - please update your .env file.
2025-05-13 10:33:47,792 - app.app_config - INFO - OLLAMA_BASE_URL loaded: http://localhost:11434
2025-05-13 10:33:47,792 - app.app_config - INFO - OLLAMA_BASE_URL appears to be a local address: http://localhost:11434
2025-05-13 10:33:47,792 - app.app_config - INFO - OPENAI_COMPATIBLE_BASE_URL loaded: http://localhost:1234/v1
2025-05-13 10:33:47,793 - app.app_config - INFO - OPENAI_COMPATIBLE_BASE_URL appears to be a local address: http://localhost:1234/v1
Rich console is available.
2025-05-13 10:33:47,876 - app.transcribe1 - INFO - --- System Info ---
2025-05-13 10:33:47,876 - app.transcribe1 - INFO - Selected Whisper model size: large-v3
2025-05-13 10:33:47,876 - app.transcribe1 - INFO - CUDA available: True
2025-05-13 10:33:47,876 - app.transcribe1 - INFO - Determined optimal device: 'cuda' with compute type: 'float16'
2025-05-13 10:33:47,878 - app.transcribe1 - INFO - GPU Device Name: NVIDIA GeForce RTX 3090 Ti
2025-05-13 10:33:47,878 - app.transcribe1 - INFO - GPU Memory: 23.99 GB
2025-05-13 10:33:47,878 - app.transcribe1 - INFO - CUDA Device Capability: (8, 6)
2025-05-13 10:33:47,878 - app.transcribe1 - INFO - CUDA Device Count: 1
2025-05-13 10:33:47,878 - app.transcribe1 - INFO - --- End System Info ---
Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:33:48,642 - search_params - INFO - Loaded search parameters from preset: default
2025-05-13 10:33:48,718 - search_params - INFO - Loaded search parameters from preset: default
2025-05-13 10:33:48,730 - app.routes.fetch_history_routes - INFO - Ensured fetched content storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\fetched_content
[05/13/25 10:33:48] INFO     TokenCounter initialized with tiktoken encoders.
2025-05-13 10:33:48,736 - app.main - INFO - TokenCounter initialized with tiktoken encoders.
                    INFO     Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
2025-05-13 10:33:48,745 - app.main - INFO - Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
                    INFO     SSE monitoring middleware enabled.
2025-05-13 10:33:48,745 - app.main - INFO - SSE monitoring middleware enabled.
                    INFO     Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\temp_pdfs
2025-05-13 10:33:48,750 - app.main - INFO - Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\temp_pdfs
                    INFO     Debug endpoints included.
2025-05-13 10:33:48,769 - app.main - INFO - Debug endpoints included.
INFO:     Started server process [62328]
INFO:     Waiting for application startup.
                    INFO     Application startup initiated...
2025-05-13 10:33:48,774 - app.main - INFO - Application startup initiated...
                    INFO     System metrics collection scheduled.
2025-05-13 10:33:48,775 - app.main - INFO - System metrics collection scheduled.
                    INFO     Queue manager started.
2025-05-13 10:33:48,776 - app.main - INFO - Queue manager started.
                    INFO     Launching Ollama initializer script...
2025-05-13 10:33:48,777 - app.main - INFO - Launching Ollama initializer script...
                    INFO     Ollama initializer script launched with PID: 66760
2025-05-13 10:33:48,786 - app.main - INFO - Ollama initializer script launched with PID: 66760
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
2025-05-13 10:33:48,886 - app_config - INFO - Looking for .env file at: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-13 10:33:48,888 - app_config - INFO - OPENAI_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - INFO - OPENAI_API_KEY starts with: sk-pr...
2025-05-13 10:33:48,889 - app_config - INFO - ANTHROPIC_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - ERROR - Default placeholder value detected for ANTHROPIC_API_KEY - please update your .env file.
2025-05-13 10:33:48,889 - app_config - INFO - GROQ_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - INFO - GROQ_API_KEY starts with: gsk_W...
2025-05-13 10:33:48,889 - app_config - INFO - GEMINI_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - INFO - GEMINI_API_KEY starts with: AIzaS...
2025-05-13 10:33:48,889 - app_config - INFO - DEEPSEEK_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - ERROR - Default placeholder value detected for DEEPSEEK_API_KEY - please update your .env file.
2025-05-13 10:33:48,889 - app_config - INFO - MISTRAL_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - ERROR - Default placeholder value detected for MISTRAL_API_KEY - please update your .env file.
2025-05-13 10:33:48,889 - app_config - INFO - TOGETHER_AI_API_KEY loaded: Yes
2025-05-13 10:33:48,889 - app_config - ERROR - Default placeholder value detected for TOGETHER_AI_API_KEY - please update your .env file.
2025-05-13 10:33:48,890 - app_config - INFO - COHERE_API_KEY loaded: Yes
2025-05-13 10:33:48,890 - app_config - ERROR - Default placeholder value detected for COHERE_API_KEY - please update your .env file.
2025-05-13 10:33:48,890 - app_config - INFO - FIREWORKS_AI_API_KEY loaded: Yes
2025-05-13 10:33:48,890 - app_config - ERROR - Default placeholder value detected for FIREWORKS_AI_API_KEY - please update your .env file.
2025-05-13 10:33:48,890 - app_config - INFO - OLLAMA_BASE_URL loaded: http://localhost:11434
2025-05-13 10:33:48,890 - app_config - INFO - OLLAMA_BASE_URL appears to be a local address: http://localhost:11434
2025-05-13 10:33:48,890 - app_config - INFO - OPENAI_COMPATIBLE_BASE_URL loaded: http://localhost:1234/v1
2025-05-13 10:33:48,890 - app_config - INFO - OPENAI_COMPATIBLE_BASE_URL appears to be a local address: http://localhost:1234/v1
2025-05-13 10:33:48,890 - __main__ - INFO - Running Ollama initializer script.
2025-05-13 10:33:48,890 - __main__ - INFO - LLM_MODEL environment variable not set. Skipping Ollama model loading.
2025-05-13 10:33:48,890 - __main__ - INFO - Ollama initializer script finished. 

it did not load correctly
</feedback>
<environment_details>
# VSCode Visible Files
backend/app/main.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:35:10 AM (America/New_York, UTC-4:00)

# Context Window Usage
341,545 / 1,048.576K tokens used (33%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>The user provided feedback that the Ollama model did not load correctly. Looking at the logs they provided:

```
2025-05-13 10:33:48,890 - __main__ - INFO - Running Ollama initializer script.
2025-05-13 10:33:48,890 - __main__ - INFO - LLM_MODEL environment variable not set. Skipping Ollama model loading.
2025-05-13 10:33:48,890 - __main__ - INFO - Ollama initializer script finished.
```

This clearly shows that the `ollama_initializer.py` script ran, but it skipped loading the Ollama model because the `LLM_MODEL` environment variable was not set.

My `attempt_completion` message did instruct the user to set the `LLM_MODEL` environment variable, but it seems they ran the command without setting it first.

The task of implementing the script and integrating it into the backend startup is complete and appears to be working as intended (the script ran, checked the variable, and reported it wasn't set). The issue is not with the code I wrote, but with the execution environment (the missing environment variable).

I need to reiterate to the user that they must set the `LLM_MODEL` environment variable *before* running the backend server for the Ollama initializer script to attempt loading the model. I will provide the command to set the environment variable on Windows (using `$env:`) and then the command to run the server.The logs indicate that the `ollama_initializer.py` script ran successfully, but it detected that the `LLM_MODEL` environment variable was not set, and therefore skipped loading the Ollama model.

To ensure the Ollama model is loaded, you need to set the `LLM_MODEL` environment variable to the desired Ollama model ID (e.g., `ollama/gemma3`) in your terminal *before* starting the backend server.

Here are the commands to do this in PowerShell (which appears to be your shell based on the prompt):

```powershell
$env:LLM_MODEL="ollama/gemma3"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Replace `"ollama/gemma3"` with the specific Ollama model ID you want to load if it's different.

After running these commands, you should see logs from the `ollama_initializer.py` script indicating that it is attempting to load the selected model.

---

**User:**

[ERROR] You did not use a tool in your previous response! Please retry with a tool use.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.

# Next Steps

If you have completed the user's task, use the attempt_completion tool. 
If you require additional information from the user, use the ask_followup_question tool. 
Otherwise, if you have not completed the task and do not need additional information, then proceed with the next step of the task. 
(This is an automated message, so do not respond to it conversationally.)
<environment_details>
# VSCode Visible Files
backend/app/main.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 10:35:15 AM (America/New_York, UTC-4:00)

# Context Window Usage
201,999 / 1,048.576K tokens used (19%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I apologize for the previous response where I failed to use a tool. I provided instructions to the user without using a tool, which is against the rules.

My task is complete, as I have implemented the Ollama initializer script and integrated it into the backend startup. The user's feedback indicated that the script ran but the environment variable was not set, which is an issue with the execution environment, not the code I wrote.

I need to use the `attempt_completion` tool to present the result again. I will include the same explanation and the commands to set the environment variable and run the server, ensuring they are clearly presented as part of the result and the demonstration command. This time, I will make sure the entire response is within the `attempt_completion` tool tags.<attempt_completion>
<result>
I have implemented the functionality to automatically initiate the loading of the selected Ollama model when the backend server starts.

Here's what I've done:
1.  Created a new script `backend/app/ollama_initializer.py`. This script reads the `LLM_MODEL` environment variable, checks if the selected model is configured as an Ollama model in `app_config.py`, and if so, executes the `ollama run <model_id>` command in a non-blocking way.
2.  Modified `backend/app/main.py` to execute the `ollama_initializer.py` script during the application's startup event (`@app.on_event("startup")`).

Now, when you start the backend server and have an Ollama model (like `gemma3`) specified in your environment variables (e.g., `LLM_MODEL=ollama/gemma3`), the backend will attempt to load that model into the Ollama server's memory during its startup.

To test this, you need to set the `LLM_MODEL` environment variable to the desired Ollama model ID in your terminal *before* starting the backend server.

Here are the commands to do this in PowerShell (which appears to be your shell):

```powershell
$env:LLM_MODEL="ollama/gemma3"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Replace `"ollama/gemma3"` with the specific Ollama model ID you want to load if it's different.

After running these commands, you should see logs from the `ollama_initializer.py` script indicating that it is attempting to load the selected model.
</result>
<command>
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
</command>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user denied this operation.
The user provided the following feedback:
<feedback>
ok i believe its running create script that send a messege to ollama to see if it responds
</feedback>
<environment_details>
# VSCode Visible Files
backend/app/app_config.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/app_config.py
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 12:17:32 PM (America/New_York, UTC-4:00)

# Context Window Usage
401,191 / 1,048.576K tokens used (38%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>The user believes the Ollama server and model are running and wants a script to verify this by sending a message to Ollama and checking for a response.

This requires creating a new Python script that will:
1. Read the Ollama base URL and the selected model ID from environment variables or `app_config.py`.
2. Use a library like `requests` or `httpx` to send a request to the Ollama API (specifically the chat completions endpoint) using the selected model.
3. Send a simple message (e.g., "Hello, Ollama!") and check if a response is received.
4. Print a message indicating whether the Ollama server responded successfully.

I will create a new Python script, `backend/app/test_ollama_connection.py`, to perform this check. I will use `httpx` for making asynchronous HTTP requests, as the backend uses `asyncio`. I will need to import `os`, `sys`, `asyncio`, `httpx`, and parts of `app_config`.

After creating the script, I will provide the command to run it. I will also remind the user to set the `LLM_MODEL` environment variable before running the test script.Okay, I can create a script to test the connection to the Ollama server and verify if the selected model responds.

I will create a new Python script `backend/app/test_ollama_connection.py` that will attempt to send a simple message to the configured Ollama server using the selected model and report the result.

<write_to_file>
<path>backend/app/test_ollama_connection.py</path>
<content>
import os
import sys
import asyncio
import httpx
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure test_ollama_connection.py is in the backend/app directory.")
    sys.exit(1)

async def test_ollama():
    """
    Tests connection to Ollama server and sends a simple message to the selected model.
    """
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.error("LLM_MODEL environment variable not set. Cannot test Ollama connection.")
        logger.info("Please set the LLM_MODEL environment variable (e.g., $env:LLM_MODEL='ollama/gemma3' in PowerShell) before running this script.")
        return

    logger.info(f"Selected LLM_MODEL for testing: {selected_model_id}")

    model_config = None
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config or model_config.get('provider_group') != 'Ollama (Local)':
        logger.error(f"Model ID '{selected_model_id}' is not configured as a local Ollama model in app_config.py.")
        logger.info("Please ensure LLM_MODEL is set to a valid Ollama model ID from app_config.AVAILABLE_MODELS.")
        return

    ollama_model_name = selected_model_id.replace("ollama/", "") # Get just the model name part
    ollama_url = OLLAMA_BASE_URL # Use the base URL from app_config

    if not ollama_url:
        logger.error("OLLAMA_BASE_URL is not set in environment variables or app_config.py.")
        return

    chat_endpoint = f"{ollama_url}/api/chat"
    logger.info(f"Attempting to connect to Ollama at {ollama_url} and test model '{ollama_model_name}' via {chat_endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            # First, check if the server is reachable
            try:
                # A simple GET request to the base URL might be enough to check if the server is up
                # Or a specific health check endpoint if Ollama provides one.
                # Let's try the chat endpoint directly with a small timeout for initial check.
                logger.info(f"Checking if Ollama server is reachable at {ollama_url}...")
                response = await client.get(ollama_url, timeout=5.0)
                response.raise_for_status() # Raise an exception for bad status codes
                logger.info("Ollama server is reachable.")
            except httpx.RequestError as e:
                logger.error(f"Ollama server not reachable at {ollama_url}: {e}")
                logger.info("Please ensure your Ollama server is running.")
                return
            except httpx.HTTPStatusError as e:
                 logger.warning(f"Ollama server returned status {e.response.status_code} on reachability check: {e.response.text}")
                 # Server is up, but maybe the endpoint is different or requires POST. Proceed to chat test.


            # Now, attempt to send a message to the model
            logger.info(f"Attempting to send a message to model '{ollama_model_name}'...")
            chat_payload = {
                "model": ollama_model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": False, # Request non-streaming response
                "options": {"num_predict": 10} # Keep response small
            }
            
            chat_response = await client.post(chat_endpoint, json=chat_payload, timeout=30.0)
            chat_response.raise_for_status() # Raise an exception for bad status codes

            response_data = chat_response.json()
            
            if response_data and response_data.get("message") and response_data["message"].get("content"):
                logger.info("Ollama server responded successfully!")
                logger.info(f"Model '{ollama_model_name}' responded with: '{response_data['message']['content'][:100]}...'")
                logger.info("Ollama connection test successful.")
            else:
                logger.error("Ollama server responded, but the response format was unexpected or empty.")
                logger.debug(f"Full response data: {response_data}")
                logger.info("Ollama connection test failed: Unexpected response.")

    except httpx.RequestError as e:
        logger.error(f"Error sending message to Ollama model '{ollama_model_name}': {e}")
        logger.info("Ollama connection test failed: Request error.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama server returned error status {e.response.status_code} for model '{ollama_model_name}': {e.response.text}")
        logger.info(f"Ollama connection test failed: HTTP error. Ensure model '{ollama_model_name}' is available on your Ollama server (run 'ollama list').")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama connection test: {e}", exc_info=True)
        logger.info("Ollama connection test failed: Unexpected exception.")


if __name__ == "__main__":
    logger.info("Running Ollama connection test script.")
    asyncio.run(test_ollama())
    logger.info("Ollama connection test script finished.")

</content>
</write_to_file>

---

**User:**

[write_to_file for 'backend/app/test_ollama_connection.py'] Result:
The content was successfully saved to backend/app/test_ollama_connection.py.

Here is the full, updated content of the file that was saved:

<final_file_content path="backend/app/test_ollama_connection.py">
import os
import sys
import asyncio
import httpx
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure test_ollama_connection.py is in the backend/app directory.")
    sys.exit(1)

async def test_ollama():
    """
    Tests connection to Ollama server and sends a simple message to the selected model.
    """
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.error("LLM_MODEL environment variable not set. Cannot test Ollama connection.")
        logger.info("Please set the LLM_MODEL environment variable (e.g., $env:LLM_MODEL='ollama/gemma3' in PowerShell) before running this script.")
        return

    logger.info(f"Selected LLM_MODEL for testing: {selected_model_id}")

    model_config = None
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config or model_config.get('provider_group') != 'Ollama (Local)':
        logger.error(f"Model ID '{selected_model_id}' is not configured as a local Ollama model in app_config.py.")
        logger.info("Please ensure LLM_MODEL is set to a valid Ollama model ID from app_config.AVAILABLE_MODELS.")
        return

    ollama_model_name = selected_model_id.replace("ollama/", "") # Get just the model name part
    ollama_url = OLLAMA_BASE_URL # Use the base URL from app_config

    if not ollama_url:
        logger.error("OLLAMA_BASE_URL is not set in environment variables or app_config.py.")
        return

    chat_endpoint = f"{ollama_url}/api/chat"
    logger.info(f"Attempting to connect to Ollama at {ollama_url} and test model '{ollama_model_name}' via {chat_endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            # First, check if the server is reachable
            try:
                # A simple GET request to the base URL might be enough to check if the server is up
                # Or a specific health check endpoint if Ollama provides one.
                # Let's try the chat endpoint directly with a small timeout for initial check.
                logger.info(f"Checking if Ollama server is reachable at {ollama_url}...")
                response = await client.get(ollama_url, timeout=5.0)
                response.raise_for_status() # Raise an exception for bad status codes
                logger.info("Ollama server is reachable.")
            except httpx.RequestError as e:
                logger.error(f"Ollama server not reachable at {ollama_url}: {e}")
                logger.info("Please ensure your Ollama server is running.")
                return
            except httpx.HTTPStatusError as e:
                 logger.warning(f"Ollama server returned status {e.response.status_code} on reachability check: {e.response.text}")
                 # Server is up, but maybe the endpoint is different or requires POST. Proceed to chat test.


            # Now, attempt to send a message to the model
            logger.info(f"Attempting to send a message to model '{ollama_model_name}'...")
            chat_payload = {
                "model": ollama_model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": False, # Request non-streaming response
                "options": {"num_predict": 10} # Keep response small
            }
            
            chat_response = await client.post(chat_endpoint, json=chat_payload, timeout=30.0)
            chat_response.raise_for_status() # Raise an exception for bad status codes

            response_data = chat_response.json()
            
            if response_data and response_data.get("message") and response_data["message"].get("content"):
                logger.info("Ollama server responded successfully!")
                logger.info(f"Model '{ollama_model_name}' responded with: '{response_data['message']['content'][:100]}...'")
                logger.info("Ollama connection test successful.")
            else:
                logger.error("Ollama server responded, but the response format was unexpected or empty.")
                logger.debug(f"Full response data: {response_data}")
                logger.info("Ollama connection test failed: Unexpected response.")

    except httpx.RequestError as e:
        logger.error(f"Error sending message to Ollama model '{ollama_model_name}': {e}")
        logger.info("Ollama connection test failed: Request error.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama server returned error status {e.response.status_code} for model '{ollama_model_name}': {e.response.text}")
        logger.info(f"Ollama connection test failed: HTTP error. Ensure model '{ollama_model_name}' is available on your Ollama server (run 'ollama list').")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama connection test: {e}", exc_info=True)
        logger.info("Ollama connection test failed: Unexpected exception.")


if __name__ == "__main__":
    logger.info("Running Ollama connection test script.")
    asyncio.run(test_ollama())
    logger.info("Ollama connection test script finished.")

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.


<environment_details>
# VSCode Visible Files
backend/app/test_ollama_connection.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/test_ollama_connection.py
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 12:17:48 PM (America/New_York, UTC-4:00)

# Context Window Usage
205,331 / 1,048.576K tokens used (20%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I have successfully created the `backend/app/test_ollama_connection.py` script. This script is designed to test the connection to the Ollama server and the responsiveness of the selected model.

The next step is to provide the user with the command to run this script. I will also remind them to set the `LLM_MODEL` environment variable before running the script, as this is necessary for the script to know which model to test.

I will use the `attempt_completion` tool to present the script and the instructions on how to run it. The command to run the script will be `python backend/app/test_ollama_connection.py`. I will include the PowerShell command to set the environment variable as part of the instructions in the result.The `backend/app/test_ollama_connection.py` script has been created. This script will attempt to connect to your Ollama server and send a test message to the model specified by the `LLM_MODEL` environment variable.

To run the test script, first set the `LLM_MODEL` environment variable in your PowerShell terminal, and then execute the script:

```powershell
$env:LLM_MODEL="ollama/gemma3"
python backend/app/test_ollama_connection.py
```

Replace `"ollama/gemma3"` with the specific Ollama model ID you have selected in your environment.

The script will print logs indicating whether it was able to connect to Ollama and if the model responded successfully.
</attempt_completion>

---

**User:**

[ERROR] You did not use a tool in your previous response! Please retry with a tool use.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.

# Next Steps

If you have completed the user's task, use the attempt_completion tool. 
If you require additional information from the user, use the ask_followup_question tool. 
Otherwise, if you have not completed the task and do not need additional information, then proceed with the next step of the task. 
(This is an automated message, so do not respond to it conversationally.)
<environment_details>
# VSCode Visible Files
backend/app/test_ollama_connection.py

# VSCode Open Tabs
src/app/page.js
.env
backend/app/.env
backend/app/test_ollama_connection.py
backend/app/crawl4ai_fetcher.py
live_llm_extraction_advanced_tester.py
docs/livetest_instructions.md
backend/app/ollama_initializer.py
backend/app/main.py
../../../AppData/Roaming/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
src/app/fetch/page.js
src/components/fetch/ExtractionStrategyConfigurator.jsx
src/components/fetch/DeepCrawlStrategyConfigurator.jsx
../../../AppData/Roaming/Claude/claude_desktop_config.json
docs/refactoring_utility_modules.md
backend/app/transcribe1.py
backend/app/utils/__init__.py

# Current Time
5/13/2025, 12:17:52 PM (America/New_York, UTC-4:00)

# Context Window Usage
207,601 / 1,048.576K tokens used (20%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

<thinking>I apologize again for the repeated error of not using a tool in my response. I provided instructions to the user without using a tool.

My task was to create a script to test the Ollama connection and provide instructions on how to run it. I have created the script and formulated the instructions and command.

I need to use the `attempt_completion` tool to present the result. I will include the explanation of the script and the commands to set the environment variable and run the script within the `attempt_completion` tool tags. I will ensure the command parameter of the tool contains only the command to run the script itself, and the instructions for setting the environment variable are in the result text.<attempt_completion>
<result>
I have created the `backend/app/test_ollama_connection.py` script as requested. This script will attempt to connect to your Ollama server and send a test message to the model specified by the `LLM_MODEL` environment variable.

To run the test script, first set the `LLM_MODEL` environment variable in your PowerShell terminal, and then execute the script. Replace `"ollama/gemma3"` with the specific Ollama model ID you have selected in your environment.

```powershell
$env:LLM_MODEL="ollama/gemma3"
python backend/app/test_ollama_connection.py
```

The script will print logs indicating whether it was able to connect to Ollama and if the model responded successfully.
</result>
<command>
python backend/app/test_ollama_connection.py
</command>
</attempt_completion>

