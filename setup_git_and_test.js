/**
 * setup_git_and_test.js - Set up Git branch and test SSE fixes
 * 
 * This script creates a Git branch for testing the SSE fixes, applies the fixes,
 * and runs tests to verify that the fixes work correctly.
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
function runCommand(command, options = {}) {
  try {
    const output = execSync(command, {
      encoding: 'utf8',
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options
    });
    return { success: true, output };
  } catch (error) {
    if (!options.ignoreError) {
      console.error(`Error executing command: ${command}`);
      console.error(error.message);
    }
    return { success: false, error: error.message };
  }
}

// Function to check if Git is installed
function checkGitInstalled() {
  console.log('Checking for Git...');
  const result = runCommand('git --version', { silent: true });
  if (!result.success) {
    console.error('Git is not installed or not in PATH.');
    console.error('Please install Git from https://git-scm.com/');
    process.exit(1);
  }
  console.log(`✅ Git is installed: ${result.output.trim()}`);
  return true;
}

// Function to check if the current directory is a Git repository
function checkGitRepo() {
  console.log('Checking if current directory is a Git repository...');
  const result = runCommand('git rev-parse --is-inside-work-tree', { silent: true, ignoreError: true });
  if (!result.success) {
    console.error('Current directory is not a Git repository.');
    
    // Ask if the user wants to initialize a Git repository
    rl.question('Do you want to initialize a Git repository? (y/n) ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        console.log('Initializing Git repository...');
        const initResult = runCommand('git init');
        if (initResult.success) {
          console.log('✅ Git repository initialized');
          
          // Create initial commit
          console.log('Creating initial commit...');
          runCommand('git add .');
          runCommand('git commit -m "Initial commit before SSE fixes"');
          console.log('✅ Initial commit created');
          
          // Continue with the script
          createBranch();
        } else {
          console.error('Failed to initialize Git repository.');
          process.exit(1);
        }
      } else {
        console.log('Exiting script. Please initialize a Git repository manually.');
        process.exit(1);
      }
    });
  } else {
    console.log('✅ Current directory is a Git repository');
    
    // Check if there are uncommitted changes
    const statusResult = runCommand('git status --porcelain', { silent: true });
    if (statusResult.output.trim() !== '') {
      console.log('⚠️ There are uncommitted changes in the repository.');
      
      // Ask if the user wants to commit the changes
      rl.question('Do you want to commit the current changes before proceeding? (y/n) ', (answer) => {
        if (answer.toLowerCase() === 'y') {
          console.log('Committing changes...');
          runCommand('git add .');
          runCommand('git commit -m "Commit changes before SSE fixes"');
          console.log('✅ Changes committed');
          
          // Continue with the script
          createBranch();
        } else {
          console.log('Continuing without committing changes...');
          createBranch();
        }
      });
    } else {
      console.log('✅ Working directory is clean');
      createBranch();
    }
  }
}

// Function to create a branch for testing the fixes
function createBranch() {
  const branchName = 'sse-fixes-' + new Date().toISOString().replace(/[:.]/g, '-');
  
  console.log(`Creating branch: ${branchName}...`);
  const result = runCommand(`git checkout -b ${branchName}`);
  
  if (result.success) {
    console.log(`✅ Created branch: ${branchName}`);
    installDependencies();
  } else {
    console.error(`Failed to create branch: ${branchName}`);
    process.exit(1);
  }
}

// Function to install dependencies
function installDependencies() {
  console.log('Installing dependencies...');
  
  // Install Node.js dependencies
  console.log('Installing Node.js dependencies...');
  runCommand('npm install --no-fund --no-audit --loglevel=error axios eventsource fs-extra chalk');
  
  // Install Python dependencies
  console.log('Installing Python dependencies...');
  runCommand('pip install rich');
  
  console.log('✅ Dependencies installed');
  
  // Ask if the user wants to apply the fixes
  rl.question('Do you want to apply the SSE fixes now? (y/n) ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      applyFixes();
    } else {
      console.log('Skipping applying fixes.');
      console.log('You can apply the fixes later by running:');
      console.log('npm run fix-all');
      rl.close();
    }
  });
}

// Function to apply the fixes
function applyFixes() {
  console.log('Applying SSE fixes...');
  
  // Apply backend fixes
  console.log('1. Applying backend fixes...');
  runCommand('python fix_sse_v6.py');
  
  // Apply frontend fixes
  console.log('2. Applying frontend fixes...');
  runCommand('node apply_sse_frontend_fixes.js');
  
  // Fix SVG viewBox issues
  console.log('3. Fixing SVG viewBox issues...');
  runCommand('node fix_svg_viewbox.js');
  
  console.log('✅ All fixes applied');
  
  // Commit the changes
  console.log('Committing the changes...');
  runCommand('git add .');
  runCommand('git commit -m "Apply SSE fixes"');
  
  console.log('✅ Changes committed');
  
  // Ask if the user wants to test the fixes
  rl.question('Do you want to test the SSE implementation now? (y/n) ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      testFixes();
    } else {
      console.log('Skipping testing.');
      console.log('You can test the fixes later by running:');
      console.log('node test_sse_implementation.js');
      finishScript();
    }
  });
}

// Function to test the fixes
function testFixes() {
  console.log('Testing SSE implementation...');
  
  // Run the test script
  runCommand('node test_sse_implementation.js');
  
  // Ask if the tests passed
  rl.question('Did the tests pass? (y/n) ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      console.log('✅ Tests passed');
      
      // Ask if the user wants to merge the changes
      rl.question('Do you want to merge the changes to the main branch? (y/n) ', (answer) => {
        if (answer.toLowerCase() === 'y') {
          mergeChanges();
        } else {
          console.log('Skipping merging changes.');
          console.log('You can merge the changes later by running:');
          console.log('git checkout main && git merge <branch-name>');
          finishScript();
        }
      });
    } else {
      console.log('❌ Tests failed');
      console.log('Please fix the issues and try again.');
      finishScript();
    }
  });
}

// Function to merge the changes
function mergeChanges() {
  console.log('Getting current branch name...');
  const branchResult = runCommand('git rev-parse --abbrev-ref HEAD', { silent: true });
  const currentBranch = branchResult.output.trim();
  
  console.log('Getting default branch name...');
  const remoteResult = runCommand('git remote show origin', { silent: true, ignoreError: true });
  let defaultBranch = 'main'; // Default to 'main' if we can't determine the default branch
  
  if (remoteResult.success) {
    const match = remoteResult.output.match(/HEAD branch: ([^\s]+)/);
    if (match && match[1]) {
      defaultBranch = match[1];
    }
  }
  
  console.log(`Merging changes from ${currentBranch} to ${defaultBranch}...`);
  
  // Checkout the default branch
  const checkoutResult = runCommand(`git checkout ${defaultBranch}`, { ignoreError: true });
  
  if (!checkoutResult.success) {
    console.error(`Failed to checkout ${defaultBranch}.`);
    console.log(`You can merge the changes later by running:`);
    console.log(`git checkout ${defaultBranch} && git merge ${currentBranch}`);
    finishScript();
    return;
  }
  
  // Merge the changes
  const mergeResult = runCommand(`git merge ${currentBranch}`);
  
  if (mergeResult.success) {
    console.log(`✅ Changes merged to ${defaultBranch}`);
    
    // Ask if the user wants to push the changes
    rl.question('Do you want to push the changes to the remote repository? (y/n) ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        console.log('Pushing changes...');
        const pushResult = runCommand('git push', { ignoreError: true });
        
        if (pushResult.success) {
          console.log('✅ Changes pushed to remote repository');
        } else {
          console.error('Failed to push changes to remote repository.');
          console.log('You can push the changes later by running:');
          console.log('git push');
        }
      } else {
        console.log('Skipping pushing changes.');
        console.log('You can push the changes later by running:');
        console.log('git push');
      }
      
      finishScript();
    });
  } else {
    console.error(`Failed to merge changes to ${defaultBranch}.`);
    console.log('You can merge the changes later by running:');
    console.log(`git checkout ${defaultBranch} && git merge ${currentBranch}`);
    finishScript();
  }
}

// Function to finish the script
function finishScript() {
  console.log('');
  console.log('=================================');
  console.log('SSE Fixes Setup Complete');
  console.log('=================================');
  console.log('');
  console.log('For more information, please read README_SSE_FIXES.md');
  console.log('');
  rl.close();
}

// Main function
function main() {
  console.log('=================================');
  console.log('PMOVES SSE Fixes Git Setup');
  console.log('=================================');
  console.log('');
  
  // Check if Git is installed
  checkGitInstalled();
  
  // Check if the current directory is a Git repository
  checkGitRepo();
}

// Run the script
main();
