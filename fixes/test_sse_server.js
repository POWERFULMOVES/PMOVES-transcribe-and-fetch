/**
 * test_sse_server.js - Server-side SSE connection test
 * 
 * This script tests the SSE connection to the backend server using Node.js.
 * It helps diagnose if the issue is with the client or the server.
 */

const { EventSource } = require('eventsource');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = 'http://localhost:8000'; // Update this to match your backend URL
const SSE_ENDPOINT = '/combined-updates';
const LOG_FILE = path.join(__dirname, 'sse_server_test_log.txt');

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

// Create EventSource with detailed options
const eventSourceOptions = {
  headers: {
    'Accept': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  },
  https: {
    rejectUnauthorized: false // For testing with self-signed certificates
  },
  withCredentials: true
};

const eventSource = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`, eventSourceOptions);

// Track received messages
let messageCount = 0;
let segmentCount = 0;
let statusCount = 0;
let errorCount = 0;
let otherCount = 0;

// Handle connection open
eventSource.onopen = (event) => {
  log('SSE connection opened successfully');
  log(`Connection details: readyState=${eventSource.readyState}`);
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
    } else if (data.type === 'heartbeat') {
      log(`Received heartbeat message: ${JSON.stringify(data)}`);
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
    log('Connection is in CLOSED state');
    
    // Attempt to reconnect after a delay
    setTimeout(() => {
      log('Attempting to reconnect...');
      // Create a new EventSource
      const newEventSource = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`, eventSourceOptions);
      // Replace the old one
      eventSource.close();
      eventSource = newEventSource;
      log('Created new EventSource for reconnection');
    }, 5000);
  }
};

// Setup cleanup on exit
process.on('SIGINT', () => {
  log('Received SIGINT, closing connection...');
  eventSource.close();
  log(`Final message counts - Total: ${messageCount}, Segments: ${segmentCount}, Status: ${statusCount}, Errors: ${errorCount}, Other: ${otherCount}`);
  process.exit(0);
});

// Set a timeout to close the connection after 60 seconds if no messages are received
const timeoutId = setTimeout(() => {
  if (messageCount === 0) {
    log('No messages received after 60 seconds. Closing connection.');
    eventSource.close();
    process.exit(1);
  }
}, 60000);

log('Test script running. Press Ctrl+C to exit.');
