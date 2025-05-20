import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional # Added List
import uuid
import aiofiles # Added for async file operations

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

    if get_client is None:
        logger.error("Supabase client (get_client) not available.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database client configuration error."
        )

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database client unavailable.")

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("id, content_storage_path, output_type, title, url")
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
        content_path_str = item_data.get("content_storage_path")
        
        # Safely get and process output_type
        output_type_value = item_data.get("output_type")
        if output_type_value is None:
            output_type = "unknown"
        else:
            output_type = str(output_type_value).lower() # Ensure it's a string before lower()

        item_title = item_data.get("title", "Untitled")
        item_url = item_data.get("url")

        if not content_path_str:
            logger.warning(f"No content_storage_path found for history item {history_id}.")
            # Return metadata even if content is missing, so frontend can display something
            return JSONResponse(
                content={
                    "message": "Content path not found for this history item.",
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type,
                    "content": None,
                    "pdf_path": None, # Explicitly null
                    "markdown_content": None, # Explicitly null
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        # The content_storage_path is expected to be relative to a known base,
        # or an absolute path if your system stores them that way.
        # For security, if it's relative, join it with a configured base.
        # If it's absolute, ensure it's within an allowed directory.
        
        # Assuming content_storage_path is a filename or relative path within CONTENT_STORAGE_BASE_DIR
        # If content_storage_path could be absolute, more robust validation is needed.
        # For now, let's assume it's a filename that needs to be joined with CONTENT_STORAGE_BASE_DIR.
        
        # Path.name will extract the filename if content_path_str is a full path
        # This is a simplification; robust path handling is complex.
        # We assume content_storage_path is the *actual* filename stored in the DB.
        filename_only = Path(content_path_str).name 
        
        # Use the secure_join to construct the full path
        # This assumes CONTENT_STORAGE_BASE_DIR is the correct base for all stored files.
        # If content_storage_path from DB is already absolute and trusted, this logic would differ.
        # Given the task, content_storage_path is likely a path that the backend needs to resolve.
        # Let's assume content_storage_path is relative to CONTENT_STORAGE_BASE_DIR
        
        # If content_storage_path is ALREADY an absolute path stored in DB:
        # full_content_path = Path(content_path_str)
        # if not full_content_path.is_absolute():
        #    logger.error(f"content_storage_path '{content_path_str}' for {history_id} is not absolute as expected.")
        #    raise HTTPException(status_code=500, detail="Invalid content path configuration.")
        # if not str(full_content_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())): # Security check
        #    logger.error(f"Access denied for path '{content_path_str}' for {history_id}.")
        #    raise HTTPException(status_code=403, detail="Access to content path denied.")
        
        # If content_storage_path is relative to CONTENT_STORAGE_BASE_DIR:
        full_content_path = CONTENT_STORAGE_BASE_DIR.joinpath(content_path_str).resolve()
        
        # Security check: ensure the resolved path is within the base directory
        if not str(full_content_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())):
            logger.error(f"Security check failed: Path '{full_content_path}' is outside of base '{CONTENT_STORAGE_BASE_DIR.resolve()}'. Original path: '{content_path_str}'")
            raise HTTPException(status_code=403, detail="Access to content path denied due to security policy.")


        if not await asyncio.to_thread(full_content_path.is_file):
            logger.error(f"Content file not found at path: {full_content_path} (from DB: {content_path_str}) for history item {history_id}.")
            return JSONResponse(
                content={
                    "message": f"Content file not found at expected location: {content_path_str}",
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type,
                    "content": None,
                    "pdf_path": None,
                    "markdown_content": None,
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"Attempting to serve file: {full_content_path} with type: {output_type}")

        if output_type in ["markdown", "md", "text", "json", "html", "xml", "txt"]: # Text-based content
            try:
                async with aiofiles.open(full_content_path, mode='r', encoding='utf-8') as f:
                    file_content = await f.read()
                
                response_payload = {
                    "title": item_title,
                    "url": item_url,
                    "history_id": str(history_id),
                    "content_type": output_type,
                    "content_storage_path": content_path_str, # Send back the original path from DB
                    "pdf_path": None, # Explicitly null if not PDF
                }
                if output_type == "markdown" or output_type == "md":
                    response_payload["markdown_content"] = file_content
                else:
                    response_payload["raw_content"] = file_content # For JSON, HTML etc.

                return JSONResponse(content=response_payload)
            except Exception as e:
                logger.error(f"Error reading text file {full_content_path} for history item {history_id}: {e}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading content file: {e}")

        elif output_type == "pdf" or output_type == "pdf_link":
            # For PDFs, the frontend FetchedContentViewer expects a 'pdf_file_path' (which it uses to construct a download link)
            # or a direct 'pdfUrl'. We will provide the 'content_storage_path' as 'pdf_file_path'.
            # The frontend will then use an endpoint like /api/download_file?file_path=...
            # This means we don't stream the PDF here, but tell the frontend where to get it.
            # The path returned should be relative to a base the /api/download_file endpoint understands,
            # or an identifier that /api/download_file can resolve.
            # For now, we return the content_storage_path from the DB.
            return JSONResponse(content={
                "title": item_title,
                "url": item_url,
                "history_id": str(history_id),
                "content_type": output_type,
                "content_storage_path": content_path_str, # Original path from DB
                "pdf_file_path": content_path_str, # This is what FetchedContentViewer looks for
                "markdown_content": None, # Explicitly null
            })
        
        else:
            logger.warning(f"Unsupported output_type '{output_type}' for history item {history_id} at path {full_content_path}.")
            # Fallback for unknown types: provide path for client to decide
            return JSONResponse(content={
                "message": f"Unsupported content type '{output_type}'. Path provided.",
                "title": item_title,
                "url": item_url,
                "history_id": str(history_id),
                "content_type": output_type,
                "content_storage_path": content_path_str,
                "file_path": content_path_str, # Generic file path
                "pdf_path": None,
                "markdown_content": None,
            })

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error retrieving content for history item {history_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve content: {str(e)}")


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

        # 1. Retrieve the fetch history record to get content_storage_path
        select_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("id, content_storage_path, output_type") # Select fields needed for deletion logic
            .eq("id", str(history_id))
            .single()
            .execute
        )

        if hasattr(select_response, 'error') and select_response.error:
            logger.error(f"Supabase error fetching history item {history_id} for deletion: {select_response.error}")
            # Check if error is because item not found (e.g. PGRST116 for PostgREST)
            if "PGRST116" in str(select_response.error.message): # Resource not found
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fetch history item not found.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error fetching item: {select_response.error.message}")
        
        if not hasattr(select_response, 'data') or not select_response.data:
            logger.warning(f"Fetch history item with ID {history_id} not found for deletion.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fetch history item not found.")

        item_data = select_response.data
        content_path_str = item_data.get("content_storage_path")

        # 2. Delete the record from the fetch_history database table
        delete_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .delete()
            .eq("id", str(history_id))
            .execute
        )

        if hasattr(delete_response, 'error') and delete_response.error:
            # Log the error but proceed to file deletion if the main issue was DB,
            # as the file might still exist. Or, decide to stop if DB deletion fails critically.
            # For now, we'll log and raise, as a failed DB delete is significant.
            logger.error(f"Supabase error deleting history item {history_id} from DB: {delete_response.error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error deleting item: {delete_response.error.message}")
        
        # Check if any rows were affected by delete (data is usually a list of deleted items)
        if not hasattr(delete_response, 'data') or not delete_response.data:
            logger.warning(f"No rows deleted for history item ID {history_id}. It might have been deleted by another process or never existed.")
            # If the item was not found by select earlier, this path might not be hit due to 404.
            # If select found it, but delete found nothing, it's an inconsistency.
            # However, the goal is deletion, so if it's gone from DB, proceed to file.

        logger.info(f"Successfully deleted record for history item ID: {history_id} from database.")

        # 3. Delete the associated local file(s)
        if content_path_str:
            # Resolve the full path similar to get_fetch_history_item_content
            full_content_path = CONTENT_STORAGE_BASE_DIR.joinpath(content_path_str).resolve()

            # Security check: ensure the resolved path is within the base directory
            if not str(full_content_path).startswith(str(CONTENT_STORAGE_BASE_DIR.resolve())):
                logger.error(f"Security check failed for file deletion: Path '{full_content_path}' is outside of base '{CONTENT_STORAGE_BASE_DIR.resolve()}'. Original path: '{content_path_str}' for item {history_id}.")
                # Even if DB record is deleted, if file path is suspicious, log and do not delete.
                # The frontend will get a 204, but an error is logged.
                # Alternatively, raise an error here to indicate partial failure.
                # For now, log and continue to return 204 as DB record is gone.
            else:
                try:
                    if await asyncio.to_thread(full_content_path.is_file):
                        await asyncio.to_thread(os.remove, full_content_path)
                        logger.info(f"Successfully deleted local content file: {full_content_path} for history item {history_id}.")
                    else:
                        logger.warning(f"Local content file not found at {full_content_path} for history item {history_id} during deletion. It might have been already deleted or path is incorrect.")
                except OSError as e:
                    logger.error(f"Error deleting local content file {full_content_path} for history item {history_id}: {e}", exc_info=True)
                    # Do not raise HTTPException here if DB deletion was successful,
                    # as the primary resource (DB record) is gone. Log the error.
                    # The client will receive 204 (No Content).
        else:
            logger.info(f"No content_storage_path found for history item {history_id}, so no local file to delete.")

        # If all operations are successful (or non-critical errors handled), return 204 No Content.
        return None # FastAPI handles 204 No Content automatically for None return with this status_code

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error deleting history item {history_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete history item: {str(e)}")