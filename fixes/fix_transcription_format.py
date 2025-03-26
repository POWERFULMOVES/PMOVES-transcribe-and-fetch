"""
This file contains fixes for the transcription format issues in the PMOVES transcription system.
It addresses JSON parsing errors by fixing the formatting of SSE (Server-Sent Events) data.
"""

import os
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_properly_formatted_transcription_segment(transcription_queue, segment_data):
    """
    Send a properly formatted transcription segment through the transcription_queue.
    
    Args:
        transcription_queue: The asyncio.Queue for sending transcription updates
        segment_data: A dictionary containing the segment information with these fields:
            - text: The transcribed text
            - start_time: Start time in seconds (float)
            - end_time: End time in seconds (float)
            - video_id: YouTube video ID
            - id: Segment ID/index
    """
    try:
        # Format according to expected frontend format
        segment_message = {
            "type": "transcription_segment",
            "content": {
                "text": segment_data["text"],
                "start_time": segment_data["start_time"],
                "end_time": segment_data["end_time"],
                "video_id": segment_data["video_id"],
                "id": segment_data["id"],
                "watch_url": segment_data.get("watch_url")
            }
        }
        
        # Send the properly formatted JSON data
        await transcription_queue.put(json.dumps(segment_message))
        logger.info(f"Sent formatted transcription segment: {segment_data['id']}")
        
    except Exception as e:
        logger.error(f"Error sending transcription segment: {str(e)}")
        # Send error notification
        await transcription_queue.put(json.dumps({
            "type": "error",
            "content": f"Error formatting transcription segment: {str(e)}"
        }))

# Example of how to use this in the transcribe_audio function
"""
# Replace this in transcribe_audio function:

await transcription_queue.put(json.dumps({
    "type": "transcription_segment",
    "content": f"| [{start_time}]({watch_url}) | {video_id} | {idx} | {start_time} | {end_time} | {segment_text} |"
}))

# With:

segment_data = {
    "text": segment_text,
    "start_time": segment.start,  # Use actual seconds value
    "end_time": segment.end,      # Use actual seconds value
    "video_id": video_id,
    "id": idx,
    "watch_url": watch_url
}
await send_properly_formatted_transcription_segment(transcription_queue, segment_data)
"""

# Patch function for transcribe1.py
def patch_transcribe_audio():
    """
    Instructions for manually updating the transcribe_audio function in transcribe1.py
    """
    return """
# In transcribe1.py, replace the segment sending code:

# Find this code in transcribe_audio function:
await transcription_queue.put(json.dumps({
    "type": "transcription_segment",
    "content": f"| [{start_time}]({watch_url}) | {video_id} | {idx} | {start_time} | {end_time} | {segment_text} |"
}))

# Replace it with:
segment_data = {
    "text": segment_text,
    "start_time": segment.start,
    "end_time": segment.end,
    "video_id": video_id,
    "id": idx,
    "watch_url": watch_url
}
await transcription_queue.put(json.dumps({
    "type": "transcription_segment",
    "content": segment_data
}))

# Similarly, in process_audio_with_groq function, find similar code and update it.
"""

# Modified version of the transcribe_audio function
"""
async def transcribe_audio(audio_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue, youtube_video_url: str):
    # ... (existing code remains the same)
    
    # Process segments with minimal delay
    for idx, segment in enumerate(segments_gen):
        try:
            # Clean and format segment text
            segment_text = segment.text.strip()
            
            # Format timestamps
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            
            # Create timestamped YouTube URL
            timestamp_seconds = int(segment.start)
            watch_url = f"{base_url}&t={timestamp_seconds}"
            
            # Format segment data for structured output
            segment_dict = {
                'watch_url': watch_url,
                'video_id': video_id,
                'id': idx,
                'start': start_time,
                'end': end_time,
                'text': segment_text
            }
            result.append(segment_dict)
            
            # Send transcription segment with proper JSON formatting
            await transcription_queue.put(json.dumps({
                "type": "transcription_segment",
                "content": {
                    "text": segment_text,
                    "start_time": segment.start,
                    "end_time": segment.end,
                    "id": idx,
                    "video_id": video_id,
                    "watch_url": watch_url
                }
            }))
            
            logger.info(f"Sent transcription segment: {segment_text} at {start_time}")
            
            # Send status updates periodically
            if idx % 5 == 0:
                await status_queue.put(json.dumps({
                    "type": "status",
                    "content": f"Transcribing segment {idx + 1}"
                }))
            
            # Format text for markdown table (for the final output)
            formatted_text = (
                f"| [{start_time}]({watch_url}) | {video_id} | "
                f"{idx} | {start_time} | {end_time} | "
                f"{segment_text} |\n"
            )
            full_text += formatted_text
            
            # Prevent blocking
            await asyncio.sleep(0)
            
        except Exception as segment_error:
            logger.error(f"Error processing segment {idx}: {str(segment_error)}")
            continue
    
    # The rest of the function remains the same...
"""

if __name__ == "__main__":
    print("This is a utility module that provides functions to fix transcription formatting issues.")
    print("To apply the fix:")
    print("1. Edit backend/app/transcribe1.py")
    print("2. Update the transcribe_audio and process_audio_with_groq functions as shown in patch_transcribe_audio()")
    print("\nFix details:")
    print(patch_transcribe_audio())
