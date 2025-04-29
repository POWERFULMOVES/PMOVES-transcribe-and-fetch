/**
 * Script to fix the CSS class formatter in AnalysisFormatter.jsx
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisFormatter.jsx file
const analysisFormatterPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisFormatter.jsx');

// Function to fix the CSS class formatter
function fixCssClassFormatter() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisFormatterPath, 'utf8');
    
    // Replace the CssClassFormatter function with a more robust implementation
    const oldCssClassFormatter = /function CssClassFormatter\(\{ content \}\) \{[\s\S]*?return \(\s*<div[\s\S]*?<\/div>\s*\);\s*\}/;
    
    const newCssClassFormatter = `function CssClassFormatter({ content }) {
  // Process the content to properly format CSS class names
  const processedContent = React.useMemo(() => {
    // First, let's handle specific patterns we know about
    let processedHtml = content;
    
    // Handle section headers with specific CSS classes
    processedHtml = processedHtml.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">([^<]+)/g, 
      '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
    
    // Handle "font-bold" sections
    processedHtml = processedHtml.replace(/"font-bold">([^<]+)/g, 
      '<strong class="font-bold">$1</strong>');
    
    // Handle numbered sections (e.g., "1." in "font-bold">Shockwave's Characterization:)
    processedHtml = processedHtml.replace(/"flex items-start mb-1">([^<]+)"text-blue-500 mr-2 mt-1">([^<]+)"font-bold">([^<]+)/g,
      '<div class="flex items-start mb-1"><span class="text-blue-500 mr-2 mt-1">$2</span><strong class="font-bold">$3</strong></div>');
    
    // Handle specific patterns from the screenshot
    processedHtml = processedHtml.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">Search Results Summary/g,
      '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">Search Results Summary</h3>');
    
    processedHtml = processedHtml.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">Key Findings:/g,
      '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">Key Findings:</h3>');
    
    // Handle "font-bold">Specific Moments:
    processedHtml = processedHtml.replace(/"font-bold">([^:]+):/g,
      '<strong class="font-bold">$1:</strong>');
    
    // Handle "flex items-start mb-1" patterns
    processedHtml = processedHtml.replace(/"flex items-start mb-1">/g,
      '<div class="flex items-start mb-1">');
    
    // Handle "text-blue-500 font-medium mr-2 mt-1" patterns
    processedHtml = processedHtml.replace(/"text-blue-500 font-medium mr-2 mt-1">([^<]+)/g,
      '<span class="text-blue-500 font-medium mr-2 mt-1">$1</span>');
    
    // Handle "text-blue-500 mr-2 mt-1" patterns
    processedHtml = processedHtml.replace(/"text-blue-500 mr-2 mt-1">([^<]+)/g,
      '<span class="text-blue-500 mr-2 mt-1">$1</span>');
    
    // Handle specific patterns for list items
    processedHtml = processedHtml.replace(/"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•([^<]+)/g,
      '<div class="flex items-start mb-1"><span class="text-blue-500 mr-2 mt-1">•</span><span>$1</span>');
    
    // Handle specific patterns for list items with bold text
    processedHtml = processedHtml.replace(/"flex items-start mb-1">"text-blue-500 mr-2 mt-1">•"font-bold">([^<]+)/g,
      '<div class="flex items-start mb-1"><span class="text-blue-500 mr-2 mt-1">•</span><strong class="font-bold">$1</strong>');
    
    // Handle "text-blue-500" patterns
    processedHtml = processedHtml.replace(/"text-blue-500">([^<]+)/g,
      '<span class="text-blue-500">$1</span>');
    
    // Handle "text-blue-700" patterns
    processedHtml = processedHtml.replace(/"text-blue-700">([^<]+)/g,
      '<span class="text-blue-700">$1</span>');
    
    // Handle "font-medium" patterns
    processedHtml = processedHtml.replace(/"font-medium">([^<]+)/g,
      '<span class="font-medium">$1</span>');
    
    // Handle "my-4 border-t border-gray-200" patterns
    processedHtml = processedHtml.replace(/"my-4 border-t border-gray-200">/g,
      '<hr class="my-4 border-t border-gray-200">');
    
    // Handle YouTube links
    processedHtml = processedHtml.replace(/🎬https:\/\/www\.youtube\.com\/watch\\?v=([^&\\s]+)/g, 
      '<a href="https://www.youtube.com/watch?v=$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>');
    
    // Clean up any remaining CSS class references
    processedHtml = processedHtml.replace(/"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/g, '');
    
    // Clean up any remaining quotes and formatting issues
    processedHtml = processedHtml.replace(/""/g, '');
    processedHtml = processedHtml.replace(/">/g, '>');
    
    // Remove any remaining target/rel attributes that are displayed as text
    processedHtml = processedHtml.replace(/ target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center">/g, '');
    processedHtml = processedHtml.replace(/ target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"> ">/g, '');
    processedHtml = processedHtml.replace(/"_blank"/g, '');
    processedHtml = processedHtml.replace(/"noopener noreferrer"/g, '');
    processedHtml = processedHtml.replace(/ target= rel=/g, '');
    processedHtml = processedHtml.replace(/ target= rel= class=>/g, '');
    
    // Fix any remaining HTML issues
    processedHtml = processedHtml.replace(/&lt;/g, '<');
    processedHtml = processedHtml.replace(/&gt;/g, '>');
    processedHtml = processedHtml.replace(/&quot;/g, '"');
    processedHtml = processedHtml.replace(/&#039;/g, "'");
    processedHtml = processedHtml.replace(/&amp;/g, '&');
    
    // Fix double quotes in text
    processedHtml = processedHtml.replace(/"([^"<>]+)"/g, '<span class="text-blue-700">"$1"</span>');
    
    // Fix any remaining issues with nested strong tags
    processedHtml = processedHtml.replace(/<\\/strong><\\/strong>/g, '</strong>');
    
    // Fix any remaining issues with class attributes
    processedHtml = processedHtml.replace(/class=>/g, 'class="text-blue-500 mr-2 mt-1">');
    processedHtml = processedHtml.replace(/class=<\\/span>/g, 'class="text-blue-500 mr-2 mt-1"></span>');
    
    // Add closing tags for any unclosed divs
    const openDivs = (processedHtml.match(/<div/g) || []).length;
    const closeDivs = (processedHtml.match(/<\\/div>/g) || []).length;
    const missingCloseDivs = openDivs - closeDivs;
    
    if (missingCloseDivs > 0) {
      for (let i = 0; i < missingCloseDivs; i++) {
        processedHtml += '</div>';
      }
    }
    
    return processedHtml;
  }, [content]);

  return (
    <div className="analysis-content analysis-formatted-content">
      <div dangerouslySetInnerHTML={{ __html: processedContent }} />
    </div>
  );
}`;
    
    // Replace the CssClassFormatter function
    content = content.replace(oldCssClassFormatter, newCssClassFormatter);
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisFormatterPath, content, 'utf8');
    console.log('Successfully fixed CSS class formatter in AnalysisFormatter.jsx');
    return true;
  } catch (error) {
    console.error('Error fixing CSS class formatter in AnalysisFormatter.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Fix CSS class formatter
    const formatterFixed = fixCssClassFormatter();
    
    if (formatterFixed) {
      console.log('CSS class formatter fixed successfully!');
      console.log('Changes:');
      console.log('1. Improved the CssClassFormatter function to better handle CSS class names');
      console.log('2. Added specific patterns to handle the formatting seen in the screenshot');
      console.log('3. Added the analysis-formatted-content class to apply the custom CSS styles');
    } else {
      console.error('Failed to fix CSS class formatter.');
    }
  } catch (error) {
    console.error('Error applying fix:', error);
  }
}

// Run the fix
applyFix();
