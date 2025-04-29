/**
 * Test script for HTML rendering in the PMOVES-transcribe-and-fetch project
 * This script demonstrates how the improved HTML rendering would work with a sample analysis
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
 * Process content that already contains HTML tags
 * Improved to handle HTML tags and CSS class names being displayed as text
 */
function processHtmlContent(content) {
  // First, check if the content contains CSS class names displayed as text
  const containsCssClassNames = /"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/i.test(content);
  
  if (containsCssClassNames) {
    // The content contains CSS class names displayed as text, so we need to fix it
    
    // Step 1: Extract all the HTML tags and their attributes
    const htmlTagsRegex = /<([a-z][a-z0-9]*)((?:\s+[a-z0-9\-_]+(?:=(?:"[^"]*"|'[^']*'))?)*?)\s*(\/?)?>/gi;
    const htmlTags = [];
    let match;
    while ((match = htmlTagsRegex.exec(content)) !== null) {
      htmlTags.push({
        tag: match[0],
        tagName: match[1],
        attributes: match[2],
        selfClosing: match[3] === '/',
        index: match.index
      });
    }
    
    // Step 2: Replace all CSS class names displayed as text with empty strings
    content = content.replace(/"([^"]*?)(text-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(font-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(bg-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(mr-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(mt-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(mb-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(ml-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(p-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(m-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(flex[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(items-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(justify-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(rounded[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(border[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(shadow[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(transition[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(duration[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(ease[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(opacity[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(transform[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(translate[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(scale[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(rotate[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(skew[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(origin[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(overflow[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(z-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(gap-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(space-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(grid[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(col-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(row-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(auto-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(min-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(max-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(w-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(h-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(top-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(right-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(bottom-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(left-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(inset-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(object-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(box-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(cursor-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(pointer-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(select-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(resize-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(sr-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(not-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(first-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(last-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(odd-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(even-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(visited-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(checked-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(focus-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(hover-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(active-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(disabled-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(placeholder-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(ring-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(backdrop-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(filter-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(blur-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(brightness-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(contrast-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(drop-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(grayscale-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(hue-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(invert-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(saturate-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(sepia-[^"]*?)"/g, '""');
    content = content.replace(/"([^"]*?)(backdrop-[^"]*?)"/g, '""');
    
    // Step 3: Replace all empty quotes with nothing
    content = content.replace(/""/g, '');
    
    // Step 4: Fix any remaining HTML issues
    content = content.replace(/&lt;/g, '<');
    content = content.replace(/&gt;/g, '>');
    content = content.replace(/&quot;/g, '"');
    content = content.replace(/&#039;/g, "'");
    content = content.replace(/&amp;/g, '&');
    
    // Step 5: Fix specific patterns in the content
    
    // Fix headings
    content = content.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">(.*?)(?=<|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
    content = content.replace(/"text-md font-semibold mt-3 mb-1 text-blue-600">(.*?)(?=<|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
    content = content.replace(/"text-lg font-semibold mt-4 mb-2 text-blue-700">(.*?)(?=<|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
    
    // Fix bold text
    content = content.replace(/"font-bold">(.*?)(?=<|$)/g, '<strong class="font-bold">$1</strong>');
    
    // Fix list items
    content = content.replace(/"flex items-start mb-1">(.*?)(?=<div|$)/g, '<div class="flex items-start mb-1">$1</div>');
    content = content.replace(/"text-blue-500 mr-2 mt-1">(.*?)(?=<|$)/g, '<span class="text-blue-500 mr-2 mt-1">$1</span>');
    content = content.replace(/"text-blue-500 font-medium mr-2 mt-1">(.*?)(?=<|$)/g, '<span class="text-blue-500 font-medium mr-2 mt-1">$1</span>');
    
    // Fix horizontal rules
    content = content.replace(/"my-4 border-t border-gray-200">/g, '<hr class="my-4 border-t border-gray-200">');
    
    // Fix YouTube links
    content = content.replace(/href="https:\/\/www\.youtube\.com\/watch\?v=([^"]+)"/g, (match, videoId) => {
      return `href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline"`;
    });
    
    // Fix links with icons
    content = content.replace(/" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">(.*?)🎬(.*?)<\/a>/g, 
      `" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>$2</a>`);
    
    // Fix double quotes in text
    content = content.replace(/"([^"<>]+)"/g, '<span class="text-blue-700">"$1"</span>');
    
    // Add proper styling to elements
    content = content.replace(/<h3>/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">');
    content = content.replace(/<h4>/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">');
    content = content.replace(/<h5>/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">');
    content = content.replace(/<h6>/g, '<h6 class="text-sm font-semibold mt-2 mb-1 text-blue-500">');
    content = content.replace(/<ul>/g, '<ul class="list-disc pl-5 space-y-1 mb-4">');
    content = content.replace(/<ol>/g, '<ol class="list-decimal pl-5 space-y-1 mb-4">');
    content = content.replace(/<li>/g, '<li class="mb-1">');
    content = content.replace(/<blockquote>/g, '<blockquote class="pl-3 border-l-2 border-blue-300 text-gray-600 italic my-2">');
    content = content.replace(/<pre>/g, '<pre class="bg-gray-100 p-3 rounded-md text-sm font-mono text-blue-600 overflow-x-auto my-2">');
    content = content.replace(/<code>/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600">');
    content = content.replace(/<a href=/g, '<a class="text-blue-600 underline hover:no-underline" href=');
    content = content.replace(/<p>/g, '<p class="mb-4">');
    
    return content;
  }
  
  return content;
}

/**
 * Format analysis content with enhanced Markdown-like formatting
 */
function formatAnalysisContent(content) {
  if (!content) return '';
  
  // Check if the content already contains HTML tags
  const containsHtml = /<[a-z][\s\S]*>/i.test(content);
  
  // If the content already contains HTML, we need to handle it differently
  if (containsHtml) {
    // Process the content to fix any issues with HTML tags
    return processHtmlContent(content);
  }
  
  return content;
}

// Process the sample analysis
const processedAnalysis = formatAnalysisContent(sampleAnalysis);

// Create an HTML file to display the processed analysis
const fs = require('fs');
const path = require('path');

const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Rendering Test</title>
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
    .analysis-formatted-content h3, 
    .analysis-formatted-content h4, 
    .analysis-formatted-content h5,
    .analysis-formatted-content h6 {
      margin-top: 1rem;
      margin-bottom: 0.5rem;
      font-weight: 600;
      line-height: 1.4;
    }
    .analysis-formatted-content h3 {
      font-size: 1.25rem;
      color: rgb(29, 78, 216);
    }
    .analysis-formatted-content h4 {
      font-size: 1.125rem;
      color: rgb(37, 99, 235);
    }
    .analysis-formatted-content h5,
    .analysis-formatted-content h6 {
      font-size: 1rem;
      color: rgb(59, 130, 246);
    }
    .analysis-formatted-content ul, 
    .analysis-formatted-content ol {
      margin-left: 1.5rem;
      margin-bottom: 1rem;
      padding-left: 1rem;
    }
    .analysis-formatted-content li {
      margin-bottom: 0.25rem;
      padding-left: 0.25rem;
    }
    .analysis-formatted-content p {
      margin-bottom: 0.75rem;
      line-height: 1.6;
    }
    .analysis-formatted-content blockquote {
      border-left: 2px solid rgb(147, 197, 253);
      padding-left: 0.75rem;
      margin: 0.75rem 0;
      font-style: italic;
      color: rgb(75, 85, 99);
    }
    .analysis-formatted-content pre {
      background-color: rgb(243, 244, 246);
      padding: 0.75rem;
      border-radius: 0.375rem;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.875rem;
      margin: 0.75rem 0;
      white-space: pre-wrap;
    }
    .analysis-formatted-content code {
      background-color: rgb(243, 244, 246);
      padding: 0.125rem 0.375rem;
      border-radius: 0.25rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.875rem;
      white-space: nowrap;
    }
    .analysis-formatted-content a {
      color: rgb(37, 99, 235);
      text-decoration: underline;
      transition: all 0.2s ease;
    }
    .analysis-formatted-content a:hover {
      text-decoration: none;
      color: rgb(29, 78, 216);
    }
    .analysis-formatted-content strong {
      font-weight: 600;
      color: rgb(31, 41, 55);
    }
    .analysis-formatted-content em {
      font-style: italic;
      color: rgb(55, 65, 81);
    }
    .analysis-formatted-content hr {
      margin: 1.5rem 0;
      border-top: 1px solid rgb(229, 231, 235);
    }
    .analysis-formatted-content .flex {
      display: flex;
    }
    .analysis-formatted-content .items-start {
      align-items: flex-start;
    }
    .analysis-formatted-content .mb-1 {
      margin-bottom: 0.25rem;
    }
    .analysis-formatted-content .mr-2 {
      margin-right: 0.5rem;
    }
    .analysis-formatted-content .mt-1 {
      margin-top: 0.25rem;
    }
    .analysis-formatted-content .text-blue-500 {
      color: rgb(59, 130, 246);
    }
    .analysis-formatted-content .font-medium {
      font-weight: 500;
    }
    .analysis-formatted-content .text-blue-700 {
      color: rgb(29, 78, 216);
    }
    .analysis-formatted-content .font-bold {
      font-weight: 700;
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
      <h2>Processed Analysis</h2>
      <div class="analysis-formatted-content">${processedAnalysis}</div>
    </div>
  </div>
</body>
</html>
`;

// Write the HTML file
fs.writeFileSync(path.join(process.cwd(), 'test_html_rendering.html'), htmlContent);

console.log('Test HTML rendering file created: test_html_rendering.html');
console.log('Open this file in a browser to see how the HTML rendering would work with the sample analysis.');
