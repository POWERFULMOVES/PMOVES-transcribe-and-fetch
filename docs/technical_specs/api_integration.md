# PMOVES API Integration Guide

## Service APIs

### 1. Transcription Service API
```python
class TranscriptionAPI:
    """
    Handles transcription requests with both local and cloud processing.
    Extensible for new transcription providers.
    """
    
    async def transcribe(
        self,
        source: Union[str, bytes, Path],
        options: TranscriptionOptions,
        processor: Literal["gpu", "groq"] = "gpu"
    ) -> TranscriptionResult:
        """
        Transcribe audio/video content.
        
        Args:
            source: File path, URL, or bytes
            options: Transcription configuration
            processor: Processing engine choice
            
        Returns:
            TranscriptionResult with segments and metadata
        """
        pass

    async def add_processor(
        self,
        processor_name: str,
        processor_impl: BaseProcessor
    ) -> None:
        """
        Add new transcription processor.
        Allows extension with new AI models/services.
        """
        pass
```

### 2. Content Service API
```python
class ContentAPI:
    """
    Handles content fetching and processing.
    Extensible for new content types and processors.
    """
    
    async def fetch_content(
        self,
        url: str,
        options: FetchOptions,
        processor: str = "jinai"
    ) -> ContentResult:
        """
        Fetch and process web content.
        
        Args:
            url: Target URL
            options: Fetch configuration
            processor: Content processor choice
            
        Returns:
            Processed content with metadata
        """
        pass

    async def register_processor(
        self,
        content_type: str,
        processor: BaseContentProcessor
    ) -> None:
        """
        Register new content processor.
        Enables support for new content types.
        """
        pass
```

### 3. Vector Service API
```python
class VectorAPI:
    """
    Handles vector operations and search.
    Extensible for new embedding models and search methods.
    """
    
    async def generate_embedding(
        self,
        content: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Generate content embedding.
        
        Args:
            content: Text to embed
            model: Embedding model choice
            
        Returns:
            Vector embedding
        """
        pass

    async def search(
        self,
        query: str,
        options: SearchOptions,
        enhancers: List[SearchEnhancer] = None
    ) -> SearchResults:
        """
        Perform vector search with optional enhancements.
        
        Args:
            query: Search query
            options: Search configuration
            enhancers: Optional search enhancers
            
        Returns:
            Enhanced search results
        """
        pass
```

## Agent Integration APIs

### 1. Agent Registry API
```python
class AgentRegistryAPI:
    """
    Manages AI agent registration and discovery.
    """
    
    async def register_agent(
        self,
        agent: BaseAgent,
        capabilities: List[str]
    ) -> str:
        """
        Register new AI agent.
        
        Args:
            agent: Agent implementation
            capabilities: Agent capabilities
            
        Returns:
            Agent ID
        """
        pass

    async def find_agents(
        self,
        capability: str,
        constraints: Dict[str, Any] = None
    ) -> List[BaseAgent]:
        """
        Find agents with specific capabilities.
        
        Args:
            capability: Required capability
            constraints: Optional constraints
            
        Returns:
            List of matching agents
        """
        pass
```

### 2. Agent Orchestration API
```python
class AgentOrchestratorAPI:
    """
    Coordinates AI agent activities.
    """
    
    async def create_pipeline(
        self,
        task: Task,
        agents: List[BaseAgent]
    ) -> Pipeline:
        """
        Create agent processing pipeline.
        
        Args:
            task: Task description
            agents: Agents to include
            
        Returns:
            Configured pipeline
        """
        pass

    async def execute_pipeline(
        self,
        pipeline: Pipeline,
        input_data: Dict[str, Any]
    ) -> PipelineResult:
        """
        Execute agent pipeline.
        
        Args:
            pipeline: Agent pipeline
            input_data: Pipeline input
            
        Returns:
            Pipeline execution results
        """
        pass
```

## Event Stream APIs

### 1. SSE Monitor API
```python
class SSEMonitorAPI:
    """
    Monitors SSE connections and events.
    """
    
    async def track_connection(
        self,
        connection_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Track new SSE connection."""
        pass

    async def log_event(
        self,
        connection_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Log SSE event."""
        pass
```

### 2. Event Processing API
```python
class EventProcessorAPI:
    """
    Processes and routes SSE events.
    """
    
    async def register_handler(
        self,
        event_type: str,
        handler: EventHandler
    ) -> None:
        """Register event handler."""
        pass

    async def process_event(
        self,
        event: Event
    ) -> ProcessingResult:
        """Process SSE event."""
        pass
```

## Storage APIs

### 1. Supabase Integration API
```python
class SupabaseAPI:
    """
    Manages Supabase operations.
    """
    
    async def store_vector(
        self,
        table: str,
        content: Dict[str, Any],
        embedding: List[float]
    ) -> str:
        """Store content with embedding."""
        pass

    async def search_vectors(
        self,
        table: str,
        query_embedding: List[float],
        options: SearchOptions
    ) -> List[Dict[str, Any]]:
        """Search vector store."""
        pass
```

### 2. File Storage API
```python
class FileStorageAPI:
    """
    Manages file operations.
    """
    
    async def store_file(
        self,
        file_data: Union[bytes, str],
        metadata: Dict[str, Any]
    ) -> str:
        """Store file with metadata."""
        pass

    async def retrieve_file(
        self,
        file_id: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Retrieve file and metadata."""
        pass
```

## Extension Points

### 1. Custom Agent Implementation
```python
class CustomAgent(BaseAgent):
    """
    Template for custom agent implementation.
    """
    
    async def initialize(self):
        """Setup agent resources."""
        self.capabilities = ['custom_capability']
        self.state = {'initialized': True}

    async def process(self, input_data: dict) -> dict:
        """Process input data."""
        # Custom processing logic
        return {'result': 'processed'}

    async def cleanup(self):
        """Cleanup resources."""
        self.state = {'initialized': False}
```

### 2. Custom Search Enhancer
```python
class CustomSearchEnhancer(SearchEnhancer):
    """
    Template for custom search enhancement.
    """
    
    async def enhance_query(self, query: str) -> str:
        """Enhance search query."""
        # Query enhancement logic
        return enhanced_query

    async def enhance_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance search results."""
        # Results enhancement logic
        return enhanced_results
```

## Usage Examples

### 1. Agent Integration
```python
# Register custom agent
agent = CustomAgent()
agent_id = await agent_registry.register_agent(
    agent,
    capabilities=['custom_capability']
)

# Create and execute pipeline
pipeline = await orchestrator.create_pipeline(
    task=Task(type='process_content'),
    agents=[agent]
)

result = await orchestrator.execute_pipeline(
    pipeline=pipeline,
    input_data={'content': 'test'}
)
```

### 2. Search Enhancement
```python
# Create custom enhancer
enhancer = CustomSearchEnhancer()

# Perform enhanced search
results = await vector_api.search(
    query='test query',
    options=SearchOptions(limit=10),
    enhancers=[enhancer]
)
``` 