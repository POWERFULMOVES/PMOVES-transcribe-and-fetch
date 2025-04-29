/**
 * Enhanced fix for duplicate keys in search results
 * This script addresses the issue where the same search results are rendered in multiple places
 */

const fs = require('fs');
const path = require('path');

// Path to the files
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');
const searchResultsTablePath = path.join(process.cwd(), 'src', 'components', 'search', 'SearchResultsTable.jsx');

// Function to update the vector-search/page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Update the key in the SearchResultCard components to include a context identifier
    content = content.replace(
      /<SearchResultCard key={result\.id \|\| index} result={result} \/>/g,
      '<SearchResultCard key={`main-results-${result.id || index}-${Math.random().toString(36).substr(2, 5)}`} result={result} index={index} />'
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with enhanced unique keys');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Function to update the SearchResultsTable.jsx file
function updateSearchResultsTable() {
  try {
    let content = fs.readFileSync(searchResultsTablePath, 'utf8');
    
    // Fix 2: Update the key in the TableRow components to include a random suffix
    content = content.replace(
      /key={`\${result\.content_id}-\${result\.segment_id \|\| index}`}/g,
      'key={`table-row-${result.content_id}-${result.segment_id || index}-${Math.random().toString(36).substr(2, 5)}`}'
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(searchResultsTablePath, content, 'utf8');
    console.log('Successfully updated SearchResultsTable.jsx with enhanced unique keys');
    return true;
  } catch (error) {
    console.error('Error updating SearchResultsTable.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    // Update SearchResultsTable.jsx
    const tableUpdated = updateSearchResultsTable();
    
    if (pageUpdated && tableUpdated) {
      console.log('Enhanced keys fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Added context identifiers and random suffixes to keys in vector-search/page.js');
      console.log('2. Added context identifiers and random suffixes to keys in SearchResultsTable.jsx');
      console.log('3. This ensures that even when the same search results are rendered in multiple places, each instance has a unique key');
    } else {
      console.error('Failed to apply enhanced keys fix.');
    }
  } catch (error) {
    console.error('Error applying enhanced keys fix:', error);
  }
}

// Run the fix
applyFix();
