import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, Callable, Set
from openai import OpenAI
from groq import Groq
from supabase import create_client, Client
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich import print as rprint
from rich.panel import Panel
from rich.syntax import Syntax
from dotenv import load_dotenv
from datetime import datetime
from tiktoken import get_encoding
from dataclasses import dataclass
from collections import defaultdict, Counter
from rich.progress import Progress
from rich.box import DOUBLE_EDGE
import pandas as pd
from pathlib import Path
import time
import traceback
import copy

# Get the app directory path
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

# Load environment variables from the specific .env file location
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"Loaded environment variables from {ENV_PATH}")
else:
    print(f"Warning: .env file not found at {ENV_PATH}")
    # Fallback to default load_dotenv behavior
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Display Icons
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
        'icon': '📄️',
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
    'webpage_content': {
        'icon': '🌐',
        'color': 'cyan',
        'border': 'cyan',
        'content_color': 'bright_cyan',
        'title': 'Web Content'
    },
    'text_content': {
        'icon': '📝',
        'color': 'yellow',
        'border': 'yellow',
        'content_color': 'bright_yellow',
        'title': 'Text Content'
    },
    'media_content': {
        'icon': '🎵',
        'color': 'red',
        'border': 'red',
        'content_color': 'bright_red',
        'title': 'Media Content'
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
        'description': 'high relevance'
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
    'title': {
        'style': 'bold cyan',
        'icon': '📊'
    },
    'header': {
        'style': 'bold magenta'
    },
    'border': {
        'style': 'blue'
    },
    'columns': {
        'score': {
            'style': None,
            'width': 8,
            'justify': 'right'
        },
        'method': {
            'style': 'cyan',
            'width': 15
        },
        'source': {
            'style': 'yellow',
            'width': 20
        },
        'content': {
            'style': 'white',
            'width': 40,
            'overflow': 'fold'
        },
        'video_id': {
            'style': 'yellow',
            'width': 15
        },
        'segment_id': {
            'style': 'yellow',
            'width': 10
        },
        'metadata': {
            'style': 'blue',
            'width': 20,
            'overflow': 'fold'
        },
        'start_time': {
            'style': 'cyan',
            'width': 10
        },
        'end_time': {
            'style': 'cyan',
            'width': 10
        },
        'watch_url': {
            'style': 'blue',
            'width': 100,
            'overflow': 'fold'
        }
    }
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
        'icon': '🔍',
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

# Search method styling
SEARCH_METHOD_STYLES = {
    'keyword': {
        'icon': '🔍',
        'color': 'cyan',
        'border': 'cyan',
        'content_color': 'bright_cyan',
        'title': 'Keyword Search'
    },
    'dot_product': {
        'icon': '🎯',
        'color': 'blue',
        'border': 'blue',
        'content_color': 'bright_blue',
        'title': 'Dot Product Search'
    },
    'hybrid': {
        'icon': '🔄',
        'color': 'green',
        'border': 'green',
        'content_color': 'bright_green',
        'title': 'Hybrid Search'
    },
    'default': {
        'icon': '📌',
        'color': 'white',
        'border': 'white',
        'content_color': 'white',
        'title': 'Unknown Search'
    }
}

@dataclass
class SearchResult:
    """Represents a search result with all relevant metadata from different database tables."""
    # Required fields
    content_id: str  # Unique identifier for the content (video_id for videos)
    content: str   # Content text from the search result
    similarity: float  # Similarity score for the search result (0.0 to 1.0)
    source: str    # Source table (video_transcriptions, document_embeddings, video_transcriptions_full, 
                   # webpage_content, text_content, media_content)
    
    # Optional fields with defaults
    title: Optional[str] = None     # Content title
    start_time: Optional[str] = None  # Start timestamp for the content
    end_time: Optional[str] = None    # End timestamp for the content
    url: Optional[str] = None   # URL to content source
    segment_id: Optional[int] = None  # Segment identifier within a video
    summary: Optional[str] = None     # Summary text (primarily for document_embeddings)
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    search_method: Optional[str] = None  # Method used for search (keyword, dot_product, hybrid)
    content_type: Optional[str] = None  # Type of content (transcript, webpage, text, video, audio)

    @property
    def video_id(self) -> str:
        """
        Returns the content_id as video_id for backward compatibility.
        This property allows existing code to access video_id attribute.
        """
        return self.content_id

    @property
    def watch_url(self) -> Optional[str]:
        """
        Returns the URL as watch_url for backward compatibility.
        """
        return self.url

    @classmethod
    def from_db_result(cls, result: Dict[str, Any]) -> 'SearchResult':
        """Create a SearchResult instance from a database result dictionary.
        
        Args:
            result: Dictionary containing search result data from database
            
        Returns:
            SearchResult: Properly formatted search result object
        """
        source = result.get('source', 'unknown')
        
        # Common values for all content types
        content_id = result.get('video_id', result.get('content_id', ''))
        similarity = float(result.get('similarity', 0))
        content_type = result.get('content_type', 'unknown')
        url = result.get('url', result.get('watch_url', ''))
        title = result.get('title', 'Untitled')
        
        # Handle fields based on table structure
        if source == 'video_transcriptions':
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            summary = None
            segment_id = result.get('segment_id')
            start_time = result.get('start_time')
            end_time = result.get('end_time')
            content_type = 'transcript'
            
        elif source == 'document_embeddings':
            content = result.get('text', '')
            metadata = None
            summary = result.get('summary')
            segment_id = result.get('segment_id')
            start_time = result.get('start_time')
            end_time = result.get('end_time')
            content_type = 'document'
            
        elif source == 'video_transcriptions_full':
            content = result.get('full_transcript', '')
            if content:
                segments = content.split('\n')
                content = next((s for s in segments if s.strip() and not s.startswith('Segment')), content)
            metadata = {
                'context_before': result.get('context_before'),
                'context_after': result.get('context_after')
            }
            summary = result.get('summary')
            segment_id = result.get('segment_id')
            start_time = result.get('start_time') if result.get('start_time') else 'FULL'
            end_time = result.get('end_time') if result.get('end_time') else 'FULL'
            content_type = 'full_transcript'
            
        elif source == 'webpage_content':
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            summary = None
            segment_id = None
            start_time = None
            end_time = None
            content_type = 'webpage'
            
        elif source == 'text_content':
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            summary = None
            segment_id = None
            start_time = None
            end_time = None
            content_type = result.get('content_type', 'text')
            
        elif source == 'media_content':
            content = result.get('content', result.get('full_transcript', ''))
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            summary = None
            segment_id = None
            start_time = None 
            end_time = None
            # content_type already set from result
        else:
            content = result.get('content', '')
            metadata = {}
            summary = None
            segment_id = None
            start_time = None
            end_time = None

        return cls(
            content_id=str(content_id),
            content=content,
            similarity=similarity,
            source=source,
            title=title,
            start_time=start_time,
            end_time=end_time,
            url=url,
            segment_id=segment_id,
            summary=summary,
            metadata=metadata,
            search_method=result.get('search_method'),
            content_type=content_type
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SearchResult to a dictionary format ready for frontend consumption.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the SearchResult with all fields
            needed by the frontend UI component.
        """
        # Generate a unique ID for this result
        result_id = f"{self.content_id}_{self.segment_id or '0'}_{self.start_time or '0'}"
        
        return {
            'id': result_id,
            'content_id': self.content_id,
            'content': self.content,
            'similarity': self.similarity,
            'source': self.source,
            'title': self.title or '',
            'start_time': self.start_time,
            'end_time': self.end_time,
            'url': self.url or '',
            'segment_id': self.segment_id,
            'summary': self.summary or '',
            'metadata': self.metadata or {},
            'search_method': self.search_method or 'unknown',
            'content_type': self.content_type or 'unknown',
            # Additional fields for frontend UI
            'priority_score': self.similarity,
            'has_context': bool(self.metadata and 
                                (self.metadata.get('context_before') or 
                                self.metadata.get('context_after'))),
            'word_count': len(self.content.split()) if self.content else 0,
            'duration': f"{self.start_time or '0'} - {self.end_time or '0'}" if self.start_time and self.end_time else None
        }

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

# Initialize Rich console
console = Console()

# Supabase client singleton
_supabase_client = None

def get_client() -> Client:
    """
    Get a client for connecting to the Supabase database.
    Creates a singleton instance if not already created.
    """
    global _supabase_client
    if _supabase_client is None:
        # Initialize Supabase client if not already done
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY environment variable is not set")
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Initialized Supabase client singleton")
    return _supabase_client

# Global search parameters
class SearchParameters:
    """Manages adjustable search parameters."""
    
    def __init__(self, preset_name="default"):
        # Import here to avoid circular imports
        from .config.search_config import get_preset, DEFAULT_SEARCH_PARAMS
        import copy
        import logging
        
        self.logger = logging.getLogger("search_params")
        
        # Load parameters from config
        try:
            self.params = copy.deepcopy(get_preset(preset_name))
            self.logger.info(f"Loaded search parameters from preset: {preset_name}")
        except Exception as e:
            self.logger.error(f"Failed to load preset {preset_name}: {str(e)}, using defaults")
            self.params = copy.deepcopy(DEFAULT_SEARCH_PARAMS)
        
        # Ensure summary_weight is set (backward compatibility)
        for tier in self.params:
            if 'summary_weight' not in self.params[tier]:
                self.params[tier]['summary_weight'] = 1.0 - self.params[tier].get('content_weight', 0.5)
    
    def load_current(self):
        """Load the current search parameters.
        
        This is a compatibility method for code that expects to refresh parameters.
        The method doesn't actually reload anything as parameters are managed in memory.
        """
        self.logger.debug("load_current() called - parameters already loaded in memory")
        return True
    
    def update_params(self, tier: str, **kwargs):
        """Update parameters for a specific search tier."""
        import logging
        logger = logging.getLogger("search_params")
        
        if tier in self.params:
            logger.info(f"Updating {tier} search parameters")
            for key, value in kwargs.items():
                if key in self.params[tier]:
                    old_value = self.params[tier][key]
                    self.params[tier][key] = float(value)
                    logger.info(f"  - {tier}.{key}: {old_value:.2f} → {float(value):.2f}")
                    
                    # If content_weight is updated, update summary_weight to be complementary
                    if key == 'content_weight':
                        self.params[tier]['summary_weight'] = 1.0 - float(value)
                        logger.info(f"  - {tier}.summary_weight updated to: {self.params[tier]['summary_weight']:.2f}")
    
    def get_params(self, tier: str) -> dict:
        """Get parameters for a specific search tier."""
        return self.params.get(tier, {})
    
    def get_all_params(self) -> dict:
        """Get all search parameters."""
        return self.params
    
    def load_preset(self, preset_name: str) -> bool:
        """Load a predefined parameter preset.
        
        Args:
            preset_name: Name of the preset to load
            
        Returns:
            bool: True if preset was loaded, False otherwise
        """
        from .config.search_config import get_preset
        import copy
        import logging
        
        logger = logging.getLogger("search_params")
        
        try:
            preset = get_preset(preset_name)
            if not preset:
                logger.warning(f"Preset '{preset_name}' not found")
                return False
                
            old_params = copy.deepcopy(self.params)
            self.params = copy.deepcopy(preset)
            
            # Log the changes
            logger.info(f"Loaded preset: {preset_name}")
            for tier in self.params:
                for param, value in self.params[tier].items():
                    if tier in old_params and param in old_params[tier]:
                        old_value = old_params[tier][param]
                        if old_value != value:
                            logger.info(f"  - {tier}.{param}: {old_value:.2f} → {value:.2f}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load preset {preset_name}: {str(e)}")
            return False

    def update_from_frontend(
        self,
        fine_grained_similarity_threshold: float = None,
        fine_grained_content_weight: float = None,
        fine_grained_result_percentage: float = None,
        fine_grained_max_results: int = None,
        contextual_similarity_threshold: float = None,
        contextual_content_weight: float = None, 
        contextual_result_percentage: float = None,
        contextual_max_results: int = None,
        overview_similarity_threshold: float = None,
        overview_content_weight: float = None,
        overview_result_percentage: float = None,
        overview_max_results: int = None,
        preset: str = None
    ) -> bool:
        """Update search parameters based on frontend inputs.
        
        Args:
            fine_grained_similarity_threshold: Similarity threshold for fine-grained tier
            fine_grained_content_weight: Content weight for fine-grained tier
            fine_grained_result_percentage: Result percentage for fine-grained tier
            fine_grained_max_results: Maximum results for fine-grained tier
            contextual_similarity_threshold: Similarity threshold for contextual tier
            contextual_content_weight: Content weight for contextual tier
            contextual_result_percentage: Result percentage for contextual tier
            contextual_max_results: Maximum results for contextual tier
            overview_similarity_threshold: Similarity threshold for overview tier
            overview_content_weight: Content weight for overview tier
            overview_result_percentage: Result percentage for overview tier
            overview_max_results: Maximum results for overview tier
            preset: Optional preset name to load
            
        Returns:
            bool: True if parameters were updated successfully
        """
        import logging
        logger = logging.getLogger("search_params")
        
        # If preset is provided, load it first
        if preset:
            if self.load_preset(preset):
                logger.info(f"Loaded preset '{preset}' from frontend request")
            else:
                logger.warning(f"Failed to load preset '{preset}' from frontend request")
                
        # Create update dictionaries for each tier with only provided parameters
        updates = {
            'fine_grained': {},
            'contextual': {},
            'overview': {}
        }
        
        # Add parameters if they are provided (not None)
        if fine_grained_similarity_threshold is not None:
            updates['fine_grained']['similarity_threshold'] = fine_grained_similarity_threshold
        if fine_grained_content_weight is not None:
            updates['fine_grained']['content_weight'] = fine_grained_content_weight
        if fine_grained_result_percentage is not None:
            updates['fine_grained']['result_percentage'] = fine_grained_result_percentage
        if fine_grained_max_results is not None:
            updates['fine_grained']['max_results'] = fine_grained_max_results
            
        if contextual_similarity_threshold is not None:
            updates['contextual']['similarity_threshold'] = contextual_similarity_threshold
        if contextual_content_weight is not None:
            updates['contextual']['content_weight'] = contextual_content_weight
        if contextual_result_percentage is not None:
            updates['contextual']['result_percentage'] = contextual_result_percentage
        if contextual_max_results is not None:
            updates['contextual']['max_results'] = contextual_max_results
            
        if overview_similarity_threshold is not None:
            updates['overview']['similarity_threshold'] = overview_similarity_threshold
        if overview_content_weight is not None:
            updates['overview']['content_weight'] = overview_content_weight
        if overview_result_percentage is not None:
            updates['overview']['result_percentage'] = overview_result_percentage
        if overview_max_results is not None:
            updates['overview']['max_results'] = overview_max_results
        
        # Apply updates for each tier
        for tier, params in updates.items():
            if params:
                self.update_params(tier, **params)
                
        # Validate the settings after all updates
        from .config.search_config import validate_search_params
        if not validate_search_params(self.params):
            logger.warning("Updated search parameters contain invalid values")
            return False
            
        return True

# Initialize global search parameters
search_params = SearchParameters()

class TokenCounter:
    """Counts tokens for embeddings and LLM generation."""
    
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {
            'input': 0,
            'output': 0
        }
        try:
            self.encoders = {
                'cl100k_base': get_encoding('cl100k_base'),  # For text-embedding-3-small
                'gpt-4': get_encoding('cl100k_base'),  # For GPT-4 models
            }
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize encoders: {str(e)}[/yellow]")
            console.print("[yellow]Token counting will be disabled.[/yellow]")
            self.encoders = None
    
    def count_embedding_tokens(self, text: str) -> int:
        """Count tokens for embedding."""
        if not self.encoders:
            return 0
            
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            console.print(f"[yellow]Warning: Error counting tokens: {str(e)}[/yellow]")
            return 0 
            
    def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
        """Count tokens for generation (input and output)."""
        result = {'input': 0, 'output': 0}
        
        if not self.encoders:
            return result
            
        try:
            input_tokens = len(self.encoders['gpt-4'].encode(input_text))
            self.generation_tokens['input'] += input_tokens
            result['input'] = input_tokens
        
            if output_text:
                output_tokens = len(self.encoders['gpt-4'].encode(output_text))
                self.generation_tokens['output'] += output_tokens
                result['output'] = output_tokens
        except Exception as e:
            console.print(f"[yellow]Warning: Could not count generation tokens: {str(e)}[/yellow]")
        
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
            'chat': 'llama3-70b-8192',  # Updated to use the latest available Groq model
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
        # Enhanced system prompt with formatting instructions
        system_prompt = '''You are an AI system that analyzes search results from a database containing:
1. video_transcriptions: Individual video segments with timestamps
2. document_embeddings: Aggregated content chunks with summaries
3. video_transcriptions_full: Complete video transcripts
4. webpage_content: Content from web pages
5. text_content: Text documents and notes
6. media_content: Audio, video, and other media

Analyze search results by:
- Evaluating relevance to the query
- Extracting key information
- Identifying connections between results
- Providing a concise summary that helps the user understand the search results

FORMAT YOUR RESPONSE USING MARKDOWN:
- Use ### for main headings and #### for subheadings
- Use **bold** for important information
- Use numbered lists (1. 2. 3.) for sequential information
- Use bullet points (- ) for non-sequential items
- For YouTube video links, use the format: 🎬 Watch Here (do not include the URL in the link text)

Example format:
### Search Results Analysis
**Total Results Analyzed:** 2 **Source:** Video Transcriptions **Average Relevance Score:** 0.311

#### Detailed Results:
1. **Result 1** - **Source:** Video Transcriptions - **Score:** 0.344
   - **Content ID:** iG1Vxj2L_ZE
   - **Timestamp:** 00:00:11 to 00:00:24
   - **URL:** 🎬 Watch Here
   - **Content Summary:** Brief description of content

### Analysis
- **Relevance Evaluation:** Evaluation of relevance
- **Key Information:** Key information extracted
- **Connections:** Connections between results

### Conclusion
Summary of findings and recommendations'''
        
        try:
            # Estimate total tokens and truncate if needed
            token_per_char_estimate = 0.25  # Rough estimate of tokens per character
            max_tokens = 120000 if provider == 'openai' else 5000  # Conservative limits for OpenAI and Groq
            
            total_chars = len(system_prompt) + len(text)
            estimated_tokens = total_chars * token_per_char_estimate
            
            # Log token estimate
            console.print(f"[yellow]Estimated token count for {provider} analysis request: {estimated_tokens:.0f}[/yellow]")
            
            # Truncate text if it exceeds token limit
            if estimated_tokens > max_tokens:
                # Calculate how much to keep
                keep_ratio = (max_tokens / estimated_tokens) * 0.9  # 90% of the limit to be safe
                keep_chars = int(total_chars * keep_ratio)
                
                # Keep system prompt and truncate the text
                system_prompt_chars = len(system_prompt)
                text_chars_to_keep = keep_chars - system_prompt_chars
                
                if text_chars_to_keep < 500:
                    return f"Error: Content too large for analysis. Estimated {estimated_tokens:.0f} tokens exceeds {max_tokens} token limit."
                
                text = text[:text_chars_to_keep] + "\n...[Content truncated due to token limits]"
                console.print(f"[yellow]Content truncated to fit within token limits. Keeping approximately {text_chars_to_keep} characters.[/yellow]")
            
            # Count input tokens for stats
            token_counter.count_generation_tokens(system_prompt + text)
            
            if provider == 'openai':
                try:
                    response = openai_client.chat.completions.create(
                        model=ModelSelector.get_chat_model('openai'),
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=2000  # Limit response size
                    )
                    output_text = response.choices[0].message.content
                    # Count output tokens
                    token_counter.count_generation_tokens("", output_text)
                    return output_text
                except Exception as e:
                    error_msg = str(e)
                    if "maximum context length" in error_msg or "context_length_exceeded" in error_msg:
                        console.print(f"[red]OpenAI context length exceeded. Try reducing the number of search results.[/red]")
                        return "Error: The amount of search result data exceeds OpenAI's token limits. Please try a more specific search or reduce the number of results."
                    else:
                        console.print(f"[red]OpenAI error: {error_msg}[/red]")
                        return f"Error generating analysis: {error_msg}"
                
            elif provider == 'groq':
                try:
                    response = groq_client.chat.completions.create(
                        model=ModelSelector.get_chat_model('groq'),
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=1000  # Limit response size even more for Groq
                    )
                    output_text = response.choices[0].message.content
                    # Count output tokens
                    token_counter.count_generation_tokens("", output_text)
                    return output_text
                except Exception as e:
                    error_msg = str(e)
                    if "Request too large" in error_msg or "rate_limit_exceeded" in error_msg:
                        console.print(f"[red]Groq token limit exceeded. Try reducing the number of search results.[/red]")
                        return "Error: The amount of search result data exceeds Groq's token limits. Please try a more specific search or reduce the number of results."
                    else:
                        console.print(f"[red]Groq error: {error_msg}[/red]")
                        return f"Error generating analysis: {error_msg}"
            else:
                return "Error: Unsupported provider"
                
        except Exception as e:
            console.print(f"[red]Error generating analysis with {provider}: {str(e)}[/]")
            return f"Error generating analysis: {str(e)}"

def analyze_search_results(search_results, provider='openai', max_results=20):
    """Generate an analysis of search results using an LLM."""
    if not search_results:
        return "No results to analyze."
    
    # Sort results by similarity score
    sorted_results = sorted(search_results, key=lambda x: x.similarity, reverse=True)
    
    # Limit the number of results for analysis if needed
    if len(sorted_results) > max_results:
        logger.info(f"Limiting analysis to top {max_results} results (from {len(sorted_results)} total)")
        analysis_results = sorted_results[:max_results]
    else:
        analysis_results = sorted_results
    
    # Calculate total content length and estimate tokens
    total_text_length = sum(len(str(result.content)) for result in analysis_results)
    logger.info(f"Analysis content length: {total_text_length} characters")
    
    # Format the results for analysis
    text = "Search Results Analysis:\n\n"
    text += f"Total available results: {len(search_results)}\n"
    text += f"Analyzing top {len(analysis_results)} results sorted by relevance.\n\n"
    
    # Group results by source
    source_groups = {}
    for result in analysis_results:
        source = result.source
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(result)
    
    # Add statistics by source
    text += "Results by Source:\n"
    for source, results in source_groups.items():
        avg_score = sum(r.similarity for r in results) / len(results)
        text += f"- {source}: {len(results)} results, avg score: {avg_score:.3f}\n"
    
    text += "\nDetailed Results:\n\n"
    
    # Add each result with its details
    for i, result in enumerate(analysis_results, 1):
        text += f"Result {i}:\n"
        text += f"Source: {result.source}\n"
        text += f"Score: {result.similarity:.3f}\n"
        
        if result.title:
            text += f"Title: {result.title}\n"
            
        if result.content_id:
            text += f"Content ID: {result.content_id}\n"
            
        if result.segment_id is not None:
            text += f"Segment ID: {result.segment_id}\n"
            
        if result.start_time and result.end_time:
            text += f"Timestamp: {result.start_time} to {result.end_time}\n"
            
        if result.url:
            text += f"URL: {result.url}\n"
        
        # Add content with truncation for very long content
        content = str(result.content)
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
        text += f"Content: {content}\n"
        
        if result.summary:
            summary = str(result.summary)
            if len(summary) > 200:
                summary = summary[:200] + "... [summary truncated]"
            text += f"Summary: {summary}\n"
        
        text += "\n"
    
    # Generate the analysis
    console.print("\n[bold magenta]Generating analysis with " + provider + "...[/bold magenta]")
    return ModelSelector.generate_analysis(text, provider)

def save_results(results: List[SearchResult], query: str, format_choice: str, openai_analysis: str = None, groq_analysis: str = None):
    """Save search results and analyses to a file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_choice == 'markdown':
        filename = f"search_results_{timestamp}.md"
        
        # Create markdown content
        markdown_content = [
            f"# Search Results for: {query}",
            f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            
            "## 🔍 Individual Search Results\n",
        ]
        
        # Add results by search method
        for method in ['keyword', 'dot_product', 'hybrid']:
            method_results = [r for r in results if r.search_method == method]
            if method_results:
                # Get method style safely with fallback to default
                method_style = SEARCH_METHOD_STYLES.get(method, SEARCH_METHOD_STYLES['default'])
                method_icon = method_style['icon']
                
                markdown_content.extend([
                    f"\n### {method_icon} {method.replace('_', ' ').title()} Search Results",
                    "| Score | Method | Source | Video ID | Content | Summary | Segment ID | Metadata | Start Time | End Time | Watch URL |",
                    "|-------|--------|--------|----------|---------|---------|------------|----------|------------|-----------|-----------|",
                ])
                
                for result in method_results:
                    try:
                        score = f"{result.similarity:.3f}"
                        # Get method style safely
                        result_method_style = SEARCH_METHOD_STYLES.get(result.search_method, SEARCH_METHOD_STYLES['default'])
                        method_str = f"{result_method_style['icon']} {result.search_method}"
                        # Get source style safely
                        source_style = SOURCE_STYLES.get(result.source, SOURCE_STYLES['default'])
                        source_str = f"{source_style['icon']} {result.source}"
                        
                        content = str(result.content).replace('|', '\\|').replace('\n', ' ')[:200] + '...'
                        summary = str(result.summary).replace('|', '\\|') if result.summary else "N/A"
                        metadata = str(result.metadata).replace('|', '\\|') if result.metadata else "N/A"
                        
                        markdown_content.append(
                            f"| {score} | {method_str} | {source_str} | {result.video_id} | {content} | {summary} | "
                            f"{result.segment_id or 'N/A'} | {metadata} | {result.start_time or 'N/A'} | "
                            f"{result.end_time or 'N/A'} | {result.watch_url or 'N/A'} |"
                        )
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not format result: {str(e)}[/yellow]")
                        continue
        
        # Add Combined Results section
        markdown_content.extend([
            "\n## 📊 Combined Results\n",
            "### Statistics",
            "```",
            f"Total Results: {len(results)}",
            f"Average Score: {sum(r.similarity for r in results)/len(results):.3f}",
            "```\n",
            "### Results Table",
            "| Score | Method | Source | Video ID | Content | Summary | Segment ID | Metadata | Start Time | End Time | Watch URL |",
            "|-------|--------|--------|----------|---------|---------|------------|----------|------------|-----------|-----------|",
        ])
        
        # Add all results sorted by score
        for result in sorted(results, key=lambda x: x.similarity, reverse=True):
            try:
                score = f"{result.similarity:.3f}"
                method_str = f"{SEARCH_METHOD_STYLES.get(result.search_method, SEARCH_METHOD_STYLES['default'])['icon']} {result.search_method}"
                source_str = f"{SOURCE_STYLES.get(result.source, SOURCE_STYLES['default'])['icon']} {result.source}"
                content = str(result.content).replace('|', '\\|').replace('\n', ' ')[:200] + '...'
                summary = str(result.summary).replace('|', '\\|') if result.summary else "N/A"
                metadata = str(result.metadata).replace('|', '\\|') if result.metadata else "N/A"
                
                markdown_content.append(
                    f"| {score} | {method_str} | {source_str} | {result.video_id} | {content} | {summary} | "
                    f"{result.segment_id or 'N/A'} | {metadata} | {result.start_time or 'N/A'} | "
                    f"{result.end_time or 'N/A'} | {result.watch_url or 'N/A'} |"
                )
            except Exception as e:
                console.print(f"[yellow]Warning: Could not format result: {str(e)}[/yellow]")
                continue
        
        # Add AI Analyses
        if openai_analysis or groq_analysis:
            markdown_content.append("\n## 🤖 AI Analysis\n")
            
        if openai_analysis:
            markdown_content.extend([
                "### OpenAI Analysis",
                "```",
                openai_analysis,
                "```\n"
            ])
            
        if groq_analysis:
            markdown_content.extend([
                "### Groq Analysis",
                "```",
                groq_analysis,
                "```\n"
            ])
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(markdown_content))
            console.print(f"[green]Results saved to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving to markdown file: {str(e)}[/red]")
            
    elif format_choice in ['csv', 'excel']:
        try:
            # Create DataFrame from results
            df = create_results_df(results)
            
            if format_choice == 'csv':
                filename = f"search_results_{timestamp}.csv"
                df.to_csv(filename, index=False)
            else:
                filename = f"search_results_{timestamp}.xlsx"
                df.to_excel(filename, index=False)
                
            console.print(f"[green]Results saved to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving to {format_choice} file: {str(e)}[/red]")

def search_all(query, max_results=30, skip_prompts=False, run_analysis=True):
    """Perform a comprehensive search across all available sources and methods."""
    # Initialize results lists
    all_results = []
    dot_product_results = []
    keyword_results = []
    hybrid_results = []
    seen_ids = set()  # Track IDs to avoid duplicates
    
    # Track token usage
    token_usage = {
        'embedding_tokens': 0,
        'generation_tokens': {
            'input': 0,
            'output': 0
        }
    }
    
    # Create a client
    client = get_client()
    
    # Initialize RichConsole for nice output
    console = Console()
    
    # Create token counter
    token_counter = TokenCounter()
    
    # Start timing
    start_time = time.time()
    
    # Status message
    console.print(f"\n[bold cyan]Searching for:[/bold cyan] {query}")
    
    # Search methods to run
    methods = ["dot_product", "keyword"]
    
    # Display parameters
    search_params = SearchParameters()
    search_params.load_current()
    all_params = search_params.get_all_params()
    
    # Only show parameters if not skipping prompts
    if not skip_prompts:
        console.print("\n[bold cyan]Search parameters:[/bold cyan]")
        for tier, params in all_params.items():
            console.print(f"\n[cyan]{tier.title()}:[/cyan]")
            for param, value in params.items():
                console.print(f"  {param}: {value}")
    
    # Convert embedding and track tokens
    try:
        embedding_start = time.time()
        # Use OpenAI client directly for embeddings instead of Supabase client
        embedding = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small",
            dimensions=1536
        ).data[0].embedding
        
        # Count tokens for embedding
        token_counter.count_embedding_tokens(query)
        
        embedding_time = time.time() - embedding_start
        console.print(f"[blue]Embedding generated in {embedding_time:.2f}s[/blue]")
    except Exception as e:
        console.print(f"[red]Error generating embedding: {str(e)}[/red]")
        return [], None, None
    
    # Run dot product search (vector similarity)
    try:
        # Get parameters for each search tier
        fine_grained_params = search_params.get_params("fine_grained")
        contextual_params = search_params.get_params("contextual") 
        overview_params = search_params.get_params("overview")
        
        # Run dot product search on video transcriptions (fine-grained segments)
        fine_grained_start = time.time()
        fine_grained_results = client.rpc(
            'dot_product_search',
            {
                'query_embedding': embedding,
                'match_count': int(max_results * fine_grained_params["result_percentage"]),
                'content_weight': fine_grained_params["content_weight"],
                'summary_weight': fine_grained_params.get("summary_weight", 1.0 - fine_grained_params["content_weight"])
            }
        ).execute().data
        fine_grained_time = time.time() - fine_grained_start
        
        # Create SearchResult objects
        for r in fine_grained_results:
            r["search_method"] = "dot_product"
            r["source"] = "video_transcriptions"
            result = SearchResult.from_db_result(r)
            dot_product_results.append(result)
        
        # Run dot product search on document embeddings (contextual segments)
        contextual_start = time.time()
        contextual_results = client.rpc(
            'dot_product_search',
            {
                'query_embedding': embedding,
                'match_count': int(max_results * contextual_params["result_percentage"]),
                'content_weight': contextual_params["content_weight"],
                'summary_weight': contextual_params.get("summary_weight", 1.0 - contextual_params["content_weight"])
            }
        ).execute().data
        contextual_time = time.time() - contextual_start
        
        # Create SearchResult objects
        for r in contextual_results:
            r["search_method"] = "dot_product"
            r["source"] = "document_embeddings"
            result = SearchResult.from_db_result(r)
            dot_product_results.append(result)
            
        # Run dot product search on full transcripts (overview)
        overview_start = time.time()
        overview_results = client.rpc(
            'dot_product_search',
            {
                'query_embedding': embedding,
                'match_count': int(max_results * overview_params["result_percentage"]),
                'content_weight': overview_params["content_weight"],
                'summary_weight': overview_params.get("summary_weight", 1.0 - overview_params["content_weight"])
            }
        ).execute().data
        overview_time = time.time() - overview_start
        
        # Create SearchResult objects
        for r in overview_results:
            r["search_method"] = "dot_product"
            r["source"] = "video_transcriptions_full"
            result = SearchResult.from_db_result(r)
            dot_product_results.append(result)
        
        # Report on vector search results
        console.print(f"[green]Fine-grained segments: {len(fine_grained_results)} results in {fine_grained_time:.2f}s[/green]")
        console.print(f"[green]Contextual segments: {len(contextual_results)} results in {contextual_time:.2f}s[/green]")
        console.print(f"[green]Overview segments: {len(overview_results)} results in {overview_time:.2f}s[/green]")
        
        # Add all dot product results to the combined set
        for result in dot_product_results:
            result_id = f"{result.content_id}_{result.segment_id or '0'}"
            if result_id not in seen_ids:
                all_results.append(result)
                seen_ids.add(result_id)
                
    except Exception as e:
        console.print(f"[red]Error during vector search: {str(e)}[/red]")
        traceback.print_exc()
    
    # Run keyword search
    try:
        keyword_start = time.time()
        keyword_results_raw = client.rpc(
            'keyword_search',
            {
                'query_text': query,
                'match_count': max_results
            }
        ).execute().data
        keyword_time = time.time() - keyword_start
        
        # Create SearchResult objects
        for r in keyword_results_raw:
            r["search_method"] = "keyword"
            r["source"] = "video_transcriptions"
            result = SearchResult.from_db_result(r)
            keyword_results.append(result)
        
        console.print(f"[green]Keyword search: {len(keyword_results_raw)} results in {keyword_time:.2f}s[/green]")
        
        # Add keyword results to the combined set, tracking IDs to avoid duplicates
        for result in keyword_results:
            result_id = f"{result.content_id}_{result.segment_id or '0'}"
            if result_id not in seen_ids:
                all_results.append(result)
                seen_ids.add(result_id)
                
    except Exception as e:
        console.print(f"[red]Error during keyword search: {str(e)}[/red]")
        traceback.print_exc()
    
    # Try hybrid search (experimental)
    try:
        # Only run hybrid search if we have both dot product and keyword results
        if dot_product_results and keyword_results:
            hybrid_start = time.time()
            
            # Get common video IDs
            dot_product_ids = set(r.content_id for r in dot_product_results)
            keyword_ids = set(r.content_id for r in keyword_results)
            common_ids = dot_product_ids.intersection(keyword_ids)
            
            # For common IDs, create hybrid results with boosted similarity scores
            for video_id in common_ids:
                # Get the best dot product result for this video
                best_dot_product = max(
                    [r for r in dot_product_results if r.content_id == video_id],
                    key=lambda x: x.similarity
                )
                
                # Get the best keyword result for this video
                best_keyword = max(
                    [r for r in keyword_results if r.content_id == video_id],
                    key=lambda x: x.similarity
                )
                
                # Create a hybrid result with boosted score
                hybrid_similarity = min(1.0, best_dot_product.similarity * 1.2)
                
                # Use the dot product result as the base but boost its score
                hybrid_result = copy.deepcopy(best_dot_product)
                hybrid_result.similarity = hybrid_similarity
                hybrid_result.search_method = "hybrid"
                
                # Add to hybrid results
                hybrid_results.append(hybrid_result)
            
            hybrid_time = time.time() - hybrid_start
            console.print(f"[green]Hybrid search: {len(hybrid_results)} results in {hybrid_time:.2f}s[/green]")
            
            # Add hybrid results to the combined set
            for result in hybrid_results:
                result_id = f"{result.content_id}_{result.segment_id or '0'}_hybrid"  # Use special ID to avoid filtering out
                if result_id not in seen_ids:
                    all_results.append(result)
                    seen_ids.add(result_id)
    
    except Exception as e:
        console.print(f"[red]Error during hybrid search: {str(e)}[/red]")
        traceback.print_exc()
    
    # Display top results
    if all_results:
        console.print("\n[bold yellow]Top Results:[/]")
        for i, result in enumerate(all_results[:5], 1):
            title = result.title if result.title else "No title"
            similarity = result.similarity if result.similarity is not None else 0
            
            search_method = result.search_method if result.search_method else "unknown"
            method_style = SEARCH_METHOD_STYLES.get(search_method, SEARCH_METHOD_STYLES['default'])
            
            source = result.source if result.source else "unknown"
            source_style = SOURCE_STYLES.get(source, SOURCE_STYLES['default'])
            
            # Style the score based on its value
            score_color = "green" if similarity > 0.8 else "yellow" if similarity > 0.6 else "red"
            
            # Print result with better formatting
            console.print(f"[bold]{i}.[/bold] [bold {score_color}]{similarity:.3f}[/bold {score_color}] "
                        f"[{method_style['color']}]{method_style['icon']} {search_method}[/{method_style['color']}] "
                        f"[{source_style['color']}]{source_style['icon']} {source}[/{source_style['color']}] "
                        f"[bold blue]{title}[/bold blue]")
            
            # Show content snippet
            content = result.content if result.content else ""
            if len(content) > 100:
                content = content[:100] + "..."
            console.print(f"   {content}")
            
            # Show video ID and timestamp if available
            if result.content_id:
                timestamp_info = f" ({result.start_time}-{result.end_time})" if result.start_time and result.end_time else ""
                console.print(f"   ID: {result.content_id}{timestamp_info}")
            
            console.print("")  # Empty line between results
    else:
        console.print("\n[yellow]No results found.[/yellow]")
    
    # End timing
    end_time = time.time()
    total_time = end_time - start_time
    console.print(f"\n[bold cyan]Search completed in {total_time:.2f} seconds[/bold cyan]")
    
    # Get token usage
    token_usage['embedding_tokens'] = token_counter.embedding_tokens
    token_usage['generation_tokens'] = token_counter.generation_tokens
    
    # Display token usage
    console.print(f"\n[bold cyan]Token usage:[/bold cyan]")
    console.print(f"[blue]Embedding Tokens:[/] {token_usage['embedding_tokens']:,}")
    
    # Run analysis with OpenAI and Groq if specified
    openai_analysis = None
    groq_analysis = None
    
    if run_analysis and all_results:
        console.print("\n[bold cyan]Running analysis...[/bold cyan]")
        
        # OpenAI Analysis
        try:
            openai_analysis = analyze_search_results(all_results, provider='openai')
            console.print(f"[blue]Generation Input Tokens:[/] {token_usage['generation_tokens']['input']:,}")
            console.print(f"[blue]Generation Output Tokens:[/] {token_usage['generation_tokens']['output']:,}")
        except Exception as e:
            console.print(f"\n[red]OpenAI Analysis Error: {str(e)}[/red]")
        
        # Groq Analysis
        try:
            groq_analysis = analyze_search_results(all_results, provider='groq', max_results=10)
        except Exception as e:
            console.print(f"\n[red]Groq Analysis Error: {str(e)}[/red]")
    else:
        console.print("\n[bold yellow]Analysis phase skipped[/]")
    
    # Option to save results
    if not skip_prompts:
        save_option = input("\nSave results? (Y/n): ").strip().lower()
        if save_option != 'n':
            format_options = {
                'md': 'Markdown',
                'json': 'JSON',
                'csv': 'CSV',
                'xlsx': 'Excel'
            }
            
            # Display format options
            console.print("\n[cyan]Available formats:[/cyan]")
            for key, name in format_options.items():
                console.print(f"  {key}: {name}")
                
            format_choice = input("Choose format (default: md): ").strip().lower()
            if not format_choice:
                format_choice = 'md'
                
            if format_choice in format_options:
                save_results(all_results, query, format_choice, openai_analysis, groq_analysis)
            else:
                console.print(f"[yellow]Invalid format choice. Using default (md).[/yellow]")
                save_results(all_results, query, 'md', openai_analysis, groq_analysis)
    
    return all_results, openai_analysis, groq_analysis

def display_results_table(results: List[SearchResult], title: str):
    """Display search results using pandas data handling with rich table display."""
    if not results:
        console.print("[yellow]No results to display.[/yellow]")
        return

    # Create DataFrame
    df = create_results_df(results)
    
    # Create rich table with same styling as before
    table = Table(
        title=f"{TABLE_STYLES['title']['icon']} [bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style=TABLE_STYLES['header']['style'],
        width=None,
        box=DOUBLE_EDGE,
        border_style=TABLE_STYLES['border']['style']
    )
    
    # Add columns in correct order
    table.add_column("Score", justify=TABLE_STYLES['columns']['score']['justify'],
                    style=TABLE_STYLES['columns']['score']['style'],
                    width=TABLE_STYLES['columns']['score']['width'])
    table.add_column("Method", style=TABLE_STYLES['columns']['method']['style'],
                    width=TABLE_STYLES['columns']['method']['width'])
    table.add_column("Source", style=TABLE_STYLES['columns']['source']['style'],
                    width=TABLE_STYLES['columns']['source']['width'])
    table.add_column("Video ID", style=TABLE_STYLES['columns']['video_id']['style'],
                    width=TABLE_STYLES['columns']['video_id']['width'])
    table.add_column("Content", style=TABLE_STYLES['columns']['content']['style'],
                    width=TABLE_STYLES['columns']['content']['width'])
    table.add_column("Summary", style=TABLE_STYLES['columns']['metadata']['style'],
                    width=TABLE_STYLES['columns']['metadata']['width'])
    table.add_column("Segment ID", style=TABLE_STYLES['columns']['segment_id']['style'],
                    width=TABLE_STYLES['columns']['segment_id']['width'])
    table.add_column("Metadata", style=TABLE_STYLES['columns']['metadata']['style'],
                    width=TABLE_STYLES['columns']['metadata']['width'])
    table.add_column("Start Time", style=TABLE_STYLES['columns']['start_time']['style'],
                    width=TABLE_STYLES['columns']['start_time']['width'])
    table.add_column("End Time", style=TABLE_STYLES['columns']['end_time']['style'],
                    width=TABLE_STYLES['columns']['end_time']['width'])
    table.add_column("Watch URL", style=TABLE_STYLES['columns']['watch_url']['style'],
                    width=TABLE_STYLES['columns']['watch_url']['width'])
    
    # Add rows with formatted data
    for _, row in df.iterrows():
        formatted_data = format_row_data(row)
        table.add_row(
            formatted_data['score'],
            formatted_data['method'],
            formatted_data['source'],
            formatted_data['video_id'],
            formatted_data['content'],
            formatted_data['summary'],
            formatted_data['segment_id'],
            formatted_data['metadata'],
            formatted_data['start_time'],
            formatted_data['end_time'],
            formatted_data['watch_url']
        )
    
    # Display with same formatting as before
    console.print("\n")
    console.print(table)
    console.print(f"{STATUS_INDICATORS['success']} [green]Found {len(results)} results[/green]")
    console.print("\n")

def display_tier_results(results: List[SearchResult], tier_name: str):
    """Display search results for a specific tier."""
    if not results:
        console.print(f"\n[yellow]No results found for {tier_name} tier.[/yellow]")
        return

    # Create a table for this tier
    table = Table(
        title=f"[bold cyan]{tier_name.title()} Tier Results[/bold cyan]",
        show_header=True,
        header_style="bold magenta"
    )
    
    # Add columns
    table.add_column("Score", justify="right", style="cyan")
    table.add_column("Content", style="green")
    table.add_column("Source", style="yellow")
    table.add_column("Timestamp", style="blue")
    
    # Add rows
    for result in results:
        content = result.content[:200] + '...' if len(result.content) > 200 else result.content
        timestamp = f"{result.start_time} - {result.end_time}"
        
        table.add_row(
            f"{result.similarity:.3f}",
            content,
            result.source,
            timestamp
        )
    
    console.print(table)
    console.print(f"\nParameters used for {tier_name} tier:")
    params = search_params.get_params(tier_name.lower())
    for key, value in params.items():
        console.print(f"  {key}: {value}")

def display_results(results: List[SearchResult], show_by_type: bool = True):
    """Display search results in a formatted table."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    # Display token usage stats
    token_counter.log_stats()

    # Limit the number of results sent for analysis to prevent token overflows
    max_results_for_analysis = 20  # Reasonable limit to prevent token overflow
    if len(results) > max_results_for_analysis:
        console.print(f"[yellow]Warning: Limiting analysis to the top {max_results_for_analysis} most relevant results (out of {len(results)}) to prevent token overflow.[/yellow]")
        analysis_results = sorted(results, key=lambda r: r.similarity if r.similarity is not None else 0, reverse=True)[:max_results_for_analysis]
    else:
        analysis_results = results

    # Generate AI analysis using both providers
    console.print("\n[bold cyan]Generating comprehensive analysis...[/bold cyan]")
    
    # Try OpenAI analysis first
    try:
        openai_analysis = analyze_search_results(analysis_results, 'openai')
        console.print("\n[bold green]OpenAI Analysis:[/bold green]")
        if "Error" in openai_analysis and ("token" in openai_analysis or "context length" in openai_analysis):
            console.print(Panel(str(openai_analysis), title="OpenAI Analysis", border_style="yellow", highlight=True))
            
            # If we encounter token limits, try with even fewer results
            if len(analysis_results) > 10:
                console.print("[yellow]Retrying OpenAI analysis with fewer results...[/yellow]")
                retry_results = analysis_results[:10]
                retry_analysis = analyze_search_results(retry_results, 'openai')
                console.print(Panel(str(retry_analysis), title="OpenAI Analysis (Retry with 10 results)", border_style="green", highlight=True))
        else:
            console.print(Panel(str(openai_analysis), title="OpenAI Analysis", border_style="green", highlight=True))
        
        # Display referenced URLs in a separate panel
        urls = [r.watch_url for r in results if r.watch_url]
        if urls:
            console.print("\n[bold green]Referenced Watch URLs:[/bold green]")
            for idx, url in enumerate(urls[:10], 1):  # Limit to top 10 URLs
                console.print(f"[{idx}] [blue][link={url}]{url}[/link][/blue]")
            if len(urls) > 10:
                console.print(f"[yellow]... and {len(urls) - 10} more URLs[/yellow]")
    except Exception as e:
        console.print(f"\n[red]OpenAI Analysis Error: {str(e)}[/red]")

    # Try Groq analysis
    try:
        groq_analysis = analyze_search_results(analysis_results, 'groq')
        console.print("\n[bold blue]Groq Analysis:[/bold blue]")
        if "Error" in groq_analysis and ("token" in groq_analysis or "too large" in groq_analysis):
            console.print(Panel(str(groq_analysis), title="Groq Analysis", border_style="yellow"))
            
            # If we encounter token limits, try with even fewer results
            if len(analysis_results) > 5:
                console.print("[yellow]Retrying Groq analysis with fewer results...[/yellow]")
                retry_results = analysis_results[:5]  # Groq has stricter limits, so use fewer results
                retry_analysis = analyze_search_results(retry_results, 'groq')
                console.print(Panel(str(retry_analysis), title="Groq Analysis (Retry with 5 results)", border_style="blue"))
        else:
            console.print(Panel(str(groq_analysis), title="Groq Analysis", border_style="blue"))
    except Exception as e:
        console.print(f"\n[red]Groq Analysis Error: {str(e)}[/red]")
    
    # Continue with the original results display
    def create_table():
        table = Table(show_header=True, header_style="bold magenta", width=None)
        table.add_column("Content", style="white", max_width=60)
        table.add_column("Source", style="yellow")
        table.add_column("Score", style="cyan", justify="right")
        table.add_column("Video ID", style="green")
        table.add_column("Segment ID", style="blue")
        table.add_column("Timestamp", style="magenta")
        
        # Sort by score
        sorted_results = sorted(results, key=lambda x: x.similarity if x.similarity is not None else 0, reverse=True)
        
        # Add rows
        for result in sorted_results:
            # Format content (truncate if needed)
            content = result.content
            if content and len(content) > 60:
                content = content[:57] + "..."
            
            # Format timestamp
            timestamp = ""
            if result.start_time and result.end_time:
                timestamp = f"{result.start_time} - {result.end_time}"
            
            # Format score
            score = f"{result.similarity:.3f}" if result.similarity is not None else "N/A"
            
            source_order = [
                'video_transcriptions', 
                'document_embeddings', 
                'video_transcriptions_full',
                'webpage_content',
                'text_content',
                'media_content'
            ]
            
            # Add row
            table.add_row(
                content or "No content",
                result.source or "Unknown",
                score,
                result.content_id or "N/A",
                str(result.segment_id) if result.segment_id is not None else "N/A",
                timestamp or "N/A"
            )
        
        return table

    if show_by_type:
        # Group results by source
        results_by_source = {}
        for result in results:
            source = result.source
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)

        # Display results for each source
        source_order = [
            'video_transcriptions', 
            'document_embeddings', 
            'video_transcriptions_full',
            'webpage_content',
            'text_content',
            'media_content'
        ]
        for source in source_order:
            if source in results_by_source:
                source_results = results_by_source[source]
                console.print(f"\n[bold blue]Results from {source}:[/bold blue]")
                display_results_table(source_results, f"{source} Results")
                console.print(f"[green]Found {len(source_results)} results from {source}[/green]")

    # Display combined results
    console.print("\n[bold blue]Combined Search Results:[/bold blue]")
    display_results_table(results, "Combined Results")
    console.print(f"\n[green]Total results: {len(results)}[/green]")

def format_full_transcript(transcript: str, max_length: int = 200) -> str:
    """Format the full transcript for display."""
    if not transcript:
        return ""
        
    # Split into segments
    segments = transcript.split("Segment ")
    segments = [s for s in segments if s.strip()]  # Remove empty segments
    
    if not segments:
        return transcript[:max_length] + "..." if len(transcript) > max_length else transcript
        
    # Take first segment and format it
    try:
        first_segment = segments[0]
        header, content = first_segment.split(":", 1)
        timestamp = header[header.find("(")+1:header.find(")")]
        content = content.strip()
        
        # Format as a single line with timestamp
        formatted = f"{timestamp}: {content}"
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "..."
            
        # Add segment count if there are more
        if len(segments) > 1:
            formatted += f" ({len(segments)} segments total)"
            
        return formatted
        
    except:
        # Fallback to simple truncation if parsing fails
        return transcript[:max_length] + "..."

def display_search_statistics(results: List[SearchResult]):
    """Display statistics about the search results."""
    if not results:
        return

    # Count results by source
    source_counts = defaultdict(int)
    for result in results:
        source_counts[result.source] += 1

    # Calculate average similarity
    avg_similarity = sum(r.similarity for r in results) / len(results)

    # Create statistics table
    table = Table(title="[bold cyan]Search Results Statistics[/bold cyan]")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    # Add rows
    table.add_row("Total Results", str(len(results)))
    table.add_row("Average Similarity", f"{avg_similarity:.3f}")
    
    # Add source breakdowns
    for source, count in source_counts.items():
        table.add_row(f"Results from {source}", str(count))

    console.print(table)

def create_results_df(results: List[SearchResult]) -> pd.DataFrame:
    """Create pandas DataFrame from search results."""
    return pd.DataFrame([{
        'Score': result.similarity,
        'Method': result.search_method,
        'Source': result.source,
        'Video ID': result.video_id,
        'Content': result.content,
        'Summary': result.summary if result.source == 'document_embeddings' else None,
        'Segment ID': result.segment_id,
        'Metadata': result.metadata,
        'Start Time': result.start_time,
        'End Time': result.end_time,
        'Watch URL': result.watch_url
    } for result in results])

def format_row_data(row: pd.Series) -> Dict[str, str]:
    """Format row data for display based on source type."""
    max_width = TABLE_STYLES['columns']['content']['width']
    
    # Format score with color based on threshold
    score = float(row['Score'])
    if score >= SCORE_STYLES['high']['threshold']:
        score_style = SCORE_STYLES['high']['style']
        description = SCORE_STYLES['high']['description']
    elif score >= SCORE_STYLES['medium']['threshold']:
        score_style = SCORE_STYLES['medium']['style']
        description = SCORE_STYLES['medium']['description']
    elif score >= SCORE_STYLES['low']['threshold']:
        score_style = SCORE_STYLES['low']['style']
        description = SCORE_STYLES['low']['description']
    else:
        score_style = SCORE_STYLES['default']['style']
        description = SCORE_STYLES['default']['description']
    formatted_score = f"[{score_style}]{score:.3f}[/] ({description})"

    # Format content based on source type
    if row['Source'] == 'video_transcriptions':
        # Format individual segment with line numbers from metadata
        content = str(row['Content'])
        line_num = row['Metadata'].get('line_number', '') if pd.notna(row['Metadata']) else ''
        segment_info = f"[Line {line_num}] " if line_num else ""
        if len(content) > max_width - len(segment_info):
            content = f"{segment_info}{content[:max_width-len(segment_info)]}..."
        else:
            content = f"{segment_info}{content}"
            
    elif row['Source'] == 'document_embeddings':
        # Show document chunk content
        content = str(row['Content'])
        if len(content) > max_width:
            content = content[:max_width] + "..."
            
    elif row['Source'] == 'video_transcriptions_full':
        # Show truncated content for display
        content = str(row['Content'])
        if len(content) > max_width:
            content = content[:max_width] + "..."
            
    elif row['Source'] == 'webpage_content':
        # Format webpage content with URL info if available
        content = str(row['Content'])
        url_info = f"[URL: {row['Metadata'].get('url', '')}] " if pd.notna(row['Metadata']) and 'url' in row['Metadata'] else ""
        if len(content) > max_width - len(url_info):
            content = f"{url_info}{content[:max_width-len(url_info)]}..."
        else:
            content = f"{url_info}{content}"
            
    elif row['Source'] == 'text_content':
        # Format text content with title if available
        content = str(row['Content'])
        title_info = f"[{row['Metadata'].get('title', '')}] " if pd.notna(row['Metadata']) and 'title' in row['Metadata'] else ""
        if len(content) > max_width - len(title_info):
            content = f"{title_info}{content[:max_width-len(title_info)]}..."
        else:
            content = f"{title_info}{content}"
            
    elif row['Source'] == 'media_content':
        # Format media content with file path and content type
        content = str(row['Content'])
        media_info = ""
        if pd.notna(row['Metadata']):
            file_path = row['Metadata'].get('file_path', '')
            content_type = row['Metadata'].get('content_type', '')
            if file_path or content_type:
                media_info = f"[{content_type}: {file_path}] "
        
        if len(content) > max_width - len(media_info):
            content = f"{media_info}{content[:max_width-len(media_info)]}..."
        else:
            content = f"{media_info}{content}"
    else:
        content = str(row['Content'])[:max_width] + "..." if len(str(row['Content'])) > max_width else str(row['Content'])

    # Get watch_url directly from database field without truncation
    watch_url = str(row['Watch URL']) if pd.notna(row['Watch URL']) else "N/A"

    return {
        'score': formatted_score,
        'method': f"{SEARCH_METHOD_STYLES.get(row['Method'], SEARCH_METHOD_STYLES['default'])['icon']} {row['Method']}" if row['Method'] else "unknown",
        'source': f"{SOURCE_STYLES.get(row['Source'], SOURCE_STYLES['default'])['icon']} {row['Source']}" if row['Source'] else "unknown",
        'video_id': str(row['Video ID']),
        'content': content,
        'summary': str(row['Summary']) if row['Source'] == 'document_embeddings' and pd.notna(row['Summary']) else "N/A",
        'segment_id': str(row['Segment ID']) if pd.notna(row['Segment ID']) else "N/A",
        'metadata': format_metadata_by_source(row),
        'start_time': str(row['Start Time']) if pd.notna(row['Start Time']) else "N/A",
        'end_time': str(row['End Time']) if pd.notna(row['End Time']) else "N/A",
        'watch_url': watch_url  # Preserve full watch_url without truncation
    }

def format_metadata_by_source(row: pd.Series) -> str:
    """Format metadata based on source type."""
    if row['Source'] == 'video_transcriptions':
        return str(row['Metadata']) if pd.notna(row['Metadata']) else "N/A"
    elif row['Source'] == 'video_transcriptions_full':
        if pd.notna(row['Metadata']):
            return str({
                'context_before': row['Metadata'].get('context_before'),
                'context_after': row['Metadata'].get('context_after')
            })
    return "N/A"

def display_results_pandas(results: List[SearchResult], title: str):
    """Display search results using pandas with interactive options."""
    if not results:
        console.print("[yellow]No results to display.[/yellow]")
        return

    # Create DataFrame
    df = create_results_df(results)
    
    # Display title and options
    console.print(f"\n{TABLE_STYLES['title']['icon']} [bold cyan]{title}[/bold cyan]")
    
    while True:
        # Show options menu
        console.print("\n[cyan]Options:[/cyan]")
        console.print("1. View all results")
        console.print("2. Sort results")
        console.print("3. Filter results")
        console.print("4. Export results")
        console.print("5. Show statistics")
        console.print("6. Return to main menu")
        
        choice = Prompt.ask("Select option", choices=['1', '2', '3', '4', '5', '6'], default='1')
        
        if choice == '1':
            # Display full results
            console.print("\n[bold cyan]Results:[/bold cyan]")
            console.print(df.to_string())
            
        elif choice == '2':
            # Sorting options
            sort_by = Prompt.ask(
                "Sort by",
                choices=['Score', 'Method', 'Source', 'none'],
                default='Score'
            )
            if sort_by != 'none':
                ascending = Prompt.ask("Order", choices=['ascending', 'descending'], default='descending')
                df = df.sort_values(by=sort_by, ascending=(ascending == 'ascending'))
                console.print(df.to_string())
                
        elif choice == '3':
            # Filtering options
            filter_by = Prompt.ask(
                "Filter by source",
                choices=['all', 'video_transcriptions', 'document_embeddings', 'video_transcriptions_full'],
                default='all'
            )
            if filter_by != 'all':
                filtered_df = df[df['Source'].str.contains(filter_by)]
                console.print(filtered_df.to_string())
                
        elif choice == '4':
            # Export options
            format_choice = Prompt.ask("Export format", choices=['csv', 'excel'], default='csv')
            filename = Prompt.ask("Filename", default=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            if format_choice == 'csv':
                df.to_csv(f"{filename}.csv", index=False)
                console.print(f"[green]Results exported to {filename}.csv[/green]")
            else:
                df.to_excel(f"{filename}.xlsx", index=False)
                console.print(f"[green]Results exported to {filename}.xlsx[/green]")
                
        elif choice == '5':
            # Display statistics
            console.print("\n[bold cyan]Statistics:[/bold cyan]")
            stats = {
                'Total Results': len(df),
                'Average Score': df['Score'].astype(float).mean(),
                'Sources': df['Source'].nunique(),
                'Methods': df['Method'].nunique()
            }
            stats_df = pd.DataFrame([stats])
            console.print(stats_df.to_string())
            
        else:
            break

def main():
    """Main function for the terminal interface"""
    search_params.load_current()
    
    # Whether to run analysis by default
    run_analysis = True
    
    # Main menu loop
    while True:
        console.print("\n[bold cyan]P-SEARCH Vector Search Tool[/bold cyan]")
        console.print("[cyan]=================================[/cyan]")
        console.print("1. [bold]Search[/bold] - Execute a search")
        console.print("2. [bold]Parameters[/bold] - View/adjust search parameters")
        console.print(f"3. [bold]Analysis[/bold] - Toggle analysis {'[green]ON[/green]' if run_analysis else '[red]OFF[/red]'}")
        console.print("4. [bold]Exit[/bold] - Exit program")
        
        # Show current settings
        params = search_params.get_all_params()
        console.print("\n[bold cyan]Current Settings:[/bold cyan]")
        console.print(f"📊 Search tiers: Fine-grained, Contextual, Overview")
        console.print(f"🔍 Total max results: {sum(params[tier]['max_results'] for tier in params)}")
        console.print(f"🧠 AI Analysis: {'[green]Enabled[/green]' if run_analysis else '[red]Disabled[/red]'}")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            # Execute search
            query = input("\nEnter search query: ").strip()
            if not query:
                console.print("[yellow]Search query cannot be empty.[/yellow]")
                continue

            max_results = int(input("\nMax results (10-100): ").strip() or "30")
            max_results = max(10, min(max_results, 100))  # Ensure within bounds
            
            results, openai_analysis, groq_analysis = search_all(query, max_results=max_results, skip_prompts=False, run_analysis=run_analysis)
            
            # Display token usage stats if analysis was run
            if run_analysis:
                token_usage = token_counter.get_stats()
                console.print("\n[bold yellow]Token Usage Statistics:[/bold yellow]")
                console.print(f"[blue]Embedding Tokens:[/blue] {token_usage['embedding_tokens']:,}")
                console.print(f"[blue]Generation Input Tokens:[/blue] {token_usage['generation_tokens']['input']:,}")
                console.print(f"[blue]Generation Output Tokens:[/blue] {token_usage['generation_tokens']['output']:,}")
                console.print(f"[blue]Total Tokens:[/blue] {token_usage['embedding_tokens'] + token_usage['generation_tokens']['input'] + token_usage['generation_tokens']['output']:,}")
            
        elif choice == '2':
            # Configure search parameters
            while True:
                console.print("\n[bold cyan]Search Parameters[/bold cyan]")
                console.print("[cyan]=================================[/cyan]")
                console.print("1. [bold]Fine-grained[/bold] - High precision results")
                console.print("2. [bold]Contextual[/bold] - Balanced results")
                console.print("3. [bold]Overview[/bold] - Broader results")
                console.print("4. [bold]Presets[/bold] - Load predefined parameters")
                console.print("5. [bold]Save[/bold] - Save current parameters")
                console.print("6. [bold]Back[/bold] - Return to main menu")
                
                param_choice = input("\nSelect parameter to adjust (1-6): ").strip()
                
                if param_choice == '1':
                    adjust_tier_params('fine_grained')
                elif param_choice == '2':
                    adjust_tier_params('contextual')
                elif param_choice == '3':
                    adjust_tier_params('overview')
                elif param_choice == '4':
                    load_preset_menu()
                elif param_choice == '5':
                    save_preset_menu()
                elif param_choice == '6':
                    break
                else:
                    console.print("[yellow]Invalid choice. Please try again.[/yellow]")
        
        elif choice == '3':
            # Toggle analysis on/off
            run_analysis = not run_analysis
            status = "[green]enabled[/green]" if run_analysis else "[red]disabled[/red]"
            console.print(f"\n[bold]AI Analysis {status}[/bold]")
            
            # Explain what this means
            if run_analysis:
                console.print("Search results will be analyzed using AI models (OpenAI & Groq).")
                console.print("You'll see a token usage preview before analysis starts.")
            else:
                console.print("Search results will be displayed without AI analysis.")
                console.print("This will be faster and won't consume any API tokens.")
            
        elif choice == '4':
            # Exit program
            console.print("[green]Exiting program. Goodbye![/green]")
            break
            
        else:
            console.print("[yellow]Invalid choice. Please try again.[/yellow]")

def adjust_tier_params(tier):
    """Helper function to adjust parameters for a specific search tier"""
    params = search_params.get_params(tier)
    
    console.print(f"\n[bold cyan]Adjusting {tier.title()} Parameters[/bold cyan]")
    for param_name, value in params.items():
        console.print(f"{param_name}: {value}")
    
    # Parameter selection
    console.print("\n[cyan]Select parameter to adjust:[/cyan]")
    for i, param_name in enumerate(params.keys(), 1):
        console.print(f"{i}. {param_name}")
    console.print(f"{len(params) + 1}. Return to previous menu")
    
    try:
        choice = int(input("\nEnter choice: ").strip())
        if choice < 1 or choice > len(params) + 1:
            console.print("[yellow]Invalid choice. No changes made.[/yellow]")
            return
            
        if choice == len(params) + 1:
            return  # Return to previous menu
            
        # Get the parameter name
        param_name = list(params.keys())[choice - 1]
            
        # Get new value
        current_value = params[param_name]
        value_type = type(current_value)
        
        if param_name.endswith("threshold") or param_name.endswith("weight"):
            console.print(f"\n[cyan]Enter new value for {param_name} (current: {current_value}):[/cyan]")
            console.print("[yellow]Note: Values should be between 0.0 and 1.0[/yellow]")
            try:
                new_value = float(input().strip() or str(current_value))
                if 0.0 <= new_value <= 1.0:
                    search_params.update_params(tier, **{param_name: new_value})
                    console.print(f"[green]Updated {param_name} to {new_value}[/green]")
                else:
                    console.print("[yellow]Value must be between 0.0 and 1.0. No changes made.[/yellow]")
            except ValueError:
                console.print("[yellow]Invalid value. No changes made.[/yellow]")
                
        elif param_name.endswith("percentage"):
            console.print(f"\n[cyan]Enter new value for {param_name} (current: {current_value}):[/cyan]")
            console.print("[yellow]Note: Values should be between 0.0 and 1.0 (represents 0-100%)[/yellow]")
            try:
                new_value = float(input().strip() or str(current_value))
                if 0.0 <= new_value <= 1.0:
                    search_params.update_params(tier, **{param_name: new_value})
                    console.print(f"[green]Updated {param_name} to {new_value}[/green]")
                else:
                    console.print("[yellow]Value must be between 0.0 and 1.0. No changes made.[/yellow]")
            except ValueError:
                console.print("[yellow]Invalid value. No changes made.[/yellow]")
                
        elif param_name.endswith("max_results"):
            console.print(f"\n[cyan]Enter new value for {param_name} (current: {current_value}):[/cyan]")
            console.print("[yellow]Note: Values should be between 1 and 100[/yellow]")
            try:
                new_value = int(input().strip() or str(current_value))
                if 1 <= new_value <= 100:
                    search_params.update_params(tier, **{param_name: new_value})
                    console.print(f"[green]Updated {param_name} to {new_value}[/green]")
                else:
                    console.print("[yellow]Value must be between 1 and 100. No changes made.[/yellow]")
            except ValueError:
                console.print("[yellow]Invalid value. No changes made.[/yellow]")
        
        else:
            console.print(f"\n[cyan]Enter new value for {param_name} (current: {current_value}):[/cyan]")
            try:
                new_value_str = input().strip() or str(current_value)
                # Try to convert to the same type as current value
                if value_type == bool:
                    new_value = new_value_str.lower() in ('true', 'yes', 'y', '1')
                else:
                    new_value = value_type(new_value_str)
                
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            except ValueError:
                console.print("[yellow]Invalid value. No changes made.[/yellow]")
    
    except ValueError:
        console.print("[yellow]Invalid choice. No changes made.[/yellow]")

def load_preset_menu():
    """Helper function to load a preset"""
    console.print("\n[bold cyan]Available Presets[/bold cyan]")
    presets = search_params.list_presets()
    
    if not presets:
        console.print("[yellow]No saved presets found.[/yellow]")
        return
    
    for i, preset in enumerate(presets, 1):
        console.print(f"{i}. {preset}")
    
    choice = input("\nSelect preset to load (number or name, blank to cancel): ").strip()
    
    if not choice:
        return
    
    # Get preset name
    preset_name = None
    if choice.isdigit() and 1 <= int(choice) <= len(presets):
        preset_name = presets[int(choice) - 1]
    elif choice in presets:
        preset_name = choice
    
    if preset_name:
        search_params.load_preset(preset_name)
        console.print(f"[green]Loaded preset '{preset_name}'[/green]")
    else:
        console.print("[yellow]Invalid preset. Please try again.[/yellow]")

def save_preset_menu():
    """Helper function to save a preset"""
    console.print("\n[bold cyan]Save Current Parameters as Preset[/bold cyan]")
    
    # Get preset name
    preset_name = input("Enter preset name (blank to cancel): ").strip()
    
    if not preset_name:
        return
    
    # Confirm if preset exists
    if preset_name in search_params.list_presets():
        confirm = input(f"Preset '{preset_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            console.print("[yellow]Save cancelled.[/yellow]")
            return
    
    # Save preset
    search_params.save_preset(preset_name)
    console.print(f"[green]Saved preset '{preset_name}'[/green]")

if __name__ == "__main__":
    main()
