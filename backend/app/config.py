import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the current directory (where config.py is)
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

logger.info(f"Looking for .env file at: {env_path}")
# Force reload of environment variables
load_dotenv(env_path, override=True)

WKHTMLTOPDF_PATH = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
WHISPER_MODEL = "large-v3"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
DEFAULT_OUTPUT_FOLDER = os.getenv('DEFAULT_OUTPUT_FOLDER', 'output')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Debug logging
logger.info(f"GROQ_API_KEY loaded: {'Yes' if GROQ_API_KEY else 'No'}")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY is not set in environment variables")
else:
    # Log first few characters to verify it's loaded correctly
    logger.info(f"GROQ_API_KEY starts with: {GROQ_API_KEY[:10]}...")

# Additional verification
if GROQ_API_KEY == "your_groq_api_key_here":
    logger.error("Default API key value detected - please update your .env file")