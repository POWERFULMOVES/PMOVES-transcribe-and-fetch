# Video Search and Analysis System

A sophisticated Python-based system for semantic video search and analysis using RAG (Retrieval-Augmented Generation) and multi-tier search strategies.

## Core Components

### 1. Search Parameters Management (`SearchParameters` class)
- Manages three-tier search strategy:
  - **Fine-grained** (segment level): High precision, content-focused
  - **Contextual** (chunk level): Balanced approach
  - **Overview** (summary level): High-level insights
- Configurable parameters per tier:
  - Similarity thresholds
  - Content/summary weights
  - Result percentages

### 2. Token Management (`TokenCounter` class)
- Tracks embedding and generation token usage
- Supports multiple encoding models
- Provides usage statistics and logging

### 3. Model Selection (`ModelSelector` class)
- Manages multiple AI providers (OpenAI, Groq)
- Handles model selection for chat and embeddings
- Implements analysis generation with system prompts

### 4. Search Functions
- `keyword_search`: Text-based search
- `dot_product_search`: Embedding similarity search
- `advanced_hybrid_search`: Combined embedding and text search
- `search_all`: Multi-tier RAG search strategy

### 5. Result Processing
- `get_complete_row_data`: Retrieves full context
- `process_search_results`: Batch processing
- `analyze_search_results`: AI-powered analysis
- `display_results`: Rich formatted output

## Database Structure

### Tables
1. **video_transcriptions**
   - Fine-grained segments with metadata
   - Timestamps and context information
   - Embedding vectors

2. **document_embeddings**
   - Contextual chunks of content
   - Summaries and aggregated text
   - Multiple embedding vectors

3. **video_transcriptions_full**
   - Complete video transcripts
   - Video metadata
   - Source information

## Enhancement Roadmap

### 1. Search Results Enhancement

#### Dynamic Result Ranking
```python
def rank_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Consider multiple factors:
    # - Similarity score
    # - Content relevance
    # - Context quality
    # - Temporal proximity
    return weighted_rank(results)
```

#### Context Enrichment
```python
def enrich_context(result: Dict[str, Any]) -> Dict[str, Any]:
    # Add:
    # - Previous/next segment summaries
    # - Related topics
    # - Key entities
    # - Timeline position
    return enriched_result
```

#### Smart Filtering
```python
def smart_filter(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Remove:
    # - Redundant information
    # - Low-quality matches
    # - Contextually irrelevant results
    return filtered_results
```

### 2. AI Summary Improvements

#### Structured Analysis
```python
def generate_structured_analysis(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        'key_points': extract_key_points(results),
        'timeline': create_timeline(results),
        'relationships': find_relationships(results),
        'insights': generate_insights(results)
    }
```

#### Interactive Summaries
```python
def generate_interactive_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        'summary': create_summary(results),
        'drill_down_points': identify_drill_down_points(results),
        'related_queries': suggest_related_queries(results),
        'highlights': extract_highlights(results)
    }
```

#### Multi-Modal Output
```python
def generate_rich_output(analysis: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'text_summary': format_text_summary(analysis),
        'visual_timeline': create_timeline_visualization(analysis),
        'topic_graph': generate_topic_graph(analysis),
        'key_moments': highlight_key_moments(analysis)
    }
```

### 3. User Experience Enhancements

#### Progressive Loading
- Implement async result loading
- Show immediate results while processing
- Allow interaction during search

#### Interactive Refinement
- Add query suggestions
- Enable result filtering
- Provide relevance feedback

#### Rich Visualization
- Add timeline views
- Show relationship graphs
- Display content heatmaps

#### Personalization
- Track user preferences
- Learn from interactions
- Adapt result ranking

## Implementation Priority

### High Priority
1. Result ranking enhancement
2. Context enrichment
3. Structured analysis

### Medium Priority
1. Interactive summaries
2. Progressive loading
3. Rich visualization

### Future Enhancements
1. Multi-modal output
2. Personalization
3. Advanced filtering

## Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key
- Groq API key
- Supabase account and credentials

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_key
   GROQ_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_SERVICE_KEY=your_key
   ```

### Usage
Run the main script:
```bash
python psearch.py
```

Use the interactive menu to:
1. Perform searches
2. Adjust search parameters
3. View results and analysis

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
