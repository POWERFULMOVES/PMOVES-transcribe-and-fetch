create_file_with_block
backend/app/tests/routes/test_tool_calling_api.py
import unittest
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.routes.llm_routes import router as llm_router # Assuming this is the correct router
from backend.app.models.tool_calling_models import InitiateToolCallRequest, SubmitArgumentChunkRequest
# ToolCallStatus might not be directly verifiable from API, but useful for context

class TestToolCallingAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = FastAPI()
        cls.app.include_router(llm_router, prefix="/api/v1") # Assuming a prefix like in other similar apps
        cls.client = TestClient(cls.app)
        # Note: State management for shared services (ToolCallStateStore etc.) is not handled here.
        # Tests assume sequential execution or that shared state impact is managed within each test.

    def test_01_initiate_tool_call_success(self):
        """Test successful initiation of a tool call."""
        init_payload = {"tool_name": "get_weather"} # Predefined schema
        response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("tool_call_id", response_data)
        self.assertTrue(isinstance(response_data["tool_call_id"], str))
        # Store for potential use in other tests, though each test should be independent if possible
        TestToolCallingAPI.shared_tool_call_id = response_data["tool_call_id"] 


    def test_02_initiate_tool_call_unknown_tool(self):
        """Test initiation with an unknown tool and no schema provided."""
        init_payload = {"tool_name": "nonexistent_tool_without_schema"}
        response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(response.status_code, 400) # Based on ArgumentAccumulatorService logic
        self.assertIn("Schema not found", response.json().get("detail", ""))


    def test_03_submit_chunks_complete_and_valid(self):
        """Test submitting chunks that form a complete and valid set of arguments."""
        init_payload = {"tool_name": "get_weather"}
        init_response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(init_response.status_code, 200, f"Failed to initiate tool call: {init_response.text}")
        tool_call_id = init_response.json()["tool_call_id"]

        chunk1_payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": "{\"location\": \"San Francisco, CA\",",
            "sequence_number": 0,
            "is_last_chunk": False
        }
        response1 = self.client.post("/api/v1/tools/submit_chunk", json=chunk1_payload)
        self.assertEqual(response1.status_code, 200, f"Chunk 1 submission failed: {response1.text}")
        self.assertEqual(response1.json().get("message"), "Chunk accumulated")

        chunk2_payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": "\"unit\": \"fahrenheit\"}",
            "sequence_number": 1,
            "is_last_chunk": True
        }
        response2 = self.client.post("/api/v1/tools/submit_chunk", json=chunk2_payload)
        self.assertEqual(response2.status_code, 200, f"Chunk 2 submission failed: {response2.text}")
        self.assertEqual(response2.json().get("message"), "Arguments complete and valid")

    def test_04_submit_chunk_invalid_tool_call_id(self):
        """Test submitting a chunk with an invalid tool_call_id."""
        payload = {
            "tool_call_id": "invalid-id-does-not-exist",
            "chunk_content": "{}",
            "sequence_number": 0,
            "is_last_chunk": True
        }
        response = self.client.post("/api/v1/tools/submit_chunk", json=payload)
        self.assertEqual(response.status_code, 404) # Expect Not Found
        self.assertIn("Tool call ID not found", response.json().get("detail", ""))


    def test_05_submit_chunk_malformed_json_final(self):
        """Test submitting a final chunk with malformed JSON."""
        init_payload = {"tool_name": "send_email"} # Another tool with a schema
        init_response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(init_response.status_code, 200, f"Failed to initiate tool call: {init_response.text}")
        tool_call_id = init_response.json()["tool_call_id"]

        payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": "{\"to\": \"test@example.com\", \"subject\": \"Hi\", \"body\": \"Missing quote", # Malformed
            "sequence_number": 0,
            "is_last_chunk": True
        }
        response = self.client.post("/api/v1/tools/submit_chunk", json=payload)
        self.assertEqual(response.status_code, 400, f"Response: {response.text}")
        self.assertIn("JSON decoding failed", response.json().get("detail", ""))

    def test_06_submit_chunk_schema_validation_error_final(self):
        """Test submitting a final chunk with valid JSON but schema non-compliance."""
        init_payload = {"tool_name": "get_weather"}
        init_response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(init_response.status_code, 200, f"Failed to initiate tool call: {init_response.text}")
        tool_call_id = init_response.json()["tool_call_id"]
        
        # Missing required "location" field
        payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": json.dumps({"unit": "celsius"}), # Valid JSON, but doesn't meet schema
            "sequence_number": 0,
            "is_last_chunk": True
        }
        response = self.client.post("/api/v1/tools/submit_chunk", json=payload)
        self.assertEqual(response.status_code, 400, f"Response: {response.text}")
        self.assertIn("'location' is a required property", response.json().get("detail", ""))

    def test_07_submit_chunk_to_terminal_state(self):
        """Test submitting a chunk to a tool call that is already completed."""
        # 1. Initiate and complete a tool call
        init_payload = {"tool_name": "get_weather"}
        init_response = self.client.post("/api/v1/tools/initiate", json=init_payload)
        self.assertEqual(init_response.status_code, 200, f"Failed to initiate tool call: {init_response.text}")
        tool_call_id = init_response.json()["tool_call_id"]

        complete_payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": json.dumps({"location": "London", "unit": "celsius"}),
            "sequence_number": 0,
            "is_last_chunk": True
        }
        complete_response = self.client.post("/api/v1/tools/submit_chunk", json=complete_payload)
        self.assertEqual(complete_response.status_code, 200, f"Failed to complete tool call: {complete_response.text}")
        self.assertEqual(complete_response.json().get("message"), "Arguments complete and valid")

        # 2. Attempt to submit another chunk to the now-completed tool call
        another_chunk_payload = {
            "tool_call_id": tool_call_id,
            "chunk_content": "{\"extra_field\": \"should_fail\"}",
            "sequence_number": 1, # Next sequence
            "is_last_chunk": False 
        }
        response = self.client.post("/api/v1/tools/submit_chunk", json=another_chunk_payload)
        self.assertEqual(response.status_code, 409) # Conflict - terminal state
        self.assertIn("Tool call is in a terminal state", response.json().get("detail", ""))

if __name__ == "__main__":
    unittest.main()
