/**
 * Direct approach to fix HTML rendering issues in the PMOVES-transcribe-and-fetch project
 * This script demonstrates a more direct approach to fix the HTML rendering issues
 */

// Sample analysis with HTML tags and CSS class names displayed as text
const sampleAnalysis = `"text-sm font-semibold mt-2 mb-1 text-blue-500">Search Results Summary 

"font-bold">Total Results Analyzed: 1
"font-bold">Source: Video Transcription
"font-bold">Relevance Score: 0.528
"my-4 border-t border-gray-200">
"text-sm font-semibold mt-2 mb-1 text-blue-500">Detailed Analysis of Result:

"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Title: Untitled
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Content ID: iG1Vxj2L_ZE
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Timestamp: 00:04:13 to 00:04:25
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">URL: "" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"> ">🎬https://www.youtube.com/watch?v=iG1Vxj2L_ZE&t=253 " target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"> "mr-1">🎬Watch Video
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Content Summary: The segment features characters Shockwave and Soundwave observing marine life outside the Nemesis. However, the moment of admiration is contrasted by Shockwave's readiness to activate his Cybertronian thresher, indicating a shift from awe to action.

"my-4 border-t border-gray-200">
"text-sm font-semibold mt-2 mb-1 text-blue-500">Key Information Extracted:
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Characters Involved: Shockwave and Soundwave
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Setting: Outside the Nemesis, observing marine life
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">Theme: A juxtaposition of wonder and impending action, highlighting the complexity of the characters' emotions and motivations.

"text-sm font-semibold mt-2 mb-1 text-blue-500">Connections:
"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•The content reflects themes common in narratives involving Cybertronian characters, where moments of beauty are often interrupted by the harsh realities of their existence and duties.

"text-sm font-semibold mt-2 mb-1 text-blue-500">Conclusion:

The result provides a brief yet intriguing glimpse into a moment shared between two characters, emphasizing the contrast between admiration for nature and the harshness of their reality. This could be of interest to fans of the franchise or those studying character dynamics in animated series.`;

/**
 * Direct approach to process HTML content
 * This function uses a more direct approach to fix the HTML rendering issues
 */
function directProcessHtmlContent(content) {
  // Step 1: Fix headings
  content = content.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">(.*?)(?=\n|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  
  // Step 2: Fix bold text
  content = content.replace(/"font-bold">(.*?)(?=\n|$)/g, '<strong class="font-bold">$1</strong>');
  
  // Step 3: Fix horizontal rules
  content = content.replace(/"my-4 border-t border-gray-200">/g, '<hr class="my-4 border-t border-gray-200">');
  
  // Step 4: Fix list items (this is a multi-step process)
  // First, capture the entire list item line
  const listItemRegex = /"flex items-start mb-1">(.*?)(?=\n|$)/g;
  const listItems = [];
  let match;
  
  // Find all list items
  while ((match = listItemRegex.exec(content)) !== null) {
    listItems.push({
      fullMatch: match[0],
      content: match[1],
      index: match.index
    });
  }
  
  // Process each list item
  for (const item of listItems) {
    // Extract the bullet point and text
    const bulletMatch = item.content.match(/"text-blue-500 mr-2 mt-1">(.*?)"font-bold">(.*?)$/);
    if (bulletMatch) {
      const bullet = bulletMatch[1];
      const text = bulletMatch[2];
      
      // Create the properly formatted list item
      const formattedItem = `<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">${bullet}</span>
  <strong class="font-bold">${text}</strong>
</div>`;
      
      // Replace the original list item with the formatted one
      content = content.replace(item.fullMatch, formattedItem);
    } else {
      // Handle list items without the font-bold part
      const simpleBulletMatch = item.content.match(/"text-blue-500 mr-2 mt-1">(.*?)(.*?)$/);
      if (simpleBulletMatch) {
        const bullet = simpleBulletMatch[1];
        const text = simpleBulletMatch[2] || '';
        
        // Create the properly formatted list item
        const formattedItem = `<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">${bullet}</span>
  <span>${text}</span>
</div>`;
        
        // Replace the original list item with the formatted one
        content = content.replace(item.fullMatch, formattedItem);
      }
    }
  }
  
  // Step 5: Fix YouTube links
  content = content.replace(/🎬https:\/\/www\.youtube\.com\/watch\?v=([^&\s]+)/g, 
    '<a href="https://www.youtube.com/watch?v=$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>');
  
  // Step 6: Remove any remaining CSS class references
  content = content.replace(/"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/g, '');
  
  // Step 7: Clean up any remaining quotes and formatting issues
  content = content.replace(/""/g, '');
  content = content.replace(/">/g, '>');
  content = content.replace(/target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">/g, '');
  
  return content;
}

// Process the sample analysis
const processedAnalysis = directProcessHtmlContent(sampleAnalysis);

// Create an HTML file to display the processed analysis
const fs = require('fs');
const path = require('path');

const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Rendering Test (Direct Approach)</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .container {
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px;
      background-color: #f8fafc;
    }
    .original, .processed {
      margin-bottom: 30px;
    }
    h2 {
      color: #2563eb;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 10px;
    }
    pre {
      background-color: #f1f5f9;
      padding: 15px;
      border-radius: 6px;
      overflow-x: auto;
      white-space: pre-wrap;
    }
    /* Styling for the processed content */
    h5.text-sm {
      font-size: 1rem;
      color: rgb(59, 130, 246);
      margin-top: 1rem;
      margin-bottom: 0.5rem;
      font-weight: 600;
      line-height: 1.4;
    }
    strong.font-bold {
      font-weight: 600;
      color: rgb(31, 41, 55);
    }
    hr.my-4 {
      margin: 1.5rem 0;
      border-top: 1px solid rgb(229, 231, 235);
    }
    div.flex {
      display: flex;
    }
    div.items-start {
      align-items: flex-start;
    }
    div.mb-1 {
      margin-bottom: 0.25rem;
    }
    span.mr-2 {
      margin-right: 0.5rem;
    }
    span.mt-1 {
      margin-top: 0.25rem;
    }
    span.text-blue-500 {
      color: rgb(59, 130, 246);
    }
    a.text-blue-600 {
      color: rgb(37, 99, 235);
      text-decoration: underline;
      transition: all 0.2s ease;
    }
    a.text-blue-600:hover {
      text-decoration: none;
      color: rgb(29, 78, 216);
    }
    .flex.items-start {
      display: flex;
      align-items: flex-start;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="original">
      <h2>Original Analysis</h2>
      <pre>${sampleAnalysis.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
    </div>
    
    <div class="processed">
      <h2>Processed Analysis (Direct Approach)</h2>
      <div class="analysis-formatted-content">${processedAnalysis}</div>
    </div>
  </div>
</body>
</html>
`;

// Write the HTML file
fs.writeFileSync(path.join(process.cwd(), 'test_html_rendering_direct.html'), htmlContent);

console.log('Test HTML rendering file created: test_html_rendering_direct.html');
console.log('Open this file in a browser to see how the direct HTML rendering approach would work with the sample analysis.');
