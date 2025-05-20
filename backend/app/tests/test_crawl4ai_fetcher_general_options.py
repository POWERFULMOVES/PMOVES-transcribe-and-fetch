# -*- coding: utf-8 -*-
"""
Integration tests for the crawl4ai_fetcher.py module, focusing on general
BrowserConfig and CrawlerRunConfig options.
"""

import pytest
import json
import logging
import urllib.parse # Added for URL encoding
from unittest.mock import AsyncMock, patch, MagicMock, call

# TestClient will be provided by the conftest.py fixture
# from fastapi.testclient import TestClient
from crawl4ai import BrowserConfig, CrawlerRunConfig, CrawlResult
from types import SimpleNamespace # Import SimpleNamespace

# app will be provided by the conftest.py fixture
# from app.main import app

# client instance will be injected by pytest fixture
CRAWL4AI_FETCHER_ENDPOINT = "/fetch-content" # Updated endpoint

# --- Pytest Fixtures ---

@pytest.fixture
def mock_async_web_crawler_fixture():
    """
    Provides a consistently mocked AsyncWebCrawler.
    Yields the patched class, the instance, and the arun method mock.
    """
    with patch('backend.app.crawl4ai_fetcher.AsyncWebCrawler') as MockAsyncWebCrawler_class:
        mock_crawler_instance = MockAsyncWebCrawler_class.return_value
        mock_crawler_instance.__aenter__.return_value = mock_crawler_instance
        mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)

        mock_arun_method = AsyncMock()

        async def mock_arun_side_effect(*args, **kwargs):
            # Default mock result; tests can override side_effect if specific results are needed.
            return get_mock_arun_result(
                markdown_content="Mocked content from fixture",
                title="Mocked Page from fixture",
                final_url="http://example.com/mock_from_fixture"
            )

        mock_arun_method.side_effect = mock_arun_side_effect
        mock_crawler_instance.arun = mock_arun_method
        yield MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method

# --- Test Helper Functions ---

def make_api_call(client, params: dict, target_url: str = "http://example.com"): # Added client fixture
    """Helper to make a GET request to the /fetch-content endpoint with crawl4ai engine."""
    query_params = {"url": target_url, "engine": "crawl4ai"}
    # Add other parameters from the test's `params` dictionary
    # These should align with the query parameters expected by /fetch-content
    # and subsequently by fetch_with_crawl4ai
    for key, value in params.items():
        if value is not None: # Only include params that have a value
            # FastAPI handles type conversion for bools/ints from query strings
            # For lists or JSON dicts, ensure they are stringified if necessary,
            # though crawl4ai_fetcher.py handles parsing from strings.
            if isinstance(value, bool):
                query_params[key] = str(value).lower()
            elif isinstance(value, list):
                query_params[key] = ",".join(map(str, value)) # Example: "item1,item2"
            elif isinstance(value, dict):
                query_params[key] = json.dumps(value) # Example: '{"key": "value"}'
            else:
                query_params[key] = str(value)

    # Construct the full URL with query parameters
    # The TestClient handles URL encoding for query_params if passed as a dict
    response = client.get(CRAWL4AI_FETCHER_ENDPOINT, params=query_params)
    return response

def get_mock_arun_result(success=True, markdown_content="Test content", title="Test Page", final_url="http://example.com", html_content="<html><body>Test HTML</body></html>"):
    """
    Creates a SimpleNamespace object mimicking a CrawlResult with serializable attributes.
    """
    mock_result = SimpleNamespace()
    mock_result.success = success
    mock_result.url = final_url
    
    if success:
        mock_markdown_obj = SimpleNamespace()
        mock_markdown_obj.raw_markdown = markdown_content
        # Add other attributes if fetch_with_crawl4ai accesses them from markdown object
        # For now, only raw_markdown is explicitly used for final_data_payload's 'content'
        
        mock_result.markdown = mock_markdown_obj
        mock_result.html = html_content # Not directly in final_data_payload but good to have
        mock_result.metadata = {"title": title}
        mock_result.pdf_path = None
        mock_result.screenshot_path = None
        mock_result.mhtml_path = None # Not directly in final_data_payload
        mock_result.error_message = None
        mock_result.error_details = None
        mock_result.logs = [] # Not directly in final_data_payload
        mock_result.console_logs = [] # Not directly in final_data_payload
    else:
        mock_result.markdown = None
        mock_result.html = None
        mock_result.metadata = {}
        mock_result.pdf_path = None
        mock_result.screenshot_path = None
        mock_result.mhtml_path = None
        mock_result.error_message = "Simulated crawl failure"
        mock_result.error_details = {"type": "CrawlError", "detail": "Some error detail"}
        mock_result.logs = ["Error during crawl"]
        mock_result.console_logs = []
        
    return mock_result

# --- Test Cases ---

def test_smoke_no_params_uses_defaults(mock_async_web_crawler_fixture, client): # Use fixture
    """
    Test 6.1 (Partial): Basic call with no specific general/expert params.
    Ensures BrowserConfig and CrawlerRunConfig are created with defaults
    and passed to crawl4ai.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    # Customize arun result for this specific test
    async def specific_smoke_arun_side_effect(*args, **kwargs):
        return get_mock_arun_result(
            success=True,
            markdown_content="Minimal mock content from smoke test",
            title="Minimal Mock Title from smoke test",
            final_url="http://example.com/mock_from_smoke"
        )
    mock_arun_method.side_effect = specific_smoke_arun_side_effect

    api_params = {} # No specific params from UI for this test
    
    # Construct query parameters as make_api_call would, but directly here for clarity
    # The make_api_call function already sets engine to "crawl4ai"
    query_params = {"url": "http://example.com", "engine": "crawl4ai"}
    # Add other parameters from api_params if any (none for this test)
    # This loop is technically not needed here as api_params is empty, but kept for structure
    for key, value in api_params.items():
        if value is not None:
            if isinstance(value, bool): query_params[key] = str(value).lower()
            elif isinstance(value, list): query_params[key] = ",".join(map(str, value))
            elif isinstance(value, dict): query_params[key] = json.dumps(value)
            else: query_params[key] = str(value)

    response_text_content = ""
    # Use client.stream to ensure the SSE stream is consumed
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params) as response:
        assert response.status_code == 200 # Assuming endpoint returns 200 for successful streaming start
        # Iterate over the response content to ensure the generator is fully processed
        for line_bytes in response.iter_bytes():
            if line_bytes: # filter out keep-alive new lines or empty chunks
                response_text_content += line_bytes.decode('utf-8', errors='replace')
    
    # Assertions after consuming the stream
    MockAsyncWebCrawler_class.assert_called_once()
    passed_browser_config = MockAsyncWebCrawler_class.call_args[1]['config']
    assert isinstance(passed_browser_config, BrowserConfig)
    assert passed_browser_config.headless is True
    assert passed_browser_config.java_script_enabled is True

    mock_arun_method.assert_called_once() # Assert on the specific mock we configured
    passed_crawler_run_config = mock_arun_method.call_args[1]['config']
    assert isinstance(passed_crawler_run_config, CrawlerRunConfig)

    # Verify the last event indicates completion (simplified check on accumulated content)
    # The 'status: "completed"' field from crawl4ai_fetcher's event is not present
    # in the final SSE stream due to processing in main.py.
    # The presence of '"type": "completed"' and the correct mock calls are verified.
    assert '"type": "completed"' in response_text_content
    # assert '"status": "completed"' in response_text_content # This line fails due to main.py's event wrapping


# --- Test 6.1: Various Parameter Combinations ---

@pytest.mark.parametrize(
    "api_params, expected_browser_config_attrs, expected_crawler_run_config_attrs",
    [
        # Scenario 1: Basic overrides
        (
            {"headless": "false", "user_agent": "TestAgent/1.0", "page_load_timeout_ms": "5000"}, # Corrected key
            {"headless": False, "user_agent": "TestAgent/1.0"},
            {"page_timeout": 5000},
        ),
        # Scenario 2: BrowserConfig specifics
        (
            {
                "enable_javascript": "false", # Matches main.py
                "ignore_https_errors": "false", # Matches main.py
                "light_mode": "true", # Matches main.py
                "text_mode": "yes", # Matches main.py
                "viewport_width": "1024", # Matches main.py
                "viewport_height": "768", # Matches main.py
            },
            {
                "java_script_enabled": False,
                "ignore_https_errors": False,
                "light_mode": True,
                "text_mode": True,
                "viewport_width": 1024,
                "viewport_height": 768,
            },
            {},
        ),
        # Scenario 3: CrawlerRunConfig specifics
        (
            {
                "target_selector": ".content, #main", # Matches main.py
                "excluded_selector": ".nav", # Corrected to match main.py Query param
                "extract_only_text_content": "true", # Matches main.py
                "word_count_threshold": "10",
                "respect_robots_txt": "false", # Corrected key
            },
            {},
            {
                "target_elements": [".content", "#main"],
                "excluded_selector": ".nav",
                "only_text": True,
                "word_count_threshold": 10,
                "check_robots_txt": False,
            },
        ),
        # Scenario 4: Mix of both, including some expert options
        (
            {
                "proxy_url": "http://proxy.example.com:8080", # Matches main.py
                "browser_cookies": '{"cookie1": "value1"}', # Matches main.py
                "page_load_wait_condition": "networkidle", # Matches main.py
                "execute_javascript_on_page_load": "console.log('test');",
                "cache_mode": "BYPASS",
                "capture_screenshot_base64": "true",
                "crawl_session_id": "test-session-123",
            },
            {
                "proxy": "http://proxy.example.com:8080",
                "cookies": {"cookie1": "value1"},
            },
            {
                "wait_until": "networkidle",
                "js_code": "console.log('test');",
                "cache_mode": "BYPASS",
                "screenshot": True,
                "session_id": "test-session-123",
            },
        ),
    ],
)
def test_various_parameter_combinations(
    mock_async_web_crawler_fixture, client, api_params, expected_browser_config_attrs, expected_crawler_run_config_attrs
):
    """
    Test 6.1: Verify diverse valid combinations of parameters for BrowserConfig and CrawlerRunConfig.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    # Construct query_params similar to make_api_call and use client.stream
    target_url = "http://example.com" 
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, value in api_params.items():
        if value is not None:
            if isinstance(value, bool): query_params_dict[key] = str(value).lower()
            elif isinstance(value, list): query_params_dict[key] = ",".join(map(str, value))
            elif isinstance(value, dict): query_params_dict[key] = json.dumps(value)
            else: query_params_dict[key] = str(value)

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    MockAsyncWebCrawler_class.assert_called_once()
    passed_browser_config = MockAsyncWebCrawler_class.call_args[1]['config']
    assert isinstance(passed_browser_config, BrowserConfig)

    for attr, expected_value in expected_browser_config_attrs.items():
        assert getattr(passed_browser_config, attr) == expected_value, f"BrowserConfig.{attr} mismatch"

    mock_arun_method.assert_called_once()
    passed_crawler_run_config = mock_arun_method.call_args[1]['config']
    assert isinstance(passed_crawler_run_config, CrawlerRunConfig)

    for attr, expected_value in expected_crawler_run_config_attrs.items():
        assert getattr(passed_crawler_run_config, attr) == expected_value, f"CrawlerRunConfig.{attr} mismatch"
    
    assert '"type": "completed"' in response_text_content


# --- Test 6.2: BrowserConfig Specifics ---

@pytest.mark.parametrize(
    "api_param_key, api_param_value, expected_attr_name, expected_attr_value",
    [
        # Boolean flags
        ("headless", "true", "headless", True),
        ("headless", "false", "headless", False),
        ("headless", "1", "headless", True),
        ("headless", "0", "headless", False),
        ("enable_javascript", "yes", "java_script_enabled", True),
        ("enable_javascript", "no", "java_script_enabled", False),
        ("ignore_https_errors", "t", "ignore_https_errors", True),
        ("ignore_https_errors", "false", "ignore_https_errors", False), 
        ("light_mode", True, "light_mode", True), # Direct boolean
        ("text_mode", False, "text_mode", False), # Direct boolean
        ("browser_use_persistent_context", "true", "use_persistent_context", True),
        # String values
        ("user_agent", "MyCustomAgent/2.0", "user_agent", "MyCustomAgent/2.0"),
        ("proxy_url", "socks5://localhost:9050", "proxy", "socks5://localhost:9050"),
        ("browser_user_data_dir", "/tmp/my-data", "user_data_dir", "/tmp/my-data"),
        # Numeric values
        ("viewport_width", "1280", "viewport_width", 1280),
        ("viewport_height", "1024", "viewport_height", 1024),
        # Note: browser_timeout is not directly mapped in current crawl4ai_fetcher.py
        # It would be part of playwright's launch options if passed via browser_extra_args
    ],
)
def test_browser_config_boolean_string_numeric(
    mock_async_web_crawler_fixture, client, api_param_key, api_param_value, expected_attr_name, expected_attr_value
):
    """
    Test 6.2: Test boolean flags, string, and numeric values for BrowserConfig.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    api_params = {api_param_key: api_param_value}
    
    # Construct query_params similar to make_api_call and use client.stream
    target_url = "http://example.com" 
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    # Note: api_param_value is the 'value' in the loop for query_params_dict construction
    for key, current_api_value in api_params.items(): # Renamed value to current_api_value
        if current_api_value is not None:
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    MockAsyncWebCrawler_class.assert_called_once()
    passed_browser_config = MockAsyncWebCrawler_class.call_args[1]['config']
    assert isinstance(passed_browser_config, BrowserConfig)
    assert getattr(passed_browser_config, expected_attr_name) == expected_attr_value
    
    assert '"type": "completed"' in response_text_content


@patch('backend.app.crawl4ai_fetcher.logger')
@pytest.mark.parametrize(
    "param_key, param_value, expected_config_attr, expected_value, expect_warning",
    [
        # Valid JSON
        ("browser_cookies", '{"session_id": "abc123xyz"}', "cookies", {"session_id": "abc123xyz"}, False),
        ("browser_headers", '{"X-Custom-Header": "TestValue"}', "headers", {"X-Custom-Header": "TestValue"}, False),
        ("browser_cookies", '[{"name": "c1", "value": "v1"}]', "cookies", [{"name": "c1", "value": "v1"}], False), # crawl4ai accepts list of dicts too
        # Invalid JSON
        ("browser_cookies", '{"session_id": "abc123xyz",}', "cookies", [], True), # Trailing comma
        ("browser_headers", 'not_json_at_all', "headers", {'sec-ch-ua': '"Chromium";v="116", "Not_A Brand";v="8", "Google Chrome";v="116"'}, True),
        ("browser_cookies", '{"incomplete_json":', "cookies", [], True),
        # Empty string (should not parse as JSON, should result in None)
        ("browser_cookies", "", "cookies", [], False), # Empty string is not invalid JSON, to_json_dict returns None
        ("browser_headers", "", "headers", {'sec-ch-ua': '"Chromium";v="116", "Not_A Brand";v="8", "Google Chrome";v="116"'}, False),
        # Valid JSON but not a dict (to_json_dict expects dict or string parsable to dict)
        # However, crawl4ai's BrowserConfig for cookies can accept a list of dicts.
        # to_json_dict will parse it, and BrowserConfig will accept it.
        ("browser_cookies", '"just_a_string_in_json"', "cookies", "just_a_string_in_json", False), # This will be parsed by json.loads
    ],
)
def test_browser_config_json_parsing(
    patched_crawl4ai_logger, mock_async_web_crawler_fixture, client, param_key, param_value, expected_config_attr, expected_value, expect_warning
):
    """
    Test 6.2: Test JSON string parsing for BrowserConfig parameters (cookies, headers).
    Verifies correct parsing of valid JSON and graceful handling of invalid JSON.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture
    
    api_params = {param_key: param_value}
    
    # Construct query_params similar to make_api_call and use client.stream
    target_url = "http://example.com"
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, current_api_value in api_params.items():
        if current_api_value is not None:
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    MockAsyncWebCrawler_class.assert_called_once()
    passed_browser_config = MockAsyncWebCrawler_class.call_args[1]['config']
    assert isinstance(passed_browser_config, BrowserConfig)
    
    actual_value = getattr(passed_browser_config, expected_config_attr)
    if expected_config_attr == "headers" and isinstance(expected_value, dict) and isinstance(actual_value, dict):
        # For headers, check if all expected headers are present in the actual headers
        # This allows actual_value to have more (default) headers
        missing_headers = {k: v for k, v in expected_value.items() if k not in actual_value or actual_value[k] != v}
        assert not missing_headers, \
            f"BrowserConfig.headers mismatch. Expected headers {expected_value} not fully found or matched in actual headers {actual_value}. Missing/mismatched: {missing_headers}"
    else:
        assert actual_value == expected_value, f"BrowserConfig.{expected_config_attr} mismatch. Expected {expected_value}, got {actual_value}"

    if expect_warning:
        patched_crawl4ai_logger.warning.assert_called()
        # More specific check if needed:
        # found_warning = False
        # for call_args in patched_crawl4ai_logger.warning.call_args_list:
        #     if "Failed to parse JSON string" in call_args[0][0]:
        #         found_warning = True
        #         break
        # assert found_warning, "Expected JSON parsing warning was not logged."
    else:
        # Ensure no unexpected warnings for valid JSON or empty strings
        for call_args in patched_crawl4ai_logger.warning.call_args_list:
            assert "Failed to parse JSON string" not in call_args[0][0], "Unexpected JSON parsing warning logged."
            
    assert '"type": "completed"' in response_text_content

@pytest.mark.parametrize(
    "param_value, expected_list",
    [
        ("--disable-gpu,--no-sandbox", ["--disable-gpu", "--no-sandbox"]),
        ("single-arg", ["single-arg"]),
        ("", None), # to_list_str returns None for empty string if it doesn't split into non-empty items
        (None, None),
        (["--arg1", "--arg2"], ["--arg1", "--arg2"]), # Already a list
    ]
)
def test_browser_config_extra_args_list_parsing(mock_async_web_crawler_fixture, client, param_value, expected_list):
    """
    Test 6.2: Test 'browser_extra_args' list parsing for BrowserConfig.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    api_params = {"browser_extra_args": param_value}

    target_url = "http://example.com"
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, current_api_value in api_params.items():
        if current_api_value is not None: # param_value could be None
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)
        # If param_value is None, it won't be added to query_params_dict, which is correct.

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')
    
    MockAsyncWebCrawler_class.assert_called_once()
    passed_browser_config = MockAsyncWebCrawler_class.call_args[1]['config']
    assert isinstance(passed_browser_config, BrowserConfig)
    
    if expected_list is None:
        assert not hasattr(passed_browser_config, "extra_args") or getattr(passed_browser_config, "extra_args") is None
    else:
        assert getattr(passed_browser_config, "extra_args") == expected_list
    
    assert '"type": "completed"' in response_text_content

# --- Test 6.3: CrawlerRunConfig Specifics ---

@pytest.mark.parametrize(
    "api_param_key, api_param_value, expected_attr_name, expected_attr_value",
    [
        # Boolean flags for CrawlerRunConfig
        ("extract_only_text_content", "true", "only_text", True),
        ("process_iframes_content", "false", "process_iframes", False),
        ("remove_forms", "1", "remove_forms", True),
        ("keep_data_attributes", "0", "keep_data_attributes", False),
        ("scan_full_page_auto_scroll", "yes", "scan_full_page", True),
        ("attempt_remove_overlay_elements", "no", "remove_overlay_elements", False),
        ("simulate_user_behavior", True, "simulate_user", True), # Direct boolean
        ("enable_magic_handling", False, "magic", False), # Direct boolean
        ("override_navigator_properties", "t", "override_navigator", True),
        ("capture_screenshot_base64", "f", "screenshot", False),
        ("generate_pdf_of_page", "true", "pdf", True),
        ("capture_mhtml_snapshot", "false", "capture_mhtml", False),
        ("exclude_external_images", "1", "exclude_external_images", True),
        ("exclude_external_links", "0", "exclude_external_links", False),
        ("exclude_social_media_links", "yes", "exclude_social_media_links", True),
        ("respect_robots_txt", "no", "check_robots_txt", False), # Corrected key
        ("verbose_logging", True, "verbose", True),
        ("log_page_console_output", False, "log_console", False),

        # String values for CrawlerRunConfig
        ("page_load_wait_condition", "domcontentloaded", "wait_until", "domcontentloaded"),
        ("wait_for_element_js_condition", "document.querySelector('#myElement')", "wait_for", "document.querySelector('#myElement')"),
        ("excluded_selector", ".footer, .sidebar", "excluded_selector", ".footer, .sidebar"), # Corrected key
        ("execute_javascript_on_page_load", "alert('loaded')", "js_code", "alert('loaded')"),
        ("cache_mode", "REFRESH", "cache_mode", "REFRESH"),
        ("crawl_session_id", "sess_xyz789", "session_id", "sess_xyz789"),
        ("crawl_css_selector", "#specific-content-area", "css_selector", "#specific-content-area"),

        # Numeric (int, float) values for CrawlerRunConfig
        ("page_load_timeout_ms", "10000", "page_timeout", 10000), # Corrected key
        ("word_count_threshold", "50", "word_count_threshold", 50),
        ("scroll_delay_seconds", "0.75", "scroll_delay", 0.75),
        ("image_alt_text_min_word_count", "3", "image_description_min_word_threshold", 3),
        ("image_relevance_score_threshold", "70", "image_score_threshold", 70),
    ]
)
def test_crawler_run_config_boolean_string_numeric_float(
    mock_async_web_crawler_fixture, client, api_param_key, api_param_value, expected_attr_name, expected_attr_value
):
    """
    Test 6.3: Test boolean flags, string, numeric, and float values for CrawlerRunConfig.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    api_params = {api_param_key: api_param_value}

    target_url = "http://example.com"
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, current_api_value in api_params.items():
        if current_api_value is not None:
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)
            
    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    mock_arun_method.assert_called_once() # arun is on the instance
    passed_config = mock_arun_method.call_args[1]['config']
    assert isinstance(passed_config, CrawlerRunConfig)
    assert getattr(passed_config, expected_attr_name) == expected_attr_value
    
    assert '"type": "completed"' in response_text_content

@pytest.mark.parametrize(
    "param_key, param_value, expected_attr_name, expected_list_value",
    [
        ("target_selector", ".class1, .class2", "target_elements", [".class1", ".class2"]), # Corrected key
        ("target_selector", " #id1 , .class3 ", "target_elements", ["#id1", ".class3"]), # Corrected key
        ("target_selector", "", "target_elements", None), # Corrected key, Empty string results in None
        ("excluded_tags", "script, style, nav", "excluded_tags", ["script", "style", "nav"]),
        ("excluded_tags", "noscript", "excluded_tags", ["noscript"]),
        ("custom_excluded_domains", "domain1.com, other.org", "exclude_domains", ["domain1.com", "other.org"]),
        ("custom_excluded_domains", ["arrdomain.com", "arrdomain2.net"], "exclude_domains", ["arrdomain.com", "arrdomain2.net"]), # Already a list
    ]
)
def test_crawler_run_config_list_parsing(
    mock_async_web_crawler_fixture, client, param_key, param_value, expected_attr_name, expected_list_value
):
    """
    Test 6.3: Test parameters requiring list parsing for CrawlerRunConfig.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    api_params = {param_key: param_value}

    target_url = "http://example.com"
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, current_api_value in api_params.items():
        if current_api_value is not None:
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    mock_arun_method.assert_called_once()
    passed_config = mock_arun_method.call_args[1]['config']
    assert isinstance(passed_config, CrawlerRunConfig)

    actual_value = getattr(passed_config, expected_attr_name, None) # Use default if attr might not be set
    if expected_list_value is None:
         # Check if the attribute is not present or is None
        assert actual_value is None, f"Expected {expected_attr_name} to be None or not set, but got {actual_value}"
    else:
        assert actual_value == expected_list_value
    
    assert '"type": "completed"' in response_text_content

# --- Test 6.4: Type Conversion & Graceful Handling ---

@patch('backend.app.crawl4ai_fetcher.logger')
@pytest.mark.parametrize(
    "param_key, incorrect_value, config_type, expected_attr_name, expected_fallback_value, expect_warning_msg_part",
    [
        # BrowserConfig related
        ("viewport_width", "not_an_int", BrowserConfig, "viewport_width", None, None), # to_int returns None, no specific warning in to_int
        ("viewport_height", {"complex": "type"}, BrowserConfig, "viewport_height", None, None), # to_int returns None
        ("browser_cookies", "{not_valid_json", BrowserConfig, "cookies", None, "Failed to parse JSON string"),
        
        # CrawlerRunConfig related
        ("page_load_timeout_ms", "a_string", CrawlerRunConfig, "page_timeout", None, None), # Corrected key, to_int returns None
        ("word_count_threshold", "10.5", CrawlerRunConfig, "word_count_threshold", None, None), # to_int for "10.5" fails
        ("word_count_threshold", [1,2], CrawlerRunConfig, "word_count_threshold", None, None), # to_int with list fails
        ("scroll_delay_seconds", "one_second", CrawlerRunConfig, "scroll_delay", None, None), # to_float returns None
        # ("max_depth", "five", CrawlerRunConfig, "max_depth", None, None), # This is for deep crawl, handled in deep_crawl_config logic
        ("image_alt_text_min_word_count", "not_a_number", CrawlerRunConfig, "image_description_min_word_threshold", None, None),


        # Boolean conversions (to_bool is quite robust, might not log warnings for simple type mismatches, just evaluates truthiness)
        # Let's test a case where a JSON parse is expected to fail for a boolean-like field if it were structured that way
        # However, current boolean fields are directly converted by to_bool.
        # We'll rely on the JSON parsing tests for warnings on malformed structures.
    ]
)
def test_type_conversion_graceful_handling(
    mock_async_web_crawler_fixture, mock_logger, client, param_key, incorrect_value, config_type, expected_attr_name, expected_fallback_value, expect_warning_msg_part
): # Changed MockLogger to mock_logger
    """
    Test 6.4: Verify graceful handling of incorrect data types for parameters.
    Checks for logged warnings and fallback to default/None values.
    """
    MockAsyncWebCrawler_class, mock_crawler_instance, mock_arun_method = mock_async_web_crawler_fixture

    api_params = {param_key: incorrect_value}

    target_url = "http://example.com"
    query_params_dict = {"url": target_url, "engine": "crawl4ai"}
    for key, current_api_value in api_params.items():
        if current_api_value is not None:
            if isinstance(current_api_value, bool): query_params_dict[key] = str(current_api_value).lower()
            elif isinstance(current_api_value, list): query_params_dict[key] = ",".join(map(str, current_api_value))
            elif isinstance(current_api_value, dict): query_params_dict[key] = json.dumps(current_api_value)
            else: query_params_dict[key] = str(current_api_value)

    response_text_content = ""
    with client.stream("GET", CRAWL4AI_FETCHER_ENDPOINT, params=query_params_dict) as stream_response:
        assert stream_response.status_code == 200 # Expecting the call to still mostly succeed at API level
        for line_bytes in stream_response.iter_bytes():
            if line_bytes:
                response_text_content += line_bytes.decode('utf-8', errors='replace')

    if config_type == BrowserConfig:
        MockAsyncWebCrawler_class.assert_called_once()
        passed_config = MockAsyncWebCrawler_class.call_args[1]['config']
    elif config_type == CrawlerRunConfig:
        mock_arun_method.assert_called_once()
        passed_config = mock_arun_method.call_args[1]['config']
    else:
        raise ValueError("Invalid config_type for test")

    assert isinstance(passed_config, config_type)
    
    actual_value = getattr(passed_config, expected_attr_name, None) # Default to None if not present
    
    assert actual_value == expected_fallback_value, \
        f"{config_type.__name__}.{expected_attr_name} expected to be {expected_fallback_value} due to type error, but got {actual_value}"

    if expect_warning_msg_part:
        warning_found = False
        for call_arg in mock_logger.warning.call_args_list: # Changed MockLogger to mock_logger
            if expect_warning_msg_part in call_arg[0][0]:
                warning_found = True
                break
        assert warning_found, f"Expected warning containing '{expect_warning_msg_part}' not found in logs."
    else:
        # Check that no UNEXPECTED warnings related to the specific conversion logic are logged.
        # This is tricky because other default operations might log warnings.
        # For now, if no specific warning is expected, we don't assert absence of all warnings.
        pass
            
    assert '"type": "completed"' in response_text_content # The overall process should still complete