# -*- coding: utf-8 -*-
"""
Module to handle content fetching using the crawl4ai library.
"""

import logging
logger = logging.getLogger(__name__) # Define logger at the top

import asyncio
import json
import os # Added for environment variables
import time # Added for timing
from typing import Dict, Any, AsyncGenerator, List, Optional, Tuple, Union, Pattern
from datetime import datetime, timezone # Added for timestamps

from crawl4ai import (
    # AsyncWebCrawler, # No longer using in-process crawler directly
    CrawlResult,
    BrowserConfig,
    CrawlerRunConfig,
    LLMConfig,
    ExtractionStrategy,
    LLMExtractionStrategy,
    CosineStrategy,
    JsonCssExtractionStrategy,
    BFSDeepCrawlStrategy,
    DFSDeepCrawlStrategy,
    BestFirstCrawlingStrategy,
    DefaultMarkdownGenerator, # Added for Markdown generator selection
)
# from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy # Not needed when using Docker client
from crawl4ai.content_filter_strategy import PruningContentFilter # Added for advanced MD generator
from crawl4ai.models import CrawlResultContainer # Added to handle new result type
from crawl4ai.models import MarkdownGenerationResult # Added for type checking markdown field
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from crawl4ai.deep_crawling.scorers import URLScorer, KeywordRelevanceScorer

# Import the Docker client
from crawl4ai.docker_client import Crawl4aiDockerClient, Crawl4aiClientError

# --- Local Imports ---
try:
    from .utils.llm_registry_service import get_llm_registry_service # Import the getter function
    LLM_REGISTRY_AVAILABLE = True
except ImportError:
    LLM_REGISTRY_AVAILABLE = False # Keep this flag
    get_llm_model_details_from_registry = None # type: ignore
    logger.error("llm_registry_service not available. LLM model selection will rely on direct parameters.")

try:
    from .app_config import LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY
    PROXY_CONFIG_LOADED = True
    logger.info(f"Successfully imported LiteLLM proxy config: URL='{LITELLM_PROXY_URL}', Key_Loaded={'Yes' if LITELLM_PROXY_API_KEY else 'No'}")
except ImportError:
    logger.warning("Could not import LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY from .app_config. Proxy integration will be disabled or use defaults.")
    LITELLM_PROXY_URL = os.getenv('LITELLM_PROXY_URL', 'http://localhost:4000') # Fallback
    LITELLM_PROXY_API_KEY = os.getenv('LITELLM_PROXY_API_KEY') # Fallback
    PROXY_CONFIG_LOADED = False

# --- Helper Functions for Type Conversion ---
def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 't')
    return bool(value)

def to_list_str(value: Any, delimiter: str = ',') -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    return None

def to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def to_json_dict(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        if not value.strip(): # Check if string is empty or only whitespace
            return None       # Return None silently for empty/whitespace strings
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON string: {value}", exc_info=True)
            return None
    return None

# to_tuple_int is not used with the new individual viewport width/height params
# def to_tuple_int(value: Any, delimiter: str = 'x') -> Optional[Tuple[int, int]]:
#     if isinstance(value, str):
#         parts = value.split(delimiter)
#         if len(parts) == 2:
#             try:
#                 return int(parts[0]), int(parts[1])
#             except ValueError:
#                 return None
#     return None

async def fetch_with_crawl4ai(url: str, original_request_params: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """
    Async generator for fetching content using the crawl4ai Docker service, yielding SSE events.
    Maps UI parameters from docs/fetch_page_enhancement_plan.md to crawl4ai config objects.
    Includes comprehensive LLM call logging and structured error reporting.
    """
    logger.info(f"crawl4ai_fetcher called for URL: {url}")
    logger.info(f"crawl4ai_fetcher received original_request_params: {original_request_params}") # DIAGNOSTIC
    logger.debug(f"Original request parameters for crawl4ai: {original_request_params}")

    params = original_request_params
    llm_log_data: Dict[str, Any] = {} # Initialize for potential LLM logging

    # Define the base URL for the crawl4ai Docker service
    # This should match the service name and port in your docker-compose-core.yml
    CRAWL4AI_SERVICE_URL = os.getenv('CRAWL4AI_SERVICE_URL', 'http://crawl4ai:11235')
    # If your crawl4ai service requires an API token (configured in its config.yml)
    CRAWL4AI_API_TOKEN = os.getenv('CRAWL4AI_API_TOKEN') # You will need to set this env var in your backend service

    crawl4ai_client = None # Initialize client to None

    try:
        yield json.dumps({"type": "status", "status": "initializing", "message": "Initializing crawl4ai service client..."})

        # --- Initialize Crawl4aiDockerClient ---
        # Pass the service URL and API token if required
        crawl4ai_client = Crawl4aiDockerClient(base_url=CRAWL4AI_SERVICE_URL, api_token=CRAWL4AI_API_TOKEN)
        await crawl4ai_client.authenticate() # Authenticate if using JWT
        yield json.dumps({"type": "status", "status": "initialized", "message": "crawl4ai service client initialized."})

        # --- BrowserConfig Population ---
        # UI parameters are sourced from docs/fetch_page_enhancement_plan.md (lines 81-133)
        # crawl4ai parameters from docs/crawl4ai/docs/md_v2/api/parameters.md

        browser_config_args = {
            "headless": to_bool(params.get("headless", True)), # Matches main.py Query param
            "user_agent": params.get("user_agent"), # Matches main.py Query param
            "proxy": params.get("proxy_url"), # Matches main.py Query param 'proxy_url', maps to 'proxy' in BrowserConfig
            "java_script_enabled": to_bool(params.get("enable_javascript", True)), # Matches main.py Query param 'enable_javascript'
            "ignore_https_errors": to_bool(params.get("ignore_https_errors", True)), # Matches main.py Query param
            "light_mode": to_bool(params.get("light_mode", False)), # Matches main.py Query param
            "text_mode": to_bool(params.get("text_mode", False)), # Matches main.py Query param
            "cookies": to_json_dict(params.get("browser_cookies")), # Matches main.py Query param
            "headers": to_json_dict(params.get("browser_headers")), # Matches main.py Query param
            "use_persistent_context": to_bool(params.get("browser_use_persistent_context")), # Matches main.py Query param
            "user_data_dir": params.get("browser_user_data_dir"), # Matches main.py Query param
            "extra_args": to_list_str(params.get("browser_extra_args")), # Matches main.py Query param
            # Viewport width and height are handled separately below as they are individual query params
        }
        # Viewport Size from UI (separate width and height)
        # These keys 'viewport_width' and 'viewport_height' match the Query params in main.py
        viewport_width_val = params.get("viewport_width")
        if viewport_width_val is not None:
            browser_config_args["viewport_width"] = to_int(viewport_width_val)
        
        viewport_height_val = params.get("viewport_height")
        if viewport_height_val is not None:
            browser_config_args["viewport_height"] = to_int(viewport_height_val)
        
        # Filter out None values for optional parameters before passing to BrowserConfig
        final_browser_config_args = {k: v for k, v in browser_config_args.items() if v is not None}
        logger.info(f"Intermediate browser_config_args: {browser_config_args}") # DIAGNOSTIC
        # Create BrowserConfig object from processed parameters
        browser_config = BrowserConfig(**final_browser_config_args)
        logger.info(f"Final browser_config_args for BrowserConfig(): {final_browser_config_args}") # DIAGNOSTIC
        logger.debug(f"BrowserConfig: {final_browser_config_args}") # Log the args passed

        # --- LLMConfig Population (Optional) ---
        # This section is for the main crawler's LLMConfig, if crawl4ai itself uses one at the top level.
        # The LLMExtractionStrategy will have its own LLMConfig instance.
        # For now, we assume the main crawler does not need a separate LLMConfig from this part of the code.
        # If it were needed, similar logic to the LLMExtractionStrategy's LLMConfig setup would apply.
        llm_config = None # Placeholder, not currently used for the main crawler instance here.
        logger.debug(f"Top-level LLMConfig for crawler (not strategy): {llm_config}")

        # --- Deep Crawl Strategy Population (Advanced) ---
        deep_crawl_strategy_instance: Optional[Union[BFSDeepCrawlStrategy, DFSDeepCrawlStrategy, BestFirstCrawlingStrategy]] = None
        # --- Determine Deep Crawl Configuration ---
        # Priority:
        # 1. Valid `deep_crawl_config` JSON blob from `params`.
        # 2. Construct from individual `deep_crawl_*` parameters in `params`.
        # 3. Default to empty config (no deep crawl).

        final_deep_crawl_dict = {}
        deep_crawl_config_blob = params.get("deep_crawl_config")

        if isinstance(deep_crawl_config_blob, str) and deep_crawl_config_blob.strip():
            try:
                parsed_blob = json.loads(deep_crawl_config_blob)
                if isinstance(parsed_blob, dict):
                    final_deep_crawl_dict = parsed_blob
                    logger.info(f"Using deep_crawl_config JSON blob: {final_deep_crawl_dict}")
                else:
                    logger.warning(f"Parsed deep_crawl_config string was not a dict: {type(parsed_blob)}. Will check individual params.")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse deep_crawl_config string: {deep_crawl_config_blob}. Will check individual params.", exc_info=True)
        elif isinstance(deep_crawl_config_blob, dict): # If it was already a dictionary (e.g. if tests pass it directly)
            final_deep_crawl_dict = deep_crawl_config_blob
            logger.info(f"Using pre-parsed deep_crawl_config dict: {final_deep_crawl_dict}")
        elif deep_crawl_config_blob is not None: # It's not a string, not a dict, but not None
             logger.warning(f"deep_crawl_config was an unexpected type: {type(deep_crawl_config_blob)}. Will check individual params.")

        # If blob wasn't used or was invalid, try constructing from individual parameters
        individual_params_for_strategy_dict = {} # Initialize here
        if not final_deep_crawl_dict:
            logger.info("deep_crawl_config JSON blob not used or invalid. Attempting to construct from individual parameters.")
            
            # Parameter names here match those potentially sent by tests or UI forms
            # (e.g., deep_crawl_strategy_name, deep_crawl_max_depth)
            strategy_from_individual = params.get("deep_crawl_strategy_name") or params.get("strategy") # Fallback for "strategy" key

            if strategy_from_individual and isinstance(strategy_from_individual, str) and strategy_from_individual.strip():
                individual_params_for_strategy_dict = {}
                
                # Max Depth
                max_depth_val = params.get("deep_crawl_max_depth")
                if max_depth_val is not None: individual_params_for_strategy_dict["max_depth"] = max(0, max_depth_val)
                
                # Max Pages
                max_pages_val = params.get("deep_crawl_max_pages")
                if max_pages_val is not None: individual_params_for_strategy_dict["max_pages"] = max(1, max_pages_val)
                
                # Include External
                include_external_val = params.get("deep_crawl_include_external")
                if include_external_val is not None: individual_params_for_strategy_dict["include_external"] = to_bool(include_external_val)

            # Score Threshold
            score_threshold_val = params.get("deep_crawl_score_threshold")
            if score_threshold_val is not None: individual_params_for_strategy_dict["score_threshold"] = score_threshold_val

            # Filter Regexes (can be list or comma-separated string)
            filter_regexes_val = params.get("deep_crawl_filter_regexes")
            if filter_regexes_val is not None:
                if isinstance(filter_regexes_val, list):
                    individual_params_for_strategy_dict["filter_regexes"] = filter_regexes_val
                elif isinstance(filter_regexes_val, str):
                     # The processing logic later expects a list for URLPatternFilter
                    individual_params_for_strategy_dict["filter_regexes"] = to_list_str(filter_regexes_val)
                else:
                    logger.warning(f"deep_crawl_filter_regexes was an unexpected type: {type(filter_regexes_val)}")

            # URL Scorer Type
            url_scorer_type_val = params.get("deep_crawl_url_scorer_type")
            if url_scorer_type_val is not None: individual_params_for_strategy_dict["url_scorer_type"] = url_scorer_type_val

            # Scorer Keywords (can be list or comma-separated string)
            scorer_keywords_val = params.get("deep_crawl_scorer_keywords")
            if scorer_keywords_val is not None:
                # The processing logic later expects a string for KeywordRelevanceScorer's keywords, then splits it
                if isinstance(scorer_keywords_val, list):
                    individual_params_for_strategy_dict["scorer_keywords"] = ",".join(scorer_keywords_val)
                elif isinstance(scorer_keywords_val, str):
                    individual_params_for_strategy_dict["scorer_keywords"] = scorer_keywords_val
                else:
                     logger.warning(f"deep_crawl_scorer_keywords was an unexpected type: {type(scorer_keywords_val)}")
            

            # --- Construct Deep Crawl Strategy from Individual Params ---
            if strategy_from_individual:
                try:
                    logger.info(f"Attempting to construct deep crawl strategy '{strategy_from_individual}' from individual parameters: {individual_params_for_strategy_dict}")
                    if strategy_from_individual.lower() == "bfs":
                        deep_crawl_strategy_instance = BFSDeepCrawlStrategy(**individual_params_for_strategy_dict)
                    elif strategy_from_individual.lower() == "dfs":
                         deep_crawl_strategy_instance = DFSDeepCrawlStrategy(**individual_params_for_strategy_dict)
                    elif strategy_from_individual.lower() == "bestfirst":
                         # BestFirstCrawlingStrategy takes url_scorer_type, filter_regexes, scorer_keywords, max_pages, include_external
                         # Need to handle scorers and filters explicitly if provided as individual params

                         url_scorer: Optional[URLScorer] = None
                         scorer_keywords: Optional[str] = individual_params_for_strategy_dict.get("scorer_keywords")
                         url_scorer_type = individual_params_for_strategy_dict.get("url_scorer_type", "keyword_relevance") # Default to keyword if not specified

                         if url_scorer_type and isinstance(url_scorer_type, str):
                            if url_scorer_type.lower() == "keyword_relevance" and scorer_keywords:
                                url_scorer = KeywordRelevanceScorer(keywords=scorer_keywords)
                            # Add other scorer types here if needed in the future
                            else:
                                logger.warning(f"Unsupported or incomplete url_scorer_type for BestFirst: {url_scorer_type}")

                         filter_chain: Optional[FilterChain] = None
                         filter_regexes: Optional[List[str]] = individual_params_for_strategy_dict.get("filter_regexes")

                         if filter_regexes:
                             filters = [URLPatternFilter(regex) for regex in filter_regexes]
                             filter_chain = FilterChain(filters=filters)

                         deep_crawl_strategy_instance = BestFirstCrawlingStrategy(
                             url_scorer=url_scorer, # Pass the instantiated scorer
                             filter_chain=filter_chain, # Pass the instantiated filter chain
                             max_pages=individual_params_for_strategy_dict.get("max_pages"),
                             include_external=individual_params_for_strategy_dict.get("include_external", False) # Default to False if not specified
                         )

                    else:
                        logger.warning(f"Unknown deep crawl strategy name from individual params: {strategy_from_individual}")

                    if deep_crawl_strategy_instance: # Check if successfully created
                         logger.info(f"Successfully constructed deep crawl strategy instance: {type(deep_crawl_strategy_instance).__name__}")
                         # If constructed from individual params, convert to dict format for final_deep_crawl_dict
                         # Note: This conversion might lose some information depending on the strategy's __dict__ or serialization
                         # A more robust approach would be to serialize the strategy instance if crawl4ai client expects a specific JSON format
                         # For now, we'll create a simple dict representation
                         final_deep_crawl_dict = {
                             "strategy_name": strategy_from_individual,
                             **{k: v for k, v in individual_params_for_strategy_dict.items() if k != "strategy_name"}
                         } # Add individual params back for logging/potential use
                         # Special handling for complex objects like scorers/filters if they were constructed
                         if isinstance(deep_crawl_strategy_instance, BestFirstCrawlingStrategy):
                              final_deep_crawl_dict["url_scorer"] = str(deep_crawl_strategy_instance.url_scorer) if deep_crawl_strategy_instance.url_scorer else None
                              final_deep_crawl_dict["filter_chain"] = str(deep_crawl_strategy_instance.filter_chain) if deep_crawl_strategy_instance.filter_chain else None


                except Exception as e:
                    logger.error(f"Error constructing deep crawl strategy from individual params: {e}", exc_info=True)

        # --- Extraction Strategy Population ---
        extraction_strategy_instance: Optional[ExtractionStrategy] = None
        extraction_strategy_type = params.get("extraction_strategy")

        if extraction_strategy_type and isinstance(extraction_strategy_type, str):
            if extraction_strategy_type.lower() == "llm":
                # --- LLMExtractionStrategy Population (Advanced) ---
                llm_extraction_strategy_params = {}

                # Get LLM Model Config from LLM Registry (Preferred)
                llm_model_alias = params.get("llm_model_alias") or os.getenv('DEFAULT_LLM_MODEL_ALIAS') # Use alias from params or env var
                llm_config_instance: Optional[LLMConfig] = None

                if llm_model_alias and LLM_REGISTRY_AVAILABLE and get_llm_registry_service:
                    llm_registry = get_llm_registry_service()
                    if llm_registry:
                        try:
                            # Get model details from the registry using the alias
                            model_details = await llm_registry.get_model_details(llm_model_alias)
                            if model_details:
                                # Construct LLMConfig using details from the registry
                                # The LiteLLM proxy URL is obtained from app_config or fallback env var
                                if PROXY_CONFIG_LOADED or LITELLM_PROXY_URL:
                                    llm_config_instance = LLMConfig(
                                        model=llm_model_alias, # Use the alias defined in LiteLLM config
                                        api_base=LITELLM_PROXY_URL, # Point to the LiteLLM proxy
                                        # API key is handled by the LiteLLM proxy based on its env config
                                        api_key=LITELLM_PROXY_API_KEY, # Pass the proxy's API key (if any)
                                        # Pass extra params from registry or request if needed by the strategy/proxy
                                        extra_params=model_details.get("extra_params"),
                                        # temperature, max_tokens, etc. can also be passed here if needed
                                        # temperature=params.get("llm_temperature"),
                                        # max_tokens=params.get("llm_max_tokens"),
                                    )
                                    logger.info(f"Using LLMConfig from registry details for alias: {llm_model_alias}")
                                else:
                                    logger.warning("LiteLLM proxy URL not configured, cannot create LLMConfig from registry.")
                            else:
                                logger.warning(f"Model details not found in registry for alias: {llm_model_alias}")
                        except Exception as e:
                            logger.error(f"Error getting model details from registry for {llm_model_alias}: {e}", exc_info=True)
                    else:
                        logger.warning("LLM registry service not initialized.")
                elif llm_model_alias:
                     logger.warning("LLM registry service not available or model alias not provided. Using direct LLM params if available.")

                # Fallback: Direct LLM Parameters (if registry not used or failed)
                if llm_config_instance is None:
                    logger.info("Attempting to construct LLMConfig from direct parameters.")
                    try:
                        # Direct parameters from the request, mapping to LLMConfig attributes
                        direct_llm_params_args = {
                            "model": params.get("llm_model"), # Direct model name/ID
                            "api_key": params.get("llm_api_key"), # Direct API Key
                            "api_base": params.get("llm_api_base"), # Direct API Base URL
                            "temperature": to_float(params.get("llm_temperature")), # Matches main.py Query param
                            "max_tokens": to_int(params.get("llm_max_tokens")), # Matches main.py Query param
                            "extra_params": to_json_dict(params.get("llm_extra_params")), # Matches main.py Query param
                            "max_retries": to_int(params.get("llm_max_retries")), # Matches main.py Query param
                            "timeout": to_float(params.get("llm_timeout")), # Matches main.py Query param
                            # provider, api_version, organization, etc. can be added if needed
                        }
                        # Filter out None values
                        filtered_direct_llm_params_args = {k: v for k, v in direct_llm_params_args.items() if v is not None}

                        if filtered_direct_llm_params_args.get("model"): # Only create if a model is specified
                             llm_config_instance = LLMConfig(**filtered_direct_llm_params_args)
                             logger.info(f"Successfully constructed LLMConfig from direct parameters: {filtered_direct_llm_params_args}")
                        else:
                            logger.warning("No LLM model specified in direct parameters. LLMExtractionStrategy will not be created.")

                    except Exception as e:
                         logger.error(f"Error constructing LLMConfig from direct parameters: {e}", exc_info=True)

                # Proceed only if LLMConfig instance was successfully created
                if llm_config_instance:
                    # --- LLMExtractionStrategy Specific Parameters ---
                    llm_strategy_args = {
                        "llm_config": llm_config_instance,
                        "prompt_template": params.get("llm_prompt_template"), # Matches main.py Query param
                        "output_format": params.get("llm_output_format"), # Matches main.py Query param (json, text)
                        "json_schema": to_json_dict(params.get("llm_json_schema")), # Matches main.py Query param (for json output)
                         # vision_enabled, audio_enabled are derived from the model capabilities via registry or config
                         "vision_enabled": to_bool(params.get("llm_vision_enabled")), # Matches main.py Query param
                         "audio_enabled": to_bool(params.get("llm_audio_enabled")), # Matches main.py Query param
                         "tool_calling_enabled": to_bool(params.get("llm_tool_calling_enabled")), # Matches main.py Query param
                         "thinking": params.get("llm_thinking"), # Matches main.py Query param
                         "reasoning_effort": params.get("llm_reasoning_effort"), # Matches main.py Query param
                         "cache_control": params.get("llm_cache_control"), # Matches main.py Query param
                         "metadata": to_json_dict(params.get("llm_metadata")), # Matches main.py Query param
                         "user": params.get("llm_user"), # Matches main.py Query param
                         "input_file_types": to_list_str(params.get("llm_input_file_types")), # Matches main.py Query param
                    }
                    # Filter out None values
                    filtered_llm_strategy_args = {k: v for k, v in llm_strategy_args.items() if v is not None}

                    try:
                        extraction_strategy_instance = LLMExtractionStrategy(**filtered_llm_strategy_args)
                        logger.info(f"Successfully created LLMExtractionStrategy with args: {filtered_llm_strategy_args}")
                    except Exception as e:
                        logger.error(f"Error creating LLMExtractionStrategy: {e}", exc_info=True)
                        # If LLMExtractionStrategy creation fails, yield an error and stop
                        yield json.dumps({"type": "error", "message": f"Failed to configure LLM Extraction Strategy: {e}"})
                        return # Stop the generator

            elif extraction_strategy_type.lower() == "cosine":
                # Cosine Strategy parameters
                cosine_strategy_args = {
                    "query": params.get("cosine_query"),
                    "threshold": to_float(params.get("cosine_threshold")), # Matches main.py Query param
                    "content_weight": to_float(params.get("cosine_content_weight")), # Matches main.py Query param
                    "summary_weight": to_float(params.get("cosine_summary_weight")), # Matches main.py Query param
                    "keywords": to_list_str(params.get("cosine_keywords")), # Matches main.py Query param
                }
                # Filter out None values
                filtered_cosine_strategy_args = {k: v for k, v in cosine_strategy_args.items() if v is not None}

                try:
                    extraction_strategy_instance = CosineStrategy(**filtered_cosine_strategy_args)
                    logger.info(f"Successfully created CosineStrategy with args: {filtered_cosine_strategy_args}")
                except Exception as e:
                     logger.error(f"Error creating CosineStrategy: {e}", exc_info=True)
                     yield json.dumps({"type": "error", "message": f"Failed to configure Cosine Extraction Strategy: {e}"})
                     return # Stop the generator

            elif extraction_strategy_type.lower() == "jsoncss":
                # JsonCss Extraction Strategy parameters
                jsoncss_strategy_args = {
                    "css_selector": params.get("jsoncss_css_selector"), # Matches main.py Query param
                    "extract_attribute": params.get("jsoncss_extract_attribute"), # Matches main.py Query param
                }
                # Filter out None values
                filtered_jsoncss_strategy_args = {k: v for k, v in jsoncss_strategy_args.items() if v is not None}

                try:
                     extraction_strategy_instance = JsonCssExtractionStrategy(**filtered_jsoncss_strategy_args)
                     logger.info(f"Successfully created JsonCssExtractionStrategy with args: {filtered_jsoncss_strategy_args}")
                except Exception as e:
                     logger.error(f"Error creating JsonCssExtractionStrategy: {e}", exc_info=True)
                     yield json.dumps({"type": "error", "message": f"Failed to configure JsonCss Extraction Strategy: {e}"})
                     return # Stop the generator
            else:
                logger.warning(f"Unknown extraction strategy type: {extraction_strategy_type}")
                yield json.dumps({"type": "error", "message": f"Unknown extraction strategy type: {extraction_strategy_type}"})
                return # Stop the generator

        # --- Markdown Generator Population ---
        # DefaultMarkdownGenerator is used unless a custom one is needed based on params.
        # Currently, no parameters in the UI map to custom Markdown generators.
        # The PruningContentFilter for advanced MD generation is tied to the generator instance, not a separate config.
        markdown_generator_instance = DefaultMarkdownGenerator()
        logger.debug("Using DefaultMarkdownGenerator.")

        # Check if advanced markdown generation is requested
        use_advanced_markdown = to_bool(params.get("use_advanced_markdown", False))
        if use_advanced_markdown:
             # Instantiate the PruningContentFilter and apply it to the generator if needed
             # PruningContentFilter is part of crawl4ai's content_filter_strategy
             pruning_filter = PruningContentFilter()
             # Assuming DefaultMarkdownGenerator can accept a content filter
             if hasattr(markdown_generator_instance, 'content_filter'):
                 markdown_generator_instance.content_filter = pruning_filter
                 logger.info("Applied PruningContentFilter to MarkdownGenerator.")
             else:
                 logger.warning("MarkdownGenerator does not support content_filter attribute. Advanced markdown not applied.")



        # --- CrawlerRunConfig Population ---
        # These parameters control the overall crawl execution.
        crawler_run_config_args = {
            "url": url, # The target URL
            "deep_crawl_strategy": deep_crawl_strategy_instance, # Pass the instantiated strategy object
            "extraction_strategy": extraction_strategy_instance, # Pass the instantiated strategy object
            "markdown_generator": markdown_generator_instance, # Pass the instantiated generator object
            "max_timeout": to_float(params.get("max_timeout", 60.0)), # Matches main.py Query param, default 60s
            "keep_html": to_bool(params.get("keep_html", False)), # Matches main.py Query param
            "keep_text": to_bool(params.get("keep_text", True)), # Matches main.py Query param
            "keep_markdown": to_bool(params.get("keep_markdown", True)), # Matches main.py Query param
            "keep_screenshots": to_bool(params.get("keep_screenshots", False)), # Matches main.py Query param
            "screenshots_dir": params.get("screenshots_dir"), # Matches main.py Query param
            "ignore_urls": to_list_str(params.get("ignore_urls")), # Matches main.py Query param
            "include_urls": to_list_str(params.get("include_urls")), # Matches main.py Query param
            "max_retries": to_int(params.get("max_retries")), # Matches main.py Query param
            "retry_delay": to_float(params.get("retry_delay")), # Matches main.py Query param
            # Add other CrawlerRunConfig parameters as needed
        }
        # Filter out None values
        filtered_crawler_run_config_args = {k: v for k, v in crawler_run_config_args.items() if v is not None}

        # Create CrawlerRunConfig object from processed parameters
        crawler_run_config = CrawlerRunConfig(**filtered_crawler_run_config_args)
        logger.debug(f"CrawlerRunConfig: {filtered_crawler_run_config_args}") # Log the args passed

        # --- Execute Crawl using Docker Client ---
        yield json.dumps({"type": "status", "status": "crawling", "message": f"Starting crawl for {url}..."})
        start_time = time.time() # Start timing

        # The crawl4ai_client.crawl() method expects a list of URLs
        urls_to_crawl = [url] # Start with the initial URL
        # If deep crawling is enabled, the client/service handles finding additional URLs
        # based on the deep_crawl_strategy provided in the config.

        # Prepare the request payload for the Docker client
        # The client expects config dictionaries, not Pydantic objects
        request_payload = {
            "urls": urls_to_crawl,
            "browser_config": browser_config.model_dump() if hasattr(browser_config, 'model_dump') else browser_config.dict(), # Use model_dump for Pydantic v2+, dict for v1
            "crawler_config": crawler_run_config.model_dump() if hasattr(crawler_run_config, 'model_dump') else crawler_run_config.dict(),
             # Note: Nested strategy/generator objects might need custom serialization if .dict()/.model_dump() isn't sufficient
             # based on crawl4ai client's API spec. Assuming they handle standard Pydantic dict output for now.
        }

        # Remove None values from the payload dictionary to avoid issues with the client API
        def remove_none_values(data):
             if isinstance(data, dict):
                 return {k: remove_none_values(v) for k, v in data.items() if v is not None}
             elif isinstance(data, list):
                 return [remove_none_values(item) for item in data if item is not None]
             else:
                 return data

        cleaned_request_payload = remove_none_values(request_payload)
        logger.info(f"Sending request payload to crawl4ai service: {cleaned_request_payload}")

        # Call the crawl method on the Docker client
        # Assuming the client's crawl method yields results as they are processed by the service
        async for crawl_result in crawl4ai_client.crawl(cleaned_request_payload):
             # crawl_result is expected to be a CrawlResult object
             logger.debug(f"Received crawl result for URL: {crawl_result.url}")

             # Process the CrawlResult and yield relevant data as SSE events
             # Example: Yield fetched content, markdown, errors, etc.
             output_data: Dict[str, Any] = {"type": "crawl_result", "url": crawl_result.url}

             if crawl_result.status:
                  output_data["status"] = crawl_result.status
             if crawl_result.error:
                 output_data["error"] = str(crawl_result.error)
                 logger.error(f"Crawl error for {crawl_result.url}: {crawl_result.error}")
                 # Depending on desired behavior, you might want to yield an error type event immediately
                 yield json.dumps({"type": "error", "message": f"Error crawling {crawl_result.url}: {crawl_result.error}", "url": crawl_result.url})
                 continue # Skip processing other fields for this error result, move to next if any

             if crawl_result.content:
                 output_data["content"] = crawl_result.content
             if crawl_result.markdown:
                  # Check if markdown is a MarkdownGenerationResult object and extract the markdown string
                 if isinstance(crawl_result.markdown, MarkdownGenerationResult):
                     output_data["markdown"] = crawl_result.markdown.markdown
                 else:
                      # Assuming it might be a string directly in some cases
                      output_data["markdown"] = str(crawl_result.markdown)
             if crawl_result.text:
                 output_data["text"] = crawl_result.text
             if crawl_result.screenshot_path:
                 output_data["screenshot_path"] = crawl_result.screenshot_path
             # Add other fields from CrawlResult as needed (e.g., metadata, links)

             # Include LLM log data if available in the result (crawl4ai might include this)
             if hasattr(crawl_result, 'llm_log_data') and crawl_result.llm_log_data:
                 output_data["llm_log_data"] = crawl_result.llm_log_data
                 logger.debug(f"LLM log data included for {crawl_result.url}")

             # You might also want to yield intermediate status updates for individual pages during deep crawls
             # if the client supports streaming those statuses.

             yield json.dumps(output_data)

        end_time = time.time() # End timing
        duration = end_time - start_time
        yield json.dumps({"type": "status", "status": "completed", "message": f"Crawl completed in {duration:.2f} seconds.", "duration": duration})

    except Crawl4aiClientError as e:
        logger.error(f"Crawl4AI client error: {e}", exc_info=True)
        yield json.dumps({"type": "error", "message": f"Crawl4AI service client error: {e}"})
    except Exception as e:
        logger.error(f"An unexpected error occurred during crawl: {e}", exc_info=True)
        yield json.dumps({"type": "error", "message": f"An unexpected error occurred: {e}"})
    finally:
        # Close the client connection if necessary (depends on the client implementation)
        if crawl4ai_client:
            try:
                await crawl4ai_client.close()
                logger.info("Crawl4AI client connection closed.")
            except Exception as e:
                logger.error(f"Error closing Crawl4AI client: {e}", exc_info=True)
