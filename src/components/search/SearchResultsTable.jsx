import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { 
  MethodBadge, 
  SourceBadge, 
  ScoreBadge 
} from './SearchBadges';
import { TABLE_STYLES, getSourceStyle, getMethodStyle } from '@/lib/search-styles';

/**
 * Component for displaying search results in a table format with enhanced styling
 */
export function SearchResultsTable({ results, onViewDetails }) {
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Early return if no results
  if (!results || results.length === 0) {
    return (
      <div className="text-center p-8 border rounded-md bg-gray-50 shadow-sm">
        <p className="text-gray-500">No search results to display.</p>
        <p className="text-xs text-gray-400 mt-2">Try adjusting your search query or parameters.</p>
      </div>
    );
  }
  
  return (
    <div 
      className="border rounded-md overflow-hidden shadow-sm transition-all duration-500"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'translateY(0)' : 'translateY(20px)'
      }}
    >
      <div className={`p-3 ${TABLE_STYLES.title.textColor} ${TABLE_STYLES.title.fontWeight} bg-gradient-to-r from-blue-50 to-cyan-50 border-b flex items-center justify-between`}>
        <div className="flex items-center">
          <span className="mr-2">{TABLE_STYLES.title.icon}</span>
          Search Results Table
        </div>
        <div className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full shadow-sm">
          {results.length} results found
        </div>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className={`${TABLE_STYLES.header.bgColor} border-b-2 ${TABLE_STYLES.border.style}`}>
              <TableHead className={`${TABLE_STYLES.header.textColor} ${TABLE_STYLES.header.fontWeight} ${TABLE_STYLES.columns.score.width} ${TABLE_STYLES.columns.score.textAlign}`}>
                <span className="flex items-center justify-end">
                  <span className="mr-1">📊</span> Score
                </span>
              </TableHead>
              <TableHead className={`${TABLE_STYLES.header.textColor} ${TABLE_STYLES.header.fontWeight} ${TABLE_STYLES.columns.method.width}`}>
                <span className="flex items-center">
                  <span className="mr-1">🔍</span> Method
                </span>
              </TableHead>
              <TableHead className={`${TABLE_STYLES.header.textColor} ${TABLE_STYLES.header.fontWeight} ${TABLE_STYLES.columns.source.width}`}>
                <span className="flex items-center">
                  <span className="mr-1">📂</span> Source
                </span>
              </TableHead>
              <TableHead className={`${TABLE_STYLES.header.textColor} ${TABLE_STYLES.header.fontWeight} ${TABLE_STYLES.columns.content.width}`}>
                <span className="flex items-center">
                  <span className="mr-1">📝</span> Content
                </span>
              </TableHead>
              <TableHead className={`${TABLE_STYLES.header.textColor} ${TABLE_STYLES.header.fontWeight} w-24 text-center`}>
                <span className="flex items-center justify-center">
                  <span className="mr-1">⚙️</span> Actions
                </span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result, index) => {
              // Get source and method styles
              const sourceStyle = result.source ? getSourceStyle(result.source) : null;
              const methodStyle = result.search_method ? getMethodStyle(result.search_method) : null;
              
              // Calculate animation delay based on index
              const animationDelay = 0.1 + (index * 0.03);
              
              return (
                <TableRow 
                  key={`table-row-${result.content_id}-${result.segment_id || index}-${Math.random().toString(36).substr(2, 5)}`}
                  className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} transition-all duration-300 hover:bg-blue-50/30`}
                  style={{ 
                    opacity: animateIn ? 1 : 0,
                    transform: animateIn ? 'translateY(0)' : 'translateY(10px)',
                    transitionDelay: `${animationDelay}s`
                  }}
                >
                  <TableCell className={`${TABLE_STYLES.columns.score.textAlign} ${TABLE_STYLES.columns.score.width}`}>
                    <ScoreBadge score={result.similarity} />
                  </TableCell>
                  <TableCell className={TABLE_STYLES.columns.method.width}>
                    <MethodBadge method={result.search_method} />
                  </TableCell>
                  <TableCell className={TABLE_STYLES.columns.source.width}>
                    <SourceBadge source={result.source} />
                  </TableCell>
                  <TableCell className={`${TABLE_STYLES.columns.content.width} ${TABLE_STYLES.columns.content.overflow}`}>
                    <div className="max-h-20 overflow-y-auto p-1 rounded-md hover:bg-gray-50">
                      {result.content?.substring(0, 150)}
                      {result.content?.length > 150 && '...'}
                    </div>
                    {result.start_time && result.end_time && (
                      <div className="text-xs text-gray-500 mt-1 flex items-center">
                        <span className="mr-1">⏱️</span>
                        {result.start_time} - {result.end_time}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2 justify-center">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className={`h-7 text-xs transition-colors ${methodStyle?.textColor || ''} hover:${methodStyle?.bgColor || 'bg-blue-50'}`}
                        onClick={() => onViewDetails && onViewDetails(result)}
                      >
                        <span className="flex items-center">
                          <span className="mr-1">🔍</span> Details
                        </span>
                      </Button>
                      {result.url && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className={`h-7 text-xs transition-colors ${sourceStyle?.textColor || ''} hover:${sourceStyle?.bgColor || 'bg-blue-50'}`}
                          asChild
                        >
                          <a 
                            href={result.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            <span className="flex items-center">
                              <span className="mr-1">🔗</span> Source
                            </span>
                          </a>
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <div className="p-2 text-xs text-gray-500 border-t bg-gray-50 flex justify-between items-center">
        <div>
          Showing {results.length} results
        </div>
        <div className="flex items-center">
          <span className="mr-1">💡</span>
          <span>Click on Details to view full content</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Component for displaying a detailed view of a single search result with enhanced styling
 */
export function SearchResultDetail({ result, onClose }) {
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);
  
  if (!result) return null;
  
  // Get source style
  const sourceStyle = result.source ? getSourceStyle(result.source) : { bgColor: 'bg-gray-100', textColor: 'text-gray-700' };
  
  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 transition-opacity duration-300"
      style={{ opacity: animateIn ? 1 : 0 }}
      onClick={(e) => {
        // Close when clicking the backdrop
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col transition-all duration-500"
        style={{ 
          transform: animateIn ? 'scale(1) translateY(0)' : 'scale(0.95) translateY(20px)'
        }}
      >
        <div className={`p-4 border-b flex justify-between items-center ${sourceStyle.bgColor ? sourceStyle.bgColor + '/20' : 'bg-gray-50'}`}>
          <h3 className={`text-lg font-medium flex items-center ${sourceStyle.textColor}`}>
            <span className="mr-2">{
              result.source === 'video_transcriptions' ? '🎬' :
              result.source === 'document_embeddings' ? '📄' :
              result.source === 'video_transcriptions_full' ? '📽️' :
              result.source === 'webpage_content' ? '🌐' :
              result.source === 'text_content' ? '📝' :
              result.source === 'media_content' ? '🎵' : '📎'
            }</span>
            Result Details
          </h3>
          <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-red-50 hover:text-red-500 transition-colors">
            ✕
          </Button>
        </div>
        
        <div className="p-4 overflow-y-auto flex-grow">
          {/* Header info */}
          <div className="mb-4 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
            <h4 className="font-medium mb-2 text-lg">
              {result.title || (result.source === 'video_transcriptions' ? 
                `Video Transcript: ${result.content_id || 'Unknown'}` : 
                result.source === 'document_embeddings' ? 
                `Document: ${result.content_id || 'Unknown'}` : 
                `Result from ${result.content_id || 'unknown source'}`)}
            </h4>
            <div className="flex flex-wrap gap-2 mb-2">
              <ScoreBadge score={result.similarity} />
              <MethodBadge method={result.search_method} />
              <SourceBadge source={result.source} />
            </div>
            {result.url && (
              <div className="text-sm mb-2 bg-blue-50 p-2 rounded-md border border-blue-100">
                <span className="font-medium flex items-center">
                  <span className="mr-1">🔗</span> Source URL:
                </span>
                <a 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="clickable-url break-all"
                >
                  {result.url}
                </a>
              </div>
            )}
          </div>
          
          {/* Content */}
          <div className="mb-4 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            <h5 className="text-sm font-medium mb-1 flex items-center">
              <span className="mr-1">📝</span> Content
            </h5>
            <div className="p-3 bg-gray-50 rounded-md whitespace-pre-line text-sm border border-gray-200 shadow-sm">
              {result.content || 'No content available'}
            </div>
          </div>
          
          {/* Metadata */}
          {result.metadata && Object.keys(result.metadata).length > 0 && (
            <div className="mb-4 animate-fadeIn" style={{ animationDelay: '0.3s' }}>
              <h5 className="text-sm font-medium mb-1 flex items-center">
                <span className="mr-1">🔍</span> Metadata
              </h5>
              <div className="p-3 bg-gray-50 rounded-md text-sm border border-gray-200 shadow-sm">
                <pre className="whitespace-pre-wrap overflow-x-auto">
                  {JSON.stringify(result.metadata, null, 2)}
                </pre>
              </div>
            </div>
          )}
          
          {/* Summary */}
          {result.summary && (
            <div className="mb-4 animate-fadeIn" style={{ animationDelay: '0.4s' }}>
              <h5 className="text-sm font-medium mb-1 flex items-center">
                <span className="mr-1">📋</span> Summary
              </h5>
              <div className="p-3 bg-blue-50 rounded-md text-sm border border-blue-100 shadow-sm">
                {result.summary}
              </div>
            </div>
          )}
          
          {/* Video/Segment info */}
          {(result.start_time || result.end_time || result.segment_id !== undefined) && (
            <div className="mb-4 animate-fadeIn" style={{ animationDelay: '0.5s' }}>
              <h5 className="text-sm font-medium mb-1 flex items-center">
                <span className="mr-1">🎬</span> Segment Information
              </h5>
              <div className="grid grid-cols-2 gap-2 p-3 bg-gray-50 rounded-md text-sm border border-gray-200 shadow-sm">
                {result.segment_id !== undefined && (
                  <>
                    <div className="font-medium flex items-center">
                      <span className="mr-1">🔢</span> Segment ID:
                    </div>
                    <div>{result.segment_id}</div>
                  </>
                )}
                {result.start_time && (
                  <>
                    <div className="font-medium flex items-center">
                      <span className="mr-1">⏱️</span> Start Time:
                    </div>
                    <div>{result.start_time}</div>
                  </>
                )}
                {result.end_time && (
                  <>
                    <div className="font-medium flex items-center">
                      <span className="mr-1">⏱️</span> End Time:
                    </div>
                    <div>{result.end_time}</div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
        
        <div className="p-4 border-t flex justify-between items-center bg-gray-50">
          <div className="text-xs text-gray-500">
            ID: {result.content_id || 'N/A'}
          </div>
          <Button 
            variant="outline" 
            onClick={onClose}
            className={`transition-colors ${sourceStyle.textColor} hover:${sourceStyle.bgColor}`}
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
