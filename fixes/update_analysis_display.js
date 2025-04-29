/**
 * Script to update AnalysisDisplay.jsx to use the new AnalysisFormatter component
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisDisplay.jsx file
const analysisDisplayPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisDisplay.jsx');

// Function to update the AnalysisDisplay.jsx file
function updateAnalysisDisplay() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisDisplayPath, 'utf8');
    
    // Check if the file already imports the AnalysisFormatter component
    if (content.includes('import { AnalysisFormatter }')) {
      console.log('The AnalysisFormatter component is already imported in the file.');
      return true;
    }
    
    // Add the import statement for the AnalysisFormatter component
    const importStatement = `import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, PROGRESS_STAGES } from '@/lib/search-styles';
import { AnalysisFormatter } from './AnalysisFormatter';`;
    
    // Replace the existing import statement
    content = content.replace(/import React.*?;/, importStatement);
    
    // Find the FormattedAnalysis component
    const formattedAnalysisRegex = /function FormattedAnalysis\(\{ content, provider \}\) \{[\s\S]*?return \(\s*<div[\s\S]*?<\/div>\s*\);\s*\}/;
    const match = content.match(formattedAnalysisRegex);
    
    if (!match) {
      console.error('Could not find the FormattedAnalysis component in the file.');
      return false;
    }
    
    // Create the new FormattedAnalysis component that uses the AnalysisFormatter
    const newFormattedAnalysis = `function FormattedAnalysis({ content, provider }) {
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
          <AnalysisFormatter content={displayContent} />
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
    
    // Replace the FormattedAnalysis component
    content = content.replace(formattedAnalysisRegex, newFormattedAnalysis);
    
    // Remove the formatAnalysisContent and ultimateProcessHtmlContent functions
    content = content.replace(/\/\*\*\s*\*\s*Format analysis content[\s\S]*?function formatAnalysisContent[\s\S]*?return formatted;\s*\}/, '');
    content = content.replace(/\/\*\*\s*\*\s*Ultimate approach[\s\S]*?function ultimateProcessHtmlContent[\s\S]*?return [`']<div class="analysis-content">[\s\S]*?<\/div>[`'];\s*\}/, '');
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisDisplayPath, content, 'utf8');
    console.log('Successfully updated AnalysisDisplay.jsx to use the AnalysisFormatter component');
    return true;
  } catch (error) {
    console.error('Error updating AnalysisDisplay.jsx:', error);
    return false;
  }
}

// Main function to apply the update
async function applyUpdate() {
  try {
    // Update AnalysisDisplay.jsx
    const displayUpdated = updateAnalysisDisplay();
    
    if (displayUpdated) {
      console.log('AnalysisDisplay.jsx updated successfully!');
      console.log('Changes:');
      console.log('1. Imported the AnalysisFormatter component');
      console.log('2. Updated the FormattedAnalysis component to use the AnalysisFormatter');
      console.log('3. Removed the formatAnalysisContent and ultimateProcessHtmlContent functions');
    } else {
      console.error('Failed to update AnalysisDisplay.jsx.');
    }
  } catch (error) {
    console.error('Error applying update:', error);
  }
}

// Run the update
applyUpdate();
