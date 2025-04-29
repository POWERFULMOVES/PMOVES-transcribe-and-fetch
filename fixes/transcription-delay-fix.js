/**
 * Transcription Delay Fix
 * 
 * This file contains the fixes for the delay between backend transcription completion
 * and frontend display. The main issues addressed are:
 * 
 * 1. Excessive logging slowing down message processing
 * 2. Inefficient message parsing and handling
 * 3. Lack of batched processing for transcription segments
 * 4. Connection management issues
 * 5. Improper error handling for non-fatal errors
 */

// Fix for useSSE.js - Optimize message parsing
function fixParseMessage() {
  return `
// Parse SSE message data consistently
const parseMessage = useCallback((data) => {
  if (!data) return null;

  // If data is already an object, return it directly, ensuring timestamp
  if (typeof data === 'object' && data !== null) {
    return { ...data, timestamp: data.timestamp || new Date().toISOString() };
  }

  // If it's not a string, we can't parse it further
  if (typeof data !== 'string') {
    return { type: 'unknown', content: data, timestamp: new Date().toISOString() };
  }

  try {
    // Handle 'data: ' prefix if present (common in raw SSE)
    const jsonStr = data.startsWith('data: ') ? data.slice(6).trim() : data.trim();

    // Check if the string is empty after trimming
    if (!jsonStr) {
        return null;
    }

    // Try parsing the potentially prefixed string
    try {
      const parsed = JSON.parse(jsonStr);
      // Ensure it's an object and add timestamp if missing
      if (typeof parsed === 'object' && parsed !== null) {
        // Add timestamp if missing
        return {
          ...parsed,
          timestamp: parsed.timestamp || new Date().toISOString()
        };
      } else {
        // If parsed result isn't an object, treat as status
        return { type: 'status', content: parsed, timestamp: new Date().toISOString() };
      }
    } catch (jsonError) {
      // Fallback: If JSON parsing fails, return as plain status
      return { type: 'status', content: jsonStr, timestamp: new Date().toISOString() };
    }
  } catch (error) {
    // Catch any unexpected errors during processing
    console.error('Error processing SSE message:', error);
    return { type: 'error', content: 'Failed to process message', timestamp: new Date().toISOString() };
  }
}, []); // Keep dependencies minimal
`;
}

// Fix for page.js - Optimize onMessage handler with batch processing
function fixOnMessage() {
  return `
// Message buffer for batch processing
const messageBuffer = useRef([]);
const processingBuffer = useRef(false);
const bufferTimeoutRef = useRef(null);

// Process message buffer in batches
const processMessageBuffer = useCallback(() => {
  if (processingBuffer.current || messageBuffer.current.length === 0) return;
  
  processingBuffer.current = true;
  
  try {
    // Get all messages from buffer
    const messages = [...messageBuffer.current];
    messageBuffer.current = [];
    
    // Process messages in order
    messages.forEach(data => {
      // Handle different message types
      if (data.type === 'transcription_segment') {
        const content = data.content;
        
        // Create segment with minimal processing
        const segment = {
          text: content.text || '',
          start_time: parseFloat(content.start_seconds || content.start_time || content.start || 0),
          end_time: parseFloat(content.end_seconds || content.end_time || content.end || 0),
          id: content.id || \`seg_\${Date.now()}\`,
          video_id: content.video_id || state.youtubeUrl?.split('v=')[1]?.split('&')[0] || '',
          watch_url: content.watch_url || generateWatchUrl(state.youtubeUrl, content.start_seconds || content.start_time || content.start)
        };
        
        // Skip validation for performance - just check text exists
        if (segment.text) {
          dispatch({ type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT, payload: segment });
          
          // Update the timer to show progress
          if (!timerActive) {
            setTimerActive(true);
          }
        }
      } else if (data.type === 'status') {
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: data.content });
      } else if (data.type === 'error') {
        // Special handling for "Set of Tasks/Futures is empty" error
        if (data.content && data.content.includes('Set of Tasks/Futures is empty')) {
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: \`Error: \${data.content}\` });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Backend task queue error - attempting to continue...' });
          return;
        }
        
        // For all other errors, proceed with normal error handling
        dispatch({ type: ACTIONS.SET_ERROR, payload: data.content });
        dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: \`Error: \${data.content}\` });
      } else if (data.type === 'transcription_complete') {
        dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Transcription process completed.' });
        disconnectSSE();
      }
    });
  } finally {
    processingBuffer.current = false;
    
    // Schedule next batch if needed
    if (messageBuffer.current.length > 0) {
      bufferTimeoutRef.current = setTimeout(processMessageBuffer, 50);
    }
  }
}, [state.youtubeUrl, dispatch, disconnectSSE, timerActive, setTimerActive, generateWatchUrl]);

// Optimized onMessage handler that uses the buffer
const onMessage = useCallback((data) => {
  // Add to buffer
  messageBuffer.current.push(data);
  
  // Schedule processing if not already scheduled
  if (!bufferTimeoutRef.current) {
    bufferTimeoutRef.current = setTimeout(() => {
      bufferTimeoutRef.current = null;
      processMessageBuffer();
    }, 50);
  }
}, [processMessageBuffer]);

// Clean up buffer timeout on unmount
useEffect(() => {
  return () => {
    if (bufferTimeoutRef.current) {
      clearTimeout(bufferTimeoutRef.current);
      bufferTimeoutRef.current = null;
    }
  };
}, []);
`;
}

// Fix for transcriptionReducer.js - Optimize segment handling
function fixReducer() {
  return `
case ACTIONS.ADD_TRANSCRIPTION_SEGMENT:
  // Ensure we're not adding duplicate segments
  const newSegment = action.payload;
  
  // Skip empty segments
  if (!newSegment || !newSegment.text) {
    return state;
  }
  
  // Use ID-based duplicate checking for better performance
  const isDuplicate = state.transcriptionSegments.some(
    segment => segment.id === newSegment.id
  );

  if (isDuplicate) {
    return state;
  }

  // Add the new segment and sort by ID (which should match time order)
  return {
    ...state,
    transcriptionSegments: [...state.transcriptionSegments, newSegment].sort((a, b) => {
      // First try to sort by ID if they're numeric
      if (!isNaN(a.id) && !isNaN(b.id)) {
        return a.id - b.id;
      }
      // Fall back to start_time
      return a.start_time - b.start_time;
    })
  };
`;
}

// Fix for connection cleanup in useSSE.js
function fixConnectionCleanup() {
  return `
// Disconnect from SSE endpoint
const disconnect = useCallback(() => {
  if (eventSourceRef.current) {
    console.log(\`[useSSE] Manually disconnecting from SSE endpoint: \${endpoint}\`);

    // Close the connection
    eventSourceRef.current.close();
    eventSourceRef.current = null;
    setConnected(false);
    
    // Handle reference counting
    if (window._sseReferenceCount && window._sseReferenceCount[endpoint]) {
      window._sseReferenceCount[endpoint]--;
      
      // Remove from global tracking if this was the last reference
      if (window._sseReferenceCount[endpoint] <= 0) {
        if (window._sseActiveConnections) {
          delete window._sseActiveConnections[endpoint];
        }
        delete window._sseReferenceCount[endpoint];
      }
    }
  }
}, [endpoint]);

// Ensure proper cleanup on unmount
useEffect(() => {
  return () => {
    if (eventSourceRef.current) {
      console.log(\`[useSSE] Cleanup: Closing connection to \${endpoint}\`);
      
      // Always close our connection
      eventSourceRef.current.close();
      
      // Update reference counting
      if (window._sseReferenceCount && window._sseReferenceCount[endpoint]) {
        window._sseReferenceCount[endpoint]--;
        
        // Only remove from global tracking if this was the last reference
        if (window._sseReferenceCount[endpoint] <= 0) {
          if (window._sseActiveConnections) {
            delete window._sseActiveConnections[endpoint];
          }
          delete window._sseReferenceCount[endpoint];
        }
      }
      
      // Always clear our reference
      eventSourceRef.current = null;
    }
    
    // Clear any timeouts
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };
}, [endpoint]);
`;
}

// Fix for onProcessVideo in page.js
function fixOnProcessVideo() {
  return `
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
      // IMPORTANT: First, ensure any existing connection is properly closed
      if (sseConnected) {
          console.log("[page.js] Disconnecting existing SSE connection");
          disconnectSSE();
          
          // Wait for disconnection to complete
          await new Promise(resolve => setTimeout(resolve, 100));
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
      const response = await axios.post(\`\${BACKEND_URL}/process-video/\`, requestData);
      console.log("Process video response:", response.data);

      if (response.data.status === 'started') {
          dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 2 });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Processing video...' });
          
          // Only now set transcribing to true to connect to SSE
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
      } else {
          throw new Error(\`Unexpected response: \${JSON.stringify(response.data)}\`);
      }
  } catch (error) {
      console.error("Error processing video:", error);
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.message || 'Unknown error occurred' });
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
  }
};
`;
}

// Export all fixes
const TranscriptionDelayFix = {
  parseMessage: fixParseMessage(),
  onMessage: fixOnMessage(),
  reducer: fixReducer(),
  connectionCleanup: fixConnectionCleanup(),
  onProcessVideo: fixOnProcessVideo()
};

// Make available in global scope for console use
window.TranscriptionDelayFix = TranscriptionDelayFix;
