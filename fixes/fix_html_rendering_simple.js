/**
 * Simple and targeted fix for HTML rendering issues in the PMOVES-transcribe-and-fetch project
 * This script directly edits the AnalysisDisplay.jsx file to add the necessary function
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisDisplay.jsx file
const analysisDisplayPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisDisplay.jsx');

// Function to update the AnalysisDisplay.jsx file
function updateAnalysisDisplay() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisDisplayPath, 'utf8');
    
    // Check if the file already has the ultimateProcessHtmlContent function
    if (content.includes('function ultimateProcessHtmlContent')) {
      console.log('The ultimateProcessHtmlContent function already exists in the file.');
      return true;
    }
    
    // Find the formatAnalysisContent function
    const formatAnalysisContentRegex = /function formatAnalysisContent\(content\) \{[\s\S]*?return formatted;\s*\}/;
    const match = content.match(formatAnalysisContentRegex);
    
    if (!match) {
      console.error('Could not find the formatAnalysisContent function in the file.');
      return false;
    }
    
    // Create the new formatAnalysisContent function with the check for CSS class names
    const newFormatAnalysisContent = `function formatAnalysisContent(content) {
  if (!content) return '';
  
  // Check if the content contains CSS class names displayed as text
  const containsCssClassNames = /"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/i.test(content);
  
  if (containsCssClassNames) {
    // The content contains CSS class names displayed as text, so we need to fix it
    return ultimateProcessHtmlContent(content);
  }
  
  // For plain text content, apply Markdown-like formatting
  let formatted = content;
  
  // Replace newlines with <br> tags
  formatted = formatted.replace(/\\n/g, '<br>');
  
  // Format headings (# Heading)
  formatted = formatted.replace(/(?:<br>|^)\\s*#\\s+(.*?)(?=<br>|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
  formatted = formatted.replace(/(?:<br>|^)\\s*##\\s+(.*?)(?=<br>|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
  formatted = formatted.replace(/(?:<br>|^)\\s*###\\s+(.*?)(?=<br>|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  
  // Format bold (**text**)
  formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-bold">$1</strong>');
  
  // Format italic (*text*)
  formatted = formatted.replace(/(?<!\\*)\\*((?!\\*).+?)\\*(?!\\*)/g, '<em class="italic">$1</em>');
  
  // Format lists
  formatted = formatted.replace(/(?:<br>|^)\\s*-\\s+(.*?)(?=<br>|$)/g, 
    '<div class="flex items-start mb-1"><span class="text-blue-500 mr-2 mt-1">•</span><span>$1</span></div>');
  
  // Format links
  formatted = formatted.replace(/\\[(.*?)\\]\\((.*?)\\)/g, 
    '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline">$1</a>');
  
  // Handle raw URLs
  formatted = formatted.replace(/(https?:\\/\\/[^\\s<]+[^<.,:;"'\\)\\]\\s])/g, 
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline">$1</a>');
  
  return formatted;
}

/**
 * Ultimate approach to process HTML content
 * This function uses a direct replacement approach to fix the HTML rendering issues
 */
function ultimateProcessHtmlContent(content) {
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
  
  // Fix any remaining issues with nested strong tags
  content = content.replace(/<\\/strong><\\/strong>/g, '</strong>');
  
  // Fix any remaining issues with class attributes
  content = content.replace(/class=>/g, 'class="text-blue-500 mr-2 mt-1">');
  content = content.replace(/class=<\\/span>/g, 'class="text-blue-500 mr-2 mt-1"></span>');
  
  // Wrap the content in a div with the analysis-content class
  return \`<div class="analysis-content">\${content}</div>\`;
}`;
    
    // Replace the formatAnalysisContent function with the new one
    content = content.replace(formatAnalysisContentRegex, newFormatAnalysisContent);
    
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
      console.log('1. Added check for CSS class names displayed as text');
      console.log('2. Added ultimateProcessHtmlContent function to handle HTML content with CSS class names');
      console.log('3. Enhanced handling of YouTube links to ensure they are properly displayed');
      console.log('4. Improved handling of list items with bullet points');
      console.log('5. Added cleanup for remaining CSS class references and formatting issues');
    } else {
      console.error('Failed to apply HTML rendering fix.');
    }
  } catch (error) {
    console.error('Error applying HTML rendering fix:', error);
  }
}

// Run the fix
applyFix();
