/**
 * Transcription Delay Test and Fix
 * Tests and fixes the delay between backend completion and frontend display
 */

// Test configuration
const config = {
  testDuration: 60000, // 1 minute
  youtubeUrl: null, // Will use the current URL in the input field
};

// Test state
let testState = {
  startTime: 0,
  backendCompletionTime: null,
  frontendCompletionTime: null,
  segmentsReceived: [],
  segmentsDisplayed: [],
  statusUpdates: []
};

// Original functions to restore later
const originals = {};

// Utility functions
function log(message) {
  console.log(`[TEST] ${message}`);
}

function formatTime(ms) {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  return `${(ms/1000).toFixed(1)}s`;
}

// Setup test hooks
function setupTestHooks() {
  log("Setting up test hooks");
  
  // Store original functions
  originals.dispatch = dispatch;
  originals.EventSource = window.EventSource;
  
  // Track status updates and segments
  dispatch = function(action) {
    const now = performance.now();
    
    // Track transcription segments
    if (action.type === ACTIONS.ADD_TRANSCRIPTION_SEGMENT) {
      testState.segmentsDisplayed.push({
        id: action.payload.id,
        text: action.payload.text,
        time: now
      });
      
      log(`Segment displayed: ID=${action.payload.id}, Time=${formatTime(now - testState.startTime)}`);
    }
    
    // Track status updates
    if (action.type === ACTIONS.ADD_STATUS_UPDATE) {
      testState.statusUpdates.push({
        content: action.payload,
        time: now
      });
      
      // Check for completion message
      if (action.payload.includes("TRANSCRIPTION COMPLETED SUCCESSFULLY") || 
          action.payload.includes("Transcription process completed")) {
        testState.frontendCompletionTime = now;
        log(`Frontend completion detected at ${formatTime(now - testState.startTime)}`);
      }
      
      log(`Status update: "${action.payload}", Time=${formatTime(now - testState.startTime)}`);
    }
    
    // Call original dispatch
    return originals.dispatch(action);
  };
  
  // Track raw SSE messages
  window.EventSource = function(...args) {
    const instance = new originals.EventSource(...args);
    
    const originalOnMessage = instance.onmessage;
    instance.onmessage = function(event) {
      try {
        const now = performance.now();
        const data = JSON.parse(event.data.startsWith('data: ') ? event.data.slice(6) : event.data);
        
        // Track transcription segments
        if (data.type === 'transcription_segment') {
          testState.segmentsReceived.push({
            id: data.content.id,
            text: data.content.text,
            time: now
          });
          
          log(`Segment received: ID=${data.content.id}, Time=${formatTime(now - testState.startTime)}`);
        }
        
        // Check for backend completion
        if (data.type === 'status' && 
            (data.content.includes("TRANSCRIPTION COMPLETED SUCCESSFULLY") || 
             data.content.includes("Transcription process completed"))) {
          testState.backendCompletionTime = now;
          log(`Backend completion detected at ${formatTime(now - testState.startTime)}`);
        }
      } catch (e) {
        // Ignore parsing errors
      }
      
      // Call original handler
      return originalOnMessage.apply(this, arguments);
    };
    
    return instance;
  };
}

// Restore original functions
function restoreTestHooks() {
  log("Restoring original hooks");
  
  dispatch = originals.dispatch;
  window.EventSource = originals.EventSource;
}

// Analyze test results
function analyzeResults() {
  log("Analyzing test results");
  
  const results = {
    backendCompletionTime: testState.backendCompletionTime,
    frontendCompletionTime: testState.frontendCompletionTime,
    segmentsReceived: testState.segmentsReceived.length,
    segmentsDisplayed: testState.segmentsDisplayed.length,
    completionDelay: null,
    averageSegmentDelay: null,
    maxSegmentDelay: null,
    segmentDelays: []
  };
  
  // Calculate completion delay
  if (results.backendCompletionTime && results.frontendCompletionTime) {
    results.completionDelay = results.frontendCompletionTime - results.backendCompletionTime;
    log(`Completion delay: ${formatTime(results.completionDelay)}`);
  } else {
    log("Could not calculate completion delay - missing timestamps");
  }
  
  // Calculate segment delays
  const segmentDelays = [];
  
  testState.segmentsReceived.forEach(received => {
    const displayed = testState.segmentsDisplayed.find(d => d.id === received.id);
    
    if (displayed) {
      const delay = displayed.time - received.time;
      segmentDelays.push({
        id: received.id,
        text: received.text,
        delay
      });
    }
  });
  
  if (segmentDelays.length > 0) {
    results.segmentDelays = segmentDelays;
    results.averageSegmentDelay = segmentDelays.reduce((sum, item) => sum + item.delay, 0) / segmentDelays.length;
    results.maxSegmentDelay = Math.max(...segmentDelays.map(item => item.delay));
    
    log(`Average segment delay: ${formatTime(results.averageSegmentDelay)}`);
    log(`Maximum segment delay: ${formatTime(results.maxSegmentDelay)}`);
    
    // Find segments with excessive delay
    const excessiveDelays = segmentDelays.filter(item => item.delay > results.averageSegmentDelay * 2);
    if (excessiveDelays.length > 0) {
      log(`Found ${excessiveDelays.length} segments with excessive delay:`);
      excessiveDelays.forEach(item => {
        log(`  Segment ${item.id}: ${formatTime(item.delay)} - "${item.text}"`);
      });
    }
  } else {
    log("Could not calculate segment delays - no matching segments");
  }
  
  // Check for missing segments
  const missingSegments = testState.segmentsReceived.filter(received => 
    !testState.segmentsDisplayed.some(displayed => displayed.id === received.id)
  );
  
  if (missingSegments.length > 0) {
    results.missingSegments = missingSegments.length;
    log(`Found ${missingSegments.length} segments that were received but not displayed`);
  }
  
  return results;
}

// Apply the fix
function applyFix() {
  log("Applying transcription delay fix");
  
  // 1. Reduce excessive logging in useSSE.js
  if (typeof parseMessage === 'function') {
    originals.parseMessage = parseMessage;
    
    // Override with optimized version
    window.parseMessage = function(data) {
      if (!data) return null;
      
      try {
        // Fast path: Handle 'data: ' prefix if present
        const jsonStr = typeof data === 'string' && data.startsWith('data: ') ? 
          data.slice(6).trim() : 
          (typeof data === 'string' ? data.trim() : data);
        
        // Skip empty messages
        if (!jsonStr) return null;
        
        // If already an object, just ensure timestamp
        if (typeof jsonStr === 'object' && jsonStr !== null) {
          return { ...jsonStr, timestamp: jsonStr.timestamp || new Date().toISOString() };
        }
        
        // Parse JSON with minimal validation
        const parsed = JSON.parse(jsonStr);
        
        // Minimal processing - just ensure timestamp exists
        if (typeof parsed === 'object' && parsed !== null) {
          if (!parsed.timestamp) parsed.timestamp = new Date().toISOString();
          return parsed;
        }
        
        // Fallback for non-object results
        return { type: 'status', content: parsed, timestamp: new Date().toISOString() };
      } catch (error) {
        // Minimal error handling
        return { type: 'error', content: 'Failed to process message', timestamp: new Date().toISOString() };
      }
    };
  }
  
  // 2. Implement batch processing for transcription segments
  // Create a message buffer
  window.messageBuffer = [];
  window.processingBuffer = false;
  window.bufferTimeout = null;
  
  // Process buffer in batches
  window.processMessageBuffer = function() {
    if (window.processingBuffer || window.messageBuffer.length === 0) return;
    
    window.processingBuffer = true;
    
    try {
      // Get all segments from buffer
      const messages = [...window.messageBuffer];
      window.messageBuffer = [];
      
      // Process messages in order
      messages.forEach(data => {
        if (data.type === 'transcription_segment') {
          const content = data.content;
          
          // Create segment with minimal processing
          const segment = {
            text: content.text || '',
            start_time: parseFloat(content.start_seconds || content.start_time || 0),
            end_time: parseFloat(content.end_seconds || content.end_time || 0),
            id: content.id || `seg_${Date.now()}`,
            video_id: content.video_id || state.youtubeUrl?.split('v=')[1] || '',
            watch_url: content.watch_url || null
          };
          
          // Skip validation for performance - just check text exists
          if (segment.text) {
            dispatch({ type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT, payload: segment });
          }
        } else {
          // Process other message types normally
          if (data.type === 'status') {
            dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: data.content });
          } else if (data.type === 'error') {
            // Special handling for "Set of Tasks/Futures is empty" error
            if (data.content && data.content.includes('Set of Tasks/Futures is empty')) {
              dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error: ${data.content}` });
              dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Backend task queue error - attempting to continue...' });
              return;
            }
            
            dispatch({ type: ACTIONS.SET_ERROR, payload: data.content });
            dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error: ${data.content}` });
          } else if (data.type === 'transcription_complete') {
            dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
            dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Transcription process completed.' });
            disconnectSSE();
          }
        }
      });
    } finally {
      window.processingBuffer = false;
      
      // Schedule next batch if needed
      if (window.messageBuffer.length > 0) {
        window.bufferTimeout = setTimeout(window.processMessageBuffer, 50);
      }
    }
  };
  
  // 3. Override onMessage to use buffer
  if (typeof onMessage === 'function') {
    originals.onMessage = onMessage;
    
    window.onMessage = function(data) {
      // Add to buffer
      window.messageBuffer.push(data);
      
      // Schedule processing if not already scheduled
      if (!window.bufferTimeout) {
        window.bufferTimeout = setTimeout(window.processMessageBuffer, 50);
      }
    };
  }
  
  log("Fix applied successfully");
}

// Remove the fix
function removeFix() {
  log("Removing transcription delay fix");
  
  // Restore original functions
  if (originals.parseMessage) {
    window.parseMessage = originals.parseMessage;
  }
  
  if (originals.onMessage) {
    window.onMessage = originals.onMessage;
  }
  
  // Clear buffer and timeout
  if (window.bufferTimeout) {
    clearTimeout(window.bufferTimeout);
    window.bufferTimeout = null;
  }
  
  window.messageBuffer = [];
  window.processingBuffer = false;
  
  log("Fix removed successfully");
}

// Run the test
async function runTest(withFix = false) {
  // Reset test state
  testState = {
    startTime: performance.now(),
    backendCompletionTime: null,
    frontendCompletionTime: null,
    segmentsReceived: [],
    segmentsDisplayed: [],
    statusUpdates: []
  };
  
  log(`Starting test ${withFix ? 'with' : 'without'} fix`);
  
  // Set up test hooks
  setupTestHooks();
  
  // Apply fix if requested
  if (withFix) {
    applyFix();
  }
  
  try {
    // Start transcription
    log("Starting transcription process");
    await onProcessVideo();
    
    // Wait for test to complete or timeout
    await new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        const now = performance.now();
        const elapsed = now - testState.startTime;
        
        // Check if both backend and frontend have completed
        if (testState.backendCompletionTime && testState.frontendCompletionTime) {
          log("Test completed - both backend and frontend finished");
          clearInterval(checkInterval);
          resolve();
        }
        
        // Check for timeout
        if (elapsed > config.testDuration) {
          log("Test timed out");
          clearInterval(checkInterval);
          resolve();
        }
      }, 1000);
    });
    
    // Analyze results
    return analyzeResults();
  } finally {
    // Remove fix if applied
    if (withFix) {
      removeFix();
    }
    
    // Restore original functions
    restoreTestHooks();
  }
}

// Compare performance with and without the fix
async function comparePerformance() {
  log("Starting performance comparison");
  
  // Test without fix
  log("Running test without fix");
  const withoutFixResults = await runTest(false);
  
  // Test with fix
  log("Running test with fix");
  const withFixResults = await runTest(true);
  
  // Compare results
  const comparison = {
    withoutFix: {
      completionDelay: withoutFixResults.completionDelay,
      averageSegmentDelay: withoutFixResults.averageSegmentDelay,
      maxSegmentDelay: withoutFixResults.maxSegmentDelay,
      segmentsReceived: withoutFixResults.segmentsReceived,
      segmentsDisplayed: withoutFixResults.segmentsDisplayed
    },
    withFix: {
      completionDelay: withFixResults.completionDelay,
      averageSegmentDelay: withFixResults.averageSegmentDelay,
      maxSegmentDelay: withFixResults.maxSegmentDelay,
      segmentsReceived: withFixResults.segmentsReceived,
      segmentsDisplayed: withFixResults.segmentsDisplayed
    },
    improvement: {}
  };
  
  // Calculate improvements
  if (withoutFixResults.completionDelay && withFixResults.completionDelay) {
    comparison.improvement.completionDelay = 
      (withoutFixResults.completionDelay - withFixResults.completionDelay) / withoutFixResults.completionDelay * 100;
    log(`Completion delay improvement: ${comparison.improvement.completionDelay.toFixed(1)}%`);
  }
  
  if (withoutFixResults.averageSegmentDelay && withFixResults.averageSegmentDelay) {
    comparison.improvement.averageSegmentDelay = 
      (withoutFixResults.averageSegmentDelay - withFixResults.averageSegmentDelay) / withoutFixResults.averageSegmentDelay * 100;
    log(`Average segment delay improvement: ${comparison.improvement.averageSegmentDelay.toFixed(1)}%`);
  }
  
  if (withoutFixResults.maxSegmentDelay && withFixResults.maxSegmentDelay) {
    comparison.improvement.maxSegmentDelay = 
      (withoutFixResults.maxSegmentDelay - withFixResults.maxSegmentDelay) / withoutFixResults.maxSegmentDelay * 100;
    log(`Maximum segment delay improvement: ${comparison.improvement.maxSegmentDelay.toFixed(1)}%`);
  }
  
  log("Performance comparison complete");
  return comparison;
}

// Run just the fix without testing
function runFixOnly() {
  log("Applying fix without testing");
  applyFix();
  
  // Return a function to remove the fix
  return function() {
    log("Removing fix");
    removeFix();
  };
}

// Export functions for console use
window.TranscriptionTest = {
  runTest,
  comparePerformance,
  applyFix,
  removeFix,
  runFixOnly
};

log("Transcription delay test loaded. Use TranscriptionTest.runTest() or TranscriptionTest.applyFix() to begin.");
