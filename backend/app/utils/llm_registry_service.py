# backend/app/utils/llm_registry_service.py
import asyncio
import logging
import time

logger = logging.getLogger(__name__) # Define logger at the top
from datetime import datetime, timezone, timedelta 
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union # Consolidated and sorted

import httpx
from pydantic import BaseModel, Field, field_validator, ValidationError
import json # Added for parsing FALLBACK_MODELS_JSON

# Attempt to import get_client for Supabase interactions
try:
    from ..db.database import get_client
except ImportError:
    logger.warning("Supabase client 'get_client' not found at ..db.database. Supabase functionalities will be disabled.")
    get_client = None # Allow module to load, but disable Supabase features

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
    status: Optional[str] = "active", # Corresponds to llm_models.status
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)), # Used for cache logic, not directly in llm_models table (which has created_at, updated_at, last_synced_at)
    additional_metadata: Optional[Dict[str, Any]] = None, # Potentially for future use, not directly in llm_models
    pricing: Optional[Dict[str, Any]] = None, # Corresponds to llm_models.pricing (JSONB)
    rate_limits: Optional[Dict[str, Any]] = None # Corresponds to llm_models.rate_limits (JSONB)
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
                
                # After updating self._cached_models, sync to Supabase
                await self._sync_models_to_supabase(self._cached_models)

            except Exception as e:
                logger.error(f"Error during model refresh: {e}", exc_info=True)
                if not self._cached_models and self._fallback_models_loaded:
                    self._cached_models = self._fallback_models_loaded
                    self._cache_timestamp = now
                    logger.warning(f"Using {len(self._fallback_models_loaded)} fallback models due to refresh error.")
                    # Also sync fallbacks if they are now the source of truth for the cache
                    await self._sync_models_to_supabase(self._cached_models)
                elif not self._cached_models:
                     logger.error("Cache remains empty after refresh error and no fallbacks.")

    async def _sync_models_to_supabase(self, models: List[StandardizedLLM]):
        """
        Synchronizes a list of StandardizedLLM models to the Supabase 'llm_models' table.
        """
        if not get_client:
            logger.warning("Supabase client not available. Skipping sync of models to Supabase.")
            return

        supabase_client = get_client()
        if not supabase_client:
            logger.error("Failed to get Supabase client instance. Skipping sync.")
            return

        logger.info(f"Starting sync of {len(models)} models to Supabase 'llm_models' table.")
        upsert_count = 0
        error_count = 0

        for model in models:
            try:
                model_dict = {
                    "model_id": model.model_id,
                    "display_name": model.display_name,
                    "provider": model.provider,
                    "family": model.family,
                    "context_window": model.context_window,
                    "capabilities": [cap.model_dump() for cap in model.capabilities] if model.capabilities else [],
                    "status": model.status or 'active', # Ensure status has a default
                    "pricing": model.pricing,
                    "rate_limits": model.rate_limits,
                    "last_synced_at": datetime.now(timezone.utc).isoformat(),
                }
                # Remove keys with None values, as Supabase might not like them for JSONB or other fields unless nullable
                model_dict = {k: v for k, v in model_dict.items() if v is not None}

                # Correctly wrap the synchronous Supabase call
                response = await asyncio.to_thread(
                    supabase_client.table("llm_models").upsert(
                        model_dict,
                        on_conflict="model_id"
                    ).execute
                )

                if response.data:
                    logger.debug(f"Successfully upserted model '{model.model_id}' to Supabase.")
                    upsert_count +=1
                else: # response.error or no data
                    error_detail = response.error.message if response.error else "No data returned"
                    logger.error(f"Failed to upsert model '{model.model_id}' to Supabase. Error: {error_detail}. Data: {model_dict}")
                    error_count += 1
            except Exception as e:
                logger.error(f"Exception during Supabase upsert for model '{model.model_id}': {e}", exc_info=True)
                error_count += 1
        
        logger.info(f"Supabase sync completed. Successfully upserted: {upsert_count}, Errors: {error_count}")


    async def get_available_models(
        self,
        provider_filter: Optional[str] = None,
        capability_filter: Optional[str] = None # e.g., "text_generation", "embedding"
    ) -> List[StandardizedLLM]:
        """
        Returns a list of available standardized LLM models.
        Attempts to fetch from Supabase first, then falls back to in-memory cache.
        Optionally filters by provider or capability type.
        """
        if get_client:
            supabase_client = get_client()
            if supabase_client:
                logger.debug("Attempting to fetch models from Supabase.")
                try:
                    query = supabase_client.table("llm_models").select("*").eq("status", "active") # Only fetch active models
                    if provider_filter:
                        query = query.eq("provider", provider_filter)
                    
                    # Correctly wrap the synchronous Supabase call
                    response = await asyncio.to_thread(query.execute)

                    if response.data:
                        db_models: List[StandardizedLLM] = []
                        for row in response.data:
                            try:
                                # Convert capabilities from list of dicts to List[ModelCapability]
                                capabilities_data = row.get("capabilities", [])
                                parsed_capabilities = [ModelCapability(**cap_data) for cap_data in capabilities_data]
                                
                                # Prepare data for StandardizedLLM, handling potential missing fields
                                model_data_for_pydantic = {
                                    "provider": row.get("provider"),
                                    "model_id": row.get("model_id"),
                                    "display_name": row.get("display_name"),
                                    "crawl4ai_compatible_id": row.get("model_id"), # Assuming model_id is compatible
                                    "family": row.get("family"),
                                    "context_window": row.get("context_window"),
                                    "capabilities": parsed_capabilities,
                                    "status": row.get("status", "active"),
                                    # last_updated is for cache staleness, not directly from this table field
                                    # additional_metadata is not stored in llm_models directly
                                    "pricing": row.get("pricing"),
                                    "rate_limits": row.get("rate_limits")
                                }
                                # Filter out None values before passing to Pydantic model if they are not Optional in model
                                model_data_for_pydantic_cleaned = {k:v for k,v in model_data_for_pydantic.items() if v is not None or k in StandardizedLLM.model_fields}


                                db_models.append(StandardizedLLM(**model_data_for_pydantic_cleaned))
                            except ValidationError as ve:
                                logger.error(f"Validation error converting Supabase row to StandardizedLLM for model_id '{row.get('model_id')}': {ve}", exc_info=True)
                            except Exception as e_row_parse:
                                logger.error(f"Error parsing row from Supabase for model_id '{row.get('model_id')}': {e_row_parse}", exc_info=True)
                        
                        if db_models:
                            logger.info(f"Successfully fetched {len(db_models)} models from Supabase.")
                            # Apply capability filter if present (provider filter was done in query)
                            if capability_filter:
                                db_models = [
                                    m for m in db_models
                                    if any(cap.type.lower() == capability_filter.lower() for cap in m.capabilities)
                                ]
                            # Update cache with Supabase data if it's more recent or cache is empty
                            # For simplicity, we'll just use this as the source of truth if available
                            # A more sophisticated cache update logic could be added here.
                            # self._cached_models = db_models # Optionally update cache
                            # self._cache_timestamp = datetime.now(timezone.utc)
                            return db_models
                except Exception as e_supabase:
                    logger.error(f"Error fetching models from Supabase: {e_supabase}", exc_info=True)
                    # Fall through to cache logic
            else:
                logger.debug("Supabase client not initialized. Falling back to cache.")
        else:
            logger.debug("Supabase client not configured. Falling back to cache.")

        # Fallback to in-memory cache if Supabase fetch fails or is not available
        logger.info("Falling back to in-memory cache for get_available_models.")
        if not self._cached_models:
            logger.warning("Model cache is empty. Consider running refresh_available_models() or checking logs.")
            return list(self._fallback_models_loaded) 

        models_to_return = list(self._cached_models) 

        if provider_filter: # Provider filter already applied if from Supabase
            models_to_return = [m for m in models_to_return if m.provider.lower() == provider_filter.lower()]

        if capability_filter:
            models_to_return = [
                m for m in models_to_return
                if any(cap.type.lower() == capability_filter.lower() for cap in m.capabilities)
            ]

        logger.debug(f"Returning {len(models_to_return)} models from cache after filters (provider: {provider_filter}, capability: {capability_filter}).")
        return models_to_return

    async def get_model_details(self, model_id: str) -> Optional[StandardizedLLM]:
        """
        Returns details for a specific model (by its full ID like 'openai/gpt-4o').
        Attempts to fetch from Supabase first, then falls back to in-memory cache.
        """
        if not model_id:
            return None

        if not model_id:
            return None

        # Try Supabase first
        if get_client:
            supabase_client = get_client()
            if supabase_client:
                logger.debug(f"Attempting to fetch model details for '{model_id}' from Supabase.")
                try:
                    # Correctly wrap the synchronous Supabase call
                    response = await asyncio.to_thread(
                        supabase_client.table("llm_models")
                        .select("*")
                        .eq("model_id", model_id)
                        .eq("status", "active")
                        .maybe_single() # Use maybe_single() if expecting one or zero results
                        .execute
                    )
                    if response.data:
                        row = response.data
                        capabilities_data = row.get("capabilities", [])
                        parsed_capabilities = [ModelCapability(**cap_data) for cap_data in capabilities_data]
                        
                        model_data_for_pydantic = {
                            "provider": row.get("provider"),
                            "model_id": row.get("model_id"),
                            "display_name": row.get("display_name"),
                            "crawl4ai_compatible_id": row.get("model_id"),
                            "family": row.get("family"),
                            "context_window": row.get("context_window"),
                            "capabilities": parsed_capabilities,
                            "status": row.get("status", "active"),
                            "pricing": row.get("pricing"),
                            "rate_limits": row.get("rate_limits")
                        }
                        model_data_for_pydantic_cleaned = {k:v for k,v in model_data_for_pydantic.items() if v is not None or k in StandardizedLLM.model_fields}
                        
                        logger.info(f"Successfully fetched model details for '{model_id}' from Supabase.")
                        return StandardizedLLM(**model_data_for_pydantic_cleaned)
                except ValidationError as ve:
                    logger.error(f"Validation error converting Supabase row to StandardizedLLM for model_id '{model_id}': {ve}", exc_info=True)
                except Exception as e_supabase_detail:
                    logger.error(f"Error fetching model details for '{model_id}' from Supabase: {e_supabase_detail}", exc_info=True)
            else:
                 logger.debug(f"Supabase client not initialized. Falling back to cache for model '{model_id}'.")
        else:
            logger.debug(f"Supabase client not configured. Falling back to cache for model '{model_id}'.")
        
        # Fallback to cache
        logger.info(f"Falling back to in-memory cache for model details of '{model_id}'.")
        for model in self._cached_models:
            if model.model_id == model_id:
                return model
        
        for model in self._fallback_models_loaded: # Check fallbacks if not in primary cache
            if model.model_id == model_id:
                logger.warning(f"Model '{model_id}' found in fallback list but not in main cache during get_model_details.")
                return model

        logger.warning(f"Model with ID '{model_id}' not found in cache or Supabase.")
        return None

    def get_cache_status(self) -> Dict[str, Any]: # This reflects in-memory cache, not Supabase state
        """Returns information about the current in-memory cache state."""
        return {
            "last_updated": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "number_of_models": len(self._cached_models),
            "using_fallbacks_only": self._cached_models == self._fallback_models_loaded and bool(self._fallback_models_loaded) and self._cache_timestamp is not None,
            "refresh_interval_seconds": LLM_REFRESH_INTERVAL_SECONDS,
            "cache_ttl_seconds": LLM_CACHE_TTL_SECONDS
        }

    # Old transcribe_audio method removed.
    # Old get_chat_completion method removed.

    async def chat_completion_advanced(
        self,
        model_alias: str,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        stream: Optional[bool] = False,
        user: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        safety_settings: Optional[List[Dict[str, Any]]] = None,
        thinking: Optional[Dict[str, Any]] = None,
        reasoning_effort: Optional[str] = None,
        cache_control: Optional[Dict[str, Any]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        request_timeout: Optional[float] = 120.0
    ) -> Union[Dict[str, Any], AsyncGenerator[bytes, None]]:
        """
        Performs a chat completion request to the LiteLLM proxy with advanced parameters.

        Args:
            model_alias: The alias of the model to use (as configured in LiteLLM).
            messages: A list of message objects.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            user: A unique identifier for the end-user.
            tools: A list of tools the model may call.
            tool_choice: Controls which tool the model should use.
            safety_settings: Safety settings for the request.
            thinking: Custom parameter for LiteLLM.
            reasoning_effort: Custom parameter for LiteLLM.
            cache_control: Cache control parameters for LiteLLM proxy.
            extra_body: Additional parameters to include in the request body.
            request_timeout: Timeout for the HTTP request in seconds.

        Returns:
            If stream is False, a dictionary containing the chat completion response.
            If stream is True, an async generator yielding bytes of the streamed response.
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status.
            httpx.RequestError: If a network error occurs.
            json.JSONDecodeError: If stream is False and the response is not valid JSON.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for chat_completion_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/chat/completions"
        logger.info(f"Attempting advanced chat completion: {endpoint_url} with model '{model_alias}', stream: {stream}")

        headers = {"Content-Type": "application/json"}
        # Use the global LITELLM_PROXY_API_KEY as the class doesn't store it per instance
        # This aligns with how _fetch_models_from_litellm_proxy and transcribe_audio use it.
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        litellm_payload = {
            "model": model_alias,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "user": user,
            "tools": tools,
            "tool_choice": tool_choice,
            "safety_settings": safety_settings,
            "thinking": thinking,
            "reasoning_effort": reasoning_effort,
            "cache_control": cache_control,
            # "extra_body" is merged below if it exists
        }

        # Merge extra_body if provided
        if extra_body:
            litellm_payload.update(extra_body)
        
        # Remove None values from the payload to avoid sending them to LiteLLM
        litellm_payload = {k: v for k, v in litellm_payload.items() if v is not None}
        
        logger.debug(f"LiteLLM payload for advanced chat completion (model: {model_alias}): {litellm_payload}")

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = None # Initialize response to None for broader scope in finally blocks
            try:
                response = await client.post(
                    endpoint_url,
                    headers=headers,
                    json=litellm_payload
                )
                response.raise_for_status() # Raise HTTPStatusError for 4xx/5xx responses

                if stream:
                    async def stream_generator():
                        # Ensure response is available in this inner scope
                        nonlocal response 
                        try:
                            async for chunk in response.aiter_bytes():
                                yield chunk
                        except Exception as e_stream: 
                            logger.error(f"Error during response streaming for model '{model_alias}': {e_stream}", exc_info=True)
                            raise 
                        finally:
                            if response:
                                await response.aclose()
                                logger.debug(f"Stream closed for model '{model_alias}'")
                    return stream_generator()
                else:
                    try:
                        response_data = response.json()
                    except json.JSONDecodeError as e_json:
                        logger.error(f"JSON decode error for non-streamed response from model '{model_alias}': {e_json.msg}. Response text (first 500 chars): {response.text[:500]}", exc_info=False)
                        # Response will be closed in the outer finally block
                        raise 
                    
                    logger.info(f"Non-streamed chat completion successful for model '{model_alias}'.")
                    return response_data

            except httpx.HTTPStatusError as e_http:
                response_text = e_http.response.text[:500] if e_http.response else "No response body"
                logger.error(
                    f"HTTP error during advanced chat completion for model '{model_alias}' ({e_http.request.url}): "
                    f"{e_http.response.status_code} - {response_text}", 
                    exc_info=True # Full traceback for HTTPStatusError
                )
                raise 
            except httpx.RequestError as e_req:
                logger.error(
                    f"Request error during advanced chat completion for model '{model_alias}' ({e_req.request.url}): {e_req}", 
                    exc_info=True
                )
                raise 
            except Exception as e_unexpected:
                logger.error(
                    f"Unexpected error during advanced chat completion for model '{model_alias}': {e_unexpected}",
                    exc_info=True
                )
                raise
            finally:
                if response and not stream: # For non-streaming, response should be closed here if not already
                    if hasattr(response, 'is_closed') and not response.is_closed:
                        await response.aclose()
                        logger.debug(f"Non-streamed response closed for model '{model_alias}' in finally block.")
                    elif not hasattr(response, 'is_closed'): # If it's not an httpx.Response (e.g. error before response)
                        pass
                # For streaming, stream_generator's finally block handles closing.

    async def create_embeddings_advanced(
        self,
        model_alias: str,
        input_data: Union[str, List[str]],
        extra_body: Optional[Dict[str, Any]] = None,
        request_timeout: Optional[float] = 60.0
    ) -> Dict[str, Any]:
        """
        Creates embeddings for the given input using the specified model via LiteLLM proxy.

        Args:
            model_alias: The alias of the embedding model to use (as configured in LiteLLM).
            input_data: A string or list of strings to embed.
            extra_body: Additional parameters to include in the request body,
                        e.g., {"encoding_format": "base64", "user": "user-123"}.
            request_timeout: Timeout for the HTTP request in seconds.

        Returns:
            A dictionary representing the embedding response from LiteLLM,
            typically mappable to OpenAI's EmbeddingResponse schema.
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status.
            httpx.RequestError: If a network error occurs.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for create_embeddings_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/embeddings"
        logger.info(f"Attempting to create embeddings: {endpoint_url} with model '{model_alias}'")

        headers = {"Content-Type": "application/json"}
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        litellm_payload = {
            "model": model_alias,
            "input": input_data,
        }

        if extra_body:
            litellm_payload.update(extra_body)
        
        # Remove None values from the payload to keep it clean
        litellm_payload = {k: v for k, v in litellm_payload.items() if v is not None}

        logger.debug(f"LiteLLM payload for embeddings (model: {model_alias}): {litellm_payload}")

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = None 
            try:
                response = await client.post(
                    endpoint_url,
                    headers=headers,
                    json=litellm_payload
                )
                response.raise_for_status() 
                
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e_json:
                    logger.error(f"JSON decode error for embeddings response from model '{model_alias}': {e_json.msg}. Response text (first 500 chars): {response.text[:500]}", exc_info=False)
                    raise
                
                logger.info(f"Embeddings creation successful for model '{model_alias}'.")
                return response_data

            except httpx.HTTPStatusError as e_http:
                response_text = e_http.response.text[:500] if e_http.response else "No response body"
                logger.error(
                    f"HTTP error during embeddings creation for model '{model_alias}' ({e_http.request.url}): "
                    f"{e_http.response.status_code} - {response_text}", 
                    exc_info=True
                )
                raise
            except httpx.RequestError as e_req:
                logger.error(
                    f"Request error during embeddings creation for model '{model_alias}' ({e_req.request.url}): {e_req}", 
                    exc_info=True
                )
                raise
            except Exception as e_unexpected: # Catch any other unexpected errors
                logger.error(
                    f"Unexpected error during embeddings creation for model '{model_alias}': {e_unexpected}",
                    exc_info=True
                )
                raise
            finally:
                if response:
                    await response.aclose()
                    logger.debug(f"Embeddings response closed for model '{model_alias}' in finally block.")

    async def analyze_vision_advanced(
        self,
        model_alias: str,
        messages: List[Dict[str, Any]], # Already converted from Pydantic ChatMessage with vision content
        max_tokens: Optional[int] = 300,
        temperature: Optional[float] = None,
        # user: Optional[str] = None, # Not in current llm_routes.py payload for vision
        extra_body: Optional[Dict[str, Any]] = None,
        request_timeout: Optional[float] = 120.0
    ) -> Dict[str, Any]: # Returns dict mappable to ChatCompletionResponse
        """
        Sends a request with vision (image) data to the LiteLLM proxy.
        Assumes messages are already formatted correctly for multimodal input.

        Args:
            model_alias: The alias of the vision model to use.
            messages: A list of message objects, with image URLs formatted as per LiteLLM expectations
                      (e.g., {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}).
            max_tokens: Maximum number of tokens to generate in the response.
            temperature: Sampling temperature.
            extra_body: Additional parameters to include in the request body.
            request_timeout: Timeout for the HTTP request in seconds.

        Returns:
            A dictionary representing the chat completion response from LiteLLM.
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status.
            httpx.RequestError: If a network error occurs.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for analyze_vision_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/chat/completions" # Vision models often use chat completions endpoint
        logger.info(f"Attempting vision analysis: {endpoint_url} with model '{model_alias}'")

        headers = {"Content-Type": "application/json"}
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        litellm_payload = {
            "model": model_alias,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if extra_body:
            litellm_payload.update(extra_body)
        
        # Remove None values from the payload
        litellm_payload = {k: v for k, v in litellm_payload.items() if v is not None}

        logger.debug(f"LiteLLM payload for vision analysis (model: {model_alias}): {litellm_payload}")

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = None
            try:
                response = await client.post(
                    endpoint_url,
                    headers=headers,
                    json=litellm_payload
                )
                response.raise_for_status()
                
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e_json:
                    logger.error(f"JSON decode error for vision analysis response from model '{model_alias}': {e_json.msg}. Response text (first 500 chars): {response.text[:500]}", exc_info=False)
                    raise
                
                logger.info(f"Vision analysis successful for model '{model_alias}'.")
                return response_data

            except httpx.HTTPStatusError as e_http:
                response_text = e_http.response.text[:500] if e_http.response else "No response body"
                logger.error(
                    f"HTTP error during vision analysis for model '{model_alias}' ({e_http.request.url}): "
                    f"{e_http.response.status_code} - {response_text}", 
                    exc_info=True
                )
                raise
            except httpx.RequestError as e_req:
                logger.error(
                    f"Request error during vision analysis for model '{model_alias}' ({e_req.request.url}): {e_req}", 
                    exc_info=True
                )
                raise
            except Exception as e_unexpected:
                logger.error(
                    f"Unexpected error during vision analysis for model '{model_alias}': {e_unexpected}",
                    exc_info=True
                )
                raise
            finally:
                if response:
                    await response.aclose()
                    logger.debug(f"Vision analysis response closed for model '{model_alias}' in finally block.")

    async def synthesize_speech_advanced(
        self,
        model_alias: str,
        input_text: str,
        voice: str,
        response_format: Optional[str] = "mp3",
        speed: Optional[float] = 1.0,
        extra_body: Optional[Dict[str, Any]] = None,
        request_timeout: Optional[float] = 120.0
    ) -> Tuple[AsyncGenerator[bytes, None], str]:
        """
        Synthesizes speech from text using the specified model via LiteLLM proxy,
        returning a stream of audio data and its media type.

        Args:
            model_alias: The alias of the TTS model to use.
            input_text: The text to synthesize.
            voice: The voice to use for synthesis.
            response_format: The desired audio format (e.g., "mp3", "opus").
            speed: The speed of the speech.
            extra_body: Additional parameters for the LiteLLM request.
            request_timeout: Timeout for the HTTP request.

        Returns:
            A tuple containing:
                - An async generator yielding bytes of the audio stream.
                - A string representing the media type of the audio (e.g., "audio/mpeg").
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status on the initial request.
            httpx.RequestError: If a network error occurs on the initial request.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for synthesize_speech_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/audio/speech"
        logger.info(f"Attempting speech synthesis: {endpoint_url} with model '{model_alias}', format: {response_format}")

        headers = {"Content-Type": "application/json"} # LiteLLM /v1/audio/speech usually expects JSON
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        litellm_payload = {
            "model": model_alias,
            "input": input_text,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
        }

        if extra_body:
            litellm_payload.update(extra_body)
        
        litellm_payload = {k: v for k, v in litellm_payload.items() if v is not None}
        logger.debug(f"LiteLLM payload for speech synthesis (model: {model_alias}): {litellm_payload}")

        media_type_map = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            # Add others if LiteLLM supports them, e.g., pcm, wav
            "pcm": "audio/wav", # Often PCM is delivered as WAV
            "wav": "audio/wav"
        }
        media_type = media_type_map.get(response_format.lower() if response_format else "mp3", "application/octet-stream")

        # httpx.AsyncClient should be managed carefully with response streaming
        # The response object itself needs to be passed to the generator
        
        client = httpx.AsyncClient(timeout=request_timeout)
        response = None # Define response here to ensure it's available in finally block
        try:
            response = await client.post(
                endpoint_url,
                headers=headers,
                json=litellm_payload
            )
            response.raise_for_status() # Check for errors before starting to stream

            # If successful up to here, prepare the generator
            async def stream_generator(r: httpx.Response, c: httpx.AsyncClient):
                try:
                    async for chunk in r.aiter_bytes():
                        yield chunk
                except httpx.ReadError as e_read: # Catch errors during streaming
                    logger.error(f"Read error during speech audio streaming for model '{model_alias}': {e_read}", exc_info=True)
                    # Error is logged, generator stops. Consumer of generator will handle abrupt end.
                except Exception as e_stream:
                    logger.error(f"Unexpected error during speech audio streaming for model '{model_alias}': {e_stream}", exc_info=True)
                finally:
                    await r.aclose()
                    await c.aclose() # Close client after response is fully processed
                    logger.debug(f"Speech audio stream and client closed for model '{model_alias}'")
            
            return (stream_generator(response, client), media_type)

        except (httpx.HTTPStatusError, httpx.RequestError) as e_req_http: # Catch initial request errors
            # These errors happen before streaming starts or if response.raise_for_status() fails
            error_message = f"Error during initial speech synthesis request for model '{model_alias}': {e_req_http}"
            if isinstance(e_req_http, httpx.HTTPStatusError):
                error_message += f" - Status: {e_req_http.response.status_code}, Response: {e_req_http.response.text[:500]}"
            logger.error(error_message, exc_info=True)
            
            if response: # If response object exists, ensure it's closed
                await response.aclose()
            await client.aclose() # Always close the client if an error occurs before returning generator
            raise # Re-raise the caught httpx error
        
        except Exception as e_unexpected: # Catch any other unexpected errors during setup
            logger.error(f"Unexpected error during speech synthesis setup for model '{model_alias}': {e_unexpected}", exc_info=True)
            if response:
                await response.aclose()
            await client.aclose()
            raise

    async def transcribe_audio_advanced(
        self,
        model_alias: str,
        file_name: str, 
        file_data: bytes, 
        content_type: str, 
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = "json", 
        temperature: Optional[float] = 0.0,
        extra_form_data: Optional[Dict[str, Any]] = None, 
        request_timeout: Optional[float] = 300.0
    ) -> Union[Dict[str, Any], str]:
        """
        Transcribes audio using the specified model via LiteLLM proxy.

        Args:
            model_alias: The alias of the transcription model.
            file_name: The original filename of the audio.
            file_data: The raw bytes of the audio file.
            content_type: The MIME type of the audio file.
            language: The language of the audio.
            prompt: An optional text prompt to guide transcription.
            response_format: Desired output format ('json', 'text', 'srt', 'verbose_json', 'vtt').
            temperature: Sampling temperature for transcription.
            extra_form_data: Additional form fields for the multipart request.
            request_timeout: Timeout for the HTTP request.

        Returns:
            A dictionary if the response format is JSON, otherwise a string.
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status.
            httpx.RequestError: If a network error occurs.
            json.JSONDecodeError: If a JSON response was expected and parsing fails.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for transcribe_audio_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/audio/transcriptions"
        logger.info(f"Attempting audio transcription: {endpoint_url} with model '{model_alias}', format: {response_format}")

        headers = {} # Content-Type will be set by httpx for multipart/form-data
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        data_payload = {
            "model": model_alias,
            "language": language,
            "prompt": prompt,
            "response_format": response_format,
            "temperature": temperature,
        }
        if extra_form_data:
            data_payload.update(extra_form_data)
        
        # Filter out None values from data_payload
        data_payload = {k: v for k, v in data_payload.items() if v is not None}
        logger.debug(f"LiteLLM data payload for audio transcription (model: {model_alias}): {data_payload}")

        files_payload = {'file': (file_name, file_data, content_type)}

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = None
            try:
                response = await client.post(
                    endpoint_url,
                    headers=headers,
                    data=data_payload,
                    files=files_payload
                )
                response.raise_for_status()
                
                # Determine how to parse based on expected response_format or Content-Type header
                # LiteLLM's /v1/audio/transcriptions should set Content-Type appropriately
                response_content_type = response.headers.get("Content-Type", "").lower()

                if "application/json" in response_content_type:
                    try:
                        return response.json()
                    except json.JSONDecodeError as e_json:
                        logger.error(f"JSON decode error for transcription response (model '{model_alias}', format '{response_format}'): {e_json.msg}. Response text (first 500 chars): {response.text[:500]}", exc_info=False)
                        raise
                else: # For 'text', 'srt', 'vtt', etc.
                    return response.text

            except httpx.HTTPStatusError as e_http:
                response_text = e_http.response.text[:500] if e_http.response else "No response body"
                logger.error(
                    f"HTTP error during audio transcription for model '{model_alias}' ({e_http.request.url}): "
                    f"{e_http.response.status_code} - {response_text}", 
                    exc_info=True
                )
                raise
            except httpx.RequestError as e_req:
                logger.error(
                    f"Request error during audio transcription for model '{model_alias}' ({e_req.request.url}): {e_req}", 
                    exc_info=True
                )
                raise
            except Exception as e_unexpected:
                logger.error(
                    f"Unexpected error during audio transcription for model '{model_alias}': {e_unexpected}",
                    exc_info=True
                )
                raise
            finally:
                if response:
                    await response.aclose()
                    logger.debug(f"Audio transcription response closed for model '{model_alias}' in finally block.")

    async def generate_image_advanced(
        self,
        model_alias: str,
        prompt: str,
        n: Optional[int] = 1,
        size: Optional[str] = None, 
        quality: Optional[str] = None, 
        style: Optional[str] = None, 
        response_format: Optional[str] = "url", 
        extra_body: Optional[Dict[str, Any]] = None,
        request_timeout: Optional[float] = 120.0
    ) -> Dict[str, Any]:
        """
        Generates an image using the specified model via LiteLLM proxy.

        Args:
            model_alias: The alias of the image generation model.
            prompt: The text prompt for image generation.
            n: The number of images to generate.
            size: The size of the generated images (e.g., '1024x1024').
            quality: The quality of the images ('standard', 'hd').
            style: The style of the images ('vivid', 'natural').
            response_format: The format of the response ('url', 'b64_json').
            extra_body: Additional parameters for the LiteLLM request.
            request_timeout: Timeout for the HTTP request.

        Returns:
            A dictionary representing the image generation response from LiteLLM.
        
        Raises:
            ValueError: If LiteLLM Proxy URL is not configured.
            httpx.HTTPStatusError: If the proxy returns an HTTP error status.
            httpx.RequestError: If a network error occurs.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        proxy_url_to_use = self.litellm_proxy_url if self.litellm_proxy_url else LITELLM_PROXY_URL
        if not proxy_url_to_use:
            logger.error("LiteLLM Proxy URL is not configured for generate_image_advanced.")
            raise ValueError("LiteLLM Proxy URL is not configured.")

        endpoint_url = f"{proxy_url_to_use}/v1/images/generations"
        logger.info(f"Attempting image generation: {endpoint_url} with model '{model_alias}'")

        headers = {"Content-Type": "application/json"}
        if LITELLM_PROXY_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_PROXY_API_KEY}"

        litellm_payload = {
            "model": model_alias,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "style": style,
            "response_format": response_format,
        }

        if extra_body:
            litellm_payload.update(extra_body)
        
        litellm_payload = {k: v for k, v in litellm_payload.items() if v is not None}
        logger.debug(f"LiteLLM payload for image generation (model: {model_alias}): {litellm_payload}")

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = None
            try:
                response = await client.post(
                    endpoint_url,
                    headers=headers,
                    json=litellm_payload
                )
                response.raise_for_status()
                
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e_json:
                    logger.error(f"JSON decode error for image generation response from model '{model_alias}': {e_json.msg}. Response text (first 500 chars): {response.text[:500]}", exc_info=False)
                    raise
                
                logger.info(f"Image generation successful for model '{model_alias}'.")
                return response_data

            except httpx.HTTPStatusError as e_http:
                response_text = e_http.response.text[:500] if e_http.response else "No response body"
                logger.error(
                    f"HTTP error during image generation for model '{model_alias}' ({e_http.request.url}): "
                    f"{e_http.response.status_code} - {response_text}", 
                    exc_info=True
                )
                raise
            except httpx.RequestError as e_req:
                logger.error(
                    f"Request error during image generation for model '{model_alias}' ({e_req.request.url}): {e_req}", 
                    exc_info=True
                )
                raise
            except Exception as e_unexpected:
                logger.error(
                    f"Unexpected error during image generation for model '{model_alias}': {e_unexpected}",
                    exc_info=True
                )
                raise
            finally:
                if response:
                    await response.aclose()
                    logger.debug(f"Image generation response closed for model '{model_alias}' in finally block.")


# --- Singleton Instance and Getter Function ---
_llm_registry_instance: Optional[LLMRegistryService] = None

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
            chat_kwargs = {"temperature": 0.7, "max_tokens": 50, "stream": False}
            # completion_response = await registry.get_chat_completion(test_chat_model_id, test_messages, **chat_kwargs)
            completion_response_dict = await registry.chat_completion_advanced(
                model_alias=test_chat_model_id, 
                messages=test_messages, 
                **chat_kwargs
            )

            if completion_response_dict and isinstance(completion_response_dict, dict):
                # Extract content from the response dictionary
                # This assumes a structure similar to OpenAI's response
                try:
                    content = completion_response_dict.get("choices")[0].get("message").get("content")
                    print(f"  LLM Response: {content}")
                except (IndexError, AttributeError, TypeError) as e_parse:
                    print(f"  Error parsing LLM response content: {e_parse}. Full response: {completion_response_dict}")
            elif hasattr(completion_response_dict, '__aiter__'): # If it's a stream
                 print(f"  LLM Response is a stream. Consuming for test...")
                 async for chunk in completion_response_dict:
                     print(f"    Stream chunk: {chunk[:50]}...") # Print first 50 bytes of chunk
                 print(f"  LLM Stream finished.")
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
