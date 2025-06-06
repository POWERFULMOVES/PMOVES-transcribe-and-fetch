"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input"; // Added
import { Label } from "@/components/ui/label"; // Added
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"; // Added
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import ReactMarkdown from 'react-markdown';
import { BACKEND_URL } from '@/lib/constants';
import FetchForm from '@/components/fetch/FetchForm';
import AdvancedFetchOptions from '@/components/fetch/AdvancedFetchOptions';
import FetchProgressTracker from '@/components/fetch/FetchProgressTracker';
import FetchHistoryTable from '@/components/fetch/FetchHistoryTable'; // Import history table
import FetchedContentViewer from '@/components/fetch/FetchedContentViewer'; // Import the new viewer
import PresetsManager from '@/components/fetch/PresetsManager'; // Import PresetsManager
import { createClient } from '@/lib/client'; // Import Supabase client creator
import { useInfiniteQuery } from '@/hooks/use-infinite-query'; // Import the hook

const ITEMS_PER_PAGE = 15;

export default function FetchContentPage({ initialActiveMainTab = "fetchContent" } = {}) {
  const [activeTab, setActiveTab] = useState("markdown"); // For content display (Markdown/PDF)
  const [mainFetchLoading, setMainFetchLoading] = useState(false);
  const [mainFetchError, setMainFetchError] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // State for SSE Fetch Progress (main content fetch)
  const [isFetchingSse, setIsFetchingSse] = useState(false); // Renamed to avoid conflict with useInfiniteQuery
  const [progressMessage, setProgressMessage] = useState("");
  const [progressPercent, setProgressPercent] = useState(0);
  const eventSourceRef = useRef(null);

  // State for Fetch History (now managed by useInfiniteQuery)
  // const [fetchHistoryItems, setFetchHistoryItems] = useState([]);
  // const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  // const [historyError, setHistoryError] = useState(null);
  // const [currentHistoryPage, setCurrentHistoryPage] = useState(1);
  // const [hasMoreHistory, setHasMoreHistory] = useState(true);
  // const [totalHistoryItems, setTotalHistoryItems] = useState(0);
  const [activeMainTab, setActiveMainTab] = useState(initialActiveMainTab); // For top-level tabs (Fetch/History)
  const { toast } = useToast();
  const [isSavedToHistory, setIsSavedToHistory] = useState(false);
  const [isSavingToHistory, setIsSavingToHistory] = useState(false);
  const [fetchingEngine, setFetchingEngine] = useState("jina"); // Isolate fetchingEngine state

  const supabase = createClient(); // Instantiate Supabase client

  // State for available LLM Models
  const [availableLlmModels, setAvailableLlmModels] = useState([]);
  const [isLoadingLlmModels, setIsLoadingLlmModels] = useState(false);

 

  // State for history filters and sort
  const [historySearchTerm, setHistorySearchTerm] = useState("");
  const [historyFilterEngine, setHistoryFilterEngine] = useState("all_engines"); // "jina", "crawl4ai", "all_engines" for all
  const [historyFilterStatus, setHistoryFilterStatus] = useState("all_statuses"); // "completed", "error", "all_statuses" for all
  const [historySortColumn, setHistorySortColumn] = useState("fetch_date");
  const [historySortDirection, setHistorySortDirection] = useState("desc"); // "asc" or "desc"

  const handleHistorySearchChange = (event) => {
    setHistorySearchTerm(event.target.value);
  };

  const historyFilters = React.useMemo(() => ({
    searchTerm: historySearchTerm,
    engine: historyFilterEngine,
    status: historyFilterStatus,
  }), [historySearchTerm, historyFilterEngine, historyFilterStatus]);

  const historySort = React.useMemo(() => ({
    column: historySortColumn,
    ascending: historySortDirection === 'asc',
  }), [historySortColumn, historySortDirection]);

  // Initialize useInfiniteQuery for fetch_history
  const {
    data: fetchHistoryItems,
    isLoading: isLoadingHistoryInitial, // isLoading from hook is for initial load
    isFetching: isLoadingHistoryMore, // isFetching from hook is for any fetch (initial or subsequent)
    error: historyError,
    fetchNextPage: loadMoreHistory,
    hasMore: hasMoreHistory,
    count: totalHistoryItems, // count from hook
    initialize: initializeHistory // Destructure initialize
  } = useInfiniteQuery({
    tableName: 'fetch_history',
    columns: '*',
    pageSize: ITEMS_PER_PAGE,
    // trailingQuery is now handled by sortOptions or default in the hook
    // trailingQuery: (query) => query.order('fetch_date', { ascending: false }),
    filters: historyFilters,
    sortOptions: historySort,
  });

  // Consolidated state for all form options
  const [formState, setFormState] = useState({
    // Basic options
    url: "",
    fetchDepth: "page_only", // Default for new select
    targetContentArea: "main_content", // Default for new select
    advancedSelector: "", // For when targetContentArea is "advanced"
    // fetchingEngine removed, now managed by its own state hook

    // Advanced options (migrated and mapped)
    targetSelectorAdvanced: "", // Previously targetSelector
    excludedSelectors: "header,footer,nav,aside,script,style", // Renamed from excludedSelector
    timeout: 60, // Updated default based on AdvancedFetchOptions
    jsonResponse: false,
    cleanFormat: true,
    browserEngine: "chromium", // Updated default based on AdvancedFetchOptions
    tokenBudget: 4000,
    extractTextOnly: false, // New, maps to removeImages conceptually (false = keep images)
    extractTables: true, // New, assuming true by default
    extractImages: true, // New, maps to !removeImages (true = extract images)
    extractLinks: true,
    imageCaptioning: false,
    cacheTtl: 3600,
    markdownFlavor: "gfm", // Updated default based on AdvancedFetchOptions
    viewportWidth: 1920, // Split from browserViewport
    viewportHeight: 1080, // Split from browserViewport
    browserLocale: "en-US",
    extractMetadata: true,
    uploadToSupabase: false,
    result: null,

    // crawl4ai - Browser & Navigation (already added in previous step, shown for context)
    crawl4aiUserAgent: "",
    crawl4aiViewportWidth: 1920,
    crawl4aiViewportHeight: 1080,
    crawl4aiProxyUrl: "",
    crawl4aiPageLoadWaitCondition: "networkidle",
    crawl4aiPageTimeout: 30000,
    crawl4aiWaitForCondition: "",
    crawl4aiEnableJs: true,
    crawl4aiIgnoreHttpsErrors: false,
    crawl4aiLightMode: false,
    crawl4aiTextMode: false,

    // crawl4ai - Content Extraction & Processing (NEW)
    crawl4aiTargetElements: "",
    crawl4aiExcludedElements: "",
    crawl4aiExcludedTags: "script,style,noscript,iframe,nav,footer,aside",
    crawl4aiExtractOnlyTextContent: false,
    crawl4aiProcessIframes: false,
    crawl4aiWordCountThreshold: 50,
    crawl4aiRemoveForms: true,
    crawl4aiKeepDataAttributes: false,

    // crawl4ai - Page Interaction & Automation (NEW)
    crawl4aiExecuteJsOnLoad: "",
    crawl4aiScanFullPage: false,
    crawl4aiScrollDelay: 2, // Default to 2 seconds, conditionally shown in UI
    crawl4aiRemoveOverlayElements: true,
    crawl4aiSimulateUserBehavior: false,
    crawl4aiEnableMagic: false,
    crawl4aiOverrideNavigator: false,

    // crawl4ai - Caching Settings (NEW)
    crawl4aiCacheMode: "enabled", // "enabled", "bypass", "write_only", "read_only", "disabled"

    // crawl4ai - Media Handling Settings (NEW)
    crawl4aiCaptureScreenshot: false,
    crawl4aiGeneratePdf: false,
    crawl4aiCaptureMhtml: false,
    crawl4aiExcludeExternalImages: false,
    crawl4aiImageAltTextMinWordCount: 0,
    crawl4aiImageRelevanceScoreThreshold: 0,

    // crawl4ai - Link & Domain Filtering (NEW)
    crawl4aiExcludeExternalLinks: false,
    crawl4aiExcludeSocialMediaLinks: false,
    crawl4aiCustomExcludedDomains: "",

    // crawl4ai - Compliance Settings (NEW)
    crawl4aiRespectRobotsTxt: true,

    // crawl4ai - Debugging & Logging (NEW - Task)
    crawl4aiVerboseLogging: false,
    crawl4aiLogPageConsoleOutput: false,

    // crawl4ai - LLM Configuration (These specific crawl4ai ones are being removed)
    // crawl4aiLlmProviderModel: "", // REMOVED
    // crawl4aiLlmApiToken: "", // REMOVED
    // crawl4aiLlmBaseUrl: "", // REMOVED
    crawl4aiMarkdownGenerator: "Default", // Added for Markdown generator selection

    // crawl4ai - Expert Options (NEW)
    crawl4aiBrowserCookies: "",
    crawl4aiBrowserHeaders: "",
    crawl4aiBrowserUsePersistentContext: false,
    crawl4aiCrawlSessionId: "",
    crawl4aiCrawlCssSelector: "",

    // crawl4ai - Strategy Configurations
    crawl4aiExtractionConfig: { strategy: 'none', params: {} },
    crawl4aiDeepCrawlConfig: { strategy: 'none', params: {} },
    // LLM Provider related fields for the new LlmConfiguration component
    llmProvider: '', // Canonical LLM provider/model
    llmApiToken: '',
    llmBaseUrl: '',
    selectedPresetIdentifier: null, // Added for preset selection
  });

  // const handleFormChange = (fieldName, value) => { // Replaced by setFormValue
  //   setFormState(prevState => ({
  //     ...prevState,
  //     [fieldName]: value,
  //   }));
  // };

  // Effect to handle the conceptual mapping of extractTextOnly and extractImages
  // removeImages is the old backend parameter.
  // If extractTextOnly is true, then removeImages should be true.
  // If extractTextOnly is false, then extractImages determines removeImages.
  // This effect is a temporary measure until backend API is updated.
  const [removeImagesBackend, setRemoveImagesBackend] = useState(false);

  useEffect(() => {
    if (formState.extractTextOnly) {
      setRemoveImagesBackend(true);
    } else {
      setRemoveImagesBackend(!formState.extractImages);
    }
  }, [formState.extractTextOnly, formState.extractImages]);

  // Effect to fetch available LLM models
  useEffect(() => {
    const fetchLlmModels = async () => {
      // Only fetch if crawl4ai is the engine and advanced options are shown, or if models haven't been loaded yet.
      // This prevents fetching if the user isn't even looking at the crawl4ai LLM options.
      if ((fetchingEngine === 'crawl4ai' && showAdvanced) || availableLlmModels.length === 0) {
        setIsLoadingLlmModels(true);
        try {
          const apiKey = process.env.NEXT_PUBLIC_BACKEND_API_KEY;
          const headers = {
            'Content-Type': 'application/json',
          };
          if (apiKey) {
            headers['Authorization'] = `Bearer ${apiKey}`;
          }

          const response = await fetch(`${BACKEND_URL}/api/v1/models`, { headers });
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Failed to fetch LLM models and parse error" }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
          }
          const models = await response.json();
          console.log('Fetched LLM Models:', models); // <-- ADD THIS LINE
          // Assuming models is an array of StandardizedLLM objects
          // We might want to filter or transform them if needed, e.g., filter by capability for crawl4ai
          setAvailableLlmModels(models || []);
          toast({ title: "LLM Models Loaded", description: `Found ${models.length} models.` });
        } catch (error) {
          console.error("Failed to fetch LLM models:", error);
          toast({
            title: "Error Loading LLM Models",
            description: error.message || "Could not fetch LLM model list from backend.",
            variant: "destructive",
          });
          setAvailableLlmModels([]); // Ensure it's an empty array on error
        } finally {
          setIsLoadingLlmModels(false);
        }
      }
    };

    // Initial fetch or fetch when relevant section is shown
    if (availableLlmModels.length === 0) {
        fetchLlmModels();
    } else if (fetchingEngine === 'crawl4ai' && showAdvanced) {
        // Optionally, re-fetch if advanced options are shown again for crawl4ai,
        // in case the list might have changed. Or rely on initial load.
        // For now, let's assume initial load is sufficient unless specific re-fetch logic is required.
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps 
  }, [fetchingEngine, showAdvanced, toast]); // BACKEND_URL is constant, availableLlmModels.length in condition


  const estimateProgress = (status) => {
    if (!status) return 0;
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes("initializing")) return 10;
    if (lowerStatus.includes("fetching main content")) return 30;
    if (lowerStatus.includes("processing content") || lowerStatus.includes("parsing content")) return 70;
    if (lowerStatus.includes("scraping additional data") || lowerStatus.includes("extracting")) return 85;
    if (lowerStatus.includes("completed") || lowerStatus.includes("finished")) return 100;
    if (lowerStatus.includes("error")) return 0; // Or maintain last known good progress
    return progressPercent; // Keep current if unknown
  };

  const handleFetchContent = async () => {
    if (!formState.url.trim()) {
      setMainFetchError("Please enter a URL to fetch content.");
      return;
    }

    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsFetchingSse(true); // Use renamed state variable
    setMainFetchError(null);
    setProgressMessage("Initializing...");
    setProgressPercent(10);
    setFormState(prev => ({ ...prev, result: null })); // Clear previous results
    setIsSavedToHistory(false); // Reset save status for new fetch
    setIsSavingToHistory(false); // Reset saving status
    let crawlResultReceived = false; // Flag to track if crawl_result event was processed for this fetch

    const params = new URLSearchParams({
      url: formState.url,
      fetch_depth: formState.fetchDepth,
      target_content_area: formState.targetContentArea,
      target_selector: formState.targetContentArea === 'advanced' ? formState.advancedSelector : formState.targetContentArea,
      excluded_selector: formState.excludedSelectors,
      timeout: formState.timeout,
      // json_response, clean_format, browser_engine, token_budget, remove_images, cache_ttl, browser_viewport, browser_locale
      // will be added conditionally for Jina or are handled by crawl4ai specific params.
      extract_links: formState.extractLinks,
      image_captioning: formState.imageCaptioning,
      markdown_flavor: formState.markdownFlavor,
      extract_metadata: formState.extractMetadata,
      upload_to_supabase: formState.uploadToSupabase,
      engine: fetchingEngine, // Use isolated state
    });

    // Add preset_id if selected (for crawl4ai engine)
    if (fetchingEngine === 'crawl4ai' && formState.selectedPresetIdentifier) {
      params.append('preset_id', formState.selectedPresetIdentifier);
    }

    if (fetchingEngine === 'jina') {
      params.append('target_selector_advanced', formState.targetSelectorAdvanced);
      params.append('json_response', formState.jsonResponse.toString());
      params.append('clean_format', formState.cleanFormat.toString());
      params.append('browser_engine', formState.browserEngine);
      params.append('token_budget', formState.tokenBudget.toString());
      params.append('remove_images', removeImagesBackend.toString());
      params.append('cache_ttl', formState.cacheTtl.toString());
      params.append('browser_viewport', `${formState.viewportWidth}x${formState.viewportHeight}`);
      params.append('browser_locale', formState.browserLocale);
      // extract_links, image_captioning, markdown_flavor, extract_metadata are already in base params
    } else if (fetchingEngine === 'crawl4ai') { // Use isolated state
      // Add crawl4ai specific browser/navigation parameters
      if (formState.crawl4aiUserAgent) params.append('crawl4ai_user_agent', formState.crawl4aiUserAgent);
      if (formState.crawl4aiViewportWidth) params.append('crawl4ai_viewport_width', formState.crawl4aiViewportWidth.toString());
      if (formState.crawl4aiViewportHeight) params.append('crawl4ai_viewport_height', formState.crawl4aiViewportHeight.toString());
      if (formState.crawl4aiProxyUrl) params.append('crawl4ai_proxy_url', formState.crawl4aiProxyUrl);
      if (formState.crawl4aiPageLoadWaitCondition) params.append('crawl4ai_page_load_wait_condition', formState.crawl4aiPageLoadWaitCondition);
      if (formState.crawl4aiPageTimeout) params.append('crawl4ai_page_timeout', formState.crawl4aiPageTimeout.toString());
      if (formState.crawl4aiWaitForCondition) params.append('crawl4ai_wait_for_condition', formState.crawl4aiWaitForCondition);
      params.append('crawl4ai_enable_js', formState.crawl4aiEnableJs.toString());
      params.append('crawl4ai_ignore_https_errors', formState.crawl4aiIgnoreHttpsErrors.toString());
      params.append('crawl4ai_light_mode', formState.crawl4aiLightMode.toString());
      params.append('crawl4ai_text_mode', formState.crawl4aiTextMode.toString());

      // Add crawl4ai specific content extraction parameters (NEW)
      if (formState.crawl4aiTargetElements) params.append('crawl4ai_target_elements', formState.crawl4aiTargetElements);
      if (formState.crawl4aiExcludedElements) params.append('crawl4ai_excluded_elements', formState.crawl4aiExcludedElements);
      if (formState.crawl4aiExcludedTags) params.append('crawl4ai_excluded_tags', formState.crawl4aiExcludedTags);
      params.append('crawl4ai_extract_only_text_content', formState.crawl4aiExtractOnlyTextContent.toString());
      params.append('crawl4ai_process_iframes', formState.crawl4aiProcessIframes.toString());
      if (formState.crawl4aiWordCountThreshold !== undefined) params.append('crawl4ai_word_count_threshold', formState.crawl4aiWordCountThreshold.toString());
      params.append('crawl4ai_remove_forms', formState.crawl4aiRemoveForms.toString());
      params.append('crawl4ai_keep_data_attributes', formState.crawl4aiKeepDataAttributes.toString());
  
        // Add crawl4ai specific page interaction parameters
        if (formState.crawl4aiExecuteJsOnLoad) params.append('crawl4ai_execute_js_on_load', formState.crawl4aiExecuteJsOnLoad);
        params.append('crawl4ai_scan_full_page', formState.crawl4aiScanFullPage.toString());
        if (formState.crawl4aiScanFullPage && formState.crawl4aiScrollDelay !== undefined) {
          params.append('crawl4ai_scroll_delay', formState.crawl4aiScrollDelay.toString());
        }
        params.append('crawl4ai_remove_overlay_elements', formState.crawl4aiRemoveOverlayElements.toString());
        params.append('crawl4ai_simulate_user_behavior', formState.crawl4aiSimulateUserBehavior.toString());
        params.append('crawl4ai_enable_magic', formState.crawl4aiEnableMagic.toString());
        params.append('crawl4ai_override_navigator', formState.crawl4aiOverrideNavigator.toString());

        // Add crawl4ai specific caching parameters
        if (formState.crawl4aiCacheMode) params.append('crawl4ai_cache_mode', formState.crawl4aiCacheMode);

        // Add crawl4ai specific media handling parameters
        params.append('crawl4ai_capture_screenshot', formState.crawl4aiCaptureScreenshot.toString());
        params.append('crawl4ai_generate_pdf', formState.crawl4aiGeneratePdf.toString());
        params.append('crawl4ai_capture_mhtml', formState.crawl4aiCaptureMhtml.toString());
        params.append('crawl4ai_exclude_external_images', formState.crawl4aiExcludeExternalImages.toString());
        if (formState.crawl4aiImageAltTextMinWordCount !== undefined) params.append('crawl4ai_image_alt_text_min_word_count', formState.crawl4aiImageAltTextMinWordCount.toString());
        if (formState.crawl4aiImageRelevanceScoreThreshold !== undefined) params.append('crawl4ai_image_relevance_score_threshold', formState.crawl4aiImageRelevanceScoreThreshold.toString());
    
          // Add crawl4ai specific link filtering and compliance parameters
          params.append('crawl4ai_exclude_external_links', formState.crawl4aiExcludeExternalLinks.toString());
          params.append('crawl4ai_exclude_social_media_links', formState.crawl4aiExcludeSocialMediaLinks.toString());
          if (formState.crawl4aiCustomExcludedDomains) params.append('crawl4ai_custom_excluded_domains', formState.crawl4aiCustomExcludedDomains);
          params.append('crawl4ai_respect_robots_txt', formState.crawl4aiRespectRobotsTxt.toString());

          // Add crawl4ai specific debugging and LLM parameters (NEW - Task)
          params.append('crawl4ai_verbose_logging', formState.crawl4aiVerboseLogging.toString());
          params.append('crawl4ai_log_page_console_output', formState.crawl4aiLogPageConsoleOutput.toString());
          // Use the global LLM settings when crawl4ai is the engine
          if (formState.llmProvider) {
            params.append('llm_provider', formState.llmProvider); // For extraction strategy
            params.append('llm_model_alias', formState.llmProvider); // For registry-based config (docker)
          }
          if (formState.llmApiToken) params.append('llm_api_key', formState.llmApiToken);
          if (formState.llmBaseUrl) params.append('crawl4ai_llm_base_url', formState.llmBaseUrl); // Changed 'llm_base_url' to 'crawl4ai_llm_base_url'
          if (formState.crawl4aiMarkdownGenerator && formState.crawl4aiMarkdownGenerator !== "Default") {
            params.append('crawl4ai_markdown_generator', formState.crawl4aiMarkdownGenerator);
          }

          // Add crawl4ai specific expert parameters (NEW)
          if (formState.crawl4aiBrowserCookies) {
            try {
              // Ensure it's a string representation of JSON if it's already an object/array from state
              const cookiesValue = typeof formState.crawl4aiBrowserCookies === 'string' ? formState.crawl4aiBrowserCookies : JSON.stringify(formState.crawl4aiBrowserCookies);
              params.append('browser_cookies', cookiesValue);
            } catch (e) {
              console.error("Error stringifying crawl4aiBrowserCookies:", e);
              // Handle error or append as is if it's already a valid string
              if (typeof formState.crawl4aiBrowserCookies === 'string') {
                params.append('browser_cookies', formState.crawl4aiBrowserCookies);
              }
            }
          }
          if (formState.crawl4aiBrowserHeaders) {
            try {
              // Ensure it's a string representation of JSON if it's already an object/array from state
              const headersValue = typeof formState.crawl4aiBrowserHeaders === 'string' ? formState.crawl4aiBrowserHeaders : JSON.stringify(formState.crawl4aiBrowserHeaders);
              params.append('browser_headers', headersValue);
            } catch (e) {
              console.error("Error stringifying crawl4aiBrowserHeaders:", e);
              // Handle error or append as is if it's already a valid string
              if (typeof formState.crawl4aiBrowserHeaders === 'string') {
                params.append('browser_headers', formState.crawl4aiBrowserHeaders);
              }
            }
          }
          params.append('browser_use_persistent_context', formState.crawl4aiBrowserUsePersistentContext.toString()); // Explicitly toString()
          if (formState.crawl4aiCrawlSessionId) params.append('crawl_session_id', formState.crawl4aiCrawlSessionId);
          if (formState.crawl4aiCrawlCssSelector) params.append('crawl_css_selector', formState.crawl4aiCrawlCssSelector);

          // Add crawl4ai strategy configurations
          if (formState.crawl4aiExtractionConfig && formState.crawl4aiExtractionConfig.strategy !== 'none') {
            params.append('extraction_config', JSON.stringify(formState.crawl4aiExtractionConfig)); // Changed to extraction_config
          }
          if (formState.crawl4aiDeepCrawlConfig && formState.crawl4aiDeepCrawlConfig.strategy !== 'none') {
            // Ensure that the params object within deep_crawl_config does not contain a 'logger' key
            // as the backend strategy expects a Logger object or None, not a config dictionary.
            const configCopy = JSON.parse(JSON.stringify(formState.crawl4aiDeepCrawlConfig));
            if (configCopy.params && typeof configCopy.params.logger !== 'undefined') {
              delete configCopy.params.logger;
            }
            params.append('deep_crawl_config', JSON.stringify(configCopy));
          }
        }

    const sseUrl = `${BACKEND_URL}/fetch-content?${params.toString()}`;
    eventSourceRef.current = new EventSource(sseUrl);

    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Update progress message based on type or status
        if (data.type === "status" && data.status) {
          setProgressMessage(data.message || data.status || "Processing...");
        } else if (data.type !== "crawl_result") { // Avoid overwriting crawl_result's own message if any
          setProgressMessage(data.message || "Processing...");
        }


        let currentProgress = estimateProgress(data.status || data.message);
        if (data.progress && typeof data.progress === 'number') {
            currentProgress = data.progress;
        }
        // Don't reset progress to 0 if it's an error, keep last known good progress or specific error progress.
        if (!(data.type === 'error' || data.status?.toLowerCase().includes('error'))) {
          setProgressPercent(currentProgress);
        }

        if (data.type === 'crawl_result') {
          // Main content arrives in the crawl_result event
          const viewerData = {
            title: data.metadata?.title || data.title || `Content from ${data.url}`,
            htmlContent: data.content, // Raw HTML from crawl_result if available
            markdownContent: data.markdown || data.content, // Prefer Markdown, fallback to HTML/content
            textContent: data.text,
            pdf_file_path: data.pdf_path, // Path if it was a PDF and crawl4ai provided it (distinct from content_storage_path for viewer)
            content_storage_path: data.content_storage_path, // NEW: Path where backend saved MD/JSON/TXT/HTML
            output_type: data.output_type, // NEW: Actual type of content in content_storage_path or for display
            metadata: data.metadata,
            links: data.links,
            screenshot_base64: data.screenshot_base64,
            url: data.url,
          };
          setFormState(prev => ({ ...prev, result: viewerData, fetchedUrl: data.url })); // Store fetchedUrl for history
          crawlResultReceived = true; // Set the flag
          // Optionally, update progress message if crawl_result has specific info
          if (data.message) setProgressMessage(data.message);

        } else if (data.type === 'completed' || data.status?.toLowerCase().includes('completed')) {
          // This event now primarily signals completion.
          // The main data should have already been set by 'crawl_result'.
          // If data.content exists here and is substantial, it might indicate an older backend version
          // or a different flow, but for the current design, we rely on 'crawl_result'.
          if (data.content && Object.keys(data.content).length > 0 && !crawlResultReceived) {
            // Fallback for old backend behavior or if crawl_result was missed
            console.warn("Received 'completed' event with content, but expected data via 'crawl_result' (crawlResultReceived is false). Using this content as a fallback.");
            const backendPayload = data.content;
            const viewerData = {
              title: backendPayload.title,
              markdownContent: backendPayload.content,
              pdf_file_path: backendPayload.pdf_path,
              metadata: backendPayload.metadata,
              links: backendPayload.links,
              url: formState.url, // Use the original requested URL as fallback
            };
            setFormState(prev => ({ ...prev, result: viewerData, fetchedUrl: formState.url }));
            crawlResultReceived = true; // Also set flag here as content was processed
          } else if (!crawlResultReceived) {
            // If completed is received but no result was set by crawl_result
            console.warn("Fetch 'completed' but no content was processed via 'crawl_result' (crawlResultReceived is false).");
            setMainFetchError("Fetch completed, but no viewable content was received.");
          }

          setProgressMessage(data.message || "Fetch completed successfully!");
          setProgressPercent(100);
          setIsFetchingSse(false);
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }
          console.log("Fetch successful, history refresh might be needed via useInfiniteQuery's mechanisms.");

        } else if (data.type === 'error' || data.status?.toLowerCase().includes('error')) {
          setMainFetchError(data.error || data.message || "An unknown error occurred during fetch.");
          setProgressMessage(data.error || data.message || "Error during fetch.");
          setProgressPercent(0); // Indicate error in progress if desired
          setIsFetchingSse(false);
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }
        }
      } catch (e) {
        console.error("Error parsing SSE message or updating state:", e);
        setMainFetchError("Received malformed progress update.");
        // Potentially keep isFetching true or set to false depending on desired behavior
      }
    };

    eventSourceRef.current.onerror = (err) => {
      console.error("EventSource failed:", err);
      setMainFetchError("Connection to server lost or failed to establish for progress updates.");
      setProgressMessage("Connection error.");
      setProgressPercent(0);
      setIsFetchingSse(false); // Use renamed state variable
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  };

  const handleCancelFetch = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsFetchingSse(false); // Use renamed state variable
    setProgressMessage("Fetch cancelled by user.");
    setProgressPercent(0);
    setFormState(prev => ({ ...prev, result: null })); // Clear fetched content
    // setError("Fetch cancelled by user."); // Optional: set error on cancel
  };
  
  // Cleanup EventSource on component unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Helper to update nested state
  const setFormValue = useCallback((key, value) => {
    setFormState(prev => {
      // Prevent update if the new value is identical to the current value
      // For objects, do a shallow comparison or deep if necessary (JSON.stringify is a simple deep compare)
      if (typeof prev[key] === 'object' && prev[key] !== null && typeof value === 'object' && value !== null) {
        if (JSON.stringify(prev[key]) === JSON.stringify(value)) {
          console.log(`[page.js] setFormValue for key '${key}': SKIPPING update, new value is same as old.`);
          return prev;
        }
      } else if (prev[key] === value) {
        console.log(`[page.js] setFormValue for key '${key}': SKIPPING update, new value is same as old.`);
        return prev;
      }
      console.log(`[page.js] setFormValue for key '${key}': UPDATING value.`);
      return { ...prev, [key]: value };
    });
  }, [setFormState]); // setFormState from useState is stable

  const handleCrawl4aiExtractionConfigChange = useCallback((config) => {
    setFormValue('crawl4aiExtractionConfig', config);
  }, [setFormValue]);

  const handleCrawl4aiDeepCrawlConfigChange = useCallback((config) => {
    setFormValue('crawl4aiDeepCrawlConfig', config);
  }, [setFormValue]);

  // Memoized setters for AdvancedFetchOptions
  const setTargetSelectorAdvancedHandler = useCallback((val) => setFormValue('targetSelectorAdvanced', val), [setFormValue]);
  const setExcludedSelectorsHandler = useCallback((val) => setFormValue('excludedSelectors', val), [setFormValue]);
  const setBrowserEngineHandler = useCallback((val) => setFormValue('browserEngine', val), [setFormValue]);
  const setTokenBudgetHandler = useCallback((val) => setFormValue('tokenBudget', val), [setFormValue]);
  const setViewportWidthHandler = useCallback((val) => setFormValue('viewportWidth', val), [setFormValue]);
  const setViewportHeightHandler = useCallback((val) => setFormValue('viewportHeight', val), [setFormValue]);
  const setMarkdownFlavorHandler = useCallback((val) => setFormValue('markdownFlavor', val), [setFormValue]);
  const setTimeoutHandler = useCallback((val) => setFormValue('timeout', val), [setFormValue]);
  const setExtractTextOnlyHandler = useCallback((val) => setFormValue('extractTextOnly', val), [setFormValue]);
  const setExtractTablesHandler = useCallback((val) => setFormValue('extractTables', val), [setFormValue]);
  const setExtractImagesHandler = useCallback((val) => setFormValue('extractImages', val), [setFormValue]);
  const setExtractLinksHandler = useCallback((val) => setFormValue('extractLinks', val), [setFormValue]);
  const setJsonResponseHandler = useCallback((val) => setFormValue('jsonResponse', val), [setFormValue]);
  const setCleanFormatHandler = useCallback((val) => setFormValue('cleanFormat', val), [setFormValue]);
  const setUploadToSupabaseHandler = useCallback((val) => setFormValue('uploadToSupabase', val), [setFormValue]);
  const setImageCaptioningHandler = useCallback((val) => setFormValue('imageCaptioning', val), [setFormValue]);
  const setCacheTtlHandler = useCallback((val) => setFormValue('cacheTtl', val), [setFormValue]);
  const setBrowserLocaleHandler = useCallback((val) => setFormValue('browserLocale', val), [setFormValue]);
  const setExtractMetadataHandler = useCallback((val) => setFormValue('extractMetadata', val), [setFormValue]);
  const setCrawl4aiUserAgentHandler = useCallback((val) => setFormValue('crawl4aiUserAgent', val), [setFormValue]);
  const setCrawl4aiViewportWidthHandler = useCallback((val) => setFormValue('crawl4aiViewportWidth', val), [setFormValue]);
  const setCrawl4aiViewportHeightHandler = useCallback((val) => setFormValue('crawl4aiViewportHeight', val), [setFormValue]);
  const setCrawl4aiProxyUrlHandler = useCallback((val) => setFormValue('crawl4aiProxyUrl', val), [setFormValue]);
  const setCrawl4aiPageLoadWaitConditionHandler = useCallback((val) => setFormValue('crawl4aiPageLoadWaitCondition', val), [setFormValue]);
  const setCrawl4aiPageTimeoutHandler = useCallback((val) => setFormValue('crawl4aiPageTimeout', val), [setFormValue]);
  const setCrawl4aiWaitForConditionHandler = useCallback((val) => setFormValue('crawl4aiWaitForCondition', val), [setFormValue]);
  const setCrawl4aiEnableJsHandler = useCallback((val) => setFormValue('crawl4aiEnableJs', val), [setFormValue]);
  const setCrawl4aiIgnoreHttpsErrorsHandler = useCallback((val) => setFormValue('crawl4aiIgnoreHttpsErrors', val), [setFormValue]);
  const setCrawl4aiLightModeHandler = useCallback((val) => setFormValue('crawl4aiLightMode', val), [setFormValue]);
  const setCrawl4aiTextModeHandler = useCallback((val) => setFormValue('crawl4aiTextMode', val), [setFormValue]);
  const setCrawl4aiTargetElementsHandler = useCallback((val) => setFormValue('crawl4aiTargetElements', val), [setFormValue]);
  const setCrawl4aiExcludedElementsHandler = useCallback((val) => setFormValue('crawl4aiExcludedElements', val), [setFormValue]);
  const setCrawl4aiExcludedTagsHandler = useCallback((val) => setFormValue('crawl4aiExcludedTags', val), [setFormValue]);
  const setCrawl4aiExtractOnlyTextContentHandler = useCallback((val) => setFormValue('crawl4aiExtractOnlyTextContent', val), [setFormValue]);
  const setCrawl4aiProcessIframesHandler = useCallback((val) => setFormValue('crawl4aiProcessIframes', val), [setFormValue]);
  const setCrawl4aiWordCountThresholdHandler = useCallback((val) => setFormValue('crawl4aiWordCountThreshold', val), [setFormValue]);
  const setCrawl4aiRemoveFormsHandler = useCallback((val) => setFormValue('crawl4aiRemoveForms', val), [setFormValue]);
  const setCrawl4aiKeepDataAttributesHandler = useCallback((val) => setFormValue('crawl4aiKeepDataAttributes', val), [setFormValue]);
  const setCrawl4aiExecuteJsOnLoadHandler = useCallback((val) => setFormValue('crawl4aiExecuteJsOnLoad', val), [setFormValue]);
  const setCrawl4aiScanFullPageHandler = useCallback((val) => setFormValue('crawl4aiScanFullPage', val), [setFormValue]);
  const setCrawl4aiScrollDelayHandler = useCallback((val) => setFormValue('crawl4aiScrollDelay', val), [setFormValue]);
  const setCrawl4aiRemoveOverlayElementsHandler = useCallback((val) => setFormValue('crawl4aiRemoveOverlayElements', val), [setFormValue]);
  const setCrawl4aiSimulateUserBehaviorHandler = useCallback((val) => setFormValue('crawl4aiSimulateUserBehavior', val), [setFormValue]);
  const setCrawl4aiEnableMagicHandler = useCallback((val) => setFormValue('crawl4aiEnableMagic', val), [setFormValue]);
  const setCrawl4aiOverrideNavigatorHandler = useCallback((val) => setFormValue('crawl4aiOverrideNavigator', val), [setFormValue]);
  const setCrawl4aiCacheModeHandler = useCallback((val) => setFormValue('crawl4aiCacheMode', val), [setFormValue]);
  const setCrawl4aiCaptureScreenshotHandler = useCallback((val) => setFormValue('crawl4aiCaptureScreenshot', val), [setFormValue]);
  const setCrawl4aiGeneratePdfHandler = useCallback((val) => setFormValue('crawl4aiGeneratePdf', val), [setFormValue]);
  const setCrawl4aiCaptureMhtmlHandler = useCallback((val) => setFormValue('crawl4aiCaptureMhtml', val), [setFormValue]);
  const setCrawl4aiExcludeExternalImagesHandler = useCallback((val) => setFormValue('crawl4aiExcludeExternalImages', val), [setFormValue]);
  const setCrawl4aiImageAltTextMinWordCountHandler = useCallback((val) => setFormValue('crawl4aiImageAltTextMinWordCount', val), [setFormValue]);
  const setCrawl4aiImageRelevanceScoreThresholdHandler = useCallback((val) => setFormValue('crawl4aiImageRelevanceScoreThreshold', val), [setFormValue]);
  const setCrawl4aiExcludeExternalLinksHandler = useCallback((val) => setFormValue('crawl4aiExcludeExternalLinks', val), [setFormValue]);
  const setCrawl4aiExcludeSocialMediaLinksHandler = useCallback((val) => setFormValue('crawl4aiExcludeSocialMediaLinks', val), [setFormValue]);
  const setCrawl4aiCustomExcludedDomainsHandler = useCallback((val) => setFormValue('crawl4aiCustomExcludedDomains', val), [setFormValue]);
  const setCrawl4aiRespectRobotsTxtHandler = useCallback((val) => setFormValue('crawl4aiRespectRobotsTxt', val), [setFormValue]);
  const setCrawl4aiVerboseLoggingHandler = useCallback((val) => setFormValue('crawl4aiVerboseLogging', val), [setFormValue]);
  const setCrawl4aiLogPageConsoleOutputHandler = useCallback((val) => setFormValue('crawl4aiLogPageConsoleOutput', val), [setFormValue]);
  const setCrawl4aiLlmProviderModelHandler = useCallback((val) => setFormValue('crawl4aiLlmProviderModel', val), [setFormValue]);
  const setCrawl4aiLlmApiTokenHandler = useCallback((val) => setFormValue('crawl4aiLlmApiToken', val), [setFormValue]);
  const setCrawl4aiLlmBaseUrlHandler = useCallback((val) => setFormValue('crawl4aiLlmBaseUrl', val), [setFormValue]);
  const setCrawl4aiMarkdownGeneratorHandler = useCallback((val) => setFormValue('crawl4aiMarkdownGenerator', val), [setFormValue]);
  const setCrawl4aiBrowserCookiesHandler = useCallback((val) => setFormValue('crawl4aiBrowserCookies', val), [setFormValue]);
  const setCrawl4aiBrowserHeadersHandler = useCallback((val) => setFormValue('crawl4aiBrowserHeaders', val), [setFormValue]);
  const setCrawl4aiBrowserUsePersistentContextHandler = useCallback((val) => setFormValue('crawl4aiBrowserUsePersistentContext', val), [setFormValue]);
  const setCrawl4aiCrawlSessionIdHandler = useCallback((val) => setFormValue('crawl4aiCrawlSessionId', val), [setFormValue]);
  const setCrawl4aiCrawlCssSelectorHandler = useCallback((val) => setFormValue('crawl4aiCrawlCssSelector', val), [setFormValue]);

  // Fetch History Data using Supabase client - REMOVED as useInfiniteQuery handles this
  // const fetchHistoryData = useCallback(async (pageToFetch, replace = false) => {
  //   if (!supabase) {
  //     setHistoryError("Supabase client not initialized.");
  //     return;
  //   }
  //   setIsLoadingHistory(true);
  //   setHistoryError(null);

  //   const itemsFrom = (pageToFetch - 1) * ITEMS_PER_PAGE;
  //   const itemsTo = itemsFrom + ITEMS_PER_PAGE - 1;

  //   try {
  //     const { data, error, count } = await supabase
  //       .from('fetch_history')
  //       .select('*', { count: 'exact' })
  //       .order('fetched_at', { ascending: false })
  //       .range(itemsFrom, itemsTo);

  //     if (error) {
  //       throw error;
  //     }

  //     setFetchHistoryItems(prevItems => replace ? data : [...prevItems, ...data]);
  //     setTotalHistoryItems(count || 0);
  //     setHasMoreHistory((replace ? data.length : fetchHistoryItems.length + data.length) < (count || 0));
  //     setCurrentHistoryPage(pageToFetch);

  //   } catch (err) {
  //     console.error("Error fetching history from Supabase:", err);
  //     setHistoryError(err.message || "An unexpected error occurred.");
  //     setHasMoreHistory(false);
  //   } finally {
  //     setIsLoadingHistory(false);
  //   }
  // }, [supabase, fetchHistoryItems.length]);

  // useEffect for initial history load - REMOVED as useInfiniteQuery handles its own initialization
  // useEffect(() => {
  //   if (activeMainTab === "fetchHistory") {
  //       // The useInfiniteQuery hook should handle its initial fetch.
  //       // If manual re-triggering is needed on tab switch, that logic would go here.
  //       // For now, relying on the hook's mount effect.
  //       // if (typeof initializeHistory === 'function' && (!fetchHistoryItems || fetchHistoryItems.length === 0)) {
  //       //   initializeHistory();
  //       // }
  //   }
  // }, [activeMainTab, initializeHistory, fetchHistoryItems]);


  // loadMoreHistory is now directly from useInfiniteQuery

  const handleSaveToHistory = async () => {
    if (!formState.result) {
      toast({
        title: "Error",
        description: "No content to save.",
        variant: "destructive",
      });
      return;
    }
    if (isSavedToHistory) {
       toast({
        title: "Already Saved",
        description: "This content has already been saved to history.",
        variant: "default",
      });
      return;
    }

    setIsSavingToHistory(true);

    const engineSpecificParams = {
      fetch_depth: formState.fetchDepth,
      target_content_area: formState.targetContentArea,
      target_selector: formState.targetContentArea === 'advanced' ? formState.advancedSelector : formState.targetContentArea,
      excluded_selector: formState.excludedSelectors,
      timeout: formState.timeout,
      // Jina specific params will be added conditionally
      extract_links: formState.extractLinks,
      image_captioning: formState.imageCaptioning,
      markdown_flavor: formState.markdownFlavor,
      extract_metadata: formState.extractMetadata,
      upload_to_supabase: formState.uploadToSupabase,
    };

    if (fetchingEngine === 'jina') { // Use isolated state
      engineSpecificParams.target_selector_advanced = formState.targetSelectorAdvanced;
      engineSpecificParams.json_response = formState.jsonResponse;
      engineSpecificParams.clean_format = formState.cleanFormat;
      engineSpecificParams.browser_engine = formState.browserEngine;
      engineSpecificParams.token_budget = formState.tokenBudget;
      engineSpecificParams.remove_images = removeImagesBackend; // This comes from a derived state
      engineSpecificParams.cache_ttl = formState.cacheTtl;
      engineSpecificParams.browser_viewport = `${formState.viewportWidth}x${formState.viewportHeight}`;
      engineSpecificParams.browser_locale = formState.browserLocale;
    } else if (fetchingEngine === 'crawl4ai') { // Use isolated state
      engineSpecificParams.crawl4ai_user_agent = formState.crawl4aiUserAgent;
      engineSpecificParams.crawl4ai_viewport_width = formState.crawl4aiViewportWidth;
      engineSpecificParams.crawl4ai_viewport_height = formState.crawl4aiViewportHeight;
      engineSpecificParams.crawl4ai_proxy_url = formState.crawl4aiProxyUrl;
      engineSpecificParams.crawl4ai_page_load_wait_condition = formState.crawl4aiPageLoadWaitCondition;
      engineSpecificParams.crawl4ai_page_timeout = formState.crawl4aiPageTimeout;
      engineSpecificParams.crawl4ai_wait_for_condition = formState.crawl4aiWaitForCondition;
      engineSpecificParams.crawl4ai_enable_js = formState.crawl4aiEnableJs;
      engineSpecificParams.crawl4ai_ignore_https_errors = formState.crawl4aiIgnoreHttpsErrors;
      engineSpecificParams.crawl4ai_light_mode = formState.crawl4aiLightMode;
      engineSpecificParams.crawl4ai_text_mode = formState.crawl4aiTextMode;
      // NEW crawl4ai content extraction params
      engineSpecificParams.crawl4ai_target_elements = formState.crawl4aiTargetElements;
      engineSpecificParams.crawl4ai_excluded_elements = formState.crawl4aiExcludedElements;
      engineSpecificParams.crawl4ai_excluded_tags = formState.crawl4aiExcludedTags;
      engineSpecificParams.crawl4ai_extract_only_text_content = formState.crawl4aiExtractOnlyTextContent;
      engineSpecificParams.crawl4ai_process_iframes = formState.crawl4aiProcessIframes;
      engineSpecificParams.crawl4ai_word_count_threshold = formState.crawl4aiWordCountThreshold;
      engineSpecificParams.crawl4ai_remove_forms = formState.crawl4aiRemoveForms;
      engineSpecificParams.crawl4ai_keep_data_attributes = formState.crawl4aiKeepDataAttributes;
      // NEW crawl4ai page interaction params
      engineSpecificParams.crawl4ai_execute_js_on_load = formState.crawl4aiExecuteJsOnLoad;
      engineSpecificParams.crawl4ai_scan_full_page = formState.crawl4aiScanFullPage;
      engineSpecificParams.crawl4ai_scroll_delay = formState.crawl4aiScrollDelay;
      engineSpecificParams.crawl4ai_remove_overlay_elements = formState.crawl4aiRemoveOverlayElements;
      engineSpecificParams.crawl4ai_simulate_user_behavior = formState.crawl4aiSimulateUserBehavior;
      engineSpecificParams.crawl4ai_enable_magic = formState.crawl4aiEnableMagic;
      engineSpecificParams.crawl4ai_override_navigator = formState.crawl4aiOverrideNavigator;

      // NEW crawl4ai caching params
      engineSpecificParams.crawl4ai_cache_mode = formState.crawl4aiCacheMode;

      // NEW crawl4ai media handling params
      engineSpecificParams.crawl4ai_capture_screenshot = formState.crawl4aiCaptureScreenshot;
      engineSpecificParams.crawl4ai_generate_pdf = formState.crawl4aiGeneratePdf;
      engineSpecificParams.crawl4ai_capture_mhtml = formState.crawl4aiCaptureMhtml;
      engineSpecificParams.crawl4ai_exclude_external_images = formState.crawl4aiExcludeExternalImages;
      engineSpecificParams.crawl4ai_image_alt_text_min_word_count = formState.crawl4aiImageAltTextMinWordCount;
      engineSpecificParams.crawl4ai_image_relevance_score_threshold = formState.crawl4aiImageRelevanceScoreThreshold;

      // NEW crawl4ai link filtering and compliance params
      engineSpecificParams.crawl4ai_exclude_external_links = formState.crawl4aiExcludeExternalLinks;
      engineSpecificParams.crawl4ai_exclude_social_media_links = formState.crawl4aiExcludeSocialMediaLinks;
      engineSpecificParams.crawl4ai_custom_excluded_domains = formState.crawl4aiCustomExcludedDomains;
      engineSpecificParams.crawl4ai_respect_robots_txt = formState.crawl4aiRespectRobotsTxt;

      // NEW crawl4ai debugging and LLM params for history (Task)
      engineSpecificParams.crawl4ai_verbose_logging = formState.crawl4aiVerboseLogging;
      engineSpecificParams.crawl4ai_log_page_console_output = formState.crawl4aiLogPageConsoleOutput;
      // Use global LLM settings for history as well
      engineSpecificParams.crawl4ai_llm_provider_model = formState.llmProvider;
      engineSpecificParams.llm_api_key = formState.llmApiToken; // ensure 'llm_api_key' is used here too
      engineSpecificParams.crawl4ai_llm_base_url = formState.llmBaseUrl;
      engineSpecificParams.crawl4ai_markdown_generator = formState.crawl4aiMarkdownGenerator; // Added for history

      // NEW crawl4ai expert params for history
      engineSpecificParams.browser_cookies = formState.crawl4aiBrowserCookies;
      engineSpecificParams.browser_headers = formState.crawl4aiBrowserHeaders;
      engineSpecificParams.browser_use_persistent_context = formState.crawl4aiBrowserUsePersistentContext;
      engineSpecificParams.crawl_session_id = formState.crawl4aiCrawlSessionId;
      engineSpecificParams.crawl_css_selector = formState.crawl4aiCrawlCssSelector;

      // Add crawl4ai strategy configurations for history
      engineSpecificParams.crawl4aiExtractionConfig = formState.crawl4aiExtractionConfig;
      engineSpecificParams.crawl4aiDeepCrawlConfig = formState.crawl4aiDeepCrawlConfig;
      engineSpecificParams.llm_provider = formState.llmProvider;
      engineSpecificParams.llm_model_alias = formState.llmProvider;
      engineSpecificParams.llm_api_key = formState.llmApiToken;
      engineSpecificParams.llm_base_url = formState.llmBaseUrl;
    }

    // Conditionally add extract_tables if it's a property in formState (i.e., was likely sent)
    if (formState.hasOwnProperty('extractTables')) {
      engineSpecificParams.extract_tables = formState.extractTables;
    }

    const payload = {
      url: formState.fetchedUrl || formState.url, // Ensure we use the actually fetched URL
      fetching_engine: fetchingEngine,
      status: 'completed', // Assuming save happens on successful fetch
      title: formState.result.title || "Untitled",
      engine_specific_parameters: engineSpecificParams,
      output_type: formState.result.output_type || (formState.result.pdf_file_path ? 'pdf_link' : 'markdown'), // Use the new output_type, fallback if needed
      raw_content_summary: typeof formState.result.markdownContent === 'string'
        ? (formState.result.markdownContent.substring(0, 250) + ((formState.result.markdownContent.length || 0) > 250 ? '...' : ''))
        : 'Summary not available.',
      content_storage_path: formState.result.content_storage_path || null, // THIS IS THE KEY CHANGE
      user_id: null, // This would need to come from auth state
    };

    try {
      const response = await fetch(`${BACKEND_URL}/api/fetch-history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Failed to save and parse error response." }));
        throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
      }

      toast({
        title: "Success!",
        description: "Content saved to history.",
        variant: "default",
      });
      setIsSavedToHistory(true);
      // TODO: Implement refresh logic for useInfiniteQuery if needed.
      // This is out of scope for the current task.
      // if (activeMainTab === "fetchHistory" && typeof initializeHistory === 'function') {
      //   initializeHistory(); // Example if hook had re-init
      // }
      console.log("Content saved, history refresh might be needed via useInfiniteQuery's mechanisms.");

    } catch (error) {
      console.error("Error saving to history:", error);
      toast({
        title: "Error Saving to History",
        description: error.message || "Could not save content to history. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSavingToHistory(false);
    }
  };

  // Placeholder handlers for FetchHistoryTable actions
  const handleViewHistoryItem = async (item) => {
    if (!item || !item.id) {
      toast({
        title: "Error",
        description: "History item ID is missing. Cannot fetch content.",
        variant: "destructive",
      });
      return;
    }

    console.log("View history item:", item);
    setActiveMainTab("fetchContent"); // Switch to the main fetch tab
    // Clear previous result and specific error for this section
    setFormState(prev => ({ ...prev, result: null }));
    setMainFetchError(null);
    toast({
      title: "Loading Content...",
      description: `Fetching content for ${item.title || item.url || item.id}.`,
    });
    window.scrollTo(0, 0); // Scroll to top

    try {
      const response = await fetch(`${BACKEND_URL}/api/fetch-history/${item.id}/content`);
      let fetchedContentData;

      if (!response.ok) {
        let errorDetail = `Failed to fetch content. Status: ${response.status}`;
        try {
          // Try to parse error response as JSON, but handle if it's not
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch (e) {
          // If response is not JSON, use the raw text if available
          try {
            const rawErrorText = await response.text();
            console.error("Non-JSON error response from server:", rawErrorText);
            errorDetail = rawErrorText || errorDetail;
          } catch (textError) {
            console.error("Failed to get raw text from error response:", textError);
          }
        }
        throw new Error(errorDetail);
      }

      try {
        fetchedContentData = await response.json();
      } catch (jsonParseError) {
        const rawResponseText = await response.text().catch(() => "Could not retrieve raw response text.");
        console.error("Failed to parse JSON response. Raw response text:", rawResponseText);
        throw new Error(`Received non-JSON response from server. Raw text: ${rawResponseText.substring(0, 100)}...`);
      }

      console.debug("Fetched content data structure:", {
        keys: Object.keys(fetchedContentData),
        contentType: fetchedContentData.content_type,
        hasMarkdown: fetchedContentData.hasOwnProperty('markdown_content'),
        hasRawContent: fetchedContentData.hasOwnProperty('raw_content'),
        hasPdfPath: fetchedContentData.hasOwnProperty('pdf_file_path') || fetchedContentData.hasOwnProperty('pdf_path'),
        title: fetchedContentData.title,
        message: fetchedContentData.message
      });

      // The backend now returns a structure like:
      // { title, url, history_id, content_type, content_storage_path, pdf_path, markdown_content, raw_content }
      // We need to map this to what FetchedContentViewer expects: { title, markdownContent, pdfUrl, pdf_file_path, metadata, links }
      
      const viewerData = {
        title: fetchedContentData.title || item.title || "Untitled",
        markdownContent: fetchedContentData.markdown_content || null,
        // pdf_file_path is what FetchedContentViewer uses to construct a download link if pdfUrl is not present
        pdf_file_path: fetchedContentData.output_type === 'pdf' || fetchedContentData.output_type === 'pdf_link' ? fetchedContentData.content_storage_path : null,
        output_type: fetchedContentData.output_type, // Pass through the output_type
        // If the backend directly provides a raw_content for JSON/HTML, we can decide how to display it.
        // For now, FetchedContentViewer primarily handles markdown and PDF links.
        // We can add raw_content to the viewerData if we want to display it, or handle it here.
        // For simplicity, if it's JSON, let's put it into markdownContent as a formatted block.
        // Potentially add metadata and links here if/when backend provides them for history items
        // metadata: fetchedContentData.metadata, (if available)
        // links: fetchedContentData.links, (if available)
      };

      if (fetchedContentData.output_type === 'json' && fetchedContentData.raw_content) {
        try {
            const jsonData = typeof fetchedContentData.raw_content === 'string' ? JSON.parse(fetchedContentData.raw_content) : fetchedContentData.raw_content;
            viewerData.markdownContent = (viewerData.markdownContent || "") +
                `\n\n## JSON Content\n\n\`\`\`json\n${JSON.stringify(jsonData, null, 2)}\n\`\`\``;
        } catch (e) {
            console.error("Error parsing JSON content from history:", e);
            viewerData.markdownContent = (viewerData.markdownContent || "") +
                `\n\n## JSON Content (raw)\n\n\`\`\`\n${fetchedContentData.raw_content}\n\`\`\``;
        }
      } else if (fetchedContentData.raw_content && !viewerData.markdownContent) {
        // For other raw content types like HTML/XML, display as is in a code block if no markdown
         viewerData.markdownContent = `## Raw Content (${fetchedContentData.output_type})\n\n\`\`\`${fetchedContentData.output_type}\n${fetchedContentData.raw_content}\n\`\`\``;
      }


      if (!viewerData.markdownContent && !viewerData.pdf_file_path) {
         // If after processing, there's still no viewable content, show a message.
         // The backend might return a message in fetchedContentData.message if content was not found on disk.
         const message = fetchedContentData.message || "No viewable content found for this item.";
         viewerData.markdownContent = `## ${fetchedContentData.title || item.title}\n\n${message}`;
      }


      setFormState(prev => ({ ...prev, result: viewerData }));
      toast({
        title: "Content Loaded",
        description: `Displaying content for ${item.title || item.url}.`,
      });

    } catch (error) {
      console.error("Error fetching history item content:", error);
      // Ensure error.message is safely accessed and used for user feedback
      const errorMessage = error.message || "An unexpected error occurred while loading content.";
      setMainFetchError(`Could not load content for "${item.title || item.url || item.id}". Error: ${errorMessage}`);
      // Update formState to reflect the error in the content area if desired, or rely on mainFetchError
      setFormState(prev => ({ ...prev, result: { markdownContent: `## Error Loading Content\n\n${errorMessage}` } }));
      toast({
        title: "Error Loading Content",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleDeleteHistoryItem = async (itemId) => {
    if (!itemId) {
      toast({
        title: "Error",
        description: "History item ID is missing.",
        variant: "destructive",
      });
      return;
    }

    const confirmed = window.confirm("Are you sure you want to delete this history item and its associated content? This action cannot be undone.");
    if (!confirmed) {
      return;
    }

    console.log("Attempting to delete history item ID:", itemId);
    try {
      const response = await fetch(`${BACKEND_URL}/api/fetch-history/${itemId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to delete item and parse error response." }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      toast({
        title: "Success!",
        description: "History item deleted successfully.",
        variant: "default",
      });

      // Refresh the history list using the initialize function from useInfiniteQuery
      if (typeof initializeHistory === 'function') {
        initializeHistory();
      } else {
        console.warn("initializeHistory function not available from useInfiniteQuery hook. History list may not refresh automatically.");
        // Fallback or alternative refresh mechanism might be needed if initialize is not exposed/working as expected.
      }

    } catch (error) {
      console.error("Error deleting history item:", error);
      toast({
        title: "Error Deleting Item",
        description: error.message || "Could not delete history item. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleRefetchHistoryItem = (item) => {
    if (!item) {
      toast({
        title: "Error",
        description: "History item data is missing.",
        variant: "destructive",
      });
      return;
    }

    setFormState(prevFormState => {
      // Start with a fresh copy of the current state, which holds all defaults
      // for fields not present in the history item's parameters.
      const newPopulatedState = { ...prevFormState };

      // Populate basic info
      newPopulatedState.url = item.url || "";
      // Set isolated fetchingEngine state directly
      setFetchingEngine(item.fetching_engine || 'jina');

      const esp = item.engine_specific_parameters || {};

      // Apply parameters from esp, mapping keys and values as needed
      for (const espKey in esp) {
        if (Object.prototype.hasOwnProperty.call(esp, espKey)) {
          const value = esp[espKey];
          let formKey = espKey; // By default, assume espKey matches formState key

          // 1. Handle key name mappings
          if (espKey === 'crawl4ai_llm_base_url') {
            newPopulatedState.llmBaseUrl = value; // Directly assign to the correct formState field
            continue; // Value handled, skip general assignment for this key
          } else if (espKey.startsWith('crawl4ai_')) {
            formKey = espKey.replace(/_([a-z])/g, (_match, letter) => letter.toUpperCase());
          } else if (espKey === 'excluded_selector') {
            formKey = 'excludedSelectors';
          } else if (espKey === 'crawl4aiExtractionConfig') {
            newPopulatedState.crawl4aiExtractionConfig = value || { strategy: 'none', params: {} };
            continue;
          } else if (espKey === 'crawl4aiDeepCrawlConfig') {
            newPopulatedState.crawl4aiDeepCrawlConfig = value || { strategy: 'none', params: {} };
            continue;
          }
          // target_selector_advanced from esp maps directly to formState.targetSelectorAdvanced

          // 2. Handle special value transformations or multi-field updates
          if (espKey === 'browser_viewport') {
            const [widthStr, heightStr] = (value || "1920x1080").split('x');
            newPopulatedState.viewportWidth = parseInt(widthStr, 10) || 1920;
            newPopulatedState.viewportHeight = parseInt(heightStr, 10) || 1080;
            continue; // Value handled, skip general assignment for this key
          } else if (espKey === 'remove_images') {
            // This backend param derives two UI fields
            if (value === true) { // remove_images: true
              newPopulatedState.extractTextOnly = true;
              newPopulatedState.extractImages = false;
            } else { // remove_images: false
              newPopulatedState.extractTextOnly = false;
              newPopulatedState.extractImages = true;
            }
            continue; // Values handled
          } else if (espKey === 'target_content_area') {
            // This will set the targetContentArea. advancedSelector is handled after the loop.
            newPopulatedState.targetContentArea = value || 'main_content';
            continue;
          } else if (espKey === 'target_selector') {
            // This value from esp is used for advancedSelector if target_content_area (from esp) is 'advanced'.
            // Handled after the loop.
            continue;
          }

          // 3. General assignment for mapped keys
          // Check if the (potentially mapped) formKey exists in our form state structure
          if (Object.prototype.hasOwnProperty.call(newPopulatedState, formKey)) {
            newPopulatedState[formKey] = value;
          }
        }
      }

      // Post-loop: Determine advancedSelector based on targetContentArea from ESP
      // Use target_content_area from esp if available, otherwise keep current form state's value or default.
      const effectiveTargetContentArea = esp.target_content_area || newPopulatedState.targetContentArea || 'main_content';
      newPopulatedState.targetContentArea = effectiveTargetContentArea; // Ensure it's correctly set in the state
      
      if (effectiveTargetContentArea === 'advanced') {
        newPopulatedState.advancedSelector = esp.target_selector || "";
      } else {
        newPopulatedState.advancedSelector = ""; // Reset if not in advanced mode
      }
      
      newPopulatedState.result = null; // Clear any previous fetch results
      return newPopulatedState;
    });

    setActiveMainTab("fetchContent");
    setShowAdvanced(true); // Assume re-fetch might use advanced options
    window.scrollTo(0, 0); // Scroll to top to see the populated form
    toast({
      title: "Form Populated",
      description: "Form populated with settings from selected history item.",
      variant: "default",
    });
  };
  
  // Callback to refresh the history list
  const handleRefreshHistory = useCallback(async () => {
    // OLD: if (historyQuery && typeof historyQuery.initialize === 'function') {
    if (typeof initializeHistory === 'function') { // Check if initializeHistory is a function
      try {
        // OLD: await historyQuery.initialize();
        await initializeHistory(); // Call the destructured function
        toast({
          title: "History Refreshed",
          description: "The fetch history has been reloaded from the server.",
        });
      } catch (error) {
        console.error("Error refreshing history:", error);
        toast({
          title: "Refresh Failed",
          description: `Could not refresh history: ${error.message}`,
          variant: "destructive",
        });
      }
    } else {
      console.warn("Attempted to refresh history, but initializeHistory function is not available.");
      toast({
        title: "Refresh Unavailable",
        description: "The history refresh function is not ready.",
        variant: "destructive",
      });
    }
  }, [initializeHistory, toast]); // Update dependency array to initializeHistory

  // Effect to load initial history data only once on mount
  useEffect(() => {
    handleRefreshHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return (
    <>
      <main className="container mx-auto mt-8 p-4"> {/* Removed max-w-4xl for wider history table */}
        <Tabs value={activeMainTab} onValueChange={setActiveMainTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3"> {/* Updated grid-cols-2 to grid-cols-3 */}
            <TabsTrigger value="fetchContent">Fetch New Content</TabsTrigger>
            <TabsTrigger value="fetchHistory">Fetch History</TabsTrigger>
            <TabsTrigger value="managePresets">Manage Presets</TabsTrigger> {/* Added PresetsManager Tab */}
          </TabsList>
          
          <TabsContent value="fetchContent">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Fetch Web Content</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <FetchForm
                  url={formState.url}
              setUrl={(val) => setFormValue('url', val)}
              selectedPresetId={formState.selectedPresetIdentifier} // Pass down selected preset
              onPresetChange={(presetId) => setFormValue('selectedPresetIdentifier', presetId)} // Handle preset change
              fetchDepth={formState.fetchDepth}
              setFetchDepth={(val) => setFormValue('fetchDepth', val)}
              targetContentArea={formState.targetContentArea}
              setTargetContentArea={(val) => setFormValue('targetContentArea', val)}
              advancedSelector={formState.advancedSelector}
              setAdvancedSelector={(val) => setFormValue('advancedSelector', val)}
              fetchingEngine={fetchingEngine}
              setFetchingEngine={setFetchingEngine}
              handleFetch={handleFetchContent}
              showAdvanced={showAdvanced}
              setShowAdvanced={setShowAdvanced}
            />

            {isFetchingSse && ( // Use renamed state variable
              <FetchProgressTracker
                progressPercent={progressPercent}
                progressMessage={progressMessage}
                onCancel={handleCancelFetch}
              />
            )}

            {showAdvanced && (
              <AdvancedFetchOptions
                fetchingEngine={fetchingEngine} // Pass isolated state
                targetSelectorAdvanced={formState.jinaTargetSelectorAdvanced}
                setTargetSelectorAdvanced={(value) => handleFormChange('jinaTargetSelectorAdvanced', value)}
                excludedSelectors={formState.jinaExcludedSelectors}
                setExcludedSelectors={(value) => handleFormChange('jinaExcludedSelectors', value)}
                browserEngine={formState.jinaBrowserEngine}
                setBrowserEngine={(value) => handleFormChange('jinaBrowserEngine', value)}
                tokenBudget={formState.jinaTokenBudget}
                setTokenBudget={(value) => handleFormChange('jinaTokenBudget', value)}
                viewportWidth={formState.jinaViewportWidth}
                setViewportWidth={(value) => handleFormChange('jinaViewportWidth', value)}
                viewportHeight={formState.jinaViewportHeight}
                setViewportHeight={(value) => handleFormChange('jinaViewportHeight', value)}
                markdownFlavor={formState.jinaMarkdownFlavor}
                setMarkdownFlavor={(value) => handleFormChange('jinaMarkdownFlavor', value)}
                timeout={formState.jinaTimeout}
                setTimeout={(value) => handleFormChange('jinaTimeout', value)}
                extractTextOnly={formState.jinaExtractTextOnly}
                setExtractTextOnly={(value) => handleFormChange('jinaExtractTextOnly', value)}
                extractTables={formState.jinaExtractTables}
                setExtractTables={(value) => handleFormChange('jinaExtractTables', value)}
                extractImages={formState.jinaExtractImages}
                setExtractImages={(value) => handleFormChange('jinaExtractImages', value)}
                extractLinks={formState.jinaExtractLinks}
                setExtractLinks={(value) => handleFormChange('jinaExtractLinks', value)}
                jsonResponse={formState.jinaJsonResponse}
                setJsonResponse={(value) => handleFormChange('jinaJsonResponse', value)}
                cleanFormat={formState.jinaCleanFormat}
                setCleanFormat={(value) => handleFormChange('jinaCleanFormat', value)}
                imageCaptioning={formState.jinaImageCaptioning}
                setImageCaptioning={(value) => handleFormChange('jinaImageCaptioning', value)}
                cacheTtl={formState.jinaCacheTtl}
                setCacheTtl={(value) => handleFormChange('jinaCacheTtl', value)}
                browserLocale={formState.jinaBrowserLocale}
                setBrowserLocale={(value) => handleFormChange('jinaBrowserLocale', value)}
                extractMetadata={formState.jinaExtractMetadata}
                setExtractMetadata={(value) => handleFormChange('jinaExtractMetadata', value)}
                
                // Crawl4ai specific props
                crawl4aiUserAgent={formState.crawl4aiUserAgent}
                setCrawl4aiUserAgent={(value) => handleFormChange('crawl4aiUserAgent', value)}
                crawl4aiViewportWidth={formState.crawl4aiViewportWidth}
                setCrawl4aiViewportWidth={(value) => handleFormChange('crawl4aiViewportWidth', value)}
                crawl4aiViewportHeight={formState.crawl4aiViewportHeight}
                setCrawl4aiViewportHeight={(value) => handleFormChange('crawl4aiViewportHeight', value)}
                crawl4aiProxyUrl={formState.crawl4aiProxyUrl}
                setCrawl4aiProxyUrl={(value) => handleFormChange('crawl4aiProxyUrl', value)}
                crawl4aiPageLoadWaitCondition={formState.crawl4aiPageLoadWaitCondition}
                setCrawl4aiPageLoadWaitCondition={(value) => handleFormChange('crawl4aiPageLoadWaitCondition', value)}
                crawl4aiPageTimeout={formState.crawl4aiPageTimeout}
                setCrawl4aiPageTimeout={(value) => handleFormChange('crawl4aiPageTimeout', value)}
                crawl4aiWaitForCondition={formState.crawl4aiWaitForCondition}
                setCrawl4aiWaitForCondition={(value) => handleFormChange('crawl4aiWaitForCondition', value)}
                crawl4aiEnableJs={formState.crawl4aiEnableJs}
                setCrawl4aiEnableJs={(value) => handleFormChange('crawl4aiEnableJs', value)}
                crawl4aiIgnoreHttpsErrors={formState.crawl4aiIgnoreHttpsErrors}
                setCrawl4aiIgnoreHttpsErrors={(value) => handleFormChange('crawl4aiIgnoreHttpsErrors', value)}
                crawl4aiLightMode={formState.crawl4aiLightMode}
                setCrawl4aiLightMode={(value) => handleFormChange('crawl4aiLightMode', value)}
                crawl4aiTextMode={formState.crawl4aiTextMode}
                setCrawl4aiTextMode={(value) => handleFormChange('crawl4aiTextMode', value)}
                crawl4aiTargetElements={formState.crawl4aiTargetElements}
                setCrawl4aiTargetElements={(value) => handleFormChange('crawl4aiTargetElements', value)}
                crawl4aiExcludedElements={formState.crawl4aiExcludedElements}
                setCrawl4aiExcludedElements={(value) => handleFormChange('crawl4aiExcludedElements', value)}
                crawl4aiExcludedTags={formState.crawl4aiExcludedTags}
                setCrawl4aiExcludedTags={(value) => handleFormChange('crawl4aiExcludedTags', value)}
                crawl4aiExtractOnlyTextContent={formState.crawl4aiExtractOnlyTextContent}
                setCrawl4aiExtractOnlyTextContent={(value) => handleFormChange('crawl4aiExtractOnlyTextContent', value)}
                crawl4aiProcessIframes={formState.crawl4aiProcessIframes}
                setCrawl4aiProcessIframes={(value) => handleFormChange('crawl4aiProcessIframes', value)}
                crawl4aiWordCountThreshold={formState.crawl4aiWordCountThreshold}
                setCrawl4aiWordCountThreshold={(value) => handleFormChange('crawl4aiWordCountThreshold', value)}
                crawl4aiRemoveForms={formState.crawl4aiRemoveForms}
                setCrawl4aiRemoveForms={(value) => handleFormChange('crawl4aiRemoveForms', value)}
                crawl4aiKeepDataAttributes={formState.crawl4aiKeepDataAttributes}
                setCrawl4aiKeepDataAttributes={(value) => handleFormChange('crawl4aiKeepDataAttributes', value)}
                crawl4aiExecuteJsOnLoad={formState.crawl4aiExecuteJsOnLoad}
                setCrawl4aiExecuteJsOnLoad={(value) => handleFormChange('crawl4aiExecuteJsOnLoad', value)}
                crawl4aiScanFullPage={formState.crawl4aiScanFullPage}
                setCrawl4aiScanFullPage={(value) => handleFormChange('crawl4aiScanFullPage', value)}
                crawl4aiScrollDelay={formState.crawl4aiScrollDelay}
                setCrawl4aiScrollDelay={(value) => handleFormChange('crawl4aiScrollDelay', value)}
                crawl4aiRemoveOverlayElements={formState.crawl4aiRemoveOverlayElements}
                setCrawl4aiRemoveOverlayElements={(value) => handleFormChange('crawl4aiRemoveOverlayElements', value)}
                crawl4aiSimulateUserBehavior={formState.crawl4aiSimulateUserBehavior}
                setCrawl4aiSimulateUserBehavior={(value) => handleFormChange('crawl4aiSimulateUserBehavior', value)}
                crawl4aiEnableMagic={formState.crawl4aiEnableMagic}
                setCrawl4aiEnableMagic={(value) => handleFormChange('crawl4aiEnableMagic', value)}
                crawl4aiOverrideNavigator={formState.crawl4aiOverrideNavigator}
                setCrawl4aiOverrideNavigator={(value) => handleFormChange('crawl4aiOverrideNavigator', value)}
                crawl4aiCacheMode={formState.crawl4aiCacheMode}
                setCrawl4aiCacheMode={(value) => handleFormChange('crawl4aiCacheMode', value)}
                crawl4aiCaptureScreenshot={formState.crawl4aiCaptureScreenshot}
                setCrawl4aiCaptureScreenshot={(value) => handleFormChange('crawl4aiCaptureScreenshot', value)}
                crawl4aiGeneratePdf={formState.crawl4aiGeneratePdf}
                setCrawl4aiGeneratePdf={(value) => handleFormChange('crawl4aiGeneratePdf', value)}
                crawl4aiCaptureMhtml={formState.crawl4aiCaptureMhtml}
                setCrawl4aiCaptureMhtml={(value) => handleFormChange('crawl4aiCaptureMhtml', value)}
                crawl4aiExcludeExternalImages={formState.crawl4aiExcludeExternalImages}
                setCrawl4aiExcludeExternalImages={(value) => handleFormChange('crawl4aiExcludeExternalImages', value)}
                crawl4aiImageAltTextMinWordCount={formState.crawl4aiImageAltTextMinWordCount}
                setCrawl4aiImageAltTextMinWordCount={(value) => handleFormChange('crawl4aiImageAltTextMinWordCount', value)}
                crawl4aiImageRelevanceScoreThreshold={formState.crawl4aiImageRelevanceScoreThreshold}
                setCrawl4aiImageRelevanceScoreThreshold={(value) => handleFormChange('crawl4aiImageRelevanceScoreThreshold', value)}
                crawl4aiExcludeExternalLinks={formState.crawl4aiExcludeExternalLinks}
                setCrawl4aiExcludeExternalLinks={(value) => handleFormChange('crawl4aiExcludeExternalLinks', value)}
                crawl4aiExcludeSocialMediaLinks={formState.crawl4aiExcludeSocialMediaLinks}
                setCrawl4aiExcludeSocialMediaLinks={(value) => handleFormChange('crawl4aiExcludeSocialMediaLinks', value)}
                crawl4aiCustomExcludedDomains={formState.crawl4aiCustomExcludedDomains}
                setCrawl4aiCustomExcludedDomains={(value) => handleFormChange('crawl4aiCustomExcludedDomains', value)}
                crawl4aiRespectRobotsTxt={formState.crawl4aiRespectRobotsTxt}
                setCrawl4aiRespectRobotsTxt={(value) => handleFormChange('crawl4aiRespectRobotsTxt', value)}
                crawl4aiVerboseLogging={formState.crawl4aiVerboseLogging}
                setCrawl4aiVerboseLogging={(value) => handleFormChange('crawl4aiVerboseLogging', value)}
                crawl4aiLogPageConsoleOutput={formState.crawl4aiLogPageConsoleOutput}
                setCrawl4aiLogPageConsoleOutput={(value) => handleFormChange('crawl4aiLogPageConsoleOutput', value)}
                
                // Pass LLM configuration from formState
                llmProvider={formState.llmProvider}
                setLlmProvider={(value) => handleFormChange('llmProvider', value)}
                llmApiToken={formState.llmApiToken}
                setLlmApiToken={(value) => handleFormChange('llmApiToken', value)}
                llmBaseUrl={formState.llmBaseUrl}
                setLlmBaseUrl={(value) => handleFormChange('llmBaseUrl', value)}
                availableLlmModels={availableLlmModels} // This comes from state, not formState
                isLoadingLlmModels={isLoadingLlmModels} // This comes from state, not formState
                
                crawl4aiMarkdownGenerator={formState.crawl4aiMarkdownGenerator}
                setCrawl4aiMarkdownGenerator={(value) => handleFormChange('crawl4aiMarkdownGenerator', value)}

                // Expert Options
                crawl4aiBrowserCookies={formState.crawl4aiBrowserCookies}
                setCrawl4aiBrowserCookies={(value) => handleFormChange('crawl4aiBrowserCookies', value)}
                crawl4aiBrowserHeaders={formState.crawl4aiBrowserHeaders}
                setCrawl4aiBrowserHeaders={(value) => handleFormChange('crawl4aiBrowserHeaders', value)}
                crawl4aiBrowserUsePersistentContext={formState.crawl4aiBrowserUsePersistentContext}
                setCrawl4aiBrowserUsePersistentContext={(value) => handleFormChange('crawl4aiBrowserUsePersistentContext', value)}
                crawl4aiCrawlSessionId={formState.crawl4aiCrawlSessionId}
                setCrawl4aiCrawlSessionId={(value) => handleFormChange('crawl4aiCrawlSessionId', value)}
                crawl4aiCrawlCssSelector={formState.crawl4aiCrawlCssSelector}
                setCrawl4aiCrawlCssSelector={(value) => handleFormChange('crawl4aiCrawlCssSelector', value)}

                // Strategy Configs passed directly
                crawl4aiExtractionConfig={formState.crawl4aiExtractionConfig}
                onCrawl4aiExtractionConfigChange={handleCrawl4aiExtractionConfigChange} // Use the correct handler
                crawl4aiDeepCrawlConfig={formState.crawl4aiDeepCrawlConfig}
                onCrawl4aiDeepCrawlConfigChange={handleCrawl4aiDeepCrawlConfigChange} // Use the correct handler

                // Common options
                uploadToSupabase={formState.uploadToSupabase}
                setUploadToSupabase={(value) => handleFormChange('uploadToSupabase', value)}
              />
            )}

                {/* Error Display */}
                {mainFetchError && !isFetchingSse && ( // Use renamed state variable
                  <div className="p-4 rounded-md bg-destructive/10 text-destructive mt-4">
                    {mainFetchError}
                  </div>
                )}

                {/* Results Display: Only show if not fetching and result exists */}
                {!isFetchingSse && formState.result && ( // Use renamed state variable
                  <>
                    <div className="flex items-center justify-end mt-4 mb-2"> {/* Adjusted margin for button placement */}
                        <Button
                          onClick={handleSaveToHistory}
                          disabled={isSavedToHistory || isSavingToHistory}
                          size="sm"
                        >
                          {isSavingToHistory ? "Saving..." : isSavedToHistory ? "Saved to History" : "Save to History"}
                        </Button>
                    </div>
                    <FetchedContentViewer fetchedData={formState.result} />
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="fetchHistory">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Fetch History</CardTitle>
                  <Button onClick={handleRefreshHistory} variant="outline" size="sm">
                    Refresh History
                  </Button>
                </div>
                {/* TODO: Add a brief description or instructions here if needed */}
              </CardHeader>
              <CardContent>
                {/* Filter and Sort Controls */}
                <div className="flex flex-wrap gap-4 mb-4 p-4 border rounded-lg">
                  <div className="flex-grow min-w-[200px]">
                    <Label htmlFor="history-search">Search URL/Title</Label>
                    <Input
                      id="history-search"
                      type="text"
                      placeholder="Search URL or Title..."
                      value={historySearchTerm}
                      onChange={handleHistorySearchChange}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="history-filter-engine">Fetching Engine</Label>
                    <Select value={historyFilterEngine} onValueChange={setHistoryFilterEngine}>
                      <SelectTrigger id="history-filter-engine" className="mt-1">
                        <SelectValue placeholder="All Engines" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_engines">All Engines</SelectItem>
                        <SelectItem value="jina">Jina</SelectItem>
                        <SelectItem value="crawl4ai">Crawl4AI</SelectItem>
                        {/* Add other engines if they become available */}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="history-filter-status">Status</Label>
                    <Select value={historyFilterStatus} onValueChange={setHistoryFilterStatus}>
                      <SelectTrigger id="history-filter-status" className="mt-1">
                        <SelectValue placeholder="All Statuses" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_statuses">All Statuses</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="error">Error</SelectItem>
                        {/* Add other relevant statuses */}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="history-sort">Sort By</Label>
                    <Select
                      value={`${historySortColumn}-${historySortDirection}`}
                      onValueChange={(value) => {
                        const [col, dir] = value.split('-');
                        setHistorySortColumn(col);
                        setHistorySortDirection(dir);
                      }}
                    >
                      <SelectTrigger id="history-sort" className="mt-1">
                        <SelectValue placeholder="Sort by..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fetch_date-desc">Date (Newest First)</SelectItem>
                        <SelectItem value="fetch_date-asc">Date (Oldest First)</SelectItem>
                        {/* Add other sortable columns if needed, e.g., title */}
                        {/* <SelectItem value="title-asc">Title (A-Z)</SelectItem> */}
                        {/* <SelectItem value="title-desc">Title (Z-A)</SelectItem> */}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {historyError && (
                  <div className="p-4 rounded-md bg-destructive/10 text-destructive">
                    Error loading history: {typeof historyError === 'object' && historyError.message ? historyError.message : String(historyError)}
                  </div>
                )}
                <FetchHistoryTable
                  fetchHistoryItems={fetchHistoryItems || []} // Pass data from hook, ensure array
                  loadMore={loadMoreHistory} // Pass fetchNextPage from hook
                  hasMore={hasMoreHistory} // Pass hasMore from hook
                  isLoadingMore={isLoadingHistoryMore || isLoadingHistoryInitial} // Use isFetching or isLoading from hook
                  onViewItem={handleViewHistoryItem}
                  onDeleteItem={handleDeleteHistoryItem}
                  onRefetchItem={handleRefetchHistoryItem}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="managePresets"> {/* Added PresetsManager Content */}
            <PresetsManager />
          </TabsContent>
        </Tabs>
      </main>
    </>
  );
}