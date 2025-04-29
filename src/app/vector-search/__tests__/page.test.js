import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VectorSearch from '../page';
import axios from 'axios';

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock axios
jest.mock('axios');

describe('VectorSearch Component', () => {
  beforeEach(() => {
    // Reset axios mock before each test
    axios.post.mockReset();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders search interface with all parameters', () => {
    render(<VectorSearch />);
    expect(screen.getByPlaceholderText('Enter your search query')).toBeInTheDocument();
    // Use a more specific selector for the search button
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('updates fine-grained search parameters', () => {
    render(<VectorSearch />);
    // Find the accordion trigger and click it to expand parameters
    const accordionTrigger = screen.getByText(/Adjust Search Parameters/i);
    fireEvent.click(accordionTrigger);
    
    // Check that sliders are present
    expect(screen.getByText(/Fine-grained \(High Precision\)/i)).toBeInTheDocument();
    // Use getAllByText and check the first one
    expect(screen.getAllByText(/Similarity Threshold:/i)[0]).toBeInTheDocument();
  });

  it('sends correct search parameters in axios POST request', async () => {
    // Mock successful response
    axios.post.mockResolvedValue({
      data: {
        results: [],
        openai_analysis: '',
        groq_analysis: '',
        metadata: {}
      }
    });

    render(<VectorSearch />);
    const searchInput = screen.getByPlaceholderText('Enter your search query');
    // Use a more specific selector for the search button
    const searchButton = screen.getByText('Search');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    // Check that axios.post was called with the correct URL and data
    expect(axios.post).toHaveBeenCalledTimes(1);
    
    // Check URL contains the correct parameters
    const calledUrl = axios.post.mock.calls[0][0];
    expect(calledUrl).toMatch(/http:\/\/localhost:8000\/api\/search/);
    expect(calledUrl).toMatch(/preset=default/);
    
    // Check request body contains the correct data
    const requestBody = axios.post.mock.calls[0][1];
    expect(requestBody).toEqual({
      query: 'test query',
      max_results: expect.any(Number),
      run_analysis: true
    });
  });

  it('handles search results and analysis', async () => {
    // Mock successful response with results and analysis
    axios.post.mockResolvedValue({
      data: {
        results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }],
        openai_analysis: 'Test OpenAI analysis',
        groq_analysis: 'Test Groq analysis',
        metadata: {
          search_duration_seconds: 1.5,
          total_results_found: 1,
          analysis_run: true
        }
      }
    });

    render(<VectorSearch />);
    const searchInput = screen.getByPlaceholderText('Enter your search query');
    // Use a more specific selector for the search button
    const searchButton = screen.getByText('Search');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    await waitFor(() => {
      // Check search results
      expect(screen.getByText('Search Results (1)')).toBeInTheDocument();
      expect(screen.getByText('Test Result 1')).toBeInTheDocument();
      
      // Check both AI analyses
      expect(screen.getByText('Test Groq analysis')).toBeInTheDocument();
      expect(screen.getByText('Test OpenAI analysis')).toBeInTheDocument();
      
      // Check metadata
      expect(screen.getByText('Duration:')).toBeInTheDocument();
      expect(screen.getByText('1.5s', { exact: false })).toBeInTheDocument();
    });
  });

  it('handles AI analysis errors gracefully', async () => {
    // Mock response with error in Groq analysis
    axios.post.mockResolvedValue({
      data: {
        results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }],
        openai_analysis: 'Test OpenAI analysis',
        groq_analysis: 'Error with Groq analysis: Token limit exceeded',
        metadata: {
          search_duration_seconds: 1.5,
          total_results_found: 1,
          analysis_run: true
        }
      }
    });

    render(<VectorSearch />);
    const searchInput = screen.getByPlaceholderText('Enter your search query');
    // Use a more specific selector for the search button
    const searchButton = screen.getByText('Search');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    await waitFor(() => {
      // Check search results still appear
      expect(screen.getByText('Search Results (1)')).toBeInTheDocument();
      expect(screen.getByText('Test Result 1')).toBeInTheDocument();
      
      // Check error message appears for Groq
      expect(screen.getByText('Token limit exceeded', { exact: false })).toBeInTheDocument();
      
      // Check OpenAI analysis still appears
      expect(screen.getByText('Test OpenAI analysis')).toBeInTheDocument();
    });
  });

  it('handles missing AI responses', async () => {
    // Mock response with no AI analysis
    axios.post.mockResolvedValue({
      data: {
        results: [{ id: 1, content: 'Test Result 1', similarity: 0.9 }],
        openai_analysis: '',
        groq_analysis: '',
        metadata: {
          search_duration_seconds: 1.5,
          total_results_found: 1,
          analysis_run: false
        }
      }
    });

    render(<VectorSearch />);
    const searchInput = screen.getByPlaceholderText('Enter your search query');
    // Use a more specific selector for the search button
    const searchButton = screen.getByText('Search');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    await waitFor(() => {
      // Check search results still appear
      expect(screen.getByText('Search Results (1)')).toBeInTheDocument();
      expect(screen.getByText('Test Result 1')).toBeInTheDocument();
      
      // Check AI analysis sections don't appear
      expect(screen.queryByText('OpenAI Analysis:')).not.toBeInTheDocument();
      expect(screen.queryByText('Groq Analysis:')).not.toBeInTheDocument();
    });
  });

  it('handles axios errors', async () => {
    // Mock axios error
    axios.post.mockRejectedValue({
      message: 'Network Error',
      response: {
        data: {
          detail: 'Connection failed'
        }
      }
    });

    render(<VectorSearch />);
    const searchInput = screen.getByPlaceholderText('Enter your search query');
    // Use a more specific selector for the search button
    const searchButton = screen.getByText('Search');

    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      fireEvent.click(searchButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });
  });

  describe('Model Responses', () => {
    it('should handle different model responses', async () => {
      // Mock successful response with different model responses
      axios.post.mockResolvedValue({
        data: {
          results: [{
            content: 'Test content',
            similarity: 0.85,
            source: 'test_source',
            search_method: 'fine_grained'
          }],
          openai_analysis: 'The system uses a multi-tier architecture...',
          groq_analysis: 'System architecture consists of...',
          metadata: {
            search_duration_seconds: 1.5,
            total_results_found: 1,
            analysis_run: true
          }
        }
      });

      render(<VectorSearch />);
      const searchInput = screen.getByPlaceholderText('Enter your search query');
      // Use a more specific selector for the search button
      const searchButton = screen.getByText('Search');

      await act(async () => {
        fireEvent.change(searchInput, { target: { value: 'What is the architecture of the system?' } });
        fireEvent.click(searchButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/multi-tier architecture/)).toBeInTheDocument();
        expect(screen.getByText(/System architecture/)).toBeInTheDocument();
      });
    });
  });
});
