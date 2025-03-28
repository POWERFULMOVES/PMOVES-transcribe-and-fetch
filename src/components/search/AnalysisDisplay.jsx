import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, PROGRESS_STAGES } from '@/lib/search-styles';

/**
 * Component for displaying AI analysis with rich formatting and animations
 */
export function AnalysisDisplay({ openaiAnalysis, groqAnalysis }) {
  const [activeTab, setActiveTab] = useState('openai');
  const [animateIn, setAnimateIn] = useState(false);
  
  // Check if analysis is available
  const hasOpenAI = openaiAnalysis && openaiAnalysis.trim() !== '';
  const hasGroq = groqAnalysis && groqAnalysis.trim() !== '';
  
  // If only one analysis is available, set it as active
  useEffect(() => {
    if (!hasOpenAI && hasGroq) setActiveTab('groq');
    else if (hasOpenAI) setActiveTab('openai');
    
    // Trigger animation after component mounts
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [hasOpenAI, hasGroq]);
  
  // If no analysis is available, show a message
  if (!hasOpenAI && !hasGroq) {
    return (
      <Card className="mb-6 overflow-hidden">
        <CardHeader className="pb-2 bg-gradient-to-r from-gray-50 to-gray-100">
          <CardTitle className="text-base flex items-center">
            <span className="mr-2 animate-pulse">{ANALYSIS_STEPS.start.icon}</span>
            AI Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-500 p-4 text-center border border-dashed border-gray-200 rounded-md bg-gray-50">
            <p className="mb-2">No AI analysis available.</p>
            <p>Enable AI analysis in search settings to see insights about your search results.</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className={`mb-6 overflow-hidden transition-all duration-500 ${animateIn ? 'opacity-100' : 'opacity-0'}`}>
      <CardHeader className="pb-2 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardTitle className="text-base flex items-center">
          <span className="mr-2">{PROGRESS_STAGES.analyze.icon}</span>
          AI Analysis Results
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger 
              value="openai" 
              disabled={!hasOpenAI}
              className={`transition-all duration-300 ${!hasOpenAI ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-100'}`}
            >
              <span className="flex items-center">
                <span className="mr-2">🧠</span>
                OpenAI Analysis
              </span>
            </TabsTrigger>
            <TabsTrigger 
              value="groq" 
              disabled={!hasGroq}
              className={`transition-all duration-300 ${!hasGroq ? 'opacity-50 cursor-not-allowed' : 'hover:bg-purple-100'}`}
            >
              <span className="flex items-center">
                <span className="mr-2">⚡</span>
                Groq Analysis
              </span>
            </TabsTrigger>
          </TabsList>
          
          {hasOpenAI && (
            <TabsContent value="openai" className="mt-4 transition-all duration-300 ease-in-out">
              <FormattedAnalysis content={openaiAnalysis} provider="OpenAI" />
            </TabsContent>
          )}
          
          {hasGroq && (
            <TabsContent value="groq" className="mt-4 transition-all duration-300 ease-in-out">
              <FormattedAnalysis content={groqAnalysis} provider="Groq" />
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}

/**
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
  const shouldTruncate = content.length > 500 && !expanded;
  const displayContent = shouldTruncate ? content.substring(0, 500) + '...' : content;
  
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
    <div className={`transition-all duration-500 ${animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      <div className={`prose prose-sm max-w-none ${provider === 'OpenAI' ? 'prose-blue' : 'prose-purple'}`}>
        <div 
          className={`p-4 rounded-md border ${style.borderColor} ${style.bgColor} 
            ${shouldTruncate ? 'max-h-96 overflow-y-auto' : ''} 
            analysis-content shadow-sm`}
          dangerouslySetInnerHTML={{ __html: formatAnalysisContent(displayContent) }}
        />
      </div>
      
      {content.length > 500 && (
        <div className="mt-2 text-right">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setExpanded(!expanded)}
            className={`h-7 text-xs transition-all duration-300 ${style.textColor} ${style.hoverColor}`}
          >
            {expanded ? '↑ Show less' : '↓ Show more'}
          </Button>
        </div>
      )}
    </div>
  );
}

/**
 * Format analysis content with enhanced Markdown-like formatting
 */
function formatAnalysisContent(content) {
  if (!content) return '';
  
  // Replace newlines with <br> tags
  let formatted = content.replace(/\n/g, '<br>');
  
  // Format headings (# Heading)
  formatted = formatted.replace(/(?:<br>|^)#\s+(.*?)(?:<br>|$)/g, '<h3 class="text-lg font-semibold mt-4 mb-2 text-blue-700">$1</h3>');
  formatted = formatted.replace(/(?:<br>|^)##\s+(.*?)(?:<br>|$)/g, '<h4 class="text-md font-semibold mt-3 mb-1 text-blue-600">$1</h4>');
  formatted = formatted.replace(/(?:<br>|^)###\s+(.*?)(?:<br>|$)/g, '<h5 class="text-sm font-semibold mt-2 mb-1 text-blue-500">$1</h5>');
  
  // Format bold (**text**)
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>');
  
  // Format italic (*text*)
  formatted = formatted.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  
  // Format lists with better styling
  // Unordered lists
  formatted = formatted.replace(/(?:<br>|^)\s*-\s+(.*?)(?=<br>|$)/g, '<br><span class="inline-flex items-start"><span class="text-blue-500 mr-2">•</span><span>$1</span></span>');
  
  // Ordered lists (improved implementation)
  formatted = formatted.replace(/(?:<br>|^)\s*(\d+)\.\s+(.*?)(?=<br>|$)/g, '<br><span class="inline-flex items-start"><span class="text-blue-500 font-medium mr-2">$1.</span><span>$2</span></span>');
  
  // Format code blocks (improved implementation)
  formatted = formatted.replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600">$1</code>');
  
  // Format horizontal rules
  formatted = formatted.replace(/(?:<br>|^)-{3,}(?:<br>|$)/g, '<hr class="my-4 border-t border-gray-200">');
  
  // Format blockquotes
  formatted = formatted.replace(/(?:<br>|^)>\s+(.*?)(?=<br>|$)/g, '<br><blockquote class="pl-3 border-l-2 border-blue-300 text-gray-600 italic">$1</blockquote>');
  
  // Format links (if any)
  formatted = formatted.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:no-underline clickable-url">$1</a>');
  
  // Highlight key terms
  formatted = formatted.replace(/"([^"]+)"/g, '<span class="text-blue-700">"$1"</span>');
  
  return formatted;
}
