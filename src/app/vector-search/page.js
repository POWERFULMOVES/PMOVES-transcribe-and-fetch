"use client";

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { createSafeEventSource, parseSseData } from '@/utils/sse-helpers';
import { Badge } from "@/components/ui/badge";
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

import { CalendarIcon, X } from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";

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
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const ITEMS_PER_PAGE = 10;

export default function VectorSearch() {
    const [query, setQuery] = useState('');
    // Use 'results' state for the list of search result objects
    const [results, setResults] = useState([]);
    const [openaiAnalysis, setOpenAIAnalysis] = useState('');
    const [openAIAnalysisReceived, setOpenAIAnalysisReceived] = useState(false);
    const [groqAnalysis, setGroqAnalysis] = useState('');
    const [groqAnalysisReceived, setGroqAnalysisReceived] = useState(false);
    const [metadata, setMetadata] = useState(null); // To store metadata like tokens, duration
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [hasSearched, setHasSearched] = useState(false); // To know when to display results section
    const [selectedResult, setSelectedResult] = useState(null); // For the detail modal
    const [sortOption, setSortOption] = useState('relevance'); // Default sort option
    const [currentPage, setCurrentPage] = useState(1); // For pagination

    // Document Types
    const availableDocTypes = ['Transcript', 'Full Transcript', 'Document', 'Webpage', 'Text', 'Video', 'Audio'];
    const [selectedDocTypes, setSelectedDocTypes] = useState({}); // None selected by default

    // Source Types
    const availableSources = [
        { value: 'document_embeddings', label: 'Documents' },
        { value: 'video_transcriptions', label: 'Video Segments' },
        { value: 'video_transcriptions_full', label: 'Full Videos' },
        { value: 'webpage_content', label: 'Webpages' },
        { value: 'text_content', label: 'Text Files' },
        { value: 'media_content', label: 'Other Media' },
    ];
    const [selectedSources, setSelectedSources] = useState({}); // None selected by default

    // Score Range
    const [scoreRange, setScoreRange] = useState([0.0, 1.0]); // [min, max]

    // Date Range
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    // Search parameters state (as you had before)
    const [searchParams, setSearchParams] = useState({
        fine_grained: { similarity_threshold: 0.75, content_weight: 0.8, result_percentage: 0.4, max_results: 15 },
        contextual:   { similarity_threshold: 0.7,  content_weight: 0.7, result_percentage: 0.35, max_results: 10 },
        overview:     { similarity_threshold: 0.65, content_weight: 0.5, result_percentage: 0.25, max_results: 5 }
    });
    const [presetValue, setPresetValue] = useState('default'); // Preset selection state
    const [runAnalysis, setRunAnalysis] = useState(true); // Analysis toggle state

    // Handler for sort option change
    const handleSortChange = (value) => {
        setSortOption(value);
    };

    // Handler for document type checkbox changes
    const handleDocTypeChange = (docType) => {
        setSelectedDocTypes(prevSelectedDocTypes => ({
            ...prevSelectedDocTypes,
            [docType]: !prevSelectedDocTypes[docType]
        }));
    };

    // Handler for source type checkbox changes
    const handleSourceChange = (sourceValue) => {
        setSelectedSources(prevSelectedSources => ({
            ...prevSelectedSources,
            [sourceValue]: !prevSelectedSources[sourceValue]
        }));
    };

    // Handler for score range slider change
    const handleScoreRangeChange = (newRange) => {
        setScoreRange(newRange);
    };

    // Handler for start date change
    const handleStartDateChange = (date) => {
        setStartDate(date);
    };

    // Handler for end date change
    const handleEndDateChange = (date) => {
        setEndDate(date);
    };
 
    // --- Filter Removal Handlers ---
    const removeDocTypeFilter = (docTypeToRemove) => {
        setSelectedDocTypes(prev => {
            const newSelected = { ...prev };
            delete newSelected[docTypeToRemove]; // Or set to false if that's how it's managed
            // If you store true/false: newSelected[docTypeToRemove] = false;
            return newSelected;
        });
    };

    const removeSourceFilter = (sourceToRemove) => {
        setSelectedSources(prev => {
            const newSelected = { ...prev };
            delete newSelected[sourceToRemove]; // Or set to false
            // If you store true/false: newSelected[sourceToRemove] = false;
            return newSelected;
        });
    };

    const resetScoreRangeFilter = () => {
        setScoreRange([0.0, 1.0]);
    };

    const clearStartDateFilter = () => {
        setStartDate(null);
    };

    const clearEndDateFilter = () => {
        setEndDate(null);
    };

    const clearAllFilters = () => {
        setSelectedDocTypes({});
        setSelectedSources({});
        setScoreRange([0.0, 1.0]);
        setStartDate(null);
        setEndDate(null);
    };
 
    // Base URL
    const baseUrl = BACKEND_URL;

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

    // --- Search state tracking ---
    const [currentStage, setCurrentStage] = useState('start');
    const [eventSource, setEventSource] = useState(null);

    // --- handleSearch using SSE for real-time updates ---
    // Debug function to log the current state
    const logCurrentState = () => {
      console.log('Current state:', {
        currentStage,
        loading,
        hasSearched,
        resultsLength: results.length,
        metadata
      });
    };
    
    const handleSearch = useCallback(() => {
        if (!query.trim()) {
            setError("Please enter a search query.");
            return;
        }

        // Clean up any existing EventSource
        if (eventSource) {
            eventSource.close();
        }

        // Only reset analysis flags if analysis is enabled
        if (runAnalysis) {
            // Reset analysis received flags
            setOpenAIAnalysisReceived(false);
            setGroqAnalysisReceived(false);
        }
        
        // Reset all states at the beginning of a new search
        setLoading(true);
        setHasSearched(true); // Indicate search has been attempted
        setResults([]); // Clear previous results
        setOpenAIAnalysis('');
        setGroqAnalysis('');
        setMetadata(null);
        setError(null);
        setCurrentStage('start'); // Reset to initial stage

        // Construct the URL with query parameters
        const searchUrl = new URL(`${baseUrl}/api/search-sse`);
        searchUrl.searchParams.append('query', query);
        searchUrl.searchParams.append('max_results', Object.values(searchParams).reduce((sum, tier) => sum + tier.max_results, 0));
        searchUrl.searchParams.append('run_analysis', runAnalysis);
        searchUrl.searchParams.append('preset', presetValue);
        
        // Add search parameters as query params
        Object.entries(searchParams).forEach(([tier, params]) => {
            Object.entries(params).forEach(([key, value]) => {
                const presetOrDefaultForParam = searchPresets[presetValue]?.[tier]?.[key] ?? searchPresets.default[tier][key];
                if (presetValue === 'custom' || value !== presetOrDefaultForParam) {
                    searchUrl.searchParams.append(`${tier}_${key}`, value);
                }
            });
        });

        console.log("Connecting to SSE endpoint:", searchUrl.toString());

        // Create SSE connection using the utility function
        // Close any existing EventSource before creating a new one
        if (eventSource) {
            console.log("Closing existing SSE connection before creating a new one");
            eventSource.close();
            setEventSource(null);
        }
        
        const newEventSource = createSafeEventSource(
            searchUrl.toString(),
            (data) => {
                // Handle different event types
                if (!data) return;
                
                console.log("SSE Event received:", data);
                
                const eventType = data.type || 'unknown';
                
                switch (eventType) {
                    case 'status':
                        // Update search flow stage based on status
                        if (data.metadata?.stage) {
                            console.log('Updating stage to:', data.metadata.stage);
                            
                            // Use a functional state update to ensure we're working with the latest state
                            setCurrentStage(prevStage => {
                                console.log('Previous stage:', prevStage, 'New stage:', data.metadata.stage);
                                return data.metadata.stage;
                            });
                            
                            // Log the update for debugging
                            setTimeout(() => {
                                console.log('Stage updated to:', data.metadata.stage);
                            }, 0);
                        }
                        
                        // Update metadata if provided - use functional update to avoid race conditions
                        if (data.metadata) {
                            setMetadata(prevMetadata => {
                                const updatedMetadata = {
                                    ...prevMetadata,
                                    ...data.metadata
                                };
                                console.log('Updated metadata:', updatedMetadata);
                                return updatedMetadata;
                            });
                        }
                        break;
                        
                    case 'results':
                        // Final results received
                        console.log('Received final results:', data.content?.length || 0, 'items');
                        
                        // Use functional update to ensure we're working with the latest state
                        setResults(prevResults => {
                            const newResults = data.content || [];
                            console.log('Updating results from', prevResults.length, 'to', newResults.length, 'items');
                            return newResults;
                        });
                        
                        // Ensure stage is updated to complete
                        setCurrentStage('complete');
                        
                        // Update metadata to indicate search is complete
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            search_complete: true,
                            ...(data.metadata || {})
                        }));
                        
                        // Only set loading to false if we have analysis or analysis is not requested
                        if (!runAnalysis || data.metadata?.analysis_complete) {
                            setLoading(false);
                            console.log('Setting loading to false after results');
                        }
                        break;
                        
                    case 'analysis':
                        // Analysis results
                        console.log('Received analysis from provider:', data.metadata?.provider);
                        
                        if (data.metadata?.provider === 'openai') {
                            if (runAnalysis) {
                                // Use functional update to ensure we're working with the latest state
                                setOpenAIAnalysisReceived(prevReceived => {
                                    if (!prevReceived) {
                                        // Only update if not already received
                                        setOpenAIAnalysis(data.content || '');
                                        console.log('OpenAI analysis set, marked as received');
                                        return true;
                                    } else {
                                        console.log('Ignoring duplicate OpenAI analysis');
                                        return prevReceived;
                                    }
                                });
                            } else {
                                // If analysis is not enabled, just set the content
                                setOpenAIAnalysis(data.content || '');
                                console.log('OpenAI analysis set (analysis tracking disabled)');
                            }
                        } else if (data.metadata?.provider === 'groq') {
                            if (runAnalysis) {
                                // Use functional update to ensure we're working with the latest state
                                setGroqAnalysisReceived(prevReceived => {
                                    if (!prevReceived) {
                                        // Only update if not already received
                                        setGroqAnalysis(data.content || '');
                                        console.log('Groq analysis set, marked as received');
                                        return true;
                                    } else {
                                        console.log('Ignoring duplicate Groq analysis');
                                        return prevReceived;
                                    }
                                });
                            } else {
                                // If analysis is not enabled, just set the content
                                setGroqAnalysis(data.content || '');
                                console.log('Groq analysis set (analysis tracking disabled)');
                            }
                        }
                        
                        // Update metadata to indicate analysis is complete
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            analysis_complete: true
                        }));
                        
                        // Check if both analyses are received or not requested
                        if (!runAnalysis || (openAIAnalysisReceived && groqAnalysisReceived)) {
                            // Ensure stage is updated to complete
                            setCurrentStage('complete');
                            setLoading(false);
                            console.log('Setting loading to false and stage to complete after analysis');
                        }
                        break;
                        
                    case 'error':
                        console.error('SSE error event:', data.content);
                        setError(data.content || 'An error occurred during search');
                        setLoading(false);
                        console.log('Setting loading to false due to error');
                        break;
                        
                    case 'complete':
                        // Search process complete
                        console.log('Search process complete');
                        setCurrentStage('complete');
                        setLoading(false);
                        console.log('Setting loading to false due to completion');
                        
                        // Ensure metadata has the required flags
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            search_complete: true
                        }));
                        
                        // Close the EventSource to prevent connection errors
                        if (newEventSource) {
                            console.log('Closing SSE connection after search completion');
                            newEventSource.close();
                            setEventSource(null);
                        }
                        break;
                        
                    case 'heartbeat':
                        // Just a heartbeat to keep the connection alive
                        console.log('Heartbeat received');
                        break;
                        
                    default:
                        console.log(`Unhandled SSE event type: ${eventType}`);
                }
                },
            (error) => {
                console.error('SSE Error:', error);
                setError('Connection error. Please try again.');
                setLoading(false);
                console.log('Setting loading to false due to connection error');
            }
        );
        
        // Store the EventSource for cleanup
        setEventSource(newEventSource);
        
        // Return cleanup function
        return () => {
            if (newEventSource) {
                console.log("Closing SSE connection");
                newEventSource.close();
                setEventSource(null);
            }
        };
    }, [query, presetValue, searchParams, runAnalysis, baseUrl, eventSource, openAIAnalysisReceived, groqAnalysisReceived]);
    
    // Clean up EventSource on unmount
    useEffect(() => {
        return () => {
            if (eventSource) {
                console.log("Component unmounting, closing SSE connection");
                eventSource.close();
            }
        };
    }, [eventSource]);

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

    // Document type mapping from display name to backend value
    const docTypeMapping = {
        'Transcript': 'transcript',
        'Full Transcript': 'full_transcript',
        'Document': 'document',
        'Webpage': 'webpage',
        'Text': 'text',
        'Video': 'video',
        'Audio': 'audio',
    };

    // Memoized filtered results
    const filteredResults = useMemo(() => {
        if (!results) return [];
        let currentResults = [...results];

        // Apply Document Type Filter
        const activeDocTypes = Object.entries(selectedDocTypes)
            .filter(([, isActive]) => isActive)
            .map(([type]) => docTypeMapping[type])
            .filter(Boolean); // Filter out any undefined mappings if a display name wasn't found

        if (activeDocTypes.length > 0) {
            currentResults = currentResults.filter(result =>
                activeDocTypes.includes(result.content_type)
            );
        }

        // Apply Source Filter
        const activeSources = Object.entries(selectedSources)
            .filter(([, isActive]) => isActive)
            .map(([sourceValue]) => sourceValue);

        if (activeSources.length > 0) {
            currentResults = currentResults.filter(result =>
                activeSources.includes(result.source)
            );
        }

        // Apply Score Range Filter
        currentResults = currentResults.filter(result =>
            (result.similarity || 0) >= scoreRange[0] && (result.similarity || 0) <= scoreRange[1]
        );
        
        // Date filtering is skipped for now as a reliable date field is not identified.
        // If startDate and endDate were to be used, the logic would be here:
        // if (startDate) {
        //     currentResults = currentResults.filter(result => {
        //         // Assuming result.metadata.created_at exists and is a comparable date string or timestamp
        //         // const resultDate = new Date(result.metadata?.created_at);
        //         // return resultDate >= startDate;
        //     });
        // }
        // if (endDate) {
        //     currentResults = currentResults.filter(result => {
        //         // const resultDate = new Date(result.metadata?.created_at);
        //         // return resultDate <= endDate;
        //     });
        // }

        return currentResults;
    }, [results, selectedDocTypes, selectedSources, scoreRange, startDate, endDate]);

    // Memoized sorted results (now operates on filteredResults)
    const sortedResults = useMemo(() => {
        if (!filteredResults) return [];
        let sortedArray = [...filteredResults];

        if (sortOption === 'relevance') {
            sortedArray.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
        } else if (sortOption === 'title') {
            sortedArray.sort((a, b) => {
                const titleA = a.title || '';
                const titleB = b.title || '';
                return titleA.localeCompare(titleB);
            });
        }
        // Add other sort options here in the future if needed
        return sortedArray;
    }, [filteredResults, sortOption]);

    // Reset current page when sortedResults or filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [sortedResults, selectedDocTypes, selectedSources, scoreRange, startDate, endDate]);

    // Calculate paginated results
    const paginatedResults = useMemo(() => {
        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
        const endIndex = startIndex + ITEMS_PER_PAGE;
        return sortedResults.slice(startIndex, endIndex);
    }, [sortedResults, currentPage]);

    // --- Render Logic ---

    const getActiveDocTypes = () => Object.keys(selectedDocTypes).filter(key => selectedDocTypes[key]);
    const getActiveSources = () => Object.keys(selectedSources).filter(key => selectedSources[key]);
    const isScoreRangeActive = () => scoreRange[0] !== 0.0 || scoreRange[1] !== 1.0;
    const isStartDateActive = () => startDate !== null;
    const isEndDateActive = () => endDate !== null;

    const anyFilterActive = () =>
        getActiveDocTypes().length > 0 ||
        getActiveSources().length > 0 ||
        isScoreRangeActive() ||
        isStartDateActive() ||
        isEndDateActive();

    return (
        <div className="container mx-auto p-4 max-w-6xl flex flex-col md:flex-row gap-4">
            {/* Left Panel */}
            {/* Left Panel Shell */}
            <Card className="w-full md:w-[300px] shrink-0">
                <CardHeader>
                    <CardTitle>Filters</CardTitle>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-[calc(100vh-200px)] pr-4"> {/* Adjust height as needed, add padding for scrollbar */}
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-sm font-medium mb-2">Document Type</h3>
                                <div className="space-y-2">
                                    {availableDocTypes.map((docType) => (
                                        <div key={docType} className="flex items-center space-x-2">
                                            <Checkbox
                                                id={`docType-${docType}`}
                                                checked={!!selectedDocTypes[docType]}
                                                onCheckedChange={() => handleDocTypeChange(docType)}
                                            />
                                            <Label htmlFor={`docType-${docType}`} className="text-sm font-normal">
                                                {docType}
                                            </Label>
                                        </div>
                                    ))}
                                </div>
                           </div>
                           {/* Source Filter Section */}
                           <div>
                               <h3 className="text-sm font-medium mb-2 mt-4">Source</h3>
                               <div className="space-y-2">
                                   {availableSources.map((source) => (
                                       <div key={source.value} className="flex items-center space-x-2">
                                           <Checkbox
                                               id={`source-${source.value}`}
                                               checked={!!selectedSources[source.value]}
                                               onCheckedChange={() => handleSourceChange(source.value)}
                                           />
                                           <Label htmlFor={`source-${source.value}`} className="text-sm font-normal">
                                               {source.label}
                                           </Label>
                                       </div>
                                   ))}
                               </div>
                          </div>
                          {/* Score Range Filter Section */}
                          <div>
                              <h3 className="text-sm font-medium mb-2 mt-4">Score Range</h3>
                              <div className="space-y-3">
                                   <Label htmlFor="score-range-slider" className="text-sm font-normal">
                                       Score: {scoreRange[0].toFixed(2)} - {scoreRange[1].toFixed(2)}
                                   </Label>
                                   <Slider
                                       id="score-range-slider"
                                       min={0}
                                       max={1}
                                       step={0.01}
                                       value={scoreRange}
                                       onValueChange={handleScoreRangeChange}
                                       className="w-full"
                                   />
                               </div>
                          </div>
                          {/* Date Range Filter Section */}
                          <div>
                              <h3 className="text-sm font-medium mb-2 mt-4">Date Range</h3>
                              <div className="space-y-3">
                                  <div>
                                      <Label htmlFor="start-date-picker" className="text-sm font-normal mb-1 block">Start Date</Label>
                                      <Popover>
                                          <PopoverTrigger asChild>
                                              <Button
                                                  id="start-date-picker"
                                                  variant={"outline"}
                                                  className="w-full justify-start text-left font-normal"
                                              >
                                                  <CalendarIcon className="mr-2 h-4 w-4" />
                                                  {startDate ? format(startDate, "PPP") : <span>Pick a date</span>}
                                              </Button>
                                          </PopoverTrigger>
                                          <PopoverContent className="w-auto p-0">
                                              <Calendar
                                                  mode="single"
                                                  selected={startDate}
                                                  onSelect={handleStartDateChange}
                                                  initialFocus
                                              />
                                          </PopoverContent>
                                      </Popover>
                                  </div>
                                  <div>
                                      <Label htmlFor="end-date-picker" className="text-sm font-normal mb-1 block">End Date</Label>
                                      <Popover>
                                          <PopoverTrigger asChild>
                                              <Button
                                                  id="end-date-picker"
                                                  variant={"outline"}
                                                  className="w-full justify-start text-left font-normal"
                                              >
                                                  <CalendarIcon className="mr-2 h-4 w-4" />
                                                  {endDate ? format(endDate, "PPP") : <span>Pick a date</span>}
                                              </Button>
                                          </PopoverTrigger>
                                          <PopoverContent className="w-auto p-0">
                                              <Calendar
                                                  mode="single"
                                                  selected={endDate}
                                                  onSelect={handleEndDateChange}
                                                  disabled={(date) => startDate && date < startDate} // Disable dates before start date
                                                  initialFocus
                                              />
                                          </PopoverContent>
                                      </Popover>
                                  </div>
                              </div>
                          </div>
                      </div>
                  </ScrollArea>
                </CardContent>
            </Card>

            {/* Right Panel */}
            <div className="flex-1 min-w-0">
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
                                        <span className="text-[hsl(var(--page-accent))] font-medium block">Vector Search</span>
                                        <p className="text-gray-600">Uses AI embeddings to find semantically similar content, even when exact keywords don't match. Provides conceptually related results.</p>
                                    </div>
                                    <div>
                                        <span className="text-[hsl(var(--page-accent))] font-medium block">Keyword Search</span>
                                        <p className="text-gray-600">Traditional text matching to find content containing specific keywords. Useful for finding exact phrases or terms.</p>
                                    </div>
                                    <div>
                                        <span className="text-[hsl(var(--page-accent))] font-medium block">Hybrid Search</span>
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
                                    <h4 className="font-semibold mb-3 text-[hsl(var(--page-accent))]">Fine-grained (High Precision)</h4>
                                    <p className="text-sm text-gray-600 mb-3">For finding specific, precise information. Best for technical details, exact quotes, and specific timestamps. Searches individual segments with high similarity thresholds.</p>
                                    {/* Similarity Threshold */}
                                    <div className="mb-4">
                                       <Label className="flex justify-between">
                                         <span>Similarity Threshold: {searchParams.fine_grained.similarity_threshold.toFixed(2)}</span>
                                         <span className="text-xs text-gray-500">Defines how closely results match the query</span>
                                       </Label>
                                       <Slider id="fg-sim" min={0} max={1} step={0.05} value={[searchParams.fine_grained.similarity_threshold]} onValueChange={([v]) => handleParamChange('fine_grained', 'similarity_threshold', v)} />
                                    </div>
                                    {/* Content Weight */}
                                    <div className="mb-4">
                                       <Label className="flex justify-between">
                                         <span>Content Weight: {searchParams.fine_grained.content_weight.toFixed(1)}</span>
                                         <span className="text-xs text-gray-500">Balances exact keyword vs. semantic concept matching</span>
                                       </Label>
                                       <Slider id="fg-weight" min={0} max={1} step={0.1} value={[searchParams.fine_grained.content_weight]} onValueChange={([v]) => handleParamChange('fine_grained', 'content_weight', v)} />
                                    </div>
                                    {/* Max Results */}
                                    <div className="mb-4">
                                       <Label className="flex justify-between">
                                         <span>Max Results: {searchParams.fine_grained.max_results}</span>
                                         <span className="text-xs text-gray-500">Max results returned by this tier</span>
                                       </Label>
                                       <Slider id="fg-max" min={1} max={30} step={1} value={[searchParams.fine_grained.max_results]} onValueChange={([v]) => handleParamChange('fine_grained', 'max_results', v)} />
                                    </div>
                                  </div>
                                  {/* Contextual Sliders */}
                                   <div className="p-4 border rounded-md">
                                     <h4 className="font-semibold mb-3 text-[hsl(var(--page-accent))]">Contextual (Balanced)</h4>
                                     <p className="text-sm text-gray-600 mb-3">For finding content with surrounding context. Best for understanding topics in context and finding related content. Balances precision and recall, includes context from surrounding segments.</p>
                                     {/* Similarity Threshold */}
                                     <div className="mb-4">
                                        <Label className="flex justify-between">
                                          <span>Similarity Threshold: {searchParams.contextual.similarity_threshold.toFixed(2)}</span>
                                          <span className="text-xs text-gray-500">Defines how closely results match the query</span>
                                        </Label>
                                        <Slider id="ctx-sim" min={0} max={1} step={0.05} value={[searchParams.contextual.similarity_threshold]} onValueChange={([v]) => handleParamChange('contextual', 'similarity_threshold', v)} />
                                     </div>
                                     {/* Content Weight */}
                                     <div className="mb-4">
                                        <Label className="flex justify-between">
                                          <span>Content Weight: {searchParams.contextual.content_weight.toFixed(1)}</span>
                                          <span className="text-xs text-gray-500">Balances exact keyword vs. semantic concept matching</span>
                                        </Label>
                                        <Slider id="ctx-weight" min={0} max={1} step={0.1} value={[searchParams.contextual.content_weight]} onValueChange={([v]) => handleParamChange('contextual', 'content_weight', v)} />
                                     </div>
                                     {/* Max Results */}
                                     <div className="mb-4">
                                        <Label className="flex justify-between">
                                          <span>Max Results: {searchParams.contextual.max_results}</span>
                                          <span className="text-xs text-gray-500">Max results returned by this tier</span>
                                        </Label>
                                        <Slider id="ctx-max" min={1} max={30} step={1} value={[searchParams.contextual.max_results]} onValueChange={([v]) => handleParamChange('contextual', 'max_results', v)} />
                                     </div>
                                   </div>
                                  {/* Overview Sliders */}
                                    <div className="p-4 border rounded-md">
                                      <h4 className="font-semibold mb-3 text-[hsl(var(--page-accent))]">Overview (Broad Insights)</h4>
                                      <p className="text-sm text-gray-600 mb-3">For getting broader insights across content. Best for exploratory searches and finding thematic connections. Uses lower thresholds to capture more conceptual matches.</p>
                                      {/* Similarity Threshold */}
                                       <div className="mb-4">
                                          <Label className="flex justify-between">
                                            <span>Similarity Threshold: {searchParams.overview.similarity_threshold.toFixed(2)}</span>
                                            <span className="text-xs text-gray-500">Defines how closely results match the query</span>
                                          </Label>
                                          <Slider id="ov-sim" min={0} max={1} step={0.05} value={[searchParams.overview.similarity_threshold]} onValueChange={([v]) => handleParamChange('overview', 'similarity_threshold', v)} />
                                       </div>
                                      {/* Content Weight */}
                                      <div className="mb-4">
                                         <Label className="flex justify-between">
                                           <span>Content Weight: {searchParams.overview.content_weight.toFixed(1)}</span>
                                           <span className="text-xs text-gray-500">Balances exact keyword vs. semantic concept matching</span>
                                         </Label>
                                         <Slider id="ov-weight" min={0} max={1} step={0.1} value={[searchParams.overview.content_weight]} onValueChange={([v]) => handleParamChange('overview', 'content_weight', v)} />
                                      </div>
                                      {/* Max Results */}
                                      <div className="mb-4">
                                         <Label className="flex justify-between">
                                           <span>Max Results: {searchParams.overview.max_results}</span>
                                           <span className="text-xs text-gray-500">Max results returned by this tier</span>
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

                {/* Active Filters Display */}
                {anyFilterActive() && (
                    <Card className="mb-6">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <CardTitle>Active Filters</CardTitle>
                                <Button variant="outline" size="sm" onClick={clearAllFilters}>
                                    Clear All Filters
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2">
                                {getActiveDocTypes().map(docType => (
                                    <Badge key={`filter-doctype-${docType}`} variant="secondary" className="flex items-center">
                                        Type: {docType}
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="ml-1 h-4 w-4 rounded-full"
                                            onClick={() => removeDocTypeFilter(docType)}
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </Badge>
                                ))}
                                {getActiveSources().map(sourceValue => {
                                    const sourceLabel = availableSources.find(s => s.value === sourceValue)?.label || sourceValue;
                                    return (
                                        <Badge key={`filter-source-${sourceValue}`} variant="secondary" className="flex items-center">
                                            Source: {sourceLabel}
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="ml-1 h-4 w-4 rounded-full"
                                                onClick={() => removeSourceFilter(sourceValue)}
                                            >
                                                <X className="h-3 w-3" />
                                            </Button>
                                        </Badge>
                                    );
                                })}
                                {isScoreRangeActive() && (
                                    <Badge variant="secondary" className="flex items-center">
                                        Score: {scoreRange[0].toFixed(2)} - {scoreRange[1].toFixed(2)}
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="ml-1 h-4 w-4 rounded-full"
                                            onClick={resetScoreRangeFilter}
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </Badge>
                                )}
                                {isStartDateActive() && (
                                    <Badge variant="secondary" className="flex items-center">
                                        Start: {format(startDate, "yyyy-MM-dd")}
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="ml-1 h-4 w-4 rounded-full"
                                            onClick={clearStartDateFilter}
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </Badge>
                                )}
                                {isEndDateActive() && (
                                    <Badge variant="secondary" className="flex items-center">
                                        End: {format(endDate, "yyyy-MM-dd")}
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="ml-1 h-4 w-4 rounded-full"
                                            onClick={clearEndDateFilter}
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </Badge>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Results Area */}
                {hasSearched && (
                    <div className="mt-6 space-y-6">
                        {/* Search Flow Visualization - Always show during search process */}
                        <SearchFlowIndicator 
                            currentStage={currentStage} 
                            metadata={metadata}
                            loading={loading}
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

                        {/* Tabbed Results View */}
                        <Tabs defaultValue="cardView" className="w-full">
                            <div className="flex justify-between items-center mt-6 mb-2">
                                <TabsList className="grid w-full grid-cols-2 md:w-[400px]">
                                    <TabsTrigger value="cardView">Card View</TabsTrigger>
                                    <TabsTrigger value="tableView">Table View</TabsTrigger>
                                </TabsList>
                                <div className="ml-4">
                                    <Select value={sortOption} onValueChange={handleSortChange}>
                                        <SelectTrigger className="w-[200px]">
                                            <SelectValue placeholder="Sort by..." />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="relevance">Sort by: Relevance</SelectItem>
                                            <SelectItem value="title">Sort by: Title</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            <TabsContent value="cardView">
                                <div className="mb-6 mt-4"> {/* Added mt-4 for spacing below tabs list */}
                                    <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
                                    <div className="space-y-4">
                                        {paginatedResults.length > 0 ? paginatedResults.map((result, index) => (
                                            <SearchResultCard key={`main-results-card-${result.id || index}-${Math.random().toString(36).substr(2, 5)}`} result={result} index={index} />
                                        )) : (
                                            <div className="text-center p-8 border rounded-md bg-gray-50">
                                                <p className="text-gray-500">No search results to display for the current page.</p>
                                                {loading && <p className="text-gray-500 mt-2">Still loading...</p>}
                                                {!loading && results.length === 0 && <p className="text-gray-500 mt-2">Try a different query or adjust filters.</p>}
                                                {!loading && results.length > 0 && paginatedResults.length === 0 && <p className="text-gray-500 mt-2">No results on this page. Try going to the first page.</p>}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </TabsContent>
                            <TabsContent value="tableView">
                                <div className="mb-6 mt-4"> {/* Added mt-4 for spacing below tabs list */}
                                    <h2 className="text-xl font-semibold mb-4">Search Results Table</h2>
                                    <SearchResultsTable
                                        results={paginatedResults}
                                        onViewDetails={(result) => setSelectedResult(result)}
                                    />
                                     {paginatedResults.length === 0 && !loading && results.length > 0 && (
                                        <div className="text-center p-8 border rounded-md bg-gray-50 mt-4">
                                            <p className="text-gray-500">No results on this page for the table view. Try going to the first page.</p>
                                        </div>
                                    )}
                                </div>
                            </TabsContent>
                        </Tabs>

                        {/* Pagination UI */}
                        {sortedResults.length > 0 && Math.ceil(sortedResults.length / ITEMS_PER_PAGE) > 1 && (
                            <div className="mt-6 flex justify-center">
                                <Pagination>
                                    <PaginationContent>
                                        <PaginationItem>
                                            <PaginationPrevious
                                                href="#"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    setCurrentPage((prev) => Math.max(prev - 1, 1));
                                                }}
                                                disabled={currentPage === 1}
                                                isActive={currentPage !== 1}
                                            />
                                        </PaginationItem>
                                        {[...Array(Math.ceil(sortedResults.length / ITEMS_PER_PAGE))].map((_, i) => {
                                            const pageNum = i + 1;
                                            // Basic pagination: show all pages. Can be enhanced later.
                                            // For more complex scenarios with ellipsis:
                                            // const totalPages = Math.ceil(sortedResults.length / ITEMS_PER_PAGE);
                                            // if (totalPages <= 7) { /* show all */ }
                                            // else { /* show first, last, current +/- 1, ellipsis */ }
                                            return (
                                                <PaginationItem key={pageNum}>
                                                    <PaginationLink
                                                        href="#"
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            setCurrentPage(pageNum);
                                                        }}
                                                        isActive={currentPage === pageNum}
                                                    >
                                                        {pageNum}
                                                    </PaginationLink>
                                                </PaginationItem>
                                            );
                                        })}
                                        <PaginationItem>
                                            <PaginationNext
                                                href="#"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    setCurrentPage((prev) => Math.min(prev + 1, Math.ceil(sortedResults.length / ITEMS_PER_PAGE)));
                                                }}
                                                disabled={currentPage === Math.ceil(sortedResults.length / ITEMS_PER_PAGE)}
                                                isActive={currentPage !== Math.ceil(sortedResults.length / ITEMS_PER_PAGE)}
                                            />
                                        </PaginationItem>
                                    </PaginationContent>
                                </Pagination>
                            </div>
                        )}
                        
                        {/* AI Analysis Display */}
                        {runAnalysis && (
                            <div className="space-y-4">
                                <AnalysisProcess
                                    currentStep={metadata?.analysis_complete ? 'complete' : 'generating'}
                                    openaiAnalysis={openaiAnalysis}
                                    groqAnalysis={groqAnalysis}
                                    accentColor="var(--page-accent)" // Pass accent color
                                />
                                
                                <AnalysisDisplay
                                    openaiAnalysis={openaiAnalysis}
                                    groqAnalysis={groqAnalysis}
                                    accentColor="var(--page-accent)" // Pass accent color
                                />
                            </div>
                        )}
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
            </div> {/* End Right Panel */}
        </div> // End Main Container
    );
}
