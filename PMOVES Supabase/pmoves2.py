from supabase.client import create_client
import openai
import os
from dotenv import load_dotenv
import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple
import time
from tqdm import tqdm
import tiktoken
from datetime import datetime
import sys
from tqdm.auto import tqdm
import threading
from threading import Timer
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import asyncio
import random
from openai import AsyncOpenAI

@dataclass
class ContentChunk:
    text: str
    video_id: str
    start_time: str
    end_time: str
    segment_ids: List[str]
    watch_url: str
    summary: str = ""

class DualEmbeddingVectorizer:
    def __init__(
        self,
        target_chunk_sentences: int = 5,
        max_chunk_chars: int = 1500,
        min_chunk_sentences: int = 3,
        batch_size: int = 10,
        embedding_model: str = "text-embedding-3-small",
        summary_model: str = "gpt-4o-mini"
    ):
        load_dotenv()
        
        # Validate environment variables
        self.validate_env_vars([
            "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENAI_API_KEY"
        ])

        # Initialize clients and services
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Setup logging
        self.setup_logging()
        
        # Store configuration
        self.target_chunk_sentences = target_chunk_sentences
        self.max_chunk_chars = max_chunk_chars
        self.min_chunk_sentences = min_chunk_sentences
        self.embedding_model = embedding_model
        self.summary_model = summary_model
        self.batch_size = batch_size
        self.tokens_sent = 0
        self.tokens_received = 0

    def validate_env_vars(self, required_vars: List[str]):
        """Validate required environment variables"""
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'vectorizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def generate_embeddings(self, text: str = None, summary: str = None) -> Tuple[List[float], List[float]]:
        """Generate embeddings with improved retry logic and input validation"""
        async def generate_single_embedding(input_text: str) -> List[float]:
            max_retries = 3
            wait_time = 1
            
            # Validate and truncate input
            if not input_text or not input_text.strip():
                return None
            
            # Truncate to max token length
            tokens = self.tokenizer.encode(input_text)
            if len(tokens) > 8191:
                self.logger.warning(f"Input text too long ({len(tokens)} tokens). Truncating to 8191 tokens.")
                tokens = tokens[:8191]
                input_text = self.tokenizer.decode(tokens)
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=input_text.replace('\n', ' ').strip()
                    )
                    return response.data[0].embedding
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    jitter = random.uniform(0, 0.1)
                    wait = (wait_time * (2**attempt)) + jitter
                    await asyncio.sleep(wait)

        async def batch_generate_embeddings(texts: List[str]) -> List[List[float]]:
            """Generate embeddings in batches for better efficiency"""
            if not texts:
                return []
            
            try:
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                self.logger.error(f"Batch embedding generation failed: {e}")
                raise

        try:
            content_embedding = None
            summary_embedding = None

            # Generate both embeddings in parallel if both inputs are provided
            if text and summary:
                embeddings = await batch_generate_embeddings([text, summary])
                if embeddings:
                    content_embedding, summary_embedding = embeddings
            else:
                if text:
                    content_embedding = await generate_single_embedding(text)
                if summary:
                    summary_embedding = await generate_single_embedding(summary)

            return content_embedding, summary_embedding

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise

    async def process_video(self, video_id: str):
        """Process video with improved batch handling"""
        start_time = datetime.now()
        self.logger.info(f"Starting video processing at {start_time}")

        # Fetch segments
        segments = self.fetch_video_segments(video_id)
        if not segments:
            self.logger.warning(f"No segments found for video_id: {video_id}")
            return

        # Phase 1: Process individual transcripts
        missing_embeddings = [
            segment for segment in segments 
            if not self.check_segment_embedding(segment['id'])
        ]

        if missing_embeddings:
            self.logger.info(f"Processing {len(missing_embeddings)} missing transcript embeddings")
            batch_size = 50  # Increased batch size
            for i in range(0, len(missing_embeddings), batch_size):
                batch = missing_embeddings[i:i + batch_size]
                await self.process_transcript_batch(batch)
                self.logger.info(f"Completed batch {i//batch_size + 1} of {(len(missing_embeddings)-1)//batch_size + 1}")

        # Phase 2: Process chunks with summaries
        chunks = self.create_chunks_from_segments(segments)
        chunks_to_process = [
            chunk for chunk in chunks 
            if not self.check_chunk_exists(chunk.video_id, chunk.segment_ids)
        ]

        if chunks_to_process:
            self.logger.info(f"Processing {len(chunks_to_process)} new chunks")
            # Prepare batch inserts
            chunk_inserts = []
            for chunk in chunks_to_process:
                chunk.summary = await self.create_summary(chunk.text)
                content_embedding, summary_embedding = await self.generate_embeddings(chunk.text, chunk.summary)
                
                chunk_inserts.append({
                    'video_id': chunk.video_id,
                    'start_time': chunk.start_time,
                    'end_time': chunk.end_time,
                    'text': chunk.text,
                    'embedding': content_embedding,
                    'summary': chunk.summary,
                    'summary_embedding': summary_embedding,
                    'segment_ids': chunk.segment_ids,
                    'watch_url': chunk.watch_url,
                    'created_at': datetime.now().isoformat()
                })

            # Perform batch insert
            try:
                self.supabase.table('document_embeddings').insert(chunk_inserts).execute()
                self.logger.info(f"Successfully inserted {len(chunk_inserts)} chunks")
            except Exception as e:
                self.logger.error(f"Error during batch insert: {e}")

        duration = datetime.now() - start_time
        self.logger.info(f"Processing complete in {duration}")

    async def create_summary(self, text: str) -> str:
        """Create summary using existing logic"""
        try:
            response = await self.client.chat.completions.create(
                model=self.summary_model,
                messages=[
                    {"role": "system", "content": "Create a brief 1-2 sentence summary of the following text:"},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return ""

    def test_connection(self):
        """Test database connection and table existence"""
        try:
            # Use table selection instead of raw SQL
            response = self.supabase.table('video_transcriptions').select(
                'id', 
                count='exact'
            ).execute()
            
            count = len(response.data)
            self.logger.info(f"Successfully connected. Found {count} total segments.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False

    def fetch_video_segments(self, video_id: str) -> List[Dict]:
        """Fetch segments for a specific video"""
        try:
            response = self.supabase.table('video_transcriptions')\
                          .select('*')\
                          .filter('video_id', 'eq', video_id)\
                          .execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Error fetching segments: {e}")
            return []

    def is_topic_boundary(self, current_text: str, next_sentence: str) -> bool:
        """Check for topic shifts"""
        transition_phrases = [
            "however,", "on the other hand,", "in contrast,", "meanwhile,", 
            "turning to", "moving on", "another", "next", "additionally,"
        ]
        
        next_sentence_lower = next_sentence.lower()
        return any(phrase in next_sentence_lower for phrase in transition_phrases)

    def create_chunks_from_segments(self, segments: List[Dict]) -> List[ContentChunk]:
        """Create chunks from segments based on semantic grouping, respecting video boundaries"""
        chunks = []
        current_segments = []
        current_char_count = 0
        current_video_id = None  # Track current video_id
        
        for i, segment in enumerate(segments):
            # Check for video boundary
            if current_video_id is not None and segment['video_id'] != current_video_id:
                # If we have enough segments, create a final chunk for the previous video
                if len(current_segments) >= self.min_chunk_sentences:
                    chunk = ContentChunk(
                        text=" ".join(seg['content'] for seg in current_segments),
                        video_id=current_segments[0]['video_id'],
                        start_time=current_segments[0]['start_time'],
                        end_time=current_segments[-1]['end_time'],
                        segment_ids=[seg['id'] for seg in current_segments],
                        watch_url=current_segments[0]['watch_url']
                    )
                    chunks.append(chunk)
                # Reset for new video
                current_segments = []
                current_char_count = 0
            
            # Update current video_id
            current_video_id = segment['video_id']
            
            # Add segment to current group
            current_segments.append(segment)
            current_char_count += len(segment['content'])
            
            create_chunk = False
            
            # Check chunking conditions
            if len(current_segments) >= self.target_chunk_sentences:
                create_chunk = True
            elif current_char_count >= self.max_chunk_chars:
                create_chunk = True
            elif len(current_segments) >= self.min_chunk_sentences:
                if i < len(segments) - 1:
                    # Check if next segment is from a different video
                    if segments[i + 1]['video_id'] != current_video_id:
                        create_chunk = True
                    else:
                        # Check for topic boundary
                        current_topic = " ".join([s['content'] for s in current_segments[-2:]])
                        next_sentence = segments[i + 1]['content']
                        if self.is_topic_boundary(current_topic, next_sentence):
                            create_chunk = True
                elif i == len(segments) - 1:  # Last segment
                    create_chunk = True
            
            # Create chunk if conditions are met
            if create_chunk and len(current_segments) >= self.min_chunk_sentences:
                chunk = ContentChunk(
                    text=" ".join(seg['content'] for seg in current_segments),
                    video_id=current_segments[0]['video_id'],
                    start_time=current_segments[0]['start_time'],
                    end_time=current_segments[-1]['end_time'],
                    segment_ids=[seg['id'] for seg in current_segments],
                    watch_url=current_segments[0]['watch_url']
                )
                chunks.append(chunk)
                
                # Reset with overlap for context continuity, but only if we're staying in the same video
                if i < len(segments) - 1 and segments[i + 1]['video_id'] == current_video_id:
                    current_segments = current_segments[-1:]  # Keep last segment for overlap
                else:
                    current_segments = []  # Complete reset at video boundary
                current_char_count = sum(len(seg['content']) for seg in current_segments)
                
                self.logger.debug(f"Created chunk with {len(current_segments)} segments, {current_char_count} chars")
        
        # Handle any remaining segments if they meet minimum requirements
        if len(current_segments) >= self.min_chunk_sentences:
            chunk = ContentChunk(
                text=" ".join(seg['content'] for seg in current_segments),
                video_id=current_segments[0]['video_id'],
                start_time=current_segments[0]['start_time'],
                end_time=current_segments[-1]['end_time'],
                segment_ids=[seg['id'] for seg in current_segments],
                watch_url=current_segments[0]['watch_url']
            )
            chunks.append(chunk)
        
        self.logger.info(f"Created {len(chunks)} chunks from {len(segments)} segments")
        return chunks

    def check_chunk_exists(self, video_id: str, segment_ids: List[str]) -> bool:
        """Check if specific chunk exists based on video_id and segment_ids"""
        try:
            # Check for exact match using table operations
            response = self.supabase.table('document_embeddings')\
                .select('id')\
                .eq('video_id', video_id)\
                .contains('segment_ids', segment_ids)\
                .execute()
            
            exists = len(response.data) > 0
            
            if exists:
                self.logger.debug(f"Chunk exists for segments {segment_ids}")
            
            return exists
                
        except Exception as e:
            self.logger.error(f"Error checking chunk existence: {e}")
            return False

    def setup_tables(self):
        """Add necessary columns to video_transcriptions"""
        try:
            # Try to call the stored procedure
            self.supabase.rpc(
                'add_vector_columns'
            ).execute()
            
            self.logger.info("Successfully set up database tables")
            
        except Exception as e:
            if 'must be owner' in str(e):
                self.logger.warning("Permission error. Please run setup SQL in Supabase SQL editor.")
                # Continue execution even if setup fails
                return
            else:
                self.logger.error(f"Error setting up tables: {e}")
                raise

    async def process_transcript_batch(self, batch: List[Dict], max_concurrent: int = 5):
        """Process a batch of transcripts concurrently with embedding generation and database updates"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_transcript(segment: Dict):
            async with semaphore:
                try:
                    content_embedding, _ = await self.generate_embeddings(segment['content'])
                    # Update the database with the embedding
                    self.supabase.table('video_transcriptions').update({
                        'embedding': content_embedding
                    }).eq('id', segment['id']).execute()
                    self.logger.debug(f"Generated and saved embedding for segment {segment['id']}")
                except Exception as e:
                    self.logger.error(f"Error processing segment {segment['id']}: {e}")

        # Run tasks concurrently
        tasks = [process_transcript(segment) for segment in batch]
        await asyncio.gather(*tasks)

    def search_transcripts(self, query: str, limit: int = 5) -> List[Dict]:
        """Search individual transcripts"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Use existing match_transcripts function
            response = self.supabase.rpc(
                'match_transcripts',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit
                }
            ).execute()
            
            # Log search results
            self.logger.info(f"Found {len(response.data)} transcript matches for query: {query[:50]}...")
            
            return response.data
            
        except Exception as e:
            self.logger.error(f"Error searching transcripts: {e}")
            raise

    def search_chunks(self, query: str, limit: int = 5) -> List[Dict]:
        """Search document chunks"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Use match_documents function (you'll need to create this)
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit
                }
            ).execute()
            
            # Log search results
            self.logger.info(f"Found {len(response.data)} chunk matches for query: {query[:50]}...")
            
            return response.data
            
        except Exception as e:
            self.logger.error(f"Error searching chunks: {e}")
            raise

    def store_chunk(self, chunk: ContentChunk, content_embedding: List[float], summary_embedding: List[float]):
        """Store chunk with both embeddings"""
        try:
            self.supabase.table('document_embeddings').insert({
                'video_id': chunk.video_id,
                'start_time': chunk.start_time,
                'end_time': chunk.end_time,
                'text': chunk.text,
                'embedding': content_embedding,
                'summary': chunk.summary,
                'summary_embedding': summary_embedding,
                'segment_ids': chunk.segment_ids,
                'watch_url': chunk.watch_url,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            self.logger.error(f"Error storing chunk: {e}")
            raise

    def check_initial_state(self, video_id: str) -> bool:
        """Check if video already has embeddings"""
        try:
            # Check transcripts table
            transcript_response = self.supabase.table('video_transcriptions')\
                .select('id')\
                .eq('video_id', video_id)\
                .not_('embedding', 'is', 'null')\
                .execute()
            
            # Check chunks table
            chunks_response = self.supabase.table('document_embeddings')\
                .select('id')\
                .eq('video_id', video_id)\
                .execute()
            
            has_transcript_embeddings = len(transcript_response.data) > 0
            has_chunk_embeddings = len(chunks_response.data) > 0
            
            self.logger.info(f"Video {video_id} state check:")
            self.logger.info(f"- Transcript embeddings: {'Yes' if has_transcript_embeddings else 'No'}")
            self.logger.info(f"- Chunk embeddings: {'Yes' if has_chunk_embeddings else 'No'}")
            
            return has_transcript_embeddings and has_chunk_embeddings
            
        except Exception as e:
            self.logger.error(f"Error checking initial state: {e}")
            return False

    async def hybrid_search(self, query: str, limit: int = 10, content_weight: float = 0.7):
        try:
            query_embedding = await self.get_embedding(query)
            
            # Remove await from the RPC call
            results = self.supabase.rpc(
                'advanced_hybrid_search',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit,
                    'content_weight': content_weight,
                    'video_filter': None,
                    'min_similarity': 0.0
                }
            ).execute()  # execute() is synchronous
            
            print(f"Fetched {len(results.data)} results with limit {limit}")
            return results.data
            
        except Exception as e:
            print(f"Error in hybrid search: {str(e)}")
            raise

    def check_segment_embedding(self, segment_id: str) -> bool:
        """Check if embedding exists for a segment"""
        try:
            response = self.supabase.table(
                'video_transcriptions').select('embedding').eq(
                    'id', segment_id).execute()
            return response.data[0]['embedding'] is not None
        except IndexError:  # Explicit handling of missing data
            return False
        except Exception as e:
            self.logger.error(
                f"Error checking segment embedding existence: {e}")
            return False

    def batch_segments(self, segments: List[Dict], batch_size: int = 10) -> List[List[Dict]]:
        """Split segments into batches"""
        return [segments[i:i + batch_size] for i in range(0, len(segments), batch_size)]

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text input with token counting"""
        try:
            # Count tokens before sending
            input_tokens = self.count_tokens(text)
            self.tokens_sent += input_tokens
            self.logger.info(f"Sending {input_tokens} tokens to embedding API")

            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text.replace('\n', ' ').strip()
            )
            
            # Log token usage from response if available
            if hasattr(response, 'usage'):
                self.tokens_received += response.usage.total_tokens
                self.logger.info(f"Received {response.usage.total_tokens} tokens from embedding API")
            
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise

    async def run(self, video_id: str, force_reprocess: bool = False):
        """Main execution function with reprocess option"""
        try:
            self.setup_tables()
            if self.test_connection():
                if not force_reprocess and self.check_initial_state(video_id):
                    return False, "Video already processed"
                await self.process_video(video_id)
                return True, "Processing complete"
        except FuturesTimeoutError:
            error_msg = "Processing timed out. This might be due to rate limiting or connectivity issues."
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self.logger.exception(error_msg)
            return False, error_msg

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.tokenizer.encode(text))

if __name__ == "__main__":
    try:
        processor = DualEmbeddingVectorizer(
            embedding_model="text-embedding-3-small",
            summary_model="gpt-4o-mini"
        )
        
        if len(sys.argv) > 1:
            video_id = sys.argv[1]
        else:
            video_id = input("Please enter the video ID to process: ")
        
        print(f"\nProcessing video: {video_id}")
        
        should_reprocess = False
        if processor.check_initial_state(video_id):
            print(f"Video {video_id} already has embeddings. Do you want to reprocess? (y/n)")
            should_reprocess = input().lower() == 'y'
            if not should_reprocess:
                print("Skipping processing.")
                sys.exit(0)
        
        success, message = asyncio.run(processor.run(video_id, force_reprocess=should_reprocess))
        print(f"\n{message}")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError processing video: {str(e)}")
        raise