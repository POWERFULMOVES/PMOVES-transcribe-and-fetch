#
# Copyright (c) 2024-2025, PMOVES
#
# SPDX-License-Identifier: Apache-2.0
#

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable # Added Callable

import httpx

# Pipecat imports
from pipecat.frames.frames import (
    Frame,
    ErrorFrame,
    LLMMessagesFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMResponseStartFrame,
    # LLMToolCallChunkFrame, # Unused
    LLMToolCallFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    TextFrame  # Added TextFrame import
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService
# from pipecat.vad.vad_analyzer import VADAnalyzer # Unused

# Argument Accumulator Service (AAS) imports
from backend.app.services.tool_calling.argument_accumulator_service import (
    ArgumentAccumulatorService,
    SubmitArgumentChunkRequest,
    ToolCallStatus,
)
from backend.app.services.tool_calling.tool_schema_manager import ToolSchemaManager
from backend.app.utils.llm_registry_service import LLMRegistryService

# LiteLLM imports (handle potential errors)
try:
    import litellm
    from litellm.exceptions import (
        Timeout, APIConnectionError, NotFoundError,
        PermissionDeniedError, ServiceUnavailableError,
        ContextWindowExceededError, BadRequestError,
        AuthenticationError, RateLimitError, APIError
    )
except ImportError:
    litellm = None
    # Define dummy exceptions if litellm is not installed
    class LiteLLMBaseError(Exception):
        def __init__(self, message, llm_provider=None, model=None, request=None, response=None):
            super().__init__(message)
            self.llm_provider = llm_provider
            self.model = model
            self.request = request
            self.response = response

    Timeout = APIConnectionError = NotFoundError = PermissionDeniedError = ServiceUnavailableError = APIError = LiteLLMBaseError
    ContextWindowExceededError = BadRequestError = AuthenticationError = RateLimitError = LiteLLMBaseError
    print("[WARN] LiteLLM not found. Using dummy exceptions.")


logger = logging.getLogger(__name__)

class LiteLLMPipecatService(LLMService):
    """
    A Pipecat service that uses LiteLLM to interact with various LLM providers,
    integrating with an LLMRegistryService for model configuration and an
    ArgumentAccumulatorService for handling streamed tool calls.

    This service:
    - Fetches model details (API key, base URL) from LLMRegistryService.
    - Uses a LiteLLM Router instance for making `acompletion` calls.
    - Supports streaming responses, including text and tool call chunks.
    - Accumulates tool argument chunks via ArgumentAccumulatorService.
    - Listens for argument completion events to trigger (placeholder) tool execution.
    - Manages a ToolSchemaManager to provide tool schemas to the LLM.
    """

    def __init__(self, llm_registry_service: LLMRegistryService, 
                 preferred_model_alias: str, 
                 litellm_router: litellm.Router, 
                 **kwargs):
        super().__init__(**kwargs)
        self._llm_registry_service: LLMRegistryService = llm_registry_service
        self._preferred_model_alias: str = preferred_model_alias
        self._litellm_router: litellm.Router = litellm_router
        self._model_id: Optional[str] = None  # Actual model ID like 'openai/gpt-4o-mini'
        self._model_config: Optional[Dict[str, Any]] = None # Full config from registry
        self._messages: List[Dict[str, Any]] = []
        self._tool_schema_manager = ToolSchemaManager() # Initialize with default schemas
        
        try:
            self._argument_accumulator_service = ArgumentAccumulatorService()
            logger.info(
                "ArgumentAccumulatorService initialized successfully "
                "within LiteLLMPipecatService.")
        except Exception as e_aas:
            logger.error(
                f"Failed to initialize ArgumentAccumulatorService: {e_aas}", 
                exc_info=True)
            self._argument_accumulator_service = None

        self._active_tool_call_streams: Dict[str, Dict[str, Any]] = {}
        self._worker_stop_event = asyncio.Event()
        self._completion_handler_tasks: List[asyncio.Task] = []
        self._tool_handlers: Dict[str, Callable] = {} # Added

    async def cleanup(self):
        """Gracefully stop the argument completion worker and other resources."""
        logger.info("Cleaning up LiteLLMPipecatService...")
        self._worker_stop_event.set()
        if self._argument_accumulator_service:
            pass
        
        for task in self._completion_handler_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Completion handler task {task.get_name()} cancelled.")
                except Exception as e:
                    logger.error(
                        f"Error during cancellation of task {task.get_name()}: {e}")
        self._completion_handler_tasks.clear()
        logger.info("LiteLLMPipecatService cleanup complete.")

    def register_tool_handler(self, tool_name: str, handler: Callable):
        """
        Registers an asynchronous handler for a given tool name.

        Args:
            tool_name: The name of the tool (must match the name in the schema).
            handler: An async function that takes tool_call_id (str) and 
                     arguments (dict) as input and returns a JSON-serializable result.
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError(f"Tool handler for '{tool_name}' must be an async function.")
        self._tool_handlers[tool_name] = handler
        logger.info(f"Registered tool handler for: {tool_name}")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMMessagesFrame):
            self._messages = frame.messages
            await self._fetch_litellm_config() 
            if not self._model_id or not self._model_config:
                logger.error(
                    f"Failed to configure model for alias '{self._preferred_model_alias}'. "
                    "Cannot proceed.")
                await self.push_frame(
                    ErrorFrame(f"LLM model '{self._preferred_model_alias}' not configured."))
                return
            
            if not self._argument_accumulator_service:
                logger.error(
                    "ArgumentAccumulatorService is not available. "
                    "Tool calling will be disabled.")

            self._active_tool_call_streams.clear()
            for task in self._completion_handler_tasks:
                if not task.done():
                    task.cancel()
            self._completion_handler_tasks.clear()

            await self._get_llm_response_streaming()

    async def _fetch_litellm_config(self):
        """
        Fetches the model configuration from the LLMRegistryService.
        Updates self._model_id and self._model_config.
        """
        try:
            logger.info(f"Fetching LLM config for alias: {self._preferred_model_alias}")
            model_details = await self._llm_registry_service.get_model_details(
                self._preferred_model_alias)
            if model_details:
                self._model_id = model_details.model_id
                self._model_config = model_details.model_dump()
                logger.info(
                    f"Successfully fetched config for '{self._preferred_model_alias}'. "
                    f"Mapped to model_id: '{self._model_id}'")
            else:
                logger.error(
                    f"Model with alias '{self._preferred_model_alias}' not found "
                    "in LLMRegistryService.")
                self._model_id = None
                self._model_config = None
        except Exception as e:
            logger.error(
                f"Error fetching LiteLLM config for alias '{self._preferred_model_alias}': {e}",
                exc_info=True)
            self._model_id = None
            self._model_config = None

    async def _get_llm_response_streaming(self):
        if not self._model_id or not self._litellm_router:
            await self.push_frame(ErrorFrame(
                f"LiteLLMPipecatService not properly configured. "
                f"Model ID: {self._model_id}, Router Available: {self._litellm_router is not None}"
            ))
            return
        
        self._active_tool_call_streams.clear()

        try:
            logger.info(
                f"Getting LLM stream from LiteLLM Router for model: {self._model_id}")
            await self.push_frame(LLMResponseStartFrame())
            await self.push_frame(LLMFullResponseStartFrame())

            stream_response = await self._litellm_router.acompletion(
                model=self._model_id,
                messages=self._messages,
                stream=True,
                tools=self._tool_schema_manager.get_all_schemas_for_llm()
            )

            async for chunk in stream_response:
                delta = chunk.choices[0].delta

                if delta.content:
                    await self.push_frame(TextFrame(delta.content))
                
                if delta.tool_calls:
                    for tool_call_chunk in delta.tool_calls:
                        tool_call_id = tool_call_chunk.id
                        function_data = tool_call_chunk.function
                        function_name = function_data.name
                        function_arguments_chunk = function_data.arguments

                        if tool_call_id not in self._active_tool_call_streams:
                            self._active_tool_call_streams[tool_call_id] = {
                                'name': function_name,
                                'current_arg_sequence': 0,
                                'initiated': False
                            }
                            logger.info(
                                f"New tool call initiated: ID {tool_call_id}, "
                                f"Name: {function_name}")
                            await self.push_frame(LLMToolCallFrame(
                                tool_call_id=tool_call_id, 
                                function_name=function_name,
                                # arguments are streamed, so not available fully here
                            ))
                            
                            if self._argument_accumulator_service:
                                task = asyncio.create_task(
                                    self._handle_argument_completion(tool_call_id))
                                self._completion_handler_tasks.append(task)
                            else:
                                logger.warning(
                                    f"No ArgumentAccumulatorService, cannot handle "
                                    f"completion for {tool_call_id}")

                        if function_arguments_chunk and self._argument_accumulator_service:
                            try:
                                self._active_tool_call_streams[tool_call_id]['current_arg_sequence'] += 1
                                current_sequence = self._active_tool_call_streams[tool_call_id]['current_arg_sequence']
                                
                                chunk_request = SubmitArgumentChunkRequest(
                                    tool_call_id=tool_call_id,
                                    chunk_content=function_arguments_chunk,
                                    sequence_number=current_sequence,
                                    is_last_chunk=False
                                )
                                await self._argument_accumulator_service.submit_argument_chunk(chunk_request)
                                self._active_tool_call_streams[tool_call_id]['initiated'] = True
                            except Exception as e:
                                logger.error(
                                    f"Error submitting argument chunk for {tool_call_id}: {e}", 
                                    exc_info=True)
                                await self.push_frame(ErrorFrame(
                                    f"Failed to submit chunk for tool call "
                                    f"{self._active_tool_call_streams[tool_call_id]['name']} "
                                    f"({tool_call_id}): {e}"))

            for tool_call_id, data in self._active_tool_call_streams.items():
                if data['initiated']:
                    logger.info(f"Submitting final empty chunk for tool_call_id: {tool_call_id}")
                    final_sequence_number = data['current_arg_sequence']
                    final_chunk_request = SubmitArgumentChunkRequest(
                        tool_call_id=tool_call_id,
                        chunk_content="",
                        sequence_number=final_sequence_number,
                        is_last_chunk=True
                    )
                    try:
                        await self._argument_accumulator_service.submit_argument_chunk(final_chunk_request)
                    except Exception as e:
                        logger.error(
                            f"Error submitting final chunk for {tool_call_id}: {e}", 
                            exc_info=True)
                        await self.push_frame(ErrorFrame(
                            f"Failed to submit final signal for tool call "
                            f"{data['name']} ({tool_call_id}): {e}"))

            # All chunks processed, finalize.
            # This will push LLMToolCallResultFrame for each completed tool call.
            for tool_call_id, details in self._active_tool_call_streams.items():
                if details.get('arguments_complete') and not details.get('result_pushed'):
                    # This case should ideally be handled by the argument completion listener,
                    # but as a fallback, ensure results are pushed.
                    # This might indicate a race condition or an unhandled completion scenario.
                    logger.warning(f"Fallback: Pushing presumed complete tool call result for {tool_call_id}")
                    # We don't have the result here, so we push an empty one or signal error
                    # For now, let's assume the handler should have pushed.
                    # This part needs careful review of the tool call lifecycle.
                    pass # Avoid pushing incomplete/erroneous results here.

            await self.push_frame(LLMFullResponseEndFrame())
            logger.info("LLM stream finished.")

        except Timeout as e:
            logger.error(
                f"LiteLLM Timeout error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Request Timed Out: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except APIConnectionError as e:
            logger.error(
                f"LiteLLM API Connection error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM API Connection Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except NotFoundError as e:
            logger.error(
                f"LiteLLM Not Found error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Not Found Error (e.g., Invalid Model ID): Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except PermissionDeniedError as e:
            logger.error(
                f"LiteLLM Permission Denied error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Permission Denied Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except ServiceUnavailableError as e:
            logger.error(
                f"LiteLLM Service Unavailable error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Service Unavailable: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except ContextWindowExceededError as e: 
            logger.error(
                f"LiteLLM Context Window Exceeded error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Context Window Exceeded: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except BadRequestError as e: 
            logger.error(
                f"LiteLLM Bad Request error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Bad Request Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except AuthenticationError as e: 
            logger.error(
                f"LiteLLM Authentication error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Authentication Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except RateLimitError as e: 
            logger.error(
                f"LiteLLM Rate Limit error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Rate Limit Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except APIError as e:
            logger.error(
                f"LiteLLM API error for model {self._model_id} "
                f"(Provider: {getattr(e, 'llm_provider', 'N/A')}, "
                f"Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM API Error: Model {self._model_id}, "
                f"Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except httpx.RequestError as e:
            logger.error(
                f"HTTP request error during LiteLLM streaming call for model {self._model_id}: {e}", 
                exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Network Request Error for LLM: Model {self._model_id}. Details: {e}"
            ))
        except Exception as e:
            logger.error(
                f"Unexpected error during LiteLLM streaming call for model {self._model_id}: {e}", 
                exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Unexpected Error during LLM streaming: Model {self._model_id}. Details: {e}"
            ))
        finally:
            self._active_tool_call_streams.clear()


    async def _handle_argument_completion(self, tool_call_id: str):
        logger.info(f"Waiting for argument completion for tool_call_id: {tool_call_id}")
        if not self._argument_accumulator_service:
            logger.error("ArgumentAccumulatorService is not available. Cannot handle tool call completion.")
            return

        try:
            # This call will block until the AAS signals completion or timeout
            final_status_data = await self._argument_accumulator_service.wait_for_completion(tool_call_id)
            
            if not final_status_data or final_status_data.status != ToolCallStatus.ARGUMENTS_COMPLETE:
                logger.error(
                    f"Argument accumulation did not complete successfully for {tool_call_id}. "
                    f"Status: {final_status_data.status if final_status_data else 'N/A'}")
                # Optionally push an error frame or handle this more gracefully
                await self.push_frame(ErrorFrame(
                    f"Tool call {tool_call_id} argument accumulation failed: "
                    f"{final_status_data.status if final_status_data else 'Unknown AAS error'}"))
                return

            tool_name = final_status_data.name
            assembled_arguments_str = final_status_data.arguments_json_str
            
            logger.info(
                f"Arguments complete for tool_call_id: {tool_call_id}, "
                f"Tool: {tool_name}, Args: {assembled_arguments_str}"
            )

            await self.push_frame(FunctionCallInProgressFrame(tool_call_id=tool_call_id, function_name=tool_name))

            tool_result: Any # Declare tool_result type
            assembled_args_dict: Dict[str, Any] = {}

            try:
                if assembled_arguments_str:
                    assembled_args_dict = json.loads(assembled_arguments_str)
            except json.JSONDecodeError as e_json:
                logger.error(
                    f"Failed to decode JSON arguments for {tool_call_id} ('{tool_name}'): {e_json}. "
                    f"Raw args: {assembled_arguments_str}")
                tool_result = {
                    "error": f"Invalid JSON arguments provided: {str(e_json)}",
                    "tool_name": tool_name,
                    "tool_call_id": tool_call_id
                }
            else:
                if tool_name in self._tool_handlers:
                    actual_tool_handler = self._tool_handlers[tool_name]
                    logger.info(f"Executing registered handler for tool: {tool_name} (ID: {tool_call_id})")
                    try:
                        # Pass tool_call_id and the parsed arguments dictionary
                        tool_result = await actual_tool_handler(tool_call_id, assembled_args_dict)
                        logger.info(f"Tool {tool_name} (ID: {tool_call_id}) executed successfully.")
                    except Exception as e_handler:
                        logger.error(f"Error executing tool handler for {tool_name} (ID: {tool_call_id}): {e_handler}", exc_info=True)
                        tool_result = {
                            "error": f"Handler execution failed: {str(e_handler)}",
                            "tool_name": tool_name,
                            "tool_call_id": tool_call_id
                        }
                else:
                    logger.error(f"No handler registered for tool: {tool_name} (ID: {tool_call_id}). Tool not implemented.")
                    # Instead of placeholder, return an error object
                    tool_result = {
                        "error": f"Tool '{tool_name}' is not registered or implemented.",
                        "tool_name": tool_name,
                        "tool_call_id": tool_call_id,
                        "status": "error_tool_not_found"
                    }

            # Push a frame indicating the function call result
            # The result here should be the direct output from the tool, JSON-serializable
            stringified_tool_result = ""
            try:
                stringified_tool_result = json.dumps(tool_result)
            except TypeError as e_type:
                logger.error(f"Failed to stringify tool result for {tool_name} (ID: {tool_call_id}): {e_type}. Result: {tool_result}")
                stringified_tool_result = json.dumps({
                    "error": f"Result serialization failed: {str(e_type)}", 
                    "tool_name": tool_name, 
                    "tool_call_id": tool_call_id
                })

            await self.push_frame(
                FunctionCallResultFrame(
                    tool_call_id=tool_call_id,
                    function_name=tool_name,
                    result=stringified_tool_result 
                )
            )

            # Prepare message to send back to LLM
            tool_result_message = {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": tool_name,
                "content": stringified_tool_result, # Send stringified result back to LLM
            }

            # Update message history and re-prompt LLM
            self._messages.append(tool_result_message)
            logger.info(f"Appended tool result for {tool_name} (ID: {tool_call_id}) to messages. Re-prompting LLM.")
            # Push messages to trigger next LLM call
            await self.push_frame(LLMMessagesFrame(messages=self._messages)) 
            # We expect the pipeline to route this frame back for another _get_llm_response_streaming call

        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for argument completion for tool_call_id: {tool_call_id}")
            await self.push_frame(ErrorFrame(f"Timeout waiting for tool arguments: {tool_call_id}"))
        except Exception as e:
            logger.error(
                f"An unexpected error occurred in _handle_argument_completion for {tool_call_id}: {e}", 
                exc_info=True
            )
            await self.push_frame(ErrorFrame(f"Unexpected error handling tool {tool_call_id}: {str(e)}"))
        finally:
            # Clean up the AAS state for this tool_call_id
            if self._argument_accumulator_service:
                await self._argument_accumulator_service.clear_tool_call_state(tool_call_id)
            # Remove from active streams tracking within this service
            if tool_call_id in self._active_tool_call_streams:
                del self._active_tool_call_streams[tool_call_id]
            logger.debug(f"Finished handling and cleanup for tool_call_id: {tool_call_id}")


    # Example of how a tool schema might be defined and added (elsewhere, e.g. main.py)
    # async def get_weather_handler(tool_call_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    #     location = args.get("location", "unknown")
    #     unit = args.get("unit", "celsius")
    #     # Actual weather fetching logic here
    #     return {"location": location, "temperature": "25", "unit": unit, "condition": "Sunny"}

    # In your pipeline setup:
    # litellm_service = LiteLLMPipecatService(...)
    # litellm_service.tool_schema_manager.add_tool_schema({ ... schema for get_weather ... })
    # litellm_service.register_tool_handler("get_weather", get_weather_handler)
    
# Example usage of LiteLLMPipecatService (conceptual, actual setup in main.py or bot.py)
# async def main():
#     # Assuming llm_registry_service and litellm_router are initialized
#     # from backend.app.utils.llm_registry_service import LLMRegistryService
#     # from litellm import Router
#     # llm_registry = LLMRegistryService()
#     # await llm_registry.refresh_models() # Populate models
    
#     # router_instance = Router(model_list=llm_registry.get_model_list_for_router())

#     # service = LiteLLMPipecatService(
#     #     llm_registry_service=llm_registry,
#     #     preferred_model_alias="openai/gpt-4o-mini", # Example alias
#     #     litellm_router=router_instance 
#     # )

#     # # Define a tool schema (OpenAI format)
#     # weather_tool_schema = {
#     #     "type": "function",
#     #     "function": {
#     #         "name": "get_current_weather",
#     #         "description": "Get the current weather in a given location",
#     #         "parameters": {
#     #             "type": "object",
#     #             "properties": {
#     #                 "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
#     #                 "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
#     #             },
#     #             "required": ["location"]
#     #         }
#     #     }
#     # }
#     # service.tool_schema_manager.add_tool_schema(weather_tool_schema)

#     # # Define a handler
#     # async def my_weather_handler(tool_call_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
#     #     logger.info(f"Handler my_weather_handler called with ID: {tool_call_id}, Args: {args}")
#     #     # Simulate API call
#     #     await asyncio.sleep(1)
#     #     return {"temperature": "30", "unit": args.get("unit", "celsius"), "condition": "Sunny"}
    
#     # service.register_tool_handler("get_current_weather", my_weather_handler)

#     # # Simulate receiving an LLMMessagesFrame
#     # messages_frame = LLMMessagesFrame(messages=[
#     #     {"role": "user", "content": "What's the weather in Boston?"}
#     # ])
#     # await service.process_frame(messages_frame, FrameDirection.DOWNSTREAM)

#     # # ... more pipeline logic to push frames and see results ...
#     # await service.cleanup()

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     # asyncio.run(main())