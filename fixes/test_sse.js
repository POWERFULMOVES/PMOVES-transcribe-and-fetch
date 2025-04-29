// Simple test script for SSE endpoint
const eventsource = require('eventsource');
const EventSource = eventsource;

console.log('Connecting to SSE endpoint...');
const sse = new EventSource('http://localhost:8000/combined-updates');

sse.onopen = () => {
  console.log('Connection opened');
};

sse.onerror = (error) => {
  console.error('Error:', error);
  sse.close();
};

sse.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    console.log(`Received ${data.type} event:`, data);
    
    // Close after receiving a few messages
    if (data.type === 'heartbeat') {
      console.log('Received heartbeat, closing connection');
      sse.close();
      process.exit(0);
    }
  } catch (error) {
    console.error('Error parsing event data:', error);
  }
};

// Set a timeout to close the connection after 20 seconds
setTimeout(() => {
  console.log('Timeout reached, closing connection');
  sse.close();
  process.exit(0);
}, 20000);

console.log('Waiting for events...');
