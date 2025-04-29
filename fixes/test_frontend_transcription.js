// Test script to verify that the frontend correctly handles transcription segments

// Import the required modules
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from './src/app/page';

// Mock the EventSource constructor
global.EventSource = jest.fn(() => ({
  addEventListener: jest.fn(),
  close: jest.fn()
}));

// Mock the axios module
jest.mock('axios', () => ({
  get: jest.fn().mockResolvedValue({ status: 200, data: { status: 'ok' } }),
  post: jest.fn().mockResolvedValue({ status: 200, data: { status: 'started' } })
}));

// Mock the localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn()
};
global.localStorage = localStorageMock;

// Test the Home component
describe('Home component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the Home component', () => {
    render(<Home />);
    expect(screen.getByText('YouTube Transcription')).toBeInTheDocument();
  });

  test('handles transcription segments correctly', async () => {
    // Render the Home component
    const { container } = render(<Home />);

    // Get the EventSource addEventListener mock
    const addEventListener = global.EventSource.mock.results[0].value.addEventListener;

    // Get the message handler
    const messageHandler = addEventListener.mock.calls[0][1];

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

    // Call the message handler with the mock segment
    messageHandler({ data: JSON.stringify(mockSegment) });

    // Wait for the segment to be rendered
    await waitFor(() => {
      // Check if the segment text is rendered
      expect(screen.getByText('This is a test transcription segment')).toBeInTheDocument();
    });
  });
});
