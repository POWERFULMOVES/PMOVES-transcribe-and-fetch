"""
Debug endpoints for troubleshooting the transcription service.
"""
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter(tags=["Debug"])

@router.get("/debug/test-sse")
async def test_sse(request: Request):
    """Test SSE endpoint that sends sample transcription segments."""
    # Get the origin from the request or use a default
    origin = request.headers.get("origin", "http://localhost:3000")
    print(f"Test SSE connection requested from {request.client.host if request.client else 'unknown'} with origin {origin}")

    async def event_generator():
        try:
            # Initial connection message
            yield f"data: {json.dumps({'type': 'status', 'content': 'Debug SSE connection established', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(1)

            # Sample transcription segment
            segment1 = {
                'type': 'transcription_segment',
                'content': {
                    'text': 'This is a test transcription segment.',
                    'start_time': 0.0,
                    'end_time': 2.0,
                    'id': 'test_segment_1',
                    'video_id': 'test_video'
                },
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(segment1)}\n\n"
            await asyncio.sleep(1)

            # Another sample segment
            segment2 = {
                'type': 'transcription_segment',
                'content': {
                    'text': 'This is another test transcription segment.',
                    'start_time': 2.0,
                    'end_time': 4.0,
                    'id': 'test_segment_2',
                    'video_id': 'test_video'
                },
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(segment2)}\n\n"
            await asyncio.sleep(1)

            # Completion message
            completion = {
                'type': 'transcription_complete',
                'content': {
                    'segments_count': 2,
                    'duration': 4.0
                },
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion)}\n\n"

        except Exception as e:
            print(f"Error in test SSE: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'timestamp': datetime.now().isoformat()})}\n\n"

    response = EventSourceResponse(event_generator())

    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    # Set other headers
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"

    return response

@router.options("/debug/test-sse")
async def options_test_sse(request: Request):
    """Handle OPTIONS requests for the test SSE endpoint."""
    from fastapi.responses import JSONResponse

    # Get the origin from the request or use a default
    origin = request.headers.get("origin", "http://localhost:3000")
    print(f"OPTIONS request for test SSE endpoint from {request.client.host if request.client else 'unknown'} with origin {origin}")

    response = JSONResponse(content={"detail": "OK"})

    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return response

@router.get("/debug/direct-sse")
async def direct_sse(request: Request):
    """Direct SSE endpoint that bypasses the queue system."""
    # Get the origin from the request or use a default
    origin = request.headers.get("origin", "http://localhost:3000")
    print(f"Direct SSE connection requested from {request.client.host if request.client else 'unknown'} with origin {origin}")

    async def event_generator():
        try:
            # Initial connection message
            yield f"data: {json.dumps({'type': 'status', 'content': 'Direct SSE connection established', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(1)

            # Send 10 transcription segments directly
            for i in range(1, 11):
                segment = {
                    'type': 'transcription_segment',
                    'content': {
                        'text': f'This is direct test segment {i}.',
                        'start_time': float(i),
                        'end_time': float(i + 1),
                        'id': f'direct_segment_{i}',
                        'video_id': 'direct_test',
                        'watch_url': 'https://www.youtube.com/watch?v=direct_test',
                        'start': f'{i}:00',
                        'end': f'{i+1}:00'
                    },
                    'timestamp': datetime.now().isoformat()
                }
                print(f"Sending direct segment {i}")
                yield f"data: {json.dumps(segment)}\n\n"
                await asyncio.sleep(0.5)

            # Send completion message
            completion = {
                'type': 'transcription_complete',
                'content': {
                    'segments_count': 10,
                    'duration': 10.0
                },
                'timestamp': datetime.now().isoformat()
            }
            print("Sending direct completion message")
            yield f"data: {json.dumps(completion)}\n\n"

        except Exception as e:
            print(f"Error in direct SSE: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'timestamp': datetime.now().isoformat()})}\n\n"

    response = EventSourceResponse(event_generator())

    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    # Set other headers
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"

    return response

@router.options("/debug/direct-sse")
async def options_direct_sse(request: Request):
    """Handle OPTIONS requests for the direct SSE endpoint."""
    from fastapi.responses import JSONResponse

    # Get the origin from the request or use a default
    origin = request.headers.get("origin", "http://localhost:3000")
    print(f"OPTIONS request for direct SSE endpoint from {request.client.host if request.client else 'unknown'} with origin {origin}")

    response = JSONResponse(content={"detail": "OK"})

    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return response

@router.post("/debug/send-test-segment")
async def send_test_segment(request: Request):
    """Send a test transcription segment to the transcription queue."""
    try:
        # Get queue manager from app state
        queue_manager = request.app.state.queue_manager

        # Create a test segment
        test_segment = {
            'type': 'transcription_segment',
            'content': {
                'text': 'This is a test transcription segment sent directly to the queue.',
                'start_time': 0.0,
                'end_time': 2.0,
                'id': 'direct_test_segment',
                'video_id': 'test_video',
                'watch_url': 'https://www.youtube.com/watch?v=test_video'
            },
            'timestamp': datetime.now().isoformat()
        }

        # Add to transcription queue
        await queue_manager.transcription_queue.put(json.dumps(test_segment))
        print(f"Test segment sent to transcription queue: {json.dumps(test_segment)}")

        # Send a completion message after a short delay
        await asyncio.sleep(2)
        completion_msg = {
            'type': 'transcription_complete',
            'content': {
                'segments_count': 1,
                'duration': 2.0
            },
            'timestamp': datetime.now().isoformat()
        }
        await queue_manager.transcription_queue.put(json.dumps(completion_msg))
        print(f"Completion message sent to transcription queue: {json.dumps(completion_msg)}")

        return {
            "status": "success",
            "message": "Test segment and completion message added to transcription queue"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send test segment: {str(e)}"
        }

@router.get("/debug/queue-status")
async def queue_status(request: Request):
    """Get the current status of the queues."""
    try:
        # Get queue manager from app state
        queue_manager = request.app.state.queue_manager

        # Get the last few items from the transcription queue without removing them
        transcription_items = []
        try:
            # Create a copy of the queue to peek at items
            queue_copy = asyncio.Queue()
            items = []

            # Get all items from the original queue
            while not queue_manager.transcription_queue.empty():
                item = await queue_manager.transcription_queue.get()
                items.append(item)

            # Put items back in the original queue and in our copy
            for item in items:
                await queue_manager.transcription_queue.put(item)
                await queue_copy.put(item)

            # Get the last 5 items from our copy for display
            while not queue_copy.empty() and len(transcription_items) < 5:
                item = await queue_copy.get()
                transcription_items.append(item)
        except Exception as queue_error:
            transcription_items = [f"Error getting queue items: {str(queue_error)}"]

        return {
            "status": "success",
            "status_queue_size": queue_manager.status_queue.qsize(),
            "transcription_queue_size": queue_manager.transcription_queue.qsize(),
            "active_transcriptions": list(queue_manager.active_transcriptions),
            "recent_transcription_items": transcription_items
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get queue status: {str(e)}"
        }
