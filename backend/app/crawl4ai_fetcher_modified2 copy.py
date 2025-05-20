# -*- coding: utf-8 -*-
"""
Module to handle content fetching using the crawl4ai library.
"""

import logging
import asyncio
import json
import os # Added for environment variables
import time # Added for timing
from typing import Dict, Any, AsyncGenerator, List, Optional, Tuple, Union, Pattern
from datetime import datetime, timezone # Added for timestamps

from crawl4ai import (
    AsyncWebCrawler,
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
from crawl4ai.content_filter_strategy import PruningContentFilter # Added for advanced MD generator
from crawl4ai.models import CrawlResultContainer # Added to handle new result type
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from crawl4ai.deep_crawling.scorers import URLScorer, KeywordRelevanceScorer

# --- Logging Configuration ---
logger = logging.getLogger(__name__)

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
    Async generator for fetching content using crawl4ai, yielding SSE events.
    Maps UI parameters from docs/fetch_page_enhancement_plan.md to crawl4ai config objects.
    Includes comprehensive LLM call logging and structured error reporting.
    """
    logger.info(f"crawl4ai_fetcher called for URL: {url}")
    logger.info(f"crawl4ai_fetcher received original_request_params: {original_request_params}") # DIAGNOSTIC
    logger.debug(f"Original request parameters for crawl4ai: {original_request_params}")

    params = original_request_params
    llm_log_data: Dict[str, Any] = {} # Initialize for potential LLM logging

    try:
        yield json.dumps({"type": "status", "status": "initializing", "message": "Initializing crawl4ai..."})

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
        browser_config = BrowserConfig(**final_browser_config_args)
        logger.info(f"Final browser_config_args for BrowserConfig(): {final_browser_config_args}") # DIAGNOSTIC
        logger.debug(f"BrowserConfig: {final_browser_config_args}") # Log the args passed

        # --- LLMConfig Population (Optional) ---
        llm_config = None
        # Check if any LLM-related parameters are present
        if params.get("llm_provider_model") or params.get("llm_api_token") or params.get("llm_base_url"):
            llm_config_args = {
                "provider": params.get("llm_provider_model"), # UI: llm_provider_model
                "api_token": params.get("llm_api_token"),    # UI: llm_api_token
                "base_url": params.get("llm_base_url"),      # UI: llm_base_url
            }
            # Filter out None values for optional parameters
            final_llm_config_args = {k: v for k, v in llm_config_args.items() if v is not None}
            if final_llm_config_args.get("provider"): # Provider is key
                 llm_config = LLMConfig(**final_llm_config_args)
            logger.debug(f"LLMConfig: {final_llm_config_args if llm_config else None}") # Log the args passed

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
        if not final_deep_crawl_dict:
            logger.info("deep_crawl_config JSON blob not used or invalid. Attempting to construct from individual parameters.")
            
            # Parameter names here match those potentially sent by tests or UI forms
            # (e.g., deep_crawl_strategy_name, deep_crawl_max_depth)
            strategy_from_individual = params.get("deep_crawl_strategy_name") or params.get("strategy") # Fallback for "strategy" key

            if strategy_from_individual and isinstance(strategy_from_individual, str) and strategy_from_individual.strip():
                individual_params_for_strategy_dict = {}
                
                # Max Depth
                max_depth_val = params.get("deep_crawl_max_depth")
                if max_depth_val is not None: individual_params_for_strategy_dict["max_depth"] = max_depth_val
                
                # Max Pages
                max_pages_val = params.get("deep_crawl_max_pages")
                if max_pages_val is not None: individual_params_for_strategy_dict["max_pages"] = max_pages_val
                
                # Include External
                include_external_val = params.get("deep_crawl_include_external")
                if include_external_val is not None: individual_params_for_strategy_dict["include_external"] = include_external_val
                
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
                        individual_params_for_strategy_dict["scorer_keywords"] = ",".join(scorer_keywords_val) # Convert to CSV string
                    elif isinstance(scorer_keywords_val, str):
                        individual_params_for_strategy_dict["scorer_keywords"] = scorer_keywords_val
                    else:
                        logger.warning(f"deep_crawl_scorer_keywords was an unexpected type: {type(scorer_keywords_val)}")

                # Scorer Weight
                scorer_weight_val = params.get("deep_crawl_scorer_weight")
                if scorer_weight_val is not None: individual_params_for_strategy_dict["scorer_weight"] = scorer_weight_val

                final_deep_crawl_dict = {
                    "strategy": strategy_from_individual,
                    "params": individual_params_for_strategy_dict
                }
                logger.info(f"Constructed deep_crawl_config from individual params: {final_deep_crawl_dict}")
            else:
                logger.info("No 'deep_crawl_strategy_name' (or 'strategy') found in individual parameters. No deep crawl strategy will be configured from individual params.")
                # final_deep_crawl_dict remains {}

        # Ensure final_deep_crawl_dict is a dict, even if all attempts failed
        if not isinstance(final_deep_crawl_dict, dict):
            logger.error(f"Internal error: final_deep_crawl_dict ended up as non-dict: {type(final_deep_crawl_dict)}. Resetting to empty.")
            final_deep_crawl_dict = {}
            
        # Use the consolidated configuration
        strategy_type = final_deep_crawl_dict.get("strategy")
        strategy_params_ui = final_deep_crawl_dict.get("params", {})
        if not isinstance(strategy_params_ui, dict):
            logger.error(f"deep_crawl_config.params is not a dictionary: {type(strategy_params_ui)}. Defaulting to empty params.")
            strategy_params_ui = {}

        logger.info(f"Received deep_crawl_config: strategy='{strategy_type}', params_keys='{list(strategy_params_ui.keys())}'")

        filter_chain_instance: Optional[FilterChain] = None
        url_scorer_instance: Optional[URLScorer] = None

        # 1. Instantiate FilterChain
        filter_regexes_ui = strategy_params_ui.get("filter_regexes")
        if filter_regexes_ui and isinstance(filter_regexes_ui, list):
            valid_regexes = [regex_str for regex_str in filter_regexes_ui if isinstance(regex_str, str) and regex_str.strip()]
            if valid_regexes:
                try:
                    url_pattern_filter = URLPatternFilter(patterns=valid_regexes)
                    filter_chain_instance = FilterChain(filters=[url_pattern_filter])
                    logger.info(f"Created FilterChain with URLPatternFilter using regexes: {valid_regexes}")
                except Exception as e_filter:
                    logger.error(f"Error creating FilterChain or URLPatternFilter: {e_filter}", exc_info=True)
            elif filter_regexes_ui:
                 logger.info("filter_regexes provided but list was empty after filtering or contained non-string/empty items.")
        elif filter_regexes_ui is not None:
             logger.warning(f"filter_regexes provided but was not a list: {type(filter_regexes_ui)}. Skipping FilterChain creation.")

        # 2. Instantiate URLScorer (conditionally)
        scorer_type_ui = strategy_params_ui.get("url_scorer_type")
        if scorer_type_ui == "KeywordRelevanceScorer":
            scorer_keywords_str_ui = strategy_params_ui.get("scorer_keywords")
            if scorer_keywords_str_ui and isinstance(scorer_keywords_str_ui, str):
                keyword_list = to_list_str(scorer_keywords_str_ui)
                scorer_weight_ui = strategy_params_ui.get("scorer_weight") # Added for weight
                
                if keyword_list:
                    scorer_args = {"keywords": keyword_list}
                    if scorer_weight_ui is not None:
                        weight_val = to_float(scorer_weight_ui)
                        if weight_val is not None:
                            scorer_args["weight"] = weight_val
                        else:
                            logger.warning(f"KeywordRelevanceScorer: scorer_weight '{scorer_weight_ui}' is invalid. Using default weight.")
                    
                    try:
                        url_scorer_instance = KeywordRelevanceScorer(**scorer_args)
                        logger.info(f"Created KeywordRelevanceScorer with args: {scorer_args}")
                    except Exception as e_scorer:
                        logger.error(f"Error creating KeywordRelevanceScorer with args {scorer_args}: {e_scorer}", exc_info=True)
                elif scorer_keywords_str_ui.strip(): # Check if original string was non-empty before parsing
                    logger.warning("KeywordRelevanceScorer selected, but scorer_keywords was empty after parsing (e.g. only delimiters).")
            elif scorer_keywords_str_ui is not None: # scorer_keywords_str_ui exists but is not a string
                logger.warning(f"KeywordRelevanceScorer selected, but scorer_keywords was not a string: {type(scorer_keywords_str_ui)}.")
            # If scorer_keywords_str_ui is None, it means "scorer_keywords" was not in strategy_params_ui, which is fine if not using KeywordRelevanceScorer
        elif scorer_type_ui and isinstance(scorer_type_ui, str) and scorer_type_ui.strip(): # A scorer type was given, but it's not "KeywordRelevanceScorer"
            logger.warning(f"Unsupported url_scorer_type: '{scorer_type_ui}'. No scorer will be instantiated.")

        # 3. Instantiate Selected Deep Crawl Strategy
        if strategy_type and isinstance(strategy_type, str) and strategy_type.lower().strip() not in ("none", "default", "none / default", ""):
            strategy_constructor_args = {}
            
            raw_max_depth = strategy_params_ui.get("max_depth")
            max_depth_val = to_int(raw_max_depth)
            if max_depth_val is not None:
                strategy_constructor_args["max_depth"] = max(0, max_depth_val)
            
            raw_max_pages = strategy_params_ui.get("max_pages")
            max_pages_val = to_int(raw_max_pages)
            if max_pages_val is not None:
                strategy_constructor_args["max_pages"] = max(1, max_pages_val)

            raw_include_external = strategy_params_ui.get("include_external")
            if raw_include_external is not None:
                 strategy_constructor_args["include_external"] = to_bool(raw_include_external)

            if filter_chain_instance:
                strategy_constructor_args["filter_chain"] = filter_chain_instance
            
            if url_scorer_instance:
                strategy_constructor_args["url_scorer"] = url_scorer_instance

            try:
                if strategy_type == "BFSDeepCrawlStrategy" or strategy_type == "DFSDeepCrawlStrategy":
                    raw_score_threshold = strategy_params_ui.get("score_threshold")
                    score_threshold_val = to_float(raw_score_threshold)
                    if score_threshold_val is not None:
                        strategy_constructor_args["score_threshold"] = score_threshold_val
                    
                    if strategy_type == "BFSDeepCrawlStrategy":
                        deep_crawl_strategy_instance = BFSDeepCrawlStrategy(**strategy_constructor_args)
                    else:
                        deep_crawl_strategy_instance = DFSDeepCrawlStrategy(**strategy_constructor_args)
                    logger.info(f"Instantiated {strategy_type} with effective params: {strategy_constructor_args}")

                elif strategy_type == "BestFirstCrawlingStrategy":
                    if not url_scorer_instance:
                        logger.warning(
                            "BestFirstCrawlingStrategy selected, but no URLScorer was configured or "
                            "successfully instantiated. This strategy typically requires a scorer to be effective."
                        )
                    deep_crawl_strategy_instance = BestFirstCrawlingStrategy(**strategy_constructor_args)
                    logger.info(f"Instantiated BestFirstCrawlingStrategy with effective params: {strategy_constructor_args}")
                
                else:
                    logger.warning(f"Unknown or unhandled deep_crawl_config.strategy: '{strategy_type}'. No deep crawl strategy will be applied.")
            
            except Exception as e_strat:
                logger.error(f"Error instantiating deep crawl strategy '{strategy_type}' with args {strategy_constructor_args}: {e_strat}", exc_info=True)
                deep_crawl_strategy_instance = None

        elif not strategy_type or not isinstance(strategy_type, str) or strategy_type.lower().strip() in ("none", "default", "none / default", ""):
            logger.info("No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).")
        

        # --- Extraction Strategy Population ---
        extraction_strategy_instance = None
        raw_extraction_config = params.get("extraction_config")

        parsed_extraction_config = {}
        if isinstance(raw_extraction_config, str):
            try:
                parsed_extraction_config = json.loads(raw_extraction_config)
                if not isinstance(parsed_extraction_config, dict):
                    logger.error(
                        f"Parsed extraction_config string did not result in a dictionary. "
                        f"Type: {type(parsed_extraction_config)}. Value: '{str(parsed_extraction_config)[:200]}'. "
                        "Proceeding with empty extraction config."
                    )
                    parsed_extraction_config = {} # Fallback
            except json.JSONDecodeError as e_json_main:
                logger.error(
                    f"Failed to parse extraction_config string: '{str(raw_extraction_config)[:200]}'. Error: {e_json_main}. "
                    "Proceeding with empty extraction config."
                )
                # parsed_extraction_config remains {}
        elif isinstance(raw_extraction_config, dict):
            parsed_extraction_config = raw_extraction_config
        elif raw_extraction_config is not None: # It's not str, not dict, but not None
            logger.error(
                f"extraction_config is of an unexpected type: {type(raw_extraction_config)}. "
                f"Value: '{str(raw_extraction_config)[:200]}'. Proceeding with empty extraction config."
            )
            # parsed_extraction_config remains {}
        # If raw_extraction_config was None, parsed_extraction_config remains {}

        strategy_name = parsed_extraction_config.get("strategy")
        raw_strategy_params = parsed_extraction_config.get("params")
        
        strategy_params_dict = {}
        if isinstance(raw_strategy_params, dict):
            strategy_params_dict = raw_strategy_params
        elif raw_strategy_params is not None: # It's not a dict, but it's not None (e.g. string, list)
            logger.warning(
                f"Extraction strategy '{strategy_name}' received 'params' that is not a dictionary "
                f"(type: {type(raw_strategy_params)}). Value: '{str(raw_strategy_params)[:100]}'. "
                "Using empty params for this strategy."
            )
            # strategy_params_dict remains {}
        # If raw_strategy_params is None (i.e., "params" key missing or parsed_extraction_config is empty),
        # or if it was not a dict and not None, strategy_params_dict remains {}

        logger.info(f"Processed extraction_config: strategy='{strategy_name}', params_keys='{list(strategy_params_dict.keys())}'")

        if strategy_name == "LLMExtractionStrategy":
            llm_log_data = { # Initialize log data for this LLM call
                "url_crawled": url,
                "request_timestamp": datetime.now(timezone.utc).isoformat(),
                "llm_call_type": "extraction", # Assuming this is for extraction
                "strategy_type": "LLMExtractionStrategy",
            }
            try:
                # Determine effective llm_provider_model
                requested_provider_model = strategy_params_dict.get("llm_provider_model")
                effective_provider_model = requested_provider_model if requested_provider_model else os.environ.get("DEFAULT_LLM_PROVIDER_MODEL", "groq/llama3-8b-8192")
                llm_log_data["llm_provider"] = effective_provider_model

                if not effective_provider_model:
                    logger.error("LLMExtractionStrategy: Critical - No LLM provider model could be determined (neither provided nor default). Cannot proceed.")
                    llm_log_data["call_successful"] = False
                    llm_log_data["error_type"] = "ConfigurationError"
                    llm_log_data["error_message_detail"] = "LLM provider model not configured or default not set."
                    raise ValueError(llm_log_data["error_message_detail"])
                elif requested_provider_model and (not isinstance(effective_provider_model, str) or '/' not in effective_provider_model or len(effective_provider_model.strip()) == 0):
                    logger.error(f"LLMExtractionStrategy: Invalid llm_provider_model format: '{effective_provider_model}'. Expected 'provider/model_name'.")
                    llm_log_data["call_successful"] = False
                    llm_log_data["error_type"] = "ConfigurationError"
                    llm_log_data["error_message_detail"] = f"Invalid llm_provider_model format: '{effective_provider_model}'. Must be a non-empty string like 'provider/model_name'."
                    raise ValueError(llm_log_data["error_message_detail"])

                # Determine effective llm_instruction
                requested_instruction = strategy_params_dict.get("llm_instruction")
                effective_instruction = requested_instruction
                
                raw_extraction_type_for_default_instr = strategy_params_dict.get("llm_extraction_type")
                temp_user_intended_extraction_type = "text"
                
                if raw_extraction_type_for_default_instr is None:
                    temp_user_intended_extraction_type = "text"
                elif isinstance(raw_extraction_type_for_default_instr, str) and raw_extraction_type_for_default_instr.strip():
                    temp_user_intended_extraction_type = raw_extraction_type_for_default_instr.strip().lower()
                    valid_extraction_types = ["json", "schema", "text", "markdown"]
                    if temp_user_intended_extraction_type not in valid_extraction_types:
                        llm_log_data["call_successful"] = False
                        llm_log_data["error_type"] = "ConfigurationError"
                        llm_log_data["error_message_detail"] = f"Invalid llm_extraction_type '{temp_user_intended_extraction_type}'. Must be one of {valid_extraction_types}."
                        logger.error(f"LLMExtractionStrategy: {llm_log_data['error_message_detail']}")
                        raise ValueError(llm_log_data["error_message_detail"])
                elif raw_extraction_type_for_default_instr is not None: # Provided, but not a string or empty after strip
                    llm_log_data["call_successful"] = False
                    llm_log_data["error_type"] = "ConfigurationError"
                    llm_log_data["error_message_detail"] = f"Invalid llm_extraction_type format: '{raw_extraction_type_for_default_instr}'. Must be a non-empty string."
                    logger.error(f"LLMExtractionStrategy: {llm_log_data['error_message_detail']}")
                    raise ValueError(llm_log_data["error_message_detail"])
                    # temp_user_intended_extraction_type = "text" # This line is now unreachable due to raise
                    # logger.warning(f"LLMExtractionStrategy: llm_extraction_type ('{raw_extraction_type_for_default_instr}') is not valid. Defaulting to 'text'.")
                
                llm_log_data["user_intended_extraction_type"] = temp_user_intended_extraction_type

                if not effective_instruction:
                    if temp_user_intended_extraction_type == "markdown":
                        effective_instruction = os.environ.get("DEFAULT_LLM_INSTRUCTION_MARKDOWN", "Convert the main content of this page to well-formatted markdown.")
                    elif temp_user_intended_extraction_type == "json":
                        effective_instruction = os.environ.get("DEFAULT_LLM_INSTRUCTION_JSON", "Extract key information from this document into a JSON structure based on the provided schema if any, or infer a suitable JSON structure.")
                    else:
                        effective_instruction = os.environ.get("DEFAULT_LLM_INSTRUCTION_TEXT", "Extract the main content from this document as plain text.")
                llm_log_data["instruction_prompt"] = (effective_instruction or "")[:500] + ("..." if len(effective_instruction or "") > 500 else "")


                llm_api_token_from_request = strategy_params_dict.get("llm_api_token")
                llm_base_url_from_request = strategy_params_dict.get("llm_base_url")
                
                strategy_llm_config_args = {"provider": effective_provider_model}
                if llm_api_token_from_request and llm_api_token_from_request.strip():
                    strategy_llm_config_args["api_token"] = llm_api_token_from_request
                if llm_base_url_from_request:
                    strategy_llm_config_args["base_url"] = llm_base_url_from_request
                
                final_strategy_llm_config_args = {k: v for k, v in strategy_llm_config_args.items() if v is not None}
                llm_log_data["llm_api_token_provided"] = bool(final_strategy_llm_config_args.get("api_token"))
                llm_log_data["llm_base_url"] = final_strategy_llm_config_args.get("base_url")

                llm_config_for_strategy = LLMConfig(**final_strategy_llm_config_args)
                
                llm_strategy_kwargs: Dict[str, Any] = {}
                # Mapping user intended type to strategy's extraction_type
                if temp_user_intended_extraction_type == "json" or temp_user_intended_extraction_type == "schema":
                    llm_strategy_kwargs["extraction_type"] = "schema"
                else: # text, markdown, or other defaults to block
                    llm_strategy_kwargs["extraction_type"] = "block"
                llm_log_data["extraction_type_setting"] = llm_strategy_kwargs["extraction_type"]

                parsed_llm_schema = to_json_dict(strategy_params_dict.get("llm_json_schema"))
                llm_log_data["schema_definition_provided"] = False
                if llm_strategy_kwargs["extraction_type"] == "schema":
                    if parsed_llm_schema is not None:
                        llm_strategy_kwargs["schema"] = parsed_llm_schema
                        llm_log_data["schema_definition_provided"] = True
                    else:
                        llm_log_data["call_successful"] = False
                        llm_log_data["error_type"] = "ConfigurationError"
                        llm_log_data["error_message_detail"] = "LLMExtractionStrategy: type is 'schema' but 'llm_json_schema' was not provided or was invalid."
                        logger.error(f"LLMExtractionStrategy: {llm_log_data['error_message_detail']}")
                        raise ValueError(llm_log_data["error_message_detail"])
                
                llm_apply_chunking_raw = strategy_params_dict.get("llm_apply_chunking")
                llm_strategy_kwargs["apply_chunking"] = to_bool(llm_apply_chunking_raw) if llm_apply_chunking_raw is not None else True
                llm_log_data["chunking_applied"] = llm_strategy_kwargs["apply_chunking"]

                llm_chunk_token_threshold_raw = strategy_params_dict.get("llm_chunk_token_threshold")
                llm_strategy_kwargs["chunk_token_threshold"] = to_int(llm_chunk_token_threshold_raw) if llm_chunk_token_threshold_raw is not None else 3000
                if not (isinstance(llm_strategy_kwargs["chunk_token_threshold"], int) and llm_strategy_kwargs["chunk_token_threshold"] > 0):
                    llm_strategy_kwargs["chunk_token_threshold"] = 3000 # Fallback
                llm_log_data["chunk_token_threshold_setting"] = llm_strategy_kwargs["chunk_token_threshold"]
                
                llm_overlap_rate_raw = strategy_params_dict.get("llm_overlap_rate")
                parsed_overlap_rate = to_float(llm_overlap_rate_raw)
                if parsed_overlap_rate is not None: llm_strategy_kwargs["overlap_rate"] = parsed_overlap_rate
                llm_log_data["chunk_overlap_rate_setting"] = llm_strategy_kwargs.get("overlap_rate")

                llm_input_format_raw = strategy_params_dict.get("llm_input_format")
                valid_input_formats = ["markdown", "fit_markdown", "html"]
                if isinstance(llm_input_format_raw, str) and llm_input_format_raw.strip() in valid_input_formats:
                    llm_strategy_kwargs["input_format"] = llm_input_format_raw.strip()
                llm_log_data["input_content_format"] = llm_strategy_kwargs.get("input_format")

                # For llm_extra_args, we expect a dict. If user provides a JSON string, parse it.
                llm_extra_args_raw = strategy_params_dict.get("llm_extra_args")
                parsed_llm_extra_args = to_json_dict(llm_extra_args_raw)
                if parsed_llm_extra_args:
                    llm_strategy_kwargs["extra_args"] = parsed_llm_extra_args
                llm_log_data["llm_extra_args"] = llm_strategy_kwargs.get("extra_args")
                
                # context_window_limit and max_tokens are part of extra_args in LiteLLM,
                # but LLMExtractionStrategy might have direct params or handle them via extra_args.
                # The doc shows them as direct params for LLMExtractionStrategy.
                context_window_raw = strategy_params_dict.get("llm_context_window_limit_override")
                if context_window_raw is not None:
                    context_window_val = to_int(context_window_raw)
                    if context_window_val is None or context_window_val <= 0:
                        llm_log_data["call_successful"] = False
                        llm_log_data["error_type"] = "ConfigurationError"
                        llm_log_data["error_message_detail"] = f"Invalid llm_context_window_limit_override: '{context_window_raw}'. Must be a positive integer."
                        logger.error(f"LLMExtractionStrategy: {llm_log_data['error_message_detail']}")
                        raise ValueError(llm_log_data["error_message_detail"])
                    llm_strategy_kwargs["context_window_limit"] = context_window_val
                llm_log_data["context_window_limit_override_setting"] = llm_strategy_kwargs.get("context_window_limit")
                
                max_tokens_raw = strategy_params_dict.get("llm_max_tokens_override")
                if max_tokens_raw is not None:
                    max_tokens_val = to_int(max_tokens_raw)
                    if max_tokens_val is None or max_tokens_val <= 0:
                        llm_log_data["call_successful"] = False
                        llm_log_data["error_type"] = "ConfigurationError"
                        llm_log_data["error_message_detail"] = f"Invalid llm_max_tokens_override: '{max_tokens_raw}'. Must be a positive integer."
                        logger.error(f"LLMExtractionStrategy: {llm_log_data['error_message_detail']}")
                        raise ValueError(llm_log_data["error_message_detail"])
                    llm_strategy_kwargs["max_tokens"] = max_tokens_val
                llm_log_data["max_tokens_override_setting"] = llm_strategy_kwargs.get("max_tokens")

                extraction_strategy_instance = LLMExtractionStrategy(
                    instruction=effective_instruction,
                    llm_config=llm_config_for_strategy,
                    **llm_strategy_kwargs
                )
                logger.info(f"Instantiated LLMExtractionStrategy. LLMConfig: {final_strategy_llm_config_args}, Instruction: '{str(effective_instruction)[:70]}...', Advanced Args: {llm_strategy_kwargs}")

            except ValueError as ve: # Catch config errors specifically
                logger.error(f"Configuration error for LLMExtractionStrategy: {ve}", exc_info=True)
                if "llm_log_data" not in locals(): llm_log_data = {} # Ensure it exists
                llm_log_data["call_successful"] = False
                llm_log_data["error_type"] = llm_log_data.get("error_type", "ConfigurationError")
                llm_log_data["error_message_detail"] = llm_log_data.get("error_message_detail", str(ve))
                
                # Yield llm_log_data event
                yield json.dumps({"type": "llm_log_event", "data": llm_log_data})
                
                error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
                yield json.dumps({
                    "type": "error",
                    "status": "error",
                    "message": "LLM strategy configuration error.",
                    "llm_error": { # This is the structured LLM error for the client
                        "error_code": "LLM_CONFIGURATION_ERROR",
                        "message": "Error configuring LLM extraction strategy.",
                        "llm_error_type": llm_log_data.get("error_type", "ConfigurationError"),
                        "details": error_payload_details # Include all collected log data
                    }
                })
                return

            except Exception as e_llm_strat_setup:
                logger.error(f"Unexpected error setting up LLMExtractionStrategy: {e_llm_strat_setup}", exc_info=True)
                if "llm_log_data" not in locals(): llm_log_data = {} # Should be defined, but safeguard
                llm_log_data["call_successful"] = False
                llm_log_data["error_type"] = "StrategySetupError"
                llm_log_data["error_message_detail"] = str(e_llm_strat_setup)

                yield json.dumps({"type": "llm_log_event", "data": llm_log_data})
                
                error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
                yield json.dumps({
                    "type": "error",
                    "status": "error",
                    "message": "Failed to initialize LLM extraction strategy.",
                     "llm_error": {
                        "error_code": "LLM_STRATEGY_SETUP_FAILED",
                        "message": "Failed to initialize LLM extraction strategy.",
                        "llm_error_type": "StrategySetupError",
                        "details": error_payload_details
                    }
                })
                return
        elif strategy_name == "JsonCssExtractionStrategy":
            schema_value = strategy_params_dict.get("schema")
            schema_dict_to_use = None

            if schema_value is None:
                logger.warning("JsonCssExtractionStrategy selected, but 'schema' is missing in params. Skipping strategy.")
            elif isinstance(schema_value, dict):
                schema_dict_to_use = schema_value
                logger.info("JsonCssExtractionStrategy: 'schema' parameter provided as a pre-parsed dictionary.")
            elif isinstance(schema_value, str):
                try:
                    schema_dict_to_use = json.loads(schema_value)
                    logger.info("JsonCssExtractionStrategy: Successfully parsed 'schema' string parameter.")
                except json.JSONDecodeError as e_json_parse:
                    logger.error(
                        f"JsonCssExtractionStrategy: Failed to parse 'schema' string. Error: {e_json_parse}. "
                        f"Schema string (first 100 chars): '{schema_value[:100]}'. Skipping strategy."
                    )
            else: # schema_value is not None, not dict, not str
                logger.error(
                    f"JsonCssExtractionStrategy: 'schema' parameter is neither a string nor a dictionary "
                    f"(type: {type(schema_value)}). Value: '{str(schema_value)[:100]}'. Skipping strategy."
                )

            if schema_dict_to_use:
                try:
                    extraction_strategy_instance = JsonCssExtractionStrategy(schema=schema_dict_to_use)
                    logger.info("Successfully instantiated JsonCssExtractionStrategy.")
                except Exception as e_json_strat_init:
                     logger.error(f"Error instantiating JsonCssExtractionStrategy: {e_json_strat_init}", exc_info=True)
                     # extraction_strategy_instance will remain None if it was, or be reset if error occurs here
            # If schema_dict_to_use is None, extraction_strategy_instance remains None

        elif strategy_name == "CosineStrategy":
            logger.debug(f"Attempting to instantiate CosineStrategy for strategy_name: {strategy_name}")
            try:
                temp_cosine_instance = CosineStrategy()
                extraction_strategy_instance = temp_cosine_instance
                logger.info(f"Successfully instantiated CosineStrategy. Type: {type(extraction_strategy_instance)}, Instance: {extraction_strategy_instance}")
            except Exception as e_cosine_strat:
                logger.error(f"Error instantiating CosineStrategy: {e_cosine_strat}", exc_info=True)
                # extraction_strategy_instance remains None if it was, or if the assignment above failed before exception.
        
        elif strategy_name is None or not strategy_name or strategy_name.lower() in ("none", "default", "none / default"):
            logger.info("No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.")
        else:
            logger.warning(f"Unknown extraction strategy: '{strategy_name}'. Using crawl4ai default behavior.")


        # --- CrawlerRunConfig Population ---
        # deep_crawl_strategy_instance will be passed directly to arun, not as part of CrawlerRunConfig
        crawler_run_config_args = {
            "extraction_strategy": extraction_strategy_instance, # Added extraction strategy
            # "llm_config": llm_config, # Removed: llm_config is not a direct param of CrawlerRunConfig
 
            # Browser & Navigation Settings
            "wait_until": params.get("page_load_wait_condition"), # Matches main.py Query param
            "page_timeout": to_int(params.get("page_load_timeout_ms")), # Matches main.py Query param 'page_load_timeout_ms'
            "wait_for": params.get("wait_for_element_js_condition"), # Matches main.py Query param

            # Content Extraction & Processing
            "target_elements": to_list_str(params.get("target_selector")), # Matches main.py Query param 'target_selector'
            "excluded_selector": params.get("excluded_selector"), # Matches main.py Query param 'excluded_selector'
            "excluded_tags": to_list_str(params.get("excluded_tags")), # Matches main.py Query param
            "only_text": to_bool(params.get("extract_only_text_content")), # Matches main.py Query param
            "process_iframes": to_bool(params.get("process_iframes_content")), # Matches main.py Query param
            "word_count_threshold": to_int(params.get("word_count_threshold")), # Matches main.py Query param
            "remove_forms": to_bool(params.get("remove_forms")), # Matches main.py Query param
            "keep_data_attributes": to_bool(params.get("keep_data_attributes")), # Matches main.py Query param

            # Page Interaction & Automation
            "js_code": params.get("execute_javascript_on_page_load"), # Matches main.py Query param
            "scan_full_page": to_bool(params.get("scan_full_page_auto_scroll")), # Matches main.py Query param
            "scroll_delay": to_float(params.get("scroll_delay_seconds")), # Matches main.py Query param
            "remove_overlay_elements": to_bool(params.get("attempt_remove_overlay_elements")), # Matches main.py Query param
            "simulate_user": to_bool(params.get("simulate_user_behavior")), # Matches main.py Query param
            "magic": to_bool(params.get("enable_magic_handling")), # Matches main.py Query param
            "override_navigator": to_bool(params.get("override_navigator_properties")), # Matches main.py Query param

            # Caching
            "cache_mode": params.get("cache_mode"), # Matches main.py Query param

            # Media Handling
            "screenshot": to_bool(params.get("capture_screenshot_base64")), # Matches main.py Query param
            "pdf": to_bool(params.get("generate_pdf_of_page")), # Matches main.py Query param 'generate_pdf'
            "capture_mhtml": to_bool(params.get("capture_mhtml_snapshot")), # Matches main.py Query param
            "exclude_external_images": to_bool(params.get("exclude_external_images")), # Matches main.py Query param
            "image_description_min_word_threshold": to_int(params.get("image_alt_text_min_word_count")), # Matches main.py Query param
            "image_score_threshold": to_int(params.get("image_relevance_score_threshold")), # Matches main.py Query param

            # Link & Domain Filtering
            "exclude_external_links": to_bool(params.get("exclude_external_links")), # Matches main.py Query param
            "exclude_social_media_links": to_bool(params.get("exclude_social_media_links")), # Matches main.py Query param
            "exclude_domains": to_list_str(params.get("custom_excluded_domains")), # Matches main.py Query param

            # Compliance
            "check_robots_txt": to_bool(params.get("respect_robots_txt")), # Matches main.py Query param 'respect_robots_txt'

            # Debugging & Logging
            "verbose": to_bool(params.get("verbose_logging")), # Matches main.py Query param
            "log_console": to_bool(params.get("log_page_console_output")), # Matches main.py Query param

            # Expert Options
            "session_id": params.get("crawl_session_id"), # Matches main.py Query param
            "css_selector": params.get("crawl_css_selector"), # Matches main.py Query param
        }

        # --- Markdown Generator Population ---
        # The query parameter name in main.py is 'crawl4ai_markdown_generator'
        markdown_generator_name_from_params = params.get("crawl4ai_markdown_generator")
        logger.info(f"Received markdown_generator_name_from_params: '{markdown_generator_name_from_params}'")

        markdown_generator_instance_for_config = None # This will be passed to CrawlerRunConfig

        if markdown_generator_name_from_params == "Default":
            logger.info("Processing 'Default' markdown generator with potential advanced options.")
            dmg_kwargs: Dict[str, Any] = {}

            # 1. Parse markdown_generator_options
            raw_md_options = params.get("markdown_generator_options")
            parsed_md_options = to_json_dict(raw_md_options)
            if parsed_md_options is not None:
                dmg_kwargs.update(parsed_md_options) # Directly update, DefaultMarkdownGenerator handles specific options
                logger.info(f"Applied markdown_generator_options: {parsed_md_options}")
            elif raw_md_options is not None: # Parsing failed but input was provided
                logger.warning(f"Failed to parse markdown_generator_options: '{str(raw_md_options)[:100]}'. Options will not be applied.")

            # 2. Parse markdown_content_source
            raw_md_content_source = params.get("markdown_content_source")
            valid_content_sources = ["raw_html", "cleaned_html", "fit_html"]
            if raw_md_content_source is not None:
                if isinstance(raw_md_content_source, str) and raw_md_content_source in valid_content_sources:
                    dmg_kwargs["content_source"] = raw_md_content_source
                    logger.info(f"Applied markdown_content_source: '{raw_md_content_source}'")
                else:
                    logger.warning(
                        f"Invalid markdown_content_source: '{raw_md_content_source}'. "
                        f"Must be one of {valid_content_sources}. Source will not be applied."
                    )
            
            # 3. Parse markdown_content_filter_config
            raw_md_filter_config = params.get("markdown_content_filter_config")
            parsed_md_filter_config = to_json_dict(raw_md_filter_config)
            
            if parsed_md_filter_config is not None:
                filter_type = parsed_md_filter_config.get("type")
                filter_params_config = parsed_md_filter_config.get("params", {})
                if not isinstance(filter_params_config, dict):
                    logger.warning(f"markdown_content_filter_config 'params' is not a dict: {type(filter_params_config)}. Using empty params for filter.")
                    filter_params_config = {}

                if filter_type == "PruningContentFilter":
                    pruning_filter_args = {}
                    # Parse PruningContentFilter specific params
                    threshold_raw = filter_params_config.get("threshold")
                    if threshold_raw is not None:
                        threshold_val = to_int(threshold_raw)
                        if threshold_val is not None:
                            pruning_filter_args["threshold"] = threshold_val
                        else:
                            logger.warning(f"PruningContentFilter: Invalid 'threshold' value: {threshold_raw}. Not applying.")
                    
                    min_length_raw = filter_params_config.get("min_length")
                    if min_length_raw is not None:
                        min_length_val = to_int(min_length_raw)
                        if min_length_val is not None:
                            pruning_filter_args["min_length"] = min_length_val
                        else:
                            logger.warning(f"PruningContentFilter: Invalid 'min_length' value: {min_length_raw}. Not applying.")

                    target_selector_raw = filter_params_config.get("target_selector")
                    if target_selector_raw is not None:
                        if isinstance(target_selector_raw, str):
                            pruning_filter_args["target_selector"] = target_selector_raw
                        else:
                            logger.warning(f"PruningContentFilter: 'target_selector' must be a string, got {type(target_selector_raw)}. Not applying.")
                    
                    try:
                        content_filter_instance = PruningContentFilter(**pruning_filter_args)
                        dmg_kwargs["content_filter"] = content_filter_instance
                        logger.info(f"Instantiated PruningContentFilter with args: {pruning_filter_args}")
                    except Exception as e_pruning_filter:
                        logger.error(f"Error instantiating PruningContentFilter with args {pruning_filter_args}: {e_pruning_filter}", exc_info=True)
                
                elif filter_type: # A type was specified, but it's not known/handled
                    logger.warning(f"Unknown markdown_content_filter_config type: '{filter_type}'. Filter will not be applied.")
                # If filter_type is None/empty, no specific filter config was intended.

            elif raw_md_filter_config is not None: # Parsing failed but input was provided
                logger.warning(f"Failed to parse markdown_content_filter_config: '{str(raw_md_filter_config)[:100]}'. Filter will not be applied.")

            # Instantiate DefaultMarkdownGenerator with collected kwargs
            try:
                markdown_generator_instance_for_config = DefaultMarkdownGenerator(**dmg_kwargs)
                logger.info(f"Instantiated DefaultMarkdownGenerator with advanced options: {dmg_kwargs}")
            except Exception as e_md_gen_adv:
                logger.error(f"Error instantiating DefaultMarkdownGenerator with advanced options {dmg_kwargs}: {e_md_gen_adv}", exc_info=True)
                markdown_generator_instance_for_config = None # Fallback to None

        elif not markdown_generator_name_from_params or not isinstance(markdown_generator_name_from_params, str) or not markdown_generator_name_from_params.strip():
            logger.info("Markdown generator is empty, None, or not specified. Setting to None for CrawlerRunConfig.")
            markdown_generator_instance_for_config = None
        else: # Non-empty, non-"Default" string (i.e., Unknown)
            logger.warning(f"Unknown markdown_generator: '{markdown_generator_name_from_params}'. Setting to None for CrawlerRunConfig.")
            markdown_generator_instance_for_config = None
        
        # Assign the final markdown_generator_instance (or None) to crawler_run_config_args
        crawler_run_config_args["markdown_generator"] = markdown_generator_instance_for_config
            
        # Filter out None values for optional parameters, except for llm_config which can be None
        # and js_code which can be an empty string (which is fine for crawl4ai if it's a string type)
        # and markdown_generator which can also be None
        final_crawler_run_config_args = {
            k: v for k, v in crawler_run_config_args.items()
            if v is not None or (k == "js_code" and isinstance(v, str)) # Removed "llm_config" from condition
        }
        logger.info(f"Intermediate crawler_run_config_args: {crawler_run_config_args}") # DIAGNOSTIC
        crawler_run_config = CrawlerRunConfig(**final_crawler_run_config_args)
        logger.info(f"Final crawler_run_config_args for CrawlerRunConfig(): {final_crawler_run_config_args}") # DIAGNOSTIC
        logger.debug(f"CrawlerRunConfig: {final_crawler_run_config_args}") # Log the args passed

        logger.info(f"Current asyncio event loop policy before AsyncWebCrawler init: {asyncio.get_event_loop_policy().__class__.__name__}")
        async with AsyncWebCrawler(config=browser_config) as crawler:
            logger.info(f"AsyncWebCrawler context entered for URL: {url}") # Added for clarity during testing/debugging
            yield json.dumps({"type": "status", "status": "fetching", "message": f"Fetching content from {url} with crawl4ai..."})
   
            arun_kwargs = {"config": crawler_run_config}
            if deep_crawl_strategy_instance:
                arun_kwargs["deep_crawl_strategy"] = deep_crawl_strategy_instance
   
            llm_call_start_time = 0
            if isinstance(extraction_strategy_instance, LLMExtractionStrategy):
                logger.info(f"LLM Extraction starting for URL: {url}")
                llm_call_start_time = time.time()
   
            raw_result = await crawler.arun(url, **arun_kwargs)
   
            if isinstance(extraction_strategy_instance, LLMExtractionStrategy) and llm_call_start_time > 0:
                llm_call_end_time = time.time()
                llm_log_data["llm_call_duration_ms"] = int((llm_call_end_time - llm_call_start_time) * 1000)
                
                # Populate usage data from strategy instance
                if hasattr(extraction_strategy_instance, 'total_usage') and extraction_strategy_instance.total_usage:
                    usage = extraction_strategy_instance.total_usage
                    llm_log_data["prompt_tokens_total"] = usage.get("prompt_tokens")
                    llm_log_data["completion_tokens_total"] = usage.get("completion_tokens")
                    llm_log_data["total_tokens_used"] = usage.get("total_tokens")
                    llm_log_data["cost"] = usage.get("cost") # LiteLLM might provide this
                
                if hasattr(extraction_strategy_instance, 'usages') and extraction_strategy_instance.usages:
                    llm_log_data["number_of_chunks_processed"] = len(extraction_strategy_instance.usages)
                    # Potentially log per_chunk_usage if needed, but it can be verbose
                    # llm_log_data["per_chunk_usage"] = extraction_strategy_instance.usages

                # Attempt to get response ID (placeholder, might need deeper LiteLLM integration insight)
                # For now, if crawl4ai's LLMExtractionStrategy exposes the raw response object or its ID:
                # llm_log_data["llm_response_id"] = getattr(extraction_strategy_instance, 'last_response_id', None)
                # This is speculative. For now, it will be None.
                llm_log_data["llm_response_id"] = None


            yield json.dumps({"type": "status", "status": "processing", "message": "Processing content fetched by crawl4ai..."})

        result: Optional[CrawlResult] = None
        if isinstance(raw_result, list):
            # ... (rest of existing result handling logic for deep crawl) ...
            if raw_result:
                result = raw_result[0]
                logger.info(f"Deep crawl returned {len(raw_result)} results. Processing the first one.")
            else: # Deep crawl returned empty list
                logger.error(f"crawl4ai deep crawl for URL {url} returned an empty list.")
                # If LLM strategy was used, log its current state
                if isinstance(extraction_strategy_instance, LLMExtractionStrategy):
                    llm_log_data["call_successful"] = False
                    llm_log_data["error_type"] = "NoContentFromDeepCrawl"
                    llm_log_data["error_message_detail"] = "Deep crawl returned no results."
                    yield json.dumps({"type": "llm_log_event", "data": llm_log_data}) # Yield log data
                
                yield json.dumps({"type": "error", "status": "error", "message": "Deep crawl returned no results."})
                return
        elif isinstance(raw_result, CrawlResultContainer):
            result = raw_result
        elif isinstance(raw_result, CrawlResult):
            result = raw_result
        else: # Unexpected result type
            logger.error(f"crawl4ai returned an unexpected result type for URL {url}: {type(raw_result)}")
            if isinstance(extraction_strategy_instance, LLMExtractionStrategy):
                llm_log_data["call_successful"] = False
                llm_log_data["error_type"] = "UnexpectedCrawlResultType"
                llm_log_data["error_message_detail"] = f"Crawl4ai returned an unexpected result type: {type(raw_result)}"
                yield json.dumps({"type": "llm_log_event", "data": llm_log_data}) # Yield log data

            yield json.dumps({"type": "error", "status": "error", "message": "Crawl4ai returned an unexpected result type."})
            return

        # --- LLM Result Processing and Error Handling ---
        llm_extracted_payload_for_sse = {} # This will hold the final LLM output or structured error for SSE

        if isinstance(extraction_strategy_instance, LLMExtractionStrategy):
            llm_log_data["crawl_status_code"] = result.status_code if result else None
            llm_log_data["crawl_session_id"] = result.session_id if result else None

            if result is None or not result.success:
                llm_log_data["call_successful"] = False
                llm_log_data["error_type"] = "CrawlFailure"
                llm_log_data["error_message_detail"] = result.error_message if result else "Crawl failed before LLM or result was None."
                
                error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
                llm_extracted_payload_for_sse = {
                    "error_code": "LLM_PRECONDITION_FAILED_CRAWL",
                    "message": "Crawl operation failed, preventing LLM extraction.",
                    "llm_error_type": llm_log_data["error_type"],
                    "details": error_payload_details
                }
                logger.error(f"LLM Extraction skipped due to crawl failure for {url}: {llm_log_data['error_message_detail']}")
            
            elif result.extracted_content is None:
                llm_log_data["call_successful"] = False
                llm_log_data["error_type"] = "NoContentFromLLM"
                llm_log_data["error_message_detail"] = "LLM extraction resulted in None content."
                llm_log_data["extracted_content_preview"] = None
                
                error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
                llm_extracted_payload_for_sse = {
                    "error_code": "LLM_NO_CONTENT_RETURNED",
                    "message": "LLM extraction returned no content.",
                    "llm_error_type": llm_log_data["error_type"],
                    "details": error_payload_details
                }
                logger.warning(f"LLM extraction for {url} resulted in None content.")

            else: # result.success is True and result.extracted_content is not None
                # Try to parse extracted_content if it's a string (might be JSON)
                parsed_llm_output = result.extracted_content
                if isinstance(result.extracted_content, str):
                    try:
                        parsed_llm_output = json.loads(result.extracted_content)
                    except json.JSONDecodeError:
                        # If not JSON, treat as plain text output. This is successful if type was text/markdown.
                        if llm_log_data.get("user_intended_extraction_type") in ["text", "markdown"]:
                            pass # It's fine, it's text
                        else: # Expected JSON but got non-JSON string
                            llm_log_data["call_successful"] = False
                            llm_log_data["error_type"] = "ParsingError"
                            llm_log_data["error_message_detail"] = "LLM returned non-JSON string when JSON was expected."
                            logger.warning(f"{llm_log_data['error_message_detail']} Output: {result.extracted_content[:100]}")
                
                if isinstance(parsed_llm_output, dict) and parsed_llm_output.get("error"):
                    # LLM itself returned a structured error
                    llm_log_data["call_successful"] = False
                    llm_log_data["error_type"] = parsed_llm_output.get("type", "LLMProviderError") # e.g. APIError
                    llm_log_data["error_message_detail"] = parsed_llm_output.get("message", str(parsed_llm_output))
                    llm_log_data["extracted_content_preview"] = json.dumps(parsed_llm_output) # Log the error structure
                    logger.warning(f"LLM extraction for {url} returned an error structure: {parsed_llm_output}")
                elif not llm_log_data.get("call_successful", True): # Check if already marked as failed (e.g. parsing error above)
                    pass # Error already logged by parsing check
                else: # Successful LLM extraction
                    llm_log_data["call_successful"] = True
                    llm_log_data["error_type"] = None
                    llm_log_data["error_message_detail"] = None
                    if isinstance(parsed_llm_output, (dict, list)):
                        llm_log_data["extracted_content_preview"] = json.dumps(parsed_llm_output)[:500] + "..."
                    else:
                        llm_log_data["extracted_content_preview"] = str(parsed_llm_output)[:500] + "..."
                
                # Prepare SSE payload based on success/failure
                if not llm_log_data["call_successful"]:
                    error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
                    llm_extracted_payload_for_sse = {
                        "error_code": "LLM_EXTRACTION_FAILED",
                        "message": "LLM extraction operation failed or returned an error.",
                        "llm_error_type": llm_log_data["error_type"],
                        "details": error_payload_details
                    }
                else: # Successful extraction, pass the content
                    llm_extracted_payload_for_sse = parsed_llm_output

            # Yield the comprehensive LLM data for DB insertion by the caller
            yield json.dumps({"type": "llm_log_event", "data": llm_log_data})


        elif result is None or not result.success: # General crawl failure, not LLM specific path
            error_message = result.error_message if result else "Crawl4ai reported failure without a specific error message or result object."
            logger.error(f"crawl4ai failed for URL {url}: {error_message}")
            # This is a general error, not an LLM error payload
            yield json.dumps({
                "type": "error", "status": "error",
                "message": error_message,
                "details": str(result.error_message) if result and result.error_message else "No specific details."
            })
            return
        else: # No LLM strategy was used, but crawl was successful
            if hasattr(result, 'extracted_content') and result.extracted_content is not None:
                 llm_extracted_payload_for_sse = result.extracted_content # Pass through non-LLM extractions
            else:
                 llm_extracted_payload_for_sse = None


        # Fallback or primary markdown content
        markdown_content_from_crawler = result.markdown.raw_markdown if result and result.markdown else None
        
        page_title = result.metadata.get("title") if result and result.metadata else url
        pdf_file_path = getattr(result, 'pdf_path', None) if result else None
        screenshot_file_path = getattr(result, 'screenshot_path', None) if result else None
        
        final_data_payload = {
            "markdown": markdown_content_from_crawler,
            "title": page_title,
            "url": result.url if result else url,
            "pdf_path": pdf_file_path,
            "screenshot_path": screenshot_file_path,
            "metadata": result.metadata if result else None,
            "error": None,
            "engine_used": "crawl4ai",
            "extracted_content": llm_extracted_payload_for_sse
        }
        
        yield json.dumps({"type": "completed", "status": "completed", "message": "Crawl4ai fetch complete.", "data": final_data_payload})
        logger.info(f"crawl4ai_fetcher completed successfully for URL: {url}")

    except asyncio.CancelledError:
        logger.info(f"crawl4ai_fetcher task cancelled for URL: {url}")
        if llm_log_data: # If LLM op was in progress
            llm_log_data["call_successful"] = False
            llm_log_data["error_type"] = "CancelledError"
            llm_log_data["error_message_detail"] = "Fetch process cancelled during LLM operation."
            yield json.dumps({"type": "llm_log_event", "data": llm_log_data}) # Yield log data
        yield json.dumps({"type": "error", "status": "error", "message": "Fetch process cancelled."})
        raise
    except Exception as e:
        logger.error(f"Error in crawl4ai_fetcher for URL {url}: {e}", exc_info=True)
        general_error_message = f"An error occurred during crawl4ai fetch: {str(e)}"
        if llm_log_data:
            llm_log_data["call_successful"] = False
            llm_log_data["error_type"] = llm_log_data.get("error_type", "UnhandledException")
            llm_log_data["error_message_detail"] = llm_log_data.get("error_message_detail", str(e))
            
            yield json.dumps({"type": "llm_log_event", "data": llm_log_data}) # Yield log data
            
            error_payload_details = {k: v for k, v in llm_log_data.items() if v is not None}
            yield json.dumps({
                "type": "error", "status": "error",
                "message": general_error_message,
                "llm_error": {
                    "error_code": "LLM_UNHANDLED_EXCEPTION",
                    "message": "Unhandled exception during LLM operation.",
                    "llm_error_type": llm_log_data["error_type"],
                    "details": error_payload_details
                }
            })
        else:
            yield json.dumps({"type": "error", "status": "error", "message": general_error_message})