# Video Search and Analysis System

A sophisticated Python-based system for semantic video search and analysis using RAG (Retrieval-Augmented Generation) and multi-tier search strategies.

## Configuration and Parameters

### 1. Model Configuration
```python
MODELS = {
    'openai': {
        'chat': 'gpt-4o-mini',
        'embedding': 'text-embedding-3-small'
    },
    'groq': {
        'chat': 'llama-3.1-70b-versatile',
        'embedding': 'text-embedding-3-small'
    }
}
```

### 2. Search Parameters by Tier
```python
SEARCH_PARAMETERS = {
    'fine_grained': {
        'similarity_threshold': 0.75,  # Minimum similarity score for segment-level matches
        'content_weight': 0.8,         # Weight given to content-based matching
        'summary_weight': 0.2,         # Weight given to summary-based matching
        'result_percentage': 0.4       # Percentage of total results to return from this tier
    },
    'contextual': {
        'similarity_threshold': 0.7,   # Minimum similarity score for chunk-level matches
        'content_weight': 0.7,         # Weight given to content-based matching
        'summary_weight': 0.3,         # Weight given to summary-based matching
        'result_percentage': 0.35      # Percentage of total results to return from this tier
    },
    'overview': {
        'similarity_threshold': 0.65,  # Minimum similarity score for summary-level matches
        'content_weight': 0.4,         # Weight given to content-based matching
        'summary_weight': 0.6,         # Weight given to summary-based matching
        'result_percentage': 0.25      # Percentage of total results to return from this tier
    }
}
```

### Parameter Adjustment Guide

#### Understanding Parameters

1. **similarity_threshold** (Range: 0.0-1.0)
   - Higher values (>0.8): Very strict matching, fewer but more precise results
   - Medium values (0.6-0.8): Balanced matching, good for most queries
   - Lower values (<0.6): Broader matching, more results but may be less relevant
   
2. **content_weight** and **summary_weight** (Must sum to 1.0)
   - content_weight: Emphasis on exact content matching
   - summary_weight: Emphasis on semantic/contextual matching
   
3. **result_percentage** (All tiers must sum to 1.0)
   - Controls the proportion of results from each search tier
   - Adjust based on whether you need more precise (fine-grained) or contextual results

#### Testing Parameter Adjustments

1. **Basic Parameter Test**
```python
# Test different similarity thresholds
test_queries = [
    "exact phrase to find",           # Test precise matching
    "similar meaning different words", # Test semantic matching
    "partial phrase match"            # Test partial matching
]

# Example test function
def test_similarity_threshold():
    thresholds = [0.65, 0.75, 0.85]
    for query in test_queries:
        for threshold in thresholds:
            search_params.update_params('fine_grained', 
                similarity_threshold=threshold)
            results = search_all(query, max_results=5)
            print(f"Query: {query}, Threshold: {threshold}")
            print(f"Results found: {len(results)}")
```

2. **Weight Balance Test**
```python
# Test content vs summary weight balance
weight_combinations = [
    (0.9, 0.1),  # Heavy content focus
    (0.7, 0.3),  # Balanced with content preference
    (0.5, 0.5),  # Equal weights
    (0.3, 0.7)   # Summary preference
]

def test_weight_balance():
    query = "technical discussion about architecture"
    for content_w, summary_w in weight_combinations:
        search_params.update_params('contextual',
            content_weight=content_w,
            summary_weight=summary_w)
        results = advanced_hybrid_search(query)
        analyze_results_relevance(results)
```

### Example Scenarios

1. **Technical Detail Search**
```python
# Best parameters for finding specific technical details
search_params.update_params('fine_grained', {
    'similarity_threshold': 0.8,
    'content_weight': 0.9,
    'summary_weight': 0.1,
    'result_percentage': 0.6
})

# Example query: "memory allocation in garbage collection"
```

2. **Conceptual Understanding Search**
```python
# Best parameters for finding high-level concepts
search_params.update_params('overview', {
    'similarity_threshold': 0.65,
    'content_weight': 0.3,
    'summary_weight': 0.7,
    'result_percentage': 0.4
})

# Example query: "explain the system architecture"
```

3. **Balanced Search**
```python
# Balanced parameters for general-purpose search
search_params.update_params('contextual', {
    'similarity_threshold': 0.7,
    'content_weight': 0.6,
    'summary_weight': 0.4,
    'result_percentage': 0.4
})

# Example query: "how does the authentication system work"
```

### Validation Checklist

Before deploying parameter changes:

1. ✓ Run basic parameter tests with standard queries
2. ✓ Verify result relevance scores meet expectations
3. ✓ Check result distribution across tiers
4. ✓ Test edge cases (very short/long queries)
5. ✓ Validate performance impact

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
- Supports multiple encoding models:
  - 'cl100k_base': For text-embedding-3-small
  - 'gpt-4': For GPT-4 models
- Provides usage statistics and logging

### 3. Model Selection (`ModelSelector` class)
- Manages multiple AI providers (OpenAI, Groq)
- Handles model selection for chat and embeddings
- Implements analysis generation with system prompts

### 4. Search Functions
- `keyword_search`: Text-based search
- `dot_product_search`: Embedding similarity search
  - Parameters: limit, use_summary, target_source
- `advanced_hybrid_search`: Combined embedding and text search
  - Parameters: content_weight_override, min_similarity
- `search_all`: Multi-tier RAG search strategy
  - Parameters: max_results, video_filter

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

## Environment Variables
Required environment variables:
- `OPENAI_API_KEY`: OpenAI API authentication
- `GROQ_API_KEY`: Groq API authentication
- `SUPABASE_URL`: Supabase instance URL
- `SUPABASE_SERVICE_KEY`: Supabase service key

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
        'relationships': find_relationships(results)
    }
```

## Usage

Run the main script:
```bash
python psearch.py
```

The system will initialize with default parameters and allow interactive searches across video content using the configured AI providers.
