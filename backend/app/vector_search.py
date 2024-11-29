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
        """Get embedding for the query text using OpenAI API"""
        try:
            # Clean and prepare query
            clean_query = query.replace('\n', ' ').strip()
            
            # Get embeddings using the OpenAI API
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=clean_query  # API expects a single string
            )
            
            # Debug logging
            self.console.print(f"[blue]Generated embedding for query: {clean_query}[/]")
            
            return response.data[0].embedding
            
        except Exception as e:
            logging.error(f"Error getting query embedding: {str(e)}")
            self.console.print(f"[red]Error getting query embedding: {str(e)}[/]")
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

    def _convert_to_search_result(self, result: Dict, search_type: str) -> SearchResult:
        """Convert a dictionary result to a SearchResult object"""
        # Extract metadata from JSONB
        metadata = result.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Generate watch URL if not present
        video_id = result.get('video_id', '')
        start_time = result.get('start_time', '')
        watch_url = result.get('watch_url')
        if not watch_url and video_id:
            seconds = self._time_to_seconds(start_time)
            watch_url = f"https://www.youtube.com/watch?v={video_id}&t={seconds}"

        # Create SearchResult object
        return SearchResult(
            text=result.get('text', '') or result.get('content', ''),
            video_id=video_id,
            start_time=start_time,
            end_time=result.get('end_time', ''),
            similarity=float(result.get('similarity', 0.0)),
            content_similarity=result.get('content_similarity'),
            summary_similarity=result.get('summary_similarity'),
            summary=result.get('summary'),
            watch_url=watch_url,
            metadata=metadata,
            created_at=result.get('created_at'),
            source_type=result.get('source_type', result.get('source_table', search_type)),  # Try multiple fields for source type
            segment_ids=result.get('segment_ids')
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
            "source_type": result.source_type,  # Use actual source type from result
            "metadata": {
                "source_file": source_file,
                "line_number": line_number
            },
            "watch_url": result.watch_url
        }

    def format_results_table(self, results: List[Dict]) -> Table:
        """Format search results into a rich table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Source")
        table.add_column("Similarity")
        table.add_column("Video ID")
        table.add_column("Time Range")
        table.add_column("Content Preview")
        table.add_column("Source File")
        table.add_column("Line")
        table.add_column("Watch URL")
        
        # Add rows
        for result in results:
            source_icon = "🎯"  # Always video_transcriptions
            similarity = f"{float(result.get('similarity', 0)) * 100:.2f}%" if result.get('similarity') else "N/A"
            time_range = f"{result.get('start_time', 'N/A')} → {result.get('end_time', 'N/A')}"
            
            # Extract metadata fields
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            source_file = metadata.get('source_file', 'N/A')
            line_number = metadata.get('line_number', 'N/A')
            
            # Format content preview
            content = result.get('text', '') or result.get('content', '')
            preview = content[:100] + "..." if len(content) > 100 else content
            
            table.add_row(
                f"{source_icon} {result.get('source_type', 'N/A')}",
                similarity,
                result.get('video_id', 'N/A'),
                time_range,
                preview,
                str(source_file),
                str(line_number),
                result.get('watch_url', 'N/A')
            )
        
        return table

    def _display_results_table(self, results: List[SearchResult], search_type: str):
        """Display search results in a formatted table"""
        table = self.format_results_table([self._convert_result_to_dict(r) for r in results])
        self.console.print(f"\n[bold cyan]{search_type} Search Results:[/]")
        self.console.print(table)

    async def dot_product_search(self, query: str) -> List[Dict]:
        """Override dot product search to handle embedding conversion"""
        try:
            # Get embedding for query
            query_embedding = await self.get_query_embedding(query)
            
            # Call parent's dot product search with the embedding
            results = await super().dot_product_search(query_embedding, self.limit)
            
            # Add debug logging
            self.console.print(f"[blue]Dot product search query: {query}[/]")
            self.console.print(f"[blue]Dot product search results: {len(results) if results else 0}[/]")
            
            return results
            
        except Exception as e:
            logging.error(f"Dot product search error: {e}")
            self.console.print(f"[red]Dot product search error: {str(e)}[/]")
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

    async def _generate_ai_response(self, query: str, results: List[Dict]) -> str:
        """Generate AI response based on search results"""
        try:
            # Prepare context from results
            context = await self._prepare_context(results)
            
            # Create the prompt
            prompt = f"""Based on the following search results, please answer this question: {query}

Context from search results:
{context}

Please provide:
1. A concise summary of the key information found
2. Any relevant context or relationships between the results
3. Note any important missing information

Answer:"""

            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate answers based on search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Get response text
            response_text = response.choices[0].message.content
            
            # Count tokens
            self.tokens_sent += len(self.tokenizer.encode(prompt))
            self.tokens_received += len(self.tokenizer.encode(response_text))
            
            # Debug logging
            self.console.print(f"[blue]Generated AI response with {len(self.tokenizer.encode(response_text))} tokens[/]")
            
            return response_text
            
        except Exception as e:
            self.console.print(f"[red]Error generating AI response: {str(e)}[/]")
            return None

    async def _prepare_context(self, results: List[Dict]) -> str:
        """Prepare context from search results for AI response"""
        context_parts = []
        
        # Group results by source type
        grouped_results = {}
        for result in results:
            source_type = result.get('source_type', 'unknown')
            if source_type not in grouped_results:
                grouped_results[source_type] = []
            grouped_results[source_type].append(result)
        
        # Add top results from each source type
        for source_type, source_results in grouped_results.items():
            if source_results:  # If there are results
                top_results = source_results[:3]  # Take top 3 results
                context_parts.append(f"\nTop {source_type} results:")
                for r in top_results:
                    # Get video info if available
                    video_info = f"[Video {r.get('video_id')} at {r.get('start_time')}] " if r.get('video_id') else ""
                    # Get content
                    content = r.get('text', '') or r.get('content', '')
                    # Add to context
                    context_parts.append(f"- {video_info}{content}")
        
        return "\n".join(context_parts)

    async def hybrid_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform hybrid search using Supabase RPC"""
        try:
            # Get query embedding
            query_embedding = await self.get_query_embedding(query)
            
            # Call the advanced_hybrid_search RPC function
            response = self.supabase.rpc(
                'advanced_hybrid_search',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit,
                    'content_weight': self.content_weight,
                    'video_filter': None,
                    'min_similarity': 0.0
                }
            ).execute()
            
            # Add debug logging
            self.console.print(f"[blue]Hybrid search query: {query}[/]")
            self.console.print(f"[blue]Hybrid search results: {len(response.data) if response.data else 0}[/]")
            
            # Return results
            return response.data if response.data else []
            
        except Exception as e:
            self.console.print(f"[red]Error in hybrid search: {str(e)}[/]")
            return []

    async def search_with_streaming(self, query: str, threshold: float = 0.7) -> AsyncGenerator[Dict, None]:
        """Stream search results with the same format as pmoves_vector_search_rag.py"""
        try:
            # Get query embedding using base class's method
            query_embedding = await self.get_query_embedding(query)
            
            # Display query information
            self.console.print(f"\nQuery tokens: {len(self.tokenizer.encode(query))}")
            self.console.print(f"Searching with limit: {self.limit}, content_weight: {self.content_weight}")
            
            # Run hybrid search
            self.console.print(f"\nRunning hybrid search...")
            hybrid_results = await self.hybrid_search(query)
            hybrid_results = [self._convert_to_search_result(r, "hybrid") for r in hybrid_results] if hybrid_results else []
            if hybrid_results:
                self.console.print(f"Fetched {len(hybrid_results)} results with limit {self.limit}")
                
                # Run dot product search with the query
                self.console.print("\nRunning dot product search...")
                dot_results = await self.dot_product_search(query)  # Pass the query string instead of embedding
                dot_results = [self._convert_to_search_result(r, "dot_product") for r in dot_results] if dot_results else []
                self
                # Run keyword search
                self.console.print("\nRunning keyword search...")
                self.console.print(f"Keyword search query: {query}")
                keyword_results = await self.keyword_search(query)
                keyword_results = [self._convert_to_search_result(r, "keyword") for r in keyword_results] if keyword_results else []
                self.console.print(f"Keyword search returned {len(keyword_results)} results")
                
                # Count tokens in results
                for result in hybrid_results + dot_results + keyword_results:
                    response_tokens = len(self.tokenizer.encode(result.text))
                    if result.summary:
                        response_tokens += len(self.tokenizer.encode(result.summary))
                    self.tokens_received += response_tokens
                
                self.console.print(
                    f"\nReceived results - Hybrid: {len(hybrid_results)}, "
                    f"Dot: {len(dot_results)}, Keyword: {len(keyword_results)}"
                )
                
                # Prepare context from all results
                all_results = hybrid_results + dot_results + keyword_results
                
                # Generate AI response using the hybrid results
                ai_response = await self._generate_ai_response(query, [self._convert_result_to_dict(r) for r in hybrid_results])
                
                # Display results tables
                for search_type, results in [
                    ("Hybrid", hybrid_results),
                    ("Dot Product", dot_results),
                    ("Keyword", keyword_results)
                ]:
                    if results:
                        table = self.format_results_table([
                            self._convert_result_to_dict(r) for r in results
                        ])
                        self.console.print(f"\n[bold cyan]{search_type} Search Results:[/]")
                        self.console.print(table)
                
                # Display token usage
                self.console.print("\n[bold cyan]Token Usage:[/]")
                self.console.print(f"[blue]Tokens sent: {self.tokens_sent}[/]")
                self.console.print(f"[yellow]Tokens received: {self.tokens_received}[/]")
                
                # Stream all results together
                yield {
                    "type": "search_results",
                    "data": {
                        "hybrid": [self._convert_result_to_dict(r) for r in hybrid_results],
                        "dot_product": [self._convert_result_to_dict(r) for r in dot_results],
                        "keyword": [self._convert_result_to_dict(r) for r in keyword_results],
                        "ai_response": ai_response,
                        "token_usage": {
                            "tokens_sent": self.tokens_sent,
                            "tokens_received": self.tokens_received,
                            "estimated_cost": self.estimate_cost(query)
                        }
                    }
                }
            
        except Exception as e:
            self.console.print(f"[red]Search error: {str(e)}[/]")
            yield {
                "type": "error",
                "data": {
                    "error": str(e)
                }
            }

    async def keyword_search(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Override keyword search to remove plain text output."""
        try:
            response = await super().keyword_search(query_text, limit)
            
            return response if response else []
            
        except Exception as e:
            logging.error(f"[red]Keyword search error: {str(e)}[/]")
            return []

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
