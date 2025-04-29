import os
import sys
import subprocess
import time
import requests
import json
from urllib.parse import urljoin

def test_sse_cors_fix():
    """
    Test the CORS fix for SSE endpoints by:
    1. Running the fix script
    2. Restarting the backend server
    3. Testing the SSE endpoint with CORS headers
    """
    print("Testing SSE CORS fix...")
    
    # Step 1: Run the fix script
    print("\n1. Applying CORS fix...")
    try:
        from fix_sse_cors import fix_sse_cors
        fix_sse_cors()
        print("✅ CORS fix applied successfully")
    except Exception as e:
        print(f"❌ Error applying CORS fix: {str(e)}")
        return False
    
    # Step 2: Check if the backend server is running
    print("\n2. Checking if backend server is running...")
    backend_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(backend_url, timeout=2)
        if response.status_code == 200:
            print("✅ Backend server is already running")
        else:
            print(f"❌ Backend server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running. Please start it with:")
        print("venv\\Scripts\\activate && cd backend && uvicorn app.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error checking backend server: {str(e)}")
        return False
    
    # Step 3: Test OPTIONS request to the SSE endpoint
    print("\n3. Testing OPTIONS request to SSE endpoint...")
    sse_url = urljoin(backend_url, "/combined-updates")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        options_response = requests.options(sse_url, headers=headers, timeout=5)
        print(f"Status code: {options_response.status_code}")
        print("Response headers:")
        for key, value in options_response.headers.items():
            if key.lower().startswith("access-control"):
                print(f"  {key}: {value}")
        
        # Check for CORS headers
        if "Access-Control-Allow-Origin" in options_response.headers:
            print("✅ CORS headers are present in OPTIONS response")
        else:
            print("❌ CORS headers are missing in OPTIONS response")
            return False
    except Exception as e:
        print(f"❌ Error testing OPTIONS request: {str(e)}")
        return False
    
    # Step 4: Test GET request to the SSE endpoint
    print("\n4. Testing GET request to SSE endpoint (checking headers only)...")
    headers = {
        "Origin": "http://localhost:3000",
        "Accept": "text/event-stream"
    }
    
    try:
        # We're not going to read the SSE stream, just check the headers
        session = requests.Session()
        response = session.get(
            sse_url, 
            headers=headers, 
            stream=True, 
            timeout=5
        )
        
        print(f"Status code: {response.status_code}")
        print("Response headers:")
        for key, value in response.headers.items():
            if key.lower().startswith("access-control"):
                print(f"  {key}: {value}")
        
        # Check for CORS headers
        if "Access-Control-Allow-Origin" in response.headers:
            print("✅ CORS headers are present in GET response")
        else:
            print("❌ CORS headers are missing in GET response")
            return False
        
        # Close the connection
        response.close()
    except Exception as e:
        print(f"❌ Error testing GET request: {str(e)}")
        return False
    
    print("\n✅ All tests passed! The CORS fix appears to be working correctly.")
    print("You should now be able to connect to the SSE endpoint from the frontend without CORS errors.")
    return True

if __name__ == "__main__":
    test_sse_cors_fix()
