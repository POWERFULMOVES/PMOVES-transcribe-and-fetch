import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import the required modules
from app.transcribe1 import process_video, extract_video_id

# Create a mock status queue and transcription queue
status_queue = asyncio.Queue()
transcription_queue = asyncio.Queue()

# Test YouTube URL
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

# Test output directory
output_dir = os.path.join(os.getcwd(), "test_output")
obsidian_dir = os.path.join(os.getcwd(), "test_obsidian")

# Create the output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(obsidian_dir, exist_ok=True)

# Test the extract_video_id function
def test_extract_video_id():
    video_id = extract_video_id(test_url)
    print(f"Extracted video ID: {video_id}")
    assert video_id == "dQw4w9WgXcQ", f"Expected 'dQw4w9WgXcQ', got '{video_id}'"
    print("extract_video_id test passed!")

# Test the process_video function with Groq
async def test_process_video_groq():
    print(f"Testing process_video with Groq transcription")
    print(f"URL: {test_url}")
    print(f"Output directory: {output_dir}")
    print(f"Obsidian directory: {obsidian_dir}")

    # Configure the model to use Groq
    model_config = {
        "model": "groq",
        "use_groq": True
    }

    # Start the process_video function
    try:
        result = await process_video(
            youtube_video_url=test_url,
            obsidian_dir=obsidian_dir,
            status_queue=status_queue,
            transcription_queue=transcription_queue,
            output_folder=output_dir,
            model_config=model_config
        )

        print(f"process_video result: {result}")

        # Check if any transcription segments were received
        print("Checking transcription segments...")
        segments_received = 0

        # Wait for up to 30 seconds for segments to be received
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                segment = transcription_queue.get_nowait()
                segments_received += 1

                # Parse the segment JSON
                segment_data = json.loads(segment)

                # Handle different segment formats
                if isinstance(segment_data, dict) and 'content' in segment_data and isinstance(segment_data['content'], dict):
                    # Groq format
                    segment_text = segment_data['content'].get('text', 'No text')
                    print(f"Received segment {segments_received} (Groq format): {segment_text[:50]}...")
                elif isinstance(segment_data, str):
                    # Local format might be just a string
                    print(f"Received segment {segments_received} (string format): {segment_data[:50]}...")
                else:
                    # Unknown format, print the whole segment for debugging
                    print(f"Received segment {segments_received} (unknown format): {str(segment_data)[:100]}...")

                # Mark the task as done
                transcription_queue.task_done()
            except asyncio.QueueEmpty:
                # No more segments in the queue
                await asyncio.sleep(1)
                continue

        print(f"Total segments received: {segments_received}")
        assert segments_received > 0, "No transcription segments were received"
        print("process_video with Groq test passed!")

    except Exception as e:
        print(f"Error in process_video with Groq: {e}")
        raise

# Test the process_video function with local transcription
async def test_process_video_local():
    print(f"Testing process_video with local transcription")
    print(f"URL: {test_url}")
    print(f"Output directory: {output_dir}")
    print(f"Obsidian directory: {obsidian_dir}")

    # Configure the model to use local transcription
    model_config = {
        "model": "local",
        "use_groq": False
    }

    # Start the process_video function
    try:
        result = await process_video(
            youtube_video_url=test_url,
            obsidian_dir=obsidian_dir,
            status_queue=status_queue,
            transcription_queue=transcription_queue,
            output_folder=output_dir,
            model_config=model_config
        )

        print(f"process_video result: {result}")

        # Check if any transcription segments were received
        print("Checking transcription segments...")
        segments_received = 0

        # Wait for up to 30 seconds for segments to be received
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                segment = transcription_queue.get_nowait()
                segments_received += 1

                # Parse the segment JSON
                print(f"Raw segment data: {segment[:200]}...")
                try:
                    segment_data = json.loads(segment)
                    print(f"Parsed segment data type: {type(segment_data).__name__}")

                    # Handle different segment formats
                    if isinstance(segment_data, dict):
                        print(f"Dict keys: {list(segment_data.keys())}")
                        if 'content' in segment_data:
                            content = segment_data['content']
                            print(f"Content type: {type(content).__name__}")
                            if isinstance(content, dict):
                                # Groq format
                                segment_text = content.get('text', 'No text')
                                print(f"Received segment {segments_received} (dict format): {segment_text[:50]}...")
                                print(f"Full content: {json.dumps(content, indent=2)}")
                            else:
                                print(f"Received segment {segments_received} (dict with non-dict content): {str(content)[:100]}...")
                        else:
                            print(f"Received segment {segments_received} (dict without content key): {str(segment_data)[:100]}...")
                    elif isinstance(segment_data, str):
                        # Local format might be just a string
                        print(f"Received segment {segments_received} (string format): {segment_data[:50]}...")
                    else:
                        # Unknown format, print the whole segment for debugging
                        print(f"Received segment {segments_received} (unknown format): {str(segment_data)[:100]}...")
                except json.JSONDecodeError as e:
                    print(f"Error parsing segment JSON: {e}")
                    print(f"Raw segment: {segment}")

                # Mark the task as done
                transcription_queue.task_done()
            except asyncio.QueueEmpty:
                # No more segments in the queue
                await asyncio.sleep(1)
                continue

        print(f"Total segments received: {segments_received}")
        assert segments_received > 0, "No transcription segments were received"
        print("process_video with local transcription test passed!")

    except Exception as e:
        print(f"Error in process_video with local transcription: {e}")
        raise



# Main function to run the tests
async def main():
    print("Starting transcription feature tests...")

    # Test extract_video_id
    test_extract_video_id()

    # Test process_video with local transcription only
    print("\n=== Testing Local Transcription ===\n")
    await test_process_video_local()

    print("\nLocal transcription test completed!")

# Run the tests
if __name__ == "__main__":
    asyncio.run(main())
