/**
 * Apply SSE fixes to both frontend and backend
 * This script runs both the frontend and backend fixes
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Function to run a command and log the output
function runCommand(command) {
  console.log(`Running command: ${command}`);
  try {
    const output = execSync(command, { encoding: 'utf8' });
    console.log(output);
    return true;
  } catch (error) {
    console.error(`Error running command: ${command}`);
    console.error(error.message);
    return false;
  }
}

// Function to check if a file exists
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    console.error(`Error checking if file exists: ${filePath}`);
    console.error(error.message);
    return false;
  }
}

// Main function to apply all fixes
async function applyFixes() {
  console.log('Applying SSE fixes to both frontend and backend...');
  
  // Check if fix scripts exist
  const frontendFixPath = path.join(process.cwd(), 'fix_sse_frontend.js');
  const dataParsingFixPath = path.join(process.cwd(), 'fix_sse_data_parsing.js');
  const remainingIssuesFixPath = path.join(process.cwd(), 'fix_sse_remaining_issues.js');
  const backendFixPath = path.join(process.cwd(), 'fix_sse_backend_simple.py');
  
  if (!fileExists(frontendFixPath)) {
    console.error(`Frontend fix script not found: ${frontendFixPath}`);
    return false;
  }
  
  if (!fileExists(dataParsingFixPath)) {
    console.error(`SSE data parsing fix script not found: ${dataParsingFixPath}`);
    return false;
  }
  
  if (!fileExists(remainingIssuesFixPath)) {
    console.error(`Remaining SSE issues fix script not found: ${remainingIssuesFixPath}`);
    return false;
  }
  
  if (!fileExists(backendFixPath)) {
    console.error(`Backend fix script not found: ${backendFixPath}`);
    return false;
  }
  
  // Apply frontend fixes
  console.log('\n=== Applying Frontend Fixes ===\n');
  const frontendSuccess = runCommand('node fix_sse_frontend.js');
  
  // Apply SSE data parsing fix
  console.log('\n=== Applying SSE Data Parsing Fix ===\n');
  const dataParsingSuccess = runCommand('node fix_sse_data_parsing.js');
  
  // Apply remaining SSE issues fix
  console.log('\n=== Applying Remaining SSE Issues Fix ===\n');
  const remainingIssuesSuccess = runCommand('node fix_sse_remaining_issues.js');
  
  // Apply backend fixes
  console.log('\n=== Applying Backend Fixes ===\n');
  const backendSuccess = runCommand('python fix_sse_backend_simple.py');
  
  // Report results
  if (frontendSuccess && dataParsingSuccess && remainingIssuesSuccess && backendSuccess) {
    console.log('\n✅ All SSE fixes applied successfully!');
    console.log('\nTo test the fixes:');
    console.log('1. Start the backend server: cd backend && uvicorn app.main:app --reload --port 8000');
    console.log('2. Start the frontend server: npm run dev');
    console.log('3. Navigate to http://localhost:3000/vector-search and test the search functionality');
    return true;
  } else {
    console.error('\n❌ Some fixes failed to apply. Please check the logs above for details.');
    if (!frontendSuccess) console.error('- Frontend fixes failed');
    if (!dataParsingSuccess) console.error('- SSE data parsing fix failed');
    if (!remainingIssuesSuccess) console.error('- Remaining SSE issues fix failed');
    if (!backendSuccess) console.error('- Backend fixes failed');
    return false;
  }
}

// Run the fixes
applyFixes().then((success) => {
  if (!success) {
    process.exit(1);
  }
});
