// This script fixes the syntax error in the vector-search/page.js file
const fs = require('fs');
const path = require('path');

// Path to the file
const filePath = 'src/app/vector-search/page.js';

console.log(`Current working directory: ${process.cwd()}`);
console.log(`Checking if file exists: ${filePath}`);
console.log(`Absolute path: ${path.resolve(filePath)}`);

// Function to fix the syntax error in a file
function fixSyntaxError(filePath) {
  console.log(`Fixing syntax error in ${filePath}...`);
  
  try {
    // Read the file
    let content = fs.readFileSync(filePath, 'utf8');
    console.log(`File content length: ${content.length}`);
    
    // Check if the error pattern exists
    const errorPattern = /console\.error\('Search error:'\s+err\);/g;
    const hasError = errorPattern.test(content);
    console.log(`File contains error pattern: ${hasError}`);
    
    // Replace the syntax error
    content = content.replace(/console\.error\('Search error:'\s+err\);/g, "console.error('Search error:', err);");
    
    // Write the fixed content back to the file
    fs.writeFileSync(filePath, content, 'utf8');
    
    console.log(`Fixed syntax error in ${filePath}`);
  } catch (error) {
    console.error(`Error fixing syntax error: ${error.message}`);
  }
}

// Fix the syntax error in the file
if (fs.existsSync(filePath)) {
  fixSyntaxError(filePath);
} else {
  console.log(`File not found: ${filePath}`);
}

console.log('Done fixing syntax error in vector-search/page.js');
