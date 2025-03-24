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
import re
import math

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
                        input=input_text.replace('\n', ' ').strip(),
                        encoding_format="float"
                    )
                    return response.data[0].embedding
                except Exception as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"Final embedding attempt failed: {str(e)}")
                        raise
                    jitter = random.uniform(0, 0.1)
                    wait = (wait_time * (2**attempt)) + jitter
                    self.logger.warning(f"Embedding attempt {attempt + 1} failed: {str(e)}. Retrying in {wait:.2f}s")
                    await asyncio.sleep(wait)

        async def batch_generate_embeddings(texts: List[str]) -> List[List[float]]:
            """Generate embeddings in batches for better efficiency"""
            if not texts:
                return []
            
            try:
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=[text.replace('\n', ' ').strip() for text in texts],
                    encoding_format="float"
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                self.logger.error(f"Batch embedding generation failed: {str(e)}")
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
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def create_summary(self, text: str) -> str:
        """Create a summary of the text using the specified model"""
        max_retries = 3
        wait_time = 1
        
        for attempt in range(max_retries):
            try:
                completion = await self.client.chat.completions.create(
                    model=self.summary_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Please summarize this text concisely:\n\n{text}"}
                    ],
                    temperature=0.3,
                    max_tokens=150
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Final summary attempt failed: {str(e)}")
                    raise
                jitter = random.uniform(0, 0.1)
                wait = (wait_time * (2**attempt)) + jitter
                self.logger.warning(f"Summary attempt {attempt + 1} failed: {str(e)}. Retrying in {wait:.2f}s")
                await asyncio.sleep(wait)

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
            self.logger.error(f"Error checking initial state: {str(e)}")
            return False

    def fetch_video_segments(self, video_id: str) -> List[Dict]:
        """Fetch segments for a specific video"""
        try:
            response = self.supabase.table('video_transcriptions')\
                .select('*')\
                .eq('video_id', video_id)\
                .execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Error fetching segments: {str(e)}")
            return []

    def check_chunk_exists(self, video_id: str, segment_ids: List[str]) -> bool:
        """Check if specific chunk exists based on video_id and segment_ids"""
        try:
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
            self.logger.error(f"Error checking chunk existence: {str(e)}")
            return False

    def is_topic_boundary(self, current_text: str, next_sentence: str) -> bool:
        """Check for topic shifts"""
        transition_phrases = [
            "however,", "on the other hand,", "in contrast,", "meanwhile,", 
            "turning to", "moving on", "another", "next", "additionally,"
        ]
        
        next_sentence_lower = next_sentence.lower()
        return any(phrase in next_sentence_lower for phrase in transition_phrases)

    async def process_video(self, video_id: str):
        """Process video with improved batch handling"""
        start_time = datetime.now()
        self.logger.info(f"Starting video processing at {start_time}")

        # Fetch segments
        segments = self.fetch_video_segments(video_id)
        if not segments:
            self.logger.warning(f"No segments found for video_id: {video_id}")
            return False, "No segments found"

        try:
            # Phase 1: Process individual segments and store in video_transcriptions
            self.logger.info(f"Phase 1: Processing {len(segments)} segments in batches")
            batch_size = 50
            phase1_success = True
            
            # Find segments missing embeddings
            missing_embeddings = [
                segment for segment in segments 
                if not segment.get('embedding')
            ]

            if missing_embeddings:
                for i in range(0, len(missing_embeddings), batch_size):
                    batch = missing_embeddings[i:i + batch_size]
                    try:
                        # Generate embeddings for batch
                        contents = [seg['content'] for seg in batch]
                        embeddings = await self.batch_generate_embeddings(contents)
                        
                        # Prepare batch updates for video_transcriptions
                        updates = []
                        for seg, embedding in zip(batch, embeddings):
                            if embedding:
                                updates.append({
                                    'id': seg['id'],
                                    'embedding': embedding
                                })
                        
                        # Update video_transcriptions
                        if updates:
                            result = self.supabase.table('video_transcriptions')\
                                .upsert(updates)\
                                .execute()
                            
                            if not result.data:
                                self.logger.error(f"Failed to update video_transcriptions for batch {i//batch_size + 1}")
                                phase1_success = False
                                break
                        
                        self.logger.info(f"Processed batch {i//batch_size + 1} of {(len(missing_embeddings)-1)//batch_size + 1}")
                    except Exception as e:
                        self.logger.error(f"Error processing batch starting at index {i}: {str(e)}")
                        phase1_success = False
                        break

            if not phase1_success:
                self.logger.error("Phase 1 failed, skipping Phase 2")
                return False, "Failed to process video transcriptions"

            # Phase 2: Create and process document chunks
            self.logger.info("Phase 2: Creating and processing document chunks")
            chunks = self.create_chunks_from_segments(segments)
            
            # Filter out existing chunks
            chunks_to_process = [
                chunk for chunk in chunks 
                if not self.check_chunk_exists(chunk.video_id, chunk.segment_ids)
            ]

            if chunks_to_process:
                self.logger.info(f"Processing {len(chunks_to_process)} new chunks")
                chunk_inserts = []
                
                for chunk in chunks_to_process:
                    try:
                        # Generate chunk text embedding
                        content_embedding, _ = await self.generate_embeddings(text=chunk.text)
                        
                        # Generate summary and its embedding
                        chunk.summary = await self.create_summary(chunk.text)
                        _, summary_embedding = await self.generate_embeddings(summary=chunk.summary)
                        
                        if content_embedding and summary_embedding:
                            chunk_inserts.append({
                                'video_id': chunk.video_id,
                                'start_time': chunk.start_time,
                                'end_time': chunk.end_time,
                                'text': chunk.text,
                                'embedding': content_embedding,  # Store chunk-level embedding
                                'summary': chunk.summary,
                                'summary_embedding': summary_embedding,
                                'segment_ids': chunk.segment_ids,
                                'watch_url': chunk.watch_url,
                                'created_at': datetime.now().isoformat()
                            })
                    except Exception as e:
                        self.logger.error(f"Error processing chunk {chunk.segment_ids}: {str(e)}")
                        continue

                # Batch insert all chunks at once
                if chunk_inserts:
                    try:
                        self.supabase.table('document_embeddings')\
                            .insert(chunk_inserts)\
                            .execute()
                        self.logger.info(f"Successfully inserted {len(chunk_inserts)} chunks")
                    except Exception as e:
                        self.logger.error(f"Error during batch insert: {str(e)}")
                        return False, f"Failed to insert chunks: {str(e)}"

            duration = datetime.now() - start_time
            self.logger.info(f"Processing complete in {duration}")
            return True, "Processing completed successfully"

        except Exception as e:
            self.logger.error(f"Error during video processing: {str(e)}")
            return False, f"Processing failed: {str(e)}"

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batches for better efficiency"""
        if not texts:
            return []
        
        try:
            # Clean and prepare texts
            cleaned_texts = [text.replace('\n', ' ').strip() for text in texts]
            
            # Generate embeddings
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=cleaned_texts,
                encoding_format="float"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            self.logger.error(f"Batch embedding generation failed: {str(e)}")
            raise

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

    async def run(self, video_id: str, force_reprocess: bool = False) -> Tuple[bool, str]:
        """Main execution function with reprocess option"""
        try:
            if not force_reprocess and self.check_initial_state(video_id):
                return False, "Video already processed"
            
            success, message = await self.process_video(video_id)
            return success, message
            
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            self.logger.exception(error_msg)
            return False, error_msg

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