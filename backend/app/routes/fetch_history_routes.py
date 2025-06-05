import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import aiofiles # Added for async file operations
from datetime import datetime # Added for created_at timestamp
from pydantic import BaseModel # Added for request/response models

from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import FileResponse, JSONResponse

# Adjust imports based on your project structure and where get_client is defined
# Assuming get_client is in psearchworking_export or a similar utility module
try:
    from ..psearchworking_export import get_client
except ImportError:
    # Fallback if the above structure is not correct, adjust as needed
    try:
        from backend.app.psearchworking_export import get_client
    except ImportError:
        get_client = None # Or raise an error if critical

# --- Pydantic Models for Create/Response ---

class FetchHistoryCreate(BaseModel):
    url: str
    title: str
    content_storage_path: str # Relative path/filename
    output_type: str
    upload_to_supabase: bool = False
    user_id: Optional[uuid.UUID] = None
    crawl_preset_id: Optional[uuid.UUID] = None
    # Example for engine_specific_parameters if needed directly in model
    # engine_specific_parameters: Optional[Dict[str, Any]] = None
    # raw_content_summary: Optional[str] = None # If short summary is also part of create model

class FetchHistoryResponse(FetchHistoryCreate):
    id: uuid.UUID
    supabase_storage_path: Optional[str] = None
    created_at: datetime


logger = logging.getLogger(__name__)
router = APIRouter()

# Define a base path for stored content if it's consistent
# This could also be an environment variable
CONTENT_STORAGE_BASE_DIR = Path(os.getenv('FETCHED_CONTENT_STORAGE_PATH', './fetched_content')).resolve()
try:
    CONTENT_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured fetched content storage directory exists: {CONTENT_STORAGE_BASE_DIR}")
except OSError as e:
    logger.error(f"CRITICAL: Could not create fetched content storage directory {CONTENT_STORAGE_BASE_DIR}: {e}. Content retrieval will fail.", exc_info=True)


def secure_join(base: Path, filename: str) -> Optional[Path]:
    """
    Safely join a base directory with a filename, preventing path traversal.
    Assumes 'filename' is just a name and not a relative path with '..'.
    """
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"Potentially unsafe filename detected: {filename}")
        return None
    
    # Normalize the base path
    resolved_base = base.resolve()
    
    # Join and resolve the full path
    full_path = (resolved_base / filename).resolve()

    # Check if the resolved path is still within the (resolved) base directory
    if full_path.parent == resolved_base or full_path == resolved_base : # full_path could be the base itself if filename is empty or "."
        return full_path
    
    logger.warning(f"Path traversal attempt blocked or invalid path. Base: '{resolved_base}', Filename: '{filename}', Resolved Full: '{full_path}'")
    return None


@router.get(
    "/fetch-history/{history_id}/content",
    tags=["Fetch History"],
    summary="Get fetched content for a history item",
    response_description="The fetched content (Markdown, JSON) or path to PDF",
)
async def get_fetch_history_item_content(history_id: uuid.UUID):
    """
    Retrieves the locally stored fetched content for a given fetch history item ID.

    - For Markdown or JSON content, the file content is returned directly.
    - For PDFs, a path or a mechanism to download/view the PDF is implied.
      (This initial version will return the path for PDFs).
    """
    logger.info(f"Request to get content for fetch history ID: {history_id}")

    supabase_client = None
    try:
        # Attempt to get the Supabase client
        if get_client is None: # This check itself implies a problem with the get_client import/availability
            logger.error("get_client function itself is None, cannot obtain Supabase client.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client source (get_client) is not available."
            )

        try:
            supabase_client = get_client()
        except ValueError as ve:
            logger.error(f"ValueError obtaining Supabase client: {ve}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database client configuration error: {ve}"
            )

        if not supabase_client:
            logger.error("get_client() returned None or a falsy value for Supabase client.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client unavailable (returned None)."
            )

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("id, content_storage_path, output_type, title, url, supabase_storage_path") # Added supabase_storage_path
            .eq("id", str(history_id))
            .single() # Expecting one item
            .execute
        )

        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error fetching history item {history_id}: {response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {response.error.message}")
        
        if not hasattr(response, 'data') or not response.data:
            logger.warning(f"Fetch history item with ID {history_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fetch history item not found.")

        item_data = response.data
        
        # Safely get and process output_type first, as it's needed for Supabase content handling
        output_type_value = item_data.get("output_type")
        if output_type_value is None:
            output_type = "unknown"
            logger.warning(f"output_type is null for history_id {history_id}. Defaulting to 'unknown'.")
        else:
            output_type = str(output_type_value).lower()

        item_title = item_data.get("title", "Untitled") # Keep for response consistency
        item_url = item_data.get("url") # Keep for response consistency
        local_content_path_str = item_data.get("content_storage_path") # Path to local file, might be primary or fallback
        db_item_supabase_path = item_data.get("supabase_storage_path")

        BUCKET_NAME = "fetched_content" # TODO: Move to config

        if db_item_supabase_path:
            logger.info(f"Supabase path found for {history_id}: {db_item_supabase_path}. Attempting Supabase download.")
            try:
                file_bytes = await asyncio.to_thread(
                    supabase_client.storage.from_(BUCKET_NAME).download, path=db_item_supabase_path
                )
                logger.info(f"Successfully downloaded content from Supabase for {history_id} from path {db_item_supabase_path}")

                response_payload_base = {
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type,
                    "content_storage_path": db_item_supabase_path, # Reflecting that it's from Supabase
                    "served_from": "supabase",
                }

                if output_type in ["markdown", "md", "text", "json", "html", "xml", "txt"]:
                    file_content = file_bytes.decode('utf-8')
                    if output_type == "markdown" or output_type == "md":
                        response_payload_base["markdown_content"] = file_content
                    else:
                        response_payload_base["raw_content"] = file_content
                    response_payload_base["pdf_supabase_signed_url"] = None
                    return JSONResponse(content=response_payload_base)

                elif output_type == "pdf":
                    try:
                        signed_url_response = await asyncio.to_thread(
                            supabase_client.storage.from_(BUCKET_NAME).create_signed_url,
                            path=db_item_supabase_path,
                            expires_in=3600  # 1 hour expiry
                        )
                        signed_url = signed_url_response.get('signedURL')
                        if signed_url:
                            response_payload_base["pdf_supabase_signed_url"] = signed_url
                            response_payload_base["markdown_content"] = None # No markdown for PDF
                            logger.info(f"Generated signed URL for Supabase PDF: {history_id}")
                            return JSONResponse(content=response_payload_base)
                        else:
                            logger.error(f"Failed to get signed URL from Supabase response for {db_item_supabase_path}. Response: {signed_url_response}")
                            # Fall through to local file logic if signed URL fails
                    except Exception as e_signed_url:
                        logger.error(f"Error generating signed URL for Supabase PDF {db_item_supabase_path}: {e_signed_url}", exc_info=True)
                        # Fall through to local file logic

            except Exception as e_supabase_dl:
                logger.error(f"Failed to download content from Supabase path {db_item_supabase_path} for {history_id}: {e_supabase_dl}. Falling back to local file system.", exc_info=True)
                # Fall through to local file system logic

        # --- Fallback to Local File System ---
        # This block is reached if:
        # 1. db_item_supabase_path was None/empty
        # 2. Download from Supabase failed (non-critical error, logged above)
        # 3. PDF signed URL generation failed

        logger.info(f"Proceeding with local file system retrieval for {history_id}. Local path: {local_content_path_str}")

        if not local_content_path_str: # Check if local path is also missing
            logger.warning(f"No local content_storage_path found for history item {history_id} after Supabase check/failure.")
            return JSONResponse(
                content={
                    "message": "Content path not found for this history item (no local path).",
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type, # Use already determined output_type
                    "content": None,
                    "pdf_path": None,
                    "markdown_content": None,
                    "served_from": "none",
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Resolve local path using local_content_path_str
        full_local_content_path = (CONTENT_STORAGE_BASE_DIR / local_content_path_str).resolve()
        
        # Security check for local path
        if not str(full_local_content_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())):
            logger.error(f"Security check failed for local path: {full_local_content_path}. Original path from DB: '{local_content_path_str}'")
            # This indicates a potentially compromised local_content_path_str in DB.
            raise HTTPException(status_code=403, detail="Access to local content path denied due to security policy.")

        if not await asyncio.to_thread(full_local_content_path.is_file):
            logger.error(f"Local content file not found at path: {full_local_content_path} (from DB local_content_path: {local_content_path_str}) for history item {history_id}.")
            return JSONResponse(
                content={
                    "message": f"Content file not found at local location: {local_content_path_str}",
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type,
                    "content": None,
                    "pdf_path": None, # local_content_path_str might be for a PDF, but pdf_file_path is used for frontend PDF link
                    "markdown_content": None,
                    "served_from": "none_found_local",
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"Attempting to serve file from local filesystem: {full_local_content_path} with type: {output_type}")

        response_payload_base_local = {
            "title": item_title,
            "url": item_url,
            "history_id": str(history_id),
            "content_type": output_type,
            "content_storage_path": local_content_path_str, # Reflecting local path
            "served_from": "local",
            "pdf_supabase_signed_url": None, # Not from Supabase
        }

        if output_type in ["markdown", "md", "text", "json", "html", "xml", "txt"]: # Text-based content
            try:
                async with aiofiles.open(full_local_content_path, mode='r', encoding='utf-8') as f:
                    file_content = await f.read()
                
                if output_type == "markdown" or output_type == "md":
                    response_payload_base_local["markdown_content"] = file_content
                else:
                    response_payload_base_local["raw_content"] = file_content
                # response_payload_base_local["pdf_path"] = None # pdf_path is ambiguous; pdf_file_path is for frontend PDF link construction

                return JSONResponse(content=response_payload_base_local)
            except Exception as e:
                logger.error(f"Error reading local text file {full_local_content_path} for history item {history_id}: {e}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading local content file: {e}")

        elif output_type == "pdf" or output_type == "pdf_link":
            # For local PDFs, provide pdf_file_path for frontend to construct download link via /download endpoint
            response_payload_base_local["pdf_file_path"] = local_content_path_str
            response_payload_base_local["markdown_content"] = None
            return JSONResponse(content=response_payload_base_local)
        
        else: # Fallback for unknown types from local storage
            logger.warning(f"Unsupported output_type '{output_type}' for local history item {history_id} at path {full_local_content_path}.")
            response_payload_base_local["message"] = f"Unsupported content type '{output_type}'. Path provided."
            response_payload_base_local["file_path"] = local_content_path_str # Generic file path
            return JSONResponse(content=response_payload_base_local)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error retrieving content for history item {history_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve content: {str(e)}")


@router.post(
    "/fetch-history/", # Assuming router is mounted at /api, making full path /api/fetch-history/
    response_model=FetchHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Fetch History"],
    summary="Create a new fetch history item"
)
async def create_fetch_history_item(
    item: FetchHistoryCreate,
    supabase_client = Depends(get_client) # Assuming get_client provides Supabase client
):
    history_id = uuid.uuid4()
    supabase_file_storage_path = None # Path within the bucket, not full URL yet
    BUCKET_NAME = "fetched_content" # TODO: Move to config or environment variable

    if get_client is None: # Ensure get_client itself is available
        logger.error("get_client function is None in create_fetch_history_item. Cannot obtain Supabase client.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client source (get_client) is not available.")
    if not supabase_client: # Ensure client was successfully obtained by Depends
        logger.error("Supabase client not available in create_fetch_history_item after Depends.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client could not be initialized.")


    if item.upload_to_supabase:
        if not item.content_storage_path:
            logger.warning(f"content_storage_path is required for Supabase upload attempt for URL: {item.url}")
            raise HTTPException(status_code=400, detail="content_storage_path is required for Supabase upload.")

        full_local_path = (CONTENT_STORAGE_BASE_DIR / item.content_storage_path).resolve()

        # Basic security check for content_storage_path to prevent traversal with item.content_storage_path
        if not str(full_local_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())):
            logger.error(f"Security check failed for local path for Supabase upload: {full_local_path}. Original path: {item.content_storage_path}")
            raise HTTPException(status_code=400, detail="Invalid content_storage_path leading to potential path traversal.")

        if not await asyncio.to_thread(full_local_path.is_file):
            logger.error(f"Local content file not found for Supabase upload: {full_local_path}")
            raise HTTPException(status_code=404, detail=f"Local content file not found: {item.content_storage_path}")

        # Sanitize filename for bucket path
        filename_in_bucket = Path(item.content_storage_path).name
        # Structure path by user_id (if available) then history_id to avoid filename collisions and organize data
        storage_path_in_bucket = f"{item.user_id or 'public'}/{history_id}/{filename_in_bucket}"

        try:
            async with aiofiles.open(full_local_path, 'rb') as f_content:
                file_bytes = await f_content.read()

            # Determine content-type for Supabase upload based on output_type or file extension
            upload_content_type = "application/octet-stream" # Default
            if item.output_type == "markdown": upload_content_type = "text/markdown"
            elif item.output_type == "html": upload_content_type = "text/html"
            elif item.output_type == "json": upload_content_type = "application/json"
            elif item.output_type == "pdf": upload_content_type = "application/pdf"
            elif item.output_type == "text" or item.output_type == "txt": upload_content_type = "text/plain"
            # Add more mappings if needed

            logger.info(f"Attempting to upload to Supabase: bucket='{BUCKET_NAME}', path='{storage_path_in_bucket}', content_type='{upload_content_type}'")

            # Supabase storage upload (blocking, run in thread)
            await asyncio.to_thread(
                supabase_client.storage.from_(BUCKET_NAME).upload,
                path=storage_path_in_bucket,
                file=file_bytes,
                file_options={"content-type": upload_content_type, "cache-control": "3600", "upsert": "false"} # upsert=false to avoid overwriting
            )
            supabase_file_storage_path = storage_path_in_bucket # Store the bucket path, not full URL
            logger.info(f"Successfully uploaded {item.content_storage_path} to Supabase bucket {BUCKET_NAME} at {storage_path_in_bucket}")

        except Exception as e: # Catch generic Supabase client error or other issues
            # Supabase client might raise a specific error type, e.g., StorageError
            # For now, catching generic Exception.
            # Check if it's a Supabase API error (often wrapped in an object with 'error' or 'message')
            supa_error_message = str(e)
            if hasattr(e, 'message'): supa_error_message = e.message

            logger.error(f"Failed to upload {item.content_storage_path} to Supabase Storage. Path: {storage_path_in_bucket}. Error: {supa_error_message}", exc_info=True)
            # Do not raise HTTPException here; save history record with supabase_file_storage_path as None
            # Frontend can be notified via the response if needed, or this can be handled as a partial success.
            # For now, we proceed to save the DB record.

    # Prepare data for DB insertion
    # Note: Pydantic models ensure item.url, item.title etc. are present if not Optional
    history_data_dict = {
        "id": history_id,
        "url": item.url,
        "title": item.title,
        "content_storage_path": item.content_storage_path, # Local path or identifier
        "output_type": item.output_type,
        "supabase_storage_path": supabase_file_storage_path, # Path in Supabase bucket
        "user_id": item.user_id, # Optional, will be None if not provided
        "crawl_preset_id": item.crawl_preset_id, # Optional
        "created_at": datetime.utcnow(), # Store as datetime object, Supabase client handles conversion
        # Ensure all fields from FetchHistoryCreate that are columns in DB are included
        # engine_specific_parameters and raw_content_summary are not in FetchHistoryCreate by default
        # Add them if they are part of the 'item' and table structure.
        # "engine_specific_parameters": item.engine_specific_parameters if hasattr(item, 'engine_specific_parameters') else None,
        # "raw_content_summary": item.raw_content_summary if hasattr(item, 'raw_content_summary') else None,
    }

    try:
        insert_response = await asyncio.to_thread(
            supabase_client.table("fetch_history").insert(history_data_dict).execute
        )
        if hasattr(insert_response, 'error') and insert_response.error:
            logger.error(f"Failed to save fetch history to DB: {insert_response.error}")
            # Consider what error message to show, as it might be complex (e.g. foreign key violation)
            db_error_detail = f"Database error creating history item: Code {insert_response.error.code}, Message: {insert_response.error.message}"
            raise HTTPException(status_code=500, detail=db_error_detail)

        if insert_response.data:
            logger.info(f"Fetch history item created with ID: {history_id} for URL: {item.url}")
            created_item_data = insert_response.data[0]
            # Pydantic model FetchHistoryResponse will validate and ensure created_at is datetime
            return FetchHistoryResponse(**created_item_data)
        else:
            logger.error("No data returned from DB insert operation for fetch history.")
            raise HTTPException(status_code=500, detail="Failed to create history item or no data returned from database.")

    except HTTPException as http_exc: # Re-raise HTTPExceptions directly
        raise http_exc
    except Exception as e: # Catch any other unexpected errors during DB interaction
        logger.error(f"Unexpected error creating fetch history item in DB for URL {item.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error during database operation: {str(e)}")


@router.delete(
    "/api/fetch-history/{history_id}",
    tags=["Fetch History"],
    summary="Delete a fetch history item and its associated content",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fetch_history_item(history_id: uuid.UUID):
    """
    Deletes a fetch history item from the database and its associated
    locally stored content file.
    """
    logger.info(f"Request to delete fetch history item ID: {history_id}")

    if get_client is None:
        logger.error("Supabase client (get_client) not available for delete operation.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database client configuration error."
        )

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable for delete.")

        # 1. Retrieve the fetch history record to get content_storage_path and supabase_storage_path
        select_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("id, content_storage_path, supabase_storage_path, output_type") # Added supabase_storage_path
            .eq("id", str(history_id))
            .single()
            .execute
        )

        if hasattr(select_response, 'error') and select_response.error:
            logger.error(f"Supabase error fetching history item {history_id} for deletion: {select_response.error.message if hasattr(select_response.error, 'message') else select_response.error}")
            if "PGRST116" in str(getattr(select_response.error, 'message', '')): # Resource not found
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fetch history item not found.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error fetching item: {getattr(select_response.error, 'message', 'Unknown DB error')}")
        
        if not hasattr(select_response, 'data') or not select_response.data:
            logger.warning(f"Fetch history item with ID {history_id} not found for deletion.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fetch history item not found.")

        item_data = select_response.data
        local_content_path_str = item_data.get("content_storage_path")
        db_item_supabase_path = item_data.get("supabase_storage_path")

        # 2. Delete the record from the fetch_history database table
        # This is done first, so if file deletions fail, the DB record is still gone.
        delete_db_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .delete()
            .eq("id", str(history_id))
            .execute
        )

        if hasattr(delete_db_response, 'error') and delete_db_response.error:
            logger.error(f"Supabase error deleting history item {history_id} from DB: {delete_db_response.error.message if hasattr(delete_db_response.error, 'message') else delete_db_response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error deleting item: {getattr(delete_db_response.error, 'message', 'Unknown DB error')}")
        
        if not hasattr(delete_db_response, 'data') or not delete_db_response.data:
            # This might happen if the item was already deleted by another request.
            # Since the goal is deletion, and it's not in the DB, this is not a critical error for this flow.
            logger.warning(f"No rows deleted from DB for history item ID {history_id}. It might have been deleted by another process.")
            # Proceed to file deletion attempts anyway, as files might be orphaned.
        else:
            logger.info(f"Successfully deleted record for history item ID: {history_id} from database.")

        # 3. Delete from Supabase Storage (if path exists)
        if db_item_supabase_path:
            BUCKET_NAME = "fetched_content" # TODO: Move to config
            try:
                logger.info(f"Attempting to delete from Supabase Storage: bucket='{BUCKET_NAME}', path='{db_item_supabase_path}' for history item {history_id}")
                # Supabase remove operation is likely blocking, run in thread
                remove_storage_response = await asyncio.to_thread(
                    supabase_client.storage.from_(BUCKET_NAME).remove,
                    paths=[db_item_supabase_path]
                )
                # remove_storage_response.data typically contains a list of successfully deleted items or is None/empty on error
                # Check for errors if the client version provides detailed error info here.
                # Some clients might raise an exception on failure which is caught below.
                # Example: if remove_storage_response and hasattr(remove_storage_response, 'error') and remove_storage_response.error:
                #    logger.error(f"Error deleting {db_item_supabase_path} from Supabase Storage for {history_id}: {remove_storage_response.error}")
                # else:
                logger.info(f"Deletion initiated for {db_item_supabase_path} from Supabase Storage for {history_id}. Response: {remove_storage_response}")

            except Exception as e_supa_delete:
                logger.error(f"Error during Supabase Storage deletion of {db_item_supabase_path} for history item {history_id}: {e_supa_delete}", exc_info=True)
                # Do not re-raise; failure here should not prevent the overall delete operation from succeeding.

        # 4. Delete the associated local file(s)
        if local_content_path_str:
            full_local_content_path = (CONTENT_STORAGE_BASE_DIR / local_content_path_str).resolve()

            if not str(full_local_content_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())):
                logger.error(f"Security check failed for local file deletion: Path '{full_local_content_path}' is outside of base '{CONTENT_STORAGE_BASE_DIR.resolve()}'. Original path: '{local_content_path_str}' for item {history_id}.")
                # Log and do not delete, but the main operation (DB delete) is considered successful.
            else:
                try:
                    if await asyncio.to_thread(full_local_content_path.is_file):
                        await asyncio.to_thread(os.remove, full_local_content_path)
                        logger.info(f"Successfully deleted local content file: {full_local_content_path} for history item {history_id}.")
                    else:
                        logger.warning(f"Local content file not found at {full_local_content_path} for history item {history_id} during deletion. It might have been already deleted.")
                except OSError as e_os_remove:
                    logger.error(f"Error deleting local content file {full_local_content_path} for history item {history_id}: {e_os_remove}", exc_info=True)
                    # Do not re-raise.
        else:
            logger.info(f"No local content_storage_path found for history item {history_id}, so no local file to delete.")

        # If all primary operations (DB delete) are successful, return 204 No Content.
        # File deletion failures are logged but don't make the endpoint fail.
        return None

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error deleting history item {history_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete history item: {str(e)}")