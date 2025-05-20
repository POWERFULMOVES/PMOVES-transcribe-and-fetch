import asyncio # Import asyncio for running async functions
import requests
import json
import time
import copy
import os
import logging
import traceback
import argparse # Added for command-line argument parsing
from dotenv import load_dotenv # For loading .env file

# Import necessary components from the LLM registry service and app_config
from backend.app.utils.llm_registry_service import initialize_llm_registry, get_available_models, get_model_details
import backend.app.app_config as app_config_module # Import app_config module as an alias

"""
Live Advanced LLM Extraction Tester for crawl4ai Fetcher

This script tests advanced parameters of the LLMExtractionStrategy
as implemented in the /fetch-content endpoint, utilizing the
centralized LLM registry service which interacts with the LiteLLM proxy.

Usage:
    python live_llm_extraction_advanced_tester.py [options]

Options:
    -h, --help
        Show this help message and exit.

    -t TEST [TEST ...], --tests TEST [TEST ...]
        Run specific test cases by their name (case-sensitive) or
        0-based index. If not provided, all defined test cases will be run.
        Example by name:
            python live_llm_extraction_advanced_tester.py -t "LLM Schema: Valid schema with type 'schema'" "LLM Input Format: Valid 'markdown'"
        Example by index:
            python live_llm_extraction_advanced_tester.py -t 0 2
        Example by mixed name and index:
            python live_llm_extraction_advanced_tester.py -t "LLM Apply Chunking: True (with default/valid chunk params)" 5
"""

# --- Configuration ---
BASE_URL = "http://localhost:8000"  # Replace with your backend URL if different
FETCH_ENDPOINT = f"{BASE_URL}/fetch-content"
DEFAULT_TEST_URL = "https://www.example.com" # A text-heavy page for testing

# Configuration for skipping rate-limit sensitive tests
SKIP_KNOWN_RATE_LIMIT_SENSITIVE_TESTS = True # Set to True to skip tests known to hit rate limits
KNOWN_RATE_LIMIT_SENSITIVE_TEST_NAMES = [
    "LLMExtract_ContentTooLarge_WithSufficientContextOverride",
    "LLMExtract_ContentTooLargeForDefaultContext_NoOverride"
    # Add other test names here if they become problematic
]

# --- Helper Function for SSE Processing ---
def process_sse_stream(response, scenario_name):
    """
    Processes an SSE stream from the backend.
    Looks for a 'completed' event and checks its status.
    Returns (True, data_dict) if completed successfully,
            (False, {"error_type": str, "messages": list, "last_data": dict}) otherwise.
    """
    last_event_data = None
    stream_completed_successfully = False
    sse_messages = [] # To store relevant SSE messages for error reporting

    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    try:
                        event_data_str = decoded_line[len('data:'):].strip()
                        if not event_data_str: # Skip empty data lines if any
                            continue
                        event_data = json.loads(event_data_str)
                        last_event_data = event_data # Keep track of the last valid data
                        
                        message_content = event_data.get('message', '')
                        event_type = event_data.get('type', '')
                        event_status = event_data.get('status', '')

                        is_error_event = event_type == "error"
                        is_failed_completion = event_type == "completed" and event_status != "completed"
                        is_significant_status = event_type == "status" and message_content and \
                                                message_content != "No message" and \
                                                "processing chunk" not in message_content.lower() and \
                                                "processed" not in message_content.lower() and \
                                                "fetching" not in message_content.lower() and \
                                                "starting" not in message_content.lower()

                        if is_error_event or is_failed_completion or is_significant_status:
                            sse_messages.append(f"SSE: Type: {event_type}, Status: {event_status}, Msg: {message_content}, Details: {event_data.get('details', 'N/A')}")

                        if event_type == "error":
                            return False, {"error_type": "sse_error", "messages": sse_messages, "last_data": event_data}

                        if event_type == "completed":
                            if event_status == "completed":
                                stream_completed_successfully = True
                                return True, event_data # Successfully completed
                            else:
                                return False, {"error_type": "sse_completion_status_failed", "messages": sse_messages, "last_data": event_data}
                    except json.JSONDecodeError as e:
                        sse_messages.append(f"WARNING: Could not decode JSON from SSE line: {decoded_line}. Error: {e}")
                    except Exception as e:
                        sse_messages.append(f"WARNING: Error processing SSE event data: {event_data_str}. Error: {e}")
                        
        if not stream_completed_successfully:
            sse_messages.append("SSE stream finished without a successful 'completed' event.")
            return False, {"error_type": "sse_incomplete", "messages": sse_messages, "last_data": last_event_data}
        
    except requests.exceptions.ChunkedEncodingError as e:
        sse_messages.append(f"FAIL: ChunkedEncodingError during SSE stream: {e}")
        return False, {"error_type": "sse_chunked_error", "messages": sse_messages, "details_str": str(e)}
    except Exception as e:
        sse_messages.append(f"FAIL: Exception during SSE stream processing: {e}")
        return False, {"error_type": "sse_generic_error", "messages": sse_messages, "details_str": str(e)}
    
    sse_messages.append("FAIL: SSE stream processing ended unexpectedly.")
    return False, {"error_type": "sse_unexpected_exit", "messages": sse_messages, "last_data": last_event_data}

# Helper function to run a single test case
def run_single_test_case(scenario_name, url, params, expected_to_pass):
    current_params = copy.deepcopy(params)
    current_params['url'] = url
    
    response_obj = None
    error_details_for_printing = []

    # Determine timeout based on test case name
    large_content_tests = [
        "LLMExtract_ContentTooLargeForDefaultContext_NoOverride_Google",
        "LLMExtract_ContentTooLarge_WithSufficientContextOverride_Google"
    ]
    current_timeout = 600 if scenario_name in large_content_tests else 180
    print(f"INFO: Using timeout {current_timeout} seconds for test '{scenario_name}'")

    try:
        response_obj = requests.get(FETCH_ENDPOINT, params=current_params, stream=True, timeout=current_timeout)
        response_obj.raise_for_status()

        actual_request_outcome, result_data = process_sse_stream(response_obj, scenario_name)

        original_sse_outcome = actual_request_outcome
        final_outcome_for_comparison = actual_request_outcome 

        is_llm_test = False
        has_extracted_content = False 

        raw_extraction_config = current_params.get('extraction_config', "")
        if isinstance(raw_extraction_config, str) and raw_extraction_config:
            try:
                extraction_config_dict = json.loads(raw_extraction_config)
                if isinstance(extraction_config_dict, dict) and \
                   extraction_config_dict.get("strategy") == "LLMExtractionStrategy":
                    is_llm_test = True
            except json.JSONDecodeError:
                error_details_for_printing.append(
                    f"  WARNING ({scenario_name}): Malformed extraction_config JSON. "
                    f"Could not determine if LLM test for refined pass/fail logic."
                )
        
        if is_llm_test:
            if actual_request_outcome and result_data and isinstance(result_data, dict):
                # Path to extracted_content in the 'completed' SSE event's result_data:
                # result_data -> content -> data -> extracted_content
                sse_event_content_field = result_data.get('content', {})
                if isinstance(sse_event_content_field, dict):
                    data_field = sse_event_content_field.get('data', {})
                    if isinstance(data_field, dict):
                        extracted_content_obj = data_field.get('extracted_content')
                        
                        # Determine the intended llm_extraction_type for this specific test run
                        # to correctly interpret extracted_content_obj
                        current_test_llm_extraction_type = "text" # Default
                        try:
                            _ec_dict = json.loads(raw_extraction_config) # raw_extraction_config is from current_params
                            _ec_params = _ec_dict.get("params", {})
                            current_test_llm_extraction_type = _ec_params.get("llm_extraction_type", "text")
                            if current_test_llm_extraction_type is None: # Handle explicit null
                                current_test_llm_extraction_type = "text"
                            current_test_llm_extraction_type = str(current_test_llm_extraction_type).lower().strip()
                        except Exception:
                            pass # Keep default "text" if parsing fails

                        if isinstance(extracted_content_obj, dict) and extracted_content_obj.get("error") is True:
                            has_extracted_content = False # Structured error from LLM
                        elif current_test_llm_extraction_type == "json":
                            # For JSON type, the extracted_content_obj *is* the content.
                            # It can be a dict or a list. It's considered "content" if it's not empty.
                            if isinstance(extracted_content_obj, (dict, list)):
                                if extracted_content_obj: # Non-empty dict or list
                                    has_extracted_content = True
                                else: # Empty dict {} or list []
                                    has_extracted_content = False
                            elif extracted_content_obj is not None: # Some other non-empty, non-error value (less ideal for JSON type)
                                has_extracted_content = True
                            else: # None
                                has_extracted_content = False
                        elif isinstance(extracted_content_obj, dict): # For text/markdown, content is nested
                            actual_content_payload = extracted_content_obj.get('content')
                            if isinstance(actual_content_payload, str) and actual_content_payload.strip():
                                has_extracted_content = True
                            elif isinstance(actual_content_payload, list) and actual_content_payload:
                                # Check if list contains any non-empty strings
                                has_extracted_content = any(isinstance(item, str) and item.strip() for item in actual_content_payload)
                        elif isinstance(extracted_content_obj, str) and extracted_content_obj.strip(): # Direct string content (e.e. for text/markdown)
                            has_extracted_content = True
                        # If extracted_content_obj is None or an empty list/dict (for non-JSON types after error check), has_extracted_content remains False
            
            if expected_to_pass: 
                if not actual_request_outcome:
                    pass 
                elif not has_extracted_content:
                    final_outcome_for_comparison = False 
                    error_details_for_printing.append(
                        f"  Reason ({scenario_name}): LLM test expected to pass and extract content, but no LLM content found."
                    )
            else: 
                if not actual_request_outcome:
                    pass 
                elif actual_request_outcome and not has_extracted_content:
                    final_outcome_for_comparison = False 
                elif actual_request_outcome and has_extracted_content:
                    pass
        
        adjusted_actual_request_outcome = final_outcome_for_comparison
        test_matches_expectation = (adjusted_actual_request_outcome == expected_to_pass)

        if test_matches_expectation:
            if adjusted_actual_request_outcome: 
                print(f"PASS (Expected): {scenario_name}")
            else: 
                print(f"FAIL (Expected): {scenario_name}")
                if is_llm_test and original_sse_outcome is True and adjusted_actual_request_outcome is False and not has_extracted_content and not expected_to_pass:
                    print(f"  Reason: LLM extraction yielded no content, aligning with expected failure mode for LLM test.")
                elif result_data and isinstance(result_data, dict) and result_data.get("error_type"):
                    print(f"  Reason: SSE Error - {result_data.get('error_type')}")
        else: 
            if adjusted_actual_request_outcome: 
                print(f"UNEXPECTED PASS: {scenario_name} (Was expected to fail)")
                if is_llm_test and has_extracted_content and not expected_to_pass: 
                    print(f"  INFO: LLM test was expected to fail (e.g., by not producing content), but valid LLM content WAS found.")
                if result_data and isinstance(result_data, dict):
                    extracted_content_snippet = result_data.get('extracted_content', {}).get('content', '')
                    markdown_content_snippet = result_data.get('markdown', '')

                    print(f"  Diagnostics for UNEXPECTED PASS - {scenario_name}:")
                    if extracted_content_snippet:
                        print(f"    Extracted Content (first 100 chars): {str(extracted_content_snippet)[:100]}")
                    else:
                        print(f"    Extracted Content: Not found or empty.")

                    if markdown_content_snippet:
                        print(f"    Markdown (first 100 chars): {str(markdown_content_snippet)[:100]}")
                    else:
                        print(f"    Markdown: Not found or empty.")
                    
                    print(f"    Full Result Data (JSON):")
                    for line_json in json.dumps(result_data, indent=1).splitlines():
                        print(f"      {line_json}")
                else:
                    print(f"  Error: UNEXPECTED PASS for {scenario_name}, but no result_data dictionary available for diagnostics.")
            else: 
                print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass)")
                if result_data and isinstance(result_data, dict):
                    error_details_for_printing.extend(result_data.get("messages", []))
                    if not result_data.get("messages"): 
                        if "last_data" in result_data and result_data["last_data"]:
                            error_details_for_printing.append(f"Last SSE Data: {json.dumps(result_data['last_data'], indent=1)}")
                        if "details_str" in result_data and result_data["details_str"]:
                            error_details_for_printing.append(f"Details: {result_data['details_str']}")
                elif result_data: 
                    error_details_for_printing.append(str(result_data))
            
                if error_details_for_printing:
                    print(f"  Details for {scenario_name}:")
                    for line_detail in error_details_for_printing[:5]: 
                        print(f"    {line_detail}")
                else:
                    print(f"  Error: Unexpected outcome for {scenario_name}, but no specific error details captured from SSE processing.")
        
        return test_matches_expectation

    except requests.exceptions.HTTPError as http_err:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        error_details_for_printing = [f"HTTP error: {http_err}"]
        if response_obj is not None and hasattr(response_obj, 'text'):
            try:
                error_content = response_obj.json()
                error_details_for_printing.append(f"Response Body (JSON): {json.dumps(error_content, indent=2)}")
            except json.JSONDecodeError:
                error_text = response_obj.text
                error_details_for_printing.append(f"Response Body (text): {(error_text[:497] + '...') if len(error_text) > 500 else error_text}")

        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - HTTP Error")
            print(f"  Reason: {http_err}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - HTTP Error")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing[:5]:
                print(f"    {line}")
        return test_matches_expectation

    except requests.exceptions.RequestException as req_err:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        error_details_for_printing = [f"Request exception: {req_err}"]
        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - Request Exception")
            print(f"  Reason: {req_err}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Request Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: 
                 print(f"    {line}")
        return test_matches_expectation

    except Exception as e:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        tb_lines = traceback.format_exc().splitlines()
        error_details_for_printing = [f"An unexpected error occurred: {e}"]
        error_details_for_printing.extend(tb_lines[:5])

        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - Unexpected Exception")
            print(f"  Reason: {e}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Unexpected Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: 
                print(f"    {line}")
        return test_matches_expectation

# --- Test Cases Definition ---
# Define test cases with a 'model_alias' that corresponds to an alias in litellm_proxy_config/config.yaml
# The test execution logic will fetch the actual model_id and provider from the registry
TEST_CASES = [
    # New test case for Gemini 2.5 Flash using registry alias
    {
        "name": "LLMExtract_Type_Text_GeminiFlash_Registry",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": { # Define as dict here, will be json.dumps later
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract a concise summary of the main content."
                    # llm_model_id_for_extraction will be added dynamically
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Gemini 2.5 Flash via LLM registry. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured in LiteLLM config."
    },
    # Add test cases for other providers using their aliases
    {
        "name": "LLMExtract_Type_Text_GroqLlama3_Registry",
        "url": DEFAULT_TEST_URL,
        "model_alias": "groq-llama3-8b", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract the main title of this page as plain text."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Groq Llama3 8b via LLM registry. Ensure 'groq-llama3-8b' is configured in LiteLLM config."
    },
    {
        "name": "LLMExtract_Type_Text_Ollama_Registry",
        "url": DEFAULT_TEST_URL,
        "model_alias": "ollama-model-proxy", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Summarize the content."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Ollama model via LLM registry. Ensure 'ollama-model-proxy' is configured in LiteLLM config and Ollama is running."
    },
     {
        "name": "LLMExtract_Type_Text_LMStudio_Registry",
        "url": DEFAULT_TEST_URL,
        "model_alias": "lmstudio-llama3-8b-proxy", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Provide a brief summary."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with LM Studio model via LLM registry. Ensure 'lmstudio-llama3-8b-proxy' is configured in LiteLLM config and LM Studio is running."
    },
    # --- Original Test Cases (Modified to use model_alias) ---
    # llm_extraction_type tests
    {
        "name": "LLMExtract_Type_Text_Google_DefaultInstruction",
        "url": "https://www.example.com",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    # llm_instruction is intentionally missing to test default
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test basic text extraction with Google model via registry and default instruction. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Text_SpecificModel_Google",
        "url": "https://www.example.com",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract the primary content as plain text."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Google Gemini model via registry and specific instruction. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Markdown_Google",
        "url": "https://www.example.com",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "markdown",
                    "llm_instruction": "Convert the main content of this page to well-formatted markdown."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test markdown extraction with Google model via registry. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Json_Google_NoSchema",
        "url": "https://jsonplaceholder.typicode.com/todos/1",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract the user ID and title from the content."
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test JSON extraction with Google model via registry, no schema. LLM should infer structure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Json_SpecificModel_WithSchema_Google",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract the id and title into a JSON object.",
                    "llm_json_schema": {
                        "type": "object",
                        "properties": {
                            "postId": {"type": "integer", "description": "The ID of the post"},
                            "postTitle": {"type": "string", "description": "The title of the post"}
                        },
                        "required": ["postId", "postTitle"]
                    }
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test JSON extraction with Google Gemini model via registry and schema. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Json_InvalidSchema_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract data.",
                    "llm_json_schema": {"type": "object", "properties": "this_is_not_valid_schema"},
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to invalid schema, not model/API key issue
        "setup_notes": "Test JSON extraction with Google model via registry and an invalid schema. Expect failure or error handling. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Null_ShouldDefaultToText_Google",
        "url": "https://www.example.com",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": None,
                    "llm_instruction": "Extract text content.",
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test null llm_extraction_type with Google model via registry, should default to 'text'. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_Missing_ShouldDefaultToText_Google",
        "url": "https://www.example.com",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_instruction": "Extract text content.",
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test missing llm_extraction_type with Google model via registry, should default to 'text'. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Type_InvalidString_ShouldFailOrHandle_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "not_a_valid_type",
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to invalid type
        "setup_notes": "Test invalid string for llm_extraction_type with Google model via registry. Expect failure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },

    # llm_provider_model tests (Keep this one as is to test invalid model handling)
    {
        "name": "LLMExtract_Model_InvalidNonExistent",
        "url": DEFAULT_TEST_URL,
        "model_alias": "nonexistent/model-v1", # This alias should not exist in config
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                }
            }
        },
        "expected_to_pass": False,
        "setup_notes": "Test with an invalid or non-existent LLM provider model alias. Expect failure."
    },

    # llm_instruction tests
    {
        "name": "LLMExtract_Instruction_NotProvided_ShouldUseDefault_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    # llm_instruction is intentionally missing
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test Google model via registry with no llm_instruction. Backend should use a default. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Instruction_EmptyString_Google",
        "url": "https://www.example.com", # Changed to a simpler URL
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "",
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test Google model via registry with empty llm_instruction. Observe behavior. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },

    # llm_json_schema tests (more specific) - using Google
    {
        "name": "LLMExtract_JsonSchema_Provided_But_Type_Not_Json_Google",
        "url": "https://www.example.com", # Changed to a simpler URL
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract text.",
                    "llm_json_schema": {"type": "object", "properties": {"key": {"type": "string"}}},
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test Google via registry: llm_json_schema when type not 'json'. Schema ignored. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    # LLMExtract_Json_NoSchema_ShouldUseGenericExtraction is already covered by LLMExtract_Type_Json_Google_NoSchema

    # llm_context_window_limit_override tests - using Google
    {
        "name": "LLMExtract_ContextWindowOverride_Valid_Google",
        "url": "https://www.lipsum.com/",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Summarize this page briefly.",
                    "llm_context_window_limit_override": 2000,
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test valid llm_context_window_limit_override with Google via registry. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_ContextWindowOverride_InvalidType_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_context_window_limit_override": "not_an_integer",
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to invalid type
        "setup_notes": "Test invalid type for llm_context_window_limit_override with Google via registry. Expect failure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_ContextWindowOverride_Zero_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_context_window_limit_override": 0,
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to zero override
        "setup_notes": "Test zero for llm_context_window_limit_override with Google via registry. Expect failure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },

    # llm_max_tokens_override tests - using Google
    {
        "name": "LLMExtract_MaxTokensOverride_Valid_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Provide a very short summary.",
                    "llm_max_tokens_override": 50,
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test valid llm_max_tokens_override with Google via registry. Extracted content short. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_MaxTokensOverride_InvalidType_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_max_tokens_override": "not_an_integer",
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to invalid type
        "setup_notes": "Test invalid type for llm_max_tokens_override with Google via registry. Expect failure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_MaxTokensOverride_Zero_Google",
        "url": DEFAULT_TEST_URL,
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_max_tokens_override": 0,
                }
            }
        },
        "expected_to_pass": False, # Expecting failure due to zero override
        "setup_notes": "Test zero for llm_max_tokens_override with Google via registry. Expect failure. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },

    # Combination and Edge Cases - using Google
    {
        "name": "LLMExtract_Combination_AllParams_Text_Google",
        "url": "https://www.example.com", # Changed to a simpler URL
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract the main topic from this document.",
                    "llm_context_window_limit_override": 3000,
                    "llm_max_tokens_override": 100
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test combination of text extraction parameters with Google Gemini via registry. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_Combination_AllParams_Json_WithSchema_Google",
        "url": "https://jsonplaceholder.typicode.com/comments/1",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract the commenter's name and email.",
                    "llm_json_schema": {
                        "type": "object",
                        "properties": {
                            "commenterName": {"type": "string"},
                            "commenterEmail": {"type": "string", "format": "email"}
                        },
                        "required": ["commenterName", "commenterEmail"]
                    },
                    "llm_context_window_limit_override": 2000,
                    "llm_max_tokens_override": 150
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test combination of JSON extraction parameters with Google Gemini via registry. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    # This test is kept to verify backend's default model behavior if no llm_provider_model is specified.
    # If backend is configured with Google as default and GEMINI_API_KEY is in its env, this should pass.
    {
        "name": "LLMExtract_MinimalParams_Text_ShouldUseBackendDefaults",
        "url": DEFAULT_TEST_URL,
        # No model_alias here, relies on backend default
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {} # No llm_model_id_for_extraction, no llm_api_token from script
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test with minimal LLM params. Relies on backend defaults (model, API key if needed by default model)."
    },
    {
        "name": "LLMExtract_ContentTooLargeForDefaultContext_NoOverride_Google",
        "url": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "What is the primary theme of this text? Respond in one sentence."
                }
            }
        },
        "expected_to_pass": True, # Expecting it to process, possibly truncated by model's actual limit if not overridden
        "setup_notes": "Test Google via registry with large content, no context override. Observe truncation/error. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    {
        "name": "LLMExtract_ContentTooLarge_WithSufficientContextOverride_Google",
        "url": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm",
        "model_alias": "gemini/gemini-2.5-flash-preview-04-17", # Alias from config.yaml
        "params": {
            "engine": "crawl4ai",
            "extraction_config": {
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Extract the names of the first three characters mentioned.",
                    "llm_context_window_limit_override": 8000 # Example, actual model limit might differ
                }
            }
        },
        "expected_to_pass": True,
        "setup_notes": "Test Google via registry with large content and context override. Ensure 'gemini/gemini-2.5-flash-preview-04-17' is configured."
    },
    # The original LLMExtract_ValidRequestTokenInExtractionConfig_GroqExample test,
    # which used a hardcoded llm_api_token, has been removed as this method of token
    # provision is likely deprecated in favor of environment variables handled by LiteLLM.
    # It is replaced by LLMExtract_Type_Text_Groq_EnvVar below.
    # {
    #     "name": "LLMExtract_ValidRequestTokenInExtractionConfig_GroqExample",
    #     "url": DEFAULT_TEST_URL,
    #     "params": {
    #         "engine": "crawl4ai",
    #         "extraction_config": json.dumps({
    #             "strategy": "LLMExtractionStrategy",
    #             "params": {
    #                 "llm_extraction_type": "text",
    #                 "llm_model_id_for_extraction": "groq/llama3-8b-8192",
    #                 "llm_instruction": "Extract the main title of this page as plain text.",
    #                 "llm_api_token": "GROQ_API_KEY_PLACEHOLDER" # This method is deprecated
    #             }
    #         })
    #     },
    #     "expected_to_pass": True,
    #     "setup_notes": "Original Groq test with deprecated API token method. Should be replaced."
    # },
    # This test is now covered by LLMExtract_Type_Text_GroqLlama3_Registry
    # {
    #     "name": "LLMExtract_Type_Text_Groq_EnvVar",
    #     "url": DEFAULT_TEST_URL,
    #     "params": {
    #         "engine": "crawl4ai",
    #         "extraction_config": json.dumps({
    #             "strategy": "LLMExtractionStrategy",
    #             "params": {
    #                 "llm_extraction_type": "text",
    #                 "llm_model_id_for_extraction": "groq/llama3-8b-8192",
    #                 "llm_instruction": "Extract the main title of this page as plain text."
    #                 # API key is expected to be picked up from GROQ_API_KEY environment variable by LiteLLM
    #             }
    #         })
    #     },
    #     "expected_to_pass": True,
    #     "setup_notes": "Test basic text extraction with a Groq model. GROQ_API_KEY environment variable must be set for LiteLLM to use."
    # }
]

# --- Main Execution Block ---
async def main():
    # Load environment variables from backend/app/.env
    dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"INFO: Loaded environment variables from {dotenv_path}")
    else:
        print(f"WARNING: .env file not found at {dotenv_path}. Relying on system environment variables.")

    # Ensure LiteLLM proxy URL is set on the imported app_config_module
    app_config_module.LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
    app_config_module.LITELLM_PROXY_API_KEY = os.getenv("LITELLM_PROXY_API_KEY") # Optional if proxy is secured

    # Initialize the LLM registry
    print("\nInitializing LLM registry...")
    try:
        # initialize_llm_registry uses the values set on app_config_module
        await initialize_llm_registry()
        print("LLM registry initialized successfully.")
        models = get_available_models()
        print(f"Successfully fetched {len(models)} models from the registry.")
        if len(models) == 0:
             print("WARNING: No models fetched from the registry. Ensure LiteLLM proxy is running and configured correctly.")
    except Exception as e:
        print(f"ERROR: Failed to initialize LLM registry: {e}")
        traceback.print_exc()
        print("Skipping tests that rely on the LLM registry.")
        # Decide how to handle this - maybe exit or skip all tests that need the registry
        return # Exit if registry initialization fails

    parser = argparse.ArgumentParser(
        description="Live Advanced LLM Extraction Tester for crawl4ai Fetcher.",
        formatter_class=argparse.RawTextHelpFormatter # To preserve formatting of help text
    )
    parser.add_argument(
        "-t", "--tests",
        nargs='+',
        help="Run specific test cases by their name (case-sensitive) or 0-based index.\n"
             "If not provided, all defined test cases will be run.\n"
             "Example by name:\n"
             "  python live_llm_extraction_advanced_tester.py -t \"LLM Schema: Valid schema with type 'schema'\" \"LLM Input Format: Valid 'markdown'\"\n"
             "Example by index:\n"
             "  python live_llm_extraction_advanced_tester.py -t 0 2\n"
             "Example by mixed name and index:\n"
             "  python live_llm_extraction_advanced_tester.py -t \"LLM Apply Chunking: True (with default/valid chunk params)\" 5"
    )
    args = parser.parse_args()

    print("\nStarting LLM Extraction Advanced Parameters live tests...")

    passed_count = 0
    failed_count = 0
    skipped_count = 0
    
    tests_to_run = []
    if args.tests:
        for test_identifier in args.tests:
            found_test = None
            # Try to match by index first
            try:
                test_idx = int(test_identifier)
                if 0 <= test_idx < len(TEST_CASES):
                    found_test = TEST_CASES[test_idx]
                else:
                    print(f"WARNING: Test index {test_idx} is out of range (0-{len(TEST_CASES)-1}). Skipping.")
            except ValueError:
                # Not an integer, try to match by name
                for tc in TEST_CASES:
                    if tc["name"] == test_identifier:
                        found_test = tc
                        break
                if not found_test:
                    print(f"WARNING: Test case name '{test_identifier}' not found. Skipping.")
            
            if found_test and found_test not in tests_to_run : # Avoid duplicates if specified multiple times
                tests_to_run.append(found_test)
    else:
        tests_to_run = TEST_CASES

    if not tests_to_run:
        print("No valid test cases selected to run.")
    else:
        print(f"Selected {len(tests_to_run)} test case(s) to run.")


    for test_case in tests_to_run:
        if SKIP_KNOWN_RATE_LIMIT_SENSITIVE_TESTS and test_case["name"] in KNOWN_RATE_LIMIT_SENSITIVE_TEST_NAMES:
            print(f"SKIPPING (Rate Limit Sensitive): {test_case['name']}")
            skipped_count += 1
            continue

        expected_to_pass_value = test_case.get("expected_to_pass", True)
        
        if "setup_notes" in test_case and test_case["setup_notes"]:
            print(f"\nINFO for {test_case['name']}: {test_case['setup_notes']}")

        # --- Dynamic Extraction Config Construction ---
        current_params = copy.deepcopy(test_case["params"])
        extraction_config_dict = current_params.get("extraction_config")

        if extraction_config_dict and extraction_config_dict.get("strategy") == "LLMExtractionStrategy":
            model_alias = test_case.get("model_alias")
            if model_alias:
                # Fetch model details from the registry using the alias
                # Note: get_model_details currently requires provider and model_id
                # We might need to enhance get_model_details or the registry
                # to look up by alias if that's the intended pattern.
                # For now, assuming model_alias is the model_id used in the registry
                # and we might need to infer provider or adjust get_model_details.
                # Let's assume model_alias is the full model_id from the registry for now.
                # A more robust approach would be to store alias->(provider, model_id) mapping.

                # Attempt to infer provider from alias if it follows 'provider/model_name' format
                inferred_provider = None
                if '/' in model_alias:
                    inferred_provider = model_alias.split('/')[0]
                    # Adjust for LiteLLM's provider names if necessary (e.g., 'gemini' vs 'google')
                    if inferred_provider == 'gemini': inferred_provider = 'google'
                    elif inferred_provider == 'ollama': inferred_provider = 'ollama'
                    elif inferred_provider == 'groq': inferred_provider = 'groq'
                    elif inferred_provider == 'lm_studio': inferred_provider = 'lm_studio'
                    # Add other provider mappings as needed

                if inferred_provider:
                     model_details = get_model_details(inferred_provider, model_alias)
                else:
                    # If alias doesn't follow provider/model_name, try fetching without provider filter
                    # This might return multiple matches if aliases are not unique across providers
                    # A better registry lookup by alias is recommended.
                    # For now, let's assume the alias is unique enough or enhance get_model_details.
                    # Let's stick to the inferred provider approach for now based on common patterns.
                    model_details = None # Cannot reliably fetch without provider

                if model_details:
                    # Update extraction_config with the actual model ID from the registry
                    extraction_config_dict["params"]["llm_model_id_for_extraction"] = model_details.model_id
                    # The backend's crawl4ai_fetcher should now use this model ID
                    # and the llm_registry_service will handle routing via the proxy.
                    print(f"INFO: Using model '{model_details.model_id}' (from alias '{model_alias}') via registry for test '{test_case['name']}'")
                else:
                    print(f"ERROR: Model alias '{model_alias}' not found in the LLM registry. Skipping test '{test_case['name']}'.")
                    skipped_count += 1
                    continue # Skip this test if model details cannot be fetched

            # Ensure extraction_config is a JSON string for the request
            current_params["extraction_config"] = json.dumps(extraction_config_dict)
        # --- End Dynamic Extraction Config Construction ---


        overall_test_success = run_single_test_case(
            scenario_name=test_case["name"],
            url=test_case["url"],
            params=current_params,
            expected_to_pass=expected_to_pass_value
        )
        if overall_test_success:
            passed_count += 1
        else:
            failed_count += 1
        
        time.sleep(0.1)

    print("\nAll LLM Extraction Advanced Parameters live tests finished.")
    print(f"Total Run: {len(tests_to_run) - skipped_count}, Passed: {passed_count}, Failed: {failed_count}, Skipped: {skipped_count}.")

if __name__ == "__main__":
    asyncio.run(main())
