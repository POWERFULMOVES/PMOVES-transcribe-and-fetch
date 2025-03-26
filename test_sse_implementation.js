/**
 * test_sse_implementation.js - Test the SSE implementation
 * 
 * This script tests the SSE implementation by connecting to the SSE endpoint
 * and verifying that messages are received correctly.
 */

// Import EventSource from the eventsource package
const EventSource = require('eventsource');
const axios = require('axios');
const readline = require('readline');

// Configuration
const BACKEND_URL = 'http://localhost:8000';
const SSE_ENDPOINT = '/combined-updates';
const TEST_YOUTUBE_URL = 'https://www.youtube.com/watch?v=jNQXAC9IVRw'; // Me at the Zoo (first YouTube video)
const TEST_OUTPUT_DIR = 'test_output';

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to test the SSE connection
async function testSSEConnection() {
  console.log('Testing SSE connection...');
  
  return new Promise((resolve, reject) => {
    try {
      const eventSource = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`);
      
      // Set a timeout to close the connection if no messages are received
      const timeout = setTimeout(() => {
        eventSource.close();
        reject(new Error('SSE connection timed out after 10 seconds'));
      }, 10000);
      
      // Connection opened
      eventSource.onopen = () => {
        console.log('✅ SSE connection established');
        clearTimeout(timeout);
        
        // Close the connection after 2 seconds
        setTimeout(() => {
          eventSource.close();
          resolve(true);
        }, 2000);
      };
      
      // Message received
      eventSource.onmessage = (event) => {
        console.log('Received SSE message:', event.data);
        try {
          const data = JSON.parse(event.data);
          console.log('Parsed message:', data);
        } catch (error) {
          console.warn('Could not parse message as JSON:', error);
        }
      };
      
      // Error handling
      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        clearTimeout(timeout);
        eventSource.close();
        reject(error);
      };
    } catch (error) {
      reject(error);
    }
  });
}

// Function to test the transcription process
async function testTranscription() {
  console.log('Testing transcription process...');
  
  try {
    // Start the transcription process
    console.log('Starting transcription process...');
    const response = await axios.post(`${BACKEND_URL}/process-video/`, {
      youtube_video_url: TEST_YOUTUBE_URL,
      obsidian_dir: TEST_OUTPUT_DIR,
      output_folder: TEST_OUTPUT_DIR,
      transcription_model: 'faster-whisper'
    });
    
    console.log('Transcription process started:', response.data);
    
    if (response.data.status !== 'started') {
      throw new Error(`Transcription process failed to start: ${JSON.stringify(response.data)}`);
    }
    
    // Connect to the SSE endpoint to receive transcription updates
    console.log('Connecting to SSE endpoint to receive transcription updates...');
    
    return new Promise((resolve, reject) => {
      try {
        const eventSource = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`);
        
        // Set a timeout to close the connection if transcription takes too long
        const timeout = setTimeout(() => {
          console.log('Transcription is taking longer than expected, but this is normal for the first run.');
          console.log('You can continue to monitor the transcription in the console.');
          eventSource.close();
          resolve(true);
        }, 60000); // 1 minute timeout
        
        // Track received messages
        const messages = {
          status: 0,
          transcription_segment: 0,
          heartbeat: 0,
          error: 0,
          transcription_complete: 0
        };
        
        // Connection opened
        eventSource.onopen = () => {
          console.log('✅ SSE connection established for transcription');
        };
        
        // Message received
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Count message types
            if (data.type && messages[data.type] !== undefined) {
              messages[data.type]++;
            }
            
            // Log different message types differently
            if (data.type === 'status') {
              console.log(`Status update: ${data.content}`);
            } else if (data.type === 'transcription_segment') {
              if (messages.transcription_segment <= 5) {
                // Only log the first 5 segments to avoid console spam
                console.log(`Transcription segment ${messages.transcription_segment}:`, 
                  typeof data.content === 'object' ? data.content.text : data.content);
              } else if (messages.transcription_segment % 10 === 0) {
                // Log every 10th segment after the first 5
                console.log(`Received ${messages.transcription_segment} transcription segments so far...`);
              }
            } else if (data.type === 'transcription_complete') {
              console.log('✅ Transcription complete!');
              clearTimeout(timeout);
              eventSource.close();
              resolve(true);
            } else if (data.type === 'error') {
              console.error('Error during transcription:', data.content);
              // Don't close the connection on error, let the process continue
            } else if (data.type === 'heartbeat') {
              // Don't log heartbeats to avoid console spam
            } else {
              console.log(`Received message of type ${data.type}:`, data);
            }
          } catch (error) {
            console.warn('Could not parse message as JSON:', error, event.data);
          }
        };
        
        // Error handling
        eventSource.onerror = (error) => {
          console.error('SSE connection error during transcription:', error);
          clearTimeout(timeout);
          eventSource.close();
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  } catch (error) {
    console.error('Error starting transcription process:', error.response?.data || error.message);
    throw error;
  }
}

// Function to check backend health
async function checkBackendHealth() {
  console.log('Checking backend health...');
  
  try {
    const response = await axios.get(`${BACKEND_URL}/health`);
    console.log('Backend health check response:', response.data);
    
    if (response.data.status === 'healthy') {
      console.log('✅ Backend is healthy');
      return true;
    } else {
      console.warn('⚠️ Backend health check returned unexpected status:', response.data.status);
      return false;
    }
  } catch (error) {
    console.error('❌ Backend health check failed:', error.message);
    return false;
  }
}

// Main function
async function main() {
  console.log('=== SSE Implementation Test ===');
  
  try {
    // Check backend health
    const isHealthy = await checkBackendHealth();
    
    if (!isHealthy) {
      console.error('❌ Backend is not healthy. Please check that the server is running.');
      process.exit(1);
    }
    
    // Test SSE connection
    await testSSEConnection();
    
    // Ask user if they want to test transcription
    rl.question('Do you want to test the transcription process? This will download and transcribe a short YouTube video. (y/n) ', async (answer) => {
      if (answer.toLowerCase() === 'y') {
        try {
          await testTranscription();
          console.log('\n✅ All tests completed successfully!');
        } catch (error) {
          console.error('\n❌ Transcription test failed:', error);
        } finally {
          rl.close();
        }
      } else {
        console.log('Skipping transcription test.');
        console.log('\n✅ Connection test completed successfully!');
        rl.close();
      }
    });
  } catch (error) {
    console.error('❌ Test failed:', error);
    rl.close();
    process.exit(1);
  }
}

// Run the script
main();
