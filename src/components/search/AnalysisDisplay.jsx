import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, PROGRESS_STAGES } from '@/lib/search-styles';
import { AnalysisFormatter } from './AnalysisFormatter';

/**
 * Component for displaying AI analysis with rich formatting and animations
 */
export function AnalysisDisplay({ openaiAnalysis, groqAnalysis }) {
  const [activeTab, setActiveTab] = useState('openai');
  const [animateIn, setAnimateIn] = useState(false);
  
  // Add custom CSS for analysis content
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
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
      .analysis-formatted-content .font-bold {
        font-weight: 700;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  
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
  
  // We'll always use the full content with the AnalysisFormatter
  // but control the display height with CSS instead of truncating the content
  const shouldTruncate = content.length > 1200 && !expanded;
  
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
            ${shouldTruncate ? 'max-h-[500px] overflow-y-auto' : ''} 
            analysis-content shadow-sm`}
        >
          <AnalysisFormatter content={content} />
        </div>
      </div>
      
      {content.length > 1200 && (
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
