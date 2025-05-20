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
