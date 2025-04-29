// Simple test script to verify SSE connection and message processing
const { EventSource } = require('eventsource');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = 'http://localhost:8000'; // Update this to match your backend URL
const SSE_ENDPOINT = '/combined-updates';
const LOG_FILE = path.join(__dirname, 'sse_test_log.txt');

// Clear previous log file
if (fs.existsSync(LOG_FILE)) {
  fs.unlinkSync(LOG_FILE);
}

// Helper function to log messages
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());
  fs.appendFileSync(LOG_FILE, logMessage);
}

// Connect to SSE endpoint
log(`Connecting to SSE endpoint: ${BACKEND_URL}${SSE_ENDPOINT}`);
const eventSource = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`, {
  withCredentials: true
});

// Track received messages
let messageCount = 0;
let segmentCount = 0;
let statusCount = 0;
let errorCount = 0;
let otherCount = 0;

// Handle connection open
eventSource.onopen = (event) => {
  log('SSE connection opened successfully');
};

// Handle messages
eventSource.onmessage = (event) => {
  messageCount++;
  
  try {
    // Try to parse the message data
    let data;
    try {
      // Handle 'data: ' prefix if present
      const jsonStr = event.data.startsWith('data: ') ? event.data.slice(6).trim() : event.data.trim();
      data = JSON.parse(jsonStr);
    } catch (parseError) {
      log(`Error parsing message: ${parseError.message}`);
      log(`Raw message data: ${event.data}`);
      errorCount++;
      return;
    }
    
    // Process different message types
    if (data.type === 'transcription_segment') {
      segmentCount++;
      const content = data.content || {};
      log(`Received transcription segment #${segmentCount}: ${JSON.stringify(content).substring(0, 100)}...`);
      
      // Validate segment data
      if (!content.text) {
        log(`WARNING: Segment has no text property: ${JSON.stringify(content)}`);
      }
    } else if (data.type === 'status') {
      statusCount++;
      log(`Received status update #${statusCount}: ${JSON.stringify(data.content)}`);
    } else if (data.type === 'transcription_complete') {
      log(`Received transcription_complete message: ${JSON.stringify(data)}`);
    } else {
      otherCount++;
      log(`Received other message type (${data.type}): ${JSON.stringify(data)}`);
    }
  } catch (error) {
    log(`Error processing message: ${error.message}`);
    errorCount++;
  }
  
  // Log message counts every 10 messages
  if (messageCount % 10 === 0) {
    log(`Message counts - Total: ${messageCount}, Segments: ${segmentCount}, Status: ${statusCount}, Errors: ${errorCount}, Other: ${otherCount}`);
  }
};

// Handle errors
eventSource.onerror = (error) => {
  log(`SSE connection error: ${error.message || 'Unknown error'}`);
  
  // Check if the connection is closed
  if (eventSource.readyState === 2) { // CLOSED
    log('Connection is in CLOSED state, attempting to reconnect...');
    
    // Wait a bit before reconnecting
    setTimeout(() => {
      log('Reconnecting...');
      // The EventSource will automatically try to reconnect
    }, 2000);
  }
};

// Setup cleanup on exit
process.on('SIGINT', () => {
  log('Received SIGINT, closing connection...');
  eventSource.close();
  log(`Final message counts - Total: ${messageCount}, Segments: ${segmentCount}, Status: ${statusCount}, Errors: ${errorCount}, Other: ${otherCount}`);
  process.exit(0);
});

log('Test script running. Press Ctrl+C to exit.');
