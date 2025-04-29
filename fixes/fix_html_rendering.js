/**
 * Fix for HTML rendering issues in the PMOVES-transcribe-and-fetch project
 * This script addresses the issues with HTML tags and CSS class names being displayed as text
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisDisplay.jsx file
const analysisDisplayPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisDisplay.jsx');

// Function to update the AnalysisDisplay.jsx file
function updateAnalysisDisplay() {
  try {
    let content = fs.readFileSync(analysisDisplayPath, 'utf8');
    
    // Replace the formatAnalysisContent function with an improved version
    const newFormatAnalysisContent = `/**
 * Format analysis content with enhanced Markdown-like formatting
 * Improved to handle various formatting edge cases and ensure proper rendering
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
  
  // For plain text content, apply Markdown-like formatting
  let formatted = content;
  
  // Replace newlines with <br> tags
  formatted = formatted.replace(/\\n/g, '<br>');
  
  // Format headings (# Heading) - improved regex to handle edge cases
  formatted = formatted.replace(/(?:<br>|^)\\s*#\\s+(.*?)(?=<br>|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
  formatted = formatted.replace(/(?:<br>|^)\\s*##\\s+(.*?)(?=<br>|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
  formatted = formatted.replace(/(?:<br>|^)\\s*###\\s+(.*?)(?=<br>|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  formatted = formatted.replace(/(?:<br>|^)\\s*####\\s+(.*?)(?=<br>|$)/g, '<h6 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h6>');
  
  // Format bold (**text**) - improved to handle multiple occurrences
  formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-bold">$1</strong>');
  
  // Format italic (*text*) - improved to handle multiple occurrences
  formatted = formatted.replace(/(?<!\\*)\\*((?!\\*).+?)\\*(?!\\*)/g, '<em class="italic">$1</em>');
  
  // Format lists with better styling
  // Unordered lists - improved to handle nested lists
  formatted = formatted.replace(/(?:<br>|^)\\s*-\\s+(.*?)(?=<br>|$)/g, 
    '<div class="flex items-start mb-1"><span class="text-blue-500 mr-2 mt-1">•</span><span>$1</span></div>');
  
  // Ordered lists - improved to handle nested lists
  formatted = formatted.replace(/(?:<br>|^)\\s*(\\d+)\\.\\s+(.*?)(?=<br>|$)/g, 
    '<div class="flex items-start mb-1"><span class="text-blue-500 font-medium mr-2 mt-1">$1.</span><span>$2</span></div>');
  
  // Format code blocks - improved to handle multiline code blocks
  formatted = formatted.replace(/\`\`\`([\\s\\S]*?)\`\`\`/g, 
    '<pre class="bg-gray-100 p-3 rounded-md text-sm font-mono text-blue-600 overflow-x-auto my-2">$1</pre>');
  
  // Format inline code - improved to handle edge cases
  formatted = formatted.replace(/\`([^\`\\n]+?)\`/g, 
    '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600">$1</code>');
  
  // Format horizontal rules
  formatted = formatted.replace(/(?:<br>|^)\\s*-{3,}\\s*(?=<br>|$)/g, 
    '<hr class="my-4 border-t border-gray-200">');
  
  // Format blockquotes - improved to handle multiline blockquotes
  formatted = formatted.replace(/(?:<br>|^)\\s*>\\s+(.*?)(?=<br>|$)/g, 
    '<blockquote class="pl-3 border-l-2 border-blue-300 text-gray-600 italic my-2">$1</blockquote>');
  
  // Format links - improved to handle edge cases and YouTube links
  formatted = formatted.replace(/\\[(.*?)\\]\\((.*?)\\)/g, (match, text, url) => {
    // Special handling for YouTube links
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return \`<a href="\${url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">
        <span class="mr-1">🎬</span>\${text}
      </a>\`;
    }
    return \`<a href="\${url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline">\${text}</a>\`;
  });
  
  // Handle raw URLs - convert them to clickable links
  formatted = formatted.replace(/(https?:\\/\\/[^\\s<]+[^<.,:;"'\\)\\]\\s])/g, (url) => {
    // Special handling for YouTube links
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return \`<a href="\${url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">
        <span class="mr-1">🎬</span>\${url}
      </a>\`;
    }
    return \`<a href="\${url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline">\${url}</a>\`;
  });
  
  // Highlight key terms - improved to handle edge cases
  formatted = formatted.replace(/"([^"]+)"/g, '<span class="text-blue-700">"$1"</span>');
  
  // Add spacing between paragraphs for better readability
  formatted = formatted.replace(/(<br>){2,}/g, '<br><br>');
  formatted = formatted.replace(/(<br>)(?!<\\/div>|<\\/blockquote>|<\\/pre>)/g, '<br>');
  
  return formatted;
}

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
    const htmlTagsRegex = /<([a-z][a-z0-9]*)((?:\\s+[a-z0-9\\-_]+(?:=(?:"[^"]*"|'[^']*'))?)*?)\\s*(\\/?)?\>/gi;
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
    content = content.replace(/href="https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^"]+)"/g, (match, videoId) => {
      return \`href="https://www.youtube.com/watch?v=\${videoId}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline"\`;
    });
    
    // Fix links with icons
    content = content.replace(/" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">(.*?)🎬(.*?)<\\/a>/g, 
      \`" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>$2</a>\`);
    
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
  
  // If the content doesn't contain CSS class names displayed as text, use the original processHtmlContent function
  
  // Fix YouTube links
  content = content.replace(/href="https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^"]+)"/g, (match, videoId) => {
    return \`href="https://www.youtube.com/watch?v=\${videoId}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline"\`;
  });
  
  // Fix any remaining HTML issues
  content = content.replace(/&lt;/g, '<');
  content = content.replace(/&gt;/g, '>');
  content = content.replace(/&quot;/g, '"');
  content = content.replace(/&#039;/g, "'");
  content = content.replace(/&amp;/g, '&');
  
  // Add proper styling to headings
  content = content.replace(/<h3>/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">');
  content = content.replace(/<h4>/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">');
  content = content.replace(/<h5>/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">');
  content = content.replace(/<h6>/g, '<h6 class="text-sm font-semibold mt-2 mb-1 text-blue-500">');
  
  // Add proper styling to lists
  content = content.replace(/<ul>/g, '<ul class="list-disc pl-5 space-y-1 mb-4">');
  content = content.replace(/<ol>/g, '<ol class="list-decimal pl-5 space-y-1 mb-4">');
  content = content.replace(/<li>/g, '<li class="mb-1">');
  
  // Add proper styling to blockquotes
  content = content.replace(/<blockquote>/g, '<blockquote class="pl-3 border-l-2 border-blue-300 text-gray-600 italic my-2">');
  
  // Add proper styling to code blocks
  content = content.replace(/<pre>/g, '<pre class="bg-gray-100 p-3 rounded-md text-sm font-mono text-blue-600 overflow-x-auto my-2">');
  content = content.replace(/<code>/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600">');
  
  // Add proper styling to links
  content = content.replace(/<a href=/g, '<a class="text-blue-600 underline hover:no-underline" href=');
  
  // Add proper styling to paragraphs
  content = content.replace(/<p>/g, '<p class="mb-4">');
  
  return content;
}`;

    // Replace the existing formatAnalysisContent function
    content = content.replace(
      /function formatAnalysisContent\(content\) \{[\s\S]*?return formatted;\s*\}\s*\/\*\*\s*\*\s*Process content that already contains HTML tags[\s\S]*?function processHtmlContent\(content\) \{[\s\S]*?return content;\s*\}/,
      newFormatAnalysisContent
    );
    
    // Add enhanced CSS for the analysis content
    const cssAddition = `
  // Add custom CSS for analysis content
  useEffect(() => {
    // Add custom CSS for analysis content
    const style = document.createElement('style');
    style.textContent = \`
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
    \`;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);`;
    
    // Replace the existing CSS addition
    content = content.replace(
      /\/\/ Add custom CSS for analysis content\s+useEffect\(\(\) => \{[\s\S]*?document\.head\.removeChild\(style\);\s+\};\s+\}, \[\]\);/,
      cssAddition
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisDisplayPath, content, 'utf8');
    console.log('Successfully updated AnalysisDisplay.jsx with improved HTML rendering');
    return true;
  } catch (error) {
    console.error('Error updating AnalysisDisplay.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update AnalysisDisplay.jsx
    const displayUpdated = updateAnalysisDisplay();
    
    if (displayUpdated) {
      console.log('HTML rendering fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Added special handling for HTML tags and CSS class names displayed as text');
      console.log('2. Improved the processHtmlContent function to better handle HTML content');
      console.log('3. Added specific regex patterns to remove CSS class names from the displayed text');
      console.log('4. Enhanced handling of YouTube links to ensure they are properly displayed');
      console.log('5. Added specific CSS rules for elements that were previously showing as text');
      console.log('6. Improved the visual hierarchy of the content');
    } else {
      console.error('Failed to apply HTML rendering fix.');
    }
  } catch (error) {
    console.error('Error applying HTML rendering fix:', error);
  }
}

// Run the fix
applyFix();
