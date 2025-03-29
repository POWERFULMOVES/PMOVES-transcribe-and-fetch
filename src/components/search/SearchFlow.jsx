import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PROGRESS_STAGES, STATUS_INDICATORS, ANALYSIS_STEPS } from '@/lib/search-styles';

/**
 * Component for displaying the search flow process with enhanced animations
 */
export function SearchFlowIndicator({ currentStage = 'start', metadata = {}, loading = false }) {
  // Debug log the current stage and loading state
  console.log('SearchFlowIndicator received:', { currentStage, loading, metadata });
  
  // Define all stages in order
  const stages = ['start', 'search', 'filter', 'combine', 'analyze', 'complete'];
  
  // Find the current stage index
  // If the stage is not found, default to the 'start' stage
  // Ensure we use 'complete' stage when loading is false and we're in the last stage
  const effectiveStage = (!loading && currentStage === 'analyze') ? 'complete' : currentStage;
  const currentIndex = stages.indexOf(effectiveStage) !== -1 ? stages.indexOf(effectiveStage) : 0;
  console.log('Stage index:', currentIndex, 'for stage:', effectiveStage);
  
  // Animation state
  const [animateIn, setAnimateIn] = useState(false);
  
  // Track previous stage for animation
  const [prevStage, setPrevStage] = useState(currentStage);
  const [stageChanged, setStageChanged] = useState(false);
  
  // Detect stage changes for animations
  useEffect(() => {
    console.log('Stage changed from', prevStage, 'to', currentStage);
    if (currentStage !== prevStage) {
      setPrevStage(currentStage);
      setStageChanged(true);
      
      // Reset stage changed flag after animation
      const timer = setTimeout(() => {
        setStageChanged(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [currentStage, prevStage]);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Force component to be visible even if animateIn is false
  const visibilityClass = 'opacity-100';
  
  return (
    <Card className={`mb-6 overflow-hidden transition-all duration-500 ${visibilityClass}`}>
      <CardHeader className="pb-2 bg-gradient-to-r from-blue-50 to-cyan-50">
        <CardTitle className="text-base flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">{PROGRESS_STAGES.start.icon}</span>
            Search Process Flow
          </div>
          {loading && (
            <div className="text-xs bg-yellow-100 px-2 py-1 rounded-full text-yellow-700 animate-pulse">
              Processing...
            </div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Progress line with animation */}
          <div className="absolute top-4 left-4 right-4 h-0.5 bg-gray-200">
            <div 
              className="h-full bg-blue-400 transition-all duration-1000" 
              style={{ 
                width: `${currentIndex === 0 ? 0 : (currentIndex / (stages.length - 1)) * 100}%`,
                transitionDelay: '0.5s'
              }}
            ></div>
          </div>
          
          {/* Stages */}
          <div className="flex justify-between relative">
            {stages.map((stage, index) => {
              const stageInfo = PROGRESS_STAGES[stage] || {
                icon: '📌',
                message: stage.charAt(0).toUpperCase() + stage.slice(1),
                textColor: 'text-gray-600',
                bgColor: 'bg-gray-100'
              };
              
              const isActive = index <= currentIndex;
              const isCurrent = index === currentIndex;
              const isPast = index < currentIndex;
              
              // Calculate delay for staggered animation
              const animationDelay = 0.1 + (index * 0.15);
              
              return (
                <div 
                  key={stage} 
                  className="flex flex-col items-center z-10"
                  style={{ 
                    transition: 'transform 0.5s ease, opacity 0.5s ease',
                    transitionDelay: `${animationDelay}s`,
                    opacity: 1, // Always visible
                    transform: animateIn ? 'translateY(0)' : 'translateY(10px)'
                  }}
                >
                  {/* Stage icon */}
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm search-flow-step
                    transition-all duration-300
                    ${isActive ? `${stageInfo.bgColor || 'bg-blue-100'}` : 'bg-gray-100'}
                    ${isActive ? `${stageInfo.textColor || 'text-blue-600'}` : 'text-gray-400'}
                    ${isCurrent ? 'ring-2 ring-offset-2 ring-blue-400 active animate-pulse' : ''}
                    ${isPast ? 'shadow-sm' : ''}
                  `}>
                    {isCurrent && loading ? (
                      <span className="animate-spin">{STATUS_INDICATORS.progress}</span>
                    ) : (
                      <span className={isPast ? 'transform scale-110' : ''}>{stageInfo.icon}</span>
                    )}
                  </div>
                  
                  {/* Stage label */}
                  <div className={`
                    mt-2 text-xs text-center max-w-[80px]
                    ${isActive ? stageInfo.textColor || 'text-blue-600' : 'text-gray-400'}
                    ${isActive ? stageInfo.fontWeight || 'font-medium' : 'font-normal'}
                    transition-all duration-300
                  `}>
                    {stageInfo.message}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Current stage indicator */}
        <div className="mt-4 pt-2 border-t border-gray-200 text-sm text-center">
          <div className={`inline-block px-3 py-1 rounded-full ${
            loading ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
          }`}>
            {loading ? (
              <span className="flex items-center">
                <span className="animate-spin mr-1">{STATUS_INDICATORS.progress}</span>
                Processing: {currentStage.charAt(0).toUpperCase() + currentStage.slice(1)} stage
              </span>
            ) : (
              <span className="flex items-center">
                <span className="mr-1">✓</span>
                {currentStage === 'complete' ? 'Search complete' : 'Stage complete'}
              </span>
            )}
          </div>
        </div>
        
        {/* Metadata display with animation */}
        {metadata && Object.keys(metadata).length > 0 && (
          <div 
            className="mt-4 pt-2 border-t border-gray-200 grid grid-cols-2 gap-2 text-xs"
            style={{ 
              transition: 'opacity 0.5s ease, transform 0.5s ease',
              transitionDelay: '1s',
              opacity: animateIn ? 1 : 0,
              transform: animateIn ? 'translateY(0)' : 'translateY(10px)'
            }}
          >
            {metadata.search_duration_seconds !== undefined && (
              <div className="p-2 bg-blue-50 rounded-md">
                <span className="text-gray-500">⏱️ Duration:</span>{' '}
                <span className="font-medium text-blue-700">{metadata.search_duration_seconds.toFixed(2)}s</span>
              </div>
            )}
            {metadata.total_results_found !== undefined && (
              <div className="p-2 bg-green-50 rounded-md">
                <span className="text-gray-500">📊 Results:</span>{' '}
                <span className="font-medium text-green-700">{metadata.total_results_found}</span>
              </div>
            )}
            {metadata.token_usage?.embedding_tokens !== undefined && (
              <div className="p-2 bg-purple-50 rounded-md">
                <span className="text-gray-500">🧠 Embedding Tokens:</span>{' '}
                <span className="font-medium text-purple-700">{metadata.token_usage.embedding_tokens.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.generation_tokens?.input !== undefined && (
              <div className="p-2 bg-yellow-50 rounded-md">
                <span className="text-gray-500">📥 Generation Input:</span>{' '}
                <span className="font-medium text-yellow-700">{metadata.token_usage.generation_tokens.input.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.generation_tokens?.output !== undefined && (
              <div className="p-2 bg-cyan-50 rounded-md">
                <span className="text-gray-500">📤 Generation Output:</span>{' '}
                <span className="font-medium text-cyan-700">{metadata.token_usage.generation_tokens.output.toLocaleString()}</span>
              </div>
            )}
            {metadata.token_usage?.total_tokens !== undefined && (
              <div className="p-2 bg-red-50 rounded-md">
                <span className="text-gray-500">💰 Total Tokens:</span>{' '}
                <span className="font-medium text-red-700">{metadata.token_usage.total_tokens.toLocaleString()}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Component for displaying search results by method with enhanced styling
 */
export function SearchResultsByMethod({ results, title, icon }) {
  // Animation state
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Group results by method
  const resultsByMethod = results.reduce((acc, result) => {
    const method = result.search_method || 'unknown';
    if (!acc[method]) acc[method] = [];
    acc[method].push(result);
    return acc;
  }, {});
  
  // Sort methods by priority: hybrid, dot_product, keyword, others
  const methodOrder = ['hybrid', 'dot_product', 'keyword'];
  const sortedMethods = Object.keys(resultsByMethod).sort(
    (a, b) => methodOrder.indexOf(a) - methodOrder.indexOf(b)
  );
  
  return (
    <Card className={`mb-6 overflow-hidden transition-all duration-500 ${animateIn ? 'opacity-100' : 'opacity-0'}`}>
      <CardHeader className="pb-2 bg-gradient-to-r from-cyan-50 to-blue-50">
        <CardTitle className="text-base flex items-center">
          {icon && <span className="mr-2">{icon}</span>}
          {title || 'Search Results by Method'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedMethods.map((method, methodIndex) => {
            const methodResults = resultsByMethod[method];
            const count = methodResults.length;
            
            // Get method style
            const methodStyle = method === 'keyword' 
              ? { bgColor: 'bg-cyan-50', borderColor: 'border-cyan-200', textColor: 'text-cyan-700' }
              : method === 'dot_product'
                ? { bgColor: 'bg-blue-50', borderColor: 'border-blue-200', textColor: 'text-blue-700' }
                : method === 'hybrid'
                  ? { bgColor: 'bg-green-50', borderColor: 'border-green-200', textColor: 'text-green-700' }
                  : { bgColor: 'bg-gray-50', borderColor: 'border-gray-200', textColor: 'text-gray-700' };
            
            // Calculate delay for staggered animation
            const animationDelay = 0.2 + (methodIndex * 0.15);
            
            return (
              <div 
                key={method} 
                className={`border rounded-md p-3 shadow-sm ${methodStyle.borderColor} ${methodStyle.bgColor} transition-all duration-500`}
                style={{ 
                  transitionDelay: `${animationDelay}s`,
                  opacity: animateIn ? 1 : 0,
                  transform: animateIn ? 'translateY(0)' : 'translateY(10px)'
                }}
              >
                <h3 className={`text-sm font-medium flex items-center mb-2 ${methodStyle.textColor}`}>
                  <span className="mr-1">{
                    method === 'keyword' ? '🔍' :
                    method === 'dot_product' ? '🎯' :
                    method === 'hybrid' ? '🔄' : '📌'
                  }</span>
                  {method.charAt(0).toUpperCase() + method.slice(1)} Search
                  <span className="ml-2 text-xs bg-white px-2 py-0.5 rounded-full shadow-sm">
                    {count} results
                  </span>
                </h3>
                
                <div className="text-xs text-gray-600 mb-2 pl-2 border-l-2 border-gray-300">
                  {method === 'keyword' && 'Traditional text matching to find content containing specific keywords.'}
                  {method === 'dot_product' && 'Vector similarity search using AI embeddings to find semantically similar content.'}
                  {method === 'hybrid' && 'Combined approach using both keyword and vector search for comprehensive results.'}
                  {method !== 'keyword' && method !== 'dot_product' && method !== 'hybrid' && 'Custom search method.'}
                </div>
                
                <div className="text-xs mt-3 pt-2 border-t border-gray-200">
                  <span className="font-medium">Top sources:</span>{' '}
                  <div className="flex flex-wrap gap-1 mt-1">
                    {Object.entries(
                      methodResults.reduce((acc, r) => {
                        acc[r.source] = (acc[r.source] || 0) + 1;
                        return acc;
                      }, {})
                    )
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 3)
                      .map(([source, count], i) => {
                        const sourceStyle = source === 'video_transcriptions' 
                          ? 'bg-green-100 text-green-700 border-green-200'
                          : source === 'document_embeddings'
                            ? 'bg-blue-100 text-blue-700 border-blue-200'
                            : source === 'video_transcriptions_full'
                              ? 'bg-purple-100 text-purple-700 border-purple-200'
                              : 'bg-gray-100 text-gray-700 border-gray-200';
                        
                        return (
                          <span 
                            key={source} 
                            className={`${sourceStyle} px-2 py-0.5 rounded-full text-xs border`}
                          >
                            {source} ({count})
                          </span>
                        );
                      })
                    }
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Component for displaying the analysis process with enhanced animations
 */
export function AnalysisProcess({ currentStep = 'start', openaiAnalysis, groqAnalysis }) {
  // Define all steps in order
  const steps = ['start', 'filtering', 'prioritizing', 'preparing', 'generating', 'complete'];
  
  // Check if analysis is available - if so, ensure we show complete
  const hasOpenAI = openaiAnalysis && openaiAnalysis.trim() !== '';
  const hasGroq = groqAnalysis && groqAnalysis.trim() !== '';
  const hasAnalysis = hasOpenAI || hasGroq;
  
  // Use effective step to ensure we show complete when analysis is available
  const effectiveStep = hasAnalysis ? 'complete' : currentStep;
  
  // Find the current step index
  const currentIndex = steps.indexOf(effectiveStep) !== -1 ? steps.indexOf(effectiveStep) : 0;
  
  // Animation state
  const [animateIn, setAnimateIn] = useState(false);
  
  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <Card className={`mb-6 overflow-hidden transition-all duration-500 ${animateIn ? 'opacity-100' : 'opacity-0'}`}>
      <CardHeader className="pb-2 bg-gradient-to-r from-cyan-50 to-purple-50">
        <CardTitle className="text-base flex items-center">
          <span className="mr-2">{PROGRESS_STAGES.analyze.icon}</span>
          AI Analysis Process
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Analysis steps with progress indicator */}
        <div className="relative mb-4 border border-gray-100 rounded-lg p-2 bg-gray-50">
          {/* Progress bar */}
          <div className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-100/50 to-blue-100/50 transition-all duration-1000 rounded-lg" 
            style={{ 
              width: `${(currentIndex / (steps.length - 1)) * 100}%`,
              transitionDelay: '0.5s'
            }}
          ></div>
          
          {/* Steps */}
          <div className="space-y-2 relative z-10">
            {steps.map((step, index) => {
              const stepInfo = ANALYSIS_STEPS[step] || {};
              const isActive = index <= currentIndex;
              const isCurrent = index === currentIndex;
              const isPast = index < currentIndex;
              
              // Calculate delay for staggered animation
              const animationDelay = 0.2 + (index * 0.1);
              
              return (
                <div 
                  key={step} 
                  className={`
                    flex items-center p-2 rounded-md transition-all duration-300
                    ${isActive ? 'bg-cyan-50 shadow-sm' : 'bg-white opacity-60'}
                  `}
                  style={{ 
                    transitionDelay: `${animationDelay}s`,
                    opacity: animateIn ? (isActive ? 1 : 0.6) : 0,
                    transform: animateIn ? 'translateX(0)' : 'translateX(-10px)'
                  }}
                >
                  <div className={`
                    w-6 h-6 rounded-full flex items-center justify-center text-xs mr-2
                    transition-all duration-300 shadow-sm
                    ${isActive ? 'bg-white text-cyan-700' : 'bg-gray-100 text-gray-400'}
                    ${isCurrent ? 'ring-2 ring-cyan-300' : ''}
                  `}>
                    {isCurrent && step !== 'complete' ? (
                      <span className="animate-spin">{STATUS_INDICATORS.progress}</span>
                    ) : (
                      <span className={isPast ? 'transform scale-110' : ''}>
                        {step === 'start' ? '🔍' :
                         step === 'filtering' ? '🔎' :
                         step === 'prioritizing' ? '⚖️' :
                         step === 'preparing' ? '📋' :
                         step === 'generating' ? '🤖' :
                         step === 'complete' ? '✅' : '📌'}
                      </span>
                    )}
                  </div>
                  <div className={`
                    text-sm transition-all duration-300
                    ${isActive ? 'text-cyan-700' : 'text-gray-400'}
                    ${isActive ? 'font-medium' : 'font-normal'}
                  `}>
                    {step === 'start' ? 'Starting Search Results Analysis...' :
                     step === 'filtering' ? 'Filtering results...' :
                     step === 'prioritizing' ? 'Prioritizing results...' :
                     step === 'preparing' ? 'Preparing analysis text...' :
                     step === 'generating' ? 'Generating AI Analysis...' :
                     step === 'complete' ? 'AI analysis completed' : step}
                  </div>
                  
                  {/* Status indicator */}
                  {isPast && (
                    <div className="ml-auto text-green-500">
                      {STATUS_INDICATORS.success}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Analysis preview */}
        {hasAnalysis && currentIndex >= steps.indexOf('complete') && (
          <div className="mt-4 pt-4 border-t border-gray-200 animate-fadeIn">
            <h3 className="text-sm font-medium mb-2">Analysis Results</h3>
            
            {hasOpenAI && (
              <div className="mb-3">
                <h4 className="text-xs font-medium text-blue-600 mb-1 flex items-center">
                  <span className="mr-1">🧠</span> OpenAI Analysis:
                </h4>
                <div className="text-xs bg-blue-50 p-2 rounded-md max-h-24 overflow-y-auto border border-blue-100 shadow-sm">
                  {openaiAnalysis.substring(0, 200)}
                  {openaiAnalysis.length > 200 && '...'}
                </div>
              </div>
            )}
            
            {hasGroq && (
              <div>
                <h4 className="text-xs font-medium text-purple-600 mb-1 flex items-center">
                  <span className="mr-1">⚡</span> Groq Analysis:
                </h4>
                <div className="text-xs bg-purple-50 p-2 rounded-md max-h-24 overflow-y-auto border border-purple-100 shadow-sm">
                  {groqAnalysis.substring(0, 200)}
                  {groqAnalysis.length > 200 && '...'}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* No analysis message */}
        {!hasAnalysis && currentIndex >= steps.indexOf('complete') && (
          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-500 text-center p-4 bg-gray-50 rounded-md">
            <p className="mb-1">No analysis results available.</p>
            <p className="text-xs">Enable AI analysis in search settings to see insights about your search results.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
