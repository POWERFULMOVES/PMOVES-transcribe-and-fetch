/**
 * test_sse_fix.js - Test script to verify the SSE connection fix
 * 
 * This script tests the SSE connection to the backend server and verifies
 * that transcription updates are properly received and displayed.
 * 
 * Usage:
 * 1. Start the backend server
 * 2. Run this script with Node.js: node test_sse_fix.js
 */

const { EventSource } = require('eventsource');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = 'http://localhost:8000';
const SSE_ENDPOINT = '/combined-updates';
const LOG_FILE = path.join(__dirname, 'sse_fix_test_log.txt');
const TEST_DURATION = 60000; // 60 seconds

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
log(`Starting SSE connection test to ${BACKEND_URL}${SSE_ENDPOINT}`);
log(`Test will run for ${TEST_DURATION / 1000} seconds`);

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
let heartbeatCount = 0;
let otherCount = 0;
let lastMessageTime = Date.now();

// Handle connection open
eventSource.onopen = (event) => {
  log('✅ SSE connection opened successfully');
  log(`Connection details: readyState=${eventSource.readyState}`);
  lastMessageTime = Date.now();
};

// Handle messages
eventSource.onmessage = (event) => {
  messageCount++;
  lastMessageTime = Date.now();
  
  try {
    // Try to parse the message data
    let data;
    try {
      // Handle 'data: ' prefix if present
      const jsonStr = event.data.startsWith('data: ') ? event.data.slice(6).trim() : event.data.trim();
      data = JSON.parse(jsonStr);
    } catch (parseError) {
      log(`❌ Error parsing message: ${parseError.message}`);
      log(`Raw message data: ${event.data}`);
      errorCount++;
      return;
    }
    
    // Process different message types
    if (data.type === 'transcription_segment') {
      segmentCount++;
      const content = data.content || {};
      log(`📝 Received transcription segment #${segmentCount}: ${JSON.stringify(content).substring(0, 100)}...`);
      
      // Validate segment data
      if (!content.text) {
        log(`⚠️ WARNING: Segment has no text property: ${JSON.stringify(content)}`);
      }
    } else if (data.type === 'status') {
      statusCount++;
      log(`ℹ️ Received status update #${statusCount}: ${JSON.stringify(data.content)}`);
    } else if (data.type === 'transcription_complete') {
      log(`🏁 Received transcription_complete message: ${JSON.stringify(data)}`);
    } else if (data.type === 'heartbeat') {
      heartbeatCount++;
      log(`💓 Received heartbeat #${heartbeatCount}`);
    } else {
      otherCount++;
      log(`📄 Received other message type (${data.type}): ${JSON.stringify(data)}`);
    }
  } catch (error) {
    log(`❌ Error processing message: ${error.message}`);
    errorCount++;
  }
  
  // Log message counts every 10 messages
  if (messageCount % 10 === 0) {
    log(`📊 Message counts - Total: ${messageCount}, Segments: ${segmentCount}, Status: ${statusCount}, Heartbeats: ${heartbeatCount}, Errors: ${errorCount}, Other: ${otherCount}`);
  }
};

// Handle errors
eventSource.onerror = (error) => {
  log(`❌ SSE connection error: ${error.message || 'Unknown error'}`);
  errorCount++;
  
  // Check if the connection is closed
  if (eventSource.readyState === 2) { // CLOSED
    log('⚠️ Connection is in CLOSED state, attempting to reconnect...');
    
    // Wait a bit before reconnecting
    setTimeout(() => {
      log('🔄 Reconnecting...');
      // The EventSource will automatically try to reconnect
    }, 2000);
  }
};

// Set up a heartbeat check to detect stalled connections
const heartbeatInterval = setInterval(() => {
  const now = Date.now();
  const timeSinceLastMessage = now - lastMessageTime;
  
  if (timeSinceLastMessage > 10000) { // 10 seconds
    log(`⚠️ No messages received for ${timeSinceLastMessage / 1000} seconds`);
  }
}, 5000);

// Set up a test timeout
setTimeout(() => {
  log('⏱️ Test duration reached, closing connection...');
  
  // Clean up
  clearInterval(heartbeatInterval);
  eventSource.close();
  
  // Log final results
  log(`\n📊 FINAL RESULTS:`);
  log(`Total test duration: ${TEST_DURATION / 1000} seconds`);
  log(`Total messages: ${messageCount}`);
  log(`Transcription segments: ${segmentCount}`);
  log(`Status updates: ${statusCount}`);
  log(`Heartbeats: ${heartbeatCount}`);
  log(`Errors: ${errorCount}`);
  log(`Other messages: ${otherCount}`);
  
  if (errorCount === 0) {
    log(`\n✅ TEST PASSED: No errors detected during the test.`);
  } else {
    log(`\n⚠️ TEST COMPLETED WITH WARNINGS: ${errorCount} errors detected during the test.`);
  }
  
  log(`\nTest log saved to: ${LOG_FILE}`);
  
  process.exit(0);
}, TEST_DURATION);

log('Test script running. Press Ctrl+C to exit early.');
