import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

# Make sure LLMRegistryService is importable if it's a concrete class used for spec
# If it's an abstract class or not directly used, spec=True might be enough.
# from backend.app.utils.llm_registry_service import LLMRegistryService

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMMessagesFrame,
    LLMTextFrame,
    ErrorFrame,
    FunctionCallInProgressFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pmoves_pipecat.src.pipecat.services.litellm_service import LiteLLMPipecatService
import litellm
from litellm.exceptions import (
    BadRequestError,
    ContextWindowExceededError,
    NotFoundError,
    PermissionDeniedError,
    ServiceUnavailableError,
    Timeout,
    APIConnectionError,
    AuthenticationError, # Ensure these are also imported if used by name
    RateLimitError,
    APIError
)
import httpx


# Helper to collect frames pushed by the service
class FrameCollector(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.frames = []

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        self.frames.append((frame, direction))

# Mock LiteLLM completion chunk structure
class MockLiteLLMChunk:
    def __init__(self, content):
        self.choices = [MagicMock()]
        self.choices[0].delta.content = content


@pytest.mark.asyncio
async def test_litellm_service_streaming_response():
    """
    Tests that LiteLLMPipecatService correctly handles streaming responses
    from LiteLLM and outputs the appropriate Pipecat frames.
    """
    # Simulate a streaming response from LiteLLM
    async def mock_acompletion(model, messages, stream=True):
        yield MockLiteLLMChunk("Hello ")
        yield MockLiteLLMChunk("world")
        yield MockLiteLLMChunk("!")

    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_streaming"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    # Mock LiteLLM router
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = mock_acompletion

    # Create service and collector
    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_streaming",
        litellm_router=mock_router
    )
    collector = FrameCollector()

    # Connect service output to collector input
    service.link(collector)

    # Simulate receiving an LLMMessagesFrame
    messages = [{"role": "user", "content": "Tell me a story."}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    # Allow tasks to run (needed for async generators/processing)
    await asyncio.sleep(0.01)

    # Check the collected frames
    # Expected frames: initial LLMMessagesFrame (passed through), Start, Text1, Text2, Text3, End

    # The initial LLMMessagesFrame is passed through immediately
    assert len(collector.frames) >= 1 and isinstance(collector.frames[0][0], LLMMessagesFrame)

    # Then the streaming response frames should follow
    # Find the index after the initial LLMMessagesFrame
    start_index = 0
    for i, (frame, direction) in enumerate(collector.frames):
        if isinstance(frame, LLMMessagesFrame) and direction == FrameDirection.DOWNSTREAM:
            start_index = i + 1
            break

    # Check the frames from the streaming response
    streaming_frames = [frame for frame, direction in collector.frames[start_index:]]

    assert len(streaming_frames) >= 5 # Expecting Start, 3 Text, End
    assert isinstance(streaming_frames[0], LLMFullResponseStartFrame)
    assert isinstance(streaming_frames[1], LLMTextFrame) and streaming_frames[1].text == "Hello "
    assert isinstance(streaming_frames[2], LLMTextFrame) and streaming_frames[2].text == "world"
    assert isinstance(streaming_frames[3], LLMTextFrame) and streaming_frames[3].text == "!"
    assert isinstance(streaming_frames[4], LLMFullResponseEndFrame)

    # Verify that the LiteLLM acompletion method was called with correct arguments
    mock_router.acompletion.assert_called_once_with(
        model="test_model_streaming", # Updated to use resolved model_id
        messages=messages,
        stream=True
    )
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_streaming")

@pytest.mark.asyncio
async def test_litellm_service_passthrough_frame():
    """
    Tests that LiteLLMPipecatService correctly passes through non-LLMMessagesFrame frames.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    # No need to set up get_model_details as it shouldn't be called for passthrough

    # Create a mock LiteLLM router (should not be called)
    mock_router = MagicMock()
    mock_router.acompletion = AsyncMock() # Should not be called

    # Create service and collector
    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_passthrough",
        litellm_router=mock_router
    )
    collector = FrameCollector()

    # Connect service output to collector input
    service.link(collector)

    # Simulate receiving a non-LLMMessagesFrame (e.g., a simple text frame)
    passthrough_frame = LLMTextFrame(text="This frame should pass through.")
    await service.process_frame(passthrough_frame, FrameDirection.DOWNSTREAM)

    # Allow tasks to run
    await asyncio.sleep(0.01)

    # Check the collected frames
    # The service should have simply pushed the incoming frame downstream
    assert len(collector.frames) == 1
    collected_frame, direction = collector.frames[0]

    assert isinstance(collected_frame, LLMTextFrame)
    assert collected_frame.text == "This frame should pass through."
    assert direction == FrameDirection.DOWNSTREAM

    # Verify that the LiteLLM acompletion method was NOT called
    mock_router.acompletion.assert_not_called()

@pytest.mark.asyncio
async def test_litellm_service_authentication_error():
    """
    Tests that LiteLLMPipecatService handles LiteLLM AuthenticationError.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_auth_error"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = AuthenticationError("Invalid API Key")
    mock_exception.status_code = 401
    mock_exception.llm_provider = "mock_provider_auth"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_auth",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2 # Can be > 2 if LLMMessagesFrame is also counted by collector before error
    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]
    
    assert "LLM Authentication Error" in error_frame.error
    assert "Model test_model_auth_error" in error_frame.error
    assert "Provider: mock_provider_auth" in error_frame.error
    assert "Status: 401" in error_frame.error
    assert "Details: Invalid API Key" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_auth")

@pytest.mark.asyncio
async def test_litellm_service_rate_limit_error():
    """
    Tests that LiteLLMPipecatService handles LiteLLM RateLimitError.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_rate_limit"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = RateLimitError("Rate limit exceeded")
    mock_exception.status_code = 429
    mock_exception.llm_provider = "mock_provider_rate_limit"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_rate_limit",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Rate Limit Error" in error_frame.error
    assert "Model test_model_rate_limit" in error_frame.error
    assert "Provider: mock_provider_rate_limit" in error_frame.error
    assert "Status: 429" in error_frame.error
    assert "Details: Rate limit exceeded" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_rate_limit")

@pytest.mark.asyncio
async def test_litellm_service_api_error():
    """
    Tests that LiteLLMPipecatService handles LiteLLM APIError.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_api_error"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = APIError("Some API error", status_code=500, llm_provider="mock_provider_api")
    # Or set them directly:
    # mock_exception.status_code = 500
    # mock_exception.llm_provider = "mock_provider_api"
    mock_router.acompletion.side_effect = mock_exception
    
    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_api_error",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM API Error" in error_frame.error
    assert "Model test_model_api_error" in error_frame.error
    assert "Provider: mock_provider_api" in error_frame.error
    assert "Status: 500" in error_frame.error # Or whatever was set
    assert "Details: Some API error" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_api_error")

@pytest.mark.asyncio
async def test_litellm_service_request_error():
    """
    Tests that LiteLLMPipecatService handles httpx RequestError.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_request_error"
    mock_llm_registry.get_model_details.return_value = mock_model_info
    
    mock_router = MagicMock()
    # httpx.RequestError does not have llm_provider or status_code typically
    mock_exception = httpx.RequestError("Network unreachable", request=httpx.Request("GET", "http://test.com"))
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_request_error",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "Network Request Error for LLM" in error_frame.error
    assert "Model test_model_request_error" in error_frame.error
    assert "Details: Network unreachable" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_request_error")

@pytest.mark.asyncio
async def test_litellm_service_unexpected_exception():
    """
    Tests that LiteLLMPipecatService handles unexpected exceptions.
    """
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_unexpected_error"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = Exception("Some unexpected issue")
    # Generic exceptions won't have llm_provider or status_code
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_unexpected_error",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "Unexpected Error during LLM streaming" in error_frame.error
    assert "Model test_model_unexpected_error" in error_frame.error
    assert "Details: Some unexpected issue" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_unexpected_error")

@pytest.mark.asyncio
async def test_litellm_service_streaming_tool_call():
    """
    Tests that LiteLLMPipecatService correctly handles streaming tool call chunks
    and accumulates arguments before pushing the frame.
    """

    # Mock LiteLLM completion chunks with a tool call that streams arguments
    async def mock_acompletion_tool_call(model, messages, stream=True):
        # Simulate streaming response: start of text, then tool call chunks, then end of text/response
        yield MockLiteLLMChunk("Okay, I can do that. ") # Text chunk

        # Simulate tool call start chunk
        mock_chunk_start = MagicMock()
        mock_chunk_start.choices = [MagicMock()]
        mock_chunk_start.choices[0].delta.content = None # No text content
        mock_chunk_start.choices[0].delta.tool_calls = [
            MagicMock(id="call_abc123", function=MagicMock(name="get_weather", arguments="{\n"), index=0)
        ]
        yield mock_chunk_start

        # Simulate tool call argument chunk 1
        mock_chunk_args1 = MagicMock()
        mock_chunk_args1.choices = [MagicMock()]
        mock_chunk_args1.choices[0].delta.content = None
        mock_chunk_args1.choices[0].delta.tool_calls = [
            MagicMock(id="call_abc123", function=MagicMock(name=None, arguments="  \"location\": \"New"), index=0) # Name is None in subsequent chunks
        ]
        yield mock_chunk_args1

        # Simulate tool call argument chunk 2
        mock_chunk_args2 = MagicMock()
        mock_chunk_args2.choices = [MagicMock()]
        mock_chunk_args2.choices[0].delta.content = None
        mock_chunk_args2.choices[0].delta.tool_calls = [
            MagicMock(id="call_abc123", function=MagicMock(name=None, arguments=" York\"\n"), index=0)
        ]
        yield mock_chunk_args2

         # Simulate tool call argument chunk 3 (end of arguments)
        mock_chunk_args3 = MagicMock()
        mock_chunk_args3.choices = [MagicMock()]
        mock_chunk_args3.choices[0].delta.content = None
        mock_chunk_args3.choices[0].delta.tool_calls = [
            MagicMock(id="call_abc123", function=MagicMock(name=None, arguments="}"), index=0)
        ]
        yield mock_chunk_args3

        # Simulate end of response chunk
        mock_chunk_end = MagicMock()
        mock_chunk_end.choices = [MagicMock()]
        mock_chunk_end.choices[0].delta.content = None
        mock_chunk_end.choices[0].delta.tool_calls = None # No more tool calls in delta
        # The `tool_calls` list being None or empty in the delta indicates the end of streaming for that tool call ID
        yield mock_chunk_end

    # Mock LiteLLM router
    mock_litellm_router = MagicMock() # Renamed from mock_router to avoid conflict if any
    mock_litellm_router.acompletion.side_effect = mock_acompletion_tool_call

    # Create service and collector
    mock_llm_registry = MagicMock() # spec=LLMRegistryService if available
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_streaming_tool_call"
    mock_llm_registry.get_model_details.return_value = mock_model_info
    
    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_streaming_tool_call",
        litellm_router=mock_litellm_router
    )
    collector = FrameCollector()

    # Connect service output to collector input
    service.link(collector)

    # Simulate receiving an LLMMessagesFrame
    messages = [{"role": "user", "content": "What's the weather in New York?"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    # Allow tasks to run
    await asyncio.sleep(0.1) # Give enough time for all chunks to process

    # Check the collected frames
    # Expected frames (simplified order): Initial Message, Start, Text, 
    # InProgress (is_final=False, chunk1), InProgress (is_final=False, chunk2), 
    # InProgress (is_final=False, chunk3), InProgress (is_final=False, chunk4),
    # InProgress (is_final=True, final accumulated), End

    # Find the frames of interest
    initial_message_frame = next((f for f, d in collector.frames if isinstance(f, LLMMessagesFrame)), None)
    start_frame = next((f for f, d in collector.frames if isinstance(f, LLMFullResponseStartFrame)), None)
    text_frame = next((f for f, d in collector.frames if isinstance(f, LLMTextFrame)), None)
    # Get all FunctionCallInProgressFrame instances
    all_tool_call_frames = [f for f, d in collector.frames if isinstance(f, FunctionCallInProgressFrame)]
    end_frame = next((f for f, d in collector.frames if isinstance(f, LLMFullResponseEndFrame)), None)

    assert initial_message_frame is not None
    assert start_frame is not None
    assert text_frame is not None, "LLMTextFrame with initial text should be present"
    assert text_frame.text == "Okay, I can do that. "
    assert end_frame is not None, "LLMFullResponseEndFrame should be present"

    # Verify tool call frames for "call_abc123"
    tool_call_frames_abc123 = [f for f in all_tool_call_frames if f.tool_call_id == "call_abc123"]
    
    # We expect 4 streaming frames (one for each chunk that contains tool_call info)
    # and 1 final summary frame pushed after the loop. Total 5.
    assert len(tool_call_frames_abc123) == 5, f"Expected 5 FunctionCallInProgressFrames for call_abc123, got {len(tool_call_frames_abc123)}"

    # First 4 frames (streaming delta) should have is_final=False
    for i in range(4):
        assert tool_call_frames_abc123[i].function_name == "get_weather", f"Frame {i} name mismatch"
        assert not tool_call_frames_abc123[i].is_final, f"Intermediate frame {i} should have is_final=False"
        # Check argument accumulation progressively
        if i == 0:
            assert tool_call_frames_abc123[i].arguments == "{\n"
        elif i == 1:
            assert tool_call_frames_abc123[i].arguments == "{\n  \"location\": \"New"
        elif i == 2:
            assert tool_call_frames_abc123[i].arguments == "{\n  \"location\": \"New York\"\n"
        elif i == 3:
            assert tool_call_frames_abc123[i].arguments == "{\n  \"location\": \"New York\"\n}"


    # The last frame for this tool call ID (pushed after stream) should have is_final=True and full arguments
    final_accumulated_frame = tool_call_frames_abc123[-1]
    assert final_accumulated_frame.function_name == "get_weather"
    expected_args = '{\n  "location": "New York"\n}' # As defined in mock chunks
    assert final_accumulated_frame.arguments.strip() == expected_args.strip()
    assert final_accumulated_frame.is_final, "Final accumulated frame should have is_final=True"
    
    # Verify that the LiteLLM acompletion method was called with the resolved model_id
    mock_litellm_router.acompletion.assert_called_once_with(
        model="test_model_streaming_tool_call", # Check against resolved model_id
        messages=messages,
        stream=True
    )
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_streaming_tool_call")


# New tests for specific LiteLLM exceptions

@pytest.mark.asyncio
async def test_litellm_service_timeout_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_timeout"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = Timeout("Test timeout message")
    mock_exception.status_code = 408
    mock_exception.llm_provider = "mock_provider_timeout"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_timeout",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Request Timed Out" in error_frame.error
    assert "Model test_model_timeout" in error_frame.error
    assert "Provider: mock_provider_timeout" in error_frame.error
    assert "Status: 408" in error_frame.error
    assert "Details: Test timeout message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_timeout")

@pytest.mark.asyncio
async def test_litellm_service_api_connection_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_api_connection"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = APIConnectionError("Test API connection message")
    mock_exception.status_code = 503 # Example
    mock_exception.llm_provider = "mock_provider_api_connection"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_api_connection",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM API Connection Error" in error_frame.error
    assert "Model test_model_api_connection" in error_frame.error
    assert "Provider: mock_provider_api_connection" in error_frame.error
    assert "Status: 503" in error_frame.error
    assert "Details: Test API connection message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_api_connection")

@pytest.mark.asyncio
async def test_litellm_service_not_found_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_not_found"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = NotFoundError("Test not found message")
    mock_exception.status_code = 404
    mock_exception.llm_provider = "mock_provider_not_found"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_not_found",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Not Found Error" in error_frame.error
    assert "Model test_model_not_found" in error_frame.error
    assert "Provider: mock_provider_not_found" in error_frame.error
    assert "Status: 404" in error_frame.error
    assert "Details: Test not found message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_not_found")

@pytest.mark.asyncio
async def test_litellm_service_permission_denied_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_permission_denied"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = PermissionDeniedError("Test permission denied message")
    mock_exception.status_code = 403
    mock_exception.llm_provider = "mock_provider_permission_denied"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_permission_denied",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Permission Denied Error" in error_frame.error
    assert "Model test_model_permission_denied" in error_frame.error
    assert "Provider: mock_provider_permission_denied" in error_frame.error
    assert "Status: 403" in error_frame.error
    assert "Details: Test permission denied message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_permission_denied")

@pytest.mark.asyncio
async def test_litellm_service_service_unavailable_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_service_unavailable"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = ServiceUnavailableError("Test service unavailable message")
    mock_exception.status_code = 503
    mock_exception.llm_provider = "mock_provider_service_unavailable"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_service_unavailable",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Service Unavailable" in error_frame.error
    assert "Model test_model_service_unavailable" in error_frame.error
    assert "Provider: mock_provider_service_unavailable" in error_frame.error
    assert "Status: 503" in error_frame.error
    assert "Details: Test service unavailable message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_service_unavailable")

@pytest.mark.asyncio
async def test_litellm_service_context_window_exceeded_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_context_window"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = ContextWindowExceededError("Test context window exceeded message", model="test_model_context_window", llm_provider="mock_provider_context_window", status_code=400)
    # Attributes can also be set directly if constructor doesn't take them all
    # mock_exception.status_code = 400
    # mock_exception.llm_provider = "mock_provider_context_window"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_context_window",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Context Window Exceeded" in error_frame.error
    assert "Model test_model_context_window" in error_frame.error
    assert "Provider: mock_provider_context_window" in error_frame.error
    assert "Status: 400" in error_frame.error
    assert "Details: Test context window exceeded message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_context_window")

@pytest.mark.asyncio
async def test_litellm_service_bad_request_error():
    mock_llm_registry = MagicMock()
    mock_model_info = MagicMock()
    mock_model_info.model_id = "test_model_bad_request"
    mock_llm_registry.get_model_details.return_value = mock_model_info

    mock_router = MagicMock()
    mock_exception = BadRequestError("Test bad request message")
    mock_exception.status_code = 400
    mock_exception.llm_provider = "mock_provider_bad_request"
    mock_router.acompletion.side_effect = mock_exception

    service = LiteLLMPipecatService(
        llm_registry_service=mock_llm_registry,
        preferred_model_alias="test_alias_bad_request",
        litellm_router=mock_router
    )
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)
    await asyncio.sleep(0.01)

    error_frame_tuple = next(f for f in collector.frames if isinstance(f[0], ErrorFrame))
    assert error_frame_tuple is not None
    error_frame = error_frame_tuple[0]

    assert "LLM Bad Request Error" in error_frame.error
    assert "Model test_model_bad_request" in error_frame.error
    assert "Provider: mock_provider_bad_request" in error_frame.error
    assert "Status: 400" in error_frame.error
    assert "Details: Test bad request message" in error_frame.error
    mock_llm_registry.get_model_details.assert_called_once_with("test_alias_bad_request")