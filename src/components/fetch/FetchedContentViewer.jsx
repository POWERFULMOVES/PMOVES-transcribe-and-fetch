import React from 'react';
import ReactMarkdown from 'react-markdown';
import JsonView from 'react18-json-view';
import 'react18-json-view/src/style.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

// Helper function to detect if content is valid structured JSON (object/array)
// or is already a suitable object/array.
const getStructuredData = (content) => {
  if (typeof content === 'object' && content !== null) {
    // Assuming if it's an object, it's suitable for JsonView.
    // More specific checks could be added here if needed (e.g. to ensure it's a plain object or array).
    return content;
  }
  if (typeof content === 'string') {
    try {
      const parsed = JSON.parse(content);
      // Ensure it's an object or array, not just a JSON primitive like "true" or "123"
      if (parsed && typeof parsed === 'object') {
        return parsed;
      }
    } catch (e) {
      // Not a parsable JSON string
    }
  }
  return null; // Not structured data we can display in JsonView
};

const FetchedContentViewer = ({ fetchedData }) => {
  if (!fetchedData) {
    return null;
  }

  // Assuming 'markdownContent' (or a similar prop like 'content') holds the primary text/JSON data.
  // 'output_type' is a new prop to guide rendering. 'contentType' is existing.
  const { title, markdownContent, pdfUrl, metadata, links, pdf_file_path, output_type, contentType } = fetchedData;

  // Prefer pdfUrl if available, otherwise construct from pdf_file_path using the correct backend endpoint
  const finalPdfUrl = pdfUrl || (pdf_file_path ? `/view-pdf?path=${encodeURIComponent(pdf_file_path)}` : null);
  
  let dataForJsonView = null;
  let markdownStringToRender = null; // Initialize to null, will hold string for ReactMarkdown

  // Use the updated getStructuredData helper on the primary content field
  const structuredContent = getStructuredData(markdownContent);

  if (output_type === 'structured_json') {
    if (structuredContent) {
      dataForJsonView = structuredContent;
    } else {
      // output_type was 'structured_json', but content isn't valid/structured.
      // Fallback: display as raw text if it's a string, or stringified if not.
      // A console warning here could be useful for debugging data inconsistencies.
      // console.warn("FetchedContentViewer: output_type is 'structured_json' but content is not valid JSON or a suitable object.");
      if (typeof markdownContent === 'string') {
        markdownStringToRender = markdownContent;
      } else if (markdownContent != null) { // Check for null/undefined before String()
        markdownStringToRender = String(markdownContent);
      }
    }
  } else {
    // output_type is not 'structured_json' (or undefined).
    // Check if content is incidentally JSON.
    if (structuredContent) {
      dataForJsonView = structuredContent;
    } else if (typeof markdownContent === 'string') {
      // It's a string, and not JSON, so treat as Markdown.
      markdownStringToRender = markdownContent;
    } else if (markdownContent != null) { // Check for null/undefined
        // Content is some other non-JSON, non-string type. Show its string representation.
        markdownStringToRender = String(markdownContent);
    }
  }
  // Note: 'contentType' from fetchedData could be used in the future for more explicit type checking,
  // for now, output_type and content analysis drive the decision.

  return (
    <Card className="mt-6 w-full">
      <CardHeader>
        {title && <CardTitle className="text-2xl font-semibold">{title}</CardTitle>}
      </CardHeader>
      <CardContent>
        {dataForJsonView ? (
          <div className="mt-4">
            <h3 className="text-xl font-semibold mb-2">JSON Content</h3>
            <JsonView
              src={dataForJsonView}
              collapsed={false}    // Expand all nodes by default
              // Default styling is applied via the imported 'react18-json-view/src/style.css'
            />
          </div>
        ) : markdownStringToRender !== null && markdownStringToRender.trim() !== '' ? (
          <div className="prose dark:prose-invert max-w-none mt-4"> {/* Added mt-4 for consistency */}
            <h3 className="text-xl font-semibold mb-2">Markdown Content</h3>
            <ReactMarkdown>{markdownStringToRender}</ReactMarkdown>
          </div>
        ) : null /* No JSON and no Markdown to render from primary content */}

        {finalPdfUrl && (
          <div className="mt-4">
            <h3 className="text-xl font-semibold mb-2">PDF Document</h3>
            <a
              href={finalPdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              View PDF: {pdf_file_path ? pdf_file_path.split('/').pop() : title || 'Document'}
            </a>
            {/* Optional: Embed PDF (more complex)
            <iframe src={finalPdfUrl} width="100%" height="600px" title="PDF Viewer" />
            */}
          </div>
        )}

        {(metadata || links) && (
          <Accordion type="single" collapsible className="w-full mt-4">
            {metadata && Object.keys(metadata).length > 0 && (
              <AccordionItem value="item-metadata">
                <AccordionTrigger>Metadata</AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc pl-5 space-y-1">
                    {Object.entries(metadata).map(([key, value]) => (
                      <li key={key}>
                        <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            )}
            {links && links.length > 0 && (
              <AccordionItem value="item-links">
                <AccordionTrigger>Extracted Links</AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc pl-5 space-y-1">
                    {links.map((link, index) => (
                      <li key={index}>
                        <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline">
                          {link.text || link.url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            )}
          </Accordion>
        )}

        {/* Updated condition for "No viewable content" message */}
        {!dataForJsonView &&
         !(markdownStringToRender && markdownStringToRender.trim() !== '') &&
         !finalPdfUrl &&
         !title &&
         Object.keys(metadata || {}).length === 0 &&
         (links || []).length === 0 && (
          <p className="mt-4">No viewable content fetched or an error occurred.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default FetchedContentViewer;