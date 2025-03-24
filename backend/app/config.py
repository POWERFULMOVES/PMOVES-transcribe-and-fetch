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

# Default paths
DEFAULT_OUTPUT_FOLDER = os.getenv('DEFAULT_OUTPUT_FOLDER', os.path.join(os.getcwd(), 'output'))
DEFAULT_OBSIDIAN_DIR = os.getenv('DEFAULT_OBSIDIAN_DIR', '')

# Path to wkhtmltopdf executable
WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
if not os.path.isfile(WKHTMLTOPDF_PATH):
    logger.warning(
        f"wkhtmltopdf not found at '{WKHTMLTOPDF_PATH}'. "
        f"PDF generation will fail unless properly configured. "
        f"Please install wkhtmltopdf or set WKHTMLTOPDF_PATH in .env file."
    )

# Whisper model settings
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'large-v3')
WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cuda')
WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'float16')

# Groq API settings
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_BASE = os.getenv('GROQ_API_BASE', 'https://api.groq.com/v1')

# Model configurations
AVAILABLE_MODELS = {
    'faster-whisper': {
        'name': 'faster-whisper',
        'description': 'Local Faster Whisper model',
        'requires_gpu': True
    },
    'llama-3.3-70b': {
        'name': 'groq/llama-3.3-70b',
        'description': 'Llama 3.3 70B via Groq API',
        'requires_api_key': True
    },
    'mixtral': {
        'name': 'groq/mixtral',
        'description': 'Mixtral via Groq API',
        'requires_api_key': True
    }
}

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

# Validate Groq API key if using Groq models
def validate_groq_config():
    """Validate Groq API configuration."""
    if not GROQ_API_KEY and any(model['requires_api_key'] for model in AVAILABLE_MODELS.values()):
        raise ValueError(
            "GROQ_API_KEY environment variable is required for Groq models. "
            "Please set it in your .env file."
        )