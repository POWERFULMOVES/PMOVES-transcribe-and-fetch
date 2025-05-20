import React from 'react';
import { render, screen } from '@testing-library/react';
import FetchedContentViewer from '../FetchedContentViewer';

// Mock react-markdown (if not already globally mocked via jest.setup.js or a __mocks__ folder)
// jest.mock('react-markdown', () => ({ children }) => <div data-testid="mock-react-markdown">{children}</div>);
// Based on the provided file structure, a __mocks__/react-markdown.js exists, so this explicit mock might not be needed here if Jest picks it up.
// We will rely on the existing mock.

// Mock react18-json-view
jest.mock('react18-json-view', () => ({ src }) => (
  <div data-testid="mock-json-view">
    <pre>{JSON.stringify(src, null, 2)}</pre>
  </div>
));

describe('FetchedContentViewer', () => {
  const mockFetchedDataBasic = {
    title: 'Test Title',
    markdownContent: 'Initial content',
    pdfUrl: null,
    metadata: {},
    links: [],
    pdf_file_path: null,
    output_type: null, // Will be varied per test
    contentType: null, // Can also be varied if needed
  };

  test('Test 9.1: Render JsonView with output_type: \'structured_json\' and valid JSON', () => {
    const jsonData = { key: 'value', nested: { num: 123 } };
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: JSON.stringify(jsonData),
      metadata: { output_type: 'structured_json' },
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByTestId('mock-json-view')).toBeInTheDocument();
    expect(screen.getByText(/"key": "value"/)).toBeInTheDocument();
    expect(screen.queryByTestId('mock-react-markdown')).not.toBeInTheDocument();
  });

  test('Test 9.2: Render JsonView with valid JSON and no output_type hint', () => {
    const jsonData = { item: 'test item', count: 42 };
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: JSON.stringify(jsonData),
      metadata: {}, // No output_type
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByTestId('mock-json-view')).toBeInTheDocument();
    expect(screen.getByText(/"item": "test item"/)).toBeInTheDocument();
    expect(screen.queryByTestId('mock-react-markdown')).not.toBeInTheDocument();
  });

  test('Test 9.3: Render ReactMarkdown with output_type: \'structured_json\' and invalid JSON', () => {
    const invalidJsonString = 'This is not valid JSON {';
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: invalidJsonString,
      metadata: { output_type: 'structured_json' },
    };
    render(<FetchedContentViewer fetchedData={props} />);
    // The component should fall back to rendering the string as Markdown
    // Assuming the mock-react-markdown renders its children
    expect(screen.getByTestId('mock-react-markdown')).toBeInTheDocument();
    expect(screen.getByText(invalidJsonString)).toBeInTheDocument();
    expect(screen.queryByTestId('mock-json-view')).not.toBeInTheDocument();
  });

  test('Test 9.4: Render ReactMarkdown with plain string/Markdown', () => {
    const markdownString = '# Hello Markdown\nThis is a test.';
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: markdownString,
      metadata: {}, // No specific output_type, or could be 'text/markdown'
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByTestId('mock-react-markdown')).toBeInTheDocument();
    expect(screen.getByText(markdownString)).toBeInTheDocument(); // Mock renders children
    expect(screen.queryByTestId('mock-json-view')).not.toBeInTheDocument();
  });

  test('Test 9.5: Render ReactMarkdown with non-string, non-JSON input (e.g., number)', () => {
    const numberContent = 12345;
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: numberContent,
      metadata: {},
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByTestId('mock-react-markdown')).toBeInTheDocument();
    // The component should convert the number to a string
    expect(screen.getByText(String(numberContent))).toBeInTheDocument();
    expect(screen.queryByTestId('mock-json-view')).not.toBeInTheDocument();

    // Test with boolean
    const booleanContent = true;
     const propsBool = {
      ...mockFetchedDataBasic,
      markdownContent: booleanContent,
      metadata: {},
    };
    render(<FetchedContentViewer fetchedData={propsBool} />);
    expect(screen.getByTestId('mock-react-markdown')).toBeInTheDocument();
    expect(screen.getByText(String(booleanContent))).toBeInTheDocument();
  });

  test('Test 9.6: Render PDF link correctly when pdf_file_path is provided', () => {
    const pdfPath = 'path/to/document.pdf';
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: 'Some other content that should not interfere.', // Ensure PDF link is independent
      pdf_file_path: pdfPath,
      metadata: {},
    };
    render(<FetchedContentViewer fetchedData={props} />);
    const pdfLink = screen.getByRole('link', { name: /View PDF: document.pdf/i });
    expect(pdfLink).toBeInTheDocument();
    expect(pdfLink).toHaveAttribute('href', `/view-pdf?path=${encodeURIComponent(pdfPath)}`);
    expect(pdfLink).toHaveAttribute('target', '_blank');
  });

  test('Test 9.6 (variant): Render PDF link correctly when pdfUrl is provided directly', () => {
    const directPdfUrl = 'https://example.com/direct.pdf';
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: null, // No other content
      pdfUrl: directPdfUrl,
      pdf_file_path: 'some/other/path.pdf', // pdfUrl should take precedence
      title: 'Direct PDF Test',
      metadata: {},
    };
    render(<FetchedContentViewer fetchedData={props} />);
    // The link text might use the title if pdf_file_path isn't used for the name part
    const pdfLink = screen.getByRole('link', { name: /View PDF: Direct PDF Test/i });
    expect(pdfLink).toBeInTheDocument();
    expect(pdfLink).toHaveAttribute('href', directPdfUrl);
    expect(pdfLink).toHaveAttribute('target', '_blank');
  });

  test('Renders "No viewable content" message when all data is null or empty', () => {
    const props = {
      title: null,
      markdownContent: null,
      pdfUrl: null,
      metadata: {},
      links: [],
      pdf_file_path: null,
      output_type: null,
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByText(/No viewable content fetched or an error occurred./i)).toBeInTheDocument();
  });

   test('Renders title when provided', () => {
    const props = { ...mockFetchedDataBasic, title: "My Awesome Title" };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.getByText("My Awesome Title")).toBeInTheDocument();
  });

  test('Does not render JsonView or ReactMarkdown if content is null and no output_type hint', () => {
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: null,
       metadata: { output_type: 'structured_json' }, // even with hint, if content is null
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.queryByTestId('mock-json-view')).not.toBeInTheDocument();
    expect(screen.queryByTestId('mock-react-markdown')).not.toBeInTheDocument();
  });
   test('Handles null markdownContent gracefully when output_type is not structured_json', () => {
    const props = {
      ...mockFetchedDataBasic,
      markdownContent: null,
      metadata: {}, // No output_type or other type
    };
    render(<FetchedContentViewer fetchedData={props} />);
    expect(screen.queryByTestId('mock-react-markdown')).not.toBeInTheDocument();
    expect(screen.queryByTestId('mock-json-view')).not.toBeInTheDocument();
    // Check for a "no content" message or ensure it doesn't crash
    // Depending on other props, it might show "No viewable content" or just the title/PDF link etc.
    // For this specific case, with only title from mockFetchedDataBasic, it should not show "No viewable content"
    // but also not render markdown/json.
    expect(screen.getByText(mockFetchedDataBasic.title)).toBeInTheDocument(); // Title should still render
  });

});