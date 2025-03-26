/**
 * fix_sse_frontend.js - Fix for SSE JSON parsing issues in the frontend
 * 
 * This script contains fixes for the JSON parsing errors in the frontend when
 * receiving SSE messages from the backend.
 */

// Fix for the onMessage handler in page.js
// The issue is that the frontend is expecting a different format than what the backend is sending
const fixedOnMessageHandler = `
onMessage: (data) => {
  console.log('SSE message received:', data);
  
  // Handle different message types
  if (data.type === 'status') {
    dispatch({ 
      type: ACTIONS.ADD_STATUS_UPDATE, 
      payload: data.content 
    });
  } else if (data.type === 'transcription_segment') {
    try {
      // Handle both string and object content formats
      let segmentContent = data.content;
      
      // If content is a string that looks like a pipe-delimited table row, parse it
      if (typeof segmentContent === 'string' && segmentContent.includes('|')) {
        // Try to extract data from markdown table format: | [timestamp](url) | video_id | id | start | end | text |
        const parts = segmentContent.split('|').filter(p => p.trim());
        if (parts.length >= 6) {
          // Extract timestamp from markdown link format [00:00](url)
          const timestampMatch = parts[0].match(/\\[(.*?)\\]/);
          const urlMatch = parts[0].match(/\\((.*?)\\)/);
          
          segmentContent = {
            watch_url: urlMatch ? urlMatch[1] : null,
            video_id: parts[1].trim(),
            id: parseInt(parts[2].trim()) || state.transcriptionSegments.length,
            start_time: timestampMatch ? timestampMatch[1] : '00:00',
            end_time: parts[4].trim(),
            text: parts[5].trim()
          };
        }
      }
      
      // Create a properly formatted segment object
      const segment = {
        text: typeof segmentContent === 'object' ? segmentContent.text : segmentContent,
        start_time: typeof segmentContent === 'object' ? 
          parseFloat(segmentContent.start_time || segmentContent.start || 0) : 0,
        end_time: typeof segmentContent === 'object' ? 
          parseFloat(segmentContent.end_time || segmentContent.end || 0) : 0,
        id: typeof segmentContent === 'object' ? 
          (segmentContent.id || state.transcriptionSegments.length) : state.transcriptionSegments.length,
        video_id: typeof segmentContent === 'object' ? 
          (segmentContent.video_id || state.youtubeUrl?.split('v=')[1] || '') : 
          (state.youtubeUrl?.split('v=')[1] || ''),
        watch_url: typeof segmentContent === 'object' && segmentContent.watch_url ? 
          segmentContent.watch_url : 
          (state.youtubeUrl?.split('v=')[1] ? 
            \`https://www.youtube.com/watch?v=\${state.youtubeUrl.split('v=')[1]}&t=\${Math.floor(
              typeof segmentContent === 'object' ? 
                parseFloat(segmentContent.start_time || segmentContent.start || 0) : 0
            )}\` : 
            null)
      };
      
      console.log('Parsed segment:', segment);
      
      // Only add valid segments with proper timing
      if (segment.text && !isNaN(segment.start_time)) {
        dispatch({ 
          type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT, 
          payload: segment 
        });
      } else {
        console.warn('Invalid segment data:', segmentContent);
      }
    } catch (error) {
      console.error('Error parsing transcription segment:', error, data);
    }
  } else if (data.type === 'transcription_complete') {
    // Disconnect the SSE connection
    disconnectSSE();
    
    dispatch({ 
      type: ACTIONS.SET_TRANSCRIBING, 
      payload: false 
    });
    dispatch({ 
      type: ACTIONS.ADD_STATUS_UPDATE, 
      payload: 'Transcription completed' 
    });
    dispatch({ 
      type: ACTIONS.SET_ACTIVE_STEP, 
      payload: 3 
    });
  } else if (data.type === 'error') {
    dispatch({ 
      type: ACTIONS.SET_ERROR, 
      payload: data.content 
    });
  } else if (data.type === 'heartbeat') {
    console.log('Heartbeat received from server');
  }
}
`;

// Fix for the parseMessage function in useSSE.js
const fixedParseMessage = `
// Parse SSE message data consistently
const parseMessage = useCallback((data) => {
  if (!data) return null;
  
  try {
    // Handle 'data: ' prefix if present
    const jsonStr = data.startsWith('data: ') ? data.slice(6) : data;
    
    // Try to parse as JSON
    try {
      return JSON.parse(jsonStr);
    } catch (jsonError) {
      // If JSON parsing fails, try to extract JSON from the string
      // This handles cases where the message might have extra text around the JSON
      const jsonMatch = jsonStr.match(/\\{.*\\}/s);
      if (jsonMatch) {
        try {
          return JSON.parse(jsonMatch[0]);
        } catch (nestedJsonError) {
          // If that also fails, return a formatted error object
          console.warn('Failed to parse nested JSON:', nestedJsonError, jsonStr);
        }
      }
      
      // If all JSON parsing attempts fail, return a formatted message
      return { 
        type: 'status', 
        content: jsonStr,
        timestamp: new Date().toISOString()
      };
    }
  } catch (error) {
    console.error('Error parsing SSE message:', error, data);
    return { 
      type: 'error', 
      content: 'Failed to parse message', 
      raw: data,
      timestamp: new Date().toISOString()
    };
  }
}, []);
`;

// Instructions for applying the fixes
console.log(`
To fix the SSE JSON parsing issues:

1. Update the onMessage handler in src/app/page.js:
   - Find the useSSE hook implementation with the onMessage callback
   - Replace the onMessage callback with the fixed version

2. Update the parseMessage function in src/hooks/useSSE.js:
   - Find the parseMessage function definition
   - Replace it with the fixed version

These changes will make the frontend more resilient to different message formats
from the backend and handle both string and object content formats properly.
`);

// Export the fixes for use in other scripts
module.exports = {
  fixedOnMessageHandler,
  fixedParseMessage
};
