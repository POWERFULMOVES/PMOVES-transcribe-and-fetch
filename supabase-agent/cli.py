import typer
import httpx
import os
import json
from dotenv import load_dotenv

# Load .env file from the current directory (supabase-agent/.env)
load_dotenv()

app = typer.Typer(help="CLI for interacting with the Supabase Agent.")

AGENT_ENDPOINT_URL = os.getenv("AGENT_ENDPOINT_URL", "http://localhost:8002")

@app.command()
def status():
    """
    Checks the health status of the Supabase Agent.
    """
    health_url = f"{AGENT_ENDPOINT_URL}/health"
    typer.echo(f"Checking agent health at: {health_url}")
    try:
        response = httpx.get(health_url, timeout=5.0)
        response.raise_for_status()
        health_data = response.json()
        typer.echo(typer.style("Agent is healthy!", fg=typer.colors.GREEN, bold=True))
        typer.echo(json.dumps(health_data, indent=2))
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent at {health_url}: {e}", fg=typer.colors.RED))
    except json.JSONDecodeError:
        typer.echo(typer.style("Failed to decode JSON response from health endpoint.", fg=typer.colors.RED))

@app.command()
def adjust_params(
    params_json: str = typer.Argument(..., help='JSON string of parameters to set. E.g., \'{"key": "value", "number": 123}\'')
):
    """
    Adjusts the agent's internal parameters.
    Example: supabase-agent-cli adjust-params '{"allow_table_management_ddl": true, "default_query_limit": 50}'
    """
    endpoint = f"{AGENT_ENDPOINT_URL}/adjust-params"
    typer.echo(f"Attempting to adjust parameters via: {endpoint}")
    try:
        params_dict = json.loads(params_json)
    except json.JSONDecodeError:
        typer.echo(typer.style("Invalid JSON string provided for parameters.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    payload = {"params": params_dict}
    try:
        response = httpx.post(endpoint, json=payload, timeout=10.0)
        response.raise_for_status() # Raise an exception for 4XX or 5XX status codes
        typer.echo(typer.style(f"Parameters adjusted successfully:", fg=typer.colors.GREEN))
        typer.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent: {e}", fg=typer.colors.RED))


@app.command()
def upsert_data(
    table_name: str = typer.Argument(..., help="Name of the table to upsert data into."),
    data_json: str = typer.Argument(..., help='JSON string of the data. Can be a single object or a list of objects. E.g., \'{"col1": "val1"}\' or \'[{"col1": "valA"}, {"col1": "valB"}]\'.'),
    conflict_on: str = typer.Option(None, "--conflict-on", "-c", help="Column name for conflict resolution (upsert behavior).")
):
    """
    Upserts data (single record or list of records) into a specified Supabase table.
    Example (single record): supabase-agent-cli upsert-data my_table '{"id": 1, "name": "Test"}' --conflict-on id
    Example (multiple records): supabase-agent-cli upsert-data my_table '[{"name": "First"}, {"name": "Second"}]'
    """
    endpoint = f"{AGENT_ENDPOINT_URL}/upsert-data"
    typer.echo(f"Attempting to upsert data into table '{table_name}' via: {endpoint}")
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError:
        typer.echo(typer.style("Invalid JSON string provided for data.", fg=typer.colors.RED))
        raise typer.Exit(code=1)
    
    payload = {"table_name": table_name, "data": data}
    if conflict_on:
        payload["conflict_on"] = conflict_on
    
    try:
        response = httpx.post(endpoint, json=payload, timeout=30.0) # Increased timeout for potentially larger data
        response.raise_for_status()
        typer.echo(typer.style(f"Data upserted successfully to table '{table_name}':", fg=typer.colors.GREEN))
        typer.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent: {e}", fg=typer.colors.RED))

@app.command()
def manage_table(
    operation: str = typer.Argument(..., help="Operation: create_table, delete_table, add_column, drop_column."),
    table_name: str = typer.Argument(..., help="Name of the table."),
    schema_json: str = typer.Option(None, "--schema", "-s", help='For create_table: JSON string of table schema. E.g., \'{"columns": [{"name": "id", "type": "SERIAL PRIMARY KEY"}, {"name": "data", "type": "TEXT"}]}\'.'),
    column_def_json: str = typer.Option(None, "--column-def", "-d", help='For add_column: JSON string of column definition. E.g., \'{"name": "new_col", "type": "VARCHAR(255)"}\'.'),
    column_name: str = typer.Option(None, "--column-name", "-n", help="For drop_column: Name of the column to drop.")
):
    """
    Manages Supabase tables (DDL operations). Requires 'allow_table_management_ddl' to be true in agent settings.
    Example (create table): supabase-agent-cli manage-table create_table new_stuff --schema '{"columns": [{"name": "id", "type": "INTEGER PRIMARY KEY"}, {"name": "value", "type": "TEXT"}]}'
    Example (add column): supabase-agent-cli manage-table add_column new_stuff --column-def '{"name": "extra_info", "type": "BOOLEAN DEFAULT FALSE"}'
    Example (drop column): supabase-agent-cli manage-table drop_column new_stuff --column-name extra_info
    Example (delete table): supabase-agent-cli manage-table delete_table new_stuff
    """
    endpoint = f"{AGENT_ENDPOINT_URL}/manage-table"
    typer.echo(f"Attempting to '{operation}' on table '{table_name}' via: {endpoint}")

    payload: dict[str, Any] = {"operation": operation, "table_name": table_name}

    if operation == "create_table":
        if not schema_json:
            typer.echo(typer.style("Error: --schema is required for 'create_table'.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
        try:
            payload["schema"] = json.loads(schema_json)
        except json.JSONDecodeError:
            typer.echo(typer.style("Invalid JSON for schema.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    elif operation == "add_column":
        if not column_def_json:
            typer.echo(typer.style("Error: --column-def is required for 'add_column'.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
        try:
            payload["column_definition"] = json.loads(column_def_json)
        except json.JSONDecodeError:
            typer.echo(typer.style("Invalid JSON for column definition.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    elif operation == "drop_column":
        if not column_name:
            typer.echo(typer.style("Error: --column-name is required for 'drop_column'.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
        payload["column_name"] = column_name
    elif operation != "delete_table": # delete_table needs no extra args beyond operation and table_name
        typer.echo(typer.style(f"Unknown or unsupported operation: {operation}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    try:
        response = httpx.post(endpoint, json=payload, timeout=20.0)
        response.raise_for_status()
        typer.echo(typer.style(f"Table management operation '{operation}' on table '{table_name}' processed successfully:", fg=typer.colors.GREEN))
        typer.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent: {e}", fg=typer.colors.RED))

@app.command()
def stream_results(
    table_name: str = typer.Argument(..., help="Name of the table to query."),
    chunk_size: int = typer.Option(50, "--chunk-size", "-cs", help="Number of records per stream chunk."),
    select: str = typer.Option("*", "--select", "-s", help="Columns to select, e.g., 'id,name'."),
    filters_json: str = typer.Option(None, "--filters", "-f", help="JSON string of filters, e.g., '[[\"status\",\"eq\",\"active\"]]'. Passed as 'filters' in query_params."),
    order_by: str = typer.Option(None, "--order-by", "-o", help="Order by column, e.g., 'created_at.desc'. Passed as 'order_by' in query_params.")
):
    """
    Streams results from a Supabase table query.
    Example: supabase-agent-cli stream-results my_table --filters '[["type", "eq", "important"]]' --order-by "timestamp.desc"
    """
    endpoint = f"{AGENT_ENDPOINT_URL}/stream-results"
    typer.echo(f"Streaming results from table '{table_name}' via: {endpoint}")

    query_params_dict = {"select": select}
    if filters_json:
        try:
            query_params_dict["filters"] = json.loads(filters_json)
        except json.JSONDecodeError:
            typer.echo(typer.style("Invalid JSON string for filters.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    if order_by:
        query_params_dict["order_by"] = order_by
        
    payload = {
        "table_name": table_name,
        "chunk_size": chunk_size,
        "query_params": query_params_dict if query_params_dict else None
    }
    
    try:
        with httpx.stream("POST", endpoint, json=payload, timeout=60.0) as response:
            response.raise_for_status()
            typer.echo(typer.style(f"Streaming data from '{table_name}':", fg=typer.colors.GREEN))
            for line in response.iter_lines():
                typer.echo(line) # Each line is a JSON string (list of records) or an error object
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent: {e}", fg=typer.colors.RED))


@app.command()
def infinite_query(
    table_name: str = typer.Argument(..., help="Name of the table to query."),
    select_params: str = typer.Option("*", help="JSON string for select columns, e.g., 'id,name'."),
    filter_params_json: str = typer.Option(None, "--filters", "-f", help='JSON string for filters, e.g., \'[{"field": "status", "operator": "eq", "value": "active"}]\'.'),
    order_params_json: str = typer.Option(None, "--order", "-o", help='JSON string for ordering, e.g., \'{"field": "created_at", "ascending": false}\'.'),
    page: int = typer.Option(1, help="Page number to fetch."),
    page_size: int = typer.Option(20, help="Number of records per page.")
):
    """
    Fetches paginated data from a Supabase table.
    Example: supabase-agent-cli infinite-query my_table --filters '[{"field":"category","operator":"eq","value":"news"}]' --page 2 --page-size 10
    """
    endpoint = f"{AGENT_ENDPOINT_URL}/infinite-query"
    typer.echo(f"Querying table '{table_name}' (page {page}, size {page_size}) via: {endpoint}")

    payload = {
        "table_name": table_name,
        "select_params": select_params,
        "page": page,
        "page_size": page_size
    }
    if filter_params_json:
        try:
            payload["filter_params"] = json.loads(filter_params_json)
        except json.JSONDecodeError:
            typer.echo(typer.style("Invalid JSON for filter_params.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    if order_params_json:
        try:
            payload["order_params"] = json.loads(order_params_json)
        except json.JSONDecodeError:
            typer.echo(typer.style("Invalid JSON for order_params.", fg=typer.colors.RED))
            raise typer.Exit(code=1)

    try:
        response = httpx.post(endpoint, json=payload, timeout=30.0)
        response.raise_for_status()
        typer.echo(typer.style(f"Paginated data from '{table_name}':", fg=typer.colors.GREEN))
        typer.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPStatusError as e:
        typer.echo(typer.style(f"HTTP error: {e.response.status_code} - {e.response.text}", fg=typer.colors.RED))
    except httpx.RequestError as e:
        typer.echo(typer.style(f"Failed to connect to agent: {e}", fg=typer.colors.RED))

# --- Supabase Client for CLI (for send-chat-message) ---
# This is separate from the agent's internal client.
# It's used by the CLI to directly interact with Supabase for message sending.
_cli_supabase_client = None

def get_cli_supabase_client():
    global _cli_supabase_client
    if _cli_supabase_client is None:
        load_dotenv() # Ensure .env is loaded for CLI context
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY") # Needs to be a key that can write to chat table
        if not supabase_url or not supabase_key:
            typer.echo(typer.style("SUPABASE_URL and SUPABASE_KEY must be set in .env for CLI to send messages.", fg=typer.colors.RED))
            raise typer.Exit(code=1)
        try:
            # Import create_client here to avoid making it a top-level dependency if CLI is just checking agent status
            from supabase import create_client, Client
            _cli_supabase_client: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            typer.echo(typer.style(f"Failed to initialize Supabase client for CLI: {e}", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    return _cli_supabase_client

@app.command()
def send_chat_message(
    user_id: str = typer.Argument(..., help="ID of the user sending the message."),
    session_id: str = typer.Argument(..., help="ID of the chat session."),
    message_text: str = typer.Argument(..., help="The text content of the message.")
):
    """
    Simulates a chat UI sending a message by inserting it into the chat input table.
    Requires SUPABASE_URL and SUPABASE_KEY (with write access) in .env.
    """
    chat_input_table = os.getenv("CHAT_INPUT_TABLE_NAME", "chat_messages")
    typer.echo(f"Attempting to send message to table '{chat_input_table}': User '{user_id}', Session '{session_id}'")

    try:
        db = get_cli_supabase_client()
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "message_text": message_text,
            "status": "new", # Default status for new messages
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = db.table(chat_input_table).insert(payload).execute()

        if response.data:
            typer.echo(typer.style(f"Message sent successfully to '{chat_input_table}'. ID: {response.data[0].get('id')}", fg=typer.colors.GREEN))
            typer.echo(json.dumps(response.data[0], indent=2))
        elif hasattr(response, 'error') and response.error:
            typer.echo(typer.style(f"Error sending message: {response.error.message}", fg=typer.colors.RED))
        else:
            typer.echo(typer.style(f"Message sending to '{chat_input_table}' did not return data or error. Response: {response}", fg=typer.colors.YELLOW))

    except typer.Exit: # Re-raise Exit exceptions from get_cli_supabase_client
        raise
    except Exception as e:
        typer.echo(typer.style(f"An unexpected error occurred while sending message: {e}", fg=typer.colors.RED))
        # Consider logging the full traceback here for debugging
        # import traceback
        # typer.echo(traceback.format_exc())


if __name__ == "__main__":
    from datetime import datetime, timezone # Add these for the CLI to run standalone if needed
    app()
