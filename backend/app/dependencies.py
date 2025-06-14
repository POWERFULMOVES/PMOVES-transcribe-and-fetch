import os
import logging
from typing import Optional

from supabase import create_client, AsyncClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

_supabase_client: Optional[AsyncClient] = None

async def get_client() -> AsyncClient:
    """
    Initializes and returns a singleton Supabase AsyncClient instance.
    """
    global _supabase_client
    if _supabase_client is None:
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError(
                    "Supabase URL or Key is not set in environment variables."
                )
            logger.info("Initializing Supabase AsyncClient singleton from dependencies...")
            _supabase_client = create_client(url, key, is_async=True)
            logger.info(
                "Supabase AsyncClient singleton initialized successfully from dependencies."
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase AsyncClient: {e}", exc_info=True)
            raise
    return _supabase_client