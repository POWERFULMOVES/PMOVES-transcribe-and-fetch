@echo off
echo PMOVES Transcription Format Fix Script
echo ===================================
echo.
echo This script will apply fixes to resolve the JSON parsing errors
echo in the transcription output.
echo.
echo Creating utils directory if it doesn't exist...
if not exist "..\src\utils" mkdir "..\src\utils"

echo.
echo Copying transcription_handler.js to utils directory...
copy /Y "transcription_handler.js" "..\src\utils\"

echo.
echo Creating backup of transcribe1.py...
copy /Y "..\backend\app\transcribe1.py" "..\backend\app\transcribe1.py.backup"

echo.
echo Copying fixed reducer...
copy /Y "transcriptionReducer.fixed.js" "..\src\app\reducers\transcriptionReducer.js.fixed"

echo.
echo Fixes have been deployed successfully!
echo.
echo Now you need to:
echo 1. Manually edit the backend/app/transcribe1.py file to update the transcription
echo    format as described in fix_transcription_format.py
echo 2. Manually update src/app/page.js to use the new transcription handler
echo    (reference the page.js.patch for guidance)
echo 3. Consider replacing src/app/reducers/transcriptionReducer.js with 
echo    transcriptionReducer.js.fixed if you want the full fix
echo.
echo NOTE: If you want to test the fixes before applying them to your main files,
echo       you can create a test branch in your Git repository.
echo.
pause
