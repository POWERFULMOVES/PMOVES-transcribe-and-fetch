import asyncio
import os
import sys
import pytest
import httpx
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'app')))

from utils.llm_registry_service import initialize_llm_registry, get_available_models, get_cache_status
from app_config import app_config

# Load environment variables from backend/app/.env
# This is necessary for AppConfig to load correctly and for tests that might
# indirectly use env vars (though registry tests primarily check structure)
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', 'app', '.env'))

# Configure AppConfig to use the LiteLLM proxy URL
# Ensure LITELLM_PROXY_URL is set in your .env file
app_config.LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
app_config.LITELLM_PROXY_API_KEY = os.getenv("LITELLM_PROXY_API_KEY") # Optional if proxy is secured

# --- Test Setup ---

@pytest.fixture(scope="module", autouse=True)
async def setup_llm_registry():
    """Initializes the LLM registry before running tests."""
    print("\nSetting up LLM registry...")
    # Ensure the LiteLLM proxy is running and accessible before running tests
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AppConfig.LLM_PROXY_URL}/model/info", timeout=5)
            response.raise_for_status()
        print(f"LiteLLM proxy is accessible at {AppConfig.LITELLM_PROXY_URL}")
    except httpx.RequestError as e:
        pytest.fail(f"LiteLLM proxy not accessible at {AppConfig.LITELLM_PROXY_URL}. Please ensure it is running. Error: {e}")
    except httpx.HTTPStatusError as e:
         pytest.fail(f"LiteLLM proxy returned an error status {e.response.status_code} from {e.request.url}. Response: {e.response.text}")

    # Initialize the registry, which fetches models from the proxy
    await initialize_llm_registry()
    print("LLM registry initialized.")

    # Yield control to run tests
    yield

    # Optional: Cleanup after tests if needed (e.g., clear cache, though not strictly necessary for in-memory)
    print("\nCleaning up LLM registry setup.")


# --- Test Cases ---

@pytest.mark.asyncio
async def test_registry_fetches_models_from_proxy():
    """Tests that the registry successfully fetches models from the LiteLLM proxy."""
    print("\nRunning test_registry_fetches_models_from_proxy...")
    models = get_available_models()
    cache_status = get_cache_status()

    print(f"Fetched {len(models)} models from registry.")
    print(f"Cache status: {cache_status}")

    assert len(models) > 0, "LLM registry should contain models fetched from the proxy."
    assert cache_status.get("model_count", 0) > 0, "Cache status should report more than 0 models."
    assert cache_status.get("last_updated") is not None, "Cache status should have a last_updated timestamp."

@pytest.mark.asyncio
async def test_registry_includes_openai_models():
    """Tests that the registry includes models from the OpenAI provider."""
    print("\nRunning test_registry_includes_openai_models...")
    openai_models = get_available_models(provider_filter="openai")
    print(f"Found {len(openai_models)} OpenAI models.")
    assert any(m.provider == "openai" for m in openai_models), "Registry should include models with provider 'openai'."
    # You can add more specific checks here based on expected OpenAI models in your config.yaml
    # e.g., assert any(m.model_id == "openai/gpt-4o-mini-2025-04-14" for m in openai_models)

@pytest.mark.asyncio
async def test_registry_includes_groq_models():
    """Tests that the registry includes models from the Groq provider."""
    print("\nRunning test_registry_includes_groq_models...")
    groq_models = get_available_models(provider_filter="groq")
    print(f"Found {len(groq_models)} Groq models.")
    assert any(m.provider == "groq" for m in groq_models), "Registry should include models with provider 'groq'."
    # Check for specific Groq models configured in config.yaml
    assert any(m.model_id == "groq/llama3-70b-8192" for m in groq_models), "Registry should include groq/llama3-70b-8192."
    assert any(m.model_id == "groq/llama3-8b-8192" for m in groq_models), "Registry should include groq/llama3-8b-8192."


@pytest.mark.asyncio
async def test_registry_includes_google_models():
    """Tests that the registry includes models from the Google provider."""
    print("\nRunning test_registry_includes_google_models...")
    google_models = get_available_models(provider_filter="google")
    print(f"Found {len(google_models)} Google models.")
    assert any(m.provider == "google" for m in google_models), "Registry should include models with provider 'google'."
    # Check for specific Google models configured in config.yaml
    assert any(m.model_id == "gemini/gemini-1.5-pro-latest" for m in google_models), "Registry should include gemini/gemini-1.5-pro-latest."
    assert any(m.model_id == "gemini/gemini-2.5-flash-preview-04-17" for m in google_models), "Registry should include gemini/gemini-2.5-flash-preview-04-17."


@pytest.mark.asyncio
async def test_registry_includes_ollama_models():
    """Tests that the registry includes models from the Ollama provider."""
    print("\nRunning test_registry_includes_ollama_models...")
    ollama_models = get_available_models(provider_filter="ollama")
    print(f"Found {len(ollama_models)} Ollama models.")
    assert any(m.provider == "ollama" for m in ollama_models), "Registry should include models with provider 'ollama'."
    # Check for specific Ollama models configured in config.yaml
    # Note: The exact model ID might depend on how Ollama reports it and LiteLLM processes it.
    # You might need to adjust this based on actual /model/info response.
    assert any("ollama" in m.model_id.lower() for m in ollama_models), "Registry should include at least one model with 'ollama' in its ID."


@pytest.mark.asyncio
async def test_registry_includes_lmstudio_models():
    """Tests that the registry includes models from the LM Studio provider."""
    print("\nRunning test_registry_includes_lmstudio_models...")
    lmstudio_models = get_available_models(provider_filter="lm_studio") # LiteLLM uses 'lm_studio' as provider name
    print(f"Found {len(lmstudio_models)} LM Studio models.")
    assert any(m.provider == "lm_studio" for m in lmstudio_models), "Registry should include models with provider 'lm_studio'."
    # Check for specific LM Studio models configured in config.yaml
    # Note: The exact model ID might depend on how LM Studio reports it and LiteLLM processes it.
    # You might need to adjust this based on actual /model/info response.
    assert any("lm_studio" in m.model_id.lower() for m in lmstudio_models), "Registry should include at least one model with 'lm_studio' in its ID."


@pytest.mark.asyncio
async def test_model_details_retrieval():
    """Tests retrieving details for a specific model."""
    print("\nRunning test_model_details_retrieval...")
    # Assuming 'openai' and 'gpt-4.1-mini-2025-04-14' are configured and available
    model_id_to_check = "openai/gpt-4.1-mini-2025-04-14"
    provider_to_check = "openai"
    model_details = get_model_details(provider_to_check, model_id_to_check)

    print(f"Retrieved details for {model_id_to_check}: {model_details}")

    assert model_details is not None, f"Should retrieve details for {model_id_to_check}."
    assert model_details.model_id == model_id_to_check
    assert model_details.provider == provider_to_check
    assert model_details.context_window is not None, "Model details should include context_window."
    assert len(model_details.capabilities) > 0, "Model details should list capabilities."

@pytest.mark.asyncio
async def test_model_details_not_found():
    """Tests retrieving details for a non-existent model."""
    print("\nRunning test_model_details_not_found...")
    model_details = get_model_details("non_existent_provider", "non_existent_model")
    assert model_details is None, "Should not retrieve details for a non-existent model."

# To run these tests:
# 1. Ensure your LiteLLM proxy is running with the desired providers configured in config.yaml
# 2. Ensure your backend/app/.env file has the necessary API keys and LITELLM_PROXY_URL
# 3. Navigate to the project root directory in your terminal
# 4. Activate your Python virtual environment
# 5. Run pytest: pytest live_llm_registry_tester.py
