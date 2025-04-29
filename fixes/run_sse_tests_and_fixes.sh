#!/bin/bash

# Make the script executable
chmod +x test_sse_backend.sh

# Function to display the menu
display_menu() {
  echo "==================================="
  echo "SSE Tests and Fixes Runner"
  echo "==================================="
  echo
  echo "Choose an option:"
  echo "1. Run SSE tests"
  echo "2. Apply SSE fixes"
  echo "3. Run tests and apply fixes"
  echo "4. Exit"
  echo
  read -p "Enter your choice (1-4): " choice
  echo
  
  case $choice in
    1) run_tests ;;
    2) apply_fixes ;;
    3) run_both ;;
    4) exit 0 ;;
    *) 
      echo "Invalid choice. Please try again."
      echo
      display_menu
      ;;
  esac
}

# Function to run the tests
run_tests() {
  echo "==================================="
  echo "Running SSE tests..."
  echo "==================================="
  echo
  echo "This will check if your backend is running and open test windows."
  echo "If your backend is already running, you can confirm when prompted."
  echo
  node run_sse_tests.js
  echo
  echo "Tests started in separate terminal windows."
  echo
  read -p "Press Enter to continue..."
  display_menu
}

# Function to apply the fixes
apply_fixes() {
  echo "==================================="
  echo "Applying SSE fixes..."
  echo "==================================="
  echo
  node apply_sse_fixes.js
  echo
  read -p "Press Enter to continue..."
  display_menu
}

# Function to run both tests and fixes
run_both() {
  echo "==================================="
  echo "Running SSE tests..."
  echo "==================================="
  echo
  node run_sse_tests.js
  echo
  echo "Tests started in separate terminal windows."
  echo
  read -p "Press Enter when you're ready to apply the fixes..."
  echo
  echo "==================================="
  echo "Applying SSE fixes..."
  echo "==================================="
  echo
  node apply_sse_fixes.js
  echo
  read -p "Press Enter to continue..."
  display_menu
}

# Start the menu
display_menu
