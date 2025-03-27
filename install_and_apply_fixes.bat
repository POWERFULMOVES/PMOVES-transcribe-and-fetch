@echo off
REM install_and_apply_fixes.bat - Install dependencies and apply SSE fixes for Windows

echo === PMOVES SSE Fixes Installation Script ===
echo This script will install dependencies and apply fixes to the SSE implementation.

REM Check if we're in the correct directory
if not exist "package.json" (
  echo Error: This script must be run from the project root directory.
  exit /b 1
)

REM Install dependencies
echo.
echo === Installing dependencies ===
call npm install eventsource axios

REM Create test_output directory if it doesn't exist
echo.
echo === Creating test_output directory ===
if not exist "test_output" mkdir test_output

REM Apply fixes
echo.
echo === Applying fixes ===

REM Check if the fixes have already been applied to simple_sse_test.js
findstr /c:"data.startsWith('data: ')" simple_sse_test.js >nul 2>&1
if %errorlevel% equ 0 (
  echo Fixes already applied to simple_sse_test.js
) else (
  echo Creating simple_sse_test.js
  echo /**> simple_sse_test.js
  echo  * simple_sse_test.js - Simple test for SSE connection>> simple_sse_test.js
  echo  */>> simple_sse_test.js
  echo.>> simple_sse_test.js
  echo // Import the EventSource constructor from the eventsource package>> simple_sse_test.js
  echo const EventSource = require('eventsource').EventSource;>> simple_sse_test.js
  echo const axios = require('axios');>> simple_sse_test.js
  echo.>> simple_sse_test.js
  echo // Configuration>> simple_sse_test.js
  echo const BACKEND_URL = 'http://localhost:8000';>> simple_sse_test.js
  echo const SSE_ENDPOINT = '/combined-updates';>> simple_sse_test.js
  echo.>> simple_sse_test.js
  echo console.log('=== Simple SSE Test ===');>> simple_sse_test.js
  echo console.log('Checking backend health...');>> simple_sse_test.js
  echo.>> simple_sse_test.js
  echo // Check backend health>> simple_sse_test.js
  echo axios.get(`${BACKEND_URL}/health`)>> simple_sse_test.js
  echo   .then(response =^> {>> simple_sse_test.js
  echo     console.log('Backend health check response:', response.data);>> simple_sse_test.js
  echo     >> simple_sse_test.js
  echo     if (response.data.status === 'healthy') {>> simple_sse_test.js
  echo       console.log('✅ Backend is healthy');>> simple_sse_test.js
  echo       testSSE();>> simple_sse_test.js
  echo     } else {>> simple_sse_test.js
  echo       console.warn('⚠️ Backend health check returned unexpected status:', response.data.status);>> simple_sse_test.js
  echo     }>> simple_sse_test.js
  echo   })>> simple_sse_test.js
  echo   .catch(error =^> {>> simple_sse_test.js
  echo     console.error('❌ Backend health check failed:', error.message);>> simple_sse_test.js
  echo   });>> simple_sse_test.js
  echo.>> simple_sse_test.js
  echo // Test SSE connection>> simple_sse_test.js
  echo function testSSE() {>> simple_sse_test.js
  echo   console.log('Testing SSE connection...');>> simple_sse_test.js
  echo   console.log('Creating EventSource...');>> simple_sse_test.js
  echo   >> simple_sse_test.js
  echo   try {>> simple_sse_test.js
  echo     // Log the EventSource constructor>> simple_sse_test.js
  echo     console.log('EventSource constructor:', EventSource);>> simple_sse_test.js
  echo     >> simple_sse_test.js
  echo     // Create the EventSource>> simple_sse_test.js
  echo     const es = new EventSource(`${BACKEND_URL}${SSE_ENDPOINT}`);>> simple_sse_test.js
  echo     console.log('EventSource created:', es);>> simple_sse_test.js
  echo     >> simple_sse_test.js
  echo     // Set up event handlers>> simple_sse_test.js
  echo     es.onopen = () =^> {>> simple_sse_test.js
  echo       console.log('✅ SSE connection established');>> simple_sse_test.js
  echo       >> simple_sse_test.js
  echo       // Close the connection after 5 seconds>> simple_sse_test.js
  echo       setTimeout(() =^> {>> simple_sse_test.js
  echo         console.log('Closing SSE connection...');>> simple_sse_test.js
  echo         es.close();>> simple_sse_test.js
  echo         console.log('SSE connection closed');>> simple_sse_test.js
  echo       }, 5000);>> simple_sse_test.js
  echo     };>> simple_sse_test.js
  echo     >> simple_sse_test.js
  echo     es.onmessage = (event) =^> {>> simple_sse_test.js
  echo       console.log('Received SSE message:', event.data);>> simple_sse_test.js
  echo       try {>> simple_sse_test.js
  echo         // Remove the "data: " prefix if it exists>> simple_sse_test.js
  echo         const jsonStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;>> simple_sse_test.js
  echo         const data = JSON.parse(jsonStr);>> simple_sse_test.js
  echo         console.log('Parsed message:', data);>> simple_sse_test.js
  echo       } catch (error) {>> simple_sse_test.js
  echo         console.warn('Could not parse message as JSON:', error);>> simple_sse_test.js
  echo       }>> simple_sse_test.js
  echo     };>> simple_sse_test.js
  echo     >> simple_sse_test.js
  echo     es.onerror = (error) =^> {>> simple_sse_test.js
  echo       console.error('SSE connection error:', error);>> simple_sse_test.js
  echo     };>> simple_sse_test.js
  echo   } catch (error) {>> simple_sse_test.js
  echo     console.error('Error creating EventSource:', error);>> simple_sse_test.js
  echo   }>> simple_sse_test.js
  echo }>> simple_sse_test.js
  echo Created simple_sse_test.js
)

REM Check if the fixes have already been applied to test_sse_implementation.js
findstr /c:"data.startsWith('data: ')" test_sse_implementation.js >nul 2>&1
if %errorlevel% equ 0 (
  echo Fixes already applied to test_sse_implementation.js
) else (
  echo Updating test_sse_implementation.js
  call node fix_sse_frontend.js
  echo Updated test_sse_implementation.js
)

echo.
echo === SSE fixes applied successfully! ===
echo.
echo You can now run the following commands to test the fixes:
echo.
echo   node simple_sse_test.js
echo   node test_sse_implementation.js
echo.
echo Note: Make sure the backend server is running before running these tests.
echo.

pause
