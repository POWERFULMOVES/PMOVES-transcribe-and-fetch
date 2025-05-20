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

3. **Centralized LLM Management**:
   - A new system for managing LLM (Large Language Model) interactions has been implemented, centered around a LiteLLM proxy.
   - **LiteLLM Proxy:** Acts as a unified gateway to various LLM providers (OpenAI, Groq, Google, Ollama, etc.). It handles API key management for these providers and routes requests accordingly.
   - **`LLMRegistryService` (`backend/app/utils/llm_registry_service.py`):** This backend service queries the LiteLLM proxy to discover available models and their capabilities.
   - **Backend Integration:** Services like `crawl4ai_fetcher.py` (for the `/fetch-content` endpoint) and direct LLM API routes (`/api/v1/llm/*`) now utilize this system. They obtain model information from the registry and send LLM requests to the LiteLLM proxy.
   - **Configuration:** Detailed information on configuring providers in the LiteLLM proxy and how the backend interacts with this system can be found in `docs/llm_configuration.md`.
   - **`crawl4ai` Usage:** For specifics on how `crawl4ai` uses this LLM system when invoked via the `/fetch-content` endpoint, refer to `docs/crawl4ai/docs/usage_with_backend.md`.

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