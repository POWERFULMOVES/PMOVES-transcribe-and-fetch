/**
 * simple_sse_test.js - Simple test for SSE connection
 */

// Import the EventSource constructor from the eventsource package
const EventSource = require('eventsource').EventSource;
const axios = require('axios');

// Configuration
const BACKEND_URL = 'http://localhost:8000';
const SSE_ENDPOINT = '/combined-updates';

console.log('=== Simple SSE Test ===');
console.log('Checking backend health...');

// Check backend health
axios.get(`${BACKEND_URL}/health`)
  .then(response => {
    console.log('Backend health check response:', response.data);
    
    if (response.data.status === 'healthy') {
      console.log('✅ Backend is healthy');
      testSSE();
    } else {
      console.warn('⚠️ Backend health check returned unexpected status:', response.data.status);
    }
  })
  .catch(error => {
    console.error('❌ Backend health check failed:', error.message);
  });

// Test SSE connection
function testSSE() {
  console.log('Testing SSE connection...');
  console.log('Creating EventSource...');
  
  try {
    // Log the EventSource constructor
    console.log('EventSource constructor:', EventSource);
    
    // Create the EventSource
    const es = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`);
    console.log('EventSource created:', es);
    
    // Set up event handlers
    es.onopen = () => {
      console.log('✅ SSE connection established');
      
      // Close the connection after 5 seconds
      setTimeout(() => {
        console.log('Closing SSE connection...');
        es.close();
        console.log('SSE connection closed');
      }, 5000);
    };
    
      es.onmessage = (event) => {
        console.log('Received SSE message:', event.data);
        try {
          // Remove the "data: " prefix if it exists
          const jsonStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;
          const data = JSON.parse(jsonStr);
          console.log('Parsed message:', data);
        } catch (error) {
          console.warn('Could not parse message as JSON:', error);
        }
      };
    
    es.onerror = (error) => {
      console.error('SSE connection error:', error);
    };
  } catch (error) {
    console.error('Error creating EventSource:', error);
  }
}
