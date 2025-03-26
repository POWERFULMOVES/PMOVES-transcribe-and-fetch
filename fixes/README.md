# PMOVES Transcription Format Fix

This guide provides a solution to fix the JSON parsing errors in the PMOVES transcription system. The issue occurs when the backend sends improperly formatted data to the frontend through Server-Sent Events (SSE).

## The Problem

When running transcriptions, you're seeing errors like:

```
00:00.00[00:04.92](https://www.youtube.com/watch?v=eMa43IfcuVY&t=4) Hi, welcome to another video.↗
00:00.00[00:07.87](https://www.youtube.com/watch?v=eMa43IfcuVY&t=7) So, Klein has gotten a pretty significant update↗
```

This is happening because:

1. The backend is sending transcription segments in a non-standard format (markdown-style table rows)
2. The frontend is expecting properly structured JSON objects
3. When the frontend tries to parse this data, it results in JSON parsing errors

## The Solution

This fix package includes several components:

1. **`transcription_handler.js`**: A utility that properly parses and processes transcription data, even when it's in the incorrect format
2. **`transcriptionReducer.fixed.js`**: An enhanced reducer that handles different data formats
3. **`fix_transcription_format.py`**: Guidelines for updating the backend code
4. **Patch files**: For updating specific parts of your codebase

## Implementation Steps

### 1. Setup

Run the `apply_fixes.bat` script to copy the utility files to the correct directories and create backups of your original files.

### 2. Fix the Backend (Python)

Edit `backend/app/transcribe1.py`:

1. Find the `transcribe_audio` function
2. Locate this code:

```python
# Send transcription segment immediately for real-time updates
await transcription_queue.put(json.dumps({
    "type": "transcription_segment",
    "content": f"| [{start_time}]({watch_url}) | {video_id} | {idx} | {start_time} | {end_time} | {segment_text} |"
}))
```

3. Replace it with:

```python
# Send transcription segment with proper JSON structure
await transcription_queue.put(json.dumps({
    "type": "transcription_segment",
    "content": {
        "text": segment_text,
        "start_time": segment.start,
        "end_time": segment.end,
        "id": idx,
        "video_id": video_id,
        "watch_url": watch_url,
        "timestamp": start_time
    }
}))
```

4. Find a similar code pattern in the `process_audio_with_groq` function and update it using the same approach.

### 3. Fix the Frontend (JavaScript)

1. Copy `transcription_handler.js` to the `src/utils` directory (done by the setup script)

2. Update `src/app/page.js`:
   - Add the import at the top: `import { parseTranscriptionSegment } from '../utils/transcription_handler';`
   - Modify the SSE message handling code to use the new parsing utility (reference `page.js.patch`)
   - Handle JSON parsing errors gracefully with the `errorCount` tracking

3. Replace or modify the reducer:
   - Either replace `src/app/reducers/transcriptionReducer.js` with `transcriptionReducer.fixed.js`
   - Or add the `PROCESS_SSE_EVENT` action and handling to your existing reducer

### 4. Optional: Add Error Recovery

If you want more robust error handling for existing transcriptions, add these to your codebase:

1. Add the error count tracking in the SSE connection setup
2. Implement reconnection logic when too many errors occur
3. Add the recovery attempts for malformed data as shown in the patch files

## Testing the Fix

After applying these changes:

1. Start your backend: `cd backend/app && uvicorn main:app --reload`
2. Start your frontend: `npm run dev`
3. Try processing a video and observe the live transcription

You should no longer see JSON parsing errors, and the transcription segments should appear correctly in the UI.

## Backward Compatibility

The fixes are designed to be backward compatible:

- The `transcription_handler.js` utility can parse both the old and new formats
- The updated reducer can handle both formats without modifying your database
- Existing transcriptions in your system will still work with the new code

## Troubleshooting

If you still experience issues after applying the fixes:

1. **Check the browser console for errors** - Look for any remaining JSON parsing issues
2. **Verify the SSE connection** - Make sure the server and client are communicating properly
3. **Inspect the network tab** - Check the actual data being sent by the server
4. **Look at the `transcription_queue.put()` calls** - Ensure all instances are updated to the new format

## Additional Notes

- The fixes maintain the same functionality while providing better error handling.
- The error recovery mechanism will try to parse malformed data and reconnect if necessary.
- This approach is more robust than a simple find-and-replace because it handles edge cases.

If you need any further assistance, please refer to the detailed comments in the code or contact technical support.
