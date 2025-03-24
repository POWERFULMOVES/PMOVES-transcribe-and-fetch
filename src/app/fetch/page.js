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
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
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
    excludedSelector: "header,footer,nav,aside,script,style",
    timeout: 300,
    jsonResponse: false,
    cleanFormat: true,
    // Advanced Jina.ai options
    browserEngine: "playwright", // or selenium
    tokenBudget: 4000,
    removeImages: false,
    extractLinks: true,
    imageCaptioning: false,
    cacheTtl: 3600,
    markdownFlavor: "github",
    browserViewport: "1920x1080",
    browserLocale: "en-US",
    extractMetadata: true,
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
          clean_format: fetchState.cleanFormat,
          // Advanced Jina.ai options
          browser_engine: fetchState.browserEngine,
          token_budget: fetchState.tokenBudget,
          remove_images: fetchState.removeImages,
          extract_links: fetchState.extractLinks,
          image_captioning: fetchState.imageCaptioning,
          cache_ttl: fetchState.cacheTtl,
          markdown_flavor: fetchState.markdownFlavor,
          browser_viewport: fetchState.browserViewport,
          browser_locale: fetchState.browserLocale,
          extract_metadata: fetchState.extractMetadata
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
              <CardTitle>Advanced Web Content Fetcher</CardTitle>
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
                  {/* Basic Options */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Browser Engine Selection */}
                    <div className="space-y-2">
                      <Label>Browser Engine</Label>
                      <Select 
                        value={fetchState.browserEngine} 
                        onValueChange={(value) => setFetchState(prev => ({ ...prev, browserEngine: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select browser engine" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="playwright">Playwright (Better Quality)</SelectItem>
                          <SelectItem value="selenium">Selenium (Faster)</SelectItem>
                        </SelectContent>
                      </Select>
                      <p className="text-sm text-muted-foreground">
                        Playwright offers better quality, Selenium is faster
                      </p>
                    </div>

                    {/* Token Budget */}
                    <div className="space-y-2">
                      <Label>Token Budget</Label>
                      <Input
                        type="number"
                        min="1000"
                        max="100000"
                        value={fetchState.tokenBudget}
                        onChange={(e) => setFetchState(prev => ({ ...prev, tokenBudget: e.target.value }))}
                      />
                      <p className="text-sm text-muted-foreground">
                        Maximum number of tokens to extract (1,000-100,000)
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Viewport Setting */}
                    <div className="space-y-2">
                      <Label>Browser Viewport</Label>
                      <Select 
                        value={fetchState.browserViewport} 
                        onValueChange={(value) => setFetchState(prev => ({ ...prev, browserViewport: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select viewport size" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1920x1080">Desktop (1920x1080)</SelectItem>
                          <SelectItem value="1366x768">Laptop (1366x768)</SelectItem>
                          <SelectItem value="768x1024">Tablet (768x1024)</SelectItem>
                          <SelectItem value="375x812">Mobile (375x812)</SelectItem>
                        </SelectContent>
                      </Select>
                      <p className="text-sm text-muted-foreground">
                        Browser viewport size for rendering the page
                      </p>
                    </div>

                    {/* Markdown Flavor */}
                    <div className="space-y-2">
                      <Label>Markdown Flavor</Label>
                      <Select 
                        value={fetchState.markdownFlavor} 
                        onValueChange={(value) => setFetchState(prev => ({ ...prev, markdownFlavor: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select markdown flavor" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="github">GitHub Flavored</SelectItem>
                          <SelectItem value="standard">Standard Markdown</SelectItem>
                          <SelectItem value="obsidian">Obsidian Compatible</SelectItem>
                        </SelectContent>
                      </Select>
                      <p className="text-sm text-muted-foreground">
                        Format of the markdown output
                      </p>
                    </div>
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

                  {/* Format Toggles */}
                  <div className="space-y-4">
                    <Label>Content Options</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="extract-links"
                          checked={fetchState.extractLinks}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, extractLinks: checked }))}
                        />
                        <Label htmlFor="extract-links">Extract Links</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="extract-metadata"
                          checked={fetchState.extractMetadata}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, extractMetadata: checked }))}
                        />
                        <Label htmlFor="extract-metadata">Extract Metadata</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="remove-images"
                          checked={fetchState.removeImages}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, removeImages: checked }))}
                        />
                        <Label htmlFor="remove-images">Remove Images</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="image-captioning"
                          checked={fetchState.imageCaptioning}
                          onCheckedChange={(checked) => setFetchState(prev => ({ ...prev, imageCaptioning: checked }))}
                        />
                        <Label htmlFor="image-captioning">Image Captioning</Label>
                      </div>
                    </div>
                  </div>

                  {/* Response Format */}
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
                        <div className="text-center py-8 text-muted-foreground space-y-4">
                          <p className="text-amber-600">PDF generation failed or is unavailable</p>
                          <p>You can still view and download the content in the Markdown tab.</p>
                          <div className="py-4">
                            <p className="text-sm">To enable PDF generation, install wkhtmltopdf:</p>
                            <a 
                              href="https://wkhtmltopdf.org/downloads.html" 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary hover:underline text-sm"
                            >
                              Download wkhtmltopdf
                            </a>
                          </div>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>

                  {/* File and Metadata Info */}
                  <div className="mt-4 space-y-4">
                    {/* File Paths */}
                    <div className="p-3 bg-muted rounded-md text-sm space-y-2">
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
                    
                    {/* Metadata Display */}
                    {fetchState.result.metadata && (
                      <Accordion type="single" collapsible className="w-full">
                        <AccordionItem value="metadata">
                          <AccordionTrigger>Page Metadata</AccordionTrigger>
                          <AccordionContent>
                            <div className="text-sm bg-muted/50 p-3 rounded-md space-y-2">
                              {Object.entries(fetchState.result.metadata).map(([key, value]) => (
                                <div key={key} className="grid grid-cols-3 gap-2">
                                  <span className="font-medium">{key}:</span>
                                  <span className="col-span-2">{typeof value === 'string' ? value : JSON.stringify(value)}</span>
                                </div>
                              ))}
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    )}
                    
                    {/* Extracted Links */}
                    {fetchState.result.links && fetchState.result.links.length > 0 && (
                      <Accordion type="single" collapsible className="w-full">
                        <AccordionItem value="links">
                          <AccordionTrigger>Extracted Links ({fetchState.result.links.length})</AccordionTrigger>
                          <AccordionContent>
                            <ScrollArea className="h-[200px]">
                              <div className="space-y-2">
                                {fetchState.result.links.map((link, index) => (
                                  <div key={index} className="text-sm border-b pb-2">
                                    <a 
                                      href={link.url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="text-primary hover:underline"
                                    >
                                      {link.text || link.url}
                                    </a>
                                  </div>
                                ))}
                              </div>
                            </ScrollArea>
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
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
