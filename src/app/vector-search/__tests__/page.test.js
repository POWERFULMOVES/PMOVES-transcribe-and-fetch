import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VectorSearch from '../page';

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('VectorSearch Component', () => {
  beforeEach(() => {
    global.EventSource = jest.fn(() => ({
      close: jest.fn(),
      onmessage: null,
      onerror: null
    }));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders search interface with all parameters', () => {
    render(<VectorSearch />);
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeInTheDocument();
  });

  it('updates fine-grained search parameters', () => {
    render(<VectorSearch />);
    const thresholdSlider = screen.getByTestId('fine-grained-threshold-slider');
    expect(thresholdSlider).toBeInTheDocument();
  });

  it('sends correct search parameters in EventSource URL', async () => {
    render(<VectorSearch />);
    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringMatching(/http:\/\/localhost:8000\/vector-search-stream/)
    );
    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringMatching(/query=test\+query/)
    );
    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringMatching(/fine_grained_similarity_threshold=0\.75/)
    );
  });

  it('handles search results and analysis', async () => {
    render(<VectorSearch />);
    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    let mockEventSource;
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
      mockEventSource = global.EventSource.mock.results[0].value;
    });

    await act(async () => {
      // Send search results
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'results',
          results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }]
        })
      });

      // Send Groq analysis
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'ai_response_groq',
          analysis: {
            provider: 'groq',
            content: 'Test Groq analysis'
          }
        })
      });

      // Send OpenAI analysis
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'ai_response_openai',
          analysis: {
            provider: 'openai',
            content: 'Test OpenAI analysis'
          }
        })
      });

      // Send completion message
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'complete',
          message: 'Search complete'
        })
      });
    });

    await waitFor(() => {
      // Check search results
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
      expect(screen.getByTestId('search-result-0')).toHaveTextContent('Test Result 1');
      
      // Check both AI analyses
      expect(screen.getByTestId('groq-analysis')).toHaveTextContent('Test Groq analysis');
      expect(screen.getByTestId('openai-analysis')).toHaveTextContent('Test OpenAI analysis');
    });
  });

  it('handles AI analysis errors gracefully', async () => {
    render(<VectorSearch />);
    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    let mockEventSource;
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
      mockEventSource = global.EventSource.mock.results[0].value;
    });

    await act(async () => {
      // Send search results
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'results',
          results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }]
        })
      });

      // Send error for Groq
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'ai_response_groq',
          analysis: {
            provider: 'groq',
            content: 'Error with Groq analysis: Token limit exceeded'
          }
        })
      });

      // Send successful OpenAI analysis
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'ai_response_openai',
          analysis: {
            provider: 'openai',
            content: 'Test OpenAI analysis'
          }
        })
      });

      // Send completion message
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'complete',
          message: 'Search complete'
        })
      });
    });

    await waitFor(() => {
      // Check search results still appear
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
      expect(screen.getByTestId('search-result-0')).toHaveTextContent('Test Result 1');
      
      // Check error message appears for Groq
      expect(screen.getByTestId('groq-analysis')).toHaveTextContent('Token limit exceeded');
      
      // Check OpenAI analysis still appears
      expect(screen.getByTestId('openai-analysis')).toHaveTextContent('Test OpenAI analysis');
    });
  });

  it('handles missing AI responses', async () => {
    render(<VectorSearch />);
    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    let mockEventSource;
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
      mockEventSource = global.EventSource.mock.results[0].value;
    });

    await act(async () => {
      // Send search results
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'results',
          results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }]
        })
      });

      // Send error about no AI analysis
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'error',
          message: 'No AI analysis was generated'
        })
      });

      // Send completion message
      mockEventSource.onmessage({
        data: JSON.stringify({
          type: 'complete',
          message: 'Search complete'
        })
      });
    });

    await waitFor(() => {
      // Check search results still appear
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
      expect(screen.getByTestId('search-result-0')).toHaveTextContent('Test Result 1');
      
      // Check error message appears
      expect(screen.getByTestId('analysis-error')).toHaveTextContent('No AI analysis was generated');
      
      // Check AI analysis sections don't appear
      expect(screen.queryByTestId('groq-analysis')).not.toBeInTheDocument();
      expect(screen.queryByTestId('openai-analysis')).not.toBeInTheDocument();
    });
  });

  it('handles EventSource errors', async () => {
    render(<VectorSearch />);
    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    let mockEventSource;
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
      mockEventSource = global.EventSource.mock.results[0].value;
    });

    await act(async () => {
      mockEventSource.onerror(new Error('Connection failed'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toHaveTextContent(/Connection error occurred/);
    });
  });

  describe('Model Responses', () => {
    const setupTest = async (query) => {
      render(<VectorSearch />);
      const searchInput = screen.getByTestId('search-input');
      const searchButton = screen.getByTestId('search-button');

      let mockEventSource;
      await act(async () => {
        fireEvent.change(searchInput, { target: { value: query } });
        fireEvent.click(searchButton);
        mockEventSource = global.EventSource.mock.results[0].value;
      });

      return mockEventSource;
    };

    it('should handle different model responses', async () => {
      const mockEventSource = await setupTest('What is the architecture of the system?');

      await act(async () => {
        mockEventSource.onmessage({
          data: JSON.stringify({
            type: 'results',
            results: [{
              content: 'Test content',
              similarity: 0.85,
              source: 'test_source',
              search_method: 'fine_grained'
            }]
          })
        });

        mockEventSource.onmessage({
          data: JSON.stringify({
            type: 'ai_response_openai',
            analysis: {
              provider: 'openai',
              content: 'The system uses a multi-tier architecture...'
            }
          })
        });

        mockEventSource.onmessage({
          data: JSON.stringify({
            type: 'ai_response_groq',
            analysis: {
              provider: 'groq',
              content: 'System architecture consists of...'
            }
          })
        });
      });

      await waitFor(() => {
        expect(screen.getByTestId('openai-analysis')).toHaveTextContent(/multi-tier architecture/);
        expect(screen.getByTestId('groq-analysis')).toHaveTextContent(/System architecture/);
      });
    });
  });
});
