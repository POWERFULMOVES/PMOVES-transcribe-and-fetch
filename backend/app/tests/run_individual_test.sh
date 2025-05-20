#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <test_file.py> [output.md]"
  exit 1
fi

TEST_FILE="$1"
OUTPUT_FILE="$2"

if [ -z "$OUTPUT_FILE" ]; then
  # Just run and print
  echo -e "\n## $TEST_FILE\n"
  pytest "$TEST_FILE"
else
  # Append to markdown
  echo -e "\n## $TEST_FILE\n" | tee -a "$OUTPUT_FILE"
  echo -e '\n```' >> "$OUTPUT_FILE"
  pytest "$TEST_FILE" | tee -a "$OUTPUT_FILE"
  echo -e '\n```' >> "$OUTPUT_FILE"
  echo "Finished $TEST_FILE (output appended to $OUTPUT_FILE)"
fi 