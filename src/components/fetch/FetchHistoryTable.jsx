import React, { useCallback } from 'react';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';

const FetchHistoryTable = ({
  fetchHistoryItems,
  loadMore,
  hasMore,
  isLoadingMore,
  onViewItem,
  onDeleteItem,
  onRefetchItem,
}) => {
  const handleCopyUrl = useCallback(async (url) => {
    if (!navigator.clipboard) {
      alert('Clipboard API not available.');
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      alert('URL copied to clipboard!'); // Replace with a proper toast notification
    } catch (err) {
      console.error('Failed to copy URL: ', err);
      alert('Failed to copy URL.'); // Replace with a proper toast notification
    }
  }, []);

  const handleCopyMarkdown = useCallback(async (markdownContent, itemUrl) => {
    if (!markdownContent) {
      alert('No Markdown content available for this item.'); // Replace with a proper toast notification
      return;
    }
    if (!navigator.clipboard) {
      alert('Clipboard API not available.');
      return;
    }
    try {
      await navigator.clipboard.writeText(markdownContent);
      alert('Markdown content copied to clipboard!'); // Replace with a proper toast notification
    } catch (err) {
      console.error('Failed to copy Markdown: ', err);
      alert('Failed to copy Markdown content.'); // Replace with a proper toast notification
    }
  }, []);


  if (!fetchHistoryItems || fetchHistoryItems.length === 0) {
    return <p>No fetch history available.</p>;
  }

  // Assuming 'item.markdown_content' holds the markdown string.
  // If the "View Content" functionality populates a different field or
  // if markdown availability needs to be checked differently, this logic might need adjustment.
  // For now, we rely on 'item.markdown_content' being present and a string.

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>URL</TableHead>
            <TableHead>Fetch Date</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Engine</TableHead>
            <TableHead>Title</TableHead>
            <TableHead className="w-[300px]">Actions</TableHead> {/* Adjusted width for more buttons */}
          </TableRow>
        </TableHeader>
        <TableBody>
          {fetchHistoryItems.map((item) => (
            <TableRow key={item.id || item.url + item.fetched_at} /* Assuming 'id' or a composite key */>
              <TableCell className="max-w-xs truncate" title={item.url}>
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                  {item.url}
                </a>
              </TableCell>
              <TableCell>
                {item.fetched_at ? new Date(item.fetched_at).toLocaleString() : 'N/A'}
              </TableCell>
              <TableCell>{item.status_code || 'N/A'}</TableCell>
              <TableCell>{item.fetching_engine || 'N/A'}</TableCell>
              <TableCell className="max-w-xs truncate" title={item.title}>
                {item.title || 'N/A'}
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-2"> {/* Use flex-wrap and gap for better responsiveness */}
                  <Button variant="outline" size="sm" onClick={() => onViewItem(item)}>
                    View
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyUrl(item.url)}
                    title="Copy URL to clipboard"
                  >
                    Copy URL
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyMarkdown(item.markdown_content || item.content_markdown || item.content, item.url)} // Fallback for markdown field name
                    disabled={!(item.markdown_content || item.content_markdown || item.content)} // Check multiple possible fields
                    title={
                      (item.markdown_content || item.content_markdown || item.content)
                        ? "Copy Markdown to clipboard"
                        : "Markdown not directly available in history list. View item to load full content."
                    }
                  >
                    Copy MD
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => onRefetchItem(item)}>
                    Re-fetch
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => onDeleteItem(item.id)}>
                    Delete
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {hasMore && loadMore && (
        <div className="mt-4 text-center">
          <Button onClick={loadMore} disabled={isLoadingMore}>
            {isLoadingMore ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}
    </div>
  );
};

export default FetchHistoryTable;