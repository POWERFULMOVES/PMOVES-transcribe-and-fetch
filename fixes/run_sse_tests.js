/**
 * Script to run all SSE tests
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Function to check if a file exists
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (err) {
    console.error(`Error checking if file exists: ${err.message}`);
    return false;
  }
}

// Function to execute a command and return its output
function executeCommand(command) {
  try {
    console.log(`Executing: ${command}`);
    const output = execSync(command, { encoding: 'utf8' });
    return { success: true, output };
  } catch (error) {
    console.error(`Command failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Function to run a test in a new terminal
function runTestInNewTerminal(command, description) {
  console.log(`\n=== Running ${description} ===`);
  console.log(`Command: ${command}`);
  console.log(`Please check the new terminal window that will open.`);
  
  // On Windows, use 'start cmd /k'
  if (process.platform === 'win32') {
    executeCommand(`start cmd /k "${command}"`);
  }
  // On macOS, use 'osascript'
  else if (process.platform === 'darwin') {
    const appleScript = `
      tell application "Terminal"
        do script "${command}"
      end tell
    `;
    executeCommand(`osascript -e '${appleScript}'`);
  }
  // On Linux, use 'x-terminal-emulator'
  else {
    executeCommand(`x-terminal-emulator -e "${command}"`);
  }
}

// Main function to run all tests
async function runAllTests() {
  console.log('Starting SSE tests...');
  
  // Check if test files exist
  const implementationTestPath = path.join(process.cwd(), 'test_sse_implementation.js');
  const backendTestPath = path.join(process.cwd(), 'test_sse_backend.sh');
  const frontendTestPath = path.join(process.cwd(), 'test_sse_frontend.js');
  
  if (!fileExists(implementationTestPath)) {
    console.error(`Implementation test file not found: ${implementationTestPath}`);
    return false;
  }
  
  if (!fileExists(backendTestPath)) {
    console.error(`Backend test file not found: ${backendTestPath}`);
    return false;
  }
  
  if (!fileExists(frontendTestPath)) {
    console.error(`Frontend test file not found: ${frontendTestPath}`);
    return false;
  }
  
  // Make the backend test script executable
  if (process.platform !== 'win32') {
    executeCommand(`chmod +x ${backendTestPath}`);
  }
  
  // Check if the backend server is running
  console.log('\nChecking if backend server is running...');
  let backendRunning = false;
  
  // Try multiple endpoints to check if backend is running
  const endpoints = [
    'http://localhost:8000/api/health',
    'http://localhost:8000/',
    'http://localhost:8000/api/search/preset-technical'
  ];
  
  for (const endpoint of endpoints) {
    try {
      console.log(`Trying to connect to ${endpoint}...`);
      const response = execSync(`curl -s -o /dev/null -w "%{http_code}" ${endpoint}`, { encoding: 'utf8' });
      if (response === '200' || response === '204' || response === '302') {
        backendRunning = true;
        console.log(`Successfully connected to ${endpoint}`);
        break;
      }
    } catch (error) {
      console.log(`Could not connect to ${endpoint}`);
    }
  }
  
  if (!backendRunning) {
    console.log('\n=== Starting Backend Server ===');
    console.log('Please start the backend server in a new terminal:');
    console.log('cd backend && python -m app.main');
    
    // Ask user to confirm backend status
    console.log('\nIs the backend server already running? (y/n)');
    const response = await new Promise(resolve => {
      process.stdin.once('data', (data) => {
        resolve(data.toString().trim().toLowerCase());
      });
    });
    
    if (response !== 'y' && response !== 'yes') {
      console.log('\nPress Enter when the backend server is running...');
      await new Promise(resolve => {
        process.stdin.once('data', () => {
          resolve();
        });
      });
    }
  } else {
    console.log('Backend server is already running.');
  }
  
  // Run the implementation test
  runTestInNewTerminal('node test_sse_implementation.js', 'Implementation Test');
  
  // Wait a bit to allow the first terminal to open
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Run the backend test
  if (process.platform === 'win32') {
    runTestInNewTerminal('test_sse_backend.sh', 'Backend Test');
  } else {
    runTestInNewTerminal('./test_sse_backend.sh', 'Backend Test');
  }
  
  // Wait a bit to allow the second terminal to open
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Run the frontend test
  runTestInNewTerminal('node test_sse_frontend.js', 'Frontend Test');
  
  console.log('\n=== All Tests Started ===');
  console.log('Please check the terminal windows that have opened.');
  console.log('After testing, you can apply the SSE fixes using:');
  console.log('node apply_sse_fixes.js');
  
  return true;
}

// Run the tests
runAllTests().catch(console.error);
