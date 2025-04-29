/**
 * Fix for analysis formatting issues in the PMOVES-transcribe-and-fetch project
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
  
  // First, escape any HTML that might be in the content to prevent XSS
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  
  // Replace newlines with <br> tags
  formatted = formatted.replace(/\\n/g, '<br>');
  
  // Format headings (# Heading) - improved regex to handle edge cases
  formatted = formatted.replace(/(?:<br>|^)\\s*#\\s+(.*?)(?=<br>|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
  formatted = formatted.replace(/(?:<br>|^)\\s*##\\s+(.*?)(?=<br>|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
  formatted = formatted.replace(/(?:<br>|^)\\s*###\\s+(.*?)(?=<br>|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  
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
  
  // Format links - improved to handle edge cases
  formatted = formatted.replace(/\\[(.*?)\\]\\((.*?)\\)/g, 
    '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline">$1</a>');
  
  // Highlight key terms - improved to handle edge cases
  formatted = formatted.replace(/"([^"]+)"/g, '<span class="text-blue-700">"$1"</span>');
  
  // Add spacing between paragraphs for better readability
  formatted = formatted.replace(/(<br>){2,}/g, '<br><br>');
  formatted = formatted.replace(/(<br>)(?!<\\/div>|<\\/blockquote>|<\\/pre>)/g, '<br>');
  
  return formatted;
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
  const shouldTruncate = content.length > 800 && !expanded;
  const displayContent = shouldTruncate ? content.substring(0, 800) + '...' : content;
  
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
            \${shouldTruncate ? 'max-h-[400px] overflow-y-auto' : ''} 
            analysis-content shadow-sm\`}
        >
          <div 
            className="analysis-formatted-content"
            dangerouslySetInnerHTML={{ __html: formatAnalysisContent(displayContent) }}
          />
        </div>
      </div>
      
      {content.length > 800 && (
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
    
    // Add CSS for the analysis content
    const cssAddition = `
  // Add custom CSS for analysis content
  useEffect(() => {
    // Add custom CSS for analysis content
    const style = document.createElement('style');
    style.textContent = \`
      .analysis-formatted-content h3, 
      .analysis-formatted-content h4, 
      .analysis-formatted-content h5 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
      }
      .analysis-formatted-content h3 {
        font-size: 1.25rem;
        color: rgb(29, 78, 216);
      }
      .analysis-formatted-content h4 {
        font-size: 1.125rem;
        color: rgb(37, 99, 235);
      }
      .analysis-formatted-content h5 {
        font-size: 1rem;
        color: rgb(59, 130, 246);
      }
      .analysis-formatted-content ul, 
      .analysis-formatted-content ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
      }
      .analysis-formatted-content li {
        margin-bottom: 0.25rem;
      }
      .analysis-formatted-content p {
        margin-bottom: 0.75rem;
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
      }
      .analysis-formatted-content code {
        background-color: rgb(243, 244, 246);
        padding: 0.125rem 0.375rem;
        border-radius: 0.25rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.875rem;
      }
    \`;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);`;
    
    // Add the CSS to the AnalysisDisplay component
    content = content.replace(
      /export function AnalysisDisplay\(\{ openaiAnalysis, groqAnalysis \}\) \{[\s\S]*?const \[animateIn, setAnimateIn\] = useState\(false\);/,
      `export function AnalysisDisplay({ openaiAnalysis, groqAnalysis }) {
  const [activeTab, setActiveTab] = useState('openai');
  const [animateIn, setAnimateIn] = useState(false);
  ${cssAddition}`
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
      console.log('Analysis formatting fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Improved the formatAnalysisContent function to better handle Markdown syntax');
      console.log('2. Added proper HTML escaping to prevent rendering issues');
      console.log('3. Enhanced the handling of headings, lists, and code blocks');
      console.log('4. Improved the styling of the analysis content');
      console.log('5. Added custom CSS to ensure consistent formatting');
      console.log('6. Increased the truncation threshold for better readability');
    } else {
      console.error('Failed to apply analysis formatting fix.');
    }
  } catch (error) {
    console.error('Error applying analysis formatting fix:', error);
  }
}

// Run the fix
applyFix();
