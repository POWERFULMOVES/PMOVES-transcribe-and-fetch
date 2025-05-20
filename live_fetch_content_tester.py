import requests
import json
import time
import copy

# --- Configuration ---
BASE_URL = "http://localhost:8000"  # Replace with your backend URL if different
FETCH_ENDPOINT = f"{BASE_URL}/fetch-content"
DEFAULT_TEST_URL = "http://example.com" # A simple, reliable URL for testing

# Configuration for selective test execution
ONLY_RUN_LLM_TOKEN_PRECEDENCE_TESTS = True# Set to True to run only the LLM token tests
LLM_TOKEN_PRECEDENCE_TEST_NAMES = [
    "LLMTokenPrecedence_RequestTokenOverridesEnv",
    "LLMTokenPrecedence_EnvTokenUsedWhenRequestTokenAbsent",
    "LLMTokenPrecedence_InvalidRequestTokenCausesFailureDespiteValidEnvToken",
    "LLMTokenPrecedence_NoRequestTokenAndNoOrInvalidEnvTokenCausesFailure"
]

# Configuration for skipping rate-limit sensitive tests
SKIP_KNOWN_RATE_LIMIT_SENSITIVE_TESTS = True # Set to True to skip tests known to hit rate limits
KNOWN_RATE_LIMIT_SENSITIVE_TEST_NAMES = [
    "LLMExtract_ContentTooLargeForDefaultContext_NoOverride",
    "LLMExtract_ContentTooLarge_WithSufficientContextOverride"
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
    # print(f"--- {scenario_name}: Processing SSE Stream ---") # Suppressed
    last_event_data = None
    stream_completed_successfully = False
    sse_messages = [] # To store relevant SSE messages for error reporting

    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                # print(f"SSE RAW: {decoded_line}") # Uncomment for verbose SSE logging
                if decoded_line.startswith('data:'):
                    try:
                        event_data_str = decoded_line[len('data:'):].strip()
                        if not event_data_str: # Skip empty data lines if any
                            continue
                        event_data = json.loads(event_data_str)
                        last_event_data = event_data # Keep track of the last valid data
                        
                        # Capture all non-empty messages for potential error reporting
                        # Simplified: capture message if it's an error, or a non-successful completion, or if it's not a generic status.
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
                                # Message already captured above if relevant
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
def run_single_test_case(scenario_name, url, params, expected_to_pass, token_test_llm_override=None): # MODIFIED SIGNATURE
    # print(f"\n--- Starting Test Case: {scenario_name} ---") # Suppressed
    
    # Use deepcopy for params to ensure modifications for LLM override don't affect original TEST_CASES
    current_params = copy.deepcopy(params)
    current_params['url'] = url

    if token_test_llm_override:
        # print(f"  LLM Override: Applying model '{token_test_llm_override}' for test '{scenario_name}'") # Optional debug
        if 'extraction_config' in current_params:
            try:
                extraction_config_dict = json.loads(current_params['extraction_config'])
                if 'params' in extraction_config_dict: # Ensure 'params' sub-dictionary exists
                    extraction_config_dict['params']['llm_provider_model'] = token_test_llm_override
                    current_params['extraction_config'] = json.dumps(extraction_config_dict)
                    # print(f"  Applied LLM Override. New extraction_config: {current_params['extraction_config']}") # Debug
                else:
                    print(f"  WARNING: 'params' key not found in extraction_config for {scenario_name} during LLM override. Skipping override.")
            except json.JSONDecodeError:
                print(f"  WARNING: Could not decode extraction_config JSON for {scenario_name} during LLM override. Skipping override.")
            except Exception as e:
                print(f"  WARNING: Error during LLM override for {scenario_name}: {e}. Skipping override.")
        else:
            print(f"  WARNING: 'extraction_config' not found in params for {scenario_name} during LLM override. Skipping override.")
    
    # print(f"Effective Request Params: {json.dumps(current_params, indent=2)}") # Suppressed
    
    response_obj = None
    error_details_for_printing = [] # Used for UNEXPECTED FAIL and other errors

    try:
        # Use current_params for the request
        response_obj = requests.get(FETCH_ENDPOINT, params=current_params, stream=True, timeout=120)
        response_obj.raise_for_status()

        actual_request_outcome, result_data = process_sse_stream(response_obj, scenario_name)

        # --- REFINED LLM PASS/FAIL LOGIC START ---
        original_sse_outcome = actual_request_outcome
        final_outcome_for_comparison = actual_request_outcome # Default to SSE/HTTP outcome

        is_llm_test = False
        has_extracted_content = False # Initialize

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
            # Check for extracted content only if SSE was successful
            if actual_request_outcome and result_data and isinstance(result_data, dict):
                extracted_content_value = result_data.get('extracted_content', {}).get('content')
                if extracted_content_value: # True if non-empty string, non-None.
                    has_extracted_content = True
            
            if expected_to_pass: # Expected to pass
                if not actual_request_outcome:
                    # SSE/HTTP failed. final_outcome_for_comparison is already False. This is an UNEXPECTED FAIL.
                    pass # Handled by initial assignment
                elif not has_extracted_content:
                    # SSE/HTTP OK, but LLM test expected to pass did not produce content.
                    final_outcome_for_comparison = False # Mark as failed for comparison.
                    error_details_for_printing.append(
                        f"  Reason ({scenario_name}): LLM test expected to pass and extract content, but no LLM content found."
                    )
                # else: actual_request_outcome is True AND has_extracted_content is True. PASS (Expected).
            
            else: # Expected to fail (expected_to_pass is False)
                if not actual_request_outcome:
                    # SSE/HTTP failed. final_outcome_for_comparison is already False. FAIL (Expected).
                    pass # Handled by initial assignment
                elif actual_request_outcome and not has_extracted_content:
                    # SSE/HTTP OK, but LLM test expected to fail produced no content. This is an expected failure mode.
                    final_outcome_for_comparison = False # Mark as failed for comparison. FAIL (Expected).
                elif actual_request_outcome and has_extracted_content:
                    # SSE/HTTP OK, AND LLM content found, but test was expected to fail. UNEXPECTED PASS.
                    # final_outcome_for_comparison remains True from initial assignment.
                    pass
        
        adjusted_actual_request_outcome = final_outcome_for_comparison
        # --- REFINED LLM PASS/FAIL LOGIC END ---

        test_matches_expectation = (adjusted_actual_request_outcome == expected_to_pass)

        if test_matches_expectation:
            if adjusted_actual_request_outcome: # Passed and was expected to pass
                print(f"PASS (Expected): {scenario_name}")
            else: # Failed and was expected to fail
                print(f"FAIL (Expected): {scenario_name}")
                if is_llm_test and original_sse_outcome is True and adjusted_actual_request_outcome is False and not has_extracted_content:
                    # This case means: SSE stream was fine, but we (correctly) failed the test because
                    # an LLM test expected to fail did so by not extracting content.
                    print(f"  Reason: LLM extraction yielded no content, aligning with expected failure mode for LLM test.")
                elif result_data and isinstance(result_data, dict) and result_data.get("error_type"):
                    # This covers cases where process_sse_stream itself returned False (actual_request_outcome was False)
                    print(f"  Reason: SSE Error - {result_data.get('error_type')}")
                # HTTP errors leading to expected failure are handled by their except blocks.
        else: # Unexpected outcome
            if adjusted_actual_request_outcome: # Passed but was expected to fail (UNEXPECTED PASS)
                print(f"UNEXPECTED PASS: {scenario_name} (Was expected to fail)")
                if is_llm_test and has_extracted_content and not expected_to_pass: # expected_to_pass is False here
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
            else: # Failed but was expected to pass (UNEXPECTED FAIL)
                print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass)")
                # Populate error_details_for_printing for UNEXPECTED FAIL
                if result_data and isinstance(result_data, dict):
                    error_details_for_printing.extend(result_data.get("messages", []))
                    if not result_data.get("messages"): # Only add these if no specific SSE messages
                        if "last_data" in result_data and result_data["last_data"]:
                            error_details_for_printing.append(f"Last SSE Data: {json.dumps(result_data['last_data'], indent=1)}")
                        if "details_str" in result_data and result_data["details_str"]:
                            error_details_for_printing.append(f"Details: {result_data['details_str']}")
                elif result_data: # If result_data is not a dict but has some value
                    error_details_for_printing.append(str(result_data))
            
                if error_details_for_printing:
                    print(f"  Details for {scenario_name}:")
                    for line_detail in error_details_for_printing[:5]: # Limit to 5 lines for brevity for UNEXPECTED FAIL
                        print(f"    {line_detail}")
                else:
                    print(f"  Error: Unexpected outcome for {scenario_name}, but no specific error details captured from SSE processing.")
        
        return test_matches_expectation

    except requests.exceptions.HTTPError as http_err:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        error_details_for_printing = [f"HTTP error: {http_err}"] # Initialize/clear for this context
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
        error_details_for_printing = [f"Request exception: {req_err}"] # Initialize/clear for this context
        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - Request Exception")
            print(f"  Reason: {req_err}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Request Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: # Print all details for this exception type
                 print(f"    {line}")
        return test_matches_expectation

    except Exception as e:
        actual_request_outcome = False
        test_matches_expectation = (actual_request_outcome == expected_to_pass)
        import traceback
        tb_lines = traceback.format_exc().splitlines()
        error_details_for_printing = [f"An unexpected error occurred: {e}"] # Initialize/clear for this context
        error_details_for_printing.extend(tb_lines[:5])

        if test_matches_expectation:
            print(f"FAIL (Expected): {scenario_name} - Unexpected Exception")
            print(f"  Reason: {e}")
        else:
            print(f"UNEXPECTED FAIL: {scenario_name} (Was expected to pass) - Unexpected Exception")
            print(f"  Details for {scenario_name}:")
            for line in error_details_for_printing: # Print all details for this exception type
                print(f"    {line}")
        return test_matches_expectation

# --- Test Cases Definition ---
# Define test cases as a list of dictionaries.
# Each dictionary should have 'name', 'url', and 'params'.
TEST_CASES = [
    # --- Original Test Cases (adapted) ---
    {
        "name": "LLM Extraction Live Test (Original)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-70b-8192",
                    "llm_instruction": "Extract the main heading of the page."
                }
            })
        }
    },
    {
        "name": "Markdown Generator Default Live Test (Original)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default"
        }
    },
    {
        "name": "Markdown Generator None Specified Live Test (Original)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai"
            # No crawl4ai_markdown_generator parameter
        }
    },
    {
        "name": "Markdown Generator Unknown Live Test (Original)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "ThisIsAnUnknownGenerator"
        }
    },

    # --- New Test Cases for Advanced DefaultMarkdownGenerator Features ---

    # markdown_generator_options tests
    {
        "name": "Advanced MD: Valid Options (strip script, no autolinks)",
        "url": "https://www.w3schools.com/tags/tag_script.asp", # URL with script tags
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": json.dumps({"strip": ["script"], "autolinks": False})
        }
    },
    {
        "name": "Advanced MD: Empty Options JSON {}",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": json.dumps({})
        }
    },
    {
        "name": "Advanced MD: Invalid Options JSON (malformed)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": '{"strip": ["script"], "autolinks": false' # Missing closing brace
        }
    },
    {
        "name": "Advanced MD: Options not provided (should use defaults)",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default"
            # markdown_generator_options is omitted
        }
    },

    # markdown_content_source tests
    {
        "name": "Advanced MD: Content Source 'raw_html'",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_source": "raw_html"
        }
    },
    {
        "name": "Advanced MD: Content Source 'cleaned_html'",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_source": "cleaned_html"
        }
    },
    {
        "name": "Advanced MD: Content Source 'fit_html'",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_source": "fit_html"
        }
    },
    {
        "name": "Advanced MD: Invalid Content Source",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_source": "invalid_source_value" # Expect backend to handle/default
        }
    },

    # markdown_content_filter_config tests
    {
        "name": "Advanced MD: PruningFilter Valid Params",
        "url": "https://www.lipsum.com/", # URL with lots of text
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"threshold": 10, "min_length": 5, "target_selector": "p"} # Target paragraphs
            })
        }
    },
    {
        "name": "Advanced MD: PruningFilter Missing 'threshold' (expect default or error)",
        "url": "https://www.lipsum.com/",
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"min_length": 5} # threshold missing
            })
        }
    },
    {
        "name": "Advanced MD: PruningFilter Invalid Param Type for 'threshold'",
        "url": "https://www.lipsum.com/",
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"threshold": "not_an_int", "min_length": 5}
            })
        }
    },
    {
        "name": "Advanced MD: Unknown Filter Type",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_filter_config": json.dumps({
                "type": "UnknownFilterType",
                "params": {}
            })
        }
    },
    {
        "name": "Advanced MD: Malformed Filter JSON",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_content_filter_config": '{"type": "PruningContentFilter", "params": {"threshold": 10' # Malformed
        }
    },

    # Combination tests
    {
        "name": "Advanced MD: Combo - Options (strip all) & Source (raw_html)",
        "url": "https://www.w3schools.com/tags/tag_script.asp",
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": json.dumps({"strip": True, "autolinks": True}), # Strip all tags
            "markdown_content_source": "raw_html"
        }
    },
    {
        "name": "Advanced MD: Combo - Options (default) & PruningFilter",
        "url": "https://www.lipsum.com/",
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            # No markdown_generator_options (use defaults)
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"threshold": 20, "min_length": 10}
            })
        }
    },
    {
        "name": "Advanced MD: Combo - All three (Options, Source, Filter)",
        "url": "https://www.w3schools.com/html/html_paragraphs.asp", # Page with paragraphs and other elements
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": json.dumps({"strip": ["header", "footer"], "baseurl": True}),
            "markdown_content_source": "cleaned_html",
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"threshold": 5, "min_length": 3, "target_selector": "p"}
            })
        }
    },
    {
        "name": "Advanced MD: Combo - Invalid options JSON, valid source, valid filter",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "crawl4ai_markdown_generator": "Default",
            "markdown_generator_options": '{"strip": True, "autolinks": True', # Invalid JSON
            "markdown_content_source": "raw_html",
            "markdown_content_filter_config": json.dumps({
                "type": "PruningContentFilter",
                "params": {"threshold": 20, "min_length": 10}
            })
            # Expect backend to reject due to invalid options JSON or handle gracefully by ignoring options
        }
    }
,
    # --- LLM API Token Precedence Tests ---
    {
        "name": "LLMTokenPrecedence_RequestTokenOverridesEnv",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main title of this page.",
                    "llm_api_token": "VALID_REQUEST_TOKEN_PLACEHOLDER"
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "USER ACTION: Set GROQ_API_KEY to a DIFFERENT valid token. Replace 'VALID_REQUEST_TOKEN_PLACEHOLDER' with another valid Groq token."
    },
    {
        "name": "LLMTokenPrecedence_EnvTokenUsedWhenRequestTokenAbsent",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main title of this page."
                    # llm_api_token omitted
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "USER ACTION: Ensure GROQ_API_KEY environment variable is set to a VALID Groq token."
    },
    {
        "name": "LLMTokenPrecedence_InvalidRequestTokenCausesFailureDespiteValidEnvToken",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main title of this page.",
                    "llm_api_token": "INVALID_TOKEN_PLACEHOLDER"
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "USER ACTION: Set GROQ_API_KEY to a VALID Groq token. Replace 'INVALID_TOKEN_PLACEHOLDER' with an INVALID token string."
    },
    {
        "name": "LLMTokenPrecedence_NoRequestTokenAndNoOrInvalidEnvTokenCausesFailure",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main title of this page."
                    # llm_api_token omitted
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "USER ACTION: Ensure GROQ_API_KEY environment variable is EITHER NOT SET or IS SET to an INVALID token."
    },
    # --- New Test Cases for Advanced LLMExtractionStrategy Features ---

    # llm_extraction_type tests
    {
        "name": "LLMExtract_Type_Text_DefaultModel",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {"llm_extraction_type": "text"}
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test basic text extraction with default model. Ensure default LLM is configured."
    },
    {
        "name": "LLMExtract_Type_Text_SpecificModel",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the primary content as plain text."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test text extraction with a specific model (groq/llama3-8b-8192)."
    },
    {
        "name": "LLMExtract_Type_Markdown_DefaultModel",
        "url": "https://www.markdownguide.org/basic-syntax",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {"llm_extraction_type": "markdown"}
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test markdown extraction with default model. URL should have markdown-like content."
    },
    {
        "name": "LLMExtract_Type_Markdown_SpecificModel",
        "url": "https://www.markdownguide.org/cheat-sheet",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "markdown",
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Convert the main content of this page to well-formatted markdown."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test markdown extraction with a specific model."
    },
    {
        "name": "LLMExtract_Type_Json_DefaultModel_NoSchema",
        "url": "https://jsonplaceholder.typicode.com/todos/1",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract the user ID and title from the content."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test JSON extraction, default model, no schema. LLM should infer structure."
    },
    {
        "name": "LLMExtract_Type_Json_SpecificModel_WithSchema",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_provider_model": "groq/llama3-8b-8192",
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
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test JSON extraction with specific model and schema."
    },
    {
        "name": "LLMExtract_Type_Json_InvalidSchema",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract data.",
                    "llm_json_schema": {"type": "object", "properties": "this_is_not_valid_schema"}
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test JSON extraction with an invalid schema. Expect failure or error handling."
    },
    {
        "name": "LLMExtract_Type_Null_ShouldDefaultToText",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": None,
                    "llm_instruction": "Extract text content."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test null llm_extraction_type, should default to 'text'."
    },
    {
        "name": "LLMExtract_Type_Missing_ShouldDefaultToText",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_instruction": "Extract text content."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test missing llm_extraction_type, should default to 'text'."
    },
    {
        "name": "LLMExtract_Type_InvalidString_ShouldFailOrHandle",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {"llm_extraction_type": "not_a_valid_type"}
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test invalid string for llm_extraction_type. Expect failure or graceful error handling."
    },

    # llm_provider_model tests
    {
        "name": "LLMExtract_Model_InvalidNonExistent",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "nonexistent/model-v1"
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test with an invalid or non-existent LLM provider model. Expect failure."
    },

    # llm_instruction tests
    {
        "name": "LLMExtract_Instruction_NotProvided_ShouldUseDefault",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text"
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test with no llm_instruction provided. Backend should use a default instruction."
    },
    {
        "name": "LLMExtract_Instruction_EmptyString",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": ""
                }
            })
        },
        "expected_to_pass": True, 
        "setup_notes": "Test with an empty string for llm_instruction. Observe backend behavior (may use default or fail)."
    },

    # llm_json_schema tests (more specific)
    {
        "name": "LLMExtract_JsonSchema_Provided_But_Type_Not_Json",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text", 
                    "llm_instruction": "Extract text.",
                    "llm_json_schema": {"type": "object", "properties": {"key": {"type": "string"}}}
                }
            })
        },
        "expected_to_pass": True, 
        "setup_notes": "Test providing llm_json_schema when type is not 'json'. Schema should be ignored."
    },
    {
        "name": "LLMExtract_Json_NoSchema_ShouldUseGenericExtraction",
        "url": "https://jsonplaceholder.typicode.com/users/1",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_instruction": "Extract the name and email of the user."
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test JSON extraction without a schema. LLM should attempt generic JSON extraction based on instruction."
    },

    # llm_context_window_limit_override tests
    {
        "name": "LLMExtract_ContextWindowOverride_Valid",
        "url": "https://www.lipsum.com/",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Summarize this page briefly.",
                    "llm_context_window_limit_override": 2000
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test valid llm_context_window_limit_override."
    },
    {
        "name": "LLMExtract_ContextWindowOverride_InvalidType",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_context_window_limit_override": "not_an_integer"
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test invalid type for llm_context_window_limit_override. Expect failure."
    },
    {
        "name": "LLMExtract_ContextWindowOverride_Zero",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_context_window_limit_override": 0
                }
            })
        },
        "expected_to_pass": False, 
        "setup_notes": "Test zero for llm_context_window_limit_override. Expect failure or default behavior."
    },

    # llm_max_tokens_override tests
    {
        "name": "LLMExtract_MaxTokensOverride_Valid",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_instruction": "Provide a very short summary.",
                    "llm_max_tokens_override": 50
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test valid llm_max_tokens_override. Extracted content should be short."
    },
    {
        "name": "LLMExtract_MaxTokensOverride_InvalidType",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_max_tokens_override": "not_an_integer"
                }
            })
        },
        "expected_to_pass": False,
        "setup_notes": "Test invalid type for llm_max_tokens_override. Expect failure."
    },
    {
        "name": "LLMExtract_MaxTokensOverride_Zero",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_max_tokens_override": 0
                }
            })
        },
        "expected_to_pass": False, 
        "setup_notes": "Test zero for llm_max_tokens_override. Expect failure or default behavior."
    },

    # Combination and Edge Cases
    {
        "name": "LLMExtract_Combination_AllParams_Text",
        "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main topic from this document.",
                    "llm_context_window_limit_override": 3000,
                    "llm_max_tokens_override": 100
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test combination of all relevant parameters for text extraction."
    },
    {
        "name": "LLMExtract_Combination_AllParams_Json_WithSchema",
        "url": "https://jsonplaceholder.typicode.com/comments/1",
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "json",
                    "llm_provider_model": "groq/llama3-8b-8192",
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
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test combination of all relevant parameters for JSON extraction with schema."
    },
    {
        "name": "LLMExtract_MinimalParams_Text_ShouldUseDefaults",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {} 
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test with minimal LLM params, relying heavily on backend defaults (type=text, default model, default instruction)."
    },
    {
        "name": "LLMExtract_ContentTooLargeForDefaultContext_NoOverride",
        "url": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm", 
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "groq/llama3-8b-8192", 
                    "llm_instruction": "What is the primary theme of this text? Respond in one sentence."
                }
            })
        },
        "expected_to_pass": True, 
        "setup_notes": "Test with content potentially larger than default context window of the model. Observe truncation or error. Model has 8k context, page is large."
    },
    {
        "name": "LLMExtract_ContentTooLarge_WithSufficientContextOverride",
        "url": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm", 
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_extraction_type": "text",
                    "llm_provider_model": "groq/llama3-70b-8192", 
                    "llm_instruction": "Extract the names of the first three characters mentioned.",
                    "llm_context_window_limit_override": 8000 
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "Test with large content and a sufficient context window override."
    },
    {
        "name": "LLMExtract_ValidRequestTokenInExtractionConfig",
        "url": DEFAULT_TEST_URL,
        "params": {
            "engine": "crawl4ai",
            "extraction_config": json.dumps({
                "strategy": "LLMExtractionStrategy",
                "params": {
                    "llm_provider_model": "groq/llama3-8b-8192",
                    "llm_instruction": "Extract the main title.",
                    "llm_api_token": "VALID_GROQ_TOKEN_FOR_TESTING_CONFIG_PARAM" 
                }
            })
        },
        "expected_to_pass": True,
        "setup_notes": "USER ACTION: Replace 'VALID_GROQ_TOKEN_FOR_TESTING_CONFIG_PARAM' with a valid Groq token."
    }
]

# --- Test Scenarios (Old functions to be removed/replaced by TEST_CASES loop) ---

# def test_llm_extraction_live(): # Will be removed
# ... (rest of old test functions also to be removed)

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting all live tests...")
    # print(f"Targeting Backend: {BASE_URL}") # Suppressed for conciseness

    # time.sleep(1) # Optional delay

    passed_count = 0
    failed_count = 0
    skipped_count = 0 # New counter for skipped tests

    for test_case in TEST_CASES:
        if ONLY_RUN_LLM_TOKEN_PRECEDENCE_TESTS and test_case["name"] not in LLM_TOKEN_PRECEDENCE_TEST_NAMES:
            # Also skip the new LLM Extraction Strategy tests if this flag is True,
            # unless we explicitly want to run them. For now, assume they are skipped if this flag is True.
            # To run them, one would need to add their names to LLM_TOKEN_PRECEDENCE_TEST_NAMES or set the flag to False.
            if not test_case["name"].startswith("LLMExtract_") and test_case["name"] not in LLM_TOKEN_PRECEDENCE_TEST_NAMES: # Ensure LLM token tests are not accidentally skipped by this logic
                # print(f"Skipping {test_case['name']} due to ONLY_RUN_LLM_TOKEN_PRECEDENCE_TESTS=True and not in LLM_TOKEN_PRECEDENCE_TEST_NAMES or LLMExtract_ prefix") # Optional debug
                continue
        
        if SKIP_KNOWN_RATE_LIMIT_SENSITIVE_TESTS and test_case["name"] in KNOWN_RATE_LIMIT_SENSITIVE_TEST_NAMES:
            print(f"SKIPPING (Rate Limit Sensitive): {test_case['name']}")
            skipped_count += 1
            continue

        # Default expected_to_pass to True if not specified, for backward compatibility with older tests
        # However, all new tests (LLM token precedence) explicitly define it.
        expected_to_pass_value = test_case.get("expected_to_pass", True)
        
        # Print setup notes if available
        if "setup_notes" in test_case and test_case["setup_notes"]:
            print(f"\nINFO for {test_case['name']}: {test_case['setup_notes']}")

        overall_test_success = run_single_test_case(
            scenario_name=test_case["name"],
            url=test_case["url"],
            params=test_case["params"],
            expected_to_pass=expected_to_pass_value,
            token_test_llm_override=test_case.get("token_test_llm_override") # New argument
        )
        if overall_test_success: # This now means the outcome matched the expectation
            passed_count += 1
        else:
            failed_count += 1
        
        time.sleep(0.1) # Reduced delay

    print("\nAll live tests finished.")
    print(f"Passed: {passed_count}, Failed: {failed_count}, Skipped: {skipped_count}.")

# Commenting out old test functions as they are now covered by the TEST_CASES loop
# # def test_llm_extraction_live():
# #     """
# #     Tests Scenario 1 (Section 4.4 - LLM Extraction).
# #     """
# #     scenario_name = "LLM Extraction Live Test"
#     """
#     Tests Scenario 1 (Section 4.4 - LLM Extraction).
#     """
#     # scenario_name = "LLM Extraction Live Test" # Duplicated
#     # print(f"\n--- Starting: {scenario_name} ---")
#
#     # extraction_config_dict = {
#     #     "strategy": "LLMExtractionStrategy",
#     #     "params": {
#     #         "llm_provider_model": "groq/llama3-70b-8192",
#     #         "llm_instruction": "Extract the main heading of the page."
#     #         # Ensure no "llm_api_token" key is here
#     #     }
#     # }
#     # params = {
#     #     "url": DEFAULT_TEST_URL,
#     #     "engine": "crawl4ai",
#     #     "extraction_config": json.dumps(extraction_config_dict)
#     # }
#
#     # try:
#     #     response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
#     #     response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#
#     #     completed_successfully, data = process_sse_stream(response, scenario_name)
#
#     #     if completed_successfully:
#     #         # Further checks specific to LLM extraction can be added here if needed
#     #         # For now, just checking completion is sufficient as per requirements
#     #         print(f"PASS: {scenario_name}")
#     #     else:
#     #         print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
#     #         if data:
#     #             print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
#     # except requests.exceptions.HTTPError as http_err:
#     #     print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
#     #     if response is not None:
#     #         print(f"Response content: {response.text}")
#     # except requests.exceptions.RequestException as req_err:
#     #     print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
#     # except Exception as e:
#     #     print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_default_live():
# #     """
# #     Tests Scenario 2 (Section 4.6 - Default Markdown Generator).
# #     """
# #     scenario_name = "Markdown Generator Default Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai",
# #         "crawl4ai_markdown_generator": "Default"
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status()
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             if data and "content" in data and data["content"]:
# #                 print(f"PASS: {scenario_name}")
# #                 # print(f"Sample Content (first 100 chars): {data['content'][:100]}") # Optional: print sample
# #             elif data and "content" in data and not data["content"]:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' in final event is empty.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #             else:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' key missing in final event or data is null.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_none_live():
# #     """
# #     Tests Scenario 3 (Section 4.6 - No Markdown Generator Specified).
# #     """
# #     scenario_name = "Markdown Generator None Specified Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai"
# #         # No crawl4ai_markdown_generator parameter
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status()
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             # Assuming crawl4ai defaults to some markdown generation if not specified
# #             if data and "content" in data: # Content might be empty if default is no content, or non-empty
# #                 print(f"PASS: {scenario_name} (Content presence: {'non-empty' if data['content'] else 'empty/null'})")
# #                 # print(f"Sample Content (first 100 chars): {str(data['content'])[:100]}") # Optional
# #             else:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' key missing in final event or data is null.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_unknown_live():
# #     """
# #     Tests Scenario 4 (Section 4.6 - Unknown Markdown Generator).
# #     """
# #     scenario_name = "Markdown Generator Unknown Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai",
# #         "crawl4ai_markdown_generator": "ThisIsAnUnknownGenerator"
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status() # Expecting 200 OK, backend should handle gracefully
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             # Backend should handle unknown generator gracefully, possibly defaulting.
# #             # The fetch itself should complete.
# #             print(f"PASS: {scenario_name} (Backend handled unknown generator, fetch completed)")
# #             if data and "content" in data:
# #                  print(f"Content presence: {'non-empty' if data['content'] else 'empty/null'}")
# #                 # print(f"Sample Content (first 100 chars): {str(data['content'])[:100]}") # Optional
# #             else:
# #                 print(f"INFO: {scenario_name} - 'content' key missing or data is null in final event, which might be expected if default is no content.")
# #                 if data:
# #                     print(f"Final event data: {json.dumps(data, indent=2)}")
#
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # This block seems to be a duplicate of the first old test function (test_llm_extraction_live)
# # and should also be commented out.
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     extraction_config_dict = {
# #         "strategy": "LLMExtractionStrategy",
# #         "params": {
# #             "llm_provider_model": "groq/llama3-70b-8192",
# #             "llm_instruction": "Extract the main heading of the page."
# #             # Ensure no "llm_api_token" key is here
# #         }
# #     }
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai",
# #         "extraction_config": json.dumps(extraction_config_dict)
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             # Further checks specific to LLM extraction can be added here if needed
# #             # For now, just checking completion is sufficient as per requirements
# #             print(f"PASS: {scenario_name}")
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_default_live(): # Already commented above
# #     """
# #     Tests Scenario 2 (Section 4.6 - Default Markdown Generator).
# #     """
# #     scenario_name = "Markdown Generator Default Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai",
# #         "crawl4ai_markdown_generator": "Default"
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status()
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             if data and "content" in data and data["content"]:
# #                 print(f"PASS: {scenario_name}")
# #                 # print(f"Sample Content (first 100 chars): {data['content'][:100]}") # Optional: print sample
# #             elif data and "content" in data and not data["content"]:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' in final event is empty.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #             else:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' key missing in final event or data is null.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_none_live(): # Already commented above
# #     """
# #     Tests Scenario 3 (Section 4.6 - No Markdown Generator Specified).
# #     """
# #     scenario_name = "Markdown Generator None Specified Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai"
# #         # No crawl4ai_markdown_generator parameter
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status()
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             # Assuming crawl4ai defaults to some markdown generation if not specified
# #             if data and "content" in data: # Content might be empty if default is no content, or non-empty
# #                 print(f"PASS: {scenario_name} (Content presence: {'non-empty' if data['content'] else 'empty/null'})")
# #                 # print(f"Sample Content (first 100 chars): {str(data['content'])[:100]}") # Optional
# #             else:
# #                 print(f"FAIL: {scenario_name} - SSE stream completed, but 'content' key missing in final event or data is null.")
# #                 print(f"Final event data: {json.dumps(data, indent=2)}")
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")
#
# # def test_markdown_generator_unknown_live(): # Already commented above
# #     """
# #     Tests Scenario 4 (Section 4.6 - Unknown Markdown Generator).
# #     """
# #     scenario_name = "Markdown Generator Unknown Live Test"
# #     print(f"\n--- Starting: {scenario_name} ---")
#
# #     params = {
# #         "url": DEFAULT_TEST_URL,
# #         "engine": "crawl4ai",
# #         "crawl4ai_markdown_generator": "ThisIsAnUnknownGenerator"
# #     }
#
# #     try:
# #         response = requests.get(FETCH_ENDPOINT, params=params, stream=True, timeout=60)
# #         response.raise_for_status() # Expecting 200 OK, backend should handle gracefully
#
# #         completed_successfully, data = process_sse_stream(response, scenario_name)
#
# #         if completed_successfully:
# #             # Backend should handle unknown generator gracefully, possibly defaulting.
# #             # The fetch itself should complete.
# #             print(f"PASS: {scenario_name} (Backend handled unknown generator, fetch completed)")
# #             if data and "content" in data:
# #                  print(f"Content presence: {'non-empty' if data['content'] else 'empty/null'}")
# #                 # print(f"Sample Content (first 100 chars): {str(data['content'])[:100]}") # Optional
# #             else:
# #                 print(f"INFO: {scenario_name} - 'content' key missing or data is null in final event, which might be expected if default is no content.")
# #                 if data:
# #                     print(f"Final event data: {json.dumps(data, indent=2)}")
#
# #         else:
# #             print(f"FAIL: {scenario_name} - SSE stream did not complete successfully or an error occurred.")
# #             if data:
# #                 print(f"Last/Error data: {json.dumps(data, indent=2)}")
#
# #     except requests.exceptions.HTTPError as http_err:
# #         print(f"FAIL: {scenario_name} - HTTP error occurred: {http_err}")
# #         if response is not None:
# #             print(f"Response content: {response.text}")
# #     except requests.exceptions.RequestException as req_err:
# #         print(f"FAIL: {scenario_name} - Request exception occurred: {req_err}")
# #     except Exception as e:
# #         print(f"FAIL: {scenario_name} - An unexpected error occurred: {e}")