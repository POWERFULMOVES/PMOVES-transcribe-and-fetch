// This script fixes the syntax error in the test files
const fs = require('fs');
const path = require('path');

// Paths to the test files
const testFiles = [
  'src/app/tests/vector-search.test.js',
  'src/app/vector-search/__tests__/page.test.js'
];

// Function to fix the syntax error in a file
function fixSyntaxError(filePath) {
  console.log(`Fixing syntax error in ${filePath}...`);
  
  // Read the file
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Replace the syntax error
  content = content.replace(/console\.error\('Search error:'\s+err\);/g, "console.error('Search error:', err);");
  
  // Write the fixed content back to the file
  fs.writeFileSync(filePath, content, 'utf8');
  
  console.log(`Fixed syntax error in ${filePath}`);
}

// Fix the syntax error in all test files
testFiles.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    fixSyntaxError(filePath);
  } else {
    console.log(`File not found: ${filePath}`);
  }
});

console.log('Done fixing syntax errors in test files');
