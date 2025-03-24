# PMOVES Agent Integration Specification

## OpenAI Agents SDK Integration

### 1. Setup and Configuration
```python
from agent_sdk import Agent, WebSearchTool, FileRetrievalTool
from typing import List, Dict, Any

class PMOVESAgentManager:
    """Manages OpenAI Agents for PMOVES"""
    
    def __init__(self):
        # Initialize core tools
        self.tools = {
            'web_search': WebSearchTool(api_key=os.getenv("OPENAI_API_KEY")),
            'file_retrieval': FileRetrievalTool(),
            'transcription': TranscriptionTool(),
            'vector_search': VectorSearchTool(),
            'content_fetch': ContentFetchTool()
        }
        
        # Initialize agent with tools
        self.agent = Agent(tools=list(self.tools.values()))

### 2. Custom PMOVES Tools
```python
class TranscriptionTool:
    """Tool for handling transcription tasks"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Handle both GPU and Groq transcription
        processor = input_data.get('processor', 'gpu')
        return await transcription_service.transcribe(
            source=input_data['source'],
            processor=processor
        )

class VectorSearchTool:
    """Tool for vector search operations"""
    
    async def execute(self, query: str) -> List[Dict[str, Any]]:
        return await vector_service.search(
            query=query,
            options=SearchOptions(limit=10)
        )

class ContentFetchTool:
    """Tool for fetching and processing web content"""
    
    async def execute(self, url: str) -> Dict[str, Any]:
        return await content_service.fetch_content(url)
```

### 3. Agent Task Definitions
```python
class PMOVESTask:
    """Defines tasks that agents can perform"""
    
    def __init__(self, task_type: str, parameters: Dict[str, Any]):
        self.type = task_type
        self.parameters = parameters
        self.tools_required = self._determine_tools()
    
    def _determine_tools(self) -> List[str]:
        """Determine required tools based on task type"""
        tool_mappings = {
            'transcribe': ['transcription'],
            'search': ['web_search', 'vector_search'],
            'fetch_content': ['content_fetch', 'web_search'],
            'analyze': ['vector_search', 'file_retrieval']
        }
        return tool_mappings.get(self.type, [])
```

## Single-File Agents Integration

### 1. Agent Definition
```python
from single_file_agents import Agent, Tool, Memory

class PMOVESAgent(Agent):
    """PMOVES implementation of single-file agent"""
    
    def __init__(self, name: str, capabilities: List[str]):
        super().__init__(
            name=name,
            capabilities=capabilities,
            memory=Memory()
        )
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        return {
            'transcribe': Tool(
                name='transcribe',
                function=self._handle_transcription,
                description='Transcribe audio/video content'
            ),
            'search': Tool(
                name='search',
                function=self._handle_search,
                description='Search content using vector similarity'
            ),
            'fetch': Tool(
                name='fetch',
                function=self._handle_fetch,
                description='Fetch and process web content'
            )
        }
```

### 2. Agent Workflows
```python
class TranscriptionWorkflow:
    """Workflow for transcription tasks"""
    
    async def execute(self, source: str) -> Dict[str, Any]:
        # 1. Analyze source type
        source_type = await self.agent.use_tool(
            'analyze_source',
            {'source': source}
        )
        
        # 2. Choose processor
        processor = 'groq' if source_type == 'long_form' else 'gpu'
        
        # 3. Transcribe content
        result = await self.agent.use_tool(
            'transcribe',
            {
                'source': source,
                'processor': processor
            }
        )
        
        # 4. Store result
        await self.agent.use_tool(
            'store_result',
            {
                'content': result,
                'metadata': {'source_type': source_type}
            }
        )
        
        return result

class SearchWorkflow:
    """Workflow for search tasks"""
    
    async def execute(self, query: str) -> Dict[str, Any]:
        # 1. Generate embedding
        embedding = await self.agent.use_tool(
            'generate_embedding',
            {'text': query}
        )
        
        # 2. Perform vector search
        vector_results = await self.agent.use_tool(
            'vector_search',
            {
                'embedding': embedding,
                'limit': 10
            }
        )
        
        # 3. Enhance results
        enhanced_results = await self.agent.use_tool(
            'enhance_results',
            {'results': vector_results}
        )
        
        return enhanced_results
```

### 3. Agent Communication
```python
class AgentCommunication:
    """Handles inter-agent communication"""
    
    async def delegate_task(
        self,
        task: PMOVESTask,
        source_agent: PMOVESAgent,
        target_agent: PMOVESAgent
    ) -> Dict[str, Any]:
        # Create handoff message
        handoff = {
            'task': task.type,
            'parameters': task.parameters,
            'context': source_agent.get_context(),
            'requirements': task.tools_required
        }
        
        # Execute handoff
        result = await target_agent.process(handoff)
        
        # Update source agent's context
        source_agent.update_context(result)
        
        return result
```

## Integration Examples

### 1. Transcription with Agent
```python
# Initialize agent
agent = PMOVESAgent('transcriber', ['transcription', 'analysis'])

# Create workflow
workflow = TranscriptionWorkflow(agent)

# Execute transcription
result = await workflow.execute('https://example.com/video.mp4')
```

### 2. Enhanced Search
```python
# Initialize agent
agent = PMOVESAgent('searcher', ['search', 'analysis'])

# Create workflow
workflow = SearchWorkflow(agent)

# Execute search
results = await workflow.execute('quantum computing')
```

### 3. Multi-Agent Task
```python
# Initialize agents
transcriber = PMOVESAgent('transcriber', ['transcription'])
searcher = PMOVESAgent('searcher', ['search'])
analyzer = PMOVESAgent('analyzer', ['analysis'])

# Create task
task = PMOVESTask(
    task_type='analyze_transcript',
    parameters={
        'source': 'video.mp4',
        'search_context': 'relevant_topics'
    }
)

# Execute with multiple agents
comm = AgentCommunication()

# 1. Transcribe
transcript = await comm.delegate_task(task, analyzer, transcriber)

# 2. Search for context
context = await comm.delegate_task(task, analyzer, searcher)

# 3. Analyze
result = await analyzer.process({
    'transcript': transcript,
    'context': context
})
``` 