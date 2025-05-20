import os
import sys
import asyncio
import httpx
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure test_ollama_connection.py is in the backend/app directory.")
    sys.exit(1)

async def test_ollama():
    """
    Tests connection to Ollama server and sends a simple message to the selected model.
    """
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.error("LLM_MODEL environment variable not set. Cannot test Ollama connection.")
        logger.info("Please set the LLM_MODEL environment variable (e.g., $env:LLM_MODEL='ollama/gemma3' in PowerShell) before running this script.")
        return

    logger.info(f"Selected LLM_MODEL for testing: {selected_model_id}")

    model_config = None
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config or model_config.get('provider_group') != 'Ollama (Local)':
        logger.error(f"Model ID '{selected_model_id}' is not configured as a local Ollama model in app_config.py.")
        logger.info("Please ensure LLM_MODEL is set to a valid Ollama model ID from app_config.AVAILABLE_MODELS.")
        return

    ollama_model_name = selected_model_id.replace("ollama/", "") # Get just the model name part
    ollama_url = OLLAMA_BASE_URL # Use the base URL from app_config

    if not ollama_url:
        logger.error("OLLAMA_BASE_URL is not set in environment variables or app_config.py.")
        return

    chat_endpoint = f"{ollama_url}/api/chat"
    logger.info(f"Attempting to connect to Ollama at {ollama_url} and test model '{ollama_model_name}' via {chat_endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            # First, check if the server is reachable
            try:
                # A simple GET request to the base URL might be enough to check if the server is up
                # Or a specific health check endpoint if Ollama provides one.
                # Let's try the chat endpoint directly with a small timeout for initial check.
                logger.info(f"Checking if Ollama server is reachable at {ollama_url}...")
                response = await client.get(ollama_url, timeout=5.0)
                response.raise_for_status() # Raise an exception for bad status codes
                logger.info("Ollama server is reachable.")
            except httpx.RequestError as e:
                logger.error(f"Ollama server not reachable at {ollama_url}: {e}")
                logger.info("Please ensure your Ollama server is running.")
                return
            except httpx.HTTPStatusError as e:
                 logger.warning(f"Ollama server returned status {e.response.status_code} on reachability check: {e.response.text}")
                 # Server is up, but maybe the endpoint is different or requires POST. Proceed to chat test.


            # Now, attempt to send a message to the model
            logger.info(f"Attempting to send a message to model '{ollama_model_name}'...")
            chat_payload = {
                "model": ollama_model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": False, # Request non-streaming response
                "options": {"num_predict": 10} # Keep response small
            }
            
            chat_response = await client.post(chat_endpoint, json=chat_payload, timeout=30.0)
            chat_response.raise_for_status() # Raise an exception for bad status codes

            response_data = chat_response.json()
            
            if response_data and response_data.get("message") and response_data["message"].get("content"):
                logger.info("Ollama server responded successfully!")
                logger.info(f"Model '{ollama_model_name}' responded with: '{response_data['message']['content'][:100]}...'")
                logger.info("Ollama connection test successful.")
            else:
                logger.error("Ollama server responded, but the response format was unexpected or empty.")
                logger.debug(f"Full response data: {response_data}")
                logger.info("Ollama connection test failed: Unexpected response.")

    except httpx.RequestError as e:
        logger.error(f"Error sending message to Ollama model '{ollama_model_name}': {e}")
        logger.info("Ollama connection test failed: Request error.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama server returned error status {e.response.status_code} for model '{ollama_model_name}': {e.response.text}")
        logger.info(f"Ollama connection test failed: HTTP error. Ensure model '{ollama_model_name}' is available on your Ollama server (run 'ollama list').")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama connection test: {e}", exc_info=True)
        logger.info("Ollama connection test failed: Unexpected exception.")


if __name__ == "__main__":
    logger.info("Running Ollama connection test script.")
    asyncio.run(test_ollama())
    logger.info("Ollama connection test script finished.")
