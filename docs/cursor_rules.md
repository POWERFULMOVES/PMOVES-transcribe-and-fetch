# Cursor IDE Rules and Best Practices

## Code Organization

### File Structure
- Keep files focused and single-purpose
- Use clear, descriptive filenames
- Group related functionality in directories
- Maximum file length: 2000 lines (split if longer)

### Code Sections
```python
# 1. Imports
from typing import List, Dict
import os

# 2. Constants and Configuration
MAX_RESULTS = 100
DEFAULT_THRESHOLD = 0.75

# 3. Type Definitions
class SearchResult:
    """Document your types"""
    pass

# 4. Helper Functions
def process_data():
    """Document your functions"""
    pass

# 5. Main Logic
def main():
    pass
```

## Documentation Standards

### Function Documentation
```python
def search_content(
    query: str,
    threshold: float = 0.75,
    max_results: int = 10
) -> List[Dict]:
    """
    Search content using vector similarity.

    Args:
        query: The search query string
        threshold: Minimum similarity threshold (0-1)
        max_results: Maximum number of results to return

    Returns:
        List of dictionaries containing search results
        
    Raises:
        ValueError: If threshold is not between 0 and 1
    """
    pass
```

### Class Documentation
```python
class VectorSearcher:
    """
    Handles vector-based semantic search operations.
    
    Attributes:
        client: Supabase client instance
        model: OpenAI/Groq model name
        
    Methods:
        search: Perform vector search
        analyze: Analyze search results
    """
    pass
```

## Error Handling

### Backend Error Handling
```python
try:
    result = process_data()
except ValueError as e:
    logger.error(f"Invalid input: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Frontend Error Handling
```javascript
try {
  const result = await searchContent(query);
  setResults(result);
} catch (error) {
  console.error('Search error:', error);
  setError(error.message);
  // Show user-friendly error message
  toast.error('Search failed. Please try again.');
}
```

## Async/Await Usage

### Backend Async
```python
async def search_endpoint(query: str):
    try:
        # Use async for I/O operations
        embedding = await generate_embedding(query)
        results = await search_database(embedding)
        return results
    except Exception as e:
        handle_error(e)
```

### Frontend Async
```javascript
async function handleSearch() {
  setLoading(true);
  try {
    const results = await searchAPI(query);
    setResults(results);
  } finally {
    setLoading(false);
  }
}
```

## State Management

### React State Guidelines
```javascript
// 1. Use appropriate hooks
const [query, setQuery] = useState('');
const [results, setResults] = useState([]);

// 2. Use reducers for complex state
const [state, dispatch] = useReducer(searchReducer, initialState);

// 3. Use context for shared state
const SearchContext = createContext();
```

## SSE Implementation

### Backend SSE
```python
async def event_generator():
    """Generate SSE events with proper formatting."""
    try:
        # 1. Start message
        yield f"data: {json.dumps({'type': 'start'})}\n\n"
        
        # 2. Progress updates
        yield f"data: {json.dumps({'type': 'progress'})}\n\n"
        
        # 3. Results
        yield f"data: {json.dumps({'type': 'results'})}\n\n"
        
        # 4. Completion
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error'})}\n\n"
```

### Frontend SSE
```javascript
function setupSSE() {
  // 1. Create connection
  const eventSource = new EventSource(url);
  
  // 2. Handle messages
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleEventType(data);
  };
  
  // 3. Handle errors
  eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
  };
  
  // 4. Cleanup
  return () => eventSource.close();
}
```

## Performance Considerations

### Backend Performance
1. Use async operations for I/O
2. Implement proper indexing
3. Cache frequently accessed data
4. Use connection pooling
5. Implement rate limiting

### Frontend Performance
1. Implement debouncing for search
2. Use virtual scrolling for large lists
3. Optimize bundle size
4. Implement proper cleanup
5. Use memoization where appropriate

## Testing Guidelines

### Backend Tests
```python
@pytest.mark.asyncio
async def test_search():
    # 1. Arrange
    query = "test query"
    
    # 2. Act
    results = await search(query)
    
    # 3. Assert
    assert len(results) > 0
    assert all(r.score >= 0.7 for r in results)
```

### Frontend Tests
```javascript
describe('SearchComponent', () => {
  it('should handle search correctly', async () => {
    // 1. Render
    render(<SearchComponent />);
    
    // 2. Interact
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'test' },
    });
    
    // 3. Assert
    await waitFor(() => {
      expect(screen.getByText('Results')).toBeInTheDocument();
    });
  });
});
```

## Git Workflow

### Commit Guidelines
1. Use descriptive commit messages
2. Reference issue numbers
3. Keep commits focused
4. Use conventional commit format

### Branch Strategy
1. main: Production code
2. develop: Development code
3. feature/*: New features
4. fix/*: Bug fixes
5. release/*: Release preparation

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
``` 