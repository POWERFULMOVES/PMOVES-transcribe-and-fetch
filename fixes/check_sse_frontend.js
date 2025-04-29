/**
 * SSE Frontend Connection Checker
 * 
 * This script checks if the frontend is properly handling SSE messages
 * by adding debug logging to the useSSE hook and the onMessage handler.
 */

const fs = require('fs');
const path = require('path');

// Paths to the files we need to check
const useSSEPath = path.join('src', 'hooks', 'useSSE.js');
const pagePath = path.join('src', 'app', 'page.js');

// Check if the files exist
if (!fs.existsSync(useSSEPath)) {
  console.error(`Error: ${useSSEPath} not found`);
  process.exit(1);
}

if (!fs.existsSync(pagePath)) {
  console.error(`Error: ${pagePath} not found`);
  process.exit(1);
}

// Read the files
let useSSEContent = fs.readFileSync(useSSEPath, 'utf8');
let pageContent = fs.readFileSync(pagePath, 'utf8');

// Add debug logging to useSSE.js
console.log('Adding debug logging to useSSE.js...');

// Check if debug logging is already added
if (!useSSEContent.includes('// SSE DEBUG LOGGING')) {
  // Add debug logging to the parseMessage function
  const parseMessageRegex = /const parseMessage = useCallback\(\(data\) => \{([\s\S]*?)\}, \[\]\);/;
  if (parseMessageRegex.test(useSSEContent)) {
    useSSEContent = useSSEContent.replace(
      parseMessageRegex,
      `const parseMessage = useCallback((data) => {
  // SSE DEBUG LOGGING
  console.log('[useSSE] Parsing message data:', typeof data, data);
$1
  // SSE DEBUG LOGGING
  console.log('[useSSE] Parsed message result:', result);
  return result;
}, []);`
    );
  } else {
    console.warn('Could not find parseMessage function in useSSE.js');
  }

  // Add debug logging to the onmessage handler
  const onmessageRegex = /eventSourceRef\.current\.onmessage = \(event\) => \{([\s\S]*?)\};/;
  if (onmessageRegex.test(useSSEContent)) {
    useSSEContent = useSSEContent.replace(
      onmessageRegex,
      `eventSourceRef.current.onmessage = (event) => {
          // SSE DEBUG LOGGING
          console.log('[useSSE] Raw SSE message received:', event.data);
$1
          // SSE DEBUG LOGGING
          console.log('[useSSE] Message processed and added to state');
        };`
    );
  } else {
    console.warn('Could not find onmessage handler in useSSE.js');
  }

  // Write the updated content back to the file
  fs.writeFileSync(useSSEPath, useSSEContent);
  console.log('Added debug logging to useSSE.js');
} else {
  console.log('Debug logging already added to useSSE.js');
}

// Add debug logging to page.js
console.log('Adding debug logging to page.js...');

// Check if debug logging is already added
if (!pageContent.includes('// PAGE.JS SSE DEBUG LOGGING')) {
  // Add debug logging to the onMessage handler in useSSE hook
  const useSSEHookRegex = /onMessage: \(data\) => \{([\s\S]*?)\},/;
  if (useSSEHookRegex.test(pageContent)) {
    pageContent = pageContent.replace(
      useSSEHookRegex,
      `onMessage: (data) => {
      // PAGE.JS SSE DEBUG LOGGING
      console.log('[page.js] SSE message received:', data);
$1
      // PAGE.JS SSE DEBUG LOGGING
      console.log('[page.js] SSE message processed');
    },`
    );
  } else {
    console.warn('Could not find onMessage handler in page.js');
  }

  // Add debug logging to the transcription segment handling
  const transcriptionSegmentRegex = /else if \(data\.type === 'transcription_segment'\) \{([\s\S]*?)\}/;
  if (transcriptionSegmentRegex.test(pageContent)) {
    pageContent = pageContent.replace(
      transcriptionSegmentRegex,
      `else if (data.type === 'transcription_segment') {
          // PAGE.JS SSE DEBUG LOGGING
          console.log('[page.js] Processing transcription segment:', data.content);
$1
          // PAGE.JS SSE DEBUG LOGGING
          console.log('[page.js] Transcription segment processed and added to state');
        }`
    );
  } else {
    console.warn('Could not find transcription_segment handler in page.js');
  }

  // Write the updated content back to the file
  fs.writeFileSync(pagePath, pageContent);
  console.log('Added debug logging to page.js');
} else {
  console.log('Debug logging already added to page.js');
}

console.log('\nSSE frontend connection checker complete.');
console.log('To test:');
console.log('1. Start the backend server: cd backend && uvicorn app.main:app --reload --port 8000');
console.log('2. Start the frontend server: npm run dev');
console.log('3. Open the browser console and navigate to http://localhost:3000');
console.log('4. Start a transcription and check the console logs for SSE messages');
console.log('5. Look for any errors or missing messages in the console logs');
