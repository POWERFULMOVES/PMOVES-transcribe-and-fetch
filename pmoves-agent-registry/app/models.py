import os
import json
from typing import Dict, Optional, List
from supabase import create_client, Client
from supabase.lib.client_options import PostgrestAPIError # For error handling
from .schemas import AgentMetadata, AgentRegistration
from datetime import datetime

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
            # Log error appropriately in a real application
            print(f"Error initializing Supabase client: {e}")
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
                    # Keep as string if not valid JSON, or handle error
                    print(f"Warning: Could not decode JSON for field {field} for agent {data.get('agent_id')}")
                    pass # Or set to None, or raise error
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
            # Handle cases where response.data might be empty or indicate an error not caught by PostgrestAPIError
            print(f"Warning: Supabase upsert for agent {reg.agent_id} returned no data or an unexpected response: {response}")
            return None
        except PostgrestAPIError as e:
            print(f"Error registering agent {reg.agent_id}: {e.message}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during agent registration {reg.agent_id}: {e}")
            return None

    def get(self, agent_id: str) -> Optional[AgentMetadata]:
        try:
            response = self.db.table("agents").select("*").eq("agent_id", agent_id).limit(1).execute()
            if response.data:
                return AgentMetadata(**self._deserialize_agent_data(response.data[0]))
            return None
        except PostgrestAPIError as e:
            print(f"Error fetching agent {agent_id}: {e.message}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching agent {agent_id}: {e}")
            return None

    def list(self) -> List[AgentMetadata]:
        try:
            response = self.db.table("agents").select("*").execute()
            if response.data:
                return [AgentMetadata(**self._deserialize_agent_data(agent_data)) for agent_data in response.data]
            return []
        except PostgrestAPIError as e:
            print(f"Error listing agents: {e.message}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while listing agents: {e}")
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
                 print(f"Warning: Heartbeat for non-existent agent {agent_id}.")
                 return None
            # If agent exists but update returned no data, this is unusual.
            print(f"Warning: Supabase heartbeat update for agent {agent_id} returned no data. Current data: {existing_agent}")
            return existing_agent # Return current state if update had issues but agent exists
        except PostgrestAPIError as e:
            print(f"Error updating heartbeat for agent {agent_id}: {e.message}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during heartbeat for agent {agent_id}: {e}")
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
            # print(f"Info: Deregister agent {agent_id}: Agent not found or already deleted. Response: {response}")
            return False
        except PostgrestAPIError as e:
            print(f"Error deregistering agent {agent_id}: {e.message}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during deregistration of agent {agent_id}: {e}")
            return False