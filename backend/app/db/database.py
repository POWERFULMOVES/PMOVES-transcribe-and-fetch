import os
from supabase import create_client
from dotenv import load_dotenv

def get_client():
    """
    Get a client for connecting to the Supabase database.
    Returns a configured Supabase client.
    """
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
            
    return create_client(supabase_url, supabase_key) 