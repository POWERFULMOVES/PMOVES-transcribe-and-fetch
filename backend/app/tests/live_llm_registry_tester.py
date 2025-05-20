# backend/app/tests/live_llm_registry_tester.py

import asyncio
import pytest
import os
import sys
import logging

# Add the backend/app directory to the sys.path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the LLM registry service and app config (for proxy URL/key)
try:
    from utils.llm_registry_service import (
        initialize_llm_registry,
        get_available_models,
        get_cache_status,
        StandardizedLLM
    )
    from app_config import LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY
    LLM_REGISTRY_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import LLM registry service or app config: {e}")
    LLM_REGISTRY_AVAILABLE = False
    # Define dummy functions/variables to allow tests to be defined, but they will fail
    def initialize_llm_registry(): raise RuntimeError("LLM registry not available")
    def get_available_models(*args, **kwargs): return []
    def get_cache_status(): return {"status": "unavailable"}
    class StandardizedLLM: pass
    LITELLM_PROXY_URL = "http://localhost:4000"
    LITELLM_PROXY_API_KEY = None


# --- Test Setup ---
@pytest.fixture(scope="module", autouse=True)
async def setup_llm_registry():
    """Initializes the LLM registry before tests run."""
    if not LLM_REGISTRY_AVAILABLE:
        pytest.skip("LLM registry service not available due to import errors.")

    logger.info("Setting up LLM registry for tests...")
    # Ensure the LiteLLM proxy is running and accessible at LITELLM_PROXY_URL
    # This test assumes the proxy is already running externally.

    # Initialize the registry - this fetches models from the proxy
    await initialize_llm_registry()
    logger.info("LLM registry setup complete.")

    # Yield control to tests
    yield

    # No specific cleanup needed for the registry in this test


# --- Test Cases ---

@pytest.mark.asyncio
async def test_registry_initialization_and_fetch():
    """Tests that the registry initializes and fetches models."""
    if not LLM_REGISTRY_AVAILABLE: pytest.skip("LLM registry service not available.")

    cache_status = get_cache_status()
    logger.info(f"Cache Status after initialization: {cache_status}")

    assert cache_status.get("number_of_models", 0) > 0, "LLM registry should have fetched models."
    assert cache_status.get("last_updated") is not None, "Cache timestamp should be set."
    assert not cache_status.get("using_fallbacks_only", False), "Registry should not be using fallbacks if proxy is running."

@pytest.mark.asyncio
async def test_get_available_models_all():
    """Tests retrieving all available models."""
    if not LLM_REGISTRY_AVAILABLE: pytest.skip("LLM registry service not available.")

    models = get_available_models()
    logger.info(f"Retrieved {len(models)} models using get_available_models().")

    assert isinstance(models, list), "get_available_models should return a list."
    assert len(models) > 0, "Should retrieve at least one model if proxy is configured."
    assert all(isinstance(m, StandardizedLLM) for m in models), "All items should be StandardizedLLM instances."

@pytest.mark.asyncio
async def test_get_available_models_filter_provider():
    """Tests filtering models by provider."""
    if not LLM_REGISTRY_AVAILABLE: pytest.skip("LLM registry service not available.")

    # This test requires a specific provider to be configured in the LiteLLM proxy config.yaml
    # Replace 'openai' with a provider you expect to be configured, e.g., 'groq', 'ollama', 'azure'
    # You might need to make this dynamic based on config or environment variables if possible.
    # For now, using 'openai' as a placeholder.
    expected_provider = "openai"

    # Check if any models for this provider are expected based on config or env
    # This is a simple check; a more robust test might read config.yaml
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_API_KEY"):
         logger.warning(f"Skipping provider filter test for '{expected_provider}' as no relevant API key is set.")
         pytest.skip(f"No API key set for expected provider '{expected_provider}'.")

    openai_models = get_available_models(provider_filter=expected_provider)
    logger.info(f"Retrieved {len(openai_models)} models filtered by provider '{expected_provider}'.")

    # Assert that models for the expected provider are found
    # This assertion might need adjustment based on your specific proxy configuration
    assert len(openai_models) > 0, f"Should find models for provider '{expected_provider}' if configured."
    assert all(m.provider.lower() == expected_provider.lower() for m in openai_models), f"All filtered models should be from provider '{expected_provider}'."

@pytest.mark.asyncio
async def test_get_available_models_filter_capability():
    """Tests filtering models by capability."""
    if not LLM_REGISTRY_AVAILABLE: pytest.skip("LLM registry service not available.")

    # This test requires models with specific capabilities to be configured.
    # Replace 'chat_completion' with a capability you expect, e.g., 'vision_input', 'embedding', 'audio_transcription'
    expected_capability = "chat_completion"

    chat_models = get_available_models(capability_filter=expected_capability)
    logger.info(f"Retrieved {len(chat_models)} models filtered by capability '{expected_capability}'.")

    # Assert that models with the expected capability are found
    # This assertion might need adjustment based on your specific proxy configuration
    assert len(chat_models) > 0, f"Should find models with capability '{expected_capability}' if configured."
    assert all(any(cap.type.lower() == expected_capability.lower() for cap in m.capabilities) for m in chat_models), f"All filtered models should have capability '{expected_capability}'."

@pytest.mark.asyncio
async def test_get_model_details():
    """Tests retrieving details for a specific model."""
    if not LLM_REGISTRY_AVAILABLE: pytest.skip("LLM registry service not available.")

    # This test requires a specific model ID to be configured in the LiteLLM proxy config.yaml
    # Replace 'openai/gpt-3.5-turbo-proxy' with an actual model_id (the internal one, e.g., 'openai/gpt-3.5-turbo')
    # that you expect to be available via the proxy.
    # You might need to make this dynamic based on config or environment variables if possible.
    # For now, using 'openai/gpt-3.5-turbo' as a placeholder internal ID.
    # The model_id in StandardizedLLM is the internal one (litellm_params.model), not the alias (model_name).
    expected_model_id = "openai/gpt-3.5-turbo"

    # Find a model in the cache that matches the expected internal ID
    all_models = get_available_models()
    target_model = next((m for m in all_models if m.model_id == expected_model_id), None)

    if target_model is None:
        logger.warning(f"Skipping get_model_details test for '{expected_model_id}' as it was not found in the cache.")
        pytest.skip(f"Model ID '{expected_model_id}' not found in the registry cache.")

    model_details = get_model_details(expected_model_id)
    logger.info(f"Retrieved details for model '{expected_model_id}'.")

    assert model_details is not None, f"Should retrieve details for model '{expected_model_id}'."
    assert isinstance(model_details, StandardizedLLM), "Retrieved details should be a StandardizedLLM instance."
    assert model_details.model_id == expected_model_id, "Retrieved model ID should match the requested ID."
    # Add more assertions to check specific fields if needed, e.g., model_details.provider, model_details.capabilities

# Note: Testing the specific task functions (generate_embedding, transcribe_audio, etc.)
# would require mocking the httpx calls or ensuring the LiteLLM proxy and providers
# are fully functional and configured for those specific models.
# These tests focus on the registry service's ability to fetch and manage model info.
# Integration tests (Task 5) will cover end-to-end calls through the registry.

# To run these tests:
# 1. Ensure LiteLLM proxy is running with configured providers.
# 2. Ensure the backend application's environment variables (like LITELLM_PROXY_URL, API keys) are set correctly.
# 3. Navigate to the backend/app directory in your terminal.
# 4. Run pytest: `pytest tests/live_llm_registry_tester.py`
#    You might need to install pytest and pytest-asyncio (`pip install pytest pytest-asyncio httpx`)
#    Ensure your PYTHONPATH includes the backend/app directory if running from elsewhere.
#    The sys.path.insert at the top of this file attempts to handle this if run from the tests directory.
