"use client";

import React, { useMemo } from 'react'; // Import useMemo
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { InfoCircledIcon } from '@radix-ui/react-icons'; // Or any other suitable icon
import ExtractionStrategyConfigurator from './ExtractionStrategyConfigurator';
import DeepCrawlStrategyConfigurator from './DeepCrawlStrategyConfigurator';
import LlmModelSelect from '@/components/llm/LlmModelSelect'; // Import the dedicated LLM model select component
import LlmConfiguration from '@/components/llm/LlmConfiguration'; // <<< ADDED IMPORT

const AdvancedFetchOptions = ({
  fetchingEngine, // New prop
  targetSelectorAdvanced,
  setTargetSelectorAdvanced,
  excludedSelectors,
  setExcludedSelectors,
  browserEngine,
  setBrowserEngine,
  tokenBudget,
  setTokenBudget,
  viewportWidth,
  setViewportWidth,
  viewportHeight,
  setViewportHeight,
  markdownFlavor,
  setMarkdownFlavor,
  timeout,
  setTimeout,
  extractTextOnly,
  setExtractTextOnly,
  extractTables,
  setExtractTables,
  extractImages,
  setExtractImages,
  extractLinks,
  setExtractLinks,
  jsonResponse,
  setJsonResponse,
  cleanFormat,
  setCleanFormat,
  uploadToSupabase,
  setUploadToSupabase,
  imageCaptioning,
  setImageCaptioning,
  cacheTtl,
  setCacheTtl,
  browserLocale,
  setBrowserLocale,
  extractMetadata,
  setExtractMetadata,
  // crawl4ai specific props
  crawl4aiUserAgent,
  setCrawl4aiUserAgent,
  crawl4aiViewportWidth,
  setCrawl4aiViewportWidth,
  crawl4aiViewportHeight,
  setCrawl4aiViewportHeight,
  crawl4aiProxyUrl,
  setCrawl4aiProxyUrl,
  crawl4aiPageLoadWaitCondition,
  setCrawl4aiPageLoadWaitCondition,
  crawl4aiPageTimeout,
  setCrawl4aiPageTimeout,
  crawl4aiWaitForCondition,
  setCrawl4aiWaitForCondition,
  crawl4aiEnableJs,
  setCrawl4aiEnableJs,
  crawl4aiIgnoreHttpsErrors,
  setCrawl4aiIgnoreHttpsErrors,
  crawl4aiLightMode,
  setCrawl4aiLightMode,
  crawl4aiTextMode,
  setCrawl4aiTextMode,
  // New crawl4ai content extraction props
  crawl4aiTargetElements,
  setCrawl4aiTargetElements,
  crawl4aiExcludedElements,
  setCrawl4aiExcludedElements,
  crawl4aiExcludedTags,
  setCrawl4aiExcludedTags,
  crawl4aiExtractOnlyTextContent,
  setCrawl4aiExtractOnlyTextContent,
  crawl4aiProcessIframes,
  setCrawl4aiProcessIframes,
  crawl4aiWordCountThreshold,
  setCrawl4aiWordCountThreshold,
  crawl4aiRemoveForms,
  setCrawl4aiRemoveForms,
  crawl4aiKeepDataAttributes,
  setCrawl4aiKeepDataAttributes,
  // New crawl4ai page interaction props
  crawl4aiExecuteJsOnLoad,
  setCrawl4aiExecuteJsOnLoad,
  crawl4aiScanFullPage,
  setCrawl4aiScanFullPage,
  crawl4aiScrollDelay,
  setCrawl4aiScrollDelay,
  crawl4aiRemoveOverlayElements,
  setCrawl4aiRemoveOverlayElements,
  crawl4aiSimulateUserBehavior,
  setCrawl4aiSimulateUserBehavior,
  crawl4aiEnableMagic,
  setCrawl4aiEnableMagic,
  crawl4aiOverrideNavigator,
  setCrawl4aiOverrideNavigator,
  // New crawl4ai caching props
  crawl4aiCacheMode,
  setCrawl4aiCacheMode,
  // New crawl4ai media handling props
  crawl4aiCaptureScreenshot,
  setCrawl4aiCaptureScreenshot,
  crawl4aiGeneratePdf,
  setCrawl4aiGeneratePdf,
  crawl4aiCaptureMhtml,
  setCrawl4aiCaptureMhtml,
  crawl4aiExcludeExternalImages,
  setCrawl4aiExcludeExternalImages,
  crawl4aiImageAltTextMinWordCount,
  setCrawl4aiImageAltTextMinWordCount,
  crawl4aiImageRelevanceScoreThreshold,
  setCrawl4aiImageRelevanceScoreThreshold,
  // New crawl4ai link filtering props
  crawl4aiExcludeExternalLinks,
  setCrawl4aiExcludeExternalLinks,
  crawl4aiExcludeSocialMediaLinks,
  setCrawl4aiExcludeSocialMediaLinks,
  crawl4aiCustomExcludedDomains,
  setCrawl4aiCustomExcludedDomains,
  // New crawl4ai compliance props
  crawl4aiRespectRobotsTxt,
  setCrawl4aiRespectRobotsTxt,
  // New crawl4ai debugging props
  crawl4aiVerboseLogging,
  setCrawl4aiVerboseLogging,
  crawl4aiLogPageConsoleOutput,
  setCrawl4aiLogPageConsoleOutput,
  // New crawl4ai LLM config props
  crawl4aiMarkdownGenerator,
  setCrawl4aiMarkdownGenerator,
  // New crawl4ai Expert Options props
  crawl4aiBrowserCookies,
  setCrawl4aiBrowserCookies,
  crawl4aiBrowserHeaders,
  setCrawl4aiBrowserHeaders,
  crawl4aiBrowserUsePersistentContext,
  setCrawl4aiBrowserUsePersistentContext,
  crawl4aiCrawlSessionId,
  setCrawl4aiCrawlSessionId,
  crawl4aiCrawlCssSelector,
  setCrawl4aiCrawlCssSelector,
  // Strategy Configurator Props
  crawl4aiExtractionConfig,
  onCrawl4aiExtractionConfigChange,
  crawl4aiDeepCrawlConfig,
  onCrawl4aiDeepCrawlConfigChange,
  // Props for LlmConfiguration (passed down from page.js)
  llmProvider,
  setLlmProvider,
  llmApiToken,
  setLlmApiToken,
  llmBaseUrl,
  setLlmBaseUrl,
  availableLlmModels,
  isLoadingLlmModels,
}) => {
  console.log('[AdvancedFetchOptions] Rendering. Engine:', fetchingEngine);

  const accordionDefaultValues = useMemo(() => [
    "content-extraction", "formatting", "browser-performance",
    "crawl4ai-browser-nav", "crawl4ai-content-extraction", "crawl4ai-page-interaction",
    "crawl4ai-caching", "crawl4ai-media-handling", "crawl4ai-link-filtering",
    "crawl4ai-compliance", "crawl4ai-debugging", "crawl4ai-expert-options",
    "crawl4ai-llm-config", "crawl4ai-extraction-strategy", "crawl4ai-deep-crawl-strategy",
    "other-options"
  ], []);

  return (
    <TooltipProvider>
      <Accordion type="multiple" className="w-full space-y-2" defaultValue={accordionDefaultValues}>
        {/* Content Extraction Section */}
        <AccordionItem value="content-extraction">
          <AccordionTrigger>Content Extraction (General & Jina.ai)</AccordionTrigger>
          <AccordionContent className="space-y-4 p-2">
            {/* Common Options */}
            <div className="flex items-center space-x-2">
              <Switch
                id="extract-images"
                checked={extractImages}
                onCheckedChange={setExtractImages}
              />
              <Label htmlFor="extract-images">
                Extract Image URLs
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>If enabled, attempts to extract URLs of images found in the content.</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="image-captioning"
                checked={imageCaptioning}
                onCheckedChange={setImageCaptioning}
              />
              <Label htmlFor="image-captioning">
                Image Captioning
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>If enabled, attempts to generate captions for images (requires compatible model).</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
            </div>

            {/* Jina.ai Specific Options */}
            {fetchingEngine === 'jina' && (
              <>
                <div>
                  <Label htmlFor="target-selector-advanced">
                    Target CSS Selector (Advanced)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Specify a CSS selector for the main content area (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="target-selector-advanced"
                    placeholder="e.g., article#main-content, .post-body"
                    value={targetSelectorAdvanced}
                    onChange={(e) => setTargetSelectorAdvanced(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="excluded-selectors">
                    Excluded CSS Selectors (comma-separated)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Specify CSS selectors for elements to exclude from extraction (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="excluded-selectors"
                    placeholder="e.g., .ads, #sidebar"
                    value={excludedSelectors}
                    onChange={(e) => setExcludedSelectors(e.target.value)}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="extract-text-only"
                    checked={extractTextOnly}
                    onCheckedChange={setExtractTextOnly}
                  />
                  <Label htmlFor="extract-text-only">
                    Extract Text Only (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>If enabled, only textual content will be extracted, ignoring tables, images, etc. (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="extract-tables"
                    checked={extractTables}
                    onCheckedChange={setExtractTables}
                  />
                  <Label htmlFor="extract-tables">
                    Extract Tables (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>If enabled, attempts to preserve and extract table structures from the content (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="extract-links"
                    checked={extractLinks}
                    onCheckedChange={setExtractLinks}
                  />
                  <Label htmlFor="extract-links">
                    Extract Links (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>If enabled, extracts hyperlink URLs found within the content (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="extract-metadata"
                    checked={extractMetadata}
                    onCheckedChange={setExtractMetadata}
                  />
                  <Label htmlFor="extract-metadata">
                    Extract Page Metadata (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Extracts metadata like title, description, keywords, etc., from the page (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
              </>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* Formatting Section */}
        <AccordionItem value="formatting">
          <AccordionTrigger>Formatting</AccordionTrigger>
          <AccordionContent className="space-y-4 p-2">
            {/* Common Options */}
            <div>
              <Label htmlFor="markdown-flavor">
                Markdown Flavor
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Choose the Markdown syntax variant for the output.</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Select value={markdownFlavor} onValueChange={setMarkdownFlavor}>
                <SelectTrigger id="markdown-flavor">
                  <SelectValue placeholder="Select flavor" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="commonmark">CommonMark</SelectItem>
                  <SelectItem value="gfm">GitHub Flavored Markdown (GFM)</SelectItem>
                  <SelectItem value="markdown-extra">Markdown Extra</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="clean-format"
                checked={cleanFormat}
                onCheckedChange={setCleanFormat}
              />
              <Label htmlFor="clean-format">
                Clean Formatting
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Apply additional cleaning to the extracted Markdown (e.g., remove excessive newlines).</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
            </div>

            {/* Jina.ai Specific Options */}
            {fetchingEngine === 'jina' && (
              <>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="json-response"
                    checked={jsonResponse}
                    onCheckedChange={setJsonResponse}
                  />
                  <Label htmlFor="json-response">
                    Return JSON Response (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>If enabled, the API will return a JSON object containing the fetched data instead of raw Markdown (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
              </>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* Browser & Performance Section */}
        <AccordionItem value="browser-performance">
          <AccordionTrigger>Browser & Performance</AccordionTrigger>
          <AccordionContent className="space-y-4 p-2">
            {/* Common Options */}
            <div>
              <Label htmlFor="timeout">
                Timeout (seconds)
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Maximum time to wait for the page to load and content to be extracted.</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Input
                id="timeout"
                type="number"
                placeholder="e.g., 60"
                value={timeout}
                onChange={(e) => setTimeout(parseInt(e.target.value, 10) || 60)}
              />
            </div>

            {/* Jina.ai Specific Options */}
            {fetchingEngine === 'jina' && (
              <>
                <div>
                  <Label htmlFor="browser-engine">
                    Browser Engine (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Select the browser engine to use for fetching and rendering the page (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Select value={browserEngine} onValueChange={setBrowserEngine}>
                    <SelectTrigger id="browser-engine">
                      <SelectValue placeholder="Select engine" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="chromium">Chromium</SelectItem>
                      <SelectItem value="firefox">Firefox</SelectItem>
                      <SelectItem value="webkit">WebKit</SelectItem>
                      <SelectItem value="requests">Requests (HTTP only)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="token-budget">
                    Token Budget (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Approximate maximum number of tokens for the extracted content (influences truncation, Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="token-budget"
                    type="number"
                    placeholder="e.g., 4000"
                    value={tokenBudget}
                    onChange={(e) => setTokenBudget(parseInt(e.target.value, 10) || 0)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="viewport-width">Viewport Width (px, Jina.ai)</Label>
                    <Input
                      id="viewport-width"
                      type="number"
                      placeholder="e.g., 1920"
                      value={viewportWidth}
                      onChange={(e) => setViewportWidth(parseInt(e.target.value, 10) || 1920)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="viewport-height">Viewport Height (px, Jina.ai)</Label>
                    <Input
                      id="viewport-height"
                      type="number"
                      placeholder="e.g., 1080"
                      value={viewportHeight}
                      onChange={(e) => setViewportHeight(parseInt(e.target.value, 10) || 1080)}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="cache-ttl">
                    Cache TTL (seconds, Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Time-to-live for cached results. 0 to disable cache (Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="cache-ttl"
                    type="number"
                    placeholder="e.g., 3600"
                    value={cacheTtl}
                    onChange={(e) => setCacheTtl(parseInt(e.target.value, 10) || 0)}
                  />
                </div>
                <div>
                  <Label htmlFor="browser-locale">
                    Browser Locale (Jina.ai)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Set the browser's language/locale (e.g., en-US, fr-FR, Jina.ai specific).</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="browser-locale"
                    type="text"
                    placeholder="e.g., en-US"
                    value={browserLocale}
                    onChange={(e) => setBrowserLocale(e.target.value)}
                  />
                </div>
              </>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* crawl4ai Browser & Navigation Settings Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-browser-nav" key={`c4ai-browser-nav-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Browser & Navigation Settings</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div>
                <Label htmlFor="crawl4ai-user-agent">
                  User Agent
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Your custom or random user agent. `user_agent_mode="random"` can shuffle it. (Corresponds to `BrowserConfig.user_agent`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-user-agent"
                  placeholder="e.g., Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
                  value={crawl4aiUserAgent}
                  onChange={(e) => setCrawl4aiUserAgent(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-viewport-width">
                    Viewport Width (px)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Initial page width (in px). Useful for testing responsive layouts. (Corresponds to `BrowserConfig.viewport_width`)'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="crawl4ai-viewport-width"
                    type="number"
                    placeholder="e.g., 1920"
                    value={crawl4aiViewportWidth}
                    onChange={(e) => setCrawl4aiViewportWidth(parseInt(e.target.value, 10) || undefined)}
                  />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-viewport-height">
                    Viewport Height (px)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Initial page height (in px). (Corresponds to `BrowserConfig.viewport_height`)'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="crawl4ai-viewport-height"
                    type="number"
                    placeholder="e.g., 1080"
                    value={crawl4aiViewportHeight}
                    onChange={(e) => setCrawl4aiViewportHeight(parseInt(e.target.value, 10) || undefined)}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="crawl4ai-proxy-url">
                  Proxy URL
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Single-proxy URL if you want all traffic to go through it, e.g. "http://user:pass@proxy:8080". (Corresponds to `BrowserConfig.proxy`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-proxy-url"
                  placeholder="e.g., http://proxy.example.com:8080"
                  value={crawl4aiProxyUrl}
                  onChange={(e) => setCrawl4aiProxyUrl(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-page-load-wait">
                  Page Load Wait Condition
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Condition for navigation to "complete". Often "networkidle" or "domcontentloaded". (Corresponds to `CrawlerRunConfig.wait_until`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Select value={crawl4aiPageLoadWaitCondition} onValueChange={setCrawl4aiPageLoadWaitCondition}>
                  <SelectTrigger id="crawl4ai-page-load-wait">
                    <SelectValue placeholder="Select condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="domcontentloaded">domcontentloaded</SelectItem>
                    <SelectItem value="load">load</SelectItem>
                    <SelectItem value="networkidle">networkidle</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="crawl4ai-page-timeout">
                  Page Timeout (ms)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Timeout for page navigation or JS steps. Increase for slow sites. (Corresponds to `CrawlerRunConfig.page_timeout`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-page-timeout"
                  type="number"
                  placeholder="e.g., 30000"
                  value={crawl4aiPageTimeout}
                  onChange={(e) => setCrawl4aiPageTimeout(parseInt(e.target.value, 10) || undefined)}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-wait-for-condition">
                  Wait For Element/JS Condition
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Wait for a CSS (`"css:selector"`) or JS (`"js:() => bool"`) condition before content extraction. (Corresponds to `CrawlerRunConfig.wait_for`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-wait-for-condition"
                  placeholder="e.g., #myElement, () => document.querySelector('#el') !== null"
                  value={crawl4aiWaitForCondition}
                  onChange={(e) => setCrawl4aiWaitForCondition(e.target.value)}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-enable-js"
                  checked={crawl4aiEnableJs}
                  onCheckedChange={setCrawl4aiEnableJs}
                />
                <Label htmlFor="crawl4ai-enable-js">
                  Enable JavaScript
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Disable if you want no JS overhead, or if only static content is needed. (Corresponds to `BrowserConfig.java_script_enabled`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-ignore-https-errors"
                  checked={crawl4aiIgnoreHttpsErrors}
                  onCheckedChange={setCrawl4aiIgnoreHttpsErrors}
                />
                <Label htmlFor="crawl4ai-ignore-https-errors">
                  Ignore HTTPS Errors
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, continues despite invalid certificates (common in dev/staging). (Corresponds to `BrowserConfig.ignore_https_errors`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-light-mode"
                  checked={crawl4aiLightMode}
                  onCheckedChange={setCrawl4aiLightMode}
                />
                <Label htmlFor="crawl4ai-light-mode">
                  Light Mode (disable images/CSS)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Disables some background features for performance gains. (Corresponds to `BrowserConfig.light_mode`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-text-mode"
                  checked={crawl4aiTextMode}
                  onCheckedChange={setCrawl4aiTextMode}
                />
                <Label htmlFor="crawl4ai-text-mode">
                  Text Mode (focus on text extraction)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, tries to disable images/other heavy content for speed. (Corresponds to `BrowserConfig.text_mode`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Content Extraction & Processing Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-content-extraction" key={`c4ai-content-extraction-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Content Extraction & Processing</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div>
                <Label htmlFor="crawl4ai-target-elements">
                  Target Elements (CSS Selectors)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'List of CSS selectors for elements to focus on for markdown generation and data extraction, while still processing the entire page for links, media, etc. (Corresponds to `CrawlerRunConfig.target_elements`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-target-elements"
                  placeholder="e.g., article, .content-body, #primary-data"
                  value={crawl4aiTargetElements}
                  onChange={(e) => setCrawl4aiTargetElements(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-excluded-elements">
                  Excluded Elements (CSS Selector)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Like `css_selector` but to exclude. E.g. `"#ads, .tracker"`. (Corresponds to `CrawlerRunConfig.excluded_selector`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-excluded-elements"
                  placeholder="e.g., .ads, nav, footer"
                  value={crawl4aiExcludedElements}
                  onChange={(e) => setCrawl4aiExcludedElements(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-excluded-tags">
                  Excluded Tags (comma-separated)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Removes entire tags (e.g. `["script", "style"]`). (Corresponds to `CrawlerRunConfig.excluded_tags`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-excluded-tags"
                  placeholder="e.g., script, style, iframe"
                  value={crawl4aiExcludedTags}
                  onChange={(e) => setCrawl4aiExcludedTags(e.target.value)}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-extract-only-text"
                  checked={crawl4aiExtractOnlyTextContent}
                  onCheckedChange={setCrawl4aiExtractOnlyTextContent}
                />
                <Label htmlFor="crawl4ai-extract-only-text">
                  Extract Only Text Content
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, tries to extract text-only content. (Corresponds to `CrawlerRunConfig.only_text`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-process-iframes"
                  checked={crawl4aiProcessIframes}
                  onCheckedChange={setCrawl4aiProcessIframes}
                />
                <Label htmlFor="crawl4ai-process-iframes">
                  Process iFrames Content
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Inlines iframe content for single-page extraction. (Corresponds to `CrawlerRunConfig.process_iframes`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div>
                <Label htmlFor="crawl4ai-word-count-threshold">
                  Word Count Threshold (Content Significance)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Skips text blocks below X words. Helps ignore trivial sections. (Corresponds to `CrawlerRunConfig.word_count_threshold`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-word-count-threshold"
                  type="number"
                  placeholder="e.g., 50"
                  value={crawl4aiWordCountThreshold}
                  onChange={(e) => setCrawl4aiWordCountThreshold(parseInt(e.target.value, 10) || undefined)}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-remove-forms"
                  checked={crawl4aiRemoveForms}
                  onCheckedChange={setCrawl4aiRemoveForms}
                />
                <Label htmlFor="crawl4ai-remove-forms">
                  Remove Forms
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, remove all `<form>` elements. (Corresponds to `CrawlerRunConfig.remove_forms`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-keep-data-attributes"
                  checked={crawl4aiKeepDataAttributes}
                  onCheckedChange={setCrawl4aiKeepDataAttributes}
                />
                <Label htmlFor="crawl4ai-keep-data-attributes">
                  Keep Data Attributes
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, preserve `data-*` attributes in cleaned HTML. (Corresponds to `CrawlerRunConfig.keep_data_attributes`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>
              <div>
                <Label htmlFor="crawl4ai-markdown-generator">
                  Markdown Generator
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If you want specialized markdown output (citations, filtering, chunking, etc.). Can be customized with options such as `content_source` parameter to select the HTML input source (\'cleaned_html\', \'raw_html\', or \'fit_html\'). (Corresponds to `CrawlerRunConfig.markdown_generator`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Select value={crawl4aiMarkdownGenerator} onValueChange={setCrawl4aiMarkdownGenerator}>
                  <SelectTrigger id="crawl4ai-markdown-generator">
                    <SelectValue placeholder="Select generator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Default">Default (cleaned_html)</SelectItem>
                    <SelectItem value="Raw HTML">Raw HTML</SelectItem>
                    <SelectItem value="Fit HTML">Fit HTML</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Page Interaction & Automation Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-page-interaction" key={`c4ai-page-interaction-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Page Interaction & Automation</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div>
                <Label htmlFor="crawl4ai-execute-js-on-load">
                  Execute JavaScript on Page Load
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'JavaScript to run after load. E.g. `"document.querySelector(\'button\')?.click();"`. (Corresponds to `CrawlerRunConfig.js_code`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Textarea
                  id="crawl4ai-execute-js-on-load"
                  placeholder="e.g., document.querySelector('#accept-cookies').click();"
                  value={crawl4aiExecuteJsOnLoad}
                  onChange={(e) => setCrawl4aiExecuteJsOnLoad(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-scan-full-page"
                  checked={crawl4aiScanFullPage}
                  onCheckedChange={setCrawl4aiScanFullPage}
                />
                <Label htmlFor="crawl4ai-scan-full-page">
                  Scan Full Page (Auto-scroll for dynamic content)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, auto-scroll the page to load dynamic content (infinite scroll). (Corresponds to `CrawlerRunConfig.scan_full_page`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              {crawl4aiScanFullPage && (
                <div>
                  <Label htmlFor="crawl4ai-scroll-delay">
                    Scroll Delay (seconds)
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Delay between scroll steps if "Scan Full Page" is enabled. (Corresponds to `CrawlerRunConfig.scroll_delay`)'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="crawl4ai-scroll-delay"
                    type="number"
                    placeholder="e.g., 2"
                    value={crawl4aiScrollDelay}
                    onChange={(e) => setCrawl4aiScrollDelay(parseFloat(e.target.value) || undefined)}
                    min="0"
                    step="0.1"
                  />
                </div>
              )}

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-remove-overlay-elements"
                  checked={crawl4aiRemoveOverlayElements}
                  onCheckedChange={setCrawl4aiRemoveOverlayElements}
                />
                <Label htmlFor="crawl4ai-remove-overlay-elements">
                  Attempt to Remove Overlay Elements
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Removes potential modals/popups blocking the main content. (Corresponds to `CrawlerRunConfig.remove_overlay_elements`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-simulate-user-behavior"
                  checked={crawl4aiSimulateUserBehavior}
                  onCheckedChange={setCrawl4aiSimulateUserBehavior}
                />
                <Label htmlFor="crawl4ai-simulate-user-behavior">
                  Simulate User Behavior (Mouse movements)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Simulate user interactions (mouse movements) to avoid bot detection. (Corresponds to `CrawlerRunConfig.simulate_user`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-enable-magic"
                  checked={crawl4aiEnableMagic}
                  onCheckedChange={setCrawl4aiEnableMagic}
                />
                <Label htmlFor="crawl4ai-enable-magic">
                  Enable "Magic" (Experimental popup/banner handling)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Automatic handling of popups/consent banners. Experimental. (Corresponds to `CrawlerRunConfig.magic`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-override-navigator"
                  checked={crawl4aiOverrideNavigator}
                  onCheckedChange={setCrawl4aiOverrideNavigator}
                />
                <Label htmlFor="crawl4ai-override-navigator">
                  Override Navigator Properties (Stealth)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Override `navigator` properties in JS for stealth. (Corresponds to `CrawlerRunConfig.override_navigator`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Caching Settings Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-caching" key={`c4ai-caching-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Caching Settings</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div>
                <Label htmlFor="crawl4ai-cache-mode">
                  Cache Mode
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Controls how caching is handled (`ENABLED`, `BYPASS`, `DISABLED`, etc.). If `None`, typically defaults to `ENABLED`. (Corresponds to `CrawlerRunConfig.cache_mode`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Select value={crawl4aiCacheMode} onValueChange={setCrawl4aiCacheMode}>
                  <SelectTrigger id="crawl4ai-cache-mode">
                    <SelectValue placeholder="Select cache mode" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="enabled">Enabled</SelectItem>
                    <SelectItem value="bypass">Bypass</SelectItem>
                    <SelectItem value="write_only">Write Only</SelectItem>
                    <SelectItem value="read_only">Read Only</SelectItem>
                    <SelectItem value="disabled">Disabled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Media Handling Settings Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-media-handling" key={`c4ai-media-handling-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Media Handling Settings</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-capture-screenshot"
                  checked={crawl4aiCaptureScreenshot}
                  onCheckedChange={setCrawl4aiCaptureScreenshot}
                />
                <Label htmlFor="crawl4ai-capture-screenshot">
                  Capture Screenshot (Base64)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Capture a screenshot (base64) in `result.screenshot`. (Corresponds to `CrawlerRunConfig.screenshot`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-generate-pdf"
                  checked={crawl4aiGeneratePdf}
                  onCheckedChange={setCrawl4aiGeneratePdf}
                />
                <Label htmlFor="crawl4ai-generate-pdf">
                  Generate PDF of Page
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, returns a PDF in `result.pdf`. (Corresponds to `CrawlerRunConfig.pdf`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-capture-mhtml"
                  checked={crawl4aiCaptureMhtml}
                  onCheckedChange={setCrawl4aiCaptureMhtml}
                />
                <Label htmlFor="crawl4ai-capture-mhtml">
                  Capture MHTML Snapshot
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, captures an MHTML snapshot of the page in `result.mhtml`. MHTML includes all page resources (CSS, images, etc.) in a single file. (Corresponds to `CrawlerRunConfig.capture_mhtml`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-exclude-external-images"
                  checked={crawl4aiExcludeExternalImages}
                  onCheckedChange={setCrawl4aiExcludeExternalImages}
                />
                <Label htmlFor="crawl4ai-exclude-external-images">
                  Exclude External Images
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Exclude images from other domains. (Corresponds to `CrawlerRunConfig.exclude_external_images`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div>
                <Label htmlFor="crawl4ai-image-alt-min-word">
                  Image Alt Text Min Word Count
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>
                        {'Minimum words for an image\'s alt text or description to be considered valid. (Corresponds to `CrawlerRunConfig.image_description_min_word_threshold`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-image-alt-min-word"
                  type="number"
                  placeholder="e.g., 3"
                  value={crawl4aiImageAltTextMinWordCount}
                  onChange={(e) => setCrawl4aiImageAltTextMinWordCount(parseInt(e.target.value, 10) || 0)}
                  min="0"
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-image-relevance-score">
                  Image Relevance Score Threshold
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Filter out low-scoring images. The crawler scores images by relevance (size, context, etc.). (Corresponds to `CrawlerRunConfig.image_score_threshold`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-image-relevance-score"
                  type="number"
                  placeholder="e.g., 0.5"
                  value={crawl4aiImageRelevanceScoreThreshold}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value);
                    setCrawl4aiImageRelevanceScoreThreshold(isNaN(val) ? 0 : Math.max(0, Math.min(1, val)));
                  }}
                  min="0"
                  max="1"
                  step="0.01"
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Link & Domain Filtering Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-link-filtering" key={`c4ai-link-filtering-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Link & Domain Filtering</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-exclude-external-links"
                  checked={crawl4aiExcludeExternalLinks}
                  onCheckedChange={setCrawl4aiExcludeExternalLinks}
                />
                <Label htmlFor="crawl4ai-exclude-external-links">
                  Exclude External Links
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Removes all links pointing outside the current domain. (Corresponds to `CrawlerRunConfig.exclude_external_links`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-exclude-social-media-links"
                  checked={crawl4aiExcludeSocialMediaLinks}
                  onCheckedChange={setCrawl4aiExcludeSocialMediaLinks}
                />
                <Label htmlFor="crawl4ai-exclude-social-media-links">
                  Exclude Social Media Links
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Strips links specifically to social sites (like Facebook or Twitter). (Corresponds to `CrawlerRunConfig.exclude_social_media_links`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div>
                <Label htmlFor="crawl4ai-custom-excluded-domains">
                  Custom Excluded Domains (comma-separated)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Provide a custom list of domains to exclude (like `["ads.com", "trackers.io"]`). (Corresponds to `CrawlerRunConfig.exclude_domains`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Textarea
                  id="crawl4ai-custom-excluded-domains"
                  placeholder="e.g., domain1.com, domain2.net"
                  value={crawl4aiCustomExcludedDomains}
                  onChange={(e) => setCrawl4aiCustomExcludedDomains(e.target.value)}
                  rows={3}
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Compliance Settings Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-compliance" key={`c4ai-compliance-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Compliance Settings</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-respect-robots-txt"
                  checked={crawl4aiRespectRobotsTxt}
                  onCheckedChange={setCrawl4aiRespectRobotsTxt}
                />
                <Label htmlFor="crawl4ai-respect-robots-txt">
                  Respect robots.txt Rules
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'When True, checks and respects robots.txt rules before crawling. Uses efficient caching with SQLite backend. (Corresponds to `CrawlerRunConfig.check_robots_txt`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Debugging & Logging Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-debugging" key={`c4ai-debugging-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Debugging & Logging</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-verbose-logging"
                  checked={crawl4aiVerboseLogging}
                  onCheckedChange={setCrawl4aiVerboseLogging}
                />
                <Label htmlFor="crawl4ai-verbose-logging">
                  Verbose Logging
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Prints logs detailing each step of crawling, interactions, or errors. (Corresponds to `CrawlerRunConfig.verbose`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-log-page-console-output"
                  checked={crawl4aiLogPageConsoleOutput}
                  onCheckedChange={setCrawl4aiLogPageConsoleOutput}
                />
                <Label htmlFor="crawl4ai-log-page-console-output">
                  Log Page Console Output
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Logs the page\'s JavaScript console output if you want deeper JS debugging. (Corresponds to `CrawlerRunConfig.log_console`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Expert Options Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-expert-options" key={`c4ai-expert-options-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - Expert Options</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              {/* BrowserConfig Expert Options */}
              <div>
                <Label htmlFor="crawl4ai-browser-cookies">
                  Browser Cookies (JSON)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Pre-set cookies, each a dict like `{"name": "session", "value": "...", "url": "..."}`. (Corresponds to `BrowserConfig.cookies`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Textarea
                  id="crawl4ai-browser-cookies"
                  placeholder='e.g., [{"name": "session", "value": "abc123"}]'
                  value={crawl4aiBrowserCookies}
                  onChange={(e) => setCrawl4aiBrowserCookies(e.target.value)}
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-browser-headers">
                  Browser Headers (JSON)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Extra HTTP headers for every request, e.g. `{"Accept-Language": "en-US"}`. (Corresponds to `BrowserConfig.headers`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Textarea
                  id="crawl4ai-browser-headers"
                  placeholder='e.g., {"Authorization": "Bearer token"}'
                  value={crawl4aiBrowserHeaders}
                  onChange={(e) => setCrawl4aiBrowserHeaders(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="crawl4ai-browser-persistent-context"
                  checked={crawl4aiBrowserUsePersistentContext}
                  onCheckedChange={setCrawl4aiBrowserUsePersistentContext}
                />
                <Label htmlFor="crawl4ai-browser-persistent-context">
                  Use Persistent Browser Context
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'If `True`, uses a **persistent** browser context (keep cookies, sessions across runs). Also sets `use_managed_browser=True`. (Corresponds to `BrowserConfig.use_persistent_context`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
              </div>

              {/* CrawlerRunConfig Expert Options */}
              <div>
                <Label htmlFor="crawl4ai-crawl-session-id">
                  Crawl Session ID
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Assign a unique ID to reuse a single browser session across multiple `arun()` calls. (Corresponds to `CrawlerRunConfig.session_id`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-crawl-session-id"
                  placeholder="e.g., my-custom-session-123"
                  value={crawl4aiCrawlSessionId}
                  onChange={(e) => setCrawl4aiCrawlSessionId(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="crawl4ai-crawl-css-selector">
                  Global CSS Selector (Expert)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Retains only the part of the page matching this selector. Affects the entire extraction process. (Corresponds to `CrawlerRunConfig.css_selector`)'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Input
                  id="crawl4ai-crawl-css-selector"
                  placeholder="e.g., body"
                  value={crawl4aiCrawlCssSelector}
                  onChange={(e) => setCrawl4aiCrawlCssSelector(e.target.value)}
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai LLM Configuration Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-llm-config" key={`c4ai-llm-config-${fetchingEngine}`}>
            <AccordionTrigger>crawl4ai - LLM Configuration</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <LlmConfiguration
                llmProvider={llmProvider}
                setLlmProvider={setLlmProvider}
                llmApiToken={llmApiToken}
                setLlmApiToken={setLlmApiToken}
                llmBaseUrl={llmBaseUrl}
                setLlmBaseUrl={setLlmBaseUrl}
                availableLlmModels={availableLlmModels}
                isLoadingLlmModels={isLoadingLlmModels}
                showCrawl4aiMarkdownGenerator={false}
              />

              <div>
                <Label htmlFor="crawl4ai-markdown-generator">Markdown Generator</Label>
                <Select
                  id="crawl4ai-markdown-generator"
                  value={crawl4aiMarkdownGenerator}
                  onValueChange={setCrawl4aiMarkdownGenerator}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Markdown Generator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Default">Default (cleaned_html)</SelectItem>
                    <SelectItem value="Raw HTML">Raw HTML</SelectItem>
                    <SelectItem value="Fit HTML">Fit HTML</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Extraction Strategy Configurator Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-extraction-strategy" key="c4ai-extraction-strategy">
            <AccordionTrigger>crawl4ai - Extraction Strategy</AccordionTrigger>
            <AccordionContent className="p-2">
              <ExtractionStrategyConfigurator
                initialConfig={crawl4aiExtractionConfig}
                onConfigChange={onCrawl4aiExtractionConfigChange}
              />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* crawl4ai Deep Crawl Strategy Configurator Section */}
        {fetchingEngine === 'crawl4ai' && (
          <AccordionItem value="crawl4ai-deep-crawl-strategy" key="c4ai-deep-crawl-strategy">
            <AccordionTrigger>crawl4ai - Deep Crawl Strategy</AccordionTrigger>
            <AccordionContent className="p-2">
              <DeepCrawlStrategyConfigurator
                initialConfig={crawl4aiDeepCrawlConfig}
                onConfigChange={onCrawl4aiDeepCrawlConfigChange}
              />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Other Options Section (Common) */}
        <AccordionItem value="other-options">
          <AccordionTrigger>Other Options</AccordionTrigger>
          <AccordionContent className="space-y-4 p-2">
            <div className="flex items-center space-x-2">
              <Switch
                id="upload-to-supabase"
                checked={uploadToSupabase}
                onCheckedChange={setUploadToSupabase}
              />
              <Label htmlFor="upload-to-supabase">
                Upload to Supabase
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>If enabled, the fetched content and metadata will be uploaded to Supabase.</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </TooltipProvider>
  );
};

export default React.memo(AdvancedFetchOptions);
