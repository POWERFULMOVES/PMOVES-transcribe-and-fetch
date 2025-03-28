"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider"; 
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { BACKEND_URL, SEARCH_PRESETS, SEARCH_PARAM_DESCRIPTIONS, SEARCH_TIER_DESCRIPTIONS, SEARCH_METHOD_DESCRIPTIONS } from '@/lib/constants';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";

// Import search components
import {
  SearchResultCard,
  SearchFlowIndicator,
  SearchResultsByMethod,
  AnalysisProcess,
  AnalysisDisplay,
  SearchResultsBySource,
  SearchResultsSummary,
  SearchResultsTable,
  SearchResultDetail
} from "@/components/search";

export default function VectorSearch() {
    const [query, setQuery] = useState('');
    // Use 'results' state for the list of search result objects
    const [results, setResults] = useState([]);
    const [openaiAnalysis, setOpenAIAnalysis] = useState('');
    const [groqAnalysis, setGroqAnalysis] = useState('');
    const [metadata, setMetadata] = useState(null); // To store metadata like tokens, duration
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [hasSearched, setHasSearched] = useState(false); // To know when to display results section
    const [selectedResult, setSelectedResult] = useState(null); // For the detail modal

    // Search parameters state (as you had before)
    const [searchParams, setSearchParams] = useState({
        fine_grained: { similarity_threshold: 0.75, content_weight: 0.8, result_percentage: 0.4, max_results: 15 },
        contextual:   { similarity_threshold: 0.7,  content_weight: 0.7, result_percentage: 0.35, max_results: 10 },
        overview:     { similarity_threshold: 0.65, content_weight: 0.5, result_percentage: 0.25, max_results: 5 }
    });
    const [presetValue, setPresetValue] = useState('default'); // Preset selection state
    const [runAnalysis, setRunAnalysis] = useState(true); // Analysis toggle state

    // Base URL (use constant or env var)
    const baseUrl = BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Use the presets from constants
    const searchPresets = SEARCH_PRESETS;

    // Parameter change handler (as you had before)
    const handleParamChange = (tier, param, value) => {
        setSearchParams(prevParams => ({
            ...prevParams,
            [tier]: { ...prevParams[tier], [param]: Number(value) }
        }));
         // Optionally reset preset value if params change manually
         setPresetValue('custom');
    };

    // Preset change handler
     const handlePresetChange = (value) => {
         setPresetValue(value);
         if (searchPresets[value]) {
             setSearchParams(searchPresets[value]);
         }
     };

    // --- New handleSearch using axios.post ---
    const handleSearch = useCallback(async () => {
        if (!query.trim()) {
            setError("Please enter a search query.");
            return;
        }

        setLoading(true);
        setHasSearched(true); // Indicate search has been attempted
        setResults([]); // Clear previous results
        setOpenAIAnalysis('');
        setGroqAnalysis('');
        setMetadata(null);
        setError(null);

        // Construct the JSON request body for POST
        const requestBody = {
            query: query,
            // Determine total max_results (maybe sum of tier max_results or a separate input?)
            // Using sum of tier max_results as an example:
            max_results: Object.values(searchParams).reduce((sum, tier) => sum + tier.max_results, 0),
            run_analysis: runAnalysis,
        };

        // Construct the URL with query parameters for overrides
        const searchUrl = new URL(`${baseUrl}/api/search`);
        // Append override parameters ONLY if preset is 'custom' or if you always want to send them
        // Or alternatively, send them in the POST body if backend accepts it (requires backend change)
        // Using Query Params as implemented in backend step 2:
        searchUrl.searchParams.append('preset', presetValue); // Send preset name
        Object.entries(searchParams).forEach(([tier, params]) => {
            Object.entries(params).forEach(([key, value]) => {
                 // Check if the current param differs from the selected preset's default
                 // or just send all params if preset is 'custom'
                 const presetOrDefaultForParam = searchPresets[presetValue]?.[tier]?.[key] ?? searchPresets.default[tier][key];
                 if (presetValue === 'custom' || value !== presetOrDefaultForParam) {
                      searchUrl.searchParams.append(`${tier}_${key}`, value);
                 }
            });
        });


        console.log("Sending POST to:", searchUrl.toString());
        console.log("Request Body:", requestBody);

        try {
            const response = await axios.post(searchUrl.toString(), requestBody);

            console.log("Search Response:", response.data);

            // Update state with results
            setResults(response.data.results || []);
            setOpenAIAnalysis(response.data.openai_analysis || '');
            setGroqAnalysis(response.data.groq_analysis || '');
            
            // Ensure metadata has the required flags
            const responseMetadata = response.data.metadata || {};
            const enhancedMetadata = {
                ...responseMetadata,
                search_complete: true,  // Ensure this flag exists
                analysis_complete: runAnalysis && 
                    (response.data.openai_analysis || response.data.groq_analysis)  // Ensure this flag exists
            };
            
            setMetadata(enhancedMetadata);

        } catch (err) {
            console.error('Search error:', err);
            const errorMsg = err.response?.data?.detail || err.message || 'Search failed';
            setError(errorMsg);
            setResults([]); // Clear results on error
        } finally {
            setLoading(false);
        }
    }, [query, presetValue, searchParams, runAnalysis, baseUrl]); // Dependencies

    // --- State Persistence (Keep as is if desired) ---
    // Helper function for safe JSON parsing
    const safeJsonParse = (str, fallback = null) => {
        try {
            return str ? JSON.parse(str) : fallback;
        } catch (e) {
            console.warn('Error parsing JSON:', e);
            return fallback;
        }
    };

    // Load state from localStorage
    useEffect(() => {
        try {
            const savedState = localStorage.getItem('vectorSearchState');
            if (savedState) {
                const parsedState = safeJsonParse(savedState);
                if (parsedState) {
                    // Only restore serializable state
                    setQuery(parsedState.query || '');
                    setPresetValue(parsedState.presetValue || 'default');
                    setSearchParams(parsedState.searchParams || searchPresets.default);
                    setRunAnalysis(parsedState.runAnalysis ?? true);
                }
            }
        } catch (error) {
            console.error('Error loading saved state:', error);
        }
    }, []);

    // Save state to localStorage
    useEffect(() => {
        try {
            // Only save serializable data
            const stateToSave = {
                query,
                presetValue,
                searchParams,
                runAnalysis
            };
            localStorage.setItem('vectorSearchState', JSON.stringify(stateToSave));
        } catch (error) {
            console.error('Error saving state:', error);
        }
    }, [query, presetValue, searchParams, runAnalysis]);

    // --- Render Logic ---
    return (
        <div className="container mx-auto p-4 max-w-6xl">
            <h1 className="text-2xl font-bold mb-6">Semantic Vector Search</h1>

            {/* Search Input Card */}
            <Card className="mb-6">
                <CardHeader>
                     <CardTitle>Search Query & Parameters</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }}>
                        {/* Query Input */}
                        <div className="flex items-center mb-4">
                            <Input
                                type="text" value={query} onChange={(e) => setQuery(e.target.value)}
                                placeholder="Enter your search query" className="flex-grow mr-4" required
                             />
                             {/* Preset Selector */}
                             <Select value={presetValue} onValueChange={handlePresetChange}>
                                 <SelectTrigger className="w-[180px] mr-4">
                                     <SelectValue placeholder="Select Preset" />
                                 </SelectTrigger>
                                 <SelectContent>
                                     <SelectItem value="default">Default</SelectItem>
                                     <SelectItem value="technical">Technical</SelectItem>
                                     <SelectItem value="conceptual">Conceptual</SelectItem>
                                     <SelectItem value="balanced">Balanced</SelectItem>
                                     <SelectItem value="custom" disabled>Custom</SelectItem> {/* Show custom when params are changed */}
                                 </SelectContent>
                             </Select>
                            <Button type="submit" disabled={loading || !query.trim()}>
                                {loading ? "Searching..." : "Search"}
                            </Button>
                        </div>
                        
                        {/* Preset Descriptions */}
                        <div className="mb-4 text-xs text-gray-600">
                            <p className="mb-1"><strong>Current Preset:</strong> {presetValue === 'custom' ? 'Custom' : presetValue.charAt(0).toUpperCase() + presetValue.slice(1)}</p>
                            {presetValue === 'default' && (
                                <p>Balanced configuration suitable for most searches with moderate thresholds across all tiers.</p>
                            )}
                            {presetValue === 'technical' && (
                                <p>High precision, focused on exact content matching. Best for finding specific technical information, code examples, or precise details.</p>
                            )}
                            {presetValue === 'conceptual' && (
                                <p>Broader semantic matching for conceptual exploration. Best for understanding high-level concepts and finding thematic connections.</p>
                            )}
                            {presetValue === 'balanced' && (
                                <p>Equal emphasis on precision and recall with moderate thresholds and equal distribution across tiers. Best for exploratory searches with a mix of specific and broad results.</p>
                            )}
                            {presetValue === 'custom' && (
                                <p>Custom configuration with your manually adjusted parameters. Open the parameters panel below to fine-tune your search.</p>
                            )}
                        </div>
                        {/* Analysis Toggle */}
                        <div className="flex items-center space-x-2 mb-6">
                            <Switch id="run-analysis" checked={runAnalysis} onCheckedChange={setRunAnalysis} />
                            <Label htmlFor="run-analysis">Enable AI Analysis {runAnalysis ? '(Will summarize results)' : '(Faster, results only)'}</Label>
                            <div className="ml-4 text-xs text-gray-500">
                                AI analysis uses OpenAI and Groq to provide summaries and insights from your search results.
                            </div>
                        </div>

                        {/* Search Methods Explanation */}
                        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Search Methods</h4>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                <div>
                                    <span className="text-blue-600 font-medium block">Vector Search</span>
                                    <p className="text-gray-600">Uses AI embeddings to find semantically similar content, even when exact keywords don't match. Provides conceptually related results.</p>
                                </div>
                                <div>
                                    <span className="text-blue-600 font-medium block">Keyword Search</span>
                                    <p className="text-gray-600">Traditional text matching to find content containing specific keywords. Useful for finding exact phrases or terms.</p>
                                </div>
                                <div>
                                    <span className="text-blue-600 font-medium block">Hybrid Search</span>
                                    <p className="text-gray-600">Combines both approaches for comprehensive results. Prioritizes based on multiple factors including similarity and content type.</p>
                                </div>
                            </div>
                        </div>

                        {/* Parameter Accordion */}
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value="params">
                            <AccordionTrigger>Adjust Search Parameters (Preset: {presetValue})</AccordionTrigger>
                            <AccordionContent className="space-y-6 pt-4">
                              {/* Parameter Explanation */}
                              <div className="p-4 border rounded-md bg-gray-50 mb-4">
                                <h4 className="font-semibold mb-3 text-gray-700">Understanding Search Parameters</h4>
                                <div className="space-y-3 text-sm">
                                  <div>
                                    <p className="font-medium">Similarity Threshold:</p>
                                    <p className="text-gray-600">Controls how closely results must match your query (0.0-1.0). Higher values (0.8+) return only very precise matches, while lower values (&lt;0.6) return broader matches.</p>
                                  </div>
                                  <div>
                                    <p className="font-medium">Content Weight:</p>
                                    <p className="text-gray-600">Adjusts the balance between exact content matching and semantic matching. Higher values prioritize exact word matches, while lower values prioritize conceptual similarity.</p>
                                  </div>
                                  <div>
                                    <p className="font-medium">Max Results:</p>
                                    <p className="text-gray-600">Controls how many results to show from each search category. Higher values provide more comprehensive results but potentially more noise.</p>
                                  </div>
                                </div>
                              </div>
                              {/* Fine-grained Sliders */}
                              <div className="p-4 border rounded-md">
                                <h4 className="font-semibold mb-3 text-blue-700">Fine-grained (High Precision)</h4>
                                <p className="text-sm text-gray-600 mb-3">For finding specific, precise information. Best for technical details, exact quotes, and specific timestamps. Searches individual segments with high similarity thresholds.</p>
                                {/* Similarity Threshold */}
                                <div className="mb-4">
                                   <Label className="flex justify-between">
                                     <span>Similarity Threshold: {searchParams.fine_grained.similarity_threshold.toFixed(2)}</span>
                                     <span className="text-xs text-gray-500">How closely results must match your query</span>
                                   </Label>
                                   <Slider id="fg-sim" min={0} max={1} step={0.05} value={[searchParams.fine_grained.similarity_threshold]} onValueChange={([v]) => handleParamChange('fine_grained', 'similarity_threshold', v)} />
                                </div>
                                {/* Content Weight */}
                                <div className="mb-4">
                                   <Label className="flex justify-between">
                                     <span>Content Weight: {searchParams.fine_grained.content_weight.toFixed(1)}</span>
                                     <span className="text-xs text-gray-500">Balance between exact matching vs. semantic matching</span>
                                   </Label>
                                   <Slider id="fg-weight" min={0} max={1} step={0.1} value={[searchParams.fine_grained.content_weight]} onValueChange={([v]) => handleParamChange('fine_grained', 'content_weight', v)} />
                                </div>
                                {/* Max Results */}
                                <div className="mb-4">
                                   <Label className="flex justify-between">
                                     <span>Max Results: {searchParams.fine_grained.max_results}</span>
                                     <span className="text-xs text-gray-500">Number of results to return from this tier</span>
                                   </Label>
                                   <Slider id="fg-max" min={1} max={30} step={1} value={[searchParams.fine_grained.max_results]} onValueChange={([v]) => handleParamChange('fine_grained', 'max_results', v)} />
                                </div>
                              </div>
                              {/* Contextual Sliders */}
                               <div className="p-4 border rounded-md">
                                 <h4 className="font-semibold mb-3 text-purple-700">Contextual (Balanced)</h4>
                                 <p className="text-sm text-gray-600 mb-3">For finding content with surrounding context. Best for understanding topics in context and finding related content. Balances precision and recall, includes context from surrounding segments.</p>
                                 {/* Similarity Threshold */}
                                 <div className="mb-4">
                                    <Label className="flex justify-between">
                                      <span>Similarity Threshold: {searchParams.contextual.similarity_threshold.toFixed(2)}</span>
                                      <span className="text-xs text-gray-500">How closely results must match your query</span>
                                    </Label>
                                    <Slider id="ctx-sim" min={0} max={1} step={0.05} value={[searchParams.contextual.similarity_threshold]} onValueChange={([v]) => handleParamChange('contextual', 'similarity_threshold', v)} />
                                 </div>
                                 {/* Content Weight */}
                                 <div className="mb-4">
                                    <Label className="flex justify-between">
                                      <span>Content Weight: {searchParams.contextual.content_weight.toFixed(1)}</span>
                                      <span className="text-xs text-gray-500">Balance between exact matching vs. semantic matching</span>
                                    </Label>
                                    <Slider id="ctx-weight" min={0} max={1} step={0.1} value={[searchParams.contextual.content_weight]} onValueChange={([v]) => handleParamChange('contextual', 'content_weight', v)} />
                                 </div>
                                 {/* Max Results */}
                                 <div className="mb-4">
                                    <Label className="flex justify-between">
                                      <span>Max Results: {searchParams.contextual.max_results}</span>
                                      <span className="text-xs text-gray-500">Number of results to return from this tier</span>
                                    </Label>
                                    <Slider id="ctx-max" min={1} max={30} step={1} value={[searchParams.contextual.max_results]} onValueChange={([v]) => handleParamChange('contextual', 'max_results', v)} />
                                 </div>
                               </div>
                               {/* Overview Sliders */}
                                <div className="p-4 border rounded-md">
                                  <h4 className="font-semibold mb-3 text-indigo-700">Overview (Broad Insights)</h4>
                                  <p className="text-sm text-gray-600 mb-3">For getting broader insights across content. Best for exploratory searches and finding thematic connections. Uses lower thresholds to capture more conceptual matches.</p>
                                  {/* Similarity Threshold */}
                                   <div className="mb-4">
                                      <Label className="flex justify-between">
                                        <span>Similarity Threshold: {searchParams.overview.similarity_threshold.toFixed(2)}</span>
                                        <span className="text-xs text-gray-500">How closely results must match your query</span>
                                      </Label>
                                      <Slider id="ov-sim" min={0} max={1} step={0.05} value={[searchParams.overview.similarity_threshold]} onValueChange={([v]) => handleParamChange('overview', 'similarity_threshold', v)} />
                                   </div>
                                  {/* Content Weight */}
                                  <div className="mb-4">
                                     <Label className="flex justify-between">
                                       <span>Content Weight: {searchParams.overview.content_weight.toFixed(1)}</span>
                                       <span className="text-xs text-gray-500">Balance between exact matching vs. semantic matching</span>
                                     </Label>
                                     <Slider id="ov-weight" min={0} max={1} step={0.1} value={[searchParams.overview.content_weight]} onValueChange={([v]) => handleParamChange('overview', 'content_weight', v)} />
                                  </div>
                                  {/* Max Results */}
                                  <div className="mb-4">
                                     <Label className="flex justify-between">
                                       <span>Max Results: {searchParams.overview.max_results}</span>
                                       <span className="text-xs text-gray-500">Number of results to return from this tier</span>
                                     </Label>
                                     <Slider id="ov-max" min={1} max={30} step={1} value={[searchParams.overview.max_results]} onValueChange={([v]) => handleParamChange('overview', 'max_results', v)} />
                                  </div>
                                </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                    </form>
                </CardContent>
            </Card>

            {/* Results Area */}
            {hasSearched && !loading && !error && (
                <div className="mt-6 space-y-6">
                    {/* Search Flow Visualization */}
                    <SearchFlowIndicator 
                        currentStage={metadata?.search_complete ? 'complete' : 'search'} 
                        metadata={metadata}
                    />
                    
                    {/* Search Results Summary */}
                    <SearchResultsSummary results={results} metadata={metadata} />
                    
                    {/* Results by Method */}
                    <SearchResultsByMethod 
                        results={results} 
                        title="Search Results by Method" 
                        icon="🔍"
                    />
                    
                    {/* Results by Source */}
                    <SearchResultsBySource results={results} />
                    
                    {/* AI Analysis Display */}
                    {runAnalysis && (
                        <>
                            <AnalysisProcess 
                                currentStep={metadata?.analysis_complete ? 'complete' : 'generating'} 
                                openaiAnalysis={openaiAnalysis} 
                                groqAnalysis={groqAnalysis}
                            />
                            
                            <AnalysisDisplay 
                                openaiAnalysis={openaiAnalysis} 
                                groqAnalysis={groqAnalysis} 
                            />
                        </>
                    )}
                    
                    {/* Results Table */}
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold mb-4">Search Results Table</h2>
                        <SearchResultsTable 
                            results={results} 
                            onViewDetails={(result) => setSelectedResult(result)} 
                        />
                    </div>
                    
                    {/* Results Cards */}
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
                        <div className="space-y-4">
                            {results.length > 0 ? results.map((result, index) => (
                                <SearchResultCard key={result.id || index} result={result} />
                            )) : (
                                <div className="text-center p-8 border rounded-md bg-gray-50">
                                    <p className="text-gray-500">No search results to display.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Loading Indicator */}
            {loading && <div className="text-center mt-6">Loading search results...</div>}

            {/* Error Display */}
            {error && !loading && (
                <Card className="mt-6 border-destructive bg-destructive/10">
                    <CardHeader><CardTitle className="text-destructive">Search Error</CardTitle></CardHeader>
                    <CardContent><p>{error}</p></CardContent>
                </Card>
            )}
            
            {/* Result Detail Modal */}
            {selectedResult && (
                <SearchResultDetail 
                    result={selectedResult} 
                    onClose={() => setSelectedResult(null)} 
                />
            )}
        </div>
    );
}
