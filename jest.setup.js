// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock ResizeObserver which is required by shadcn components
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock global fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ data: [], models: [] }), // Adjust mock response as needed
  })
);

// Mock scrollIntoView for JSDOM compatibility with Radix UI components
Element.prototype.scrollIntoView = jest.fn();

// Mock window.scrollTo to prevent jsdom errors in tests
window.scrollTo = jest.fn();

// Mock EventSource for tests that use Server-Sent Events
class MockEventSource {
  constructor(url, options) {
    this.url = url;
    this.options = options;
    this.readyState = 0; // CONNECTING
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;

    // Simulate connection opening
    // In a real test environment, you might want to control this more precisely
    // or use a more sophisticated mock library.
    setTimeout(() => {
      if (this.readyState === 0) { // Only transition if still connecting
        this.readyState = 1; // OPEN
        if (this.onopen) {
          this.onopen({ type: 'open', target: this });
        }
      }
    }, 10);

    // Store instance for debugging or advanced scenarios if needed
    if (!global._mockEventSources) {
      global._mockEventSources = [];
    }
    global._mockEventSources.push(this);
  }

  // Method to simulate receiving a message from the server
  simulateMessage(data, eventType = 'message') {
    if (this.readyState !== 1) return; // Can only receive messages when OPEN
    if (this.onmessage) {
      this.onmessage({ data, type: eventType, target: this });
    }
  }

  // Method to simulate an error from the server or network
  simulateError(error) {
    if (this.readyState === 2) return; // Cannot error if already CLOSED
    this.readyState = 2; // Typically errors close the connection
    if (this.onerror) {
      this.onerror(error);
    }
    // Also remove from active list if managing them
    if (global._mockEventSources) {
        global._mockEventSources = global._mockEventSources.filter(src => src !== this);
    }
  }

  // Method to close the connection
  close() {
    if (this.readyState === 2) return; // Already closed
    this.readyState = 2; // CLOSED
    // Note: Real EventSource might trigger an error event on close if it was unexpected,
    // but for a manual close(), it usually doesn't.
    // If an onclose event handler existed, it would be called.
    if (global._mockEventSources) {
        global._mockEventSources = global._mockEventSources.filter(src => src !== this);
    }
  }
}
global.EventSource = MockEventSource;
