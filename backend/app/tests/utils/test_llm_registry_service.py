import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import httpx # Import for type hinting and spec for MagicMock

# Assuming LLMRegistryService and config constants are importable
# Adjust the import path based on your project structure
from backend.app.utils.llm_registry_service import LLMRegistryService, LITELLM_PROXY_URL, LITELLM_PROXY_API_KEY

# Helper to consume async generator
async def consume_async_gen(gen):
    data = []
    async for item in gen:
        data.append(item)
    return data

# Base class for common setup
class TestLLMRegistryServiceAdvancedMethodsBase(unittest.IsolatedAsyncioTestCase):
    MOCK_PROXY_URL = "http://mock-litellm-proxy:4000"
    MOCK_API_KEY = "test-api-key"

    @patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', MOCK_API_KEY)
    @patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', MOCK_PROXY_URL)
    async def asyncSetUp(self):
        # Initialize LLMRegistryService with potentially mocked config
        # The class LLMRegistryService reads LITELLM_PROXY_URL upon instantiation
        # and LITELLM_PROXY_API_KEY directly from the module when methods are called.
        # So, patching them at the module level as above is correct.
        self.service = LLMRegistryService()
        self.assertEqual(self.service.litellm_proxy_url, self.MOCK_PROXY_URL)
        # LITELLM_PROXY_API_KEY is not stored in self.service but used directly by methods.

        # Common mock data
        self.model_alias = "test-model"
        self.mock_headers_with_auth = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.MOCK_API_KEY}"
        }
        self.mock_headers_without_auth = {"Content-Type": "application/json"}


@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestChatCompletionAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):

    async def test_chat_completion_advanced_non_streaming_success(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "chatcmpl-123", "choices": [{"message": {"content": "Hello"}}]}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.aclose = AsyncMock() # Mock aclose if it's an async method

        mock_client_cm = MagicMock() # Mock for the client instance within 'async with'
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        messages = [{"role": "user", "content": "Hi"}]
        response_data = await self.service.chat_completion_advanced(
            model_alias=self.model_alias, messages=messages, stream=False
        )

        self.assertEqual(response_data, {"id": "chatcmpl-123", "choices": [{"message": {"content": "Hello"}}]})
        expected_payload = {"model": self.model_alias, "messages": messages, "stream": False, "temperature": 0.7}
        mock_client_cm.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/chat/completions",
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        mock_response.aclose.assert_called_once()

    async def test_chat_completion_advanced_streaming_success(self, mock_async_client_constructor):
        mock_response_stream = MagicMock(spec=httpx.Response)
        mock_response_stream.status_code = 200
        mock_response_stream.headers = {"Content-Type": "text/event-stream"}
        
        async def mock_aiter_bytes_func():
            yield b"data: chunk1\n\n"
            yield b"data: chunk2\n\n"
        
        mock_response_stream.aiter_bytes = mock_aiter_bytes_func
        mock_response_stream.aclose = AsyncMock()

        mock_client_cm_stream = MagicMock()
        mock_client_cm_stream.post.return_value = mock_response_stream
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm_stream
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        messages = [{"role": "user", "content": "Stream test"}]
        stream_gen = await self.service.chat_completion_advanced(
            model_alias=self.model_alias, messages=messages, stream=True
        )

        self.assertTrue(hasattr(stream_gen, '__aiter__')) # Check if it's an async generator
        
        chunks = await consume_async_gen(stream_gen)
        self.assertEqual(chunks, [b"data: chunk1\n\n", b"data: chunk2\n\n"])
        
        expected_payload = {"model": self.model_alias, "messages": messages, "stream": True, "temperature": 0.7}
        mock_client_cm_stream.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/chat/completions",
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        # aclose is called by the stream_generator's finally block in the service
        self.assertTrue(mock_response_stream.aclose.called)


    async def test_chat_completion_advanced_http_status_error(self, mock_async_client_constructor):
        mock_response_error = MagicMock(spec=httpx.Response)
        mock_response_error.status_code = 500
        mock_response_error.text = "Internal Server Error"
        mock_response_error.request = MagicMock(spec=httpx.Request)
        mock_response_error.request.url = f"{self.MOCK_PROXY_URL}/v1/chat/completions"
        mock_response_error.aclose = AsyncMock()
        mock_response_error.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError("Error!", request=mock_response_error.request, response=mock_response_error))


        mock_client_cm_error = MagicMock()
        mock_client_cm_error.post.return_value = mock_response_error
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm_error
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        messages = [{"role": "user", "content": "Error test"}]
        with self.assertRaises(httpx.HTTPStatusError):
            await self.service.chat_completion_advanced(
                model_alias=self.model_alias, messages=messages, stream=False
            )
        self.assertTrue(mock_response_error.aclose.called)

    async def test_chat_completion_advanced_request_error(self, mock_async_client_constructor):
        mock_request = MagicMock(spec=httpx.Request)
        mock_request.url = f"{self.MOCK_PROXY_URL}/v1/chat/completions"

        mock_client_cm_req_error = MagicMock()
        mock_client_cm_req_error.post.side_effect = httpx.RequestError("Connection failed", request=mock_request)
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm_req_error
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)
        
        messages = [{"role": "user", "content": "Request error test"}]
        with self.assertRaises(httpx.RequestError):
            await self.service.chat_completion_advanced(
                model_alias=self.model_alias, messages=messages, stream=False
            )
            
    async def test_chat_completion_advanced_json_decode_error(self, mock_async_client_constructor):
        mock_response_json_error = MagicMock(spec=httpx.Response)
        mock_response_json_error.status_code = 200
        mock_response_json_error.text = "Not a valid JSON"
        mock_response_json_error.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        mock_response_json_error.aclose = AsyncMock()

        mock_client_cm_json_error = MagicMock()
        mock_client_cm_json_error.post.return_value = mock_response_json_error
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm_json_error
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        messages = [{"role": "user", "content": "JSON error test"}]
        with self.assertRaises(json.JSONDecodeError):
            await self.service.chat_completion_advanced(
                model_alias=self.model_alias, messages=messages, stream=False
            )
        self.assertTrue(mock_response_json_error.aclose.called)

    @patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', None) # Test without API Key
    async def test_chat_completion_advanced_no_api_key(self, mock_async_client_constructor_no_key, _): # _ for LITELLM_PROXY_URL
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "chatcmpl-123"}
        mock_response.aclose = AsyncMock()

        mock_client_cm_no_key = MagicMock()
        mock_client_cm_no_key.post.return_value = mock_response
        mock_async_client_constructor_no_key.return_value.__aenter__.return_value = mock_client_cm_no_key
        mock_async_client_constructor_no_key.return_value.__aexit__ = AsyncMock(return_value=None)
        
        messages = [{"role": "user", "content": "Hi"}]
        await self.service.chat_completion_advanced(
            model_alias=self.model_alias, messages=messages, stream=False, extra_body={"custom": "value"}
        )
        expected_payload = {"model": self.model_alias, "messages": messages, "stream": False, "temperature": 0.7, "custom": "value"}
        mock_client_cm_no_key.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/chat/completions",
            headers=self.mock_headers_without_auth, # No Authorization header
            json=expected_payload
        )

# Similar test classes would follow for other methods:
# TestCreateEmbeddingsAdvanced, TestAnalyzeVisionAdvanced, TestSynthesizeSpeechAdvanced,
# TestTranscribeAudioAdvanced, TestGenerateImageAdvanced

@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestCreateEmbeddingsAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):
    async def test_create_embeddings_advanced_success(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"object": "list", "data": [{"embedding": [0.1, 0.2]}]}
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        input_data = "Embed this"
        extra_body = {"encoding_format": "float"}
        response_data = await self.service.create_embeddings_advanced(
            model_alias=self.model_alias, input_data=input_data, extra_body=extra_body
        )

        self.assertEqual(response_data, {"object": "list", "data": [{"embedding": [0.1, 0.2]}]})
        expected_payload = {"model": self.model_alias, "input": input_data, "encoding_format": "float"}
        mock_client_cm.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/embeddings",
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        mock_response.aclose.assert_called_once()

    async def test_create_embeddings_advanced_http_error(self, mock_async_client_constructor):
        mock_response_error = MagicMock(spec=httpx.Response)
        mock_response_error.status_code = 400
        mock_response_error.text = "Bad Request"
        mock_response_error.request = MagicMock(spec=httpx.Request)
        mock_response_error.request.url = f"{self.MOCK_PROXY_URL}/v1/embeddings"
        mock_response_error.aclose = AsyncMock()
        mock_response_error.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError("Error!", request=mock_response_error.request, response=mock_response_error))

        mock_client_cm_error = MagicMock()
        mock_client_cm_error.post.return_value = mock_response_error
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm_error
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        with self.assertRaises(httpx.HTTPStatusError):
            await self.service.create_embeddings_advanced(model_alias=self.model_alias, input_data="test")
        self.assertTrue(mock_response_error.aclose.called)

@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestAnalyzeVisionAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):
    async def test_analyze_vision_advanced_success(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Image description"}}]}
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        messages = [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:..."}}]}]
        extra_body = {"custom_param": "vision_value"}
        response_data = await self.service.analyze_vision_advanced(
            model_alias=self.model_alias, messages=messages, max_tokens=150, extra_body=extra_body
        )

        self.assertEqual(response_data, {"choices": [{"message": {"content": "Image description"}}]})
        expected_payload = {"model": self.model_alias, "messages": messages, "max_tokens": 150, "custom_param": "vision_value"}
        mock_client_cm.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/chat/completions", # Vision uses chat completions
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        mock_response.aclose.assert_called_once()

@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestSynthesizeSpeechAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):
    async def test_synthesize_speech_advanced_success(self, mock_async_client_constructor):
        mock_response_stream = MagicMock(spec=httpx.Response)
        mock_response_stream.status_code = 200
        mock_response_stream.headers = {"Content-Type": "audio/mpeg"} # Default for mp3
        
        async def mock_aiter_bytes_tts():
            yield b"tts_chunk1"
            yield b"tts_chunk2"
        
        mock_response_stream.aiter_bytes = mock_aiter_bytes_tts
        mock_response_stream.aclose = AsyncMock() # Mock aclose for the response

        mock_client_cm_tts = MagicMock() # Mock for the client instance
        mock_client_cm_tts.post.return_value = mock_response_stream
        
        # The AsyncClient itself needs its __aexit__ mocked for when it's closed by stream_generator
        mock_async_client_instance = MagicMock()
        mock_async_client_instance.__aenter__.return_value = mock_client_cm_tts
        mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_async_client_constructor.return_value = mock_async_client_instance


        input_text = "Hello world"
        voice = "alloy"
        response_format = "mp3"
        
        stream_gen, media_type = await self.service.synthesize_speech_advanced(
            model_alias=self.model_alias, input_text=input_text, voice=voice, response_format=response_format
        )

        self.assertEqual(media_type, "audio/mpeg")
        self.assertTrue(hasattr(stream_gen, '__aiter__'))
        
        chunks = await consume_async_gen(stream_gen)
        self.assertEqual(chunks, [b"tts_chunk1", b"tts_chunk2"])
        
        expected_payload = {
            "model": self.model_alias, "input": input_text, "voice": voice, 
            "response_format": response_format, "speed": 1.0
        }
        mock_client_cm_tts.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/audio/speech",
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        # aclose for response and client are called by the stream_generator's finally block
        self.assertTrue(mock_response_stream.aclose.called)
        self.assertTrue(mock_async_client_instance.__aexit__.called)


    async def test_synthesize_speech_advanced_http_error_before_stream(self, mock_async_client_constructor):
        mock_response_error = MagicMock(spec=httpx.Response)
        mock_response_error.status_code = 503
        mock_response_error.text = "Service Unavailable"
        mock_response_error.request = MagicMock(spec=httpx.Request)
        mock_response_error.request.url = f"{self.MOCK_PROXY_URL}/v1/audio/speech"
        mock_response_error.aclose = AsyncMock()
        mock_response_error.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError("Error!", request=mock_response_error.request, response=mock_response_error)
        )

        mock_client_cm_error = MagicMock()
        mock_client_cm_error.post.return_value = mock_response_error
        
        mock_async_client_instance_err = MagicMock()
        mock_async_client_instance_err.__aenter__.return_value = mock_client_cm_error
        mock_async_client_instance_err.__aexit__ = AsyncMock(return_value=None)
        mock_async_client_constructor.return_value = mock_async_client_instance_err

        with self.assertRaises(httpx.HTTPStatusError):
            await self.service.synthesize_speech_advanced(
                model_alias=self.model_alias, input_text="test", voice="echo"
            )
        self.assertTrue(mock_response_error.aclose.called)
        self.assertTrue(mock_async_client_instance_err.__aexit__.called)


@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestTranscribeAudioAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):
    async def test_transcribe_audio_advanced_json_response(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"text": "Transcription result"}
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        file_data = b"audio_bytes"
        file_name = "audio.mp3"
        content_type = "audio/mpeg"
        
        response_data = await self.service.transcribe_audio_advanced(
            model_alias=self.model_alias, file_name=file_name, file_data=file_data, 
            content_type=content_type, response_format="json"
        )

        self.assertEqual(response_data, {"text": "Transcription result"})
        expected_data_payload = {
            "model": self.model_alias, "response_format": "json", "temperature": 0.0
        }
        expected_files_payload = {'file': (file_name, file_data, content_type)}
        
        mock_client_cm.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {self.MOCK_API_KEY}"}, # httpx sets Content-Type for multipart
            data=expected_data_payload,
            files=expected_files_payload
        )
        mock_response.aclose.assert_called_once()

    async def test_transcribe_audio_advanced_text_response(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Simple text transcription"
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        response_data = await self.service.transcribe_audio_advanced(
            model_alias=self.model_alias, file_name="a.wav", file_data=b"...", 
            content_type="audio/wav", response_format="text"
        )
        self.assertEqual(response_data, "Simple text transcription")


@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_API_KEY', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_API_KEY)
@patch('backend.app.utils.llm_registry_service.LITELLM_PROXY_URL', TestLLMRegistryServiceAdvancedMethodsBase.MOCK_PROXY_URL)
@patch('backend.app.utils.llm_registry_service.httpx.AsyncClient')
class TestGenerateImageAdvanced(TestLLMRegistryServiceAdvancedMethodsBase):
    async def test_generate_image_advanced_success(self, mock_async_client_constructor):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": 123, "data": [{"url": "http://image.url"}]}
        mock_response.aclose = AsyncMock()

        mock_client_cm = MagicMock()
        mock_client_cm.post.return_value = mock_response
        mock_async_client_constructor.return_value.__aenter__.return_value = mock_client_cm
        mock_async_client_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

        prompt = "A cat playing piano"
        response_data = await self.service.generate_image_advanced(
            model_alias=self.model_alias, prompt=prompt, n=1, size="1024x1024"
        )

        self.assertEqual(response_data, {"created": 123, "data": [{"url": "http://image.url"}]})
        expected_payload = {
            "model": self.model_alias, "prompt": prompt, "n": 1, 
            "size": "1024x1024", "response_format": "url"
        }
        mock_client_cm.post.assert_called_once_with(
            f"{self.MOCK_PROXY_URL}/v1/images/generations",
            headers=self.mock_headers_with_auth,
            json=expected_payload
        )
        mock_response.aclose.assert_called_once()

if __name__ == '__main__':
    unittest.main()
