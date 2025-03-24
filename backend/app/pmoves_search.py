import os
import sys
import json
import time
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field

# External dependencies
from openai import OpenAI
from groq import Groq
from supabase import create_client, Client
from tiktoken import get_encoding
from dotenv import load_dotenv

# Rich library imports
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.progress import Progress

# Database Table Formats and Column Mappings
VIDEO_TRANSCRIPTIONS_FORMAT = {
    'id': 'str',
    'video_id': 'str',
    'segment_id': 'int',
    'watch_url': 'str',
    'start_time': 'str',
    'end_time': 'str',
    'content': 'str',
    'created_at': 'datetime',
    'metadata': 'Dict[str, Any]',
    'summary': 'str',
    'embedding': 'List[float]',
    'summary_embedding': 'List[float]',
    'chunk_id': 'int',
    'full_transcript_id': 'str'
}

DOCUMENT_EMBEDDINGS_FORMAT = {
    'id': 'int',
    'video_id': 'str',
    'start_time': 'str',
    'end_time': 'str',
    'text': 'str',
    'summary': 'str',
    'segment_ids': 'List[str]',
    'watch_url': 'str',
    'created_at': 'datetime',
    'embedding': 'List[float]',
    'summary_embedding': 'List[float]'
}

VIDEO_TRANSCRIPTIONS_FULL_FORMAT = {
    'video_id': 'str',
    'full_transcript': 'str',
    'upload_date': 'datetime',
    'source_file': 'str'
}

# Table Names
VIDEO_TRANSCRIPTIONS_TABLE = 'video_transcriptions'
DOCUMENT_EMBEDDINGS_TABLE = 'document_embeddings'
VIDEO_TRANSCRIPTIONS_FULL_TABLE = 'video_transcriptions_full'

# Table Display Formats
SEARCH_RESULT_TABLE_FORMAT = {
    'columns': [
        ('Content', 'display_content'),
        ('Summary', 'display_summary'),
        ('Time', 'time_range'),
        ('Score', 'similarity'),
        ('Video ID', 'video_id'),
        ('Segment', 'segment_id'),
        ('Created', 'created_display')
    ],
    'metadata_fields': ['metadata_display', 'watch_url', 'chunk_id', 'full_transcript_id']
}

RESULT_DISPLAY_LENGTH = {
    'content': 200,
    'summary': 100,
    'metadata': 150
}

# Display Formatting Constants
SEARCH_ICONS = {
    'keyword': '🔍',
    'dot_product': '🎯',
    'advanced_hybrid': '🔄',
    'fine-grained': '🔍',
    'contextual': '🎯',
    'summary-based': '🔄',
    'default': '📌'
}

SOURCE_STYLES = {
    'document_embeddings': {
        'icon': '📄',
        'color': 'blue',
        'border': 'blue',
        'content_color': 'bright_blue',
        'title': 'Document Embeddings'
    },
    'video_transcriptions': {
        'icon': '🎬',
        'color': 'green',
        'border': 'green',
        'content_color': 'bright_green',
        'title': 'Video Transcriptions'
    },
    'video_transcriptions_full': {
        'icon': '📽️',
        'color': 'magenta',
        'border': 'magenta',
        'content_color': 'bright_magenta',
        'title': 'Full Transcriptions'
    },
    'default': {
        'icon': '📎',
        'color': 'white',
        'border': 'white',
        'content_color': 'white',
        'title': 'Unknown Source'
    }
}

# Score Thresholds and Colors
SCORE_STYLES = {
    'high': {
        'threshold': 0.8,
        'style': 'bold green',
        'icon': '🌟'
    },
    'good': {
        'threshold': 0.8,
        'style': 'green',
        'icon': '✨'
    },
    'fair': {
        'threshold': 0.7,
        'style': 'yellow',
        'icon': '✓'
    },
    'medium': {
        'threshold': 0.6,
        'style': 'bold yellow',
        'description': 'medium relevance'
    },
    'low': {
        'threshold': 0.0,
        'style': 'bold red',
        'description': 'low relevance'
    },
    'default': {
        'style': 'dim',
        'description': 'N/A'
    }
}

# Table Styling
TABLE_STYLES = {
    'default': {
        'header_style': 'bold cyan',
        'row_style': 'white',
        'border_style': 'blue',
        'padding': (0, 1),
        'title_style': 'bold blue'
    },
    'results': {
        'header_style': 'bold green',
        'row_style': 'bright_white',
        'border_style': 'green',
        'padding': (0, 1),
        'title_style': 'bold green'
    },
    'error': {
        'header_style': 'bold red',
        'row_style': 'red',
        'border_style': 'red',
        'padding': (0, 1),
        'title_style': 'bold red'
    }
}

RESULT_TABLE_FORMAT = {
    'columns': [
        ('Content', 'display_content', 100),  # column name, field name, max width
        ('Score', 'similarity', 10),
        ('Source', 'source', 20),
        ('Time', 'time_range', 30),
        ('Video ID', 'video_id', 15),
        ('Created', 'created_display', 25)
    ],
    'metadata_columns': [
        ('Summary', 'display_summary', 80),
        ('Metadata', 'metadata_display', 50)
    ]
}

COLUMN_WIDTHS = {
    'content': 100,
    'summary': 80,
    'metadata': 50,
    'score': 10,
    'source': 20,
    'time': 30,
    'video_id': 15,
    'created': 25
}

TABLE_HEADERS = {
    'search_results': [
        'Content',
        'Score',
        'Source',
        'Time',
        'Video ID',
        'Created'
    ],
    'metadata': [
        'Summary',
        'Metadata',
        'Watch URL',
        'Segment ID'
    ]
}

# Status and Progress Indicators
STATUS_INDICATORS = {
    'success': '✓',
    'error': '❌',
    'progress': '⏳',
    'pointer': '👉'
}

# Analysis Process Steps
ANALYSIS_STEPS = {
    'start': '[bold cyan]Starting Search Results Analysis...[/bold cyan]',
    'filtering': '[cyan]Filtering results...[/cyan]',
    'prioritizing': '[cyan]Prioritizing results...[/cyan]',
    'preparing': '[cyan]Preparing analysis text...[/cyan]',
    'generating': '[bold cyan]🤖 Generating AI Analysis...[/bold cyan]',
    'complete': '[green]AI analysis completed[/green]'
}

# Error Message Templates
ERROR_TEMPLATES = {
    'no_results': "[yellow]{indicator} No results found for {search_type}[/yellow]",
    'search_error': "[red]{indicator} {search_type} error: {error}[/red]",
    'analysis_error': "[red]{indicator} Analysis error: {error}[/red]"
}

# Success Message Templates
SUCCESS_TEMPLATES = {
    'results_found': "[green]{indicator} Found {count} results[/green]",
    'analysis_ready': "[green]{indicator} Combined results ready for analysis[/green]",
    'analysis_complete': "[green]{indicator} Analysis completed successfully[/green]"
}

# Progress Stage Icons and Messages
PROGRESS_STAGES = {
    'start': {
        'icon': '🚀',
        'style': 'bold cyan',
        'message': 'Starting Search Operation'
    },
    'search': {
        'icon': '🔍',
        'style': 'bold yellow',
        'message': 'Executing Search'
    },
    'filter': {
        'icon': '🔄',
        'style': 'bold blue',
        'message': 'Filtering Results'
    },
    'combine': {
        'icon': '📊',
        'style': 'bold magenta',
        'message': 'Combining Results'
    },
    'analyze': {
        'icon': '🤖',
        'style': 'bold green',
        'message': 'Analyzing Results'
    },
    'complete': {
        'icon': '✅',
        'style': 'bold green',
        'message': 'Operation Complete'
    }
}

SEARCH_METHOD_STYLES = {
    'keyword': {
        'icon': '🔍',
        'color': 'yellow',
        'description': 'Text-based search'
    },
    'dot_product': {
        'icon': '🎯',
        'color': 'green',
        'description': 'Semantic similarity search'
    },
    'advanced_hybrid': {
        'icon': '🔄',
        'color': 'blue',
        'description': 'Combined keyword and semantic search'
    },
    'fine_grained': {
        'icon': '🎯',
        'color': 'cyan',
        'description': 'Detailed segment analysis'
    },
    'contextual': {
        'icon': '🌐',
        'color': 'magenta',
        'description': 'Context-aware search'
    },
    'overview': {
        'icon': '📊',
        'color': 'yellow',
        'description': 'High-level summary search'
    },
    'default': {
        'icon': '📝',
        'color': 'white',
        'description': 'General search'
    }
}

# Table Display Formats
RESULT_TABLE_FORMAT = {
    'columns': [
        ('Content', 'display_content', 100),  # column name, field name, max width
        ('Score', 'similarity', 10),
        ('Source', 'source', 20),
        ('Time', 'time_range', 30),
        ('Video ID', 'video_id', 15),
        ('Created', 'created_display', 25)
    ],
    'metadata_columns': [
        ('Summary', 'display_summary', 80),
        ('Metadata', 'metadata_display', 50)
    ]
}

COLUMN_WIDTHS = {
    'content': 100,
    'summary': 80,
    'metadata': 50,
    'score': 10,
    'source': 20,
    'time': 30,
    'video_id': 15,
    'created': 25
}

SOURCE_STYLES = {
    'document_embeddings': {
        'icon': '📄',
        'color': 'blue',
        'border': 'blue',
        'content_color': 'bright_blue',
        'title': 'Document Embeddings'
    },
    'video_transcriptions': {
        'icon': '🎬',
        'color': 'green',
        'border': 'green',
        'content_color': 'bright_green',
        'title': 'Video Transcriptions'
    },
    'video_transcriptions_full': {
        'icon': '📽️',
        'color': 'magenta',
        'border': 'magenta',
        'content_color': 'bright_magenta',
        'title': 'Full Transcriptions'
    },
    'default': {
        'icon': '📎',
        'color': 'white',
        'border': 'white',
        'content_color': 'white',
        'title': 'Unknown Source'
    }
}

SCORE_STYLES = {
    'high': {
        'threshold': 0.8,
        'style': 'bold green',
        'icon': '🌟'
    },
    'good': {
        'threshold': 0.7,
        'style': 'green',
        'icon': '✨'
    },
    'fair': {
        'threshold': 0.6,
        'style': 'yellow',
        'icon': '✓'
    },
    'low': {
        'threshold': 0.0,
        'style': 'red',
        'icon': '⚠️'
    },
    'default': {
        'style': 'dim',
        'icon': '❌'
    }
}

TABLE_STYLES = {
    'title': {
        'icon': '📊',
        'style': 'bold blue'
    },
    'header': {
        'style': 'bold cyan'
    },
    'border': {
        'style': 'blue'
    },
    'columns': {
        'Content': {'style': 'white', 'width': 60, 'overflow': 'fold'},
        'Score': {'style': 'bold', 'width': 8, 'justify': 'right'},
        'Source': {'style': 'cyan', 'width': 20},
        'Time': {'style': 'cyan', 'width': 20},
        'Video ID': {'style': 'yellow', 'width': 15},
        'Created': {'style': 'dim', 'width': 25}
    }
}

SEARCH_ICONS = {
    'keyword': '🔍',
    'dot_product': '🎯',
    'advanced_hybrid': '🔄',
    'default': '📌'
}

@dataclass
class DocumentEmbedding:
    """Type-safe structure for document_embeddings table."""
    id: int
    video_id: str
    start_time: str
    end_time: str
    text: str
    summary: str
    segment_ids: List[str]
    watch_url: str
    created_at: datetime
    embedding: List[float]  # public.vector(1536)
    summary_embedding: List[float]  # public.vector(1536)

@dataclass
class VideoTranscription:
    """Type-safe structure for video_transcriptions table."""
    id: str  # uuid
    video_id: str
    segment_id: int
    watch_url: str
    start_time: str
    end_time: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any]  # jsonb
    summary: str
    embedding: List[float]  # public.vector(1536)
    summary_embedding: List[float]  # public.vector(1536)
    chunk_id: int
    full_transcript_id: str

@dataclass
class VideoTranscriptionFull:
    """Type-safe structure for video_transcriptions_full table."""
    video_id: str
    full_transcript: str
    upload_date: datetime
    source_file: str

@dataclass
class SearchResult:
    """Type-safe structure for search results."""
    id: str
    video_id: str
    content: str
    source: str
    similarity: float
    start_time: str = ""  # Changed to str to match database schema
    end_time: str = ""    # Changed to str to match database schema
    created_at: str = ""
    summary: str = ""
    metadata: Dict = field(default_factory=dict)
    segment_id: str = ""
    chunk_id: str = ""
    full_transcript_id: str = ""
    watch_url: str = ""
    source_file: str = ""
    search_method: str = ""
    tier: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Create a SearchResult from a dictionary, handling missing fields."""
        # Required fields
        required = {
            'id': str(data.get('id', '')),
            'video_id': str(data.get('video_id', '')),
            'content': str(data.get('text', data.get('content', ''))),
            'source': str(data.get('source', 'unknown')),
            'similarity': float(data.get('similarity', 0.0))
        }
        
        # Optional fields with defaults
        optional = {
            'start_time': str(data.get('start_time', '')),  # Keep as string
            'end_time': str(data.get('end_time', '')),      # Keep as string
            'created_at': str(data.get('created_at', '')),
            'summary': str(data.get('summary', '')),
            'metadata': dict(data.get('metadata', {})),
            'segment_id': str(data.get('segment_id', '')),
            'chunk_id': str(data.get('chunk_id', '')),
            'full_transcript_id': str(data.get('full_transcript_id', '')),
            'watch_url': str(data.get('watch_url', '')),
            'source_file': str(data.get('source_file', '')),
            'search_method': str(data.get('search_method', '')),
            'tier': str(data.get('tier', ''))
        }
        
        return cls(**required, **optional)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SearchResult to a dictionary."""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'content': self.content,
            'source': self.source,
            'similarity': self.similarity,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'created_at': self.created_at,
            'summary': self.summary,
            'metadata': self.metadata,
            'segment_id': self.segment_id,
            'chunk_id': self.chunk_id,
            'full_transcript_id': self.full_transcript_id,
            'watch_url': self.watch_url,
            'source_file': self.source_file,
            'search_method': self.search_method,
            'tier': self.tier
        }

def validate_search_result(result: Dict[str, Any]) -> bool:
    """Validate search result against expected schema."""
    try:
        # Get source from result
        source = result.get('source', '')
        if source == 'document_embeddings':
            required_fields = {'id', 'video_id', 'start_time', 'end_time', 'text', 'summary'}
        elif source == 'video_transcriptions':
            required_fields = {'id', 'video_id', 'segment_id', 'content', 'start_time', 'end_time'}
        elif source == 'video_transcriptions_full':
            required_fields = {'video_id', 'full_transcript'}
        else:
            return False
            
        return all(field in result for field in required_fields)
    except Exception:
        return False

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
openai_client = OpenAI(api_key=api_key)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")
groq_client = Groq(api_key=groq_api_key)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY environment variable is not set")
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize Rich console
console = Console()

# Global search parameters
class SearchParameters:
    """Manages adjustable search parameters."""
    
    def __init__(self):
        # Default parameters
        self.params = {
            'fine_grained': {
                'similarity_threshold': 0.75,
                'content_weight': 0.8,
                'summary_weight': 0.2,
                'result_percentage': 0.4
            },
            'contextual': {
                'similarity_threshold': 0.7,
                'content_weight': 0.7,
                'summary_weight': 0.3,
                'result_percentage': 0.35
            },
            'overview': {
                'similarity_threshold': 0.65,
                'content_weight': 0.4,
                'summary_weight': 0.6,
                'result_percentage': 0.25
            }
        }
    
    def update_params(self, tier: str, **kwargs):
        """Update parameters for a specific search tier."""
        if tier in self.params:
            for key, value in kwargs.items():
                if key in self.params[tier]:
                    self.params[tier][key] = float(value)
    
    def get_params(self, tier: str) -> dict:
        """Get parameters for a specific search tier."""
        return self.params.get(tier, {})
    
    def get_all_params(self) -> dict:
        """Get all search parameters."""
        return self.params

# Initialize global search parameters
search_params = SearchParameters()

class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {
            'input': 0,
            'output': 0
        }
        self.encoders = {
            'cl100k_base': get_encoding('cl100k_base'),  # For text-embedding-3-small
            'gpt-4': get_encoding('cl100k_base'),  # For GPT-4 models
        }
    
    def count_embedding_tokens(self, text: str) -> int:
        """Count tokens for embedding."""
        tokens = len(self.encoders['cl100k_base'].encode(text))
        self.embedding_tokens += tokens
        return tokens
    
    def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
        """Count tokens for generation (input and output)."""
        input_tokens = len(self.encoders['gpt-4'].encode(input_text))
        self.generation_tokens['input'] += input_tokens
        
        result = {'input': input_tokens, 'output': 0}
        
        if output_text:
            output_tokens = len(self.encoders['gpt-4'].encode(output_text))
            self.generation_tokens['output'] += output_tokens
            result['output'] = output_tokens
        
        return result
    
    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': self.embedding_tokens + sum(self.generation_tokens.values())
        }
    
    def log_stats(self):
        """Log current token usage statistics."""
        stats = self.get_stats()
        console.print(Panel.fit(
            f"[bold]Token Usage Stats[/bold]\n"
            f"Embedding tokens: {stats['embedding_tokens']:,}\n"
            f"Generation input tokens: {stats['generation_tokens']['input']:,}\n"
            f"Generation output tokens: {stats['generation_tokens']['output']:,}\n"
            f"Total tokens: {stats['total_tokens']:,}",
            title="Token Counter"
        ))

# Initialize token counter
token_counter = TokenCounter()

class ModelSelector:
    """Manages model selection and execution for different AI providers."""
    
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
    
    @staticmethod
    def get_available_providers():
        return list(ModelSelector.MODELS.keys())
    
    @staticmethod
    def get_chat_model(provider: str):
        return ModelSelector.MODELS[provider]['chat']
    
    @staticmethod
    def get_embedding_model(provider: str):
        return ModelSelector.MODELS[provider]['embedding']
    
    @staticmethod
    def generate_analysis(text: str, provider: str = 'openai') -> str:
        """Generate analysis using the specified provider."""
        try:
            # Use a shorter system prompt for Groq
            groq_system_prompt = """You are an AI assistant analyzing video transcription segments. Focus on:
1. Key points and insights
2. Relationships between segments
3. Reliability of information
4. Suggested timestamps to watch

Keep responses concise and informative."""

            openai_system_prompt = '''You are an advanced AI system designed to analyze and interpret data from a structured database related to video content, document embeddings, and transcriptions. Here is the structure and purpose of the key tables:

1. **video_transcriptions**: This table contains individual segments of transcriptions with associated metadata:
   - `content`: The text of a specific segment.
   - `video_id`: Unique identifier for the video.
   - `segment_id`: Identifier for the specific segment in a video.
   - `start_time`, `end_time`: Timestamps indicating the duration of the segment.
   - `watch_url`: URL to view the video starting at the segment's timestamp.
   - `embedding`: A numerical vector representing the segment's semantic meaning.
   - `context_before`, `context_after`: Text from the preceding and following segments for additional context.

2. **document_embeddings**: This table represents aggregated chunks of video content and their summaries:
   - `text`: The aggregated text content of multiple segments.
   - `summary`: A high-level summary of the aggregated text.
   - `embedding`: A numerical vector representing the chunk's semantic meaning.
   - `summary_embedding`: A numerical vector for the summary's semantic meaning.
   - `video_id`: Unique identifier for the video.
   - `start_time`, `end_time`: Timestamps for the aggregated content.

3. **video_transcriptions_full**: This table contains full transcriptions for videos:
   - `full_transcript`: The complete transcription of the video.
   - `video_id`: Unique identifier for the video.

Your task is to:
- **Answer Questions**: Respond to user queries using the most relevant data from the database. Prioritize results with the highest similarity scores when embeddings are used.
- **Summarize Results**: Provide concise and accurate summaries using data from `summary`, `content`, and `full_transcript`.
- **Provide Insights**: Use the context fields (`context_before`, `context_after`) to offer a broader understanding of individual segments. For example, explain how a segment fits into the larger video narrative.
- **Handle Queries Dynamically**: Adapt to the type of query:
  - For specific details, use `video_transcriptions` (segment-level granularity).
  - For high-level summaries, use `document_embeddings` (chunk or summary-level insights).
  - For full-context queries, incorporate `video_transcriptions_full` (complete video transcriptions).

Always reference `video_id`, timestamps, and `watch_url` where appropriate to provide actionable responses. Ensure your responses are clear, concise, and aligned with the database structure.'''

            if provider == 'groq':
                print("\nAttempting Groq analysis...")
                response = groq_client.chat.completions.create(
                    model=ModelSelector.get_chat_model('groq'),
                    messages=[
                        {"role": "system", "content": groq_system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                # Count output tokens
                content = response.choices[0].message.content
                token_counter.count_generation_tokens("", content)
                return content

            else:  # openai
                print("\nAttempting OpenAI analysis...")
                response = openai_client.chat.completions.create(
                    model=ModelSelector.get_chat_model('openai'),
                    messages=[
                        {"role": "system", "content": openai_system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                # Count output tokens
                content = response.choices[0].message.content
                token_counter.count_generation_tokens("", content)
                return content

        except Exception as e:
            return f"Error with {provider} analysis: {str(e)}"

def analyze_search_results(results: List[SearchResult], provider: str = 'openai') -> str:
    """Analyze search results using the specified AI provider."""
    try:
        # Filtering stage
        filtered_results = []
        seen_content = set()
        
        for result in results:
            if not result.content:
                continue
            content = result.content.strip()
            if not content or content in seen_content:
                continue
            if result.similarity < 0.3:
                continue
            seen_content.add(content)
            filtered_results.append(result)
        
        # Prioritize results
        enriched_results = prioritize_results(filtered_results)[:5]
        
        # Prepare analysis text
        result_texts = []
        for idx, result in enumerate(enriched_results, 1):
            result_text = [
                f"\n{idx}. Source: {result.source}",
                f"Content: {result.content[:300]}",
                f"Similarity: {result.similarity:.3f}",
                f"Video: {result.video_id}"
            ]
            if result.watch_url:
                result_text.append(f"Watch URL: {result.watch_url}")
            result_texts.append('\n'.join(result_text))
        
        combined_text = "\n---\n".join(result_texts)
        
        # Generate AI analysis
        return ModelSelector.generate_analysis(combined_text, provider)
        
    except Exception as e:
        return f"Error analyzing search results: {str(e)}"

def calculate_duration(start_time: str, end_time: str) -> str:
    """Calculate duration between two timestamps."""
    try:
        # Convert timestamps to seconds
        def time_to_seconds(t):
            h, m, s = map(float, t.split(':'))
            return h * 3600 + m * 60 + s
            
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)
        duration = end_seconds - start_seconds
        
        # Format duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    except:
        return "Unknown duration"

def get_video_metadata(video_id: str) -> Dict[str, Any]:
    """Retrieve metadata for a video from the database."""
    try:
        # Get metadata from video_transcriptions table instead
        result = supabase.table('video_transcriptions') \
            .select('video_id, metadata') \
            .eq('video_id', video_id) \
            .limit(1) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get('metadata', {})
        return {}
        
    except Exception as e:
        console.print(f"[red]Error fetching video metadata: {str(e)}[/red]")
        return {}

def enrich_result_metadata(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add additional context and metadata to search results."""
    enriched = result.copy()
    
    try:
        # Add video metadata if available
        if result.get('video_id'):
            video_data = get_video_metadata(result['video_id'])
            enriched['video_title'] = video_data.get('title')
            enriched['video_description'] = video_data.get('description')
            
        # Add temporal context
        if result.get('start_time') and result.get('end_time'):
            enriched['duration'] = calculate_duration(
                result['start_time'], 
                result['end_time']
            )
            
        # Add content statistics
        if content := result.get('content'):
            enriched['content_length'] = len(content)
            enriched['word_count'] = len(content.split())
            
        # Add context availability flags
        enriched['has_context'] = bool(
            result.get('context_before') or 
            result.get('context_after')
        )
        
        # Add summary availability flag
        enriched['has_summary'] = bool(result.get('summary'))
        
    except Exception as e:
        console.print(f"[red]Error enriching result metadata: {str(e)}[/red]")
        
    return enriched

def prioritize_results(results: List[SearchResult]) -> List[SearchResult]:
    """Prioritize results based on multiple factors."""
    try:
        # Define scoring weights
        weights = {
            'similarity': 0.4,
            'content_length': 0.2,
            'has_summary': 0.2,
            'word_count': 0.1
        }
        
        # Calculate composite score for each result
        scored_results = []
        for result in results:
            score = 0
            score += result.similarity * weights['similarity']
            score += min(len(result.content) / 1000, 1) * weights['content_length']
            score += bool(result.summary) * weights['has_summary']
            score += min(len(result.content.split()) / 200, 1) * weights['word_count']
            
            # Create a tuple of (score, result) for sorting
            scored_results.append((score, result))
        
        # Sort by composite score
        sorted_results = [r for _, r in sorted(scored_results, key=lambda x: x[0], reverse=True)]
        return sorted_results
        
    except Exception as e:
        console.print(f"[red]Error prioritizing results: {str(e)}[/red]")
        return results

def log_operation(operation: str, params: Dict[str, Any], results: List[Dict[str, Any]] = None) -> None:
    """Log database operations with enhanced formatting."""
    
    # Create operation header
    operation_icon = {
        'Keyword Search': '🔍',
        'Dot Product Search': '🎯',
        'Advanced Hybrid Search': '🔄'
    }.get(operation, '📌')
    
    console.print(f"\n[bold cyan]{operation_icon} {operation} Operation Log[/bold cyan]")
    
    # Create parameters table
    params_table = Table(
        title="[bold yellow]Search Parameters[/bold yellow]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    params_table.add_column("Parameter", style="cyan")
    params_table.add_column("Value", style="green")
    
    # Filter out embeddings from parameters
    display_params = params.copy()
    if 'query_embedding' in display_params:
        display_params['query_embedding'] = '<embedding vector>'
    
    # Add parameters to table
    for key, value in display_params.items():
        params_table.add_row(str(key), str(value))
    
    console.print(params_table)
    
    # Log results if available
    if results:
        result_count = len(results)
        
        # Create results summary table
        summary_table = Table(
            title=f"[bold yellow]Results Summary ({result_count} items)[/bold yellow]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        # Add source distribution
        source_counts = {}
        for result in results:
            source = result.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        summary_table.add_column("Source", style="cyan")
        summary_table.add_column("Count", style="green", justify="right")
        summary_table.add_column("Percentage", style="yellow", justify="right")
        
        for source, count in source_counts.items():
            percentage = (count / result_count) * 100
            summary_table.add_row(
                f"{source}",
                str(count),
                f"{percentage:.1f}%"
            )
        
        console.print(summary_table)
    
    # Add performance metrics if available
    metrics_table = Table(
        title="[bold yellow]Performance Metrics[/bold yellow]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    
    # Add token usage
    token_stats = token_counter.get_stats()
    metrics_table.add_row("Embedding Tokens", f"{token_stats['embedding_tokens']:,}")
    metrics_table.add_row("Generation Input Tokens", f"{token_stats['generation_tokens']['input']:,}")
    metrics_table.add_row("Generation Output Tokens", f"{token_stats['generation_tokens']['output']:,}")
    metrics_table.add_row("Total Tokens", f"{token_stats['total_tokens']:,}")
    
    console.print(metrics_table)
    
    # Add separator
    console.print("[yellow]" + "="*50 + "[/yellow]\n")

def get_embedding(text: str) -> List[float]:
    """Get embedding for the given text using OpenAI's API."""
    try:
        console.print(f"\n[bold yellow]Generating Embedding[/bold yellow]")
        console.print(Panel(f"[cyan]Text:[/cyan] {text[:100]}{'...' if len(text) > 100 else ''}"))
        console.print(f"[cyan]Model:[/cyan] text-embedding-3-small")
        
        start_time = datetime.now()
        # Count embedding tokens
        token_counter.count_embedding_tokens(text)
        
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        end_time = datetime.now()
        
        embedding = response.data[0].embedding
        duration = (end_time - start_time).total_seconds()
        
        console.print(f"[green]✓ Embedding generated successfully[/green]")
        console.print(f"[cyan]Embedding dimensions:[/cyan] {len(embedding)}")
        console.print(f"[cyan]Generation time:[/cyan] {duration:.2f} seconds")
        console.print("[yellow]" + "="*50 + "[/yellow]\n")
        
        return embedding
    except Exception as e:
        console.print(f"[red]Error generating embedding: {str(e)}[/red]")
        raise

def get_complete_row_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve complete row data based on the source table."""
    try:
        source = result.get('source', '')
        video_id = result.get('video_id', '')
        
        if not source or not video_id:
            return result
            
        query = None
        if source == 'document_embeddings':
            start_time = result.get('start_time', '')
            query = supabase.table('document_embeddings').select(
                'id', 'video_id', 'start_time', 'end_time', 'text', 
                'summary', 'segment_ids', 'watch_url', 'created_at'
            ).eq('video_id', video_id)
            if start_time:
                query = query.eq('start_time', start_time)
        elif source == 'video_transcriptions':
            start_time = result.get('start_time', '')
            query = supabase.table('video_transcriptions').select(
                'id', 'video_id', 'segment_id', 'watch_url', 'start_time',
                'end_time', 'content', 'created_at', 'metadata', 'summary',
                'chunk_id', 'full_transcript_id'
            ).eq('video_id', video_id)
            if start_time:
                query = query.eq('start_time', start_time)
        elif source == 'video_transcriptions_full':
            query = supabase.table('video_transcriptions_full').select(
                'video_id', 'full_transcript', 'upload_date', 'source_file'
            ).eq('video_id', video_id)
            
        if query:
            response = query.execute()
            if response.data and len(response.data) > 0:
                # Merge the new data with the original result
                # Keep the similarity score from the search
                similarity = result.get('similarity', 0)
                result.update(response.data[0])
                result['similarity'] = similarity
                
                # For video_transcriptions_full, set content to full_transcript
                if source == 'video_transcriptions_full':
                    result['content'] = result.get('full_transcript', '')
                    # Set start_time and end_time to None since it's the full transcript
                    result['start_time'] = 'FULL'
                    result['end_time'] = 'FULL'
                
                console.print(f"[green]✓ Retrieved complete data for {source} record[/green]")
            else:
                console.print(f"[yellow]! No additional data found for {source} record[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error retrieving complete row data: {str(e)}[/red]")
        console.print(f"[yellow]Debug - Result data:[/yellow]")
        console.print(result)
    
    return result

def process_search_results(results: List[Dict[str, Any]]) -> List[SearchResult]:
    """Process search results with consistent formatting."""
    if not results:
        return []
        
    processed_results = []
    
    for result in results:
        try:
            # Get complete data
            complete_result = get_complete_row_data(result)
            
            # For full transcripts, truncate content before processing
            if complete_result.get('source') == 'video_transcriptions_full':
                complete_result['content'] = truncate_content(
                    complete_result.get('full_transcript', ''),
                    max_length=200
                )
            
            # Convert to type-safe SearchResult
            search_result = SearchResult.from_db_result(
                complete_result,
                complete_result.get('source', 'unknown')
            )
            
            processed_results.append(search_result)
            
        except Exception as e:
            console.print(f"[red]Error processing result: {str(e)}[/red]")
            continue
    
    return processed_results

def format_result_row(result: SearchResult) -> List[str]:
    """Format a search result into a table row."""
    try:
        source_style = get_source_style(result.source)
        score_style = get_score_style(result.similarity)
        
        # Format content with source-specific styling
        content = result.content
        if content:
            content = content[:200] + '...' if len(content) > 200 else content
            content = f"[{source_style['content_color']}]{content}[/]"
        else:
            content = "[dim]No content[/dim]"
        
        # Format score with appropriate style
        score = f"[{score_style}]{result.similarity:.2f}[/]"
        
        # Format source with icon
        source = f"{source_style['icon']} [{source_style['color']}]{result.source}[/]"
        
        # Format time range
        time_range = format_time_range(result.start_time, result.end_time) or "[dim]N/A[/dim]"
        
        # Format video ID
        video_id = f"[dim]{result.video_id}[/dim]" if result.video_id else "[dim]N/A[/dim]"
        
        # Format created timestamp
        created = result.created_at or "[dim]N/A[/dim]"
        
        return [content, score, source, time_range, video_id, created]
        
    except Exception as e:
        console.print(f"[red]Error formatting row: {str(e)}[/red]")
        return None

def create_results_table(results: List[SearchResult], title: str = "Search Results") -> Table:
    """Create a formatted table for search results."""
    if not results:
        return None
        
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title=title,
        title_style="bold blue",
        padding=(0, 1)
    )
    
    # Add columns with appropriate widths
    columns = [
        ("Content", 60),
        ("Score", 10),
        ("Source", 20),
        ("Time", 25),
        ("Video ID", 15),
        ("Created", 20)
    ]
    
    for header, width in columns:
        table.add_column(header, width=width)
    
    # Add rows
    for result in results:
        try:
            if isinstance(result, SearchResult):
                row = format_result_row(result)
                if row:
                    table.add_row(*row)
        except Exception as e:
            console.print(f"[red]Error adding row: {str(e)}[/red]")
            continue
    
    return table

def display_results(results: List[SearchResult]):
    """Display final formatted results with metadata."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    try:
        # Main results table
        table = create_results_table(results)
        if table:
            console.print(table)
            console.print(f"\n[dim]Found {len(results)} results[/dim]")
        
        # Metadata table if available
        metadata_results = [r for r in results if r.metadata or r.summary]
        if metadata_results:
            metadata_table = Table(
                title="[bold cyan]Additional Information[/bold cyan]",
                show_header=True,
                header_style="bold yellow",
                border_style="blue",
                padding=(0, 1)
            )
            
            metadata_table.add_column("Video ID", style="dim")
            metadata_table.add_column("Summary", style="cyan")
            metadata_table.add_column("Metadata", style="white")
            
            for result in metadata_results:
                metadata_table.add_row(
                    result.video_id or "N/A",
                    result.summary or "N/A",
                    format_metadata(result.metadata) or "N/A"
                )
            
            console.print("\n", metadata_table)
            
    except Exception as e:
        console.print(f"[red]Error displaying results: {str(e)}[/red]")

def display_search_header(search_type: str, query: str):
    """Display consistent header for all search types."""
    icons = {
        'keyword': '🔍',
        'dot_product': '🎯',
        'advanced_hybrid': '🔄'
    }
    icon = icons.get(search_type, '📌')
    console.print(f"\n[bold cyan]{icon} Executing {search_type.title()} Search[/bold cyan]")
    console.print(f"[dim]Query: {query}[/dim]")

def keyword_search(query: str, limit: int = 10) -> List[SearchResult]:
    """Perform keyword-based search."""
    try:
        display_search_header('keyword', query)
        
        params = {
            'query_text': str(query),
            'match_count': limit
        }
        
        with console.status("[bold yellow]Searching...[/bold yellow]"):
            response = supabase.rpc('keyword_search', params).execute()
            
        log_operation("Keyword Search", params, response.data)
        results = response.data if response.data else []
        
        if not results:
            console.print("[yellow]❌ No results found[/yellow]")
            return []
            
        console.print(f"[green]✓ Found {len(results)} results[/green]")
        return process_search_results(results)
    except Exception as e:
        console.print(f"[red]❌ Keyword search error: {str(e)}[/red]")
        return []

def dot_product_search(query: str, limit: int = 10, use_summary: bool = False, target_source: str = None) -> List[SearchResult]:
    """Perform dot product similarity search."""
    try:
        display_search_header('dot_product', query)
        
        with console.status("[bold yellow]Generating embedding...[/bold yellow]"):
            query_embedding = get_embedding(query)
            
        if not query_embedding:
            console.print("[red]❌ Failed to generate embedding[/red]")
            return []
            
        # Set weights based on use_summary flag
        content_weight = 0.2 if use_summary else 0.8
        summary_weight = 0.8 if use_summary else 0.2
            
        params = {
            'query_embedding': query_embedding,
            'match_count': limit,
            'content_weight': content_weight,
            'summary_weight': summary_weight,
            'video_filter': None
        }
        
        with console.status("[bold yellow]Searching...[/bold yellow]"):
            response = supabase.rpc('dot_product_search', params).execute()
            
        log_operation("Dot Product Search", params, response.data)
        
        # Process and validate results
        results = []
        if response.data:
            for item in response.data:
                if not item.get('video_id') and not item.get('content'):
                    continue
                
                if 'source' not in item:
                    if item.get('full_transcript'):
                        item['source'] = 'video_transcriptions_full'
                    elif item.get('segment_id') is not None:
                        item['source'] = 'video_transcriptions'
                    else:
                        item['source'] = 'document_embeddings'
                
                if target_source and item['source'] != target_source:
                    continue
                    
                if not use_summary and item['source'] == 'video_transcriptions_full':
                    continue
                    
                if use_summary and item['source'] == 'video_transcriptions':
                    continue
                
                results.append(item)
        
        if not results:
            console.print("[yellow]❌ No matching results found[/yellow]")
            return []
            
        console.print(f"[green]✓ Found {len(results)} results[/green]")
        return process_search_results(results)
    except Exception as e:
        console.print(f"[red]❌ Dot product search error: {str(e)}[/red]")
        return []

def advanced_hybrid_search(query: str, limit: int = 10, content_weight_override: float = None, min_similarity: float = 0.7) -> List[SearchResult]:
    """Perform advanced hybrid search combining embeddings and text."""
    try:
        display_search_header('advanced_hybrid', query)
        
        with console.status("[bold yellow]Generating embedding...[/bold yellow]"):
            query_embedding = get_embedding(query)
        
        if not query_embedding:
            console.print("[red]❌ Failed to generate embedding[/red]")
            return []
            
        actual_content_weight = content_weight_override if content_weight_override is not None else 0.7
        actual_summary_weight = 1.0 - actual_content_weight
        
        params = {
            'query_embedding': query_embedding,
            'match_count': limit,
            'content_weight': actual_content_weight,
            'summary_weight': actual_summary_weight,
            'video_filter': None,
            'min_similarity': min_similarity
        }
        
        with console.status("[bold yellow]Searching...[/bold yellow]"):
            response = supabase.rpc('advanced_hybrid_search', params).execute()
            
        log_operation("Advanced Hybrid Search", params, response.data)
        
        results = []
        if response.data:
            for item in response.data:
                if not item.get('video_id') and not item.get('content'):
                    continue
                    
                if 'source' not in item:
                    if item.get('full_transcript'):
                        item['source'] = 'video_transcriptions_full'
                    elif item.get('segment_id') is not None:
                        item['source'] = 'video_transcriptions'
                    else:
                        item['source'] = 'document_embeddings'
                
                results.append(item)
        
        if not results:
            console.print("[yellow]❌ No results found[/yellow]")
            return []
            
        console.print(f"[green]✓ Found {len(results)} results[/green]")
        return process_search_results(results)
    except Exception as e:
        console.print(f"[red] Advanced hybrid search error: {str(e)}[/red]")
        return []

def execute_search_tier(
    query: str,
    tier_name: str,
    search_func: Callable,
    params: Dict[str, Any],
    max_results: int,
    seen_segments: Set[str]
):
    """Execute a search tier with consistent formatting and logging."""
    tier_results = []
    
    # Extract only the parameters needed for advanced_hybrid_search
    search_params = {
        'content_weight_override': params.get('content_weight'),
        'min_similarity': params.get('similarity_threshold', 0.7)
    }
    
    # Execute search with appropriate parameters
    results = search_func(
        query=query,
        limit=max_results,
        **search_params
    )
    
    # Process results
    for result in results:
        if not isinstance(result, SearchResult):
            result = SearchResult.from_db_result(result, result.get('source', 'unknown'))
            
        # Skip if we've seen this segment before
        key = f"{result.video_id}_{result.start_time}_{result.end_time}"
        if key in seen_segments:
            continue
            
        seen_segments.add(key)
        result.tier = tier_name.lower()
        result.search_method = tier_name.lower()
        tier_results.append(result)
    
    display_tier_results(tier_results, tier_name)
    return tier_results

def search_all(query: str, max_results: int = 10, video_filter: str = None) -> List[SearchResult]:
    """Perform all search types with consistent formatting and execution."""
    try:
        # Initialize search
        console.print("\n[bold cyan]📊 Combined Search Operation[/bold cyan]")
        console.print(f"[dim]Query: {query}[/dim]")
        all_results: List[SearchResult] = []
        
        # Execute individual searches
        search_types = [
            ('Keyword Search', 'keyword', keyword_search),
            ('Dot Product Search', 'dot_product', dot_product_search),
            ('Advanced Hybrid Search', 'advanced_hybrid', advanced_hybrid_search)
        ]
        
        # First phase: Execute all searches and collect results
        for display_name, search_type, search_func in search_types:
            console.print(f"\n[bold cyan]{SEARCH_ICONS[search_type]} Executing {display_name}[/bold cyan]")
            results = search_func(query=query, limit=max_results)
            if results:
                console.print(f"\n[bold blue]{display_name} Results:[/bold blue]")
                display_tier_results(results, display_name)
                for result in results:
                    result.tier = search_type
                    result.search_method = search_type
                    all_results.append(result)

        # Show initial combined results
        if not all_results:
            console.print(format_status_message(
                "No results found across all search methods",
                "warning"
            ))
            return []

        # Sort and display all results by score before processing
        console.print("\n[bold cyan]📊 Total Search Results (Sorted by Score)[/bold cyan]")
        all_sorted_results = sorted(all_results, key=lambda x: x.similarity, reverse=True)
        display_initial_combined_results(all_sorted_results)
        
        console.print("\n[bold green]👉 Press Enter to continue with processing...[/bold green]")
        input()

        # Second phase: Process and analyze results
        console.print("\n[bold cyan]📊 Processing Combined Results[/bold cyan]")
        unique_results: List[SearchResult] = []
        seen_segments = set()
        
        # Remove duplicates
        for result in all_sorted_results:
            key = f"{result.video_id}_{result.source}"
            if key not in seen_segments:
                seen_segments.add(key)
                unique_results.append(result)
        
        console.print(f"[cyan]Removed {len(all_sorted_results) - len(unique_results)} duplicate results[/cyan]")
        
        # Display statistics and combined results
        display_search_statistics(unique_results)
        display_combined_results(unique_results)
        
        # Third phase: Analysis
        if unique_results:
            console.print("\n[bold cyan]🤖 Starting Analysis Phase[/bold cyan]")
            display_results(unique_results)
        
        console.print("\n[bold green]✓ Search operation completed[/bold green]")
        return unique_results
        
    except Exception as e:
        display_error('Search', 'Error during search operation', e)
        return []

def get_search_icon(search_method: str) -> str:
    """Get icon for search method."""
    return SEARCH_ICONS.get(search_method, SEARCH_ICONS['default'])

def get_source_style(source: str) -> dict:
    """Get styling information for source type."""
    style = SOURCE_STYLES.get(source, SOURCE_STYLES['default'])
    return {
        'icon': style['icon'],
        'color': style['color'],
        'border': style['border'],
        'content_color': style['content_color'],
        'title': style['title']
    }

def get_search_method_style(method: str) -> dict:
    """Get styling information for search method."""
    return SEARCH_METHOD_STYLES.get(method, SEARCH_METHOD_STYLES['default'])

def get_score_style(score: float) -> str:
    """Get color for similarity score."""
    for level, config in SCORE_STYLES.items():
        if level != 'default' and score >= config['threshold']:
            return config['style']
    return SCORE_STYLES['default']['style']

def truncate_content(content: str, max_length: int = 200) -> str:
    """Helper function to truncate content consistently."""
    if not content:
        return ""
        
    return content[:max_length] + "..." if len(content) > max_length else content

def display_tier_results(results: List[SearchResult], tier_name: str):
    """Display search results for a specific tier with enhanced formatting."""
    if not results:
        console.print(format_status_message(f"No results found for {tier_name}", "warning"))
        return

    # Group results by source
    grouped_results = defaultdict(list)
    for result in results:
        grouped_results[result.source].append(result)
    
    # Display results for each source type with source-specific styling
    for source, source_results in grouped_results.items():
        source_style = SOURCE_STYLES.get(source, SOURCE_STYLES['default'])
        method_style = SEARCH_METHOD_STYLES.get(tier_name.lower().replace(' ', '_'), SEARCH_METHOD_STYLES['default'])
        
        table = create_full_results_table(f"{method_style['icon']} {tier_name} Results - {source_style['icon']} {source}")
        table.title_style = f"bold {method_style['color']}"
        table.border_style = source_style['border']
        
        for result in source_results:
            display_result_row(table, result)
        
        console.print(table)
    
    # Show summary statistics for this tier
    method_counts = defaultdict(int)
    source_counts = defaultdict(int)
    for result in results:
        method_counts[result.search_method] += 1
        source_counts[result.source] += 1
    
    console.print("\n[cyan]Results by Source:[/cyan]")
    for source, count in source_counts.items():
        source_style = get_source_style(source)
        console.print(f"  {source_style['icon']} {source}: {count}")
    
    console.print(format_status_message(
        f"Found {len(results)} results in {tier_name}",
        "success"
    ))

def display_results(results: List[SearchResult], show_by_type: bool = True):
    """Display search results in an enhanced formatted table."""
    if not results:
        console.print("[yellow]❌ No results found.[/yellow]")
        return
        
    # Show analysis start
    console.print("\n[bold cyan]🤖 Starting Analysis Phase[/bold cyan]")
    
    # Show filtering stage
    console.print(ANALYSIS_STEPS['filtering'])
    filtered_results = []
    seen_content = set()
    
    with console.status("[yellow]Processing results...[/yellow]") as status:
        for idx, result in enumerate(results, 1):
            status.update(f"[yellow]Filtering result {idx}/{len(results)}[/yellow]")
            if not result.content:
                continue
            content = result.content.strip()
            if not content or content in seen_content:
                continue
            if result.similarity < 0.3:
                continue
            seen_content.add(content)
            filtered_results.append(result)
    
    console.print(format_status_message(
        f"Filtered {len(results)} results to {len(filtered_results)} unique results",
        "info"
    ))
    
    # Display filtered results with full details
    console.print("\n[bold cyan]Filtered Results:[/bold cyan]")
    table = create_full_results_table("Filtered Search Results")
    for result in filtered_results:
        display_result_row(table, result)
    console.print(table)

    # Show prioritization stage
    console.print(ANALYSIS_STEPS['prioritizing'])
    enriched_results = prioritize_results(filtered_results)[:5]
    
    console.print(format_status_message(
        f"Selected top {len(enriched_results)} results for analysis",
        "info"
    ))
    
    # Display prioritized results with full details
    console.print("\n[bold cyan]Top Priority Results:[/bold cyan]")
    priority_table = create_full_results_table("Priority Results for Analysis")
    for result in enriched_results:
        display_result_row(priority_table, result)
    console.print(priority_table)

    # Show preparation stage
    console.print(ANALYSIS_STEPS['preparing'])
    result_texts = []
    for idx, result in enumerate(enriched_results, 1):
        result_text = [
            f"\n{idx}. Source: {result.source}",
            f"Content: {result.content[:300]}",
            f"Similarity: {result.similarity:.3f}",
            f"Video: {result.video_id}"
        ]
        if result.watch_url:
            result_text.append(f"Watch URL: {result.watch_url}")
        result_texts.append('\n'.join(result_text))
    
    combined_text = "\n---\n".join(result_texts)
    console.print(Panel(
        combined_text,
        title="[bold cyan]Analysis Input[/bold cyan]",
        border_style="blue"
    ))

    # Show analysis generation
    console.print(ANALYSIS_STEPS['generating'])
    
    analysis_table = Table(
        title="[bold cyan]AI Analysis Results[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        padding=(0, 1)
    )
    analysis_table.add_column("Provider", style="cyan", width=10)
    analysis_table.add_column("Analysis", style="white", overflow="fold")

    # Run analyses
    analyses = {}
    
    # Run OpenAI and Groq analyses sequentially
    with console.status("[yellow]Running analyses...[/yellow]") as status:
        # OpenAI Analysis
        try:
            status.update("[bold green]Running OpenAI Analysis...[/bold green]")
            analyses['openai'] = analyze_search_results(filtered_results, 'openai')
        except Exception as e:
            analyses['openai'] = f"Error: {str(e)}"

        # Groq Analysis
        try:
            status.update("[bold blue]Running Groq Analysis...[/bold blue]")
            analyses['groq'] = analyze_search_results(filtered_results, 'groq')
        except Exception as e:
            analyses['groq'] = f"Error: {str(e)}"

    # Display results
    for provider, content in analyses.items():
        icon = "🔍" if "Error" not in str(content) else "❌"
        title_color = "green" if provider == "openai" else "blue"
        
        analysis_table.add_row(
            f"{icon} {provider.title()}",
            Panel(
                str(content),
                title=f"[bold {title_color}]{provider.title()} Insights[/bold {title_color}]",
                border_style=title_color,
                padding=(1, 2)
            )
        )

    console.print("\n[bold cyan]Analysis Results:[/bold cyan]")
    console.print(analysis_table)
    console.print(ANALYSIS_STEPS['complete'])

def format_full_transcript(transcript: str, max_length: int = 200) -> str:
    """Format the full transcript for display, showing segment information."""
    if not transcript:
        return ""
        
    # Split into segments
    segments = transcript.split("Segment ")
    segments = [s for s in segments if s.strip()]  # Remove empty segments
    
    if not segments:
        return transcript[:max_length] + "..." if len(transcript) > max_length else transcript
        
    # Format first few segments
    formatted_segments = []
    total_length = 0
    
    for segment in segments:
        if total_length >= max_length:
            break
            
        # Extract timestamp and content
        try:
            # Split at first colon to separate header from content
            header, content = segment.split(":", 1)
            # Extract timestamp from header
            start_idx = header.find("(")
            end_idx = header.find(")")
            timestamp = header[start_idx+1:end_idx].strip() if start_idx != -1 and end_idx != -1 else ""
            # Clean up content
            content = content.strip()
            
            segment_text = f"{timestamp}: {content}"
            if total_length + len(segment_text) > max_length:
                # Truncate last segment if needed
                remaining = max_length - total_length
                if remaining > 10:  # Only add if we can show meaningful content
                    segment_text = segment_text[:remaining] + "..."
                formatted_segments.append(segment_text)
                break
            else:
                formatted_segments.append(segment_text)
                total_length += len(segment_text)
        except:
            # If segment parsing fails, add raw text
            if total_length < max_length:
                segment_text = segment[:max_length-total_length] + "..."
                formatted_segments.append(segment_text)
            break
    
    result = "\n".join(formatted_segments)
    if len(segments) > len(formatted_segments):
        result += f"\n... ({len(segments) - len(formatted_segments)} more segments)"
    
    return result

def create_results_table(title: str) -> Table:
    """Create a consistently styled results table."""
    table = Table(
        title=f"[{TABLE_STYLES['title']['style']}]{TABLE_STYLES['title']['icon']} {title}[/{TABLE_STYLES['title']['style']}]",
        show_header=True,
        header_style=TABLE_STYLES['header']['style'],
        border_style=TABLE_STYLES['border']['style']
    )
    
    # Add columns with consistent styling
    for col_name, col_style in TABLE_STYLES['columns'].items():
        table.add_column(
            col_name.title(),
            style=col_style['style'],
            width=col_style.get('width'),
            justify=col_style.get('justify', 'left'),
            overflow=col_style.get('overflow')
        )
    
    return table

def format_status_message(message: str, status: str) -> str:
    """Format a status message according to standards."""
    status_formats = {
        'success': {'prefix': '✓', 'style': 'green'},
        'error': {'prefix': '❌', 'style': 'red'},
        'warning': {'prefix': '⚠️', 'style': 'yellow'},
        'info': {'prefix': 'ℹ️', 'style': 'cyan'}
    }
    fmt = status_formats.get(status, status_formats['info'])
    return f"[{fmt['style']}]{fmt['prefix']} {message}[/{fmt['style']}]"

def create_source_table(source: str, title: str) -> Table:
    """Create a table with source-specific styling."""
    source_configs = {
        'document_embeddings': {
            'icon': '📄',
            'color': 'blue',
            'columns': [
                ('Score', {'style': 'bold', 'width': 8, 'justify': 'right'}),
                ('Content', {'style': 'white', 'width': 50, 'overflow': 'fold'}),
                ('Summary', {'style': 'cyan', 'width': 30}),
                ('ID', {'style': 'yellow', 'width': 15}),
                ('URL', {'style': 'blue underline', 'width': 30})
            ]
        },
        'video_transcriptions': {
            'icon': '🎬',
            'color': 'green',
            'title': 'Video Transcriptions',
            'columns': [
                ('Score', {'style': 'bold', 'width': 8, 'justify': 'right'}),
                ('Segment', {'style': 'yellow', 'width': 10}),
                ('Content', {'style': 'white', 'width': 40, 'overflow': 'fold'}),
                ('Summary', {'style': 'cyan', 'width': 30}),
                ('Time', {'style': 'cyan', 'width': 20}),
                ('ID', {'style': 'yellow', 'width': 15}),
                ('URL', {'style': 'blue underline', 'width': 30})
            ]
        },
        'video_transcriptions_full': {
            'icon': '📽️',
            'color': 'magenta',
            'title': 'Full Transcriptions',
            'columns': [
                ('Score', {'style': 'bold', 'width': 8, 'justify': 'right'}),
                ('Content', {'style': 'white', 'width': 60, 'overflow': 'fold'}),
                ('ID', {'style': 'yellow', 'width': 15}),
                ('Segments', {'style': 'cyan', 'width': 15}),
                ('URL', {'style': 'blue underline', 'width': 30})
            ]
        }
    }
    
    if source not in source_configs:
        console.print(f"[yellow]⚠️ Unknown source type: {source}, using default layout[/yellow]")
        source = 'document_embeddings'  # Use default layout
    
    config = source_configs[source]
    table = Table(
        title=f"[bold {config['color']}]{config['icon']} {title}[/bold {config['color']}]",
        show_header=True,
        header_style="bold yellow",
        border_style=config['color'],
        padding=(0, 1)
    )
    
    for col_name, col_style in config['columns']:
        table.add_column(col_name, **col_style)
    
    return table

def get_score_style(score: float) -> str:
    """Get color for similarity score."""
    for level, config in SCORE_STYLES.items():
        if level != 'default' and score >= config['threshold']:
            return config['style']
    return SCORE_STYLES['default']['style']

def get_source_style(source: str) -> dict:
    """Get the appropriate style for a source."""
    return SOURCE_STYLES.get(source, SOURCE_STYLES['default'])

def format_timestamp(timestamp: str) -> str:
    """Format timestamp into HH:MM:SS."""
    if not timestamp or timestamp == 'FULL':
        return timestamp or ""
    
    try:
        if ':' in timestamp:  # Already in HH:MM:SS format
            return timestamp
            
        # Try to convert to float first
        seconds = float(timestamp)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif minutes > 0:
            return f"{minutes:02d}:{seconds:02d}"
        return f"{seconds:02d}"
    except (ValueError, TypeError):
        # If conversion fails, return the original string
        return str(timestamp)

def format_time_range(start: str, end: str) -> str:
    """Format time range into human readable string."""
    if not start or not end:
        return ""
    if start == 'FULL' or end == 'FULL':
        return 'FULL'
    
    start_str = format_timestamp(start)
    end_str = format_timestamp(end)
    return f"[dim]{start_str} → {end_str}[/dim]"

def format_metadata(metadata: Dict) -> str:
    """Format metadata dictionary into displayable string."""
    if not metadata:
        return ""
    
    formatted = []
    for key, value in metadata.items():
        if isinstance(value, (dict, list)):
            value = str(value)
        formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)

def create_full_results_table(title: str) -> Table:
    """Create a table showing all result fields with source-specific styling."""
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add all columns in consistent order with appropriate styling
    columns = [
        ("Score", {'style': 'bold', 'width': 8, 'justify': 'right'}),
        ("Method", {'style': 'cyan', 'width': 15}),
        ("Source", {'style': 'cyan', 'width': 20}),
        ("Video ID", {'style': 'yellow', 'width': 15}),
        ("Content", {'style': 'white', 'width': 60, 'overflow': 'fold'}),
        ("Summary", {'style': 'cyan', 'width': 30, 'overflow': 'fold'}),
        ("Metadata", {'style': 'white', 'width': 30, 'overflow': 'fold'}),
        ("Start Time", {'style': 'cyan', 'width': 12}),
        ("End Time", {'style': 'cyan', 'width': 12}),
        ("Segment ID", {'style': 'yellow', 'width': 10}),
        ("Watch URL", {'style': 'blue underline', 'width': 30})
    ]
    
    for col_name, col_style in columns:
        table.add_column(col_name, **col_style)
    
    return table

def display_result_row(table: Table, result: SearchResult):
    """Add a result row with consistent formatting and source-specific styling."""
    source_style = get_source_style(result.source)
    method_style = SEARCH_METHOD_STYLES.get(result.search_method, SEARCH_METHOD_STYLES['default'])
    score_color = get_score_style(result.similarity)
    
    # Format metadata if available
    metadata = getattr(result, 'metadata', {})
    metadata_str = format_metadata(metadata) if metadata else "N/A"
    
    # Format content with source-specific color
    content = result.content[:200] + '...' if len(result.content) > 200 else result.content
    formatted_content = f"[{source_style['content_color']}]{content}[/{source_style['content_color']}]"
    
    table.add_row(
        f"[{score_color}]{result.similarity:.3f}[/{score_color}]",
        f"[{method_style['color']}]{method_style['icon']} {result.search_method}[/{method_style['color']}]",
        f"[{source_style['color']}]{source_style['icon']} {result.source}[/{source_style['color']}]",
        result.video_id,
        formatted_content,
        result.summary or "N/A",
        metadata_str[:100] + "..." if len(metadata_str) > 100 else metadata_str,
        result.start_time,
        result.end_time,
        str(result.segment_id) if result.segment_id is not None else "N/A",
        str(result.watch_url or 'N/A')
    )

def display_initial_combined_results(results: List[SearchResult]):
    """Display initial combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Initial Search Results (Sorted by Score)")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    
    # Show result counts by search method
    method_counts = defaultdict(int)
    for result in results:
        method_counts[result.search_method] += 1
    
    console.print("\n[cyan]Results by Search Method:[/cyan]")
    for method, count in method_counts.items():
        icon = SEARCH_ICONS.get(method, '📌')
        console.print(f"  {icon} {method.title()}: {count}")
    
    console.print(format_status_message(
        f"Total results found: {len(results)}",
        "success"
    ))

def display_combined_results(results: List[SearchResult]):
    """Display combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Combined Search Results")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    console.print(format_status_message(
        f"Total combined results: {len(results)}",
        "success"
    ))

def format_result_row(result: SearchResult) -> List[str]:
    """Format a search result into a table row."""
    source_style = SOURCE_STYLES.get(result.source, SOURCE_STYLES['default'])
    score_style = get_score_style(result.similarity)
    
    # Format content with source-specific styling
    content = f"[{source_style['content_color']}]{result.content[:COLUMN_WIDTHS['content']]}[/]"
    if len(result.content) > COLUMN_WIDTHS['content']:
        content += "[dim]...[/dim]"
    
    # Format score with appropriate style
    score = f"[{score_style['style']}]{result.similarity:.2f}[/]"
    
    # Format source with icon
    source = f"{source_style['icon']} [{source_style['color']}]{result.source}[/]"
    
    # Format time range
    time_range = format_time_range(result.start_time, result.end_time)
    
    # Format video ID
    video_id = f"[dim]{result.video_id}[/dim]"
    
    # Format created timestamp
    created = format_timestamp(result.created_at) if result.created_at else ""
    
    return [content, score, source, time_range, video_id, created]

def create_results_table(results: List[SearchResult], title: str = "Search Results") -> Table:
    """Create a formatted table for search results."""
    if not results:
        return None
        
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title=title,
        title_style="bold blue",
        padding=(0, 1)
    )
    
    # Add columns with appropriate widths
    for header, field, width in RESULT_TABLE_FORMAT['columns']:
        table.add_column(header, width=width)
    
    # Add rows
    for result in results:
        try:
            if validate_search_result(result.__dict__):
                row = format_result_row(result)
                if row:
                    table.add_row(*row)
        except Exception as e:
            console.print(f"[red]Error formatting result: {str(e)}[/red]")
            continue
    
    return table

def display_tier_results(results: List[SearchResult], title: str):
    """Display results from a specific search tier."""
    if not results:
        return
        
    table = create_results_table(results, title)
    console.print(table)
    console.print(f"\n[dim]Found {len(results)} results[/dim]")

def display_results(results: List[SearchResult]):
    """Display final formatted results with metadata."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    try:
        # Main results table
        table = create_results_table(results)
        if table:
            console.print(table)
            console.print(f"\n[dim]Found {len(results)} results[/dim]")
        
        # Metadata table if available
        metadata_results = [r for r in results if r.metadata or r.summary]
        if metadata_results:
            metadata_table = Table(
                title="[bold cyan]Additional Information[/bold cyan]",
                show_header=True,
                header_style="bold yellow",
                border_style="blue",
                padding=(0, 1)
            )
            
            metadata_table.add_column("Video ID", style="dim")
            metadata_table.add_column("Summary", style="cyan")
            metadata_table.add_column("Metadata", style="white")
            
            for result in metadata_results:
                metadata_table.add_row(
                    result.video_id,
                    result.summary or "N/A",
                    format_metadata(result.metadata) or "N/A"
                )
            
            console.print("\n", metadata_table)
            
    except Exception as e:
        console.print(f"[red]Error displaying results: {str(e)}[/red]")

def display_search_statistics(results: List[SearchResult]):
    """Display comprehensive search statistics."""
    stats_table = Table(
        title="[bold cyan]📊 Search Statistics[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add columns
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", style="green", justify="right")
    stats_table.add_column("Details", style="white")
    
    # Calculate statistics
    total_results = len(results)
    source_counts = defaultdict(int)
    score_ranges = defaultdict(int)
    
    for result in results:
        source_counts[result.source] += 1
        if result.similarity >= 0.8:
            score_ranges['high'] += 1
        elif result.similarity >= 0.6:
            score_ranges['medium'] += 1
        else:
            score_ranges['low'] += 1
    
    # Add rows
    stats_table.add_row(
        "Total Results",
        str(total_results),
        "Combined across all search methods"
    )
    
    # Source distribution
    for source, count in source_counts.items():
        source_style = get_source_style(source)
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{source_style['icon']} {source}",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    # Score distribution
    for range_name, count in score_ranges.items():
        icon = "🟢" if range_name == "high" else "🟡" if range_name == "medium" else "🔴"
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{icon} {range_name.title()} Relevance",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    console.print(stats_table)

def display_error(error_type: str, message: str, details: Any = None):
    """Display consistently formatted error messages."""
    error_panel = Panel(
        f"{message}\n\n{str(details) if details else ''}",
        title=f"[bold red]❌ {error_type} Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(error_panel)

def display_analysis_progress(stage: str, results: List[SearchResult] = None):
    """Display analysis progress with consistent formatting."""
    if stage not in ANALYSIS_STEPS:
        return
        
    console.print(ANALYSIS_STEPS[stage])
    if results:
        result_count = len(results)
        console.print(Panel(
            f"Processing {result_count} result{'s' if result_count != 1 else ''}",
            style="dim",
            border_style="blue"
        ))

def display_search_progress(stage: str, message: str = None, status: str = 'info'):
    """Display consistent search progress indicators."""
    if stage not in PROGRESS_STAGES:
        return
    
    stage_info = PROGRESS_STAGES[stage]
    display_msg = message or stage_info['message']
    
    console.print(f"\n[{stage_info['style']}]{stage_info['icon']} {display_msg}[/{stage_info['style']}]")

def format_metadata(metadata: Dict) -> str:
    """Format metadata dictionary into displayable string."""
    if not metadata:
        return ""
    
    formatted = []
    for key, value in metadata.items():
        if isinstance(value, (dict, list)):
            value = str(value)
        formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)

def format_time_range(start: str, end: str) -> str:
    """Format time range into human readable string."""
    if not start or not end:
        return ""
    if start == 'FULL' or end == 'FULL':
        return 'FULL'
    
    start_str = format_timestamp(start)
    end_str = format_timestamp(end)
    return f"[dim]{start_str} → {end_str}[/dim]"

def create_full_results_table(title: str) -> Table:
    """Create a table showing all result fields with source-specific styling."""
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add all columns in consistent order with appropriate styling
    columns = [
        ("Score", {'style': 'bold', 'width': 8, 'justify': 'right'}),
        ("Method", {'style': 'cyan', 'width': 15}),
        ("Source", {'style': 'cyan', 'width': 20}),
        ("Video ID", {'style': 'yellow', 'width': 15}),
        ("Content", {'style': 'white', 'width': 60, 'overflow': 'fold'}),
        ("Summary", {'style': 'cyan', 'width': 30, 'overflow': 'fold'}),
        ("Metadata", {'style': 'white', 'width': 30, 'overflow': 'fold'}),
        ("Start Time", {'style': 'cyan', 'width': 12}),
        ("End Time", {'style': 'cyan', 'width': 12}),
        ("Segment ID", {'style': 'yellow', 'width': 10}),
        ("Watch URL", {'style': 'blue underline', 'width': 30})
    ]
    
    for col_name, col_style in columns:
        table.add_column(col_name, **col_style)
    
    return table

def display_result_row(table: Table, result: SearchResult):
    """Add a result row with consistent formatting and source-specific styling."""
    source_style = get_source_style(result.source)
    method_style = SEARCH_METHOD_STYLES.get(result.search_method, SEARCH_METHOD_STYLES['default'])
    score_color = get_score_style(result.similarity)
    
    # Format metadata if available
    metadata = getattr(result, 'metadata', {})
    metadata_str = format_metadata(metadata) if metadata else "N/A"
    
    # Format content with source-specific color
    content = result.content[:200] + '...' if len(result.content) > 200 else result.content
    formatted_content = f"[{source_style['content_color']}]{content}[/{source_style['content_color']}]"
    
    table.add_row(
        f"[{score_color}]{result.similarity:.3f}[/{score_color}]",
        f"[{method_style['color']}]{method_style['icon']} {result.search_method}[/{method_style['color']}]",
        f"[{source_style['color']}]{source_style['icon']} {result.source}[/{source_style['color']}]",
        result.video_id,
        formatted_content,
        result.summary or "N/A",
        metadata_str[:100] + "..." if len(metadata_str) > 100 else metadata_str,
        result.start_time,
        result.end_time,
        str(result.segment_id) if result.segment_id is not None else "N/A",
        str(result.watch_url or 'N/A')
    )

def display_initial_combined_results(results: List[SearchResult]):
    """Display initial combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Initial Search Results (Sorted by Score)")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    
    # Show result counts by search method
    method_counts = defaultdict(int)
    for result in results:
        method_counts[result.search_method] += 1
    
    console.print("\n[cyan]Results by Search Method:[/cyan]")
    for method, count in method_counts.items():
        icon = SEARCH_ICONS.get(method, '📌')
        console.print(f"  {icon} {method.title()}: {count}")
    
    console.print(format_status_message(
        f"Total results found: {len(results)}",
        "success"
    ))

def display_combined_results(results: List[SearchResult]):
    """Display combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Combined Search Results")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    console.print(format_status_message(
        f"Total combined results: {len(results)}",
        "success"
    ))

def format_result_row(result: SearchResult) -> List[str]:
    """Format a search result into a table row."""
    source_style = SOURCE_STYLES.get(result.source, SOURCE_STYLES['default'])
    score_style = get_score_style(result.similarity)
    
    # Format content with source-specific styling
    content = f"[{source_style['content_color']}]{result.content[:COLUMN_WIDTHS['content']]}[/]"
    if len(result.content) > COLUMN_WIDTHS['content']:
        content += "[dim]...[/dim]"
    
    # Format score with appropriate style
    score = f"[{score_style['style']}]{result.similarity:.2f}[/]"
    
    # Format source with icon
    source = f"{source_style['icon']} [{source_style['color']}]{result.source}[/]"
    
    # Format time range
    time_range = format_time_range(result.start_time, result.end_time)
    
    # Format video ID
    video_id = f"[dim]{result.video_id}[/dim]"
    
    # Format created timestamp
    created = format_timestamp(result.created_at) if result.created_at else ""
    
    return [content, score, source, time_range, video_id, created]

def create_results_table(results: List[SearchResult], title: str = "Search Results") -> Table:
    """Create a formatted table for search results."""
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title=title,
        title_style="bold blue",
        padding=(0, 1)
    )
    
    # Add columns with appropriate widths
    for header, field, width in RESULT_TABLE_FORMAT['columns']:
        table.add_column(header, width=width)
    
    # Add rows
    for result in results:
        if validate_search_result(result.__dict__):
            table.add_row(*format_result_row(result))
    
    return table

def display_tier_results(results: List[SearchResult], title: str):
    """Display results from a specific search tier."""
    if not results:
        return
        
    table = create_results_table(results, title)
    console.print(table)
    console.print(f"\n[dim]Found {len(results)} results[/dim]")

def display_results(results: List[SearchResult]):
    """Display final formatted results with metadata."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    # Main results table
    table = create_results_table(results)
    console.print(table)
    
    # Metadata table if available
    metadata_results = [r for r in results if r.metadata or r.summary]
    if metadata_results:
        metadata_table = create_metadata_table(metadata_results)
        console.print("\n[bold cyan]Additional Information:[/bold cyan]")
        console.print(metadata_table)

def create_metadata_table(results: List[SearchResult]) -> Table:
    """Create a table for result metadata."""
    table = Table(
        title="[bold cyan]Metadata[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add metadata columns
    for header, field, width in RESULT_TABLE_FORMAT['metadata_columns']:
        table.add_column(header, width=width)
    
    # Add rows
    for result in results:
        summary = result.summary[:COLUMN_WIDTHS['summary']] if result.summary else ""
        metadata = format_metadata(result.metadata) if result.metadata else ""
        
        if summary or metadata:
            table.add_row(
                f"[bright_white]{summary}[/]",
                f"[dim]{metadata}[/]"
            )
    
    return table

def display_search_statistics(results: List[SearchResult]):
    """Display comprehensive search statistics."""
    stats_table = Table(
        title="[bold cyan]📊 Search Statistics[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add columns
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", style="green", justify="right")
    stats_table.add_column("Details", style="white")
    
    # Calculate statistics
    total_results = len(results)
    source_counts = defaultdict(int)
    score_ranges = defaultdict(int)
    
    for result in results:
        source_counts[result.source] += 1
        if result.similarity >= 0.8:
            score_ranges['high'] += 1
        elif result.similarity >= 0.6:
            score_ranges['medium'] += 1
        else:
            score_ranges['low'] += 1
    
    # Add rows
    stats_table.add_row(
        "Total Results",
        str(total_results),
        "Combined across all search methods"
    )
    
    # Source distribution
    for source, count in source_counts.items():
        source_style = get_source_style(source)
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{source_style['icon']} {source}",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    # Score distribution
    for range_name, count in score_ranges.items():
        icon = "🟢" if range_name == "high" else "🟡" if range_name == "medium" else "🔴"
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{icon} {range_name.title()} Relevance",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    console.print(stats_table)

def display_error(error_type: str, message: str, details: Any = None):
    """Display consistently formatted error messages."""
    error_panel = Panel(
        f"{message}\n\n{str(details) if details else ''}",
        title=f"[bold red]❌ {error_type} Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(error_panel)

def display_analysis_progress(stage: str, results: List[SearchResult] = None):
    """Display analysis progress with consistent formatting."""
    if stage not in ANALYSIS_STEPS:
        return
        
    console.print(ANALYSIS_STEPS[stage])
    if results:
        result_count = len(results)
        console.print(Panel(
            f"Processing {result_count} result{'s' if result_count != 1 else ''}",
            style="dim",
            border_style="blue"
        ))

def display_search_progress(stage: str, message: str = None, status: str = 'info'):
    """Display consistent search progress indicators."""
    if stage not in PROGRESS_STAGES:
        return
    
    stage_info = PROGRESS_STAGES[stage]
    display_msg = message or stage_info['message']
    
    console.print(f"\n[{stage_info['style']}]{stage_info['icon']} {display_msg}[/{stage_info['style']}]")

def format_metadata(metadata: Dict) -> str:
    """Format metadata dictionary into displayable string."""
    if not metadata:
        return ""
    
    formatted = []
    for key, value in metadata.items():
        if isinstance(value, (dict, list)):
            value = str(value)
        formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)

def format_time_range(start: str, end: str) -> str:
    """Format time range into human readable string."""
    if not start or not end:
        return ""
    if start == 'FULL' or end == 'FULL':
        return 'FULL'
    
    start_str = format_timestamp(start)
    end_str = format_timestamp(end)
    return f"[dim]{start_str} → {end_str}[/dim]"

def create_full_results_table(title: str) -> Table:
    """Create a table showing all result fields with source-specific styling."""
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add all columns in consistent order with appropriate styling
    columns = [
        ("Score", {'style': 'bold', 'width': 8, 'justify': 'right'}),
        ("Method", {'style': 'cyan', 'width': 15}),
        ("Source", {'style': 'cyan', 'width': 20}),
        ("Video ID", {'style': 'yellow', 'width': 15}),
        ("Content", {'style': 'white', 'width': 60, 'overflow': 'fold'}),
        ("Summary", {'style': 'cyan', 'width': 30, 'overflow': 'fold'}),
        ("Metadata", {'style': 'white', 'width': 30, 'overflow': 'fold'}),
        ("Start Time", {'style': 'cyan', 'width': 12}),
        ("End Time", {'style': 'cyan', 'width': 12}),
        ("Segment ID", {'style': 'yellow', 'width': 10}),
        ("Watch URL", {'style': 'blue underline', 'width': 30})
    ]
    
    for col_name, col_style in columns:
        table.add_column(col_name, **col_style)
    
    return table

def display_result_row(table: Table, result: SearchResult):
    """Add a result row with consistent formatting and source-specific styling."""
    source_style = get_source_style(result.source)
    method_style = SEARCH_METHOD_STYLES.get(result.search_method, SEARCH_METHOD_STYLES['default'])
    score_color = get_score_style(result.similarity)
    
    # Format metadata if available
    metadata = getattr(result, 'metadata', {})
    metadata_str = format_metadata(metadata) if metadata else "N/A"
    
    # Format content with source-specific color
    content = result.content[:200] + '...' if len(result.content) > 200 else result.content
    formatted_content = f"[{source_style['content_color']}]{content}[/{source_style['content_color']}]"
    
    table.add_row(
        f"[{score_color}]{result.similarity:.3f}[/{score_color}]",
        f"[{method_style['color']}]{method_style['icon']} {result.search_method}[/{method_style['color']}]",
        f"[{source_style['color']}]{source_style['icon']} {result.source}[/{source_style['color']}]",
        result.video_id,
        formatted_content,
        result.summary or "N/A",
        metadata_str[:100] + "..." if len(metadata_str) > 100 else metadata_str,
        result.start_time,
        result.end_time,
        str(result.segment_id) if result.segment_id is not None else "N/A",
        str(result.watch_url or 'N/A')
    )

def display_initial_combined_results(results: List[SearchResult]):
    """Display initial combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Initial Search Results (Sorted by Score)")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    
    # Show result counts by search method
    method_counts = defaultdict(int)
    for result in results:
        method_counts[result.search_method] += 1
    
    console.print("\n[cyan]Results by Search Method:[/cyan]")
    for method, count in method_counts.items():
        icon = SEARCH_ICONS.get(method, '📌')
        console.print(f"  {icon} {method.title()}: {count}")
    
    console.print(format_status_message(
        f"Total results found: {len(results)}",
        "success"
    ))

def display_combined_results(results: List[SearchResult]):
    """Display combined results with all fields."""
    if not results:
        return
        
    table = create_full_results_table("📊 Combined Search Results")
    
    for result in results:
        display_result_row(table, result)
    
    console.print(table)
    console.print(format_status_message(
        f"Total combined results: {len(results)}",
        "success"
    ))

def format_result_row(result: SearchResult) -> List[str]:
    """Format a search result into a table row."""
    source_style = SOURCE_STYLES.get(result.source, SOURCE_STYLES['default'])
    score_style = get_score_style(result.similarity)
    
    # Format content with source-specific styling
    content = f"[{source_style['content_color']}]{result.content[:COLUMN_WIDTHS['content']]}[/]"
    if len(result.content) > COLUMN_WIDTHS['content']:
        content += "[dim]...[/dim]"
    
    # Format score with appropriate style
    score = f"[{score_style['style']}]{result.similarity:.2f}[/]"
    
    # Format source with icon
    source = f"{source_style['icon']} [{source_style['color']}]{result.source}[/]"
    
    # Format time range
    time_range = format_time_range(result.start_time, result.end_time)
    
    # Format video ID
    video_id = f"[dim]{result.video_id}[/dim]"
    
    # Format created timestamp
    created = format_timestamp(result.created_at) if result.created_at else ""
    
    return [content, score, source, time_range, video_id, created]

def create_results_table(results: List[SearchResult], title: str = "Search Results") -> Table:
    """Create a formatted table for search results."""
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title=title,
        title_style="bold blue",
        padding=(0, 1)
    )
    
    # Add columns with appropriate widths
    for header, field, width in RESULT_TABLE_FORMAT['columns']:
        table.add_column(header, width=width)
    
    # Add rows
    for result in results:
        if validate_search_result(result.__dict__):
            table.add_row(*format_result_row(result))
    
    return table

def display_tier_results(results: List[SearchResult], title: str):
    """Display results from a specific search tier."""
    if not results:
        return
        
    table = create_results_table(results, title)
    console.print(table)
    console.print(f"\n[dim]Found {len(results)} results[/dim]")

def display_results(results: List[SearchResult]):
    """Display final formatted results with metadata."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    # Main results table
    table = create_results_table(results)
    console.print(table)
    
    # Metadata table if available
    metadata_results = [r for r in results if r.metadata or r.summary]
    if metadata_results:
        metadata_table = create_metadata_table(metadata_results)
        console.print("\n[bold cyan]Additional Information:[/bold cyan]")
        console.print(metadata_table)

def display_search_statistics(results: List[SearchResult]):
    """Display comprehensive search statistics."""
    stats_table = Table(
        title="[bold cyan]📊 Search Statistics[/bold cyan]",
        show_header=True,
        header_style="bold yellow",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Add columns
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", style="green", justify="right")
    stats_table.add_column("Details", style="white")
    
    # Calculate statistics
    total_results = len(results)
    source_counts = defaultdict(int)
    score_ranges = defaultdict(int)
    
    for result in results:
        source_counts[result.source] += 1
        if result.similarity >= 0.8:
            score_ranges['high'] += 1
        elif result.similarity >= 0.6:
            score_ranges['medium'] += 1
        else:
            score_ranges['low'] += 1
    
    # Add rows
    stats_table.add_row(
        "Total Results",
        str(total_results),
        "Combined across all search methods"
    )
    
    # Source distribution
    for source, count in source_counts.items():
        source_style = get_source_style(source)
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{source_style['icon']} {source}",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    # Score distribution
    for range_name, count in score_ranges.items():
        icon = "🟢" if range_name == "high" else "🟡" if range_name == "medium" else "🔴"
        percentage = (count / total_results) * 100 if total_results > 0 else 0
        stats_table.add_row(
            f"{icon} {range_name.title()} Relevance",
            str(count),
            f"{percentage:.1f}% of total results"
        )
    
    console.print(stats_table)

def display_error(error_type: str, message: str, details: Any = None):
    """Display consistently formatted error messages."""
    error_panel = Panel(
        f"{message}\n\n{str(details) if details else ''}",
        title=f"[bold red]❌ {error_type} Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(error_panel)

def display_analysis_progress(stage: str, results: List[SearchResult] = None):
    """Display analysis progress with consistent formatting."""
    if stage not in ANALYSIS_STEPS:
        return
        
    console.print(ANALYSIS_STEPS[stage])
    if results:
        result_count = len(results)
        console.print(Panel(
            f"Processing {result_count} result{'s' if result_count != 1 else ''}",
            style="dim",
            border_style="blue"
        ))

def display_search_progress(stage: str, message: str = None, status: str = 'info'):
    """Display consistent search progress indicators."""
    if stage not in PROGRESS_STAGES:
        return
    
    stage_info = PROGRESS_STAGES[stage]
    display_msg = message or stage_info['message']
    
    console.print(f"\n[{stage_info['style']}]{stage_info['icon']} {display_msg}[/{stage_info['style']}]")

def main():
    """Main function to handle user interactions."""
    while True:
        console.print("\n[bold cyan]🔍 PMOVES Search Interface[/bold cyan]")
        console.print("\n1. Perform search")
        console.print("2. Adjust search parameters")
        console.print("3. Exit")
        choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="1")

        if choice == "1":
            # Get search query
            query = Prompt.ask("\n[cyan]Enter your search query[/cyan]")
            if not query:
                console.print("[yellow]No query provided. Returning to menu...[/yellow]")
                continue

            # Execute search with progress indicators
            with Progress() as progress:
                task = progress.add_task("[cyan]Searching...", total=3)
                
                # Keyword Search
                console.print("\n[bold cyan]🔍 Executing Keyword Search[/bold cyan]")
                keyword_results = keyword_search(query)
                if keyword_results:
                    display_tier_results(keyword_results, "Keyword Search Results")
                progress.update(task, advance=1)
                
                # Dot Product Search
                console.print("\n[bold cyan]🎯 Executing Dot Product Search[/bold cyan]")
                dot_product_results = dot_product_search(query)
                if dot_product_results:
                    display_tier_results(dot_product_results, "Dot Product Search Results")
                progress.update(task, advance=1)
                
                # Advanced Hybrid Search
                console.print("\n[bold cyan]🔄 Executing Advanced Hybrid Search[/bold cyan]")
                hybrid_results = advanced_hybrid_search(query)
                if hybrid_results:
                    display_tier_results(hybrid_results, "Advanced Hybrid Search Results")
                progress.update(task, advance=1)

            # Combine all results
            all_results = []
            all_results.extend(keyword_results)
            all_results.extend(dot_product_results)
            all_results.extend(hybrid_results)

            if not all_results:
                console.print("[yellow]No results found.[/yellow]")
                continue

            # Show initial combined results
            console.print("\n[bold cyan]📊 Initial Combined Results[/bold cyan]")
            all_sorted_results = sorted(all_results, key=lambda x: x.similarity, reverse=True)
            display_search_statistics(all_sorted_results)
            display_results(all_sorted_results)

            # Pause for review
            console.print("\n[bold green]👉 Press Enter to continue with processing...[/bold green]")
            input()

            # Process and deduplicate
            console.print("\n[bold cyan]🔄 Processing Combined Results[/bold cyan]")
            with Progress() as progress:
                task = progress.add_task("[cyan]Removing duplicates...", total=len(all_sorted_results))
                unique_results = []
                seen_segments = set()
                
                for result in all_sorted_results:
                    key = f"{result.video_id}_{result.source}"
                    if key not in seen_segments:
                        seen_segments.add(key)
                        unique_results.append(result)
                    progress.update(task, advance=1)

            # Show statistics and final results
            console.print(f"\n[cyan]Removed {len(all_sorted_results) - len(unique_results)} duplicate results[/cyan]")
            display_search_statistics(unique_results)
            
            # Analysis phase
            if unique_results:
                console.print("\n[bold cyan]🤖 Starting Analysis Phase[/bold cyan]")
                with Progress() as progress:
                    task = progress.add_task("[cyan]Analyzing results...", total=4)
                    
                    # Filtering stage
                    console.print("\n[cyan]Filtering results...[/cyan]")
                    progress.update(task, advance=1)
                    
                    # Prioritization
                    console.print("[cyan]Prioritizing content...[/cyan]")
                    progress.update(task, advance=1)
                    
                    # Analysis preparation
                    console.print("[cyan]Preparing analysis...[/cyan]")
                    progress.update(task, advance=1)
                    
                    # AI analysis
                    console.print("[cyan]Running AI analysis...[/cyan]")
                    progress.update(task, advance=1)
                
                display_results(unique_results)

        elif choice == "2":
            # Display current parameters
            console.print("\n[bold cyan]Current Search Parameters:[/bold cyan]")
            for tier, params in search_params.get_all_params().items():
                console.print(f"\n[bold]{tier.title()}[/bold]")
                for param, value in params.items():
                    console.print(f"  {param}: {value}")
            
            # Get tier selection
            valid_tiers = ["fine_grained", "contextual", "overview"]
            tier = Prompt.ask(
                "\nSelect tier to adjust",
                choices=valid_tiers,
                default="fine_grained"
            )
            
            # Get parameter selection
            params = search_params.get_params(tier)
            console.print(f"\n[bold cyan]Parameters for {tier}:[/bold cyan]")
            param_list = list(params.keys())
            for i, param in enumerate(param_list, 1):
                console.print(f"{i}. {param}: {params[param]}")
            
            param_choice = Prompt.ask(
                "\nSelect parameter to adjust",
                choices=[str(i) for i in range(1, len(param_list) + 1)],
                default="1"
            )
            param_name = param_list[int(param_choice) - 1]
            current_value = params[param_name]
            
            # Get new value
            while True:
                try:
                    new_value = float(Prompt.ask(
                        f"\nEnter new value for {param_name} (current: {current_value})"
                    ))
                    if 0 <= new_value <= 1:
                        break
                    console.print("[red]Value must be between 0 and 1[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
            
            # Update parameter
            search_params.update_params(tier, **{param_name: new_value})
            console.print(f"\n[green]Successfully updated {param_name} to {new_value} for {tier} tier[/green]")

        elif choice == "3":
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error during search: {str(e)}[/red]")
        sys.exit(1)
