import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SourceBadge, MethodBadge } from './SearchBadges';
import { getSourceStyle, getMethodStyle } from '@/lib/search-styles';

/**
 * Component for displaying search results grouped by source with enhanced styling and animations
 */
export function SearchResultsBySource({ results }) {
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Group results by source
  const resultsBySource = results.reduce((acc, result) => {
    const source = result.source || 'unknown';
    if (!acc[source]) acc[source] = [];
    acc[source].push(result);
    return acc;
  }, {});
  
  // Sort sources by count (descending)
  const sortedSources = Object.keys(resultsBySource).sort(
    (a, b) => resultsBySource[b].length - resultsBySource[a].length
  );
  
  // Calculate total results
  const totalResults = results.length;
  
  return (
    <Card 
      className="mb-6 overflow-hidden shadow-sm transition-all duration-500"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'translateY(0)' : 'translateY(20px)'
      }}
    >
      <CardHeader className="pb-2 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardTitle className="text-base flex items-center justify-between">
          <span className="flex items-center">
            <span className="mr-2">📊</span>
            Results by Source
          </span>
          <span className="text-xs bg-white px-2 py-1 rounded-full shadow-sm text-gray-500">
            {totalResults} total results
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {sortedSources.map((source, sourceIndex) => {
            const sourceResults = resultsBySource[source];
            const count = sourceResults.length;
            const percentage = Math.round((count / totalResults) * 100);
            const sourceStyle = getSourceStyle(source);
            
            // Calculate animation delay based on index
            const animationDelay = 0.2 + (sourceIndex * 0.1);
            
            // Calculate average score
            const avgScore = sourceResults.reduce((sum, r) => sum + (r.similarity || 0), 0) / count;
            
            // Get top method
            const methods = sourceResults.map(r => r.search_method || 'unknown');
            const methodCounts = methods.reduce((acc, method) => {
              acc[method] = (acc[method] || 0) + 1;
              return acc;
            }, {});
            const topMethod = Object.entries(methodCounts)
              .sort((a, b) => b[1] - a[1])[0][0];
            const methodStyle = getMethodStyle(topMethod);
            
            return (
              <div 
                key={source} 
                className="space-y-2 p-3 rounded-lg border border-gray-100 shadow-sm"
                style={{ 
                  opacity: animateIn ? 1 : 0,
                  transform: animateIn ? 'translateY(0)' : 'translateY(10px)',
                  transitionDelay: `${animationDelay}s`,
                  transition: 'all 0.5s ease'
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <SourceBadge source={source} />
                    <span className="ml-2 text-sm text-gray-500 bg-white px-2 py-0.5 rounded-full shadow-sm">
                      {count} results ({percentage}%)
                    </span>
                  </div>
                </div>
                
                {/* Progress bar with animation */}
                <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                  <div 
                    className={`h-3 rounded-full ${sourceStyle.bgColor} transition-all duration-1000`} 
                    style={{ 
                      width: animateIn ? `${percentage}%` : '0%',
                      transitionDelay: `${animationDelay + 0.3}s`
                    }}
                  ></div>
                </div>
                
                {/* Source statistics */}
                <div className="grid grid-cols-2 gap-4 text-xs mt-2">
                  <div className={`p-2 rounded-md ${sourceStyle.bgColor}/10 border border-gray-100`}>
                    <div className="font-medium mb-1 flex items-center">
                      <span className="mr-1">📈</span> Average Score
                    </div>
                    <div className={`text-lg font-bold ${sourceStyle.textColor}`}>
                      {avgScore.toFixed(3)}
                    </div>
                  </div>
                  
                  <div className={`p-2 rounded-md ${methodStyle?.bgColor || 'bg-gray-50'}/10 border border-gray-100`}>
                    <div className="font-medium mb-1 flex items-center">
                      <span className="mr-1">🔍</span> Top Method
                    </div>
                    <div className="flex items-center">
                      <MethodBadge method={topMethod} />
                      <span className="ml-1 text-xs text-gray-500">
                        ({Math.round((methodCounts[topMethod] / count) * 100)}%)
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Content preview */}
                {sourceResults.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-100">
                    <div className="text-xs text-gray-500 mb-1 flex items-center">
                      <span className="mr-1">📝</span> Sample content:
                    </div>
                    <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded-md border border-gray-100 max-h-12 overflow-hidden">
                      {sourceResults[0].content?.substring(0, 100)}
                      {sourceResults[0].content?.length > 100 && '...'}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* No results message */}
        {sortedSources.length === 0 && (
          <div className="text-sm text-gray-500 p-6 text-center border border-dashed border-gray-200 rounded-lg bg-gray-50">
            <p className="mb-1">No results available to display.</p>
            <p className="text-xs text-gray-400">Try adjusting your search query or parameters.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Component for displaying a summary of search results with enhanced styling
 */
export function SearchResultsSummary({ results, metadata = {} }) {
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
      <Card 
        className="mb-6 overflow-hidden shadow-sm transition-all duration-500"
        style={{ 
          opacity: animateIn ? 1 : 0,
          transform: animateIn ? 'translateY(0)' : 'translateY(20px)'
        }}
      >
        <CardHeader className="pb-2 bg-gradient-to-r from-gray-50 to-gray-100">
          <CardTitle className="text-base flex items-center">
            <span className="mr-2">📊</span>
            Search Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-500 p-6 text-center border border-dashed border-gray-200 rounded-lg bg-gray-50">
            <p className="mb-1">No results available to summarize.</p>
            <p className="text-xs text-gray-400">Try adjusting your search query or parameters.</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // Calculate statistics
  const totalResults = results.length;
  const avgScore = results.reduce((sum, r) => sum + (r.similarity || 0), 0) / totalResults;
  
  // Count by method
  const methodCounts = results.reduce((acc, r) => {
    const method = r.search_method || 'unknown';
    acc[method] = (acc[method] || 0) + 1;
    return acc;
  }, {});
  
  // Count by source
  const sourceCounts = results.reduce((acc, r) => {
    const source = r.source || 'unknown';
    acc[source] = (acc[source] || 0) + 1;
    return acc;
  }, {});
  
  return (
    <Card 
      className="mb-6 overflow-hidden shadow-sm transition-all duration-500"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'translateY(0)' : 'translateY(20px)'
      }}
    >
      <CardHeader className="pb-2 bg-gradient-to-r from-blue-50 to-green-50">
        <CardTitle className="text-base flex items-center justify-between">
          <span className="flex items-center">
            <span className="mr-2">📊</span>
            Search Summary
          </span>
          <span className="text-xs bg-white px-2 py-1 rounded-full shadow-sm text-gray-500">
            {totalResults} total results
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Left column - Basic stats */}
          <div 
            className="space-y-3 p-3 rounded-lg border border-blue-100 bg-blue-50/30"
            style={{ 
              opacity: animateIn ? 1 : 0,
              transform: animateIn ? 'translateX(0)' : 'translateX(-10px)',
              transitionDelay: '0.2s',
              transition: 'all 0.5s ease'
            }}
          >
            <div className="text-sm font-medium text-blue-700 flex items-center">
              <span className="mr-1">📈</span> Basic Statistics
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white p-2 rounded-md shadow-sm border border-blue-100">
                <div className="text-xs text-gray-500">Total Results</div>
                <div className="text-lg font-bold text-blue-700">{totalResults}</div>
              </div>
              
              <div className="bg-white p-2 rounded-md shadow-sm border border-blue-100">
                <div className="text-xs text-gray-500">Average Score</div>
                <div className="text-lg font-bold text-blue-700">{avgScore.toFixed(3)}</div>
              </div>
              
              <div className="bg-white p-2 rounded-md shadow-sm border border-blue-100">
                <div className="text-xs text-gray-500">Duration</div>
                <div className="text-lg font-bold text-blue-700">
                  {metadata.search_duration_seconds ? 
                    `${metadata.search_duration_seconds.toFixed(2)}s` : 
                    'N/A'}
                </div>
              </div>
              
              <div className="bg-white p-2 rounded-md shadow-sm border border-blue-100">
                <div className="text-xs text-gray-500">Tokens Used</div>
                <div className="text-lg font-bold text-blue-700">
                  {metadata.token_usage?.total_tokens ? 
                    metadata.token_usage.total_tokens.toLocaleString() : 
                    'N/A'}
                </div>
              </div>
            </div>
          </div>
          
          {/* Right column - Method & Source breakdown */}
          <div 
            className="space-y-3"
            style={{ 
              opacity: animateIn ? 1 : 0,
              transform: animateIn ? 'translateX(0)' : 'translateX(10px)',
              transitionDelay: '0.3s',
              transition: 'all 0.5s ease'
            }}
          >
            <div className="p-3 rounded-lg border border-green-100 bg-green-50/30">
              <div className="text-sm font-medium text-green-700 mb-2 flex items-center">
                <span className="mr-1">🔍</span> By Method
              </div>
              <div className="space-y-2">
                {Object.entries(methodCounts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([method, count], index) => {
                    const methodStyle = getMethodStyle(method);
                    const percentage = Math.round((count / totalResults) * 100);
                    
                    return (
                      <div key={method} className="space-y-1">
                        <div className="flex justify-between text-sm items-center">
                          <div className="flex items-center">
                            <MethodBadge method={method} />
                          </div>
                          <div className="text-xs font-medium">
                            {count} ({percentage}%)
                          </div>
                        </div>
                        
                        {/* Progress bar */}
                        <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className={`h-1.5 rounded-full ${methodStyle?.bgColor || 'bg-gray-300'} transition-all duration-1000`} 
                            style={{ 
                              width: animateIn ? `${percentage}%` : '0%',
                              transitionDelay: `${0.4 + (index * 0.1)}s`
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
            
            <div className="p-3 rounded-lg border border-purple-100 bg-purple-50/30">
              <div className="text-sm font-medium text-purple-700 mb-2 flex items-center">
                <span className="mr-1">📂</span> By Source
              </div>
              <div className="space-y-2">
                {Object.entries(sourceCounts)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 3)
                  .map(([source, count], index) => {
                    const sourceStyle = getSourceStyle(source);
                    const percentage = Math.round((count / totalResults) * 100);
                    
                    return (
                      <div key={source} className="space-y-1">
                        <div className="flex justify-between text-sm items-center">
                          <div className="flex items-center">
                            <SourceBadge source={source} />
                          </div>
                          <div className="text-xs font-medium">
                            {count} ({percentage}%)
                          </div>
                        </div>
                        
                        {/* Progress bar */}
                        <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className={`h-1.5 rounded-full ${sourceStyle.bgColor} transition-all duration-1000`} 
                            style={{ 
                              width: animateIn ? `${percentage}%` : '0%',
                              transitionDelay: `${0.6 + (index * 0.1)}s`
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                {Object.keys(sourceCounts).length > 3 && (
                  <div className="text-xs text-purple-500 italic text-center mt-1 bg-white p-1 rounded-md">
                    +{Object.keys(sourceCounts).length - 3} more sources
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
