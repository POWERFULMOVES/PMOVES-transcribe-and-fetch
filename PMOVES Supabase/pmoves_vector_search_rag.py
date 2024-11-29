import asyncio
import openai
import os
from dotenv import load_dotenv
from typing import List, Dict, Union
import asyncpg
import tiktoken
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from pmoves2 import DualEmbeddingVectorizer
from supabase.client import create_client
from datetime import datetime
from openai import AsyncOpenAI

from pmoves_vector_searchkdot import VectorSearcher as DotProductSearcher

@dataclass
class SearchResult:
    text: str
    video_id: str
    start_time: str
    end_time: str
    similarity: float
    content_similarity: float = None
    summary_similarity: float = None
    summary: str = None
    watch_url: str = None
    metadata: Dict = None
    created_at: datetime = None
    source_type: str = None
    segment_ids: List[str] = None

class VectorSearcher:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.openai_client = AsyncOpenAI(api_key=api_key)
        
        # Initialize Supabase client
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Initialize the dual embedding vectorizer
        self.vectorizer = DualEmbeddingVectorizer(
            embedding_model="text-embedding-3-small",
            summary_model="gpt-4o-mini"
        )
        
        self.console = Console()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.content_weight = 0.7  # default weight
        self.limit = 10  # default limit
        self.context_window = 2  # Number of additional segments for context
        
        # Add token counters
        self.tokens_sent = 0
        self.tokens_received = 0

    async def connect_db(self):
        """Establish a connection to the Supabase database."""
        try:
            # Use the same connection method as the hybrid search
            return self.supabase
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    async def dot_product_search(self, query_embedding: List[float], limit: int = 10) -> List[Dict]:
        """Perform a dot product vector search."""
        try:
            response = self.supabase.rpc(
                'dot_product_search',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit
                }
            ).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            self.console.print(f"[red]Dot product search error: {str(e)}[/]")
            return []

    async def keyword_search(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Perform a keyword search."""
        try:
            response = self.supabase.rpc(
                'keyword_search',
                {
                    'query_text': query_text,
                    'match_count': limit
                }
            ).execute()
            
            # Add debug logging
            self.console.print(f"[blue]Keyword search query: {query_text}[/]")
            self.console.print(f"[blue]Keyword search results: {len(response.data) if response.data else 0}[/]")
            
            return response.data if response.data else []
            
        except Exception as e:
            self.console.print(f"[red]Keyword search error: {str(e)}[/]")
            return []

    async def fetch_context(self, segment_id: str):
        """Fetch surrounding segments for context."""
        try:
            print(f"Fetching context for segment ID: {segment_id}")
            async with await self.connect_db() as conn:
                # Get the current segment and its timestamp
                current_segment = await conn.fetchrow(
                    """
                    SELECT * FROM video_transcriptions 
                    WHERE segment_id = $1
                    """, 
                    segment_id
                )
                
                if not current_segment:
                    return []
                    
                # Get surrounding segments
                rows = await conn.fetch(
                    """
                    SELECT * FROM video_transcriptions
                    WHERE video_id = $1
                    AND start_time <= $2
                    AND end_time >= $3
                    ORDER BY start_time
                    LIMIT $4
                    """,
                    current_segment['video_id'],
                    current_segment['end_time'],
                    current_segment['start_time'],
                    self.context_window * 2 + 1
                )
                
                results = [dict(row) for row in rows]
                print(f"Context fetched with {len(results)} segments.")
                return results
            
        except Exception as e:
            print(f"Error fetching context: {e}")
            return []

    def estimate_cost(self, query: str) -> float:
        """Estimate the cost of the search based on token count"""
        # Current pricing for text-embedding-3-small is $0.00002 per 1K tokens
        COST_PER_1K_TOKENS = 0.00002
        
        # Count tokens in the query
        tokens = len(self.tokenizer.encode(query))
        
        # Calculate cost
        cost = (tokens / 1000) * COST_PER_1K_TOKENS
        
        return cost

    async def _prepare_context(self, results: List[SearchResult]) -> str:
        """Prepare context from search results for AI response"""
        context_parts = []
        
        # Group results by source type
        grouped_results = {}
        for result in results:
            source_type = result.source_type
            if source_type not in grouped_results:
                grouped_results[source_type] = []
            grouped_results[source_type].append(result)
        
        # Add top results from each search method
        for search_type, search_results in grouped_results.items():
            if search_results:  # If there are results
                top_results = search_results[:3]  # Take top 3 results
                context_parts.append(f"\nTop {search_type} results:")
                for r in top_results:
                    context_parts.append(f"- [Video {r.video_id} at {r.start_time}] {r.text}")
        
        return "\n".join(context_parts)

    async def _generate_ai_response(self, query: str, context: str) -> str:
        """Generate AI response based on search results"""
        try:
            prompt = f"""Based on the following search results, please answer this question: {query}

Context from search results:
{context}

Please provide a comprehensive answer using the information from the search results. 
If the search results don't contain enough information to answer the question fully, 
please indicate what information is missing.

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
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.console.print(f"[red]Error generating AI response: {str(e)}[/]")
            return f"Error generating AI response: {str(e)}"

    async def display_results(self, results: Dict[str, List[SearchResult]], query: str):
        """Display enhanced search results with source statistics and content"""
        cost = self.estimate_cost(query)
        self.console.print(f"\n[yellow]Estimated search cost: ${cost:.6f}[/]")
        
        # Display AI Response first
        if 'ai_response' in results:
            self.console.print("\n[bold green]AI Response:[/]")
            self.console.print(f"[white]{results['ai_response']}[/]")
            self.console.print("\n[cyan]---[/]")
        
        # Display results from each search method
        for search_type in ['hybrid', 'dot_product', 'keyword']:
            if search_type in results and results[search_type]:
                self.console.print(f"\n[bold cyan]{search_type.title()} Search Results:[/]")
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Source")
                table.add_column("Similarity")
                table.add_column("Video ID")
                table.add_column("Time Range")
                table.add_column("Content Preview")
                table.add_column("Source File")
                table.add_column("Line")
                table.add_column("Watch URL")
                
                for r in results[search_type]:
                    source_icon = "📄" if r.source_type == "document_embeddings" else "🎯"
                    preview_text = (r.summary if hasattr(r, 'summary') and r.summary else r.text[:100] + "...")
                    
                    # Extract metadata information
                    source_file = "N/A"
                    line_number = "N/A"
                    
                    if r.metadata:
                        try:
                            # Debug print to see what's in metadata
                            self.console.print(f"[dim]Debug - Metadata: {r.metadata}[/]")
                            
                            # Since it's JSONB, it's already a dict
                            source_file = r.metadata.get('source_file', 'N/A')
                            line_number = r.metadata.get('line_number', 'N/A')
                            
                        except Exception as e:
                            self.console.print(f"[dim red]Error accessing metadata: {e}[/]")
                    
                    table.add_row(
                        f"{source_icon} {r.source_type}",
                        f"{r.similarity:.2%}",
                        r.video_id,
                        f"{r.start_time} → {r.end_time}",
                        preview_text,
                        str(source_file),
                        str(line_number),
                        r.watch_url if r.watch_url else "N/A"
                    )
                self.console.print(table)
        
        # Display token usage after results
        self.console.print("\n[bold cyan]Token Usage:[/]")
        self.console.print(f"[blue]Tokens sent: {self.tokens_sent}[/]")
        self.console.print(f"[yellow]Tokens received: {self.tokens_received}[/]")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.tokenizer.encode(text))

    async def search_all(self, query: str, limit: int = None, content_weight: float = None) -> Dict[str, List[SearchResult]]:
        """Search using all available methods and generate AI response"""
        try:
            # Use instance values if no parameters provided
            limit = limit or self.limit
            content_weight = content_weight or self.content_weight
            
            # Count tokens in query
            query_tokens = self.count_tokens(query)
            self.tokens_sent += query_tokens
            self.console.print(f"[blue]Query tokens: {query_tokens}[/]")
            
            self.console.print(f"Searching with limit: {limit}, content_weight: {content_weight}")
            
            # Get query embedding
            query_embedding = await self.vectorizer.get_embedding(query)
            
            # Run hybrid search
            hybrid_results = await self.hybrid_search(query, limit)
            self.console.print(f"Fetched {len(hybrid_results)} results with limit {limit}")
            
            # Run dot product search
            self.console.print("Running dot product search...")
            dot_results = await self.dot_product_search(query_embedding, limit)
            
            # Run keyword search with debug info
            self.console.print("Running keyword search...")
            keyword_results = await self.keyword_search(query, limit)
            self.console.print(f"[blue]Keyword search returned {len(keyword_results)} results[/]")
            if not keyword_results:
                self.console.print("[yellow]No keyword results found - debugging info:[/]")
                # Try a simple test query
                test_results = await self.keyword_search("the", 1)
                self.console.print(f"Test query 'the' returned: {len(test_results)} results")
            
            # Convert results to SearchResult objects
            hybrid_search_results = [self._convert_to_search_result(r, "hybrid") for r in hybrid_results]
            dot_search_results = [self._convert_to_search_result(r, "dot_product") for r in dot_results]
            keyword_search_results = [self._convert_to_search_result(r, "keyword") for r in keyword_results]
            
            # Count tokens in results
            for result in hybrid_search_results + dot_search_results + keyword_search_results:
                response_tokens = self.count_tokens(result.text)
                if result.summary:
                    response_tokens += self.count_tokens(result.summary)
                self.tokens_received += response_tokens
            
            self.console.print(
                f"Received results - Hybrid: {len(hybrid_results)}, "
                f"Dot: {len(dot_results)}, Keyword: {len(keyword_results)}"
            )
            
            # Prepare context from all results
            all_results = hybrid_search_results + dot_search_results + keyword_search_results
            context = await self._prepare_context(all_results)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(query, context)
            
            # Count tokens in AI response
            if ai_response:
                self.tokens_received += self.count_tokens(ai_response)
            
            self.console.print(f"[green]Total tokens sent: {self.tokens_sent}[/]")
            self.console.print(f"[yellow]Total tokens received: {self.tokens_received}[/]")
            
            return {
                "hybrid": hybrid_search_results,
                "dot_product": dot_search_results,
                "keyword": keyword_search_results,
                "ai_response": ai_response
            }
            
        except Exception as e:
            self.console.print(f"[red]Error during search: {str(e)}[/]")
            raise

    async def get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for the query text"""
        try:
            # Get API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            # Initialize the OpenAI client
            client = AsyncOpenAI(api_key=api_key)
            
            # Get embeddings using the new API style
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=query.replace('\n', ' ').strip()
            )
            
            return response.data[0].embedding
        except Exception as e:
            self.console.print(f"[red]Error getting query embedding: {str(e)}[/]")
            raise

    async def hybrid_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform hybrid search using Supabase RPC"""
        try:
            # Get query embedding
            query_embedding = await self.vectorizer.get_embedding(query)
            
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
            
            return response.data if response.data else []
            
        except Exception as e:
            self.console.print(f"[red]Error in hybrid search: {str(e)}[/]")
            return []

    def _convert_to_search_result(self, result: Dict, search_type: str) -> SearchResult:
        """Convert a dictionary result to a SearchResult object"""
        return SearchResult(
            text=result.get('text', ''),
            video_id=result.get('video_id', ''),
            start_time=result.get('start_time', ''),
            end_time=result.get('end_time', ''),
            similarity=result.get('similarity', 0.0),
            content_similarity=result.get('content_similarity'),
            summary_similarity=result.get('summary_similarity'),
            summary=result.get('summary'),
            watch_url=result.get('watch_url'),
            metadata=result.get('metadata', {}),
            created_at=result.get('created_at'),
            source_type=result.get('source_table', search_type),
            segment_ids=result.get('segment_ids')
        )

    async def save_results_to_log(self, results: Dict[str, List[SearchResult]], query: str, filename: str = None):
        """Save search results to a log file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.log"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Search Query: {query}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
                
                # Write AI Response if available
                if 'ai_response' in results:
                    f.write("=== AI Response ===\n")
                    f.write(f"{results['ai_response']}\n\n")
                
                # Write results from each search method
                for search_type in ['hybrid', 'dot_product', 'keyword']:
                    if search_type in results and results[search_type]:
                        f.write(f"\n=== {search_type.title()} Search Results ===\n")
                        
                        for r in results[search_type]:
                            f.write("\n---\n")
                            f.write(f"Source: {r.source_type}\n")
                            f.write(f"Similarity: {r.similarity:.2%}\n")
                            f.write(f"Video ID: {r.video_id}\n")
                            f.write(f"Time Range: {r.start_time} → {r.end_time}\n")
                            f.write(f"Content: {r.text}\n")
                            
                            if r.summary:
                                f.write(f"Summary: {r.summary}\n")
                            
                            if r.metadata:
                                f.write("Metadata:\n")
                                for key, value in r.metadata.items():
                                    f.write(f"  {key}: {value}\n")
                            
                            f.write(f"Watch URL: {r.watch_url if r.watch_url else 'N/A'}\n")
                
                # Write token usage
                f.write("\n=== Token Usage ===\n")
                f.write(f"Tokens sent: {self.tokens_sent}\n")
                f.write(f"Tokens received: {self.tokens_received}\n")
                
            return filename
            
        except Exception as e:
            self.console.print(f"[red]Error saving results to log: {str(e)}[/]")
            return None

async def main():
    searcher = VectorSearcher()
    last_results = None  # Store the last search results
    
    while True:
        try:
            searcher.console.print("\n[bold cyan]=== Search Options ===[/]")
            searcher.console.print("1. [green]Search[/]")
            searcher.console.print("2. [yellow]Change Settings[/]")
            searcher.console.print("3. [blue]Save Last Results to Log[/]")
            searcher.console.print("4. [red]Quit[/]")
            
            choice = input("\nChoose an option (1-4): ")
            
            if choice == "1":
                try:
                    query = input("\nEnter search query: ")
                    results = await searcher.search_all(query)
                    await searcher.display_results(results, query)
                    last_results = (results, query)  # Store results and query
                except EOFError:
                    searcher.console.print("[red]Input was interrupted[/]")
                    break
                except Exception as e:
                    searcher.console.print(f"[red]Error during search: {str(e)}[/]")
            
            elif choice == "2":
                searcher.console.print(f"\n[bold cyan]Current Settings:[/]")
                searcher.console.print(f"Results Limit: [green]{searcher.limit}[/]")
                searcher.console.print(
                    f"Content Weight: [green]{searcher.content_weight:.2f}[/] "
                    f"(Keyword Weight: [yellow]{1-searcher.content_weight:.2f}[/])"
                )
                
                try:
                    new_limit = input("\nEnter new results limit (or press Enter to skip): ")
                    if new_limit:
                        searcher.limit = max(1, min(100, int(new_limit)))  # Constrain between 1 and 100
                        
                    new_weight = input("Enter new content weight (0.0-1.0) (or press Enter to skip): ")
                    if new_weight:
                        searcher.content_weight = max(0.0, min(1.0, float(new_weight)))  # Constrain between 0 and 1
                    
                    searcher.console.print("\n[green]Settings updated![/]")
                    searcher.console.print(f"New Results Limit: [blue]{searcher.limit}[/]")
                    searcher.console.print(
                        f"New Content Weight: [blue]{searcher.content_weight:.2f}[/] "
                        f"(Keyword Weight: [yellow]{1-searcher.content_weight:.2f}[/])"
                    )
                    
                except ValueError:
                    searcher.console.print("\n[red]Invalid input! Settings unchanged.[/]")
                    
            elif choice == "3":
                if last_results is None:
                    searcher.console.print("[yellow]No search results available to save[/]")
                else:
                    results, query = last_results
                    custom_filename = input("Enter filename (or press Enter for automatic name): ").strip()
                    filename = await searcher.save_results_to_log(results, query, 
                                                                custom_filename if custom_filename else None)
                    if filename:
                        searcher.console.print(f"[green]Results saved to: {filename}[/]")
                    
            elif choice == "4":
                searcher.console.print("\n[yellow]Goodbye![/]")
                break
                
            else:
                searcher.console.print("\n[red]Invalid choice! Please try again.[/]")
                
        except EOFError:
            searcher.console.print("[red]Input was interrupted[/]")
            break
        except KeyboardInterrupt:
            searcher.console.print("[red]Program interrupted by user[/]")
            break
        except Exception as e:
            searcher.console.print(f"[red]Unexpected error: {str(e)}[/]")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nProgram terminated due to error: {str(e)}")