# Test Results

## test_crawl4ai_fetcher_deep_strategies.py

```
FFFFF
================================== FAILURES ===================================
_ test_deep_crawl_strategy_instantiation[BFSDeepCrawlStrategy-BFSDeepCrawlStrategy-params_in0-expected_params_subset0] _
test_crawl4ai_fetcher_deep_strategies.py:105: in test_deep_crawl_strategy_instantiation
    assert isinstance(deep_crawl_strategy, strategy_class)
E   AssertionError: assert False
E    +  where False = isinstance(None, <class 'crawl4ai.deep_crawling.bfs_strategy.BFSDeepCrawlStrategy'>)
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:10,938 - backend.app.main - INFO - Application startup initiated...
2025-05-09 15:34:10,938 - backend.app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:10,938 - backend.app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     backend.app.main:main.py:621 Application startup initiated...
INFO     backend.app.main:main.py:626 System metrics collection scheduled.
INFO     backend.app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:10,950 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:10,951 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:11,141 - backend.app.psearchworking - INFO - Initialized Supabase client singleton
2025-05-09 15:34:11,332 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.382s)
2025-05-09 15:34:11,416 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:11,418 - backend.app.main - INFO - Initial fetch history record created with ID: d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 for URL: http://example.com
2025-05-09 15:34:11,520 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:11,520 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:11,545 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:11,546 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:11,546 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:11,546 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:11,546 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:11,552 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:12,082 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:12,328 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:12,328 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:12,328 - backend.app.main - INFO - Attempting to update fetch_history record ID: d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 with status: success
2025-05-09 15:34:12,347 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 "HTTP/2 200 OK"
2025-05-09 15:34:12,348 - backend.app.main - INFO - Successfully updated fetch history d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 with status: success
2025-05-09 15:34:12,348 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:12,348 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BFSDeepCrawlStrategy&deep_crawl_max_depth=3&deep_crawl_max_pages=10 "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.psearchworking:psearchworking.py:510 Initialized Supabase client singleton
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.382s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history d7a6b3c9-f4d4-40d8-9e95-b958bf6169e8 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BFSDeepCrawlStrategy&deep_crawl_max_depth=3&deep_crawl_max_pages=10 "HTTP/1.1 200 OK"
_ test_deep_crawl_strategy_instantiation[DFSDeepCrawlStrategy-DFSDeepCrawlStrategy-params_in1-expected_params_subset1] _
test_crawl4ai_fetcher_deep_strategies.py:105: in test_deep_crawl_strategy_instantiation
    assert isinstance(deep_crawl_strategy, strategy_class)
E   AssertionError: assert False
E    +  where False = isinstance(None, <class 'crawl4ai.deep_crawling.dfs_strategy.DFSDeepCrawlStrategy'>)
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:12,354 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:12,354 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:12,355 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.001s)
2025-05-09 15:34:12,369 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:12,369 - backend.app.main - INFO - Initial fetch history record created with ID: db4e3bdf-8dfd-49ae-ae30-57a41959fda8 for URL: http://example.com
2025-05-09 15:34:12,472 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:12,472 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:12,494 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:12,494 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:12,494 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:12,494 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:12,494 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:12,499 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:12,971 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:13,083 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:13,083 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:13,083 - backend.app.main - INFO - Attempting to update fetch_history record ID: db4e3bdf-8dfd-49ae-ae30-57a41959fda8 with status: success
2025-05-09 15:34:13,101 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.db4e3bdf-8dfd-49ae-ae30-57a41959fda8 "HTTP/2 200 OK"
2025-05-09 15:34:13,101 - backend.app.main - INFO - Successfully updated fetch history db4e3bdf-8dfd-49ae-ae30-57a41959fda8 with status: success
2025-05-09 15:34:13,101 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:13,102 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=DFSDeepCrawlStrategy&deep_crawl_max_depth=2&deep_crawl_max_pages=5&deep_crawl_include_external=true "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: db4e3bdf-8dfd-49ae-ae30-57a41959fda8 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: db4e3bdf-8dfd-49ae-ae30-57a41959fda8 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.db4e3bdf-8dfd-49ae-ae30-57a41959fda8 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history db4e3bdf-8dfd-49ae-ae30-57a41959fda8 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=DFSDeepCrawlStrategy&deep_crawl_max_depth=2&deep_crawl_max_pages=5&deep_crawl_include_external=true "HTTP/1.1 200 OK"
_ test_deep_crawl_strategy_instantiation[BestFirstCrawlingStrategy-BestFirstCrawlingStrategy-params_in2-expected_params_subset2] _
test_crawl4ai_fetcher_deep_strategies.py:105: in test_deep_crawl_strategy_instantiation
    assert isinstance(deep_crawl_strategy, strategy_class)
E   AssertionError: assert False
E    +  where False = isinstance(None, <class 'crawl4ai.deep_crawling.bff_strategy.BestFirstCrawlingStrategy'>)
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:13,107 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:13,107 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:13,108 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.001s)
2025-05-09 15:34:13,123 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:13,124 - backend.app.main - INFO - Initial fetch history record created with ID: e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad for URL: http://example.com
2025-05-09 15:34:13,226 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:13,226 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:13,247 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:13,247 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:13,247 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:13,247 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:13,247 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:13,252 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:13,702 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:13,820 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:13,820 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:13,820 - backend.app.main - INFO - Attempting to update fetch_history record ID: e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad with status: success
2025-05-09 15:34:13,838 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad "HTTP/2 200 OK"
2025-05-09 15:34:13,839 - backend.app.main - INFO - Successfully updated fetch history e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad with status: success
2025-05-09 15:34:13,839 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:13,840 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_max_pages=3&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=test%2Cdata "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history e3ab47f7-8da5-4b7d-8663-2ae51b7b18ad with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_max_pages=3&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=test%2Cdata "HTTP/1.1 200 OK"
________________________ test_filter_chain_integration ________________________
test_crawl4ai_fetcher_deep_strategies.py:135: in test_filter_chain_integration
    assert deep_crawl_strategy is not None
E   assert None is not None
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:13,845 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:13,846 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:13,847 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:13,866 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:13,867 - backend.app.main - INFO - Initial fetch history record created with ID: 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 for URL: http://example.com
2025-05-09 15:34:13,969 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:13,969 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:13,990 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:13,990 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:13,990 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:13,990 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:13,990 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:13,995 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:14,462 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:14,589 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:14,590 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:14,590 - backend.app.main - INFO - Attempting to update fetch_history record ID: 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 with status: success
2025-05-09 15:34:14,605 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 "HTTP/2 200 OK"
2025-05-09 15:34:14,605 - backend.app.main - INFO - Successfully updated fetch history 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 with status: success
2025-05-09 15:34:14,605 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:14,606 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_filter_regexes=http%3A%2F%2Fexample.com%2Fallowed%2F.%2A%2Chttp%3A%2F%2Fanother.com%2F.%2A&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=dummy "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history 5ce212c3-7fe0-42ee-beb2-3bb86d6d9bb5 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_filter_regexes=http%3A%2F%2Fexample.com%2Fallowed%2F.%2A%2Chttp%3A%2F%2Fanother.com%2F.%2A&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=dummy "HTTP/1.1 200 OK"
__________________ test_keyword_relevance_scorer_integration __________________
test_crawl4ai_fetcher_deep_strategies.py:186: in test_keyword_relevance_scorer_integration
    assert deep_crawl_strategy is not None
E   assert None is not None
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:14,611 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:14,611 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:14,612 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.001s)
2025-05-09 15:34:14,628 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:14,628 - backend.app.main - INFO - Initial fetch history record created with ID: 5f901ebf-d7ae-444e-ab6d-d93ca991e64c for URL: http://example.com
2025-05-09 15:34:14,729 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:14,729 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:14,751 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:14,751 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:14,751 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:14,751 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:14,751 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:14,757 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:15,222 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:15,331 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:15,331 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:15,332 - backend.app.main - INFO - Attempting to update fetch_history record ID: 5f901ebf-d7ae-444e-ab6d-d93ca991e64c with status: success
2025-05-09 15:34:15,352 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.5f901ebf-d7ae-444e-ab6d-d93ca991e64c "HTTP/2 200 OK"
2025-05-09 15:34:15,353 - backend.app.main - INFO - Successfully updated fetch history 5f901ebf-d7ae-444e-ab6d-d93ca991e64c with status: success
2025-05-09 15:34:15,353 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:15,354 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=important%2Crelevant%2Ctest "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: 5f901ebf-d7ae-444e-ab6d-d93ca991e64c for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: 5f901ebf-d7ae-444e-ab6d-d93ca991e64c with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.5f901ebf-d7ae-444e-ab6d-d93ca991e64c "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history 5f901ebf-d7ae-444e-ab6d-d93ca991e64c with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&deep_crawl_strategy_name=BestFirstCrawlingStrategy&deep_crawl_max_depth=1&deep_crawl_url_scorer_type=KeywordRelevanceScorer&deep_crawl_scorer_keywords=important%2Crelevant%2Ctest "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:15,358 - backend.app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:15,358 - backend.app.main - INFO - Queue manager stopped.
---------------------------- Captured log teardown ----------------------------
INFO     backend.app.main:main.py:635 Application shutdown initiated...
INFO     backend.app.main:main.py:638 Queue manager stopped.
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

backend/app/tests/test_crawl4ai_fetcher_deep_strategies.py::test_deep_crawl_strategy_instantiation[BFSDeepCrawlStrategy-BFSDeepCrawlStrategy-params_in0-expected_params_subset0]
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:884: DeprecationWarning: The event_loop fixture provided by pytest-asyncio has been redefined in
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\conftest.py:18
  Replacing the event_loop fixture with a custom implementation is deprecated
  and will lead to errors in the future.
  If you want to request an asyncio event loop with a scope other than function
  scope, use the "loop_scope" argument to the asyncio mark when marking the tests.
  If you want to return different types of event loops, use the event_loop_policy
  fixture.
  
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_crawl4ai_fetcher_deep_strategies.py::test_deep_crawl_strategy_instantiation[BFSDeepCrawlStrategy-BFSDeepCrawlStrategy-params_in0-expected_params_subset0]
FAILED test_crawl4ai_fetcher_deep_strategies.py::test_deep_crawl_strategy_instantiation[DFSDeepCrawlStrategy-DFSDeepCrawlStrategy-params_in1-expected_params_subset1]
FAILED test_crawl4ai_fetcher_deep_strategies.py::test_deep_crawl_strategy_instantiation[BestFirstCrawlingStrategy-BestFirstCrawlingStrategy-params_in2-expected_params_subset2]
FAILED test_crawl4ai_fetcher_deep_strategies.py::test_filter_chain_integration
FAILED test_crawl4ai_fetcher_deep_strategies.py::test_keyword_relevance_scorer_integration
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
```

## test_crawl4ai_fetcher_extraction_strategies.py

```
FFFFF
================================== FAILURES ===================================
______ TestLLMExtractionStrategy.test_llm_strategy_with_required_params _______
test_crawl4ai_fetcher_extraction_strategies.py:118: in test_llm_strategy_with_required_params
    assert strategy_instance is not None, "Extraction strategy was not set"
E   AssertionError: Extraction strategy was not set
E   assert None is not None
---------------------------- Captured stdout setup ----------------------------
Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
Rich console is available.
Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:21,169 - root - INFO - Patched AppStatus.should_exit_event with new event for loop 1896738493968
2025-05-09 15:34:21,171 - app.main - INFO - Policy set in main.py (top level): WindowsProactorEventLoopPolicy
2025-05-09 15:34:21,172 - app.main - INFO - Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
2025-05-09 15:34:21,361 - app.main - INFO - Async OpenAI client initialized.
2025-05-09 15:34:21,553 - app.main - INFO - Async Groq client initialized.
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - --- System Info ---
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - Selected Whisper model size: medium
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - CUDA available: True
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - Determined optimal device: 'cuda' with compute type: 'float16'
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - GPU Device Name: NVIDIA GeForce RTX 3090 Ti
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - GPU Memory: 23.99 GB
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - CUDA Device Capability: (8, 6)
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - CUDA Device Count: 1
2025-05-09 15:34:21,561 - app.transcribe1 - INFO - --- End System Info ---
2025-05-09 15:34:21,951 - search_params - INFO - Loaded search parameters from preset: default
2025-05-09 15:34:21,951 - search_params - INFO - Loaded search parameters from preset: default
2025-05-09 15:34:21,959 - app.routes.fetch_history_routes - INFO - Ensured fetched content storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\fetched_content
2025-05-09 15:34:21,962 - app.main - INFO - TokenCounter initialized with tiktoken encoders.
2025-05-09 15:34:21,968 - app.main - INFO - Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
2025-05-09 15:34:21,968 - app.main - INFO - SSE monitoring middleware enabled.
2025-05-09 15:34:21,972 - app.main - INFO - Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\temp_pdfs
2025-05-09 15:34:21,984 - app.main - INFO - Debug endpoints included.
2025-05-09 15:34:21,997 - app.main - INFO - Application startup initiated...
2025-05-09 15:34:21,997 - app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:21,997 - app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:46 Patched AppStatus.should_exit_event with new event for loop 1896738493968
INFO     app.main:main.py:35 Policy set in main.py (top level): WindowsProactorEventLoopPolicy
INFO     app.main:main.py:150 Loaded environment variables from C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\.env
INFO     app.main:main.py:162 Async OpenAI client initialized.
INFO     app.main:main.py:174 Async Groq client initialized.
INFO     app.transcribe1:transcribe1.py:83 --- System Info ---
INFO     app.transcribe1:transcribe1.py:84 Selected Whisper model size: medium
INFO     app.transcribe1:transcribe1.py:85 CUDA available: True
INFO     app.transcribe1:transcribe1.py:86 Determined optimal device: 'cuda' with compute type: 'float16'
INFO     app.transcribe1:transcribe1.py:89 GPU Device Name: NVIDIA GeForce RTX 3090 Ti
INFO     app.transcribe1:transcribe1.py:91 GPU Memory: 23.99 GB
INFO     app.transcribe1:transcribe1.py:92 CUDA Device Capability: (8, 6)
INFO     app.transcribe1:transcribe1.py:93 CUDA Device Count: 1
INFO     app.transcribe1:transcribe1.py:96 --- End System Info ---
INFO     search_params:psearchworking.py:528 Loaded search parameters from preset: default
INFO     search_params:psearchworking.py:528 Loaded search parameters from preset: default
INFO     app.routes.fetch_history_routes:fetch_history_routes.py:31 Ensured fetched content storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\fetched_content
INFO     app.main:main.py:322 TokenCounter initialized with tiktoken encoders.
INFO     app.main:main.py:560 Configuring CORS for origins: ['http://localhost:3000', 'http://127.0.0.1:3000']
INFO     app.main:main.py:577 SSE monitoring middleware enabled.
INFO     app.main:main.py:1424 Ensured PDF storage directory exists: C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\temp_pdfs
INFO     app.main:main.py:2120 Debug endpoints included.
INFO     app.main:main.py:621 Application startup initiated...
INFO     app.main:main.py:626 System metrics collection scheduled.
INFO     app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:22,008 - app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:22,009 - app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com/llm_test, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:22,197 - app.psearchworking - INFO - Initialized Supabase client singleton
2025-05-09 15:34:22,386 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.378s)
2025-05-09 15:34:22,438 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:22,440 - app.main - INFO - Initial fetch history record created with ID: 3dbe4b12-62bf-4982-948f-8c50cf2f58ea for URL: http://example.com/llm_test
2025-05-09 15:34:22,541 - app.main - INFO - Using crawl4ai engine for URL: http://example.com/llm_test
2025-05-09 15:34:22,541 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com/llm_test
2025-05-09 15:34:22,561 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:22,562 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:22,562 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:22,562 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:22,562 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:22,567 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:23,057 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com/llm_test
2025-05-09 15:34:23,165 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com/llm_test
2025-05-09 15:34:23,165 - app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com/llm_test
2025-05-09 15:34:23,165 - app.main - INFO - Attempting to update fetch_history record ID: 3dbe4b12-62bf-4982-948f-8c50cf2f58ea with status: success
2025-05-09 15:34:23,184 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.3dbe4b12-62bf-4982-948f-8c50cf2f58ea "HTTP/2 200 OK"
2025-05-09 15:34:23,184 - app.main - INFO - Successfully updated fetch history 3dbe4b12-62bf-4982-948f-8c50cf2f58ea with status: success
2025-05-09 15:34:23,184 - app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_test
2025-05-09 15:34:23,185 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_test&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20key%20information.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%7D%7D "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from testclient
INFO     app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com/llm_test, Engine: crawl4ai, PDF: True, Supabase: False
INFO     app.psearchworking:psearchworking.py:510 Initialized Supabase client singleton
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.378s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 3dbe4b12-62bf-4982-948f-8c50cf2f58ea for URL: http://example.com/llm_test
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com/llm_test
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com/llm_test
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com/llm_test
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com/llm_test
WARNING  app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com/llm_test
INFO     app.main:main.py:1540 Attempting to update fetch_history record ID: 3dbe4b12-62bf-4982-948f-8c50cf2f58ea with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.3dbe4b12-62bf-4982-948f-8c50cf2f58ea "HTTP/2 200 OK"
INFO     app.main:main.py:1549 Successfully updated fetch history 3dbe4b12-62bf-4982-948f-8c50cf2f58ea with status: success
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_test
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_test&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20key%20information.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%7D%7D "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:23,190 - app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:23,190 - app.main - INFO - Queue manager stopped.
2025-05-09 15:34:23,192 - root - INFO - Restored original AppStatus.should_exit_event.
---------------------------- Captured log teardown ----------------------------
INFO     app.main:main.py:635 Application shutdown initiated...
INFO     app.main:main.py:638 Queue manager stopped.
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:57 Restored original AppStatus.should_exit_event.
______ TestLLMExtractionStrategy.test_llm_strategy_with_optional_params _______
test_crawl4ai_fetcher_extraction_strategies.py:164: in test_llm_strategy_with_optional_params
    assert isinstance(strategy_instance, LLMExtractionStrategy)
E   AssertionError: assert False
E    +  where False = isinstance(None, <class 'crawl4ai.extraction_strategy.LLMExtractionStrategy'>)
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:23,192 - root - INFO - Patched AppStatus.should_exit_event with new event for loop 1896738493968
2025-05-09 15:34:23,194 - app.main - INFO - Application startup initiated...
2025-05-09 15:34:23,194 - app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:23,194 - app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:46 Patched AppStatus.should_exit_event with new event for loop 1896738493968
INFO     app.main:main.py:621 Application startup initiated...
INFO     app.main:main.py:626 System metrics collection scheduled.
INFO     app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:23,204 - app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:23,205 - app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com/llm_optional, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:23,206 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:23,222 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:23,223 - app.main - INFO - Initial fetch history record created with ID: 1cf747ac-bbd6-45ac-976d-ea5c9910220c for URL: http://example.com/llm_optional
2025-05-09 15:34:23,324 - app.main - INFO - Using crawl4ai engine for URL: http://example.com/llm_optional
2025-05-09 15:34:23,324 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com/llm_optional
2025-05-09 15:34:23,345 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:23,345 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:23,345 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:23,345 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:23,345 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:23,350 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:23,808 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com/llm_optional
2025-05-09 15:34:23,917 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com/llm_optional
2025-05-09 15:34:23,917 - app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com/llm_optional
2025-05-09 15:34:23,918 - app.main - INFO - Attempting to update fetch_history record ID: 1cf747ac-bbd6-45ac-976d-ea5c9910220c with status: success
2025-05-09 15:34:23,933 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.1cf747ac-bbd6-45ac-976d-ea5c9910220c "HTTP/2 200 OK"
2025-05-09 15:34:23,934 - app.main - INFO - Successfully updated fetch history 1cf747ac-bbd6-45ac-976d-ea5c9910220c with status: success
2025-05-09 15:34:23,934 - app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_optional
2025-05-09 15:34:23,934 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_optional&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20detailed%20data.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%2C%20%22llm_api_token%22%3A%20%22test_api_token_from_request%22%2C%20%22llm_base_url%22%3A%20%22http%3A%2F%2Flocalhost%3A1234%2Fv1%22%7D%7D "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from testclient
INFO     app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com/llm_optional, Engine: crawl4ai, PDF: True, Supabase: False
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 1cf747ac-bbd6-45ac-976d-ea5c9910220c for URL: http://example.com/llm_optional
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com/llm_optional
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com/llm_optional
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com/llm_optional
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com/llm_optional
WARNING  app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com/llm_optional
INFO     app.main:main.py:1540 Attempting to update fetch_history record ID: 1cf747ac-bbd6-45ac-976d-ea5c9910220c with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.1cf747ac-bbd6-45ac-976d-ea5c9910220c "HTTP/2 200 OK"
INFO     app.main:main.py:1549 Successfully updated fetch history 1cf747ac-bbd6-45ac-976d-ea5c9910220c with status: success
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_optional
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_optional&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20detailed%20data.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%2C%20%22llm_api_token%22%3A%20%22test_api_token_from_request%22%2C%20%22llm_base_url%22%3A%20%22http%3A%2F%2Flocalhost%3A1234%2Fv1%22%7D%7D "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:23,939 - app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:23,939 - app.main - INFO - Queue manager stopped.
2025-05-09 15:34:23,940 - root - INFO - Restored original AppStatus.should_exit_event.
---------------------------- Captured log teardown ----------------------------
INFO     app.main:main.py:635 Application shutdown initiated...
INFO     app.main:main.py:638 Queue manager stopped.
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:57 Restored original AppStatus.should_exit_event.
_ TestLLMExtractionStrategy.test_llm_strategy_api_token_precedence_env_over_request _
test_crawl4ai_fetcher_extraction_strategies.py:206: in test_llm_strategy_api_token_precedence_env_over_request
    assert isinstance(strategy_instance, LLMExtractionStrategy)
E   AssertionError: assert False
E    +  where False = isinstance(None, <class 'crawl4ai.extraction_strategy.LLMExtractionStrategy'>)
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:23,940 - root - INFO - Patched AppStatus.should_exit_event with new event for loop 1896738493968
2025-05-09 15:34:23,942 - app.main - INFO - Application startup initiated...
2025-05-09 15:34:23,942 - app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:23,942 - app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:46 Patched AppStatus.should_exit_event with new event for loop 1896738493968
INFO     app.main:main.py:621 Application startup initiated...
INFO     app.main:main.py:626 System metrics collection scheduled.
INFO     app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:23,952 - app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:23,953 - app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com/llm_token_precedence, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:23,954 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:23,967 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:23,968 - app.main - INFO - Initial fetch history record created with ID: 42dff0fd-78ca-4286-9bc9-b8f47a853549 for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,069 - app.main - INFO - Using crawl4ai engine for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,069 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,089 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:24,089 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:24,089 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:24,089 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:24,089 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:24,095 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:24,581 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,693 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,693 - app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,693 - app.main - INFO - Attempting to update fetch_history record ID: 42dff0fd-78ca-4286-9bc9-b8f47a853549 with status: success
2025-05-09 15:34:24,707 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.42dff0fd-78ca-4286-9bc9-b8f47a853549 "HTTP/2 200 OK"
2025-05-09 15:34:24,708 - app.main - INFO - Successfully updated fetch history 42dff0fd-78ca-4286-9bc9-b8f47a853549 with status: success
2025-05-09 15:34:24,708 - app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_token_precedence
2025-05-09 15:34:24,709 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_token_precedence&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20with%20env%20token.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%2C%20%22llm_api_token%22%3A%20%22token_from_request_should_be_ignored%22%7D%7D "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from testclient
INFO     app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com/llm_token_precedence, Engine: crawl4ai, PDF: True, Supabase: False
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 42dff0fd-78ca-4286-9bc9-b8f47a853549 for URL: http://example.com/llm_token_precedence
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com/llm_token_precedence
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com/llm_token_precedence
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com/llm_token_precedence
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com/llm_token_precedence
WARNING  app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com/llm_token_precedence
INFO     app.main:main.py:1540 Attempting to update fetch_history record ID: 42dff0fd-78ca-4286-9bc9-b8f47a853549 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.42dff0fd-78ca-4286-9bc9-b8f47a853549 "HTTP/2 200 OK"
INFO     app.main:main.py:1549 Successfully updated fetch history 42dff0fd-78ca-4286-9bc9-b8f47a853549 with status: success
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_token_precedence
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_token_precedence&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20with%20env%20token.%22%2C%20%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%2C%20%22llm_api_token%22%3A%20%22token_from_request_should_be_ignored%22%7D%7D "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:24,715 - app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:24,715 - app.main - INFO - Queue manager stopped.
2025-05-09 15:34:24,716 - root - INFO - Restored original AppStatus.should_exit_event.
---------------------------- Captured log teardown ----------------------------
INFO     app.main:main.py:635 Application shutdown initiated...
INFO     app.main:main.py:638 Queue manager stopped.
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:57 Restored original AppStatus.should_exit_event.
______ TestLLMExtractionStrategy.test_llm_strategy_missing_instructions _______
test_crawl4ai_fetcher_extraction_strategies.py:241: in test_llm_strategy_missing_instructions
    assert any(
E   AssertionError: Expected warning for missing LLM instructions not found in logs
E   assert False
E    +  where False = any(<generator object TestLLMExtractionStrategy.test_llm_strategy_missing_instructions.<locals>.<genexpr> at 0x000001B9A11AB6B0>)
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:24,716 - root - INFO - Patched AppStatus.should_exit_event with new event for loop 1896738493968
2025-05-09 15:34:24,718 - app.main - INFO - Application startup initiated...
2025-05-09 15:34:24,718 - app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:24,718 - app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:46 Patched AppStatus.should_exit_event with new event for loop 1896738493968
INFO     app.main:main.py:621 Application startup initiated...
INFO     app.main:main.py:626 System metrics collection scheduled.
INFO     app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:24,727 - app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:24,728 - app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com/llm_no_instructions, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:24,729 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:24,741 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:24,742 - app.main - INFO - Initial fetch history record created with ID: 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:24,843 - app.main - INFO - Using crawl4ai engine for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:24,843 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:24,863 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:24,863 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:24,863 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:24,864 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:24,864 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:24,869 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:25,351 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:25,463 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:25,463 - app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com/llm_no_instructions
2025-05-09 15:34:25,463 - app.main - INFO - Attempting to update fetch_history record ID: 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 with status: success
2025-05-09 15:34:25,479 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 "HTTP/2 200 OK"
2025-05-09 15:34:25,480 - app.main - INFO - Successfully updated fetch history 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 with status: success
2025-05-09 15:34:25,480 - app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_no_instructions
2025-05-09 15:34:25,480 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_no_instructions&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%7D%7D "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from testclient
INFO     app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com/llm_no_instructions, Engine: crawl4ai, PDF: True, Supabase: False
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 for URL: http://example.com/llm_no_instructions
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com/llm_no_instructions
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com/llm_no_instructions
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com/llm_no_instructions
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com/llm_no_instructions
WARNING  app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com/llm_no_instructions
INFO     app.main:main.py:1540 Attempting to update fetch_history record ID: 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 "HTTP/2 200 OK"
INFO     app.main:main.py:1549 Successfully updated fetch history 8b8b7a1e-4d9f-4873-b4ae-077f9ecbcdf7 with status: success
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_no_instructions
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_no_instructions&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_provider_model%22%3A%20%22openai%2Fgpt-4o-mini%22%7D%7D "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:25,485 - app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:25,485 - app.main - INFO - Queue manager stopped.
2025-05-09 15:34:25,486 - root - INFO - Restored original AppStatus.should_exit_event.
---------------------------- Captured log teardown ----------------------------
INFO     app.main:main.py:635 Application shutdown initiated...
INFO     app.main:main.py:638 Queue manager stopped.
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:57 Restored original AppStatus.should_exit_event.
________ TestLLMExtractionStrategy.test_llm_strategy_missing_provider _________
test_crawl4ai_fetcher_extraction_strategies.py:279: in test_llm_strategy_missing_provider
    assert any(
E   AssertionError: Expected warning for missing LLM provider not found in logs
E   assert (False or False)
E    +  where False = any(<generator object TestLLMExtractionStrategy.test_llm_strategy_missing_provider.<locals>.<genexpr> at 0x000001B99E7C3AC0>)
E    +  and   False = any(<generator object TestLLMExtractionStrategy.test_llm_strategy_missing_provider.<locals>.<genexpr> at 0x000001B99E7C2DC0>)
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:25,487 - root - INFO - Patched AppStatus.should_exit_event with new event for loop 1896738493968
2025-05-09 15:34:25,489 - app.main - INFO - Application startup initiated...
2025-05-09 15:34:25,489 - app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:25,489 - app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:46 Patched AppStatus.should_exit_event with new event for loop 1896738493968
INFO     app.main:main.py:621 Application startup initiated...
INFO     app.main:main.py:626 System metrics collection scheduled.
INFO     app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:25,499 - app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:25,499 - app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com/llm_no_provider, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:25,500 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.001s)
2025-05-09 15:34:25,514 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:25,514 - app.main - INFO - Initial fetch history record created with ID: 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 for URL: http://example.com/llm_no_provider
2025-05-09 15:34:25,615 - app.main - INFO - Using crawl4ai engine for URL: http://example.com/llm_no_provider
2025-05-09 15:34:25,615 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com/llm_no_provider
2025-05-09 15:34:25,637 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:25,637 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:25,637 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:25,637 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:25,637 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:25,643 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:26,094 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com/llm_no_provider
2025-05-09 15:34:26,199 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com/llm_no_provider
2025-05-09 15:34:26,199 - app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com/llm_no_provider
2025-05-09 15:34:26,199 - app.main - INFO - Attempting to update fetch_history record ID: 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 with status: success
2025-05-09 15:34:26,217 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.591d7b5a-4b15-4295-b0a4-b33ca5a61b84 "HTTP/2 200 OK"
2025-05-09 15:34:26,218 - app.main - INFO - Successfully updated fetch history 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 with status: success
2025-05-09 15:34:26,218 - app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_no_provider
2025-05-09 15:34:26,218 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_no_provider&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20something.%22%7D%7D "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from testclient
INFO     app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com/llm_no_provider, Engine: crawl4ai, PDF: True, Supabase: False
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 for URL: http://example.com/llm_no_provider
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com/llm_no_provider
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com/llm_no_provider
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com/llm_no_provider
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com/llm_no_provider
WARNING  app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com/llm_no_provider
INFO     app.main:main.py:1540 Attempting to update fetch_history record ID: 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.591d7b5a-4b15-4295-b0a4-b33ca5a61b84 "HTTP/2 200 OK"
INFO     app.main:main.py:1549 Successfully updated fetch history 591d7b5a-4b15-4295-b0a4-b33ca5a61b84 with status: success
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com/llm_no_provider
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com%2Fllm_no_provider&engine=crawl4ai&extraction_config=%7B%22strategy%22%3A%20%22LLMExtractionStrategy%22%2C%20%22params%22%3A%20%7B%22llm_instructions%22%3A%20%22Extract%20something.%22%7D%7D "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:26,223 - app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:26,223 - app.main - INFO - Queue manager stopped.
2025-05-09 15:34:26,224 - root - INFO - Restored original AppStatus.should_exit_event.
---------------------------- Captured log teardown ----------------------------
INFO     app.main:main.py:635 Application shutdown initiated...
INFO     app.main:main.py:638 Queue manager stopped.
INFO     root:test_crawl4ai_fetcher_extraction_strategies.py:57 Restored original AppStatus.should_exit_event.
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:884: DeprecationWarning: The event_loop fixture provided by pytest-asyncio has been redefined in
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\conftest.py:18
  Replacing the event_loop fixture with a custom implementation is deprecated
  and will lead to errors in the future.
  If you want to request an asyncio event loop with a scope other than function
  scope, use the "loop_scope" argument to the asyncio mark when marking the tests.
  If you want to return different types of event loops, use the event_loop_policy
  fixture.
  
    warnings.warn(

backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_missing_provider
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:944: DeprecationWarning: There is no current event loop
    loop = policy.get_event_loop()

backend/app/tests/test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_missing_provider
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:949: DeprecationWarning: pytest-asyncio detected an unclosed event loop when tearing down the event_loop
  fixture: <ProactorEventLoop running=False closed=False debug=False>
  pytest-asyncio will close the event loop for you, but future versions of the
  library will no longer do so. In order to ensure compatibility with future
  versions, please make sure that:
      1. Any custom "event_loop" fixture properly closes the loop after yielding it
      2. The scopes of your custom "event_loop" fixtures do not overlap
      3. Your code does not modify the event loop in async fixtures or tests
  
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_required_params
FAILED test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_with_optional_params
FAILED test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_api_token_precedence_env_over_request
FAILED test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_missing_instructions
FAILED test_crawl4ai_fetcher_extraction_strategies.py::TestLLMExtractionStrategy::test_llm_strategy_missing_provider
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
```

## test_crawl4ai_fetcher_general_options.py

```
FFFFF
================================== FAILURES ===================================
_____________________ test_smoke_no_params_uses_defaults ______________________
C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\unittest\mock.py:928: in assert_called_once
    raise AssertionError(msg)
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.

During handling of the above exception, another exception occurred:
test_crawl4ai_fetcher_general_options.py:123: in test_smoke_no_params_uses_defaults
    MockAsyncWebCrawler.assert_called_once()
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:34:32,129 - backend.app.main - INFO - Application startup initiated...
2025-05-09 15:34:32,129 - backend.app.main - INFO - System metrics collection scheduled.
2025-05-09 15:34:32,129 - backend.app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     backend.app.main:main.py:621 Application startup initiated...
INFO     backend.app.main:main.py:626 System metrics collection scheduled.
INFO     backend.app.main:main.py:627 Queue manager started.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:32,141 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:32,142 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:32,332 - backend.app.psearchworking - INFO - Initialized Supabase client singleton
2025-05-09 15:34:32,522 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.381s)
2025-05-09 15:34:32,567 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:32,569 - backend.app.main - INFO - Initial fetch history record created with ID: be13cc5c-e4d7-4506-8e13-178eb1697ef5 for URL: http://example.com
2025-05-09 15:34:32,671 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:32,671 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:32,692 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:32,693 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:32,693 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:32,693 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:32,693 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:32,698 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:33,167 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:33,562 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:33,562 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:33,562 - backend.app.main - INFO - Attempting to update fetch_history record ID: be13cc5c-e4d7-4506-8e13-178eb1697ef5 with status: success
2025-05-09 15:34:33,579 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.be13cc5c-e4d7-4506-8e13-178eb1697ef5 "HTTP/2 200 OK"
2025-05-09 15:34:33,579 - backend.app.main - INFO - Successfully updated fetch history be13cc5c-e4d7-4506-8e13-178eb1697ef5 with status: success
2025-05-09 15:34:33,579 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:33,580 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.psearchworking:psearchworking.py:510 Initialized Supabase client singleton
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.381s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: be13cc5c-e4d7-4506-8e13-178eb1697ef5 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: be13cc5c-e4d7-4506-8e13-178eb1697ef5 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.be13cc5c-e4d7-4506-8e13-178eb1697ef5 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history be13cc5c-e4d7-4506-8e13-178eb1697ef5 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai "HTTP/1.1 200 OK"
_ test_various_parameter_combinations[api_params0-expected_browser_config_attrs0-expected_crawler_run_config_attrs0] _
C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\unittest\mock.py:928: in assert_called_once
    raise AssertionError(msg)
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.

During handling of the above exception, another exception occurred:
test_crawl4ai_fetcher_general_options.py:230: in test_various_parameter_combinations
    MockAsyncWebCrawler.assert_called_once()
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:33,607 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:33,608 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:33,608 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.001s)
2025-05-09 15:34:33,623 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:33,623 - backend.app.main - INFO - Initial fetch history record created with ID: 0d1a0f55-8b02-4697-87ad-c4767724e953 for URL: http://example.com
2025-05-09 15:34:33,724 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:33,724 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:33,745 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:33,745 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:33,745 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:33,745 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:33,745 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:33,750 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:34,236 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:34,872 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:34,872 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:34,872 - backend.app.main - INFO - Attempting to update fetch_history record ID: 0d1a0f55-8b02-4697-87ad-c4767724e953 with status: success
2025-05-09 15:34:34,888 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.0d1a0f55-8b02-4697-87ad-c4767724e953 "HTTP/2 200 OK"
2025-05-09 15:34:34,889 - backend.app.main - INFO - Successfully updated fetch history 0d1a0f55-8b02-4697-87ad-c4767724e953 with status: success
2025-05-09 15:34:34,889 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:34,890 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&headless=false&user_agent=TestAgent%2F1.0&page_timeout_ms=5000 "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: 0d1a0f55-8b02-4697-87ad-c4767724e953 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: 0d1a0f55-8b02-4697-87ad-c4767724e953 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.0d1a0f55-8b02-4697-87ad-c4767724e953 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history 0d1a0f55-8b02-4697-87ad-c4767724e953 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&headless=false&user_agent=TestAgent%2F1.0&page_timeout_ms=5000 "HTTP/1.1 200 OK"
_ test_various_parameter_combinations[api_params1-expected_browser_config_attrs1-expected_crawler_run_config_attrs1] _
C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\unittest\mock.py:928: in assert_called_once
    raise AssertionError(msg)
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.

During handling of the above exception, another exception occurred:
test_crawl4ai_fetcher_general_options.py:230: in test_various_parameter_combinations
    MockAsyncWebCrawler.assert_called_once()
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:34,912 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:34,913 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:34,914 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:34,929 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:34,929 - backend.app.main - INFO - Initial fetch history record created with ID: d2384ead-de66-45cc-aad0-02f33cb203a1 for URL: http://example.com
2025-05-09 15:34:35,031 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:35,031 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:35,052 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:35,052 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:35,052 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:35,052 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:35,052 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:35,058 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:35,524 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:35,888 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:35,888 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:35,888 - backend.app.main - INFO - Attempting to update fetch_history record ID: d2384ead-de66-45cc-aad0-02f33cb203a1 with status: success
2025-05-09 15:34:35,903 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.d2384ead-de66-45cc-aad0-02f33cb203a1 "HTTP/2 200 OK"
2025-05-09 15:34:35,903 - backend.app.main - INFO - Successfully updated fetch history d2384ead-de66-45cc-aad0-02f33cb203a1 with status: success
2025-05-09 15:34:35,904 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:35,904 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&enable_javascript=false&ignore_https_errors=0&light_mode=true&text_mode=yes&viewport_width=1024&viewport_height=768 "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: d2384ead-de66-45cc-aad0-02f33cb203a1 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: d2384ead-de66-45cc-aad0-02f33cb203a1 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.d2384ead-de66-45cc-aad0-02f33cb203a1 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history d2384ead-de66-45cc-aad0-02f33cb203a1 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&enable_javascript=false&ignore_https_errors=0&light_mode=true&text_mode=yes&viewport_width=1024&viewport_height=768 "HTTP/1.1 200 OK"
_ test_various_parameter_combinations[api_params2-expected_browser_config_attrs2-expected_crawler_run_config_attrs2] _
C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\unittest\mock.py:928: in assert_called_once
    raise AssertionError(msg)
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.

During handling of the above exception, another exception occurred:
test_crawl4ai_fetcher_general_options.py:230: in test_various_parameter_combinations
    MockAsyncWebCrawler.assert_called_once()
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:35,927 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:35,928 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:35,929 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:35,943 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:35,943 - backend.app.main - INFO - Initial fetch history record created with ID: 9c23d1b4-32e2-44b3-8837-382129f479f3 for URL: http://example.com
2025-05-09 15:34:36,046 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:36,046 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:36,066 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:36,067 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:36,067 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:36,067 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:36,067 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:36,072 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:36,526 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:37,007 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:37,007 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:37,007 - backend.app.main - INFO - Attempting to update fetch_history record ID: 9c23d1b4-32e2-44b3-8837-382129f479f3 with status: success
2025-05-09 15:34:37,023 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.9c23d1b4-32e2-44b3-8837-382129f479f3 "HTTP/2 200 OK"
2025-05-09 15:34:37,024 - backend.app.main - INFO - Successfully updated fetch history 9c23d1b4-32e2-44b3-8837-382129f479f3 with status: success
2025-05-09 15:34:37,024 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:37,024 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&target_elements_css_selectors=.content%2C%20%23main&excluded_elements_css_selector=.nav&extract_only_text_content=true&word_count_threshold=10&respect_robots_txt_rules=false "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: 9c23d1b4-32e2-44b3-8837-382129f479f3 for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: 9c23d1b4-32e2-44b3-8837-382129f479f3 with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.9c23d1b4-32e2-44b3-8837-382129f479f3 "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history 9c23d1b4-32e2-44b3-8837-382129f479f3 with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&target_elements_css_selectors=.content%2C%20%23main&excluded_elements_css_selector=.nav&extract_only_text_content=true&word_count_threshold=10&respect_robots_txt_rules=false "HTTP/1.1 200 OK"
_ test_various_parameter_combinations[api_params3-expected_browser_config_attrs3-expected_crawler_run_config_attrs3] _
C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\unittest\mock.py:928: in assert_called_once
    raise AssertionError(msg)
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.

During handling of the above exception, another exception occurred:
test_crawl4ai_fetcher_general_options.py:230: in test_various_parameter_combinations
    MockAsyncWebCrawler.assert_called_once()
E   AssertionError: Expected 'AsyncWebCrawler' to have been called once. Called 0 times.
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:37,048 - backend.app.main - INFO - --> GET /fetch-content from testclient
2025-05-09 15:34:37,049 - backend.app.main - INFO - SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
2025-05-09 15:34:37,050 - backend.app.main - INFO - <-- GET /fetch-content - Status=200 (0.002s)
2025-05-09 15:34:37,064 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:34:37,064 - backend.app.main - INFO - Initial fetch history record created with ID: 6329d887-8397-43a4-9096-3f178633f9da for URL: http://example.com
2025-05-09 15:34:37,177 - backend.app.main - INFO - Using crawl4ai engine for URL: http://example.com
2025-05-09 15:34:37,177 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: http://example.com
2025-05-09 15:34:37,197 - backend.app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:34:37,197 - backend.app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:34:37,197 - backend.app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:34:37,198 - backend.app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:34:37,198 - backend.app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:34:37,203 - backend.app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:34:37,691 - backend.app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: http://example.com
2025-05-09 15:34:38,174 - backend.app.crawl4ai_fetcher - INFO - crawl4ai_fetcher completed successfully for URL: http://example.com
2025-05-09 15:34:38,174 - backend.app.main - WARNING - Engine crawl4ai returned no markdown content for URL: http://example.com
2025-05-09 15:34:38,174 - backend.app.main - INFO - Attempting to update fetch_history record ID: 6329d887-8397-43a4-9096-3f178633f9da with status: success
2025-05-09 15:34:38,189 - httpx - INFO - HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.6329d887-8397-43a4-9096-3f178633f9da "HTTP/2 200 OK"
2025-05-09 15:34:38,190 - backend.app.main - INFO - Successfully updated fetch history 6329d887-8397-43a4-9096-3f178633f9da with status: success
2025-05-09 15:34:38,190 - backend.app.main - INFO - SSE /fetch-content event generator finished for testclient, URL: http://example.com
2025-05-09 15:34:38,190 - httpx - INFO - HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&proxy_url=http%3A%2F%2Fproxy.example.com%3A8080&browser_cookies=%7B%22cookie1%22%3A%20%22value1%22%7D&page_load_wait_condition=networkidle&execute_javascript_on_page_load=console.log%28%27test%27%29%3B&cache_mode=BYPASS&capture_screenshot_base64=true&crawl_session_id=test-session-123 "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /fetch-content from testclient
INFO     backend.app.main:main.py:1617 SSE /fetch-content request from testclient for URL: http://example.com, Engine: crawl4ai, PDF: True, Supabase: False
INFO     backend.app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.002s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     backend.app.main:main.py:1701 Initial fetch history record created with ID: 6329d887-8397-43a4-9096-3f178633f9da for URL: http://example.com
INFO     backend.app.main:main.py:1728 Using crawl4ai engine for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: http://example.com
INFO     backend.app.crawl4ai_fetcher:crawl4ai_fetcher.py:517 crawl4ai_fetcher completed successfully for URL: http://example.com
WARNING  backend.app.main:main.py:1870 Engine crawl4ai returned no markdown content for URL: http://example.com
INFO     backend.app.main:main.py:1540 Attempting to update fetch_history record ID: 6329d887-8397-43a4-9096-3f178633f9da with status: success
INFO     httpx:_client.py:1038 HTTP Request: PATCH https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history?id=eq.6329d887-8397-43a4-9096-3f178633f9da "HTTP/2 200 OK"
INFO     backend.app.main:main.py:1549 Successfully updated fetch history 6329d887-8397-43a4-9096-3f178633f9da with status: success
INFO     backend.app.main:main.py:2008 SSE /fetch-content event generator finished for testclient, URL: http://example.com
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/fetch-content?url=http%3A%2F%2Fexample.com&engine=crawl4ai&proxy_url=http%3A%2F%2Fproxy.example.com%3A8080&browser_cookies=%7B%22cookie1%22%3A%20%22value1%22%7D&page_load_wait_condition=networkidle&execute_javascript_on_page_load=console.log%28%27test%27%29%3B&cache_mode=BYPASS&capture_screenshot_base64=true&crawl_session_id=test-session-123 "HTTP/1.1 200 OK"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:34:38,211 - backend.app.main - INFO - Application shutdown initiated...
2025-05-09 15:34:38,211 - backend.app.main - INFO - Queue manager stopped.
---------------------------- Captured log teardown ----------------------------
INFO     backend.app.main:main.py:635 Application shutdown initiated...
INFO     backend.app.main:main.py:638 Queue manager stopped.
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_crawl4ai_fetcher_general_options.py::test_smoke_no_params_uses_defaults
FAILED test_crawl4ai_fetcher_general_options.py::test_various_parameter_combinations[api_params0-expected_browser_config_attrs0-expected_crawler_run_config_attrs0]
FAILED test_crawl4ai_fetcher_general_options.py::test_various_parameter_combinations[api_params1-expected_browser_config_attrs1-expected_crawler_run_config_attrs1]
FAILED test_crawl4ai_fetcher_general_options.py::test_various_parameter_combinations[api_params2-expected_browser_config_attrs2-expected_crawler_run_config_attrs2]
FAILED test_crawl4ai_fetcher_general_options.py::test_various_parameter_combinations[api_params3-expected_browser_config_attrs3-expected_crawler_run_config_attrs3]
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
```

## test_crawl4ai_fetcher_llmconfig.py

```
...FF                                                                    [100%]
================================== FAILURES ===================================
_______________ test_llmconfig_missing_provider_or_instructions _______________
test_crawl4ai_fetcher_llmconfig.py:371: in test_llmconfig_missing_provider_or_instructions
    assert any(
E   assert False
E    +  where False = any(<generator object test_llmconfig_missing_provider_or_instructions.<locals>.<genexpr> at 0x00000293C5C05BE0>)
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
_____________________ test_llmconfig_instantiation_errors _____________________
test_crawl4ai_fetcher_llmconfig.py:480: in test_llmconfig_instantiation_errors
    assert called_run_config_correctly, "CrawlerRunConfig not called with extraction_strategy as None/absent after LLMConfig error."
E   AssertionError: CrawlerRunConfig not called with extraction_strategy as None/absent after LLMConfig error.
E   assert False
---------------------------- Captured stdout call -----------------------------
[INIT].... → Crawl4AI 0.6.2
[INIT].... → Crawl4AI 0.6.2
[INIT].... → Crawl4AI 0.6.2
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

backend/app/tests/test_crawl4ai_fetcher_llmconfig.py::test_llmconfig_provider_parsing
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:884: DeprecationWarning: The event_loop fixture provided by pytest-asyncio has been redefined in
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\conftest.py:18
  Replacing the event_loop fixture with a custom implementation is deprecated
  and will lead to errors in the future.
  If you want to request an asyncio event loop with a scope other than function
  scope, use the "loop_scope" argument to the asyncio mark when marking the tests.
  If you want to return different types of event loops, use the event_loop_policy
  fixture.
  
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_crawl4ai_fetcher_llmconfig.py::test_llmconfig_missing_provider_or_instructions
FAILED test_crawl4ai_fetcher_llmconfig.py::test_llmconfig_instantiation_errors
```

## test_crawl4ai_fetcher_markdown_config.py

```
FFFFF
================================== FAILURES ===================================
_______________________ test_markdown_generator_default _______________________
test_crawl4ai_fetcher_markdown_config.py:34: in test_markdown_generator_default
    assert response.status_code == 200
E   assert 405 == 200
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:58,357 - app.main - INFO - --> POST /fetch-content from 127.0.0.1
2025-05-09 15:34:58,358 - app.main - INFO - <-- POST /fetch-content - Status=405 (0.001s)
2025-05-09 15:34:58,358 - httpx - INFO - HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> POST /fetch-content from 127.0.0.1
INFO     app.main:main.py:613 <-- POST /fetch-content - Status=405 (0.001s)
INFO     httpx:_client.py:1786 HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
______________ test_markdown_generator_empty_or_none[-<lambda>] _______________
test_crawl4ai_fetcher_markdown_config.py:208: in test_markdown_generator_empty_or_none
    assert response.status_code == 200, f"Failed for case: {markdown_generator_value}, Response: {response.text}"
E   AssertionError: Failed for case: , Response: {"detail":"Method Not Allowed"}
E   assert 405 == 200
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:58,548 - app.main - INFO - --> POST /fetch-content from 127.0.0.1
2025-05-09 15:34:58,548 - app.main - INFO - <-- POST /fetch-content - Status=405 (0.000s)
2025-05-09 15:34:58,548 - httpx - INFO - HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> POST /fetch-content from 127.0.0.1
INFO     app.main:main.py:613 <-- POST /fetch-content - Status=405 (0.000s)
INFO     httpx:_client.py:1786 HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
____________ test_markdown_generator_empty_or_none[None-<lambda>0] ____________
test_crawl4ai_fetcher_markdown_config.py:208: in test_markdown_generator_empty_or_none
    assert response.status_code == 200, f"Failed for case: {markdown_generator_value}, Response: {response.text}"
E   AssertionError: Failed for case: None, Response: {"detail":"Method Not Allowed"}
E   assert 405 == 200
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:58,553 - app.main - INFO - --> POST /fetch-content from 127.0.0.1
2025-05-09 15:34:58,553 - app.main - INFO - <-- POST /fetch-content - Status=405 (0.000s)
2025-05-09 15:34:58,553 - httpx - INFO - HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> POST /fetch-content from 127.0.0.1
INFO     app.main:main.py:613 <-- POST /fetch-content - Status=405 (0.000s)
INFO     httpx:_client.py:1786 HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
____________ test_markdown_generator_empty_or_none[None-<lambda>1] ____________
test_crawl4ai_fetcher_markdown_config.py:208: in test_markdown_generator_empty_or_none
    assert response.status_code == 200, f"Failed for case: {markdown_generator_value}, Response: {response.text}"
E   AssertionError: Failed for case: None, Response: {"detail":"Method Not Allowed"}
E   assert 405 == 200
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:58,558 - app.main - INFO - --> POST /fetch-content from 127.0.0.1
2025-05-09 15:34:58,558 - app.main - INFO - <-- POST /fetch-content - Status=405 (0.001s)
2025-05-09 15:34:58,558 - httpx - INFO - HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> POST /fetch-content from 127.0.0.1
INFO     app.main:main.py:613 <-- POST /fetch-content - Status=405 (0.001s)
INFO     httpx:_client.py:1786 HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
_______________________ test_markdown_generator_unknown _______________________
test_crawl4ai_fetcher_markdown_config.py:238: in test_markdown_generator_unknown
    assert response.status_code == 200, f"Response: {response.text}"
E   AssertionError: Response: {"detail":"Method Not Allowed"}
E   assert 405 == 200
E    +  where 405 = <Response [405 Method Not Allowed]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:34:58,562 - app.main - INFO - --> POST /fetch-content from 127.0.0.1
2025-05-09 15:34:58,562 - app.main - INFO - <-- POST /fetch-content - Status=405 (0.000s)
2025-05-09 15:34:58,562 - httpx - INFO - HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> POST /fetch-content from 127.0.0.1
INFO     app.main:main.py:613 <-- POST /fetch-content - Status=405 (0.000s)
INFO     httpx:_client.py:1786 HTTP Request: POST http://test/fetch-content "HTTP/1.1 405 Method Not Allowed"
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_default
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:884: DeprecationWarning: The event_loop fixture provided by pytest-asyncio has been redefined in
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\conftest.py:18
  Replacing the event_loop fixture with a custom implementation is deprecated
  and will lead to errors in the future.
  If you want to request an asyncio event loop with a scope other than function
  scope, use the "loop_scope" argument to the asyncio mark when marking the tests.
  If you want to return different types of event loops, use the event_loop_policy
  fixture.
  
    warnings.warn(

backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_default
backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[-<lambda>]
backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[None-<lambda>0]
backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[None-<lambda>1]
backend/app/tests/test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_unknown
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\httpx\_client.py:1437: DeprecationWarning: The 'app' shortcut is now deprecated. Use the explicit style 'transport=ASGITransport(app=...)' instead.
    warnings.warn(message, DeprecationWarning)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_default
FAILED test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[-<lambda>]
FAILED test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[None-<lambda>0]
FAILED test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_empty_or_none[None-<lambda>1]
FAILED test_crawl4ai_fetcher_markdown_config.py::test_markdown_generator_unknown
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
```

## test_fetch_history_saving.py

```
F                                                                        [100%]
================================== FAILURES ===================================
_______________ test_save_crawl4ai_parameters_to_fetch_history ________________
test_fetch_history_saving.py:149: in test_save_crawl4ai_parameters_to_fetch_history
    assert '"status":"completed"' in sse_content or '"type":"completed"' in sse_content, "Fetch did not complete successfully via SSE"
E   AssertionError: Fetch did not complete successfully via SSE
E   assert ('"status":"completed"' in 'data: {"type": "status", "content": "history_created", "timestamp": "2025-05-09T15:35:05.492934", "id": "1746819305.4...pe AsyncMock is not JSON serializable", "timestamp": "2025-05-09T15:35:05.624598", "id": "1746819305.6245987"}\r\n\r\n' or '"type":"completed"' in 'data: {"type": "status", "content": "history_created", "timestamp": "2025-05-09T15:35:05.492934", "id": "1746819305.4...pe AsyncMock is not JSON serializable", "timestamp": "2025-05-09T15:35:05.624598", "id": "1746819305.6245987"}\r\n\r\n')
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:05,054 - app.main - INFO - --> GET /fetch-content from 127.0.0.1
2025-05-09 15:35:05,055 - app.main - INFO - SSE /fetch-content request from 127.0.0.1 for URL: https://example.com/crawlaitest, Engine: crawl4ai, PDF: False, Supabase: False
2025-05-09 15:35:05,246 - app.psearchworking - INFO - Initialized Supabase client singleton
2025-05-09 15:35:05,442 - app.main - INFO - <-- GET /fetch-content - Status=200 (0.388s)
2025-05-09 15:35:05,491 - httpx - INFO - HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
2025-05-09 15:35:05,492 - app.main - INFO - Initial fetch history record created with ID: 30058f67-864a-4180-ba61-ecf7458a7cbe for URL: https://example.com/crawlaitest
2025-05-09 15:35:05,595 - app.main - INFO - Using crawl4ai engine for URL: https://example.com/crawlaitest
2025-05-09 15:35:05,595 - app.crawl4ai_fetcher - INFO - crawl4ai_fetcher called for URL: https://example.com/crawlaitest
2025-05-09 15:35:05,616 - app.crawl4ai_fetcher - INFO - Received deep_crawl_config: strategy='None', params_keys='[]'
2025-05-09 15:35:05,616 - app.crawl4ai_fetcher - INFO - No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
2025-05-09 15:35:05,616 - app.crawl4ai_fetcher - INFO - Processed extraction_config: strategy='None', params_keys='[]'
2025-05-09 15:35:05,616 - app.crawl4ai_fetcher - INFO - No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
2025-05-09 15:35:05,616 - app.crawl4ai_fetcher - INFO - No specific markdown_generator provided. Using crawl4ai default.
2025-05-09 15:35:05,621 - app.crawl4ai_fetcher - INFO - Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
2025-05-09 15:35:05,622 - app.crawl4ai_fetcher - INFO - AsyncWebCrawler context entered for URL: https://example.com/crawlaitest
2025-05-09 15:35:05,623 - app.crawl4ai_fetcher - ERROR - Error in crawl4ai_fetcher for URL https://example.com/crawlaitest: Object of type AsyncMock is not JSON serializable
Traceback (most recent call last):
  File "C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\crawl4ai_fetcher.py", line 516, in fetch_with_crawl4ai
    yield json.dumps({"type": "completed", "status": "completed", "message": "Crawl4ai fetch complete.", "data": final_data_payload})
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type AsyncMock is not JSON serializable
2025-05-09 15:35:05,624 - app.main - ERROR - Error event from crawl4ai_fetcher: An error occurred during crawl4ai fetch: Object of type AsyncMock is not JSON serializable
2025-05-09 15:35:05,625 - app.main - INFO - SSE /fetch-content event generator finished for 127.0.0.1, URL: https://example.com/crawlaitest
2025-05-09 15:35:05,625 - httpx - INFO - HTTP Request: GET http://test/fetch-content?url=https%3A%2F%2Fexample.com%2Fcrawlaitest&engine=crawl4ai&generate_pdf=false&upload_to_supabase=false&headless=false&user_agent=Test%20User%20Agent%20For%20Crawl4AI%20History&browser_engine=playwright&extraction_strategy=llm&output_format=markdown&token_budget=3000&llm_provider=openai&llm_model_name=gpt-4o-mini-test&llm_temperature=0.5&respect_robots_txt=false&crawl4ai_interaction_timeout_ms=45000&take_screenshot=true&page_load_wait_condition=networkidle&target_elements_css_selectors=article%2C%20.content&excluded_elements_css_selector=.ads%2C%20.header&process_iframes_content=true&cache_mode=BYPASS "HTTP/1.1 200 OK"
------------------------------ Captured log call ------------------------------
INFO     app.main:main.py:609 --> GET /fetch-content from 127.0.0.1
INFO     app.main:main.py:1617 SSE /fetch-content request from 127.0.0.1 for URL: https://example.com/crawlaitest, Engine: crawl4ai, PDF: False, Supabase: False
INFO     app.psearchworking:psearchworking.py:510 Initialized Supabase client singleton
INFO     app.main:main.py:613 <-- GET /fetch-content - Status=200 (0.388s)
INFO     httpx:_client.py:1038 HTTP Request: POST https://supabasepmoves.cataclysmstudios.net/rest/v1/fetch_history "HTTP/2 201 Created"
INFO     app.main:main.py:1701 Initial fetch history record created with ID: 30058f67-864a-4180-ba61-ecf7458a7cbe for URL: https://example.com/crawlaitest
INFO     app.main:main.py:1728 Using crawl4ai engine for URL: https://example.com/crawlaitest
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:95 crawl4ai_fetcher called for URL: https://example.com/crawlaitest
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:170 Received deep_crawl_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:264 No specific deep crawl strategy selected or 'None/Default'. Crawler will use its default behavior (no deep crawling).
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:314 Processed extraction_config: strategy='None', params_keys='[]'
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:394 No specific extraction strategy selected or 'None/Default'. Using crawl4ai default behavior.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:469 No specific markdown_generator provided. Using crawl4ai default.
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:483 Current asyncio event loop policy before AsyncWebCrawler init: WindowsProactorEventLoopPolicy
INFO     app.crawl4ai_fetcher:crawl4ai_fetcher.py:485 AsyncWebCrawler context entered for URL: https://example.com/crawlaitest
ERROR    app.crawl4ai_fetcher:crawl4ai_fetcher.py:524 Error in crawl4ai_fetcher for URL https://example.com/crawlaitest: Object of type AsyncMock is not JSON serializable
Traceback (most recent call last):
  File "C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\crawl4ai_fetcher.py", line 516, in fetch_with_crawl4ai
    yield json.dumps({"type": "completed", "status": "completed", "message": "Crawl4ai fetch complete.", "data": final_data_payload})
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\json\encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type AsyncMock is not JSON serializable
ERROR    app.main:main.py:1757 Error event from crawl4ai_fetcher: An error occurred during crawl4ai fetch: Object of type AsyncMock is not JSON serializable
INFO     app.main:main.py:2008 SSE /fetch-content event generator finished for 127.0.0.1, URL: https://example.com/crawlaitest
INFO     httpx:_client.py:1786 HTTP Request: GET http://test/fetch-content?url=https%3A%2F%2Fexample.com%2Fcrawlaitest&engine=crawl4ai&generate_pdf=false&upload_to_supabase=false&headless=false&user_agent=Test%20User%20Agent%20For%20Crawl4AI%20History&browser_engine=playwright&extraction_strategy=llm&output_format=markdown&token_budget=3000&llm_provider=openai&llm_model_name=gpt-4o-mini-test&llm_temperature=0.5&respect_robots_txt=false&crawl4ai_interaction_timeout_ms=45000&take_screenshot=true&page_load_wait_condition=networkidle&target_elements_css_selectors=article%2C%20.content&excluded_elements_css_selector=.ads%2C%20.header&process_iframes_content=true&cache_mode=BYPASS "HTTP/1.1 200 OK"
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

backend/app/tests/test_fetch_history_saving.py::test_save_crawl4ai_parameters_to_fetch_history
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pytest_asyncio\plugin.py:884: DeprecationWarning: The event_loop fixture provided by pytest-asyncio has been redefined in
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\tests\conftest.py:18
  Replacing the event_loop fixture with a custom implementation is deprecated
  and will lead to errors in the future.
  If you want to request an asyncio event loop with a scope other than function
  scope, use the "loop_scope" argument to the asyncio mark when marking the tests.
  If you want to return different types of event loops, use the event_loop_policy
  fixture.
  
    warnings.warn(

backend/app/tests/test_fetch_history_saving.py::test_save_crawl4ai_parameters_to_fetch_history
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\httpx\_client.py:1437: DeprecationWarning: The 'app' shortcut is now deprecated. Use the explicit style 'transport=ASGITransport(app=...)' instead.
    warnings.warn(message, DeprecationWarning)

backend/app/tests/test_fetch_history_saving.py::test_save_crawl4ai_parameters_to_fetch_history
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\_pytest\stash.py:108: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    del self._storage[key]
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_fetch_history_saving.py::test_save_crawl4ai_parameters_to_fetch_history
```

## test_search_config.py

```
FFFFF
================================== FAILURES ===================================
___________________________ test_get_search_config ____________________________
test_search_config.py:15: in test_get_search_config
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
---------------------------- Captured stderr setup ----------------------------
2025-05-09 15:35:12,109 - backend.app.main - INFO - Application startup initiated...
2025-05-09 15:35:12,109 - backend.app.main - INFO - System metrics collection scheduled.
2025-05-09 15:35:12,109 - backend.app.main - INFO - Queue manager started.
----------------------------- Captured log setup ------------------------------
INFO     backend.app.main:main.py:621 Application startup initiated...
INFO     backend.app.main:main.py:626 System metrics collection scheduled.
INFO     backend.app.main:main.py:627 Queue manager started.
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:12,120 - backend.app.main - INFO - --> GET /api/search-config from testclient
2025-05-09 15:35:12,120 - backend.app.main - INFO - <-- GET /api/search-config - Status=404 (0.000s)
2025-05-09 15:35:12,121 - httpx - INFO - HTTP Request: GET http://testserver/api/search-config "HTTP/1.1 404 Not Found"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /api/search-config from testclient
INFO     backend.app.main:main.py:613 <-- GET /api/search-config - Status=404 (0.000s)
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/api/search-config "HTTP/1.1 404 Not Found"
__________________________ test_update_search_config __________________________
test_search_config.py:44: in test_update_search_config
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:12,306 - backend.app.main - INFO - --> GET /api/search-config from testclient
2025-05-09 15:35:12,306 - backend.app.main - INFO - <-- GET /api/search-config - Status=404 (0.000s)
2025-05-09 15:35:12,307 - httpx - INFO - HTTP Request: GET http://testserver/api/search-config "HTTP/1.1 404 Not Found"
2025-05-09 15:35:12,307 - backend.app.main - INFO - --> POST /api/search-config from testclient
2025-05-09 15:35:12,308 - backend.app.main - INFO - <-- POST /api/search-config - Status=404 (0.001s)
2025-05-09 15:35:12,308 - httpx - INFO - HTTP Request: POST http://testserver/api/search-config "HTTP/1.1 404 Not Found"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /api/search-config from testclient
INFO     backend.app.main:main.py:613 <-- GET /api/search-config - Status=404 (0.000s)
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/api/search-config "HTTP/1.1 404 Not Found"
INFO     backend.app.main:main.py:609 --> POST /api/search-config from testclient
INFO     backend.app.main:main.py:613 <-- POST /api/search-config - Status=404 (0.001s)
INFO     httpx:_client.py:1038 HTTP Request: POST http://testserver/api/search-config "HTTP/1.1 404 Not Found"
______________________________ test_get_presets _______________________________
test_search_config.py:62: in test_get_presets
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:12,311 - backend.app.main - INFO - --> GET /api/search-config/presets from testclient
2025-05-09 15:35:12,311 - backend.app.main - INFO - <-- GET /api/search-config/presets - Status=404 (0.000s)
2025-05-09 15:35:12,312 - httpx - INFO - HTTP Request: GET http://testserver/api/search-config/presets "HTTP/1.1 404 Not Found"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /api/search-config/presets from testclient
INFO     backend.app.main:main.py:613 <-- GET /api/search-config/presets - Status=404 (0.000s)
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/api/search-config/presets "HTTP/1.1 404 Not Found"
___________________________ test_get_preset_config ____________________________
test_search_config.py:75: in test_get_preset_config
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:12,315 - backend.app.main - INFO - --> GET /api/search-config/preset/technical from testclient
2025-05-09 15:35:12,315 - backend.app.main - INFO - <-- GET /api/search-config/preset/technical - Status=404 (0.000s)
2025-05-09 15:35:12,316 - httpx - INFO - HTTP Request: GET http://testserver/api/search-config/preset/technical "HTTP/1.1 404 Not Found"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> GET /api/search-config/preset/technical from testclient
INFO     backend.app.main:main.py:613 <-- GET /api/search-config/preset/technical - Status=404 (0.000s)
INFO     httpx:_client.py:1038 HTTP Request: GET http://testserver/api/search-config/preset/technical "HTTP/1.1 404 Not Found"
______________________________ test_load_preset _______________________________
test_search_config.py:91: in test_load_preset
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
---------------------------- Captured stderr call -----------------------------
2025-05-09 15:35:12,319 - backend.app.main - INFO - --> POST /api/search-config/preset from testclient
2025-05-09 15:35:12,319 - backend.app.main - INFO - <-- POST /api/search-config/preset - Status=404 (0.000s)
2025-05-09 15:35:12,319 - httpx - INFO - HTTP Request: POST http://testserver/api/search-config/preset "HTTP/1.1 404 Not Found"
------------------------------ Captured log call ------------------------------
INFO     backend.app.main:main.py:609 --> POST /api/search-config/preset from testclient
INFO     backend.app.main:main.py:613 <-- POST /api/search-config/preset - Status=404 (0.000s)
INFO     httpx:_client.py:1038 HTTP Request: POST http://testserver/api/search-config/preset "HTTP/1.1 404 Not Found"
-------------------------- Captured stderr teardown ---------------------------
2025-05-09 15:35:12,322 - backend.app.main - INFO - Application shutdown initiated...
2025-05-09 15:35:12,322 - backend.app.main - INFO - Queue manager stopped.
---------------------------- Captured log teardown ----------------------------
INFO     backend.app.main:main.py:635 Application shutdown initiated...
INFO     backend.app.main:main.py:638 Queue manager stopped.
============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\ctranslate2\__init__.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\ctranslate2\__init__.py:8: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    import pkg_resources

..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:5
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:5: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_search_engine_binary = read_text("fake_http_header.data", "top-level-domain-to-search-engines.json")

..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
..\..\..\..\..\..\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79
  C:\Users\russe\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\Lib\importlib\resources\_legacy.py:79: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with open_text(package, resource, encoding, errors) as fp:

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:6
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:6: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    domain_to_languages_binary = read_text("fake_http_header.data", "top-level-domain-to-languages.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:7
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:7: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_user_agent = read_text("fake_http_header.data", "browser-to-user-agent.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:8
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:8: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    encoding_values_dict_binary = read_text("fake_http_header.data", "encoding-values.json")

..\..\..\.venv\Lib\site-packages\fake_http_header\constants.py:9
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fake_http_header\constants.py:9: DeprecationWarning: read_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    browser_to_accept_value_binary = read_text("fake_http_header.data", "browser-to-accept-values.json")

..\routes\content_upserter.py:30
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\routes\content_upserter.py:30: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    @validator('date', pre=True)

..\main.py:619
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:619: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
..\..\..\.venv\Lib\site-packages\fastapi\applications.py:4495
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\.venv\Lib\site-packages\fastapi\applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

..\main.py:633
  C:\Users\russe\Documents\GitHub\PMOVES-transcribe-and-fetch\backend\app\main.py:633: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_search_config.py::test_get_search_config - assert 404 == 200
FAILED test_search_config.py::test_update_search_config - assert 404 == 200
FAILED test_search_config.py::test_get_presets - assert 404 == 200
FAILED test_search_config.py::test_get_preset_config - assert 404 == 200
FAILED test_search_config.py::test_load_preset - assert 404 == 200
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
```

All tests complete. Results saved to test_results.md.
