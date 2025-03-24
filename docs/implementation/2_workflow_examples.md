# PMOVES Agent Workflow Examples

## 1. Video Processing and Search Workflow

This workflow demonstrates how to process a video, transcribe it, and make it searchable.

```python
from typing import Dict, Any
from .agents import TranscriptionAgent, SearchAgent
from .utils import VideoProcessor

async def process_and_index_video(video_url: str) -> Dict[str, Any]:
    """Process a video and make it searchable"""
    
    # Initialize agents
    transcription_agent = TranscriptionAgent()
    search_agent = SearchAgent()
    
    try:
        # 1. Process video and generate transcription
        transcription_result = await transcription_agent.process_media(
            source=video_url,
            options={
                'language': 'en',
                'diarization': True,
                'timestamps': True
            }
        )
        
        # 2. Generate embeddings for transcription segments
        segments = VideoProcessor.split_into_segments(
            transcription=transcription_result['transcription'],
            segment_length=30  # 30-second segments
        )
        
        # 3. Index segments for search
        indexed_segments = []
        for segment in segments:
            # Generate embedding
            embedding_data = await search_agent.use_tool(
                'generate_embedding',
                segment['text']
            )
            
            # Store in vector database
            indexed_segment = await search_agent.vector_service.store(
                content=segment['text'],
                embedding=embedding_data['embedding'],
                metadata={
                    'video_url': video_url,
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'speakers': segment.get('speakers', [])
                }
            )
            indexed_segments.append(indexed_segment)
        
        return {
            'video_url': video_url,
            'transcription': transcription_result['transcription'],
            'metadata': transcription_result['metadata'],
            'indexed_segments': indexed_segments,
            'processor_used': transcription_result['processor_used']
        }
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise
```

## 2. Multi-Source Search Workflow

This workflow demonstrates searching across multiple content sources with result aggregation.

```python
from .agents import SearchAgent, ContentFetchAgent
from typing import List, Dict, Any

async def multi_source_search(
    query: str,
    sources: List[str] = ['transcripts', 'documents', 'web']
) -> Dict[str, Any]:
    """Search across multiple content sources"""
    
    # Initialize agents
    search_agent = SearchAgent()
    fetch_agent = ContentFetchAgent()
    
    try:
        results = {}
        
        # 1. Analyze query
        query_analysis = await search_agent.use_tool('analyze_query', query)
        
        # 2. Generate embedding if needed
        if query_analysis['search_type'] in ['vector', 'hybrid']:
            embedding_data = await search_agent.use_tool(
                'generate_embedding',
                query_analysis['optimized_query']
            )
        
        # 3. Search each source
        for source in sources:
            if source == 'transcripts':
                # Search video transcripts
                results['transcripts'] = await search_agent.use_tool(
                    'vector_search',
                    {
                        'embedding': embedding_data['embedding'],
                        'collection': 'transcripts',
                        'limit': 5
                    }
                )
                
            elif source == 'documents':
                # Search document embeddings
                results['documents'] = await search_agent.use_tool(
                    'vector_search',
                    {
                        'embedding': embedding_data['embedding'],
                        'collection': 'documents',
                        'limit': 5
                    }
                )
                
            elif source == 'web':
                # Fetch and search web content
                web_results = await fetch_agent.fetch_and_process(
                    url=query_analysis['optimized_query'],
                    options={'extract_text': True}
                )
                results['web'] = web_results
        
        # 4. Combine and rank results
        combined_results = await search_agent.use_tool(
            'combine_results',
            {
                'query': query,
                'results': results,
                'weights': {
                    'transcripts': 0.4,
                    'documents': 0.4,
                    'web': 0.2
                }
            }
        )
        
        return {
            'query_analysis': query_analysis,
            'results': combined_results,
            'source_breakdown': {
                source: len(results.get(source, [])) 
                for source in sources
            }
        }
        
    except Exception as e:
        print(f"Error in multi-source search: {str(e)}")
        raise
```

## 3. Content Analysis Workflow

This workflow demonstrates analyzing content across different sources and generating insights.

```python
from .agents import SearchAgent, ContentFetchAgent
from .analyzers import ContentAnalyzer
from typing import Dict, Any, List

async def analyze_content(
    topic: str,
    sources: List[str],
    analysis_type: str = 'comprehensive'
) -> Dict[str, Any]:
    """Analyze content and generate insights"""
    
    # Initialize agents
    search_agent = SearchAgent()
    fetch_agent = ContentFetchAgent()
    analyzer = ContentAnalyzer()
    
    try:
        # 1. Gather content from sources
        content_map = {}
        for source in sources:
            # Search for relevant content
            search_results = await search_agent.search(
                query=topic,
                options={'limit': 10}
            )
            
            # Fetch full content where needed
            full_content = []
            for result in search_results['results']:
                if result.get('url'):
                    content = await fetch_agent.fetch_and_process(
                        url=result['url'],
                        options={'clean_html': True}
                    )
                    full_content.append(content)
                else:
                    full_content.append(result)
            
            content_map[source] = full_content
        
        # 2. Analyze content
        analysis_results = {}
        for source, content in content_map.items():
            # Perform analysis based on type
            if analysis_type == 'comprehensive':
                analysis = await analyzer.analyze_comprehensive(
                    content=content,
                    topic=topic
                )
            elif analysis_type == 'summary':
                analysis = await analyzer.analyze_summary(
                    content=content,
                    topic=topic
                )
            else:
                analysis = await analyzer.analyze_basic(
                    content=content,
                    topic=topic
                )
            
            analysis_results[source] = analysis
        
        # 3. Generate insights
        insights = await analyzer.generate_insights(
            analyses=analysis_results,
            topic=topic
        )
        
        return {
            'topic': topic,
            'analysis_type': analysis_type,
            'source_analyses': analysis_results,
            'insights': insights,
            'content_coverage': {
                source: len(content) 
                for source, content in content_map.items()
            }
        }
        
    except Exception as e:
        print(f"Error analyzing content: {str(e)}")
        raise
```

## 4. Real-Time Monitoring Workflow

This workflow demonstrates monitoring and analyzing streaming content.

```python
from .agents import SearchAgent, ContentFetchAgent
from .monitors import StreamMonitor
from typing import Dict, Any, AsyncGenerator

async def monitor_content_stream(
    topics: List[str],
    sources: List[str],
    interval: int = 60
) -> AsyncGenerator[Dict[str, Any], None]:
    """Monitor and analyze streaming content"""
    
    # Initialize components
    search_agent = SearchAgent()
    fetch_agent = ContentFetchAgent()
    monitor = StreamMonitor(interval=interval)
    
    try:
        # 1. Set up monitoring for each source
        for source in sources:
            await monitor.add_source(
                source=source,
                topics=topics
            )
        
        # 2. Start monitoring loop
        async for update in monitor.stream():
            # Process new content
            if update.get('new_content'):
                # Analyze content
                analysis = await search_agent.search(
                    query=update['content'],
                    options={'limit': 5}
                )
                
                # Fetch full content if needed
                if update.get('url'):
                    full_content = await fetch_agent.fetch_and_process(
                        url=update['url']
                    )
                    update['full_content'] = full_content
                
                # Add analysis
                update['analysis'] = analysis
            
            # Yield update
            yield {
                'timestamp': update['timestamp'],
                'source': update['source'],
                'topics': topics,
                'content': update.get('content'),
                'analysis': update.get('analysis'),
                'metrics': update.get('metrics')
            }
            
    except Exception as e:
        print(f"Error in content monitoring: {str(e)}")
        raise
    finally:
        await monitor.cleanup()
```

## Usage Examples

### 1. Process and Index Video
```python
# Process video
result = await process_and_index_video(
    video_url="https://example.com/video.mp4"
)

print(f"Processed video with {len(result['indexed_segments'])} segments")
print(f"Processor used: {result['processor_used']}")
```

### 2. Multi-Source Search
```python
# Search across sources
results = await multi_source_search(
    query="machine learning applications",
    sources=['transcripts', 'documents', 'web']
)

print("Search results by source:")
for source, count in results['source_breakdown'].items():
    print(f"{source}: {count} results")
```

### 3. Content Analysis
```python
# Analyze content
analysis = await analyze_content(
    topic="artificial intelligence trends",
    sources=['academic', 'news', 'social'],
    analysis_type='comprehensive'
)

print("\nKey insights:")
for insight in analysis['insights']:
    print(f"- {insight}")
```

### 4. Content Monitoring
```python
# Monitor content
async for update in monitor_content_stream(
    topics=["AI news", "technology updates"],
    sources=["news_feeds", "social_media"],
    interval=300  # 5 minutes
):
    print(f"\nUpdate from {update['source']}:")
    print(f"Topics matched: {update['topics']}")
    if update.get('analysis'):
        print("Analysis available")
``` 