#!/bin/bash

# Output markdown file
OUTPUT_FILE="test_results.md"

# List of test files
TEST_FILES=(
  "test_crawl4ai_fetcher_deep_strategies.py"
  "test_crawl4ai_fetcher_extraction_strategies.py"
  "test_crawl4ai_fetcher_general_options.py"
  "test_crawl4ai_fetcher_llmconfig.py"
  "test_crawl4ai_fetcher_markdown_config.py"
  "test_fetch_history_saving.py"
  "test_search_config.py"
)

# Remove previous output file if exists
rm -f "$OUTPUT_FILE"

echo "# Test Results" >> "$OUTPUT_FILE"

for TEST_FILE in "${TEST_FILES[@]}"; do
  echo "\n## $TEST_FILE\n" | tee -a "$OUTPUT_FILE"
  echo '\n```' >> "$OUTPUT_FILE"
  pytest "$TEST_FILE" | tee -a "$OUTPUT_FILE"
  echo '\n```' >> "$OUTPUT_FILE"
  echo "Finished $TEST_FILE"
done

echo "\nAll tests complete. Results saved to $OUTPUT_FILE." 