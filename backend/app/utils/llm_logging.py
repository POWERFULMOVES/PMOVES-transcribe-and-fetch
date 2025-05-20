import logging
from supabase import Client
from datetime import datetime
import json # For llm_extra_args if it's a string, though dict is preferred

# Configure a basic logger
logger = logging.getLogger(__name__)
# Example basic config if not configured elsewhere in the app:
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def _to_bool(value: any) -> bool | None:
    """Converts a value to boolean, handling common string representations."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
    # Try converting to int then bool for 0/1 cases
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        logger.warning(f"Could not convert value '{value}' of type {type(value)} to boolean.")
        return None # Or raise an error, or return a default

def _to_int(value: any) -> int | None:
    """Converts a value to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert value '{value}' of type {type(value)} to int.")
        return None

def _to_float(value: any) -> float | None:
    """Converts a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert value '{value}' of type {type(value)} to float.")
        return None

def log_llm_call(llm_log_data_dict: dict, supabase_client: Client) -> None:
    """
    Logs LLM call data to the Supabase llm_call_logs table.

    Args:
        llm_log_data_dict: The dictionary containing LLM log event data.
        supabase_client: An initialized Supabase client instance.
    """
    try:
        # Prepare data for insertion, mapping dict keys to table columns
        # and performing necessary type conversions.
        data_to_insert = {
            "url_crawled": llm_log_data_dict.get("url_crawled"),
            "request_timestamp": llm_log_data_dict.get("request_timestamp"), # Assumed to be ISO 8601 string or datetime object
            "llm_call_type": llm_log_data_dict.get("llm_call_type"),
            "strategy_type": llm_log_data_dict.get("strategy_type"),
            "llm_provider": llm_log_data_dict.get("llm_provider"),
            "model_name": llm_log_data_dict.get("model_name"),
            "llm_api_token_provided": _to_bool(llm_log_data_dict.get("llm_api_token_provided")),
            "llm_base_url": llm_log_data_dict.get("llm_base_url"),
            "instruction_prompt": llm_log_data_dict.get("instruction_prompt"),
            "user_intended_extraction_type": llm_log_data_dict.get("user_intended_extraction_type"),
            "extraction_type_setting": llm_log_data_dict.get("extraction_type_setting"),
            "schema_definition_provided": _to_bool(llm_log_data_dict.get("schema_definition_provided")),
            "chunking_applied": _to_bool(llm_log_data_dict.get("chunking_applied")),
            "chunk_token_threshold_setting": _to_int(llm_log_data_dict.get("chunk_token_threshold_setting")),
            "chunk_overlap_rate_setting": _to_float(llm_log_data_dict.get("chunk_overlap_rate_setting")),
            "input_content_format": llm_log_data_dict.get("input_content_format"),
            "llm_extra_args": llm_log_data_dict.get("llm_extra_args"), # Should be a dict for JSONB
            "llm_call_duration_ms": _to_int(llm_log_data_dict.get("llm_call_duration_ms")),
            "call_successful": _to_bool(llm_log_data_dict.get("call_successful")),
            "prompt_tokens_total": _to_int(llm_log_data_dict.get("prompt_tokens_total")),
            "completion_tokens_total": _to_int(llm_log_data_dict.get("completion_tokens_total")),
            "total_tokens_used": _to_int(llm_log_data_dict.get("total_tokens_used")),
            "cost": _to_float(llm_log_data_dict.get("cost")), # Numeric in DB
            "number_of_chunks_processed": _to_int(llm_log_data_dict.get("number_of_chunks_processed")),
            "llm_response_id": llm_log_data_dict.get("llm_response_id"),
            "error_type": llm_log_data_dict.get("error_type"),
            "error_message_detail": llm_log_data_dict.get("error_message_detail"),
            "extracted_content_preview": llm_log_data_dict.get("extracted_content_preview"),
            "input_text_preview": llm_log_data_dict.get("input_text_preview"),
            "crawl_status_code": _to_int(llm_log_data_dict.get("crawl_status_code")),
            "crawl_session_id": llm_log_data_dict.get("crawl_session_id"),
        }

        # Filter out None values if the database schema doesn't allow NULLs for certain fields
        # or if you prefer not to send them. For this schema, most fields are nullable.
        # data_to_insert = {k: v for k, v in data_to_insert.items() if v is not None}

        # Perform the insertion
        response = supabase_client.table("llm_call_logs").insert(data_to_insert).execute()

        # Log success or check response if needed
        if response.data:
            logger.info(f"Successfully logged LLM call. Log ID (from response): {response.data[0].get('id') if response.data and len(response.data) > 0 else 'N/A'}")
        else:
            # This case might indicate an issue if data was expected in the response
            # For insert, often an empty list or specific error structure is returned on failure by some clients
            logger.warning(f"LLM call log insertion executed, but response.data is empty or not as expected: {response}")
            if hasattr(response, 'error') and response.error:
                 logger.error(f"Supabase API Error during LLM log insertion: {response.error.message}")


    except Exception as e:
        # Catching supabase.lib.client_options.APIError specifically can be done
        # or a more general exception.
        logger.error(f"Error logging LLM call to Supabase: {e}", exc_info=True)
        # Depending on requirements, you might want to re-raise the exception
        # or handle it silently after logging.

if __name__ == '__main__':
    # Example Usage (requires a Supabase client and connection details)
    # This is for testing purposes and should be adapted or removed for production.
    
    # Basic logging setup for the example
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Mock Supabase client for local testing without actual DB connection
    class MockSupabaseClient:
        def table(self, table_name):
            logger.info(f"MockSupabaseClient: Accessing table '{table_name}'")
            return self
        
        def insert(self, data):
            logger.info(f"MockSupabaseClient: Preparing to insert data: {json.dumps(data, indent=2, default=str)}")
            # Simulate a successful response structure
            class MockResponse:
                def __init__(self, data_inserted):
                    # Simulate the structure of a successful insert response
                    # Supabase often returns the inserted row(s) in `data`
                    self.data = [data_inserted] # Or an empty list if that's what your client version does
                    self.error = None 
                    # Add other attributes like count if your client version provides them
                    self.count = len(self.data) if self.data else 0


                def execute(self):
                    logger.info("MockSupabaseClient: Executing insert.")
                    # In a real scenario, this would make the API call
                    # For mock, just return self to simulate the chained call ending
                    return self # The execute() method itself returns the response object

            # Create a mock response object. You might need to adjust this based on
            # the actual structure returned by your version of the supabase-py client.
            # Typically, an insert operation returns the inserted record(s).
            # We'll add a dummy 'id' as the DB would.
            mock_inserted_data = data.copy()
            mock_inserted_data['id'] = 'mock-uuid-generated-by-db' 
            mock_inserted_data['created_at'] = datetime.utcnow().isoformat() + '+00:00' # Simulate DB timestamp
            
            return MockResponse(mock_inserted_data)


    mock_client = MockSupabaseClient()

    sample_log_data_valid = {
        "url_crawled": "http://example.com/article1",
        "request_timestamp": datetime.utcnow().isoformat() + "Z", # ISO 8601 format
        "llm_call_type": "extraction",
        "strategy_type": "full_page_summary",
        "llm_provider": "OpenAI",
        "model_name": "gpt-3.5-turbo",
        "llm_api_token_provided": True,
        "llm_base_url": "https://api.openai.com/v1",
        "instruction_prompt": "Summarize the following content...",
        "user_intended_extraction_type": "summary",
        "extraction_type_setting": "text_summary",
        "schema_definition_provided": False,
        "chunking_applied": True,
        "chunk_token_threshold_setting": 1000,
        "chunk_overlap_rate_setting": 0.1,
        "input_content_format": "text/plain",
        "llm_extra_args": {"temperature": 0.7, "max_tokens": 500},
        "llm_call_duration_ms": 12345,
        "call_successful": True,
        "prompt_tokens_total": 1200,
        "completion_tokens_total": 300,
        "total_tokens_used": 1500,
        "cost": 0.0025,
        "number_of_chunks_processed": 2,
        "llm_response_id": "resp_abc123",
        "error_type": None,
        "error_message_detail": None,
        "extracted_content_preview": "This is a summary of the article...",
        "input_text_preview": "The full article text starts here...",
        "crawl_status_code": 200,
        "crawl_session_id": "sess_xyz789"
    }

    sample_log_data_minimal = {
        "model_name": "gpt-4",
        "call_successful": "false", # Test string boolean
        "cost": "0.123", # Test string float
        "total_tokens_used": "500" # Test string int
    }
    
    sample_log_data_error = {
        "model_name": "gpt-error-model",
        "call_successful": False,
        "error_type": "APIError",
        "error_message_detail": "The model failed to respond due to an internal server error.",
        "request_timestamp": "2023-10-26T10:30:00Z" # Example timestamp
    }

    logger.info("Testing with valid sample data:")
    log_llm_call(sample_log_data_valid, mock_client)
    
    logger.info("\nTesting with minimal sample data (and string types for conversion):")
    log_llm_call(sample_log_data_minimal, mock_client)

    logger.info("\nTesting with error sample data:")
    log_llm_call(sample_log_data_error, mock_client)

    # Example of how to use with a real Supabase client (requires environment variables)
    # import os
    # from supabase import create_client
    # SUPABASE_URL = os.environ.get("SUPABASE_URL")
    # SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # Use service key for backend operations
    # if SUPABASE_URL and SUPABASE_KEY:
    #     real_supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    #     logger.info("\nTesting with REAL Supabase client (if configured):")
    #     log_llm_call(sample_log_data_valid, real_supabase_client)
    # else:
    #     logger.warning("\nSkipping real Supabase client test: SUPABASE_URL or SUPABASE_SERVICE_KEY not set.")