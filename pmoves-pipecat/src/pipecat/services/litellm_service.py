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
    AuthenticationError, # Already used, ensure it's part of this block or imported
    RateLimitError,     # Already used
    APIError            # Already used
)
import logging
import httpx

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

logger = logging.getLogger(__name__)

class LiteLLMPipecatService(LLMService):
    """
    A Pipecat LLM Service that uses LiteLLM for interacting with various LLMs.
    Handles streaming responses from LiteLLM and pushes them as Pipecat frames.
    Integrates with the LLMRegistryService for dynamic model selection.
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
        self._litellm_router = litellm_router # Use the provided router instance
        self._model_id = None # Will be fetched from registry based on alias
        self._messages = [] # To maintain conversation history
        self._accumulated_tool_args = {} # To accumulate tool call arguments from streaming chunks

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
                await self.push_frame(ErrorFrame(f"Failed to load model {self._preferred_model_alias}"), FrameDirection.DOWNSTREAM)

        # Pass the frame along the pipeline
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
            # Should not happen if _fetch_litellm_config was successful, but for safety
            logger.error("Attempted to get LLM response without messages, router, or model ID.")
            return

        logger.debug(f"Making LiteLLM streaming call with model ID: {self._model_id}")

        try:
            # Signal the start of the LLM response
            await self.push_frame(LLMFullResponseStartFrame())

            # Make the streaming call to LiteLLM using the fetched router and model ID
            stream_response = await self._litellm_router.acompletion(
                model=self._model_id,
                messages=self._messages,
                stream=True
            )

            # Process the streaming response chunks
            async for chunk in stream_response:
                # Extract text content from the chunk (LiteLLM chunks are often OpenAI compatible)
                content = chunk.choices[0].delta.content or ""
                if content:
                    # Push text chunks as Pipecat frames
                    await self.push_frame(LLMTextFrame(content))

                # Handle tool calls
                tool_calls = getattr(chunk.choices[0].delta, 'tool_calls', None)
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_call_id = getattr(tool_call, 'id', None)
                        function_name = getattr(tool_call.function, 'name', None)
                        function_arguments_chunk = getattr(tool_call.function, 'arguments', None)
                        tool_call_index = getattr(tool_call, 'index', 0) # Default to 0 if index not present

                        if tool_call_id:
                            if tool_call_id not in self._accumulated_tool_args:
                                self._accumulated_tool_args[tool_call_id] = {}

                            if tool_call_index not in self._accumulated_tool_args[tool_call_id]:
                                self._accumulated_tool_args[tool_call_id][tool_call_index] = {
                                    'name': function_name, # Store the name when first seen
                                    'arguments': ''
                                }

                            if function_arguments_chunk:
                                # Accumulate argument chunks
                                self._accumulated_tool_args[tool_call_id][tool_call_index]['arguments'] += function_arguments_chunk

                            # Push a FunctionCallInProgressFrame with the current accumulated arguments
                            # We push this on each chunk to show progress, but the arguments are accumulated.
                            # A final frame will be pushed when the call ends or stream finishes.
                            current_name = self._accumulated_tool_args[tool_call_id][tool_call_index].get('name', function_name)
                            current_args = self._accumulated_tool_args[tool_call_id][tool_call_index].get('arguments', '')

                            await self.push_frame(FunctionCallInProgressFrame(
                                function_name=current_name,
                                tool_call_id=tool_call_id,
                                arguments=current_args,
                                is_final=False # Explicitly mark as not final during streaming
                            ))
                # TODO: Handle tool calls completion (e.g., when a tool_call_id is no longer in delta)

            # After the stream finishes, push final FunctionCallInProgressFrames for any accumulated calls
            for tool_call_id, calls_by_index in self._accumulated_tool_args.items():
                 for tool_call_index, call_data in calls_by_index.items():
                     # Push a final frame with the complete accumulated arguments
                     # This frame indicates the tool call is complete and all arguments are sent.
                     logger.debug(f"Pushing final FunctionCallInProgressFrame for tool_call_id: {tool_call_id}, index: {tool_call_index}")
                     await self.push_frame(FunctionCallInProgressFrame(
                         function_name=call_data.get('name'),
                         tool_call_id=tool_call_id,
                         arguments=call_data.get('arguments'),
                         is_final=True # Mark as final
                     ))
            self._accumulated_tool_args = {} # Clear accumulated arguments after processing

            # Signal the end of the LLM response
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
        except ContextWindowExceededError as e: # Specific BadRequestError
            logger.error(f"LiteLLM Context Window Exceeded error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Context Window Exceeded: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except BadRequestError as e: # More general BadRequestError
            logger.error(f"LiteLLM Bad Request error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Bad Request Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except AuthenticationError as e: # Existing, now with more details
            logger.error(f"LiteLLM Authentication error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Authentication Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except RateLimitError as e: # Existing, now with more details
            logger.error(f"LiteLLM Rate Limit error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM Rate Limit Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except APIError as e: # Existing, more general LiteLLM error, with details
            logger.error(f"LiteLLM API error for model {self._model_id} (Provider: {getattr(e, 'llm_provider', 'N/A')}, Status: {getattr(e, 'status_code', 'N/A')}): {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"LLM API Error: Model {self._model_id}, Provider: {getattr(e, 'llm_provider', 'N/A')}. Details: {e}"
            ))
        except httpx.RequestError as e: # Network errors
            # httpx errors might not have llm_provider or status_code in the same way
            logger.error(f"HTTP request error during LiteLLM streaming call for model {self._model_id}: {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Network Request Error for LLM: Model {self._model_id}. Details: {e}"
            ))
        except Exception as e: # Most generic handler
            logger.error(f"Unexpected error during LiteLLM streaming call for model {self._model_id}: {e}", exc_info=True)
            await self.push_frame(ErrorFrame(
                f"Unexpected Error during LLM streaming: Model {self._model_id}. Details: {e}"
            ))

# Example Usage (Conceptual):
# Assuming you have your LiteLLM router initialized elsewhere
# from your_app.litellm_setup import litellm_router
# from pipecat.pipeline.pipeline import Pipeline
# from pipecat.transports.your_transport import YourTransport # Replace with your transport

# # Initialize the LiteLLM router (example configuration)
# model_list = [
#     {"model_name": "my-openai-model", "litellm_params": {"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}},
#     {"model_name": "my-gemini-model", "litellm_params": {"model": "gemini-pro", "api_key": os.getenv("GEMINI_API_KEY")}},
# ]
# litellm_router = litellm.Router(model_list=model_list)

# # Initialize your transport (e.g., WebSocket, Daily)
# transport = YourTransport(...)

# # Create an instance of your custom LiteLLMPipecatService
# lite_llm_service = LiteLLMPipecatService(
#     litellm_router=litellm_router,
#     model_alias="my-openai-model" # Specify which model alias to use
# )

# # Build your Pipecat pipeline
# pipeline = Pipeline([
#     transport.input(),
#     # ... other processors (e.g., ASR for audio input)
#     lite_llm_service, # Add your custom LLM service here
#     # ... other processors (e.g., TTS for audio output)
#     transport.output()
# ])

# # Now you can run the pipeline
# # asyncio.run(pipeline.run()) 