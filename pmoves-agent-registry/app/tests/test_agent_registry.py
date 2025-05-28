import unittest
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timezone
import json

# Assuming models and schemas are in pmoves-agent-registry.app
from pmoves_agent_registry.app.models import AgentStore
from pmoves_agent_registry.app.schemas import AgentRegistration, AgentMetadata
from supabase.lib.client_options import PostgrestAPIError

class TestAgentStore(unittest.TestCase):

    @patch.dict(os.environ, {"SUPABASE_URL": "mock_url", "SUPABASE_KEY": "mock_key"})
    @patch('pmoves_agent_registry.app.models.create_client')
    def setUp(self, mock_create_client):
        self.mock_supabase_client = MagicMock()
        mock_create_client.return_value = self.mock_supabase_client
        self.agent_store = AgentStore()
        
        # Common mock data
        self.agent_id = "test_agent_001"
        self.now = datetime.now(timezone.utc)
        self.base_agent_data = {
            "agent_id": self.agent_id,
            "name": "Test Agent",
            "description": "A test agent",
            "capabilities": ["test", "mock"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
            "status": "active",
            "endpoint": "http://localhost:8000/agent",
            "dependencies": ["dep1"],
            "version": "1.0",
            "tags": ["test_env"],
            "last_heartbeat": self.now,
            "config": {"key": "value"}
        }
        self.agent_reg = AgentRegistration(**self.base_agent_data)
        self.agent_meta = AgentMetadata(**self.base_agent_data)

    # Test __init__
    @patch.dict(os.environ, {"SUPABASE_URL": "mock_url", "SUPABASE_KEY": "mock_key"})
    @patch('pmoves_agent_registry.app.models.create_client')
    def test_init_success(self, mock_create_client_success):
        mock_client = MagicMock()
        mock_create_client_success.return_value = mock_client
        store = AgentStore()
        self.assertIsNotNone(store.db)
        self.assertEqual(store.db, mock_client)
        mock_create_client_success.assert_called_once_with("mock_url", "mock_key")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_env_vars(self):
        with self.assertRaises(ValueError) as context:
            AgentStore()
        self.assertIn("SUPABASE_URL and SUPABASE_KEY must be set", str(context.exception))

    @patch.dict(os.environ, {"SUPABASE_URL": "mock_url", "SUPABASE_KEY": "mock_key"})
    @patch('pmoves_agent_registry.app.models.create_client', side_effect=Exception("Init failed"))
    def test_init_supabase_client_exception(self, mock_create_client_fail):
        with self.assertRaises(Exception) as context:
            AgentStore()
        self.assertIn("Init failed", str(context.exception))

    # Test _serialize_agent_data
    def test_serialize_agent_data_full(self):
        data_to_serialize = self.agent_meta.dict()
        serialized = self.agent_store._serialize_agent_data(data_to_serialize)
        
        self.assertEqual(serialized['agent_id'], self.agent_id)
        self.assertEqual(serialized['capabilities'], json.dumps(self.base_agent_data['capabilities']))
        self.assertEqual(serialized['input_schema'], json.dumps(self.base_agent_data['input_schema']))
        self.assertEqual(serialized['output_schema'], json.dumps(self.base_agent_data['output_schema']))
        self.assertEqual(serialized['dependencies'], json.dumps(self.base_agent_data['dependencies']))
        self.assertEqual(serialized['tags'], json.dumps(self.base_agent_data['tags']))
        self.assertEqual(serialized['config'], json.dumps(self.base_agent_data['config']))
        self.assertEqual(serialized['last_heartbeat'], self.base_agent_data['last_heartbeat'].isoformat())

    def test_serialize_agent_data_partial_and_none(self):
        partial_data = {
            "agent_id": "agent_002",
            "name": "Partial Agent",
            "capabilities": None, # Test None
            "input_schema": {"type": "string"}, # Test present
            # output_schema is missing
        }
        serialized = self.agent_store._serialize_agent_data(partial_data)
        self.assertEqual(serialized['agent_id'], "agent_002")
        self.assertIsNone(serialized['capabilities'])
        self.assertEqual(serialized['input_schema'], json.dumps({"type": "string"}))
        self.assertNotIn('output_schema', serialized) # Should not add missing fields

    # Test _deserialize_agent_data
    def test_deserialize_agent_data_full(self):
        serialized_data = {
            **self.base_agent_data, # Start with original types
            'capabilities': json.dumps(self.base_agent_data['capabilities']),
            'input_schema': json.dumps(self.base_agent_data['input_schema']),
            'output_schema': json.dumps(self.base_agent_data['output_schema']),
            'dependencies': json.dumps(self.base_agent_data['dependencies']),
            'tags': json.dumps(self.base_agent_data['tags']),
            'config': json.dumps(self.base_agent_data['config']),
            'last_heartbeat': self.base_agent_data['last_heartbeat'].isoformat()
        }
        deserialized = self.agent_store._deserialize_agent_data(serialized_data)
        self.assertEqual(deserialized['agent_id'], self.agent_id)
        self.assertEqual(deserialized['capabilities'], self.base_agent_data['capabilities'])
        self.assertEqual(deserialized['input_schema'], self.base_agent_data['input_schema'])
        self.assertEqual(deserialized['output_schema'], self.base_agent_data['output_schema'])
        self.assertEqual(deserialized['dependencies'], self.base_agent_data['dependencies'])
        self.assertEqual(deserialized['tags'], self.base_agent_data['tags'])
        self.assertEqual(deserialized['config'], self.base_agent_data['config'])
        self.assertEqual(deserialized['last_heartbeat'], self.base_agent_data['last_heartbeat'])

    def test_deserialize_agent_data_partial_and_pre_typed(self):
        data = {
            "agent_id": "agent_003",
            "name": "Pre-typed Agent",
            "capabilities": ["already_list"], # Already a list
            "input_schema": None, # Test None
            # output_schema is missing
        }
        deserialized = self.agent_store._deserialize_agent_data(data)
        self.assertEqual(deserialized['capabilities'], ["already_list"])
        self.assertIsNone(deserialized['input_schema'])

    @patch('builtins.print')
    def test_deserialize_agent_data_json_decode_error(self, mock_print):
        data_with_bad_json = {
            "agent_id": "agent_004",
            "name": "Bad JSON Agent",
            "capabilities": "{not_json_at_all",
            "last_heartbeat": self.now.isoformat()
        }
        deserialized = self.agent_store._deserialize_agent_data(data_with_bad_json)
        self.assertEqual(deserialized['capabilities'], "{not_json_at_all") # Stays as string
        self.assertEqual(deserialized['last_heartbeat'], self.now)
        mock_print.assert_called_with("Warning: Could not decode JSON for field capabilities for agent agent_004")

    # Test register
    def test_register_success(self):
        mock_response = MagicMock()
        # Simulate Supabase returning the inserted data, which needs deserialization by AgentMetadata
        raw_db_return = self.agent_store._serialize_agent_data(self.agent_meta.dict())
        mock_response.data = [raw_db_return] # Supabase returns a list
        self.mock_supabase_client.table().upsert().execute.return_value = mock_response

        with patch.object(self.agent_store, '_serialize_agent_data', wraps=self.agent_store._serialize_agent_data) as mock_serialize, \
             patch.object(self.agent_store, '_deserialize_agent_data', wraps=self.agent_store._deserialize_agent_data) as mock_deserialize:
            
            # The input to register is AgentRegistration, but it becomes AgentMetadata internally
            # before serialization, so we use agent_meta for comparison after deserialization.
            registered_agent = self.agent_store.register(self.agent_reg)

            self.assertIsNotNone(registered_agent)
            self.assertIsInstance(registered_agent, AgentMetadata)
            # Compare all fields of AgentMetadata
            for key in AgentMetadata.__fields__.keys():
                 self.assertEqual(getattr(registered_agent, key), getattr(self.agent_meta, key))

            mock_serialize.assert_called_once()
            # The AgentMetadata constructor calls .dict() which might trigger _deserialize_agent_data if fields are complex
            # and then response.data[0] is passed to _deserialize_agent_data
            self.assertTrue(mock_deserialize.call_count >= 1) 
            self.mock_supabase_client.table("agents").upsert.assert_called_once()
            
            # Check that the data passed to upsert had last_heartbeat set
            # The actual call to upsert is with the serialized data
            args, kwargs = self.mock_supabase_client.table("agents").upsert.call_args
            upsert_data = args[0] 
            self.assertIn('last_heartbeat', upsert_data)
            self.assertIsNotNone(upsert_data['last_heartbeat'])


    def test_register_supabase_api_error(self):
        self.mock_supabase_client.table().upsert().execute.side_effect = PostgrestAPIError("DB error")
        result = self.agent_store.register(self.agent_reg)
        self.assertIsNone(result)

    def test_register_generic_exception(self):
        self.mock_supabase_client.table().upsert().execute.side_effect = Exception("Generic error")
        result = self.agent_store.register(self.agent_reg)
        self.assertIsNone(result)

    def test_register_supabase_no_data_response(self):
        mock_response = MagicMock()
        mock_response.data = [] # Empty list
        self.mock_supabase_client.table().upsert().execute.return_value = mock_response
        result = self.agent_store.register(self.agent_reg)
        self.assertIsNone(result)

    # Test get
    def test_get_success(self):
        mock_response = MagicMock()
        serialized_agent_data = self.agent_store._serialize_agent_data(self.agent_meta.dict())
        mock_response.data = [serialized_agent_data]
        self.mock_supabase_client.table().select().eq().limit().execute.return_value = mock_response

        with patch.object(self.agent_store, '_deserialize_agent_data', wraps=self.agent_store._deserialize_agent_data) as mock_deserialize:
            agent = self.agent_store.get(self.agent_id)
            self.assertIsNotNone(agent)
            self.assertIsInstance(agent, AgentMetadata)
            self.assertEqual(agent.agent_id, self.agent_id)
            for key in AgentMetadata.__fields__.keys():
                 self.assertEqual(getattr(agent, key), getattr(self.agent_meta, key))
            mock_deserialize.assert_called_once_with(serialized_agent_data)
        self.mock_supabase_client.table("agents").select("*").eq("agent_id", self.agent_id).limit(1).execute.assert_called_once()


    def test_get_not_found(self):
        mock_response = MagicMock()
        mock_response.data = []
        self.mock_supabase_client.table().select().eq().limit().execute.return_value = mock_response
        agent = self.agent_store.get("unknown_id")
        self.assertIsNone(agent)

    def test_get_supabase_api_error(self):
        self.mock_supabase_client.table().select().eq().limit().execute.side_effect = PostgrestAPIError("DB error")
        agent = self.agent_store.get(self.agent_id)
        self.assertIsNone(agent)

    def test_get_generic_exception(self):
        self.mock_supabase_client.table().select().eq().limit().execute.side_effect = Exception("Generic error")
        agent = self.agent_store.get(self.agent_id)
        self.assertIsNone(agent)

    # Test list
    def test_list_success_multiple_agents(self):
        agent2_data = {**self.base_agent_data, "agent_id": "agent_002", "name": "Agent Two"}
        agent_meta2 = AgentMetadata(**agent2_data)

        serialized_agent1 = self.agent_store._serialize_agent_data(self.agent_meta.dict())
        serialized_agent2 = self.agent_store._serialize_agent_data(agent_meta2.dict())
        
        mock_response = MagicMock()
        mock_response.data = [serialized_agent1, serialized_agent2]
        self.mock_supabase_client.table().select().execute.return_value = mock_response

        with patch.object(self.agent_store, '_deserialize_agent_data', wraps=self.agent_store._deserialize_agent_data) as mock_deserialize:
            agents = self.agent_store.list()
            self.assertEqual(len(agents), 2)
            self.assertIsInstance(agents[0], AgentMetadata)
            self.assertIsInstance(agents[1], AgentMetadata)
            self.assertEqual(agents[0].agent_id, self.agent_id)
            self.assertEqual(agents[1].agent_id, "agent_002")
            self.assertEqual(mock_deserialize.call_count, 2)
            mock_deserialize.assert_any_call(serialized_agent1)
            mock_deserialize.assert_any_call(serialized_agent2)
        self.mock_supabase_client.table("agents").select("*").execute.assert_called_once()

    def test_list_no_agents(self):
        mock_response = MagicMock()
        mock_response.data = []
        self.mock_supabase_client.table().select().execute.return_value = mock_response
        agents = self.agent_store.list()
        self.assertEqual(len(agents), 0)

    def test_list_supabase_api_error(self):
        self.mock_supabase_client.table().select().execute.side_effect = PostgrestAPIError("DB error")
        agents = self.agent_store.list()
        self.assertEqual(len(agents), 0)

    def test_list_generic_exception(self):
        self.mock_supabase_client.table().select().execute.side_effect = Exception("Generic error")
        agents = self.agent_store.list()
        self.assertEqual(len(agents), 0)

    # Test heartbeat
    def test_heartbeat_success(self):
        new_heartbeat_time = datetime.now(timezone.utc)
        
        # Mock for the update call
        mock_update_response = MagicMock()
        # Supabase update might return the updated record(s)
        updated_raw_data = self.agent_store._serialize_agent_data({
            **self.agent_meta.dict(), 
            "last_heartbeat": new_heartbeat_time, 
            "status": "active"
        })
        mock_update_response.data = [updated_raw_data] # Assuming it returns the updated record
        self.mock_supabase_client.table().update().eq().execute.return_value = mock_update_response

        # Mock for the self.get call within heartbeat
        # This get call should return the fully updated agent
        mock_get_response = MagicMock()
        # The data returned by get() should be what AgentMetadata expects after deserialization
        final_agent_data_for_get = AgentMetadata(**{
            **self.agent_meta.dict(), 
            "last_heartbeat": new_heartbeat_time, 
            "status": "active"
        }).dict()
        # self.get will deserialize this, so provide serialized version for its mock
        mock_get_response.data = [self.agent_store._serialize_agent_data(final_agent_data_for_get)]
        
        # Configure the mock_supabase_client to handle both the update and the subsequent select from get()
        # The first execute() is for update, the second for select().eq().limit().execute() from self.get()
        self.mock_supabase_client.table().update().eq().execute.return_value = mock_update_response
        # For the self.get call:
        self.mock_supabase_client.table().select().eq().limit().execute.return_value = mock_get_response
        
        with patch.object(self.agent_store, 'get', wraps=self.agent_store.get) as mock_get_method:
            updated_agent = self.agent_store.heartbeat(self.agent_id, new_heartbeat_time)

            self.assertIsNotNone(updated_agent)
            self.assertEqual(updated_agent.agent_id, self.agent_id)
            self.assertEqual(updated_agent.last_heartbeat, new_heartbeat_time)
            self.assertEqual(updated_agent.status, "active")

            # Check that update was called with correct data
            args, kwargs = self.mock_supabase_client.table("agents").update.call_args
            update_payload = args[0]
            self.assertEqual(update_payload["last_heartbeat"], new_heartbeat_time.isoformat())
            self.assertEqual(update_payload["status"], "active")
            self.assertIn("updated_at", update_payload) # Check that updated_at is being set

            self.mock_supabase_client.table("agents").update(update_payload).eq("agent_id", self.agent_id).execute.assert_called_once()
            mock_get_method.assert_called_once_with(self.agent_id)


    def test_heartbeat_agent_not_found(self):
        # Update returns no data
        mock_update_response = MagicMock()
        mock_update_response.data = []
        self.mock_supabase_client.table().update().eq().execute.return_value = mock_update_response
        
        # self.get also returns None
        with patch.object(self.agent_store, 'get', return_value=None) as mock_get_method:
            result = self.agent_store.heartbeat("unknown_id", self.now)
            self.assertIsNone(result)
            mock_get_method.assert_called_once_with("unknown_id") # get is called to confirm non-existence

    @patch('builtins.print')
    def test_heartbeat_update_returns_no_data_agent_exists(self, mock_print):
        # Update returns no data
        mock_update_response = MagicMock()
        mock_update_response.data = []
        self.mock_supabase_client.table().update().eq().execute.return_value = mock_update_response

        # But self.get returns the agent (as if update failed to return data but agent is there)
        # The agent_meta here would be the state *before* the heartbeat update was meant to apply
        with patch.object(self.agent_store, 'get', return_value=self.agent_meta) as mock_get_method:
            result = self.agent_store.heartbeat(self.agent_id, self.now)
            
            self.assertIsNotNone(result)
            # Should return the existing agent data if update returned nothing but agent exists
            self.assertEqual(result.agent_id, self.agent_meta.agent_id)
            self.assertEqual(result.last_heartbeat, self.agent_meta.last_heartbeat) # Unchanged
            
            mock_get_method.assert_called_once_with(self.agent_id)
            mock_print.assert_any_call(f"Warning: Supabase heartbeat update for agent {self.agent_id} returned no data. Current data: {self.agent_meta}")


    def test_heartbeat_supabase_api_error(self):
        self.mock_supabase_client.table().update().eq().execute.side_effect = PostgrestAPIError("DB error")
        result = self.agent_store.heartbeat(self.agent_id, self.now)
        self.assertIsNone(result)

    def test_heartbeat_generic_exception(self):
        self.mock_supabase_client.table().update().eq().execute.side_effect = Exception("Generic error")
        result = self.agent_store.heartbeat(self.agent_id, self.now)
        self.assertIsNone(result)

    # Test deregister
    def test_deregister_success(self):
        mock_response = MagicMock()
        # Supabase delete can return the deleted rows
        mock_response.data = [self.agent_store._serialize_agent_data(self.agent_meta.dict())] 
        self.mock_supabase_client.table().delete().eq().execute.return_value = mock_response
        
        result = self.agent_store.deregister(self.agent_id)
        self.assertTrue(result)
        self.mock_supabase_client.table("agents").delete().eq("agent_id", self.agent_id).execute.assert_called_once()

    def test_deregister_non_existent_agent(self):
        mock_response = MagicMock()
        mock_response.data = [] # No data indicates agent not found or already deleted
        self.mock_supabase_client.table().delete().eq().execute.return_value = mock_response
        
        result = self.agent_store.deregister("unknown_id")
        self.assertFalse(result)

    def test_deregister_supabase_api_error(self):
        self.mock_supabase_client.table().delete().eq().execute.side_effect = PostgrestAPIError("DB error")
        result = self.agent_store.deregister(self.agent_id)
        self.assertFalse(result)

    def test_deregister_generic_exception(self):
        self.mock_supabase_client.table().delete().eq().execute.side_effect = Exception("Generic error")
        result = self.agent_store.deregister(self.agent_id)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
