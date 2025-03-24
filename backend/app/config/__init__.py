"""
Config package for PMOVES search application.
"""

# Import and re-export transcription config variables
from .transcription_config import (
    WHISPER_MODEL,
    WHISPER_DEVICE, 
    WHISPER_COMPUTE_TYPE,
    GROQ_API_KEY,
    DEFAULT_OUTPUT_FOLDER
)

# Import and re-export search config
from .search_config import (
    DEFAULT_SEARCH_PARAMS,
    SEARCH_PRESETS,
    validate_search_params,
    get_preset
) 