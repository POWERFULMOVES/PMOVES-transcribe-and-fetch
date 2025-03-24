"use client";

import React, { useEffect, useCallback, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image';

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ScrollArea,
  ScrollBar,
} from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { transcriptionReducer, initialState as transcriptionInitialState, ACTIONS } from './reducers/transcriptionReducer';
import { storage } from './utils/storage';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { permanentMarker, fZeroFont } from './fonts';
import { 
  BACKEND_URL,
  TRANSCRIPTION_STATUS,
  ALERT_TYPES 
} from '@/lib/constants';

const steps = [
  'Enter YouTube URL',
  'Process Video',
  'Transcribe Audio',
  'Transcription Complete'
];

export default function Home() {
  const [initialState, setInitialState] = useState(null);
  
  // Load state on mount
  useEffect(() => {
    const savedState = storage.get('transcriptionState');
    if (savedState) {
      setInitialState(savedState);
    }
  }, []);

  // Initialize reducer with loaded state
  const [state, dispatch] = useReducer(
    transcriptionReducer,
    {
      ...transcriptionInitialState,
      ...(initialState || {
        statusUpdates: [],
        transcriptionSegments: [],
        activeStep: 0,
        transcribing: false,
        error: null,
        loading: false,
        tabValue: 'status'
      })
    }
  );

  const [elapsedTime, setElapsedTime] = useState(0);
  const [activeTab, setActiveTab] = useState("status");
  const [backendStatus, setBackendStatus] = useState("unknown");
  const transcriptionBoxRef = useRef(null);
  const paperRef = useRef(null);
  let resizeObserver;
  let rafId;
  const statusBoxRef = useRef(null);

  // Define eventSource as a ref to keep state between renders
  const eventSource = useRef(null);

  // Function to manually check backend health
  const checkBackendHealth = async () => {
    setBackendStatus("checking");
    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: "Manually checking backend connection..." });
    
    try {
      // Try different endpoints with increasing timeouts
      const endpoints = [
        { url: BACKEND_URL, name: "root" },
        { url: `${BACKEND_URL}/health`, name: "health" }
      ];
      
      for (const endpoint of endpoints) {
        try {
          console.log(`Trying ${endpoint.name} endpoint at ${endpoint.url}`);
          const response = await fetch(endpoint.url, {
            method: 'GET',
            cache: 'no-store',
            headers: {
              'Cache-Control': 'no-cache',
              'Pragma': 'no-cache'
            },
            signal: AbortSignal.timeout(15000) // 15 second timeout
          });
          
          if (response.ok) {
            const data = await response.json();
            console.log(`${endpoint.name} endpoint success:`, data);
            setBackendStatus("connected");
            dispatch({ 
              type: ACTIONS.ADD_STATUS_UPDATE, 
              payload: `Backend connection successful via ${endpoint.name} endpoint` 
            });
            return true;
          }
        } catch (error) {
          console.error(`Error connecting to ${endpoint.name} endpoint:`, error);
        }
      }
      
      // If we get here, all attempts failed
      console.error("All backend connection attempts failed");
      setBackendStatus("error");
      dispatch({ 
        type: ACTIONS.ADD_STATUS_UPDATE, 
        payload: "All backend connection attempts failed. Please check that the server is running." 
      });
      return false;
    } catch (error) {
      console.error("Error in checkBackendHealth:", error);
      setBackendStatus("error");
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: `Backend connection error: ${error.message}` 
      });
      return false;
    }
  };

  // Function to set up Server-Sent Events connection
  const setupSSE = () => {
    // Close any existing connection
    if (eventSource.current) {
      console.log(`Closing existing SSE connection, readyState: ${eventSource.current.readyState}`);
      eventSource.current.close();
      eventSource.current = null;
    }

    // Create an abort controller with timeout
    const timeoutId = setTimeout(() => {
      console.log('SSE connection timed out');
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Connection to server timed out' 
      });
      
      // Stop transcribing if connection times out
      dispatch({ 
        type: ACTIONS.SET_TRANSCRIBING, 
        payload: false 
      });
    }, 30000); // 30 second timeout

    console.log(`Setting up new SSE connection to ${BACKEND_URL}/combined-updates at ${new Date().toISOString()}`);
    
    try {
      // Create a new EventSource connection with options
      eventSource.current = new EventSource(`${BACKEND_URL}/combined-updates`, { 
        withCredentials: true 
      });
      
      // Connection opened
      eventSource.current.onopen = (event) => {
        clearTimeout(timeoutId); // Clear timeout on successful connection
        console.log(`SSE connection opened successfully, readyState: ${eventSource.current.readyState}`);
        dispatch({ 
          type: ACTIONS.ADD_STATUS_UPDATE, 
          payload: 'Real-time updates connected' 
        });
      };
      
      // Message received
      eventSource.current.onmessage = (event) => {
        if (!event.data || event.data === '') {
          console.log('Empty SSE message received, ignoring');
          return;
        }
        
        try {
          const data = JSON.parse(event.data);
          console.log('SSE message received:', data);
          
          // Handle different message types
          if (data.type === 'status') {
            dispatch({ 
              type: ACTIONS.ADD_STATUS_UPDATE, 
              payload: data.content 
            });
          } else if (data.type === 'transcription_segment') {
            dispatch({ 
              type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT, 
              payload: data.content 
            });
          } else if (data.type === 'transcription_complete') {
            dispatch({ 
              type: ACTIONS.SET_TRANSCRIBING, 
              payload: false 
            });
            dispatch({ 
              type: ACTIONS.ADD_STATUS_UPDATE, 
              payload: 'Transcription completed' 
            });
          } else if (data.type === 'error') {
            dispatch({ 
              type: ACTIONS.SET_ERROR, 
              payload: data.content 
            });
          } else if (data.type === 'heartbeat') {
            console.log('Heartbeat received from server');
          }
        } catch (error) {
          console.error('Error parsing SSE message:', error, event.data);
        }
      };
      
      // Error handling with exponential backoff
      let retryCount = 0;
      const maxRetries = 3;
      
      eventSource.current.onerror = (error) => {
        console.error('SSE connection error:', error);
        
        if (retryCount < maxRetries) {
          const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
          retryCount++;
          
          console.log(`Attempting to reconnect SSE in ${delay}ms (attempt ${retryCount} of ${maxRetries})`);
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: `Connection error, retrying in ${delay / 1000} seconds...` 
          });
          
          setTimeout(setupSSE, delay);
        } else {
          console.error('Max SSE reconnection attempts reached');
          dispatch({ 
            type: ACTIONS.SET_ERROR, 
            payload: 'Failed to establish connection with server after multiple attempts' 
          });
          
          // Close the connection
          if (eventSource.current) {
            eventSource.current.close();
            eventSource.current = null;
          }
          
          // Stop transcribing
          dispatch({ 
            type: ACTIONS.SET_TRANSCRIBING, 
            payload: false 
          });
        }
      };
    } catch (setupError) {
      clearTimeout(timeoutId);
      console.error('Error setting up SSE connection:', setupError);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: `Error setting up SSE connection: ${setupError.message}` 
      });
    }
  };

  useEffect(() => {
    const handleResize = () => {
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
      rafId = window.requestAnimationFrame(() => {
        // Add your resize logic here if needed
      });
    };

    if (paperRef.current) {
      resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(paperRef.current);
    }

    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
    };
  }, []);

  // Validation functions
  const validateYoutubeUrl = (url) => {
    const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return regex.test(url);
  };

  const validateObsidianDir = (dir) => {
    return dir && dir.trim().length > 0;
  };

  // Input sanitization function
  const sanitizeInput = (input) => {
    return input.replace(/[<>]/g, "");
  };

  // Function to handle fetching content
  const handleFetchContent = async () => {
    const sanitizedFetchUrl = sanitizeInput(state.fetchUrl);

    if (!sanitizedFetchUrl.trim()) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: "Please enter a URL to fetch content." });
      return;
    }

    try {
      dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Fetching content...' });
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: ACTIONS.SET_ERROR, payload: null });

      const response = await axios.get(`${BACKEND_URL}/fetch-content`, {
        params: {
          url: sanitizedFetchUrl,
          json_response: state.jsonResponse,
          timeout: state.timeout,
          target_selector: state.targetSelector
        }
      });

      if (response.data.markdown_path) {
        try {
          const markdownResponse = await axios.get(`${BACKEND_URL}/fetch-markdown`, {
            params: { path: response.data.markdown_path }
          });

          const content = typeof markdownResponse.data === 'object' 
            ? JSON.stringify(markdownResponse.data, null, 2)
            : markdownResponse.data;

          dispatch({ 
            type: ACTIONS.SET_FETCH_RESULT, 
            payload: {
              markdown_content: content,
              markdown_path: response.data.markdown_path,
              pdf_path: response.data.pdf_path
            }
          });
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: 'Content fetched successfully.' 
          });
        } catch (markdownError) {
          console.error("Error fetching Markdown content:", markdownError);
          dispatch({ 
            type: ACTIONS.SET_ERROR, 
            payload: `Error fetching content: ${markdownError.message}` 
          });
        }
      } else {
        dispatch({ 
          type: ACTIONS.SET_ERROR, 
          payload: "No content found in response." 
        });
      }
    } catch (error) {
      console.error("Error fetching content:", error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: `Error: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

// Function to handle video processing
const handleProcessVideo = async () => {
  if (!state.youtubeUrl || !state.obsidianDir) {
    dispatch({
      type: ACTIONS.SET_ERROR,
      payload: "Please fill in all required fields"
    });
    return;
  }

  try {
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.SET_ERROR, payload: null });
    dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
    dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });

    // Make the initial request to start processing
    const response = await axios.post(`${BACKEND_URL}/process-video/`, {
      youtube_video_url: state.youtubeUrl,
      obsidian_dir: state.obsidianDir,
      output_folder: state.outputFolder,
      transcription_model: state.transcriptionModel, // This should be 'groq' or 'faster-whisper'
      use_groq: state.transcriptionModel === 'groq' // Explicitly set based on model selection
    });

    if (response.data && response.data.status === 'started') {
      dispatch({
        type: ACTIONS.ADD_STATUS_UPDATE,
        payload: "Video processing started successfully"
      });
    }

    // Rest of the function...
  } catch (error) {
    // Error handling...
  }
};

// Function to handle directory selection
const handleSelectOutputFolder = async () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.webkitdirectory = true;
  input.onchange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      const path = files[0].webkitRelativePath.split('/')[0];
      dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: path });
    }
  };
  input.click();
};

// Function to format elapsed time
const formatElapsedTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// Add this helper function for scrolling
const scrollToBottom = (elementRef) => {
  if (!elementRef.current) return;
  
  // Try multiple scroll approaches to ensure it works across browsers
  try {
    // Method 1: Direct parent scrolling
    const parent = elementRef.current.parentElement;
    if (parent) {
      parent.scrollTop = parent.scrollHeight;
    }
    
    // Method 2: Try scroll area if there is one
    const scrollArea = document.getElementById('transcription-scroll-area');
    if (scrollArea) {
      scrollArea.scrollTop = scrollArea.scrollHeight;
      
      // Also try viewport if exists
      const viewport = scrollArea.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight;
      }
    }
  } catch (error) {
    console.error('Error scrolling to bottom:', error);
  }
};

// Replace the existing useEffect for transcription scrolling with this improved version
useEffect(() => {
  // Only attempt to scroll if we have transcription segments and we're actively transcribing
  if (state.transcriptionSegments.length > 0 && state.transcribing) {
    // Use requestAnimationFrame to ensure the DOM has updated before scrolling
    requestAnimationFrame(() => {
      scrollToBottom(transcriptionBoxRef);
    });
  }
}, [state.transcriptionSegments, state.transcribing]);

  // Update the SSE handling
  useEffect(() => {
    // Set up SSE if transcribing
    if (state.transcribing) {
      setupSSE();
    }
    
    // Cleanup on unmount
    return () => {
      if (eventSource.current) {
        console.log("Component unmounting, closing SSE connection");
        eventSource.current.close();
        eventSource.current = null;
      }
    };
  }, [state.transcribing]); // Only re-run when transcribing state changes

  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log(`Testing connection to backend: ${BACKEND_URL}`);
        
        // Try the main endpoint
        const response = await axios.get(BACKEND_URL, {
          timeout: 20000, // 20 seconds timeout
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        console.log("Backend connected successfully:", response.data);
        
        dispatch({ 
          type: ACTIONS.ADD_STATUS_UPDATE, 
          payload: 'Backend connection test successful' 
        });
        
        if (response.data && response.data.status === 'ok') {
          console.log("Backend is ready");
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: `Backend ready: ${response.data.message}` 
          });
        }
      } catch (error) {
        console.error("Error connecting to backend:", error);
        
        // Try the health endpoint as fallback
        try {
          const healthResponse = await axios.get(`${BACKEND_URL}/health`, {
            timeout: 20000, // 20 seconds timeout
            headers: {
              'Cache-Control': 'no-cache',
              'Pragma': 'no-cache'
            }
          });
          
          if (healthResponse.data && healthResponse.data.status === 'healthy') {
            console.log("Health check successful:", healthResponse.data);
            dispatch({ 
              type: ACTIONS.ADD_STATUS_UPDATE, 
              payload: `Backend health check successful: ${healthResponse.data.message}` 
            });
            return;
          }
        } catch (healthError) {
          console.error("Health endpoint failed:", healthError);
          dispatch({ 
            type: ACTIONS.SET_ERROR, 
            payload: `Backend connection failed: ${error.message || 'Unknown error'}` 
          });
          
          // Display helpful instructions
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: 'Check if server is running by opening a terminal and running "cd backend/app" then "uvicorn main:app --reload"' 
          });
        }
      }
    };
    
    // Test connection immediately when component mounts
    testConnection();
  }, []);

  // Update the timer effect to properly handle transcription state
  useEffect(() => {
    let timer;
    if (state.transcribing) {
      console.log('Starting timer');
      setElapsedTime(0); // Reset timer when starting new transcription
      timer = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      console.log('Stopping timer');
      if (timer) {
        clearInterval(timer);
      }
    }
    
    return () => {
      if (timer) {
        console.log('Cleaning up timer');
        clearInterval(timer);
      }
    };
  }, [state.transcribing]);

  // Update the process video function
  const onProcessVideo = async () => {
    try {
      console.log("Starting video processing...");
      
      // Validate inputs
      if (!validateYoutubeUrl(state.youtubeUrl)) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Please enter a valid YouTube URL' });
        return;
      }

      // Reset state
      dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
      dispatch({ type: ACTIONS.SET_ERROR, payload: null });
      setElapsedTime(0);

      // Prepare request data
      const requestData = {
        youtube_video_url: state.youtubeUrl,
        obsidian_dir: state.obsidianDir,
        output_folder: state.outputFolder,
        transcription_model: state.transcriptionModel || "faster-whisper",
        use_groq: state.transcriptionModel === 'groq'  // Explicitly set based on model selection
      };

      console.log("Request data:", requestData);

      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
      dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 1 });
      dispatch({ 
        type: ACTIONS.ADD_STATUS_UPDATE, 
        payload: 'Starting video processing...' 
      });

      console.log("Sending request to backend...");
      const response = await axios.post(`${BACKEND_URL}/process-video/`, requestData);

      console.log("Process video response:", response.data);

      if (response.data.status === 'started') {
        dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 2 });
        console.log("Video processing started successfully");
      }

    } catch (error) {
      console.error("Error processing video:", error);
      const errorMessage = error.response?.data?.detail || error.message;
      dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
      dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
      setElapsedTime(0);
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Save state changes
  useEffect(() => {
    try {
      // Create a clean object with only serializable data
      const stateToSave = {
        transcribing: state.transcribing,
        statusUpdates: state.statusUpdates,
        transcriptionSegments: state.transcriptionSegments,
        activeStep: state.activeStep,
        youtubeUrl: state.youtubeUrl
      };
      
      storage.set('transcriptionState', stateToSave);
    } catch (error) {
      console.error('Error saving state to localStorage:', error);
    }
  }, [state]);

  // Add a check for ongoing transcription on mount
  useEffect(() => {
    const checkTranscriptionStatus = async () => {
      if (state.transcribing) {
        try {
          // Optionally check with backend if transcription is still running
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: 'Reconnecting to previous transcription...' 
          });
        } catch (error) {
          console.error('Error checking transcription status:', error);
          dispatch({ 
            type: ACTIONS.SET_TRANSCRIBING, 
            payload: false 
          });
          storage.remove('transcriptionState');
        }
      }
    };

    checkTranscriptionStatus();
  }, []);

  // Auto-scroll status updates to bottom
  useEffect(() => {
    if (statusBoxRef.current && state.statusUpdates.length > 0) {
      const scrollArea = statusBoxRef.current.parentElement;
      if (scrollArea) {
        setTimeout(() => {
          scrollArea.scrollTo({
            top: scrollArea.scrollHeight,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  }, [state.statusUpdates]);

  // Auto-scroll transcription to bottom
  useEffect(() => {
    if (transcriptionBoxRef.current && state.transcriptionSegments.length > 0) {
      const scrollArea = transcriptionBoxRef.current.parentElement;
      if (scrollArea) {
        setTimeout(() => {
          scrollArea.scrollTo({
            top: scrollArea.scrollHeight,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  }, [state.transcriptionSegments]);

  // Update the status display component to show model type
  const StatusUpdates = ({ updates, model }) => (
    <div className="space-y-2">
      {updates.map((update, index) => (
        <div key={index} className="text-sm">
          <span className={`${
            model === 'groq' 
              ? "text-blue-600 dark:text-blue-400"
              : "text-green-600 dark:text-green-400"
          }`}>
            {model === 'groq' ? '☁️ Groq Cloud: ' : '💻 Local Whisper: '}
          </span>
          {update}
        </div>
      ))}
    </div>
  );

  // Add this useEffect for handling transcription updates scroll
  useEffect(() => {
    if (transcriptionBoxRef.current) {
      const scrollArea = transcriptionBoxRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollArea) {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }
    }
  }, [state.transcriptionSegments]);

  // Add this for status updates scroll
  useEffect(() => {
    if (statusBoxRef.current) {
      const scrollArea = statusBoxRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollArea) {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }
    }
  }, [state.statusUpdates]);

  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [threshold, setThreshold] = useState(0.7);

  const handleVectorSearch = async () => {
    try {
      setSearchLoading(true);
      const response = await axios.post(`${BACKEND_URL}/vector-search`, {
        query,
        threshold
      });
      setSearchResults(response.data.results);
    } catch (error) {
      console.error('Error performing vector search:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  // Add this for more granular transcription handling
  const splitTranscriptionUpdates = (state, newSegment) => {
    if (!newSegment || newSegment.trim() === '') return state.transcriptionSegments;

    const cleanSegment = newSegment.trim();
    
    // If we don't have any segments yet, just add this one
    if (state.transcriptionSegments.length === 0) {
      return [cleanSegment];
    }
    
    // Get the last segment to check for updates
    const lastSegment = state.transcriptionSegments[state.transcriptionSegments.length - 1];
    
    // Check if the new segment is just a duplicate of the last one
    if (cleanSegment === lastSegment) {
      return state.transcriptionSegments;
    }
    
    // Check if new segment contains the previous one (common during incremental updates)
    if (cleanSegment.includes(lastSegment)) {
      return [
        ...state.transcriptionSegments.slice(0, -1),
        cleanSegment
      ];
    }
    
    // Check if we're starting a new sentence (previous ended with period, question mark, etc.)
    const lastChar = lastSegment.slice(-1);
    if (['.', '!', '?', ':'].includes(lastChar)) {
      return [...state.transcriptionSegments, cleanSegment];
    }
    
    // Otherwise, try to merge with previous segment for a smoother experience
    const mergedSegment = lastSegment + ' ' + cleanSegment;
    return [
      ...state.transcriptionSegments.slice(0, -1),
      mergedSegment
    ];
  };

  return (
    <>
      <main className="container mx-auto mt-8 p-4 max-w-3xl">
        {/* Progress Steps */}
        <Card className="glass-card mb-8">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center relative">
              {/* Progress Bar */}
              <div className="absolute top-1/2 left-0 right-0 h-1 bg-muted -translate-y-1/2">
                <div 
                  className="h-full gradient-progress transition-all duration-300"
                  style={{ 
                    width: `${(state.activeStep / (steps.length - 1)) * 100}%`,
                  }}
                />
              </div>
              
              {/* Step Circles */}
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col items-center relative z-10">
                  <div 
                    className={`
                      rounded-full w-8 h-8 flex items-center justify-center
                      transition-colors duration-300
                      ${state.activeStep >= index || 
                        (state.transcriptionSegments?.length > 0 && index === steps.length - 1)
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted text-muted-foreground'
                      }
                    `}
                  >
                    {index + 1}
                  </div>
                  <span 
                    className={`
                      text-sm mt-2 whitespace-nowrap
                      transition-colors duration-300
                      ${state.activeStep >= index || 
                        (state.transcriptionSegments?.length > 0 && index === steps.length - 1)
                        ? 'text-primary' 
                        : 'text-muted-foreground'
                      }
                    `}
                  >
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Form */}
        <Card>
          <CardContent className="space-y-4 pt-6">
            {/* Model Selection */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Transcription Model</Label>
                {state.transcriptionModel && (
                  <div className={`px-2 py-1 text-xs font-medium rounded-full ${
                    state.transcriptionModel === "groq" 
                      ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300" 
                      : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                  }`}>
                    {state.transcriptionModel === "groq" ? "☁️ CLOUD API" : "💻 LOCAL GPU"}
                  </div>
                )}
              </div>
              <Select
                value={state.transcriptionModel}
                onValueChange={(value) => dispatch({ 
                  type: ACTIONS.SET_TRANSCRIPTION_MODEL, 
                  payload: value 
                })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select transcription model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="faster-whisper">Faster Whisper (Uses local GPU)</SelectItem>
                  <SelectItem value="groq">Groq API (Cloud-based - saves GPU resources)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                {state.transcriptionModel === "groq" 
                  ? "Using Groq API will process audio in the cloud and preserve your GPU resources. Requires an OpenAI API key in the backend (.env file)." 
                  : "Using Faster Whisper will utilize your local GPU for transcription"}
              </p>
            </div>

            {/* YouTube URL Input */}
            <div className="space-y-2">
              <Label>YouTube Video URL</Label>
              <Input
                type="text"
                placeholder="Enter YouTube Video URL"
                value={state.youtubeUrl}
                onChange={(e) => dispatch({ type: ACTIONS.SET_YOUTUBE_URL, payload: e.target.value })}
              />
            </div>

            {/* Directory Input */}
            <div className="space-y-2">
              <Label>Save Directory</Label>
              <Input
                type="text"
                value={state.obsidianDir}
                onChange={(e) => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: e.target.value })}
              />
            </div>

            {/* Output Folder */}
            <div className="space-y-2">
              <Label>Output Folder</Label>
              <Input
                type="text"
                value={state.outputFolder}
                onChange={(e) => dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: e.target.value })}
              />
            </div>

            {/* Buttons */}
            <div className="space-y-2">
              <Button
                className="w-full"
                variant="outline"
                onClick={handleSelectOutputFolder}
              >
                Select Output Folder
              </Button>

              <Button
                className="w-full gradient-button"
                onClick={onProcessVideo}
                disabled={state.loading || !state.youtubeUrl}
              >
                {state.loading ? 'Processing...' : 'Process Video'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Output Section with Vertical Layout */}
        <div className="mt-8 space-y-4">
          {/* Status Updates Box */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Status Updates</CardTitle>
                {state.transcriptionModel && (
                  <div className={`px-3 py-1 text-xs font-bold rounded-full ${
                    state.transcriptionModel === "groq" 
                      ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300" 
                      : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                  }`}>
                    {state.transcriptionModel === "groq" 
                      ? "☁️ USING CLOUD PROCESSING" 
                      : "💻 USING LOCAL GPU"}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[250px] w-full rounded-md border p-4">
                <div ref={statusBoxRef} className="space-y-2">
                  <StatusUpdates updates={state.statusUpdates} model={state.transcriptionModel} />
                </div>
                <ScrollBar />
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Add this after the status updates box */}
          <div className="mt-4 flex justify-between items-center">
            <div>
              <span className="text-sm mr-2">Backend Status:</span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                backendStatus === "connected" ? "bg-green-100 text-green-800" :
                backendStatus === "error" ? "bg-red-100 text-red-800" :
                backendStatus === "checking" ? "bg-yellow-100 text-yellow-800" :
                "bg-gray-100 text-gray-800"
              }`}>
                {backendStatus === "connected" ? "Connected" :
                 backendStatus === "error" ? "Connection Error" :
                 backendStatus === "checking" ? "Checking..." :
                 "Unknown"}
              </span>
            </div>
            
            <Button 
              size="sm" 
              variant="outline" 
              onClick={checkBackendHealth} 
              disabled={backendStatus === "checking"}
            >
              {backendStatus === "checking" ? "Checking..." : "Check Connection"}
            </Button>
          </div>

          {/* Live Transcription Box - Resizable */}
          <Card>
            <CardHeader className="flex flex-row justify-between items-center pb-2">
              <CardTitle>Live Transcription</CardTitle>
              <div className="flex items-center space-x-2">
                {state.transcriptionModel && (
                  <div className={`px-2 py-1 text-xs font-medium rounded-full ${
                    state.transcriptionModel === "groq" 
                      ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300" 
                      : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                  }`}>
                    {state.transcriptionModel === "groq" ? "☁️ CLOUD API" : "💻 LOCAL GPU"}
                  </div>
                )}
                {state.transcribing && (
                  <span className="animate-pulse text-primary flex items-center">
                    <span className="mr-2">●</span> Transcribing... {formatElapsedTime(elapsedTime)}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="resize-y overflow-auto min-h-[250px] h-[400px] max-h-[800px]">
                <ScrollArea className="h-full w-full rounded-md border p-4" id="transcription-scroll-area">
                  <div ref={transcriptionBoxRef} className="space-y-1 relative">
                    {state.transcriptionSegments.length > 0 ? (
                      state.transcriptionSegments.map((segment, index) => (
                        <div 
                          key={index} 
                          className={`text-sm py-1 transition-all duration-150 ${
                            index === state.transcriptionSegments.length - 1 && state.transcribing 
                              ? 'border-l-2 border-primary pl-2 font-medium' 
                              : 'pl-2'
                          }`}
                        >
                          {segment}
                          {index === state.transcriptionSegments.length - 1 && state.transcribing && (
                            <span className="inline-block w-1.5 h-4 bg-primary ml-0.5 animate-pulse-fast"></span>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-muted-foreground text-center p-4">
                        {state.transcribing ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-pulse">Waiting for transcription to begin</div>
                            <span className="ml-1 inline-flex">
                              <span className="animate-[bounce_1s_infinite_100ms] mr-0.5">.</span>
                              <span className="animate-[bounce_1s_infinite_200ms] mr-0.5">.</span>
                              <span className="animate-[bounce_1s_infinite_300ms]">.</span>
                            </span>
                          </div>
                        ) : (
                          "No transcription data available. Click 'Process Video' to start."
                        )}
                      </div>
                    )}
                  </div>
                  <ScrollBar />
                </ScrollArea>
              </div>
            </CardContent>
          </Card>

          {/* Web Pages Tab Content - Keep as is */}
          <Card className={activeTab === 'webpages' ? '' : 'hidden'}>
            {/* URL Input */}
            <div className="space-y-2">
              <Label>URL to Fetch</Label>
              <Input
                placeholder="Enter URL to fetch"
                value={state.fetchUrl}
                onChange={(e) => dispatch({ type: ACTIONS.SET_FETCH_URL, payload: e.target.value })}
              />
            </div>

            {/* Advanced Options Accordion */}
            <Accordion type="single" collapsible>
              <AccordionItem value="advanced-options">
                <AccordionTrigger>Advanced Options</AccordionTrigger>
                <AccordionContent>
                  {/* Target Selector */}
                  <div className="space-y-2 mb-4">
                    <Label>Target Selector</Label>
                    <Input
                      placeholder="CSS Selector (e.g., article, .main-content)"
                      value={state.targetSelector}
                      onChange={(e) => dispatch({ 
                        type: ACTIONS.SET_TARGET_SELECTOR, 
                        payload: e.target.value 
                      })}
                    />
                    <p className="text-sm text-muted-foreground">
                      Specify elements to extract (e.g., article, .main-content)
                    </p>
                  </div>

                  {/* Excluded Selector */}
                  <div className="space-y-2 mb-4">
                    <Label>Exclude Elements</Label>
                    <Input
                      placeholder="Elements to exclude (e.g., nav, footer, .ads)"
                      value={state.excludedSelector}
                      onChange={(e) => dispatch({ 
                        type: ACTIONS.SET_EXCLUDED_SELECTOR, 
                        payload: e.target.value 
                      })}
                    />
                    <p className="text-sm text-muted-foreground">
                      Specify elements to remove (e.g., nav, footer, .ads)
                    </p>
                  </div>

                  {/* Timeout Setting */}
                  <div className="space-y-2 mb-4">
                    <Label>Timeout (seconds)</Label>
                    <Input
                      type="number"
                      min="0"
                      max="300"
                      value={state.timeout}
                      onChange={(e) => dispatch({ 
                        type: ACTIONS.SET_TIMEOUT, 
                        payload: e.target.value 
                      })}
                    />
                  </div>

                  {/* Response Format */}
                  <div className="space-y-2">
                    <Label>Response Format</Label>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="json-mode"
                          checked={state.jsonResponse}
                          onCheckedChange={(checked) => dispatch({ 
                            type: ACTIONS.SET_JSON_RESPONSE, 
                            payload: checked 
                          })}
                        />
                        <Label htmlFor="json-mode">JSON Response</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="clean-mode"
                          checked={state.cleanFormat}
                          onCheckedChange={(checked) => dispatch({ 
                            type: ACTIONS.SET_CLEAN_FORMAT, 
                            payload: checked 
                          })}
                        />
                        <Label htmlFor="clean-mode">Clean Format</Label>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            {/* Fetch Button */}
            <Button
              onClick={handleFetchContent}
              disabled={state.loading}
              className="w-full gradient-button"
            >
              {state.loading ? 'Fetching...' : 'Fetch Content'}
            </Button>

            {/* Results Display */}
            <ScrollArea className="h-[400px] w-full rounded-md border p-4">
              {state.fetchResult ? (
                <div className="space-y-4">
                  {/* Tabs for switching between Markdown and PDF */}
                  <Tabs defaultValue="markdown" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="markdown">Markdown View</TabsTrigger>
                      <TabsTrigger value="pdf">PDF View</TabsTrigger>
                    </TabsList>

                    <TabsContent value="markdown">
                      {/* Markdown Content Display */}
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown 
                          components={{
                            h1: ({node, ...props}) => (
                              <h1 className="text-2xl font-bold mb-4" {...props} />
                            ),
                            h2: ({node, ...props}) => (
                              <h2 className="text-xl font-semibold mb-3" {...props} />
                            ),
                            a: ({node, ...props}) => (
                              <a 
                                className="text-primary hover:underline" 
                                target="_blank"
                                rel="noopener noreferrer"
                                {...props}
                              />
                            ),
                            p: ({node, ...props}) => (
                              <p className="mb-4 leading-relaxed" {...props} />
                            ),
                            ul: ({node, ...props}) => (
                              <ul className="list-disc list-inside mb-4" {...props} />
                            ),
                            li: ({node, ...props}) => (
                              <li className="mb-2" {...props} />
                            ),
                          }}
                        >
                          {typeof state.fetchResult.markdown_content === 'object' 
                            ? JSON.stringify(state.fetchResult.markdown_content, null, 2)
                            : state.fetchResult.markdown_content || 'No content fetched yet.'
                          }
                        </ReactMarkdown>
                      </div>
                    </TabsContent>

                    <TabsContent value="pdf" className="h-full">
                      {/* PDF Viewer */}
                      {state.fetchResult?.pdf_path ? (
                        <div className="w-full min-h-[600px] relative bg-white rounded-md shadow">
                          <iframe
                            src={`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`}
                            className="w-full h-full absolute inset-0 rounded-md"
                            title="PDF Viewer"
                            onError={(e) => {
                              console.error("PDF loading error:", e);
                              dispatch({ 
                                type: ACTIONS.SET_ERROR, 
                                payload: "Error loading PDF. Please try downloading instead." 
                              });
                            }}
                          />
                          <div className="absolute top-4 right-4 space-x-2 z-10">
                            <Button
                              onClick={() => window.open(`${BACKEND_URL}/download-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`, '_blank')}
                              variant="secondary"
                              size="sm"
                              className="bg-white/90 hover:bg-white"
                            >
                              Download PDF
                            </Button>
                            <Button
                              onClick={() => window.open(`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`, '_blank')}
                              variant="secondary"
                              size="sm"
                              className="bg-white/90 hover:bg-white"
                            >
                              Open in New Tab
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <p>PDF is being generated...</p>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>

                  {/* File Info Footer */}
                  <div className="mt-4 p-3 bg-muted rounded-md text-sm space-y-2">
                    {state.fetchResult.markdown_path && (
                      <p className="text-muted-foreground">
                        📄 Markdown: {state.fetchResult.markdown_path}
                      </p>
                    )}
                    {state.fetchResult.pdf_path && (
                      <p className="text-muted-foreground">
                        📑 PDF: {state.fetchResult.pdf_path}
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>Enter a URL above and click "Fetch Content" to get started</p>
                </div>
              )}
              <ScrollBar />
            </ScrollArea>
          </Card>
        </div>

        {/* Vector Search Tab */}
        <Card className={activeTab === 'vector-search' ? '' : 'hidden'}>
          <CardHeader>
            <CardTitle>Vector Search</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Enter your search query..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
                <Button 
                  onClick={handleVectorSearch} 
                  disabled={searchLoading}
                  className="min-w-[100px]"
                >
                  {searchLoading ? 'Searching...' : 'Search'}
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Similarity Threshold: {threshold}</Label>
                  <Slider
                    value={[threshold]}
                    onValueChange={(value) => setThreshold(value[0])}
                    min={0}
                    max={1}
                    step={0.1}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {searchResults.length > 0 && (
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Video ID</TableHead>
                      <TableHead>Time Range</TableHead>
                      <TableHead>Text</TableHead>
                      <TableHead>Similarity</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {searchResults.map((result, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{result.video_id}</TableCell>
                        <TableCell>{result.start_time} - {result.end_time}</TableCell>
                        <TableCell className="max-w-md truncate">{result.text}</TableCell>
                        <TableCell>{(result.similarity * 100).toFixed(2)}%</TableCell>
                        <TableCell>
                          {result.watch_url && (
                            <Button
                              variant="outline"
                              size="sm"
                              asChild
                            >
                              <a
                                href={result.watch_url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                Watch
                              </a>
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            )}
          </CardContent>
        </Card>

        {/* Error Display */}
        {state.error && (
          <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
            <p className="font-semibold">Error:</p>
            <p>{state.error}</p>
          </div>
        )}
      </main>
    </>
  );
}