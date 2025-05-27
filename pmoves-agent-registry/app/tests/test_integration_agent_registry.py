import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pmoves_agent_registry.app.main import app
from pmoves_agent_registry.app.schemas import AgentMetadata, AgentRegistration, AgentHeartbeat
from datetime import datetime, timezone

# Patching agent_store where it's imported and used in main.py
@patch('pmoves_agent_registry.app.main.agent_store', new_callable=MagicMock)
class TestAgentRegistryIntegration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Define common test data
        self.agent_id = "test_agent_001"
        self.now = datetime.now(timezone.utc)
        
        # This dictionary represents the expected JSON structure for an AgentMetadata object
        # Useful for comparing against response.json()
        self.base_agent_dict_json_compatible = {
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
            "last_heartbeat": self.now.isoformat(), # JSON uses ISO string for datetime
            "config": {"key": "value"}
        }
        
        # This is the Pydantic model instance that mock agent_store methods will return
        self.mock_agent_metadata_object = AgentMetadata(
            agent_id=self.agent_id,
            name="Test Agent",
            description="A test agent",
            capabilities=["test", "mock"],
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            status="active",
            endpoint="http://localhost:8000/agent",
            dependencies=["dep1"],
            version="1.0",
            tags=["test_env"],
            last_heartbeat=self.now, # Pydantic model uses datetime object
            config={"key": "value"}
        )

    # Test GET /agents
    def test_list_agents_empty(self, mock_agent_store: MagicMock):
        mock_agent_store.list.return_value = []
        response = self.client.get("/agents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        mock_agent_store.list.assert_called_once()

    def test_list_agents_with_data(self, mock_agent_store: MagicMock):
        mock_data_list = [self.mock_agent_metadata_object]
        mock_agent_store.list.return_value = mock_data_list
        
        response = self.client.get("/agents")
        self.assertEqual(response.status_code, 200)
        
        response_json = response.json()
        self.assertEqual(len(response_json), 1)
        # Compare the first item with the JSON compatible dict
        self.assertEqual(response_json[0], self.base_agent_dict_json_compatible)
        mock_agent_store.list.assert_called_once()

    # Test GET /agents/{agent_id}
    def test_get_agent_by_id_success(self, mock_agent_store: MagicMock):
        mock_agent_store.get.return_value = self.mock_agent_metadata_object
        
        response = self.client.get(f"/agents/{self.agent_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.base_agent_dict_json_compatible)
        mock_agent_store.get.assert_called_once_with(self.agent_id)

    def test_get_agent_by_id_not_found(self, mock_agent_store: MagicMock):
        mock_agent_store.get.return_value = None
        response = self.client.get("/agents/unknown_agent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Agent not found"})
        mock_agent_store.get.assert_called_once_with("unknown_agent")

    # Test POST /agents/register
    def test_register_agent_success(self, mock_agent_store: MagicMock):
        # This is the payload sent by the client, conforming to AgentRegistration
        reg_data_payload = {
            "agent_id": self.agent_id,
            "name": "Test Agent",
            "description": "A test agent",
            "capabilities": ["test", "mock"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
            "status": "active", # Initial status
            "endpoint": "http://localhost:8000/agent",
            "dependencies": ["dep1"],
            "version": "1.0",
            "tags": ["test_env"],
            # "last_heartbeat" is not provided by client in registration
            "config": {"key": "value"}
            # No last_heartbeat here
        }
        
        # agent_store.register is expected to return a full AgentMetadata object
        # which includes last_heartbeat set by the server.
        mock_agent_store.register.return_value = self.mock_agent_metadata_object
        
        response = self.client.post("/agents/register", json=reg_data_payload)
        self.assertEqual(response.status_code, 200) # As per main.py, returns the object
        self.assertEqual(response.json(), self.base_agent_dict_json_compatible) # Response should match full metadata
        
        mock_agent_store.register.assert_called_once()
        call_args = mock_agent_store.register.call_args[0][0]
        self.assertIsInstance(call_args, AgentRegistration)
        self.assertEqual(call_args.agent_id, self.agent_id)
        # Ensure that the AgentRegistration model passed to store has no last_heartbeat (or is None)
        self.assertIsNone(call_args.last_heartbeat)


    def test_register_agent_invalid_input_missing_field(self, mock_agent_store: MagicMock):
        invalid_payload = {"name": "Test Agent Only"} # Missing agent_id, description, etc.
        response = self.client.post("/agents/register", json=invalid_payload)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity
        mock_agent_store.register.assert_not_called()

    def test_register_agent_store_returns_none(self, mock_agent_store: MagicMock):
        # Minimal valid payload for AgentRegistration
        reg_data_payload = {
            "agent_id": "agent_minimal", "name": "Minimal Agent", "description": "Desc",
            "capabilities": [], "input_schema": {}, "output_schema": {}, "status": "pending"
        } 
        
        mock_agent_store.register.return_value = None # Simulate agent_store failing to register
        
        response = self.client.post("/agents/register", json=reg_data_payload)
        # Current main.py returns the result of agent_store.register directly.
        # If it's None, FastAPI will return a 200 OK with a JSON `null` body.
        self.assertEqual(response.status_code, 200) 
        self.assertIsNone(response.json()) # Body should be null
        mock_agent_store.register.assert_called_once()

    # Test POST /agents/heartbeat
    def test_heartbeat_success(self, mock_agent_store: MagicMock):
        heartbeat_payload = {"agent_id": self.agent_id, "timestamp": self.now.isoformat()}
        
        # Simulate heartbeat returning the updated agent metadata
        # For this test, we assume the heartbeat logic in agent_store updates the last_heartbeat
        # and returns the full AgentMetadata. The self.mock_agent_metadata_object already has 'now'
        # as its last_heartbeat, so it serves as a valid return object.
        mock_agent_store.heartbeat.return_value = self.mock_agent_metadata_object
        
        response = self.client.post("/agents/heartbeat", json=heartbeat_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.base_agent_dict_json_compatible)
        
        mock_agent_store.heartbeat.assert_called_once()
        call_args = mock_agent_store.heartbeat.call_args[0][0]
        self.assertIsInstance(call_args, AgentHeartbeat)
        self.assertEqual(call_args.agent_id, self.agent_id)
        # FastAPI/Pydantic converts ISO string to datetime for the model
        self.assertEqual(call_args.timestamp, self.now)


    def test_heartbeat_agent_not_found(self, mock_agent_store: MagicMock):
        mock_agent_store.heartbeat.return_value = None
        heartbeat_payload = {"agent_id": "unknown_agent", "timestamp": self.now.isoformat()}
        
        response = self.client.post("/agents/heartbeat", json=heartbeat_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Agent not found or heartbeat failed"})
        
        mock_agent_store.heartbeat.assert_called_once()
        call_args = mock_agent_store.heartbeat.call_args[0][0]
        self.assertEqual(call_args.agent_id, "unknown_agent")


    def test_heartbeat_invalid_input(self, mock_agent_store: MagicMock):
        invalid_payload = {"timestamp": self.now.isoformat()} # Missing agent_id
        response = self.client.post("/agents/heartbeat", json=invalid_payload)
        self.assertEqual(response.status_code, 422)
        mock_agent_store.heartbeat.assert_not_called()

    # Test DELETE /agents/{agent_id}
    def test_deregister_agent_success(self, mock_agent_store: MagicMock):
        mock_agent_store.deregister.return_value = True
        response = self.client.delete(f"/agents/{self.agent_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "Agent deregistered"})
        mock_agent_store.deregister.assert_called_once_with(self.agent_id)

    def test_deregister_agent_not_found(self, mock_agent_store: MagicMock):
        mock_agent_store.deregister.return_value = False
        response = self.client.delete("/agents/unknown_agent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Agent not found"})
        mock_agent_store.deregister.assert_called_once_with("unknown_agent")

if __name__ == '__main__':
    # This allows running the tests directly from the file, e.g., `python test_integration_agent_registry.py`
    # The `argv` and `exit` parameters are to ensure compatibility with different execution environments.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
