# Search Parameters Integration

This document explains the integration between the frontend and backend for search parameter configuration.

## Overview

The system now supports a full round-trip configuration of search parameters between the frontend and backend:

1. Frontend sliders control search parameters for three tiers:
   - Fine-grained (high precision)
   - Contextual (balanced)
   - Overview (broad insights)

2. Each tier has four configurable parameters:
   - `similarity_threshold`: How similar results must be to be included (0.0-1.0)
   - `content_weight`: Balance between exact and semantic matching (0.0-1.0)
   - `result_percentage`: Portion of results to allocate to this tier (0.0-1.0)
   - `max_results`: Maximum number of results to return for this tier (1-50)

3. Parameters are passed to the backend via API calls

## Configuration Files

Search parameters are now centralized in a configuration file:

- `backend/app/config/search_config.py`: Contains defaults and presets for search parameters

## API Endpoints

The following API endpoints are available:

- `GET /api/search-config`: Retrieve current search parameters
- `POST /api/search-config`: Update search parameters
- `GET /api/search-config/presets`: List available presets
- `GET /api/search-config/preset/{preset_name}`: Get a specific preset
- `POST /api/search-config/preset`: Load a preset configuration

## Presets

Four preset configurations are available:

1. **Default**: Balanced for general search
2. **Technical**: High precision, content focused
3. **Conceptual**: Broader, semantic matching
4. **Balanced**: Equal weight to all aspects

## Enhanced Streaming Endpoint

The `/vector-search-stream` endpoint now accepts:

- All search parameters for each tier
- `preset` parameter to load a specific configuration
- Enhanced logging of parameter changes and result counts

## Logging

Enhanced logging shows:
- Which parameters are changed and by how much
- The current values used for search
- The number of results requested and returned

## Testing

Tests are available:

- Backend: `backend/app/tests/test_search_config.py`
- Frontend: `src/app/tests/vector-search.test.js`

## Example Usage

```javascript
// Frontend: Setting parameters
setSearchParams({
  fine_grained: {
    similarity_threshold: 0.75,
    content_weight: 0.8,
    result_percentage: 0.4,
    max_results: 15
  },
  // ... other tiers
});

// Frontend: Loading a preset
const url = new URL('http://localhost:8000/vector-search-stream');
url.searchParams.append('preset', 'technical');
```

```python
# Backend: Updating parameters
search_params.update_from_frontend(
    fine_grained_similarity_threshold=0.8,
    fine_grained_max_results=20,
    # ... other parameters
)

# Backend: Loading a preset
search_params.load_preset("technical")
```

## Validation

All parameters are validated against defined limits to ensure they fall within acceptable ranges. 