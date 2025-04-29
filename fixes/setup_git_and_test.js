/**
 * setup_git_and_test.js - Set up Git repository and run SSE tests
 * 
 * This script helps users set up the Git repository and run the SSE tests.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to execute a command and return the output
function runCommand(command) {
  console.log(`Running command: ${command}`);
  try {
    const output = execSync(command, { encoding: 'utf8' });
    return { success: true, output };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Function to check if Git is installed
function checkGit() {
  console.log('Checking if Git is installed...');
  const result = runCommand('git --version');
  if (result.success) {
    console.log(`✅ Git is installed: ${result.output.trim()}`);
    return true;
  } else {
    console.error('❌ Git is not installed or not in the PATH.');
    console.error('Please install Git from https://git-scm.com/downloads');
    return false;
  }
}

// Function to check if the current directory is a Git repository
function checkGitRepo() {
  console.log('Checking if the current directory is a Git repository...');
  const result = runCommand('git status');
  if (result.success) {
    console.log('✅ Current directory is a Git repository.');
    return true;
  } else {
    console.error('❌ Current directory is not a Git repository.');
    return false;
  }
}

// Function to initialize a Git repository
function initGitRepo() {
  console.log('Initializing Git repository...');
  const result = runCommand('git init');
  if (result.success) {
    console.log('✅ Git repository initialized.');
    return true;
  } else {
    console.error('❌ Failed to initialize Git repository:', result.error);
    return false;
  }
}

// Function to create a new branch
function createBranch(branchName) {
  console.log(`Creating branch: ${branchName}...`);
  const result = runCommand(`git checkout -b ${branchName}`);
  if (result.success) {
    console.log(`✅ Branch ${branchName} created.`);
    return true;
  } else {
    console.error(`❌ Failed to create branch ${branchName}:`, result.error);
    return false;
  }
}

// Function to add files to Git
function addFiles() {
  console.log('Adding files to Git...');
  const filesToAdd = [
    'simple_sse_test.js',
    'test_sse_implementation.js',
    'fix_sse_frontend.js',
    'README_SSE_FIXES.md',
    'install_and_apply_fixes.sh',
    'install_and_apply_fixes.bat'
  ];
  
  // Check which files exist
  const existingFiles = filesToAdd.filter(file => fs.existsSync(file));
  
  if (existingFiles.length === 0) {
    console.error('❌ No files to add.');
    return false;
  }
  
  const result = runCommand(`git add ${existingFiles.join(' ')}`);
  if (result.success) {
    console.log(`✅ Added ${existingFiles.length} files to Git.`);
    return true;
  } else {
    console.error('❌ Failed to add files to Git:', result.error);
    return false;
  }
}

// Function to commit changes
function commitChanges(message) {
  console.log(`Committing changes with message: ${message}...`);
  const result = runCommand(`git commit -m "${message}"`);
  if (result.success) {
    console.log('✅ Changes committed.');
    return true;
  } else {
    console.error('❌ Failed to commit changes:', result.error);
    return false;
  }
}

// Function to run the SSE tests
function runTests() {
  console.log('Running SSE tests...');
  
  // Check if the backend server is running
  console.log('Checking if the backend server is running...');
  const healthCheckResult = runCommand('curl -s http://localhost:8000/health');
  if (!healthCheckResult.success) {
    console.error('❌ Backend server is not running.');
    console.error('Please start the backend server with:');
    console.error('  venv\\Scripts\\activate && cd backend && uvicorn app.main:app --reload --port 8000');
    return false;
  }
  
  // Run the simple SSE test
  console.log('Running simple SSE test...');
  const simpleTestResult = runCommand('node simple_sse_test.js');
  if (!simpleTestResult.success) {
    console.error('❌ Simple SSE test failed:', simpleTestResult.error);
    return false;
  }
  
  // Run the SSE implementation test
  console.log('Running SSE implementation test...');
  const implementationTestResult = runCommand('node test_sse_implementation.js');
  if (!implementationTestResult.success) {
    console.error('❌ SSE implementation test failed:', implementationTestResult.error);
    return false;
  }
  
  console.log('✅ All SSE tests passed.');
  return true;
}

// Main function
async function main() {
  console.log('=== Git Setup and SSE Test Script ===');
  
  // Check if Git is installed
  if (!checkGit()) {
    rl.close();
    return;
  }
  
  // Check if the current directory is a Git repository
  const isGitRepo = checkGitRepo();
  
  if (!isGitRepo) {
    rl.question('Do you want to initialize a Git repository? (y/n) ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        if (initGitRepo()) {
          rl.question('Enter a name for the branch (default: sse-fixes): ', (branchName) => {
            const branch = branchName.trim() || 'sse-fixes';
            if (createBranch(branch)) {
              if (addFiles()) {
                commitChanges('Add SSE fixes');
                rl.question('Do you want to run the SSE tests? (y/n) ', (answer) => {
                  if (answer.toLowerCase() === 'y') {
                    runTests();
                  }
                  rl.close();
                });
              } else {
                rl.close();
              }
            } else {
              rl.close();
            }
          });
        } else {
          rl.close();
        }
      } else {
        rl.close();
      }
    });
  } else {
    rl.question('Do you want to create a new branch for SSE fixes? (y/n) ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        rl.question('Enter a name for the branch (default: sse-fixes): ', (branchName) => {
          const branch = branchName.trim() || 'sse-fixes';
          if (createBranch(branch)) {
            if (addFiles()) {
              commitChanges('Add SSE fixes');
              rl.question('Do you want to run the SSE tests? (y/n) ', (answer) => {
                if (answer.toLowerCase() === 'y') {
                  runTests();
                }
                rl.close();
              });
            } else {
              rl.close();
            }
          } else {
            rl.close();
          }
        });
      } else {
        rl.question('Do you want to run the SSE tests? (y/n) ', (answer) => {
          if (answer.toLowerCase() === 'y') {
            runTests();
          }
          rl.close();
        });
      }
    });
  }
}

// Run the script
main();
