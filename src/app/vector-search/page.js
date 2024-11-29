"use client";

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { BACKEND_URL } from '@/lib/constants';

export default function VectorSearch() {
  const [query, setQuery] = useState('');
  const [sections, setSections] = useState([]);
  const [aiResponse, setAiResponse] = useState(null);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [threshold, setThreshold] = useState(0.7);
  const [activeTab, setActiveTab] = useState("results");
  const eventSourceRef = useRef(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSections([]);
      setAiResponse(null);
      setTokenUsage(null);

      // Close any existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Start streaming connection
      const es = new EventSource(`${process.env.NEXT_PUBLIC_BACKEND_URL}/vector-search-stream?query=${encodeURIComponent(query)}&threshold=${threshold}`);
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case "search_results":
            // Handle all search results at once
            const { hybrid, dot_product, keyword, ai_response, token_usage } = data.data;
            
            // Set sections for each search type
            setSections([
              { header: "Hybrid Search Results", results: hybrid, count: hybrid.length },
              { header: "Dot Product Search Results", results: dot_product, count: dot_product.length },
              { header: "Keyword Search Results", results: keyword, count: keyword.length }
            ]);
            
            // Set AI response
            setAiResponse(ai_response);
            
            // Set token usage
            setTokenUsage(token_usage);
            break;
            
          case "error":
            setError(data.data);
            es.close();
            break;
        }
      };

      es.onerror = () => {
        setError("Error connecting to search stream");
        es.close();
        setLoading(false);
      };

    } catch (error) {
      setError(error.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Vector Search</CardTitle>
          <CardDescription>
            Search through video transcripts using semantic similarity
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Enter your search query..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSearch();
                    }
                  }}
                />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={loading}
                className="min-w-[100px]"
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Similarity Threshold: {threshold}</Label>
                <Slider
                  value={[threshold]}
                  onValueChange={(value) => setThreshold(value[0])}
                  min={0}
                  max={1}
                  step={0.1}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="flex-1 space-y-4 p-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList>
                <TabsTrigger value="results">Search Results</TabsTrigger>
                <TabsTrigger value="ai">AI Response</TabsTrigger>
              </TabsList>
              
              <TabsContent value="results">
                <div className="space-y-4">
                  {sections.map((section, index) => (
                    <Accordion key={index} type="single" collapsible>
                      <AccordionItem value={section.header}>
                        <AccordionTrigger>
                          {section.header} ({section.count} results)
                        </AccordionTrigger>
                        <AccordionContent>
                          <ScrollArea className="h-[400px]">
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Source</TableHead>
                                  <TableHead>Similarity</TableHead>
                                  <TableHead>Video ID</TableHead>
                                  <TableHead>Time Range</TableHead>
                                  <TableHead>Content Preview</TableHead>
                                  <TableHead>Source File</TableHead>
                                  <TableHead>Line</TableHead>
                                  <TableHead>Watch URL</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {section.results.map((result, idx) => (
                                  <TableRow key={idx}>
                                    <TableCell>{result.source_type}</TableCell>
                                    <TableCell>{typeof result.similarity === 'number' ? `${(result.similarity * 100).toFixed(2)}%` : result.similarity}</TableCell>
                                    <TableCell>{result.video_id}</TableCell>
                                    <TableCell>{`${result.start_time} → ${result.end_time}`}</TableCell>
                                    <TableCell className="max-w-md">{result.text?.substring(0, 100)}...</TableCell>
                                    <TableCell>{result.metadata?.source_file || 'N/A'}</TableCell>
                                    <TableCell>{result.metadata?.line_number || 'N/A'}</TableCell>
                                    <TableCell>
                                      {result.watch_url && (
                                        <a href={result.watch_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-700">
                                          Watch
                                        </a>
                                      )}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </ScrollArea>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="ai">
                {aiResponse && (
                  <Card>
                    <CardHeader>
                      <CardTitle>AI Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="whitespace-pre-wrap">{aiResponse}</div>
                      {tokenUsage && (
                        <div className="mt-4 text-sm text-gray-500">
                          <p>Tokens sent: {tokenUsage.tokens_sent}</p>
                          <p>Tokens received: {tokenUsage.tokens_received}</p>
                          <p>Estimated cost: ${tokenUsage.estimated_cost.toFixed(6)}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
