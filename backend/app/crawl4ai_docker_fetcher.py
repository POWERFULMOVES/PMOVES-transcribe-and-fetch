# -*- coding: utf-8 -*-
"""
Module to handle content fetching using the crawl4ai Docker service.
"""

import logging
logger = logging.getLogger(__name__) # Define logger at the top

import asyncio
import json
import os
import time
from typing import Dict, Any, AsyncGenerator, List, Optional, Tuple, Union, Pattern
from datetime import datetime, timezone
import httpx # Added for async HTTP requests

from crawl4ai import (
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
    DefaultMarkdownGenerator,
)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.models import CrawlResultContainer, MarkdownGenerationResult
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter, DomainFilter
from crawl4ai.deep_crawling.scorers import URLScorer, KeywordRelevanceScorer

from crawl4ai.docker_client import Crawl4aiDockerClient, Crawl4aiClientError

# --- Local Imports ---
try:
    from .utils.llm_registry_service import get_llm_registry_service
    LLM_REGISTRY_AVAILABLE = True
except ImportError:
    LLM_REGISTRY_AVAILABLE = False
    get_llm_model_details_from_registry = None
    logger.error("llm_registry_service not available. LLM model selection will rely on direct parameters.")

try:
    from .app_config import LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY
    PROXY_CONFIG_LOADED = True
    logger.info(f"Successfully imported LiteLLM proxy config: URL='{LITELLM_PROXY_URL}', Key_Loaded={'Yes' if LITELLM_PROXY_API_KEY else 'No'}")
except ImportError:
    logger.warning("Could not import LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY from .app_config. Proxy integration will be disabled or use defaults.")
    LITELLM_PROXY_URL = os.getenv('LITELLM_PROXY_URL', 'http://localhost:4000')
    LITELLM_PROXY_API_KEY = os.getenv('LITELLM_PROXY_API_KEY')
    PROXY_CONFIG_LOADED = False

try:
    from .models.presets_models import CrawlPresetResponse # Corrected relative import
except ImportError: # Handle cases where models might not be in this exact path during isolated testing
    logger.warning("Could not import CrawlPresetResponse from .models.presets_models. Defining a fallback for this subtask.")
    from pydantic import BaseModel, Field as PydanticField # Use PydanticField to avoid conflict with FastAPI's Field
    from uuid import UUID as PyUUID # Use PyUUID to avoid conflict with FastAPI's UUID

    class CrawlPresetResponse(BaseModel):
        preset_id: PyUUID
        preset_name: str
        description: Optional[str] = None
        version: int = 1
        crawl_tool: str = "crawl4ai"
        strategy_definition: Dict[str, Any] = PydanticField(...)
        target_capability: Optional[str] = None
        tags: Optional[List[str]] = None
        created_by: Optional[PyUUID] = None
        created_at: datetime
        updated_at: datetime
        class Config:
            orm_mode = True


# --- Helper Functions for Type Conversion ---
# (to_bool, to_list_str, to_int, to_float, to_json_dict remain the same)
def to_bool(value: Any) -> bool:
    if isinstance(value, bool): return value
    if isinstance(value, str): return value.lower() in ('true', 'yes', '1', 't')
    return bool(value)

def to_list_str(value: Any, delimiter: str = ',') -> Optional[List[str]]:
    if value is None: return None
    if isinstance(value, list): return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str): return [item.strip() for item in value.split(delimiter) if item.strip()]
    return None

def to_int(value: Any) -> Optional[int]:
    if value is None: return None
    try: return int(value)
    except (ValueError, TypeError): return None

def to_float(value: Any) -> Optional[float]:
    if value is None: return None
    try: return float(value)
    except (ValueError, TypeError): return None

def to_json_dict(value: Any) -> Optional[Dict[str, Any]]:
    if value is None: return None
    if isinstance(value, dict): return value
    if isinstance(value, str):
        if not value.strip(): return None
        try: return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON string: {value}", exc_info=True)
            return None
    return None

async def fetch_with_crawl4ai_docker(url: str, original_request_params: Dict[str, Any]) -> AsyncGenerator[str, None]:
    logger.info(f"fetch_with_crawl4ai_docker called for URL: {url}")
    logger.debug(f"Original request parameters for crawl4ai: {original_request_params}")

    params = original_request_params

    # --- Preset Fetching Logic ---
    loaded_strategy_definition_from_preset: Optional[Dict[str, Any]] = None
    preset_identifier = original_request_params.get('preset_id') or original_request_params.get('preset_name')

    if preset_identifier:
        logger.info(f"Preset identifier found: '{preset_identifier}'. Attempting to fetch preset.")
        BACKEND_SERVICE_URL = os.getenv("BACKEND_SERVICE_URL", "http://localhost:8000")
        preset_api_url = f"{BACKEND_SERVICE_URL}/api/presets/{preset_identifier}"
        logger.info(f"Calling Presets API: GET {preset_api_url}")
        try:
            async with httpx.AsyncClient() as client:
                api_response = await client.get(preset_api_url, timeout=10.0)

            if api_response.status_code == 200:
                preset_data = api_response.json()
                try:
                    fetched_preset = CrawlPresetResponse(**preset_data)
                    loaded_strategy_definition_from_preset = fetched_preset.strategy_definition
                    logger.info(f"Successfully fetched and parsed preset '{preset_identifier}'. Using its strategy_definition.")
                    logger.debug(f"Strategy definition from preset: {json.dumps(loaded_strategy_definition_from_preset, default=str)[:500]}...")
                except Exception as pydantic_err: # Catch Pydantic validation error
                    logger.error(f"Pydantic validation error for fetched preset '{preset_identifier}': {pydantic_err}", exc_info=True)
            elif api_response.status_code == 404:
                logger.warning(f"Preset '{preset_identifier}' not found (404) at API: {preset_api_url}")
            else:
                logger.error(f"Failed to fetch preset '{preset_identifier}'. Status: {api_response.status_code}, Response: {api_response.text[:200]}")
        except httpx.RequestError as http_err:
            logger.error(f"HTTP request error fetching preset '{preset_identifier}' from {preset_api_url}: {http_err}", exc_info=True)
        except Exception as e_preset_fetch:
            logger.error(f"Unexpected error fetching preset '{preset_identifier}': {e_preset_fetch}", exc_info=True)

    # --- Determine Final strategy_definition ---
    # This variable (lowercase) will be used by all subsequent configuration logic
    strategy_definition: Dict[str, Any] = {}
    direct_sd_from_params = original_request_params.get('strategy_definition')

    if loaded_strategy_definition_from_preset:
        strategy_definition = loaded_strategy_definition_from_preset
        if direct_sd_from_params:
            logger.warning("Both a preset and a direct 'strategy_definition' were provided. Prioritizing preset's definition.")
    elif isinstance(direct_sd_from_params, dict):
        strategy_definition = direct_sd_from_params
        logger.info("Using 'strategy_definition' (dict) directly from request parameters.")
    elif isinstance(direct_sd_from_params, str):
        logger.info("Attempting to parse 'strategy_definition' (string) from request parameters.")
        try:
            parsed_direct_sd = json.loads(direct_sd_from_params)
            if isinstance(parsed_direct_sd, dict):
                strategy_definition = parsed_direct_sd
            else:
                logger.error(f"Parsed direct 'strategy_definition' is not a dict: {type(parsed_direct_sd)}. Ignoring.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse direct 'strategy_definition' JSON string: {direct_sd_from_params[:200]}...", exc_info=True)

    if strategy_definition:
        logger.info(f"Final 'strategy_definition' (type: {type(strategy_definition)}) will be used for configuration: {json.dumps(strategy_definition, default=str)[:500]}...")
    else:
        logger.info("No 'strategy_definition' (from preset or direct params) will be used. Relying on individual fallback flat parameters from 'params'.")


    CRAWL4AI_SERVICE_URL = 'http://localhost:11235'
    logger.warning(f"FORCED CRAWL4AI_SERVICE_URL: {CRAWL4AI_SERVICE_URL}")
    CRAWL4AI_API_TOKEN = os.getenv('CRAWL4AI_API_TOKEN')
    crawl4ai_client = None

    try:
        yield json.dumps({"type": "status", "status": "initializing", "message": "Initializing crawl4ai service client..."})
        crawl4ai_client = Crawl4aiDockerClient(base_url=CRAWL4AI_SERVICE_URL)
        try:
            await crawl4ai_client.authenticate("placeholder@example.com")
            logger.info("Crawl4aiDockerClient.authenticate() called successfully.")
        except Exception as auth_err:
            logger.error(f"Error during Crawl4aiDockerClient.authenticate() call: {auth_err}", exc_info=True)
            yield json.dumps({"type": "error", "message": f"Error during client authentication handshake: {auth_err}"})
            return
        yield json.dumps({"type": "status", "status": "initialized", "message": "crawl4ai service client initialized."})

        # --- BrowserConfig Population ---
        logger.info("Populating BrowserConfig...")
        sd_browser_config = strategy_definition.get('browser_config', {})

        browser_config_args = {
            "headless": to_bool(sd_browser_config.get("headless", params.get("headless", True))),
            "user_agent": sd_browser_config.get("user_agent", params.get("user_agent")),
            "proxy": sd_browser_config.get("proxy", params.get("proxy_url")),
            "java_script_enabled": to_bool(sd_browser_config.get("java_script_enabled", params.get("enable_javascript", True))),
            "ignore_https_errors": to_bool(sd_browser_config.get("ignore_https_errors", params.get("ignore_https_errors", True))),
            "light_mode": to_bool(sd_browser_config.get("light_mode", params.get("light_mode", False))),
            "text_mode": to_bool(sd_browser_config.get("text_mode", params.get("text_mode", False))),
            "cookies": sd_browser_config.get("cookies") if isinstance(sd_browser_config.get("cookies"), (dict, list)) else to_json_dict(params.get("browser_cookies")),
            "headers": sd_browser_config.get("headers") if isinstance(sd_browser_config.get("headers"), dict) else to_json_dict(params.get("browser_headers")),
            "use_persistent_context": to_bool(sd_browser_config.get("use_persistent_context", params.get("browser_use_persistent_context"))),
            "user_data_dir": sd_browser_config.get("user_data_dir", params.get("browser_user_data_dir")),
            "extra_args": sd_browser_config.get("extra_args") if isinstance(sd_browser_config.get("extra_args"), list) else to_list_str(params.get("browser_extra_args")),
            "viewport_width": to_int(sd_browser_config.get("viewport_width", params.get("viewport_width"))),
            "viewport_height": to_int(sd_browser_config.get("viewport_height", params.get("viewport_height"))),
            "browser_type": sd_browser_config.get("browser_type", params.get("browser_engine", "chromium")),
        }
        if browser_config_args["browser_type"] == "playwright":
            browser_config_args["browser_type"] = "chromium"
            logger.info("Mapped browser_engine 'playwright' to 'chromium' for BrowserConfig.")
        final_browser_config_args = {k: v for k, v in browser_config_args.items() if v is not None}
        logger.debug(f"Final arguments for BrowserConfig: {final_browser_config_args}")
        browser_config = BrowserConfig(**final_browser_config_args)
        logger.info(f"BrowserConfig populated. Headless: {browser_config.headless}, Text Mode: {browser_config.text_mode}")

        # --- LLMConfig (Global - from strategy_definition.llm_config) ---
        global_llm_config: Optional[LLMConfig] = None
        sd_global_llm_config_data = strategy_definition.get('llm_config', {})
        if sd_global_llm_config_data and isinstance(sd_global_llm_config_data, dict):
            logger.info(f"Global LLMConfig found in strategy_definition: {sd_global_llm_config_data}")
            if sd_global_llm_config_data.get("provider") and sd_global_llm_config_data.get("model"):
                global_llm_config_params = {k:v for k,v in sd_global_llm_config_data.items() if v is not None}
                if "base_url" in global_llm_config_params: global_llm_config_params["api_base"] = global_llm_config_params.pop("base_url")
                if "api_token" in global_llm_config_params: global_llm_config_params["api_key"] = global_llm_config_params.pop("api_token")
                try:
                    global_llm_config = LLMConfig(**global_llm_config_params)
                    logger.info(f"Instantiated global LLMConfig: {global_llm_config}")
                except Exception as e_llm_global: logger.error(f"Error instantiating global LLMConfig from strategy_definition: {e_llm_global}", exc_info=True)
            else: logger.warning("Global LLMConfig in strategy_definition missing provider or model.")

        # --- Deep Crawl Strategy ---
        logger.info("Populating Deep Crawl Strategy...")
        deep_crawl_strategy_instance: Optional[Union[BFSDeepCrawlStrategy, DFSDeepCrawlStrategy, BestFirstCrawlingStrategy]] = None
        sd_main_strategy_name = strategy_definition.get('strategy')
        sd_main_params = strategy_definition.get('params', {})
        sd_deep_crawl_block = strategy_definition.get('deep_crawl_strategy', {})

        dc_name_to_use = None
        dc_params_to_use = {}

        if isinstance(sd_deep_crawl_block, dict) and sd_deep_crawl_block.get('strategy'):
            dc_name_to_use = sd_deep_crawl_block.get('strategy')
            dc_params_to_use = sd_deep_crawl_block.get('params', {})
            logger.info(f"Using explicit 'deep_crawl_strategy' block: Name='{dc_name_to_use}', Params='{dc_params_to_use}'")
        elif isinstance(sd_main_strategy_name, str) and any(s_type.lower() in sd_main_strategy_name.lower() for s_type in ["bfs", "dfs", "bestfirst", "crawlstrategy"]):
            dc_name_to_use = sd_main_strategy_name
            dc_params_to_use = sd_main_params
            logger.info(f"Using top-level 'strategy':'{dc_name_to_use}' and 'params' for deep crawl.")

        if dc_name_to_use:
            logger.info(f"Attempting to instantiate deep crawl strategy '{dc_name_to_use}' from strategy_definition.")
            try:
                strategy_name_lower = dc_name_to_use.lower()
                if "bfsdeepcrawlstrategy" in strategy_name_lower or strategy_name_lower == "bfs":
                    deep_crawl_strategy_instance = BFSDeepCrawlStrategy(**{k:v for k,v in dc_params_to_use.items() if k in BFSDeepCrawlStrategy.model_fields})
                elif "dfsdeepcrawlstrategy" in strategy_name_lower or strategy_name_lower == "dfs":
                    deep_crawl_strategy_instance = DFSDeepCrawlStrategy(**{k:v for k,v in dc_params_to_use.items() if k in DFSDeepCrawlStrategy.model_fields})
                elif "bestfirstcrawlingstrategy" in strategy_name_lower or strategy_name_lower == "bestfirst":
                    bf_init_params = {k:v for k,v in dc_params_to_use.items() if k in BestFirstCrawlingStrategy.model_fields and k not in ['url_scorer', 'filter_chain']}
                    url_scorer_data = dc_params_to_use.get('url_scorer')
                    if isinstance(url_scorer_data, dict) and url_scorer_data.get('type'):
                        scorer_type_str = url_scorer_data['type']
                        scorer_params_data = url_scorer_data.get('params', {})
                        logger.info(f"Attempting to instantiate URLScorer from strategy_definition: Type='{scorer_type_str}', Params='{scorer_params_data}'")
                        if scorer_type_str.lower() == "keywordrelevancescorer":
                            try:
                                bf_init_params['url_scorer'] = KeywordRelevanceScorer(**scorer_params_data)
                                logger.info(f"Instantiated KeywordRelevanceScorer with params: {scorer_params_data}")
                            except Exception as e_scorer: logger.error(f"Error instantiating KeywordRelevanceScorer: {e_scorer}", exc_info=True)
                        else: logger.warning(f"Unsupported URLScorer type: {scorer_type_str}")

                    filter_chain_data = dc_params_to_use.get('filter_chain')
                    if isinstance(filter_chain_data, dict) and isinstance(filter_chain_data.get('filters'), list):
                        filter_objects = []
                        logger.info(f"Attempting to instantiate FilterChain with filters: {filter_chain_data['filters']}")
                        for filter_data in filter_chain_data['filters']:
                            if isinstance(filter_data, dict) and filter_data.get('type'):
                                filter_type_str = filter_data['type']
                                filter_params_data = filter_data.get('params', {})
                                filter_instance = None
                                if filter_type_str.lower() == "urlpatternfilter":
                                    try: filter_instance = URLPatternFilter(**filter_params_data); logger.info(f"Instantiated URLPatternFilter: {filter_params_data}")
                                    except Exception as e_f: logger.error(f"Error URLPatternFilter: {e_f}", exc_info=True)
                                elif filter_type_str.lower() == "domainfilter":
                                    try: filter_instance = DomainFilter(**filter_params_data); logger.info(f"Instantiated DomainFilter: {filter_params_data}")
                                    except Exception as e_f: logger.error(f"Error DomainFilter: {e_f}", exc_info=True)
                                else: logger.warning(f"Unsupported Filter type: {filter_type_str}")
                                if filter_instance: filter_objects.append(filter_instance)
                        if filter_objects: bf_init_params['filter_chain'] = FilterChain(filters=filter_objects); logger.info(f"Instantiated FilterChain with {len(filter_objects)} filters.")
                        else: logger.warning("No valid filters for FilterChain.")
                    deep_crawl_strategy_instance = BestFirstCrawlingStrategy(**bf_init_params)
                if deep_crawl_strategy_instance: logger.info(f"Instantiated deep crawl strategy from strategy_definition: {type(deep_crawl_strategy_instance).__name__}")
            except Exception as e: logger.error(f"Error instantiating deep crawl strategy '{dc_name_to_use}' from strategy_definition: {e}", exc_info=True)

        if not deep_crawl_strategy_instance:
            logger.info("Deep crawl strategy not from SD. Checking fallback 'params.deep_crawl_config' or individual 'deep_crawl_*' params.")
            fb_dc_conf_blob = params.get("deep_crawl_config")
            fb_dc_name = params.get("deep_crawl_strategy_name")
            current_fb_dc_params = {}
            fb_dc_name_to_use = fb_dc_name
            if isinstance(fb_dc_conf_blob, str): fb_dc_conf_blob = to_json_dict(fb_dc_conf_blob)
            if isinstance(fb_dc_conf_blob, dict) and fb_dc_conf_blob.get("strategy"):
                 fb_dc_name_to_use = fb_dc_conf_blob.get("strategy")
                 current_fb_dc_params = fb_dc_conf_blob.get("params", {})
            elif fb_dc_name_to_use:
                 if params.get("deep_crawl_max_depth") is not None: current_fb_dc_params["max_depth"] = to_int(params.get("deep_crawl_max_depth"))
                 if params.get("deep_crawl_max_pages") is not None: current_fb_dc_params["max_pages"] = to_int(params.get("deep_crawl_max_pages"))
                 if params.get("deep_crawl_include_external") is not None: current_fb_dc_params["include_external"] = to_bool(params.get("deep_crawl_include_external"))
                 if "bestfirst" in fb_dc_name_to_use.lower():
                    if params.get("deep_crawl_url_scorer_type"): current_fb_dc_params["url_scorer_type"] = params.get("deep_crawl_url_scorer_type")
                    if params.get("deep_crawl_scorer_keywords"): current_fb_dc_params["scorer_keywords"] = params.get("deep_crawl_scorer_keywords")
                    if params.get("deep_crawl_scorer_weight") is not None: current_fb_dc_params["scorer_weight"] = to_float(params.get("deep_crawl_scorer_weight"))
                    if params.get("deep_crawl_filter_regexes") is not None: current_fb_dc_params["filter_regexes"] = to_list_str(params.get("deep_crawl_filter_regexes"))
            
            if fb_dc_name_to_use:
                try:
                    fb_strategy_name_lower = fb_dc_name_to_use.lower()
                    if "bfs" in fb_strategy_name_lower: deep_crawl_strategy_instance = BFSDeepCrawlStrategy(**current_fb_dc_params)
                    elif "dfs" in fb_strategy_name_lower: deep_crawl_strategy_instance = DFSDeepCrawlStrategy(**current_fb_dc_params)
                    elif "bestfirst" in fb_strategy_name_lower:
                        fb_bf_params = {k:v for k,v in current_fb_dc_params.items() if k in ["max_depth", "max_pages", "include_external"]}
                        fb_url_scorer: Optional[URLScorer] = None
                        if current_fb_dc_params.get("url_scorer_type", "").lower() == "keywordrelevancescorer" and current_fb_dc_params.get("scorer_keywords"):
                            fb_url_scorer = KeywordRelevanceScorer(keywords=str(current_fb_dc_params["scorer_keywords"]), weight=float(current_fb_dc_params.get("scorer_weight", 1.0)))
                        if fb_url_scorer: fb_bf_params['url_scorer'] = fb_url_scorer
                        fb_filter_regexes = current_fb_dc_params.get("filter_regexes")
                        if fb_filter_regexes and isinstance(fb_filter_regexes, list):
                            fb_filters_obj = [URLPatternFilter(regex) for regex in fb_filter_regexes]
                            if fb_filters_obj: fb_bf_params['filter_chain'] = FilterChain(filters=fb_filters_obj)
                        deep_crawl_strategy_instance = BestFirstCrawlingStrategy(**fb_bf_params)
                    if deep_crawl_strategy_instance: logger.info(f"Constructed deep crawl strategy from fallback: {type(deep_crawl_strategy_instance).__name__}")
                except Exception as e_fb_dcs: logger.error(f"Error constructing deep crawl strategy from fallback '{fb_dc_name_to_use}': {e_fb_dcs}", exc_info=True)


        # --- Extraction Strategy ---
        logger.info("Populating Extraction Strategy...")
        extraction_strategy_instance: Optional[ExtractionStrategy] = None
        sd_extraction_block = strategy_definition.get('extraction_strategy', {})
        if not sd_extraction_block and isinstance(sd_main_params, dict) :
            sd_extraction_block = sd_main_params.get('extraction_strategy', {})

        if sd_extraction_block and isinstance(sd_extraction_block.get('type'), str):
            ext_type = sd_extraction_block.get('type','').lower()
            ext_params_data = sd_extraction_block.get('params', {})
            logger.info(f"Using 'extraction_strategy' from strategy_definition: Type='{ext_type}', Params='{json.dumps(ext_params_data, default=str)}'")
            try:
                if "llmextractionstrategy" in ext_type or ext_type == "llm":
                    logger.info(f"Configuring LLMExtractionStrategy from strategy_definition params: {json.dumps(ext_params_data, default=str)}")
                    llm_config_for_strategy: Optional[LLMConfig] = None
                    sd_llm_config_data = ext_params_data.get('llm_config', {})
                    if isinstance(sd_llm_config_data, dict) and sd_llm_config_data.get("provider") and sd_llm_config_data.get("model"):
                        logger.info(f"Found llm_config in extraction_strategy params: {sd_llm_config_data}")
                        llm_c_args = {k:v for k,v in sd_llm_config_data.items() if v is not None}
                        if "base_url" in llm_c_args: llm_c_args["api_base"] = llm_c_args.pop("base_url")
                        if "api_token" in llm_c_args: llm_c_args["api_key"] = llm_c_args.pop("api_token")
                        try:
                            llm_config_for_strategy = LLMConfig(**llm_c_args)
                            logger.info(f"LLMConfig for LLMExtractionStrategy created from extraction_strategy.params.llm_config: {llm_config_for_strategy}")
                        except Exception as e_llm_cfg_sd: logger.error(f"Error creating LLMConfig from extraction_strategy.params.llm_config: {e_llm_cfg_sd}", exc_info=True)
                    if not llm_config_for_strategy and global_llm_config:
                        llm_config_for_strategy = global_llm_config
                        logger.info("Using global LLMConfig for LLMExtractionStrategy.")
                    if not llm_config_for_strategy:
                        logger.info("LLMConfig not available from strategy_definition for LLMExtractionStrategy. Attempting fallback to original 'params'.")
                        llm_model_alias_fb = params.get("llm_model_alias") or os.getenv('DEFAULT_LLM_MODEL_ALIAS')
                        if llm_model_alias_fb and LLM_REGISTRY_AVAILABLE and get_llm_registry_service:
                            llm_registry = get_llm_registry_service()
                            if llm_registry:
                                model_details_fb = await llm_registry.get_model_details(llm_model_alias_fb)
                                if model_details_fb and (PROXY_CONFIG_LOADED or LITELLM_PROXY_URL):
                                    llm_config_for_strategy = LLMConfig(provider=llm_model_alias_fb, api_base=LITELLM_PROXY_URL, api_key=LITELLM_PROXY_API_KEY, extra_params=model_details_fb.get("extra_params"), temperature=to_float(ext_params_data.get("temperature", params.get("llm_temperature"))), max_tokens=to_int(ext_params_data.get("max_tokens", params.get("llm_max_tokens"))))
                                    logger.info(f"LLMConfig for LLMExtractionStrategy created from LLM Registry (fallback): {llm_model_alias_fb}")
                        if not llm_config_for_strategy:
                            fb_llm_provider = ext_params_data.get("provider", params.get("llm_model", params.get("provider")))
                            fb_llm_model = ext_params_data.get("model", params.get("llm_model_name", fb_llm_provider))
                            fb_llm_api_base = ext_params_data.get("api_base", params.get("crawl4ai_llm_base_url", params.get("api_base")))
                            fb_llm_api_key = ext_params_data.get("api_key", params.get("llm_api_key"))
                            if fb_llm_provider and fb_llm_model:
                                direct_llm_fb_args = { "provider": fb_llm_provider, "model": fb_llm_model, "api_key": fb_llm_api_key, "api_base": fb_llm_api_base, "temperature": to_float(ext_params_data.get("temperature", params.get("llm_temperature"))), "max_tokens": to_int(ext_params_data.get("max_tokens", params.get("llm_max_tokens"))), "extra_params": ext_params_data.get("extra_params", to_json_dict(params.get("llm_extra_params")))}
                                direct_llm_fb_args = {k:v for k,v in direct_llm_fb_args.items() if v is not None}
                                try:
                                    llm_config_for_strategy = LLMConfig(**direct_llm_fb_args)
                                    logger.info(f"LLMConfig for LLMExtractionStrategy created from direct fallback params (merged with SD where possible): {direct_llm_fb_args}")
                                except Exception as e_llm_cfg_fb_direct: logger.error(f"Error creating LLMConfig from merged/fallback params: {e_llm_cfg_fb_direct}", exc_info=True)
                            else: logger.warning("Insufficient params for LLMConfig from fallback/merged.")
                    if llm_config_for_strategy:
                        schema_json_val = ext_params_data.get('schema_json', ext_params_data.get('json_schema', params.get("llm_json_schema")))
                        if isinstance(schema_json_val, str): schema_json_val = to_json_dict(schema_json_val)
                        instruction_val = ext_params_data.get('instruction', ext_params_data.get('prompt_template', params.get("llm_prompt_template")))
                        if schema_json_val:
                            llm_strat_args = { "llm_config": llm_config_for_strategy, "json_schema": schema_json_val, "prompt_template": instruction_val, "output_format": ext_params_data.get("output_format", params.get("llm_output_format")), "vision_enabled": to_bool(ext_params_data.get("vision_enabled", params.get("llm_vision_enabled", False))), "audio_enabled": to_bool(ext_params_data.get("audio_enabled", params.get("llm_audio_enabled", False))), "tool_calling_enabled": to_bool(ext_params_data.get("tool_calling_enabled", params.get("llm_tool_calling_enabled", False))), "thinking": ext_params_data.get("thinking", params.get("llm_thinking")), "reasoning_effort": ext_params_data.get("reasoning_effort", params.get("llm_reasoning_effort")), "cache_control": ext_params_data.get("cache_control", params.get("llm_cache_control")), "metadata": ext_params_data.get("metadata", to_json_dict(params.get("llm_metadata"))), "user": ext_params_data.get("user", params.get("llm_user")), "input_file_types": ext_params_data.get("input_file_types", to_list_str(params.get("llm_input_file_types")))}
                            final_llm_strat_args = {k:v for k,v in llm_strat_args.items() if v is not None}
                            extraction_strategy_instance = LLMExtractionStrategy(**final_llm_strat_args)
                            logger.info(f"LLMExtractionStrategy instantiated. Schema provided: {bool(schema_json_val)}, Instruction provided: {bool(instruction_val)}")
                        else: logger.warning("Could not instantiate LLMExtractionStrategy: JSON schema (schema_json) is missing.")
                    else: logger.warning("LLMConfig not successfully created, cannot instantiate LLMExtractionStrategy.")
                elif "cosinestrategy" in ext_type or ext_type == "cosine":
                    extraction_strategy_instance = CosineStrategy(**{k:v for k,v in ext_params_data.items() if k in CosineStrategy.model_fields})
                elif "jsoncssextractionstrategy" in ext_type or ext_type == "jsoncss":
                    extraction_strategy_instance = JsonCssExtractionStrategy(**{k:v for k,v in ext_params_data.items() if k in JsonCssExtractionStrategy.model_fields})
                if extraction_strategy_instance: logger.info(f"Instantiated extraction strategy from strategy_definition: {type(extraction_strategy_instance).__name__}")
            except Exception as e: logger.error(f"Error instantiating extraction strategy '{ext_type}' from strategy_definition: {e}", exc_info=True)
        if not extraction_strategy_instance: # Fallback
            logger.info("Extraction strategy not fully parsed from strategy_definition or not defined. Checking fallback parameters.")
            fb_ext_type = params.get("extraction_strategy")
            if fb_ext_type == "llm" and not extraction_strategy_instance:
                logger.warning("LLM Extraction via fallback (simplified as SD path failed): This indicates missing LLM config in SD.")
                llm_model_alias_fb = params.get("llm_model_alias")
                llm_json_schema_fb = to_json_dict(params.get("llm_json_schema"))
                if llm_model_alias_fb and llm_json_schema_fb and LLM_REGISTRY_AVAILABLE and get_llm_registry_service :
                     temp_llm_config = LLMConfig(provider=llm_model_alias_fb, api_base=LITELLM_PROXY_URL, api_key=LITELLM_PROXY_API_KEY)
                     extraction_strategy_instance = LLMExtractionStrategy(llm_config=temp_llm_config, json_schema=llm_json_schema_fb)
                     logger.info("Used simplified fallback for LLMExtractionStrategy based on top-level 'params'.")

        # --- Markdown Generator ---
        logger.info("Populating Markdown Generator...")
        markdown_generator_instance = DefaultMarkdownGenerator()
        sd_md_config = strategy_definition.get('markdown_generator_config', {})
        if not sd_md_config and isinstance(sd_main_params, dict): sd_md_config = sd_main_params.get('markdown_generator_config',{})
        if sd_md_config and isinstance(sd_md_config.get('type'), str):
            logger.info(f"Using 'markdown_generator_config' from strategy_definition: {sd_md_config}")
            if sd_md_config.get('type','').lower() != "defaultmarkdown": logger.warning(f"Custom markdown generator type '{sd_md_config.get('type')}' from SD not yet fully supported, using Default.")
        sd_run_config_for_md = strategy_definition.get('run_config', sd_main_params if isinstance(sd_main_params, dict) else {})
        use_adv_md_sd = sd_md_config.get('params',{}).get('use_advanced_markdown', sd_run_config_for_md.get('use_advanced_markdown'))
        use_adv_md_final = to_bool(use_adv_md_sd if use_adv_md_sd is not None else params.get("use_advanced_markdown", False))
        if use_adv_md_final:
            if hasattr(markdown_generator_instance, 'content_filter'):
                markdown_generator_instance.content_filter = PruningContentFilter()
                logger.info("Applied PruningContentFilter to MarkdownGenerator.")
            else: logger.warning("MarkdownGenerator does not support content_filter. Advanced markdown (pruning) not applied.")
        logger.info(f"Final Markdown Generator: {type(markdown_generator_instance).__name__}")

        # --- CrawlerRunConfig ---
        logger.info("Populating CrawlerRunConfig...")
        sd_run_config_block = strategy_definition.get('run_config', {})
        if not sd_run_config_block and isinstance(sd_main_params, dict) and any(k in sd_main_params for k in ["page_timeout", "screenshot", "only_text", "max_retries", "retry_delay", "ignore_urls", "include_urls"]):
            logger.info("Using top-level 'params' from strategy_definition as source for run_config.")
            sd_run_config_block = sd_main_params
        elif sd_run_config_block: logger.info(f"Using 'run_config' block from strategy_definition: {json.dumps(sd_run_config_block, default=str)}")
        else: logger.info("No 'run_config' block in strategy_definition, or top-level 'params' did not seem to contain run_config settings. Relying on fallbacks.")
        page_timeout_final_ms = to_int(sd_run_config_block.get("page_timeout", params.get("crawl4ai_page_timeout")))
        if page_timeout_final_ms is None and params.get("timeout") is not None:
            page_timeout_val_s = to_int(params.get("timeout"))
            if page_timeout_val_s is not None: page_timeout_final_ms = page_timeout_val_s * 1000
        if page_timeout_final_ms is None: page_timeout_final_ms = 60000
        logger.info(f"Effective Page Timeout for CrawlerRunConfig: {page_timeout_final_ms}ms")
        crawler_run_config_args = {"deep_crawl_strategy": deep_crawl_strategy_instance, "extraction_strategy": extraction_strategy_instance, "markdown_generator": markdown_generator_instance, "screenshot": to_bool(sd_run_config_block.get("screenshot", params.get("capture_screenshot", False))), "ignore_urls": sd_run_config_block.get("ignore_urls") if isinstance(sd_run_config_block.get("ignore_urls"), list) else to_list_str(params.get("ignore_urls")), "include_urls": sd_run_config_block.get("include_urls") if isinstance(sd_run_config_block.get("include_urls"), list) else to_list_str(params.get("include_urls")), "max_retries": to_int(sd_run_config_block.get("max_retries", params.get("max_retries"))), "retry_delay": to_float(sd_run_config_block.get("retry_delay", params.get("retry_delay"))), "page_timeout": page_timeout_final_ms, "only_text": to_bool(sd_run_config_block.get("only_text", params.get("only_text", False)))}
        final_crawler_run_config_args = {k: v for k, v in crawler_run_config_args.items() if v is not None}
        logger.debug(f"Final arguments for CrawlerRunConfig constructor: { {k: (type(v).__name__ if isinstance(v, (ExtractionStrategy, BFSDeepCrawlStrategy, DFSDeepCrawlStrategy, BestFirstCrawlingStrategy, DefaultMarkdownGenerator)) else v) for k,v in final_crawler_run_config_args.items()} }")
        crawler_config_object: Optional[CrawlerRunConfig] = None
        try:
            crawler_config_object = CrawlerRunConfig(**final_crawler_run_config_args)
            logger.info(f"CrawlerRunConfig object created successfully.")
        except Exception as e_crc_create:
            logger.error(f"Error creating CrawlerRunConfig object: {e_crc_create}", exc_info=True)
            yield json.dumps({"type": "error", "message": f"Error creating CrawlerRunConfig: {e_crc_create}"})
            return
        
        # --- Execute Crawl using Docker Client ---
        yield json.dumps({"type": "status", "status": "crawling", "message": f"Starting crawl for {url}..."})
        start_time = time.time()
        urls_to_crawl = [url]
        logger.info(f"Calling crawl4ai_client.crawl with: urls_count={len(urls_to_crawl)}, browser_config_valid={isinstance(browser_config, BrowserConfig)}, crawler_config_valid={isinstance(crawler_config_object, CrawlerRunConfig)}")
        crawl_result_item = None
        try:
            base_timeout_ms_eff = crawler_config_object.page_timeout if crawler_config_object and crawler_config_object.page_timeout is not None else 60000
            grace_period_seconds = 30
            effective_timeout_seconds = (base_timeout_ms_eff / 1000.0) + grace_period_seconds
            logger.info(f"Attempting crawl with client-side timeout: {effective_timeout_seconds:.2f} seconds (base: {base_timeout_ms_eff}ms).")
            crawl_result_item = await asyncio.wait_for(crawl4ai_client.crawl(urls=urls_to_crawl, browser_config=browser_config, crawler_config=crawler_config_object), timeout=effective_timeout_seconds)
        except asyncio.TimeoutError:
            logger.error(f"Client-side timeout after {effective_timeout_seconds:.2f}s waiting for crawl4ai Docker service for URL: {url}")
            yield json.dumps({"type": "error", "status": "timeout", "message": "The content fetch operation timed out on the client side."})
            raise
        except Crawl4aiClientError as ce:
            logger.error(f"Crawl4aiClientError during crawl for {url}: {ce}", exc_info=True)
            yield json.dumps({"type": "error", "status": "client_error", "message": f"Crawl4AI service client error: {str(ce)}" })
            raise
        except Exception as e_crawl:
            logger.error(f"Exception during crawl4ai_client.crawl for {url}: {e_crawl}", exc_info=True)
            yield json.dumps({"type": "error", "status": "crawl_exception", "message": f"An unexpected error occurred during the crawl execution: {str(e_crawl)}"})
            raise
        if isinstance(crawl_result_item, CrawlResult):
            logger.debug(f"Received crawl result for URL: {crawl_result_item.url}")
            output_data: Dict[str, Any] = {"type": "crawl_result", "timestamp": datetime.now(timezone.utc).isoformat(), "id": str(time.time()), "url": crawl_result_item.url}
            if crawl_result_item.status_code: output_data["status_code"] = crawl_result_item.status_code
            if crawl_result_item.error_message:
                output_data["error"] = str(crawl_result_item.error_message)
                logger.error(f"Crawl error for {crawl_result_item.url}: {crawl_result_item.error_message}")
                yield json.dumps({"type": "error", "timestamp": datetime.now(timezone.utc).isoformat(), "id": str(time.time()), "message": f"Error reported by crawler for {crawl_result_item.url}: {crawl_result_item.error_message}", "url": crawl_result_item.url})
            if crawl_result_item.cleaned_html: output_data["content"] = crawl_result_item.cleaned_html
            elif crawl_result_item.extracted_content: output_data["content"] = crawl_result_item.extracted_content
            elif crawl_result_item.html: output_data["content"] = crawl_result_item.html
            else: output_data["content"] = ""
            md_property = crawl_result_item.markdown
            if isinstance(md_property, MarkdownGenerationResult): output_data["markdown"] = md_property.raw_markdown if md_property.raw_markdown is not None else ""
            elif isinstance(md_property, str): output_data["markdown"] = md_property
            else: output_data["markdown"] = ""
            output_data["text"] = crawl_result_item.extracted_content if crawl_result_item.extracted_content is not None else ""
            if crawl_result_item.screenshot: output_data["screenshot_base64"] = crawl_result_item.screenshot
            if crawl_result_item.metadata: output_data["metadata"] = crawl_result_item.metadata
            if crawl_result_item.links: output_data["links"] = crawl_result_item.links
            if hasattr(crawl_result_item, 'llm_log_data') and crawl_result_item.llm_log_data:
                output_data["llm_log_data"] = crawl_result_item.llm_log_data
                logger.debug(f"LLM log data included for {crawl_result_item.url}")
            logger.info(f"Yielding crawl_result event for {crawl_result_item.url} (Content length: {len(output_data.get('content', ''))}, Markdown length: {len(output_data.get('markdown', ''))})")
            yield json.dumps(output_data, default=str)
        elif crawl_result_item is None and not (crawler_config_object and crawler_config_object.stream if crawler_config_object else False) :
            logger.warning("Crawl client returned None for a non-streaming request. This might indicate an issue or no content.")
            yield json.dumps({"type": "status", "status": "no_content", "message": "Crawl returned no content or an empty result.", "url": url})
        else:
            logger.error(f"Unexpected result type from crawl_ai_client.crawl: {type(crawl_result_item)}. Expected CrawlResult for single non-streaming URL.")
            yield json.dumps({"type": "error", "message": f"Unexpected result type from crawl client: {type(crawl_result_item)}"}) 
        end_time = time.time()
        duration = end_time - start_time
        yield json.dumps({"type": "status", "status": "completed", "message": f"Crawl completed in {duration:.2f} seconds.", "duration": duration})
    except Crawl4aiClientError as e:
        logger.error(f"Crawl4AI client error: {e}", exc_info=True)
        yield json.dumps({"type": "error", "status": "client_error_outer", "message": f"Crawl4AI service client error: {e}"})
    except Exception as e:
        logger.error(f"An unexpected error occurred during crawl: {e}", exc_info=True)
        yield json.dumps({"type": "error", "status": "unexpected_error_outer", "message": f"An unexpected error occurred: {e}"})
    finally:
        if crawl4ai_client:
            try:
                await crawl4ai_client.close()
                logger.info("Crawl4AI client connection closed.")
            except Exception as e:
                logger.error(f"Error closing Crawl4AI client: {e}", exc_info=True)
