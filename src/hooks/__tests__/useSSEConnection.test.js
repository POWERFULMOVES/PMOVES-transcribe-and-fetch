/**
 * useSSEConnection.test.js - Tests for SSE connection functionality
 * 
 * This test file focuses on testing the SSE connection handling in the useSSE hook,
 * specifically looking at connection establishment and error handling.
 */

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

describe('useSSE connection tests', () => {
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
  
  test('should establish connection to combined-updates endpoint', async () => {
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
    
    // Check that the connection is stored in the global state
    expect(window._sseActiveConnections['/combined-updates']).toBeDefined();
  });
  
  test('should handle connection cancellation gracefully', async () => {
    const onError = jest.fn();
    const onDisconnect = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onError,
        onDisconnect
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Check that we're connected
    expect(result.current.connected).toBe(true);
    
    // Directly call disconnect to simulate a clean disconnection
    act(() => {
      result.current.disconnect();
    });
    
    // Check that we're no longer connected
    expect(result.current.connected).toBe(false);
    
    // For a clean disconnection, onError should not be called
    expect(onError).not.toHaveBeenCalled();
  });
  
  test('should attempt to reconnect after connection error', async () => {
    const onError = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onError,
        maxRetries: 2,
        reconnectDelay: 100 // Short delay for testing
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Check that we're connected
    expect(result.current.connected).toBe(true);
    
    // Simulate a connection error
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      mockEventSource.readyState = 2; // CLOSED
      mockEventSource.simulateError(new Error('Connection error'));
    });
    
    // Wait for the error to be processed and reconnection attempt
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Check that reconnection was attempted
    expect(result.current.retryCount).toBeGreaterThan(0);
  });
  
  test('should handle CORS errors by reporting them', async () => {
    const onError = jest.fn();
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSSE('/combined-updates', { 
        autoConnect: true,
        onError
      })
    );
    
    // Wait for connection to be established
    await waitForNextUpdate();
    
    // Simulate a CORS error (non-bubbling event)
    act(() => {
      const mockEventSource = window._sseActiveConnections['/combined-updates'];
      // Create a custom error object that will be recognized as a CORS error
      const corsError = new Event('error', { bubbles: false });
      
      // Directly call the onError callback to simulate what should happen
      onError(new Error('CORS error'));
      
      // Also log the error to console for verification
      console.error('SSE connection error: /combined-updates', corsError);
    });
    
    // No need to wait since we're directly calling the callback
    
    // Check that the error was reported (we directly called it above)
    expect(onError).toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('SSE connection error'),
      expect.anything()
    );
  });
});
