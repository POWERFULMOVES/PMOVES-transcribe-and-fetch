/**
 * useSSE.js - A custom React hook for Server-Sent Events (SSE) connections
 * 
 * This hook provides a standardized way to handle SSE connections across the application,
 * with consistent error handling, reconnection logic, and message parsing.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { BACKEND_URL } from '@/lib/constants';

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
  
  // Parse SSE message data consistently
  const parseMessage = useCallback((data) => {
    if (!data) return null;
    
    try {
      // Handle 'data: ' prefix if present
      const jsonStr = data.startsWith('data: ') ? data.slice(6) : data;
      return JSON.parse(jsonStr);
    } catch (error) {
      console.error('Error parsing SSE message:', error, data);
      return { type: 'error', message: 'Failed to parse message', raw: data };
    }
  }, []);
  
  // Connect to SSE endpoint
  const connect = useCallback(() => {
    // Clear any existing connection
    if (eventSourceRef.current) {
      console.log(`Closing existing SSE connection to ${endpoint}`);
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Set connection timeout
    timeoutRef.current = setTimeout(() => {
      console.log(`SSE connection to ${endpoint} timed out`);
      setError(new Error('Connection timed out'));
      
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      if (onError) {
        onError(new Error('Connection timed out'));
      }
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
      
      eventSourceRef.current = new EventSource(`${BACKEND_URL}${endpoint}`, eventSourceOptions);
      
      // Connection opened
      eventSourceRef.current.onopen = (event) => {
        console.log(`SSE connection opened: ${endpoint}`);
        setConnected(true);
        setError(null);
        setRetryCount(0);
        
        // Clear timeout
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }
        
        if (onConnect) {
          onConnect(event);
        }
      };
      
      // Message received
      eventSourceRef.current.onmessage = (event) => {
        // Call raw message handler if provided
        if (onRawMessage) {
          onRawMessage(event);
        }
        
        // Parse message
        const parsedMessage = parseMessage(event.data);
        
        if (parsedMessage) {
          // Update state
          setLastMessage(parsedMessage);
          setMessages(prev => [...prev, parsedMessage]);
          
          // Call message handler if provided
          if (onMessage) {
            onMessage(parsedMessage);
          }
        }
      };
      
      // Error handling
      eventSourceRef.current.onerror = (error) => {
        console.error(`SSE connection error: ${endpoint}`, error);
        
        // Check if the error is due to CORS
        const isCorsError = error instanceof Event && !error.bubbles;
        if (isCorsError) {
          console.error("Possible CORS error detected. Make sure the server has proper CORS headers.");
        }
        
        // Update state
        setConnected(false);
        setError(error);
        
        // Call error handler if provided
        if (onError) {
          onError(error);
        }
        
        // Close the connection
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        
        // Attempt reconnection with exponential backoff
        if (retryCount < maxRetries) {
          const nextRetryCount = retryCount + 1;
          const delay = reconnectDelay * Math.pow(2, retryCount);
          
          console.log(`Attempting to reconnect SSE in ${delay}ms (attempt ${nextRetryCount} of ${maxRetries})`);
          setRetryCount(nextRetryCount);
          
          setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.error(`Max SSE reconnection attempts reached for ${endpoint}`);
          
          // Call disconnect handler if provided
          if (onDisconnect) {
            onDisconnect(new Error('Max reconnection attempts reached'));
          }
        }
      };
    } catch (error) {
      console.error(`Error setting up SSE connection to ${endpoint}:`, error);
      setError(error);
      
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
    parseMessage
  ]);
  
  // Disconnect from SSE endpoint
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log(`Manually disconnecting from SSE endpoint: ${endpoint}`);
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setConnected(false);
      
      if (onDisconnect) {
        onDisconnect();
      }
    }
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, [endpoint, onDisconnect]);
  
  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setLastMessage(null);
  }, []);
  
  // Connect on mount if autoConnect is true
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        console.log(`Cleaning up SSE connection to ${endpoint}`);
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [autoConnect, connect, endpoint]);
  
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
