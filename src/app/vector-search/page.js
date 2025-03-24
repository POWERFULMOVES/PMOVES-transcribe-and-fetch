"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { fetchEventSource } from '@microsoft/fetch-event-source';
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import { BACKEND_URL } from '@/lib/constants';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";

export default function VectorSearch() {
  const [query, setQuery] = useState('');
  const [sections, setSections] = useState([]);
  const [aiResponses, setAiResponses] = useState({
    openai: '',
    groq: ''
  });
  const [tokenUsage, setTokenUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamLogs, setStreamLogs] = useState([]);
  const [operationDetails, setOperationDetails] = useState({
    type: 'Advanced Hybrid Search',
    parameters: {},
    resultsCount: 0
  });
  const [searchParams, setSearchParams] = useState({
    fine_grained: {
      similarity_threshold: 0.75,
      content_weight: 0.8,
      result_percentage: 0.4,
      max_results: 15
    },
    contextual: {
      similarity_threshold: 0.7,
      content_weight: 0.7,
      result_percentage: 0.35,
      max_results: 10
    },
    overview: {
      similarity_threshold: 0.65,
      content_weight: 0.5,
      result_percentage: 0.25,
      max_results: 5
    }
  });
  const eventSourceRef = useRef(null);
  const abortController = useRef(null);
  const streamLogRef = useRef(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [presetValue, setPresetValue] = useState('default');
  const [runAnalysis, setRunAnalysis] = useState(true);
  const [analysisPreview, setAnalysisPreview] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState([]);
  const [groqAnalysis, setGroqAnalysis] = useState('');
  const [openAIAnalysis, setOpenAIAnalysis] = useState('');
  const [tokensUsed, setTokensUsed] = useState(null);
  const [searchLogs, setSearchLogs] = useState([]);

  // Base URL for API requests
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const searchPresets = {
    default: {
      fine_grained: {
        similarity_threshold: 0.75,
        content_weight: 0.8,
        result_percentage: 0.4,
        max_results: 15
      },
      contextual: {
        similarity_threshold: 0.7,
        content_weight: 0.7,
        result_percentage: 0.35,
        max_results: 10
      },
      overview: {
        similarity_threshold: 0.65,
        content_weight: 0.5,
        result_percentage: 0.25,
        max_results: 5
      }
    },
    technical: {
      fine_grained: {
        similarity_threshold: 0.8,
        content_weight: 0.9,
        result_percentage: 0.6,
        max_results: 20
      },
      contextual: {
        similarity_threshold: 0.75,
        content_weight: 0.8,
        result_percentage: 0.3,
        max_results: 10
      },
      overview: {
        similarity_threshold: 0.7,
        content_weight: 0.7,
        result_percentage: 0.1,
        max_results: 3
      }
    },
    conceptual: {
      fine_grained: {
        similarity_threshold: 0.7,
        content_weight: 0.6,
        result_percentage: 0.2,
        max_results: 5
      },
      contextual: {
        similarity_threshold: 0.7,
        content_weight: 0.5,
        result_percentage: 0.4,
        max_results: 15
      },
      overview: {
        similarity_threshold: 0.65,
        content_weight: 0.3,
        result_percentage: 0.4,
        max_results: 15
      }
    },
    balanced: {
      fine_grained: {
        similarity_threshold: 0.7,
        content_weight: 0.6,
        result_percentage: 0.4,
        max_results: 12
      },
      contextual: {
        similarity_threshold: 0.7,
        content_weight: 0.6,
        result_percentage: 0.4,
        max_results: 12
      },
      overview: {
        similarity_threshold: 0.65,
        content_weight: 0.4,
        result_percentage: 0.2,
        max_results: 8
      }
    }
  };

  const handleParamChange = (tier, param, value) => {
    setSearchParams(prevParams => ({
      ...prevParams,
      [tier]: {
        ...prevParams[tier],
        [param]: Number(value)
      }
    }));
  };

  // Move addStreamLog before setupSSE
  const addStreamLog = useCallback((message) => {
    setStreamLogs(prev => [...prev, message]);
    if (streamLogRef.current) {
      streamLogRef.current.scrollTop = streamLogRef.current.scrollHeight;
    }
  }, []);

  // Add cleanup function
  const cleanupStorage = useCallback(() => {
    try {
      localStorage.removeItem('vectorSearchState');
      console.log('Cleaned up vector search state');
    } catch (error) {
      console.error('Error cleaning up state:', error);
    }
  }, []);

  // Add setupSSE function definition
  const setupSSE = useCallback(() => {
    if (!query.trim()) return;
    
    // Build the search URL with parameters
    const url = new URL(`${baseUrl}/vector-search-stream`);
    url.searchParams.append('query', query);
    url.searchParams.append('preset', presetValue);
    url.searchParams.append('run_analysis', runAnalysis);
    
    // Add all search parameters
    Object.entries(searchParams).forEach(([tier, params]) => {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(`${tier}_${key}`, value);
      });
    });
    
    console.log('Setting up SSE connection to:', url.toString());
    
    try {
      // Close any existing connection
      if (eventSourceRef.current) {
        console.log('Closing existing SSE connection');
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }

      const eventSource = new EventSource(url.toString());
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection opened successfully');
        setError(null);
        addStreamLog('Connected to search stream...');
      };

      eventSource.onmessage = (event) => {
        if (!event.data) {
          console.warn('Empty SSE message received');
          return;
        }

        try {
          // Log raw data for debugging
          console.log('Raw SSE data received:', event.data);

          // Handle different data formats
          let data;
          if (typeof event.data === 'string') {
            // Remove any 'data: ' prefix if present
            const cleanData = event.data.replace(/^data:\s*/, '').trim();
            try {
              data = JSON.parse(cleanData);
            } catch (parseError) {
              console.warn('Failed to parse SSE data as JSON:', parseError);
              // If it's not JSON, try to handle it as a plain message
              data = {
                type: 'status',
                message: cleanData
              };
            }
          } else if (typeof event.data === 'object') {
            // If it's already an object, use it directly
            data = event.data;
          } else {
            console.warn('Unexpected SSE data format:', typeof event.data);
            return;
          }

          // Log parsed data for debugging
          console.log('Parsed SSE data:', data);

          // Ensure we have a valid type
          if (!data.type) {
            console.warn('SSE message missing type:', data);
            return;
          }

          switch (data.type) {
            case 'status':
              addStreamLog(data.message || data.content || 'Status update received');
              break;

            case 'results':
              if (data.results && Array.isArray(data.results)) {
                setSections(prevSections => {
                  const existingResults = new Map(
                    prevSections.map(section => [
                      `${section.video_id}-${section.start_time}-${section.end_time}-${section.content}`,
                      section
                    ])
                  );

                  data.results.forEach(result => {
                    const resultKey = `${result.video_id}-${result.start_time}-${result.end_time}-${result.content}`;
                    if (!existingResults.has(resultKey)) {
                      existingResults.set(resultKey, {
                        id: result.id || `result-${Date.now()}-${Math.random()}`,
                        content: result.content || result.text || '',
                        similarity: result.similarity || 0,
                        source: result.source || 'unknown',
                        start_time: String(result.start_time || 'N/A'),
                        end_time: String(result.end_time || 'N/A'),
                        watch_url: String(result.watch_url || ''),
                        summary: String(result.summary || ''),
                        search_method: result.search_method || 'unknown',
                        priority_score: result.priority_score,
                        has_context: result.has_context,
                        video_title: result.video_title,
                        word_count: result.word_count,
                        duration: result.duration,
                        video_id: result.video_id
                      });
                    }
                  });

                  const sortedResults = Array.from(existingResults.values())
                    .sort((a, b) => (b.similarity || 0) - (a.similarity || 0));

                  // Update operation details
                  setOperationDetails(prev => ({
                    ...prev,
                    resultsCount: sortedResults.length
                  }));

                  return sortedResults;
                });

                addStreamLog(`Received ${data.results.length} search results`);
              } else if (data.data && Array.isArray(data.data.results)) {
                // Handle nested results format
                const results = data.data.results;
                setSections(prevSections => {
                  // ... same processing as above ...
                  return prevSections;
                });
                addStreamLog(`Received ${results.length} search results`);
              } else {
                console.warn('Invalid results format:', data);
              }
              break;

            case 'analysis_preview':
              const preview = data.preview || data.data;
              if (preview) {
                setAnalysisPreview(preview);
                addStreamLog(`Analysis preview received: ${preview.result_count || 0} results selected`);
              }
              break;

            case 'ai_response_openai':
              const openaiAnalysis = data.analysis || data.content || data.data;
              if (openaiAnalysis) {
                setOpenAIAnalysis(openaiAnalysis);
                addStreamLog('Received OpenAI analysis');
              }
              break;

            case 'ai_response_groq':
              const groqAnalysis = data.analysis || data.content || data.data;
              if (groqAnalysis) {
                setGroqAnalysis(groqAnalysis);
                addStreamLog('Received Groq analysis');
              }
              break;

            case 'token_usage':
              const usage = data.usage || data.data;
              if (usage) {
                setTokensUsed(usage);
                addStreamLog(`Token usage updated - Total: ${usage.total || 0}`);
              }
              break;

            case 'error':
              const errorMessage = data.message || data.error || data.content || 'Unknown error occurred';
              console.error('Search error:', errorMessage);
              setError(errorMessage);
              addStreamLog(`Error: ${errorMessage}`);
              if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
              }
              setLoading(false);
              break;

            case 'complete':
              console.log('Search complete');
              addStreamLog('Search complete');
              if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
              }
              setLoading(false);
              break;

            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (err) {
          console.error('Error processing SSE message:', err, 'Raw data:', event.data);
          setError(`Error processing search results: ${err.message}`);
        }
      };

      eventSource.onerror = (err) => {
        console.error('SSE connection error:', err);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        setError('Connection error occurred. Please try again.');
        // Clean up storage on connection error
        cleanupStorage();
        setLoading(false);
      };

    } catch (err) {
      console.error('Error setting up SSE connection:', err);
      setError('Failed to connect to search stream');
      setLoading(false);
    }
  }, [baseUrl, query, presetValue, searchParams, runAnalysis, addStreamLog, cleanupStorage]);

  // Modify handleSearch to use setupSSE
  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setHasSearched(true);
    setResults([]);
    setGroqAnalysis('');
    setOpenAIAnalysis('');
    setTokensUsed(null);
    setError(null);
    setSearchLogs([]);

    // Update operation details
    setOperationDetails({
      type: "Advanced Hybrid Search",
      parameters: {
        query: query,
        preset: presetValue,
        ...searchParams,
        run_analysis: runAnalysis
      }
    });

    // Set up SSE connection
    setupSSE();
  }, [query, presetValue, searchParams, runAnalysis, setupSSE]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        console.log('Cleaning up SSE connection');
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  // Add this helper function at the top of your component
  const safeJsonParse = (str, fallback = null) => {
    try {
      return str ? JSON.parse(str) : fallback;
    } catch (e) {
      console.warn('Error parsing JSON:', e);
      return fallback;
    }
  };

  // Update the state loading effect
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

  // Update the state saving effect
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

  // Add cleanup to component unmount
  useEffect(() => {
    return () => {
      // Only cleanup if there was an error
      if (error) {
        cleanupStorage();
      }
    };
  }, [error, cleanupStorage]);

  const SearchLogs = ({ searchResults }) => {
    const { query, sections, searchParams, loading, operationDetails, analysisPreview } = searchResults;

    return (
      <div className="space-y-6">
        {/* Database Operation Card */}
        {sections && sections.length > 0 && (
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle>Database Operation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="font-medium">Operation Type:</p>
                  <p>{operationDetails?.type || "Advanced Hybrid Search"}</p>
                </div>
                <div>
                  <p className="font-medium">Parameters:</p>
                  <pre className="text-xs overflow-auto max-h-40 bg-gray-100 p-2 rounded">
                    {JSON.stringify(operationDetails?.parameters || searchParams, null, 2)}
                  </pre>
                </div>
                <div>
                  <p className="font-medium">Results Found:</p>
                  <p>{operationDetails?.resultsCount !== undefined ? operationDetails.resultsCount : sections.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Preview Card */}
        {analysisPreview && (
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle>Analysis Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p><strong>Results selected for analysis:</strong> {analysisPreview.result_count}</p>
                  <p><strong>Content length:</strong> {analysisPreview.total_content_length.toLocaleString()} characters</p>
                  {analysisPreview.results_for_analysis && (
                    <div className="mt-2">
                      <p><strong>Top sources for analysis:</strong></p>
                      <ul className="list-disc pl-5 text-sm">
                        {analysisPreview.results_for_analysis.slice(0, 3).map((result, index) => (
                          <li key={index} className="truncate">{result.source || result.url || 'Unknown source'}</li>
                        ))}
                        {analysisPreview.results_for_analysis.length > 3 && (
                          <li>...and {analysisPreview.results_for_analysis.length - 3} more</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
                <div>
                  <p className="font-medium">Estimated token usage:</p>
                  <div className="ml-4 space-y-2">
                    <div>
                      <p><strong>OpenAI:</strong></p>
                      <div className="ml-4">
                        <p>Input: {Math.round(analysisPreview.token_estimates.openai.input).toLocaleString()} tokens</p>
                        <p>Output: {analysisPreview.token_estimates.openai.output.toLocaleString()} tokens</p>
                        <p>Total: <span className={analysisPreview.token_estimates.openai.total > 15000 ? "text-red-500 font-bold" : ""}>
                          {Math.round(analysisPreview.token_estimates.openai.total).toLocaleString()} tokens
                        </span></p>
                      </div>
                    </div>
                    <div>
                      <p><strong>Groq:</strong></p>
                      <div className="ml-4">
                        <p>Input: {Math.round(analysisPreview.token_estimates.groq.input).toLocaleString()} tokens</p>
                        <p>Output: {analysisPreview.token_estimates.groq.output.toLocaleString()} tokens</p>
                        <p>Total: <span className={analysisPreview.token_estimates.groq.total > 8000 ? "text-red-500 font-bold" : ""}>
                          {Math.round(analysisPreview.token_estimates.groq.total).toLocaleString()} tokens
                        </span></p>
                      </div>
                    </div>
                  </div>
                  {(analysisPreview.token_estimates.openai.total > 15000 || analysisPreview.token_estimates.groq.total > 8000) && (
                    <p className="mt-2 text-red-500 text-sm">Warning: Estimated token count exceeds recommended limits. Results may be truncated.</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Table */}
        <div className="bg-gray-900/50 rounded-lg overflow-hidden border border-gray-800">
          <div className="p-4 border-b border-gray-800">
            <h3 className="text-yellow-400 font-semibold">Search Results</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Method</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Content</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-magenta-400 uppercase tracking-wider">Watch</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {sections.map((result, index) => (
                  <TableRow key={`result-${result.id || index}`} className="hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-sm ${
                        result.search_method === 'hybrid' ? 'bg-purple-400/10 text-purple-400' :
                        result.search_method === 'dot_product' ? 'bg-blue-400/10 text-blue-400' :
                        'bg-gray-400/10 text-gray-400'
                      }`}>
                        {result.search_method === 'hybrid' ? 'Hybrid' :
                         result.search_method === 'dot_product' ? 'Dot Product' :
                         result.search_method || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${
                            result.similarity > 0.8 ? 'bg-green-400' :
                            result.similarity > 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                          }`}></div>
                          <span className="text-cyan-400">{result.similarity.toFixed(3)}</span>
                        </div>
                        {result.priority_score && (
                          <div className="text-xs text-gray-400">
                            Priority: {result.priority_score.toFixed(2)}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <div className="text-green-400">{result.content}</div>
                        {result.summary && (
                          <div className="text-sm text-gray-400">
                            Summary: {result.summary}
                          </div>
                        )}
                        {result.has_context && (
                          <div className="flex gap-1 mt-1">
                            <span className="px-2 py-0.5 text-xs bg-blue-400/20 text-blue-400 rounded-full">
                              Has Context
                            </span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <span className="text-yellow-400 px-2 py-1 rounded-full bg-yellow-400/10 text-sm">
                          {result.source}
                        </span>
                        {result.video_title && (
                          <div className="text-sm text-gray-400">
                            {result.video_title}
                          </div>
                        )}
                        {result.word_count && (
                          <div className="text-xs text-gray-500">
                            Words: {result.word_count}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-2">
                        <span className="text-blue-400">
                          {result.start_time && result.end_time ? `${result.start_time} - ${result.end_time}` : 'N/A'}
                        </span>
                        {result.duration && (
                          <div className="text-xs text-gray-400">
                            Duration: {result.duration}
                          </div>
                        )}
                        {result.watch_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="mt-2 text-cyan-400 border-cyan-400/20 hover:bg-cyan-400/10"
                            onClick={() => window.open(result.watch_url, '_blank')}
                          >
                            <svg
                              className="w-4 h-4 mr-1"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                            Watch Video
                          </Button>
                        )}
                      </div>
                    </td>
                  </TableRow>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // Add AnalysisPreview component
  const AnalysisPreview = ({ preview }) => {
    if (!preview) return null;
    
    return (
      <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium mb-2">Analysis Preview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p><strong>Results for analysis:</strong> {preview.result_count}</p>
            <p><strong>Content length:</strong> {preview.total_content_length} characters</p>
          </div>
          <div>
            <p className="font-medium">Estimated token usage:</p>
            <div className="ml-4">
              <p><strong>OpenAI:</strong> {Math.round(preview.token_estimates.openai.input)} input + {preview.token_estimates.openai.output} output = {Math.round(preview.token_estimates.openai.total)} total</p>
              <p><strong>Groq:</strong> {Math.round(preview.token_estimates.groq.input)} input + {preview.token_estimates.groq.output} output = {Math.round(preview.token_estimates.groq.total)} total</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <h1 className="text-2xl font-bold mb-6">Semantic Vector Search</h1>
      
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }}>
          <div className="flex items-center mb-4">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query"
              className="flex-grow border rounded p-2 mr-4"
              required
            />
            <select
              value={presetValue}
              onChange={(e) => {
                setPresetValue(e.target.value);
                setSearchParams(searchPresets[e.target.value]);
              }}
              className="border rounded p-2 mr-4"
            >
              <option value="default">Default</option>
              <option value="technical">Technical</option>
              <option value="conceptual">Conceptual</option>
              <option value="balanced">Balanced</option>
            </select>
            <button 
              type="submit" 
              disabled={loading || !query.trim()}
              className={`bg-blue-500 text-white px-4 py-2 rounded ${loading ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-600"}`}
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
          
          <div className="flex items-center mb-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="run-analysis"
                checked={runAnalysis}
                onChange={(e) => setRunAnalysis(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="run-analysis" className="text-sm font-medium text-gray-700">
                Enable AI Analysis {runAnalysis ? '(Will analyze results)' : '(Will skip analysis)'}
              </label>
            </div>
          </div>
          
          {/* Preset Description */}
          <div className="mb-6 p-4 bg-gray-100 rounded-lg border border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Search Preset Guide</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-blue-600 font-medium block">Technical Details</span>
                <p className="text-gray-600">Best for finding specific technical information, code examples, or precise details. Uses higher thresholds and content weights.</p>
              </div>
              <div>
                <span className="text-blue-600 font-medium block">Conceptual Understanding</span>
                <p className="text-gray-600">Ideal for understanding high-level concepts, architecture, or system design. Emphasizes semantic and thematic matching.</p>
              </div>
              <div>
                <span className="text-blue-600 font-medium block">Balanced Search</span>
                <p className="text-gray-600">General-purpose search with equal emphasis on precision and recall. Good for exploratory searches.</p>
              </div>
              <div>
                <span className="text-blue-600 font-medium block">Default</span>
                <p className="text-gray-600">Standard configuration balancing all search aspects. Suitable for most queries.</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {/* Fine-grained Search Parameters */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-blue-700">Fine-grained Search Parameters</h3>
                <span className="text-xs text-green-600 px-2 py-1 rounded-full bg-green-50">High Precision</span>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="fine-grained-similarity" 
                      className="text-sm text-gray-700"
                    >
                      Similarity Threshold: {searchParams.fine_grained.similarity_threshold}
                    </label>
                    <div className="text-xs">
                      {searchParams.fine_grained.similarity_threshold > 0.8 ? (
                        <span className="text-green-600">Very Precise</span>
                      ) : searchParams.fine_grained.similarity_threshold > 0.6 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Broad</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="fine-grained-similarity"
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    value={searchParams.fine_grained.similarity_threshold}
                    onChange={(e) => handleParamChange('fine_grained', 'similarity_threshold', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Broader Results</span>
                    <span>More Precise</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="fine-grained-content-weight" 
                      className="text-sm text-gray-700"
                    >
                      Content Weight: {searchParams.fine_grained.content_weight}
                    </label>
                    <div className="text-xs">
                      {searchParams.fine_grained.content_weight > 0.7 ? (
                        <span className="text-green-600">Exact Matching</span>
                      ) : searchParams.fine_grained.content_weight > 0.4 ? (
                        <span className="text-yellow-600">Mixed</span>
                      ) : (
                        <span className="text-blue-600">Semantic</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="fine-grained-content-weight"
                    type="range"
                    min={0}
                    max={1}
                    step={0.1}
                    value={searchParams.fine_grained.content_weight}
                    onChange={(e) => handleParamChange('fine_grained', 'content_weight', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Semantic Matching</span>
                    <span>Exact Matching</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="fine-grained-max-results" 
                      className="text-sm text-gray-700"
                    >
                      Max Results: {searchParams.fine_grained.max_results}
                    </label>
                    <div className="text-xs">
                      {searchParams.fine_grained.max_results > 15 ? (
                        <span className="text-green-600">More Results</span>
                      ) : searchParams.fine_grained.max_results > 8 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Fewer Results</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="fine-grained-max-results"
                    type="range"
                    min={1}
                    max={30}
                    step={1}
                    value={searchParams.fine_grained.max_results}
                    onChange={(e) => handleParamChange('fine_grained', 'max_results', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Fewer Results</span>
                    <span>More Results</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Contextual Search Parameters */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-blue-700">Contextual Search Parameters</h3>
                <span className="text-xs text-purple-600 px-2 py-1 rounded-full bg-purple-50">Balanced</span>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="contextual-similarity" 
                      className="text-sm text-gray-700"
                    >
                      Similarity Threshold: {searchParams.contextual.similarity_threshold}
                    </label>
                    <div className="text-xs">
                      {searchParams.contextual.similarity_threshold > 0.8 ? (
                        <span className="text-green-600">Strong Context</span>
                      ) : searchParams.contextual.similarity_threshold > 0.6 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Loose Context</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="contextual-similarity"
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    value={searchParams.contextual.similarity_threshold}
                    onChange={(e) => handleParamChange('contextual', 'similarity_threshold', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Broader Context</span>
                    <span>Tighter Context</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="contextual-content-weight" 
                      className="text-sm text-gray-700"
                    >
                      Content Weight: {searchParams.contextual.content_weight}
                    </label>
                    <div className="text-xs">
                      {searchParams.contextual.content_weight > 0.7 ? (
                        <span className="text-green-600">Content Focus</span>
                      ) : searchParams.contextual.content_weight > 0.4 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Context Focus</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="contextual-content-weight"
                    type="range"
                    min={0}
                    max={1}
                    step={0.1}
                    value={searchParams.contextual.content_weight}
                    onChange={(e) => handleParamChange('contextual', 'content_weight', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Context Priority</span>
                    <span>Content Priority</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="contextual-max-results" 
                      className="text-sm text-gray-700"
                    >
                      Max Results: {searchParams.contextual.max_results}
                    </label>
                    <div className="text-xs">
                      {searchParams.contextual.max_results > 15 ? (
                        <span className="text-green-600">More Results</span>
                      ) : searchParams.contextual.max_results > 8 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Fewer Results</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="contextual-max-results"
                    type="range"
                    min={1}
                    max={30}
                    step={1}
                    value={searchParams.contextual.max_results}
                    onChange={(e) => handleParamChange('contextual', 'max_results', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Fewer Results</span>
                    <span>More Results</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Overview Search Parameters */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-blue-700">Overview Search Parameters</h3>
                <span className="text-xs text-blue-600 px-2 py-1 rounded-full bg-blue-50">Broad Insights</span>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="overview-similarity" 
                      className="text-sm text-gray-700"
                    >
                      Similarity Threshold: {searchParams.overview.similarity_threshold}
                    </label>
                    <div className="text-xs">
                      {searchParams.overview.similarity_threshold > 0.8 ? (
                        <span className="text-green-600">Focused Topics</span>
                      ) : searchParams.overview.similarity_threshold > 0.6 ? (
                        <span className="text-yellow-600">Mixed Topics</span>
                      ) : (
                        <span className="text-blue-600">Broad Topics</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="overview-similarity"
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    value={searchParams.overview.similarity_threshold}
                    onChange={(e) => handleParamChange('overview', 'similarity_threshold', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Related Topics</span>
                    <span>Specific Topics</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="overview-content-weight" 
                      className="text-sm text-gray-700"
                    >
                      Content Weight: {searchParams.overview.content_weight}
                    </label>
                    <div className="text-xs">
                      {searchParams.overview.content_weight > 0.7 ? (
                        <span className="text-green-600">Literal</span>
                      ) : searchParams.overview.content_weight > 0.4 ? (
                        <span className="text-yellow-600">Mixed</span>
                      ) : (
                        <span className="text-blue-600">Thematic</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="overview-content-weight"
                    type="range"
                    min={0}
                    max={1}
                    step={0.1}
                    value={searchParams.overview.content_weight}
                    onChange={(e) => handleParamChange('overview', 'content_weight', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Thematic Focus</span>
                    <span>Literal Focus</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label 
                      htmlFor="overview-max-results" 
                      className="text-sm text-gray-700"
                    >
                      Max Results: {searchParams.overview.max_results}
                    </label>
                    <div className="text-xs">
                      {searchParams.overview.max_results > 15 ? (
                        <span className="text-green-600">More Results</span>
                      ) : searchParams.overview.max_results > 8 ? (
                        <span className="text-yellow-600">Balanced</span>
                      ) : (
                        <span className="text-blue-600">Fewer Results</span>
                      )}
                    </div>
                  </div>
                  <input
                    id="overview-max-results"
                    type="range"
                    min={1}
                    max={30}
                    step={1}
                    value={searchParams.overview.max_results}
                    onChange={(e) => handleParamChange('overview', 'max_results', e.target.value)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Fewer Results</span>
                    <span>More Results</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
      
      {/* Search Logs */}
      {hasSearched && (
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-bold mb-4">Database Operation</h2>
          <div className="mb-4">
            <h3 className="font-bold mb-2">Operation Type:</h3>
            <p>{operationDetails?.type || "Advanced Hybrid Search"}</p>
          </div>
          <div className="mb-4">
            <h3 className="font-bold mb-2">Parameters:</h3>
            <pre className="bg-gray-100 p-2 rounded">
              {JSON.stringify(operationDetails?.parameters || searchParams, null, 2)}
            </pre>
          </div>
          <div>
            <h3 className="font-bold mb-2">Results:</h3>
            <p>{operationDetails?.resultsCount !== undefined ? operationDetails.resultsCount : results.length} matching sections found</p>
          </div>
          
          {/* Search Logs List */}
          {searchLogs.length > 0 && (
            <div className="mt-4">
              <h3 className="font-bold mb-2">Search Log:</h3>
              <ul className="list-disc pl-5">
                {searchLogs.map((log, index) => (
                  <li key={index}>{log.message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Results Display */}
      {hasSearched && results.length > 0 && (
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-bold mb-4">Search Results</h2>
          {results.map((result, index) => (
            <div key={index} className="border-b border-gray-200 mb-4 pb-4">
              <div className="flex justify-between">
                <span className="font-bold">Score: {result.similarity.toFixed(2)}</span>
                <span className="text-gray-500">{result.search_method || 'hybrid'}</span>
              </div>
              <p className="mt-2">{result.content}</p>
              <div className="mt-2 text-sm text-gray-500">
                <span>{result.source}</span>
                {result.start_time && (
                  <span className="ml-2">
                    Time: {result.start_time} - {result.end_time}
                  </span>
                )}
                {result.watch_url && (
                  <a 
                    href={result.watch_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-500"
                  >
                    Watch Video
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* AI Analysis Display */}
      {hasSearched && (openAIAnalysis || groqAnalysis) && (
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-bold mb-4">AI Analysis</h2>
          
          {openAIAnalysis && (
            <div className="mb-4">
              <h3 className="font-bold mb-2">OpenAI Analysis:</h3>
              <div className="bg-gray-100 p-3 rounded whitespace-pre-wrap">
                {openAIAnalysis}
              </div>
            </div>
          )}
          
          {groqAnalysis && (
            <div>
              <h3 className="font-bold mb-2">Groq Analysis:</h3>
              <div className="bg-gray-100 p-3 rounded whitespace-pre-wrap">
                {groqAnalysis}
              </div>
            </div>
          )}
          
          {tokensUsed && (
            <div className="mt-4">
              <h3 className="font-bold mb-2">Token Usage:</h3>
              <pre className="bg-gray-100 p-2 rounded">
                {JSON.stringify(tokensUsed, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
      
      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-100 text-red-700 p-4 rounded-lg">
          <h2 className="font-bold mb-2">Error:</h2>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}
