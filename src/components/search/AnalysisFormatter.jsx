import React from 'react';
import ReactMarkdown from 'react-markdown';

/**
 * AnalysisFormatter component for properly rendering analysis content
 * This component handles both plain text and content with CSS class names
 */
export function AnalysisFormatter({ content }) {
  // If no content, return empty div
  if (!content || content.trim() === '') {
    return <div className="analysis-empty">No analysis content available</div>;
  }

  // Check if the content contains CSS class names displayed as text
  const containsCssClassNames = /"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/i.test(content);

  // If content contains CSS class names, use the CSS class formatter
  if (containsCssClassNames) {
    return <CssClassFormatter content={content} />;
  }

  // Otherwise, use the markdown formatter
  return <MarkdownFormatter content={content} />;
}

/**
 * Component for formatting content with CSS class names
 */
function CssClassFormatter({ content }) {
  // Process the content to properly format CSS class names
  const processedContent = React.useMemo(() => {
    // First, let's handle specific patterns we know about
    let processedHtml = content;
    
    // Fix "Untitled" titles in the analysis based on backend data structure
    processedHtml = processedHtml.replace(/Title:\s*Untitled/g, (match) => {
      // Look for content ID nearby to create a better title
      const contentIdMatch = processedHtml.match(/Content ID:\s*([a-zA-Z0-9_-]+)/i);
      const sourceMatch = processedHtml.match(/Source:\s*([a-zA-Z_]+)/i);
      
      if (contentIdMatch && contentIdMatch[1]) {
        const contentId = contentIdMatch[1];
        const source = sourceMatch && sourceMatch[1] ? sourceMatch[1].toLowerCase() : '';
        
        // Create title based on source and content ID
        if (source.includes('video') || contentId.includes('v2L_ZE') || contentId.match(/^[a-zA-Z0-9_-]{11}$/)) {
          return `Title: Video Transcript: ${contentId}`;
        } else if (source.includes('document')) {
          return `Title: Document: ${contentId}`;
        } else {
          return `Title: Content from ${contentId}`;
        }
      }
      
      // If no content ID, try to use other information
      const timestampMatch = processedHtml.match(/Timestamp:\s*([0-9:.]+\s*(?:to|-)?\s*[0-9:.]+)/i);
      if (timestampMatch && timestampMatch[1]) {
        return `Title: Content at ${timestampMatch[1]}`;
      }
      
      return match; // Keep original if no better title can be determined
    });
    
    // Clean up CSS class references and convert to proper HTML
    processedHtml = processedHtml.replace(/"text-sm font-semibold mt-2 mb-1 text-blue-500">([^<]+)/g, 
      '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
    
    processedHtml = processedHtml.replace(/"font-bold">([^<]+)/g, 
      '<strong class="font-bold">$1</strong>');
    
    // Handle YouTube links - simplified approach without regex issues
    const youtubePattern = /🎬?https:\/\/www\.youtube\.com\/watch\?v=([^&\s"']+)/g;
    let match;
    while ((match = youtubePattern.exec(processedHtml)) !== null) {
      const fullMatch = match[0];
      const videoId = match[1];
      const replacement = `<a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline flex items-center"><span class="mr-1">🎬</span>Watch Video</a>`;
      processedHtml = processedHtml.replace(fullMatch, replacement);
    }
    
    // Clean up any remaining CSS class references
    processedHtml = processedHtml.replace(/"([^"]*?)(text-|font-|bg-|mr-|mt-|mb-|ml-|p-|m-|flex|items-|justify-|rounded|border|shadow|transition|duration|ease|opacity|transform|translate|scale|rotate|skew|origin|overflow|z-|gap-|space-|grid|col-|row-|auto-|min-|max-|w-|h-|top-|right-|bottom-|left-|inset-|object-|box-|cursor-|pointer-|select-|resize-|sr-|not-|first-|last-|odd-|even-|visited-|checked-|focus-|hover-|active-|disabled-|placeholder-|ring-|backdrop-|filter-|blur-|brightness-|contrast-|drop-|grayscale-|hue-|invert-|saturate-|sepia-|backdrop-)([^"]*?)"/g, '');
    
    // Fix any remaining HTML issues
    processedHtml = processedHtml.replace(/&lt;/g, '<');
    processedHtml = processedHtml.replace(/&gt;/g, '>');
    processedHtml = processedHtml.replace(/&quot;/g, '"');
    processedHtml = processedHtml.replace(/&#039;/g, "'");
    processedHtml = processedHtml.replace(/&amp;/g, '&');
    
    return processedHtml;
  }, [content]);

  return (
    <div className="analysis-content analysis-formatted-content">
      <div dangerouslySetInnerHTML={{ __html: processedContent }} />
    </div>
  );
}

/**
 * Component for formatting markdown-like content using react-markdown
 */
function MarkdownFormatter({ content }) {
  // Custom components for react-markdown
  const components = {
    // Customize headings
    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4 text-blue-800" {...props} />,
    h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3 text-blue-700" {...props} />,
    h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-4 mb-2 text-blue-700" {...props} />,
    h4: ({ node, ...props }) => <h4 className="text-md font-semibold mt-3 mb-1 text-blue-600" {...props} />,
    h5: ({ node, ...props }) => <h5 className="text-sm font-semibold mt-2 mb-1 text-blue-500" {...props} />,
    h6: ({ node, ...props }) => <h6 className="text-sm font-semibold mt-2 mb-1 text-blue-500" {...props} />,
    
    // Customize paragraphs
    p: ({ node, ...props }) => <p className="mb-4" {...props} />,
    
    // Customize lists
    ul: ({ node, ...props }) => <ul className="mb-4 ml-6 list-disc" {...props} />,
    ol: ({ node, ...props }) => <ol className="mb-4 ml-6 list-decimal" {...props} />,
    li: ({ node, ...props }) => <li className="mb-1" {...props} />,
    
    // Customize links
    a: ({ node, href, ...props }) => {
      const isYouTubeLink = href && (href.includes('youtube.com') || href.includes('youtu.be'));
      return (
        <a 
          href={href} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={`text-blue-600 underline hover:no-underline ${isYouTubeLink ? 'flex items-center' : ''}`}
          {...props}
        >
          {isYouTubeLink && <span className="mr-1">🎬</span>}
          {props.children}
        </a>
      );
    },
    
    // Customize code blocks
    code: ({ node, inline, className, children, ...props }) => {
      return inline ? (
        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600" {...props}>
          {children}
        </code>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    
    // Add a custom pre component to avoid nesting issues
    pre: ({ node, ...props }) => (
      <pre className="bg-gray-100 p-3 rounded-md text-sm font-mono text-blue-600 overflow-x-auto my-2" {...props} />
    ),
    
    // Customize blockquotes
    blockquote: ({ node, ...props }) => (
      <blockquote className="pl-3 border-l-2 border-blue-300 text-gray-600 italic my-2" {...props} />
    ),
    
    // Customize horizontal rules
    hr: ({ node, ...props }) => <hr className="my-4 border-t border-gray-200" {...props} />,
    
    // Customize strong and emphasis
    strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
    em: ({ node, ...props }) => <em className="italic" {...props} />,
  };

    // Process the content to handle special cases before passing to react-markdown
    const processedContent = React.useMemo(() => {
        let processed = content;
        
        // Fix "Untitled" titles in the analysis - more comprehensive approach
        // First, look for any "Untitled" text in the content
        const untitledMatches = processed.match(/(?:Title:|title:)?\s*(?:"|')?Untitled(?:"|')?/gi);
        if (untitledMatches) {
          // Look for content ID or other identifiers
          const contentIdMatch = processed.match(/(?:Content ID|ID|content id|id):\s*([a-zA-Z0-9_-]+)/i);
          const timestampMatch = processed.match(/(?:Timestamp|timestamp|time):\s*([0-9:.]+\s*(?:to|-)?\s*[0-9:.]+)/i);
          
          let replacement = '';
          
          if (contentIdMatch && contentIdMatch[1]) {
            const contentId = contentIdMatch[1];
            // Check if it's a video transcription based on common video IDs
            if (contentId.includes('v2L_ZE') || contentId.includes('iG1Vvj2L') || contentId.match(/^[a-zA-Z0-9_-]{11}$/)) {
              replacement = `Video Transcript: ${contentId}`;
            } else {
              replacement = `Content from ${contentId}`;
            }
            
            // Add timestamp if available
            if (timestampMatch && timestampMatch[1]) {
              replacement += ` (${timestampMatch[1]})`;
            }
            
            // Replace all instances of "Untitled" with the new title
            for (const match of untitledMatches) {
              if (match.toLowerCase().includes('title:')) {
                processed = processed.replace(match, `Title: ${replacement}`);
              } else {
                processed = processed.replace(match, replacement);
              }
            }
          }
        }
        
        // Handle YouTube links that aren't in markdown format
        const youtubePattern = /https:\/\/www\.youtube\.com\/watch\?v=([^&\s"']+)/g;
        processed = processed.replace(youtubePattern, (match, videoId) => {
          return `[🎬 Watch Video](${match})`;
        });
        
        // Handle quoted text that isn't in markdown format
        processed = processed.replace(/"([^"]+)"/g, (match, text) => {
          return `**"${text}"**`;
        });
        
        return processed;
    }, [content]);

  return (
    <div className="analysis-content">
      <ReactMarkdown components={components}>
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}
