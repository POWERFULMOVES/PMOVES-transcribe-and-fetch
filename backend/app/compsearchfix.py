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
    from .psearchworking import token_counter
    
    # Start timing
    start_time = time.time()
    
    # Status message
    console.print(f"\n[bold cyan]Searching for:[/bold cyan] {query}")
    
    # Search methods to run
    methods = ["dot_product", "keyword"]
    
    # Display parameters
    from .psearchworking import SearchParameters
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
            'search_video_transcriptions',
            {
                'query_embedding': embedding,
                'similarity_threshold': fine_grained_params["similarity_threshold"],
                'content_weight': fine_grained_params["content_weight"],
                'match_count': int(max_results * fine_grained_params["result_percentage"])
            }
        ).execute().data
        fine_grained_time = time.time() - fine_grained_start
        
        # Create SearchResult objects
        from .psearchworking import SearchResult
        for r in fine_grained_results:
            r["search_method"] = "dot_product"
            r["source"] = "video_transcriptions"
            result = SearchResult.from_db_result(r)
            dot_product_results.append(result)
        
        # Run dot product search on document embeddings (contextual segments)
        contextual_start = time.time()
        contextual_results = client.rpc(
            'search_document_embeddings',
            {
                'query_embedding': embedding,
                'similarity_threshold': contextual_params["similarity_threshold"],
                'content_weight': contextual_params["content_weight"],
                'match_count': int(max_results * contextual_params["result_percentage"])
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
            'search_video_transcriptions_full',
            {
                'query_embedding': embedding,
                'similarity_threshold': overview_params["similarity_threshold"],
                'content_weight': overview_params["content_weight"],
                'match_count': int(max_results * overview_params["result_percentage"])
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
                'search_query': query,
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
            from .psearchworking import SEARCH_METHOD_STYLES
            method_style = SEARCH_METHOD_STYLES.get(search_method, SEARCH_METHOD_STYLES['default'])
            
            source = result.source if result.source else "unknown"
            from .psearchworking import SOURCE_STYLES
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
            from .psearchworking import analyze_search_results
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
                from .psearchworking import save_results
                save_results(all_results, query, format_choice, openai_analysis, groq_analysis)
            else:
                console.print(f"[yellow]Invalid format choice. Using default (md).[/yellow]")
                save_results(all_results, query, 'md', openai_analysis, groq_analysis)
    
    return all_results, openai_analysis, groq_analysis
