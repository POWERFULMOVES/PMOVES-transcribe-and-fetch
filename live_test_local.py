import requests
import json
import time
import copy
import os
import logging
import traceback
import argparse
from dotenv import load_dotenv

"""
Enhanced Live Local LLM Extraction Tester for crawl4ai Fetcher

This script tests the LLMExtractionStrategy using the local LLM model
configured via the LLM_MODEL environment variable.

It assumes:
1. The PMOVES backend is running at http://localhost:8000.
2. The local LLM server (Ollama, LM Studio, etc.) corresponding to the
   configured LLM_MODEL is running and accessible.
3. The necessary environment variables for the LLM server's base URL
   (e.g., OLLAMA_BASE_URL, OPENAI_COMPATIBLE_BASE_URL) are set,
   either in the system environment or in backend/app/.env.
4. The LLM_MODEL environment variable is set to the ID of the local
   model you wish to test (e.g., 'ollama/gemma3', 'openai/gemma3').

Usage:
    python live_llm_test_enhanced.py [options]

Options:
    -h, --help
        Show this help message and exit.

    -u URL, --url URL
        Specify the URL to fetch content from. Defaults to https://www.example.com.
"""

# --- Configuration ---
BASE_URL = "http://localhost:8000"  # PMOVES backend URL
FETCH_ENDPOINT = f"{BASE_URL}/fetch-content"
DEFAULT_TEST_URL = "https://www.example.com" # A simple page for basic extraction

# --- Helper Function for SSE Processing (Adapted from live_llm_local_tester.py) ---
def process_sse_stream(response, scenario_name):
    last_event_data = None
    stream_completed_successfully = False
    sse_messages = []
    extracted_content = None

    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"DEBUG: Received SSE line: {decoded_line}") # Added debug print
                if decoded_line.startswith('data:'):
                    try:
                        event_data_str = decoded_line[len('data:'):].strip()
                        if not event_data_str:
                            continue
                        event_data = json.loads(event_data_str)
                        last_event_data = event_data
                        
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
                            print(f"ERROR: SSE Error event received: {json.dumps(event_data, indent=2)}") # Added error print
                            return False, {"error_type": "sse_error", "messages": sse_messages, "last_data": event_data}

                        if event_type == "completed":
                            print(f"INFO: SSE Completed event received: {json.dumps(event_data, indent=2)}") # Added completed print
                            if event_status == "completed":
                                stream_completed_successfully = True
                                extracted_content = event_data.get('content', {}).get('data', {}).get('extracted_content')
                                return True, {"extracted_content": extracted_content, "raw_sse_data": event_data}
                            else:
                                return False, {"error_type": "sse_completion_status_failed", "messages": sse_messages, "last_data": event_data}
                    except json.JSONDecodeError as e:
                        sse_messages.append(f"WARNING: Could not decode JSON from SSE line: {decoded_line}. Error: {e}")
                        print(f"WARNING: Could not decode JSON from SSE line: {decoded_line}. Error: {e}") # Added warning print
                    except Exception as e:
                        sse_messages.append(f"WARNING: Error processing SSE event data: {event_data_str}. Error: {e}")
                        print(f"WARNING: Error processing SSE event data: {event_data_str}. Error: {e}") # Added warning print
                        
        if not stream_completed_successfully:
            sse_messages.append("SSE stream finished without a successful 'completed' event.")
            print("WARNING: SSE stream finished without a successful 'completed' event.") # Added warning print
            return False, {"error_type": "sse_incomplete", "messages": sse_messages, "last_data": last_event_data}
        
    except requests.exceptions.ChunkedEncodingError as e:
        sse_messages.append(f"FAIL: ChunkedEncodingError during SSE stream: {e}")
        print(f"FAIL: ChunkedEncodingError during SSE stream: {e}") # Added fail print
        return False, {"error_type": "sse_chunked_error", "messages": sse_messages, "details_str": str(e)}
    except Exception as e:
        sse_messages.append(f"FAIL: Exception during SSE stream processing: {e}")
        print(f"FAIL: Exception during SSE stream processing: {e}") # Added fail print
        return False, {"error_type": "sse_generic_error", "messages": sse_messages, "details_str": str(e)}
    
    sse_messages.append("FAIL: SSE stream processing ended unexpectedly.")
    print("FAIL: SSE stream processing ended unexpectedly.") # Added fail print
    return False, {"error_type": "sse_unexpected_exit", "messages": sse_messages, "last_data": last_event_data}

# Helper function to run a single test case
def run_single_test_case(scenario_name, url, params, expected_to_pass):
    current_params = copy.deepcopy(params)
    current_params['url'] = url
    
    response_obj = None
    error_details_for_printing = []
    current_timeout = 180 # Default timeout for local models, can be adjusted

    print(f"\n--- Running Test Case: {scenario_name} ---")
    print(f"INFO: Using timeout {current_timeout} seconds for test '{scenario_name}'")
    print(f"INFO: Request URL: {FETCH_ENDPOINT}")
    print(f"INFO: Request Params: {json.dumps(current_params, indent=2)}") # Added params print

    try:
        response_obj = requests.get(FETCH_ENDPOINT, params=current_params, stream=True, timeout=current_timeout)
        response_obj.raise_for_status()

        actual_request_outcome, result_data = process_sse_stream(response_obj, scenario_name)
        
        has_extracted_content = False
        extracted_content_payload = None

        if actual_request_outcome and result_data and isinstance(result_data, dict):
            extracted_content_obj = result_data.get('extracted_content')
            if isinstance(extracted_content_obj, dict) and extracted_content_obj.get("error") is True:
                has_extracted_content = False
            elif isinstance(extracted_content_obj, dict):
                extracted_content_payload = extracted_content_obj.get('content')
                if isinstance(extracted_content_payload, str) and extracted_content_payload.strip():
                    has_extracted_content = True
                elif isinstance(extracted_content_payload, list) and extracted_content_payload:
                    has_extracted_content = any(isinstance(item, str) and item.strip() for item in extracted_content_payload)
            elif isinstance(extracted_content_obj, str) and extracted_content_obj.strip():
                extracted_content_payload = extracted_content_obj
                has_extracted_content = True
        
        final_outcome_for_comparison = actual_request_outcome and has_extracted_content # Test passes only if SSE completes AND content is extracted

        test_matches_expectation = (final_outcome_for_comparison == expected_to_pass)

        if test_matches_expectation:
            if final_outcome_for_comparison:
                print(f"RESULT: PASS (Expected): {scenario_name}")
                if extracted_content_payload:
                     print(f"  Extracted Content (first 200 chars): {str(extracted_content_payload)[:200]}")
            else:
                print(f"RESULT: FAIL (Expected): {scenario_name}")
                if result_data and isinstance(result_data, dict) and result_data.get("error_type"):
                    print(f"  Reason: SSE Error - {result_data.get('error_type')}")
                elif error_details_for_printing:
                     for line_detail in error_details_for_printing[:1]: print(f"    {line_detail}")

        else: # Unexpected outcome
            if final_outcome_for_comparison: # Unexpectedly passed
                print(f"RESULT: UNEXPECTED PASS: {scenario_name} (Was expected to fail)")
                if extracted_content_payload:
                    print(f"  INFO: LLM test was expected to fail but valid LLM content WAS found.")
                    print(f"  Extracted Content (first 200 chars): {str(extracted_content_payload)[:200]}")
            else: # Unexpectedly failed
                print(f"RESULT: UNEXPECTED FAIL: {scenario_name} (Was expected to pass)")
                if result_data and isinstance(result_data, dict):
                    error_details_for_printing.extend(result_data.get("messages", []))
                    if not result_data.get("messages") and "last_data" in result_data and result_data["last_data"]:
                        error_details_for_printing.append(f"Last SSE Data: {json.dumps(result_data['last_data'], indent=1)}")
                elif result_data:
                    error_details_for_printing.append(str(result_data))
            
            if error_details_for_printing:
                print(f"  Details for {scenario_name}:")
                for line_detail in error_details_for_printing[:5]:
                    print(f"    {line_detail}")
        
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
            print(f"RESULT: FAIL (Expected): {scenario_name} - HTTP Error: {http_err}")
        else:
            print(f"RESULT: UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - HTTP Error")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing[:5]: print(f"    {line}")
        return test_matches_expectation

    except requests.exceptions.RequestException as req_err:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        error_details_for_printing = [f"Request exception: {req_err}"]
        if test_matches_expectation:
            print(f"RESULT: FAIL (Expected): {scenario_name} - Request Exception: {req_err}")
        else:
            print(f"RESULT: UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Request Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: print(f"    {line}")
        return test_matches_expectation

    except Exception as e:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        tb_lines = traceback.format_exc().splitlines()
        error_details_for_printing = [f"An unexpected error occurred: {e}"]
        error_details_for_printing.extend(tb_lines[:5])

        if test_matches_expectation:
            print(f"RESULT: FAIL (Expected): {scenario_name} - Unexpected Exception: {e}")
        else:
            print(f"RESULT: UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Unexpected Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: print(f"    {line}")
        return test_matches_expectation

# --- Test Cases Definition ---
# Test case to use the local LLM model configured via LLM_MODEL environment variable
# This test assumes the configured model is capable of basic text extraction.
TEST_CASES = []

# --- Main Execution Block ---
if __name__ == "__main__":
    # Load environment variables from backend/app/.env
    # This ensures OLLAMA_BASE_URL and OPENAI_COMPATIBLE_BASE_URL are loaded if set there.
    dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
        print(f"INFO: Loaded environment variables from {dotenv_path}")
    else:
        print(f"WARNING: .env file not found at {dotenv_path}. Relying on system environment variables.")

    # Log status of relevant base URLs
    ollama_base = os.getenv('OLLAMA_BASE_URL')
    openai_compatible_base = os.getenv('OPENAI_COMPATIBLE_BASE_URL')

    print(f"INFO: OLLAMA_BASE_URL: {ollama_base if ollama_base else 'Not set (LiteLLM might use default or fail)'}")
    print(f"INFO: OPENAI_COMPATIBLE_BASE_URL: {openai_compatible_base if openai_compatible_base else 'Not set (LiteLLM will fail for openai/lm-studio-model without it)'}")
    if not openai_compatible_base:
        print("WARNING: OPENAI_COMPATIBLE_BASE_URL is not set. OpenAI-compatible tests will likely fail.")

    # Get the selected LLM model ID from environment variables
    selected_llm_model_id = os.getenv('LLM_MODEL')
    if not selected_llm_model_id:
        print("ERROR: LLM_MODEL environment variable is not set. Cannot determine which local model to test.")
        exit(1)
    print(f"INFO: Selected LLM_MODEL for testing: {selected_llm_model_id}")

    # Dynamically add the test case based on the configured model
    TEST_CASES.append({
        "name": f"LLMLocal_ConfiguredModel_{selected_llm_model_id.replace('/', '_')}_Text",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": selected_llm_model_id,
                    "llm_instruction": "Extract the main title of this page as plain text."
                    # The base URL (OLLAMA_BASE_URL or OPENAI_COMPATIBLE_BASE_URL)
                    # is expected to be set in .env or system env, matching the provider
                    # implied by selected_llm_model_id (e.g., 'ollama/...' or 'openai/...')
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": f"Test text extraction with the configured local model '{selected_llm_model_id}'. Requires the corresponding local LLM server running and its base URL configured."
    })


    parser = argparse.ArgumentParser(
        description="Enhanced Live Local LLM Extraction Tester for crawl4ai Fetcher.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-u", "--url",
        help=f"Specify the URL to fetch content from. Defaults to {DEFAULT_TEST_URL}.",
        default=DEFAULT_TEST_URL
    )
    # Removed -t/--tests option as we only run the configured model test now

    args = parser.parse_args()

    print("\nStarting Enhanced Local LLM Extraction live test...")
    
    passed_count = 0
    failed_count = 0
    
    # We only run the single dynamically generated test case
    tests_to_run = TEST_CASES

    if not tests_to_run:
        print("No test cases defined (this should not happen if LLM_MODEL is set).")
    else:
        print(f"Running test case: {tests_to_run[0]['name']}")

    # Run the single test case
    test_case = tests_to_run[0]
    expected_to_pass_value = test_case.get("expected_to_pass", True)
    
    if "setup_notes" in test_case and test_case["setup_notes"]:
        print(f"\nINFO for {test_case['name']}: {test_case['setup_notes']}")

    overall_test_success = run_single_test_case(
        scenario_name=test_case["name"],
        url=args.url, # Use the URL from command line arguments
        params=test_case["params"],
        expected_to_pass=expected_to_pass_value
    )
    if overall_test_success:
        passed_count += 1
    else:
        failed_count += 1
    
    # Removed sleep as there's only one test now

    print("\nEnhanced Local LLM Extraction live test finished.")
    print(f"Total Run: 1, Passed: {passed_count}, Failed: {failed_count}.")
