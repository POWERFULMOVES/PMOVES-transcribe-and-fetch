/**
 * test_sse_latency.js - Test script to measure SSE connection latency
 * 
 * This script tests the SSE connection to the backend server and measures
 * the latency between when segments are received.
 * 
 * Usage:
 * 1. Start the backend server
 * 2. Run this script with Node.js: node test_sse_latency.js
 */

const { EventSource } = require('eventsource');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = 'http://localhost:8000';
const SSE_ENDPOINT = '/combined-updates';
const LOG_FILE = path.join(__dirname, 'sse_latency_test_log.txt');
const TEST_DURATION = 120000; // 120 seconds

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
log(`Starting SSE latency test to ${BACKEND_URL}${SSE_ENDPOINT}`);
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
let lastSegmentTime = Date.now();
let segmentLatencies = [];

// Handle connection open
eventSource.onopen = (event) => {
  log('✅ SSE connection opened successfully');
  log(`Connection details: readyState=${eventSource.readyState}`);
  lastMessageTime = Date.now();
  lastSegmentTime = Date.now();
};

// Handle messages
eventSource.onmessage = (event) => {
  messageCount++;
  const now = Date.now();
  const timeSinceLastMessage = now - lastMessageTime;
  lastMessageTime = now;
  
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
      
      // Calculate latency for segments
      const segmentLatency = now - lastSegmentTime;
      segmentLatencies.push(segmentLatency);
      lastSegmentTime = now;
      
      log(`📝 Received transcription segment #${segmentCount}: ${JSON.stringify(content).substring(0, 100)}...`);
      log(`⏱️ Latency since last segment: ${segmentLatency}ms`);
      
      // Validate segment data
      if (!content.text) {
        log(`⚠️ WARNING: Segment has no text property: ${JSON.stringify(content)}`);
      }
      
      // Check for priority flag
      if (data.priority === 'high') {
        log(`🚀 Segment has high priority flag`);
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
  
  // Calculate latency statistics
  let avgLatency = 0;
  let minLatency = Number.MAX_SAFE_INTEGER;
  let maxLatency = 0;
  
  if (segmentLatencies.length > 0) {
    avgLatency = segmentLatencies.reduce((sum, latency) => sum + latency, 0) / segmentLatencies.length;
    minLatency = Math.min(...segmentLatencies);
    maxLatency = Math.max(...segmentLatencies);
  }
  
  // Log final results
  log(`\n📊 FINAL RESULTS:`);
  log(`Total test duration: ${TEST_DURATION / 1000} seconds`);
  log(`Total messages: ${messageCount}`);
  log(`Transcription segments: ${segmentCount}`);
  log(`Status updates: ${statusCount}`);
  log(`Heartbeats: ${heartbeatCount}`);
  log(`Errors: ${errorCount}`);
  log(`Other messages: ${otherCount}`);
  
  log(`\n⏱️ LATENCY STATISTICS:`);
  log(`Average segment latency: ${avgLatency.toFixed(2)}ms`);
  log(`Minimum segment latency: ${minLatency === Number.MAX_SAFE_INTEGER ? 'N/A' : minLatency}ms`);
  log(`Maximum segment latency: ${maxLatency}ms`);
  
  if (errorCount === 0) {
    log(`\n✅ TEST PASSED: No errors detected during the test.`);
  } else {
    log(`\n⚠️ TEST COMPLETED WITH WARNINGS: ${errorCount} errors detected during the test.`);
  }
  
  log(`\nTest log saved to: ${LOG_FILE}`);
  
  process.exit(0);
}, TEST_DURATION);

log('Test script running. Press Ctrl+C to exit early.');
