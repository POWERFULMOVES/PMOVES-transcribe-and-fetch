/**
 * Script to fix the unicode escape error in AnalysisFormatter.jsx
 */

const fs = require('fs');
const path = require('path');

// Path to the AnalysisFormatter.jsx file
const analysisFormatterPath = path.join(process.cwd(), 'src', 'components', 'search', 'AnalysisFormatter.jsx');

// Function to fix the unicode escape error
function fixUnicodeEscape() {
  try {
    // Read the current content of the file
    let content = fs.readFileSync(analysisFormatterPath, 'utf8');
    
    // Find and fix the problematic YouTube link regex
    // The issue is likely with the backslash in the regex pattern
    
    // Replace the problematic line with a fixed version
    content = content.replace(
      /processedHtml = processedHtml\.replace\(\/🎬https:\/\/www\.youtube\.com\/watch\\\?v=\(\[^&\\\\s\]\+\)\/g,/g,
      `processedHtml = processedHtml.replace(/🎬https:\\/\\/www\\.youtube\\.com\\/watch\\?v=([^&\\s]+)/g,`
    );
    
    // Also fix any other potential YouTube link regex issues
    content = content.replace(
      /https:\/\/www\.youtube\.com\/watch\\\?v=/g,
      `https://www.youtube.com/watch?v=`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(analysisFormatterPath, content, 'utf8');
    console.log('Successfully fixed unicode escape error in AnalysisFormatter.jsx');
    return true;
  } catch (error) {
    console.error('Error fixing unicode escape error in AnalysisFormatter.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Fix unicode escape error
    const escapeFixed = fixUnicodeEscape();
    
    if (escapeFixed) {
      console.log('Unicode escape error fixed successfully!');
    } else {
      console.error('Failed to fix unicode escape error.');
    }
  } catch (error) {
    console.error('Error applying fix:', error);
  }
}

// Run the fix
applyFix();
