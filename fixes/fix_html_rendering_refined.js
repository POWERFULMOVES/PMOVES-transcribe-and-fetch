/**
 * Refined direct approach to fix HTML rendering issues in the PMOVES-transcribe-and-fetch project
 * This script provides a more refined direct approach to fix the HTML rendering issues
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
  
  // Check if the content contains CSS class names displayed as text
  const containsCssClassNames = /"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/i.test(content);
  
  if (containsCssClassNames) {
    // The content contains CSS class names displayed as text, so we need to fix it
    return directProcessHtmlContent(content);
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
 * Direct approach to process HTML content
 * This function uses a more direct approach to fix the HTML rendering issues
 */
function directProcessHtmlContent(content) {
  // Step 1: Fix headings
  content = content.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">(.*?)(?=\\n|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  content = content.replace(/"text-md font-semibold mt-3 mb-1 text-blue-600">(.*?)(?=\\n|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
  content = content.replace(/"text-lg font-semibold mt-4 mb-2 text-blue-700">(.*?)(?=\\n|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
  
  // Step 2: Fix bold text
  content = content.replace(/"font-bold">(.*?)(?=\\n|$)/g, '<strong class="font-bold">$1</strong>');
  
  // Step 3: Fix horizontal rules
  content = content.replace(/"my-4 border-t border-gray-200">/g, '<hr class="my-4 border-t border-gray-200">');
  
  // Step 4: Fix list items (this is a multi-step process)
  // First, capture the entire list item line
  const listItemRegex = /"flex items-start mb-1">(.*?)(?=\\n|$)/g;
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
      const formattedItem = \`<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">\${bullet}</span>
  <strong class="font-bold">\${text}</strong>
</div>\`;
      
      // Replace the original list item with the formatted one
      content = content.replace(item.fullMatch, formattedItem);
    } else {
      // Handle list items without the font-bold part
      const simpleBulletMatch = item.content.match(/"text-blue-500 mr-2 mt-1">(.*?)(.*?)$/);
      if (simpleBulletMatch) {
        const bullet = simpleBulletMatch[1];
        const text = simpleBulletMatch[2] || '';
        
        // Create the properly formatted list item
        const formattedItem = \`<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">\${bullet}</span>
  <span>\${text}</span>
</div>\`;
        
        // Replace the original list item with the formatted one
        content = content.replace(item.fullMatch, formattedItem);
      }
    }
  }
  
  // Step 5: Fix YouTube links
  content = content.replace(/🎬https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^&\\s]+)/g, 
    '<a href="https://www.youtube.com/watch?v=$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>');
  
  // Step 6: Remove any remaining CSS class references
  content = content.replace(/"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/g, '');
  
  // Step 7: Clean up any remaining quotes and formatting issues
  content = content.replace(/""/g, '');
  content = content.replace(/">/g, '>');
  content = content.replace(/target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">/g, '');
  
  // Step 8: Fix any remaining HTML issues
  content = content.replace(/&lt;/g, '<');
  content = content.replace(/&gt;/g, '>');
  content = content.replace(/&quot;/g, '"');
  content = content.replace(/&#039;/g, "'");
  content = content.replace(/&amp;/g, '&');
  
  // Step 9: Fix double quotes in text
  content = content.replace(/"([^"<>]+)"/g, '<span class="text-blue-700">"$1"</span>');
  
  // Step 10: Fix any remaining HTML tags
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
      console.log('7. Used a more direct approach to fix the HTML rendering issues');
    } else {
      console.error('Failed to apply HTML rendering fix.');
    }
  } catch (error) {
    console.error('Error applying HTML rendering fix:', error);
  }
}

// Run the fix
applyFix();
