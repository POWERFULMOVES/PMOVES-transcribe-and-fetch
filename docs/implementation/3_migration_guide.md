# PMOVES Migration Guide: Transitioning to Agent-Based Architecture

This guide outlines the step-by-step process for migrating existing PMOVES functionality to the new agent-based architecture.

## 1. Preparation Phase

### 1.1 Environment Setup
```bash
# Create a new virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install required packages
pip install openai single-file-agents fastapi uvicorn

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort mypy
```

### 1.2 Project Structure Update
```
pmoves/
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── transcription.py
│   ├── search.py
│   └── content_fetch.py
├── services/
│   ├── __init__.py
│   ├── transcription.py
│   ├── vector_search.py
│   └── content_fetch.py
├── utils/
│   ├── __init__.py
│   ├── monitoring.py
│   └── processors.py
└── tests/
    ├── __init__.py
    ├── test_agents/
    └── test_services/
```

## 2. Migration Steps

### 2.1 Service Layer Migration

1. Identify existing services:
```python
# Before: transcribe1.py
def transcribe_video(url: str) -> Dict[str, Any]:
    # Direct implementation
    pass

# After: services/transcription.py
class TranscriptionService:
    def __init__(self):
        self.processors = {
            'gpu': GPUTranscriber(),
            'groq': GroqTranscriber()
        }
    
    async def transcribe(
        self,
        source: str,
        processor: str = 'gpu',
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        processor_instance = self.processors[processor]
        return await processor_instance.transcribe(source, options)
```

2. Migrate vector search:
```python
# Before: vector_search.py
def search_vectors(query: str) -> List[Dict[str, Any]]:
    # Direct implementation
    pass

# After: services/vector_search.py
class VectorSearchService:
    def __init__(self):
        self.embedding_model = "text-embedding-3-small"
        self.vector_store = VectorStore()
    
    async def search(
        self,
        query: str,
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        embedding = await self.generate_embedding(query)
        return await self.vector_store.search(embedding, options)
```

### 2.2 Agent Implementation

1. Create base agent:
```python
# agents/base.py
from typing import Dict, Any, List
from single_file_agents import Agent as BaseAgent

class PMOVESBaseAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        capabilities: List[str],
        services: Dict[str, Any]
    ):
        super().__init__(name=name, capabilities=capabilities)
        self.services = services
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize agent tools"""
        raise NotImplementedError
```

2. Implement specific agents:
```python
# agents/transcription.py
class TranscriptionAgent(PMOVESBaseAgent):
    def __init__(self):
        super().__init__(
            name="transcription_agent",
            capabilities=["transcription"],
            services={"transcription": TranscriptionService()}
        )
    
    def _initialize_tools(self) -> Dict[str, Any]:
        return {
            'transcribe': Tool(
                name='transcribe',
                function=self._transcribe,
                description='Transcribe media content'
            )
        }
    
    async def _transcribe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.services['transcription'].transcribe(
            source=data['source'],
            processor=data.get('processor', 'gpu'),
            options=data.get('options')
        )
```

### 2.3 API Endpoint Migration

1. Update FastAPI endpoints:
```python
# Before
@app.post("/transcribe")
async def transcribe_endpoint(url: str):
    return await transcribe_video(url)

# After
@app.post("/transcribe")
async def transcribe_endpoint(request: TranscriptionRequest):
    agent = TranscriptionAgent()
    return await agent.process_media(
        source=request.url,
        options=request.options
    )
```

2. Add agent management:
```python
# main.py
from fastapi import FastAPI
from .agents import AgentManager

app = FastAPI()
agent_manager = AgentManager()

@app.on_event("startup")
async def startup_event():
    await agent_manager.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    await agent_manager.cleanup()
```

## 3. Testing Migration

### 3.1 Unit Tests
```python
# tests/test_agents/test_transcription.py
import pytest
from pmoves.agents import TranscriptionAgent

@pytest.mark.asyncio
async def test_transcription_agent():
    agent = TranscriptionAgent()
    result = await agent.process_media(
        source="test_video.mp4",
        options={'language': 'en'}
    )
    assert result['transcription']
    assert result['metadata']
```

### 3.2 Integration Tests
```python
# tests/test_integration/test_workflows.py
import pytest
from pmoves.agents import TranscriptionAgent, SearchAgent

@pytest.mark.asyncio
async def test_transcribe_and_search_workflow():
    # 1. Transcribe
    trans_agent = TranscriptionAgent()
    trans_result = await trans_agent.process_media(
        source="test_video.mp4"
    )
    
    # 2. Search
    search_agent = SearchAgent()
    search_result = await search_agent.search(
        query="test query",
        options={'limit': 5}
    )
    
    assert trans_result['transcription']
    assert search_result['results']
```

## 4. Monitoring Migration

### 4.1 Add Agent Monitoring
```python
# utils/monitoring.py
class AgentMonitor:
    def __init__(self):
        self.metrics = {}
    
    async def track_agent(
        self,
        agent_name: str,
        operation: str,
        duration: float,
        status: str
    ):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = {
                'operations': {},
                'total_calls': 0,
                'errors': 0
            }
        
        self.metrics[agent_name]['total_calls'] += 1
        if status == 'error':
            self.metrics[agent_name]['errors'] += 1
```

### 4.2 Implement Monitoring Middleware
```python
# middleware/monitoring.py
from fastapi import Request
from .utils import AgentMonitor

async def agent_monitoring_middleware(request: Request, call_next):
    monitor = AgentMonitor()
    
    try:
        response = await call_next(request)
        await monitor.track_request(request, response)
        return response
    except Exception as e:
        await monitor.track_error(request, e)
        raise
```

## 5. Gradual Migration Strategy

1. Phase 1: Core Services
- Migrate transcription service
- Migrate vector search service
- Add basic agent implementations

2. Phase 2: API Layer
- Update endpoints to use agents
- Implement monitoring
- Add error handling

3. Phase 3: Advanced Features
- Implement multi-agent workflows
- Add content analysis
- Enable real-time monitoring

4. Phase 4: Testing & Validation
- Update test suite
- Validate performance
- Monitor error rates

## 6. Rollback Plan

1. Maintain Legacy Code:
```python
# Keep legacy implementations with new names
async def legacy_transcribe_video(url: str) -> Dict[str, Any]:
    # Original implementation
    pass

# Add feature flag for rollback
USE_AGENTS = os.getenv("USE_AGENTS", "true").lower() == "true"

@app.post("/transcribe")
async def transcribe_endpoint(request: TranscriptionRequest):
    if USE_AGENTS:
        agent = TranscriptionAgent()
        return await agent.process_media(
            source=request.url,
            options=request.options
        )
    else:
        return await legacy_transcribe_video(request.url)
```

2. Monitoring During Migration:
```python
# Add migration metrics
class MigrationMonitor:
    def __init__(self):
        self.metrics = {
            'legacy_calls': 0,
            'agent_calls': 0,
            'errors': {
                'legacy': 0,
                'agent': 0
            }
        }
    
    async def track_call(self, system: str, success: bool):
        if system == 'legacy':
            self.metrics['legacy_calls'] += 1
        else:
            self.metrics['agent_calls'] += 1
        
        if not success:
            self.metrics['errors'][system] += 1
```

## 7. Validation Checklist

- [ ] All core services migrated to agent-based architecture
- [ ] API endpoints updated to use agents
- [ ] Monitoring implemented for all agents
- [ ] Test coverage maintained or improved
- [ ] Performance metrics within acceptable ranges
- [ ] Error rates monitored and acceptable
- [ ] Documentation updated
- [ ] Team trained on new architecture
- [ ] Rollback plan tested and verified 