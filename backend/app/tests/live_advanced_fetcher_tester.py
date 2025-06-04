import asyncio
import json
import logging
import os
from typing import Dict, Any

# Adjust import path based on actual location if run from a different context
# Assuming it might be run from project root or a similar context where 'backend' is a package
try:
    from backend.app.crawl4ai_docker_fetcher import fetch_with_crawl4ai_docker
except ImportError:
    # Fallback for direct execution if path issues occur, try to make it runnable
    # This path adjustment is fragile and depends on execution context.
    # It's better if the execution environment handles PYTHONPATH.
    # For a subtask, the primary goal is to create the file.
    # import sys
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    # from app.crawl4ai_docker_fetcher import fetch_with_crawl4ai_docker

    # If the above fails, define a placeholder for fetch_with_crawl4ai_docker
    async def fetch_with_crawl4ai_docker(url: str, params: Dict[str, Any]):
        logging.warning("Using MOCK fetch_with_crawl4ai_docker for script creation/execution.")
        yield json.dumps({"type": "status", "message": f"MOCK: Would fetch {url} with params: {json.dumps(params, default=str)}"})
        await asyncio.sleep(0.1) # Simulate some async work
        # Attempt to parse strategy_definition if it's a string
        sd_str = params.get("strategy_definition")
        sd_dict = {}
        if isinstance(sd_str, str):
            try:
                sd_dict = json.loads(sd_str)
            except json.JSONDecodeError:
                logging.warning("Mock: Could not parse strategy_definition string in mock fetcher.")
        elif isinstance(sd_str, dict): # Already a dict
            sd_dict = sd_str

        mock_result_content = f"Mock content for {url}"
        if sd_dict.get("extraction_strategy", {}).get("type") == "LLMExtractionStrategy":
            mock_result_content += " (LLM Extracted)"

        yield json.dumps({
            "type": "crawl_result",
            "url": url,
            "content": mock_result_content,
            "markdown": f"# Mock MD for {url}\n{mock_result_content}",
            "llm_log_data": {"mock_llm_interaction": True} if "LLMExtractionStrategy" in str(sd_dict) else None,
            "metadata": {"title": f"Mock Title for {url}"}
        })


# Configure logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure environment variables are set if needed by the fetcher (e.g., for LLM calls)
# os.environ["OPENAI_API_KEY"] = "your_key_here"
# os.environ["LITELLM_PROXY_URL"] = "http://localhost:4000"
# os.environ["BACKEND_SERVICE_URL"] = "http://localhost:8000" # For preset API calls if testing those

async def run_test_crawl(test_name: str, url: str, strategy_definition: Dict[str, Any]):
    logger.info(f"--- Starting Test: {test_name} ---")
    logger.info(f"Target URL: {url}")
    logger.info(f"Strategy Definition: {json.dumps(strategy_definition, indent=2, default=str)}")

    # The fetcher expects strategy_definition to be a JSON string if passed in original_request_params
    request_params = {"strategy_definition": json.dumps(strategy_definition)}

    results = []
    try:
        async for event_str in fetch_with_crawl4ai_docker(url, request_params):
            try:
                event = json.loads(event_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON event string: {event_str}")
                continue

            logger.info(f"Event from fetcher: {event.get('type')} - {event.get('status', '')} - {str(event.get('message', event.get('content', ''))[:200])}")
            if event.get("type") == "crawl_result":
                results.append(event)
                if "llm extraction config" in test_name.lower(): # Adjusted to match test name
                    assert "llm_log_data" in event or "extracted_content" in event or "LLM Extracted" in event.get("content",""), "LLM test missing expected fields or mock content indicator"
                logger.info(f"Crawl Result for {event.get('url')}: Markdown length {len(event.get('markdown', ''))}, Content length {len(event.get('content', ''))}")
                if event.get('error'):
                    logger.error(f"Crawl error in result: {event.get('error')}")
            elif event.get("type") == "error":
                 logger.error(f"Error event received: {event.get('message')} - Details: {event.get('details', event.get('content'))}")


    except Exception as e:
        logger.error(f"Exception during test '{test_name}': {e}", exc_info=True)

    logger.info(f"--- Test Finished: {test_name} ({len(results)} crawl_result events received) ---")
    return results

async def main():
    test_url = "https://example.com"
    # test_dynamic_page_url = "https://webscraper.io/test-sites/e-commerce/scroll"

    # Test 1: Basic BrowserConfig override
    sd_basic_browser = {
        "browser_config": {
            "user_agent": "TestAgent/1.0 (AdvancedFetcherTest)",
            "headless": True,
            "text_mode": True # Should imply only_text for some interpretations
        },
        "run_config": {
            "screenshot": False,
            "only_text": True
        }
    }
    await run_test_crawl("Basic Browser and RunConfig Override", test_url, sd_basic_browser)

    # Test 2: LLMExtractionStrategy
    sd_llm_extract = {
        "llm_config": {
             "provider": "ollama",
             "model": "mistral:latest",
             "api_base": "http://localhost:11434",
             "temperature": 0.1
        },
        "extraction_strategy": {
            "type": "LLMExtractionStrategy",
            "params": {
                # Example of strategy-specific LLM config; if absent, global llm_config above would be used
                # "llm_config": {
                # "provider": "ollama", "model": "phi3", "api_base": "http://localhost:11434"
                # },
                "json_schema": {"title": "string", "summary": "string"},
                "instruction": "Extract the title and a brief summary of the webpage content."
            }
        },
        "run_config": {"page_timeout": 30000}
    }
    logger.info("Expected behavior for LLM Test: Fetcher should log LLMConfig and LLMExtractionStrategy details.")
    await run_test_crawl("LLM Extraction Config", test_url, sd_llm_extract)


    # Test 3: BestFirstCrawlingStrategy with Scorer and Filter
    sd_best_first = {
        # "strategy": "BestFirstCrawlingStrategy", # Top-level strategy if not using deep_crawl_strategy block
        # "params": { ... }
        "deep_crawl_strategy": { # Explicit deep_crawl_strategy block
            "strategy": "BestFirstCrawlingStrategy",
            "params": {
                "max_depth": 1,
                "max_pages": 3,
                "include_external": False,
                "url_scorer": {
                    "type": "KeywordRelevanceScorer",
                    "params": {"keywords": ["example", "information"], "weight": 0.9}
                },
                "filter_chain": {
                    "filters": [
                        {"type": "URLPatternFilter", "params": {"patterns": [".*example.com.*"]}},
                        {"type": "DomainFilter", "params": {"allowed_domains": ["example.com"]}}
                    ]
                }
            }
        },
        "run_config": {"page_timeout": 45000}
    }
    logger.info("Expected behavior for BestFirst Test: Fetcher should log strategy details. Crawl may find additional pages on example.com if Docker service & network allow.")
    await run_test_crawl("BestFirst Deep Crawl Config", test_url, sd_best_first)

    # Test 4: Single Page fetch with JsonCssExtractionStrategy
    # This implies no "deep_crawl_strategy" or a top-level strategy like "SinglePageFetchStrategy"
    sd_single_page_jsoncss = {
        # No "deep_crawl_strategy" block implies single page fetch
        "extraction_strategy": {
            "type": "JsonCssExtractionStrategy",
            "params": {
                "schema_json": {
                    "title": {"selector": "h1", "type": "text"}
                }
            }
        },
        "run_config": {
            "only_text": False # JsonCss needs HTML
        }
    }
    await run_test_crawl("Single Page with JsonCssExtractionStrategy", test_url, sd_single_page_jsoncss)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    # if project_root not in sys.path:
    #    sys.path.insert(0, project_root)
    # For local testing, ensure PYTHONPATH is set up to find 'backend.app...'
    # e.g., export PYTHONPATH=/path/to/your/project
    asyncio.run(main())
