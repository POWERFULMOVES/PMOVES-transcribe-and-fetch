#!/usr/bin/env python3
"""
fix_sse_v6.py - Comprehensive SSE Implementation Fix

This script fixes the SSE (Server-Sent Events) implementation in the PMOVES transcription project:
1. Re-enables the SSE monitoring middleware
2. Optimizes the SSE monitor for high message volumes
3. Enhances terminal output with rich formatting
4. Standardizes SSE message format across all endpoints

Usage:
    python fix_sse_v6.py

The script will create backup files before making changes.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rich console
console = Console()

def create_backup(file_path):
    """Create a backup of the file before modifying it."""
    backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup: {backup_path}")
    return backup_path

def fix_main_py():
    """Fix the main.py file to re-enable SSE monitoring middleware."""
    file_path = "backend/app/main.py"
    
    # Create backup
    backup_path = create_backup(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the commented middleware line
    updated_content = re.sub(
        r'# Temporarily disable SSE monitoring middleware\s*# app\.middleware\("http"\)\(sse_monitoring_middleware\)',
        '# Enable SSE monitoring middleware\napp.middleware("http")(sse_monitoring_middleware)',
        content
    )
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"Updated {file_path} - Re-enabled SSE monitoring middleware")
    console.print(Panel(f"[green]✓ Successfully re-enabled SSE monitoring middleware in {file_path}[/green]"))

def fix_sse_monitor():
    """Optimize the SSE monitor for high message volumes."""
    file_path = "backend/app/monitoring/sse_monitor.py"
    
    # Create backup
    backup_path = create_backup(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the track_message method for better performance
    updated_track_message = """
    def track_message(self, client_id: str, message_type: str, data: Any, direction: str = 'sent'):
        '''Track SSE message with optimized performance for high-frequency messages.'''
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
        
        # Log the message with rich formatting
        try:
            # Only log certain message types to avoid console spam
            if message_type in ['status', 'error', 'heartbeat', 'connection_closed']:
                data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
                
                # Use different colors based on message type
                if message_type == 'status':
                    self.logger.info(f"[SSE {direction}] {client_id} - [cyan]{message_type}[/cyan] - {data_str[:200]}...")
                elif message_type == 'error':
                    self.logger.error(f"[SSE {direction}] {client_id} - [red]{message_type}[/red] - {data_str[:200]}...")
                elif message_type == 'heartbeat':
                    # Don't log heartbeats to reduce noise
                    pass
                elif message_type == 'connection_closed':
                    self.logger.info(f"[SSE {direction}] {client_id} - [yellow]{message_type}[/yellow] - {data_str[:200]}...")
                else:
                    # For other types, log with less detail
                    self.logger.info(f"[SSE {direction}] {client_id} - {message_type}")
            elif message_type == 'transcription_segment':
                # For transcription segments, only log occasionally to reduce spam
                if self.connections[client_id]['message_count'] % 10 == 0:
                    self.logger.info(f"[SSE {direction}] {client_id} - [green]{message_type}[/green] - Segment #{self.connections[client_id]['message_count']}")
        except Exception as e:
            self.logger.error(f"Error logging message: {str(e)}")
        
        # Only update display periodically to prevent performance issues
        current_time = time.time()
        if not hasattr(self, '_last_display_update') or current_time - self._last_display_update > 2.0:
            self._last_display_update = current_time
            self._update_display()
    """
    
    # Replace the track_message method
    pattern = r'def track_message\(self, client_id: str, message_type: str, data: Any, direction: str = \'sent\'\):.*?self\._update_display\(\)'
    updated_content = re.sub(pattern, updated_track_message.strip(), content, flags=re.DOTALL)
    
    # Update the _update_display method for better performance
    updated_update_display = """
    def _update_display(self):
        '''Update the console display with current status (optimized for performance)'''
        # Only show active connections and recent messages
        if not self.connections:
            return  # Skip display update if no connections
            
        # Create connections table
        conn_table = Table(title="Active SSE Connections")
        conn_table.add_column("Client ID", style="cyan")
        conn_table.add_column("Endpoint", style="green")
        conn_table.add_column("Connected At", style="yellow")
        conn_table.add_column("Messages", style="magenta")
        
        for client_id, info in self.connections.items():
            conn_table.add_row(
                client_id[:8] + "...",  # Truncate long client IDs
                info['endpoint'],
                info['connected_at'].strftime("%H:%M:%S"),
                str(info['message_count'])
            )
        
        # Create recent messages table (only show last 3 messages to reduce clutter)
        msg_table = Table(title="Recent SSE Messages")
        msg_table.add_column("Time", style="cyan")
        msg_table.add_column("Client", style="green")
        msg_table.add_column("Type", style="yellow")
        msg_table.add_column("Direction", style="magenta")
        msg_table.add_column("Data Preview", style="blue")
        
        # Filter out heartbeat messages and only show last 3 non-heartbeat messages
        filtered_messages = [
            msg for msg in list(self.messages)
            if msg['type'] != 'heartbeat'
        ][-3:]
        
        for msg in filtered_messages:
            try:
                # Format data preview based on message type
                if isinstance(msg['data'], dict):
                    data_preview = json.dumps(msg['data'])[:50] + "..." if len(json.dumps(msg['data'])) > 50 else json.dumps(msg['data'])
                else:
                    data_preview = str(msg['data'])[:50] + "..." if len(str(msg['data'])) > 50 else str(msg['data'])
                
                # Use different styles based on message type
                type_style = "green"
                if msg['type'] == 'error':
                    type_style = "red bold"
                elif msg['type'] == 'status':
                    type_style = "cyan"
                elif msg['type'] == 'transcription_segment':
                    type_style = "yellow"
                
                msg_table.add_row(
                    msg['timestamp'].strftime("%H:%M:%S"),
                    msg['client_id'][:8],
                    f"[{type_style}]{msg['type']}[/{type_style}]",
                    msg['direction'],
                    data_preview
                )
            except Exception as e:
                self.logger.error(f"Error formatting message: {str(e)}")
        
        # Clear console and display tables
        self.console.clear()
        self.console.print(conn_table)
        self.console.print(msg_table)
        
        # Add summary statistics
        total_messages = sum(c['message_count'] for c in self.connections.values())
        self.console.print(f"[bold]Total connections:[/bold] {len(self.connections)} | [bold]Total messages:[/bold] {total_messages}")
    """
    
    # Replace the _update_display method
    pattern = r'def _update_display\(self\):.*?self\.console\.print\(msg_table\)'
    updated_content = re.sub(pattern, updated_update_display.strip(), content, flags=re.DOTALL)
    
    # Add missing imports
    if "import time" not in content:
        updated_content = re.sub(
            r'import threading',
            'import threading\nimport time',
            updated_content
        )
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"Updated {file_path} - Optimized SSE monitor for high message volumes")
    console.print(Panel(f"[green]✓ Successfully optimized SSE monitor in {file_path}[/green]"))

def fix_transcribe_py():
    """Enhance the terminal output for transcription with rich formatting."""
    file_path = "backend/app/transcribe1.py"
    
    # Create backup
    backup_path = create_backup(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add rich formatting imports if not already present
    if "from rich.panel import Panel" not in content:
        imports_to_add = """
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
"""
        # Add after existing imports
        updated_content = re.sub(
            r'import re\n',
            f'import re\n{imports_to_add}\n',
            content
        )
    else:
        updated_content = content
    
    # Add console initialization
    if "console = Console()" not in updated_content:
        updated_content = re.sub(
            r'logger = logging\.getLogger\(__name__\)',
            'logger = logging.getLogger(__name__)\n\n# Initialize rich console\nconsole = Console()',
            updated_content
        )
    
    # Enhance the transcribe_audio function with rich formatting
    # Find the function definition
    transcribe_audio_pattern = r'async def transcribe_audio\(.*?\):'
    match = re.search(transcribe_audio_pattern, updated_content)
    
    if match:
        # Find the position to insert the rich formatting code
        insert_pos = match.end()
        
        # Add rich formatting code after the function definition
        rich_formatting_code = """
    # Create a rich progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[bold green]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        transcription_task = progress.add_task("[cyan]Transcribing audio...", total=None)
        """
        
        # Insert the rich formatting code
        updated_content = updated_content[:insert_pos] + rich_formatting_code + updated_content[insert_pos:]
    
    # Enhance the segment processing with rich formatting
    segment_processing_pattern = r'# Process segments with minimal delay\s+for idx, segment in enumerate\(segments_gen\):'
    updated_segment_processing = """
        # Process segments with rich formatting
        for idx, segment in enumerate(segments_gen):
            # Update progress
            progress.update(transcription_task, advance=1, description=f"[cyan]Transcribing segment {idx+1}")
"""
    
    updated_content = re.sub(segment_processing_pattern, updated_segment_processing, updated_content)
    
    # Enhance the segment display
    segment_display_pattern = r'# Send transcription segment immediately for real-time updates.*?logger\.info\(f"Sent transcription segment: {segment_text} at {start_time}"\)'
    updated_segment_display = """
                # Format segment for display
                segment_panel = Panel(
                    f"{segment_text}",
                    title=f"[bold green]Segment {idx+1}[/bold green]",
                    subtitle=f"[yellow]{start_time} - {end_time}[/yellow]",
                    border_style="green"
                )
                
                # Display in console with rich formatting
                if idx % 5 == 0:  # Only show every 5th segment to reduce console spam
                    console.print(segment_panel)
                
                # Send transcription segment immediately for real-time updates
                await transcription_queue.put(json.dumps({
                    "type": "transcription_segment",
                    "content": {
                        "watch_url": watch_url,
                        "video_id": video_id,
                        "id": idx,
                        "start": start_time,
                        "end": end_time,
                        "text": segment_text
                    },
                    "timestamp": datetime.now().isoformat()
                }))
                logger.info(f"Sent transcription segment: {segment_text[:50]}... at {start_time}")
"""
    
    updated_content = re.sub(segment_display_pattern, updated_segment_display, updated_content, flags=re.DOTALL)
    
    # Add datetime import if not already present
    if "from datetime import datetime" not in updated_content:
        updated_content = re.sub(
            r'import re\n',
            'import re\nfrom datetime import datetime\n',
            updated_content
        )
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"Updated {file_path} - Enhanced terminal output for transcription")
    console.print(Panel(f"[green]✓ Successfully enhanced terminal output in {file_path}[/green]"))

def fix_combined_updates_endpoint():
    """Standardize the SSE message format in the combined-updates endpoint."""
    file_path = "backend/app/main.py"
    
    # Read the file (we already have a backup from fix_main_py)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the combined-updates endpoint
    combined_updates_pattern = r'@app\.get\("/combined-updates"\)\nasync def get_combined_updates\(request: Request\):.*?return response'
    match = re.search(combined_updates_pattern, content, re.DOTALL)
    
    if match:
        combined_updates_code = match.group(0)
        
        # Add a standardized message formatter function
        formatter_function = """
# Standardized SSE message formatter
def format_sse_message(message_type: str, content: Any, metadata: dict = None) -> str:
    '''Format a message for SSE transmission with consistent structure.'''
    message = {
        "type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    if metadata:
        message["metadata"] = metadata
        
    return f"data: {json.dumps(message)}\\n\\n"

"""
        
        # Insert the formatter function before the combined-updates endpoint
        updated_content = content.replace(combined_updates_code, formatter_function + combined_updates_code)
        
        # Update the event_generator to use the formatter function
        event_generator_pattern = r'async def event_generator\(\):.*?yield f"data: {completion_message}\\n\\n"'
        match = re.search(event_generator_pattern, updated_content, re.DOTALL)
        
        if match:
            event_generator_code = match.group(0)
            
            # Replace the connection message
            updated_event_generator = event_generator_code.replace(
                """connection_message = json.dumps({
            "type": "status",
            "content": f"SSE connection established from {client_host}",
            "timestamp": datetime.now().isoformat()
        })
        yield f"data: {connection_message}\\n\\n\"""",
                """# Send immediate confirmation that connection is established
        yield format_sse_message(
            "status",
            f"SSE connection established from {client_host}"
        )"""
            )
            
            # Replace the heartbeat message
            updated_event_generator = updated_event_generator.replace(
                """heartbeat_msg = json.dumps({
                        'type': 'heartbeat', 
                        'timestamp': datetime.now().isoformat()
                    })
                    console.print(f"[dim]Sending heartbeat: {heartbeat_msg}[/dim]")
                    yield f"data: {heartbeat_msg}\\n\\n\"""",
                """console.print(f"[dim]Sending heartbeat[/dim]")
                    yield format_sse_message('heartbeat', 'ping')"""
            )
            
            # Replace the completion message
            updated_event_generator = updated_event_generator.replace(
                """completion_message = json.dumps({
                "type": "connection_closed",
                "content": "SSE connection closed - transcription complete",
                "timestamp": datetime.now().isoformat()
            })
            console.print("[bold blue]Sending connection closed message[/bold blue]")
            yield f"data: {completion_message}\\n\\n\"""",
                """console.print("[bold blue]Sending connection closed message[/bold blue]")
            yield format_sse_message(
                "connection_closed",
                "SSE connection closed - transcription complete"
            )"""
            )
            
            # Update the event_generator in the content
            updated_content = updated_content.replace(event_generator_code, updated_event_generator)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Updated {file_path} - Standardized SSE message format")
        console.print(Panel(f"[green]✓ Successfully standardized SSE message format in {file_path}[/green]"))
    else:
        logger.error("Could not find combined-updates endpoint in main.py")
        console.print(Panel(f"[red]✗ Could not find combined-updates endpoint in {file_path}[/red]"))

def main():
    """Main function to apply all fixes."""
    console.print(Panel.fit(
        "[bold cyan]PMOVES SSE Implementation Fix[/bold cyan]\n\n"
        "This script will fix the SSE implementation in the PMOVES transcription project:\n"
        "1. Re-enable the SSE monitoring middleware\n"
        "2. Optimize the SSE monitor for high message volumes\n"
        "3. Enhance terminal output with rich formatting\n"
        "4. Standardize SSE message format across all endpoints\n\n"
        "[yellow]Backups will be created before making changes.[/yellow]",
        title="fix_sse_v6.py",
        border_style="cyan"
    ))
    
    try:
        # Fix main.py to re-enable SSE monitoring middleware
        fix_main_py()
        
        # Fix sse_monitor.py to optimize for high message volumes
        fix_sse_monitor()
        
        # Fix transcribe1.py to enhance terminal output
        fix_transcribe_py()
        
        # Fix combined-updates endpoint to standardize SSE message format
        fix_combined_updates_endpoint()
        
        console.print(Panel(
            "[bold green]✓ All fixes applied successfully![/bold green]\n\n"
            "The SSE implementation has been fixed and optimized.\n"
            "You can now run the server with the improved SSE functionality.",
            title="Success",
            border_style="green"
        ))
    except Exception as e:
        logger.error(f"Error applying fixes: {str(e)}")
        console.print(Panel(
            f"[bold red]✗ Error applying fixes: {str(e)}[/bold red]\n\n"
            "Please check the logs for more details.",
            title="Error",
            border_style="red"
        ))

if __name__ == "__main__":
    main()
