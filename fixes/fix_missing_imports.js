/**
 * Script to fix missing imports in AnalysisDisplay.jsx
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisDisplay.jsx file
const analysisDisplayPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisDisplay.jsx');

// Function to fix the missing imports
function fixMissingImports() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisDisplayPath, 'utf8');
    
    // Add the missing imports
    const importStatement = `import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ANALYSIS_STEPS, PROGRESS_STAGES } from '@/lib/search-styles';
import { AnalysisFormatter } from './AnalysisFormatter';`;
    
    // Replace the existing import statements
    content = content.replace(/import React.*?;(\s*import .*?;)*/, importStatement);
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisDisplayPath, content, 'utf8');
    console.log('Successfully fixed missing imports in AnalysisDisplay.jsx');
    return true;
  } catch (error) {
    console.error('Error fixing missing imports in AnalysisDisplay.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Fix missing imports
    const importsFixed = fixMissingImports();
    
    if (importsFixed) {
      console.log('Missing imports fixed successfully!');
    } else {
      console.error('Failed to fix missing imports.');
    }
  } catch (error) {
    console.error('Error applying fix:', error);
  }
}

// Run the fix
applyFix();
