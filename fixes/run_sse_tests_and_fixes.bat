@echo off
echo ===================================
echo SSE Tests and Fixes Runner
echo ===================================
echo.

:menu
echo Choose an option:
echo 1. Run SSE tests
echo 2. Apply SSE fixes
echo 3. Run tests and apply fixes
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto run_tests
if "%choice%"=="2" goto apply_fixes
if "%choice%"=="3" goto run_both
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:run_tests
echo.
echo ===================================
echo Running SSE tests...
echo ===================================
echo.
echo This will check if your backend is running and open test windows.
echo If your backend is already running, you can confirm when prompted.
echo.
node run_sse_tests.js
echo.
echo Tests started in separate terminal windows.
echo.
pause
goto menu

:apply_fixes
echo.
echo ===================================
echo Applying SSE fixes...
echo ===================================
echo.
node apply_sse_fixes.js
echo.
pause
goto menu

:run_both
echo.
echo ===================================
echo Running SSE tests...
echo ===================================
echo.
node run_sse_tests.js
echo.
echo Tests started in separate terminal windows.
echo.
echo Press any key when you're ready to apply the fixes...
pause
echo.
echo ===================================
echo Applying SSE fixes...
echo ===================================
echo.
node apply_sse_fixes.js
echo.
pause
goto menu

:end
echo.
echo Exiting...
exit /b 0
