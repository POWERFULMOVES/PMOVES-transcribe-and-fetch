"""
Search configuration file for PMOVES vector search.

This file contains default values and preset configurations for the search parameters
used in the vector search functionality. Both frontend and backend can use these values
to ensure consistency.
"""

import logging
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Default search parameters
DEFAULT_SEARCH_PARAMS = {
    "fine_grained": {
        "similarity_threshold": 0.75,
        "content_weight": 0.8,
        "result_percentage": 0.4,
        "max_results": 15
    },
    "contextual": {
        "similarity_threshold": 0.7,
        "content_weight": 0.7,
        "result_percentage": 0.35,
        "max_results": 10
    },
    "overview": {
        "similarity_threshold": 0.65,
        "content_weight": 0.5,
        "result_percentage": 0.25,
        "max_results": 5
    }
}

# Preset configurations for different search scenarios
SEARCH_PRESETS = {
    "default": DEFAULT_SEARCH_PARAMS,
    
    "technical": {
        "fine_grained": {
            "similarity_threshold": 0.8,
            "content_weight": 0.9,
            "result_percentage": 0.6,
            "max_results": 20
        },
        "contextual": {
            "similarity_threshold": 0.75,
            "content_weight": 0.8,
            "result_percentage": 0.3,
            "max_results": 10
        },
        "overview": {
            "similarity_threshold": 0.7,
            "content_weight": 0.7,
            "result_percentage": 0.1,
            "max_results": 3
        }
    },
    
    "conceptual": {
        "fine_grained": {
            "similarity_threshold": 0.7,
            "content_weight": 0.6,
            "result_percentage": 0.2,
            "max_results": 5
        },
        "contextual": {
            "similarity_threshold": 0.7,
            "content_weight": 0.5,
            "result_percentage": 0.4,
            "max_results": 15
        },
        "overview": {
            "similarity_threshold": 0.65,
            "content_weight": 0.3,
            "result_percentage": 0.4,
            "max_results": 15
        }
    },
    
    "balanced": {
        "fine_grained": {
            "similarity_threshold": 0.7,
            "content_weight": 0.6,
            "result_percentage": 0.4,
            "max_results": 12
        },
        "contextual": {
            "similarity_threshold": 0.7,
            "content_weight": 0.6,
            "result_percentage": 0.4,
            "max_results": 12
        },
        "overview": {
            "similarity_threshold": 0.65,
            "content_weight": 0.4,
            "result_percentage": 0.2,
            "max_results": 8
        }
    }
}

# Validation settings
VALIDATION_LIMITS = {
    "similarity_threshold": {
        "min": 0.0,
        "max": 1.0
    },
    "content_weight": {
        "min": 0.0,
        "max": 1.0
    },
    "result_percentage": {
        "min": 0.0,
        "max": 1.0
    },
    "max_results": {
        "min": 1,
        "max": 50
    }
}

def validate_search_params(params: dict) -> bool:
    """Validate search parameters to ensure they're within acceptable ranges.
    
    Args:
        params: Dictionary of search parameters by tier
        
    Returns:
        bool: True if all parameters are valid, False otherwise
    """
    if not params:
        return False
        
    for tier, tier_params in params.items():
        # Check required parameters
        if 'similarity_threshold' not in tier_params:
            logging.warning(f"Missing similarity_threshold for {tier}")
            return False
            
        if 'content_weight' not in tier_params:
            logging.warning(f"Missing content_weight for {tier}")
            return False
            
        if 'result_percentage' not in tier_params:
            logging.warning(f"Missing result_percentage for {tier}")
            return False
            
        # Value range validation
        similarity = tier_params.get('similarity_threshold')
        if not 0 <= similarity <= 1:
            logging.warning(f"Invalid similarity_threshold for {tier}: {similarity}")
            return False
            
        content_weight = tier_params.get('content_weight')
        if not 0 <= content_weight <= 1:
            logging.warning(f"Invalid content_weight for {tier}: {content_weight}")
            return False
            
        result_percentage = tier_params.get('result_percentage')
        if not 0 <= result_percentage <= 1:
            logging.warning(f"Invalid result_percentage for {tier}: {result_percentage}")
            return False
            
        # Validate max_results if present
        if 'max_results' in tier_params:
            max_results = tier_params.get('max_results')
            # Convert to int if it's a float
            if isinstance(max_results, float):
                tier_params['max_results'] = int(max_results)
            # Validate range
            if not 1 <= int(tier_params['max_results']) <= 50:
                logging.warning(f"Invalid max_results for {tier}: {max_results}")
                return False
            
    return True

def get_preset(preset_name: str = "default") -> dict:
    """Get a specific preset configuration by name.
    
    Args:
        preset_name: Name of the preset to retrieve
        
    Returns:
        dict: Preset configuration or default if not found
    """
    return SEARCH_PRESETS.get(preset_name, DEFAULT_SEARCH_PARAMS)

@router.get("/", summary="Get Default Search Configuration")
async def get_default_search_config_route(): # Renamed to avoid conflict if imported directly
    """
    Retrieve the default search parameters.
    This endpoint is tested by `test_get_search_config`.
    """
    return DEFAULT_SEARCH_PARAMS

@router.get("/presets", summary="Get All Search Presets")
async def get_all_search_presets_route(): # Renamed
    """
    Retrieve all available search preset configurations.
    This endpoint is tested by `test_get_presets`.
    The test expects the response in the format: {"presets": {"default": ..., ...}}
    """
    return {"presets": SEARCH_PRESETS}

@router.get("/presets/{preset_name}", summary="Get Specific Search Preset")
async def get_specific_search_preset_route(preset_name: str): # Renamed
    """
    Retrieve a specific search preset configuration by name.
    This endpoint is tested by `test_get_preset_config`.
    """
    preset = SEARCH_PRESETS.get(preset_name)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found.")
    return preset