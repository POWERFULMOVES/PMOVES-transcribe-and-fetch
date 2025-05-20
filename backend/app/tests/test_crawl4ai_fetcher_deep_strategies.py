from fastapi.testclient import TestClient
import pytest
import logging # Added for caplog level setting
from unittest.mock import patch, MagicMock, ANY, AsyncMock
from typing import Optional

# TestClient and app will be provided by the conftest.py fixture
from crawl4ai import (
    BFSDeepCrawlStrategy,
    DFSDeepCrawlStrategy,
    BestFirstCrawlingStrategy,
    FilterChain,
    URLPatternFilter,
    KeywordRelevanceScorer,
    CrawlerRunConfig,
    CrawlResult # For mocking arun return
)
from crawl4ai.markdown_generation_strategy import MarkdownGenerationResult # For mocking arun return

# client fixture is now in conftest.py

@pytest.fixture
def mock_arun():
    with patch("crawl4ai.AsyncWebCrawler.arun", new_callable=AsyncMock) as mock_async_arun:
        # Simulate a successful crawl result
        mock_crawl_result = CrawlResult(
            success=True,
            url="http://example.com",
            html="<html><body>Mocked HTML content</body></html>",
            markdown=MarkdownGenerationResult(
                raw_markdown="mocked content",
                markdown_with_citations="mocked content",
                references_markdown="",
                fit_markdown=None,
                fit_html=None
            ),
            metadata={"title": "Mocked Title"},
            error_message=None,
            error_details=None,
            screenshot_path=None,
            pdf_path=None,
            mhtml_path=None,
            logs=[],
            console_logs=[]
        )
        # Set the return value for the AsyncMock. When awaited, it will return this.
        mock_async_arun.return_value = mock_crawl_result
        yield mock_async_arun

# Removed mock_logger_warning, mock_logger_info, mock_logger_error fixtures
# as they will be replaced by caplog.

# Test 4.1: Strategy Instantiation (BFS/DFS/BestFirst)
@pytest.mark.parametrize(
    "strategy_name, strategy_class, params_in, expected_params_subset",
    [
        ("BFSDeepCrawlStrategy", BFSDeepCrawlStrategy, {"max_depth": 3, "max_pages": 10}, {"max_depth": 3, "max_pages": 10}),
        ("DFSDeepCrawlStrategy", DFSDeepCrawlStrategy, {"max_depth": 2, "max_pages": 5, "include_external": True}, {"max_depth": 2, "max_pages": 5, "include_external": True}),
        ("BestFirstCrawlingStrategy", BestFirstCrawlingStrategy, {"max_depth": 1, "max_pages": 3, "url_scorer_type": "KeywordRelevanceScorer", "scorer_keywords": "test,data"}, {"max_depth": 1, "max_pages": 3}), # Scorer tested separately
    ],
)
async def test_deep_crawl_strategy_instantiation(
    client: TestClient, mock_arun: AsyncMock, strategy_name: str, strategy_class: type, params_in: dict, expected_params_subset: dict
):
    api_query_params = {
        "url": "http://example.com",
        "engine": "crawl4ai",
        "deep_crawl_strategy_name": strategy_name,
    }
    for key, value in params_in.items():
        query_key = f"deep_crawl_{key}"
        api_query_params[query_key] = value
    
    response = client.get("/fetch-content", params=api_query_params)
    response.read() # Ensure the response is fully read for TestClient

    assert response.status_code == 200
    mock_arun.assert_called_once()
    
    # Inspect the arguments passed to arun
    call_args = mock_arun.call_args
    assert call_args is not None
    
    # The deep_crawl_strategy is now passed as a direct keyword argument to arun
    deep_crawl_strategy = call_args.kwargs.get('deep_crawl_strategy')
    
    assert deep_crawl_strategy is not None, "deep_crawl_strategy not found in arun call kwargs"
    assert isinstance(deep_crawl_strategy, strategy_class)
    
    for key, value in expected_params_subset.items():
        assert getattr(deep_crawl_strategy, key) == value, f"Mismatch for param {key}"

# Test 4.2: FilterChain Integration
async def test_filter_chain_integration(client: TestClient, mock_arun: AsyncMock, caplog): # Replaced mock_logger_info with caplog
    caplog.set_level(logging.INFO) # Ensure INFO messages are captured

    filter_regexes_list = ["http://example.com/allowed/.*", "http://another.com/.*"]
    api_query_params = {
        "url": "http://example.com",
        "engine": "crawl4ai",
        "deep_crawl_strategy_name": "BestFirstCrawlingStrategy", # Could be any strategy that accepts filter_chain
        "deep_crawl_max_depth": 1,
        "deep_crawl_filter_regexes": ",".join(filter_regexes_list),
        # Need a scorer for BestFirst, even if dummy for this test focus
        "deep_crawl_url_scorer_type": "KeywordRelevanceScorer",
        "deep_crawl_scorer_keywords": "dummy"
    }
    response = client.get("/fetch-content", params=api_query_params)
    response.read()

    assert response.status_code == 200
    mock_arun.assert_called_once()
    
    call_args = mock_arun.call_args
    assert call_args is not None
    deep_crawl_strategy = call_args.kwargs.get('deep_crawl_strategy')

    assert deep_crawl_strategy is not None, "deep_crawl_strategy not found in arun call kwargs"
    assert isinstance(deep_crawl_strategy.filter_chain, FilterChain)
    assert len(deep_crawl_strategy.filter_chain.filters) == 1
    assert isinstance(deep_crawl_strategy.filter_chain.filters[0], URLPatternFilter)
    
    # Check if the patterns were correctly passed to URLPatternFilter
    # The actual patterns are stored as compiled regex objects in URLPatternFilter
    # We can check if the logger message indicates correct creation
    # Or, if URLPatternFilter stores the original strings, check that.
    # For now, let's assume the instance check is primary.
    # We can also check the log message for "Created FilterChain with URLPatternFilter using regexes"
    
    found_log = False
    expected_log_substring = f"Created FilterChain with URLPatternFilter using regexes: {filter_regexes_list}"
    for record in caplog.records:
        if record.levelname == "INFO" and expected_log_substring in record.message:
            found_log = True
            break
    assert found_log, f"Log message for FilterChain creation with correct regexes not found. Expected substring: '{expected_log_substring}' in any INFO log. Captured text: {caplog.text}"
    
    # Verify the patterns in the filter directly if possible (depends on URLPatternFilter impl)
    # url_pattern_filter_instance = deep_crawl_strategy.filter_chain.filters[0]
    # This requires knowing how URLPatternFilter stores its patterns.
    # Assuming it has a 'patterns' attribute that stores the compiled regex objects
    # and we want to check the original strings if they were stored or reconstructable.
    # For simplicity, the log check is a good indirect verification.


# Test 4.3: KeywordRelevanceScorer Integration
async def test_keyword_relevance_scorer_integration(client: TestClient, mock_arun: AsyncMock, caplog): # Replaced mock_logger_info with caplog
    caplog.set_level(logging.INFO) # Ensure INFO messages are captured

    keywords_list = ["important", "relevant", "test"]
    api_query_params = {
        "url": "http://example.com",
        "engine": "crawl4ai",
        "deep_crawl_strategy_name": "BestFirstCrawlingStrategy",
        "deep_crawl_max_depth": 1,
        "deep_crawl_url_scorer_type": "KeywordRelevanceScorer",
        "deep_crawl_scorer_keywords": ",".join(keywords_list), # Passed as comma-separated string
    }
    response = client.get("/fetch-content", params=api_query_params)
    response.read()

    assert response.status_code == 200
    mock_arun.assert_called_once()
    
    call_args = mock_arun.call_args
    assert call_args is not None
    deep_crawl_strategy = call_args.kwargs.get('deep_crawl_strategy')
        
    assert deep_crawl_strategy is not None, "deep_crawl_strategy not found in arun call kwargs"
    assert isinstance(deep_crawl_strategy.url_scorer, KeywordRelevanceScorer)
    
    # Check if the keywords were correctly passed
    # KeywordRelevanceScorer stores them in a '_keywords' attribute (set of strings)
    assert set(deep_crawl_strategy.url_scorer._keywords) == set(keywords_list), \
        f"Expected keywords {set(keywords_list)}, but got {deep_crawl_strategy.url_scorer._keywords}"

    found_log = False
    # Adjusted to match the actual log message "with args: {'keywords': ...}"
    expected_log_substring = f"Created KeywordRelevanceScorer with args: {{'keywords': {keywords_list}}}"
    for record in caplog.records:
        if record.levelname == "INFO" and expected_log_substring in record.message:
            found_log = True
            break
    assert found_log, f"Log message for KeywordRelevanceScorer creation with correct keywords not found. Expected substring: '{expected_log_substring}' in any INFO log. Captured text: {caplog.text}"


# Test 4.4: BestFirstCrawlingStrategy without Scorer
async def test_best_first_without_scorer(client: TestClient, mock_arun: AsyncMock, caplog): # Replaced mock_logger_warning with caplog
    caplog.set_level(logging.WARNING) # Ensure WARNING messages are captured (INFO will also be captured if set to INFO or DEBUG)

    api_query_params = {
        "url": "http://example.com",
        "engine": "crawl4ai",
        "deep_crawl_strategy_name": "BestFirstCrawlingStrategy",
        "deep_crawl_max_depth": 1,
        # No url_scorer_type or scorer_keywords
    }
    response = client.get("/fetch-content", params=api_query_params)
    response.read()

    assert response.status_code == 200
    mock_arun.assert_called_once()
    
    call_args = mock_arun.call_args
    assert call_args is not None
    deep_crawl_strategy = call_args.kwargs.get('deep_crawl_strategy')

    assert deep_crawl_strategy is not None, "deep_crawl_strategy not found in arun call kwargs"
    assert isinstance(deep_crawl_strategy, BestFirstCrawlingStrategy)
    assert deep_crawl_strategy.url_scorer is None # Or a default scorer if crawl4ai implements one

    # Verify warning logged
    expected_warning_substring = (
        "BestFirstCrawlingStrategy selected, but no URLScorer was configured or "
        "successfully instantiated. This strategy typically requires a scorer to be effective."
    )
    
    warning_found = False
    for record in caplog.records:
        if record.levelname == "WARNING" and expected_warning_substring in record.message:
            warning_found = True
            break
    assert warning_found, f"Expected warning log containing '{expected_warning_substring}' not found. Captured text: {caplog.text}"

# Test 4.5: "None" Strategy
@pytest.mark.parametrize(
    "deep_crawl_config_payload",
    [
        ({"strategy": "none"}),
        ({"strategy": "None"}),
        ({"strategy": "NONE"}),
        ({"strategy": "default"}),
        ({"strategy": ""}), # Empty string
        ({}), # Empty params, implies no strategy
        None, # Entire deep_crawl_config missing
    ]
)
async def test_none_deep_crawl_strategy(client: TestClient, mock_arun: AsyncMock, deep_crawl_config_payload: Optional[dict]):
    api_query_params = {
        "url": "http://example.com",
        "engine": "crawl4ai",
    }
    if deep_crawl_config_payload is not None:
        strategy_name = deep_crawl_config_payload.get("strategy")
        if strategy_name is not None: # Handles cases like {"strategy": "none"} or {"strategy": ""}
            api_query_params["deep_crawl_strategy_name"] = strategy_name
        # If deep_crawl_config_payload is an empty dict {}, strategy_name is None, so param not added.
        # This matches behavior where no strategy implies no deep crawl.
        
        # Handle other potential params if they were part of the "none" strategy test cases,
        # though typically "none" implies no other deep crawl params.
        # For this test, only "strategy" key in deep_crawl_config_payload is relevant.

    response = client.get("/fetch-content", params=api_query_params)
    response.read()

    assert response.status_code == 200
    mock_arun.assert_called_once()
    
    call_args = mock_arun.call_args
    assert call_args is not None
        
    # For "none" strategy, deep_crawl_strategy should not be passed to arun
    assert 'deep_crawl_strategy' not in call_args.kwargs or call_args.kwargs.get('deep_crawl_strategy') is None