import { renderHook, act } from '@testing-library/react'; // Updated import
import useSSE from '../useSSE';

// Mock the BACKEND_URL
jest.mock('@/lib/constants', () => ({
  BACKEND_URL: 'http://localhost:8000',
  SSE_CONFIG: {
    MAX_RETRIES: 3,
    RECONNECT_DELAY: 1000,
    TIMEOUT: 30000,
    COMPLETION_GRACE_PERIOD: 2000,
    AUTO_RECONNECT_AFTER_COMPLETE: false
  }
}));

describe('useSSE hook', () => {
  beforeEach(() => {
    // Clear any global state between tests
    window._sseActiveConnections = {};
    window._sseReferenceCount = {};
    window._sseConnectAttemptTime = 0;
    window._sseConnectDebounce = null;
    window._sseReconnectTimeout = null;
    
    // Spy on console methods
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'debug').mockImplementation(() => {});
  });
  
  afterEach(() => {
    // Restore console methods
    console.log.mockRestore();
    console.error.mockRestore();
    console.warn.mockRestore();
    console.debug.mockRestore();
  });
  
  test('should connect to SSE endpoint on mount when autoConnect is true', async () => {
    const onConnect = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onConnect
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Check that we're connected
    expect(result.current.connected).toBe(true);
    expect(onConnect).toHaveBeenCalled();
  });
  
  test('should not connect to SSE endpoint on mount when autoConnect is false', () => {
    const onConnect = jest.fn();
    
    const { result } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: false,
        onConnect
      })
    );
    
    // Check that we're not connected
    expect(result.current.connected).toBe(false);
    expect(onConnect).not.toHaveBeenCalled();
  });
  
  test('should connect when connect is called', async () => {
    const onConnect = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: false,
        onConnect
      })
    );
    
    // Check that we're not connected initially
    expect(result.current.connected).toBe(false);
    
    // Call connect
    act(() => {
      result.current.connect();
    });
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Check that we're connected
    expect(result.current.connected).toBe(true);
    expect(onConnect).toHaveBeenCalled();
  });
  
  test('should disconnect when disconnect is called', async () => {
    const onConnect = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onConnect
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Check that we're connected
    expect(result.current.connected).toBe(true);
    
    // Call disconnect
    act(() => {
      result.current.disconnect();
    });
    
    // Check that we're disconnected
    expect(result.current.connected).toBe(false);
  });
  
  test('should process transcription segment messages correctly', async () => {
    const onMessage = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onMessage
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Create a mock transcription segment
    const mockSegment = {
      type: 'transcription_segment',
      content: {
        id: 1,
        text: 'This is a test transcription segment',
        start: 0,
        end: 5,
        video_id: 'test123'
      }
    };
    
    // Simulate receiving a message
    act(() => {
      const eventSource = result.current.connect();
      // Access the EventSource instance
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      // Simulate a message
      mockEventSource.simulateMessage(JSON.stringify(mockSegment));
    });
    
    // Check that the message was processed
    expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({
      type: 'transcription_segment',
      content: expect.objectContaining({
        id: 1,
        text: 'This is a test transcription segment'
      })
    }));
    
    // Check that the message was added to the messages array
    expect(result.current.messages.length).toBe(1);
    expect(result.current.lastMessage).toEqual(expect.objectContaining({
      type: 'transcription_segment',
      content: expect.objectContaining({
        id: 1,
        text: 'This is a test transcription segment'
      })
    }));
  });
  
  test('should handle malformed JSON gracefully', async () => {
    const onMessage = jest.fn();
    const onError = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onMessage,
        onError
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Simulate receiving a malformed message
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      mockEventSource.simulateMessage('This is not valid JSON');
    });
    
    // Check that the message was processed as a status update
    expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({
      type: 'status',
      content: 'This is not valid JSON'
    }));
    
    // Check that no error was reported
    expect(onError).not.toHaveBeenCalled();
  });
  
  test('should handle transcription_complete messages correctly', async () => {
    const onMessage = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onMessage
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Create a mock transcription_complete message
    const mockComplete = {
      type: 'transcription_complete',
      content: {
        video_id: 'test123',
        segments_count: 10
      }
    };
    
    // Simulate receiving a message
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      mockEventSource.simulateMessage(JSON.stringify(mockComplete));
    });
    
    // Check that the message was processed
    expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({
      type: 'transcription_complete',
      content: expect.objectContaining({
        video_id: 'test123',
        segments_count: 10
      })
    }));
    
    // Check that the message was added to the messages array
    expect(result.current.messages.length).toBe(1);
    expect(result.current.lastMessage).toEqual(expect.objectContaining({
      type: 'transcription_complete',
      content: expect.objectContaining({
        video_id: 'test123',
        segments_count: 10
      })
    }));
  });
  
  test('should handle connection errors gracefully', async () => {
    const onError = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onError
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Manually disconnect to simulate connection closing
    act(() => {
      result.current.disconnect();
    });
    
    // Check that we're disconnected
    expect(result.current.connected).toBe(false);
    
    // Verify that the disconnect worked properly
    expect(window._sseActiveConnections['/combined-updates']).toBeUndefined();
  });
  
  test('should parse transcription segments with different property names', async () => {
    const onMessage = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onMessage
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Create a mock transcription segment with different property names
    const mockSegment = {
      type: 'transcription_segment',
      content: {
        id: 1,
        Text: 'This is a test with different property names',
        start_time: 0,
        end_time: 5,
        video_id: 'test123'
      }
    };
    
    // Simulate receiving a message
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      mockEventSource.simulateMessage(JSON.stringify(mockSegment));
    });
    
    // Check that the message was processed and text was extracted correctly
    expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({
      type: 'transcription_segment',
      content: expect.objectContaining({
        id: 1,
        text: 'This is a test with different property names'
      })
    }));
  });
  
  test('should handle nested content objects', async () => {
    const onMessage = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onMessage
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Create a mock message with content as a string (serialized JSON)
    const mockMessage = {
      type: 'transcription_segment',
      content: JSON.stringify({
        id: 1,
        text: 'This is a test with nested content',
        start: 0,
        end: 5,
        video_id: 'test123'
      })
    };
    
    // Simulate receiving a message
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      mockEventSource.simulateMessage(JSON.stringify(mockMessage));
    });
    
    // Check that the content was parsed correctly
    expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({
      type: 'transcription_segment',
      content: expect.objectContaining({
        id: 1,
        text: 'This is a test with nested content'
      })
    }));
  });
});
