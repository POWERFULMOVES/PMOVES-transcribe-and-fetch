/**
 * Fix for duplicate keys in search results
 * This script addresses the "Encountered two children with the same key" error
 */

const fs = require('fs');
const path = require('path');

// Path to the file that renders the search results
const searchResultsPath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Function to update the search results rendering
function updateSearchResults() {
  try {
    let content = fs.readFileSync(searchResultsPath, 'utf8');
    
    // Fix: Update the results mapping to include index in the key
    content = content.replace(
      /{results.length > 0 \? results.map\(\(result\) => \(/g,
      '{results.length > 0 ? results.map((result, index) => ('
    );
    
    content = content.replace(
      /<SearchResultCard key={result.id} result={result} \/>/g,
      '<SearchResultCard key={`${result.id}_${index}`} result={result} index={index} />'
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(searchResultsPath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with unique keys');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update search results rendering
    const resultsUpdated = updateSearchResults();
    
    if (resultsUpdated) {
      console.log('Duplicate keys fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Added unique keys to search result components using both ID and index');
      console.log('2. Fixed "Encountered two children with the same key" error');
    } else {
      console.error('Failed to apply duplicate keys fix.');
    }
  } catch (error) {
    console.error('Error applying duplicate keys fix:', error);
  }
}

// Run the fix
applyFix();
