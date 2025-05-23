import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple, Any
from backend.app.models.tool_calling_models import ToolCallState, ToolCallStatus
import logging

# Configure basic logging if running standalone for testing
# logging.basicConfig(level=logging.INFO)

DEFAULT_IDLE_TIMEOUT_SECONDS = 300  # 5 minutes
DEFAULT_TOTAL_TIMEOUT_SECONDS = 3600  # 1 hour
CLEANUP_INTERVAL_SECONDS = 60  # 1 minute

class ToolCallStateStore:
    def __init__(self, idle_timeout_seconds: int = DEFAULT_IDLE_TIMEOUT_SECONDS, total_timeout_seconds: int = DEFAULT_TOTAL_TIMEOUT_SECONDS):
        self._active_states: Dict[str, ToolCallState] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self.idle_timeout_seconds = idle_timeout_seconds
        self.total_timeout_seconds = total_timeout_seconds
        self.logger = logging.getLogger(__name__)
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start_cleanup_worker(self):
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            self.logger.info("ToolCallStateStore cleanup worker started.")
        else:
            self.logger.info("ToolCallStateStore cleanup worker already running.")

    async def stop_cleanup_worker(self):
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                self.logger.info("ToolCallStateStore cleanup worker cancelled.")
            finally:
                self._cleanup_task = None
                self.logger.info("ToolCallStateStore cleanup worker stopped.")
        else:
            self.logger.info("ToolCallStateStore cleanup worker not running or already stopped.")

    async def _get_lock(self, tool_call_id: str) -> asyncio.Lock:
        # This method assumes that _locks dictionary itself doesn't need a separate lock
        # for this simple retrieval/creation, as asyncio.Lock() is thread-safe for instantiation.
        # If _locks were to be frequently modified by many coroutines simultaneously in complex ways,
        # (e.g. clearing, iterating and modifying by other admin tasks), then _locks itself might need a lock.
        if tool_call_id not in self._locks:
            self._locks[tool_call_id] = asyncio.Lock()
        return self._locks[tool_call_id]

    async def create_state(self, initial_state: ToolCallState) -> None:
        lock = await self._get_lock(initial_state.tool_call_id)
        async with lock:
            if initial_state.tool_call_id in self._active_states:
                raise ValueError(f"Tool call state with ID {initial_state.tool_call_id} already exists.")
            # Ensure created_at and last_activity_at are set if not already (Pydantic default_factory should handle this)
            current_time = datetime.now(timezone.utc)
            if initial_state.created_at.tzinfo is None: # Ensure timezone aware
                 initial_state.created_at = current_time
            initial_state.last_activity_at = current_time # Always set/update last_activity_at on creation

            self._active_states[initial_state.tool_call_id] = initial_state
            self.logger.info(f"Tool call state created: {initial_state.tool_call_id}")

    async def get_state(self, tool_call_id: str) -> Optional[ToolCallState]:
        lock = await self._get_lock(tool_call_id)
        async with lock:
            state = self._active_states.get(tool_call_id)
            if state:
                state.last_activity_at = datetime.now(timezone.utc)
                self.logger.debug(f"Tool call state retrieved, last_activity_at updated: {tool_call_id}")
            return state

    async def update_state(self, tool_call_id: str, updates: Dict[str, Any]) -> Optional[ToolCallState]:
        lock = await self._get_lock(tool_call_id)
        async with lock:
            existing_state = self._active_states.get(tool_call_id)
            if not existing_state:
                self.logger.warning(f"Attempted to update non-existent state: {tool_call_id}")
                return None

            # Ensure last_activity_at is always updated.
            updates_with_activity = updates.copy()
            updates_with_activity['last_activity_at'] = datetime.now(timezone.utc)
            
            try:
                updated_state = existing_state.model_copy(update=updates_with_activity)
                self._active_states[tool_call_id] = updated_state
                self.logger.debug(f"Tool call state updated: {tool_call_id}, updates: {updates}")
                return updated_state
            except Exception as e: # Broad exception for Pydantic validation or other errors
                self.logger.error(f"Error updating state for {tool_call_id}: {e}. Updates: {updates_with_activity}")
                return None


    async def delete_state(self, tool_call_id: str) -> bool:
        lock = await self._get_lock(tool_call_id)
        async with lock:
            if tool_call_id in self._active_states:
                del self._active_states[tool_call_id]
                # Also remove the lock for this ID to prevent self._locks from growing indefinitely
                if tool_call_id in self._locks:
                    del self._locks[tool_call_id]
                self.logger.info(f"Tool call state deleted: {tool_call_id}")
                return True
            self.logger.warning(f"Attempted to delete non-existent state: {tool_call_id}")
            return False

    async def _periodic_cleanup(self):
        self.logger.info("Periodic cleanup task started.")
        try:
            while True:
                await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
                self.logger.debug("Running periodic cleanup scan...")
                now = datetime.now(timezone.utc)
                
                # Iterate over a copy of keys to allow modification
                tool_call_ids_to_check = list(self._active_states.keys())

                for tool_call_id in tool_call_ids_to_check:
                    lock = await self._get_lock(tool_call_id) # Get lock for this specific state
                    async with lock:
                        state = self._active_states.get(tool_call_id)
                        if not state: # State might have been deleted since we got the keys
                            continue

                        timed_out = False
                        reason = ""

                        # Check for total timeout
                        if (now - state.created_at).total_seconds() > self.total_timeout_seconds:
                            timed_out = True
                            reason = "total lifetime"
                            self.logger.info(f"Tool call {tool_call_id} exceeded total timeout ({self.total_timeout_seconds}s).")
                        
                        # Check for idle timeout
                        elif (now - state.last_activity_at).total_seconds() > self.idle_timeout_seconds:
                            timed_out = True
                            reason = "idle activity"
                            self.logger.info(f"Tool call {tool_call_id} exceeded idle timeout ({self.idle_timeout_seconds}s).")

                        if timed_out:
                            self.logger.info(f"Timing out state {tool_call_id} due to {reason}.")
                            state.status = ToolCallStatus.TIMEOUT
                            state.last_activity_at = now # Update activity time for the timeout event
                            # No need to call self.update_state as we have the lock and will delete it
                            
                            # Delete the state
                            if tool_call_id in self._active_states: # Re-check before delete
                                del self._active_states[tool_call_id]
                            if tool_call_id in self._locks: # And its lock
                                del self._locks[tool_call_id]
                            self.logger.info(f"Tool call state {tool_call_id} deleted due to {reason} timeout.")
                self.logger.debug("Periodic cleanup scan complete.")
        except asyncio.CancelledError:
            self.logger.info("Periodic cleanup task was cancelled.")
            # Propagate cancellation if necessary or handle cleanup
        except Exception as e:
            self.logger.error(f"Unexpected error in periodic cleanup: {e}", exc_info=True)
            # Consider if the task should attempt to restart or if it should terminate.
            # For now, it terminates on unexpected errors.
        finally:
            self.logger.info("Periodic cleanup task finished.")
