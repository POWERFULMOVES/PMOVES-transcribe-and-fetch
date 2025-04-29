/**
 * Test script for SSE implementation
 * This script tests both the frontend and backend SSE implementation
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { execSync } = require('child_process');

// Create a simple HTML file for testing SSE
const testHtmlPath = path.join(process.cwd(), 'test_sse.html');
const testHtmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSE Test</title>
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
            height: 400px;
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
    <h1>SSE Test</h1>
    
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
    
    <script>
        // Elements
        const statusEl = document.getElementById('connection-status');
        const eventsEl = document.getElementById('events');
        const connectBtn = document.getElementById('connect');
        const disconnectBtn = document.getElementById('disconnect');
        const clearBtn = document.getElementById('clear');
        
        // SSE connection
        let eventSource = null;
        
        // Parse SSE data
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
            
            try {
                statusEl.textContent = 'Connecting...';
                
                // Create EventSource
                eventSource = new EventSource('http://localhost:8000/api/search/preset-technical');
                
                // Handle connection open
                eventSource.onopen = function() {
                    statusEl.textContent = 'Connected';
                    addEvent('Connection', 'Connected to SSE endpoint');
                };
                
                // Handle messages
                eventSource.onmessage = function(event) {
                    console.log('Raw SSE message:', event.data);
                    
                    try {
                        const data = parseSseData(event.data);
                        addEvent(data.type || 'Message', data);
                    } catch (e) {
                        addEvent('Error', \`Failed to parse message: \${e.message}\`);
                        console.error('Error handling SSE message:', e);
                    }
                };
                
                // Handle errors
                eventSource.onerror = function(error) {
                    statusEl.textContent = 'Error';
                    addEvent('Error', 'SSE connection error');
                    console.error('SSE connection error:', error);
                };
            } catch (error) {
                statusEl.textContent = 'Failed to connect';
                addEvent('Error', \`Failed to create EventSource: \${error.message}\`);
                console.error('Failed to create EventSource:', error);
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
        
        // Event listeners
        connectBtn.addEventListener('click', connect);
        disconnectBtn.addEventListener('click', disconnect);
        clearBtn.addEventListener('click', clearEvents);
    </script>
</body>
</html>
`;

// Create a simple Node.js server to serve the test HTML
const serverScript = `
const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    if (req.url === '/') {
        fs.readFile('test_sse.html', (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading test_sse.html');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    } else {
        res.writeHead(404);
        res.end('Not found');
    }
});

server.listen(3001, () => {
    console.log('Test server running at http://localhost:3001');
});
`;

// Write the test HTML file
fs.writeFileSync(testHtmlPath, testHtmlContent);
console.log(`Created test HTML file: ${testHtmlPath}`);

// Function to test the SSE implementation
async function testSseImplementation() {
    console.log('Testing SSE implementation...');
    
    // Check if the backend server is running
    let backendRunning = false;
    
    // Try multiple endpoints to check if backend is running
    const endpoints = [
        'http://localhost:8000/api/health',
        'http://localhost:8000/',
        'http://localhost:8000/api/search/preset-technical'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`Trying to connect to ${endpoint}...`);
            const response = execSync(`curl -s -o /dev/null -w "%{http_code}" ${endpoint}`, { encoding: 'utf8' });
            if (response === '200' || response === '204' || response === '302') {
                backendRunning = true;
                console.log(`Successfully connected to ${endpoint}`);
                break;
            }
        } catch (error) {
            console.log(`Could not connect to ${endpoint}`);
        }
    }
    
    if (!backendRunning) {
        console.log('\nBackend server might not be running or accessible.');
        console.log('Do you want to continue anyway? (y/n)');
        
        const response = await new Promise(resolve => {
            process.stdin.once('data', (data) => {
                resolve(data.toString().trim().toLowerCase());
            });
        });
        
        if (response !== 'y' && response !== 'yes') {
            console.log('\nPlease start the backend server:');
            console.log('cd backend && python -m app.main');
            console.log('Then run this test script again');
            return;
        }
    } else {
        console.log('Backend server is running');
    }
    
    console.log('Starting test server...');
    
    // Start the test server
    const testServer = http.createServer((req, res) => {
        if (req.url === '/') {
            fs.readFile(testHtmlPath, (err, data) => {
                if (err) {
                    res.writeHead(500);
                    res.end('Error loading test_sse.html');
                    return;
                }
                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.end(data);
            });
        } else {
            res.writeHead(404);
            res.end('Not found');
        }
    });
    
    testServer.listen(3001, () => {
        console.log('Test server running at http://localhost:3001');
        console.log('Open http://localhost:3001 in your browser to test the SSE implementation');
        console.log('Press Ctrl+C to stop the test server');
    });
}

// Run the test
testSseImplementation().catch(console.error);
