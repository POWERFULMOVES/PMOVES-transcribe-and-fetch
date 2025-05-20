import os
import subprocess
import sys
import logging
from pathlib import Path
import httpx

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend/app to sys.path to allow importing app_config
backend_app_dir = Path(__file__).parent
sys.path.insert(0, str(backend_app_dir))

try:
    from app_config import AVAILABLE_MODELS, OLLAMA_BASE_URL
except ImportError:
    logger.error("Could not import app_config. Make sure ollama_initializer.py is in the backend/app directory.")
    sys.exit(1)

async def ensure_ollama_model_loaded():
    """
    Checks the selected LLM model from environment variables and
    loads it via the Ollama API if it's an Ollama model and not already loaded.
    """
    selected_model_id = os.getenv('LLM_MODEL')

    if not selected_model_id:
        logger.info("LLM_MODEL environment variable not set. Skipping Ollama model loading.")
        return

    logger.info(f"Selected LLM_MODEL: {selected_model_id}")

    model_config = None
    for model_info in AVAILABLE_MODELS.values():
        if model_info.get('id') == selected_model_id:
            model_config = model_info
            break

    if not model_config:
        logger.warning(f"Model ID '{selected_model_id}' not found in AVAILABLE_MODELS config. Cannot determine if it's an Ollama model.")
        return

    if model_config.get('provider_group') == 'Ollama (Local)':
        ollama_model_id = model_config.get('id')
        logger.info(f"Selected model '{selected_model_id}' is an Ollama model. Checking if loaded via Ollama API.")

        try:
            async with httpx.AsyncClient() as client:
                # Check if Ollama server is running and model is loaded
                try:
                    response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
                    response.raise_for_status()
                    loaded_models = response.json().get('models', [])
                    loaded_model_names = [model.get('name') for model in loaded_models]

                    if f"{ollama_model_id}:latest" in loaded_model_names or ollama_model_id in loaded_model_names:
                        logger.info(f"Ollama model '{ollama_model_id}' is already loaded.")
                        return
                    else:
                        logger.info(f"Ollama model '{ollama_model_id}' not loaded. Attempting to pull.")
                        # Initiate model pull
                        pull_response = await client.post(
                            f"{OLLAMA_BASE_URL}/api/pull",
                            json={"name": ollama_model_id, "stream": False},
                            timeout=600 # Allow up to 10 minutes for pull
                        )
                        pull_response.raise_for_status()
                        logger.info(f"Ollama model '{ollama_model_id}' pull initiated successfully.")

                except httpx.ConnectError:
                    logger.error(f"Could not connect to Ollama server at {OLLAMA_BASE_URL}. Make sure Ollama is running.")
                except httpx.RequestError as e:
                    logger.error(f"An error occurred while requesting Ollama API: {e}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred during Ollama API interaction: {e}")

        except Exception as e:
            logger.error(f"An error occurred during Ollama initialization: {e}")
    else:
        logger.info(f"Selected model '{selected_model_id}' is not an Ollama model. Skipping Ollama model loading.")

if __name__ == "__main__":
    logger.info("Running Ollama initializer script.")
    # Note: Running this script directly will not work as expected
    # because ensure_ollama_model_loaded is now an async function.
    # It is intended to be called from an async context like FastAPI startup.
    logger.warning("Running ollama_initializer.py directly will not execute the async logic.")
    logger.info("Ollama initializer script finished.")
