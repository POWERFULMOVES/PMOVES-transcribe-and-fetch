import pytest
from unittest.mock import AsyncMock, patch, ANY

from crawl4ai import DefaultMarkdownGenerator, CrawlResult
from crawl4ai.markdown_generation_strategy import MarkdownGenerationResult as Crawl4aiMarkdownResult

@pytest.mark.asyncio
@patch("app.crawl4ai_fetcher.AsyncWebCrawler.arun", new_callable=AsyncMock)
async def test_markdown_generator_default(mock_arun, async_client):
    mock_arun.return_value = CrawlResult(
        success=True, url="http://example.com", html="<html></html>",
        markdown=Crawl4aiMarkdownResult(raw_markdown="Mocked content", markdown_with_citations="Mocked content", references_markdown=""),
        metadata={"title": "Mocked Title"}, error_message=None, error_details=None,
        pdf_path=None, screenshot_path=None, mhtml_path=None, logs=[], console_logs=[]
    )
    response = await async_client.get(
        "/fetch-content",
        params={"url": "http://example.com", "engine": "crawl4ai", "crawl4ai_markdown_generator": "Default"}
    )
    assert response.status_code == 200
    mock_arun.assert_called_once()
    assert mock_arun.call_args is not None
    config_passed_to_arun = mock_arun.call_args.kwargs.get('config') or (mock_arun.call_args.args[0] if mock_arun.call_args.args else None)
    assert config_passed_to_arun is not None, "Config not passed to arun"
    assert isinstance(config_passed_to_arun.markdown_generator, DefaultMarkdownGenerator)

@pytest.mark.asyncio
@patch("app.crawl4ai_fetcher.AsyncWebCrawler.arun", new_callable=AsyncMock)
@patch("app.crawl4ai_fetcher.logger.warning") # This mock is for the logger instance in crawl4ai_fetcher module
async def test_markdown_generator_empty_or_none(mock_fetcher_logger_warning, mock_arun, async_client, markdown_generator_value):
    mock_arun.return_value = CrawlResult(
        success=True, url="http://example.com", html="<html></html>",
        markdown=Crawl4aiMarkdownResult(raw_markdown="Mocked content", markdown_with_citations="Mocked content", references_markdown=""),
        metadata={"title": "Mocked Title"}, error_message=None, error_details=None,
        pdf_path=None, screenshot_path=None, mhtml_path=None, logs=[], console_logs=[]
    )
    current_test_params = {"url": "http://example.com", "engine": "crawl4ai"}
    if markdown_generator_value == "":
        current_test_params["crawl4ai_markdown_generator"] = ""
    elif markdown_generator_value is None:
        pass # Omit for None/missing

    response = await async_client.get("/fetch-content", params=current_test_params)
    assert response.status_code == 200
    mock_arun.assert_called_once()
    mock_fetcher_logger_warning.assert_not_called() # No warning for valid empty/None
    assert mock_arun.call_args is not None
    config_passed_to_arun = mock_arun.call_args.kwargs.get('config') or (mock_arun.call_args.args[0] if mock_arun.call_args.args else None)
    assert config_passed_to_arun is not None, "Config not passed to arun"
    assert config_passed_to_arun.markdown_generator is None

@pytest.mark.asyncio
@patch("app.crawl4ai_fetcher.AsyncWebCrawler.arun", new_callable=AsyncMock)
@patch("app.crawl4ai_fetcher.logger") # Patch the logger object used in crawl4ai_fetcher
async def test_markdown_generator_unknown(mock_fetcher_logger, mock_arun, async_client):
    mock_arun.return_value = CrawlResult(
        success=True, url="http://example.com", html="<html></html>",
        markdown=Crawl4aiMarkdownResult(raw_markdown="Mocked content", markdown_with_citations="Mocked content", references_markdown=""),
        metadata={"title": "Mocked Title"}, error_message=None, error_details=None,
        pdf_path=None, screenshot_path=None, mhtml_path=None, logs=[], console_logs=[]
    )
    response = await async_client.get(
        "/fetch-content",
        params={"url": "http://example.com", "engine": "crawl4ai", "crawl4ai_markdown_generator": "UnknownGenerator"}
    )
    assert response.status_code == 200
    mock_fetcher_logger.warning.assert_called_once() # Assert on the 'warning' method of the patched logger
    args, _ = mock_fetcher_logger.warning.call_args
    assert "Unknown markdown_generator" in args[0]
    assert "UnknownGenerator" in args[0]
    mock_arun.assert_called_once()
    assert mock_arun.call_args is not None
    config_passed_to_arun = mock_arun.call_args.kwargs.get('config') or (mock_arun.call_args.args[0] if mock_arun.call_args.args else None)
    assert config_passed_to_arun is not None, "Config not passed to arun"
    assert config_passed_to_arun.markdown_generator is None

# Parametrize test_markdown_generator_empty_or_none separately for clarity
test_markdown_generator_empty_or_none = pytest.mark.parametrize(
    "markdown_generator_value",
    [
        "",     # Empty string
        None,   # Represents missing or explicit None
    ]
)(test_markdown_generator_empty_or_none)