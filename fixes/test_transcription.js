// Test script to verify that transcription segments are being properly sent to the frontend

// Mock the SSE connection
const mockSSE = {
  addEventListener: jest.fn(),
  close: jest.fn()
};

// Mock the EventSource constructor
global.EventSource = jest.fn(() => mockSSE);

// Import the useSSE hook
import { useSSE } from '../src/hooks/useSSE';

// Mock the dispatch function
const mockDispatch = jest.fn();

// Test the useSSE hook
describe('useSSE hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle transcription segments correctly', () => {
    // Create a mock transcription segment
    const mockSegment = {
      type: 'transcription_segment',
      content: {
        text: 'This is a test transcription segment',
        start_time: 10.5,
        end_time: 15.2,
        id: 1,
        video_id: 'test-video-id',
        watch_url: 'https://www.youtube.com/watch?v=test-video-id&t=10'
      }
    };

    // Call the useSSE hook
    const { connected } = useSSE('http://localhost:8000/combined-updates', mockDispatch);

    // Get the message handler
    const messageHandler = mockSSE.addEventListener.mock.calls[0][1];

    // Create a mock event
    const mockEvent = {
      data: JSON.stringify(mockSegment)
    };

    // Call the message handler with the mock event
    messageHandler(mockEvent);

    // Verify that dispatch was called with the correct action
    expect(mockDispatch).toHaveBeenCalledWith({
      type: 'ADD_TRANSCRIPTION_SEGMENT',
      payload: mockSegment.content
    });
  });
});
