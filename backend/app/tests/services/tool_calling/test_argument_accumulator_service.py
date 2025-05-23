import asyncio
import unittest
import uuid
import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, call

from backend.app.services.tool_calling.argument_accumulator_service import ArgumentAccumulatorService
from backend.app.services.tool_calling.tool_call_state_store import ToolCallStateStore
from backend.app.services.tool_calling.tool_schema_manager import ToolSchemaManager
from backend.app.services.tool_calling.validation_service import ValidationService
from backend.app.models.tool_calling_models import (
    ToolCallState,
    ToolCallStatus,
    InitiateToolCallRequest,
    SubmitArgumentChunkRequest,
    ToolSchema
)

# Disable logging for tests to keep output clean
logging.disable(logging.CRITICAL)

class TestArgumentAccumulatorService(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_state_store = AsyncMock(spec=ToolCallStateStore)
        self.mock_schema_manager = MagicMock(spec=ToolSchemaManager) # Most methods are sync
        self.mock_validation_service = MagicMock(spec=ValidationService) # Most methods are sync

        self.accumulator = ArgumentAccumulatorService(
            self.mock_state_store,
            self.mock_schema_manager,
            self.mock_validation_service
        )
        
        # Patch _notify_subscribers
        self.mock_notify_subscribers = AsyncMock()
        self.accumulator._notify_subscribers = self.mock_notify_subscribers

        self.sample_tool_name = "test_tool"
        self.sample_schema: ToolSchema = {"type": "object", "properties": {"param": {"type": "string"}}, "required": ["param"]}
        self.sample_tool_call_id = str(uuid.uuid4())

    # Test initiate_tool_call
    async def test_initiate_tool_call_success(self):
        self.mock_schema_manager.get_schema.return_value = self.sample_schema
        request = InitiateToolCallRequest(tool_name=self.sample_tool_name, tool_call_id=self.sample_tool_call_id)
        
        tool_call_id_result = await self.accumulator.initiate_tool_call(request)
        self.assertEqual(tool_call_id_result, self.sample_tool_call_id)

        self.mock_state_store.create_state.assert_called_once()
        created_state_arg = self.mock_state_store.create_state.call_args[0][0]
        
        self.assertIsInstance(created_state_arg, ToolCallState)
        self.assertEqual(created_state_arg.tool_call_id, self.sample_tool_call_id)
        self.assertEqual(created_state_arg.tool_name, self.sample_tool_name)
        self.assertEqual(created_state_arg.tool_schema, self.sample_schema)
        self.assertEqual(created_state_arg.status, ToolCallStatus.PENDING)

    async def test_initiate_tool_call_with_provided_schema(self):
        provided_schema: ToolSchema = {"type": "object", "properties": {"arg": {"type": "integer"}}}
        request = InitiateToolCallRequest(tool_name=self.sample_tool_name, tool_schema=provided_schema, tool_call_id=self.sample_tool_call_id)
        
        tool_call_id_result = await self.accumulator.initiate_tool_call(request)
        self.assertEqual(tool_call_id_result, self.sample_tool_call_id)

        self.mock_schema_manager.get_schema.assert_not_called()
        self.mock_state_store.create_state.assert_called_once()
        created_state_arg = self.mock_state_store.create_state.call_args[0][0]
        self.assertEqual(created_state_arg.tool_schema, provided_schema)

    async def test_initiate_tool_call_no_schema_found(self):
        self.mock_schema_manager.get_schema.return_value = None
        request = InitiateToolCallRequest(tool_name="unknown_tool")
        
        async with self.assertRaisesRegex(ValueError, "Schema not found for tool: unknown_tool"):
            await self.accumulator.initiate_tool_call(request)
        self.mock_state_store.create_state.assert_not_called()

    # Test submit_argument_chunk - Successful Path
    async def test_submit_argument_chunk_accumulate_and_complete(self):
        # Initial state setup
        current_state = ToolCallState(
            tool_call_id=self.sample_tool_call_id,
            tool_name=self.sample_tool_name,
            tool_schema=self.sample_schema,
            status=ToolCallStatus.PENDING
        )
        # Mock get_state to return the current state, then subsequent updated states
        self.mock_state_store.get_state.return_value = current_state
        
        self.mock_validation_service.validate_accumulated_arguments.return_value = (True, None)

        # Chunk 1
        req1 = SubmitArgumentChunkRequest(tool_call_id=self.sample_tool_call_id, chunk_content='{"param": "', sequence_number=0, is_last_chunk=False)
        success, msg = await self.accumulator.submit_argument_chunk(req1)
        self.assertTrue(success)
        self.assertEqual(msg, "Chunk accumulated")

        # Verify update_state call after chunk 1
        self.mock_state_store.update_state.assert_any_call(
            self.sample_tool_call_id,
            unittest.mock.ANY # Checking specific content is complex due to datetime
        )
        # Update current_state to reflect changes for next get_state call
        current_state.status = ToolCallStatus.ACCUMULATING
        current_state.partial_arg_buffers = {0: '{"param": "'}
        
        # Chunk 2 (last chunk)
        req2 = SubmitArgumentChunkRequest(tool_call_id=self.sample_tool_call_id, chunk_content='value"}', sequence_number=1, is_last_chunk=True)
        success, msg = await self.accumulator.submit_argument_chunk(req2)
        self.assertTrue(success)
        self.assertEqual(msg, "Arguments complete and valid")

        # Check the final update_state call content
        # There will be multiple calls, ensure the last one is for ARGUMENTS_COMPLETE
        final_update_call = None
        for call_item in self.mock_state_store.update_state.call_args_list:
            if call_item[0][1].get("status") == ToolCallStatus.ARGUMENTS_COMPLETE:
                final_update_call = call_item
                break
        
        self.assertIsNotNone(final_update_call, "ARGUMENTS_COMPLETE update not found")
        args, _ = final_update_call
        self.assertEqual(args[0], self.sample_tool_call_id)
        self.assertEqual(args[1]['status'], ToolCallStatus.ARGUMENTS_COMPLETE)
        self.assertEqual(args[1]['accumulated_args'], {"param": "value"})
        self.assertEqual(args[1]['partial_arg_buffers'], {}) # Buffer should be cleared

        # Check notification
        self.mock_notify_subscribers.assert_called_with(
            self.sample_tool_call_id,
            {"status": ToolCallStatus.ARGUMENTS_COMPLETE, "data": {"param": "value"}, "tool_call_id": self.sample_tool_call_id}
        )

    # Test submit_argument_chunk - Error Paths
    async def test_submit_argument_chunk_tool_call_not_found(self):
        self.mock_state_store.get_state.return_value = None
        request = SubmitArgumentChunkRequest(tool_call_id="unknown_id", chunk_content="{}", sequence_number=0, is_last_chunk=True)
        success, message = await self.accumulator.submit_argument_chunk(request)
        self.assertFalse(success)
        self.assertEqual(message, "Tool call ID not found")

    async def test_submit_argument_chunk_terminal_state(self):
        state = ToolCallState(tool_call_id=self.sample_tool_call_id, tool_name="t", tool_schema={}, status=ToolCallStatus.COMPLETED)
        self.mock_state_store.get_state.return_value = state
        request = SubmitArgumentChunkRequest(tool_call_id=self.sample_tool_call_id, chunk_content="{}", sequence_number=0, is_last_chunk=True)
        success, message = await self.accumulator.submit_argument_chunk(request)
        self.assertFalse(success)
        self.assertIn("Tool call is in a terminal state", message)

    async def test_submit_argument_chunk_json_decoding_error(self):
        state = ToolCallState(
            tool_call_id=self.sample_tool_call_id, 
            tool_name=self.sample_tool_name, 
            tool_schema=self.sample_schema, 
            status=ToolCallStatus.ACCUMULATING,
            partial_arg_buffers={0: '{"param": "value'} # Malformed JSON
        )
        self.mock_state_store.get_state.return_value = state
        
        request = SubmitArgumentChunkRequest(tool_call_id=self.sample_tool_call_id, chunk_content="", sequence_number=1, is_last_chunk=True)
        success, message = await self.accumulator.submit_argument_chunk(request)
        
        self.assertFalse(success)
        self.assertIn("JSON decoding failed", message)
        
        # Check state store update for FAILED status
        failed_update_call = None
        for call_item in self.mock_state_store.update_state.call_args_list:
            if call_item[0][1].get("status") == ToolCallStatus.FAILED:
                failed_update_call = call_item
                break
        self.assertIsNotNone(failed_update_call, "FAILED status update not found")
        args, _ = failed_update_call
        self.assertEqual(args[1]['status'], ToolCallStatus.FAILED)
        self.assertIn("JSON decoding failed", args[1]['error_details'])

        self.mock_notify_subscribers.assert_called_with(
            self.sample_tool_call_id,
            unittest.mock.ANY # More specific check if needed: {"status": ToolCallStatus.FAILED, "error": message_containing_json_error, ...}
        )
        self.assertEqual(self.mock_notify_subscribers.call_args[0][1]['status'], ToolCallStatus.FAILED)


    async def test_submit_argument_chunk_validation_error(self):
        state = ToolCallState(
            tool_call_id=self.sample_tool_call_id, 
            tool_name=self.sample_tool_name, 
            tool_schema=self.sample_schema, 
            status=ToolCallStatus.ACCUMULATING,
            partial_arg_buffers={0: '{"param_wrong": "value"}'} # Valid JSON, but invalid against schema
        )
        self.mock_state_store.get_state.return_value = state
        self.mock_validation_service.validate_accumulated_arguments.return_value = (False, "Schema validation failed")
        
        request = SubmitArgumentChunkRequest(tool_call_id=self.sample_tool_call_id, chunk_content="", sequence_number=1, is_last_chunk=True)
        success, message = await self.accumulator.submit_argument_chunk(request)

        self.assertFalse(success)
        self.assertEqual(message, "Schema validation failed")

        failed_update_call = None
        for call_item in self.mock_state_store.update_state.call_args_list:
            if call_item[0][1].get("status") == ToolCallStatus.FAILED:
                failed_update_call = call_item
                break
        self.assertIsNotNone(failed_update_call, "FAILED status update not found")
        args, _ = failed_update_call
        self.assertEqual(args[1]['status'], ToolCallStatus.FAILED)
        self.assertEqual(args[1]['error_details'], "Schema validation failed")

        self.mock_notify_subscribers.assert_called_with(
            self.sample_tool_call_id,
            {"status": ToolCallStatus.FAILED, "error": "Schema validation failed", "tool_call_id": self.sample_tool_call_id}
        )

    # Test cancel_tool_call
    async def test_cancel_tool_call_success(self):
        state = ToolCallState(tool_call_id=self.sample_tool_call_id, tool_name="t", tool_schema={}, status=ToolCallStatus.PENDING)
        self.mock_state_store.get_state.return_value = state
        
        cancelled = await self.accumulator.cancel_tool_call(self.sample_tool_call_id)
        self.assertTrue(cancelled)
        
        self.mock_state_store.update_state.assert_called_once()
        args, _ = self.mock_state_store.update_state.call_args
        self.assertEqual(args[0], self.sample_tool_call_id)
        self.assertEqual(args[1]['status'], ToolCallStatus.CANCELLED)
        
        self.mock_notify_subscribers.assert_called_with(
            self.sample_tool_call_id,
            {"status": ToolCallStatus.CANCELLED, "tool_call_id": self.sample_tool_call_id}
        )

    async def test_cancel_tool_call_not_found_or_terminal(self):
        self.mock_state_store.get_state.return_value = None
        cancelled_not_found = await self.accumulator.cancel_tool_call(self.sample_tool_call_id)
        self.assertFalse(cancelled_not_found)
        self.mock_state_store.update_state.assert_not_called()
        self.mock_notify_subscribers.assert_not_called()

        state_completed = ToolCallState(tool_call_id=self.sample_tool_call_id, tool_name="t", tool_schema={}, status=ToolCallStatus.COMPLETED)
        self.mock_state_store.get_state.return_value = state_completed
        cancelled_terminal = await self.accumulator.cancel_tool_call(self.sample_tool_call_id)
        self.assertFalse(cancelled_terminal)
        # update_state should not be called if already terminal, and no notification for re-cancelling
        self.mock_state_store.update_state.assert_not_called() # Assuming it was not called for the None case
        self.mock_notify_subscribers.assert_not_called()


    # Test Notification Subscription
    async def test_subscribe_to_notifications(self):
        queue = await self.accumulator.subscribe_to_notifications(self.sample_tool_call_id)
        self.assertIsInstance(queue, asyncio.Queue)
        self.assertIn(self.sample_tool_call_id, self.accumulator._notification_queues)
        self.assertEqual(self.accumulator._notification_queues[self.sample_tool_call_id], queue)

    # Test process_timeout
    async def test_process_timeout_notifies(self):
        timeout_state = ToolCallState(
            tool_call_id=self.sample_tool_call_id,
            tool_name=self.sample_tool_name,
            tool_schema=self.sample_schema,
            status=ToolCallStatus.TIMEOUT,
            error_details="Tool call timed out by store"
        )
        self.mock_state_store.get_state.return_value = timeout_state

        await self.accumulator.process_timeout(self.sample_tool_call_id)

        self.mock_notify_subscribers.assert_called_once_with(
            self.sample_tool_call_id,
            {"status": ToolCallStatus.TIMEOUT, "error": "Tool call timed out by store", "tool_call_id": self.sample_tool_call_id}
        )

    async def test_process_timeout_wrong_status(self):
        active_state = ToolCallState(
            tool_call_id=self.sample_tool_call_id,
            tool_name=self.sample_tool_name,
            tool_schema=self.sample_schema,
            status=ToolCallStatus.ACCUMULATING
        )
        self.mock_state_store.get_state.return_value = active_state
        await self.accumulator.process_timeout(self.sample_tool_call_id)
        self.mock_notify_subscribers.assert_not_called()

    async def test_process_timeout_no_state(self):
        self.mock_state_store.get_state.return_value = None
        await self.accumulator.process_timeout(self.sample_tool_call_id)
        self.mock_notify_subscribers.assert_not_called()


if __name__ == '__main__':
    unittest.main()
