import asyncio
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

# Assuming get_client is in ..db.database, adjust if necessary
try:
    from ..db.database import get_client
except ImportError:
    from psearchworking_export import get_client # type: ignore

from ..models.system_models import AgentRegistry, AgentRegistryCreate

router = APIRouter()

@router.post("/", response_model=AgentRegistry, status_code=status.HTTP_201_CREATED)
async def register_agent(
    agent_create: AgentRegistryCreate,
    supabase_client = Depends(get_client)
):
    """
    Register a new agent.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .insert(agent_create.model_dump(exclude_none=True)) # exclude_none for optional fields
            .execute
        )
        if not response.data:
            error_msg = response.error.message if response.error else "Unknown database error during agent registration"
            # Check for unique constraint violation on agent_id
            if response.error and "unique constraint" in response.error.message.lower() and "agent_registry_agent_id_key" in response.error.message.lower():
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Agent with agent_id '{agent_create.agent_id}' already exists.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register agent: {error_msg}")
        return AgentRegistry(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        # Catch potential DB unique constraint violations for agent_id that might not be caught by Supabase error parsing
        if "unique constraint" in str(e).lower() and "agent_registry_agent_id_key" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Agent with agent_id '{agent_create.agent_id}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/", response_model=List[AgentRegistry])
async def list_registered_agents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    supabase_client = Depends(get_client)
):
    """
    List all registered agents with pagination and optional filtering by type or status.
    """
    try:
        query = supabase_client.table("agent_registry").select("*")
        if type_filter:
            query = query.eq("type", type_filter)
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = await asyncio.to_thread(
            query.limit(limit).offset(offset).execute
        )

        if not response.data:
            return [] # Not an error if no agents match filters or table is empty
        return [AgentRegistry(**item) for item in response.data]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{agent_record_id}", response_model=AgentRegistry)
async def get_agent_by_record_id(
    agent_record_id: uuid.UUID,
    supabase_client = Depends(get_client)
):
    """
    Get a specific agent by its database record UUID.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .select("*")
            .eq("id", str(agent_record_id))
            .maybe_single()
            .execute
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent with record ID '{agent_record_id}' not found.")
        return AgentRegistry(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/agent/{agent_id_str}", response_model=AgentRegistry)
async def get_agent_by_agent_id_string(
    agent_id_str: str,
    supabase_client = Depends(get_client)
):
    """
    Get a specific agent by its unique string agent_id.
    """
    try:
        response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .select("*")
            .eq("agent_id", agent_id_str)
            .maybe_single()
            .execute
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent with agent_id '{agent_id_str}' not found.")
        return AgentRegistry(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/{agent_record_id}", response_model=AgentRegistry)
async def update_agent_registration(
    agent_record_id: uuid.UUID,
    agent_update: AgentRegistryCreate, # Can reuse Create model for updates
    supabase_client = Depends(get_client)
):
    """
    Update an agent's registration by its record UUID.
    """
    try:
        # Ensure agent_id is not being changed to one that already exists if part of update
        # This is complex with unique constraints and might be better handled by DB error.
        # For simplicity, direct update is shown. DB will error on unique constraint violation for agent_id.
        
        update_data = agent_update.model_dump(exclude_unset=True, exclude_none=True) # For partial updates

        response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .update(update_data)
            .eq("id", str(agent_record_id))
            .execute
        )
        if not response.data:
            check_exists_response = await asyncio.to_thread(
                supabase_client.table("agent_registry").select("id").eq("id", str(agent_record_id)).maybe_single().execute
            )
            if not check_exists_response.data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent with record ID '{agent_record_id}' not found.")
            
            error_msg = response.error.message if response.error else "Update failed or resource not found"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update agent registration: {error_msg}")
        
        return AgentRegistry(**response.data[0])
    except HTTPException:
        raise
    except Exception as e: # Catch potential DB unique constraint violations for agent_id
        if "unique constraint" in str(e).lower() and "agent_registry_agent_id_key" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Agent ID '{agent_update.agent_id}' already exists for another agent.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.delete("/{agent_record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_registration(
    agent_record_id: uuid.UUID,
    supabase_client = Depends(get_client)
):
    """
    Delete an agent's registration by its record UUID.
    """
    try:
        # First, check if the item exists
        check_response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .select("id")
            .eq("id", str(agent_record_id))
            .maybe_single()
            .execute
        )
        if not check_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent with record ID '{agent_record_id}' not found.")

        # If it exists, proceed with deletion
        response = await asyncio.to_thread(
            supabase_client.table("agent_registry")
            .delete()
            .eq("id", str(agent_record_id))
            .execute
        )
        if response.error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete agent registration: {response.error.message}")
        
        return None # No content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")
