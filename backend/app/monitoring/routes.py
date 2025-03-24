from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from .sse_monitor import sse_monitor
import json

router = APIRouter()

@router.get("/monitoring/sse/stats")
async def get_sse_stats():
    """Get current SSE connection statistics"""
    return sse_monitor.get_connection_stats()

@router.get("/monitoring/sse/history")
async def get_sse_history(limit: int = 100):
    """Get SSE message history"""
    return sse_monitor.get_message_history(limit)

@router.get("/monitoring/sse/dashboard", response_class=HTMLResponse)
async def sse_dashboard():
    """Simple dashboard to view SSE activity"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE Monitor Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            function updateStats() {
                fetch('/monitoring/sse/stats')
                    .then(response => response.json())
                    .then(stats => {
                        document.getElementById('activeConnections').textContent = stats.active_connections;
                        document.getElementById('totalMessages').textContent = stats.total_messages;
                        
                        const connectionsList = document.getElementById('connectionsList');
                        connectionsList.innerHTML = '';
                        Object.entries(stats.connections).forEach(([clientId, info]) => {
                            connectionsList.innerHTML += `
                                <div class="p-4 bg-gray-100 rounded mb-2">
                                    <div class="font-bold">${clientId}</div>
                                    <div>Endpoint: ${info.endpoint}</div>
                                    <div>Messages: ${info.message_count}</div>
                                    <div>Connected: ${new Date(info.connected_at).toLocaleTimeString()}</div>
                                </div>
                            `;
                        });
                    });
            }

            function updateHistory() {
                fetch('/monitoring/sse/history?limit=10')
                    .then(response => response.json())
                    .then(messages => {
                        const historyList = document.getElementById('messageHistory');
                        historyList.innerHTML = '';
                        messages.forEach(msg => {
                            historyList.innerHTML += `
                                <div class="p-4 ${msg.direction === 'sent' ? 'bg-blue-100' : 'bg-green-100'} rounded mb-2">
                                    <div class="font-bold">${msg.type}</div>
                                    <div>Client: ${msg.client_id}</div>
                                    <div>Time: ${new Date(msg.timestamp).toLocaleTimeString()}</div>
                                    <div class="mt-2 p-2 bg-white rounded">
                                        <pre class="whitespace-pre-wrap">${JSON.stringify(msg.data, null, 2)}</pre>
                                    </div>
                                </div>
                            `;
                        });
                    });
            }

            // Update every second
            setInterval(() => {
                updateStats();
                updateHistory();
            }, 1000);

            // Initial update
            document.addEventListener('DOMContentLoaded', () => {
                updateStats();
                updateHistory();
            });
        </script>
    </head>
    <body class="bg-gray-50 p-8">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl font-bold mb-8">SSE Monitor Dashboard</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h2 class="text-xl font-bold mb-4">Active Connections</h2>
                    <div class="bg-white p-6 rounded-lg shadow-md">
                        <div class="text-4xl font-bold mb-2" id="activeConnections">-</div>
                        <div class="text-gray-600">Active Connections</div>
                        <div class="text-4xl font-bold mt-4" id="totalMessages">-</div>
                        <div class="text-gray-600">Total Messages</div>
                    </div>
                    
                    <div class="mt-8">
                        <h3 class="text-lg font-bold mb-4">Connection Details</h3>
                        <div id="connectionsList"></div>
                    </div>
                </div>
                
                <div>
                    <h2 class="text-xl font-bold mb-4">Recent Messages</h2>
                    <div id="messageHistory"></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html 