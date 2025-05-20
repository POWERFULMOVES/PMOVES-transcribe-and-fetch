import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge"; // Using generic Badge for some meta fields
import { 
  MethodBadge, 
  SourceBadge, 
  ScoreBadge, 
  TimestampBadge,
  SegmentBadge,
  WordCountBadge,
  ContentTypeBadge // Added ContentTypeBadge
} from './SearchBadges';
import { getSourceStyle } from '@/lib/search-styles'; // getMethodStyle might not be needed directly if MethodBadge handles it

/**
 * Component for displaying a single search result with rich formatting.
 */
export function SearchResultCard({ result }) { // Removed index prop
  const [expanded, setExpanded] = useState(false);
  const [animateIn, setAnimateIn] = useState(false);
  
  // Animation effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 100); // Simple delay for all cards, can be adjusted or made dynamic if needed
    return () => clearTimeout(timer);
  }, []);

  // Destructure result for easier access, providing defaults
  const {
    id, // Unique result ID from to_dict()
    content_id,
    content = '',
    similarity = 0,
    source = 'unknown',
    title,
    url,
    start_time,
    end_time,
    segment_id,
    summary,
    metadata = {},
    search_method = 'unknown',
    content_type = 'unknown',
    word_count = 0,
    duration, // Formatted string like "start - end"
    has_context, // Boolean
    priority_score // Alias for similarity
  } = result;

  const displayTitle = title || (metadata && metadata.title) || 'Untitled Result';
  
  const displayContent = expanded || content.length <= 200 
    ? content 
    : `${content.substring(0, 200)}...`;
  
  const sourceStyle = getSourceStyle(source);

  // Use duration if available, otherwise format from start/end times
  const timeDisplay = duration || (start_time && end_time ? `${start_time} - ${end_time}` : null);

  return (
    <Card 
      className={`mb-4 overflow-hidden border-l-4 shadow-sm transition-all duration-500 ${sourceStyle.borderColor}`}
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'translateY(0)' : 'translateY(10px)', // Subtle animation
      }}
    >
      <CardHeader className={`pb-2 ${sourceStyle.bgColor ? sourceStyle.bgColor + '/10' : 'bg-gray-50'}`}>
        <div className="flex justify-between items-start">
          <div className="flex-grow">
            <CardTitle className={`text-lg font-semibold ${sourceStyle.textColor}`}>
              {displayTitle}
            </CardTitle>
            <div className="flex flex-wrap gap-2 mt-2 items-center">
              <ScoreBadge score={similarity} />
              <SourceBadge source={source} />
              <ContentTypeBadge contentType={content_type} />
              <MethodBadge method={search_method} />
              {segment_id !== undefined && segment_id !== null && <SegmentBadge segmentId={segment_id} />}
              {timeDisplay && <TimestampBadge startTime={start_time} endTime={end_time} duration={duration} />}
              <WordCountBadge count={word_count} />
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-3 pb-3">
        {/* Main content */}
        {content && (
          <div className="mt-1 text-sm text-gray-700 whitespace-pre-line selection:bg-yellow-200">
            {displayContent}
            {!expanded && content.length > 200 && (
              <Button 
                variant="link" 
                className="p-0 h-auto text-xs ml-1 text-blue-600 hover:text-blue-800" 
                onClick={() => setExpanded(true)}
              >
                Show more
              </Button>
            )}
          </div>
        )}
        
        {/* Summary (if available and expanded) */}
        {expanded && summary && (
          <div className="mt-3 border-t pt-2 animate-fadeIn">
            <h4 className="text-xs font-semibold text-gray-500 mb-1">Summary:</h4>
            <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded-md border border-gray-200 whitespace-pre-line">
              {summary}
            </div>
          </div>
        )}

        {/* Context (if available and expanded) */}
        {expanded && has_context && (metadata.context_before || metadata.context_after) && (
          <div className="mt-3 border-t pt-2 animate-fadeIn">
            <h4 className="text-xs font-semibold text-gray-500 mb-1">Context:</h4>
            {metadata.context_before && (
              <div className="text-xs text-gray-500 mb-1 italic bg-gray-50 p-2 rounded-md border border-gray-200">
                <span className="font-semibold text-gray-600">Before: </span>
                {metadata.context_before}
              </div>
            )}
            {metadata.context_after && (
              <div className="text-xs text-gray-500 italic bg-gray-50 p-2 rounded-md border border-gray-200">
                <span className="font-semibold text-gray-600">After: </span>
                {metadata.context_after}
              </div>
            )}
          </div>
        )}
      </CardContent>
      
      <CardFooter className="pt-2 pb-3 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-gray-50/50 border-t">
        <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-gray-500 mb-2 sm:mb-0">
          {content_id && <span><Badge variant="outline" className="text-xs">Content ID: {content_id}</Badge></span>}
          {id && <span><Badge variant="outline" className="text-xs">Result ID: {id}</Badge></span>}
        </div>
        <div className="flex gap-2 items-center">
          {url && (
            <Button 
              variant="outline" 
              size="sm" 
              asChild 
              className="h-7 text-xs"
            >
              <a href={url} target="_blank" rel="noopener noreferrer" className="clickable-url flex items-center">
                <span className="mr-1">🔗</span> View Source
              </a>
            </Button>
          )}
          {content.length > 200 && ( // Show less button only if content was truncated
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setExpanded(!expanded)}
              className="h-7 text-xs"
            >
              {expanded ? 'Show less' : 'Show more'}
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
