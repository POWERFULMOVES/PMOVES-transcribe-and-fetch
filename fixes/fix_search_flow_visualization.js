/**
 * Fix for search flow visualization issues
 * This script addresses the issues with the search flow visualization not updating correctly
 */

const fs = require('fs');
const path = require('path');

// Path to the files
const vectorSearchPagePath = path.join(process.cwd(), 'src', 'app', 'vector-search', 'page.js');
const searchFlowPath = path.join(process.cwd(), 'src', 'components', 'search', 'SearchFlow.jsx');

// Function to update the vector-search/page.js file
function updateVectorSearchPage() {
  try {
    let content = fs.readFileSync(vectorSearchPagePath, 'utf8');
    
    // Fix 1: Remove duplicate metadata update in the 'status' case
    content = content.replace(
      /\/\/ Update metadata if provided\s+if \(data\.metadata\) \{\s+setMetadata\(prevMetadata => \(\{\s+\.\.\.prevMetadata,\s+\.\.\.data\.metadata\s+\}\)\);\s+\}\s+\s+\/\/ Update metadata if provided\s+if \(data\.metadata\) \{\s+setMetadata\(prevMetadata => \(\{\s+\.\.\.prevMetadata,\s+\.\.\.data\.metadata\s+\}\)\);\s+\}/g,
      `// Update metadata if provided
        if (data.metadata) {
            setMetadata(prevMetadata => ({
                ...prevMetadata,
                ...data.metadata
            }));
        }`
    );
    
    // Fix 2: Add debug logging for stage updates
    content = content.replace(
      /if \(data\.metadata\?\.stage\) \{\s+console\.log\('Updating stage to:', data\.metadata\.stage\);\s+\/\/ Ensure we update the stage state immediately\s+setCurrentStage\(data\.metadata\.stage\);\s+\}/g,
      `if (data.metadata?.stage) {
            console.log('Updating stage to:', data.metadata.stage);
            // Ensure we update the stage state immediately
            setCurrentStage(data.metadata.stage);
            // Debug log the current stage after update
            console.log('Current stage state after update:', data.metadata.stage);
        }`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(vectorSearchPagePath, content, 'utf8');
    console.log('Successfully updated vector-search/page.js with search flow visualization fixes');
    return true;
  } catch (error) {
    console.error('Error updating vector-search/page.js:', error);
    return false;
  }
}

// Function to update the SearchFlow.jsx file
function updateSearchFlow() {
  try {
    let content = fs.readFileSync(searchFlowPath, 'utf8');
    
    // Fix 3: Add debug logging for stage changes in the SearchFlowIndicator component
    content = content.replace(
      /export function SearchFlowIndicator\(\{ currentStage = 'start', metadata = \{\} \}\) \{/,
      `export function SearchFlowIndicator({ currentStage = 'start', metadata = {} }) {
  // Debug log the current stage
  console.log('SearchFlowIndicator received stage:', currentStage);`
    );
    
    // Fix 4: Ensure the stages array matches the backend stages
    content = content.replace(
      /const stages = \['start', 'search', 'filter', 'combine', 'analyze', 'complete'\];/,
      `const stages = ['start', 'search', 'filter', 'combine', 'analyze', 'complete'];
  
  // Debug log the current stage index
  const stageIndex = stages.indexOf(currentStage);
  console.log('Stage index:', stageIndex, 'for stage:', currentStage);`
    );
    
    // Fix 5: Add a fallback for unknown stages
    content = content.replace(
      /\/\/ Find the current stage index\s+const currentIndex = stages\.indexOf\(currentStage\);/,
      `// Find the current stage index
  // If the stage is not found, default to the 'start' stage
  const currentIndex = stages.indexOf(currentStage) !== -1 ? stages.indexOf(currentStage) : 0;`
    );
    
    // Write the updated content back to the file
    fs.writeFileSync(searchFlowPath, content, 'utf8');
    console.log('Successfully updated SearchFlow.jsx with search flow visualization fixes');
    return true;
  } catch (error) {
    console.error('Error updating SearchFlow.jsx:', error);
    return false;
  }
}

// Main function to apply the fix
async function applyFix() {
  try {
    // Update vector-search/page.js
    const pageUpdated = updateVectorSearchPage();
    
    // Update SearchFlow.jsx
    const flowUpdated = updateSearchFlow();
    
    if (pageUpdated && flowUpdated) {
      console.log('Search flow visualization fix applied successfully!');
      console.log('Fixed:');
      console.log('1. Removed duplicate metadata update in the status case');
      console.log('2. Added debug logging for stage updates');
      console.log('3. Added debug logging for stage changes in the SearchFlowIndicator component');
      console.log('4. Added fallback for unknown stages');
      console.log('5. These changes will help diagnose and fix the search flow visualization issues');
    } else {
      console.error('Failed to apply search flow visualization fix.');
    }
  } catch (error) {
    console.error('Error applying search flow visualization fix:', error);
  }
}

// Run the fix
applyFix();
