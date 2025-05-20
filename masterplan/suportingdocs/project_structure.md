# PMOVES Project Structure and Guidelines

## Project Overview
PMOVES is a transcription and search platform that combines vector search capabilities with OpenAI and Groq integrations for advanced content analysis.

## Directory Structure

```
PMOVES-transcribe-and-fetch/
├── backend/                  # Backend FastAPI application
│   ├── app/
│   │   ├── main.py          # Main FastAPI application entry point
│   │   ├── psearchworking.py # Core vector search implementation
│   │   ├── pmoves_upserter.py # Content upserter functionality
│   │   ├── transcribe1.py   # Transcription service
│   │   ├── crawl4ai_fetcher.py # Crawler integration for /fetch-content
│   │   ├── config/          # Configuration modules
│   │   ├── db/             # Database related code
│   │   ├── monitoring/     # SSE and system monitoring
│   │   ├── routes/         # API route handlers (including /api/v1/llm/*)
│   │   └── utils/
│   │       └── llm_registry_service.py # Service for LLM model discovery
│   └── .env               # Environment variables for backend AND proxy
│
├── docs/
│   ├── llm_configuration.md # Guide for setting up LiteLLM proxy & backend LLM integration
│   ├── livetest_instructions.md # Instructions for running live tests
│   ├── api_llm_endpoints.md   # Documentation for direct LLM API endpoints
│   ├── project_overview.md
│   ├── project_structure.md
│   └── crawl4ai/
│       └── docs/
│           └── usage_with_backend.md # How crawl4ai uses the LLM system
│
├── frontend/                 # Frontend Next.js application (structure illustrative)
│   ├── src/
│   │   ├── app/
│   │   │   ├── vector-search/ 
│   │   │   ├── upserter/     
│   │   │   └── api/
│   │   ├── components/
│   │   │   └── search/
│   │   └── lib/
│   └── ...
│
├── litellm_proxy_config/     # Configuration for the LiteLLM proxy
│   └── config.yaml        # LiteLLM proxy model and provider settings
│
├── PMOVES Supabase/          # Supabase database setup (structure illustrative)
│   └── supabasedocs/
│
├── docker-compose.backend.yml      # Docker Compose for the backend service
├── docker-compose.litellm-proxy.yml # Docker Compose for the LiteLLM proxy service
├── pyproject.toml                  # Python project metadata and dependencies
├── README.md                       # Main project README
└── .env.example                    # Example environment file (usually in backend/app/)
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