# backend/app/utils/llm_registry_service.py
import asyncio
import logging
import time

logger = logging.getLogger(__name__) # Define logger at the top
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, AsyncGenerator

import httpx
from pydantic import BaseModel, Field, field_validator
import json # Added for parsing FALLBACK_MODELS_JSON

# --- Configuration ---
try:
    from ..app_config import ( # Changed to relative import
        LITELLM_PROXY_URL,
        LITELLM_PROXY_API_KEY,
        LLM_REFRESH_INTERVAL_SECONDS,
        LLM_CACHE_TTL_SECONDS,
        FALLBACK_MODELS_JSON
    )
except ImportError:
    logger.error("Failed to import configurations from backend.app.app_config. Using default/placeholder values.")
    # Define placeholders if import fails, to allow module to load for basic testing/linting
    LITELLM_PROXY_URL = "http://localhost:4000"
    LITELLM_PROXY_API_KEY = None
    LLM_REFRESH_INTERVAL_SECONDS = 3600
    LLM_CACHE_TTL_SECONDS = 3700
    FALLBACK_MODELS_JSON = '[]'

# --- Pydantic Models for Standardized LLM Representation ---
class ModelCapability(BaseModel):
    type: str  # e.g., "text_generation", "vision_input", "chat_completion", "embedding", "audio_transcription"
    details: Optional[Dict[str, Any]] = None  # e.g., max_output_tokens, supported_mime_types, embedding_dimensions, supports_diarization

class StandardizedLLM(BaseModel):
    provider: str
    model_id: str  # Provider's original model ID (from LiteLLM response 'id' or 'model_name')
    display_name: str
    crawl4ai_compatible_id: Optional[str] = None
    family: Optional[str] = None
    context_window: Optional[int] = None
    capabilities: List[ModelCapability] = Field(default_factory=list)
    status: Optional[str] = "active"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    additional_metadata: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, Any]] = None
    # For LiteLLM, the 'id' field in their /v1/models response is usually the full model name like "openai/gpt-3.5-turbo"
    # We will use this as our primary model_id and also populate crawl4ai_compatible_id if needed.

# --- LLM Registry Service Class ---
class LLMRegistryService:
    def __init__(self, litellm_proxy_url_override: Optional[str] = None):
        logger.info(f"Initializing LLMRegistryService instance. Override URL: {litellm_proxy_url_override}")
        
        # Determine the LiteLLM Proxy URL to use
        self.litellm_proxy_url = litellm_proxy_url_override if litellm_proxy_url_override else LITELLM_PROXY_URL
        if not self.litellm_proxy_url:
            logger.error("LiteLLM Proxy URL is not configured. LLMRegistryService may not function correctly.")
            # Optionally raise an error or handle this state appropriately
            # raise ValueError("LiteLLM Proxy URL must be provided either via override or app_config.")

        logger.info(f"LLMRegistryService will use LiteLLM Proxy URL: {self.litellm_proxy_url}")

        # Initialize cache variables within the instance
        self._cached_models: List[StandardizedLLM] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_lock = asyncio.Lock()
        self._fallback_models_loaded: List[StandardizedLLM] = []
        self._load_fallback_models() # Load fallbacks on instance creation
        logger.info("LLMRegistryService instance created.")

    def _load_fallback_models(self):
        """Loads fallback models from configuration."""
        try:
            models_data = json.loads(FALLBACK_MODELS_JSON)
            self._fallback_models_loaded = [StandardizedLLM(**model_data) for model_data in models_data]
            logger.info(f"Loaded {len(self._fallback_models_loaded)} fallback models into instance.")
        except Exception as e:
            logger.error(f"Error loading fallback models into instance: {e}", exc_info=True)
            self._fallback_models_loaded = []

    async def _fetch_models_from_litellm_proxy(self) -> List[StandardizedLLM]:
        """
        Fetches the list of available models from the LiteLLM proxy's /model/info endpoint
        and transforms them into the StandardizedLLM format.
        """
        endpoint_url = f"{self.litellm_proxy_url}/model/info" # Use instance's URL
        logger.info(f"Attempting to fetch models from LiteLLM proxy: {endpoint_url}")
        headers = {}
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        transformed_models: List[StandardizedLLM] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint_url, headers=headers)
                response.raise_for_status()

                litellm_response_data = response.json()
                # LiteLLM's /model/info endpoint returns a structure like:
                # {"data": [{"model_name": "azure-gpt-3.5", "litellm_params":{...}, "model_info":{...}}, ...]}

                if not isinstance(litellm_response_data, dict) or "data" not in litellm_response_data or not isinstance(litellm_response_data["data"], list):
                    logger.error(f"Unexpected response structure from LiteLLM proxy /model/info: {litellm_response_data}")
                    return transformed_models

                for model_entry in litellm_response_data["data"]:
                    if not isinstance(model_entry, dict):
                        logger.warning(f"Skipping non-dict model entry from LiteLLM /model/info: {model_entry}")
                        continue

                    # Primary model identifier from /model/info is 'model_name'
                    # This is the alias defined in config.yaml (e.g., "gpt-3.5-turbo-proxy")
                    # The actual provider model is in litellm_params.model (e.g., "openai/gpt-3.5-turbo")
                    model_alias = model_entry.get("model_name")
                    litellm_params = model_entry.get("litellm_params", {})
                    model_info = model_entry.get("model_info", {})

                    if not model_alias or not isinstance(model_alias, str):
                        logger.warning(f"Skipping model entry with missing or invalid 'model_name': {model_entry}")
                        continue

                    # The 'id' field in StandardizedLLM should be the unique identifier used by LiteLLM internally,
                    # often provider/model_name. This is usually found in litellm_params.model.
                    internal_model_id = litellm_params.get("model", model_alias)


                    provider_name = model_info.get("litellm_provider", "unknown")
                    # If litellm_provider is not in model_info, try to infer from internal_model_id
                    if provider_name == "unknown" and isinstance(internal_model_id, str) and '/' in internal_model_id:
                        provider_name = internal_model_id.split('/', 1)[0]


                    capabilities = []
                    mode_value = model_info.get("mode") # Get the mode value
                    mode = mode_value.lower() if isinstance(mode_value, str) else "" # Call .lower() only if it's a string

                    if mode == "chat":
                        capabilities.append(ModelCapability(type="chat_completion"))
                        capabilities.append(ModelCapability(type="text_generation"))
                        # Check for vision capabilities based on model_alias or internal_model_id keywords
                        if any(kw in model_alias.lower() for kw in ["vision", "image", "multimodal"]) or \
                           any(kw in internal_model_id.lower() for kw in ["vision", "image", "multimodal"]):
                            capabilities.append(ModelCapability(type="vision_input"))
                    elif mode == "embedding":
                        capabilities.append(ModelCapability(type="embedding"))
                    elif mode == "completion": # For text-completion only models
                        capabilities.append(ModelCapability(type="text_generation"))
                    # Add more specific capability inference based on model_alias or internal_model_id if mode is generic
                    elif "whisper" in model_alias.lower() or "transcribe" in model_alias.lower() or "audio" in model_alias.lower():
                         capabilities.append(ModelCapability(type="audio_transcription"))
                         if "diarize" in model_alias.lower() or "speaker" in model_alias.lower():
                             capabilities.append(ModelCapability(type="audio_diarization", details={"info": "Inferred from model name"}))
                    elif "tts" in model_alias.lower() or "speech" in model_alias.lower():
                        capabilities.append(ModelCapability(type="text_to_speech"))
                    elif "image-generation" in model_alias.lower() or "dall-e" in model_alias.lower() or "stable-diffusion" in model_alias.lower():
                        capabilities.append(ModelCapability(type="image_generation"))

                    if not capabilities: # Fallback if mode is not helpful
                        if "embedding" in model_alias.lower(): capabilities.append(ModelCapability(type="embedding"))
                        else: # Default to chat/text if nothing else matches
                            capabilities.append(ModelCapability(type="chat_completion"))
                            capabilities.append(ModelCapability(type="text_generation"))


                    context_window = model_info.get("max_input_tokens")
                    if context_window is None:
                        context_window = model_info.get("max_tokens") # Common fallback field name

                    if isinstance(context_window, str):
                        try:
                            context_window = int(context_window)
                        except ValueError:
                            logger.warning(f"Could not parse context_window '{context_window}' to int for model '{model_alias}'.")
                            context_window = None

                    family = model_info.get("model_family") # LiteLLM might provide this in model_info
                    if not family and isinstance(model_alias, str): # Basic inference if not provided
                        if "gpt-4" in model_alias: family = "GPT-4"
                        elif "gpt-3.5" in model_alias: family = "GPT-3.5"
                        elif "gemini" in model_alias: family = "Gemini"
                        elif "claude-3" in model_alias: family = "Claude 3"
                        elif "claude-2" in model_alias: family = "Claude 2"
                        elif "llama" in model_alias: family = "Llama"
                        elif "command-r" in model_alias: family = "Command R"

                    try:
                        std_model = StandardizedLLM(
                            provider=provider_name,
                            model_id=internal_model_id, # Use the internal ID (e.g. openai/gpt-3.5-turbo)
                            display_name=model_alias, # The user-facing name from config.yaml
                            crawl4ai_compatible_id=internal_model_id, # crawl4ai likely uses the internal ID
                            family=family,
                            context_window=context_window,
                            capabilities=capabilities,
                            status="active",
                            additional_metadata=model_entry # Store the whole original entry
                        )
                        transformed_models.append(std_model)
                    except Exception as e_transform:
                        logger.error(f"Error transforming LiteLLM model entry '{model_alias}': {e_transform}. Entry: {model_entry}", exc_info=True)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching models from LiteLLM proxy ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
        except httpx.RequestError as e:
            logger.error(f"Request error fetching models from LiteLLM proxy ({e.request.url}): {e}", exc_info=True)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error parsing response from LiteLLM proxy: {e.msg} at line {e.lineno} col {e.colno}. Response text: {e.doc}", exc_info=False)
        except Exception as e:
            logger.error(f"Unexpected error fetching models from LiteLLM proxy: {e}", exc_info=True)

        logger.info(f"Fetched and transformed {len(transformed_models)} models from LiteLLM proxy using /model/info.")
        return transformed_models


    async def refresh_available_models(self, force_refresh: bool = False):
        """
        Fetches models from the LiteLLM proxy and updates the cache.
        Uses a lock to prevent concurrent refreshes.
        """
        async with self._cache_lock:
            now = datetime.now(timezone.utc)
            if not force_refresh and self._cache_timestamp and (now - self._cache_timestamp).total_seconds() < LLM_REFRESH_INTERVAL_SECONDS:
                logger.info(f"Model cache is still fresh. Last updated: {self._cache_timestamp}. Skipping refresh.")
                return

            logger.info("Refreshing LLM model cache...")
            try:
                fetched_models = await self._fetch_models_from_litellm_proxy()
                if fetched_models:
                    self._cached_models = fetched_models
                    self._cache_timestamp = now
                    logger.info(f"LLM model cache updated with {len(self._cached_models)} models at {now.isoformat()}.")
                elif not self._cached_models and self._fallback_models_loaded: # First fetch failed, but we have fallbacks
                    self._cached_models = self._fallback_models_loaded
                    self._cache_timestamp = now # Mark as "updated" with fallbacks
                    logger.warning(f"Failed to fetch models from proxy, but using {len(self._fallback_models_loaded)} fallback models.")
                elif not self._cached_models: # First fetch failed, no fallbacks
                     logger.error("Failed to fetch models from proxy and no fallback models available. Cache remains empty.")
                else: # Subsequent fetch failed, keep stale cache
                     logger.warning("Failed to fetch models from proxy. Retaining stale cache.")

            except Exception as e:
                logger.error(f"Error during model refresh: {e}", exc_info=True)
                if not self._cached_models and self._fallback_models_loaded:
                    self._cached_models = self._fallback_models_loaded
                    self._cache_timestamp = now
                    logger.warning(f"Using {len(self._fallback_models_loaded)} fallback models due to refresh error.")
                elif not self._cached_models:
                     logger.error("Cache remains empty after refresh error and no fallbacks.")


    def get_available_models(
        self,
        provider_filter: Optional[str] = None,
        capability_filter: Optional[str] = None # e.g., "text_generation", "embedding"
    ) -> List[StandardizedLLM]:
        """
        Returns a list of available standardized LLM models from the cache.
        Optionally filters by provider or capability type.
        """
        if not self._cached_models:
            logger.warning("Model cache is empty. Consider running refresh_available_models() or checking logs.")
            # Potentially trigger a synchronous refresh here if absolutely needed, but be careful with blocking.
            # For now, just return empty or fallbacks if any.
            return list(self._fallback_models_loaded) # Return a copy

        models_to_return = list(self._cached_models) # Return a copy

        if provider_filter:
            models_to_return = [m for m in models_to_return if m.provider.lower() == provider_filter.lower()]

        if capability_filter:
            models_to_return = [
                m for m in models_to_return
                if any(cap.type.lower() == capability_filter.lower() for cap in m.capabilities)
            ]

        logger.debug(f"Returning {len(models_to_return)} models after filters (provider: {provider_filter}, capability: {capability_filter}).")
        return models_to_return

    def get_model_details(self, model_id: str) -> Optional[StandardizedLLM]:
        """
        Returns details for a specific model (by its full ID like 'openai/gpt-4o') from the cache.
        """
        if not model_id:
            return None

        for model in self._cached_models:
            if model.model_id == model_id:
                return model

        # If not found in primary cache, check fallbacks (though primary cache should contain them if loaded)
        for model in self._fallback_models_loaded:
            if model.model_id == model_id:
                logger.warning(f"Model '{model_id}' found in fallback list but not in main cache.")
                return model

        logger.warning(f"Model with ID '{model_id}' not found in cache.")
        return None

    def get_cache_status(self) -> Dict[str, Any]:
        """Returns information about the current cache state."""
        return {
            "last_updated": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "number_of_models": len(self._cached_models),
            "using_fallbacks_only": self._cached_models == self._fallback_models_loaded and bool(self._fallback_models_loaded) and self._cache_timestamp is not None,
            "refresh_interval_seconds": LLM_REFRESH_INTERVAL_SECONDS,
            "cache_ttl_seconds": LLM_CACHE_TTL_SECONDS
        }

    async def transcribe_audio(self, model_id: str, audio_data: bytes, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Sends audio data to the LiteLLM proxy for transcription.

        Args:
            model_id: The ID of the transcription model to use (as configured in LiteLLM).
            audio_data: The audio content as bytes.
            **kwargs: Additional parameters to pass to the LiteLLM transcription endpoint.

        Returns:
            A dictionary containing the transcription results (full text and segments)
            or None if the transcription fails.
        """
        endpoint_url = f"{self.litellm_proxy_url}/v1/audio/transcriptions" # Use instance's URL
        logger.info(f"Attempting transcription via LiteLLM proxy: {endpoint_url} with model '{model_id}'")

        headers = {}
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        # LiteLLM expects the audio file as a multipart/form-data file upload
        # and the model ID as a form field.
        files = {'file': ('audio.mp3', audio_data, 'audio/mpeg')} # Assuming mp3 format is acceptable or handled by proxy
        data = {'model': model_id}

        # Include any additional kwargs as form data
        for key, value in kwargs.items():
            data[key] = value

        try:
            async with httpx.AsyncClient(timeout=600.0) as client: # Increased timeout for transcription
                response = await client.post(endpoint_url, headers=headers, files=files, data=data)
                response.raise_for_status() # Raise an exception for bad status codes

                transcription_result = response.json()
                logger.info(f"Transcription successful for model '{model_id}'.")

                # LiteLLM's /v1/audio/transcriptions endpoint (OpenAI compatible)
                # returns a structure like: {"text": "...", "segments": [...]}
                # We need to return this structure or adapt it if necessary for transcribe1.py

                # Ensure the response has the expected keys
                if "text" in transcription_result and "segments" in transcription_result:
                     return transcription_result
                else:
                     logger.error(f"Unexpected response structure from LiteLLM transcription endpoint: {transcription_result}")
                     return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during transcription via LiteLLM proxy ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error during transcription via LiteLLM proxy ({e.request.url}): {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during transcription via LiteLLM proxy: {e}", exc_info=True)
            return None

    async def get_chat_completion(self, model_id: str, messages: list, **kwargs) -> Optional[str]:
        """
        Gets a chat completion from the LiteLLM proxy.

        Args:
            model_id: The ID of the chat model to use (as configured in LiteLLM).
            messages: A list of message objects (e.g., [{"role": "user", "content": "Hello"}]).
            **kwargs: Additional parameters for the chat completion request (e.g., temperature, max_tokens).

        Returns:
            The content of the first choice's message as a string, or None if an error occurs.
        """
        endpoint_url = f"{self.litellm_proxy_url}/v1/chat/completions" # Use instance's URL
        logger.info(f"Attempting chat completion via LiteLLM proxy: {endpoint_url} with model '{model_id}'")

        headers = {"Content-Type": "application/json"}
        if LITELLM_PROXY_API_KEY: # Use the global API key from app_config for now
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        payload = {
            "model": model_id,
            "messages": messages,
            **kwargs
        }
        
        # Default stream to False if not provided, as this method expects a single response
        if "stream" not in payload:
            payload["stream"] = False

        try:
            async with httpx.AsyncClient(timeout=kwargs.get("request_timeout", 120.0)) as client: # Allow timeout override
                response = await client.post(endpoint_url, headers=headers, json=payload)
                response.raise_for_status()
                
                completion_data = response.json()
                
                if completion_data.get("choices") and isinstance(completion_data["choices"], list) and len(completion_data["choices"]) > 0:
                    first_choice = completion_data["choices"][0]
                    if first_choice.get("message") and isinstance(first_choice["message"], dict):
                        content = first_choice["message"].get("content")
                        if content:
                            logger.info(f"Chat completion successful for model '{model_id}'.")
                            return str(content)
                        else:
                            logger.warning(f"Chat completion response for model '{model_id}' had no content in the first choice's message.")
                    else:
                        logger.warning(f"Chat completion response for model '{model_id}' had no 'message' object in the first choice.")
                else:
                    logger.warning(f"Chat completion response for model '{model_id}' had no 'choices' or choices were empty.")
                
                return None # Fallthrough if expected data not found

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during chat completion ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
        except httpx.RequestError as e:
            logger.error(f"Request error during chat completion ({e.request.url}): {e}", exc_info=True)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error parsing chat completion response: {e.msg}. Response text: {e.doc}", exc_info=False)
        except Exception as e:
            logger.error(f"Unexpected error during chat completion: {e}", exc_info=True)
        
        return None


# --- Singleton Instance and Getter Function ---
_llm_registry_instance: Optional[LLMRegistryService] = None
_instance_lock = asyncio.Lock()

async def initialize_llm_registry(litellm_proxy_url_override: Optional[str] = None):
    """
    Initializes the singleton LLMRegistryService instance.
    Accepts an optional URL override for the LiteLLM proxy.
    """
    global _llm_registry_instance
    async with _instance_lock:
        if _llm_registry_instance is None:
            logger.info(f"Creating and initializing LLMRegistryService instance. Override URL: {litellm_proxy_url_override}")
            _llm_registry_instance = LLMRegistryService(litellm_proxy_url_override=litellm_proxy_url_override)
            await _llm_registry_instance.refresh_available_models(force_refresh=True)
            logger.info("LLMRegistryService instance initialized.")
        else:
            logger.info(f"LLMRegistryService instance already initialized. Override URL '{litellm_proxy_url_override}' ignored if provided now.")

def get_llm_registry_service() -> LLMRegistryService:
    """Returns the singleton LLMRegistryService instance."""
    if _llm_registry_instance is None:
        logger.error("LLMRegistryService accessed before initialization!")
        raise RuntimeError("LLMRegistryService has not been initialized. Call initialize_llm_registry() first.")
    return _llm_registry_instance

# --- Periodic Refresh Task ---
async def _periodic_refresh_task(): # No change needed here, it uses the singleton
    """Periodic refresh logic that would be run as a background task."""
    # This task needs to get the instance using get_llm_registry_service()
    # It should only start after the instance is initialized.
    # The scheduling of this task should happen in main.py after initialize_llm_registry completes.
    logger.info("Starting periodic LLM model cache refresh task...")
    # Wait for initial initialization to complete (optional, but safer)
    
    # This loop might be problematic if initialization fails repeatedly.
    # Consider a timeout or a different mechanism for task startup.
    instance_ready = False
    while not instance_ready:
        try:
            registry_service = get_llm_registry_service() # Get the singleton instance
            instance_ready = True
        except RuntimeError: # If get_llm_registry_service raises error because it's not initialized
            logger.info("Periodic refresh task waiting for LLMRegistryService initialization...")
            await asyncio.sleep(5) # Wait and retry

    while True:
        await asyncio.sleep(LLM_REFRESH_INTERVAL_SECONDS)
        logger.info("Triggering periodic LLM model cache refresh...")
        try:
            await registry_service.refresh_available_models() # Call method on the instance
        except Exception as e_refresh:
            logger.error(f"Error during periodic model refresh: {e_refresh}", exc_info=True)


# --- Example Usage (if running this script directly) ---
if __name__ == "__main__":
    # Example usage (for testing this module directly)
    logging.basicConfig(level=logging.INFO)

    async def main_test():
        # Test with an override URL
        test_proxy_url = "http://localhost:4000" # Replace with your actual test proxy if different
        print(f"Initializing LLM Registry with override URL: {test_proxy_url}...")
        await initialize_llm_registry(litellm_proxy_url_override=test_proxy_url) 

        registry = get_llm_registry_service()

        print("\nCache Status:")
        print(json.dumps(registry.get_cache_status(), indent=2))

        chat_models = registry.get_available_models(capability_filter="chat_completion")
        if chat_models:
            print(f"\nAvailable Chat Models (Total: {len(chat_models)}):")
            for model in chat_models[:5]: # Print first 5
                print(f"  - {model.display_name} ({model.model_id}), Provider: {model.provider}")

            # Test chat completion with the first available chat model
            test_chat_model_id = chat_models[0].model_id 
            print(f"\nTesting chat completion with model: {test_chat_model_id}")
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What is the capital of France?"}
            ]
            # Example of additional kwargs:
            # chat_kwargs = {"temperature": 0.7, "max_tokens": 50}
            # completion_response = await registry.get_chat_completion(test_chat_model_id, test_messages, **chat_kwargs)
            completion_response = await registry.get_chat_completion(test_chat_model_id, test_messages)

            if completion_response:
                print(f"  LLM Response: {completion_response}")
            else:
                print("  Failed to get chat completion.")
        else:
            print("\nNo chat models available to test completion.")
        
        # Example of other model types (if available and configured in your LiteLLM proxy)
        # embedding_models = registry.get_available_models(capability_filter="embedding")
        # if embedding_models:
        #     print(f"\nAvailable Embedding Models (First 5 of {len(embedding_models)}):")
        #     for model in embedding_models[:5]: print(f"  - {model.display_name} ({model.model_id})")

        # transcription_models = registry.get_available_models(capability_filter="audio_transcription")
        # if transcription_models:
        #     print(f"\nAvailable Transcription Models (First 5 of {len(transcription_models)}):")
        #     for model in transcription_models[:5]: print(f"  - {model.display_name} ({model.model_id})")

        # The periodic refresh task is more for a long-running service.
        # For this direct test, we've already refreshed once during initialization.


    # Run the async test function
    asyncio.run(main_test())
