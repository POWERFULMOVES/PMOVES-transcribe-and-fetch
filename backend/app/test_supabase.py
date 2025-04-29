"""
Test script to check Supabase connection and search functionality.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Import after loading environment variables
try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase-py package not installed. Run 'pip install supabase'")
    sys.exit(1)

def get_client() -> Client:
    """
    Get a client for connecting to the Supabase database.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY environment variable is not set")
    
    print(f"Connecting to Supabase URL: {supabase_url}")
    client = create_client(supabase_url, supabase_key)
    return client

def test_connection():
    """Test the Supabase connection."""
    try:
        client = get_client()
        print("Successfully connected to Supabase!")
        return client
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None

def test_search(client, query="test"):
    """Test the search functionality."""
    if not client:
        print("No Supabase client available.")
        return
    
    try:
        # Test video_transcriptions table
        print(f"\nTesting video_transcriptions table with query: '{query}'")
        response = client.table("video_transcriptions").select("*").limit(5).execute()
        data = response.data
        print(f"Found {len(data)} records in video_transcriptions table")
        if data:
            print(f"First record: {data[0]}")
        
        # Test document_embeddings table
        print(f"\nTesting document_embeddings table")
        response = client.table("document_embeddings").select("*").limit(5).execute()
        data = response.data
        print(f"Found {len(data)} records in document_embeddings table")
        if data:
            print(f"First record: {data[0]}")
        
        # Test video_transcriptions_full table
        print(f"\nTesting video_transcriptions_full table")
        response = client.table("video_transcriptions_full").select("*").limit(5).execute()
        data = response.data
        print(f"Found {len(data)} records in video_transcriptions_full table")
        if data:
            print(f"First record: {data[0]}")
        
    except Exception as e:
        print(f"Error testing search: {e}")

if __name__ == "__main__":
    client = test_connection()
    if client:
        test_search(client)
    else:
        print("Failed to connect to Supabase. Check your environment variables.")
