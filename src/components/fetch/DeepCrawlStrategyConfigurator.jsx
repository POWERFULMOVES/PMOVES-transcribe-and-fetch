"use client";

import React, { useCallback } from 'react'; // Import useState and useEffect if they are used by other logic, otherwise remove. For this refactor, they are removed.
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { InfoCircledIcon } from '@radix-ui/react-icons';

const DEEP_CRAWL_STRATEGIES = [
  { value: 'None', label: 'None / Default' },
  { value: 'BFSDeepCrawlStrategy', label: 'BFS Deep Crawl Strategy' },
  { value: 'DFSDeepCrawlStrategy', label: 'DFS Deep Crawl Strategy' },
  { value: 'BestFirstCrawlingStrategy', label: 'Best First Crawling Strategy' },
];

const URL_SCORERS = [
  { value: 'KeywordRelevanceScorer', label: 'Keyword Relevance Scorer' },
  // Add other scorers here if needed in the future
];

const DeepCrawlStrategyConfiguratorComponent = ({ onConfigChange, initialConfig = {} }) => {
  console.log('[DeepCrawlStrategyConfigurator] Rendering. Config from props:', JSON.stringify(initialConfig));

  const currentStrategy = initialConfig.strategy || 'None';
  const defaultInternalParams = { // Define defaults for internal consistency if needed by UI before propogation
    max_depth: '',
    max_pages: '',
    include_external: false,
    url_filter_patterns: '',
    score_threshold: '',
    url_scorer: '',
    scorer_keywords: '',
  };
  const currentParams = { ...defaultInternalParams, ...(initialConfig.params || {}) };

  // Helper to build the final params object for onConfigChange, ensuring correct types and structure
  // This function is now defined inside the component or imported if it's generic enough.
  // For this diff, let's assume it's defined here for clarity.
  const buildOutputConfig = useCallback((strategy, sourceParams) => {
    const outputParams = {};
    if (strategy === 'None') {
      return { strategy: 'None', params: outputParams };
    }

    const safeSourceParams = typeof sourceParams === 'object' && sourceParams !== null ? sourceParams : {};

    if (safeSourceParams.max_depth !== '' && safeSourceParams.max_depth !== null && safeSourceParams.max_depth !== undefined) {
      const val = parseInt(String(safeSourceParams.max_depth), 10);
      if (!isNaN(val)) outputParams.max_depth = val;
    }
    if (safeSourceParams.max_pages !== '' && safeSourceParams.max_pages !== null && safeSourceParams.max_pages !== undefined) {
      const val = parseInt(String(safeSourceParams.max_pages), 10);
      if (!isNaN(val)) outputParams.max_pages = val;
    }
    outputParams.include_external = !!safeSourceParams.include_external;

    if (safeSourceParams.url_filter_patterns && String(safeSourceParams.url_filter_patterns).trim()) {
      outputParams.filter_chain = {
        URLPatternFilter: String(safeSourceParams.url_filter_patterns).split('\n').map(s => s.trim()).filter(s => s),
      };
    }

    if (strategy === 'BFSDeepCrawlStrategy' || strategy === 'DFSDeepCrawlStrategy') {
      if (safeSourceParams.score_threshold !== '' && safeSourceParams.score_threshold !== null && safeSourceParams.score_threshold !== undefined) {
         const val = parseFloat(String(safeSourceParams.score_threshold));
         if (!isNaN(val)) outputParams.score_threshold = val;
      }
    }

    if (strategy === 'BestFirstCrawlingStrategy') {
      if (safeSourceParams.url_scorer && safeSourceParams.url_scorer !== 'none_scorer_option') {
        if (safeSourceParams.url_scorer === 'KeywordRelevanceScorer' && safeSourceParams.scorer_keywords && String(safeSourceParams.scorer_keywords).trim()) {
          outputParams.url_scorer = {
            KeywordRelevanceScorer: {
              keywords: String(safeSourceParams.scorer_keywords).split(',').map(s => s.trim()).filter(s => s),
            },
          };
        } else if (safeSourceParams.url_scorer && safeSourceParams.url_scorer !== 'KeywordRelevanceScorer') {
          // This condition ensures that if url_scorer is something other than KeywordRelevanceScorer (and not 'none_scorer_option'), it's passed through.
          outputParams.url_scorer = safeSourceParams.url_scorer;
        }
        // If url_scorer is 'KeywordRelevanceScorer' but no keywords, it's omitted.
        // If url_scorer is 'none_scorer_option', it's omitted by the outer if.
      }
    }
    return { strategy, params: outputParams };
  }, []); // buildOutputConfig is a pure function of its args, can be memoized or defined outside if preferred.

  // REMOVED: useState for selectedStrategy and params
  // REMOVED: useEffect for initialConfig synchronization
  // REMOVED: useEffect for onConfigChange based on internal state
  // REMOVED: useEffect for logging selectedStrategy (as internal state is gone)

  const handleStrategySelectChange = useCallback((newStrategyValue) => {
    if (onConfigChange) {
      console.log(`[DeepCrawlStrategyConfigurator] Strategy changed to: ${newStrategyValue}. Calling onConfigChange.`);
      // When strategy changes, params need to be adjusted.
      // Preserve common params, clear/default strategy-specific ones.
      const baseParamsForNewStrategy = {
        max_depth: currentParams.max_depth || '',
        max_pages: currentParams.max_pages || '',
        include_external: currentParams.include_external || false,
        url_filter_patterns: currentParams.url_filter_patterns || '',
        score_threshold: (newStrategyValue === 'BFSDeepCrawlStrategy' || newStrategyValue === 'DFSDeepCrawlStrategy') ? (currentParams.score_threshold || '') : '',
        url_scorer: (newStrategyValue === 'BestFirstCrawlingStrategy') ? (currentParams.url_scorer || '') : '',
        scorer_keywords: (newStrategyValue === 'BestFirstCrawlingStrategy' && (currentParams.url_scorer === 'KeywordRelevanceScorer')) ? (currentParams.scorer_keywords || '') : '',
      };
      const newConfig = buildOutputConfig(newStrategyValue, baseParamsForNewStrategy);
      onConfigChange(newConfig);
    }
  }, [onConfigChange, currentParams, buildOutputConfig]); // currentParams is from props

  const handleParamChange = useCallback((paramName, value) => {
    if (onConfigChange) {
      const updatedSourceParams = {
        ...currentParams,
        [paramName]: value,
      };
      console.log(`[DeepCrawlStrategyConfigurator] Param '${paramName}' changed to '${value}'. Calling onConfigChange.`);
      const newConfig = buildOutputConfig(currentStrategy, updatedSourceParams);
      onConfigChange(newConfig);
    }
  }, [onConfigChange, currentStrategy, currentParams, buildOutputConfig]);

  return (
    <TooltipProvider>
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Deep Crawling Strategy Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="deep-crawl-strategy">
              Select Strategy
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{'Choose the algorithm for discovering and visiting new pages found on the initial URL(s). \'None\' disables deep crawling.'}</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <Select
              value={currentStrategy}
              onValueChange={handleStrategySelectChange}
              id="deep-crawl-strategy"
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a deep crawling strategy" />
              </SelectTrigger>
              <SelectContent>
                {DEEP_CRAWL_STRATEGIES.map((strategy) => (
                  <SelectItem key={strategy.value} value={strategy.value}>
                    {strategy.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {currentStrategy !== 'None' && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="max-depth">
                    Max Depth
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Maximum depth of links to follow from the initial URL(s). 0 means only the initial page(s). Empty means no limit.'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="max-depth"
                    type="number"
                    placeholder="e.g., 3 (empty = no limit)"
                    value={currentParams.max_depth || ''}
                    onChange={(e) => handleParamChange('max_depth', e.target.value)}
                    min="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max-pages">
                    Max Pages
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Maximum total number of pages to crawl (including initial URL(s)). Empty means no limit.'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="max-pages"
                    type="number"
                    placeholder="e.g., 100 (empty = no limit)"
                    value={currentParams.max_pages || ''}
                    onChange={(e) => handleParamChange('max_pages', e.target.value)}
                    min="0"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="include-external"
                    checked={!!currentParams.include_external}
                    onCheckedChange={(checked) => handleParamChange('include_external', checked)}
                  />
                  <Label htmlFor="include-external">
                    Include External Links
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'If enabled, the crawler will follow links pointing to different domains. If disabled, it stays on the same domain(s) as the initial URL(s).'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="url-filter-patterns">
                  URL Filter Regex Patterns (one per line)
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{'Provide regular expressions (one per line) to filter which URLs are followed. Only URLs matching at least one pattern will be considered for crawling (if not excluded by other rules like domain restrictions).'}</p>
                    </TooltipContent>
                  </Tooltip>
                </Label>
                <Textarea
                  id="url-filter-patterns"
                  placeholder="e.g., ^https://example\\.com/blog/.*&#10;/products/.*"
                  value={currentParams.url_filter_patterns || ''}
                  onChange={(e) => handleParamChange('url_filter_patterns', e.target.value)}
                  rows={3}
                />
              </div>

              {(currentStrategy === 'BFSDeepCrawlStrategy' || currentStrategy === 'DFSDeepCrawlStrategy') && (
                <div className="space-y-2">
                  <Label htmlFor="score-threshold">
                    Score Threshold
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{'Minimum score a URL must have to be crawled. Used by BFS/DFS strategies if a scorer is implicitly active or planned for future versions. (Default: -Infinity)'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </Label>
                  <Input
                    id="score-threshold"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 0.5 (empty = -Infinity)"
                    value={currentParams.score_threshold || ''}
                    onChange={(e) => handleParamChange('score_threshold', e.target.value)}
                  />
                </div>
              )}

              {currentStrategy === 'BestFirstCrawlingStrategy' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="url-scorer">
                      URL Scorer
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{'Select a strategy to score URLs, influencing crawl priority for the \'Best First\' strategy. \'None\' uses default link order.'}</p>
                        </TooltipContent>
                      </Tooltip>
                    </Label>
                    <Select
                      value={currentParams.url_scorer || ''}
                      onValueChange={(value) => handleParamChange('url_scorer', value)}
                      id="url-scorer"
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a URL scorer" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none_scorer_option">None</SelectItem>
                        {URL_SCORERS.map((scorer) => (
                          <SelectItem key={scorer.value} value={scorer.value}>
                            {scorer.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {currentParams.url_scorer === 'KeywordRelevanceScorer' && (
                    <div className="space-y-2">
                      <Label htmlFor="scorer-keywords">
                        Keywords (comma-separated)
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{'Comma-separated keywords used by the \'Keyword Relevance Scorer\' to prioritize URLs containing these terms in the URL path or query string.'}</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="scorer-keywords"
                        type="text"
                        placeholder="e.g., AI, machine learning, data"
                        value={currentParams.scorer_keywords || ''}
                        onChange={(e) => handleParamChange('scorer_keywords', e.target.value)}
                      />
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  );
};

export default React.memo(DeepCrawlStrategyConfiguratorComponent);