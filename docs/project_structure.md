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
│   │   ├── vector-search/ # Vector search interface
│   │   ├── upserter/     # Content upserting interface
│   │   └── api/          # API route handlers
│   ├── components/        # Reusable React components
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
   - Real-time search results
   - Parameter adjustment
   - Result visualization

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