/**
 * Fix for SSE implementation in the frontend
 * This script updates the sse-helpers.js file to ensure proper handling of SSE events
 */

const fs = require('fs');
const path = require('path');

// Path to the sse-helpers.js file
const sseHelpersPath = path.join(process.cwd(), 'src', 'utils', 'sse-helpers.js');

// Updated content for sse-helpers.js
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

// Path to the vector-search page.js file
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Function to update the vector-search page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Ensure proper handling of SSE events in the handleSearch function
    content = content.replace(
      /const handleSearch = useCallback\(\) => \{([\s\S]*?)const newEventSource = createSafeEventSource\(([\s\S]*?)setEventSource\(newEventSource\);/m,
      `const handleSearch = useCallback(() => {$1const newEventSource = createSafeEventSource($2
        // Ensure we have a valid EventSource
        if (!newEventSource) {
          setError('Failed to establish SSE connection. Please try again.');
          setLoading(false);
          return;
        }
        
        setEventSource(newEventSource);`
    );
    
    // Fix 2: Improve the switch case for handling different event types
    content = content.replace(
      /switch \(eventType\) \{([\s\S]*?)default:([\s\S]*?)}\s*}/m,
      `switch (eventType) {
                    case 'status':
                        // Update search flow stage based on status
                        if (data.metadata?.stage) {
                            console.log('Updating stage to:', data.metadata.stage);
                            setCurrentStage(data.metadata.stage);
                        }
                        
                        // Update metadata if provided
                        if (data.metadata) {
                            setMetadata(prevMetadata => ({
                                ...prevMetadata,
                                ...data.metadata
                            }));
                        }
                        break;
                        
                    case 'results':
                        // Final results received
                        console.log('Received final results:', data.content?.length || 0, 'items');
                        setResults(data.content || []);
                        
                        // Ensure stage is updated to complete
                        setCurrentStage('complete');
                        
                        // Only set loading to false if we have analysis or analysis is not requested
                        if (!runAnalysis || data.metadata?.analysis_complete) {
                            setLoading(false);
                        }
                        break;
                        
                    case 'analysis':
                        // Analysis results
                        console.log('Received analysis from provider:', data.metadata?.provider);
                        if (data.metadata?.provider === 'openai') {
                            setOpenAIAnalysis(data.content || '');
                        } else if (data.metadata?.provider === 'groq') {
                            setGroqAnalysis(data.content || '');
                        }
                        
                        // Update metadata to indicate analysis is complete
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            analysis_complete: true
                        }));
                        break;
                        
                    case 'error':
                        console.error('SSE error event:', data.content);
                        setError(data.content || 'An error occurred during search');
                        setLoading(false);
                        break;
                        
                    case 'complete':
                        // Search process complete
                        console.log('Search process complete');
                        setCurrentStage('complete');
                        setLoading(false);
                        
                        // Ensure metadata has the required flags
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            search_complete: true
                        }));
                        break;
                        
                    case 'heartbeat':
                        // Just a heartbeat to keep the connection alive
                        console.log('Heartbeat received');
                        break;
                        
                    default:$2}
                }`
    );
    
    // Fix 3: Ensure proper cleanup of EventSource
    content = content.replace(
      /useEffect\(\(\) => \{([\s\S]*?)if \(eventSource\) \{([\s\S]*?)}\s*}\s*}, \[eventSource\]\);/m,
      `useEffect(() => {
        return () => {
            if (eventSource) {
                console.log("Component unmounting, closing SSE connection");
                eventSource.close();
                setEventSource(null);
            }
        };
    }, [eventSource]);`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Main function to apply all fixes
async function applyFixes() {
  try {
    // Update sse-helpers.js
    fs.writeFileSync(sseHelpersPath, updatedSseHelpers, 'utf8');
    console.log('Successfully updated sse-helpers.js');
    
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    if (pageUpdated) {
      console.log('All SSE frontend fixes applied successfully!');
    } else {
      console.error('Failed to apply some SSE frontend fixes.');
    }
  } catch (error) {
    console.error('Error applying SSE frontend fixes:', error);
  }
}

// Run the fix
applyFixes();
