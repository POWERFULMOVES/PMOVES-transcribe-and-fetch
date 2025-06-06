import os
import logging
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Singleton instance of the Supabase client
_supabase_client: Optional[Client] = None


def get_client() -> Client:
    """
    Initializes and returns a singleton Supabase client instance.
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
            logger.info("Initializing Supabase client singleton from dependencies...")
            _supabase_client = create_client(url, key)
            logger.info(
                "Supabase client singleton initialized successfully from dependencies."
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            # Re-raise to make it clear that initialization failed
            raise
    return _supabase_client
