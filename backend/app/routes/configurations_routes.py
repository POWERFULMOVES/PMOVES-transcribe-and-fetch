import asyncio
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

# Assuming get_client is in ..db.database, adjust if necessary
try:
    from ..db.database import get_client
except ImportError:
    # Fallback for environments where this specific path might not be resolvable
    # during local development or testing outside the full app context.
    # In a real deployment, this path should be correct.
    from psearchworking_export import get_client # type: ignore

from ..models.system_models import AppConfiguration, AppConfigurationCreate

router = APIRouter()

@router.post("/", response_model=AppConfiguration, status_code=status.HTTP_201_CREATED)
async def create_configuration(
    config: AppConfigurationCreate,
    supabase_client = Depends(get_client) # Changed from supabase.Client to just get_client
):
    """
    Create a new application configuration.
    """
    try:
        # Supabase-py v1.x (sync) needs to be wrapped for async FastAPI
        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .insert(config.model_dump())
            .execute
        )
        if not response.data:
            error_msg = response.error.message if response.error else "Unknown database error"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create configuration: {error_msg}")
        return AppConfiguration(**response.data[0])
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/", response_model=List[AppConfiguration])
async def list_configurations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    supabase_client = Depends(get_client)
):
    """
    List all application configurations with pagination.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .select("*")
            .limit(limit)
            .offset(offset)
            .execute
        )
        if not response.data:
            # It's not an error if no configurations exist, return empty list
            return []
        return [AppConfiguration(**item) for item in response.data]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{config_id}", response_model=AppConfiguration)
async def get_configuration_by_id(
    config_id: uuid.UUID,
    supabase_client = Depends(get_client)
):
    """
    Get a specific configuration by its UUID.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .select("*")
            .eq("id", str(config_id))
            .maybe_single() # Use maybe_single for one or none
            .execute
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Configuration with ID '{config_id}' not found.")
        return AppConfiguration(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/key/{config_key}", response_model=AppConfiguration)
async def get_configuration_by_key(
    config_key: str,
    supabase_client = Depends(get_client)
):
    """
    Get a specific configuration by its unique config_key.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .select("*")
            .eq("config_key", config_key)
            .maybe_single() # Use maybe_single as config_key is unique
            .execute
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Configuration with key '{config_key}' not found.")
        return AppConfiguration(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/{config_id}", response_model=AppConfiguration)
async def update_configuration(
    config_id: uuid.UUID,
    config_update: AppConfigurationCreate, # Can reuse Create model for updates if all fields are updatable
    supabase_client = Depends(get_client)
):
    """
    Update a configuration by its UUID.
    """
    try:
        # Ensure the config_key is not being changed to one that already exists (if it's part of update)
        # This check is complex with unique constraints and might be better handled by DB error or specific logic
        # For simplicity, direct update is shown. DB will error on unique constraint violation for config_key.

        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .update(config_update.model_dump(exclude_unset=True)) # exclude_unset for partial updates
            .eq("id", str(config_id))
            .execute
        )
        if not response.data:
            # Check if the reason for no data is that the ID didn't exist
            check_exists_response = await asyncio.to_thread(
                supabase_client.table("app_configurations").select("id").eq("id", str(config_id)).maybe_single().execute
            )
            if not check_exists_response.data:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Configuration with ID '{config_id}' not found.")
            # If it exists but update returned no data, it's an issue (though upsert behavior might differ)
            # For basic update, if data isn't returned by `execute` it usually means no rows matched or error.
            # Supabase update often returns the updated data. If not, it's an issue or was a no-op.
            # Assuming if response.data is empty after update, and ID exists, it implies an issue or no change.
            # Let's re-fetch to be sure or rely on Supabase error.
            # For now, if no data, assume not found or error during update.
            error_msg = response.error.message if response.error else "Update failed or resource not found"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update configuration: {error_msg}")

        return AppConfiguration(**response.data[0])
    except HTTPException:
        raise
    except Exception as e: # Catch potential DB unique constraint violations for config_key here
        if "unique constraint" in str(e).lower() and "app_configurations_config_key_key" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Configuration key '{config_update.config_key}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuration(
    config_id: uuid.UUID,
    supabase_client = Depends(get_client)
):
    """
    Delete a configuration by its UUID.
    """
    try:
        # First, check if the item exists to provide a 404 if it doesn't
        check_response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .select("id")
            .eq("id", str(config_id))
            .maybe_single()
            .execute
        )
        if not check_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Configuration with ID '{config_id}' not found.")

        # If it exists, proceed with deletion
        response = await asyncio.to_thread(
            supabase_client.table("app_configurations")
            .delete()
            .eq("id", str(config_id))
            .execute
        )
        # Delete doesn't typically return data in response.data for Supabase, check for error
        if response.error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete configuration: {response.error.message}")

        # No content to return on successful delete
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")
