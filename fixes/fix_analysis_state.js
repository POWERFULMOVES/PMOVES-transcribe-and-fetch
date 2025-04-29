/**
 * Fix for missing analysis state variables
 * This script addresses the "setOpenAIAnalysisReceived is not defined" error
 */

const fs = require('fs');
const path = require('path');

// Path to the vector-search page.js file
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Function to update the vector-search page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix: Add the missing state variables
    // Look for the openAIAnalysis and groqAnalysis state declarations
    content = content.replace(
      /const \[openaiAnalysis, setOpenAIAnalysis\] = useState\(''\);/,
      `const [openaiAnalysis, setOpenAIAnalysis] = useState('');
    const [openAIAnalysisReceived, setOpenAIAnalysisReceived] = useState(false);`
    );
    
    content = content.replace(
      /const \[groqAnalysis, setGroqAnalysis\] = useState\(''\);/,
      `const [groqAnalysis, setGroqAnalysis] = useState('');
    const [groqAnalysisReceived, setGroqAnalysisReceived] = useState(false);`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with missing state variables');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    if (pageUpdated) {
      console.log('Analysis state fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Added missing state variables for openAIAnalysisReceived and groqAnalysisReceived');
      console.log('2. Fixed "setOpenAIAnalysisReceived is not defined" error');
    } else {
      console.error('Failed to apply analysis state fix.');
    }
  } catch (error) {
    console.error('Error applying analysis state fix:', error);
  }
}

// Run the fix
applyFix();
