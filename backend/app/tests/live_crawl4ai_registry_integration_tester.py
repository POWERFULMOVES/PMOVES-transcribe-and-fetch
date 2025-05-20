import asyncio
import logging
import os
import pytest
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming the backend is running locally and accessible
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")

# --- Test Cases ---

@pytest.mark.asyncio
async def test_crawl4ai_text_extraction_with_llm_registry():
    """
    Test crawl4ai text extraction using an LLM via the registry and proxy.
    Assumes 'groq-llama3-8b' is configured in LiteLLM proxy config.
    """
    logger.info("Starting crawl4ai text extraction integration test.")

    test_url = "https://www.example.com"
    model_alias = "groq-llama3-8b" # Example text model alias
    instruction = "Extract the main title of this page as plain text."

    # Construct the extraction_config payload
    extraction_config = {
        "strategy": "LLMExtractionStrategy",
        "params": {
            "llm_extraction_type": "text",
            "llm_model_id_for_extraction": model_alias,
            "llm_instruction": instruction,
            # Add other relevant LLM parameters as needed
        }
    }

    # URL-encode the extraction_config
    import urllib.parse
    encoded_extraction_config = urllib.parse.quote(json.dumps(extraction_config))

    # Construct the request URL for the /fetch-content endpoint
    request_url = f"{BACKEND_API_URL}/fetch-content?url={urllib.parse.quote(test_url)}&engine=crawl4ai&extraction_config={encoded_extraction_config}"

    logger.info(f"Sending request to: {request_url}")

    extracted_content = ""
    try:
        async with httpx.AsyncClient() as client:
            # The /fetch-content endpoint returns Server-Sent Events (SSE)
            async with client.stream("GET", request_url, timeout=300.0) as response:
                response.raise_for_status() # Raise an exception for bad status codes

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            # SSE data is typically JSON
                            event_data = json.loads(line[len("data:"):].strip())
                            logger.debug(f"Received SSE event: {event_data}")

                            if event_data.get("type") == "extraction_result":
                                extracted_content = event_data.get("content", {}).get("extracted_text", "")
                                logger.info(f"Received extraction_result: {extracted_content}")
                                # In a real test, you'd perform assertions on extracted_content here
                                # For this example, we'll just capture it and assert at the end.

                            if event_data.get("type") in ["status", "error"]:
                                # Log status and error messages from the stream
                                logger.info(f"SSE Status/Error: {event_data.get('status') or event_data.get('type')}: {event_data.get('content', {}).get('message') or event_data.get('message')}")

                            if event_data.get("status") in ["completed", "failed", "error"]:
                                # Stop processing stream on terminal status
                                break

                        except json.JSONDecodeError:
                            logger.warning(f"Could not decode JSON from SSE line: {line}")
                        except Exception as e_event:
                            logger.error(f"Error processing SSE event line '{line}': {e_event}", exc_info=True)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during fetch-content request ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
        pytest.fail(f"HTTP error during fetch-content: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error during fetch-content request ({e.request.url}): {e}", exc_info=True)
        pytest.fail(f"Request error during fetch-content: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during crawl4ai text extraction test: {e}", exc_info=True)
        pytest.fail(f"Unexpected error during test: {e}")

    # Basic assertion: Check if any content was extracted.
    # More specific assertions would check the content itself.
    assert extracted_content, "No content was extracted by the LLM extraction strategy."
    logger.info("Crawl4ai text extraction integration test completed successfully.")


@pytest.mark.asyncio
async def test_crawl4ai_vision_analysis_with_llm_registry():
    """
    Test crawl4ai vision analysis using an LLM via the registry and proxy.
    Assumes a vision model like 'openai-gpt-4o' or 'google-gemini-pro-vision'
    is configured in LiteLLM proxy config.
    """
    logger.info("Starting crawl4ai vision analysis integration test.")

    # Use a simple page URL, the image URL will be in the instruction/payload
    test_url = "https://www.example.com" 
    # Example vision model alias - replace with one configured in your LiteLLM proxy
    vision_model_alias = "openai-gpt-4o" 
    # Example public image URL
    image_url = "https://www.gstatic.com/webp/gallery3/1.png" 
    instruction = f"Describe the image at this URL: {image_url}"

    # Construct the extraction_config payload for vision
    extraction_config = {
        "strategy": "LLMExtractionStrategy",
        "params": {
            "llm_extraction_type": "vision", # Specify vision type
            "llm_model_id_for_extraction": vision_model_alias,
            "llm_instruction": instruction,
            # Depending on backend implementation, image URL might be passed differently.
            # Assuming it's handled within the instruction for simplicity based on common patterns.
            # If the backend expects a structured input for images, this payload needs adjustment.
        }
    }

    # URL-encode the extraction_config
    import urllib.parse
    encoded_extraction_config = urllib.parse.quote(json.dumps(extraction_config))

    # Construct the request URL for the /fetch-content endpoint
    request_url = f"{BACKEND_API_URL}/fetch-content?url={urllib.parse.quote(test_url)}&engine=crawl4ai&extraction_config={encoded_extraction_config}"

    logger.info(f"Sending request to: {request_url}")

    extracted_content = ""
    try:
        async with httpx.AsyncClient() as client:
            # The /fetch-content endpoint returns Server-Sent Events (SSE)
            async with client.stream("GET", request_url, timeout=300.0) as response:
                response.raise_for_status() # Raise an exception for bad status codes

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            # SSE data is typically JSON
                            event_data = json.loads(line[len("data:"):].strip())
                            logger.debug(f"Received SSE event: {event_data}")

                            if event_data.get("type") == "extraction_result":
                                # For vision, the result might be in 'extracted_text' or another field
                                extracted_content = event_data.get("content", {}).get("extracted_text", "")
                                logger.info(f"Received extraction_result: {extracted_content}")
                                # In a real test, you'd perform assertions on extracted_content here

                            if event_data.get("type") in ["status", "error"]:
                                # Log status and error messages from the stream
                                logger.info(f"SSE Status/Error: {event_data.get('status') or event_data.get('type')}: {event_data.get('content', {}).get('message') or event_data.get('message')}")

                            if event_data.get("status") in ["completed", "failed", "error"]:
                                # Stop processing stream on terminal status
                                break

                        except json.JSONDecodeError:
                            logger.warning(f"Could not decode JSON from SSE line: {line}")
                        except Exception as e_event:
                            logger.error(f"Error processing SSE event line '{line}': {e_event}", exc_info=True)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during fetch-content request ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
        pytest.fail(f"HTTP error during fetch-content: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error during fetch-content request ({e.request.url}): {e}", exc_info=True)
        pytest.fail(f"Request error during fetch-content: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during crawl4ai vision analysis test: {e}", exc_info=True)
        pytest.fail(f"Unexpected error during test: {e}")

    # Basic assertion: Check if any content was extracted.
    assert extracted_content, "No content was extracted by the LLM vision analysis strategy."
    logger.info("Crawl4ai vision analysis integration test completed successfully.")


@pytest.mark.asyncio
async def test_backend_audio_transcription_with_llm_registry():
    """
    Test backend audio transcription using an LLM via the registry and proxy.
    This test calls the direct /llm/transcribe-audio endpoint, not the crawl4ai fetcher,
    as crawl4ai_fetcher does not currently support audio input for LLM transcription.
    Assumes an audio transcription model (e.g., 'openai-whisper-1') is configured
    in LiteLLM proxy config and a test audio file named 'test_audio.mp3' exists
    in the backend/app/tests/ directory.
    """
    logger.info("Starting backend audio transcription test.")

    # --- Configuration ---
    # Assumes 'openai-whisper-1' is configured in LiteLLM proxy config for transcription
    model_alias = "openai-whisper-1" 
    # Assumes a test audio file exists in the tests directory
    test_audio_file_path = os.path.join(os.path.dirname(__file__), "test_audio.mp3")

    if not os.path.exists(test_audio_file_path):
        pytest.skip(f"Test audio file not found at {test_audio_file_path}. Skipping audio transcription test.")
        return # Ensure the test function exits

    logger.info(f"Using test audio file: {test_audio_file_path}")

    # --- Send Request ---
    # The /llm/transcribe-audio endpoint expects multipart/form-data
    # with 'model_alias' as a form field and the audio file as a 'file' field.
    files = {'file': ('test_audio.mp3', open(test_audio_file_path, 'rb'), 'audio/mpeg')}
    data = {'model_alias': model_alias}

    request_url = f"{BACKEND_API_URL}/llm/transcribe-audio"
    logger.info(f"Sending POST request to: {request_url}")

    transcription_result = None
    try:
        async with httpx.AsyncClient(timeout=300.0) as client: # Increased timeout for audio
            response = await client.post(
                request_url,
                data=data,
                files=files
            )
            response.raise_for_status() # Raise an exception for bad status codes

            # The response should be JSON containing the transcription
            transcription_result = response.json()
            logger.info(f"Received transcription response: {transcription_result}")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during audio transcription request ({e.request.url}): {e.response.status_code} - {e.response.text}", exc_info=True)
        pytest.fail(f"HTTP error during audio transcription: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error during audio transcription request ({e.request.url}): {e}", exc_info=True)
        pytest.fail(f"Request error during audio transcription: {e}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from audio transcription endpoint. Response text: {response.text}", exc_info=True)
        pytest.fail("Invalid JSON response from audio transcription endpoint.")
    except Exception as e:
        logger.error(f"Unexpected error during backend audio transcription test: {e}", exc_info=True)
        pytest.fail(f"Unexpected error during test: {e}")
    finally:
        # Ensure the file handle is closed
        if 'files' in locals() and 'file' in files and files['file'][1]:
            files['file'][1].close()


    # --- Assertions ---
    assert transcription_result is not None, "Transcription result is None."
    assert isinstance(transcription_result, dict), "Transcription result is not a dictionary."
    assert "text" in transcription_result, "Transcription result does not contain 'text' field."
    assert isinstance(transcription_result["text"], str), "'text' field in transcription result is not a string."
    assert len(transcription_result["text"]) > 0, "Transcribed text is empty."

    logger.info("Backend audio transcription test completed successfully.")


# Example of how to run this test file:
# 1. Ensure LiteLLM proxy and backend are running.
# 2. Ensure necessary environment variables (like BACKEND_API_URL) are set.
# 3. Ensure the models used in tests (e.g., 'groq-llama3-8b', 'openai-gpt-4o', 'openai-whisper-1') are configured in LiteLLM proxy config.
# 4. Ensure a test audio file named 'test_audio.mp3' exists in the backend/app/tests/ directory.
# 5. Run pytest from the project root: `pytest backend/app/tests/live_crawl4ai_registry_integration_tester.py`
