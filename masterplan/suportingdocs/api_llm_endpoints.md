# LLM API Endpoints

This document outlines the backend API endpoints provided for interacting with various Large Language Model (LLM) capabilities. These endpoints directly call the LiteLLM proxy's data plane endpoints (e.g., `/v1/chat/completions`, `/v1/embeddings`), leveraging the `llm_registry_service` for model information.

All LLM-specific endpoints are prefixed with `/api/v1`.

## Common Concepts

*   **`model_alias`**: Most endpoints require a `model_alias` in the request. This alias corresponds to a model configured in the LiteLLM proxy's `config.yaml` (e.g., `openai-chat`, `groq-llama3-8b`, `openai-embedding`, `openai-dalle3`). The backend endpoints use this alias to specify which model the LiteLLM proxy should use for the request, and the `llm_registry_service` can be used to retrieve information about available models based on this alias.
*   **Authentication**: These endpoints are protected by the same authentication mechanisms as the rest of the backend API (if any are configured, e.g., API keys).
*   **Error Handling**: Errors from the LLM providers or the proxy will be propagated. Standard HTTP error codes (e.g., 400, 422, 500, 503) will be used.

---

## 1. Get LLM Routes Status

*   **Endpoint:** `GET /api/v1/llm/status`
*   **Purpose:** A basic health check endpoint to confirm that the LLM routing module is active.
*   **Request Body:** None
*   **Response Body:**
    ```json
    {
        "status": "LLM routes are active"
    }
    ```
*   **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/llm/status"
    ```

---

## 2. Chat Completions

*   **Endpoint:** `POST /api/v1/llm/chat`
*   **Purpose:** Generates a model response for a given chat conversation.
*   **Request Body (`ChatCompletionRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-chat')",
        "messages": [
            {
                "role": "string (e.g., 'user', 'assistant', 'system')",
                "content": "string"
            }
        ],
        "temperature": "float (optional, default: 0.7)",
        "max_tokens": "integer (optional)",
        "stream": "boolean (optional, default: false)",
        "user": "string (optional)"
    }
    ```
*   **Response Body (`ChatCompletionResponse`):**
    ```json
    {
        "id": "string",
        "object": "chat.completion",
        "created": "integer (timestamp)",
        "model": "string (actual model name used)",
        "choices": [
            {
                "index": "integer",
                "message": {
                    "role": "string",
                    "content": "string"
                },
                "finish_reason": "string (optional)"
            }
        ],
        "usage": {
            "prompt_tokens": "integer",
            "completion_tokens": "integer (optional)",
            "total_tokens": "integer"
        }
    }
    ```
    *Note: Streaming responses (`stream: true`) are not fully implemented in the Pydantic model mapping for this endpoint yet and will raise a 501 error. The underlying service call might support streaming.*
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "groq-llama3-8b", 
        "messages": [{"role": "user", "content": "Hello, how are you?"}]
    }'
    ```

---

## 3. Embeddings

*   **Endpoint:** `POST /api/v1/llm/embeddings`
*   **Purpose:** Generates an embedding vector for given input text(s).
*   **Request Body (`EmbeddingRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-embedding')",
        "input": "string OR array of strings"
    }
    ```
*   **Response Body (`EmbeddingResponse`):**
    ```json
    {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": ["array of floats"],
                "index": "integer"
            }
        ],
        "model": "string (actual model name used)",
        "usage": {
            "prompt_tokens": "integer",
            "total_tokens": "integer"
        }
    }
    ```
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/embeddings" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "openai-embedding-ada-002", 
        "input": "The quick brown fox jumps over the lazy dog"
    }'
    ```

---

## 4. Image Generation

*   **Endpoint:** `POST /api/v1/llm/generate-image`
*   **Purpose:** Generates image(s) from a text prompt.
*   **Request Body (`ImageGenerationRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-dalle3')",
        "prompt": "string",
        "n": "integer (optional, default: 1, max depends on provider)",
        "size": "string (optional, e.g., '1024x1024')",
        "quality": "string (optional, e.g., 'standard', 'hd')",
        "style": "string (optional, e.g., 'vivid', 'natural')",
        "response_format": "string (optional, default: 'url', can be 'b64_json')"
    }
    ```
*   **Response Body (`ImageGenerationResponse`):**
    ```json
    {
        "created": "integer (timestamp)",
        "data": [
            {
                "b64_json": "string (optional, if response_format is 'b64_json')",
                "url": "string (optional, if response_format is 'url')",
                "revised_prompt": "string (optional)"
            }
        ]
    }
    ```
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/generate-image" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "openai-dalle3", 
        "prompt": "A futuristic cityscape at sunset",
        "n": 1,
        "size": "1024x1024"
    }'
    ```

---

## 5. Text Completion (Legacy)

*   **Endpoint:** `POST /api/v1/llm/text-completion`
*   **Purpose:** Generates text completions for a given prompt. (Note: Many newer models prefer chat completions.)
*   **Request Body (`TextCompletionRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-text-davinci-003')",
        "prompt": "string OR array of strings",
        "max_tokens": "integer (optional, default: 16)",
        "temperature": "float (optional, default: 0.7)",
        "stream": "boolean (optional, default: false)",
        "user": "string (optional)"
    }
    ```
*   **Response Body (`TextCompletionResponse`):**
    ```json
    {
        "id": "string",
        "object": "text_completion",
        "created": "integer (timestamp)",
        "model": "string (actual model name used)",
        "choices": [
            {
                "text": "string",
                "index": "integer",
                "logprobs": "object (optional)",
                "finish_reason": "string (optional)"
            }
        ],
        "usage": {
            "prompt_tokens": "integer",
            "completion_tokens": "integer (optional)",
            "total_tokens": "integer"
        }
    }
    ```
    *Note: Streaming responses (`stream: true`) are not fully implemented in the Pydantic model mapping for this endpoint yet and will raise a 501 error.*
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/text-completion" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "openai-gpt-3.5-turbo-instruct", 
        "prompt": "Once upon a time,"
    }'
    ```

---

## 6. Audio Transcription

*   **Endpoint:** `POST /api/v1/llm/transcribe-audio`
*   **Purpose:** Transcribes an audio file into text.
*   **Request Body:** `multipart/form-data` containing:
    *   `model_alias`: string (e.g., `openai-whisper`)
    *   `file`: The audio file to transcribe.
    *   `language`: string (optional, ISO 639-1 code, e.g., `en`)
    *   `prompt`: string (optional)
    *   `response_format`: string (optional, default: `json`, e.g., `text`, `srt`, `verbose_json`, `vtt`)
    *   `temperature`: float (optional, default: `0.0`)
*   **Response Body (`AudioTranscriptionResponse`):**
    *   If `response_format` is `json` or `verbose_json`:
        ```json
        {
            "text": "string (transcribed text)",
            "language": "string (optional, detected language)",
            "duration": "float (optional, audio duration in seconds)",
            "segments": ["array of objects (optional, if verbose_json)"],
            "words": ["array of objects (optional, if verbose_json with word timestamps)"]
        }
        ```
    *   If `response_format` is `text`, `srt`, `vtt`: The response body will be a plain string with the transcript in the requested format. The `AudioTranscriptionResponse` model will wrap this in `{"text": "..."}`.
*   **Example (using curl with form data):**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/transcribe-audio" \
    -F "model_alias=openai-whisper-1" \
    -F "file=@/path/to/your/audio.mp3" \
    -F "response_format=json"
    ```

---

## 7. Text-to-Speech (TTS)

*   **Endpoint:** `POST /api/v1/llm/text-to-speech`
*   **Purpose:** Synthesizes speech from input text.
*   **Request Body (`TextToSpeechRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-tts-1')",
        "input": "string (text to synthesize)",
        "voice": "string (e.g., 'alloy', 'echo')",
        "response_format": "string (optional, default: 'mp3', e.g., 'opus', 'aac', 'flac')",
        "speed": "float (optional, default: 1.0, range: 0.25 to 4.0)"
    }
    ```
*   **Response Body:** The raw audio data stream. The `Content-Type` header will indicate the audio format (e.g., `audio/mpeg` for mp3). The `Content-Disposition` header will suggest a filename for download.
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/text-to-speech" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "openai-tts-1", 
        "input": "Hello world, this is a test of text to speech.",
        "voice": "alloy",
        "response_format": "mp3"
    }' --output speech.mp3
    ```

---

## 8. Vision Analysis

*   **Endpoint:** `POST /api/v1/llm/vision-analyze`
*   **Purpose:** Analyzes an image using a vision-capable LLM, often with a text prompt.
*   **Request Body (`VisionAnalysisRequest`):**
    ```json
    {
        "model_alias": "string (e.g., 'openai-gpt-4-vision')",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "string (e.g., 'What is in this image?')"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                             "url": "string (URL or base64 data URI of the image)"
                        }
                    }
                ]
            }
        ],
        "max_tokens": "integer (optional, default: 300)",
        "temperature": "float (optional)"
    }
    ```
*   **Response Body (`ChatCompletionResponse` - reused for vision analysis):**
    ```json
    {
        "id": "string",
        "object": "chat.completion", 
        "created": "integer (timestamp)",
        "model": "string (actual model name used)",
        "choices": [
            {
                "index": "integer",
                "message": {
                    "role": "assistant",
                    "content": "string (textual analysis of the image)"
                },
                "finish_reason": "string (optional)"
            }
        ],
        "usage": {
            "prompt_tokens": "integer",
            "completion_tokens": "integer (optional)",
            "total_tokens": "integer"
        }
    }
    ```
*   **Example (using an image URL):**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/llm/vision-analyze" \
    -H "Content-Type: application/json" \
    -d '{
        "model_alias": "openai-gpt-4o", 
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Describe this image."},
                    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
                ]
            }
        ],
        "max_tokens": 500
    }'
    ```

---
