"""
Config package for PMOVES search application.

NOTE: All runtime config (e.g., WHISPER_MODEL, API keys) should be imported directly from app_config.py.
This __init__.py only re-exports search config for convenience.
"""

# Import and re-export search config only
from .search_config import (
    DEFAULT_SEARCH_PARAMS,
    SEARCH_PRESETS,
    validate_search_params,
    get_preset
) 