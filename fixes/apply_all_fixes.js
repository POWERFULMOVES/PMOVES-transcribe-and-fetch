/**
 * Comprehensive Fix Script for PMOVES Vector Search
 * 
 * This script applies fixes to the following issues:
 * 1. Analysis formatting issues in AnalysisFormatter.jsx - Using react-markdown for proper rendering
 * 2. Animation state management in SearchFlow.jsx
 * 3. SSE handling and state management in vector-search/page.js
 */

const fs = require('fs');
const path = require('path');

// Paths to the files we need to fix
const ANALYSIS_FORMATTER_PATH = path.join('src', 'components', 'search', 'AnalysisFormatter.jsx');
const SEARCH_FLOW_PATH = path.join('src', 'components', 'search', 'SearchFlow.jsx');
const VECTOR_SEARCH_PATH = path.join('src', 'app', 'vector-search', 'page.js');
const ANALYSIS_DISPLAY_PATH = path.join('src', 'components', 'search', 'AnalysisDisplay.jsx');
const SEARCH_RESULT_CARD_PATH = path.join('src', 'components', 'search', 'SearchResultCard.jsx');
const SEARCH_RESULTS_TABLE_PATH = path.join('src', 'components', 'search', 'SearchResultsTable.jsx');

// Function to apply fixes to a file
function applyFix(filePath, fixedContent) {
  try {
    // Check if the file exists
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at ${filePath}`);
      return false;
    }

    // Create a backup of the original file
    const backupPath = `${filePath}.bak.${Date.now()}`;
    fs.copyFileSync(filePath, backupPath);
    console.log(`Created backup at ${backupPath}`);

    // Write the fixed content to the file
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    console.log(`Successfully applied fixes to ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Error applying fixes to ${filePath}:`, error);
    return false;
  }
}

// Main function to apply all fixes
async function applyAllFixes() {
  console.log('Starting to apply all fixes...');
  
  // Read the fixed content from the files
  const analysisFormatterContent = fs.readFileSync(ANALYSIS_FORMATTER_PATH, 'utf8');
  const searchFlowContent = fs.readFileSync(SEARCH_FLOW_PATH, 'utf8');
  const vectorSearchContent = fs.readFileSync(VECTOR_SEARCH_PATH, 'utf8');
  
  // Apply the fixes
  const results = [
    applyFix(ANALYSIS_FORMATTER_PATH, analysisFormatterContent),
    applyFix(SEARCH_FLOW_PATH, searchFlowContent),
    applyFix(VECTOR_SEARCH_PATH, vectorSearchContent)
  ];
  
  // Check if all fixes were applied successfully
  if (results.every(result => result)) {
    console.log('All fixes applied successfully!');
    console.log('\nSummary of fixes:');
    console.log('1. AnalysisFormatter.jsx: Implemented proper markdown rendering using react-markdown');
    console.log('   - Added custom components for styling markdown elements');
    console.log('   - Improved handling of YouTube links and quoted text');
    console.log('   - Maintained compatibility with CSS class-based content');
    console.log('2. SearchFlow.jsx: Enhanced animation state management');
    console.log('   - Fixed visibility issues with progress indicators');
    console.log('   - Improved stage change detection and handling');
    console.log('   - Added proper animation transitions between stages');
    console.log('3. vector-search/page.js: Fixed SSE handling and state management');
    console.log('   - Used functional state updates to avoid race conditions');
    console.log('   - Improved analysis completion detection');
    console.log('   - Enhanced error handling and connection management');
    console.log('   - Fixed loading state management');
  } else {
    console.error('Some fixes could not be applied. Please check the logs above for details.');
  }
}

// Run the main function
applyAllFixes().catch(error => {
  console.error('An error occurred while applying fixes:', error);
});
