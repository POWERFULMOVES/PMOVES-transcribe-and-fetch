// Simple test script for SSE endpoint using fetch
const fetch = require('node-fetch');

console.log('Testing SSE endpoint with curl...');

// Use curl to test the SSE endpoint
const { exec } = require('child_process');
exec('curl -N http://localhost:8000/combined-updates', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`Stderr: ${stderr}`);
    return;
  }
  console.log(`Stdout: ${stdout}`);
});

console.log('Curl command executed. Waiting for response...');
