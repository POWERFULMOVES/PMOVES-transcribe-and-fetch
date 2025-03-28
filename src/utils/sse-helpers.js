/**
 * Utility functions for handling Server-Sent Events (SSE)
 */

/**
 * Safely parse SSE event data
 * @param {string|object} data - The data from the SSE event
 * @returns {object} The parsed data object
 */
export function parseSseData(data) {
  if (!data) return null;
  
  try {
    // Check if data is already an object
    if (typeof data === 'object' && data !== null) {
      return data;
    }
    
    // Try to parse as JSON
    return JSON.parse(data);
  } catch (e) {
    console.warn('Error parsing SSE data:', e);
    // Return as-is if parsing fails
    return { content: data, type: 'unknown' };
  }
}

/**
 * Create an EventSource with error handling
 * @param {string} url - The SSE endpoint URL
 * @param {function} onMessage - Callback for message events
 * @param {function} onError - Callback for error events
 * @returns {EventSource} The configured EventSource object
 */
export function createSafeEventSource(url, onMessage, onError) {
  const eventSource = new EventSource(url);
  
  eventSource.onmessage = (event) => {
    try {
      const data = parseSseData(event.data);
      onMessage(data);
    } catch (e) {
      console.error('Error handling SSE message:', e);
      if (onError) onError(e);
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
    if (onError) onError(error);
  };
  
  return eventSource;
}
