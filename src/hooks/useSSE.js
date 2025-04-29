/**
 * useSSE.js - A custom React hook for Server-Sent Events (SSE) connections
 *
 * This hook provides a standardized way to handle SSE connections across the application,
 * with consistent error handling, reconnection logic, and message parsing.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { BACKEND_URL, SSE_CONFIG } from '@/lib/constants';

/**
 * Custom hook for Server-Sent Events (SSE) connections
 *
 * @param {string} endpoint - The SSE endpoint to connect to (without the base URL)
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoConnect - Whether to connect automatically on mount (default: true)
 * @param {boolean} options.withCredentials - Whether to include credentials in the request (default: true)
 * @param {number} options.maxRetries - Maximum number of reconnection attempts (default: 3)
 * @param {number} options.reconnectDelay - Base delay for reconnection in ms (default: 1000)
 * @param {number} options.timeout - Connection timeout in ms (default: 30000)
 * @param {Function} options.onMessage - Callback for parsed messages (default: null)
 * @param {Function} options.onRawMessage - Callback for raw message events (default: null)
 * @param {Function} options.onConnect - Callback when connection is established (default: null)
 * @param {Function} options.onError - Callback when connection errors occur (default: null)
 * @param {Function} options.onDisconnect - Callback when connection is closed (default: null)
 * @returns {Object} - SSE connection state and control functions
 */
const useSSE = (
  endpoint,
  {
    autoConnect = true,
    withCredentials = true,
    maxRetries = 3,
    reconnectDelay = 1000,
    timeout = 30000,
    onMessage = null,
    onRawMessage = null,
    onConnect = null,
    onError = null,
    onDisconnect = null
  } = {}
) => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [lastMessage, setLastMessage] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const eventSourceRef = useRef(null);
  const timeoutRef = useRef(null);
  const lastMessageRef = useRef(null);

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

    // Log the raw JSON string for debugging
    console.log('[parseMessage] Raw JSON string:', jsonStr);

    // Try parsing the potentially prefixed string
    try {
      const parsed = JSON.parse(jsonStr);
      console.log('[parseMessage] Successfully parsed JSON:', parsed);

      // Ensure it's an object and add timestamp if missing
      if (typeof parsed === 'object' && parsed !== null) {
        // Add timestamp if missing
        const result = {
          ...parsed,
          timestamp: parsed.timestamp || new Date().toISOString()
        };

        // Special handling for transcription segments
        if (result.type === 'transcription_segment') {
          console.log('[parseMessage] Processing transcription segment:', result);

          // Ensure content exists and is properly formatted
          if (!result.content) {
            console.warn('[parseMessage] Transcription segment has no content:', result);
            result.content = {};
          } else if (typeof result.content === 'string') {
            try {
              // Try to parse content if it's a string
              result.content = JSON.parse(result.content);
              console.log('[parseMessage] Parsed content string to object:', result.content);
            } catch (contentError) {
              console.warn('[parseMessage] Failed to parse content string:', contentError);
              // Keep content as string if parsing fails
            }
          }

          // Ensure content has text property
          if (result.content && !result.content.text && typeof result.content === 'object') {
            // Try to extract text from other properties
            result.content.text = result.content.Text || result.content.transcript || '';
            console.log('[parseMessage] Extracted text from other properties:', result.content.text);
          }
        }

        return result;
      } else {
        // If parsed result isn't an object, treat as status
        console.log('[parseMessage] Parsed result is not an object, treating as status');
        return { type: 'status', content: parsed, timestamp: new Date().toISOString() };
      }
    } catch (jsonError) {
      console.warn('[parseMessage] JSON parsing failed:', jsonError.message);
      console.warn('[parseMessage] Attempted to parse:', jsonStr);

      // Try to extract transcription segment from string if it looks like one
      if (jsonStr.includes('"type":"transcription_segment"') || jsonStr.includes('"type": "transcription_segment"')) {
        console.log('[parseMessage] String appears to contain a transcription segment, attempting direct extraction');

        try {
          // Try to extract the JSON object using regex
          const match = jsonStr.match(/\{.*"type"\s*:\s*"transcription_segment".*\}/);
          if (match) {
            const extractedJson = match[0];
            console.log('[parseMessage] Extracted JSON string:', extractedJson);

            const extracted = JSON.parse(extractedJson);
            console.log('[parseMessage] Successfully parsed extracted JSON:', extracted);

            return {
              ...extracted,
              timestamp: extracted.timestamp || new Date().toISOString()
            };
          }
        } catch (extractError) {
          console.warn('[parseMessage] Failed to extract transcription segment:', extractError);
        }
      }

      // Fallback: If JSON parsing fails, return as plain status
      return { type: 'status', content: jsonStr, timestamp: new Date().toISOString() };
    }
  } catch (error) {
    // Catch any unexpected errors during processing
    console.error('Error processing SSE message:', error);
    return { type: 'error', content: 'Failed to process message', timestamp: new Date().toISOString() };
  }
}, []); // Keep dependencies minimal


  // Connect to SSE endpoint
  const connect = useCallback(() => {
    // Generate a unique ID for this connection attempt for better logging
    const connectionId = Math.random().toString(36).substring(2, 9);
    console.log(`[useSSE] Connection attempt ${connectionId} to ${endpoint}`);

    // If we're already connected with a valid EventSource, don't reconnect
    if (eventSourceRef.current && eventSourceRef.current.readyState !== 2) { // Check readyState (0=CONNECTING, 1=OPEN, 2=CLOSED)
        console.log(`[useSSE] Already connected or connecting to ${endpoint}, skipping connection attempt ${connectionId}`);
        return;
    }

    // Simplified: Always try to close any existing ref before creating a new one
    if (eventSourceRef.current) {
        console.log(`[useSSE] Closing potentially stale EventSource ref before reconnecting.`);
        eventSourceRef.current.close();
        eventSourceRef.current = null;
    }
    setConnected(false); // Ensure connection state is false before attempting

    // Clear any existing timeout
    if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
    }

    // Set connection timeout
    timeoutRef.current = setTimeout(() => {
        console.error(`SSE connection to ${endpoint} timed out (attempt ${connectionId})`); // Log as error
        const timeoutError = new Error('Connection timed out');
        setError(timeoutError);

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setConnected(false);

        if (onError) {
            onError(timeoutError);
        }
        // Consider adding retry logic here if needed

    }, timeout);


    try {
        console.log(`Connecting to SSE endpoint: ${BACKEND_URL}${endpoint}`);

        // Log the URL and options for debugging
        console.log(`SSE URL: ${BACKEND_URL}${endpoint}`);
        console.log(`SSE withCredentials: ${withCredentials}`);

        // Create new EventSource with specific options
        const eventSourceOptions = {
            withCredentials
        };

        // Create a new EventSource for THIS hook instance
        const newEventSource = new EventSource(`${BACKEND_URL}${endpoint}`, eventSourceOptions);
        eventSourceRef.current = newEventSource;

        // Set a flag to track if onopen has been called
        let openHandled = false;

        // Connection opened
        newEventSource.onopen = (event) => {
            // Ensure this handler belongs to the current EventSource
            if (event.target !== eventSourceRef.current) {
                console.warn("[useSSE] onopen called on a stale EventSource instance. Ignoring.");
                return;
            }
            console.log(`SSE connection opened: ${endpoint}`);
            setConnected(true);
            setError(null);
            setRetryCount(0);
            openHandled = true;

            // Clear timeout
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }

            if (onConnect) {
                onConnect(event);
            }
        };

        // Set a short timeout to check if onopen was called
        // setTimeout(() => {
        //     if (!openHandled && eventSourceRef.current === newEventSource) {
        //         console.warn(`SSE connection not opened after 2s, check network/backend: ${endpoint}`);
        //         // Don't force onopen, let the timeout handle it if it's truly stuck
        //     }
        // }, 2000); // Reduced log noise

        // Message received
        newEventSource.onmessage = (event) => {
            // Ensure this handler belongs to the current EventSource
            if (event.target !== eventSourceRef.current) {
                console.warn("[useSSE] onmessage called on a stale EventSource instance. Ignoring.");
                return;
            }
            // SSE DEBUG LOGGING
            console.log('[useSSE] Raw SSE message received:', event.data);

            try {
                // Call raw message handler if provided
                if (onRawMessage) {
                    onRawMessage(event);
                }

                // Log raw message for debugging
                // console.debug('SSE raw message received:', event.data); // Reduce noise

                // Parse message
                let parsedMessage;
                try {
                    parsedMessage = parseMessage(event.data);
                } catch (parseError) {
                    console.error('[useSSE] Error parsing message:', parseError, event.data);
                    parsedMessage = {
                        type: 'error',
                        content: `Parse error: ${parseError.message}`,
                        timestamp: new Date().toISOString()
                    };
                }

                if (parsedMessage) {
                    setLastMessage(parsedMessage);
                    lastMessageRef.current = parsedMessage;
                    setMessages(prev => [...prev, parsedMessage]);

                    // Call message handler if provided
                    if (onMessage) {
                        try {
                            // Use window.onMessageOptimized if available (less direct dependency)
                            if (window.onMessageOptimized) {
                                window.onMessageOptimized(parsedMessage);
                            } else {
                                onMessage(parsedMessage);
                            }
                        } catch (callbackError) {
                            console.error('[useSSE] Error in onMessage callback:', callbackError);
                        }
                    } else {
                        // Fallback if no specific handler but global exists
                         if (window.onMessageOptimized) {
                            try {
                                window.onMessageOptimized(parsedMessage);
                            } catch (fallbackError) {
                                console.error('[useSSE] Error in window.onMessageOptimized fallback:', fallbackError);
                            }
                        }
                    }
                }
            } catch (messageError) {
                console.error('Error handling SSE message:', messageError, event.data);
                if (onError) {
                    onError(new Error(`Message processing error: ${messageError.message}`));
                }
            }
        };

        // Error handling
        newEventSource.onerror = (error) => {
             // Ensure this handler belongs to the current EventSource
            if (error.target !== eventSourceRef.current) {
                console.warn("[useSSE] onerror called on a stale EventSource instance. Ignoring.");
                return;
            }
            console.error(`SSE connection error: ${endpoint}`, error);

            // Clear any existing timeout
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }

            // Close the connection on ANY error to force reconnect attempt if needed
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
            setConnected(false);
            const connectionError = error instanceof Error ? error : new Error('SSE connection error');
            setError(connectionError);

            // Call onError callback if provided
            if (onError) {
                onError(connectionError);
            }

            // Attempt reconnection with exponential backoff
            if (retryCount < maxRetries) {
                const nextRetryCount = retryCount + 1;
                const delay = reconnectDelay * Math.pow(2, retryCount);

                console.log(`Attempting to reconnect SSE in ${delay}ms (attempt ${nextRetryCount} of ${maxRetries})`);
                setRetryCount(nextRetryCount);

                const reconnectTimeout = setTimeout(() => {
                     // Check if component is still mounted or if connection succeeded meanwhile
                     if (eventSourceRef.current && eventSourceRef.current.readyState !== 2) return; // Already connected/connecting
                     console.log(`[useSSE] Executing reconnect attempt ${nextRetryCount}...`);
                     connect(); // Attempt to connect again
                }, delay);
                // Store the timeout reference for potential cleanup
                // window._sseReconnectTimeout = reconnectTimeout; // Removed global
            } else {
                console.error(`Max SSE reconnection attempts reached for ${endpoint}`);
                if (onDisconnect) {
                    onDisconnect(new Error('Max reconnection attempts reached'));
                }
            }
        };
    } catch (error) {
        console.error(`Error setting up SSE connection to ${endpoint}:`, error);
        setError(error);
        setConnected(false);
        if (onError) {
            onError(error);
        }
    }
}, [
    endpoint,
    withCredentials,
    maxRetries,
    reconnectDelay,
    timeout,
    onMessage,
    onRawMessage,
    onConnect,
    onError,
    onDisconnect,
    retryCount,
    parseMessage,
    // Removed internal state dependencies like 'connected' to avoid loops
]);

// Disconnect from SSE endpoint
const disconnect = useCallback(() => {
    // Only disconnect if we have a valid, non-closed EventSource reference
    if (eventSourceRef.current && eventSourceRef.current.readyState !== 2) {
        console.log(`[useSSE] Manually disconnecting from SSE endpoint: ${endpoint}`);
        eventSourceRef.current.close();
    }
    // Clean up references and state regardless
    eventSourceRef.current = null;
    setConnected(false);
    setError(null);
    setRetryCount(0); // Reset retries on manual disconnect
    if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
    }
    if (onDisconnect) {
        onDisconnect(); // Call disconnect handler
    }
}, [endpoint, onDisconnect]);

// Clear messages
const clearMessages = useCallback(() => {
    setMessages([]);
    setLastMessage(null);
    lastMessageRef.current = null; // Also clear the ref
}, []);

// Ensure proper cleanup on unmount
useEffect(() => {
    const currentEventSource = eventSourceRef.current; // Capture ref for cleanup function
    const hookId = Math.random().toString(36).substring(2, 9);
    console.log(`[useSSE] Hook instance ${hookId} mounted for ${endpoint}`);

    if (autoConnect) {
        console.log(`[useSSE] Auto-connecting hook instance ${hookId} to ${endpoint}`);
        connect();
    }

    return () => {
        console.log(`[useSSE] Hook instance ${hookId} unmounting for ${endpoint}`);
        if (currentEventSource) {
            console.log(`[useSSE] Cleanup: Closing EventSource connection for hook ${hookId}`);
            currentEventSource.close();
        }
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }
        // Clear any pending reconnect timeouts associated with this instance (if stored locally)
        // If timeouts were stored globally, this becomes complex. Local management is safer.
        console.log(`[useSSE] Hook instance ${hookId} unmount cleanup completed`);
    };
// eslint-disable-next-line react-hooks/exhaustive-deps
}, [autoConnect, endpoint]); // Intentionally only run on mount/unmount based on these
// Connect/disconnect should be called manually or triggered by other state if autoConnect is false.


return {
    connected,
    error,
    messages,
    lastMessage,
    retryCount,
    connect,
    disconnect,
    clearMessages
};
};

export default useSSE;
