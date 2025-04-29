/**
 * Fix for analysis flags issues (version 2)
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
    
    // Fix 1: Ensure the state variables are properly defined
    // Look for the useState declarations for openAIAnalysis and groqAnalysis
    content = content.replace(
      /const \[openAIAnalysis, setOpenAIAnalysis\] = useState\(''\);([\s\S]*?)const \[groqAnalysis, setGroqAnalysis\] = useState\(''\);/m,
      `const [openAIAnalysis, setOpenAIAnalysis] = useState('');
    const [openAIAnalysisReceived, setOpenAIAnalysisReceived] = useState(false);$1const [groqAnalysis, setGroqAnalysis] = useState('');
    const [groqAnalysisReceived, setGroqAnalysisReceived] = useState(false);`
    );
    
    // Fix 2: Modify the handleSearch function to conditionally reset the flags
    content = content.replace(
      /const handleSearch = useCallback\(\(\) => \{([\s\S]*?)setLoading\(true\);/m,
      `const handleSearch = useCallback(() => {$1
        // Reset analysis received flags
        setOpenAIAnalysisReceived(false);
        setGroqAnalysisReceived(false);
        setLoading(true);`
    );
    
    // Fix 3: Update the analysis case to handle the flags properly
    content = content.replace(
      /case 'analysis':([\s\S]*?)if \(data\.metadata\?\.provider === 'openai'\) \{([\s\S]*?)setOpenAIAnalysis\(data\.content \|\| ''\);([\s\S]*?)\} else if \(data\.metadata\?\.provider === 'groq'\) \{([\s\S]*?)setGroqAnalysis\(data\.content \|\| ''\);([\s\S]*?)\}/m,
      `case 'analysis':
                        // Analysis results
                        console.log('Received analysis from provider:', data.metadata?.provider);
                        if (data.metadata?.provider === 'openai') {
                            // Only set if not already received to prevent loops
                            if (!openAIAnalysisReceived) {
                                setOpenAIAnalysis(data.content || '');
                                setOpenAIAnalysisReceived(true);
                                console.log('OpenAI analysis set, marked as received');
                            } else {
                                console.log('Ignoring duplicate OpenAI analysis');
                            }
                        } else if (data.metadata?.provider === 'groq') {
                            // Only set if not already received to prevent loops
                            if (!groqAnalysisReceived) {
                                setGroqAnalysis(data.content || '');
                                setGroqAnalysisReceived(true);
                                console.log('Groq analysis set, marked as received');
                            } else {
                                console.log('Ignoring duplicate Groq analysis');
                            }
                        }`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with analysis flags fix v2');
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
      console.log('Analysis flags fix v2 applied successfully!');
      console.log('Fixed:');
      console.log('1. Added missing state variables for analysis flags');
      console.log('2. Fixed "setOpenAIAnalysisReceived is not defined" error');
      console.log('3. Improved handling of analysis flags');
    } else {
      console.error('Failed to apply analysis flags fix v2.');
    }
  } catch (error) {
    console.error('Error applying analysis flags fix v2:', error);
  }
}

// Run the fix
applyFix();
