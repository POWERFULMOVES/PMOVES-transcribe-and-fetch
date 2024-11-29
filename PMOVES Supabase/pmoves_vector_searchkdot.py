
import asyncio
from typing import List, Dict
import asyncpg
import os

class VectorSearcher:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.db_url = os.getenv("SUPABASE_DB_URL")
        self.content_weight = 0.7
        self.limit = 10

    async def connect_db(self):
        """Establish a connection to the Supabase database."""
        return await asyncpg.connect(self.db_url)

    async def dot_product_search(self, query_embedding: List[float], limit: int = 10):
        """Perform a dot product vector search."""
        async with await self.connect_db() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM dot_product_search($1::vector, $2);
                """,
                query_embedding, limit
            )
        return [dict(row) for row in rows]

    async def keyword_search(self, query_text: str, limit: int = 10):
        """Perform a keyword search."""
        async with await self.connect_db() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM keyword_search($1, $2);
                """,
                query_text, limit
            )
        return [dict(row) for row in rows]

    async def combined_search(self, query_text: str, query_embedding: List[float], limit: int = 10):
        """Combine dot product and keyword search results."""
        dot_product_results = await self.dot_product_search(query_embedding, limit)
        keyword_results = await self.keyword_search(query_text, limit)

        # Merge and rank results based on a combined similarity score
        combined_results = dot_product_results + keyword_results
        combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)

        return combined_results[:limit]

    async def display_results(self, results: List[Dict], query: str):
        """Display results."""
        print(f"\n[Query: {query}]")
        for result in results:
            print(f"Video ID: {result['video_id']}")
            print(f"Text: {result['text']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Watch URL: {result['watch_url']}")
            print("-" * 50)

# Usage example:
async def main():
    searcher = VectorSearcher()

    # Example query embedding and text
    query_text = "expansion of space"
    query_embedding = [0.1, 0.2, 0.3, 0.4]  # Replace with actual embedding

    # Perform the combined search
    results = await searcher.combined_search(query_text, query_embedding)

    # Display results
    await searcher.display_results(results, query_text)

# Uncomment below to run
# asyncio.run(main())
