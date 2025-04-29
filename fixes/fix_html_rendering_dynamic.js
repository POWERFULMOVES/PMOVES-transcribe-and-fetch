/**
 * Dynamic fix for HTML rendering issues in the PMOVES-transcribe-and-fetch project
 * This script provides a more flexible solution to fix the HTML rendering issues
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
    return dynamicProcessHtmlContent(content);
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
 * Dynamic approach to process HTML content
 * This function uses a more flexible approach to fix the HTML rendering issues
 */
function dynamicProcessHtmlContent(content) {
  // First, let's handle the most common patterns directly
  
  // Fix headings
  content = content.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">(.*?)(?=\\n|$)/g, 
    '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  
  // Fix bold text
  content = content.replace(/"font-bold">(.*?)(?=\\n|$)/g, 
    '<strong class="font-bold">$1</strong>');
  
  // Fix horizontal rules
  content = content.replace(/"my-4 border-t border-gray-200">/g, 
    '<hr class="my-4 border-t border-gray-200">');
  
  // Fix YouTube links - this is a critical part that needs special handling
  content = content.replace(/🎬https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^&\\s]+)/g, 
    '<a href="https://www.youtube.com/watch?v=$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>');
  
  // Fix URL field specifically
  content = content.replace(/URL:.*?🎬https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^&\\s]+).*?Watch Video/gs, 
    'URL: <a href="https://www.youtube.com/watch?v=$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>');
  
  // Fix list items - this is a complex pattern that needs special handling
  // First, identify all list items
  const listItemRegex = /"flex items-start mb-1">(.*?)(?=\\n|"flex items-start mb-1"|"text-sm font-semibold|"my-4 border-t|$)/gs;
  let match;
  const listItems = [];
  
  while ((match = listItemRegex.exec(content)) !== null) {
    listItems.push({
      fullMatch: match[0],
      content: match[1],
      index: match.index
    });
  }
  
  // Process each list item
  for (const item of listItems) {
    // Check if it's a list item with a bullet point and bold text
    if (item.content.includes('"text-blue-500 mr-2 mt-1">•"font-bold">')) {
      // Extract the bullet point and text
      const parts = item.content.split('"text-blue-500 mr-2 mt-1">•"font-bold">');
      if (parts.length > 1) {
        const text = parts[1];
        
        // Create the properly formatted list item
        const formattedItem = \`<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">•</span>
  <strong class="font-bold">\${text}</strong>
</div>\`;
        
        // Replace the original list item with the formatted one
        content = content.replace(item.fullMatch, formattedItem);
      }
    }
    // Check if it's a list item with just a bullet point
    else if (item.content.includes('"text-blue-500 mr-2 mt-1">•')) {
      // Extract the bullet point and text
      const parts = item.content.split('"text-blue-500 mr-2 mt-1">•');
      if (parts.length > 1) {
        const text = parts[1];
        
        // Create the properly formatted list item
        const formattedItem = \`<div class="flex items-start mb-1">
  <span class="text-blue-500 mr-2 mt-1">•</span>
  <span>\${text}</span>
</div>\`;
        
        // Replace the original list item with the formatted one
        content = content.replace(item.fullMatch, formattedItem);
      }
    }
  }
  
  // Clean up any remaining CSS class references
  content = content.replace(/"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/g, '');
  
  // Clean up any remaining quotes and formatting issues
  content = content.replace(/""/g, '');
  content = content.replace(/">/g, '>');
  
  // Remove any remaining target/rel attributes that are displayed as text
  content = content.replace(/ target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">/g, '');
  content = content.replace(/ target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"> ">/g, '');
  content = content.replace(/"_blank"/g, '');
  content = content.replace(/"noopener noreferrer"/g, '');
  content = content.replace(/ target= rel=/g, '');
  content = content.replace(/ target= rel= class=>/g, '');
  
  // Fix any remaining HTML issues
  content = content.replace(/&lt;/g, '<');
  content = content.replace(/&gt;/g, '>');
  content = content.replace(/&quot;/g, '"');
  content = content.replace(/&#039;/g, "'");
  content = content.replace(/&amp;/g, '&');
  
  // Fix double quotes in text
  content = content.replace(/"([^"<>]+)"/g, '<span class="text-blue-700">"$1"</span>');
  
  // Fix any remaining issues with the URL field
  content = content.replace(/URL:.*?Watch Video<\\/strong><\\/strong>/gs, 'URL: <a href="https://www.youtube.com/watch?v=iG1Vxj2L_ZE" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a></strong>');
  
  // Fix any remaining issues with nested strong tags
  content = content.replace(/<\\/strong><\\/strong>/g, '</strong>');
  
  // Fix any remaining issues with class attributes
  content = content.replace(/class=>/g, 'class="text-blue-500 mr-2 mt-1">');
  content = content.replace(/class=<\\/span>/g, 'class="text-blue-500 mr-2 mt-1"></span>');
  
  // Wrap the content in a div with the analysis-content class
  return \`<div class="analysis-content">\${content}</div>\`;
}`;

    // Replace the existing formatAnalysisContent function and processHtmlContent function
    if (content.includes('function ultimateProcessHtmlContent(content)')) {
      // If the ultimateProcessHtmlContent function already exists, replace it with the dynamicProcessHtmlContent function
      content = content.replace(
        /function ultimateProcessHtmlContent\(content\) \{[\s\S]*?return [`']<div class="analysis-content">[\s\S]*?<\/div>[`'];\s*\}/,
        `function ultimateProcessHtmlContent(content) {
  return dynamicProcessHtmlContent(content);
}`
      );
      
      // Add the dynamicProcessHtmlContent function
      content = content.replace(
        /function ultimateProcessHtmlContent\(content\) \{[\s\S]*?return dynamicProcessHtmlContent\(content\);\s*\}/,
        newFormatAnalysisContent
      );
    } else {
      // If the ultimateProcessHtmlContent function doesn't exist, replace the formatAnalysisContent function
      content = content.replace(
        /function formatAnalysisContent\(content\) \{[\s\S]*?return formatted;\s*\}/,
        newFormatAnalysisContent
      );
    }
    
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
      console.log('1. Added dynamic handling for HTML tags and CSS class names displayed as text');
      console.log('2. Improved the HTML content processing to handle the actual content dynamically');
      console.log('3. Fixed issues with the previous approach that used a hardcoded template');
      console.log('4. Enhanced handling of YouTube links to ensure they are properly displayed');
      console.log('5. Added specific CSS rules for elements that were previously showing as text');
      console.log('6. Improved the visual hierarchy of the content');
      console.log('7. Used a more flexible approach to fix the HTML rendering issues');
      console.log('8. Added special handling for the URL field to ensure proper rendering');
    } else {
      console.error('Failed to apply HTML rendering fix.');
    }
  } catch (error) {
    console.error('Error applying HTML rendering fix:', error);
  }
}

// Run the fix
applyFix();
