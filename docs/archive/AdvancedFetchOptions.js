import React from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// import Crawl4aiStrategyConfig from './Crawl4aiStrategyConfig'; // This was commented out, keep as is or remove fully
import ExtractionStrategyConfigurator from './ExtractionStrategyConfigurator'; // Re-add import
import DeepCrawlStrategyConfigurator from './DeepCrawlStrategyConfigurator'; // Re-add import
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Ensure all props are destructured, including the new LLM ones
export default function AdvancedFetchOptions({
  fetchingEngine,
  targetSelectorAdvanced, setTargetSelectorAdvanced,
  excludedSelectors, setExcludedSelectors,
  browserEngine, setBrowserEngine,
  tokenBudget, setTokenBudget,
  viewportWidth, setViewportWidth,
  viewportHeight, setViewportHeight,
  markdownFlavor, setMarkdownFlavor,
  timeout, setTimeout,
  extractTextOnly, setExtractTextOnly,
  extractTables, setExtractTables,
  extractImages, setExtractImages,
  extractLinks, setExtractLinks,
  jsonResponse, setJsonResponse,
  cleanFormat, setCleanFormat,
  uploadToSupabase, setUploadToSupabase,
  imageCaptioning, setImageCaptioning,
  cacheTtl, setCacheTtl,
  browserLocale, setBrowserLocale,
  extractMetadata, setExtractMetadata,
  crawl4aiUserAgent, setCrawl4aiUserAgent,
  crawl4aiViewportWidth, setCrawl4aiViewportWidth,
  crawl4aiViewportHeight, setCrawl4aiViewportHeight,
  crawl4aiProxyUrl, setCrawl4aiProxyUrl,
  crawl4aiPageLoadWaitCondition, setCrawl4aiPageLoadWaitCondition,
  crawl4aiPageTimeout, setCrawl4aiPageTimeout,
  crawl4aiWaitForCondition, setCrawl4aiWaitForCondition,
  crawl4aiEnableJs, setCrawl4aiEnableJs,
  crawl4aiIgnoreHttpsErrors, setCrawl4aiIgnoreHttpsErrors,
  crawl4aiLightMode, setCrawl4aiLightMode,
  crawl4aiTextMode, setCrawl4aiTextMode,
  crawl4aiTargetElements, setCrawl4aiTargetElements,
  crawl4aiExcludedElements, setCrawl4aiExcludedElements,
  crawl4aiExcludedTags, setCrawl4aiExcludedTags,
  crawl4aiExtractOnlyTextContent, setCrawl4aiExtractOnlyTextContent,
  crawl4aiProcessIframes, setCrawl4aiProcessIframes,
  crawl4aiWordCountThreshold, setCrawl4aiWordCountThreshold,
  crawl4aiRemoveForms, setCrawl4aiRemoveForms,
  crawl4aiKeepDataAttributes, setCrawl4aiKeepDataAttributes,
  crawl4aiExecuteJsOnLoad, setCrawl4aiExecuteJsOnLoad,
  crawl4aiScanFullPage, setCrawl4aiScanFullPage,
  crawl4aiScrollDelay, setCrawl4aiScrollDelay,
  crawl4aiRemoveOverlayElements, setCrawl4aiRemoveOverlayElements,
  crawl4aiSimulateUserBehavior, setCrawl4aiSimulateUserBehavior,
  crawl4aiEnableMagic, setCrawl4aiEnableMagic,
  crawl4aiOverrideNavigator, setCrawl4aiOverrideNavigator,
  crawl4aiCacheMode, setCrawl4aiCacheMode,
  crawl4aiCaptureScreenshot, setCrawl4aiCaptureScreenshot,
  crawl4aiGeneratePdf, setCrawl4aiGeneratePdf,
  crawl4aiCaptureMhtml, setCrawl4aiCaptureMhtml,
  crawl4aiExcludeExternalImages, setCrawl4aiExcludeExternalImages,
  crawl4aiImageAltTextMinWordCount, setCrawl4aiImageAltTextMinWordCount,
  crawl4aiImageRelevanceScoreThreshold, setCrawl4aiImageRelevanceScoreThreshold,
  crawl4aiExcludeExternalLinks, setCrawl4aiExcludeExternalLinks,
  crawl4aiExcludeSocialMediaLinks, setCrawl4aiExcludeSocialMediaLinks,
  crawl4aiCustomExcludedDomains, setCrawl4aiCustomExcludedDomains,
  crawl4aiRespectRobotsTxt, setCrawl4aiRespectRobotsTxt,
  crawl4aiVerboseLogging, setCrawl4aiVerboseLogging,
  crawl4aiLogPageConsoleOutput, setCrawl4aiLogPageConsoleOutput,
  // Generic LLM props
  llmProvider, setLlmProvider,
  llmApiToken, setLlmApiToken,
  llmBaseUrl, setLlmBaseUrl,
  availableModels,
  // Crawl4AI specific LLM related prop
  crawl4aiMarkdownGenerator, setCrawl4aiMarkdownGenerator,
  // Expert Options
  crawl4aiBrowserCookies, setCrawl4aiBrowserCookies,
  crawl4aiBrowserHeaders, setCrawl4aiBrowserHeaders,
  crawl4aiBrowserUsePersistentContext, setCrawl4aiBrowserUsePersistentContext,
  crawl4aiCrawlSessionId, setCrawl4aiCrawlSessionId,
  crawl4aiCrawlCssSelector, setCrawl4aiCrawlCssSelector,
  // Strategy Configs
  crawl4aiExtractionConfig, onCrawl4aiExtractionConfigChange,
  crawl4aiDeepCrawlConfig, onCrawl4aiDeepCrawlConfigChange,
  // New props for LLM models
  availableLlmModels,
  isLoadingLlmModels,
  // crawl4ai expert props
  crawl4aiTargetElement,
  setCrawl4aiTargetElement,
  crawl4aiMaxDepth,
  setCrawl4aiMaxDepth,
  crawl4aiMaxPages,
  setCrawl4aiMaxPages,
  crawl4aiIncludeDomains,
  setCrawl4aiIncludeDomains,
  crawl4aiExcludeDomains,
  setCrawl4aiExcludeDomains,
  crawl4aiConcurrency,
  setCrawl4aiConcurrency,
  crawl4aiMaxRetries,
  setCrawl4aiMaxRetries,
  crawl4aiPageLoadTimeout,
  setCrawl4aiPageLoadTimeout,
  crawl4aiPuppeteerHeadless,
  setCrawl4aiPuppeteerHeadless,
  crawl4aiRandomUserAgent,
  setCrawl4aiRandomUserAgent,
  crawl4aiStealthMode,
  setCrawl4aiStealthMode,
  crawl4aiExtractVisibleTextOnly,
  setCrawl4aiExtractVisibleTextOnly,
  crawl4aiLlmProvider,
  setCrawl4aiLlmProvider,
  crawl4aiLlmProviderModel,
  setCrawl4aiLlmProviderModel,
  crawl4aiLlmApiToken,
  setCrawl4aiLlmApiToken,
  crawl4aiLlmBaseUrl,
  setCrawl4aiLlmBaseUrl,
  crawl4aiUseFileSaver,
  setCrawl4aiUseFileSaver,
  crawl4aiOutputDirectory,
  setCrawl4aiOutputDirectory,
  crawl4aiSaveScreenshots,
  setCrawl4aiSaveScreenshots,
  crawl4aiScreenshotDirectory,
  setCrawl4aiScreenshotDirectory,
  crawl4aiSaveRawHtml,
  setCrawl4aiSaveRawHtml,
  crawl4aiRawHtmlDirectory,
  setCrawl4aiRawHtmlDirectory,
  crawl4aiSavePdfs,
  setCrawl4aiSavePdfs,
  crawl4aiPdfDirectory,
  setCrawl4aiPdfDirectory,
  crawl4aiSaveMhtml,
  setCrawl4aiSaveMhtml,
  crawl4aiMhtmlDirectory,
  setCrawl4aiMhtmlDirectory,
  crawl4aiLogHttpRequests,
  setCrawl4aiLogHttpRequests,
  crawl4aiHttpRequestsLogFile,
  setCrawl4aiHttpRequestsLogFile,
  crawl4aiLogCacheHits,
  setCrawl4aiLogCacheHits,
  crawl4aiCacheHitsLogFile,
  setCrawl4aiCacheHitsLogFile,
  crawl4aiSkipSslVerification,
  setCrawl4aiSkipSslVerification,
  crawl4aiAdditionalPuppeteerLaunchArgs,
  setCrawl4aiAdditionalPuppeteerLaunchArgs,
  crawl4aiCrawlerType,
  setCrawl4aiCrawlerType,
  crawl4aiPlaywrightEngine,
  setCrawl4aiPlaywrightEngine,
  crawl4aiPlaywrightBrowserType,
  setCrawl4aiPlaywrightBrowserType,
  crawl4aiPlaywrightStealth,
  setCrawl4aiPlaywrightStealth,
  crawl4aiPageContentSelectors,
  setCrawl4aiPageContentSelectors,
  crawl4aiSkipUrlRegex,
  setCrawl4aiSkipUrlRegex,
  crawl4aiMustMatchUrlRegex,
  setCrawl4aiMustMatchUrlRegex,
  crawl4aiUrlQueueMaxSize,
  setCrawl4aiUrlQueueMaxSize,
  crawl4aiRateLimitRequestsPerSecond,
  setCrawl4aiRateLimitRequestsPerSecond,
  crawl4aiHttpTimeout,
  setCrawl4aiHttpTimeout,
  crawl4aiAcceptedHttpStatusCodes,
  setCrawl4aiAcceptedHttpStatusCodes,
  crawl4aiMaxFileSize,
  setCrawl4aiMaxFileSize,
  crawl4aiMaxResponseSize,
  setCrawl4aiMaxResponseSize,
  crawl4aiOutputFormat,
  setCrawl4aiOutputFormat,
  crawl4aiGcsBucketName,
  setCrawl4aiGcsBucketName,
  crawl4aiGcsProjectId,
  setCrawl4aiGcsProjectId,
  crawl4aiS3BucketName,
  setCrawl4aiS3BucketName,
  crawl4aiS3Region,
  setCrawl4aiS3Region,
  crawl4aiS3AccessKeyId,
  setCrawl4aiS3AccessKeyId,
  crawl4aiS3SecretAccessKey,
  setCrawl4aiS3SecretAccessKey,
  crawl4aiAzureStorageAccountName,
  setCrawl4aiAzureStorageAccountName,
  crawl4aiAzureStorageAccountKey,
  setCrawl4aiAzureStorageAccountKey,
  crawl4aiAzureContainerName,
  setCrawl4aiAzureContainerName,
  crawl4aiUseGoogleScraper,
  setCrawl4aiUseGoogleScraper,
  crawl4aiGoogleScraperApiKey,
  setCrawl4aiGoogleScraperApiKey,
  crawl4aiGoogleScraperNumResults,
  setCrawl4aiGoogleScraperNumResults,
  crawl4aiGoogleScraperCountryCode,
  setCrawl4aiGoogleScraperCountryCode,
  crawl4aiGoogleScraperLanguageCode,
  setCrawl4aiGoogleScraperLanguageCode,
  crawl4aiUseSerpApi,
  setCrawl4aiUseSerpApi,
  crawl4aiSerpApiKey,
  setCrawl4aiSerpApiKey,
  crawl4aiSerpApiNumResults,
  setCrawl4aiSerpApiNumResults,
  crawl4aiSerpApiCountryCode,
  setCrawl4aiSerpApiCountryCode,
  crawl4aiSerpApiLanguageCode,
  setCrawl4aiSerpApiLanguageCode,
  crawl4aiUseApifyScraper,
  setCrawl4aiUseApifyScraper,
  crawl4aiApifyApiKey,
  setCrawl4aiApifyApiKey,
  crawl4aiApifyActorId,
  setCrawl4aiApifyActorId,
  crawl4aiEnableJavascript,
  setCrawl4aiEnableJavascript,
  crawl4aiEnableCss,
  setCrawl4aiEnableCss,
  crawl4aiEnableImages,
  setCrawl4aiEnableImages,
  crawl4aiEnableMedia,
  setCrawl4aiEnableMedia,
  crawl4aiEnableStylesheets,
  setCrawl4aiEnableStylesheets,
  crawl4aiEnableFonts,
  setCrawl4aiEnableFonts,
  crawl4aiEnableXhr,
  setCrawl4aiEnableXhr,
  crawl4aiEnableFrames,
  setCrawl4aiEnableFrames,
  crawl4aiEnableWebSockets,
  setCrawl4aiEnableWebSockets,
  crawl4aiRequestHeaders,
  setCrawl4aiRequestHeaders,
  crawl4aiUseSessionCookies,
  setCrawl4aiUseSessionCookies,
  crawl4aiPuppeteerUserDataDir,
  setCrawl4aiPuppeteerUserDataDir,
  crawl4aiPuppeteerViewportWidth,
  setCrawl4aiPuppeteerViewportWidth,
  crawl4aiPuppeteerViewportHeight,
  setCrawl4aiPuppeteerViewportHeight,
  crawl4aiPuppeteerDeviceScaleFactor,
  setCrawl4aiPuppeteerDeviceScaleFactor,
  crawl4aiPuppeteerIsMobile,
  setCrawl4aiPuppeteerIsMobile,
  crawl4aiPuppeteerHasTouch,
  setCrawl4aiPuppeteerHasTouch,
  crawl4aiPuppeteerIsLandscape,
  setCrawl4aiPuppeteerIsLandscape,
  crawl4aiBrowserDownloadPath,
  setCrawl4aiBrowserDownloadPath,
  crawl4aiCustomBrowserPath,
  setCrawl4aiCustomBrowserPath,
  crawl4aiExtractMetadata,
  setCrawl4aiExtractMetadata,
  crawl4aiExtractSocialMediaTags,
  setCrawl4aiExtractSocialMediaTags,
  crawl4aiExtractStructuredData,
  setCrawl4aiExtractStructuredData,
  crawl4aiExtractHyperlinks,
  setCrawl4aiExtractHyperlinks,
  crawl4aiHyperlinkFormat,
  setCrawl4aiHyperlinkFormat,
  crawl4aiExtractImageUrls,
  setCrawl4aiExtractImageUrls,
  crawl4aiImageUrlFormat,
  setCrawl4aiImageUrlFormat,
  crawl4aiExtractVideoUrls,
  setCrawl4aiExtractVideoUrls,
  crawl4aiVideoUrlFormat,
  setCrawl4aiVideoUrlFormat,
  crawl4aiExtractAudioUrls,
  setCrawl4aiExtractAudioUrls,
  crawl4aiAudioUrlFormat,
  setCrawl4aiAudioUrlFormat,
  crawl4aiExtractFileUrls,
  setCrawl4aiExtractFileUrls,
  crawl4aiFileUrlFormat,
  setCrawl4aiFileUrlFormat,
  crawl4aiExtractEmbeddedContent,
  setCrawl4aiExtractEmbeddedContent,
  crawl4aiMaxContentLength,
  setCrawl4aiMaxContentLength,
  crawl4aiNormalizeWhitespace,
  setCrawl4aiNormalizeWhitespace,
  crawl4aiRemoveDuplicateContent,
  setCrawl4aiRemoveDuplicateContent,
  crawl4aiTextProcessingPipeline,
  setCrawl4aiTextProcessingPipeline,
  crawl4aiContentChunkingStrategy,
  setCrawl4aiContentChunkingStrategy,
  crawl4aiContentChunkSize,
  setCrawl4aiContentChunkSize,
  crawl4aiContentChunkOverlap,
  setCrawl4aiContentChunkOverlap,
  crawl4aiAutoRotateImages,
  setCrawl4aiAutoRotateImages,
  crawl4aiImagePreprocessingPipeline,
  setCrawl4aiImagePreprocessingPipeline,
  crawl4aiOcrEnabled,
  setCrawl4aiOcrEnabled,
  crawl4aiOcrLanguages,
  setCrawl4aiOcrLanguages,
  crawl4aiPdfTextExtractionMethod,
  setCrawl4aiPdfTextExtractionMethod,
  crawl4aiTableExtractionMethod,
  setCrawl4aiTableExtractionMethod,
  crawl4aiAutoDetectTables,
  setCrawl4aiAutoDetectTables,
  crawl4aiTableOutputFormat,
  setCrawl4aiTableOutputFormat,
  crawl4aiCustomProcessingScript,
  setCrawl4aiCustomProcessingScript,
  crawl4aiNotificationWebhookUrl,
  setCrawl4aiNotificationWebhookUrl,
  crawl4aiNotificationEmail,
  setCrawl4aiNotificationEmail,
  crawl4aiRunInBackground,
  setCrawl4aiRunInBackground,
  crawl4aiJobTags,
  setCrawl4aiJobTags,
}) {
  return (
    <Accordion type="multiple" className="w-full mt-4 space-y-4">
      {fetchingEngine === 'jina' && (
        <AccordionItem value="jina-options">
          <AccordionTrigger>Jina Specific Options</AccordionTrigger>
          <AccordionContent className="space-y-4 p-4">
            {/* Jina specific options from original formState */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="target-selector-advanced">Target Selector (Advanced)</Label>
                <Input id="target-selector-advanced" value={targetSelectorAdvanced} onChange={(e) => setTargetSelectorAdvanced(e.target.value)} placeholder="e.g., #main-content, .article-body" />
              </div>
              <div>
                <Label htmlFor="excluded-selectors">Excluded CSS Selectors</Label>
                <Input id="excluded-selectors" value={excludedSelectors} onChange={(e) => setExcludedSelectors(e.target.value)} placeholder="header,footer,nav" />
              </div>
              <div>
                <Label htmlFor="browser-engine">Browser Engine (Jina)</Label>
                <Select value={browserEngine} onValueChange={setBrowserEngine}>
                  <SelectTrigger id="browser-engine"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="chromium">Chromium</SelectItem>
                    <SelectItem value="firefox">Firefox</SelectItem>
                    <SelectItem value="webkit">WebKit</SelectItem>
                    <SelectItem value="playwright">Playwright (Default)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="token-budget">Token Budget (Jina)</Label>
                <Input id="token-budget" type="number" value={tokenBudget} onChange={(e) => setTokenBudget(parseInt(e.target.value, 10))} />
              </div>
              <div className="md:col-span-1">
                <Label htmlFor="viewport-width">Viewport Width (Jina)</Label>
                <Input id="viewport-width" type="number" value={viewportWidth} onChange={(e) => setViewportWidth(parseInt(e.target.value, 10))} placeholder="1920" />
              </div>
              <div className="md:col-span-1">
                <Label htmlFor="viewport-height">Viewport Height (Jina)</Label>
                <Input id="viewport-height" type="number" value={viewportHeight} onChange={(e) => setViewportHeight(parseInt(e.target.value, 10))} placeholder="1080" />
              </div>
              <div>
                <Label htmlFor="markdown-flavor">Markdown Flavor (Jina)</Label>
                <Select value={markdownFlavor} onValueChange={setMarkdownFlavor}>
                  <SelectTrigger id="markdown-flavor"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="commonmark">CommonMark</SelectItem>
                    <SelectItem value="gfm">GitHub Flavored (GFM)</SelectItem>
                    <SelectItem value="markdown_extra">Markdown Extra</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="timeout">Timeout (seconds, Jina)</Label>
                <Input id="timeout" type="number" value={timeout} onChange={(e) => setTimeout(parseInt(e.target.value, 10))} />
              </div>
              <div>
                <Label htmlFor="cache-ttl">Cache TTL (seconds, Jina)</Label>
                <Input id="cache-ttl" type="number" value={cacheTtl} onChange={(e) => setCacheTtl(parseInt(e.target.value, 10))} />
              </div>
              <div>
                <Label htmlFor="browser-locale">Browser Locale (Jina)</Label>
                <Input id="browser-locale" value={browserLocale} onChange={(e) => setBrowserLocale(e.target.value)} placeholder="en-US, fr-FR" />
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
              <div className="flex items-center space-x-2">
                <Checkbox id="extract-text-only" checked={extractTextOnly} onCheckedChange={setExtractTextOnly} />
                <Label htmlFor="extract-text-only">Extract Text Only (No Images/Structure)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="extract-tables" checked={extractTables} onCheckedChange={setExtractTables} />
                <Label htmlFor="extract-tables">Extract Tables</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="extract-images" checked={extractImages} onCheckedChange={setExtractImages} />
                <Label htmlFor="extract-images">Extract Images</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="extract-links" checked={extractLinks} onCheckedChange={setExtractLinks} />
                <Label htmlFor="extract-links">Extract Links</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="json-response" checked={jsonResponse} onCheckedChange={setJsonResponse} />
                <Label htmlFor="json-response">JSON Response (Raw from Jina)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="clean-format" checked={cleanFormat} onCheckedChange={setCleanFormat} />
                <Label htmlFor="clean-format">Clean Formatting (Jina)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="image-captioning" checked={imageCaptioning} onCheckedChange={setImageCaptioning} />
                <Label htmlFor="image-captioning">Enable Image Captioning (Jina)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="extract-metadata" checked={extractMetadata} onCheckedChange={setExtractMetadata} />
                <Label htmlFor="extract-metadata">Extract Page Metadata (Jina)</Label>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      )}

      {fetchingEngine === 'crawl4ai' && (
        <>
          <AccordionItem value="crawl4ai-browser-nav">
            <AccordionTrigger>Crawl4AI: Browser & Navigation</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-user-agent">User Agent</Label>
                  <Input id="crawl4ai-user-agent" value={crawl4aiUserAgent} onChange={(e) => setCrawl4aiUserAgent(e.target.value)} placeholder="Mozilla/5.0 ..." />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-proxy-url">Proxy URL</Label>
                  <Input id="crawl4ai-proxy-url" value={crawl4aiProxyUrl} onChange={(e) => setCrawl4aiProxyUrl(e.target.value)} placeholder="http://user:pass@host:port" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-viewport-width">Viewport Width</Label>
                  <Input id="crawl4ai-viewport-width" type="number" value={crawl4aiViewportWidth} onChange={(e) => setCrawl4aiViewportWidth(parseInt(e.target.value, 10))} placeholder="1920" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-viewport-height">Viewport Height</Label>
                  <Input id="crawl4ai-viewport-height" type="number" value={crawl4aiViewportHeight} onChange={(e) => setCrawl4aiViewportHeight(parseInt(e.target.value, 10))} placeholder="1080" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-page-load-wait">Page Load Wait Condition</Label>
                  <Select value={crawl4aiPageLoadWaitCondition} onValueChange={setCrawl4aiPageLoadWaitCondition}>
                    <SelectTrigger id="crawl4ai-page-load-wait"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="load">Load</SelectItem>
                      <SelectItem value="domcontentloaded">DOM Content Loaded</SelectItem>
                      <SelectItem value="networkidle">Network Idle (Default)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="crawl4ai-page-timeout">Page Timeout (ms)</Label>
                  <Input id="crawl4ai-page-timeout" type="number" value={crawl4aiPageTimeout} onChange={(e) => setCrawl4aiPageTimeout(parseInt(e.target.value, 10))} placeholder="30000" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-wait-for-condition">Wait for JS Condition (Advanced)</Label>
                  <Input id="crawl4ai-wait-for-condition" value={crawl4aiWaitForCondition} onChange={(e) => setCrawl4aiWaitForCondition(e.target.value)} placeholder="e.g., window.myFlag === true" />
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-enable-js" checked={crawl4aiEnableJs} onCheckedChange={setCrawl4aiEnableJs} />
                  <Label htmlFor="crawl4ai-enable-js">Enable JavaScript</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-ignore-https" checked={crawl4aiIgnoreHttpsErrors} onCheckedChange={setCrawl4aiIgnoreHttpsErrors} />
                  <Label htmlFor="crawl4ai-ignore-https">Ignore HTTPS Errors</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-light-mode" checked={crawl4aiLightMode} onCheckedChange={setCrawl4aiLightMode} />
                  <Label htmlFor="crawl4ai-light-mode">Light Mode</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-text-mode" checked={crawl4aiTextMode} onCheckedChange={setCrawl4aiTextMode} />
                  <Label htmlFor="crawl4ai-text-mode">Text Mode</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-content-extraction">
            <AccordionTrigger>Crawl4AI: Content Extraction & Processing</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-target-elements">Target CSS Selectors</Label>
                  <Input id="crawl4ai-target-elements" value={crawl4aiTargetElements} onChange={(e) => setCrawl4aiTargetElements(e.target.value)} placeholder="e.g., article, .content" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-excluded-elements">Excluded CSS Selectors</Label>
                  <Input id="crawl4ai-excluded-elements" value={crawl4aiExcludedElements} onChange={(e) => setCrawl4aiExcludedElements(e.target.value)} placeholder="e.g., .ads, #comments" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-excluded-tags">Excluded HTML Tags</Label>
                  <Input id="crawl4ai-excluded-tags" value={crawl4aiExcludedTags} onChange={(e) => setCrawl4aiExcludedTags(e.target.value)} placeholder="script,style,nav" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-word-count-threshold">Min Word Count Threshold</Label>
                  <Input id="crawl4ai-word-count-threshold" type="number" value={crawl4aiWordCountThreshold} onChange={(e) => setCrawl4aiWordCountThreshold(parseInt(e.target.value, 10))} placeholder="50" />
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-extract-only-text" checked={crawl4aiExtractOnlyTextContent} onCheckedChange={setCrawl4aiExtractOnlyTextContent} />
                  <Label htmlFor="crawl4ai-extract-only-text">Extract Only Text</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-process-iframes" checked={crawl4aiProcessIframes} onCheckedChange={setCrawl4aiProcessIframes} />
                  <Label htmlFor="crawl4ai-process-iframes">Process iFrames</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-remove-forms" checked={crawl4aiRemoveForms} onCheckedChange={setCrawl4aiRemoveForms} />
                  <Label htmlFor="crawl4ai-remove-forms">Remove Forms</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-keep-data-attributes" checked={crawl4aiKeepDataAttributes} onCheckedChange={setCrawl4aiKeepDataAttributes} />
                  <Label htmlFor="crawl4ai-keep-data-attributes">Keep Data Attributes</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-page-interaction">
            <AccordionTrigger>Crawl4AI: Page Interaction & Automation</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div>
                <Label htmlFor="crawl4ai-execute-js-on-load">JavaScript to Execute on Page Load</Label>
                <textarea
                  id="crawl4ai-execute-js-on-load"
                  value={crawl4aiExecuteJsOnLoad}
                  onChange={(e) => setCrawl4aiExecuteJsOnLoad(e.target.value)}
                  placeholder="Enter JS code to run after page loads..."
                  className="w-full p-2 border rounded-md min-h-[80px] text-sm"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-scroll-delay">Scroll Delay (seconds, if auto-scroll)</Label>
                  <Input id="crawl4ai-scroll-delay" type="number" value={crawl4aiScrollDelay} onChange={(e) => setCrawl4aiScrollDelay(parseFloat(e.target.value))} placeholder="2" />
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-scan-full-page" checked={crawl4aiScanFullPage} onCheckedChange={setCrawl4aiScanFullPage} />
                  <Label htmlFor="crawl4ai-scan-full-page">Scan Full Page (Auto-Scroll)</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-remove-overlays" checked={crawl4aiRemoveOverlayElements} onCheckedChange={setCrawl4aiRemoveOverlayElements} />
                  <Label htmlFor="crawl4ai-remove-overlays">Attempt Remove Overlays</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-simulate-user" checked={crawl4aiSimulateUserBehavior} onCheckedChange={setCrawl4aiSimulateUserBehavior} />
                  <Label htmlFor="crawl4ai-simulate-user">Simulate User Behavior</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-enable-magic" checked={crawl4aiEnableMagic} onCheckedChange={setCrawl4aiEnableMagic} />
                  <Label htmlFor="crawl4ai-enable-magic">Enable Magic Handling</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-override-nav" checked={crawl4aiOverrideNavigator} onCheckedChange={setCrawl4aiOverrideNavigator} />
                  <Label htmlFor="crawl4ai-override-nav">Override Navigator Props</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-caching">
            <AccordionTrigger>Crawl4AI: Caching Settings</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div>
                <Label htmlFor="crawl4ai-cache-mode">Cache Mode</Label>
                <Select value={crawl4aiCacheMode} onValueChange={setCrawl4aiCacheMode}>
                  <SelectTrigger id="crawl4ai-cache-mode"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="enabled">Enabled (Read/Write)</SelectItem>
                    <SelectItem value="bypass">Bypass (Ignore Cache)</SelectItem>
                    <SelectItem value="write_only">Write Only</SelectItem>
                    <SelectItem value="read_only">Read Only</SelectItem>
                    <SelectItem value="disabled">Disabled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-media">
            <AccordionTrigger>Crawl4AI: Media Handling</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-alt-min-words">Image Alt Text Min Words</Label>
                  <Input id="crawl4ai-alt-min-words" type="number" value={crawl4aiImageAltTextMinWordCount} onChange={(e) => setCrawl4aiImageAltTextMinWordCount(parseInt(e.target.value, 10))} placeholder="0" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-img-relevance">Image Relevance Score Threshold</Label>
                  <Input id="crawl4ai-img-relevance" type="number" value={crawl4aiImageRelevanceScoreThreshold} onChange={(e) => setCrawl4aiImageRelevanceScoreThreshold(parseInt(e.target.value, 10))} placeholder="0" />
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-screenshot" checked={crawl4aiCaptureScreenshot} onCheckedChange={setCrawl4aiCaptureScreenshot} />
                  <Label htmlFor="crawl4ai-screenshot">Capture Screenshot</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-pdf" checked={crawl4aiGeneratePdf} onCheckedChange={setCrawl4aiGeneratePdf} />
                  <Label htmlFor="crawl4ai-pdf">Generate PDF</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-mhtml" checked={crawl4aiCaptureMhtml} onCheckedChange={setCrawl4aiCaptureMhtml} />
                  <Label htmlFor="crawl4ai-mhtml">Capture MHTML Snapshot</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-exclude-ext-img" checked={crawl4aiExcludeExternalImages} onCheckedChange={setCrawl4aiExcludeExternalImages} />
                  <Label htmlFor="crawl4ai-exclude-ext-img">Exclude External Images</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-links-compliance">
            <AccordionTrigger>Crawl4AI: Link Filtering & Compliance</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div>
                <Label htmlFor="crawl4ai-custom-excluded-domains">Custom Excluded Domains (comma-separated)</Label>
                <Input id="crawl4ai-custom-excluded-domains" value={crawl4aiCustomExcludedDomains} onChange={(e) => setCrawl4aiCustomExcludedDomains(e.target.value)} placeholder="e.g., analytics.example.com, ads.domain.net" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-exclude-ext-links" checked={crawl4aiExcludeExternalLinks} onCheckedChange={setCrawl4aiExcludeExternalLinks} />
                  <Label htmlFor="crawl4ai-exclude-ext-links">Exclude External Links</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-exclude-social" checked={crawl4aiExcludeSocialMediaLinks} onCheckedChange={setCrawl4aiExcludeSocialMediaLinks} />
                  <Label htmlFor="crawl4ai-exclude-social">Exclude Social Media Links</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-respect-robots" checked={crawl4aiRespectRobotsTxt} onCheckedChange={setCrawl4aiRespectRobotsTxt} />
                  <Label htmlFor="crawl4ai-respect-robots">Respect robots.txt</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
          
          <AccordionItem value="crawl4ai-extraction-strategy">
            <AccordionTrigger>Crawl4AI: Extraction Strategy</AccordionTrigger>
            <AccordionContent className="p-4">
              <ExtractionStrategyConfigurator
                config={crawl4aiExtractionConfig}
                onChange={onCrawl4aiExtractionConfigChange}
              />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="crawl4ai-deepcrawl-strategy">
            <AccordionTrigger>Crawl4AI: Deep Crawl Strategy</AccordionTrigger>
            <AccordionContent className="p-4">
              <DeepCrawlStrategyConfigurator
                config={crawl4aiDeepCrawlConfig}
                onChange={onCrawl4aiDeepCrawlConfigChange}
              />
            </AccordionContent>
          </AccordionItem>
        </>
      )}

      {/* LLM Configuration Section - MOVED HERE and corrected */}
      <AccordionItem value="llm-config">
        <AccordionTrigger>LLM Configuration (for Crawl4AI & other future uses)</AccordionTrigger>
        <AccordionContent className="space-y-4 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="llm-provider">LLM Provider/Model</Label>
              <Select value={llmProvider} onValueChange={setLlmProvider}>
                <SelectTrigger id="llm-provider">
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  {isLoadingLlmModels ? (
                    <SelectItem value="loading-true" disabled>
                      Loading models...
                    </SelectItem>
                  ) : availableLlmModels && availableLlmModels.length > 0 ? (
                    availableLlmModels.map((model) => (
                      <SelectItem key={model.crawl4ai_compatible_id || model.model_id} value={model.crawl4ai_compatible_id || model.model_id}>
                        {model.display_name || model.model_id} {model.provider && `(${model.provider})`}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="no-models" disabled>
                      No models available.
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Select a registered LLM. List is dynamically loaded from backend.
              </p>
            </div>
            <div>
              <Label htmlFor="llm-api-token">LLM API Token/Key</Label>
              <Input 
                id="llm-api-token" 
                type="password" 
                value={llmApiToken || ""} 
                onChange={(e) => setLlmApiToken(e.target.value)} 
                placeholder="Enter API token if required by provider" 
              />
            </div>
            <div>
              <Label htmlFor="llm-base-url">LLM Base URL (Optional)</Label>
              <Input 
                id="llm-base-url" 
                value={llmBaseUrl || ""} 
                onChange={(e) => setLlmBaseUrl(e.target.value)} 
                placeholder="e.g., http://localhost:11434 for local Ollama" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                Required for local models like Ollama or custom/self-hosted API endpoints.
              </p>
            </div>
            {/* This part remains specific to crawl4ai's markdown generation feature */}
            {fetchingEngine === 'crawl4ai' && (
              <div>
                <Label htmlFor="crawl4ai-markdown-generator">Markdown Generator (Crawl4AI)</Label>
                <Select value={crawl4aiMarkdownGenerator || 'Default'} onValueChange={setCrawl4aiMarkdownGenerator}>
                  <SelectTrigger id="crawl4ai-markdown-generator">
                    <SelectValue placeholder="Select Markdown Generator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Default">Default</SelectItem>
                    <SelectItem value="Newspaper3k">Newspaper3k</SelectItem>
                    <SelectItem value="Readability">Readability</SelectItem>
                    <SelectItem value="LLM">LLM (Experimental)</SelectItem>
                  </SelectContent>
                </Select>
                 <p className="text-xs text-muted-foreground mt-1">
                  Choose how Crawl4AI generates final Markdown output.
                </p>
              </div>
            )}
          </div>
        </AccordionContent>
      </AccordionItem>

      {fetchingEngine === 'crawl4ai' && (
        <>
          <AccordionItem value="crawl4ai-debugging">
            <AccordionTrigger>Crawl4AI: Debugging & Logging</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-verbose-logging" checked={crawl4aiVerboseLogging} onCheckedChange={setCrawl4aiVerboseLogging} />
                  <Label htmlFor="crawl4ai-verbose-logging">Verbose Logging</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-log-page-console" checked={crawl4aiLogPageConsoleOutput} onCheckedChange={setCrawl4aiLogPageConsoleOutput} />
                  <Label htmlFor="crawl4ai-log-page-console">Log Page Console Output</Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
          
          <AccordionItem value="expert-options">
            <AccordionTrigger>Crawl4AI: Expert Options</AccordionTrigger>
            <AccordionContent className="space-y-4 p-4">
              <div>
                <Label htmlFor="crawl4ai-cookies">Browser Cookies (JSON string or array)</Label>
                <textarea
                  id="crawl4ai-cookies"
                  value={crawl4aiBrowserCookies}
                  onChange={(e) => setCrawl4aiBrowserCookies(e.target.value)}
                  placeholder={`[{"name": "cookie_name", "value": "cookie_value", "domain": ".example.com"}]`}
                  className="w-full p-2 border rounded-md min-h-[80px] text-sm"
                />
              </div>
              <div>
                <Label htmlFor="crawl4ai-headers">Browser Headers (JSON string)</Label>
                <textarea
                  id="crawl4ai-headers"
                  value={crawl4aiBrowserHeaders}
                  onChange={(e) => setCrawl4aiBrowserHeaders(e.target.value)}
                  placeholder={`{"X-Custom-Header": "value"}`}
                  className="w-full p-2 border rounded-md min-h-[80px] text-sm"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crawl4ai-session-id">Crawl Session ID</Label>
                  <Input id="crawl4ai-session-id" value={crawl4aiCrawlSessionId} onChange={(e) => setCrawl4aiCrawlSessionId(e.target.value)} placeholder="Optional session identifier" />
                </div>
                <div>
                  <Label htmlFor="crawl4ai-css-selector">Global CSS Selector (Crawl4AI)</Label>
                  <Input id="crawl4ai-css-selector" value={crawl4aiCrawlCssSelector} onChange={(e) => setCrawl4aiCrawlCssSelector(e.target.value)} placeholder="Overrides other selectors if set" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                  <Checkbox id="crawl4ai-persistent-context" checked={crawl4aiBrowserUsePersistentContext} onCheckedChange={setCrawl4aiBrowserUsePersistentContext} />
                  <Label htmlFor="crawl4ai-persistent-context">Use Persistent Browser Context</Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        </>
      )}

      {/* Common Options */}
      <AccordionItem value="common-options">
        <AccordionTrigger>Common Fetch Options</AccordionTrigger>
        <AccordionContent className="space-y-4 p-4">
          <div className="flex items-center space-x-2">
            <Checkbox id="upload-to-supabase" checked={uploadToSupabase} onCheckedChange={setUploadToSupabase} />
            <Label htmlFor="upload-to-supabase">Upload to Supabase (Generate Embedding & Store)</Label>
          </div>
           <p className="text-xs text-muted-foreground">
            If checked, the fetched content will be processed for embedding and stored in the Supabase database.
            This is useful for making the content searchable later.
          </p>
        </AccordionContent>
      </AccordionItem>

    </Accordion>
  );
} 