# PMOVES Agent Implementation Templates

## 1. Transcription Agent

```python
from typing import Dict, Any, List
from single_file_agents import Agent, Tool, Memory
from .utils import validate_source, process_metadata

class TranscriptionAgent(Agent):
    """Agent for handling transcription operations"""
    
    def __init__(self):
        super().__init__(
            name="transcription_agent",
            capabilities=["transcription", "audio_processing", "metadata_extraction"],
            memory=Memory()
        )
        self.supported_formats = ["mp4", "mp3", "wav", "avi", "mkv"]
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        return {
            'validate_source': Tool(
                name='validate_source',
                function=self._validate_source,
                description='Validate media source format and accessibility'
            ),
            'process_audio': Tool(
                name='process_audio',
                function=self._process_audio,
                description='Process and optimize audio for transcription'
            ),
            'transcribe': Tool(
                name='transcribe',
                function=self._transcribe,
                description='Perform transcription using GPU or Groq'
            ),
            'extract_metadata': Tool(
                name='extract_metadata',
                function=self._extract_metadata,
                description='Extract metadata from transcription'
            )
        }
    
    async def _validate_source(self, source: str) -> Dict[str, Any]:
        """Validate media source"""
        return await validate_source(source, self.supported_formats)
    
    async def _process_audio(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio for optimal transcription"""
        from .audio_processor import optimize_audio
        return await optimize_audio(source['path'])
    
    async def _transcribe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform transcription"""
        processor = 'groq' if data.get('duration', 0) > 600 else 'gpu'
        return await self.transcription_service.transcribe(
            audio=data['processed_audio'],
            processor=processor,
            options={
                'language': data.get('language', 'en'),
                'speaker_diarization': data.get('diarization', True),
                'timestamps': True
            }
        )
    
    async def _extract_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and process metadata"""
        return await process_metadata(result)
    
    async def process_media(self, source: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            # 1. Validate source
            validation = await self.use_tool('validate_source', source)
            if not validation['valid']:
                raise ValueError(f"Invalid source: {validation['error']}")
            
            # 2. Process audio
            processed = await self.use_tool('process_audio', validation)
            
            # 3. Transcribe
            transcription = await self.use_tool('transcribe', {
                **processed,
                **(options or {})
            })
            
            # 4. Extract metadata
            metadata = await self.use_tool('extract_metadata', transcription)
            
            return {
                'transcription': transcription,
                'metadata': metadata,
                'source': source,
                'processor_used': transcription['processor']
            }
            
        except Exception as e:
            self.memory.add_error(str(e))
            raise
```

## 2. Search Agent

```python
class SearchAgent(Agent):
    """Agent for handling vector and hybrid search operations"""
    
    def __init__(self):
        super().__init__(
            name="search_agent",
            capabilities=["vector_search", "keyword_search", "result_analysis"],
            memory=Memory()
        )
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        return {
            'analyze_query': Tool(
                name='analyze_query',
                function=self._analyze_query,
                description='Analyze and optimize search query'
            ),
            'generate_embedding': Tool(
                name='generate_embedding',
                function=self._generate_embedding,
                description='Generate vector embedding for query'
            ),
            'vector_search': Tool(
                name='vector_search',
                function=self._vector_search,
                description='Perform vector similarity search'
            ),
            'keyword_search': Tool(
                name='keyword_search',
                function=self._keyword_search,
                description='Perform keyword-based search'
            ),
            'combine_results': Tool(
                name='combine_results',
                function=self._combine_results,
                description='Combine and rank search results'
            )
        }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze and optimize search query"""
        return {
            'original_query': query,
            'optimized_query': await self.query_optimizer.optimize(query),
            'search_type': await self.query_analyzer.determine_search_type(query)
        }
    
    async def _generate_embedding(self, query: str) -> Dict[str, Any]:
        """Generate vector embedding"""
        return {
            'embedding': await self.embedding_service.generate(query),
            'model_used': 'text-embedding-3-small'
        }
    
    async def _vector_search(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform vector search"""
        return await self.vector_service.search(
            embedding=data['embedding'],
            options={
                'limit': data.get('limit', 10),
                'threshold': data.get('threshold', 0.7)
            }
        )
    
    async def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform keyword search"""
        return await self.search_service.keyword_search(
            query=query,
            options={
                'limit': 10,
                'fuzzy_match': True
            }
        )
    
    async def _combine_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine and rank results"""
        vector_results = data.get('vector_results', [])
        keyword_results = data.get('keyword_results', [])
        
        return await self.result_combiner.combine(
            vector_results=vector_results,
            keyword_results=keyword_results,
            strategy='hybrid_score'
        )
    
    async def search(self, query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute search pipeline"""
        try:
            # 1. Analyze query
            analysis = await self.use_tool('analyze_query', query)
            
            # 2. Generate embedding if needed
            if analysis['search_type'] in ['vector', 'hybrid']:
                embedding_data = await self.use_tool('generate_embedding', 
                    analysis['optimized_query']
                )
            
            # 3. Perform searches
            results = {}
            if analysis['search_type'] in ['vector', 'hybrid']:
                results['vector_results'] = await self.use_tool('vector_search', {
                    'embedding': embedding_data['embedding'],
                    **(options or {})
                })
            
            if analysis['search_type'] in ['keyword', 'hybrid']:
                results['keyword_results'] = await self.use_tool('keyword_search',
                    analysis['optimized_query']
                )
            
            # 4. Combine results if needed
            if analysis['search_type'] == 'hybrid':
                results['combined_results'] = await self.use_tool('combine_results', results)
            
            return {
                'query_analysis': analysis,
                'results': results.get('combined_results') or results.get('vector_results') or results.get('keyword_results'),
                'search_type': analysis['search_type']
            }
            
        except Exception as e:
            self.memory.add_error(str(e))
            raise
```

## 3. Content Fetch Agent

```python
class ContentFetchAgent(Agent):
    """Agent for fetching and processing web content"""
    
    def __init__(self):
        super().__init__(
            name="content_fetch_agent",
            capabilities=["web_scraping", "content_processing", "metadata_extraction"],
            memory=Memory()
        )
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        return {
            'validate_url': Tool(
                name='validate_url',
                function=self._validate_url,
                description='Validate URL and check accessibility'
            ),
            'fetch_content': Tool(
                name='fetch_content',
                function=self._fetch_content,
                description='Fetch content from URL'
            ),
            'process_content': Tool(
                name='process_content',
                function=self._process_content,
                description='Clean and process fetched content'
            ),
            'extract_metadata': Tool(
                name='extract_metadata',
                function=self._extract_metadata,
                description='Extract metadata from content'
            )
        }
    
    async def fetch_and_process(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute content fetch pipeline"""
        try:
            # 1. Validate URL
            validation = await self.use_tool('validate_url', url)
            if not validation['valid']:
                raise ValueError(f"Invalid URL: {validation['error']}")
            
            # 2. Fetch content
            content = await self.use_tool('fetch_content', url)
            
            # 3. Process content
            processed = await self.use_tool('process_content', {
                'content': content,
                'options': options
            })
            
            # 4. Extract metadata
            metadata = await self.use_tool('extract_metadata', processed)
            
            return {
                'url': url,
                'content': processed['content'],
                'metadata': metadata,
                'timestamp': processed['timestamp']
            }
            
        except Exception as e:
            self.memory.add_error(str(e))
            raise
```

## Usage Examples

### 1. Transcription Pipeline
```python
# Initialize agent
transcription_agent = TranscriptionAgent()

# Process video
result = await transcription_agent.process_media(
    source="https://example.com/video.mp4",
    options={
        'language': 'en',
        'diarization': True
    }
)

# Access results
transcription = result['transcription']
metadata = result['metadata']
```

### 2. Search Pipeline
```python
# Initialize agent
search_agent = SearchAgent()

# Perform search
results = await search_agent.search(
    query="quantum computing applications",
    options={
        'limit': 20,
        'threshold': 0.75
    }
)

# Access results
analysis = results['query_analysis']
search_results = results['results']
```

### 3. Content Fetch Pipeline
```python
# Initialize agent
fetch_agent = ContentFetchAgent()

# Fetch and process content
result = await fetch_agent.fetch_and_process(
    url="https://example.com/article",
    options={
        'extract_images': True,
        'clean_html': True
    }
)

# Access results
content = result['content']
metadata = result['metadata']
``` 