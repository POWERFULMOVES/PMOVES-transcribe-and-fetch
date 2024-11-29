# search_vectors.py
from supabase.client import create_client
import openai
import os
from dotenv import load_dotenv
from typing import List, Dict, Union
import tiktoken
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from pmoves2 import DualEmbeddingVectorizer
import asyncio
from datetime import datetime

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
    transcript_metadata: Dict = None
    created_at: datetime = None
    source_type: str = None
    segment_ids: List[str] = None

class VectorSearcher:
    def __init__(self):
        load_dotenv()
        
        # Initialize the dual embedding vectorizer
        self.vectorizer = DualEmbeddingVectorizer(
            embedding_model="text-embedding-3-small",
            summary_model="gpt-4o-mini"
        )
        
        self.console = Console()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.content_weight = 0.7  # default weight
        self.limit = 10  # default limit

    async def search_all(self, query: str, limit: int = None, content_weight: float = None) -> Dict[str, List[SearchResult]]:
        """Search both transcripts and chunks using hybrid search"""
        try:
            # Use instance values if no parameters provided
            limit = limit or self.limit
            content_weight = content_weight or self.content_weight
            
            # Add debug print
            print(f"Searching with limit: {limit}, content_weight: {content_weight}")
            
            hybrid_results = await self.vectorizer.hybrid_search(
                query=query, 
                limit=limit,
                content_weight=content_weight
            )
            
            # Add debug print
            print(f"Received {len(hybrid_results)} results")
            
            results = {
                'chunks': [
                    SearchResult(
                        text=r['text'],
                        video_id=r['video_id'],
                        start_time=r['start_time'],
                        end_time=r['end_time'],
                        similarity=r['similarity'],
                        content_similarity=r.get('content_similarity'),
                        summary_similarity=r.get('summary_similarity'),
                        summary=r.get('summary'),
                        watch_url=r.get('watch_url'),
                        transcript_metadata=r.get('transcript_metadata', {}),
                        created_at=r.get('created_at'),
                        source_type=r.get('source_table'),
                        segment_ids=r.get('segment_ids')
                    ) for r in hybrid_results
                ]
            }
            
            return results

        except Exception as e:
            self.console.print(f"[red]Error searching: {str(e)}[/]")
            raise

    def estimate_cost(self, query: str) -> float:
        """Estimate the cost of the search based on token count"""
        # Current pricing for text-embedding-3-small is $0.00002 per 1K tokens
        COST_PER_1K_TOKENS = 0.00002
        
        # Count tokens in the query
        tokens = len(self.tokenizer.encode(query))
        
        # Calculate cost
        cost = (tokens / 1000) * COST_PER_1K_TOKENS
        
        return cost

    def display_results(self, results: Dict[str, List[SearchResult]], query: str):
        """Display enhanced search results with source statistics and content"""
        cost = self.estimate_cost(query)
        self.console.print(f"\n[yellow]Estimated search cost: ${cost:.6f}[/]")
        
        if results['chunks']:
            # Count results by source
            sources = {}
            for r in results['chunks']:
                sources[r.source_type] = sources.get(r.source_type, 0) + 1
                
            self.console.print("\n[bold cyan]Search Sources:[/]")
            for source, count in sources.items():
                self.console.print(f"[blue]{source}:[/] {count} results")
                
            self.console.print("\n[bold cyan]Search Results:[/]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Source")
            table.add_column("Similarity")
            table.add_column("Video ID")
            table.add_column("Time Range")
            table.add_column("Content Preview")
            table.add_column("Watch URL")
            
            for r in results['chunks']:
                source_icon = "📄" if r.source_type == "document_embeddings" else "🎯"
                # Get appropriate preview text
                preview_text = (r.summary if r.source_type == "document_embeddings" else r.text[:100] + "...")
                
                table.add_row(
                    f"{source_icon} {r.source_type}",
                    f"{r.similarity:.2%}",
                    r.video_id,
                    f"{r.start_time} → {r.end_time}",
                    preview_text,
                    r.watch_url if r.watch_url else "N/A"
                )
            self.console.print(table)
            
            # Detailed view of top result
            if results['chunks']:
                r = results['chunks'][0]
                self.console.print("\n[bold cyan]Top Result Details:[/]")
                self.console.print(f"[yellow]Source:[/] {r.source_type}")
                self.console.print(f"[yellow]Full Text:[/] {r.text}")
                if r.transcript_metadata:
                    self.console.print("\n[yellow]Transcript Metadata:[/]")
                    for k, v in r.transcript_metadata.items():
                        self.console.print(f"[blue]{k}:[/] {v}")
                if r.source_type == "document_embeddings" and r.summary:
                    self.console.print("\n[yellow]Chunk Summary:[/]")
                    self.console.print(f"[blue]{r.summary}[/]")

    def set_search_params(self, limit: int = None, content_weight: float = None):
        """Update search parameters"""
        if limit is not None:
            self.limit = max(1, min(100, limit))  # Constrain between 1 and 100
        if content_weight is not None:
            self.content_weight = max(0.0, min(1.0, content_weight))  # Constrain between 0 and 1

async def main():
    searcher = VectorSearcher()
    
    while True:
        print("\n=== Search Options ===")
        print("1. Search")
        print("2. Change Settings")
        print("3. Quit")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "1":
            query = input("\nEnter search query: ")
            results = await searcher.search_all(query)
            searcher.display_results(results, query)
            
        elif choice == "2":
            print(f"\nCurrent Settings:")
            print(f"Results Limit: {searcher.limit}")
            print(f"Content Weight: {searcher.content_weight:.2f} (Summary Weight: {1-searcher.content_weight:.2f})")
            
            try:
                new_limit = input("\nEnter new results limit (or press Enter to skip): ")
                if new_limit:
                    new_limit = int(new_limit)
                    
                new_weight = input("Enter new content weight (0.0-1.0) (or press Enter to skip): ")
                if new_weight:
                    new_weight = float(new_weight)
                    
                searcher.set_search_params(
                    limit=new_limit if new_limit else None,
                    content_weight=new_weight if new_weight else None
                )
                
                print("\nSettings updated!")
                print(f"New Results Limit: {searcher.limit}")
                print(f"New Content Weight: {searcher.content_weight:.2f} (Summary Weight: {1-searcher.content_weight:.2f})")
                
            except ValueError:
                print("\n[red]Invalid input! Settings unchanged.[/]")
                
        elif choice == "3":
            break
            
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    asyncio.run(main())