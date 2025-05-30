import os
import json
import logging # Added
from typing import Dict, Optional, List
from supabase import create_client, Client
from supabase.lib.client_options import PostgrestAPIError # For error handling
from .schemas import AgentMetadata, AgentRegistration
from datetime import datetime

logger = logging.getLogger(__name__) # Added

# Supabase Table Schema for 'agents' table
# CREATE TABLE public.agents (
#     agent_id TEXT PRIMARY KEY,
#     name TEXT NOT NULL,
#     description TEXT,
#     capabilities JSONB, -- List[str]
#     input_schema JSONB, -- Dict[str, Any]
#     output_schema JSONB, -- Dict[str, Any]
#     status TEXT,
#     endpoint TEXT,
#     dependencies JSONB, -- List[str]
#     version TEXT,
#     tags JSONB, -- List[str]
#     last_heartbeat TIMESTAMPTZ,
#     config JSONB, -- Dict[str, Any]
#     created_at TIMESTAMPTZ DEFAULT now(),
#     updated_at TIMESTAMPTZ DEFAULT now()
# );
#
# -- Optional: Trigger to update 'updated_at' timestamp
# CREATE OR REPLACE FUNCTION trigger_set_timestamp()
# RETURNS TRIGGER AS $$
# BEGIN
#   NEW.updated_at = NOW();
#   RETURN NEW;
# END;
# $$ LANGUAGE plpgsql;
#
# CREATE TRIGGER set_timestamp
# BEFORE UPDATE ON public.agents
# FOR EACH ROW
# EXECUTE PROCEDURE trigger_set_timestamp();

class AgentStore:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        try:
            self.db: Client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            logger.error("Error initializing Supabase client: %s", e, exc_info=True) # Modified
            raise

    def _serialize_agent_data(self, agent_data: dict) -> dict:
        """Converts complex types to JSON strings for Supabase."""
        data = agent_data.copy()
        for field in ['capabilities', 'input_schema', 'output_schema', 'dependencies', 'tags', 'config']:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])
        if 'last_heartbeat' in data and data['last_heartbeat']:
            data['last_heartbeat'] = data['last_heartbeat'].isoformat()
        return data

    def _deserialize_agent_data(self, agent_data: dict) -> dict:
        """Converts JSON strings from Supabase back to complex types."""
        data = agent_data.copy()
        for field in ['capabilities', 'input_schema', 'output_schema', 'dependencies', 'tags', 'config']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    logger.warning("Could not decode JSON for field %s for agent %s", field, data.get('agent_id')) # Modified
                    pass 
        if 'last_heartbeat' in data and isinstance(data['last_heartbeat'], str):
            data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return data

    def register(self, reg: AgentRegistration) -> Optional[AgentMetadata]:
        agent_dict = reg.dict()
        agent_dict['last_heartbeat'] = datetime.now() # Set initial heartbeat
        
        # Ensure all fields from AgentMetadata are present, even if None
        full_agent_data = AgentMetadata(**agent_dict).dict()
        
        data_to_insert = self._serialize_agent_data(full_agent_data)

        try:
            # Upsert logic: update if agent_id exists, otherwise insert
            response = self.db.table("agents").upsert(data_to_insert).execute()
            if response.data:
                return AgentMetadata(**self._deserialize_agent_data(response.data[0]))
            logger.warning("Supabase upsert for agent %s returned no data or an unexpected response: %s", reg.agent_id, response) # Modified
            return None
        except PostgrestAPIError as e:
            logger.error("Error registering agent %s: %s", reg.agent_id, getattr(e, 'message', str(e)), exc_info=True) # Modified
            return None
        except Exception as e:
            logger.error("Unexpected error during agent registration %s: %s", reg.agent_id, e, exc_info=True) # Modified
            return None

    def get(self, agent_id: str) -> Optional[AgentMetadata]:
        try:
            response = self.db.table("agents").select("*").eq("agent_id", agent_id).limit(1).execute()
            if response.data:
                return AgentMetadata(**self._deserialize_agent_data(response.data[0]))
            return None
        except PostgrestAPIError as e:
            logger.error("Error fetching agent %s: %s", agent_id, getattr(e, 'message', str(e)), exc_info=True) # Modified
            return None
        except Exception as e:
            logger.error("Unexpected error while fetching agent %s: %s", agent_id, e, exc_info=True) # Modified
            return None

    def list(
        self,
        capability: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[AgentMetadata]:
        try:
            query = self.db.table("agents").select("*")

            if capability:
                # Assumes 'capabilities' is a JSONB array of strings.
                # Supabase/PostgREST `cs` operator means "contains specified element(s)".
                # For a single string element in a JSON array: capabilities.cs."element"
                # The Python client might represent this as: .cs("capabilities", f'{{"{capability}"}}') if it expects a JSON literal
                # or more simply if it handles string elements in arrays directly.
                # Given the schema comments (List[str]), `cs` with the direct string value is likely correct.
                query = query.cs("capabilities", capability)

            if status:
                query = query.eq("status", status)

            if name:
                # Use 'ilike' for case-insensitive partial match (e.g., %name%)
                query = query.ilike("name", f"%{name}%")

            if tag:
                # Assumes 'tags' is a JSONB array of strings
                query = query.cs("tags", tag)
            
            response = query.execute()

            if response.data:
                return [AgentMetadata(**self._deserialize_agent_data(agent_data)) for agent_data in response.data]
            return []
        except PostgrestAPIError as e:
            # Replace print with structured logging later
            logger.error("Error listing agents with filters: %s", getattr(e, 'message', str(e)), exc_info=True) # Modified
            return []
        except Exception as e:
            # Replace print with structured logging later
            logger.error("Unexpected error while listing agents with filters: %s", e, exc_info=True) # Modified
            return []

    def heartbeat(self, agent_id: str, timestamp: datetime) -> Optional[AgentMetadata]:
        update_data = {
            "last_heartbeat": timestamp.isoformat(),
            "status": "active",
            "updated_at": datetime.now().isoformat() # Manually update updated_at if no trigger
        }
        try:
            response = self.db.table("agents").update(update_data).eq("agent_id", agent_id).execute()
            if response.data:
                return self.get(agent_id) # Fetch the updated record to return full metadata
            # This case might mean the agent_id didn't exist, or the update didn't return data.
            # Depending on strictness, you might log or handle this differently.
            # For now, if no data, means agent likely not found or update failed silently for some reason.
            existing_agent = self.get(agent_id)
            if not existing_agent:
                 logger.warning("Heartbeat for non-existent agent %s.", agent_id) # Modified
                 return None
            # If agent exists but update returned no data, this is unusual.
            logger.warning("Supabase heartbeat update for agent %s returned no data. Current data: %s", agent_id, existing_agent) # Modified
            return existing_agent # Return current state if update had issues but agent exists
        except PostgrestAPIError as e:
            logger.error("Error updating heartbeat for agent %s: %s", agent_id, getattr(e, 'message', str(e)), exc_info=True) # Modified
            return None
        except Exception as e:
            logger.error("Unexpected error during heartbeat for agent %s: %s", agent_id, e, exc_info=True) # Modified
            return None

    def deregister(self, agent_id: str) -> bool:
        try:
            response = self.db.table("agents").delete().eq("agent_id", agent_id).execute()
            # Check if any data was returned (Supabase delete can return the deleted rows)
            # and if the count of deleted items (if available in response) is greater than 0
            if response.data: # Successfully deleted
                return True
            # If no data, it might mean the agent_id didn't exist.
            # To be certain, we can check if it exists first, but that's an extra query.
            # For now, if response.data is empty, assume it was not found or already deleted.
            # logger.info("Deregister agent %s: Agent not found or already deleted. Response: %s", agent_id, response) # Example of an info log
            return False
        except PostgrestAPIError as e:
            logger.error("Error deregistering agent %s: %s", agent_id, getattr(e, 'message', str(e)), exc_info=True) # Modified
            return False
        except Exception as e:
            logger.error("Unexpected error during deregistration of agent %s: %s", agent_id, e, exc_info=True) # Modified
            return False