/**
 * fix_sse_error_handling.js
 * 
 * This script fixes the error handling in the useSSE hook to ensure
 * that errors are properly reported to the onError callback.
 */

const fs = require('fs');
const path = require('path');

// Path to the useSSE.js file
const useSSEPath = path.join(__dirname, 'src', 'hooks', 'useSSE.js');

console.log('Applying SSE error handling fixes...');

// Read the file
let useSSEContent = fs.readFileSync(useSSEPath, 'utf8');

// Fix 1: Improve error handling in the onerror handler
console.log('Fixing error handling in the onerror handler...');

// Find the onerror handler in the connect function
const onerrorRegex = /eventSourceRef\.current\.onerror = \(error\) => \{[\s\S]*?}\;/;
const onerrorMatch = useSSEContent.match(onerrorRegex);

if (onerrorMatch) {
  const oldOnerrorHandler = onerrorMatch[0];
  
  // Create the improved onerror handler
  const newOnerrorHandler = `eventSourceRef.current.onerror = (error) => {
    console.error(\`SSE connection error: \${endpoint}\`, error);

    // Check if the error is due to CORS
    const isCorsError = error instanceof Event && !error.bubbles;
    if (isCorsError) {
      console.error("Possible CORS error detected. Make sure the server has proper CORS headers.");
    }

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    // Always call onError callback if provided, regardless of connection state
    if (onError) {
      onError(error instanceof Error ? error : new Error('SSE connection error'));
    }

    // Check if we received a transcription_complete message recently
    // If so, this error might be expected as the server closes the connection
    const lastMessage = lastMessageRef.current;
    if (lastMessage && lastMessage.type === 'transcription_complete') {
      const timeSinceComplete = Date.now() - new Date(lastMessage.timestamp || Date.now()).getTime();
      if (timeSinceComplete < SSE_CONFIG.COMPLETION_GRACE_PERIOD) { // Within grace period of completion
        console.log(\`[useSSE] Connection closed after transcription_complete (expected behavior) - \${timeSinceComplete}ms since completion\`);
        // Don't treat this as an error
        setConnected(false);

        // If auto-reconnect after complete is disabled, don't attempt to reconnect
        if (!SSE_CONFIG.AUTO_RECONNECT_AFTER_COMPLETE) {
          console.log('[useSSE] Auto-reconnect after complete is disabled, not reconnecting');
          return;
        }
      }
    }

    // Only close the connection and attempt reconnection if the readyState is CLOSED (2)
    // EventSource.CLOSED = 2
    if (eventSourceRef.current && eventSourceRef.current.readyState === 2) {
      console.log('[useSSE] Connection is in CLOSED state, will attempt to reconnect');

      // Now we can set connected to false
      setConnected(false);

      // Close the connection
      eventSourceRef.current.close();
      eventSourceRef.current = null;

      // Attempt reconnection with exponential backoff
      if (retryCount < maxRetries) {
        const nextRetryCount = retryCount + 1;
        const delay = reconnectDelay * Math.pow(2, retryCount);

        console.log(\`Attempting to reconnect SSE in \${delay}ms (attempt \${nextRetryCount} of \${maxRetries})\`);
        setRetryCount(nextRetryCount);

        // Store the timeout so we can clear it if needed
        const reconnectTimeout = setTimeout(() => {
          // Check again if we've received a transcription_complete message
          // This prevents unnecessary reconnections after completion
          const currentLastMessage = lastMessageRef.current;
          if (currentLastMessage && currentLastMessage.type === 'transcription_complete' && !SSE_CONFIG.AUTO_RECONNECT_AFTER_COMPLETE) {
            console.log('[useSSE] Skipping reconnect attempt because transcription is complete');
            return;
          }

          connect();
        }, delay);

        // Store the timeout reference for cleanup
        window._sseReconnectTimeout = reconnectTimeout;
      } else {
        console.error(\`Max SSE reconnection attempts reached for \${endpoint}\`);

        // Call disconnect handler if provided
        if (onDisconnect) {
          onDisconnect(new Error('Max reconnection attempts reached'));
        }
      }
    } else {
      console.log('[useSSE] Connection error occurred but connection is still active or connecting. Not reconnecting yet.');
    }
  };`;
  
  // Replace the old handler with the new one
  useSSEContent = useSSEContent.replace(oldOnerrorHandler, newOnerrorHandler);
}

// Write the updated content back to the file
fs.writeFileSync(useSSEPath, useSSEContent);

console.log('SSE error handling fixes applied successfully!');
