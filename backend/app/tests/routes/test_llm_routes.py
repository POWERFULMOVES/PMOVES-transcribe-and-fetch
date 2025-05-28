import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import httpx # For error types and Request object
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Adjust imports based on your project structure
from backend.app.main import app # Assuming your FastAPI app instance is here
from backend.app.utils.llm_registry_service import LLMRegistryService, get_llm_registry_service
from backend.app.routes.llm_routes import (
    ChatCompletionRequest, ChatMessage, ChatCompletionResponse,
    EmbeddingRequest, EmbeddingResponse,
    ImageGenerationRequest, ImageGenerationResponse,
    TextToSpeechRequest,
    VisionAnalysisRequest,
    TextCompletionRequest, TextCompletionResponse,
    AudioTranscriptionResponse # For the transcription endpoint response model
)

# Helper to consume async generator
async def consume_async_gen(gen):
    data = b"" # Assuming bytes for streaming content
    async for item in gen:
        data += item
    return data

async def consume_json_stream_gen(gen):
    data_chunks = []
    async for item in gen:
        data_chunks.append(item)
    return b"".join(data_chunks)


class TestLLMRoutes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.mock_llm_service = MagicMock(spec=LLMRegistryService)
        # Common data
        self.model_alias = "test-model-alias"

    def tearDown(self):
        app.dependency_overrides.clear()

    # --- Tests for /llm/chat (Refactored) ---

    async def test_chat_completions_non_streaming_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        
        expected_response_data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": self.model_alias, # Service should return actual model, route ensures it's in response
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello there!"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        self.mock_llm_service.chat_completion_advanced = AsyncMock(return_value=expected_response_data)

        request_payload = {
            "model_alias": self.model_alias,
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "temperature": 0.5
        }
        response = self.client.post("/llm/chat", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)
        self.mock_llm_service.chat_completion_advanced.assert_called_once()
        # Detailed argument checking can be added here if needed

    async def test_chat_completions_streaming_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service

        async def mock_stream_generator():
            yield b"data: chunk1\n\n"
            yield b"data: chunk2\n\n"
            yield b"data: [DONE]\n\n"

        self.mock_llm_service.chat_completion_advanced = AsyncMock(return_value=mock_stream_generator())

        request_payload = {
            "model_alias": self.model_alias,
            "messages": [{"role": "user", "content": "Hello stream"}],
            "stream": True
        }
        response = self.client.post("/llm/chat", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        
        stream_content = await consume_json_stream_gen(response.iter_bytes())
        self.assertEqual(stream_content, b"data: chunk1\n\ndata: chunk2\n\ndata: [DONE]\n\n")
        self.mock_llm_service.chat_completion_advanced.assert_called_once()

    async def test_chat_completions_service_http_status_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 500
        mock_http_response.text = '{"error": {"message": "proxy server error"}}'
        mock_http_response.json.return_value = {"error": {"message": "proxy server error"}}

        self.mock_llm_service.chat_completion_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                message="Server error", request=mock_request, response=mock_http_response
            )
        )

        request_payload = {"model_alias": self.model_alias, "messages": [{"role": "user", "content": "Err"}]}
        response = self.client.post("/llm/chat", json=request_payload)

        self.assertEqual(response.status_code, 500)
        self.assertIn("proxy server error", response.json()["detail"])

    async def test_chat_completions_service_request_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        self.mock_llm_service.chat_completion_advanced = AsyncMock(
            side_effect=httpx.RequestError(message="Connection failed", request=mock_request)
        )

        request_payload = {"model_alias": self.model_alias, "messages": [{"role": "user", "content": "ConnErr"}]}
        response = self.client.post("/llm/chat", json=request_payload)

        self.assertEqual(response.status_code, 503)
        self.assertIn("Failed to connect to LLM service", response.json()["detail"])
        
    async def test_chat_completions_request_validation_error(self):
        # No need to mock service here as FastAPI validation happens first
        request_payload = {"model_alias": self.model_alias} # Missing 'messages'
        response = self.client.post("/llm/chat", json=request_payload)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity

    # --- Tests for /llm/embeddings (Refactored) ---
    async def test_create_embeddings_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        expected_response_data = {
            "object": "list",
            "data": [{"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}],
            "model": self.model_alias, # Service should return actual model
            "usage": {"prompt_tokens": 2, "total_tokens": 2}
        }
        self.mock_llm_service.create_embeddings_advanced = AsyncMock(return_value=expected_response_data)

        request_payload = {"model_alias": self.model_alias, "input": "Embed this text"}
        response = self.client.post("/llm/embeddings", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)
        self.mock_llm_service.create_embeddings_advanced.assert_called_once_with(
            model_alias=self.model_alias,
            input_data="Embed this text",
            extra_body=None 
        )

    async def test_create_embeddings_service_http_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 401
        mock_http_response.text = '{"error": "Unauthorized"}'
        mock_http_response.json.return_value = {"error": "Unauthorized"}
        self.mock_llm_service.create_embeddings_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError("Auth error", request=mock_request, response=mock_http_response)
        )
        request_payload = {"model_alias": self.model_alias, "input": "Test input"}
        response = self.client.post("/llm/embeddings", json=request_payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Unauthorized", response.json()["detail"])

    async def test_create_embeddings_request_validation_error(self):
        request_payload = {"model_alias": self.model_alias} # Missing 'input'
        response = self.client.post("/llm/embeddings", json=request_payload)
        self.assertEqual(response.status_code, 422)

    # --- Tests for /llm/generate-image (Refactored) ---
    async def test_generate_image_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        expected_response_data = {
            "created": int(time.time()),
            "data": [{"url": "http://example.com/image.png"}]
        }
        self.mock_llm_service.generate_image_advanced = AsyncMock(return_value=expected_response_data)

        request_payload = {"model_alias": self.model_alias, "prompt": "A cat"}
        response = self.client.post("/llm/generate-image", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)
        self.mock_llm_service.generate_image_advanced.assert_called_once_with(
            model_alias=self.model_alias,
            prompt="A cat",
            n=1, # Default from Pydantic model
            size=None, # Default
            quality=None, # Default
            style=None, # Default
            response_format="url", # Default
            extra_body=None
        )

    async def test_generate_image_service_http_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 400
        mock_http_response.text = '{"error": "Bad prompt"}'
        mock_http_response.json.return_value = {"error": "Bad prompt"}
        self.mock_llm_service.generate_image_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError("Bad req", request=mock_request, response=mock_http_response)
        )
        request_payload = {"model_alias": self.model_alias, "prompt": "A cat"}
        response = self.client.post("/llm/generate-image", json=request_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bad prompt", response.json()["detail"])

    async def test_generate_image_request_validation_error(self):
        request_payload = {"model_alias": self.model_alias} # Missing 'prompt'
        response = self.client.post("/llm/generate-image", json=request_payload)
        self.assertEqual(response.status_code, 422)
        
    # --- Tests for /llm/vision-analyze (Refactored) ---
    async def test_vision_analyze_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        expected_response_data = {
            "id": "vision-cmpl-123", "object": "chat.completion", "created": 12345,
            "model": self.model_alias,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Image analyzed"}, "finish_reason": "stop"}]
        }
        self.mock_llm_service.analyze_vision_advanced = AsyncMock(return_value=expected_response_data)
        
        messages = [{"role": "user", "content": [{"type": "text", "text": "Describe"}, {"type": "image_url", "image_url": {"url": "data:..."}}]}]
        request_payload = {"model_alias": self.model_alias, "messages": messages}
        response = self.client.post("/llm/vision-analyze", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)
        self.mock_llm_service.analyze_vision_advanced.assert_called_once()
        # Can add more detailed arg checking

    async def test_vision_analyze_service_http_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 415 # Unsupported Media Type
        mock_http_response.text = '{"error": "Bad image format"}'
        mock_http_response.json.return_value = {"error": "Bad image format"}
        self.mock_llm_service.analyze_vision_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError("Bad image", request=mock_request, response=mock_http_response)
        )
        request_payload = {"model_alias": self.model_alias, "messages": [{"role": "user", "content": "..."}]}
        response = self.client.post("/llm/vision-analyze", json=request_payload)
        self.assertEqual(response.status_code, 415)
        self.assertIn("Bad image format", response.json()["detail"])
        
    async def test_vision_analyze_request_validation_error(self):
        request_payload = {"model_alias": self.model_alias} # Missing 'messages'
        response = self.client.post("/llm/vision-analyze", json=request_payload)
        self.assertEqual(response.status_code, 422)

    # --- Tests for /llm/text-to-speech (Refactored) ---
    async def test_text_to_speech_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service

        async def mock_tts_stream_generator():
            yield b"audio_chunk_1"
            yield b"audio_chunk_2"

        media_type = "audio/mpeg"
        self.mock_llm_service.synthesize_speech_advanced = AsyncMock(
            return_value=(mock_tts_stream_generator(), media_type)
        )

        request_payload = {"model_alias": self.model_alias, "input": "Speak this", "voice": "alloy"}
        response = self.client.post("/llm/text-to-speech", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], media_type)
        self.assertTrue("attachment; filename=" in response.headers["content-disposition"])
        
        stream_content = await consume_async_gen(response.iter_bytes())
        self.assertEqual(stream_content, b"audio_chunk_1audio_chunk_2")
        self.mock_llm_service.synthesize_speech_advanced.assert_called_once()

    async def test_text_to_speech_service_http_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 400
        mock_http_response.text = '{"error": "Invalid voice"}'
        mock_http_response.json.return_value = {"error": "Invalid voice"}
        self.mock_llm_service.synthesize_speech_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError("Bad voice", request=mock_request, response=mock_http_response)
        )
        request_payload = {"model_alias": self.model_alias, "input": "Speak this", "voice": "invalid_voice"}
        response = self.client.post("/llm/text-to-speech", json=request_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid voice", response.json()["detail"])

    async def test_text_to_speech_request_validation_error(self):
        request_payload = {"model_alias": self.model_alias, "input": "Speak"} # Missing 'voice'
        response = self.client.post("/llm/text-to-speech", json=request_payload)
        self.assertEqual(response.status_code, 422)

    # --- Tests for /llm/transcribe-audio (Refactored) ---
    async def test_transcribe_audio_json_response_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        expected_response_data = {"text": "This is a transcription."}
        self.mock_llm_service.transcribe_audio_advanced = AsyncMock(return_value=expected_response_data)

        files = {'file': ('audio.mp3', b'fake_audio_bytes', 'audio/mpeg')}
        data = {'model_alias': self.model_alias, 'response_format': 'json'}
        
        response = self.client.post("/llm/transcribe-audio", files=files, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)
        self.mock_llm_service.transcribe_audio_advanced.assert_called_once()
        # More detailed arg checking for file_data, file_name, content_type etc.

    async def test_transcribe_audio_text_response_success(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        expected_text_response = "Simple text transcription."
        self.mock_llm_service.transcribe_audio_advanced = AsyncMock(return_value=expected_text_response)

        files = {'file': ('audio.wav', b'other_fake_bytes', 'audio/wav')}
        data = {'model_alias': self.model_alias, 'response_format': 'text'}

        response = self.client.post("/llm/transcribe-audio", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, expected_text_response)
        self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")

    async def test_transcribe_audio_service_http_error(self):
        app.dependency_overrides[get_llm_registry_service] = lambda: self.mock_llm_service
        mock_request = MagicMock(spec=httpx.Request)
        mock_http_response = MagicMock(spec=httpx.Response)
        mock_http_response.status_code = 413 # Payload too large
        mock_http_response.text = '{"error": "File too large"}'
        mock_http_response.json.return_value = {"error": "File too large"}
        self.mock_llm_service.transcribe_audio_advanced = AsyncMock(
            side_effect=httpx.HTTPStatusError("Too large", request=mock_request, response=mock_http_response)
        )
        files = {'file': ('large_audio.mp3', b'large_fake_bytes', 'audio/mpeg')}
        data = {'model_alias': self.model_alias}
        response = self.client.post("/llm/transcribe-audio", files=files, data=data)
        self.assertEqual(response.status_code, 413)
        self.assertIn("File too large", response.json()["detail"])

    async def test_transcribe_audio_request_validation_error_no_file(self):
        data = {'model_alias': self.model_alias} # Missing 'file'
        response = self.client.post("/llm/transcribe-audio", data=data) # No files part
        self.assertEqual(response.status_code, 422) # FastAPI should catch missing file
    
    async def test_transcribe_audio_request_validation_error_no_model(self):
        files = {'file': ('audio.mp3', b'fake_audio_bytes', 'audio/mpeg')}
        # Missing 'model_alias' in data
        response = self.client.post("/llm/transcribe-audio", files=files, data={})
        self.assertEqual(response.status_code, 422)


    # --- Tests for /llm/text-completion (NOT Refactored - uses direct httpx) ---
    @patch('backend.app.routes.llm_routes.httpx.AsyncClient')
    async def test_text_completion_non_streaming_success(self, mock_async_client_constructor_direct):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "cmpl-123", "object": "text_completion", "created": 1677652288,
            "model": self.model_alias,
            "choices": [{"text": "Generated text", "index": 0, "finish_reason": "length"}]
        }
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor_direct.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor_direct.return_value.__aexit__ = AsyncMock(return_value=None)

        request_payload = {"model_alias": self.model_alias, "prompt": "Complete this:", "stream": False}
        response = self.client.post("/llm/text-completion", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["choices"][0]["text"], "Generated text")
        # Direct httpx call, so no service method mock to check

    @patch('backend.app.routes.llm_routes.httpx.AsyncClient')
    async def test_text_completion_streaming_success(self, mock_async_client_constructor_direct_stream):
        mock_response_stream = MagicMock(spec=httpx.Response)
        mock_response_stream.status_code = 200
        mock_response_stream.headers = {"Content-Type": "text/event-stream"}
        
        async def mock_aiter_bytes_tc():
            yield b"data: tc_chunk1\n\n"
            yield b"data: tc_chunk2\n\n"
        
        mock_response_stream.aiter_bytes = mock_aiter_bytes_tc
        mock_response_stream.aclose = AsyncMock()

        mock_client_cm_stream = MagicMock()
        mock_client_cm_stream.post.return_value = mock_response_stream
        mock_async_client_constructor_direct_stream.return_value.__aenter__.return_value = mock_client_cm_stream
        mock_async_client_constructor_direct_stream.return_value.__aexit__ = AsyncMock(return_value=None)

        request_payload = {"model_alias": self.model_alias, "prompt": "Stream this completion:", "stream": True}
        response = self.client.post("/llm/text-completion", json=request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        
        stream_content = await consume_json_stream_gen(response.iter_bytes())
        self.assertEqual(stream_content, b"data: tc_chunk1\n\ndata: tc_chunk2\n\n")

    @patch('backend.app.routes.llm_routes.httpx.AsyncClient')
    async def test_text_completion_direct_http_error(self, mock_async_client_constructor_direct_err):
        mock_response_error = MagicMock(spec=httpx.Response)
        mock_response_error.status_code = 500
        mock_response_error.text = '{"error": "Direct proxy error"}'
        mock_response_error.request = MagicMock(spec=httpx.Request)
        mock_response_error.aclose = AsyncMock()
        mock_response_error.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError("Direct error", request=mock_response_error.request, response=mock_response_error)
        )

        mock_client_cm_error = MagicMock()
        mock_client_cm_error.post.return_value = mock_response_error
        mock_async_client_constructor_direct_err.return_value.__aenter__.return_value = mock_client_cm_error
        mock_async_client_constructor_direct_err.return_value.__aexit__ = AsyncMock(return_value=None)

        request_payload = {"model_alias": self.model_alias, "prompt": "Error test"}
        response = self.client.post("/llm/text-completion", json=request_payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Direct proxy error", response.json()["detail"])


if __name__ == '__main__':
    unittest.main()
