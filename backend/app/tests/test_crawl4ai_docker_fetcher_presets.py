import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
import uuid
from datetime import datetime, timezone

from backend.app.crawl4ai_docker_fetcher import fetch_with_crawl4ai_docker, BACKEND_SERVICE_URL
from crawl4ai import BrowserConfig, CrawlerRunConfig, CrawlResult
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy, LLMConfig
from crawl4ai.deep_crawl_strategy import BFSDeepCrawlStrategy
from crawl4ai.filter import FilterChain, UrlFilter
from crawl4ai.markdown_generator import DefaultMarkdownGenerator, MarkdownGeneratorConfig
from crawl4ai.utils import ConfigError


# --- Helper Function to Create Mock Preset API Response ---
def create_mock_preset_response_data(preset_id, strategy_definition, name="Test Preset"):
    return {
        "preset_id": str(preset_id),
        "preset_name": name,
        "description": "A test preset description",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": strategy_definition,
        "target_capability": "web_research",
        "tags": ["test", "example"],
        "created_by": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

# --- Mock CrawlResult ---
def mock_crawl_result(url="http://example.com", html_content="<html><body>Mocked content</body></html>", success=True):
    return CrawlResult(
        url=url,
        html_content=html_content,
        markdown_content=html_content, # simplified for mock
        success=success,
        screenshot_path=None,
        metadata={},
        extracted_data=None,
        links=[],
        error_message=None if success else "Simulated crawl error"
    )

# --- Tests ---

@pytest.mark.asyncio
async def test_fetch_with_basic_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/basic"

    mock_strategy_def = {
        "browser_config": {"params": {"headless": False, "user_agent": "PresetTestAgent1"}},
        "run_config": {"params": {"screenshot": True, "page_timeout": 60000}}
    }
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)

    # Mock Presets API response
    # Ensure the URL matches how it's constructed in crawl4ai_docker_fetcher.py
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]

        request_params = {"preset_id": str(preset_id)}

        results = []
        async for result_event_str in fetch_with_crawl4ai_docker(target_url, request_params):
            results.append(json.loads(result_event_str))

        mock_docker_crawl.assert_called_once()
        args, kwargs = mock_docker_crawl.call_args

        passed_browser_config: BrowserConfig = kwargs.get("browser_config")
        assert isinstance(passed_browser_config, BrowserConfig)
        assert passed_browser_config.headless is False
        assert passed_browser_config.user_agent == "PresetTestAgent1"

        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert isinstance(passed_crawler_config, CrawlerRunConfig)
        assert passed_crawler_config.screenshot is True
        assert passed_crawler_config.page_timeout == 60000

        # Check that the final event stream contains the crawl_result
        assert any(r.get("type") == "crawl_result" for r in results)
        assert results[-1].get("type") == "completed" # Last event should be 'completed'


@pytest.mark.asyncio
async def test_fetch_with_extraction_strategy_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/extract"
    mock_strategy_def = {
        "extraction_strategy": {
            "type": "JsonCssExtractionStrategy",
            "params": {
                "schema_name": "product_details",
                "schema_definition": {"title": {"css_selector": "h1", "type": "text"}}
            }
        }
    }
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass # Consume generator

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert isinstance(passed_crawler_config.extraction_strategy, JsonCssExtractionStrategy)
        assert passed_crawler_config.extraction_strategy.schema_name == "product_details"
        assert "title" in passed_crawler_config.extraction_strategy.schema_definition


@pytest.mark.asyncio
async def test_fetch_with_deep_crawl_strategy_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/deep"
    mock_strategy_def = {
        "deep_crawl_strategy": {
            "type": "BFSDeepCrawlStrategy",
            "params": {
                "max_depth": 2,
                "url_filters": [{"type": "UrlFilter", "params": {"allowed_domains": ["example.com"]}}]
            }
        }
    }
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert isinstance(passed_crawler_config.deep_crawl_strategy, BFSDeepCrawlStrategy)
        assert passed_crawler_config.deep_crawl_strategy.max_depth == 2
        assert isinstance(passed_crawler_config.deep_crawl_strategy.url_filters, FilterChain)
        assert len(passed_crawler_config.deep_crawl_strategy.url_filters.filters) == 1
        assert isinstance(passed_crawler_config.deep_crawl_strategy.url_filters.filters[0], UrlFilter)


@pytest.mark.asyncio
async def test_fetch_with_markdown_generator_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/markdown"
    mock_strategy_def = {
        "markdown_generator_config": {
            "params": {
                "html2text_options": {"bypass_tables": True},
                "content_filter": {"type": "SimpleWordCountFilter", "params": {"min_words": 10}}
            }
        }
    }
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert isinstance(passed_crawler_config.markdown_generator, DefaultMarkdownGenerator)
        assert passed_crawler_config.markdown_generator.config.html2text_options.get("bypass_tables") is True
        assert passed_crawler_config.markdown_generator.config.content_filter is not None # Further checks if needed


@pytest.mark.asyncio
async def test_fetch_fallback_to_flat_params(httpx_mock):
    target_url = "http://example.com/flat"
    # No preset_id in request_params, so no API call to mock for presets

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]

        # These are "flat" parameters passed directly in the request
        request_params = {
            "headless": "false", # Note: params from query are strings
            "user_agent": "FlatParamAgent",
            "screenshot": "true",
            "page_timeout": "45000"
        }

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args

        passed_browser_config: BrowserConfig = kwargs.get("browser_config")
        assert passed_browser_config.headless is False # Verifies string "false" is parsed to bool
        assert passed_browser_config.user_agent == "FlatParamAgent"

        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert passed_crawler_config.screenshot is True
        assert passed_crawler_config.page_timeout == 45000 # Verifies string "45000" is parsed to int


@pytest.mark.asyncio
async def test_fetch_preset_overrides_direct_strategy_definition(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/override"

    # Preset defines headless: True
    preset_strategy_def = {"browser_config": {"params": {"headless": True, "user_agent": "PresetAgent"}}}
    preset_api_response = create_mock_preset_response_data(preset_id, preset_strategy_def)
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    # Direct strategy_definition (as a string, like from query param) defines headless: False
    direct_strategy_def_str = json.dumps({
        "browser_config": {"params": {"headless": False, "user_agent": "DirectAgent"}}
    })

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]

        request_params = {
            "preset_id": str(preset_id),
            "strategy_definition": direct_strategy_def_str # This should be ignored in favor of preset
        }

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_browser_config: BrowserConfig = kwargs.get("browser_config")
        assert passed_browser_config.headless is True # Preset's value (True) should take precedence
        assert passed_browser_config.user_agent == "PresetAgent"


@pytest.mark.asyncio
async def test_fetch_preset_not_found(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/notfound"

    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, status_code=404, json={"detail": "Preset not found"})

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        # The crawl client should ideally not be called if preset fetch fails critically.
        # The fetcher might proceed with default/flat params or raise an error.
        # Current fetcher logs error and proceeds with defaults/flat params.
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)] # Mock it just in case

        request_params = {"preset_id": str(preset_id)}

        results = []
        async for result_event_str in fetch_with_crawl4ai_docker(target_url, request_params):
            results.append(json.loads(result_event_str))

        # Assert that the crawl still happened (with default config)
        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_browser_config: BrowserConfig = kwargs.get("browser_config")
        # Check for default user_agent or headless state if applicable
        assert passed_browser_config.user_agent is not None # Default user agent from crawl4ai

        # Check for status message indicating preset fetch failure
        assert any("Failed to fetch preset" in r.get("message", "") and r.get("type") == "status" for r in results)


@pytest.mark.asyncio
async def test_fetch_preset_api_error(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/api_error"

    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, status_code=500, json={"detail": "Internal Server Error"})

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        results = []
        async for result_event_str in fetch_with_crawl4ai_docker(target_url, request_params):
            results.append(json.loads(result_event_str))

        mock_docker_crawl.assert_called_once() # Still proceeds with default config
        # Check for status message indicating preset API error
        assert any("Error fetching preset" in r.get("message", "") and r.get("type") == "status" for r in results)

@pytest.mark.asyncio
async def test_fetch_with_llm_extraction_strategy_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/llm_extract"
    mock_strategy_def = {
        "extraction_strategy": {
            "type": "LLMExtractionStrategy",
            "params": {
                "llm_config": {"provider": "openai", "model": "gpt-3.5-turbo", "api_key": "test_key"},
                "schema_name": "summary_points",
                "schema_definition": {"summary": "text", "key_points": ["text"]}
            }
        }
    }
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)
    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        async for _ in fetch_with_crawl4ai_docker(target_url, request_params):
            pass

        mock_docker_crawl.assert_called_once()
        _, kwargs = mock_docker_crawl.call_args
        passed_crawler_config: CrawlerRunConfig = kwargs.get("crawler_config")
        assert isinstance(passed_crawler_config.extraction_strategy, LLMExtractionStrategy)
        assert isinstance(passed_crawler_config.extraction_strategy.llm_config, LLMConfig)
        assert passed_crawler_config.extraction_strategy.llm_config.model == "gpt-3.5-turbo"
        assert passed_crawler_config.extraction_strategy.schema_name == "summary_points"


@pytest.mark.asyncio
async def test_invalid_strategy_definition_in_preset(httpx_mock):
    preset_id = uuid.uuid4()
    target_url = "http://example.com/invalid_preset"

    # Invalid: "browser_config" should be a dict, not a string
    mock_strategy_def = {"browser_config": "this-is-wrong"}
    preset_api_response = create_mock_preset_response_data(preset_id, mock_strategy_def)

    presets_api_url = f"{BACKEND_SERVICE_URL.rstrip('/')}/api/presets/{preset_id}"
    httpx_mock.add_response(url=presets_api_url, json=preset_api_response)

    with patch("backend.app.crawl4ai_docker_fetcher.Crawl4aiDockerClient.crawl", new_callable=AsyncMock) as mock_docker_crawl:
        mock_docker_crawl.return_value = [mock_crawl_result(url=target_url)]
        request_params = {"preset_id": str(preset_id)}

        results = []
        # Expect ConfigError to be caught and reported as a status message
        async for result_event_str in fetch_with_crawl4ai_docker(target_url, request_params):
            results.append(json.loads(result_event_str))

        # Crawl should still proceed with default configurations
        mock_docker_crawl.assert_called_once()

        # Check for status message indicating configuration error from preset
        assert any("Error applying strategy definition from preset" in r.get("message", "") and r.get("type") == "status" for r in results)

```
