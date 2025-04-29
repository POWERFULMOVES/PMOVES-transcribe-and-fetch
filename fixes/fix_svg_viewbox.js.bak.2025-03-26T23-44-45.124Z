/**
 * fix_svg_viewbox.js - Fix SVG viewBox attribute issues
 * 
 * This script fixes the SVG viewBox attribute error that appears in the console logs.
 * The error is: "Error: <svg> attribute viewBox: Expected number, "0 0 100% 4"."
 */

const fs = require('fs');
const path = require('path');

// Function to find all SVG files in the project
function findSvgFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && !filePath.includes('node_modules') && !filePath.includes('.next')) {
      findSvgFiles(filePath, fileList);
    } else if (file.endsWith('.svg')) {
      fileList.push(filePath);
    } else if (file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.tsx')) {
      // Check JS/JSX/TSX files for inline SVGs
      const content = fs.readFileSync(filePath, 'utf8');
      if (content.includes('<svg') && content.includes('viewBox')) {
        fileList.push(filePath);
      }
    }
  });
  
  return fileList;
}

// Function to fix SVG viewBox attributes
function fixSvgViewBox(filePath) {
  console.log(`Checking ${filePath}...`);
  
  try {
    // Read the file
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Check if the file contains the problematic viewBox attribute
    if (content.includes('viewBox="0 0 100% 4"')) {
      console.log(`Found problematic viewBox in ${filePath}`);
      
      // Create backup
      const backupPath = `${filePath}.bak.${new Date().toISOString().replace(/:/g, '-')}`;
      fs.writeFileSync(backupPath, content, 'utf8');
      console.log(`Created backup: ${backupPath}`);
      
      // Fix the viewBox attribute
      content = content.replace(/viewBox="0 0 100% 4"/g, 'viewBox="0 0 100 4"');
      
      // Write the updated content
      fs.writeFileSync(filePath, content, 'utf8');
      
      console.log(`✅ Fixed viewBox attribute in ${filePath}`);
      return true;
    }
    
    // Check for other percentage-based viewBox values
    const viewBoxRegex = /viewBox="([^"]*?)%([^"]*)"/g;
    let match;
    let modified = false;
    
    while ((match = viewBoxRegex.exec(content)) !== null) {
      console.log(`Found percentage in viewBox: ${match[0]} in ${filePath}`);
      
      // Create backup if not already created
      if (!modified) {
        const backupPath = `${filePath}.bak.${new Date().toISOString().replace(/:/g, '-')}`;
        fs.writeFileSync(backupPath, content, 'utf8');
        console.log(`Created backup: ${backupPath}`);
        modified = true;
      }
      
      // Extract the viewBox values
      const fullMatch = match[0];
      const values = fullMatch.substring(9, fullMatch.length - 1).split(' ');
      
      // Replace percentage values with fixed numbers
      const fixedValues = values.map(val => {
        if (val.includes('%')) {
          return val.replace('%', '') === '100%' ? '100' : '100';
        }
        return val;
      });
      
      // Create the fixed viewBox attribute
      const fixedViewBox = `viewBox="${fixedValues.join(' ')}"`;
      
      // Replace the problematic viewBox with the fixed one
      content = content.replace(fullMatch, fixedViewBox);
      
      console.log(`Fixed viewBox: ${fullMatch} -> ${fixedViewBox}`);
    }
    
    // If modifications were made, write the updated content
    if (modified) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ Fixed viewBox attributes in ${filePath}`);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`Error fixing ${filePath}:`, error);
    return false;
  }
}

// Main function
function main() {
  console.log('Fixing SVG viewBox attribute issues...');
  
  // Find all SVG files in the project
  const svgFiles = findSvgFiles(path.join(__dirname));
  console.log(`Found ${svgFiles.length} SVG files to check`);
  
  // Fix viewBox attributes in each file
  let fixedCount = 0;
  svgFiles.forEach(filePath => {
    const fixed = fixSvgViewBox(filePath);
    if (fixed) {
      fixedCount++;
    }
  });
  
  if (fixedCount > 0) {
    console.log(`\n✅ Fixed viewBox attributes in ${fixedCount} files`);
  } else {
    console.log('\n✅ No problematic viewBox attributes found');
  }
  
  // Also check for the specific pmoves.svg file mentioned in the error
  const pmovesSvgPath = path.join(__dirname, 'public', 'images', 'pmoves.svg');
  if (fs.existsSync(pmovesSvgPath)) {
    console.log(`\nChecking specific file: ${pmovesSvgPath}`);
    const fixed = fixSvgViewBox(pmovesSvgPath);
    if (fixed) {
      console.log(`✅ Fixed viewBox attribute in ${pmovesSvgPath}`);
    } else {
      console.log(`No problematic viewBox attribute found in ${pmovesSvgPath}`);
    }
  } else {
    console.log(`\nSpecific file not found: ${pmovesSvgPath}`);
  }
}

// Run the script
main();
