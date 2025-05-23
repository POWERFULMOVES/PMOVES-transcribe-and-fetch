#
# Copyright (c) 2024-2025, PMOVES
#
# SPDX-License-Identifier: Apache-2.0
#

import asyncio
import os
import litellm
from litellm.exceptions import (
    APIConnectionError,
    BadRequestError,
    ContextWindowExceededError,
    NotFoundError,
    PermissionDeniedError,
    ServiceUnavailableError,
    Timeout,
    AuthenticationError,
    RateLimitError,
    APIError
)
import logging
import httpx
import uuid # Added
import json # Added for dumping assembled args
from typing import Dict, Any # Added for type hinting

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMMessagesFrame,
    LLMTextFrame,
    FunctionCallInProgressFrame,
    ErrorFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.llm_service import LLMService

# Import the LLMRegistryService
from backend.app.utils.llm_registry_service import LLMRegistryService

# Imports for Tool Calling Integration
from backend.app.models.tool_calling_models import ( # Added
    ToolCallStatus,
    InitiateToolCallRequest,
    SubmitArgumentChunkRequest
)
from backend.app.services.tool_calling.argument_accumulator_service import ArgumentAccumulatorService # Added
from backend.app.services.tool_calling.tool_schema_manager import ToolSchemaManager # Added
from backend.app.services.tool_calling.tool_call_state_store import ToolCallStateStore # Added
from backend.app.services.tool_calling.validation_service import ValidationService # Added


logger = logging.getLogger(__name__)

class LiteLLMPipecatService(LLMService):
    """
    A Pipecat LLM Service that uses LiteLLM for interacting with various LLMs.
    Handles streaming responses from LiteLLM and pushes them as Pipecat frames.
    Integrates with the LLMRegistryService for dynamic model selection.
    Integrates with ArgumentAccumulatorService for robust tool call argument handling.
    """

    def __init__(self, llm_registry_service: LLMRegistryService, preferred_model_alias: str, litellm_router: litellm.Router, **kwargs):
        """
        Initializes the LiteLLMPipecatService.

        Args:
            llm_registry_service: An instance of the LLMRegistryService.
            preferred_model_alias: The alias of the preferred model from the registry.
            litellm_router: An initialized LiteLLM Router instance.
            **kwargs: Additional keyword arguments for the base LLMService.
        """
        super().__init__(**kwargs)
        self._llm_registry_service = llm_registry_service
        self._preferred_model_alias = preferred_model_alias
        self._litellm_router = litellm_router
        self._model_id = None
        self._messages = []
        
        # Tool Calling Integration Initialization
        self._tool_schema_manager = ToolSchemaManager()
        self._tool_call_state_store = ToolCallStateStore()
        # Start the cleanup worker for the state store.
        # Note: If LiteLLMPipecatService instances are short-lived, this might repeatedly start/stop.
        # Ideally, ToolCallStateStore would be a longer-lived singleton.
        # Consider a more robust lifecycle management for state_store if this service is frequently created/destroyed.
        asyncio.create_task(self._tool_call_state_store.start_cleanup_worker())

        self._validation_service = ValidationService()
        self._argument_accumulator_service = ArgumentAccumulatorService(
            state_store=self._tool_call_state_store,
            schema_manager=self._tool_schema_manager,
            validation_service=self._validation_service
        )
        self._active_tool_call_streams: Dict[str, Dict[str, Any]] = {}


    async def cleanup(self):
        """
        Clean up resources, like stopping the ToolCallStateStore worker.
        This method might be called if the Pipecat pipeline has a teardown phase.
        """
        logger.info("Cleaning up LiteLLMPipecatService, stopping ToolCallStateStore worker.")
        if self._tool_call_state_store:
            await self._tool_call_state_store.stop_cleanup_worker()
        await super().cleanup()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """
        Processes incoming frames and triggers LLM calls for messages.
        """
        # Process incoming frames (e.g., user messages)
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMMessagesFrame) and direction == FrameDirection.DOWNSTREAM:
            # Assuming LLMMessagesFrame contains the message history
            self._messages = frame.messages

            # Fetch LiteLLM config (specifically model_id) from registry before triggering LLM call
            await self._fetch_litellm_config()

            if self._litellm_router and self._model_id:
                # Trigger the LLM call
                await self._get_llm_response_streaming()
            else:
                logger.error(f"Failed to fetch LiteLLM config for model alias: {self._preferred_model_alias}. Cannot process message.")
                await self.push_frame(ErrorFrame(f"Failed to load model {self._preferred_model_alias}"), FrameDirection.DOWNSTREAM) # Ensure this is pushed downstream
                return # Do not push the original frame if we error out here.

        # Pass the frame along the pipeline
        # Only push the original frame if it wasn't an LLMMessagesFrame causing an LLM call
        # or if the LLM call was successfully initiated.
        # If it was an LLMMessagesFrame, the response frames will be pushed by _get_llm_response_streaming
        if not (isinstance(frame, LLMMessagesFrame) and direction == FrameDirection.DOWNSTREAM):
            await self.push_frame(frame, direction)


    async def _fetch_litellm_config(self):
        """
        Fetches the LiteLLM model ID and other details from the LLMRegistryService
        based on the preferred model alias.
        """
        try:
            model_info = self._llm_registry_service.get_model_details(self._preferred_model_alias)
            if model_info:
                # Assuming model_info.model_id is the identifier needed for router.acompletion
                self._model_id = model_info.model_id
                # You can potentially store other model_info details here if needed later

                if not self._model_id:
                     logger.error(f"Model ID not found in registry details for alias {self._preferred_model_alias}.")
            else:
                logger.error(f"Model alias {self._preferred_model_alias} not found in registry.")

        except Exception as e:
            logger.error(f"Error fetching model details from registry for alias {self._preferred_model_alias}: {e}", exc_info=True)
            self._model_id = None # Ensure model_id is None if fetching fails


    async def _get_llm_response_streaming(self):
        """
        Makes a streaming call to LiteLLM and pushes response chunks as frames.
        """
        if not self._messages or not self._litellm_router or not self._model_id:
            logger.error("Attempted to get LLM response without messages, router, or model ID.")
            return

        logger.debug(f"Making LiteLLM streaming call with model ID: {self._model_id}")
        self._active_tool_call_streams.clear() # Clear for new LLM response processing

        try:
            await self.push_frame(LLMFullResponseStartFrame())

            stream_response = await self._litellm_router.acompletion(
                model=self._model_id,
                messages=self._messages,
                stream=True,
                # Ensure tools are passed if required by the model/LiteLLM setup
                # tools=self._tool_schema_manager.get_all_schemas_for_llm() # Example
            )

            async for chunk in stream_response:
                content = chunk.choices[0].delta.content or ""
                if content:
                    await self.push_frame(LLMTextFrame(content))

                tool_calls = getattr(chunk.choices[0].delta, 'tool_calls', None)
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_call_id = getattr(tool_call, 'id', None)
                        function_name = getattr(tool_call.function, 'name', None)
                        function_arguments_chunk = getattr(tool_call.function, 'arguments', None)
                        # tool_call_index = getattr(tool_call, 'index', 0) # LiteLLM might provide this

                        if tool_call_id and function_name and tool_call_id not in self._active_tool_call_streams:
                            logger.info(f"First appearance of tool_call_id: {tool_call_id} for function: {function_name}")
                            self._active_tool_call_streams[tool_call_id] = {
                                'name': function_name,
                                'current_arg_sequence': 0,
                                'initiated': False
                            }
                            # TODO: Extract schema from tool_call if provided by LiteLLM, else None.
                            # Example: tool_schema = getattr(tool_call, 'schema', None)
                            init_request = InitiateToolCallRequest(
                                tool_name=function_name,
                                tool_call_id=tool_call_id
                                # tool_schema=tool_schema # Pass if available
                            )
                            try:
                                await self._argument_accumulator_service.initiate_tool_call(init_request)
                                self._active_tool_call_streams[tool_call_id]['initiated'] = True
                                asyncio.create_task(self._handle_argument_completion(tool_call_id))
                                logger.debug(f"Tool call initiated and listener started for {tool_call_id}")
                            except Exception as e:
                                logger.error(f"Error initiating tool call {tool_call_id} for {function_name}: {e}", exc_info=True)
                                # Potentially push an error frame or mark as failed
                                await self.push_frame(ErrorFrame(f"Failed to initiate tool call {function_name} ({tool_call_id}): {e}"))


                        if tool_call_id and tool_call_id in self._active_tool_call_streams and function_arguments_chunk:
                            if not self._active_tool_call_streams[tool_call_id]['initiated']:
                                logger.warning(f"Received argument chunk for {tool_call_id} but not initiated. Skipping.")
                                continue
                            
                            current_sequence = self._active_tool_call_streams[tool_call_id]['current_arg_sequence']
                            chunk_request = SubmitArgumentChunkRequest(
                                tool_call_id=tool_call_id,
                                chunk_content=function_arguments_chunk,
                                sequence_number=current_sequence,
                                is_last_chunk=False # Will send a final True chunk later
                            )
                            try:
                                await self._argument_accumulator_service.submit_argument_chunk(chunk_request)
                                self._active_tool_call_streams[tool_call_id]['current_arg_sequence'] += 1
                                logger.debug(f"Submitted chunk {current_sequence} for {tool_call_id}")
                                # Optionally push FunctionCallInProgressFrame with raw chunk for UI
                                # await self.push_frame(FunctionCallInProgressFrame(
                                #    function_name=self._active_tool_call_streams[tool_call_id]['name'],
                                #    tool_call_id=tool_call_id,
                                #    arguments=function_arguments_chunk, # Send only the current chunk
                                #    is_final=False 
                                # ))
                            except Exception as e:
                                logger.error(f"Error submitting argument chunk for {tool_call_id}: {e}", exc_info=True)
                                # Mark as failed or push error frame
                                await self.push_frame(ErrorFrame(f"Failed to submit chunk for tool call {self._active_tool_call_streams[tool_call_id]['name']} ({tool_call_id}): {e}"))


            # After the stream, submit final chunks for all initiated tool calls
            for tool_call_id, data in self._active_tool_call_streams.items():
                if data['initiated']:
                    logger.info(f"Submitting final empty chunk for tool_call_id: {tool_call_id}")
                    final_sequence_number = data['current_arg_sequence']
                    final_chunk_request = SubmitArgumentChunkRequest(
                        tool_call_id=tool_call_id,
                        chunk_content="", # Empty content for the final signal
                        sequence_number=final_sequence_number,
                        is_last_chunk=True
                    )
                    try:
                        await self._argument_accumulator_service.submit_argument_chunk(final_chunk_request)
                    except Exception as e:
                        logger.error(f"Error submitting final chunk for {tool_call_id}: {e}", exc_info=True)
                        # This error might mean the tool call won't complete correctly.
                        # _handle_argument_completion might receive a FAILED/TIMEOUT from the accumulator.
                        await self.push_frame(ErrorFrame(f"Failed to submit final signal for tool call {data['name']} ({tool_call_id}): {e}"))

            await self.push_frame(LLMFullResponseEndFrame())

        except Timeout as e:
            logger.error(f"LiteLLM Timeout error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Request Timed Out: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except APIConnectionError as e:
            logger.error(f"LiteLLM API Connection error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM API Connection Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except NotFoundError as e:
            logger.error(f"LiteLLM Not Found error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Not Found Error (e.g., Invalid Model ID): Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except PermissionDeniedError as e:
            logger.error(f"LiteLLM Permission Denied error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Permission Denied Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except ServiceUnavailableError as e:
            logger.error(f"LiteLLM Service Unavailable error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Service Unavailable: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except ContextWindowExceededError as e: 
            logger.error(f"LiteLLM Context Window Exceeded error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Context Window Exceeded: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except BadRequestError as e: 
            logger.error(f"LiteLLM Bad Request error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Bad Request Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except AuthenticationError as e: 
            logger.error(f"LiteLLM Authentication error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Authentication Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except RateLimitError as e: 
            logger.error(f"LiteLLM Rate Limit error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Rate Limit Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except APIError as e: 
            logger.error(f"LiteLLM API error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM API Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except httpx.RequestError as e: 
            logger.error(f"HTTP request error during LiteLLM streaming call for model {self._model_id}: {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Network Request Error for LLM: Model {self._model_id}. Details: {e}"
            ))
        except Exception as e: 
            logger.error(f"Unexpected error during LiteLLM streaming call for model {self._model_id}: {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Unexpected Error during LLM streaming: Model {self._model_id}. Details: {e}"
            ))
        finally:
            # Ensure active tool call streams are cleared if an error occurs mid-stream
            # or if they are not processed fully by the end of the function.
            # However, _handle_argument_completion tasks might still be running.
            # A more robust cleanup of these tasks might be needed if an exception occurs.
            # For now, clearing the dict prevents re-processing on a subsequent call.
            self._active_tool_call_streams.clear()


    async def _handle_argument_completion(self, tool_call_id: str):
        """
        Listens for argument accumulation completion events for a given tool_call_id.
        """
        if not self._argument_accumulator_service:
            logger.error(f"_handle_argument_completion: _argument_accumulator_service not initialized for {tool_call_id}")
            return

        try:
            queue = await self._argument_accumulator_service.subscribe_to_notifications(tool_call_id)
            logger.info(f"Subscribed to argument completion for tool_call_id: {tool_call_id}")
            
            event = await queue.get() # Wait for the final event
            logger.info(f"Received argument completion event for {tool_call_id}: {event}")

            tool_data = self._active_tool_call_streams.get(tool_call_id, {})
            tool_name = tool_data.get('name', 'unknown_tool')

            if event and event.get("status") == ToolCallStatus.ARGUMENTS_COMPLETE:
                assembled_args = event.get("data", {})
                logger.info(f"Tool call {tool_call_id} ({tool_name}) arguments complete. Ready for dispatch.")
                await self.push_frame(FunctionCallInProgressFrame(
                    function_name=tool_name,
                    tool_call_id=tool_call_id,
                    arguments=json.dumps(assembled_args), # Arguments are now structured JSON
                    is_final=True 
                ))
                # TODO: Trigger actual tool dispatch here or signal readiness to another component.
            elif event:
                error_message = event.get("error", "Unknown error during argument accumulation")
                logger.error(f"Tool call {tool_call_id} ({tool_name}) argument accumulation failed or was cancelled/timed out: {error_message}")
                await self.push_frame(ErrorFrame(f"Tool call {tool_call_id} ({tool_name}) failed: {error_message}"))
            else:
                logger.error(f"Received empty event for tool_call_id: {tool_call_id}. This should not happen.")
                await self.push_frame(ErrorFrame(f"Tool call {tool_call_id} ({tool_name}) failed due to an unexpected empty event."))

        except asyncio.CancelledError:
            logger.info(f"Argument completion handler for {tool_call_id} was cancelled.")
        except Exception as e:
            logger.error(f"Error in _handle_argument_completion for {tool_call_id}: {e}", exc_info=True)
            tool_name_fallback = self._active_tool_call_streams.get(tool_call_id, {}).get('name', 'unknown_tool')
            await self.push_frame(ErrorFrame(f"Error processing tool call {tool_call_id} ({tool_name_fallback}): {e}"))
        finally:
            # Clean up from self._active_tool_call_streams if it's still there.
            # This dict is primarily for the duration of one _get_llm_response_streaming call.
            # If this handler outlives that, specific cleanup might be needed.
            # However, _active_tool_call_streams.clear() at the start of _get_llm_response_streaming
            # should handle most cases for subsequent LLM calls.
            if tool_call_id in self._active_tool_call_streams:
                 logger.debug(f"Tool call {tool_call_id} processing finished, removing from active streams if present.")
                 # No, don't delete here, it's cleared at the start of the main streaming method.
                 # If deleted here, subsequent chunks in the *same* LLM stream for other tools might have issues
                 # if this handler finishes early. The main _get_llm_response_streaming owns the lifecycle of this dict.


# Example Usage (Conceptual):
# Assuming you have your LiteLLM router initialized elsewhere
# from your_app.litellm_setup import litellm_router # Example
# from backend.app.utils.llm_registry_service import LLMRegistryService # Example
# from pipecat.pipeline.pipeline import Pipeline # Example
# from pipecat.transports.local.local_transport import LocalTransport # Example

# async def main_example():
#     # Setup LLM Registry (example)
#     registry = LLMRegistryService()
#     registry.register_model(
#         alias="gpt-4o-mini-test", 
#         model_id="gpt-4o-mini", 
#         # ... other params like api_key, base_url if needed by LiteLLM for this model
#     )

#     # Setup LiteLLM Router (example)
#     # This would typically be more sophisticated, loading from config or registry details
#     model_list = [{
#         "model_name": "gpt-4o-mini-test", # Alias used in registry
#         "litellm_params": {"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}
#     }]
#     litellm_router = litellm.Router(model_list=model_list)


#     # Initialize your transport (e.g., WebSocket, Daily, Local for testing)
#     # transport = LocalTransport() # Using LocalTransport for this example

#     # Create an instance of your custom LiteLLMPipecatService
#     lite_llm_service = LiteLLMPipecatService(
#         llm_registry_service=registry,
#         litellm_router=litellm_router,
#         preferred_model_alias="gpt-4o-mini-test" 
#     )
    
#     # Add a cleanup method to the service for graceful shutdown of the worker
#     # pipeline.on_stop(lite_llm_service.cleanup) # If pipeline supports hooks

#     # Build your Pipecat pipeline
#     # pipeline = Pipeline([
#     #     transport.input(),
#     #     # ... other processors 
#     #     lite_llm_service, 
#     #     # ... other processors
#     #     transport.output()
#     # ])

#     # Run the pipeline
#     # await pipeline.run_async()

# # if __name__ == "__main__":
# #    asyncio.run(main_example())