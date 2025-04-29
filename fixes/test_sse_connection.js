/**
 * test_sse_connection.js - Test script to verify SSE connection stability
 * 
 * This script tests the SSE connection to the backend server and verifies
 * that the connection remains stable over time.
 * 
 * Usage:
 * 1. Start the backend server
 * 2. Run this script with Node.js: node test_sse_connection.js
 */

const { EventSource } = require('eventsource');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = 'http://localhost:8000';
const SSE_ENDPOINT = '/combined-updates';
const LOG_FILE = path.join(__dirname, 'sse_connection_test_log.txt');
const TEST_DURATION = 300000; // 5 minutes
const RECONNECT_INTERVAL = 1000; // 1 second

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

// Track connection state
let connectionState = {
  isConnected: false,
  connectionCount: 0,
  lastConnectedAt: null,
  lastDisconnectedAt: null,
  messageCount: 0,
  lastMessageAt: null,
  errors: 0
};

// Function to create and manage EventSource connection
function createConnection() {
  log(`Creating SSE connection to ${BACKEND_URL}${SSE_ENDPOINT}`);
  
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
  
  // Handle connection open
  eventSource.onopen = (event) => {
    connectionState.isConnected = true;
    connectionState.connectionCount++;
    connectionState.lastConnectedAt = new Date();
    
    log(`✅ SSE connection #${connectionState.connectionCount} opened successfully`);
    log(`Connection details: readyState=${eventSource.readyState}`);
  };
  
  // Handle messages
  eventSource.onmessage = (event) => {
    connectionState.messageCount++;
    connectionState.lastMessageAt = new Date();
    
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
        return;
      }
      
      // Log message details
      log(`📝 Received message #${connectionState.messageCount}: type=${data.type}, id=${data.id || 'none'}`);
      
      // Log detailed message content for specific types
      if (data.type === 'transcription_segment') {
        const content = data.content || {};
        log(`Transcription segment: ${JSON.stringify(content).substring(0, 100)}...`);
      } else if (data.type === 'status') {
        log(`Status update: ${JSON.stringify(data.content)}`);
      } else if (data.type === 'heartbeat') {
        log(`Heartbeat received: ${data.content}`);
      }
    } catch (error) {
      log(`❌ Error processing message: ${error.message}`);
    }
  };
  
  // Handle errors
  eventSource.onerror = (error) => {
    connectionState.errors++;
    log(`❌ SSE connection error: ${error.message || 'Unknown error'}`);
    
    // Check if the connection is closed
    if (eventSource.readyState === 2) { // CLOSED
      connectionState.isConnected = false;
      connectionState.lastDisconnectedAt = new Date();
      log(`⚠️ Connection closed. Will attempt to reconnect in ${RECONNECT_INTERVAL/1000} seconds...`);
      
      // Close the current connection
      eventSource.close();
      
      // Wait a bit before reconnecting
      setTimeout(() => {
        log('🔄 Reconnecting...');
        createConnection();
      }, RECONNECT_INTERVAL);
    }
  };
  
  return eventSource;
}

// Start the test
log(`Starting SSE connection stability test to ${BACKEND_URL}${SSE_ENDPOINT}`);
log(`Test will run for ${TEST_DURATION / 60000} minutes`);

// Create initial connection
let eventSource = createConnection();

// Set up a heartbeat check to detect stalled connections
const connectionCheckInterval = setInterval(() => {
  if (connectionState.isConnected) {
    const now = new Date();
    const timeSinceLastMessage = connectionState.lastMessageAt ? 
      now - connectionState.lastMessageAt : 
      now - connectionState.lastConnectedAt;
    
    log(`Connection status: Connected for ${(now - connectionState.lastConnectedAt) / 1000} seconds`);
    log(`Last message received ${timeSinceLastMessage / 1000} seconds ago`);
    
    // If no message received for too long, consider the connection stalled
    if (timeSinceLastMessage > 30000) { // 30 seconds
      log(`⚠️ No messages received for ${timeSinceLastMessage / 1000} seconds - connection may be stalled`);
      log(`Closing current connection and reconnecting...`);
      
      // Close the current connection
      eventSource.close();
      connectionState.isConnected = false;
      connectionState.lastDisconnectedAt = now;
      
      // Create a new connection
      setTimeout(() => {
        eventSource = createConnection();
      }, RECONNECT_INTERVAL);
    }
  } else {
    log(`Connection status: Disconnected`);
  }
}, 10000); // Check every 10 seconds

// Set up a test timeout
setTimeout(() => {
  log('⏱️ Test duration reached, closing connection...');
  
  // Clean up
  clearInterval(connectionCheckInterval);
  eventSource.close();
  
  // Log final results
  log(`\n📊 FINAL RESULTS:`);
  log(`Total test duration: ${TEST_DURATION / 60000} minutes`);
  log(`Total connections established: ${connectionState.connectionCount}`);
  log(`Total messages received: ${connectionState.messageCount}`);
  log(`Total errors: ${connectionState.errors}`);
  
  if (connectionState.errors === 0 && connectionState.connectionCount === 1) {
    log(`\n✅ TEST PASSED: Connection remained stable throughout the test.`);
  } else if (connectionState.errors > 0 || connectionState.connectionCount > 1) {
    log(`\n⚠️ TEST COMPLETED WITH WARNINGS: Connection had issues during the test.`);
    log(`Errors: ${connectionState.errors}, Reconnections: ${connectionState.connectionCount - 1}`);
  }
  
  log(`\nTest log saved to: ${LOG_FILE}`);
  
  process.exit(0);
}, TEST_DURATION);

log('Test script running. Press Ctrl+C to exit early.');
