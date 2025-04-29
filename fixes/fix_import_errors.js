/**
 * Script to fix import errors in AnalysisDisplay.jsx
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisDisplay.jsx file
const analysisDisplayPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisDisplay.jsx');

// Function to fix the import errors
function fixImportErrors() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisDisplayPath, 'utf8');
    
    // Fix the import statements - ensure each component is only imported once
    const importStatement = `import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, PROGRESS_STAGES } from '@/lib/search-styles';
import { AnalysisFormatter } from './AnalysisFormatter';`;
    
    // Replace all import statements at the beginning of the file
    content = content.replace(/import React.*?;(\s*import .*?;)*/, importStatement);
    
    // Remove any duplicate import statements throughout the file
    content = content.replace(/import \{ Card,.*?\} from "@\/components\/ui\/card";/g, '');
    content = content.replace(/import \{ Tabs,.*?\} from "@\/components\/ui\/tabs";/g, '');
    content = content.replace(/import \{ Button \} from "@\/components\/ui\/button";/g, '');
    content = content.replace(/import \{ ANALYSIS_STEPS, PROGRESS_STAGES \} from '@\/lib\/search-styles';/g, '');
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisDisplayPath, content, 'utf8');
    console.log('Successfully fixed import errors in AnalysisDisplay.jsx');
    return true;
  } catch (error) {
    console.error('Error fixing import errors in AnalysisDisplay.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Fix import errors
    const errorsFixed = fixImportErrors();
    
    if (errorsFixed) {
      console.log('Import errors fixed successfully!');
    } else {
      console.error('Failed to fix import errors.');
    }
  } catch (error) {
    console.error('Error applying fix:', error);
  }
}

// Run the fix
applyFix();
