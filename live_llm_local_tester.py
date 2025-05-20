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
Live Local LLM Extraction Tester for crawl4ai Fetcher using PMOVES app_config

This script tests LLMExtractionStrategy with local model providers
(Ollama, LM Studio via OpenAI-compatible endpoint) as configured
in backend/app/app_config.py.

It assumes that the local LLM servers (Ollama, LM Studio) are running
and accessible, and that the necessary environment variables for their
base URLs (OLLAMA_BASE_URL, OPENAI_COMPATIBLE_BASE_URL) are set,
either in the system environment or in backend/app/.env.

Usage:
    python live_llm_local_tester.py [options]

Options:
    -h, --help
        Show this help message and exit.

    -t TEST [TEST ...], --tests TEST [TEST ...]
        Run specific test cases by their name (case-sensitive) or
        0-based index. If not provided, all defined test cases will be run.
"""

# --- Configuration ---
BASE_URL = "http://localhost:8000"  # PMOVES backend URL
FETCH_ENDPOINT = f"{BASE_URL}/fetch-content"
DEFAULT_TEST_URL = "https://www.example.com" # A simple page for basic extraction

# --- Helper Function for SSE Processing (Copied from live_llm_extraction_advanced_tester.py) ---
def process_sse_stream(response, scenario_name):
    last_event_data = None
    stream_completed_successfully = False
    sse_messages = []

    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
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
                            return False, {"error_type": "sse_error", "messages": sse_messages, "last_data": event_data}

                        if event_type == "completed":
                            if event_status == "completed":
                                stream_completed_successfully = True
                                return True, event_data
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

# Helper function to run a single test case (Adapted from live_llm_extraction_advanced_tester.py)
def run_single_test_case(scenario_name, url, params, expected_to_pass):
    current_params = copy.deepcopy(params)
    current_params['url'] = url
    
    response_obj = None
    error_details_for_printing = []
    current_timeout = 180 # Default timeout for local models, can be adjusted

    print(f"INFO: Using timeout {current_timeout} seconds for test '{scenario_name}'")

    try:
        response_obj = requests.get(FETCH_ENDPOINT, params=current_params, stream=True, timeout=current_timeout)
        response_obj.raise_for_status()

        actual_request_outcome, result_data = process_sse_stream(response_obj, scenario_name)
        
        original_sse_outcome = actual_request_outcome
        final_outcome_for_comparison = actual_request_outcome
        is_llm_test = True # All tests in this script are LLM tests
        has_extracted_content = False

        if actual_request_outcome and result_data and isinstance(result_data, dict):
            sse_event_content_field = result_data.get('content', {})
            if isinstance(sse_event_content_field, dict):
                data_field = sse_event_content_field.get('data', {})
                if isinstance(data_field, dict):
                    extracted_content_obj = data_field.get('extracted_content')
                    if isinstance(extracted_content_obj, dict) and extracted_content_obj.get("error") is True:
                        has_extracted_content = False
                    elif isinstance(extracted_content_obj, dict):
                        actual_content_payload = extracted_content_obj.get('content')
                        if isinstance(actual_content_payload, str) and actual_content_payload.strip():
                            has_extracted_content = True
                        elif isinstance(actual_content_payload, list) and actual_content_payload:
                            has_extracted_content = any(isinstance(item, str) and item.strip() for item in actual_content_payload)
                    elif isinstance(extracted_content_obj, str) and extracted_content_obj.strip():
                        has_extracted_content = True
        
        if expected_to_pass:
            if not actual_request_outcome or not has_extracted_content:
                final_outcome_for_comparison = False
                if not actual_request_outcome:
                     error_details_for_printing.append(f"  Reason ({scenario_name}): SSE stream did not complete successfully.")
                elif not has_extracted_content:
                    error_details_for_printing.append(f"  Reason ({scenario_name}): LLM test expected to pass and extract content, but no LLM content found.")
        else: # expected_to_fail
            if actual_request_outcome and has_extracted_content: # Unexpectedly passed and got content
                final_outcome_for_comparison = True # Treat as if it passed for comparison logic
            elif actual_request_outcome and not has_extracted_content: # Passed SSE but no content (correct for some failure modes)
                final_outcome_for_comparison = False
            # If not actual_request_outcome, it correctly failed, so final_outcome_for_comparison remains False

        test_matches_expectation = (final_outcome_for_comparison == expected_to_pass)

        if test_matches_expectation:
            if final_outcome_for_comparison:
                print(f"PASS (Expected): {scenario_name}")
            else:
                print(f"FAIL (Expected): {scenario_name}")
                if result_data and isinstance(result_data, dict) and result_data.get("error_type"):
                    print(f"  Reason: SSE Error - {result_data.get('error_type')}")
                elif error_details_for_printing:
                     for line_detail in error_details_for_printing[:1]: print(f"    {line_detail}")

        else: # Unexpected outcome
            if final_outcome_for_comparison: # Unexpectedly passed
                print(f"UNEXPECTED PASS: {scenario_name} (Was expected to fail)")
                if has_extracted_content:
                    print(f"  INFO: LLM test was expected to fail but valid LLM content WAS found.")
                if result_data and isinstance(result_data, dict):
                    extracted_content_snippet = result_data.get('content', {}).get('data',{}).get('extracted_content',{}).get('content','')
                    print(f"    Extracted Content (first 100 chars): {str(extracted_content_snippet)[:100]}")
            else: # Unexpectedly failed
                print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass)")
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
            print(f"FAIL (Expected): {scenario_name} - HTTP Error: {http_err}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - HTTP Error")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing[:5]: print(f"    {line}")
        return test_matches_expectation

    except requests.exceptions.RequestException as req_err:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        error_details_for_printing = [f"Request exception: {req_err}"]
        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - Request Exception: {req_err}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Request Exception")
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
            print(f"FAIL (Expected): {scenario_name} - Unexpected Exception: {e}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Unexpected Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: print(f"    {line}")
        return test_matches_expectation

# --- Test Cases Definition ---
TEST_CASES = [
    {
        "name": "LLMLocal_Ollama_Gemma3_Text",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "ollama/gemma3", # Changed
                    "llm_instruction": "Extract the main title of this page as plain text."
                    # OLLAMA_BASE_URL is expected to be set in .env or system env
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Ollama (gemma3 model). Requires Ollama server running and OLLAMA_BASE_URL configured if not default."
    },
    {
        "name": "LLMLocal_Ollama_Phi4_Reasoning_Text",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "ollama/phi4", # Changed
                    "llm_instruction": "Summarize the main content of this page in one sentence."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with Ollama (phi4 reasoning model). Requires Ollama server running and OLLAMA_BASE_URL configured."
    },
    {
        "name": "LLMLocal_LMStudio_Gemma3_Text",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "openai/gemma3", # Changed - Assumes LM Studio recognizes 'gemma3'
                    "llm_instruction": "What is the primary subject of this webpage? Respond concisely."
                    # OPENAI_COMPATIBLE_BASE_URL must be set to LM Studio's server endpoint.
                    # OPENAI_API_KEY can be a dummy value like "lm-studio" if server allows.
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with LM Studio (gemma3 model). Requires server running, OPENAI_COMPATIBLE_BASE_URL set, and LM Studio configured to serve 'gemma3'."
    },
    {
        "name": "LLMLocal_LMStudio_Phi4_Text",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "openai/phi4", # Changed - Assumes LM Studio recognizes 'phi4'
                    "llm_instruction": "Extract the main idea of this page in one phrase."
                    # OPENAI_COMPATIBLE_BASE_URL must be set to LM Studio's server endpoint.
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with LM Studio (phi4 model). Requires server running, OPENAI_COMPATIBLE_BASE_URL set, and LM Studio configured to serve 'phi4'."
    },
    {
        "name": "LLMLocal_Ollama_InvalidModel_ShouldFail",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "ollama/nonexistent-model-123",
                    "llm_instruction": "Extract text."
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test with a non-existent Ollama model. Expect failure."
    }
]

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
        print("WARNING: OPENAI_COMPATIBLE_BASE_URL is not set. LM Studio tests will likely fail.")


    parser = argparse.ArgumentParser(
        description="Live Local LLM Extraction Tester for crawl4ai Fetcher.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-t", "--tests",
        nargs='+',
        help="Run specific test cases by name (case-sensitive) or 0-based index."
    )
    args = parser.parse_args()

    print("\nStarting Local LLM Extraction live tests...")
    
    passed_count = 0
    failed_count = 0
    
    tests_to_run = []
    if args.tests:
        for test_identifier in args.tests:
            found_test = None
            try:
                test_idx = int(test_identifier)
                if 0 <= test_idx < len(TEST_CASES):
                    found_test = TEST_CASES[test_idx]
                else:
                    print(f"WARNING: Test index {test_idx} is out of range. Skipping.")
            except ValueError:
                for tc in TEST_CASES:
                    if tc["name"] == test_identifier:
                        found_test = tc
                        break
                if not found_test:
                    print(f"WARNING: Test case name '{test_identifier}' not found. Skipping.")
            
            if found_test and found_test not in tests_to_run:
                tests_to_run.append(found_test)
    else:
        tests_to_run = TEST_CASES

    if not tests_to_run:
        print("No valid test cases selected to run.")
    else:
        print(f"Selected {len(tests_to_run)} test case(s) to run.")

    for test_case in tests_to_run:
        expected_to_pass_value = test_case.get("expected_to_pass", True)
        
        if "setup_notes" in test_case and test_case["setup_notes"]:
            print(f"\nINFO for {test_case['name']}: {test_case['setup_notes']}")

        overall_test_success = run_single_test_case(
            scenario_name=test_case["name"],
            url=test_case["url"],
            params=test_case["params"],
            expected_to_pass=expected_to_pass_value
        )
        if overall_test_success:
            passed_count += 1
        else:
            failed_count += 1
        
        time.sleep(0.5) # Small delay between tests

    print("\nAll Local LLM Extraction live tests finished.")
    print(f"Total Run: {len(tests_to_run)}, Passed: {passed_count}, Failed: {failed_count}.")