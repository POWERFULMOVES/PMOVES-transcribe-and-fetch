/**
 * Apply Transcription Fixes
 * 
 * This script applies the fixes for the transcription delay issue.
 * It modifies the following files:
 * 1. src/hooks/useSSE.js
 * 2. src/app/page.js
 * 3. src/app/reducers/transcriptionReducer.js
 */

// Import the fixes
const { parseMessage, onMessage, reducer, connectionCleanup, onProcessVideo } = TranscriptionDelayFix;

// Apply fixes to useSSE.js
async function fixUseSSE() {
  try {
    // Get the current content
    const response = await fetch('src/hooks/useSSE.js');
    let content = await response.text();
    
    // Replace parseMessage implementation
    content = content.replace(
      /\/\/ Parse SSE message data consistently[\s\S]*?const parseMessage = useCallback\(\(data\) => \{[\s\S]*?\}, \[\]\);/,
      parseMessage
    );
    
    // Replace disconnect and cleanup implementation
    content = content.replace(
      /\/\/ Disconnect from SSE endpoint[\s\S]*?const disconnect = useCallback\(\) => \{[\s\S]*?\}, \[endpoint\]\);/,
      connectionCleanup
    );
    
    // Save the modified file
    const blob = new Blob([content], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = 'useSSE.fixed.js';
    a.click();
    
    console.log('useSSE.js fixes applied and saved to useSSE.fixed.js');
    return true;
  } catch (error) {
    console.error('Error fixing useSSE.js:', error);
    return false;
  }
}

// Apply fixes to page.js
async function fixPageJs() {
  try {
    // Get the current content
    const response = await fetch('src/app/page.js');
    let content = await response.text();
    
    // Add message buffer implementation before the useSSE hook
    const sseHookPattern = /\/\/ --- SSE Hook Setup ---[\s\S]*?const \{[\s\S]*?\} = useSSE/;
    content = content.replace(
      sseHookPattern,
      onMessage + '\n\n  // --- SSE Hook Setup ---\n  const {'
    );
    
    // Replace onProcessVideo implementation
    content = content.replace(
      /\/\/ Handle Process Video Request[\s\S]*?const onProcessVideo = async \(\) => \{[\s\S]*?try \{[\s\S]*?\} catch \(error\) \{[\s\S]*?\}/,
      onProcessVideo
    );
    
    // Save the modified file
    const blob = new Blob([content], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = 'page.fixed.js';
    a.click();
    
    console.log('page.js fixes applied and saved to page.fixed.js');
    return true;
  } catch (error) {
    console.error('Error fixing page.js:', error);
    return false;
  }
}

// Apply fixes to transcriptionReducer.js
async function fixReducer() {
  try {
    // Get the current content
    const response = await fetch('src/app/reducers/transcriptionReducer.js');
    let content = await response.text();
    
    // Replace ADD_TRANSCRIPTION_SEGMENT case
    content = content.replace(
      /case ACTIONS\.ADD_TRANSCRIPTION_SEGMENT:[\s\S]*?return \{[\s\S]*?transcriptionSegments:[\s\S]*?\};/,
      reducer
    );
    
    // Save the modified file
    const blob = new Blob([content], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcriptionReducer.fixed.js';
    a.click();
    
    console.log('transcriptionReducer.js fixes applied and saved to transcriptionReducer.fixed.js');
    return true;
  } catch (error) {
    console.error('Error fixing transcriptionReducer.js:', error);
    return false;
  }
}

// Apply all fixes
async function applyAllFixes() {
  console.log('Applying all transcription fixes...');
  
  const useSSEFixed = await fixUseSSE();
  const pageFixed = await fixPageJs();
  const reducerFixed = await fixReducer();
  
  if (useSSEFixed && pageFixed && reducerFixed) {
    console.log('All fixes applied successfully!');
    console.log('Please review the fixed files and apply them to your codebase.');
  } else {
    console.error('Some fixes failed to apply. Please check the console for errors.');
  }
}

// Make available in global scope for console use
window.applyTranscriptionFixes = {
  fixUseSSE,
  fixPageJs,
  fixReducer,
  applyAllFixes
};
