import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

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

    # Mock LiteLLM router
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = mock_acompletion

    # Create service and collector
    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
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
        model="test-model",
        messages=messages,
        stream=True
    )

@pytest.mark.asyncio
async def test_litellm_service_passthrough_frame():
    """
    Tests that LiteLLMPipecatService correctly passes through non-LLMMessagesFrame frames.
    """
    # Create a mock LiteLLM router (should not be called)
    mock_router = MagicMock()
    mock_router.acompletion = AsyncMock()

    # Create service and collector
    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
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
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = litellm.exceptions.AuthenticationError("Invalid API Key")

    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2
    assert isinstance(collector.frames[1][0], ErrorFrame)
    assert "Authentication Error" in collector.frames[1][0].error

@pytest.mark.asyncio
async def test_litellm_service_rate_limit_error():
    """
    Tests that LiteLLMPipecatService handles LiteLLM RateLimitError.
    """
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = litellm.exceptions.RateLimitError("Rate limit exceeded")

    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2
    assert isinstance(collector.frames[1][0], ErrorFrame)
    assert "Rate Limit Error" in collector.frames[1][0].error

@pytest.mark.asyncio
async def test_litellm_service_api_error():
    """
    Tests that LiteLLMPipecatService handles LiteLLM APIError.
    """
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = litellm.exceptions.APIError("Some API error")

    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2
    assert isinstance(collector.frames[1][0], ErrorFrame)
    assert "API Error" in collector.frames[1][0].error

@pytest.mark.asyncio
async def test_litellm_service_request_error():
    """
    Tests that LiteLLMPipecatService handles httpx RequestError.
    """
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = httpx.RequestError("Network unreachable", request=httpx.Request("GET", "http://test.com"))

    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2
    assert isinstance(collector.frames[1][0], ErrorFrame)
    assert "Network Request Error" in collector.frames[1][0].error

@pytest.mark.asyncio
async def test_litellm_service_unexpected_exception():
    """
    Tests that LiteLLMPipecatService handles unexpected exceptions.
    """
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = Exception("Some unexpected issue")

    service = LiteLLMPipecatService(litellm_router=mock_router, model_alias="test-model")
    collector = FrameCollector()
    service.link(collector)

    messages = [{"role": "user", "content": "Test"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    await asyncio.sleep(0.01)

    # Expected frames: initial LLMMessagesFrame, ErrorFrame
    assert len(collector.frames) >= 2
    assert isinstance(collector.frames[1][0], ErrorFrame)
    assert "Unexpected Error during LLM streaming" in collector.frames[1][0].error

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
    mock_router = MagicMock()
    mock_router.acompletion.side_effect = mock_acompletion_tool_call

    # Create service and collector
    # Using MagicMock for llm_registry_service and litellm_router for simplicity in this unit test
    mock_llm_registry = MagicMock()
    mock_litellm_router = MagicMock()
    mock_litellm_router.acompletion.side_effect = mock_acompletion_tool_call

    # The LiteLLMPipecatService now expects the router during init
    service = LiteLLMPipecatService(llm_registry_service=mock_llm_registry, preferred_model_alias="test-model", litellm_router=mock_litellm_router)
    collector = FrameCollector()

    # Connect service output to collector input
    service.link(collector)

    # Simulate receiving an LLMMessagesFrame
    messages = [{"role": "user", "content": "What's the weather in New York?"}]
    await service.process_frame(LLMMessagesFrame(messages=messages), FrameDirection.DOWNSTREAM)

    # Allow tasks to run
    await asyncio.sleep(0.1) # Give enough time for all chunks to process

    # Check the collected frames
    # Expected frames (simplified order): Initial Message, Start, Text, InProgress (chunk1), InProgress (chunk2), InProgress (chunk3), InProgress (final), End

    # Find the frames of interest
    initial_message_frame = next((f for f,d in collector.frames if isinstance(f, LLMMessagesFrame)), None)
    start_frame = next((f for f,d in collector.frames if isinstance(f, LLMFullResponseStartFrame)), None)
    text_frame = next((f for f,d in collector.frames if isinstance(f, LLMTextFrame)), None)
    tool_call_frames = [f for f,d in collector.frames if isinstance(f, FunctionCallInProgressFrame)]
    end_frame = next((f for f,d in collector.frames if isinstance(f, LLMFullResponseEndFrame)), None)

    assert initial_message_frame is not None
    assert start_frame is not None
    assert text_frame is not None
    assert text_frame.text == "Okay, I can do that. "
    assert end_frame is not None

    # Verify tool call frames
    assert len(tool_call_frames) >= 4 # Expecting at least 4 in-progress frames for this stream

    # Check the accumulated arguments in the last FunctionCallInProgressFrame for this tool call ID
    # We need to find the frames specific to "call_abc123"
    tool_call_frames_abc123 = [f for f in tool_call_frames if f.tool_call_id == "call_abc123"]
    assert len(tool_call_frames_abc123) >= 4 # Expecting at least 4 frames for this ID

    # The last frame for this tool call ID should have the full arguments
    final_tool_call_frame = tool_call_frames_abc123[-1]

    assert final_tool_call_frame.function_name == "get_weather"
    # Note: The test simulates LiteLLM streaming which might send partial JSON. The service accumulates these.
    # We need to check if the *accumulated* argument string in the final frame is correct.
    expected_args = '{\n  "location": "New York"\n}'
    assert final_tool_call_frame.arguments.strip() == expected_args.strip()

    # Verify that the LiteLLM acompletion method was called
    mock_litellm_router.acompletion.assert_called_once_with(
        model="test-model",
        messages=messages,
        stream=True
    ) 