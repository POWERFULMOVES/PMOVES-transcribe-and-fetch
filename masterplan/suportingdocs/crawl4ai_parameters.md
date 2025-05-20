# `crawl4ai` Parameter Compilation Report

## Confirmation of Full Documentation Retrieval
Based on the analysis of the initial truncated fetch from `https://docs.crawl4ai.com/api/parameters/` (as detailed in `docs/searchstopped.md`) and the content of the subsequent fetch, it is confirmed that the complete parameter documentation from the target URL appears to have been successfully retrieved. The second fetch provided content immediately following the truncation point, leading into standard website footer information, indicating no further parameter definitions were missed.

## Comprehensive `crawl4ai` Parameter List

### I. `BrowserConfig` Parameters
*(Controls the browser environment; typically set once when initializing `AsyncWebCrawler`)*

*   `browser_type`: Specifies the browser engine to use (e.g., "chromium", "firefox", "webkit"). (Type: `str` / Default: `"chromium"`)
*   `headless`: Boolean indicating whether to run the browser in headless mode. True for no visible UI. (Type: `bool` / Default: `True`)
*   `viewport_width`: Initial page width in pixels. (Type: `int` / Default: `1080`)
*   `viewport_height`: Initial page height in pixels. (Type: `int` / Default: `600`)
*   `proxy`: Single proxy URL string (e.g., `"http://user:pass@proxy:8080"`). (Type: `str` / Default: `None`)
*   `proxy_config`: Dictionary for advanced or multi-proxy setups. (Type: `dict` / Default: `None`)
*   `use_persistent_context`: If True, uses a persistent browser context, keeping cookies and sessions across runs. (Type: `bool` / Default: `False`)
*   `user_data_dir`: Directory path to store user data (profiles, cookies) for persistent sessions. (Type: `str` / Default: `None`)
*   `ignore_https_errors`: If True, continues navigation despite invalid SSL certificates. (Type: `bool` / Default: `True`)
*   `java_script_enabled`: Enables or disables JavaScript execution on pages. (Type: `bool` / Default: `True`)
*   `cookies`: A list of cookie dictionaries to pre-set in the browser. (Type: `list[dict]` / Default: `None`)
*   `headers`: Dictionary of extra HTTP headers to send with every request. (Type: `dict` / Default: `None`)
*   `user_agent`: Custom user agent string. Can be set to `"random"` if `user_agent_mode="random"`. (Type: `str` / Default: `None`, uses Playwright default)
*   `light_mode`: If True, disables some background features like images and CSS for potentially faster, lighter crawls. (Type: `bool` / Default: `False`)
*   `text_mode`: If True, attempts to disable images and other heavy content to focus on text extraction for speed. (Type: `bool` / Default: `False`)
*   `use_managed_browser`: For advanced interactions using the Chrome DevTools Protocol (CDP). (Type: `bool` / Default: `False`)
*   `extra_args`: A list of additional command-line arguments to pass to the browser instance on launch. (Type: `list[str]` / Default: `None`)

### II. `CrawlerRunConfig` Parameters
*(Controls individual crawl operations; typically passed to `arun()` or `arun_many()` methods)*

#### A) Content Processing & Extraction
*   `word_count_threshold`: Minimum word count for a text block to be considered significant content. (Type: `int` / Default: `~200`)
*   `extraction_strategy`: An instance of an `ExtractionStrategy` subclass (e.g., `JsonCssExtractionStrategy`, `LLMExtractionStrategy`) to define how structured data is extracted. (Type: `ExtractionStrategy` / Default: `None`)
*   `markdown_generator`: An instance of a `MarkdownGenerationStrategy` subclass to customize Markdown output. (Type: `MarkdownGenerationStrategy` / Default: `DefaultMarkdownGenerator()`)
*   `css_selector`: A CSS selector string. Only content within elements matching this selector will be processed. (Type: `str` / Default: `None`)
*   `target_elements`: A list of CSS selectors for elements to specifically focus on for markdown generation or data extraction. (Type: `list[str]` / Default: `None`)
*   `excluded_tags`: A list of HTML tags (e.g., `"script"`, `"style"`) to remove from the content before processing. (Type: `list[str]` / Default: Common non-content tags)
*   `excluded_selector`: A CSS selector string for elements to exclude from processing (e.g., `"#ads, .tracker"`). (Type: `str` / Default: `None`)
*   `only_text`: If True, attempts to extract only the textual content, stripping most HTML tags. (Type: `bool` / Default: `False`)
*   `prettify_html`: If True, beautifies the final cleaned HTML output (cosmetic, may slow down processing). (Type: `bool` / Default: `False`)
*   `keep_data_attributes`: If True, preserves `data-*` attributes in the cleaned HTML. (Type: `bool` / Default: `False`)
*   `remove_forms`: If True, removes all `<form>` elements from the content. (Type: `bool` / Default: `False`)
*   `process_iframes`: If True, attempts to inline content from `<iframe>` elements for single-page extraction. (Type: `bool` / Default: `False`)

#### B) Caching & Session
*   `cache_mode`: A `CacheMode` enum value (`ENABLED`, `BYPASS`, `WRITE_ONLY`, `READ_ONLY`, `DISABLED`) or `None`. Controls caching behavior. (Type: `CacheMode` / Default: `CacheMode.ENABLED`)
*   `session_id`: A unique string ID to reuse a browser session across multiple `arun()` calls. (Type: `str` / Default: `None`)
*   `bypass_cache`: Shortcut for `CacheMode.BYPASS`. If True, ignores cache reads and writes. (Type: `bool` / Default: `False`)
*   `disable_cache`: Shortcut for `CacheMode.DISABLED`. If True, disables caching entirely. (Type: `bool` / Default: `False`)
*   `no_cache_read`: Shortcut for `CacheMode.WRITE_ONLY`. If True, writes to cache but doesn't read from it. (Type: `bool` / Default: `False`)
*   `no_cache_write`: Shortcut for `CacheMode.READ_ONLY`. If True, reads from cache but doesn't write to it. (Type: `bool` / Default: `False`)

#### C) Page Navigation & Timing
*   `wait_until`: Navigation completion condition (e.g., `"domcontentloaded"`, `"load"`, `"networkidle"`). (Type: `str` / Default: `"domcontentloaded"`)
*   `page_timeout`: Timeout in milliseconds for page navigation or JavaScript execution steps. (Type: `int` / Default: `60000`)
*   `wait_for`: A CSS selector (e.g., `"css:.article-loaded"`) or JavaScript condition (e.g., `"js:() => document.readyState === 'complete'"`) to wait for before extraction. (Type: `str` / Default: `None`)
*   `wait_for_images`: If True, waits for images to load before proceeding. (Type: `bool` / Default: `False`)
*   `delay_before_return_html`: Additional pause in seconds before capturing the final HTML. (Type: `float` / Default: `0.1`)
*   `mean_delay`: For `arun_many()`, the base for random delay interval in seconds between crawls. (Type: `float` / Default: `0.1`)
*   `max_range`: For `arun_many()`, the range for random delay interval (actual delay = `mean_delay` +/- `max_range`). (Type: `float` / Default: `0.3`)
*   `semaphore_count`: Maximum number of concurrent crawls for `arun_many()`. (Type: `int` / Default: `5`)

#### D) Page Interaction
*   `js_code`: A string or list of strings containing JavaScript code to execute on the page after it loads. (Type: `str` or `list[str]` / Default: `None`)
*   `js_only`: If True, reuses an existing browser session for JavaScript execution without a full page reload. (Type: `bool` / Default: `False`)
*   `scan_full_page`: If True, automatically scrolls the page to load dynamic content (e.g., infinite scroll). (Type: `bool` / Default: `False`)
*   `scroll_delay`: Delay in seconds between scrolls if `scan_full_page` is True. (Type: `float` / Default: `0.2`)
*   `remove_overlay_elements`: If True, attempts to identify and remove common overlay elements like modals or popups. (Type: `bool` / Default: `False`)
*   `simulate_user`: If True, simulates mouse movements to potentially avoid bot detection. (Type: `bool` / Default: `False`)
*   `override_navigator`: If True, overrides JavaScript `navigator` properties for stealth purposes. (Type: `bool` / Default: `False`)
*   `magic`: If True, enables experimental automatic handling of popups and consent banners. (Type: `bool` / Default: `False`)

#### E) Media Handling
*   `screenshot`: If True, captures a screenshot of the page (returned as base64 encoded string). (Type: `bool` / Default: `False`)
*   `pdf`: If True, generates a PDF of the page. (Type: `bool` / Default: `False`)
*   `capture_mhtml`: If True, captures an MHTML snapshot of the page. (Type: `bool` / Default: `False`)
*   `image_description_min_word_threshold`: Minimum word count for an image's alt text to be considered valid. (Type: `int` / Default: `~50`)
*   `image_score_threshold`: Threshold for filtering out low-scoring or irrelevant images. (Type: `int` / Default: `~3`)
*   `exclude_external_images`: If True, excludes images hosted on domains different from the crawled page. (Type: `bool` / Default: `False`)

#### F) Link/Domain Handling
*   `exclude_social_media_domains`: A list of social media domain strings to exclude from link processing or following. (Type: `list[str]` / Default: Standard list like Facebook, Twitter)
*   `exclude_external_links`: If True, removes links pointing to domains different from the current page's domain. (Type: `bool` / Default: `False`)
*   `exclude_social_media_links`: If True, removes links pointing to social media sites. (Type: `bool` / Default: `False`)
*   `exclude_domains`: A custom list of domain strings to exclude (e.g., `["ads.com", "trackers.io"]`). (Type: `list[str]` / Default: `[]`)

#### G) Debug & Logging
*   `verbose`: If True, prints detailed logs detailing each step of crawling, interactions, or errors. (Type: `bool` / Default: `True`)
*   `log_console`: If True, logs the page’s JavaScript console output for deeper JS debugging. (Type: `bool` / Default: `False`)

#### H) Compliance & Ethics
*   `check_robots_txt`: If True, checks and respects `robots.txt` rules before crawling. Uses an efficient caching mechanism with an SQLite backend. (Type: `bool` / Default: `False`)
*   `user_agent`: The user agent string to identify your crawler. This is also used for `robots.txt` checking when enabled. (Type: `str` / Default: `None`)

### III. `LLMConfig` Parameters
*(For configuring LLM providers used in strategies like `LLMExtractionStrategy` or `LLMContentFilter`)*

*   `provider`: String identifying the LLM provider and model to use. Examples: `"ollama/llama3"`, `"groq/llama3-70b-8192"`, `"openai/gpt-4o-mini"`. (Type: `str` / Default: `"openai/gpt-4o-mini"`)
*   `api_token`: API token for the specified LLM provider.
    *   Optional: If not provided, the library attempts to read it from environment variables based on the provider (e.g., `GEMINI_API_KEY` for Gemini models).
    *   Can be an environment variable reference (e.g., `"env:GROQ_API_KEY"`).
    (Type: `str` / Default: `None` or read from environment variable)
*   `base_url`: Custom API endpoint URL if your LLM provider uses one (e.g., for self-hosted models or proxies). (Type: `str` / Default: `None` or provider's default)
### IV. Deep Crawling Strategy Parameters
*(Parameters for configuring deep crawling strategies like `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, and `BestFirstCrawlingStrategy`)*

#### A) Common Deep Crawling Strategy Parameters
*(These parameters are generally applicable to `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, and `BestFirstCrawlingStrategy` unless specified otherwise in their respective sections.)*

*   `max_depth`: The maximum depth to crawl. (Type: `int` / Required)
*   `filter_chain`: An instance of `FilterChain` used to filter URLs during the crawl. (Type: `FilterChain` / Default: `FilterChain()`)
*   `url_scorer`: An optional `URLScorer` instance to score URLs, influencing crawl order or selection. Crucial for `BestFirstCrawlingStrategy`. (Type: `Optional[URLScorer]` / Default: `None`)
*   `include_external`: If True, allows the crawler to follow links to external domains. (Type: `bool` / Default: `False`)
*   `max_pages`: The maximum number of pages to crawl. (Type: `int` / Default: `float('inf')`)
*   `logger`: An optional `logging.Logger` instance for custom logging. (Type: `Optional[logging.Logger]` / Default: `None`)

#### B) `BFSDeepCrawlStrategy` & `DFSDeepCrawlStrategy` Specific Parameters
*(These strategies share the common parameters and have the following additional/specific ones.)*

*   `score_threshold`: A threshold for the `url_scorer`. URLs scoring below this threshold might be ignored or deprioritized. (Type: `float` / Default: `float('-inf')`)
    *   *Note: While `url_scorer` is optional for BFS/DFS, `score_threshold` is relevant if a scorer is provided.*

#### C) `BestFirstCrawlingStrategy` Specific Parameters
*(This strategy shares the common parameters. Key distinctions are highlighted below.)*

*   `url_scorer`: **Crucial for this strategy.** The `BestFirstCrawlingStrategy` relies heavily on the `url_scorer` to prioritize which URLs to visit next. Without a meaningful scorer, its effectiveness is limited. (Type: `Optional[URLScorer]` / Default: `None` - but highly recommended to be set)
    *   *Note: `score_threshold` is not explicitly listed as a direct constructor parameter for `BestFirstCrawlingStrategy` in the provided research, unlike BFS/DFS. The scoring mechanism directly influences the priority queue.*

#### D) `FilterChain` Configuration
*(Used by deep crawling strategies to filter which URLs are considered for crawling.)*

*   `FilterChain` is initialized with a list of `URLFilter` instances.
    *   Example: `filters = [URLPatternFilter(patterns=[r"https://example.com/products/.*"]), URLPatternFilter(patterns=[r".*/blog/.*"], filter_type="exclude")]`
    *   `filter_chain = FilterChain(filters=filters)`
*   **`URLPatternFilter`**: A common `URLFilter` that filters URLs based on a list of regular expression patterns.
    *   `patterns`: A list of strings or compiled regex patterns. (Type: `List[Union[str, Pattern]]`)
    *   `filter_type`: Can be `"include"` (default) or `"exclude"`. If "include", URLs must match one ofr the patterns. If "exclude", URLs matching any pattern are discarded.

#### E) `URLScorer` Configuration (Example: `KeywordRelevanceScorer`)
*(Used by deep crawling strategies, especially `BestFirstCrawlingStrategy`, to score and prioritize URLs.)*

*   `URLScorer` is a base class. Implementations like `KeywordRelevanceScorer` provide specific scoring logic.
*   **`KeywordRelevanceScorer`**: Scores URLs based on the presence and relevance of specified keywords found in the URL string or potentially in fetched content (depending on implementation details not fully covered here).
    *   Initialized with `keywords`: A list of keywords to score against. (Type: `List[str]`)
    *   Example: `scorer = KeywordRelevanceScorer(keywords=["ai", "machine learning", "data science"])`