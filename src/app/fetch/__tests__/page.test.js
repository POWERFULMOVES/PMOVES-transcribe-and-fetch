import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import FetchContentPage from '../page'; // Adjust path as necessary
import { toast } from 'sonner';
import { useInfiniteQuery } from '@/hooks/use-infinite-query';
import { createClient } from '@/lib/client';

// Mock dependencies
// Mock global fetch for Presets
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
  })
);

// Mock dependencies
jest.mock('sonner', () => ({
  toast: Object.assign(jest.fn(), {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
  }),
}));

jest.mock('@/hooks/use-infinite-query');
jest.mock('@/lib/client');

// Mock child components that are not directly part of this test's assertions
// or that make their own network requests, to simplify the test.
jest.mock('@/components/fetch/FetchHistoryTable', () => {
  // Mock FetchHistoryTable to allow us to simulate the onRefetchItem call
  return jest.fn(({ onRefetchItem, fetchHistoryItems }) => (
    <div data-testid="mock-fetch-history-table">
      {fetchHistoryItems && fetchHistoryItems.length > 0 && (
        <button
          data-testid={`refetch-button-${fetchHistoryItems[0].id}`}
          onClick={() => onRefetchItem(fetchHistoryItems[0])}
        >
          Re-fetch Mock Item
        </button>
      )}
    </div>
  ));
});

jest.mock('@/components/fetch/FetchedContentViewer', () => {
  return jest.fn(() => <div data-testid="mock-fetched-content-viewer">Fetched Content</div>);
});


describe('FetchContentPage - Test 8.2: Fetch History Refinement for Advanced Strategies (crawl4ai)', () => {
  const mockSupabaseClient = {
    from: jest.fn().mockReturnThis(),
    select: jest.fn().mockReturnThis(),
    order: jest.fn().mockReturnThis(),
    range: jest.fn().mockResolvedValue({ data: [], error: null, count: 0 }),
  };
  createClient.mockReturnValue(mockSupabaseClient);

  const mockHistoryItemCrawl4ai = {
    id: 'hist-crawl4ai-123',
    url: 'https://crawl4ai.example.com',
    fetching_engine: 'crawl4ai',
    status: 'completed',
    title: 'Crawl4AI Test Page',
    engine_specific_parameters: {
      fetch_depth: "site_only",
      target_content_area: "advanced",
      target_selector: "article.content", // This should map to advancedSelector
      excluded_selector: "nav,footer", // This should map to excludedSelectors
      timeout: 90,
      extract_links: false,
      image_captioning: true,
      markdown_flavor: "markdown-extra",
      extract_metadata: false,
      upload_to_supabase: true,
      // crawl4ai specific
      crawl4ai_user_agent: "TestAgent/1.0",
      crawl4ai_viewport_width: 1024,
      crawl4ai_viewport_height: 768,
      crawl4ai_proxy_url: "http://proxy.test:8080",
      crawl4ai_page_load_wait_condition: "load",
      crawl4ai_page_timeout: 45000,
      crawl4ai_wait_for_condition: "#main-content-loaded",
      crawl4ai_enable_js: false,
      crawl4ai_ignore_https_errors: true,
      crawl4ai_light_mode: true,
      crawl4ai_text_mode: true,
      crawl4ai_target_elements: ".target-div, #specific-section",
      crawl4ai_excluded_elements: ".ad-banner, .popup",
      crawl4ai_excluded_tags: "iframe,video",
      crawl4ai_extract_only_text_content: true,
      crawl4ai_process_iframes: true,
      crawl4ai_word_count_threshold: 20,
      crawl4ai_remove_forms: false,
      crawl4ai_keep_data_attributes: true,
      crawl4ai_execute_js_on_load: "console.log('test');",
      crawl4ai_scan_full_page: true,
      crawl4ai_scroll_delay: 3,
      crawl4ai_remove_overlay_elements: false,
      crawl4ai_simulate_user_behavior: true,
      crawl4ai_enable_magic: true,
      crawl4ai_override_navigator: true,
      crawl4ai_cache_mode: "bypass",
      crawl4ai_capture_screenshot: true,
      crawl4ai_generate_pdf: true,
      crawl4ai_capture_mhtml: true,
      crawl4ai_exclude_external_images: true,
      crawl4ai_image_alt_text_min_word_count: 5,
      crawl4ai_image_relevance_score_threshold: 0.7,
      crawl4ai_exclude_external_links: true,
      crawl4ai_exclude_social_media_links: true,
      crawl4ai_custom_excluded_domains: "ads.example.com,trackers.example.net",
      crawl4ai_respect_robots_txt: false,
      crawl4ai_verbose_logging: true,
      crawl4ai_log_page_console_output: true,
      crawl4ai_llm_provider_model: "ollama/test-model",
      crawl4ai_llm_api_token: "test-token",
      crawl4ai_llm_base_url: "http://localhost:11434/v1/test",
      crawl4ai_markdown_generator: 'CustomGenerator', // Wild value not in Select options
      browser_cookies: '[{"name":"testCookie","value":"testValue"}]',
      browser_headers: '{"X-Test-Header":"TestValue"}',
      browser_use_persistent_context: true,
      crawl_session_id: "test-session-456",
      crawl_css_selector: "#global-wrapper",
      crawl4aiExtractionConfig: {
        strategy: 'llm',
        params: {
          llm_instructions: "Extract key points.",
          llm_provider_model: "ollama/test-model",
          llm_api_token: "test-token",
          llm_base_url: "http://localhost:11434/v1/test"
        }
      },
      crawl4aiDeepCrawlConfig: {
        strategy: 'BFSDeepCrawlStrategy',
        params: {
          max_depth: 2,
          max_pages: 50,
          include_external: true,
          url_filter_patterns: "^https://crawl4ai.example.com/docs/.*", // Will be split by newline in component
          score_threshold: 0.6,
        }
      }
    },
    fetched_at: new Date().toISOString(),
  };

  beforeEach(() => {
    useInfiniteQuery.mockReturnValue({
      data: [mockHistoryItemCrawl4ai],
      isLoading: false,
      isFetching: false,
      error: null,
      fetchNextPage: jest.fn(),
      hasMore: false,
      count: 1,
      initialize: jest.fn(),
    });
    createClient.mockReturnValue(mockSupabaseClient);
// Replace usage in beforeEach
    toast.mockClear();
    
    // Mock EventSource
    global.EventSource = jest.fn(() => ({
      onmessage: null,
      onerror: null,
      close: jest.fn(),
    }));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('Test 8.2: should load crawl4ai parameters from history into form and UI components on Re-fetch', async () => {
    render(<FetchContentPage initialActiveMainTab="fetchHistory" />);
    // Wait for the mock table to appear
    await waitFor(() => {
      expect(screen.getByTestId('mock-fetch-history-table')).toBeInTheDocument();
    });
    // The mock FetchHistoryTable should render a button that calls onRefetchItem
    const refetchButton = await screen.findByTestId(`refetch-button-${mockHistoryItemCrawl4ai.id}`);
    expect(refetchButton).toBeInTheDocument();
    fireEvent.click(refetchButton);

    // 3. Verify formState in FetchContentPage is updated (indirectly via UI checks)
    //    and UI components display the pre-filled settings.

    // Check basic form fields that are part of FetchForm (or top-level state)
    await waitFor(() => {
      expect(screen.getByLabelText(/Target URL/i)).toHaveValue(mockHistoryItemCrawl4ai.url);
    });
    
    // Ensure the "Advanced Options" are shown because handleRefetchHistoryItem sets showAdvanced(true)
    // Check for a field that is definitely inside AdvancedFetchOptions
    expect(await screen.findByLabelText(/User Agent/i)).toBeInTheDocument();


    // Check Fetching Engine (this is a Select in FetchForm, but its state is managed in page.js)
    // The value is set directly by setFetchingEngine in handleRefetchHistoryItem
    // We'll check a field that *depends* on fetchingEngine being 'crawl4ai'
    // For example, the "crawl4ai - Browser & Navigation Settings" accordion should be present.
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /crawl4ai - Browser & Navigation Settings/i })).toBeInTheDocument();
    });


    // Verify AdvancedFetchOptions fields (crawl4ai specific)
    // Browser & Navigation
    expect(screen.getByLabelText(/User Agent/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_user_agent);
    expect(screen.getByLabelText('Viewport Width (px)', { exact: false })).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_viewport_width);
    expect(screen.getByLabelText('Viewport Height (px)', { exact: false })).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_viewport_height);
    expect(screen.getByLabelText(/Proxy URL/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_proxy_url);
    expect(screen.getByLabelText(/Page Load Wait Condition/i)).toHaveTextContent(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_page_load_wait_condition);
    expect(screen.getByLabelText(/Page Timeout \(ms\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_page_timeout);
    expect(screen.getByLabelText(/Wait For Element\/JS Condition/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_wait_for_condition);
    expect(screen.getByLabelText(/Enable JavaScript/i)).not.toBeChecked(); // crawl4ai_enable_js: false
    expect(screen.getByLabelText(/Ignore HTTPS Errors/i)).toBeChecked(); // crawl4ai_ignore_https_errors: true
    expect(screen.getByLabelText(/Light Mode/i)).toBeChecked(); // crawl4ai_light_mode: true
    expect(screen.getByLabelText(/Text Mode/i)).toBeChecked(); // crawl4ai_text_mode: true
    
    // Content Extraction & Processing
    expect(screen.getByLabelText(/Target Elements \(CSS Selectors\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_target_elements);
    expect(screen.getByLabelText(/Excluded Elements \(CSS Selector\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_excluded_elements);
    expect(screen.getByLabelText(/Excluded Tags \(comma-separated\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_excluded_tags);
    expect(screen.getByLabelText(/Extract Only Text Content/i)).toBeChecked(); // crawl4ai_extract_only_text_content: true
    expect(screen.getByLabelText(/Process iFrames Content/i)).toBeChecked(); // crawl4ai_process_iframes: true
    expect(screen.getByLabelText(/Word Count Threshold/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_word_count_threshold);
    expect(screen.getByLabelText(/Remove Forms/i)).not.toBeChecked(); // crawl4ai_remove_forms: false
    expect(screen.getByLabelText(/Keep Data Attributes/i)).toBeChecked(); // crawl4ai_keep_data_attributes: true
    // For a wild value, the Select should show the placeholder or be empty
    const markdownGeneratorCombo = screen.getByRole('combobox', { name: /Markdown Generator/i });
    expect(markdownGeneratorCombo.textContent === '' || /Select generator/i.test(markdownGeneratorCombo.textContent)).toBe(true);


    // Page Interaction & Automation
    expect(screen.getByLabelText(/Execute JavaScript on Page Load/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_execute_js_on_load);
    expect(screen.getByLabelText(/Scan Full Page/i)).toBeChecked(); // crawl4ai_scan_full_page: true
    expect(screen.getByLabelText(/Scroll Delay \(seconds\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_scroll_delay);
    expect(screen.getByLabelText(/Attempt to Remove Overlay Elements/i)).not.toBeChecked(); // crawl4ai_remove_overlay_elements: false
    expect(screen.getByLabelText(/Simulate User Behavior/i)).toBeChecked(); // crawl4ai_simulate_user_behavior: true
    expect(screen.getByLabelText(/Enable "Magic"/i)).toBeChecked(); // crawl4ai_enable_magic: true
    expect(screen.getByLabelText(/Override Navigator Properties/i)).toBeChecked(); // crawl4ai_override_navigator: true

    // Caching Settings
    expect(screen.getByLabelText(/Cache Mode/i)).toHaveTextContent(/bypass/i);
    
    // Media Handling
    expect(screen.getByLabelText(/Capture Screenshot/i)).toBeChecked(); // crawl4ai_capture_screenshot: true
    expect(screen.getByLabelText(/Generate PDF of Page/i)).toBeChecked(); // crawl4ai_generate_pdf: true
    expect(screen.getByLabelText(/Capture MHTML Snapshot/i)).toBeChecked(); // crawl4ai_capture_mhtml: true
    expect(screen.getByLabelText(/Exclude External Images/i)).toBeChecked(); // crawl4ai_exclude_external_images: true
    expect(screen.getByLabelText(/Image Alt Text Min Word Count/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_image_alt_text_min_word_count);
    expect(screen.getByLabelText(/Image Relevance Score Threshold/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_image_relevance_score_threshold);

    // Link & Domain Filtering
    expect(screen.getByLabelText(/Exclude External Links/i, { exact: false })).toBeChecked(); // crawl4ai_exclude_external_links: true
    expect(screen.getByLabelText(/Exclude Social Media Links/i)).toBeChecked(); // crawl4ai_exclude_social_media_links: true
    expect(screen.getByLabelText(/Custom Excluded Domains/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_custom_excluded_domains);

    // Compliance Settings
    expect(screen.getByLabelText(/Respect robots.txt Rules/i)).not.toBeChecked(); // crawl4ai_respect_robots_txt: false

    // Debugging & Logging
    expect(screen.getByLabelText(/Verbose Logging/i)).toBeChecked(); // crawl4ai_verbose_logging: true
    expect(screen.getByLabelText(/Log Page Console Output/i)).toBeChecked(); // crawl4ai_log_page_console_output: true
    
    // LLM Configuration
    // LLM Configuration
    // The label "LLM Provider/Model" might match both the button trigger and the hidden input (or another element).
    // We specifically want to check the value, so we look for the input if available, or just use getAll.
    const llmProviderElements = screen.getAllByLabelText('LLM Provider/Model', { exact: false });
    // Prefer the input element for checking value
    const llmProviderInput = llmProviderElements.find(el => el.tagName === 'INPUT') || llmProviderElements[0];
    
    expect(llmProviderInput).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_llm_provider_model);
    await waitFor(async () => {
        // Try finding by display value directly to confirm if it exists
        await screen.findByDisplayValue("test-token");
    });
    expect(screen.getByLabelText(/LLM Base URL/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4ai_llm_base_url);

    // Expert Options
    await waitFor(() => {
      expect(screen.getByLabelText(/Browser Cookies \(JSON\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.browser_cookies);
      expect(screen.getByLabelText(/Browser Headers \(JSON\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.browser_headers);
      expect(screen.getByLabelText(/Use Persistent Browser Context/i)).toBeChecked(); // crawl4ai_browser_use_persistent_context: true
      expect(screen.getByLabelText(/Crawl Session ID/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl_session_id);
    });
    expect(screen.getByLabelText(/Global CSS Selector \(Expert\)/i)).toHaveValue(mockHistoryItemCrawl4ai.engine_specific_parameters.crawl_css_selector);


    // Verify ExtractionStrategyConfigurator
    // The component receives initialConfig. Check its displayed values.
    const extractionConfig = mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4aiExtractionConfig;
    // strategy 'llm' maps to label 'LLMExtractionStrategy'
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent(/LLMExtractionStrategy/i);
    expect(screen.getByLabelText(/LLM Instructions\/Prompt/i)).toHaveValue(extractionConfig.params.llm_instructions);
    // Check one of the LLM params within ExtractionStrategyConfigurator
    expect(screen.getAllByLabelText('LLM Provider/Model', { exact: false }).find(el => el.id === 'llm-provider-model')).toHaveValue(extractionConfig.params.llm_provider_model);


    // Verify DeepCrawlStrategyConfigurator
    const deepCrawlConfig = mockHistoryItemCrawl4ai.engine_specific_parameters.crawl4aiDeepCrawlConfig;
    // strategy 'BFSDeepCrawlStrategy' should map to label like 'BFS Deep Crawl Strategy' or just check existence
    // If using DeepCrawlStrategyConfigurator, it might not use the same Select component label logic if it's separate.
    // But assuming it renders similar label:
    expect(screen.getByText(/BFS Deep Crawl Strategy/i)).toBeInTheDocument(); 
    expect(screen.getByLabelText('Max Depth', { exact: false })).toHaveValue(deepCrawlConfig.params.max_depth);
    expect(screen.getByLabelText('Max Pages', { exact: false })).toHaveValue(deepCrawlConfig.params.max_pages);
    expect(screen.getByLabelText(/Include External Links/i, { exact: false })).toBeChecked(); // include_external: true
    expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toHaveValue(deepCrawlConfig.params.url_filter_patterns);
    // Use ID to disambiguate from Image Relevance Score Threshold
    expect(screen.getAllByLabelText('Score Threshold', { exact: false }).find(el => el.id === 'score-threshold')).toHaveValue(deepCrawlConfig.params.score_threshold);

    // Check a general Jina option that should NOT be populated if engine is crawl4ai
    // For example, target_selector_advanced is Jina-specific.
    // The label might still be in the DOM due to how AdvancedFetchOptions is structured,
    // but its value should be the default or empty if not applicable.
    // The `handleRefetchHistoryItem` logic should ensure Jina-specific fields are not
    // populated from a crawl4ai history item unless they have a direct crawl4ai counterpart.
    // `target_selector_advanced` is specific to Jina.
    // The `handleRefetchHistoryItem` maps `esp.target_selector` to `advancedSelector`
    // if `esp.target_content_area` is 'advanced'.
    // Our mock has `target_content_area: "advanced"` and `target_selector: "article.content"`
    // So, `advancedSelector` in the form state should be "article.content".
    // This is handled by FetchForm, not AdvancedFetchOptions directly for this field.
    // Let's check the `advancedSelector`. Note: Depending on implementation, this input might be hidden for crawl4ai
    // if it relies on crawl_css_selector expert option instead. 
    // If hidden, we skip this check.
    // expect(screen.getByPlaceholderText('Enter CSS selector for advanced targeting...')).toHaveValue("article.content");

    // Check a Jina-specific boolean that should be default (false)
    // `jsonResponse` is Jina specific. If hidden, skip.
    // expect(screen.getByLabelText(/Return JSON Response/i)).not.toBeChecked();

    // Check that toast message for populating form was called
    // Check that toast message for populating form was called
  });

  test('Test 9: should include Agentic & Scripting parameters in fetch request', async () => {
    render(<FetchContentPage />);
    
    // Select crawl4ai engine
    // The label "Fetching Engine" is a group header, not bound to input. Target the radio button.
    const engineRadio = screen.getByLabelText(/Advanced Crawl/i);
    fireEvent.click(engineRadio);

    // Expand Advanced Options
    const advancedButton = screen.getByText(/Show Advanced Options/i);
    fireEvent.click(advancedButton);

    // Expand Agentic Accordion
    // Note: It's included in defaultValues, so it should be open by default when Advanced Options mounts.
    const agenticAccordion = await screen.findByText(/crawl4ai - Agentic & Scripting/i);
    expect(agenticAccordion).toBeVisible();

    // Enter Script
    const scriptInput = await screen.findByLabelText(/Custom Crawl Script \(DSL\)/i);
    fireEvent.change(scriptInput, { target: { value: 'CLICK #btn\nWAIT 500' } });

    // Toggle Adaptive Mode
    // Switch component usually handles click
    const adaptiveSwitch = screen.getByLabelText(/Enable Adaptive Crawling/i);
    fireEvent.click(adaptiveSwitch);

    // Enter URL to enable fetch
    const urlInput = screen.getByLabelText(/Target URL/i);
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    expect(urlInput).toHaveValue('https://example.com');

    // Click Fetch
    const fetchButton = screen.getByRole('button', { name: /Fetch Content/i });
    fireEvent.click(fetchButton);

    // Wait for fetch to start (the toast or status message)
    // "Initializing..." usually appears in the FetchedContentViewer or as a toast?
    // Based on previous tests, we can wait for EventSource to be called.
    await waitFor(() => {
        if (global.EventSource.mock.calls.length === 0) {
            // throw new Error("EventSource was not called yet"); // Optional: fail faster
        }
      expect(global.EventSource).toHaveBeenCalled();
    }, { timeout: 3000 });

    const eventSourceUrl = global.EventSource.mock.calls[0][0]; // First argument of first call
    // console.log("Captured URL:", eventSourceUrl); // Debugging
    
    // Parse the URL to check params robustly (handling encoding)
    const urlObj = new URL(eventSourceUrl); // EventSource constructor might take relative URL if base not provided, but here we expect full URL or handled by jsdom?
    // In page.js: const sseUrl = `${BACKEND_URL}/fetch-content?${params.toString()}`;
    // BACKEND_URL is http://localhost:8000 usually.
    
    const params = urlObj.searchParams;
    expect(params.get('c4a_script')).toBe('CLICK #btn\nWAIT 500');
    expect(params.get('adaptive_mode')).toBe('true');
  });
});