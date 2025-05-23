import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple, List
import logging

from backend.app.models.tool_calling_models import (
    ToolCallState,
    ToolCallStatus,
    InitiateToolCallRequest,
    SubmitArgumentChunkRequest,
    ToolSchema
)
from .tool_call_state_store import ToolCallStateStore
from .tool_schema_manager import ToolSchemaManager
from .validation_service import ValidationService

class ArgumentAccumulatorService:
    def __init__(self, state_store: ToolCallStateStore, schema_manager: ToolSchemaManager, validation_service: ValidationService):
        self.state_store = state_store
        self.schema_manager = schema_manager
        self.validation_service = validation_service
        self.logger = logging.getLogger(__name__)
        self._notification_queues: Dict[str, asyncio.Queue] = {}
        self._queue_locks: Dict[str, asyncio.Lock] = {} # For managing access to _notification_queues entries

    async def _get_notification_queue_lock(self, tool_call_id: str) -> asyncio.Lock:
        # This lock is for synchronizing access to the self._notification_queues dictionary for a specific tool_call_id
        if tool_call_id not in self._queue_locks:
            self._queue_locks[tool_call_id] = asyncio.Lock()
        return self._queue_locks[tool_call_id]

    async def _get_or_create_notification_queue(self, tool_call_id: str) -> asyncio.Queue:
        lock = await self._get_notification_queue_lock(tool_call_id)
        async with lock:
            if tool_call_id not in self._notification_queues:
                self._notification_queues[tool_call_id] = asyncio.Queue()
                self.logger.debug(f"Notification queue created for tool_call_id: {tool_call_id}")
            return self._notification_queues[tool_call_id]

    async def subscribe_to_notifications(self, tool_call_id: str) -> asyncio.Queue:
        self.logger.info(f"New subscription for notifications for tool_call_id: {tool_call_id}")
        return await self._get_or_create_notification_queue(tool_call_id)

    async def _notify_subscribers(self, tool_call_id: str, event: Dict[str, Any]):
        lock = await self._get_notification_queue_lock(tool_call_id)
        async with lock:
            if tool_call_id in self._notification_queues:
                try:
                    queue = self._notification_queues[tool_call_id]
                    await queue.put(event)
                    self.logger.debug(f"Notified subscribers for {tool_call_id} with event: {event.get('status')}")

                    # Clean up queue and lock for terminal events
                    status = event.get("status")
                    if status in [ToolCallStatus.COMPLETED, ToolCallStatus.FAILED, ToolCallStatus.CANCELLED, ToolCallStatus.TIMEOUT]:
                        del self._notification_queues[tool_call_id]
                        # The lock itself in _queue_locks can be removed too
                        if tool_call_id in self._queue_locks: # Should always be true if queue existed
                            del self._queue_locks[tool_call_id]
                        self.logger.info(f"Notification queue and lock cleaned up for terminal event {status} for {tool_call_id}")
                except Exception as e:
                    self.logger.error(f"Error notifying subscribers for {tool_call_id}: {e}", exc_info=True)
            else:
                self.logger.debug(f"No active notification queue for {tool_call_id} to send event: {event.get('status')}")


    async def initiate_tool_call(self, request: InitiateToolCallRequest) -> str:
        tool_call_id = request.tool_call_id or str(uuid.uuid4())
        
        schema = request.tool_schema
        if not schema:
            schema = self.schema_manager.get_schema(request.tool_name)
            if not schema:
                self.logger.error(f"Schema not found for tool: {request.tool_name}")
                raise ValueError(f"Schema not found for tool: {request.tool_name}")

        initial_state = ToolCallState(
            tool_call_id=tool_call_id,
            tool_name=request.tool_name,
            tool_schema=schema,
            status=ToolCallStatus.PENDING
            # created_at and last_activity_at are set by Pydantic default_factory
        )
        
        try:
            await self.state_store.create_state(initial_state)
            self.logger.info(f"Tool call initiated: {tool_call_id} for tool {request.tool_name}")
            return tool_call_id
        except ValueError as e: # Handles case where state already exists
            self.logger.error(f"Failed to initiate tool call {tool_call_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error initiating tool call {tool_call_id}: {e}", exc_info=True)
            # Potentially update state to FAILED if it was partially created or if this is critical
            raise # Re-raise the original error after logging

    async def submit_argument_chunk(self, request: SubmitArgumentChunkRequest) -> Tuple[bool, Optional[str]]:
        state = await self.state_store.get_state(request.tool_call_id)

        if not state:
            self.logger.warning(f"Submit chunk: Tool call ID {request.tool_call_id} not found.")
            return False, "Tool call ID not found"

        if state.status in [ToolCallStatus.COMPLETED, ToolCallStatus.FAILED, ToolCallStatus.CANCELLED, ToolCallStatus.TIMEOUT]:
            msg = f"Tool call {request.tool_call_id} is in a terminal state: {state.status}"
            self.logger.warning(f"Submit chunk: {msg}")
            return False, msg

        updated_fields: Dict[str, Any] = {"last_activity_at": datetime.now(timezone.utc)}

        if state.status == ToolCallStatus.PENDING:
            state.status = ToolCallStatus.ACCUMULATING
            updated_fields["status"] = state.status
        
        current_buffers = state.partial_arg_buffers.copy()
        current_buffers[request.sequence_number] = request.chunk_content
        updated_fields["partial_arg_buffers"] = current_buffers
        
        # Optimistically update state with new chunk and status (if changed)
        await self.state_store.update_state(request.tool_call_id, updated_fields)
        state = await self.state_store.get_state(request.tool_call_id) # refresh state
        if not state: # Should not happen if update was successful
             return False, "Failed to retrieve state after update"


        if request.is_last_chunk:
            self.logger.info(f"Last chunk received for {request.tool_call_id}. Attempting reassembly.")
            state.status = ToolCallStatus.REASSEMBLING # Mark reassembling
            await self.state_store.update_state(request.tool_call_id, {"status": state.status})


            # Sort by sequence number and join
            sorted_sequence_numbers = sorted(state.partial_arg_buffers.keys())
            
            # Check for missing chunks if expected_chunk_count was set
            if state.expected_chunk_count is not None and len(sorted_sequence_numbers) != state.expected_chunk_count:
                error_msg = f"Missing chunks: expected {state.expected_chunk_count}, got {len(sorted_sequence_numbers)}"
                self.logger.error(f"Reassembly failed for {request.tool_call_id}: {error_msg}")
                state.status = ToolCallStatus.FAILED
                state.error_details = error_msg
                await self.state_store.update_state(request.tool_call_id, {"status": state.status, "error_details": state.error_details})
                await self._notify_subscribers(request.tool_call_id, {"status": ToolCallStatus.FAILED, "error": error_msg, "tool_call_id": request.tool_call_id})
                return False, error_msg

            full_json_string = "".join(state.partial_arg_buffers[i] for i in sorted_sequence_numbers)
            
            parsed_args: Optional[Dict[str, Any]] = None
            try:
                state.status = ToolCallStatus.VALIDATING # Mark validating
                await self.state_store.update_state(request.tool_call_id, {"status": state.status})

                parsed_args = json.loads(full_json_string)
                self.logger.debug(f"JSON decoded successfully for {request.tool_call_id}")
            except json.JSONDecodeError as e:
                error_msg = f"JSON decoding failed: {e}"
                self.logger.error(f"Reassembly failed for {request.tool_call_id}: {error_msg}")
                state.status = ToolCallStatus.FAILED
                state.error_details = error_msg
                await self.state_store.update_state(request.tool_call_id, {"status": state.status, "error_details": state.error_details, "partial_arg_buffers": {}}) # Clear buffer on error
                await self._notify_subscribers(request.tool_call_id, {"status": ToolCallStatus.FAILED, "error": error_msg, "tool_call_id": request.tool_call_id})
                return False, error_msg

            is_valid, validation_error_msg = self.validation_service.validate_accumulated_arguments(state.tool_schema, parsed_args)
            if not is_valid:
                self.logger.error(f"Validation failed for {request.tool_call_id}: {validation_error_msg}")
                state.status = ToolCallStatus.FAILED
                state.error_details = validation_error_msg
                await self.state_store.update_state(request.tool_call_id, {"status": state.status, "error_details": state.error_details, "partial_arg_buffers": {}}) # Clear buffer on error
                await self._notify_subscribers(request.tool_call_id, {"status": ToolCallStatus.FAILED, "error": validation_error_msg, "tool_call_id": request.tool_call_id})
                return False, validation_error_msg

            self.logger.info(f"Arguments complete and valid for {request.tool_call_id}")
            state.accumulated_args = parsed_args
            state.status = ToolCallStatus.ARGUMENTS_COMPLETE
            state.partial_arg_buffers = {} # Clear buffer
            await self.state_store.update_state(
                request.tool_call_id,
                {"accumulated_args": state.accumulated_args, "status": state.status, "partial_arg_buffers": state.partial_arg_buffers}
            )
            await self._notify_subscribers(request.tool_call_id, {"status": ToolCallStatus.ARGUMENTS_COMPLETE, "data": parsed_args, "tool_call_id": request.tool_call_id})
            return True, "Arguments complete and valid"
        else:
            # Not the last chunk, just acknowledge accumulation
            self.logger.debug(f"Chunk {request.sequence_number} accumulated for {request.tool_call_id}")
            return True, "Chunk accumulated"

    async def cancel_tool_call(self, tool_call_id: str) -> bool:
        state = await self.state_store.get_state(tool_call_id)
        if not state or state.status in [ToolCallStatus.COMPLETED, ToolCallStatus.FAILED, ToolCallStatus.CANCELLED, ToolCallStatus.TIMEOUT]:
            self.logger.warning(f"Cancel request for {tool_call_id}: Not found or already in terminal state ({state.status if state else 'N/A'}).")
            return False

        update_data = {
            "status": ToolCallStatus.CANCELLED,
            "last_activity_at": datetime.now(timezone.utc)
        }
        await self.state_store.update_state(tool_call_id, update_data)
        await self._notify_subscribers(tool_call_id, {"status": ToolCallStatus.CANCELLED, "tool_call_id": tool_call_id})
        self.logger.info(f"Tool call cancelled: {tool_call_id}")
        return True

    async def process_timeout(self, tool_call_id: str):
        """
        Handles notification for a tool call that has been marked as TIMEOUT by the ToolCallStateStore.
        The state store is responsible for updating the state's status to TIMEOUT.
        This method ensures that subscribers are notified of this timeout event.
        """
        state = await self.state_store.get_state(tool_call_id) # State store updates last_activity_at
        
        if state and state.status == ToolCallStatus.TIMEOUT:
            self.logger.warning(f"Processing timeout notification for tool call {tool_call_id}.")
            await self._notify_subscribers(
                tool_call_id, 
                {"status": ToolCallStatus.TIMEOUT, "error": state.error_details or "Tool call timed out", "tool_call_id": tool_call_id}
            )
        elif state:
            self.logger.info(f"process_timeout called for {tool_call_id}, but status is {state.status}, not TIMEOUT.")
        else:
            self.logger.warning(f"process_timeout called for non-existent tool call ID: {tool_call_id}")

    async def get_tool_call_state_details(self, tool_call_id: str) -> Optional[ToolCallState]:
        """ Utility method to get the current state of a tool call. """
        return await self.state_store.get_state(tool_call_id)
