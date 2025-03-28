import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  MethodBadge, 
  SourceBadge, 
  ScoreBadge, 
  TimestampBadge,
  SegmentBadge,
  WordCountBadge
} from './SearchBadges';
import { getSourceStyle, getMethodStyle } from '@/lib/search-styles';

/**
 * Component for displaying a single search result with rich formatting and animations
 */
export function SearchResultCard({ result, index = 0 }) {
  const [expanded, setExpanded] = useState(false);
  const [animateIn, setAnimateIn] = useState(false);
  
  // Calculate word count if not provided
  const wordCount = result.word_count || (result.content ? result.content.split(/\s+/).length : 0);
  
  // Format content for display
  const displayContent = expanded || result.content?.length <= 200 
    ? result.content 
    : `${result.content?.substring(0, 200)}...`;
  
  // Check if result has context
  const hasContext = result.has_context || 
    (result.metadata && (result.metadata.context_before || result.metadata.context_after));
  
  // Get source style
  const sourceStyle = result.source ? getSourceStyle(result.source) : { bgColor: 'bg-gray-100', textColor: 'text-gray-700' };
  
  // Get method style
  const methodStyle = result.search_method ? getMethodStyle(result.search_method) : { bgColor: 'bg-gray-100', textColor: 'text-gray-700' };
  
  // Animation delay based on index
  const animationDelay = 0.1 + (index * 0.05);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <Card 
      className={`mb-4 overflow-hidden border-l-4 search-result-card shadow-sm transition-all duration-500 ${result.source ? getSourceStyle(result.source).borderColor : ''}`}
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'translateY(0)' : 'translateY(20px)',
        transitionDelay: `${animationDelay}s`
      }}
    >
      <CardHeader className={`pb-2 ${sourceStyle.bgColor ? sourceStyle.bgColor + '/10' : 'bg-gray-50'}`}>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className={`text-base font-medium ${sourceStyle.textColor}`}>
              {result.title || `Result from ${result.content_id || 'unknown source'}`}
            </CardTitle>
            <div className="flex flex-wrap gap-2 mt-1">
              <ScoreBadge score={result.similarity} />
              <MethodBadge method={result.search_method} />
              <SourceBadge source={result.source} />
              {result.segment_id !== undefined && <SegmentBadge segmentId={result.segment_id} />}
              {(result.start_time || result.end_time) && 
                <TimestampBadge startTime={result.start_time} endTime={result.end_time} />
              }
              <WordCountBadge count={wordCount} />
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-3">
        {/* Main content */}
        <div className="mt-2 text-sm whitespace-pre-line">
          {displayContent}
          {!expanded && result.content?.length > 200 && (
            <Button 
              variant="link" 
              className="p-0 h-auto text-xs ml-1" 
              onClick={() => setExpanded(true)}
            >
              <span className="flex items-center">
                <span className="mr-1">↓</span> Show more
              </span>
            </Button>
          )}
        </div>
        
        {/* Context (if available) */}
        {expanded && hasContext && (
          <div className="mt-4 border-t pt-2 animate-fadeIn">
            <h4 className="text-xs font-semibold text-gray-500 mb-1 flex items-center">
              <span className="mr-1">📌</span> Context
            </h4>
            {result.metadata?.context_before && (
              <div className="text-xs text-gray-600 mb-2 italic bg-gray-50 p-2 rounded-md border border-gray-100">
                <span className="font-semibold">Before: </span>
                {result.metadata.context_before}
              </div>
            )}
            {result.metadata?.context_after && (
              <div className="text-xs text-gray-600 italic bg-gray-50 p-2 rounded-md border border-gray-100">
                <span className="font-semibold">After: </span>
                {result.metadata.context_after}
              </div>
            )}
          </div>
        )}
        
        {/* Summary (if available) */}
        {expanded && result.summary && (
          <div className="mt-4 border-t pt-2 animate-fadeIn">
            <h4 className="text-xs font-semibold text-gray-500 mb-1 flex items-center">
              <span className="mr-1">📝</span> Summary
            </h4>
            <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded-md border border-gray-100">
              {result.summary}
            </div>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="pt-0 flex justify-between bg-gray-50/50">
        <div className="text-xs text-gray-500 flex items-center">
          <span className="mr-1">🆔</span>
          {result.content_id || 'N/A'}
        </div>
        <div className="flex gap-2">
          {result.url && (
            <Button 
              variant="outline" 
              size="sm" 
              asChild 
              className={`h-7 text-xs transition-colors ${methodStyle.textColor} hover:${methodStyle.bgColor}`}
            >
              <a href={result.url} target="_blank" rel="noopener noreferrer" className="clickable-url flex items-center">
                <span className="mr-1">🔗</span> View Source
              </a>
            </Button>
          )}
          {expanded && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setExpanded(false)}
              className="h-7 text-xs"
            >
              <span className="flex items-center">
                <span className="mr-1">↑</span> Show less
              </span>
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
