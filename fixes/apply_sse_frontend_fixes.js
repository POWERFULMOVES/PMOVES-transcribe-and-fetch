/**
 * apply_sse_frontend_fixes.js - Apply SSE frontend fixes
 * 
 * This script applies the fixes for SSE JSON parsing issues in the frontend.
 * It updates the onMessage handler in page.js and the parseMessage function in useSSE.js.
 */

const fs = require('fs');
const path = require('path');
const { fixedOnMessageHandler, fixedParseMessage } = require('./fix_sse_frontend');

// Paths to the files we need to modify
const pageJsPath = path.join(__dirname, 'src', 'app', 'page.js');
const useSSEPath = path.join(__dirname, 'src', 'hooks', 'useSSE.js');

// Create backup of files before modifying
function createBackup(filePath) {
  const backupPath = `${filePath}.bak.${new Date().toISOString().replace(/:/g, '-')}`;
  fs.copyFileSync(filePath, backupPath);
  console.log(`Created backup: ${backupPath}`);
  return backupPath;
}

// Apply fix to page.js
function fixPageJs() {
  console.log(`Fixing ${pageJsPath}...`);
  
  try {
    // Create backup
    createBackup(pageJsPath);
    
    // Read the file
    let content = fs.readFileSync(pageJsPath, 'utf8');
    
    // Find the onMessage handler
    const onMessageRegex = /onMessage:\s*\(data\)\s*=>\s*\{[\s\S]*?(?=onError:|},\s*onError:)/;
    const match = content.match(onMessageRegex);
    
    if (!match) {
      console.error('Could not find onMessage handler in page.js');
      return false;
    }
    
    // Replace the onMessage handler
    content = content.replace(onMessageRegex, fixedOnMessageHandler);
    
    // Write the updated content
    fs.writeFileSync(pageJsPath, content, 'utf8');
    
    console.log(`✅ Successfully updated onMessage handler in ${pageJsPath}`);
    return true;
  } catch (error) {
    console.error(`Error fixing ${pageJsPath}:`, error);
    return false;
  }
}

// Apply fix to useSSE.js
function fixUseSSE() {
  console.log(`Fixing ${useSSEPath}...`);
  
  try {
    // Create backup
    createBackup(useSSEPath);
    
    // Read the file
    let content = fs.readFileSync(useSSEPath, 'utf8');
    
    // Find the parseMessage function
    const parseMessageRegex = /\/\/\s*Parse SSE message data consistently[\s\S]*?const parseMessage[\s\S]*?}\s*\}\s*,\s*\[\]\);/;
    const match = content.match(parseMessageRegex);
    
    if (!match) {
      console.error('Could not find parseMessage function in useSSE.js');
      return false;
    }
    
    // Replace the parseMessage function
    content = content.replace(parseMessageRegex, fixedParseMessage);
    
    // Write the updated content
    fs.writeFileSync(useSSEPath, content, 'utf8');
    
    console.log(`✅ Successfully updated parseMessage function in ${useSSEPath}`);
    return true;
  } catch (error) {
    console.error(`Error fixing ${useSSEPath}:`, error);
    return false;
  }
}

// Main function
function main() {
  console.log('Applying SSE frontend fixes...');
  
  const pageJsFixed = fixPageJs();
  const useSSEFixed = fixUseSSE();
  
  if (pageJsFixed && useSSEFixed) {
    console.log('\n✅ All fixes applied successfully!');
    console.log('\nYou can now restart the frontend to see the changes in action.');
  } else {
    console.log('\n❌ Some fixes could not be applied. Please check the logs above.');
  }
}

// Run the script
main();
