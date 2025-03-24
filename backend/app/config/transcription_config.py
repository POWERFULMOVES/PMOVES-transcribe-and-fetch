"""
Transcription configuration file for PMOVES.

This file contains configuration variables for the transcription functionality
including Whisper model settings and API keys.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get the app directory path
APP_DIR = Path(__file__).parent.parent.absolute()
ENV_PATH = APP_DIR / '.env'

# Load environment variables from the specific .env file location
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"Loaded environment variables from {ENV_PATH}")
else:
    print(f"Warning: .env file not found at {ENV_PATH}")
    # Fallback to default load_dotenv behavior
    load_dotenv()

# Whisper model configuration
WHISPER_MODEL = "medium"
WHISPER_DEVICE = "cpu"  # can be "cpu" or "cuda" 
WHISPER_COMPUTE_TYPE = "int8"  # can be "float16", "int8", etc.

# API keys - get from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY environment variable is not set")

# Output folder
DEFAULT_OUTPUT_FOLDER = "transcriptions" 