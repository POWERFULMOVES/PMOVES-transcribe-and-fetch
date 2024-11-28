"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { BACKEND_URL } from '@/lib/constants';

export default function FetchContent() {
  const [activeTab, setActiveTab] = useState("markdown");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fetchState, setFetchState] = useState({
    url: "",
    targetSelector: "",
    excludedSelector: "",
    timeout: 300,
    jsonResponse: false,
    cleanFormat: true,
    result: null
  });

  const handleFetchContent = async () => {
    if (!fetchState.url.trim()) {
      setError("Please enter a URL to fetch content.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(`${BACKEND_URL}/fetch-content`, {
        params: {
          url: fetchState.url,
          json_response: fetchState.jsonResponse,
          timeout: fetchState.timeout,
          target_selector: fetchState.targetSelector,
          excluded_selector: fetchState.excludedSelector,
          clean_format: fetchState.cleanFormat
        }
      });

      setFetchState(prev => ({ ...prev, result: response.data }));
    } catch (error) {
      console.error("Error fetching content:", error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <main className="container mx-auto mt-8 p-4 max-w-4xl">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Web Content Fetcher</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* URL Input */}
            <div className="space-y-2">
              <Label>URL to Fetch</Label>
              <Input
                placeholder="Enter URL to fetch content from"
                value={fetchState.url}
                onChange={(e) => setFetchState(prev => ({ ...prev, url: e.target.value }))}
              />
            </div>

            {/* Advanced Options */}
            <Accordion type="single" collapsible>
              <AccordionItem value="advanced-options">
                <AccordionTrigger>Advanced Options</AccordionTrigger>
                <AccordionContent className="space-y-4">
                  {/* Target Selector */}
                  <div className="space-y-2">
                    <Label>Target Selector</Label>
                    <Input
                      placeholder="CSS Selector (e.g., article, .main-content)"
                      value={fetchState.targetSelector}
                      onChange={(e) => setFetchState(prev => ({ ...prev, targetSelector: e.target.value }))}
                    />
                    <p className="text-sm text-muted-foreground">
                      Specify elements to extract (e.g., article, .main-content)
                    </p>
                  </div>

                  {/* Excluded Selector */}
                  <div className="space-y-2">
                    <Label>Exclude Elements</Label>
                    <Input
                      placeholder="Elements to exclude (e.g., nav, footer, .ads)"
                      value={fetchState.excludedSelector}
                      onChange={(e) => setFetchState(prev => ({ ...prev, excludedSelector: e.target.value }))}
                    />
                    <p className="text-sm text-muted-foreground">
                      Specify elements to remove (e.g., nav, footer, .ads)
                    </p>
                  </div>

                  {/* Timeout Setting */}
                  <div className="space-y-2">
                    <Label>Timeout (seconds)</Label>
                    <Input
                      type="number"
                      min="0"
                      max="300"
                      value={fetchState.timeout}
                      onChange={(e) => setFetchState(prev => ({ ...prev, timeout: e.target.value }))}
                    />
                  </div>

                  {/* Format Options */}
                  <div className="space-y-2">
                    <Label>Response Format</Label>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="json-mode"
                          checked={fetchState.jsonResponse}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, jsonResponse: checked }))}
                        />
                        <Label htmlFor="json-mode">JSON Response</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="clean-mode"
                          checked={fetchState.cleanFormat}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, cleanFormat: checked }))}
                        />
                        <Label htmlFor="clean-mode">Clean Format</Label>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            {/* Fetch Button */}
            <Button
              onClick={handleFetchContent}
              disabled={loading}
              className="w-full"
            >
              {loading ? 'Fetching...' : 'Fetch Content'}
            </Button>

            {/* Error Display */}
            {error && (
              <div className="p-4 rounded-md bg-destructive/10 text-destructive">
                {error}
              </div>
            )}

            {/* Results Display */}
            {fetchState.result && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Fetched Content</CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="markdown">Markdown</TabsTrigger>
                      <TabsTrigger value="pdf">PDF</TabsTrigger>
                    </TabsList>

                    <TabsContent value="markdown">
                      <ScrollArea className="h-[600px] w-full rounded-md border p-4">
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <ReactMarkdown
                            components={{
                              h1: ({node, ...props}) => <h1 className="text-2xl font-bold mb-4" {...props} />,
                              h2: ({node, ...props}) => <h2 className="text-xl font-semibold mb-3" {...props} />,
                              a: ({node, ...props}) => (
                                <a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />
                              ),
                              p: ({node, ...props}) => <p className="mb-4 leading-relaxed" {...props} />,
                              ul: ({node, ...props}) => <ul className="list-disc list-inside mb-4" {...props} />,
                              li: ({node, ...props}) => <li className="mb-2" {...props} />,
                            }}
                          >
                            {typeof fetchState.result.markdown_content === 'object'
                              ? JSON.stringify(fetchState.result.markdown_content, null, 2)
                              : fetchState.result.markdown_content || 'No content fetched yet.'
                            }
                          </ReactMarkdown>
                        </div>
                      </ScrollArea>
                    </TabsContent>

                    <TabsContent value="pdf" className="h-full">
                      {fetchState.result?.pdf_path ? (
                        <div className="w-full min-h-[600px] relative bg-white rounded-md shadow">
                          <iframe
                            src={`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(fetchState.result.pdf_path)}`}
                            className="w-full h-full absolute inset-0 rounded-md"
                            title="PDF Viewer"
                          />
                          <div className="absolute top-4 right-4 space-x-2 z-10">
                            <Button
                              onClick={() => window.open(`${BACKEND_URL}/download-pdf?path=${encodeURIComponent(fetchState.result.pdf_path)}`, '_blank')}
                              variant="secondary"
                              size="sm"
                              className="bg-white/90 hover:bg-white"
                            >
                              Download PDF
                            </Button>
                            <Button
                              onClick={() => window.open(`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(fetchState.result.pdf_path)}`, '_blank')}
                              variant="secondary"
                              size="sm"
                              className="bg-white/90 hover:bg-white"
                            >
                              Open in New Tab
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <p>PDF is being generated...</p>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>

                  {/* File Info Footer */}
                  <div className="mt-4 p-3 bg-muted rounded-md text-sm space-y-2">
                    {fetchState.result.markdown_path && (
                      <p className="text-muted-foreground">
                        📄 Markdown: {fetchState.result.markdown_path}
                      </p>
                    )}
                    {fetchState.result.pdf_path && (
                      <p className="text-muted-foreground">
                        📑 PDF: {fetchState.result.pdf_path}
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      </main>
    </>
  );
}
