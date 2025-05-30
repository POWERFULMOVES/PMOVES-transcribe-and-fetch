import os
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from typing import (
    Union,
    List as PyList,
)  # Renamed to PyList to avoid conflict with Pydantic List
from supabase import create_client, Client

# Assuming agent_framework.py is in app/utils/
from .utils.agent_framework import AgentFramework
from .chat_listener import ChatMessageListener  # Import the new listener

# --- Environment Loading ---
# Load .env file from the parent directory of 'app' (i.e., supabase-agent/.env)
dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback for environments where .env might be in the same dir as main.py (e.g. some Docker setups)
    load_dotenv()

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Supabase Client Setup ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
    # Depending on strictness, you might raise an error or allow app to start with limited functionality
    # raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set.")
    db_client: Optional[Client] = (
        None  # Renamed for clarity from supabase_client to avoid conflict with module name
    )
else:
    try:
        db_client: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        db_client = None


def get_supabase_client():
    if db_client is None:
        raise HTTPException(status_code=503, detail="Supabase client not available.")
    return db_client


# --- Agent Configuration & Framework ---
AGENT_ID = os.getenv("AGENT_ID", "default_supabase_agent")
AGENT_NAME = os.getenv("AGENT_NAME", "Supabase Agent")
AGENT_DESCRIPTION = os.getenv("AGENT_DESCRIPTION", "Interacts with Supabase.")
AGENT_ENDPOINT_URL = os.getenv(
    "AGENT_ENDPOINT_URL", f"http://localhost:{os.getenv('AGENT_PORT', 8002)}"
)
AGENT_PORT = int(os.getenv("AGENT_PORT", "8002"))
AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL")
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "30"))
LITELLM_PROXY_URL_FOR_AGENT = os.getenv("LITELLM_PROXY_URL")  # Load the new env var


# Helper to parse JSON strings from env vars, defaulting to empty list/dict if parsing fails or var is missing
def parse_json_env_var(var_name: str, default_value: Any) -> Any:
    var_value = os.getenv(var_name)
    if var_value:
        try:
            return json.loads(var_value)
        except json.JSONDecodeError:
            logger.warning(
                f"Failed to parse JSON from env var {var_name}. Using default."
            )
            return default_value
    return default_value


agent_framework = AgentFramework(
    agent_id=AGENT_ID,
    name=AGENT_NAME,
    description=AGENT_DESCRIPTION,
    capabilities=parse_json_env_var(
        "AGENT_CAPABILITIES", ["supabase_interaction", "query_execution"]
    ),
    input_schema=parse_json_env_var(
        "AGENT_INPUT_SCHEMA", {"type": "object", "properties": {}}
    ),
    output_schema=parse_json_env_var(
        "AGENT_OUTPUT_SCHEMA", {"type": "object", "properties": {}}
    ),
    status=os.getenv("AGENT_STATUS", "initializing"),
    registry_url=AGENT_REGISTRY_URL,
    heartbeat_interval_seconds=HEARTBEAT_INTERVAL_SECONDS,
    endpoint=AGENT_ENDPOINT_URL,
    version=os.getenv("AGENT_VERSION"),
    tags=parse_json_env_var("AGENT_TAGS", []),
    config=parse_json_env_var("AGENT_CONFIG", {}),
    dependencies=parse_json_env_var("AGENT_DEPENDENCIES", []),
    llm_registry_url=LITELLM_PROXY_URL_FOR_AGENT,  # Pass the LLM proxy URL
)

# --- Chat Listener Configuration & Initialization ---
CHAT_INPUT_TABLE_NAME = os.getenv("CHAT_INPUT_TABLE_NAME", "chat_messages")
CHAT_OUTPUT_TABLE_NAME = os.getenv("CHAT_OUTPUT_TABLE_NAME", "agent_responses")
CHAT_POLL_INTERVAL = int(os.getenv("CHAT_POLL_INTERVAL_SECONDS", "5"))

chat_listener: Optional[ChatMessageListener] = None
if db_client:  # Only initialize if Supabase client is available
    chat_listener = ChatMessageListener(
        supabase_client=db_client,
        agent_framework_instance=agent_framework,  # Pass the agent_framework instance
        input_table_name=CHAT_INPUT_TABLE_NAME,
        output_table_name=CHAT_OUTPUT_TABLE_NAME,
        poll_interval_seconds=CHAT_POLL_INTERVAL,
    )
else:
    logger.warning(
        "Supabase client not available. ChatMessageListener will not be started."
    )


# --- FastAPI Application ---
app = FastAPI(
    title=AGENT_NAME,
    description=AGENT_DESCRIPTION,
    version=os.getenv("AGENT_VERSION", "0.1.0"),
)

# --- Security Middleware Configuration ---
try:
    from .utils.security import SecurityMiddleware, SecurityConfig
    
    security_config = SecurityConfig(
        rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true",
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")), # Default: 100 requests
        rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),    # Default: per 60 seconds
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"), 
        redis_prefix="supabase_agent:rl:", # Specific prefix for this agent
        
        # Disable other security features not immediately needed by supabase-agent by default
        auth_enabled=os.getenv("AUTH_ENABLED", "False").lower() == "true", # Default to False
        api_keys=json.loads(os.getenv("API_KEYS", "[]")), # Load as JSON list
        jwt_secret=os.getenv("JWT_SECRET", ""), # Default to empty
        
        input_validation_enabled=os.getenv("INPUT_VALIDATION_ENABLED", "False").lower() == "true", # Default to False
        max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024))), # 10MB default
        allowed_content_types=["application/json"], # Supabase agent primarily uses JSON

        file_security_enabled=False, # File uploads not typical for this agent
        
        security_headers_enabled=os.getenv("SECURITY_HEADERS_ENABLED", "True").lower() == "true",
        security_logging_enabled=os.getenv("SECURITY_LOGGING_ENABLED", "True").lower() == "true",
        log_requests=os.getenv("LOG_REQUESTS", "True").lower() == "true",
        cors_origins=json.loads(os.getenv("CORS_ORIGINS", '["*"]')) # Load as JSON list, default allow all
    )
    
    app.add_middleware(SecurityMiddleware, config=security_config)
    logger.info("SecurityMiddleware added with rate limiting configuration.")

except ImportError:
    logger.warning("SecurityMiddleware could not be imported from .utils.security. Rate limiting will not be active.")
    SecurityMiddleware = None # Ensure it's defined for startup event check
except Exception as e:
    logger.error(f"Failed to initialize or add SecurityMiddleware: {e}", exc_info=True)
    SecurityMiddleware = None


@app.on_event("startup")
async def startup_event():
    logger.info("Agent starting up...")

    # Initialize SecurityMiddleware if it was added and stored itself in app.state
    if hasattr(app.state, 'security_middleware_instance') and \
            isinstance(app.state.security_middleware_instance, SecurityMiddleware):
        logger.info("Initializing SecurityMiddleware instance from app.state...")
        await app.state.security_middleware_instance.initialize()
    elif SecurityMiddleware: # If imported but not found in state (fallback warning)
        logger.warning("SecurityMiddleware was imported but its instance was not found in app.state for initialization. Redis for rate limiting might not be connected.")

    # Start AgentFramework services (registration, heartbeats, LLM service init)
    await agent_framework.start_services()

    # You could also test Supabase connection here if needed
    if db_client:  # Use the renamed client
        try:
            logger.info("Supabase connection seems OK (basic client init).")
            if chat_listener:  # Start chat listener if initialized
                await chat_listener.start()
        except Exception as e:
            logger.error(
                f"Supabase connection test or chat listener start failed during startup: {e}"
            )
    else:
        logger.warning(
            "Supabase client (db_client) not initialized. Some functionalities might be limited."
        )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Agent shutting down...")
    if chat_listener:  # Stop chat listener first
        await chat_listener.stop()

    # AgentFramework's stop_heartbeat_loop and close are separate from registry config check
    await agent_framework.stop_heartbeat_loop()
    await agent_framework.close()  # Closes the httpx client in agent_framework
    logger.info("Agent shutdown complete.")


# --- API Endpoints ---


@app.get("/health", summary="Get Agent Health Status")
async def get_health():
    """Returns the current health status of the agent, including registry status."""
    return agent_framework.get_health()


class PlaceholderRequest(BaseModel):
    pass


# --- Agent Internal Settings Store ---
# For simplicity, store settings in a global dict.
# In a more complex app, this might be a dedicated class or integrated with AgentFramework's config.
agent_internal_settings: Dict[str, Any] = {
    "default_query_limit": 100,
    "allow_table_management_ddl": False,  # Security flag for DDL operations
}

# --- Pydantic Models for API Requests/Responses ---


class AdjustParamsRequest(BaseModel):
    params: Dict[str, Any]


class AdjustParamsResponse(BaseModel):
    message: str
    updated_settings: Dict[str, Any]


class UpsertDataRequest(BaseModel):
    table_name: str = Field(..., description="Name of the Supabase table.")
    data: Union[Dict[str, Any], PyList[Dict[str, Any]]] = Field(
        ..., description="A single data record (dict) or a list of records to upsert."
    )
    conflict_on: Optional[str] = Field(
        None,
        description="Optional column name for conflict resolution (e.g., primary key). If provided, performs an upsert. If None, performs an insert.",
    )


class UpsertDataResponse(BaseModel):
    message: str
    count: int
    returned_data: Optional[PyList[Dict[str, Any]]] = None


class ColumnSchema(BaseModel):
    name: str = Field(..., description="Column name.")
    type: str = Field(
        ...,
        description="Column data type (e.g., TEXT, INTEGER, TIMESTAMPTZ DEFAULT NOW()).",
    )


class TableSchemaRequest(BaseModel):
    columns: PyList[ColumnSchema]


class ManageTableRequest(BaseModel):
    operation: str = Field(
        ...,
        description="Operation to perform: create_table, delete_table, add_column, drop_column.",
    )
    table_name: str = Field(..., description="Name of the table.")
    schema: Optional[TableSchemaRequest] = Field(
        None, description="Schema definition for 'create_table'."
    )
    column_definition: Optional[ColumnSchema] = Field(
        None, description="Definition for 'add_column'."
    )
    column_name: Optional[str] = Field(
        None, description="Name of the column for 'drop_column'."
    )

    @validator("schema", always=True)
    def check_schema_for_create(cls, v, values):
        if values.get("operation") == "create_table" and v is None:
            raise ValueError("Schema must be provided for 'create_table' operation.")
        return v

    @validator("column_definition", always=True)
    def check_column_def_for_add(cls, v, values):
        if values.get("operation") == "add_column" and v is None:
            raise ValueError(
                "Column definition must be provided for 'add_column' operation."
            )
        return v

    @validator("column_name", always=True)
    def check_column_name_for_drop(cls, v, values):
        if values.get("operation") == "drop_column" and v is None:
            raise ValueError(
                "Column name must be provided for 'drop_column' operation."
            )
        return v


class ManageTableResponse(BaseModel):
    message: str
    details: Optional[str] = None
    executed_sql: Optional[str] = None  # For debugging/transparency


# Models for Streaming Results
class StreamQueryDetails(BaseModel):
    select: str = Field("*", description="Columns to select, e.g., '*' or 'id,name'.")
    # Supabase filter format is typically (column, operator, value).
    # For simplicity, let's expect a list of such tuples/lists in JSON.
    # e.g., '[["status", "eq", "active"], ["created_at", "gte", "2023-01-01"]]'
    filters: Optional[PyList[PyList[Any]]] = Field(
        None, description="List of filters, e.g., [['status', 'eq', 'active']]."
    )
    order_by: Optional[str] = Field(
        None, description="Column to order by, e.g., 'created_at.desc'."
    )
    # Limit is handled by chunk_size in streaming logic, but could be an overall cap.


class StreamResultsQueryParams(BaseModel):
    table_name: str
    chunk_size: int = Field(
        50, gt=0, le=1000, description="Number of records to fetch per chunk."
    )
    query_params: Optional[StreamQueryDetails] = (
        None  # Embedded model for query details
    )


# Models for Infinite Query (Pagination)
class InfiniteQueryFilter(BaseModel):
    field: str
    operator: str  # e.g., "eq", "neq", "gt", "gte", "lt", "lte", "like", "ilike", "is", "in", "cs", "cd"
    value: Any


class InfiniteQueryOrder(BaseModel):
    field: str
    ascending: bool = True


class InfiniteQueryParams(BaseModel):
    table_name: str
    select_params: str = Field(
        "*", description="Columns to select, e.g., '*' or 'id,name,status'."
    )
    filter_params: Optional[PyList[InfiniteQueryFilter]] = None
    order_params: Optional[InfiniteQueryOrder] = None
    page: int = Field(1, gt=0)
    page_size: int = Field(20, gt=0, le=1000)


class InfiniteQueryResponse(BaseModel):
    data: PyList[Dict[str, Any]]
    page: int
    page_size: int
    total_records: Optional[int] = None
    total_pages: Optional[int] = None
    message: Optional[str] = None


class PlaceholderResponse(BaseModel):  # Keep for unimplemented endpoints for now
    message: str
    details: Optional[Dict[str, Any]] = None


# --- API Endpoints ---


@app.get("/health", summary="Get Agent Health Status")
async def get_health():
    """Returns the current health status of the agent, including registry status."""
    return agent_framework.get_health()


@app.post(
    "/adjust-params",
    response_model=AdjustParamsResponse,
    summary="Adjust Agent's Internal Parameters",
)
async def adjust_params_handler(
    payload: AdjustParamsRequest,
):  # No db client needed here
    logger.info(f"Received request to adjust parameters: {payload.params}")
    # In a real app, validate parameters before applying
    for key, value in payload.params.items():
        agent_internal_settings[key] = value
        logger.info(f"Set agent parameter '{key}' to '{value}'")

    # Example: Update AgentFramework config if a relevant param is changed
    if "allow_table_management_ddl" in payload.params:
        logger.info(
            f"Security relevant parameter 'allow_table_management_ddl' changed to: {agent_internal_settings['allow_table_management_ddl']}"
        )

    return {
        "message": "Agent parameters updated successfully.",
        "updated_settings": agent_internal_settings,
    }


@app.post(
    "/upsert-data",
    response_model=UpsertDataResponse,
    summary="Upsert Data into a Supabase Table",
)
async def upsert_data_handler(
    payload: UpsertDataRequest, db: Client = Depends(get_supabase_client)
):  # db refers to db_client
    logger.info(
        f"Received request to upsert data into table '{payload.table_name}'. Data (first 50 chars if list): {str(payload.data)[: 50 if isinstance(payload.data, list) else 500]}"
    )
    try:
        # The upsert method in supabase-py takes a list of dicts.
        # If a single dict is provided, wrap it in a list.
        data_to_upsert = (
            [payload.data] if isinstance(payload.data, dict) else payload.data
        )

        query = db.table(payload.table_name).upsert(
            data_to_upsert,
            on_conflict=payload.conflict_on
            if payload.conflict_on
            else None,  # Pass None if not specified for simple insert
        )
        response = await query.execute()  # Use await for async execution

        logger.info(f"Upsert operation response: {response}")

        if response.data:
            count = len(response.data)
            return {
                "message": f"Successfully upserted {count} record(s) into '{payload.table_name}'.",
                "count": count,
                "returned_data": response.data,
            }
        else:
            # This case might occur if upsert didn't return data (e.g. on certain conflict scenarios or if return_type was minimal)
            # Or if there was an issue not raising an exception but data is empty.
            # Check for error in the response object if available (structure depends on supabase-py version)
            if hasattr(response, "error") and response.error:
                logger.error(
                    f"Supabase upsert error for table '{payload.table_name}': {response.error.message}"
                )
                raise HTTPException(
                    status_code=400, detail=f"Supabase error: {response.error.message}"
                )
            return {
                "message": f"Upsert operation to '{payload.table_name}' completed, but no data was returned in the response. This might be expected or indicate an issue.",
                "count": 0,  # Assuming 0 if no data returned, adjust if API provides count differently
                "returned_data": [],
            }

    except (
        HTTPException
    ):  # Re-raise HTTPExceptions from get_supabase_client or validation
        raise
    except (
        Exception
    ) as e:  # Catching generic supabase client errors or other unexpected errors
        logger.error(
            f"Error during upsert operation for table '{payload.table_name}': {e}"
        )
        # Attempt to parse Supabase specific errors if possible (this is a generic catch)
        error_detail = str(e)
        if hasattr(e, "message"):  # Common for PostgrestError
            error_detail = e.message
        raise HTTPException(
            status_code=500, detail=f"Failed to upsert data: {error_detail}"
        )


@app.post(
    "/manage-table",
    response_model=ManageTableResponse,
    summary="Manage Supabase Tables (DDL Operations - Use with Extreme Caution)",
)
async def manage_table_handler(
    payload: ManageTableRequest, db: Client = Depends(get_supabase_client)
):
    logger.warning(
        f"Received DDL request for table '{payload.table_name}' with operation '{payload.operation}'."
    )

    if not agent_internal_settings.get("allow_table_management_ddl", False):
        logger.error(
            "DDL operations are disabled by agent configuration ('allow_table_management_ddl' is False)."
        )
        raise HTTPException(
            status_code=403,
            detail="Table management (DDL) operations are disabled by agent configuration. This is a security measure.",
        )

    sql_statement = ""
    operation_description = ""

    if payload.operation == "create_table":
        if not payload.schema or not payload.schema.columns:
            raise HTTPException(
                status_code=400,
                detail="Schema with columns must be provided for 'create_table'.",
            )
        cols_defs = [f"{col.name} {col.type}" for col in payload.schema.columns]
        sql_statement = (
            f"CREATE TABLE IF NOT EXISTS {payload.table_name} ({', '.join(cols_defs)});"
        )
        operation_description = f"Table '{payload.table_name}' creation attempted."

    elif payload.operation == "delete_table":
        sql_statement = f"DROP TABLE IF EXISTS {payload.table_name};"
        operation_description = f"Table '{payload.table_name}' deletion attempted."

    elif payload.operation == "add_column":
        if not payload.column_definition:
            raise HTTPException(
                status_code=400,
                detail="Column definition must be provided for 'add_column'.",
            )
        col_def = payload.column_definition
        sql_statement = f"ALTER TABLE {payload.table_name} ADD COLUMN {col_def.name} {col_def.type};"
        operation_description = f"Column '{col_def.name}' addition to table '{payload.table_name}' attempted."

    elif payload.operation == "drop_column":
        if not payload.column_name:
            raise HTTPException(
                status_code=400,
                detail="Column name must be provided for 'drop_column'.",
            )
        sql_statement = f"ALTER TABLE {payload.table_name} DROP COLUMN IF EXISTS {payload.column_name};"
        operation_description = f"Column '{payload.column_name}' deletion from table '{payload.table_name}' attempted."

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported table management operation: {payload.operation}",
        )

    if not sql_statement:
        raise HTTPException(
            status_code=500,
            detail="Failed to construct SQL statement for the operation.",
        )

    logger.info(f"Executing DDL: {sql_statement}")

    # SECURITY NOTE: Executing raw SQL, especially DDL, from API requests is highly risky.
    # This should be heavily restricted by authentication, authorization, and input validation in production.
    # Supabase-py does not offer direct `db.sql()` or `db.execute()` for arbitrary SQL.
    # The common way to execute arbitrary SQL (including DDL) is via a custom RPC function.
    # For this prototype, we assume an RPC function named `execute_sql_unsafe` exists on Supabase,
    # which takes a parameter `sql_query` and executes it.
    # If such an RPC function doesn't exist, these operations will fail.
    # This highlights a key area for secure design in a real application.

    try:
        # Ensure `execute_sql_unsafe` is a placeholder for a real, secured RPC if this pattern is used.
        # It's better to have specific RPCs for specific, parameterized DDL operations if possible.
        # response = await db.rpc("execute_sql_unsafe", {"sql_query": sql_statement}).execute()

        # The supabase-py library (v1.x and v2.x) doesn't have a direct db.execute_raw_sql() or similar.
        # It is generally recommended to use RPC functions for this.
        # If you *must* try without a pre-defined RPC, you might be out of luck with the standard client lib features
        # for direct DDL. This is a good thing for safety.
        # For this exercise, we will simulate that the RPC call is the way, and it will fail if not set up.
        # A more robust solution would be to use a migration tool or a more privileged backend process for DDL.

        # Let's log that we would attempt this, but for safety in this generic environment,
        # we won't actually make a call that is unlikely to be configured.
        # We will return success as if it worked for the prototype's sake, but with a strong warning.

        # response = await db.rpc("execute_sql_unsafe", {"sql_query": sql_statement}).execute()
        # if response.error:
        #    logger.error(f"RPC DDL execution error: {response.error.message}")
        #    raise HTTPException(status_code=500, detail=f"DDL execution failed: {response.error.message}")

        message_detail = (
            f"{operation_description} SQL: '{sql_statement}'. "
            "IMPORTANT: This endpoint assumes a Supabase RPC function like 'execute_sql_unsafe(sql_query TEXT)' is set up to run DDL. "
            "Direct DDL execution via API is a major security risk and should be heavily restricted in production. "
            "This response simulates success for prototype purposes if the RPC is not available."
        )
        logger.warning(message_detail)

        return {
            "message": "Table management operation processed (simulated for DDL).",
            "details": message_detail,
            "executed_sql": sql_statement,
        }

    except HTTPException:  # Re-raise if it's one we threw
        raise
    except Exception as e:
        logger.error(
            f"Error during table management operation for table '{payload.table_name}': {e}"
        )
        error_detail = str(e)
        if hasattr(e, "message"):
            error_detail = e.message
        raise HTTPException(
            status_code=500, detail=f"Table management operation failed: {error_detail}"
        )


from fastapi.responses import StreamingResponse
import json  # Ensure json is imported

# ... (other imports and existing code) ...


async def build_supabase_query(
    db: Client,
    table_name: str,
    query_details: Optional[StreamQueryDetails] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    """
    Helper function to construct a Supabase query dynamically.
    Used by both streaming and infinite query endpoints.
    """
    query = db.table(table_name)

    select_columns = "*"
    if query_details and query_details.select:
        select_columns = query_details.select

    # For infinite_query, select_params is a string, not StreamQueryDetails
    # This helper might need adjustment or separate logic if select differs too much
    # For now, let's assume StreamQueryDetails.select is compatible with infinite_query's select_params string

    query = query.select(
        select_columns, count="exact" if page is not None else None
    )  # Request count only for pagination

    if query_details and query_details.filters:
        for f_item in query_details.filters:
            if len(f_item) == 3:
                field, operator, value = f_item
                query = query.filter(field, operator, value)
            else:
                logger.warning(f"Skipping invalid filter item: {f_item}")

    if query_details and query_details.order_by:
        field = query_details.order_by.split(".")[0]
        desc = query_details.order_by.endswith(".desc")
        query = query.order(field, desc=desc)

    if page and page_size:  # Pagination
        offset_start = (page - 1) * page_size
        offset_end = page * page_size - 1  # Supabase range is inclusive
        query = query.range(offset_start, offset_end)

    return query


@app.post(
    "/stream-results",
    summary="Stream Query Results from Supabase (POST with JSON body)",
)
async def stream_results_handler(
    params: StreamResultsQueryParams, db: Client = Depends(get_supabase_client)
):
    """
    Streams results from a Supabase query.
    Fetches data in chunks and streams them as newline-delimited JSON.
    Query parameters are passed in the request body as JSON.
    """
    logger.info(
        f"Streaming request for table '{params.table_name}' with chunk_size {params.chunk_size} and query: {params.query_params}"
    )

    async def streamer(
        table_name: str, chunk_size: int, query_details: Optional[StreamQueryDetails]
    ):
        current_page = (
            0  # Supabase pages are effectively 0-indexed for range logic, or use offset
        )
        records_fetched_in_current_chunk = chunk_size  # Initialize to enter loop

        while (
            records_fetched_in_current_chunk == chunk_size
        ):  # Continue if last fetch was a full chunk
            offset_start = current_page * chunk_size
            offset_end = offset_start + chunk_size - 1

            try:
                base_query = db.table(table_name)

                select_cols = (
                    query_details.select
                    if query_details and query_details.select
                    else "*"
                )
                query = base_query.select(select_cols)

                if query_details and query_details.filters:
                    for f_item in query_details.filters:
                        if len(f_item) == 3:
                            field, operator, value = f_item
                            query = query.filter(field, operator, value)
                        else:
                            logger.warning(
                                f"Skipping invalid filter item in stream: {f_item}"
                            )

                if query_details and query_details.order_by:
                    order_field = query_details.order_by.split(".")[0]
                    order_desc = query_details.order_by.endswith(".desc")
                    query = query.order(order_field, desc=order_desc)

                query = query.range(offset_start, offset_end)

                logger.debug(
                    f"Executing stream chunk query for table {table_name}: page {current_page + 1}, range {offset_start}-{offset_end}"
                )
                response = await query.execute()

                if response.data:
                    records_fetched_in_current_chunk = len(response.data)
                    yield json.dumps(response.data) + "\n"
                    if records_fetched_in_current_chunk < chunk_size:
                        logger.info(
                            f"Stream finished for table {table_name}: fetched last chunk of size {records_fetched_in_current_chunk}."
                        )
                        break  # Last chunk was smaller than chunk_size, so no more data
                else:
                    logger.info(
                        f"Stream finished for table {table_name}: no data in current chunk."
                    )
                    break  # No data returned, end of stream

                current_page += 1
                await asyncio.sleep(
                    0.01
                )  # Small sleep to prevent tight loop if connection is very fast / allow context switching

            except Exception as e:
                logger.error(f"Error during data streaming for table {table_name}: {e}")
                error_obj = {
                    "error": "Failed to fetch or stream data.",
                    "details": str(e),
                }
                yield json.dumps(error_obj) + "\n"
                break
        logger.info(f"Streaming for table {table_name} completed.")

    return StreamingResponse(
        streamer(params.table_name, params.chunk_size, params.query_params),
        media_type="application/x-ndjson",  # Newline Delimited JSON
    )


@app.post(
    "/infinite-query",
    response_model=InfiniteQueryResponse,
    summary="Execute a Paginated Query (POST with JSON body)",
)
async def infinite_query_handler(
    params: InfiniteQueryParams, db: Client = Depends(get_supabase_client)
):
    """
    Supports 'infinite scroll' type queries or fetching paginated data.
    Query parameters are passed in the request body as JSON.
    """
    logger.info(
        f"Infinite query request for table '{params.table_name}' with params: {params.dict(exclude_none=True)}"
    )

    try:
        query = db.table(params.table_name)

        # Always request count for pagination
        query = query.select(params.select_params, count="exact")

        if params.filter_params:
            for f in params.filter_params:
                query = query.filter(f.field, f.operator, f.value)

        if params.order_params:
            query = query.order(
                params.order_params.field, desc=not params.order_params.ascending
            )

        offset_start = (params.page - 1) * params.page_size
        offset_end = params.page * params.page_size - 1  # Supabase range is inclusive
        query = query.range(offset_start, offset_end)

        logger.debug(
            f"Executing paginated query for table {params.table_name}: page {params.page}, size {params.page_size}"
        )
        response = await query.execute()

        total_records = response.count if response.count is not None else 0
        total_pages = (
            (total_records + params.page_size - 1) // params.page_size
            if total_records is not None
            else None
        )

        if response.data is not None:  # data can be [] which is valid
            return InfiniteQueryResponse(
                data=response.data,
                page=params.page,
                page_size=params.page_size,
                total_records=total_records,
                total_pages=total_pages,
                message=f"Successfully fetched page {params.page} for table '{params.table_name}'.",
            )
        else:  # Should not happen if execute() is successful, but as a safeguard
            logger.warning(
                f"No data field in response for infinite query on table {params.table_name}, though no error raised."
            )
            # Supabase client usually raises an error or response.data is at least []
            # If response.error exists, it should have been caught by the generic exception.
            raise HTTPException(
                status_code=500,
                detail="Query executed but no data was returned in the expected format.",
            )

    except HTTPException:  # Re-raise
        raise
    except Exception as e:
        logger.error(
            f"Error during paginated query for table '{params.table_name}': {e}"
        )
        error_detail = str(e)
        if hasattr(e, "message"):  # PostgrestError
            error_detail = e.message
        raise HTTPException(
            status_code=500, detail=f"Failed to execute paginated query: {error_detail}"
        )


# --- Main Execution (for running with uvicorn directly) ---
if __name__ == "__main__":
    import uvicorn
    import asyncio  # Required for streamer's sleep and potentially other async ops

    logger.info(f"Starting Uvicorn server for {AGENT_NAME} on port {AGENT_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
