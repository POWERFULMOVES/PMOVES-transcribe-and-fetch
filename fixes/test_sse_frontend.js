/**
 * Test script for frontend SSE implementation
 * This script tests the frontend SSE implementation by mocking the backend SSE endpoint
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Create a simple HTML file for testing the frontend SSE implementation
const testHtmlPath = path.join(process.cwd(), 'test_sse_frontend.html');
const testHtmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frontend SSE Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #status {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
        }
        #events {
            border: 1px solid #ccc;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .event {
            margin-bottom: 10px;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }
        .event-type {
            font-weight: bold;
            color: #0066cc;
        }
        .event-content {
            margin-left: 10px;
        }
        button {
            padding: 8px 16px;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0055aa;
        }
        .stage {
            display: inline-block;
            margin-right: 10px;
            padding: 5px 10px;
            background-color: #eee;
            border-radius: 4px;
        }
        .stage.active {
            background-color: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Frontend SSE Test</h1>
    
    <div id="status">Connection status: <span id="connection-status">Disconnected</span></div>
    
    <div id="stages">
        <div class="stage" id="stage-start">Start</div>
        <div class="stage" id="stage-search">Search</div>
        <div class="stage" id="stage-filter">Filter</div>
        <div class="stage" id="stage-combine">Combine</div>
        <div class="stage" id="stage-analyze">Analyze</div>
        <div class="stage" id="stage-complete">Complete</div>
    </div>
    
    <h2>Events</h2>
    <div id="events"></div>
    
    <button id="connect">Connect to SSE</button>
    <button id="disconnect">Disconnect</button>
    <button id="clear">Clear Events</button>
    
    <h2>Test Controls</h2>
    <button id="test-flow">Test Complete Flow</button>
    <button id="test-error">Test Error</button>
    
    <script>
        // Import the SSE helpers from the project
        // In a real test, you would import the actual SSE helpers from the project
        // For this test, we'll implement them here
        
        /**
         * Safely parse SSE event data
         * @param {string|object} data - The data from the SSE event
         * @returns {object} The parsed data object
         */
        function parseSseData(data) {
            if (!data) return null;
            
            try {
                // Check if data is already an object
                if (typeof data === 'object' && data !== null) {
                    return data;
                }
                
                // Try to parse as JSON
                return JSON.parse(data);
            } catch (e) {
                console.warn('Error parsing SSE data:', e);
                // Return as-is if parsing fails
                return { content: data, type: 'unknown' };
            }
        }
        
        /**
         * Create an EventSource with error handling
         * @param {string} url - The SSE endpoint URL
         * @param {function} onMessage - Callback for message events
         * @param {function} onError - Callback for error events
         * @returns {EventSource} The configured EventSource object
         */
        function createSafeEventSource(url, onMessage, onError) {
            console.log('Creating SSE connection to:', url);
            
            try {
                const eventSource = new EventSource(url);
                
                eventSource.onmessage = (event) => {
                    try {
                        console.log('Raw SSE message received:', event.data);
                        const data = parseSseData(event.data);
                        onMessage(data);
                    } catch (e) {
                        console.error('Error handling SSE message:', e);
                        if (onError) onError(e);
                    }
                };
                
                eventSource.onerror = (error) => {
                    console.error('SSE connection error:', error);
                    if (onError) onError(error);
                };
                
                eventSource.onopen = () => {
                    console.log('SSE connection opened successfully');
                };
                
                return eventSource;
            } catch (error) {
                console.error('Failed to create EventSource:', error);
                if (onError) onError(error);
                return null;
            }
        }
        
        // Elements
        const statusEl = document.getElementById('connection-status');
        const eventsEl = document.getElementById('events');
        const connectBtn = document.getElementById('connect');
        const disconnectBtn = document.getElementById('disconnect');
        const clearBtn = document.getElementById('clear');
        const testFlowBtn = document.getElementById('test-flow');
        const testErrorBtn = document.getElementById('test-error');
        
        // SSE connection
        let eventSource = null;
        
        // Add event to the events container
        function addEvent(eventType, data) {
            const eventEl = document.createElement('div');
            eventEl.className = 'event';
            
            const typeEl = document.createElement('div');
            typeEl.className = 'event-type';
            typeEl.textContent = \`[\${new Date().toLocaleTimeString()}] \${eventType}\`;
            
            const contentEl = document.createElement('div');
            contentEl.className = 'event-content';
            
            if (typeof data === 'object') {
                contentEl.textContent = JSON.stringify(data, null, 2);
            } else {
                contentEl.textContent = data;
            }
            
            eventEl.appendChild(typeEl);
            eventEl.appendChild(contentEl);
            eventsEl.appendChild(eventEl);
            
            // Scroll to bottom
            eventsEl.scrollTop = eventsEl.scrollHeight;
            
            // Update stage if applicable
            if (data && data.metadata && data.metadata.stage) {
                updateStage(data.metadata.stage);
            }
        }
        
        // Update the active stage
        function updateStage(stage) {
            // Reset all stages
            document.querySelectorAll('.stage').forEach(el => {
                el.classList.remove('active');
            });
            
            // Set active stage
            const stageEl = document.getElementById(\`stage-\${stage}\`);
            if (stageEl) {
                stageEl.classList.add('active');
            }
        }
        
        // Connect to SSE endpoint
        function connect() {
            if (eventSource) {
                eventSource.close();
            }
            
            statusEl.textContent = 'Connecting...';
            
            // In a real test, you would connect to the actual SSE endpoint
            // For this test, we'll connect to our mock SSE endpoint
            eventSource = createSafeEventSource('/sse-mock', (data) => {
                // Handle message
                addEvent(data.type || 'Message', data);
            }, (error) => {
                // Handle error
                statusEl.textContent = 'Error';
                addEvent('Error', 'SSE connection error');
            });
            
            if (eventSource) {
                statusEl.textContent = 'Connected';
                addEvent('Connection', 'Connected to SSE endpoint');
            } else {
                statusEl.textContent = 'Failed to connect';
                addEvent('Error', 'Failed to create EventSource');
            }
        }
        
        // Disconnect from SSE endpoint
        function disconnect() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
                statusEl.textContent = 'Disconnected';
                addEvent('Connection', 'Disconnected from SSE endpoint');
            }
        }
        
        // Clear events
        function clearEvents() {
            eventsEl.innerHTML = '';
            updateStage(null);
        }
        
        // Test complete flow
        function testFlow() {
            // Simulate a complete SSE flow
            addEvent('status', {
                type: 'status',
                content: 'Starting search operation',
                metadata: { stage: 'start' }
            });
            
            setTimeout(() => {
                addEvent('status', {
                    type: 'status',
                    content: 'Configuring search parameters',
                    metadata: { stage: 'search' }
                });
            }, 1000);
            
            setTimeout(() => {
                addEvent('status', {
                    type: 'status',
                    content: 'Executing search query',
                    metadata: { stage: 'filter' }
                });
            }, 2000);
            
            setTimeout(() => {
                addEvent('status', {
                    type: 'status',
                    content: 'Combining search results',
                    metadata: { stage: 'combine' }
                });
            }, 3000);
            
            setTimeout(() => {
                addEvent('status', {
                    type: 'status',
                    content: 'Analyzing search results',
                    metadata: { stage: 'analyze' }
                });
            }, 4000);
            
            setTimeout(() => {
                addEvent('results', {
                    type: 'results',
                    content: [
                        { id: 1, title: 'Result 1', score: 0.95 },
                        { id: 2, title: 'Result 2', score: 0.85 },
                        { id: 3, title: 'Result 3', score: 0.75 }
                    ],
                    metadata: { stage: 'complete' }
                });
            }, 5000);
            
            setTimeout(() => {
                addEvent('analysis', {
                    type: 'analysis',
                    content: 'This is the analysis of the search results.',
                    metadata: { provider: 'openai', stage: 'complete' }
                });
            }, 6000);
            
            setTimeout(() => {
                addEvent('complete', {
                    type: 'complete',
                    content: 'Search process complete',
                    metadata: { stage: 'complete' }
                });
            }, 7000);
        }
        
        // Test error
        function testError() {
            // Simulate an error in the SSE flow
            addEvent('status', {
                type: 'status',
                content: 'Starting search operation',
                metadata: { stage: 'start' }
            });
            
            setTimeout(() => {
                addEvent('status', {
                    type: 'status',
                    content: 'Configuring search parameters',
                    metadata: { stage: 'search' }
                });
            }, 1000);
            
            setTimeout(() => {
                addEvent('error', {
                    type: 'error',
                    content: 'An error occurred during search',
                    metadata: { stage: 'filter' }
                });
            }, 2000);
        }
        
        // Event listeners
        connectBtn.addEventListener('click', connect);
        disconnectBtn.addEventListener('click', disconnect);
        clearBtn.addEventListener('click', clearEvents);
        testFlowBtn.addEventListener('click', testFlow);
        testErrorBtn.addEventListener('click', testError);
    </script>
</body>
</html>
`;

// Create a simple Node.js server to serve the test HTML and mock SSE endpoint
const port = 3002;
const server = http.createServer((req, res) => {
    if (req.url === '/') {
        // Serve the test HTML
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(testHtmlContent);
    } else if (req.url === '/sse-mock') {
        // Mock SSE endpoint
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });
        
        // Send initial message
        res.write(`data: ${JSON.stringify({
            type: 'status',
            content: 'Connected to mock SSE endpoint',
            timestamp: new Date().toISOString(),
            metadata: { stage: 'start' }
        })}\n\n`);
        
        // Keep the connection alive with a heartbeat
        const heartbeatInterval = setInterval(() => {
            res.write(`data: ${JSON.stringify({
                type: 'heartbeat',
                content: 'ping',
                timestamp: new Date().toISOString()
            })}\n\n`);
        }, 10000);
        
        // Close the connection when the client disconnects
        req.on('close', () => {
            clearInterval(heartbeatInterval);
        });
    } else {
        // Not found
        res.writeHead(404);
        res.end('Not found');
    }
});

// Write the test HTML file
fs.writeFileSync(testHtmlPath, testHtmlContent);
console.log(`Created test HTML file: ${testHtmlPath}`);

// Start the server
server.listen(port, () => {
    console.log(`Frontend SSE test server running at http://localhost:${port}`);
    console.log(`Open http://localhost:${port} in your browser to test the frontend SSE implementation`);
    console.log('Press Ctrl+C to stop the server');
});
