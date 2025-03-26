from datetime import datetime
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.logging import RichHandler
import asyncio
from collections import deque
import threading

console = Console()

class SSEMonitor:
    def __init__(self, max_history: int = 1000):
        self.messages = deque(maxlen=max_history)
        self.connections = {}
        self.console = Console()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Setup file handler
        file_handler = logging.FileHandler(
            log_dir / f'sse_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        # Setup rich console handler
        console_handler = RichHandler(console=self.console)
        
        # Configure logger
        self.logger = logging.getLogger('sse_monitor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def track_connection(self, client_id: str, endpoint: str):
        """Track new SSE connection"""
        self.connections[client_id] = {
            'endpoint': endpoint,
            'connected_at': datetime.now(),
            'message_count': 0
        }
        self.logger.info(f"New SSE connection: {client_id} to {endpoint}")
        self._update_display()

    def track_disconnection(self, client_id: str):
        """Track SSE disconnection"""
        if client_id in self.connections:
            conn_info = self.connections.pop(client_id)
            duration = datetime.now() - conn_info['connected_at']
            self.logger.info(
                f"SSE disconnection: {client_id} from {conn_info['endpoint']} "
                f"(duration: {duration}, messages: {conn_info['message_count']})"
            )
            self._update_display()

    def track_message(self, client_id: str, message_type: str, data: Any, direction: str = 'sent'):
        """Track SSE message"""
        timestamp = datetime.now()
        
        # Format message for storage
        message_info = {
            'timestamp': timestamp,
            'client_id': client_id,
            'type': message_type,
            'data': data,
            'direction': direction
        }
        
        # Add to history
        self.messages.append(message_info)
        
        # Update connection stats
        if client_id in self.connections:
            self.connections[client_id]['message_count'] += 1
        
        # Log the message
        try:
            data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            self.logger.info(
                f"SSE {direction}: {client_id} - {message_type} - {data_str[:200]}..."
                if len(data_str) > 200 else data_str
            )
        except Exception as e:
            self.logger.error(f"Error logging message: {str(e)}")
        
        self._update_display()

    def _update_display(self):
        """Update the console display with current status"""
        # Create connections table
        conn_table = Table(title="Active SSE Connections")
        conn_table.add_column("Client ID")
        conn_table.add_column("Endpoint")
        conn_table.add_column("Connected At")
        conn_table.add_column("Messages")
        
        for client_id, info in self.connections.items():
            conn_table.add_row(
                client_id,
                info['endpoint'],
                info['connected_at'].strftime("%H:%M:%S"),
                str(info['message_count'])
            )
        
        # Create recent messages table
        msg_table = Table(title="Recent SSE Messages")
        msg_table.add_column("Time")
        msg_table.add_column("Client")
        msg_table.add_column("Type")
        msg_table.add_column("Direction")
        msg_table.add_column("Data Preview")
        
        for msg in list(self.messages)[-5:]:  # Show last 5 messages
            try:
                data_preview = json.dumps(msg['data'])[:50] + "..." if len(str(msg['data'])) > 50 else str(msg['data'])
                msg_table.add_row(
                    msg['timestamp'].strftime("%H:%M:%S"),
                    msg['client_id'][:8],
                    msg['type'],
                    msg['direction'],
                    data_preview
                )
            except Exception as e:
                self.logger.error(f"Error formatting message: {str(e)}")
        
        # Clear console and display tables
        self.console.clear()
        self.console.print(conn_table)
        self.console.print(msg_table)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about SSE connections"""
        return {
            'active_connections': len(self.connections),
            'total_messages': sum(c['message_count'] for c in self.connections.values()),
            'connections': self.connections
        }

    def get_message_history(self, limit: Optional[int] = None) -> list:
        """Get message history with optional limit"""
        messages = list(self.messages)
        if limit:
            messages = messages[-limit:]
        return messages

# Create global monitor instance
sse_monitor = SSEMonitor()

def format_sse_message(data: Any, event_type: str) -> str:
    """Format a message for SSE transmission and log it"""
    message = f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"
    return message

def monitor_sse_message(client_id: str, message: str, endpoint: str):
    """Monitor an SSE message being sent"""
    try:
        # Parse the message to extract type and data
        message_data = message.replace('data: ', '').strip()
        parsed_data = json.loads(message_data)
        
        sse_monitor.track_message(
            client_id=client_id,
            message_type=parsed_data.get('type', 'unknown'),
            data=parsed_data.get('data'),
            direction='sent'
        )
    except Exception as e:
        logging.error(f"Error monitoring SSE message: {str(e)}")

# Example middleware for FastAPI
async def sse_monitoring_middleware(request, call_next):
    """Middleware to monitor SSE connections"""
    response = await call_next(request)
    
    # Check if this is an SSE connection
    if response.headers.get('content-type') == 'text/event-stream':
        client_id = request.headers.get('client-id', f'client_{datetime.now().timestamp()}')
        sse_monitor.track_connection(client_id, request.url.path)
        
        # Wrap response to monitor messages
        original_send = response.send
        
        async def monitored_send(message):
            if message.get('type') == 'http.response.body':
                monitor_sse_message(client_id, message.get('body', b'').decode(), request.url.path)
            await original_send(message)
        
        response.send = monitored_send
        
        # Track disconnection when client disconnects
        @response.background
        async def disconnect_tracking():
            try:
                await response.is_disconnected()
                sse_monitor.track_disconnection(client_id)
            except Exception as e:
                logging.error(f"Error tracking disconnection: {str(e)}")
    
    return response 