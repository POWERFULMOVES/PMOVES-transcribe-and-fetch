import asyncio
import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone, timedelta
import uuid
import logging

from backend.app.services.tool_calling.tool_call_state_store import ToolCallStateStore
from backend.app.models.tool_calling_models import ToolCallState, ToolCallStatus

# Disable logging for tests to keep output clean, unless specifically testing logging
logging.disable(logging.CRITICAL)

class TestToolCallStateStore(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Using short timeouts for easier testing
        self.idle_timeout_seconds = 2  # Short idle timeout
        self.total_timeout_seconds = 4 # Short total timeout
        
        # Patch the config values used by the store if they are directly imported at module level
        # For this test, we pass them directly to constructor, so module patching isn't strictly needed here for these values
        # but it's good practice if the store relied on them directly from app_config at module level.
        # We also need to control TOOL_CALL_CLEANUP_INTERVAL_SECONDS for tests.
        self.cleanup_interval_seconds = 1 
        
        self.patcher_idle = patch('backend.app.services.tool_calling.tool_call_state_store.TOOL_CALL_IDLE_TIMEOUT_SECONDS', self.idle_timeout_seconds)
        self.patcher_total = patch('backend.app.services.tool_calling.tool_call_state_store.TOOL_CALL_TOTAL_TIMEOUT_SECONDS', self.total_timeout_seconds)
        self.patcher_cleanup = patch('backend.app.services.tool_calling.tool_call_state_store.TOOL_CALL_CLEANUP_INTERVAL_SECONDS', self.cleanup_interval_seconds)

        self.mock_idle_config = self.patcher_idle.start()
        self.mock_total_config = self.patcher_total.start()
        self.mock_cleanup_config = self.patcher_cleanup.start()

        self.store = ToolCallStateStore(
            idle_timeout_seconds=self.idle_timeout_seconds,
            total_timeout_seconds=self.total_timeout_seconds
        )
        # The store's __init__ will use the passed values, or if it used module-level defaults, the patches would apply.

        self.sample_tool_call_id = str(uuid.uuid4())
        self.sample_schema = {"type": "object", "properties": {"param": {"type": "string"}}}
        self.initial_state = ToolCallState(
            tool_call_id=self.sample_tool_call_id,
            tool_name="test_tool",
            tool_schema=self.sample_schema,
            status=ToolCallStatus.PENDING
            # created_at and last_activity_at will be set by Pydantic/Store
        )

    async def asyncTearDown(self):
        if self.store:
            await self.store.stop_cleanup_worker()
        self.patcher_idle.stop()
        self.patcher_total.stop()
        self.patcher_cleanup.stop()


    async def test_create_and_get_state(self):
        created_time_before = datetime.now(timezone.utc)
        await self.store.create_state(self.initial_state)
        created_time_after = datetime.now(timezone.utc)

        state = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNotNone(state)
        self.assertEqual(state.tool_call_id, self.sample_tool_call_id)
        self.assertEqual(state.status, ToolCallStatus.PENDING)
        # Check if created_at is within the expected range
        self.assertTrue(created_time_before <= state.created_at <= created_time_after)
        
        original_last_activity_at = state.last_activity_at
        await asyncio.sleep(0.01) # Ensure time advances
        state_after_get = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNotNone(state_after_get)
        self.assertTrue(state_after_get.last_activity_at > original_last_activity_at)

    async def test_create_state_already_exists(self):
        await self.store.create_state(self.initial_state)
        with self.assertRaises(ValueError):
            await self.store.create_state(self.initial_state)

    async def test_get_nonexistent_state(self):
        state = await self.store.get_state(str(uuid.uuid4()))
        self.assertIsNone(state)

    async def test_update_state(self):
        await self.store.create_state(self.initial_state)
        original_state = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNotNone(original_state)
        original_last_activity = original_state.last_activity_at

        await asyncio.sleep(0.01) # Ensure time advances for last_activity_at update
        updates = {"status": ToolCallStatus.ACCUMULATING, "accumulated_args": {"key": "value"}}
        updated_state = await self.store.update_state(self.sample_tool_call_id, updates)
        self.assertIsNotNone(updated_state)
        self.assertEqual(updated_state.status, ToolCallStatus.ACCUMULATING)
        self.assertEqual(updated_state.accumulated_args, {"key": "value"})
        self.assertTrue(updated_state.last_activity_at > original_last_activity)

    async def test_update_nonexistent_state(self):
        updated_state = await self.store.update_state(str(uuid.uuid4()), {"status": ToolCallStatus.COMPLETED})
        self.assertIsNone(updated_state)

    async def test_delete_state(self):
        await self.store.create_state(self.initial_state)
        self.assertIn(self.sample_tool_call_id, self.store._locks) # Check lock exists

        deleted = await self.store.delete_state(self.sample_tool_call_id)
        self.assertTrue(deleted)

        state_after_delete = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNone(state_after_delete)
        self.assertNotIn(self.sample_tool_call_id, self.store._locks) # Check lock is removed

    async def test_delete_nonexistent_state(self):
        deleted = await self.store.delete_state(str(uuid.uuid4()))
        self.assertFalse(deleted)

    @patch('asyncio.sleep', new_callable=AsyncMock)
    @patch('backend.app.services.tool_calling.tool_call_state_store.datetime')
    async def test_idle_timeout(self, mock_datetime, mock_sleep):
        # Let one sleep cycle pass, then raise CancelledError to stop the worker
        mock_sleep.side_effect = [None, asyncio.CancelledError()] 
        
        t0 = datetime.now(timezone.utc)
        mock_datetime.now.return_value = t0
        
        await self.store.create_state(self.initial_state)
        initial_db_state = await self.store.get_state(self.sample_tool_call_id) # Sets initial activity
        self.assertIsNotNone(initial_db_state)

        await self.store.start_cleanup_worker() # Start the worker

        # Advance time past idle timeout but not total timeout
        mock_datetime.now.return_value = t0 + timedelta(seconds=self.idle_timeout_seconds + 1)
        
        with self.assertRaises(asyncio.CancelledError): # Expected from mock_sleep
            await self.store._cleanup_task 

        state_after_timeout = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNone(state_after_timeout) # State should be deleted by timeout logic

    @patch('asyncio.sleep', new_callable=AsyncMock)
    @patch('backend.app.services.tool_calling.tool_call_state_store.datetime')
    async def test_total_timeout(self, mock_datetime, mock_sleep):
        mock_sleep.side_effect = [None, asyncio.CancelledError()]

        t0 = datetime.now(timezone.utc)
        mock_datetime.now.return_value = t0
        
        # Manually set created_at to be old for testing total timeout
        self.initial_state.created_at = t0 - timedelta(seconds=self.total_timeout_seconds - 1)
        self.initial_state.last_activity_at = t0 # Activity is recent
        await self.store.create_state(self.initial_state)

        await self.store.start_cleanup_worker()

        # Advance time past total timeout
        mock_datetime.now.return_value = t0 + timedelta(seconds=2) # created_at is now past total_timeout

        with self.assertRaises(asyncio.CancelledError):
            await self.store._cleanup_task

        state_after_timeout = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNone(state_after_timeout)

    @patch('asyncio.sleep', new_callable=AsyncMock)
    @patch('backend.app.services.tool_calling.tool_call_state_store.datetime')
    async def test_state_not_timed_out_if_active(self, mock_datetime, mock_sleep):
        mock_sleep.side_effect = [None, asyncio.CancelledError()]

        t0 = datetime.now(timezone.utc)
        mock_datetime.now.return_value = t0
        
        await self.store.create_state(self.initial_state)
        
        await self.store.start_cleanup_worker()

        # Advance time close to idle timeout
        t_activity = t0 + timedelta(seconds=self.idle_timeout_seconds - 1)
        mock_datetime.now.return_value = t_activity
        active_state = await self.store.get_state(self.sample_tool_call_id) # This updates last_activity_at
        self.assertIsNotNone(active_state)

        # Advance time just past original idle timeout (but activity was recent)
        mock_datetime.now.return_value = t0 + timedelta(seconds=self.idle_timeout_seconds + 1)

        with self.assertRaises(asyncio.CancelledError):
             await self.store._cleanup_task
        
        state_after_cleanup_run = await self.store.get_state(self.sample_tool_call_id)
        self.assertIsNotNone(state_after_cleanup_run) # State should still exist

    async def test_start_and_stop_cleanup_worker(self):
        self.assertIsNone(self.store._cleanup_task)
        await self.store.start_cleanup_worker()
        self.assertIsNotNone(self.store._cleanup_task)
        self.assertFalse(self.store._cleanup_task.done())

        await self.store.stop_cleanup_worker()
        # The task might be cancelled or None after stop_cleanup_worker
        if self.store._cleanup_task is not None: # If task is not None, it should be done
            self.assertTrue(self.store._cleanup_task.done()) 
        
        # Call stop again, should not raise error
        await self.store.stop_cleanup_worker()


if __name__ == '__main__':
    unittest.main()
