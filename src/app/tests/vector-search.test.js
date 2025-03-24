import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import VectorSearch from '../vector-search/page';
import '@testing-library/jest-dom';
import axios from 'axios';
import fetchMock from 'jest-fetch-mock';

// Mock axios
jest.mock('axios');

// Mock EventSource
class MockEventSource {
  constructor(url) {
    this.url = url;
    this.onmessage = jest.fn();
    this.onopen = jest.fn();
    this.onerror = jest.fn();
    
    // Call onopen immediately
    setTimeout(() => {
      if (this.onopen) this.onopen();
      
      // Simulate receiving search results
      const events = [
        { type: 'log', message: 'Starting search operation...' },
        { type: 'log', message: 'Found 5 results' },
        { 
          type: 'results', 
          results: [
            {
              id: 'result-1',
              content: 'Test content 1',
              similarity: 0.85,
              source: 'test_source',
              video_id: '123',
              search_method: 'hybrid'
            }
          ]
        },
        { type: 'ai_response_openai', analysis: 'OpenAI Analysis' },
        { type: 'ai_response_groq', analysis: 'Groq Analysis' },
        { type: 'token_usage', usage: { sent: 100, received: 200 } },
        { type: 'complete', message: 'Search operation complete' }
      ];
      
      // Send each event with a small delay
      events.forEach((event, index) => {
        setTimeout(() => {
          this.onmessage({ data: JSON.stringify(event) });
        }, 100 * (index + 1));
      });
    }, 10);
  }
  
  close() {
    // Clean up
  }
}

// Replace global EventSource with mock
global.EventSource = MockEventSource;

// Mock local storage for settings
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('VectorSearch Component', () => {
  beforeEach(() => {
    // Mock API responses
    axios.get.mockImplementation(url => {
      if (url.includes('/api/search-config')) {
        return Promise.resolve({
          data: {
            fine_grained: {
              similarity_threshold: 0.75,
              content_weight: 0.8,
              result_percentage: 0.4,
              max_results: 15
            },
            contextual: {
              similarity_threshold: 0.7,
              content_weight: 0.6,
              result_percentage: 0.4,
              max_results: 10
            },
            overview: {
              similarity_threshold: 0.65,
              content_weight: 0.5,
              result_percentage: 0.2,
              max_results: 5
            }
          }
        });
      }
      if (url.includes('/api/search-config/presets')) {
        return Promise.resolve({
          data: {
            presets: ['default', 'technical', 'conceptual', 'balanced']
          }
        });
      }
      return Promise.reject(new Error('Not found'));
    });
    
    axios.post.mockImplementation(url => {
      if (url.includes('/api/search-config/preset')) {
        return Promise.resolve({
          data: {
            success: true,
            message: 'Preset loaded successfully'
          }
        });
      }
      return Promise.reject(new Error('Not found'));
    });
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders search interface with sliders', async () => {
    render(<VectorSearch />);
    
    // Check that main components render
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeInTheDocument();
    
    // Check that sliders for parameters render
    expect(screen.getByText(/Similarity Threshold/i)).toBeInTheDocument();
    expect(screen.getByText(/Content Weight/i)).toBeInTheDocument();
    
    // Check that max_results sliders render
    const maxResultsLabels = screen.getAllByText(/Max Results/i);
    expect(maxResultsLabels.length).toBeGreaterThan(0);
  });

  test('updates search parameters when sliders change', async () => {
    render(<VectorSearch />);
    
    // Get the fine-grained threshold slider
    const slider = screen.getByTestId('fine-grained-threshold-slider');
    
    // Simulate changing the slider
    fireEvent.change(slider, { target: { value: 0.85 } });
    
    // Wait for the UI to update
    await waitFor(() => {
      // Check that the value is displayed
      expect(screen.getByText(/0.85/)).toBeInTheDocument();
    });
  });

  test('performs search and displays results', async () => {
    render(<VectorSearch />);
    
    // Enter search query
    const searchInput = screen.getByTestId('search-input');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    
    // Click search button
    const searchButton = screen.getByTestId('search-button');
    fireEvent.click(searchButton);
    
    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText(/Found 5 results/i)).toBeInTheDocument();
    });
    
    // Check that AI responses render
    await waitFor(() => {
      expect(screen.getByTestId('openai-response')).toHaveTextContent('OpenAI Analysis');
      expect(screen.getByTestId('groq-response')).toHaveTextContent('Groq Analysis');
    });
  });
}); 