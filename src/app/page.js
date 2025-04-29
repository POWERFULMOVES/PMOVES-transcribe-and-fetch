// --- START OF COMPLETE page.js with fixes ---

"use client";

import React, { useEffect, useCallback, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image'; // Assuming you might use this later
import useSSE from '@/hooks/useSSE'; // Correct path assuming hooks folder at src level

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
  CardDescription // Added import
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
// Ensure correct path to reducer and constants
import { transcriptionReducer, initialState as transcriptionInitialState, ACTIONS } from './reducers/transcriptionReducer'; // Assuming reducer is in the same folder structure
import { storage } from './utils/storage'; // Assuming utils is in the same folder structure
import { SSE_CONFIG } from '@/lib/constants'; // Import SSE configuration
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
// Assuming fonts are configured elsewhere or remove if not used directly here
// import { permanentMarker, fZeroFont } from './fonts';
import {
  BACKEND_URL
} from '@/lib/constants'; // Assuming lib folder at src level

// Transcription styling constants
const TRANSCRIPTION_STYLES = {
  groq: {
    icon: '☁️',
    color: 'blue',
    border: 'blue-200',
    content_color: 'blue-700',
    title: 'Groq Cloud Transcription',
    hover: 'hover:bg-blue-50 dark:hover:bg-blue-900/20'
  },
  'faster-whisper': {
    icon: '💻',
    color: 'green',
    border: 'green-200',
    content_color: 'green-700',
    title: 'Local Whisper Transcription',
    hover: 'hover:bg-green-50 dark:hover:bg-green-900/20'
  },
  default: {
    icon: '🎙️',
    color: 'gray',
    border: 'gray-200',
    content_color: 'gray-700',
    title: 'Transcription',
    hover: 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
  }
};

// --- Helper Functions ---
// Function to format elapsed time
const formatElapsedTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// Function to format timestamps (e.g., 00:12.34)
const formatTimeStamp = (seconds) => {
  if (isNaN(seconds) || seconds < 0) return '00:00.00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 100);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(2, '0')}`;
};

// Helper for scrolling
const scrollToBottom = (elementRef) => {
    if (!elementRef.current) return;
    // Use requestAnimationFrame to ensure DOM is updated before scrolling
    requestAnimationFrame(() => {
        const scrollContainer = elementRef.current.closest('[data-radix-scroll-area-viewport]') || elementRef.current.parentElement;
        if (scrollContainer) {
            scrollContainer.scrollTo({
                top: scrollContainer.scrollHeight,
                behavior: 'auto'
            });
        }
    });
};

// Validation functions
const validateYoutubeUrl = (url) => {
  const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
  return regex.test(url);
};

const validateObsidianDir = (dir) => {
  // Basic check: not empty. A more robust check might involve backend validation if possible.
  return dir && dir.trim().length > 0;
};

// Input sanitization function (basic example)
const sanitizeInput = (input) => {
  // Prevent basic script injection attempts. Consider a more robust library if needed.
  if (typeof input !== 'string') return '';
  // Corrected basic sanitization
  return input.replace(/</g, "<").replace(/>/g, ">");
};

// Generate YouTube watch URL from video URL and timestamp
const generateWatchUrl = (videoUrl, startSeconds) => {
  if (!videoUrl) return '';

  // Extract video ID from YouTube URL
  const videoIdMatch = videoUrl.match(/(?:v=|\/)([a-zA-Z0-9_-]{11})(?:\?|&|$|\/)/);
  const videoId = videoIdMatch ? videoIdMatch[1] : '';

  if (!videoId) return '';

  // Create timestamped URL if startSeconds is provided
  const timestamp = startSeconds && !isNaN(startSeconds) ? `&t=${Math.floor(startSeconds)}` : '';
  return `https://www.youtube.com/watch?v=${videoId}${timestamp}`;
};

// Validate transcription segment data
const isValidSegment = (segment) => {
  console.log('[isValidSegment] Validating segment:', segment);

  // Check if segment has required fields
  if (!segment) {
    console.warn('[isValidSegment] Segment is null or undefined');
    return false;
  }

  // Handle different segment formats
  // Some backends send segment data directly, others nest it under 'content'
  const segmentData = segment.content && typeof segment.content === 'object' ? segment.content : segment;

  // Check if text is valid - handle different property names (text or Text)
  const segmentText = segmentData.text || segmentData.Text || '';
  if (!segmentText) {
    console.warn('[isValidSegment] Segment has no text property');
    // Try to extract text from a markdown-formatted string if present
    if (typeof segmentData === 'string' && segmentData.includes('|')) {
      // This might be a markdown table row, try to extract text
      const parts = segmentData.split('|');
      if (parts.length >= 6) { // Assuming format: | timestamp | id | start | end | text |
        segmentData.text = parts[5].trim();
        console.log('[isValidSegment] Extracted text from markdown:', segmentData.text);
      } else {
        console.warn('[isValidSegment] Could not extract text from string format');
        return false;
      }
    } else {
      console.warn('[isValidSegment] No text found in segment');
      return false;
    }
  }

  if (typeof segmentText !== 'string') {
    console.warn('[isValidSegment] Segment text is not a string:', typeof segmentText);
    return false;
  }

  if (segmentText.trim() === '') {
    console.warn('[isValidSegment] Segment text is empty after trimming');
    return false;
  }

  // Ensure segment has the text property directly
  if (!segment.text) {
    segment.text = segmentText;
  }

  // Handle different time property names (start_time, start, startTime, etc.)
  let startTime = segmentData.start_time || segmentData.start || segmentData.startTime || segmentData.start_seconds || 0;
  let endTime = segmentData.end_time || segmentData.end || segmentData.endTime || segmentData.end_seconds || 0;

  // Convert string timestamps to numbers if needed
  if (typeof startTime === 'string') {
    // Check if it's a formatted timestamp like "00:01:23"
    if (startTime.includes(':')) {
      // Convert HH:MM:SS format to seconds
      const parts = startTime.split(':');
      if (parts.length === 3) {
        startTime = parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseFloat(parts[2]);
      } else if (parts.length === 2) {
        startTime = parseInt(parts[0]) * 60 + parseFloat(parts[1]);
      }
    } else {
      startTime = parseFloat(startTime) || 0;
    }
  }

  if (typeof endTime === 'string') {
    // Check if it's a formatted timestamp like "00:01:23"
    if (endTime.includes(':')) {
      // Convert HH:MM:SS format to seconds
      const parts = endTime.split(':');
      if (parts.length === 3) {
        endTime = parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseFloat(parts[2]);
      } else if (parts.length === 2) {
        endTime = parseInt(parts[0]) * 60 + parseFloat(parts[1]);
      }
    } else {
      endTime = parseFloat(endTime) || 0;
    }
  }

  // Ensure start_time is valid
  if (isNaN(startTime) || startTime < 0) {
    console.warn('[isValidSegment] Invalid start_time, using 0:', startTime);
    startTime = 0;
  }

  // Ensure end_time is valid
  if (isNaN(endTime) || endTime <= 0) {
    console.warn('[isValidSegment] Invalid end_time, using start_time + 1:', endTime);
    endTime = startTime + 1;
  }

  // Ensure end_time is greater than or equal to start_time
  if (endTime < startTime) {
    console.warn('[isValidSegment] end_time < start_time, fixing:', endTime, '<', startTime);
    endTime = startTime + 1;
  }

  // Update the segment with normalized values
  segment.start_time = startTime;
  segment.end_time = endTime;

  // Ensure watch_url is present if video_id is available
  if (segmentData.video_id && !segment.watch_url && startTime >= 0) {
    segment.watch_url = `https://www.youtube.com/watch?v=${segmentData.video_id}&t=${Math.floor(startTime)}`;
  }

  // Ensure id is present
  if (!segment.id && segmentData.id) {
    segment.id = segmentData.id;
  }

  console.log('[isValidSegment] Segment is valid after normalization:', segment);
  return true;
};


// --- Components ---

// Status Updates Component
const StatusUpdates = ({ updates, model }) => {
    // Filter out duplicate updates and limit to the most recent 100 updates
    const uniqueUpdates = updates
        .filter((update, index, self) => {
            // Keep only the first occurrence of each update
            return self.indexOf(update) === index;
        })
        .slice(-100); // Only show the most recent 100 updates

    return (
        <div className="space-y-2">
            {uniqueUpdates.map((update, index) => (
                <div key={index} className="text-sm flex items-start">
                    <span className={`mr-2 ${model === 'groq' ? "text-blue-600 dark:text-blue-400" : "text-green-600 dark:text-green-400"}`}>
                        {model === 'groq' ? '☁️' : '💻'}
                    </span>
                    {/* Ensure update content is displayed correctly */}
                    <span className="flex-1">{typeof update === 'object' ? JSON.stringify(update) : update}</span>
                </div>
            ))}
        </div>
    );
};

// Transcription Segment Component
const TranscriptionSegment = ({ segment, index, isLatest, isTranscribing, model }) => {
    
    const style = TRANSCRIPTION_STYLES[model] || TRANSCRIPTION_STYLES.default;
    const duration = segment.end_time && segment.start_time && !isNaN(segment.end_time) && !isNaN(segment.start_time)
        ? (segment.end_time - segment.start_time).toFixed(2) + 's'
        : '';

    return (
        <div className={
            `group relative rounded-lg p-3 transition-colors ` +
            (style.border === 'blue-200' ? 'border-blue-200 hover:bg-blue-50 dark:hover:bg-blue-900/20 ' : '') +
            (style.border === 'green-200' ? 'border-green-200 hover:bg-green-50 dark:hover:bg-green-900/20 ' : '') +
            (style.border === 'gray-200' ? 'border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800/50 ' : '')
        }>
            {/* Header with timestamp and watch link */}
            <div className="flex justify-between items-center mb-1 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                    <span>{style.icon}</span>
                    <span>
                        {/* Use formatTimeStamp for start and end times */}
                        {formatTimeStamp(segment.start_time)} - {formatTimeStamp(segment.end_time)}
                        {duration && ` (${duration})`}
                    </span>
                </div>

                {/* Watch link */}
                {segment.watch_url && (
                    <a
                        href={segment.watch_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`opacity-0 group-hover:opacity-100 transition-opacity text-${style.color}-600 hover:underline flex items-center`}
                        title="Watch segment on YouTube"
                    >
                        <span className="mr-1">Watch</span>
                        {/* External Link Icon */}
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                )}
            </div>

            {/* Transcription text */}
            <div className={
                `text-sm sm:text-base leading-relaxed ` +
                (style.content_color === 'blue-700' ? 'text-blue-700 dark:text-blue-300 ' : '') +
                (style.content_color === 'green-700' ? 'text-green-700 dark:text-green-300 ' : '') +
                (style.content_color === 'gray-700' ? 'text-gray-700 dark:text-gray-300 ' : '')
            }>
                {segment.text}
                {isLatest && isTranscribing && (
                    <span className={
                        `inline-block w-1.5 h-4 ml-0.5 animate-pulse-fast align-middle ` +
                        (style.color === 'blue' ? 'bg-blue-500 ' : '') +
                        (style.color === 'green' ? 'bg-green-500 ' : '') +
                        (style.color === 'gray' ? 'bg-gray-500 ' : '')
                    }></span>
                )}
            </div>
        </div>
    );
};

// --- Main Component ---
export default function Home() {
  // --- State, Reducer, and Refs Initialization (must come first!) ---
  // Use state for initial state to trigger reducer initialization after mount
  const [initialStateLoaded, setInitialStateLoaded] = useState(false);
  const [persistedState, setPersistedState] = useState(null);
  // Load state on mount
  useEffect(() => {
    const savedState = storage.get('transcriptionState');
    if (savedState) {
      setPersistedState(savedState);
    }
    setInitialStateLoaded(true); // Indicate that loading attempt is complete
  }, []);
  // Initialize reducer only after attempting to load persisted state
  const [state, dispatch] = useReducer(
    transcriptionReducer,
    persistedState || transcriptionInitialState
  );
  const messageBuffer = useRef([]);
  const bufferTimeoutRef = useRef(null);
  const BATCH_DELAY = 150; // Process buffer every 150ms
  const initialCheckDoneRef = useRef(false);

  // --- Timer State ---
  const [timerActive, setTimerActive] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [activeTab, setActiveTab] = useState("transcription"); // Default to transcription tab
  const [backendStatus, setBackendStatus] = useState("unknown");

  const transcriptionBoxRef = useRef(null);
  const statusBoxRef = useRef(null);
  const disconnectTimeoutRef = useRef(null);
  const scrollAreaRef = useRef(null); // Add ref for ScrollArea

  // --- Timer Effects ---

  // Start/stop timer based on transcription state
  useEffect(() => {
    // Only start the timer if we're actively transcribing AND have at least one segment
    const shouldRunTimer = state.transcribing && state.transcriptionSegments.length > 0;

    if (shouldRunTimer && !timerActive) {
      console.log('[page.js] Setting timer active - transcribing and have segments');
      setTimerActive(true);
    } else if (!state.transcribing && timerActive) {
      console.log('[page.js] Setting timer inactive - no longer transcribing');
      setTimerActive(false);
    }
    // Reset elapsed time whenever transcription starts or stops
    // Or maybe only when it stops?
    if (!state.transcribing) {
        setElapsedTime(0);
    }

  }, [state.transcribing, state.transcriptionSegments.length, timerActive]);

  // Actual timer implementation
  useEffect(() => {
    let timer;

    if (timerActive) {
      console.log('[page.js] Starting timer interval');
      timer = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      console.log('[page.js] Timer is inactive');
    }

    return () => {
      if (timer) {
        console.log('[page.js] Cleaning up timer interval');
        clearInterval(timer);
      }
    };
  }, [timerActive]); // Only rerun when timerActive changes

  // --- FIX 1: DEFINE STEPS ARRAY ---
  const steps = [
    'Enter YouTube URL',
    'Process Video',
    'Transcribe Audio',
    'Transcription Complete'
  ];
  // --- END OF FIX 1 ---

  // --- Backend Health Check ---
  const checkBackendHealth = useCallback(async () => {
    setBackendStatus("checking");
    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: "Checking backend connection..." });

    try {
        const endpoints = [
            { url: `${BACKEND_URL}/`, name: "root" },
            { url: `${BACKEND_URL}/health`, name: "health" }
        ];
        let connected = false;
        for (const endpoint of endpoints) {
            try {
                console.log(`Trying endpoint: ${endpoint.url}`);
                const response = await axios.get(endpoint.url, {
                    timeout: 15000, // 15 seconds
                     headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
                });
                if (response.status === 200) {
                    console.log(`${endpoint.name} endpoint success:`, response.data);
                    setBackendStatus("connected");
                    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Backend connection successful (${endpoint.name})` });
                    connected = true;
                    break; // Stop checking once connected
                }
            } catch (endpointError) {
                 console.warn(`Endpoint ${endpoint.url} failed: ${endpointError.message}`);
            }
        }
        if (!connected) {
            throw new Error("All backend connection attempts failed.");
        }
        return connected;
    } catch (error) {
        console.error("Error checking backend health:", error);
        setBackendStatus("error");
        dispatch({ type: ACTIONS.SET_ERROR, payload: `Backend connection error: ${error.message}` });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Backend connection failed. Please ensure the server is running.'});
        return false;
    }
  }, [dispatch]); // dispatch is stable, no need to list ACTIONS

  // Run health check on mount
  useEffect(() => {
      checkBackendHealth();

      // Cleanup function to clear any timeouts when the component unmounts
      return () => {
        if (disconnectTimeoutRef.current) {
          clearTimeout(disconnectTimeoutRef.current);
          disconnectTimeoutRef.current = null;
        }
      };
  }, [checkBackendHealth]); // Run once on mount

  // --- SSE Hook Setup ---
  const {
    connected: sseConnected,
    error: sseError,
    connect: connectSSE,
    disconnect: disconnectSSE
  } = useSSE('/combined-updates', { // Ensure this endpoint matches backend
    autoConnect: false,
    withCredentials: true,
    maxRetries: SSE_CONFIG.MAX_RETRIES,
    reconnectDelay: SSE_CONFIG.RECONNECT_DELAY,
    timeout: SSE_CONFIG.TIMEOUT,
    onConnect: () => {
      console.log('[page.js] SSE connection established');
      dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Real-time updates connected' });
    },
    onMessage: (data) => {
      console.log('[useSSE.onMessage] Received:', data);
      // Use the window reference to avoid circular dependency
      if (window.onMessageOptimized) {
        window.onMessageOptimized(data);
      } else {
        // Fallback to direct dispatch if optimized handler is not available
        if (data.type === 'status') {
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: data.content });
        }
      }
    },
    onError: (error) => {
      console.error('[page.js] SSE connection error:', error);
      dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Connection error: ${error.message || 'Unknown error'}` });
    },
    onDisconnect: (error) => {
      console.log(`[page.js] SSE connection closed. ${error ? `Reason: ${error.message}` : 'Manual disconnect or completion.'}`);
      if (error && state.transcribing) {
        dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Connection to server lost: ${error.message}` });
      }
    }
  });

  // Main cleanup effect that runs on component unmount
  useEffect(() => {
    // Generate a unique ID for this component instance
    const componentId = Math.random().toString(36).substring(2, 9);
    console.log(`[page.js] Component instance ${componentId} mounted`);

    return () => {
      console.log(`[page.js] Component instance ${componentId} unmounting`);

      // Clean up all timeouts
      if (bufferTimeoutRef.current) {
        clearTimeout(bufferTimeoutRef.current);
        bufferTimeoutRef.current = null;
      }

      // Explicitly disconnect SSE on actual component unmount
      if (sseConnected) {
        console.log(`[page.js] Component instance ${componentId} unmounting, disconnecting SSE`);
        disconnectSSE();
      }
    };
  }, []); // Empty dependency array ensures this only runs on mount/unmount

  // --- SSE Connection Management ---
  useEffect(() => {
    // Check if we need to connect on page load/refresh
    const checkForActiveTranscription = async () => {
      try {
        console.log("[page.js] Checking for active transcription on backend...");
        // Check if there's an active transcription by calling the backend
        const response = await fetch(`${BACKEND_URL}/transcription-status`, {
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        });
        const data = await response.json();
        console.log("[page.js] Transcription status response:", data);

        if (data.active) {
          console.log("[page.js] Found active transcription on page load, connecting to SSE");
          // Set transcribing state to true to trigger connection
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Reconnecting to active transcription...' });
        } else {
          console.log("[page.js] No active transcription found on backend");
        }
      } catch (error) {
        console.error("[page.js] Error checking for active transcription:", error);
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error checking transcription status: ${error.message}` });
      }
    };

    // On initial mount, check for active transcription
    if (!state.transcribing && initialStateLoaded && !initialCheckDoneRef.current) {
      console.log("[page.js] Initial load, checking for active transcription");
      initialCheckDoneRef.current = true;
      checkForActiveTranscription();
    }
  }, [initialStateLoaded, state.transcribing, dispatch, BACKEND_URL]);

  // Handle shouldDisconnect state changes
  useEffect(() => {
    if (state.shouldDisconnect && sseConnected) {
      console.log('[page.js] shouldDisconnect is true, disconnecting SSE');
      disconnectSSE();
      // Reset the flag after disconnection
      dispatch({ type: ACTIONS.SET_SHOULD_DISCONNECT, payload: false });
    }
  }, [state.shouldDisconnect, sseConnected, disconnectSSE, dispatch]);

  // Single useEffect for SSE connection management with stable dependencies
  useEffect(() => {
    // Generate a unique ID for this effect instance for better logging
    const effectId = Math.random().toString(36).substring(2, 9);
    console.log(`[page.js] SSE connection management effect ${effectId} mounted`);

    // Store the current transcribing state to prevent stale closures
    const isCurrentlyTranscribing = state.transcribing;
    const isCurrentlyConnected = sseConnected;

    // Connection management - only connect when transcribing starts and we're not already connected
    if (isCurrentlyTranscribing && !isCurrentlyConnected) {
      console.log(`[page.js] Effect ${effectId}: state.transcribing is true and not connected, calling connectSSE()`);
      // Connect to SSE - use a small delay to prevent rapid reconnections
      setTimeout(() => {
        if (state.transcribing && !sseConnected) { // Double-check state hasn't changed
          connectSSE();
        }
      }, 100);
    }

    // Return a cleanup function that only runs when the component actually unmounts
    return () => {
      console.log(`[page.js] Effect ${effectId} cleanup running`);

      // We don't need to disconnect here - the SSE hook will handle cleanup
      // This prevents unnecessary disconnections during re-renders
    };
  }, [state.transcribing]); // Only depend on transcribing state to prevent reconnections

  // --- Scroll Auto ---
  useEffect(() => {
    scrollToBottom(statusBoxRef);
  }, [state.statusUpdates]);

  useEffect(() => {
    // Try scrolling the ScrollArea component directly
    if (scrollAreaRef.current) {
       const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
       if (viewport) {
           requestAnimationFrame(() => {
               viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'auto' });
           });
       }
    }
  }, [state.transcriptionSegments]); // Keep dependency on segments

  // --- State Persistence ---
  useEffect(() => {
    if (!initialStateLoaded) return; // Don't save until initial load is done

    try {
      const stateToSave = {
        youtubeUrl: state.youtubeUrl,
        obsidianDir: state.obsidianDir,
        outputFolder: state.outputFolder,
        transcriptionModel: state.transcriptionModel,
        // Avoid saving large/transient state
      };
      storage.set('transcriptionState', stateToSave);
    } catch (error) {
      console.error('Error saving state to localStorage:', error);
    }
  }, [
      initialStateLoaded, // Ensure initial load is complete
      state.youtubeUrl,
      state.obsidianDir,
      state.outputFolder,
      state.transcriptionModel,
     ]);

  // --- Event Handlers ---

  // Handle Process Video Request
  const onProcessVideo = async () => {
    if (!initialStateLoaded) return; // Prevent actions before state is ready

    if (!validateYoutubeUrl(state.youtubeUrl)) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Please enter a valid YouTube URL' });
        return;
    }
    if (!validateObsidianDir(state.obsidianDir)) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Please enter a valid Save Directory' });
        return;
    }

    try {
        // Instead of disconnecting, we'll let the useSSE hook handle the connection
        // The hook will keep the connection open if we're in the middle of a transcription
        // and will only close it if we're not
        if (sseConnected) {
            console.log("[page.js] Existing SSE connection detected - will be maintained if needed");
            // We don't need to disconnect here - the hook will handle it
        }

        // Reset state completely
        console.log("[page.js] Resetting state for new transcription");
        dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });

        // Clear message buffer
        messageBuffer.current = [];
        if (bufferTimeoutRef.current) {
            clearTimeout(bufferTimeoutRef.current);
            bufferTimeoutRef.current = null;
        }

        // Clear any disconnect timeouts
        if (disconnectTimeoutRef.current) {
            clearTimeout(disconnectTimeoutRef.current);
            disconnectTimeoutRef.current = null;
        }

        // Reset timer completely
        setElapsedTime(0); // Reset timer visually
        setTimerActive(false); // Ensure timer is not active until we get segments

        const requestData = {
            youtube_video_url: state.youtubeUrl,
            obsidian_dir: state.obsidianDir,
            output_folder: state.outputFolder || 'output',
            transcription_model: state.transcriptionModel || "faster-whisper",
            use_groq: state.transcriptionModel === 'groq'
        };

        // Set up new state
        dispatch({ type: ACTIONS.SET_LOADING, payload: true });
        dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 1 });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Initiating video processing...' });

        console.log("Sending process request:", requestData);
        const response = await axios.post(`${BACKEND_URL}/process-video/`, requestData);
        console.log("Process video response:", response.data);

        if (response.data.status === 'started') {
            dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 2 });
            dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Processing video...' });

            // Only now set transcribing to true to connect to SSE
            dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
        } else {
            throw new Error(`Unexpected response: ${JSON.stringify(response.data)}`);
        }
    } catch (error) {
        console.error("Error processing video:", error);
        let errorMessage = error.message || 'Unknown error occurred';

        // Handle API error responses
        if (error.response?.data?.detail) {
            const details = error.response.data.detail;
            errorMessage = Array.isArray(details)
                ? details.map(err => `${err.loc?.[1] || 'Input'}: ${err.msg}`).join('; ')
                : String(details);
        }

        dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
        setTimerActive(false);
    }
  };

  // Handle selecting output folder (Note: Browser limitations apply)
  const handleSelectOutputFolder = async () => {
    alert("Selecting directories directly isn't reliably supported by browsers for security reasons. Please paste the full path to your desired save directory.");
    // Consider a backend endpoint to list user-accessible directories if feasible/secure
  };

  // --- Fetch Content Handlers (Web Pages Tab) ---
  const handleFetchContent = async () => {
    const sanitizedFetchUrl = sanitizeInput(state.fetchUrl);
    if (!sanitizedFetchUrl.trim()) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: "Please enter a URL to fetch content." });
      return;
    }

    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.SET_ERROR, payload: null });
    dispatch({ type: ACTIONS.SET_FETCH_RESULT, payload: null }); // Clear previous result
    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Fetching content from: ${sanitizedFetchUrl}` });

    try {
      const response = await axios.post(`${BACKEND_URL}/api/content/fetch-and-upsert`, { // Use the correct combined endpoint
          url: sanitizedFetchUrl,
          process_pdf: true, // Assuming you always want PDF for web fetches
          metadata: { source_type: 'webpage' }, // Add basic metadata
          target_selector: state.targetSelector || null, // Pass optional selectors
          exclude_selectors: state.excludedSelector ? state.excludedSelector.split(',').map(s => s.trim()) : null,
          // Other options like cleanFormat might be handled server-side now
      });

      console.log("Fetch/Upsert Response:", response.data);

      if (response.data.success && response.data.content_data) {
           dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Content fetched & upserted. Content ID: ${response.data.content_data.content_id}` });
           // Display fetched markdown content immediately
           dispatch({
               type: ACTIONS.SET_FETCH_RESULT,
               payload: {
                   markdown_content: response.data.content_data.markdown_content || "Markdown content not available.",
                   // You might not get paths back directly anymore, adjust as needed
                   // markdown_path: response.data.markdown_path,
                   // pdf_path: response.data.pdf_path
               }
           });
      } else {
          throw new Error(response.data.message || "Failed to fetch or upsert content.");
      }
    } catch (error) {
      console.error("Error fetching/upserting content:", error);
      const errorMsg = error.response?.data?.detail || error.message || "Unknown error occurred";
      dispatch({ type: ACTIONS.SET_ERROR, payload: `Fetch failed: ${errorMsg}` });
      dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Fetch failed: ${errorMsg}` });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };


  // --- Vector Search Handlers --- (Placeholder - keep simple for now)
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchThreshold, setSearchThreshold] = useState(0.7);

  const handleVectorSearch = async () => {
      alert("Vector search functionality needs integration with the new search endpoint.");
      // Implementation needed here using /api/search or /api/search-sse
  };

  // Function to process the buffered messages
  const processBuffer = useCallback(() => {
    console.log('[processBuffer] Contents of messageBuffer.current before clearing and dispatching:', messageBuffer.current); // Log buffer contents before clearing
    if (messageBuffer.current.length > 0) {
      console.log(`[processBuffer] Processing ${messageBuffer.current.length} buffered segments.`);
      // Create a copy of the buffer to dispatch
      const segmentsToDispatch = [...messageBuffer.current];
      // Clear the buffer immediately
      messageBuffer.current = [];
      console.log('[processBuffer] Dispatching segments:', segmentsToDispatch); // Log segments being dispatched
      // Dispatch the batch action
      dispatch({ type: ACTIONS.ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS, payload: segmentsToDispatch });
    }
    // Clear the timeout ref so a new one can be set
    bufferTimeoutRef.current = null;
  }, [dispatch]); // Dependency on dispatch (stable)

  // --- Message Handling --- (RE-ADD THIS FUNCTION)
  const onMessage = useCallback((data) => {
    console.log('[onMessage] Raw data received:', data); // Log raw data

    try {
      let message;
      if (typeof data === 'string') {
        // Handle potential multiple JSON objects in one message (less common with SSE but possible)
        try {
             message = JSON.parse(data);
        } catch (e) {
             console.warn('[onMessage] Failed initial JSON parse, might be malformed or multiple objects. Raw:', data);
             // Attempt to handle potential malformed JSON or just treat as status
              dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Received potentially malformed data: ${data.substring(0, 100)}...` });
             return; // Skip further processing for this message
        }

      } else if (typeof data === 'object' && data !== null) {
        message = data; // Assume already parsed if object
      } else {
        console.warn('[onMessage] Received data is not a string or object:', data);
        return; // Ignore non-string/object data
      }

      console.log('[onMessage] Parsed message object:', message); // Log parsed message object

      // --- Message Type Handling ---
      switch (message.type) {
        case 'status':
          console.log('[onMessage] Dispatching ADD_STATUS_UPDATE:', message.content);
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: message.content });
          break;
        case 'transcription_segment':
          const segment = message.content; // Assuming content *is* the segment object
          console.log('[onMessage] Received transcription_segment segment object:', segment); // Log segment object
          if (isValidSegment(segment)) {
            // Add to buffer instead of dispatching directly
            messageBuffer.current.push(segment);
            console.log(`[onMessage] Segment added to buffer. Buffer size: ${messageBuffer.current.length}`); // Log when segment is added to buffer

            // If no timeout is scheduled, schedule one
            if (bufferTimeoutRef.current === null) {
              bufferTimeoutRef.current = setTimeout(processBuffer, BATCH_DELAY);
              console.log(`[onMessage] Scheduled buffer processing in ${BATCH_DELAY}ms`);
            }
          } else {
            console.warn('[onMessage] Received invalid segment, skipping:', segment);
          }
          break;
        case 'transcription_complete':
          console.log('[onMessage] Received transcription_complete');
          // Process any remaining buffer immediately before handling completion
          if (bufferTimeoutRef.current) {
              clearTimeout(bufferTimeoutRef.current); // Clear scheduled timeout
          }
          processBuffer(); // Process remaining segments

          dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 3 }); // Move to final step
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
          dispatch({ type: ACTIONS.SET_LOADING, payload: false });
          setTimerActive(false); // Stop the timer visually
          break;
        case 'error':
          console.error('[onMessage] Received error message:', message.content);
           // Process any remaining buffer before handling error
          if (bufferTimeoutRef.current) {
              clearTimeout(bufferTimeoutRef.current);
          }
          processBuffer(); // Process remaining segments

          dispatch({ type: ACTIONS.SET_ERROR, payload: `Backend Error: ${message.content}` });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error: ${message.content}` });
          dispatch({ type: ACTIONS.SET_LOADING, payload: false });
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
          setTimerActive(false);
          break;
        case 'heartbeat':
          console.log('[onMessage] Received heartbeat:', message.content);
          // Optional: Update a 'last heartbeat received' state if needed
          break;
        case 'video_metadata':
           console.log('[onMessage] Received video_metadata:', message.content);
           dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Metadata: ${message.content.title}` });
           break;
        case 'connection_status':
          if (message.content === 'safe_to_disconnect') {
            console.log('[onMessage] Received safe_to_disconnect. Setting shouldDisconnect=true.');
             // Process any remaining buffer immediately before disconnecting
            if (bufferTimeoutRef.current) {
                clearTimeout(bufferTimeoutRef.current);
            }
            processBuffer(); // Process remaining segments
            dispatch({ type: ACTIONS.SET_SHOULD_DISCONNECT, payload: true });
          }
          break;
        default:
          console.warn('[onMessage] Received unknown message type:', message.type, message);
      }
    } catch (error) {
        // Also process buffer in case of top-level error during message handling
        if (bufferTimeoutRef.current) {
            clearTimeout(bufferTimeoutRef.current);
        }
        processBuffer();

      if (error instanceof SyntaxError && typeof data === 'string') {
        console.warn('[onMessage] Received non-JSON message or parse error, treating as status:', data);
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: data });
      } else {
        console.error('[onMessage] Error processing message:', error, 'Raw data:', data);
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error processing update: ${error.message}` });
      }
    }
  }, [dispatch, state.transcribing, processBuffer]); // Add processBuffer to dependencies

  // Reference the optimized handler for the SSE hook
  useEffect(() => {
    // Ensure processBuffer doesn't trigger unnecessary disconnects on unmount
    const currentTimeoutRef = bufferTimeoutRef; // Capture ref for cleanup
    window.onMessageOptimized = onMessage;
    return () => {
        window.onMessageOptimized = undefined;
        // Clear any pending timeout on unmount
        if (currentTimeoutRef.current) {
            clearTimeout(currentTimeoutRef.current);
            console.log('[page.js cleanup] Cleared pending buffer timeout.');
        }
    };
  }, [onMessage]); // onMessage dependency is correct here

   // --- Render Logic ---
  if (!initialStateLoaded) {
      return <div className="flex justify-center items-center h-screen">Loading...</div>; // Or a spinner
  }

  return (
    <>
      <main className="container mx-auto mt-8 p-4 max-w-4xl"> {/* Increased max width */}
        {/* <h1 className="text-3xl font-bold mb-6 text-center">PMOVES Transcription & Content Processor</h1> */}

         {/* Progress Steps */}
         <Card className="mb-8 shadow-lg backdrop-blur-sm bg-white/80 dark:bg-black/70">
           <CardContent className="pt-6">
             <div className="flex justify-between items-center relative">
               {/* Progress Bar */}
               <div className="absolute top-1/2 left-0 right-0 h-1 bg-muted -translate-y-1/2 rounded-full overflow-hidden">
                 <div
                   className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-500 ease-out"
                   style={{
                     width: `${(state.activeStep / (steps.length - 1)) * 100}%`, // Use steps here
                   }}
                 />
               </div>

               {/* Step Circles */}
               {steps.map((step, index) => ( // Use steps here
                 <div key={index} className="flex flex-col items-center relative z-10">
                   <div
                     className={`
                       rounded-full w-8 h-8 flex items-center justify-center border-2 transition-all duration-300
                       ${state.activeStep >= index ? 'bg-[hsl(var(--page-accent))] text-[hsl(var(--background))] border-[hsl(var(--page-accent))]' : 'bg-muted text-muted-foreground border-gray-300 dark:border-gray-600'}
                       ${state.activeStep === index ? 'ring-2 ring-[hsl(var(--page-accent))] ring-offset-2 dark:ring-offset-background' : ''}
                     `}
                   >
                     {state.activeStep > index ? '✓' : index + 1}
                   </div>
                   <span
                     className={`
                       text-xs sm:text-sm mt-2 text-center font-medium
                       transition-colors duration-300
                       ${state.activeStep >= index ? 'text-[hsl(var(--page-accent))]' : 'text-muted-foreground'}
                     `}
                   >
                     {step}
                   </span>
                 </div>
               ))}
             </div>
           </CardContent>
         </Card>


         {/* Tabs for different functionalities */}
         <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
                <TabsTrigger value="transcription">Video Transcription</TabsTrigger>
                <TabsTrigger value="webpages">Web Content Fetch</TabsTrigger>
                <TabsTrigger value="vector-search">Vector Search</TabsTrigger>
            </TabsList>

            {/* --- Transcription Tab --- */}
            <TabsContent value="transcription">
                <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70 mb-6">
                    <CardHeader>
                        <CardTitle>Video Transcription Setup</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 pt-6">
                        {/* Model Selection */}
                        <div className="space-y-2">
                            <Label className="font-semibold">Transcription Model</Label>
                            <Select
                                value={state.transcriptionModel}
                                onValueChange={(value) => dispatch({ type: ACTIONS.SET_TRANSCRIPTION_MODEL, payload: value })}
                            >
                                <SelectTrigger className="w-full">
                                <SelectValue placeholder="Select transcription model" />
                                </SelectTrigger>
                                <SelectContent>
                                <SelectItem value="faster-whisper">Faster Whisper (Local GPU)</SelectItem>
                                <SelectItem value="groq">Groq API (Cloud)</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-muted-foreground mt-1">
                                {state.transcriptionModel === "groq"
                                ? "Cloud processing via Groq API. Saves local GPU resources. Requires API key in backend."
                                : "Local processing using Faster Whisper on your GPU."}
                            </p>
                        </div>

                        {/* YouTube URL Input */}
                        <div className="space-y-2">
                        <Label htmlFor="youtube-url" className="font-semibold">YouTube Video URL</Label>
                        <Input
                            id="youtube-url"
                            type="text"
                            placeholder="https://www.youtube.com/watch?v=..."
                            value={state.youtubeUrl}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_YOUTUBE_URL, payload: e.target.value })}
                            className={!validateYoutubeUrl(state.youtubeUrl) && state.youtubeUrl ? 'border-red-500' : ''}
                        />
                        {!validateYoutubeUrl(state.youtubeUrl) && state.youtubeUrl && (
                            <p className="text-xs text-red-600">Please enter a valid YouTube URL.</p>
                        )}
                        </div>

                        {/* Directory Input */}
                        <div className="space-y-2">
                        <Label htmlFor="obsidian-dir" className="font-semibold">Save Directory (Full Path)</Label>
                        <Input
                            id="obsidian-dir"
                            type="text"
                            placeholder="e.g., C:\\Users\\You\\Documents\\Transcripts or /Users/you/transcripts"
                            value={state.obsidianDir}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: e.target.value })}
                            className={!validateObsidianDir(state.obsidianDir) && state.obsidianDir ? 'border-red-500' : ''}
                        />
                         {!validateObsidianDir(state.obsidianDir) && state.obsidianDir && (
                            <p className="text-xs text-red-600">Save directory cannot be empty.</p>
                        )}
                        <p className="text-xs text-muted-foreground">Enter the full path where transcripts should be saved.</p>
                        </div>

                        {/* Output Folder (Optional - can be relative) */}
                        {/* <div className="space-y-2">
                        <Label htmlFor="output-folder">Output Subfolder (Optional)</Label>
                        <Input
                            id="output-folder"
                            type="text"
                            placeholder="e.g., video_outputs (relative to Save Directory)"
                            value={state.outputFolder}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: e.target.value })}
                        />
                        </div> */}

                        {/* Process Button */}
                        <Button
                            className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out transform hover:scale-105"
                            onClick={onProcessVideo}
                            disabled={state.loading || !validateYoutubeUrl(state.youtubeUrl) || !validateObsidianDir(state.obsidianDir) || !initialStateLoaded}
                        >
                            {state.loading ? (
                                <>
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Processing...
                                </>
                            ) : 'Process Video'}
                        </Button>
                    </CardContent>
                </Card>

                {/* Output Area */}
                <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                   {/* Status Updates Box */}
                    <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70">
                        <CardHeader>
                        <div className="flex justify-between items-center">
                            <CardTitle>Status Updates</CardTitle>
                            <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                backendStatus === 'connected' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                                backendStatus === 'error' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' :
                                'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                            }`}>
                            Backend: {backendStatus.charAt(0).toUpperCase() + backendStatus.slice(1)}
                            </span>
                        </div>
                        </CardHeader>
                        <CardContent>
                        <ScrollArea className="h-[300px] w-full rounded-md border p-3">
                             {/* Ensure statusBoxRef is attached here */}
                            <div ref={statusBoxRef}>
                                <StatusUpdates updates={state.statusUpdates} model={state.transcriptionModel} />
                            </div>
                            <ScrollBar orientation="vertical" />
                        </ScrollArea>
                        </CardContent>
                    </Card>

                    {/* Live Transcription Box */}
                    <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70">
                        <CardHeader className="flex flex-row justify-between items-center pb-2">
                            <CardTitle>Live Transcription</CardTitle>
                            <div className="flex items-center space-x-2">
                                {state.transcriptionModel && (
                                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                                    state.transcriptionModel === "groq" ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300" : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                                    }`}>
                                    {state.transcriptionModel === "groq" ? "☁️ Cloud" : "💻 Local"}
                                    </span>
                                )}
                                {state.transcribing && (
                                    <span className={`text-sm text-primary flex items-center ${timerActive ? 'animate-pulse' : ''}`}>
                                    {timerActive ? (
                                        <svg className="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                    ) : (
                                        <svg className="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    )}
                                    {formatElapsedTime(elapsedTime)}
                                    </span>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent>
                            {/* Ensure ScrollArea wraps the div with the ref */}
                             <ScrollArea ref={scrollAreaRef} className="h-[300px] w-full rounded-md border p-3" id="transcription-scroll-area">
                                {/* Attach ref to the direct child containing segments */}
                                <div className="space-y-2">
                                {/* --- DEBUG LOG: Log segment count before mapping --- */}
                                {console.log(`[Render] Rendering ${state.transcriptionSegments.length} segments.`)}
                                {state.transcriptionSegments.length > 0 ? (
                                    state.transcriptionSegments
                                    // .sort((a, b) => a.start_time - b.start_time) // Sorting done in reducer
                                    .map((segment, index) => (
                                        <TranscriptionSegment
                                        key={segment.id || `seg-${index}-${Math.random()}`} // Ensure key is truly unique
                                        segment={segment}
                                        index={index}
                                        isLatest={index === state.transcriptionSegments.length - 1}
                                        isTranscribing={state.transcribing}
                                        model={state.transcriptionModel}
                                        />
                                    ))
                                ) : (
                                    <div className="flex items-center justify-center h-full text-muted-foreground text-sm py-10">
                                    {state.loading || state.transcribing ? "Waiting for transcription data..." : "Transcription output will appear here."}
                                    </div>
                                )}
                                </div>
                                <ScrollBar orientation="vertical" />
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </div>
            </TabsContent>

             {/* --- Web Pages Tab --- */}
            <TabsContent value="webpages">
                <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70">
                    <CardHeader><CardTitle>Fetch & Process Web Content</CardTitle></CardHeader>
                    <CardContent className="space-y-6">
                       {/* URL Input */}
                       <div className="space-y-2">
                           <Label htmlFor="fetch-url">URL to Fetch</Label>
                           <Input id="fetch-url" placeholder="Enter URL (e.g., https://example.com/article)" value={state.fetchUrl} onChange={(e) => dispatch({ type: ACTIONS.SET_FETCH_URL, payload: e.target.value })}/>
                       </div>
                       {/* Advanced Options Accordion */}
                       <Accordion type="single" collapsible className="w-full border rounded-md">
                           <AccordionItem value="advanced-options">
                              <AccordionTrigger className="px-4 py-2 text-sm font-medium">Advanced Fetch Options</AccordionTrigger>
                              <AccordionContent className="p-4 space-y-4 bg-muted/30 dark:bg-muted/10">
                                 <div className="space-y-2"><Label htmlFor="target-selector">Target CSS Selector (Optional)</Label><Input id="target-selector" placeholder="e.g., article, .main-content, #content-body" value={state.targetSelector} onChange={(e) => dispatch({ type: ACTIONS.SET_TARGET_SELECTOR, payload: e.target.value })}/><p className="text-xs text-muted-foreground">Extract content only from elements matching this selector.</p></div>
                                 <div className="space-y-2"><Label htmlFor="exclude-selector">Exclude CSS Selectors (Optional)</Label><Input id="exclude-selector" placeholder="e.g., nav, footer, .ad-banner, script" value={state.excludedSelector} onChange={(e) => dispatch({ type: ACTIONS.SET_EXCLUDED_SELECTOR, payload: e.target.value })}/><p className="text-xs text-muted-foreground">Remove elements matching these selectors (comma-separated).</p></div>
                              </AccordionContent>
                           </AccordionItem>
                       </Accordion>
                       {/* Fetch Button */}
                       <Button onClick={handleFetchContent} disabled={state.loading || !state.fetchUrl.trim()} className="w-full bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out transform hover:scale-105">{state.loading ? 'Fetching...' : 'Fetch & Upsert Content'}</Button>
                       {/* Results Display Area */}
                       <div className="mt-4">
                           <Label className="font-semibold">Fetched Content (Markdown)</Label>
                           <ScrollArea className="h-[400px] w-full rounded-md border p-4 mt-2 bg-background">
                                {state.fetchResult?.markdown_content ? (<div className="prose prose-sm dark:prose-invert max-w-none"><ReactMarkdown components={{ a: ({node, ...props}) => (<a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />), }}>{typeof state.fetchResult.markdown_content === 'object' ? `\`\`\`json\n${JSON.stringify(state.fetchResult.markdown_content, null, 2)}\n\`\`\`` : state.fetchResult.markdown_content}</ReactMarkdown></div>) : (<div className="text-center py-8 text-muted-foreground">{state.loading ? "Fetching..." : "Fetched content will appear here."}</div>)}
                                <ScrollBar orientation="vertical" />
                           </ScrollArea>
                       </div>
                    </CardContent>
                </Card>
            </TabsContent>

             {/* --- Vector Search Tab --- */}
            <TabsContent value="vector-search">
                 <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70">
                    <CardHeader><CardTitle>Vector Search</CardTitle><CardDescription>Search through processed content using semantic meaning.</CardDescription></CardHeader>
                   <CardContent className="space-y-6">
                       {/* Search Input & Button */}
                       <div className="flex items-center gap-4">
                           <Input placeholder="Enter your search query..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="flex-grow"/>
                           <Button onClick={handleVectorSearch} disabled={searchLoading || !searchQuery.trim()}>{searchLoading ? 'Searching...' : 'Search'}</Button>
                       </div>
                       {/* Similarity Slider */}
                       <div className="space-y-2">
                           <Label htmlFor="similarity-slider">Similarity Threshold: {searchThreshold.toFixed(2)}</Label>
                           <Slider id="similarity-slider" value={[searchThreshold]} onValueChange={(value) => setSearchThreshold(value[0])} min={0} max={1} step={0.05} className="w-full"/>
                           <p className="text-xs text-muted-foreground">Adjust how closely results must match (higher = more strict).</p>
                       </div>
                       {/* Results Table */}
                       {searchResults.length > 0 && !searchLoading && (
                           <div className="mt-4">
                               <Label className="font-semibold">Search Results</Label>
                               <ScrollArea className="h-[500px] w-full rounded-md border mt-2">
                                   <Table>
                                        <TableHeader><TableRow><TableHead className="w-[120px]">Content ID</TableHead><TableHead className="w-[150px]">Time Range</TableHead><TableHead>Text Snippet</TableHead><TableHead className="w-[100px] text-right">Similarity</TableHead><TableHead className="w-[100px]">Actions</TableHead></TableRow></TableHeader>
                                        <TableBody>
                                            {searchResults.map((result, index) => (
                                                <TableRow key={result.id || index}>
                                                    <TableCell className="font-medium truncate" title={result.video_id || result.content_id}>{result.video_id || result.content_id || 'N/A'}</TableCell>
                                                    <TableCell className="text-xs">{result.start_time && result.end_time ? `${formatTimeStamp(result.start_time)} - ${formatTimeStamp(result.end_time)}` : 'N/A'}</TableCell>
                                                    <TableCell className="max-w-sm truncate" title={result.text || result.content}>{result.text || result.content || 'No content'}</TableCell>
                                                    <TableCell className="text-right font-mono">{result.similarity ? `${(result.similarity * 100).toFixed(1)}%` : 'N/A'}</TableCell>
                                                    <TableCell>{result.watch_url && (<Button variant="outline" size="sm" asChild><a href={result.watch_url} target="_blank" rel="noopener noreferrer" title="Watch on YouTube">{/* Watch Icon */}<svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg></a></Button>)}</TableCell>
                                                </TableRow>
                                             ))}
                                         </TableBody>
                                    </Table>
                                </ScrollArea>
                            </div>
                        )}
                        {searchLoading && <div className="text-center py-8 text-muted-foreground">Searching...</div>}
                        {!searchLoading && searchResults.length === 0 && searchQuery && (<div className="text-center py-8 text-muted-foreground">No results found for your query. Try adjusting the threshold or query.</div>)}
                    </CardContent>
                </Card>
            </TabsContent>
         </Tabs>

        {/* Error Display */}
        {state.error && (
          <Card className="mt-6 border-destructive bg-destructive/10 shadow-md">
             <CardHeader><CardTitle className="text-destructive flex items-center">{/* Warning Icon */}<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> Error Encountered</CardTitle></CardHeader>
             <CardContent className="text-destructive text-sm"><pre className="whitespace-pre-wrap break-words">{state.error}</pre></CardContent>
          </Card>
        )}
      </main>
    </>
  );
}
