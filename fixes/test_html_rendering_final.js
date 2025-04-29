/**
 * Test Script for HTML Rendering and Animation Fixes
 * 
 * This script tests the fixes implemented for:
 * 1. Analysis formatting using react-markdown
 * 2. Animation state management in SearchFlow
 * 3. SSE handling and state management in vector-search/page.js
 */

const fs = require('fs');
const path = require('path');

// Paths to the files we need to test
const ANALYSIS_FORMATTER_PATH = path.join('src', 'components', 'search', 'AnalysisFormatter.jsx');
const SEARCH_FLOW_PATH = path.join('src', 'components', 'search', 'SearchFlow.jsx');
const VECTOR_SEARCH_PATH = path.join('src', 'app', 'vector-search', 'page.js');

// Test data for analysis formatting
const TEST_MARKDOWN = `
# Test Heading 1

## Test Heading 2

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
- List item 3

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3

> This is a blockquote

\`\`\`
This is a code block
\`\`\`

This is a [link](https://example.com)

This is a YouTube link: https://www.youtube.com/watch?v=dQw4w9WgXcQ

This is "quoted text" that should be highlighted.
`;

// Function to check if a file contains specific patterns
function checkFileForPatterns(filePath, patterns) {
  try {
    // Check if the file exists
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at ${filePath}`);
      return false;
    }

    // Read the file content
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Check each pattern
    const results = patterns.map(pattern => {
      const regex = new RegExp(pattern.regex);
      const matches = content.match(regex);
      return {
        name: pattern.name,
        found: !!matches,
        count: matches ? matches.length : 0
      };
    });
    
    return results;
  } catch (error) {
    console.error(`Error checking file ${filePath}:`, error);
    return false;
  }
}

// Main function to run all tests
async function runTests() {
  console.log('Starting tests for HTML rendering and animation fixes...');
  
  // Test AnalysisFormatter.jsx
  console.log('\nTesting AnalysisFormatter.jsx...');
  const analysisFormatterPatterns = [
    { name: 'ReactMarkdown import', regex: 'import ReactMarkdown from' },
    { name: 'MarkdownFormatter component', regex: 'function MarkdownFormatter' },
    { name: 'Custom components for react-markdown', regex: 'components\\s*=' },
    { name: 'YouTube link handling', regex: 'isYouTubeLink' },
    { name: 'CSS class formatter', regex: 'function CssClassFormatter' }
  ];
  
  const analysisFormatterResults = checkFileForPatterns(ANALYSIS_FORMATTER_PATH, analysisFormatterPatterns);
  
  if (analysisFormatterResults) {
    console.log('Results:');
    analysisFormatterResults.forEach(result => {
      console.log(`  - ${result.name}: ${result.found ? '✅ Found' : '❌ Not found'} (${result.count} matches)`);
    });
    
    const allFound = analysisFormatterResults.every(result => result.found);
    console.log(`Overall: ${allFound ? '✅ All patterns found' : '❌ Some patterns missing'}`);
  }
  
  // Test SearchFlow.jsx
  console.log('\nTesting SearchFlow.jsx...');
  const searchFlowPatterns = [
    { name: 'Animation state', regex: '\\[animateIn, setAnimateIn\\]' },
    { name: 'Stage change detection', regex: 'stageChanged' },
    { name: 'Functional component with props', regex: 'export function SearchFlowIndicator' },
    { name: 'Progress visualization', regex: 'Progress line with animation' },
    { name: 'Visibility class', regex: 'visibilityClass' }
  ];
  
  const searchFlowResults = checkFileForPatterns(SEARCH_FLOW_PATH, searchFlowPatterns);
  
  if (searchFlowResults) {
    console.log('Results:');
    searchFlowResults.forEach(result => {
      console.log(`  - ${result.name}: ${result.found ? '✅ Found' : '❌ Not found'} (${result.count} matches)`);
    });
    
    const allFound = searchFlowResults.every(result => result.found);
    console.log(`Overall: ${allFound ? '✅ All patterns found' : '❌ Some patterns missing'}`);
  }
  
  // Test vector-search/page.js
  console.log('\nTesting vector-search/page.js...');
  const vectorSearchPatterns = [
    { name: 'Functional state updates', regex: 'prevMetadata =>' },
    { name: 'SSE connection handling', regex: 'createSafeEventSource' },
    { name: 'Analysis completion detection', regex: 'analysis_complete' },
    { name: 'Error handling', regex: 'setError\\(' },
    { name: 'Loading state management', regex: 'setLoading\\(' },
    { name: 'SearchResultsTable component', regex: '<SearchResultsTable' },
    { name: 'SearchResultCard component', regex: '<SearchResultCard' }
  ];
  
  const vectorSearchResults = checkFileForPatterns(VECTOR_SEARCH_PATH, vectorSearchPatterns);
  
  if (vectorSearchResults) {
    console.log('Results:');
    vectorSearchResults.forEach(result => {
      console.log(`  - ${result.name}: ${result.found ? '✅ Found' : '❌ Not found'} (${result.count} matches)`);
    });
    
    const allFound = vectorSearchResults.every(result => result.found);
    console.log(`Overall: ${allFound ? '✅ All patterns found' : '❌ Some patterns missing'}`);
  }
  
  // Overall test results
  console.log('\nOverall Test Results:');
  const allTests = [
    { name: 'AnalysisFormatter.jsx', results: analysisFormatterResults },
    { name: 'SearchFlow.jsx', results: searchFlowResults },
    { name: 'vector-search/page.js', results: vectorSearchResults }
  ];
  
  let allPassed = true;
  
  allTests.forEach(test => {
    if (test.results) {
      const passed = test.results.every(result => result.found);
      console.log(`  - ${test.name}: ${passed ? '✅ PASSED' : '❌ FAILED'}`);
      if (!passed) allPassed = false;
    } else {
      console.log(`  - ${test.name}: ❌ TEST ERROR`);
      allPassed = false;
    }
  });
  
  console.log(`\nFinal Result: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  
  if (allPassed) {
    console.log('\nAll fixes have been successfully implemented and verified!');
    console.log('You can now run the apply_all_fixes.js script to apply these fixes to your project.');
  } else {
    console.log('\nSome fixes may not be properly implemented. Please review the test results above.');
  }
}

// Run the tests
runTests().catch(error => {
  console.error('An error occurred while running tests:', error);
});
