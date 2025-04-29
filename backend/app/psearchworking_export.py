"""
Export module for psearchworking.py

This module re-exports the necessary functions and classes from psearchworking.py
to provide a clean interface for other modules to use.
"""

from .psearchworking import (
    search_all, analyze_search_results, get_client,
    SearchParameters, SearchResult,
    TokenCounter, ModelSelector
)

# Initialize global search parameters
from .psearchworking import SearchParameters
global_search_params = SearchParameters()

# Re-export the necessary functions and classes
__all__ = [
    'search_all',
    'analyze_search_results',
    'get_client',
    'SearchParameters',
    'global_search_params',
    'SearchResult',
    'TokenCounter',
    'ModelSelector'
]
