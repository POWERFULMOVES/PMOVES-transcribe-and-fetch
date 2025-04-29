/**
 * Fix for analysis flags issues
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
    
    // Fix: Ensure analysis flags are properly initialized and only used when runAnalysis is true
    content = content.replace(
      /const handleSearch = useCallback\(\(\) => \{([\s\S]*?)\/\/ Reset analysis received flags([\s\S]*?)setLoading\(true\);/m,
      `const handleSearch = useCallback(() => {$1
        // Only reset analysis flags if analysis is enabled
        if (runAnalysis) {
            // Reset analysis received flags
            setOpenAIAnalysisReceived(false);
            setGroqAnalysisReceived(false);
        }
        setLoading(true);`
    );
    
    // Fix: Update the analysis case to check if runAnalysis is true before using the flags
    content = content.replace(
      /case 'analysis':([\s\S]*?)if \(data\.metadata\?\.provider === 'openai'\) \{([\s\S]*?)\/\/ Only set if not already received to prevent loops([\s\S]*?)if \(!openAIAnalysisReceived\) \{([\s\S]*?)\} else \{([\s\S]*?)\}([\s\S]*?)\} else if \(data\.metadata\?\.provider === 'groq'\) \{([\s\S]*?)\/\/ Only set if not already received to prevent loops([\s\S]*?)if \(!groqAnalysisReceived\) \{([\s\S]*?)\} else \{([\s\S]*?)\}([\s\S]*?)\}/m,
      `case 'analysis':
                        // Analysis results
                        console.log('Received analysis from provider:', data.metadata?.provider);
                        if (data.metadata?.provider === 'openai') {
                            if (runAnalysis) {
                                // Only set if not already received to prevent loops
                                if (!openAIAnalysisReceived) {
                                    setOpenAIAnalysis(data.content || '');
                                    setOpenAIAnalysisReceived(true);
                                    console.log('OpenAI analysis set, marked as received');
                                } else {
                                    console.log('Ignoring duplicate OpenAI analysis');
                                }
                            } else {
                                // If analysis is not enabled, just set the content
                                setOpenAIAnalysis(data.content || '');
                                console.log('OpenAI analysis set (analysis tracking disabled)');
                            }
                        } else if (data.metadata?.provider === 'groq') {
                            if (runAnalysis) {
                                // Only set if not already received to prevent loops
                                if (!groqAnalysisReceived) {
                                    setGroqAnalysis(data.content || '');
                                    setGroqAnalysisReceived(true);
                                    console.log('Groq analysis set, marked as received');
                                } else {
                                    console.log('Ignoring duplicate Groq analysis');
                                }
                            } else {
                                // If analysis is not enabled, just set the content
                                setGroqAnalysis(data.content || '');
                                console.log('Groq analysis set (analysis tracking disabled)');
                            }
                        }`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with analysis flags fix');
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
      console.log('Analysis flags fix applied successfully!');
      console.log('Fixed:');
      console.log('1. "setOpenAIAnalysisReceived is not defined" error when analysis is not selected');
      console.log('2. Improved handling of analysis flags based on runAnalysis state');
    } else {
      console.error('Failed to apply analysis flags fix.');
    }
  } catch (error) {
    console.error('Error applying analysis flags fix:', error);
  }
}

// Run the fix
applyFix();
