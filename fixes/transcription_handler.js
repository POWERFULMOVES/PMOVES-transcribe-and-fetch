/**
 * Improved Transcription Segment Handler
 * This file provides utility functions to parse and process transcription data
 * to fix the JSON parsing errors in the PMOVES transcription system.
 */

/**
 * Parse the transcription segment from the SSE event data
 * Handles both old and new format for backward compatibility
 * 
 * @param {string} eventData - The data received from the SSE event
 * @returns {Object} - The parsed transcription segment data
 */
export function parseTranscriptionSegment(eventData) {
  try {
    // First, try to parse as JSON
    const data = JSON.parse(eventData);
    
    // Check if it's a transcription segment
    if (data.type === 'transcription_segment') {
      const content = data.content;
      
      // Handle the new format (properly structured JSON)
      if (typeof content === 'object' && content !== null) {
        return {
          type: 'transcription_segment',
          content: {
            text: content.text || '',
            start_time: parseFloat(content.start_time) || 0,
            end_time: parseFloat(content.end_time) || 0,
            id: content.id || 0,
            video_id: content.video_id || '',
            watch_url: content.watch_url || '',
            timestamp: content.timestamp || formatTimeStamp(content.start_time || 0)
          }
        };
      }
      
      // Handle the old format (markdown table string)
      if (typeof content === 'string') {
        // Try to extract data from the markdown table format
        // Format: | [00:00.00](https://youtube.com/watch?v=ID&t=0) | video_id | id | start | end | text |
        const tableRegex = /\| \[([\d:\.]+)\]\((https?:\/\/[^\s\)]+)\) \| ([^\|]+) \| (\d+) \| ([^\|]+) \| ([^\|]+) \| (.+) \|/;
        const match = content.match(tableRegex);
        
        if (match) {
          const [, timestamp, watchUrl, videoId, id, start, end, text] = match;
          
          // Extract start_time in seconds from the URL's t parameter
          const urlParams = new URL(watchUrl).searchParams;
          const startTime = parseFloat(urlParams.get('t') || '0');
          
          // Estimate end_time based on start time and text length
          const endTime = startTime + (text.length / 20); // Rough estimate: 20 chars ≈ 1 second
          
          return {
            type: 'transcription_segment',
            content: {
              text: text.trim(),
              start_time: startTime,
              end_time: endTime,
              id: parseInt(id, 10) || 0,
              video_id: videoId.trim(),
              watch_url: watchUrl,
              timestamp: timestamp
            }
          };
        }
        
        // If format doesn't match the expected pattern, create a minimal object
        return {
          type: 'transcription_segment',
          content: {
            text: content,
            start_time: 0,
            end_time: 0,
            id: 0,
            video_id: '',
            watch_url: '',
            timestamp: '00:00.00'
          }
        };
      }
    }
    
    // Return the original data if not a transcription segment
    return data;
  } catch (error) {
    console.error('Error parsing transcription segment:', error, eventData);
    
    // Try to recover from invalid JSON format
    // Check if it's the problematic format like:
    // 00:00.00[00:04.92](https://www.youtube.com/watch?v=eMa43IfcuVY&t=4) Hi, welcome to another video.↗
    const recoveryRegex = /([\d:\.]+)\[([\d:\.]+)\]\((https?:\/\/[^\s\)]+)\) (.+)/;
    const match = typeof eventData === 'string' ? eventData.match(recoveryRegex) : null;
    
    if (match) {
      const [, timestamp1, timestamp2, watchUrl, text] = match;
      
      // Extract video_id from URL
      const videoIdMatch = watchUrl.match(/v=([^&]+)/);
      const videoId = videoIdMatch ? videoIdMatch[1] : '';
      
      // Extract start_time in seconds from the URL's t parameter
      const tParamMatch = watchUrl.match(/t=(\d+)/);
      const startTime = tParamMatch ? parseFloat(tParamMatch[1]) : 0;
      
      // Create recovered segment data
      return {
        type: 'transcription_segment',
        content: {
          text: text.trim(),
          start_time: startTime,
          end_time: startTime + (text.length / 20), // Rough estimate
          id: Date.now(), // Use timestamp as fallback ID
          video_id: videoId,
          watch_url: watchUrl,
          timestamp: timestamp1
        }
      };
    }
    
    // Return a minimal object if recovery fails
    return {
      type: 'error',
      content: `Failed to parse segment data: ${error.message}`
    };
  }
}

/**
 * Format a timestamp in seconds to HH:MM:SS.MS format
 * 
 * @param {number} seconds - The time in seconds
 * @returns {string} - Formatted timestamp
 */
export function formatTimeStamp(seconds) {
  if (isNaN(seconds) || seconds < 0) return '00:00.00';
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 100);
  
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(2, '0')}`;
}

/**
 * Safely extract YouTube video ID from a URL
 * 
 * @param {string} url - YouTube URL
 * @returns {string} - Video ID or empty string if not found
 */
export function extractVideoId(url) {
  if (!url) return '';
  
  try {
    // Handle both youtube.com and youtu.be links
    const match = url.match(
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?/]+)/
    );
    return match ? match[1] : '';
  } catch (error) {
    console.error('Error extracting video ID:', error);
    return '';
  }
}

/**
 * Create a YouTube timestamp URL
 * 
 * @param {string} videoId - YouTube video ID
 * @param {number} startTime - Start time in seconds
 * @returns {string} - YouTube URL with timestamp
 */
export function createYoutubeTimestampUrl(videoId, startTime) {
  if (!videoId) return '';
  
  const timestamp = Math.floor(startTime);
  return `https://www.youtube.com/watch?v=${videoId}&t=${timestamp}`;
}

/**
 * Add a new transcription segment to the existing segments array
 * Handles deduplication and sorting
 * 
 * @param {Array} segments - Existing transcription segments
 * @param {Object} newSegment - New segment to add
 * @returns {Array} - Updated segments array
 */
export function addTranscriptionSegment(segments, newSegment) {
  if (!newSegment || !newSegment.text) return segments;
  
  // Check for duplicates
  const isDuplicate = segments.some(segment => 
    segment.start_time === newSegment.start_time && 
    segment.end_time === newSegment.end_time && 
    segment.text === newSegment.text
  );
  
  if (isDuplicate) return segments;
  
  // Add the new segment and sort by start_time
  return [...segments, newSegment].sort((a, b) => a.start_time - b.start_time);
}
