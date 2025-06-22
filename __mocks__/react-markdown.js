// Mock implementation of react-markdown
import React from 'react';

const ReactMarkdown = ({ children }) => {
  // Render children directly, wrapped in a div with the data-testid
  // This allows tests to assert that ReactMarkdown was rendered and to check its content.
  return <div data-testid="mock-react-markdown">{children}</div>;
};

module.exports = ReactMarkdown;
