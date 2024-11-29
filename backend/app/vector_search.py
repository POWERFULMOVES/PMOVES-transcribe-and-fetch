import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional, List
import json
from datetime import datetime
import logging
from rich.table import Table
from rich.console import Console
import os
from openai import AsyncOpenAI

# Add PMOVES Supabase directory to path
PMOVES_DIR = Path(__file__).parent.parent.parent / "PMOVES Supabase"
sys.path.append(str(PMOVES_DIR))

from pmoves_vector_search_rag import VectorSearcher as BaseVectorSearcher, SearchResult
from pydantic import BaseModel

class VectorSearchRequest(BaseModel):
    query: str
    threshold: float = 0.7
    limit: Optional[int] = 10
    content_weight: Optional[float] = 0.7

class VectorSearchResponse(BaseModel):
    results: list
    ai_response: Optional[str]
    metadata: Dict

class VectorSearcher(BaseVectorSearcher):
    def __init__(self):
        # Initialize base class first
        super().__init__()
        # Initialize our console
        self.console = Console()

    async def get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for the query text using the base class's OpenAI client"""
        try:
            # Use the base class's OpenAI client
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error getting query embedding: {str(e)}")
            raise

    def _time_to_seconds(self, time_str: str) -> int:
        """Convert HH:MM:SS time format to seconds"""
        if not time_str:
            return 0
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + int(s)
            return 0
        except:
            return 0

    def _convert_keyword_result(self, result: Dict) -> Dict:
        """Convert keyword search result to match hybrid/dot product format"""
        # Extract metadata from the result
        metadata = {}
        if isinstance(result.get('metadata'), dict):
            metadata = result['metadata']
        elif isinstance(result.get('metadata'), str):
            try:
                metadata = json.loads(result['metadata'])
            except:
                metadata = {}
        
        # Format video_id to match other search types
        video_id = result.get('video_id', '').replace('_ZE', ' ZE')
        start_time = result.get('start_time', '')
        
        # Generate watch URL with timestamp
        watch_url = None
        if video_id:
            seconds = self._time_to_seconds(start_time)
            watch_url = f"https://www.youtube.com/watch?v={video_id}&t={seconds}"
        
        return {
            "text": result.get('content', ''),  # Content field maps to text
            "video_id": video_id,
            "start_time": start_time,
            "end_time": result.get('end_time', ''),
            "similarity": float(result.get('similarity', 0.0)) if result.get('similarity') else 1.0,
            "source_type": "video_transcriptions",  # Match the source format of other searches
            "metadata": metadata,
            "watch_url": watch_url
        }

    def _convert_to_search_result(self, result: Dict, search_type: str) -> SearchResult:
        """Convert a dictionary to a SearchResult object"""
        # Extract basic fields
        text = result.get('text', '') or result.get('content', '')
        video_id = result.get('video_id', '').replace('_ZE', ' ZE')  # Ensure consistent video ID format
        start_time = result.get('start_time', '')
        end_time = result.get('end_time', '')
        similarity = float(result.get('similarity', 0.0))
        
        # Extract metadata fields
        metadata = {}
        raw_metadata = result.get('metadata', {})
        if isinstance(raw_metadata, str):
            try:
                metadata = json.loads(raw_metadata)
            except:
                metadata = {}
        elif isinstance(raw_metadata, dict):
            metadata = raw_metadata

        # Ensure source_file is present in metadata
        if 'source_file' not in metadata:
            # If source_file is at root level, move it to metadata
            source_file = result.get('source_file', '')
            if source_file:
                metadata['source_file'] = source_file
            else:
                # Generate source file name from video ID if not present
                video_title = result.get('title', '').replace(' ', '_') or 'Unknown_Video'
                metadata['source_file'] = f"{video_title}_Transformers_#10_(Energon)"

        # Ensure line_number is present in metadata
        if 'line_number' not in metadata:
            metadata['line_number'] = result.get('line_number', 'N/A')

        # Generate watch URL if not present
        watch_url = result.get('watch_url')
        if not watch_url and video_id:
            seconds = self._time_to_seconds(start_time)
            watch_url = f"https://www.youtube.com/watch?v={video_id}&t={seconds}"

        return SearchResult(
            text=text,
            video_id=video_id,
            start_time=start_time,
            end_time=end_time,
            similarity=similarity,
            source_type="video_transcriptions",
            metadata=metadata,
            watch_url=watch_url
        )

    def _convert_result_to_dict(self, result: SearchResult) -> Dict:
        """Convert a SearchResult object to a dictionary for JSON serialization"""
        # Extract source file and line number from metadata
        source_file = result.metadata.get('source_file', 'N/A') if result.metadata else 'N/A'
        line_number = result.metadata.get('line_number', 'N/A') if result.metadata else 'N/A'
        
        return {
            "text": result.text,
            "video_id": result.video_id,
            "start_time": result.start_time,
            "end_time": result.end_time,
            "similarity": result.similarity,
            "source_type": "video_transcriptions",
            "metadata": {
                "source_file": source_file,
                "line_number": line_number
            },
            "watch_url": result.watch_url
        }

    def _display_results_table(self, results: List[SearchResult], search_type: str):
        """Display search results in a formatted table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Source")
        table.add_column("Similarity")
        table.add_column("Video ID")
        table.add_column("Time Range")
        table.add_column("Content Preview")
        table.add_column("Source File")
        table.add_column("Line")
        table.add_column("Watch URL")
        
        for result in results:
            source_icon = "🎯"  # Always video_transcriptions
            preview_text = result.text[:100] + "..." if len(result.text) > 100 else result.text
            source_file = result.metadata.get('source_file', 'N/A') if result.metadata else 'N/A'
            line_number = result.metadata.get('line_number', 'N/A') if result.metadata else 'N/A'
            
            table.add_row(
                f"{source_icon} video_transcriptions",
                f"{result.similarity:.2%}",
                result.video_id,
                f"{result.start_time} → {result.end_time}",
                preview_text,
                str(source_file),
                str(line_number),
                result.watch_url if result.watch_url else "N/A"
            )
        
        self.console.print(f"\n[bold cyan]{search_type} Search Results:[/]")
        self.console.print(table)

    async def dot_product_search(self, query: str) -> List[Dict]:
        """Override dot product search to handle embedding conversion"""
        try:
            # Get embedding for query
            query_embedding = await self.get_query_embedding(query)
            
            # Call parent's dot product search with the embedding
            return await super().dot_product_search(query_embedding)
            
        except Exception as e:
            logging.error(f"Dot product search error: {e}")
            return []

    async def generate_ai_response(self, query: str, results: List[Dict]) -> str:
        """Generate AI response for the search results"""
        try:
            # Convert dictionary results to SearchResult objects
            search_results = []
            for r in results:
                result = SearchResult(
                    text=r['text'],
                    video_id=r['video_id'],
                    start_time=r['start_time'],
                    end_time=r['end_time'],
                    similarity=float(r['similarity']),
                    source_type=r['source_type'],  # Use source_type instead of source
                    metadata=r.get('metadata', {})
                )
                search_results.append(result)

            # Prepare context for AI
            context = "\n".join([f"Content: {r.text}\nSource: {r.source_type}\nSimilarity: {r.similarity:.2%}\n" 
                               for r in search_results])

            prompt = f"""Based on the search results below, provide a concise summary of the information relevant to the query: "{query}"

Search Results:
{context}

Please provide:
1. A summary of the key information found
2. Any relevant context or relationships between the results
3. Note any important missing information

Answer:"""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate answers based on search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Track token usage
            self.tokens_received += len(self.tokenizer.encode(response.choices[0].message.content))
            
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Error generating AI response: {str(e)}")
            return f"Error generating AI response: {str(e)}"

    async def search_with_streaming(self, query: str, threshold: float = 0.7) -> AsyncGenerator[Dict, None]:
        """Stream search results with the same format as pmoves_vector_search_rag.py"""
        try:
            # Get query embedding using base class's method
            query_embedding = await self.get_query_embedding(query)
            
            # Display query information
            self.console.print(f"\nQuery tokens: {len(self.tokenizer.encode(query))}")
            self.console.print(f"Searching with limit: {self.limit}, content_weight: {self.content_weight}")
            
            # Run hybrid search using base class's method
            self.console.print(f"\nRunning hybrid search...")
            hybrid_results = await super().hybrid_search(query)
            if hybrid_results:
                hybrid_results = [self._convert_to_search_result(r, "hybrid") for r in hybrid_results]
                self.console.print(f"Fetched {len(hybrid_results)} results with limit {self.limit}")
                self._display_results_table(hybrid_results, "Hybrid")
                
                # Run dot product search with the embedding
                self.console.print("\nRunning dot product search...")
                dot_results = await self.dot_product_search(query)
                dot_results = [self._convert_to_search_result(r, "dot_product") for r in dot_results] if dot_results else []
                if dot_results:
                    self._display_results_table(dot_results, "Dot Product")
                
                # Run keyword search
                self.console.print("\nRunning keyword search...")
                self.console.print(f"Keyword search query: {query}")
                raw_keyword_results = await self.keyword_search(query)
                
                # Convert keyword results to match hybrid/dot product format
                keyword_results = []
                if raw_keyword_results:
                    keyword_results = [
                        self._convert_to_search_result(
                            self._convert_keyword_result(r), 
                            "keyword"
                        ) for r in raw_keyword_results
                    ]
                self.console.print(f"Keyword search returned {len(keyword_results)} results")
                if keyword_results:
                    self._display_results_table(keyword_results, "Keyword")
                
                # Convert results to dictionaries for JSON serialization
                hybrid_dicts = [self._convert_result_to_dict(r) for r in hybrid_results]
                dot_dicts = [self._convert_result_to_dict(r) for r in dot_results]
                keyword_dicts = [self._convert_result_to_dict(r) for r in keyword_results]
                
                # Generate AI response using the hybrid results
                ai_response = await self.generate_ai_response(query, hybrid_dicts)
                
                # Calculate token usage and cost
                usage = self.calculate_token_usage()
                
                # Display results summary
                self.console.print(f"\nReceived results - Hybrid: {len(hybrid_results)}, " 
                                 f"Dot: {len(dot_results)}, Keyword: {len(keyword_results)}")
                
                # Display token usage
                self.console.print(f"\nTotal tokens sent: {usage['tokens_sent']}")
                self.console.print(f"Total tokens received: {usage['tokens_received']}")
                self.console.print(f"\nEstimated search cost: ${usage['estimated_cost']:.6f}\n")
                
                # Display AI Response
                self.console.print("\nAI Response:")
                self.console.print(ai_response)
                
                # Stream all results together
                yield {
                    "type": "search_results",
                    "data": {
                        "hybrid": hybrid_dicts,
                        "dot_product": dot_dicts,
                        "keyword": keyword_dicts,
                        "ai_response": ai_response,
                        "token_usage": usage
                    }
                }
            
            # Generate and stream AI response
            all_results = hybrid_results + dot_results + keyword_results
            if all_results:
                context = await self._prepare_context(all_results)
                ai_response = await self._generate_ai_response(query, context)
                
                if ai_response:
                    yield {
                        "type": "ai_response",
                        "data": ai_response
                    }
            
            # Stream token usage
            yield {
                "type": "token_usage",
                "data": {
                    "sent": self.tokens_sent,
                    "received": self.tokens_received
                }
            }
            
        except Exception as e:
            logging.error(f"Search error: {e}")
            yield {
                "type": "error",
                "data": str(e)
            }

    async def keyword_search(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Override keyword search to remove plain text output."""
        try:
            response = await super().keyword_search(query_text, limit)
            
            return response if response else []
            
        except Exception as e:
            logging.error(f"[red]Keyword search error: {str(e)}[/]")
            return []

    def format_results_table(self, results: List[Dict], search_type: str) -> str:
        """Format search results into a rich table"""
        table = Table(title=f"{search_type} Search Results")
        
        # Add columns
        table.add_column("Source", style="cyan")
        table.add_column("Similarity", style="magenta")
        table.add_column("Video ID", style="green")
        table.add_column("Time Range", style="yellow")
        table.add_column("Content Preview", style="white", no_wrap=False)
        table.add_column("Source File", style="blue")
        table.add_column("Line", style="red")
        table.add_column("Watch URL", style="green")
        
        # Add rows
        for result in results:
            source_icon = "🎯"  # Always video_transcriptions
            similarity = f"{float(result.get('similarity', 0)) * 100:.2f}%" if result.get('similarity') else "N/A"
            time_range = f"{result.get('start_time', 'N/A')} → {result.get('end_time', 'N/A')}"
            
            table.add_row(
                f"{source_icon} video_transcriptions",
                similarity,
                result.get('video_id', 'N/A'),
                time_range,
                result.get('content', 'N/A')[:50] + "..." if result.get('content') else 'N/A',
                result.get('source_file', 'N/A'),
                str(result.get('line_number', 'N/A')),
                result.get('watch_url', 'N/A')
            )
        
        # Render table to string
        console = Console(record=True)
        console.print(table)
        return console.export_text()

    def calculate_token_usage(self):
        """Calculate total token usage and estimated cost."""
        embedding_cost_per_1k = 0.00002  # $0.00002 per 1K tokens for text-embedding-3-small
        completion_cost_per_1k = 0.01    # $0.01 per 1K tokens for GPT-4 completion
        
        total_sent = self.tokens_sent
        total_received = self.tokens_received
        
        # Calculate costs
        embedding_cost = (total_sent / 1000) * embedding_cost_per_1k
        completion_cost = (total_received / 1000) * completion_cost_per_1k
        total_cost = embedding_cost + completion_cost
        
        return {
            "tokens_sent": total_sent,
            "tokens_received": total_received,
            "estimated_cost": total_cost,
            "cost_breakdown": {
                "embedding_cost": embedding_cost,
                "completion_cost": completion_cost
            }
        }

async def run_vector_search(query: str, threshold: float = 0.7) -> AsyncGenerator[Dict, None]:
    """Helper function to run vector search with streaming results."""
    searcher = VectorSearcher()
    async for result in searcher.search_with_streaming(query, threshold):
        yield result
