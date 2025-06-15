"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input"; // Added
import { Label } from "@/components/ui/label"; // Added
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"; // Added
import { toast } from "sonner";
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
import { createClient } from '@/lib/client'; // Import Supabase client creator
import { useInfiniteQuery } from '@/hooks/use-infinite-query'; // Import the hook
import { Progress } from "@/components/ui/progress";
import ResultsDisplay from "@/components/fetch/ResultsDisplay";

const ITEMS_PER_PAGE = 15;

// Debounce utility function
function debounce(func, delay) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, delay);
  };
}

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

  const [activeMainTab, setActiveMainTab] = useState(initialActiveMainTab); // For top-level tabs (Fetch/History)
  const [isSavedToHistory, setIsSavedToHistory] = useState(false);
  const [isSavingToHistory, setIsSavingToHistory] = useState(false);
  const [fetchingEngine, setFetchingEngine] = useState("jina"); // Isolate fetchingEngine state

  const supabase = createClient(); // Instantiate Supabase client

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
    filters: historyFilters,
    sortOptions: historySort,
  });

  // Consolidated state for all form options
  const [formState, setFormState] = useState({
    // Basic options
    url: "",
    fetchDepth: "page_only", 
    targetContentArea: "main_content", 
    advancedSelector: "", 
    targetSelectorAdvanced: "", 
    excludedSelectors: "header,footer,nav,aside,script,style", 
    timeout: 60, 
    jsonResponse: false,
    cleanFormat: true,
    browserEngine: "chromium", 
    tokenBudget: 4000,
    extractTextOnly: false, 
    extractTables: true, 
    extractImages: true, 
    extractLinks: true,
    imageCaptioning: false,
    cacheTtl: 3600,
    markdownFlavor: "gfm", 
    viewportWidth: 1920, 
    viewportHeight: 1080, 
    browserLocale: "en-US",
    extractMetadata: true,
    uploadToSupabase: false,
    result: null,
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
    crawl4aiTargetElements: "",
    crawl4aiExcludedElements: "",
    crawl4aiExcludedTags: "script,style,noscript,iframe,nav,footer,aside",
    crawl4aiExtractOnlyTextContent: false,
    crawl4aiProcessIframes: false,
    crawl4aiWordCountThreshold: 50,
    crawl4aiRemoveForms: true,
    crawl4aiKeepDataAttributes: false,
    crawl4aiExecuteJsOnLoad: "",
    crawl4aiScanFullPage: false,
    crawl4aiScrollDelay: 2, 
    crawl4aiRemoveOverlayElements: true,
    crawl4aiSimulateUserBehavior: false,
    crawl4aiEnableMagic: false,
    crawl4aiOverrideNavigator: false,
    crawl4aiCacheMode: "enabled", 
    crawl4aiCaptureScreenshot: false,
    crawl4aiGeneratePdf: false,
    crawl4aiCaptureMhtml: false,
    crawl4aiExcludeExternalImages: false,
    crawl4aiImageAltTextMinWordCount: 0,
    crawl4aiImageRelevanceScoreThreshold: 0,
    crawl4aiExcludeExternalLinks: false,
    crawl4aiExcludeSocialMediaLinks: false,
    crawl4aiCustomExcludedDomains: "",
    crawl4aiRespectRobotsTxt: true,
    crawl4aiVerboseLogging: false,
    crawl4aiLogPageConsoleOutput: false,
    llmProvider: "", 
    llmApiToken: "", 
    llmBaseUrl: "",  
    crawl4aiMarkdownGenerator: "Default", 
    crawl4aiBrowserCookies: "",
    crawl4aiBrowserHeaders: "",
    crawl4aiBrowserUsePersistentContext: false,
    crawl4aiCrawlSessionId: "",
    crawl4aiCrawlCssSelector: "",
    crawl4aiExtractionConfig: { strategy: 'none', params: {} },
    crawl4aiDeepCrawlConfig: { strategy: 'None', params: {} },
  });

  const [removeImagesBackend, setRemoveImagesBackend] = useState(false);

  useEffect(() => {
    if (formState.extractTextOnly) {
      setRemoveImagesBackend(true);
    } else {
      setRemoveImagesBackend(!formState.extractImages);
    }
  }, [formState.extractTextOnly, formState.extractImages]);


  const estimateProgress = (status) => {
    if (!status) return 0;
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes("initializing")) return 10;
    if (lowerStatus.includes("fetching main content")) return 30;
    if (lowerStatus.includes("processing content") || lowerStatus.includes("parsing content")) return 70;
    if (lowerStatus.includes("scraping additional data") || lowerStatus.includes("extracting")) return 85;
    if (lowerStatus.includes("completed") || lowerStatus.includes("finished")) return 100;
    if (lowerStatus.includes("error")) return 0; 
    return progressPercent; 
  };

  const handleFetchContent = async () => {
    if (!formState.url.trim()) {
      setMainFetchError("Please enter a URL to fetch content.");
      return;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsFetchingSse(true); 
    setMainFetchError(null);
    setProgressMessage("Initializing...");
    setProgressPercent(10);
    setFormState(prev => ({ ...prev, result: null })); 
    setIsSavedToHistory(false); 
    setIsSavingToHistory(false); 

    const params = new URLSearchParams({
      url: formState.url,
      fetch_depth: formState.fetchDepth,
      target_content_area: formState.targetContentArea,
      target_selector: formState.targetContentArea === 'advanced' ? formState.advancedSelector : formState.targetContentArea,
      excluded_selector: formState.excludedSelectors,
      timeout: formState.timeout,
      extract_links: formState.extractLinks,
      image_captioning: formState.imageCaptioning,
      markdown_flavor: formState.markdownFlavor,
      extract_metadata: formState.extractMetadata,
      upload_to_supabase: formState.uploadToSupabase,
      engine: fetchingEngine, 
    });

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
    } else if (fetchingEngine === 'crawl4ai') { 
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
      if (formState.crawl4aiTargetElements) params.append('crawl4ai_target_elements', formState.crawl4aiTargetElements);
      if (formState.crawl4aiExcludedElements) params.append('crawl4ai_excluded_elements', formState.crawl4aiExcludedElements);
      if (formState.crawl4aiExcludedTags) params.append('crawl4ai_excluded_tags', formState.crawl4aiExcludedTags);
      params.append('crawl4ai_extract_only_text_content', formState.crawl4aiExtractOnlyTextContent.toString());
      params.append('crawl4ai_process_iframes', formState.crawl4aiProcessIframes.toString());
      if (formState.crawl4aiWordCountThreshold !== undefined) params.append('crawl4ai_word_count_threshold', formState.crawl4aiWordCountThreshold.toString());
      params.append('crawl4ai_remove_forms', formState.crawl4aiRemoveForms.toString());
      params.append('crawl4ai_keep_data_attributes', formState.crawl4aiKeepDataAttributes.toString());
        if (formState.crawl4aiExecuteJsOnLoad) params.append('crawl4ai_execute_js_on_load', formState.crawl4aiExecuteJsOnLoad);
        params.append('crawl4ai_scan_full_page', formState.crawl4aiScanFullPage.toString());
        if (formState.crawl4aiScanFullPage && formState.crawl4aiScrollDelay !== undefined) {
          params.append('crawl4ai_scroll_delay', formState.crawl4aiScrollDelay.toString());
        }
        params.append('crawl4ai_remove_overlay_elements', formState.crawl4aiRemoveOverlayElements.toString());
        params.append('crawl4ai_simulate_user_behavior', formState.crawl4aiSimulateUserBehavior.toString());
        params.append('crawl4ai_enable_magic', formState.crawl4aiEnableMagic.toString());
        params.append('crawl4ai_override_navigator', formState.crawl4aiOverrideNavigator.toString());
        if (formState.crawl4aiCacheMode) params.append('crawl4ai_cache_mode', formState.crawl4aiCacheMode);
        params.append('crawl4ai_capture_screenshot', formState.crawl4aiCaptureScreenshot.toString());
        params.append('crawl4ai_generate_pdf', formState.crawl4aiGeneratePdf.toString());
        params.append('crawl4ai_capture_mhtml', formState.crawl4aiCaptureMhtml.toString());
        params.append('crawl4ai_exclude_external_images', formState.crawl4aiExcludeExternalImages.toString());
        if (formState.crawl4aiImageAltTextMinWordCount !== undefined) params.append('crawl4ai_image_alt_text_min_word_count', formState.crawl4aiImageAltTextMinWordCount.toString());
        if (formState.crawl4aiImageRelevanceScoreThreshold !== undefined) params.append('crawl4ai_image_relevance_score_threshold', formState.crawl4aiImageRelevanceScoreThreshold.toString());
          params.append('crawl4ai_exclude_external_links', formState.crawl4aiExcludeExternalLinks.toString());
          params.append('crawl4ai_exclude_social_media_links', formState.crawl4aiExcludeSocialMediaLinks.toString());
          if (formState.crawl4aiCustomExcludedDomains) params.append('crawl4ai_custom_excluded_domains', formState.crawl4aiCustomExcludedDomains);
          params.append('crawl4ai_respect_robots_txt', formState.crawl4aiRespectRobotsTxt.toString());
          params.append('crawl4ai_verbose_logging', formState.crawl4aiVerboseLogging.toString());
          params.append('crawl4ai_log_page_console_output', formState.crawl4aiLogPageConsoleOutput.toString());
          if (formState.llmProvider) params.append('llm_provider', formState.llmProvider);
          if (formState.llmApiToken) params.append('llm_api_key', formState.llmApiToken); 
          if (formState.llmBaseUrl) params.append('llm_base_url', formState.llmBaseUrl);
          if (formState.crawl4aiMarkdownGenerator && formState.crawl4aiMarkdownGenerator !== "Default") {
            params.append('crawl4ai_markdown_generator', formState.crawl4aiMarkdownGenerator);
          }
          if (formState.crawl4aiBrowserCookies) {
            try {
              const cookiesValue = typeof formState.crawl4aiBrowserCookies === 'string' ? formState.crawl4aiBrowserCookies : JSON.stringify(formState.crawl4aiBrowserCookies);
              params.append('browser_cookies', cookiesValue);
            } catch (e) {
              console.error("Error stringifying crawl4aiBrowserCookies:", e);
              if (typeof formState.crawl4aiBrowserCookies === 'string') {
                params.append('browser_cookies', formState.crawl4aiBrowserCookies);
              }
            }
          }
          if (formState.crawl4aiBrowserHeaders) {
            try {
              const headersValue = typeof formState.crawl4aiBrowserHeaders === 'string' ? formState.crawl4aiBrowserHeaders : JSON.stringify(formState.crawl4aiBrowserHeaders);
              params.append('browser_headers', headersValue);
            } catch (e) {
              console.error("Error stringifying crawl4aiBrowserHeaders:", e);
              if (typeof formState.crawl4aiBrowserHeaders === 'string') {
                params.append('browser_headers', formState.crawl4aiBrowserHeaders);
              }
            }
          }
          params.append('browser_use_persistent_context', formState.crawl4aiBrowserUsePersistentContext.toString()); 
          if (formState.crawl4aiCrawlSessionId) params.append('crawl_session_id', formState.crawl4aiCrawlSessionId);
          if (formState.crawl4aiCrawlCssSelector) params.append('crawl_css_selector', formState.crawl4aiCrawlCssSelector);
          if (formState.crawl4aiExtractionConfig && formState.crawl4aiExtractionConfig.strategy !== 'none') {
            params.append('crawl4ai_extraction_strategy', JSON.stringify(formState.crawl4aiExtractionConfig));
          }
          if (formState.crawl4aiDeepCrawlConfig && formState.crawl4aiDeepCrawlConfig.strategy !== 'None') {
            params.append('crawl4ai_deep_crawl_strategy', JSON.stringify(formState.crawl4aiDeepCrawlConfig));
          }
        }

    const sseUrl = `${BACKEND_URL}/fetch-content?${params.toString()}`;
    eventSourceRef.current = new EventSource(sseUrl);

    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgressMessage(data.status || data.message || "Processing...");
        
        let currentProgress = estimateProgress(data.status || data.message);
        if (data.progress && typeof data.progress === 'number') {
            currentProgress = data.progress;
        }
        setProgressPercent(currentProgress);

        if (data.type === 'completed' || data.status?.toLowerCase().includes('completed')) {
          const backendPayload = data.content || {};
          const viewerData = {
            title: backendPayload.title,
            markdownContent: backendPayload.content, 
            pdf_file_path: backendPayload.pdf_path, 
            metadata: backendPayload.metadata,
            links: backendPayload.links,
          };
          setFormState(prev => ({ ...prev, result: viewerData }));
          setProgressMessage("Fetch completed successfully!");
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
          setIsFetchingSse(false); 
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }
        }
      } catch (e) {
        console.error("Error parsing SSE message or updating state:", e);
        setMainFetchError("Received malformed progress update.");
      }
    };

    eventSourceRef.current.onerror = (err) => {
      console.error("EventSource failed:", err);
      setMainFetchError("Connection to server lost or failed to establish for progress updates.");
      setProgressMessage("Connection error.");
      setProgressPercent(0);
      setIsFetchingSse(false); 
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
    setIsFetchingSse(false); 
    setProgressMessage("Fetch cancelled by user.");
    setProgressPercent(0);
    setFormState(prev => ({ ...prev, result: null })); 
  };
  
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const setFormValue = useCallback((key, value) => {
    setFormState(prev => {
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
  }, [setFormState]); 

  const handleCrawl4aiExtractionConfigChange = useCallback((config) => {
    setFormValue('crawl4aiExtractionConfig', config);
  }, [setFormValue]);

  const handleCrawl4aiDeepCrawlConfigChange = useCallback((config) => {
    setFormValue('crawl4aiDeepCrawlConfig', config);
  }, [setFormValue]);

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
  const setLlmProviderHandler = useCallback((val) => setFormValue('llmProvider', val), [setFormValue]); 
  const setLlmApiTokenHandler = useCallback((val) => setFormValue('llmApiToken', val), [setFormValue]); 
  const setLlmBaseUrlHandler = useCallback((val) => setFormValue('llmBaseUrl', val), [setFormValue]);   
  const setCrawl4aiMarkdownGeneratorHandler = useCallback((val) => setFormValue('crawl4aiMarkdownGenerator', val), [setFormValue]);
  const setCrawl4aiBrowserCookiesHandler = useCallback((val) => setFormValue('crawl4aiBrowserCookies', val), [setFormValue]);
  const setCrawl4aiBrowserHeadersHandler = useCallback((val) => setFormValue('crawl4aiBrowserHeaders', val), [setFormValue]);
  const setCrawl4aiBrowserUsePersistentContextHandler = useCallback((val) => setFormValue('crawl4aiBrowserUsePersistentContext', val), [setFormValue]);
  const setCrawl4aiCrawlSessionIdHandler = useCallback((val) => setFormValue('crawl4aiCrawlSessionId', val), [setFormValue]);
  const setCrawl4aiCrawlCssSelectorHandler = useCallback((val) => setFormValue('crawl4aiCrawlCssSelector', val), [setFormValue]);

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
      extract_links: formState.extractLinks,
      image_captioning: formState.imageCaptioning,
      markdown_flavor: formState.markdownFlavor,
      extract_metadata: formState.extractMetadata,
      upload_to_supabase: formState.uploadToSupabase,
    };

    if (fetchingEngine === 'jina') { 
      engineSpecificParams.target_selector_advanced = formState.targetSelectorAdvanced;
      engineSpecificParams.json_response = formState.jsonResponse;
      engineSpecificParams.clean_format = formState.cleanFormat;
      engineSpecificParams.browser_engine = formState.browserEngine;
      engineSpecificParams.token_budget = formState.tokenBudget;
      engineSpecificParams.remove_images = removeImagesBackend; 
      engineSpecificParams.cache_ttl = formState.cacheTtl;
      engineSpecificParams.browser_viewport = `${formState.viewportWidth}x${formState.viewportHeight}`;
      engineSpecificParams.browser_locale = formState.browserLocale;
    } else if (fetchingEngine === 'crawl4ai') { 
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
      engineSpecificParams.crawl4ai_target_elements = formState.crawl4aiTargetElements;
      engineSpecificParams.crawl4ai_excluded_elements = formState.crawl4aiExcludedElements;
      engineSpecificParams.crawl4ai_excluded_tags = formState.crawl4aiExcludedTags;
      engineSpecificParams.crawl4ai_extract_only_text_content = formState.crawl4aiExtractOnlyTextContent;
      engineSpecificParams.crawl4ai_process_iframes = formState.crawl4aiProcessIframes;
      engineSpecificParams.crawl4ai_word_count_threshold = formState.crawl4aiWordCountThreshold;
      engineSpecificParams.crawl4ai_remove_forms = formState.crawl4aiRemoveForms;
      engineSpecificParams.crawl4ai_keep_data_attributes = formState.crawl4aiKeepDataAttributes;
      engineSpecificParams.crawl4ai_execute_js_on_load = formState.crawl4aiExecuteJsOnLoad;
      engineSpecificParams.crawl4ai_scan_full_page = formState.crawl4aiScanFullPage;
      engineSpecificParams.crawl4ai_scroll_delay = formState.crawl4aiScrollDelay;
      engineSpecificParams.crawl4ai_remove_overlay_elements = formState.crawl4aiRemoveOverlayElements;
      engineSpecificParams.crawl4ai_simulate_user_behavior = formState.crawl4aiSimulateUserBehavior;
      engineSpecificParams.crawl4ai_enable_magic = formState.crawl4aiEnableMagic;
      engineSpecificParams.crawl4ai_override_navigator = formState.crawl4aiOverrideNavigator;
      engineSpecificParams.crawl4ai_cache_mode = formState.crawl4aiCacheMode;
      engineSpecificParams.crawl4ai_capture_screenshot = formState.crawl4aiCaptureScreenshot;
      engineSpecificParams.crawl4ai_generate_pdf = formState.crawl4aiGeneratePdf;
      engineSpecificParams.crawl4ai_capture_mhtml = formState.crawl4aiCaptureMhtml;
      engineSpecificParams.crawl4ai_exclude_external_images = formState.crawl4aiExcludeExternalImages;
      engineSpecificParams.crawl4ai_image_alt_text_min_word_count = formState.crawl4aiImageAltTextMinWordCount;
      engineSpecificParams.crawl4ai_image_relevance_score_threshold = formState.crawl4aiImageRelevanceScoreThreshold;
      engineSpecificParams.crawl4ai_exclude_external_links = formState.crawl4aiExcludeExternalLinks;
      engineSpecificParams.crawl4ai_exclude_social_media_links = formState.crawl4aiExcludeSocialMediaLinks;
      engineSpecificParams.crawl4ai_custom_excluded_domains = formState.crawl4aiCustomExcludedDomains;
      engineSpecificParams.crawl4ai_respect_robots_txt = formState.crawl4aiRespectRobotsTxt;
      engineSpecificParams.crawl4ai_verbose_logging = formState.crawl4aiVerboseLogging;
      engineSpecificParams.crawl4ai_log_page_console_output = formState.crawl4aiLogPageConsoleOutput;
      engineSpecificParams.llm_provider = formState.llmProvider; 
      engineSpecificParams.llm_api_key = formState.llmApiToken; 
      engineSpecificParams.llm_base_url = formState.llmBaseUrl;   
      engineSpecificParams.crawl4ai_markdown_generator = formState.crawl4aiMarkdownGenerator; 
      engineSpecificParams.browser_cookies = formState.crawl4aiBrowserCookies;
      engineSpecificParams.browser_headers = formState.crawl4aiBrowserHeaders;
      engineSpecificParams.browser_use_persistent_context = formState.crawl4aiBrowserUsePersistentContext;
      engineSpecificParams.crawl_session_id = formState.crawl4aiCrawlSessionId;
      engineSpecificParams.crawl_css_selector = formState.crawl4aiCrawlCssSelector;
      engineSpecificParams.crawl4aiExtractionConfig = formState.crawl4aiExtractionConfig;
      engineSpecificParams.crawl4aiDeepCrawlConfig = formState.crawl4aiDeepCrawlConfig;
    }

    if (formState.hasOwnProperty('extractTables')) {
      engineSpecificParams.extract_tables = formState.extractTables;
    }

    const payload = {
      url: formState.url,
      fetching_engine: fetchingEngine, 
      status: 'completed',
      title: formState.result.metadata?.title || formState.result.title || "Untitled",
      engine_specific_parameters: engineSpecificParams,
      output_type: formState.result.pdf_path ? 'pdf_link' : 'markdown',
      raw_content_summary: typeof formState.result.markdown_content === 'string'
        ? (formState.result.markdown_content.substring(0, 250) + ((formState.result.markdown_content.length || 0) > 250 ? '...' : ''))
        : 'Summary not available for non-string content.',
      content_storage_path: formState.result.pdf_path || formState.result.markdown_path || null,
      user_id: null,
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
    setActiveMainTab("fetchContent"); 
    setFormState(prev => ({ ...prev, result: null, error: null })); 
    toast({
      title: "Loading Content...",
      description: `Fetching content for ${item.title || item.url}.`,
    });
    window.scrollTo(0, 0); 

    try {
      const response = await fetch(`${BACKEND_URL}/api/fetch-history/${item.id}/content`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch content and parse error." }));
        throw new Error(errorData.detail || `Failed to fetch content. Status: ${response.status}`);
      }
      const fetchedContentData = await response.json();
      
      const viewerData = {
        title: fetchedContentData.title || item.title || "Untitled",
        markdownContent: fetchedContentData.markdown_content || null,
        pdf_file_path: fetchedContentData.output_type === 'pdf' || fetchedContentData.output_type === 'pdf_link' ? fetchedContentData.content_storage_path : null,
      };

      if (fetchedContentData.output_type === 'json' && fetchedContentData.raw_content) {
        try {
            const jsonData = typeof fetchedContentData.raw_content === 'string' ? JSON.parse(fetchedContentData.raw_content) : fetchedContentData.raw_content;
            viewerData.markdownContent = (viewerData.markdownContent || "") +
                `\n\n## JSON Content\n\n\`\`\`json\n${JSON.stringify(jsonData, null, 2)}\n\`\`\`\`;
        } catch (e) {
            console.error("Error parsing JSON content from history:", e);
            viewerData.markdownContent = (viewerData.markdownContent || "") +
                `\n\n## JSON Content (raw)\n\n\`\`\`\n${fetchedContentData.raw_content}\n\`\`\`\`;
        }
      } else if (fetchedContentData.raw_content && !viewerData.markdownContent) {
         viewerData.markdownContent = `## Raw Content (${fetchedContentData.output_type})\n\n\`\`\`${fetchedContentData.output_type}\n${fetchedContentData.raw_content}\n\`\`\`\`;
      }


      if (!viewerData.markdownContent && !viewerData.pdf_file_path) {
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
      setFormState(prev => ({ ...prev, result: { markdown_content: `## Error Loading Content\n\nCould not load content for "${item.title || item.url}".\n\n**Error:** ${error.message}` } }));
      toast({
        title: "Error Loading Content",
        description: error.message || "An unexpected error occurred.",
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

      if (typeof initializeHistory === 'function') {
        initializeHistory();
      } else {
        console.warn("initializeHistory function not available from useInfiniteQuery hook. History list may not refresh automatically.");
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
      const newPopulatedState = { ...prevFormState };
      newPopulatedState.url = item.url || "";
      setFetchingEngine(item.fetching_engine || 'jina');

      const esp = item.engine_specific_parameters || {};

      for (const espKey in esp) {
        if (Object.prototype.hasOwnProperty.call(esp, espKey)) {
          const value = esp[espKey];
          let formKey = espKey; 

          if (espKey.startsWith('crawl4ai_')) {
            formKey = espKey.replace(/_([a-z])/g, (_match, letter) => letter.toUpperCase());
          } else if (espKey === 'excluded_selector') {
            formKey = 'excludedSelectors';
          } else if (espKey === 'crawl4aiExtractionConfig') {
            newPopulatedState.crawl4aiExtractionConfig = value || { strategy: 'none', params: {} };
            continue;
          } else if (espKey === 'crawl4aiDeepCrawlConfig') {
            newPopulatedState.crawl4aiDeepCrawlConfig = value || { strategy: 'None', params: {} };
            continue;
          }
          
          if (espKey === 'browser_viewport') {
            const [widthStr, heightStr] = (value || "1920x1080").split('x');
            newPopulatedState.viewportWidth = parseInt(widthStr, 10) || 1920;
            newPopulatedState.viewportHeight = parseInt(heightStr, 10) || 1080;
            continue; 
          } else if (espKey === 'remove_images') {
            if (value === true) { 
              newPopulatedState.extractTextOnly = true;
              newPopulatedState.extractImages = false;
            } else { 
              newPopulatedState.extractTextOnly = false;
              newPopulatedState.extractImages = true;
            }
            continue; 
          } else if (espKey === 'target_content_area') {
            newPopulatedState.targetContentArea = value || 'main_content';
            continue;
          } else if (espKey === 'target_selector') {
            continue;
          }

          if (Object.prototype.hasOwnProperty.call(newPopulatedState, formKey)) {
            newPopulatedState[formKey] = value;
          }
        }
      }
      const effectiveTargetContentArea = esp.target_content_area || newPopulatedState.targetContentArea || 'main_content';
      newPopulatedState.targetContentArea = effectiveTargetContentArea; 
      
      if (effectiveTargetContentArea === 'advanced') {
        newPopulatedState.advancedSelector = esp.target_selector || "";
      } else {
        newPopulatedState.advancedSelector = ""; 
      }
      
      newPopulatedState.result = null; 
      return newPopulatedState;
    });

    setActiveMainTab("fetchContent");
    setShowAdvanced(true); 
    window.scrollTo(0, 0); 
    toast({
      title: "Form Populated",
      description: "Form populated with settings from selected history item.",
      variant: "default",
    });
  };
  
  const handleRefreshHistory = useCallback(async () => {
    if (typeof initializeHistory === 'function') { 
      try {
        await initializeHistory(); 
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
  }, [initializeHistory, toast]); 

  useEffect(() => {
    handleRefreshHistory();
  }, []); 

  const [availableModels, setAvailableModels] = useState([]); 
  const [isLoading, setIsLoading] = useState(false); // This isLoading is not the same as history loading
  const [progress, setProgress] = useState(0);     // This progress is not the same as SSE progress
  // const [sseClient, setSseClient] = useState(null); // THIS LINE AND THE SUBSEQUENT USEEFFECT ARE THE PROBLEM

  const debouncedSetFormState = useCallback(debounce((newState) => {
    setFormState(prevState => ({ ...prevState, ...newState }));
  }, 300), []);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/v1/models`); 
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        const models = await response.json();
        setAvailableModels(models || []);
        if (models && models.length > 0 && !formState.llmProvider) {
          // setFormState(prevState => ({ ...prevState, llmProvider: models[0].model_alias }));
        }
        toast({ title: "Models Loaded", description: `Found ${models.length} models.` });
      } catch (error) {
        console.error("Failed to fetch models:", error);
        toast({
          title: "Error Loading Models",
          description: error.message || "Could not fetch model list from backend.",
          variant: "destructive",
        });
        setAvailableModels([]); 
      }
    };

    fetchModels();
  }, [toast, formState.llmProvider]); // Added dependencies

  /*
  // Effect to handle SSE connection - THIS ENTIRE BLOCK IS PROBLEMATIC AND REDUNDANT
  // The main SSE logic is in handleFetchContent using eventSourceRef.current
  useEffect(() => {
    // This block attempts to use sseClient from useState, which causes issues.
    // It's also redundant with the eventSourceRef.current logic in handleFetchContent.
    // Commenting it out as per FETCH_COMPONENT_UPDATES.md
    //
    // if (formState.fetchingEngine === 'crawl4ai' && sseClient) { // sseClient would be the EventSource instance here
    //   sseClient.onmessage = (event) => {
    //     try {
    //       const data = JSON.parse(event.data);
    //       setProgressMessage(data.status || data.message || "Processing...");
          
    //       let currentProgress = estimateProgress(data.status || data.message);
    //       if (data.progress && typeof data.progress === 'number') {
    //           currentProgress = data.progress;
    //       }
    //       setProgressPercent(currentProgress);

    //       if (data.type === 'completed' || data.status?.toLowerCase().includes('completed')) {
    //         const backendPayload = data.content || {};
    //         const viewerData = {
    //           title: backendPayload.title,
    //           markdownContent: backendPayload.content, 
    //           pdf_file_path: backendPayload.pdf_path, 
    //           metadata: backendPayload.metadata,
    //           links: backendPayload.links,
    //         };
    //         setFormState(prev => ({ ...prev, result: viewerData }));
    //         setProgressMessage("Fetch completed successfully!");
    //         setProgressPercent(100);
    //         setIsFetchingSse(false); 
    //         if (sseClient) { 
    //           sseClient.close();
    //           setSseClient(null); // Call the setter
    //         }
    //         console.log("Fetch successful, history refresh might be needed via useInfiniteQuery's mechanisms.");
    //       } else if (data.type === 'error' || data.status?.toLowerCase().includes('error')) {
    //         setMainFetchError(data.error || data.message || "An unknown error occurred during fetch.");
    //         setProgressMessage(data.error || data.message || "Error during fetch.");
    //         setIsFetchingSse(false); 
    //         if (sseClient) { 
    //           sseClient.close();
    //           setSseClient(null); // Call the setter
    //         }
    //       }
    //     } catch (e) {
    //       console.error("Error parsing SSE message or updating state:", e);
    //       setMainFetchError("Received malformed progress update.");
    //     }
    //   };

    //   sseClient.onerror = (err) => { 
    //     console.error("EventSource failed:", err);
    //     setMainFetchError("Connection to server lost or failed to establish for progress updates.");
    //     setProgressMessage("Connection error.");
    //     setProgressPercent(0);
    //     setIsFetchingSse(false); 
    //     if (sseClient) { 
    //       sseClient.close();
    //       setSseClient(null); // Call the setter
    //     }
    //   };
    // }
    // // Cleanup function
    // return () => {
    //   if (sseClient) { // Check if sseClient (the EventSource instance from state) exists
    //     sseClient.close();
    //     setSseClient(null); // Reset the state
    //   }
    // };
  }, [formState.fetchingEngine, sseClient, setSseClient, estimateProgress, setProgressMessage, setProgressPercent, setMainFetchError, setIsFetchingSse, toast]); // Dependencies based on usage
  */

  return (
    <>
      <main className="container mx-auto mt-8 p-4"> 
        <Tabs value={activeMainTab} onValueChange={setActiveMainTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="fetchContent">Fetch New Content</TabsTrigger>
            <TabsTrigger value="fetchHistory">Fetch History</TabsTrigger>
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

            {isFetchingSse && ( 
              <FetchProgressTracker
                progressPercent={progressPercent}
                progressMessage={progressMessage}
                onCancel={handleCancelFetch}
              />
            )}

            {showAdvanced && (
              <AdvancedFetchOptions
                fetchingEngine={fetchingEngine} 
                targetSelectorAdvanced={formState.targetSelectorAdvanced}
                setTargetSelectorAdvanced={setTargetSelectorAdvancedHandler}
                excludedSelectors={formState.excludedSelectors} 
                setExcludedSelectors={setExcludedSelectorsHandler} 
                browserEngine={formState.browserEngine}
                setBrowserEngine={setBrowserEngineHandler}
                tokenBudget={formState.tokenBudget}
                setTokenBudget={setTokenBudgetHandler}
                viewportWidth={formState.viewportWidth}
                setViewportWidth={setViewportWidthHandler}
                viewportHeight={formState.viewportHeight}
                setViewportHeight={setViewportHeightHandler}
                markdownFlavor={formState.markdownFlavor}
                setMarkdownFlavor={setMarkdownFlavorHandler}
                timeout={formState.timeout}
                setTimeout={setTimeoutHandler}
                extractTextOnly={formState.extractTextOnly}
                setExtractTextOnly={setExtractTextOnlyHandler}
                extractTables={formState.extractTables}
                setExtractTables={setExtractTablesHandler}
                extractImages={formState.extractImages}
                setExtractImages={setExtractImagesHandler}
                extractLinks={formState.extractLinks}
                setExtractLinks={setExtractLinksHandler}
                jsonResponse={formState.jsonResponse}
                setJsonResponse={setJsonResponseHandler}
                cleanFormat={formState.cleanFormat}
                setCleanFormat={setCleanFormatHandler}
                uploadToSupabase={formState.uploadToSupabase}
                setUploadToSupabase={setUploadToSupabaseHandler}
                imageCaptioning={formState.imageCaptioning}
                setImageCaptioning={setImageCaptioningHandler}
                cacheTtl={formState.cacheTtl}
                setCacheTtl={setCacheTtlHandler}
                browserLocale={formState.browserLocale}
                setBrowserLocale={setBrowserLocaleHandler}
                extractMetadata={formState.extractMetadata}
                setExtractMetadata={setExtractMetadataHandler}
                crawl4aiUserAgent={formState.crawl4aiUserAgent}
                setCrawl4aiUserAgent={setCrawl4aiUserAgentHandler}
                crawl4aiViewportWidth={formState.crawl4aiViewportWidth}
                setCrawl4aiViewportWidth={setCrawl4aiViewportWidthHandler}
                crawl4aiViewportHeight={formState.crawl4aiViewportHeight}
                setCrawl4aiViewportHeight={setCrawl4aiViewportHeightHandler}
                crawl4aiProxyUrl={formState.crawl4aiProxyUrl}
                setCrawl4aiProxyUrl={setCrawl4aiProxyUrlHandler}
                crawl4aiPageLoadWaitCondition={formState.crawl4aiPageLoadWaitCondition}
                setCrawl4aiPageLoadWaitCondition={setCrawl4aiPageLoadWaitConditionHandler}
                crawl4aiPageTimeout={formState.crawl4aiPageTimeout}
                setCrawl4aiPageTimeout={setCrawl4aiPageTimeoutHandler}
                crawl4aiWaitForCondition={formState.crawl4aiWaitForCondition}
                setCrawl4aiWaitForCondition={setCrawl4aiWaitForConditionHandler}
                crawl4aiEnableJs={formState.crawl4aiEnableJs}
                setCrawl4aiEnableJs={setCrawl4aiEnableJsHandler}
                crawl4aiIgnoreHttpsErrors={formState.crawl4aiIgnoreHttpsErrors}
                setCrawl4aiIgnoreHttpsErrors={setCrawl4aiIgnoreHttpsErrorsHandler}
                crawl4aiLightMode={formState.crawl4aiLightMode}
                setCrawl4aiLightMode={setCrawl4aiLightModeHandler}
                crawl4aiTextMode={formState.crawl4aiTextMode}
                setCrawl4aiTextMode={setCrawl4aiTextModeHandler}
                crawl4aiTargetElements={formState.crawl4aiTargetElements}
                setCrawl4aiTargetElements={setCrawl4aiTargetElementsHandler}
                crawl4aiExcludedElements={formState.crawl4aiExcludedElements}
                setCrawl4aiExcludedElements={setCrawl4aiExcludedElementsHandler}
                crawl4aiExcludedTags={formState.crawl4aiExcludedTags}
                setCrawl4aiExcludedTags={setCrawl4aiExcludedTagsHandler}
                crawl4aiExtractOnlyTextContent={formState.crawl4aiExtractOnlyTextContent}
                setCrawl4aiExtractOnlyTextContent={setCrawl4aiExtractOnlyTextContentHandler}
                crawl4aiProcessIframes={formState.crawl4aiProcessIframes}
                setCrawl4aiProcessIframes={setCrawl4aiProcessIframesHandler}
                crawl4aiWordCountThreshold={formState.crawl4aiWordCountThreshold}
                setCrawl4aiWordCountThreshold={setCrawl4aiWordCountThresholdHandler}
                crawl4aiRemoveForms={formState.crawl4aiRemoveForms}
                setCrawl4aiRemoveForms={setCrawl4aiRemoveFormsHandler}
                crawl4aiKeepDataAttributes={formState.crawl4aiKeepDataAttributes}
                setCrawl4aiKeepDataAttributes={setCrawl4aiKeepDataAttributesHandler}
                crawl4aiExecuteJsOnLoad={formState.crawl4aiExecuteJsOnLoad}
                setCrawl4aiExecuteJsOnLoad={setCrawl4aiExecuteJsOnLoadHandler}
                crawl4aiScanFullPage={formState.crawl4aiScanFullPage}
                setCrawl4aiScanFullPage={setCrawl4aiScanFullPageHandler}
                crawl4aiScrollDelay={formState.crawl4aiScrollDelay}
                setCrawl4aiScrollDelay={setCrawl4aiScrollDelayHandler}
                crawl4aiRemoveOverlayElements={formState.crawl4aiRemoveOverlayElements}
                setCrawl4aiRemoveOverlayElements={setCrawl4aiRemoveOverlayElementsHandler}
                crawl4aiSimulateUserBehavior={formState.crawl4aiSimulateUserBehavior}
                setCrawl4aiSimulateUserBehavior={setCrawl4aiSimulateUserBehaviorHandler}
                crawl4aiEnableMagic={formState.crawl4aiEnableMagic}
                setCrawl4aiEnableMagic={setCrawl4aiEnableMagicHandler}
                crawl4aiOverrideNavigator={formState.crawl4aiOverrideNavigator}
                setCrawl4aiOverrideNavigator={setCrawl4aiOverrideNavigatorHandler}
                crawl4aiCacheMode={formState.crawl4aiCacheMode}
                setCrawl4aiCacheMode={setCrawl4aiCacheModeHandler}
                crawl4aiCaptureScreenshot={formState.crawl4aiCaptureScreenshot}
                setCrawl4aiCaptureScreenshot={setCrawl4aiCaptureScreenshotHandler}
                crawl4aiGeneratePdf={formState.crawl4aiGeneratePdf}
                setCrawl4aiGeneratePdf={setCrawl4aiGeneratePdfHandler}
                crawl4aiCaptureMhtml={formState.crawl4aiCaptureMhtml}
                setCrawl4aiCaptureMhtml={setCrawl4aiCaptureMhtmlHandler}
                crawl4aiExcludeExternalImages={formState.crawl4aiExcludeExternalImages}
                setCrawl4aiExcludeExternalImages={setCrawl4aiExcludeExternalImagesHandler}
                crawl4aiImageAltTextMinWordCount={formState.crawl4aiImageAltTextMinWordCount}
                setCrawl4aiImageAltTextMinWordCount={setCrawl4aiImageAltTextMinWordCountHandler}
                crawl4aiImageRelevanceScoreThreshold={formState.crawl4aiImageRelevanceScoreThreshold}
                setCrawl4aiImageRelevanceScoreThreshold={setCrawl4aiImageRelevanceScoreThresholdHandler}
                crawl4aiExcludeExternalLinks={formState.crawl4aiExcludeExternalLinks}
                setCrawl4aiExcludeExternalLinks={setCrawl4aiExcludeExternalLinksHandler}
                crawl4aiExcludeSocialMediaLinks={formState.crawl4aiExcludeSocialMediaLinks}
                setCrawl4aiExcludeSocialMediaLinks={setCrawl4aiExcludeSocialMediaLinksHandler}
                crawl4aiCustomExcludedDomains={formState.crawl4aiCustomExcludedDomains}
                setCrawl4aiCustomExcludedDomains={setCrawl4aiCustomExcludedDomainsHandler}
                crawl4aiRespectRobotsTxt={formState.crawl4aiRespectRobotsTxt}
                setCrawl4aiRespectRobotsTxt={setCrawl4aiRespectRobotsTxtHandler}
                crawl4aiVerboseLogging={formState.crawl4aiVerboseLogging}
                setCrawl4aiVerboseLogging={setCrawl4aiVerboseLoggingHandler}
                crawl4aiLogPageConsoleOutput={formState.crawl4aiLogPageConsoleOutput}
                setCrawl4aiLogPageConsoleOutput={setCrawl4aiLogPageConsoleOutputHandler}
                llmProvider={formState.llmProvider} 
                setLlmProvider={setLlmProviderHandler} 
                llmApiToken={formState.llmApiToken} 
                setLlmApiToken={setLlmApiTokenHandler} 
                llmBaseUrl={formState.llmBaseUrl} 
                setLlmBaseUrl={setLlmBaseUrlHandler} 
                availableModels={availableModels} // Pass available models to AdvancedFetchOptions
                crawl4aiMarkdownGenerator={formState.crawl4aiMarkdownGenerator}
                setCrawl4aiMarkdownGenerator={setCrawl4aiMarkdownGeneratorHandler}
                crawl4aiBrowserCookies={formState.crawl4aiBrowserCookies}
                setCrawl4aiBrowserCookies={setCrawl4aiBrowserCookiesHandler}
                crawl4aiBrowserHeaders={formState.crawl4aiBrowserHeaders}
                setCrawl4aiBrowserHeaders={setCrawl4aiBrowserHeadersHandler}
                crawl4aiBrowserUsePersistentContext={formState.crawl4aiBrowserUsePersistentContext}
                setCrawl4aiBrowserUsePersistentContext={setCrawl4aiBrowserUsePersistentContextHandler}
                crawl4aiCrawlSessionId={formState.crawl4aiCrawlSessionId}
                setCrawl4aiCrawlSessionId={setCrawl4aiCrawlSessionIdHandler}
                crawl4aiCrawlCssSelector={formState.crawl4aiCrawlCssSelector}
                setCrawl4aiCrawlCssSelector={setCrawl4aiCrawlCssSelectorHandler}
                crawl4aiExtractionConfig={formState.crawl4aiExtractionConfig}
                onCrawl4aiExtractionConfigChange={handleCrawl4aiExtractionConfigChange}
                crawl4aiDeepCrawlConfig={formState.crawl4aiDeepCrawlConfig}
                onCrawl4aiDeepCrawlConfigChange={handleCrawl4aiDeepCrawlConfigChange}
              />
            )}

                {mainFetchError && !isFetchingSse && ( 
                  <div className="p-4 rounded-md bg-destructive/10 text-destructive mt-4\">\
                    {mainFetchError}
                  </div>
                )}

                {!isFetchingSse && formState.result && ( 
                  <>
                    <div className="flex items-center justify-end mt-4 mb-2"> 
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
              </CardHeader>
              <CardContent>
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
                  fetchHistoryItems={fetchHistoryItems || []} 
                  loadMore={loadMoreHistory} 
                  hasMore={hasMoreHistory} 
                  isLoadingMore={isLoadingHistoryMore || isLoadingHistoryInitial} 
                  onViewItem={handleViewHistoryItem}
                  onDeleteItem={handleDeleteHistoryItem}
                  onRefetchItem={handleRefetchHistoryItem}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </>
  );
}