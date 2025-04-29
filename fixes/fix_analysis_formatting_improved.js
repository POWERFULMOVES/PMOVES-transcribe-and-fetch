/**
 * Improved fix for analysis formatting issues in the PMOVES-transcribe-and-fetch project
 * This script addresses the issues with the text formatting in the AI analysis
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
 */
function processHtmlContent(content) {
  // Replace any class attributes that are being displayed as text
  content = content.replace(/"([^"]*?)(text-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(font-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(bg-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(mr-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(mt-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(mb-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(ml-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(p-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(m-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(flex[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(items-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(justify-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(rounded[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(border[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(shadow[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(transition[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(duration[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(ease[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(opacity[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(transform[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(translate[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(scale[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(rotate[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(skew[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(origin[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(overflow[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(z-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(gap-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(space-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(grid[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(col-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(row-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(auto-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(min-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(max-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(w-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(h-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(top-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(right-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(bottom-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(left-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(inset-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(object-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(box-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(cursor-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(pointer-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(select-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(resize-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(sr-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(not-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(first-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(last-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(odd-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(even-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(visited-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(checked-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(focus-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(hover-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(active-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(disabled-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(placeholder-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(ring-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(backdrop-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(filter-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(blur-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(brightness-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(contrast-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(drop-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(grayscale-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(hue-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(invert-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(saturate-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(sepia-[^"]*?)"/g, '"$1"');
  content = content.replace(/"([^"]*?)(backdrop-[^"]*?)"/g, '"$1"');
  
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
      /function formatAnalysisContent\(content\) \{[\s\S]*?return formatted;\s*\}/,
      newFormatAnalysisContent
    );
    
    // Update the FormattedAnalysis component to improve the display
    const updatedFormattedAnalysis = `/**
 * Component for displaying formatted analysis content with animations
 */
function FormattedAnalysis({ content, provider }) {
  const [expanded, setExpanded] = useState(false);
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 150);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Determine if content should be truncated
  const shouldTruncate = content.length > 1200 && !expanded;
  const displayContent = shouldTruncate ? content.substring(0, 1200) + '...' : content;
  
  // Provider-specific styling
  const providerStyles = {
    OpenAI: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      hoverColor: 'hover:bg-blue-100',
      gradientFrom: 'from-blue-50',
      gradientTo: 'to-blue-100'
    },
    Groq: {
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-800',
      hoverColor: 'hover:bg-purple-100',
      gradientFrom: 'from-purple-50',
      gradientTo: 'to-purple-100'
    }
  };
  
  const style = providerStyles[provider];
  
  return (
    <div className={\`transition-all duration-500 \${animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}\`}>
      <div className={\`prose prose-sm max-w-none \${provider === 'OpenAI' ? 'prose-blue' : 'prose-purple'}\`}>
        <div 
          className={\`p-4 rounded-md border \${style.borderColor} \${style.bgColor} 
            \${shouldTruncate ? 'max-h-[500px] overflow-y-auto' : ''} 
            analysis-content shadow-sm\`}
        >
          <div 
            className="analysis-formatted-content"
            dangerouslySetInnerHTML={{ __html: formatAnalysisContent(displayContent) }}
          />
        </div>
      </div>
      
      {content.length > 1200 && (
        <div className="mt-2 text-right">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setExpanded(!expanded)}
            className={\`h-7 text-xs transition-all duration-300 \${style.textColor} \${style.hoverColor}\`}
          >
            {expanded ? '↑ Show less' : '↓ Show more'}
          </Button>
        </div>
      )}
    </div>
  );
}`;

    // Replace the existing FormattedAnalysis component
    content = content.replace(
      /function FormattedAnalysis\(\{ content, provider \}\) \{[\s\S]*?<\/div>\s*\);[\s\S]*?\}/,
      updatedFormattedAnalysis
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
    console.log('Successfully updated AnalysisDisplay.jsx with improved formatting');
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
      console.log('Improved analysis formatting fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Added special handling for content that already contains HTML tags');
      console.log('2. Removed HTML escaping for trusted content from AI models');
      console.log('3. Added a processHtmlContent function to fix HTML tags displayed as text');
      console.log('4. Enhanced handling of YouTube links to ensure they are clickable');
      console.log('5. Improved CSS styling for better readability and visual hierarchy');
      console.log('6. Increased the truncation threshold for better readability');
      console.log('7. Added specific CSS classes to ensure proper rendering of HTML elements');
    } else {
      console.error('Failed to apply improved analysis formatting fix.');
    }
  } catch (error) {
    console.error('Error applying improved analysis formatting fix:', error);
  }
}

// Run the fix
applyFix();
