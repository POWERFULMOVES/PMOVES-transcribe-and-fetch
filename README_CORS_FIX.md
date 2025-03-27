# CORS Fix for SSE Connections

This repository contains scripts to fix CORS (Cross-Origin Resource Sharing) issues with Server-Sent Events (SSE) connections in the PMOVES transcription backend.

## Problem

The application is experiencing CORS errors when trying to establish SSE connections from the frontend to the backend. The main issues are:

1. Using wildcard origin (`"*"`) with `allow_credentials=True` in CORS middleware, which is not allowed by browsers
2. Using a fixed origin instead of the actual request origin in SSE endpoint CORS headers

## Solution

The fix involves:

1. Replacing wildcard origin (`"*"`) with specific origins (`["http://localhost:3000", "http://127.0.0.1:3000"]`) in CORS middleware
2. Using the actual request origin instead of a fixed origin in SSE endpoint CORS headers
3. Ensuring the `origin` variable is properly defined before it's used

## Scripts

- `test_fix_sse_cors.py`: Tests the CORS fix without modifying the actual file
- `fix_sse_cors.py`: Applies the CORS fix to the backend/app/main.py file

## Usage

### Testing the Fix

Run the test script to see what changes would be made without modifying the file:

```bash
python test_fix_sse_cors.py
```

This will show you a diff of the changes that would be made.

### Applying the Fix

Run the fix script to apply the changes to the backend/app/main.py file:

```bash
python fix_sse_cors.py
```

This will:
1. Create a backup of the original file at `backend/app/main.py.bak.cors_fix`
2. Apply the CORS fixes to the file
3. Print a summary of the changes made

### Verifying the Fix

After applying the fix, you can:

1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend development server and test the SSE connection

## Notes

- The fix assumes the backend is running on port 8000 and the frontend on port 3000
- If you're using different ports or domains, you'll need to modify the allowed origins in the fix script
- A backup of the original file is created before making any changes, so you can always revert if needed
