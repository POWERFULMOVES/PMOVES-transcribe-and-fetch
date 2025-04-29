/**
 * Fix for SSE connection issues and stage updates
 * This script addresses the SSE connection errors and stage update issues
 */

const fs = require('fs');
const path = require('path');

// Path to the vector-search page.js file
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');

// Function to update the vector-search page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Update the newEventSource variable to properly close the existing EventSource
    content = content.replace(
      /const newEventSource = createSafeEventSource\(/g,
      `// Close any existing EventSource before creating a new one
        if (eventSource) {
            console.log("Closing existing SSE connection before creating a new one");
            eventSource.close();
            setEventSource(null);
        }
        
        const newEventSource = createSafeEventSource(`
    );
    
    // Fix 2: Update the stage handling in the switch statement
    content = content.replace(
      /case 'status':([\s\S]*?)if \(data\.metadata\?\.stage\) \{([\s\S]*?)console\.log\('Updating stage to:', data\.metadata\.stage\);([\s\S]*?)setCurrentStage\(data\.metadata\.stage\);([\s\S]*?)\}/m,
      `case 'status':
                        // Update search flow stage based on status
                        if (data.metadata?.stage) {
                            console.log('Updating stage to:', data.metadata.stage);
                            // Ensure we update the stage state immediately
                            setCurrentStage(data.metadata.stage);
                        }
                        
                        // Update metadata if provided
                        if (data.metadata) {
                            setMetadata(prevMetadata => ({
                                ...prevMetadata,
                                ...data.metadata
                            }));
                        }`
    );
    
    // Fix 3: Ensure the EventSource is properly closed in the cleanup function
    content = content.replace(
      /return \(\) => \{([\s\S]*?)if \(newEventSource\) \{([\s\S]*?)console\.log\("Closing SSE connection"\);([\s\S]*?)newEventSource\.close\(\);([\s\S]*?)\}([\s\S]*?)\};/m,
      `return () => {$1if (newEventSource) {$2console.log("Closing SSE connection");$3newEventSource.close();
                setEventSource(null);$4}$5};`
    );
    
    // Fix 4: Update the SearchFlowIndicator component usage to properly handle stage updates
    content = content.replace(
      /<SearchFlowIndicator ([\s\S]*?)currentStage={metadata\?\.search_complete \? 'complete' : 'search'} ([\s\S]*?)\/>/m,
      `<SearchFlowIndicator $1currentStage={currentStage} $2/>`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with SSE connection fixes');
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
      console.log('SSE connection fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Properly closed EventSource before creating a new one');
      console.log('2. Improved stage update handling in the switch statement');
      console.log('3. Ensured EventSource is properly closed in the cleanup function');
      console.log('4. Updated SearchFlowIndicator to use currentStage directly');
    } else {
      console.error('Failed to apply SSE connection fix.');
    }
  } catch (error) {
    console.error('Error applying SSE connection fix:', error);
  }
}

// Run the fix
applyFix();
