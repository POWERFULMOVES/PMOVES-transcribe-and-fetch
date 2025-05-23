create_file_with_block
pmoves-pipecat/tests/services/__init__.py
create_file_with_block
pmoves-pipecat/tests/services/test_litellm_service_tool_integration.py
import asyncio
import unittest
import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, call

# Adjust imports based on actual file structure
# Assuming 'src' is in PYTHONPATH or tests are run from a level where 'src' is accessible
from pipecat.services.litellm_service import LiteLLMPipecatService
from backend.app.utils.llm_registry_service import LLMRegistryService, StandardizedLLM
from backend.app.services.tool_calling.argument_accumulator_service import ArgumentAccumulatorService
from backend.app.services.tool_calling.tool_call_state_store import ToolCallStateStore
from backend.app.services.tool_calling.tool_schema_manager import ToolSchemaManager
from backend.app.services.tool_calling.validation_service import ValidationService
from pipecat.frames.frames import (
    LLMMessagesFrame, 
    FunctionCallInProgressFrame, 
    ErrorFrame, 
    LLMFullResponseStartFrame, 
    LLMFullResponseEndFrame,
    LLMTextFrame # For potential text parts in stream
)
from backend.app.models.tool_calling_models import ToolCallStatus

# Mock litellm at the top level for tests if it's not installed in the test environment
# or to control its behavior globally for these tests.
# However, we are mocking the router instance specifically in setUp.
# import litellm # This would be the actual import if not fully mocking

# Disable logging for tests to keep output clean
logging.disable(logging.CRITICAL)

class TestLiteLLMServiceToolIntegration(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Instantiate actual backend services
        self.schema_manager = ToolSchemaManager()  # Has "get_weather", "send_email"
        self.state_store = ToolCallStateStore(idle_timeout_seconds=5, total_timeout_seconds=10)
        await self.state_store.start_cleanup_worker()
        self.validation_service = ValidationService()
        self.accumulator_service = ArgumentAccumulatorService(self.state_store, self.schema_manager, self.validation_service)

        # Mock LLMRegistryService
        self.mock_llm_registry = MagicMock(spec=LLMRegistryService)
        mock_model_info = StandardizedLLM(
            provider="test_provider",
            model_id="test_model_with_tools", # This is the ID LiteLLM will use
            display_name="Test Model with Tools",
            crawl4ai_compatible_id="test_model_with_tools_crawl_id" # Different for clarity
        )
        self.mock_llm_registry.get_model_details.return_value = mock_model_info

        # Mock litellm.Router instance
        # We don't need to mock the whole module `litellm`, just the router object passed to the service
        self.mock_litellm_router = AsyncMock() # spec=litellm.Router - if litellm is importable

        self.service = LiteLLMPipecatService(
            llm_registry_service=self.mock_llm_registry,
            preferred_model_alias="test_model_with_tools", # Alias used to fetch from registry
            litellm_router=self.mock_litellm_router
        )
        self.service.push_frame = AsyncMock()

    async def asyncTearDown(self):
        await self.state_store.stop_cleanup_worker()
        if hasattr(self.service, 'cleanup'): # If a cleanup method is added to LiteLLMPipecatService
            await self.service.cleanup()


    async def _generate_mock_llm_stream_chunks(self, tool_call_id: str, tool_name: str, argument_parts: list[str], text_content: Optional[str] = None):
        # First chunk: text content (if any) and initial tool call
        if text_content:
            choice_text = MagicMock()
            choice_text.delta.content = text_content
            choice_text.delta.tool_calls = None
            chunk_text = MagicMock()
            chunk_text.choices = [choice_text]
            yield chunk_text
            
        # Tool call chunks
        for i, arg_part in enumerate(argument_parts):
            tool_call_mock = MagicMock()
            tool_call_mock.id = tool_call_id
            tool_call_mock.type = 'function'
            
            # First tool_call chunk includes the name, subsequent ones might not (or might repeat it)
            # OpenAI typically sends name only in the first chunk for a given tool_call_id
            func_mock = MagicMock(arguments=arg_part)
            if i == 0:
                func_mock.name = tool_name
            else:
                func_mock.name = None # Or tool_name, depending on exact LLM behavior being mimicked

            tool_call_mock.function = func_mock
            
            choice_tool = MagicMock()
            choice_tool.delta.content = None # No text content in tool call chunks
            choice_tool.delta.tool_calls = [tool_call_mock]
            
            chunk_tool = MagicMock()
            # LiteLLM chunk might have an 'id' attribute for the chunk itself
            chunk_tool.id = f"chunk_id_{i}" 
            chunk_tool.choices = [choice_tool]
            yield chunk_tool

    async def test_tool_call_successful_accumulation_and_dispatch_signal(self):
        tool_call_id = "call_test123_success"
        tool_name = "get_weather"
        argument_parts = ['{"location": "Sunnyvale, CA"', ', "unit": "fahrenheit"}']
        expected_final_args = {"location": "Sunnyvale, CA", "unit": "fahrenheit"}

        self.mock_litellm_router.acompletion.return_value = self._generate_mock_llm_stream_chunks(
            tool_call_id, tool_name, argument_parts, text_content="Let me get that weather for you."
        )

        messages_frame = LLMMessagesFrame([{"role": "user", "content": "What's the weather?"}])
        await self.service.process_frame(messages_frame, "DOWNSTREAM") # FrameDirection.DOWNSTREAM

        await asyncio.sleep(0.2) # Increased sleep for robust event propagation

        # Verify calls
        self.mock_llm_registry.get_model_details.assert_called_with("test_model_with_tools")
        self.mock_litellm_router.acompletion.assert_called_once()

        # Check pushed frames
        # Order: Start, Text (optional), FunctionCall (final), End
        pushed_frame_types = [type(call_args[0][0]) for call_args in self.service.push_frame.call_args_list]
        
        self.assertIn(LLMFullResponseStartFrame, pushed_frame_types)
        self.assertIn(LLMTextFrame, pushed_frame_types) # From text_content
        self.assertIn(FunctionCallInProgressFrame, pushed_frame_types)
        self.assertIn(LLMFullResponseEndFrame, pushed_frame_types)

        found_function_call = False
        for call_args in self.service.push_frame.call_args_list:
            frame = call_args[0][0]
            if isinstance(frame, FunctionCallInProgressFrame):
                self.assertEqual(frame.tool_call_id, tool_call_id)
                self.assertEqual(frame.function_name, tool_name)
                self.assertEqual(json.loads(frame.arguments), expected_final_args) # Arguments should be JSON string
                self.assertTrue(frame.is_final)
                found_function_call = True
                break
        self.assertTrue(found_function_call, "Final FunctionCallInProgressFrame not found or incorrect")

    async def test_tool_call_accumulation_fails_validation(self):
        tool_call_id = "call_fail_validation_123"
        tool_name = "get_weather"
        # Invalid: "location" is required, but "location_misspelled" is provided
        argument_parts = ['{"location_misspelled": "Testville", "unit": "celsius"}'] 

        self.mock_litellm_router.acompletion.return_value = self._generate_mock_llm_stream_chunks(
            tool_call_id, tool_name, argument_parts
        )

        messages_frame = LLMMessagesFrame([{"role": "user", "content": "What's the weather in Testville?"}])
        await self.service.process_frame(messages_frame, "DOWNSTREAM")

        await asyncio.sleep(0.2) # Allow processing

        # Check for ErrorFrame
        found_error_frame = False
        for call_args in self.service.push_frame.call_args_list:
            frame = call_args[0][0]
            if isinstance(frame, ErrorFrame):
                self.assertIn(tool_call_id, frame.error)
                self.assertIn("failed", frame.error.lower())
                # Check for schema validation specific message (from jsonschema)
                self.assertIn("'location' is a required property", frame.error)
                found_error_frame = True
                break
        self.assertTrue(found_error_frame, "ErrorFrame for validation failure not found or incorrect")

    async def test_tool_call_json_decoding_error(self):
        tool_call_id = "call_json_decode_error_123"
        tool_name = "get_weather"
        # Invalid JSON: missing closing brace for location
        argument_parts = ['{"location": "Testville', ', "unit": "celsius"}'] 

        self.mock_litellm_router.acompletion.return_value = self._generate_mock_llm_stream_chunks(
            tool_call_id, tool_name, argument_parts
        )

        messages_frame = LLMMessagesFrame([{"role": "user", "content": "Weather?"}])
        await self.service.process_frame(messages_frame, "DOWNSTREAM")

        await asyncio.sleep(0.2) # Allow processing

        found_error_frame = False
        for call_args in self.service.push_frame.call_args_list:
            frame = call_args[0][0]
            if isinstance(frame, ErrorFrame):
                self.assertIn(tool_call_id, frame.error)
                self.assertIn("failed", frame.error.lower())
                self.assertIn("JSON decoding failed", frame.error)
                found_error_frame = True
                break
        self.assertTrue(found_error_frame, "ErrorFrame for JSON decoding error not found or incorrect")

if __name__ == '__main__':
    unittest.main()
