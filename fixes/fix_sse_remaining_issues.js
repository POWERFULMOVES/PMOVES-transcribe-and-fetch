/**
 * Fix for remaining SSE issues
 * This script addresses:
 * 1. Duplicate keys in search results
 * 2. SSE connection errors after search completion
 * 3. Analysis loop not stopping when complete
 */

const fs = require('fs');
const path = require('path');

// Path to the vector-search page.js file
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Path to the SearchResultCard.jsx file
const searchResultCardPath = path.join(process.cwd(), 'src', 'components', 'search', 'SearchResultCard.jsx');

// Function to update the vector-search page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Ensure EventSource is properly closed after search completion
    content = content.replace(
      /case 'complete':([\s\S]*?)setLoading\(false\);([\s\S]*?)break;/m,
      `case 'complete':
                        // Search process complete
                        console.log('Search process complete');
                        setCurrentStage('complete');
                        setLoading(false);
                        
                        // Ensure metadata has the required flags
                        setMetadata(prevMetadata => ({
                            ...prevMetadata,
                            search_complete: true
                        }));
                        
                        // Close the EventSource to prevent connection errors
                        if (eventSource) {
                            console.log('Closing SSE connection after search completion');
                            eventSource.close();
                            setEventSource(null);
                        }
                        break;`
    );
    
    // Fix 2: Prevent analysis loop by adding a flag to track if analysis has been received
    content = content.replace(
      /const \[openAIAnalysis, setOpenAIAnalysis\] = useState\(''\);([\s\S]*?)const \[groqAnalysis, setGroqAnalysis\] = useState\(''\);/m,
      `const [openAIAnalysis, setOpenAIAnalysis] = useState('');
    const [openAIAnalysisReceived, setOpenAIAnalysisReceived] = useState(false);$1const [groqAnalysis, setGroqAnalysis] = useState('');
    const [groqAnalysisReceived, setGroqAnalysisReceived] = useState(false);`
    );
    
    // Update the analysis case to track received analyses
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
    
    // Reset analysis received flags when starting a new search
    content = content.replace(
      /const handleSearch = useCallback\(\(\) => \{([\s\S]*?)setLoading\(true\);/m,
      `const handleSearch = useCallback(() => {$1
        // Reset analysis received flags
        setOpenAIAnalysisReceived(false);
        setGroqAnalysisReceived(false);
        setLoading(true);`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Function to update the SearchResultCard.jsx file to fix duplicate keys
function updateSearchResultCard() {
  try {
    let content = fs.readFileSync(searchResultCardPath, 'utf8');
    
    // Fix: Add index to key to ensure uniqueness
    content = content.replace(
      /key=\{result\.id\}/g,
      'key={`${result.id}_${index}`}'
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(searchResultCardPath, content, 'utf8');
    console.log('Successfully updated SearchResultCard.jsx');
    return true;
  } catch (error) {
    console.error('Error updating SearchResultCard.jsx:', error);
    return false;
  }
}

// Main function to apply all fixes
async function applyFixes() {
  try {
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    // Update SearchResultCard.jsx
    const cardUpdated = updateSearchResultCard();
    
    if (pageUpdated && cardUpdated) {
      console.log('All remaining SSE issues fixed successfully!');
      console.log('Fixed:');
      console.log('1. Duplicate keys in search results');
      console.log('2. SSE connection errors after search completion');
      console.log('3. Analysis loop not stopping when complete');
    } else {
      console.error('Failed to apply some fixes.');
    }
  } catch (error) {
    console.error('Error applying fixes:', error);
  }
}

// Run the fix
applyFixes();
