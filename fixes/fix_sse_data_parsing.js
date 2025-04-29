/**
 * Fix for SSE data parsing issues
 * This script updates the sse-helpers.js file to properly handle SSE data format
 */

const fs = require('fs');
const path = require('path');

// Path to the sse-helpers.js file
const sseHelpersPath = path.join(process.cwd(), 'src', 'utils', 'sse-helpers.js');

// Updated content for sse-helpers.js with fixed data parsing
const updatedSseHelpers = `/**
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
    
    // Handle SSE format with "data: " prefix
    if (typeof data === 'string' && data.startsWith('data: ')) {
      // Extract the JSON part after "data: "
      const jsonStr = data.substring(6).trim();
      return JSON.parse(jsonStr);
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
 * Create an EventSource with error handling and reconnection logic
 * @param {string} url - The SSE endpoint URL
 * @param {function} onMessage - Callback for message events
 * @param {function} onError - Callback for error events
 * @returns {EventSource} The configured EventSource object
 */
export function createSafeEventSource(url, onMessage, onError) {
  console.log('Creating SSE connection to:', url);
  
  try {
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = (event) => {
      try {
        console.log('Raw SSE message received:', event.data);
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
    
    eventSource.onopen = () => {
      console.log('SSE connection opened successfully');
    };
    
    return eventSource;
  } catch (error) {
    console.error('Failed to create EventSource:', error);
    if (onError) onError(error);
    return null;
  }
}
`;

// Main function to apply the fix
async function applyFix() {
  try {
    // Update sse-helpers.js
    fs.writeFileSync(sseHelpersPath, updatedSseHelpers, 'utf8');
    console.log('Successfully updated sse-helpers.js with fixed data parsing');
    console.log('This fix addresses the "Unexpected token \'d\'" error by properly handling the SSE data format with "data: " prefix');
  } catch (error) {
    console.error('Error applying SSE data parsing fix:', error);
  }
}

// Run the fix
applyFix();
