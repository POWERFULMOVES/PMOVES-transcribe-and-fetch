/**
 * fix_sse_frontend.js - Fix SSE message parsing in frontend code
 * 
 * This script updates the useSSE.js hook to handle the "data: " prefix in SSE messages.
 */

const fs = require('fs');
const path = require('path');

// Path to the useSSE.js file
const useSSEPath = path.join('src', 'hooks', 'useSSE.js');

// Read the current content of the file
console.log(`Reading ${useSSEPath}...`);
let content;
try {
  content = fs.readFileSync(useSSEPath, 'utf8');
  console.log(`Successfully read ${useSSEPath}`);
} catch (error) {
  console.error(`Error reading ${useSSEPath}:`, error);
  process.exit(1);
}

// Find the onmessage handler and update it to handle the "data: " prefix
const originalOnMessagePattern = /eventSource\.onmessage\s*=\s*\(\s*event\s*\)\s*=>\s*{[^}]*try\s*{[^}]*const\s+data\s*=\s*JSON\.parse\s*\(\s*event\.data\s*\)/;
const updatedOnMessage = `eventSource.onmessage = (event) => {
      try {
        // Remove the "data: " prefix if it exists
        const jsonStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;
        const data = JSON.parse(jsonStr)`;

// Replace the onmessage handler
const updatedContent = content.replace(originalOnMessagePattern, updatedOnMessage);

// Check if the content was updated
if (content === updatedContent) {
  console.error('Could not find the onmessage handler in the useSSE.js file.');
  process.exit(1);
}

// Write the updated content back to the file
console.log(`Writing updated content to ${useSSEPath}...`);
try {
  fs.writeFileSync(useSSEPath, updatedContent, 'utf8');
  console.log(`✅ Successfully updated ${useSSEPath}`);
} catch (error) {
  console.error(`Error writing to ${useSSEPath}:`, error);
  process.exit(1);
}

console.log('✅ SSE frontend fix applied successfully!');
