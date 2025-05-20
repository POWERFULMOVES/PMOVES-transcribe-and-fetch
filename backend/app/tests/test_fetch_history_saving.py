import pytest
import asyncio
import logging # Added import
from httpx import AsyncClient
from unittest.mock import MagicMock, patch, AsyncMock

logger = logging.getLogger(__name__) # Added logger instance

from fastapi.testclient import TestClient # Using TestClient for easier app integration if needed, but AsyncClient for async nature
from app.main import app # Import your FastAPI app

# If your app needs specific startup/shutdown, consider fixtures
# For now, we'll use AsyncClient directly with the app

@pytest.mark.asyncio
async def test_save_crawl4ai_parameters_to_fetch_history():
    """
    Test 8.1: Verify that engine_specific_parameters for crawl4ai
    are correctly saved to the fetch_history table via the /fetch-content endpoint.
    """
    api_payload = {
        "url": "https://example.com/crawlaitest",
        "engine": "crawl4ai",
        "generate_pdf": False, # Keep post-fetch processing minimal for this test
        "upload_to_supabase": False,

        # crawl4ai specific parameters (matching all_request_params in main.py)
        "headless": False, # Non-default
        "user_agent": "Test User Agent For Crawl4AI History",
        "browser_engine": "playwright", # Default, but explicit
        "extraction_strategy": "llm",
        "output_format": "markdown",
        "token_budget": 3000,
        "llm_provider": "openai",
        "llm_model_name": "gpt-4o-mini-test",
        "llm_temperature": 0.5,
        "respect_robots_txt": False,
        "crawl4ai_interaction_timeout_ms": 45000,
        # Example for complex params (extraction_config, deep_crawl_config)
        # These are passed as query parameters, so they'd be strings if directly in URL,
        # but FastAPI handles Query() type conversion.
        # For the test, we pass them as they'd be in `all_request_params`
        # The /fetch-content endpoint expects these as individual query params,
        # not a nested dict in a POST body.
        # The `all_request_params` dict in main.py is flat.
        # So, we don't need to send "extraction_config": {"strategy": "LLM", ...}
        # Instead, we send the flattened params like "extraction_strategy": "llm"
        # Let's add a few more distinct ones:
        "take_screenshot": True,
        "page_load_wait_condition": "networkidle", # from crawl4ai run config
        "target_elements_css_selectors": "article, .content", # as string, will be parsed to list
        "excluded_elements_css_selector": ".ads, .header",
        "process_iframes_content": True,
        "cache_mode": "BYPASS", # from crawl4ai run config
    }

    # Mock CrawlResult object that arun should return
    # Ensure it's a structure that's serializable, similar to a real CrawlResult
    # from crawl4ai import CrawlResult, MarkdownGenerationResult # Already imported if needed by main code
    # For mocking, we can construct a dictionary or a MagicMock with serializable fields.
    # Using a dictionary for return_value is safer for JSON serialization.
    
    # If CrawlResult and MarkdownGenerationResult are Pydantic models,
    # FastAPI/Pydantic will handle their serialization if fields are serializable.
    # The issue arises if a mock object itself is passed where a serializable value is expected.
    
    # Let's use a structure that mimics CrawlResult with serializable data
    # Align mock_crawl_result_data with CrawlResult Pydantic model
    mock_crawl_result_data = {
        "success": True,
        "url": api_payload["url"],
        "html": "<html><body>Test HTML</body></html>",
        "cleaned_html": "<body>Test HTML</body>", # Example cleaned HTML
        "markdown": { # Mimicking MarkdownGenerationResult
            "raw_markdown": "# Test Content\nThis is a test.",
            "markdown_with_citations": "# Test Content\nThis is a test.",
            "references_markdown": "",
            "fit_markdown": None,
            "fit_html": None
        },
        "metadata": {"title": "Test Crawl Page"},
        "pdf": None,  # CrawlResult has 'pdf: Optional[bytes]'
        "screenshot": None,  # CrawlResult has 'screenshot: Optional[str]' (base64)
        "mhtml": None,  # CrawlResult has 'mhtml: Optional[str]'
        "error_message": None,
        # Fields from CrawlResult model, set to default/None if not specifically tested for content
        "media": {},
        "links": {},
        "downloaded_files": None,
        "extracted_content": None,
        "session_id": None,
        "response_headers": None,
        "status_code": 200, # Example status code
        "ssl_certificate": None, # Would need a mock SSLCertificate if accessed
        "dispatch_result": None, # Would need a mock DispatchResult if accessed
        "network_requests": [],
        "console_messages": [] # Renamed from console_logs to match CrawlResult
    }
    
    # If the code expects a CrawlResult object, we can mock it to behave like one
    # but ensure its attributes that get serialized are actual data.
    mock_crawl_result_obj = MagicMock(name="CrawlResultMock")
    
    # Assign all attributes from mock_crawl_result_data to mock_crawl_result_obj
    # This ensures the mock object has the same attributes as the data dict.
    for key, value in mock_crawl_result_data.items():
        if key == "markdown" and isinstance(value, dict): # Handle nested markdown mock
            mock_markdown_generation_result = MagicMock(name="MarkdownGenerationResultMock")
            for md_key, md_value in value.items():
                setattr(mock_markdown_generation_result, md_key, md_value)
            setattr(mock_crawl_result_obj, key, mock_markdown_generation_result)
        else:
            setattr(mock_crawl_result_obj, key, value)

    # Explicitly ensure critical attributes are set as per problem description,
    # though the loop above should cover them if they are in mock_crawl_result_data.
    # This is more for clarity and to ensure no typos.
    mock_crawl_result_obj.success = mock_crawl_result_data["success"]
    mock_crawl_result_obj.url = mock_crawl_result_data["url"]
    # mock_crawl_result_obj.markdown is set by the loop
    mock_crawl_result_obj.html = mock_crawl_result_data["html"]
    mock_crawl_result_obj.metadata = mock_crawl_result_data["metadata"]
    mock_crawl_result_obj.pdf = mock_crawl_result_data["pdf"] # Should be None or bytes
    mock_crawl_result_obj.screenshot = mock_crawl_result_data["screenshot"] # Should be None or str (base64)
    mock_crawl_result_obj.error_message = mock_crawl_result_data["error_message"]
    # Ensure console_messages is used if that's what CrawlResult has (it does)
    mock_crawl_result_obj.console_messages = mock_crawl_result_data["console_messages"]


    # Patch the .arun() method of AsyncWebCrawler where it's used
    # The actual class is in 'crawl4ai.crawler.AsyncWebCrawler'
    # But we need to patch it where it's imported and used in crawl4ai_fetcher.py
    with patch('app.crawl4ai_fetcher.AsyncWebCrawler') as MockAsyncWebCrawler:
        mock_crawler_instance = MockAsyncWebCrawler.return_value
        # The return_value of an AsyncMock should be what the await returns.
        # If arun is an async method, its direct return is a coroutine.
        # The AsyncMock handles the awaitable part.
        mock_crawler_instance.arun = AsyncMock(return_value=mock_crawl_result_obj)

        async with AsyncClient(app=app, base_url="http://test") as ac: # Renamed client to ac to avoid conflict with pytest fixture
            # The /fetch-content endpoint is a GET request with query parameters
            response = await ac.get("/fetch-content", params=api_payload)

            assert response.status_code == 200, f"API call failed: {response.text}"
            
            # Wait for SSE to complete (simplified: check for "completed" event)
            # A more robust way would be to consume the stream until a specific message or timeout
            sse_content = response.text
            assert '"status":"completed"' in sse_content or '"type":"completed"' in sse_content, "Fetch did not complete successfully via SSE"
            assert '"status":"error"' not in sse_content and '"type":"error"' not in sse_content, f"SSE stream reported an error: {sse_content}"


            # Now, fetch the history record
            # Give a slight delay for the history record to be written, especially the final update
            await asyncio.sleep(0.5)
            
            history_response = await ac.get("/api/fetch-history", params={"limit": 1})
            assert history_response.status_code == 200, f"Failed to fetch history: {history_response.text}"
            
            history_data = history_response.json()
            assert len(history_data) > 0, "No history records found"
            
            latest_history_entry = history_data[0]
            
            assert latest_history_entry["url"] == api_payload["url"]
            assert latest_history_entry["fetching_engine"] == "crawl4ai"
            assert latest_history_entry["status"] == "success" # Assuming the mock leads to success
            
            saved_params = latest_history_entry.get("engine_specific_parameters")
            assert saved_params is not None, "engine_specific_parameters not found in history"

            # Verify that the parameters sent in the API call are present in saved_params
            # `all_request_params` in main.py is the source of truth for what's saved.
            # We need to compare against the `api_payload` keys that would form `all_request_params`.
            
            # Construct the expected `all_request_params` based on our `api_payload`
            # and the defaults for non-provided params in the /fetch-content signature.
            # For simplicity in this test, we'll check a subset of what we sent.
            # A more thorough test would reconstruct the full expected `all_request_params`.
            
            expected_subset_params = {
                "url": api_payload["url"],
                "engine": api_payload["engine"],
                "headless": api_payload["headless"],
                "user_agent": api_payload["user_agent"],
                "extraction_strategy": api_payload["extraction_strategy"],
                "llm_provider": api_payload["llm_provider"],
                "llm_model_name": api_payload["llm_model_name"],
                "respect_robots_txt": api_payload["respect_robots_txt"],
                "take_screenshot": api_payload["take_screenshot"],
                "page_load_wait_condition": api_payload["page_load_wait_condition"],
                "target_elements_css_selectors": api_payload["target_elements_css_selectors"],
                "excluded_elements_css_selector": api_payload["excluded_elements_css_selector"],
                "process_iframes_content": api_payload["process_iframes_content"],
                "cache_mode": api_payload["cache_mode"],
                # These were part of the payload and should be in engine_specific_parameters
                "generate_pdf": api_payload["generate_pdf"],
                "upload_to_supabase": api_payload["upload_to_supabase"],
            }

            for key, expected_value in expected_subset_params.items():
                assert key in saved_params, f"Key '{key}' not found in saved_params"
                # Special handling for params that might be type-converted by Pydantic/FastAPI
                # or have defaults applied if not in api_payload.
                # For this test, we assume direct match for what we sent.
                if saved_params[key] != expected_value:
                    # FastAPI might convert bools from strings if they came via query
                    # Our api_payload has them as correct types already.
                    # For stringified lists like target_elements_css_selectors, FastAPI converts them.
                    # The `all_request_params` dict in main.py will have the Python types.
                    # Let's check the type if they don't match.
                    print(f"Mismatch for key '{key}': Expected '{expected_value}' (type {type(expected_value)}), Got '{saved_params[key]}' (type {type(saved_params[key])})")
                assert saved_params[key] == expected_value, f"Mismatch for key '{key}'"

            # Check a few more that have defaults if not provided, to ensure they are captured
            # These would be in `all_request_params` with their default values.
            assert "browser_engine" in saved_params and saved_params["browser_engine"] == "playwright"
            assert "output_format" in saved_params and saved_params["output_format"] == "markdown"
            assert "token_budget" in saved_params and saved_params["token_budget"] == 3000
            assert "llm_temperature" in saved_params and saved_params["llm_temperature"] == 0.5
            assert "crawl4ai_interaction_timeout_ms" in saved_params and saved_params["crawl4ai_interaction_timeout_ms"] == 45000

            # Ensure that Jina-specific params are not polluting if engine is crawl4ai
            # (unless they have shared names and defaults, which is fine)
            assert "jina_timeout_seconds" in saved_params # This is a general param in all_request_params
            assert "json_response" in saved_params # This is a general param in all_request_params

            logger.info("Test test_save_crawl4ai_parameters_to_fetch_history passed.")

# To run this test:
# Ensure your FastAPI server is NOT running separately if using TestClient that spins up the app.
# If using AsyncClient against a running server, ensure it's running.
# Here, AsyncClient(app=app) will run the app in-process for testing.
# Command: pytest backend/app/tests/test_fetch_history_saving.py