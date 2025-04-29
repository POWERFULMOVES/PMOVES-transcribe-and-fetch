/**
 * Fix for duplicate state variable declarations and code blocks
 * This script addresses the compilation errors in vector-search/page.js
 */

const fs = require('fs');
const path = require('path');

// Path to the vector-search page.js file
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Function to update the vector-search page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Remove duplicate state variable declarations
    content = content.replace(
      /const \[openAIAnalysisReceived, setOpenAIAnalysisReceived\] = useState\(false\);\s+const \[openAIAnalysisReceived, setOpenAIAnalysisReceived\] = useState\(false\);/g,
      `const [openAIAnalysisReceived, setOpenAIAnalysisReceived] = useState(false);`
    );
    
    content = content.replace(
      /const \[groqAnalysisReceived, setGroqAnalysisReceived\] = useState\(false\);\s+const \[groqAnalysisReceived, setGroqAnalysisReceived\] = useState\(false\);/g,
      `const [groqAnalysisReceived, setGroqAnalysisReceived] = useState(false);`
    );
    
    // Fix 2: Remove duplicate "Close any existing EventSource" blocks
    content = content.replace(
      /\/\/ Close any existing EventSource before creating a new one\s+if \(eventSource\) \{\s+console\.log\("Closing existing SSE connection before creating a new one"\);\s+eventSource\.close\(\);\s+setEventSource\(null\);\s+\}\s+\s+\/\/ Close any existing EventSource before creating a new one\s+if \(eventSource\) \{\s+console\.log\("Closing existing SSE connection before creating a new one"\);\s+eventSource\.close\(\);\s+setEventSource\(null\);\s+\}/g,
      `// Close any existing EventSource before creating a new one
        if (eventSource) {
            console.log("Closing existing SSE connection before creating a new one");
            eventSource.close();
            setEventSource(null);
        }`
    );
    
    // Fix 3: Remove duplicate "Update metadata if provided" blocks
    content = content.replace(
      /\/\/ Update metadata if provided\s+if \(data\.metadata\) \{\s+setMetadata\(prevMetadata => \(\{\s+\.\.\.prevMetadata,\s+\.\.\.data\.metadata\s+\}\)\);\s+\}\s+\s+\/\/ Update metadata if provided\s+if \(data\.metadata\) \{\s+setMetadata\(prevMetadata => \(\{\s+\.\.\.prevMetadata,\s+\.\.\.data\.metadata\s+\}\)\);\s+\}\s+\s+\/\/ Update metadata if provided\s+if \(data\.metadata\) \{\s+setMetadata\(prevMetadata => \(\{\s+\.\.\.prevMetadata,\s+\.\.\.data\.metadata\s+\}\)\);\s+\}/g,
      `// Update metadata if provided
                        if (data.metadata) {
                            setMetadata(prevMetadata => ({
                                ...prevMetadata,
                                ...data.metadata
                            }));
                        }`
    );
    
    // Fix 4: Remove duplicate setEventSource(null) calls in cleanup function
    content = content.replace(
      /newEventSource\.close\(\);\s+setEventSource\(null\);\s+setEventSource\(null\);/g,
      `newEventSource.close();
                setEventSource(null);`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with fixes for duplicate declarations');
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
      console.log('Duplicate declarations fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Removed duplicate state variable declarations for openAIAnalysisReceived and groqAnalysisReceived');
      console.log('2. Removed duplicate "Close any existing EventSource" blocks');
      console.log('3. Removed duplicate "Update metadata if provided" blocks');
      console.log('4. Removed duplicate setEventSource(null) calls in cleanup function');
    } else {
      console.error('Failed to apply duplicate declarations fix.');
    }
  } catch (error) {
    console.error('Error applying duplicate declarations fix:', error);
  }
}

// Run the fix
applyFix();
