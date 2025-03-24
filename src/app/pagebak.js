'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Input,
  Label,
  Slider,
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  ScrollArea,
  ScrollBar,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  Switch,
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
  Checkbox,
} from '@/components/ui';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { BACKEND_URL } from '@/lib/constants';
import { useToast } from '@/components/hooks/use-toast';

const DEFAULT_OBSIDIAN_DIR = '/path/to/obsidian';
const DEFAULT_OUTPUT_DIR = '/path/to/output';

export default function Page() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [webpageUrl, setWebpageUrl] = useState('');
  const [query, setQuery] = useState('');
  const [threshold, setThreshold] = useState(0.7);
  const [activeTab, setActiveTab] = useState('youtube');
  const [youtubeLoading, setYoutubeLoading] = useState(false);
  const [webpageLoading, setWebpageLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [downloadOptions, setDownloadOptions] = useState({
    format: 'mp4',
    quality: 'best',
    subtitles: false,
    audioOnly: false,
    customArgs: '',
  });
  const [config, setConfig] = useState({
    obsidianDir: DEFAULT_OBSIDIAN_DIR,
    outputFolder: DEFAULT_OUTPUT_DIR,
    transcriptionModel: 'faster-whisper',
    useGroq: false,
    showAdvanced: false,
    useSupabase: true,
  });
  const [state, setState] = useState({
    fetchResult: null,
    error: null
  });
  const { toast } = useToast();

  const handleYoutubeProcess = async () => {
    if (!youtubeUrl) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please enter a valid YouTube URL",
      });
      return;
    }

    setYoutubeLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/process-video/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          youtube_video_url: youtubeUrl,
          obsidian_dir: config.obsidianDir,
          output_folder: config.outputFolder,
          transcription_model: config.transcriptionModel,
          use_groq: config.useGroq,
          download_options: downloadOptions,
          use_supabase: config.useSupabase,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setState(prev => ({ ...prev, fetchResult: data }));
      setActiveTab('content');
      toast({
        title: "Success",
        description: `Video processed and saved to ${config.outputFolder}`,
      });
    } catch (error) {
      setState(prev => ({ ...prev, error }));
      toast({
        variant: "destructive",
        title: "Failed to process video",
        description: error.message,
      });
    } finally {
      setYoutubeLoading(false);
    }
  };

  const handleWebpageFetch = async () => {
    if (!webpageUrl) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please enter a valid webpage URL",
      });
      return;
    }

    setWebpageLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/fetch-webpage/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: webpageUrl,
          obsidian_dir: config.obsidianDir,
          output_folder: config.outputFolder,
          use_supabase: config.useSupabase,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setState(prev => ({ ...prev, fetchResult: data }));
      setActiveTab('content');
      toast({
        title: "Success",
        description: `Webpage fetched and saved to ${config.outputFolder}`,
      });
    } catch (error) {
      setState(prev => ({ ...prev, error }));
      toast({
        variant: "destructive",
        title: "Failed to fetch webpage",
        description: error.message,
      });
    } finally {
      setWebpageLoading(false);
    }
  };

  const handleVectorSearch = async () => {
    if (!query) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please enter a search query",
      });
      return;
    }

    setSearchLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/vector-search/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          threshold,
          use_supabase: config.useSupabase,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSearchResults(data.results);
      toast({
        title: "Search Complete",
        description: `Found ${data.results.length} results with similarity above ${threshold}`,
      });
    } catch (error) {
      setState(prev => ({ ...prev, error }));
      toast({
        variant: "destructive",
        title: "Search Failed",
        description: error.message,
      });
    } finally {
      setSearchLoading(false);
    }
  };

  const handleDirectorySelect = async (type) => {
    try {
      const response = await fetch(`${BACKEND_URL}/select-directory`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to select directory');
      }
      
      const { path } = await response.json();
      const configKey = type === 'obsidian' ? 'obsidianDir' : 'outputFolder';
      setConfig(prev => ({
        ...prev,
        [configKey]: path
      }));
      
      toast({
        title: "Directory Selected",
        description: `${type === 'obsidian' ? 'Obsidian' : 'Output'} directory set to: ${path}`,
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Directory Selection Failed",
        description: error.message || "Failed to select directory. Using default path.",
      });
    }
  };

  const handleModelChange = (value) => {
    setConfig(prev => ({ ...prev, transcriptionModel: value }));
    
    if (value !== 'faster-whisper' && !config.useGroq) {
      toast({
        variant: "warning",
        title: "Groq API Required",
        description: "This model requires Groq API. Enabling Groq integration.",
      });
      setConfig(prev => ({ ...prev, useGroq: true }));
    }
  };

  return (
    <ErrorBoundary>
      <main className="flex flex-col items-center justify-center p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full max-w-4xl">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="youtube">YouTube</TabsTrigger>
            <TabsTrigger value="webpage">Webpage</TabsTrigger>
            <TabsTrigger value="content">Content</TabsTrigger>
            <TabsTrigger value="vector-search">Search</TabsTrigger>
          </TabsList>

          {/* YouTube Transcriber Tab */}
          <TabsContent value="youtube">
            <Card>
              <CardHeader>
                <CardTitle>YouTube Video Transcriber</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col space-y-4">
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="Enter YouTube URL..."
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                      />
                    </div>
                    <Button 
                      onClick={handleYoutubeProcess} 
                      disabled={youtubeLoading}
                      className="min-w-[100px]"
                    >
                      {youtubeLoading ? 'Processing...' : 'Process Video'}
                    </Button>
                  </div>

                  {/* YouTube Download Options */}
                  <Accordion type="single" collapsible>
                    <AccordionItem value="download-options">
                      <AccordionTrigger>Download Options (yt-dlp)</AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-4 p-3">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label>Format</Label>
                              <Select
                                value={downloadOptions.format}
                                onValueChange={(value) => setDownloadOptions(prev => ({ ...prev, format: value }))}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select format" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="mp4">MP4</SelectItem>
                                  <SelectItem value="webm">WebM</SelectItem>
                                  <SelectItem value="m4a">M4A (audio)</SelectItem>
                                  <SelectItem value="mp3">MP3 (audio)</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>

                            <div className="space-y-2">
                              <Label>Quality</Label>
                              <Select
                                value={downloadOptions.quality}
                                onValueChange={(value) => setDownloadOptions(prev => ({ ...prev, quality: value }))}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select quality" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="best">Best</SelectItem>
                                  <SelectItem value="1080p">1080p</SelectItem>
                                  <SelectItem value="720p">720p</SelectItem>
                                  <SelectItem value="480p">480p</SelectItem>
                                  <SelectItem value="360p">360p</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Checkbox 
                                id="audio-only" 
                                checked={downloadOptions.audioOnly}
                                onCheckedChange={(checked) => 
                                  setDownloadOptions(prev => ({ 
                                    ...prev, 
                                    audioOnly: checked === true 
                                  }))
                                }
                              />
                              <Label htmlFor="audio-only">Audio Only</Label>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Checkbox 
                                id="subtitles" 
                                checked={downloadOptions.subtitles}
                                onCheckedChange={(checked) => 
                                  setDownloadOptions(prev => ({ 
                                    ...prev, 
                                    subtitles: checked === true 
                                  }))
                                }
                              />
                              <Label htmlFor="subtitles">Download Subtitles</Label>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <Label>Custom yt-dlp Arguments</Label>
                            <Input
                              placeholder="--write-auto-sub --sub-langs all"
                              value={downloadOptions.customArgs}
                              onChange={(e) => setDownloadOptions(prev => ({ ...prev, customArgs: e.target.value }))}
                            />
                            <p className="text-xs text-muted-foreground">
                              Advanced: Add custom yt-dlp command-line arguments
                            </p>
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>

                  {/* Advanced Settings */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>Show Advanced Settings</Label>
                      <Switch
                        checked={config.showAdvanced}
                        onCheckedChange={(checked) => setConfig(prev => ({ ...prev, showAdvanced: checked }))}
                      />
                    </div>

                    {config.showAdvanced && (
                      <div className="space-y-4 p-4 bg-muted rounded-lg">
                        <div className="space-y-2">
                          <Label>Transcription Model</Label>
                          <Select
                            value={config.transcriptionModel}
                            onValueChange={handleModelChange}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select model" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="faster-whisper">Faster Whisper</SelectItem>
                              <SelectItem value="llama-3.3-70b">Llama 3.3 70B (Groq)</SelectItem>
                              <SelectItem value="mixtral">Mixtral (Groq)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label>Use Groq API</Label>
                            <Switch
                              checked={config.useGroq}
                              onCheckedChange={(checked) => setConfig(prev => ({ ...prev, useGroq: checked }))}
                            />
                          </div>
                          {config.useGroq && (
                            <p className="text-sm text-muted-foreground">
                              Using Groq's high-performance API for faster processing
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label>Save to Supabase</Label>
                            <Switch
                              checked={config.useSupabase}
                              onCheckedChange={(checked) => setConfig(prev => ({ ...prev, useSupabase: checked }))}
                            />
                          </div>
                          {config.useSupabase && (
                            <p className="text-sm text-muted-foreground">
                              Saving transcriptions to Supabase for vector search
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label>Obsidian Directory</Label>
                          <div className="flex gap-2">
                            <Input
                              value={config.obsidianDir}
                              onChange={(e) => setConfig(prev => ({ ...prev, obsidianDir: e.target.value }))}
                              placeholder={DEFAULT_OBSIDIAN_DIR}
                            />
                            <Button
                              variant="outline"
                              onClick={() => handleDirectorySelect('obsidian')}
                            >
                              Browse
                            </Button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label>Output Directory</Label>
                          <div className="flex gap-2">
                            <Input
                              value={config.outputFolder}
                              onChange={(e) => setConfig(prev => ({ ...prev, outputFolder: e.target.value }))}
                              placeholder={DEFAULT_OUTPUT_DIR}
                            />
                            <Button
                              variant="outline"
                              onClick={() => handleDirectorySelect('output')}
                            >
                              Browse
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Webpage Fetcher Tab */}
          <TabsContent value="webpage">
            <Card>
              <CardHeader>
                <CardTitle>Fetch Webpage Content</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col space-y-4">
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="Enter webpage URL..."
                        value={webpageUrl}
                        onChange={(e) => setWebpageUrl(e.target.value)}
                      />
                    </div>
                    <Button 
                      onClick={handleWebpageFetch} 
                      disabled={webpageLoading}
                      className="min-w-[100px]"
                    >
                      {webpageLoading ? 'Fetching...' : 'Fetch Content'}
                    </Button>
                  </div>

                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      This will fetch the webpage content and convert it to Markdown and PDF formats using jinai.
                      The content will be saved to your Obsidian directory and the output folder.
                    </p>
                  </div>

                  {config.showAdvanced && (
                    <div className="space-y-4 p-4 bg-muted rounded-lg">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label>Save to Supabase</Label>
                          <Switch
                            checked={config.useSupabase}
                            onCheckedChange={(checked) => setConfig(prev => ({ ...prev, useSupabase: checked }))}
                          />
                        </div>
                        {config.useSupabase && (
                          <p className="text-sm text-muted-foreground">
                            Saving webpage content to Supabase for vector search
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label>Obsidian Directory</Label>
                        <div className="flex gap-2">
                          <Input
                            value={config.obsidianDir}
                            onChange={(e) => setConfig(prev => ({ ...prev, obsidianDir: e.target.value }))}
                            placeholder={DEFAULT_OBSIDIAN_DIR}
                          />
                          <Button
                            variant="outline"
                            onClick={() => handleDirectorySelect('obsidian')}
                          >
                            Browse
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Output Directory</Label>
                        <div className="flex gap-2">
                          <Input
                            value={config.outputFolder}
                            onChange={(e) => setConfig(prev => ({ ...prev, outputFolder: e.target.value }))}
                            placeholder={DEFAULT_OUTPUT_DIR}
                          />
                          <Button
                            variant="outline"
                            onClick={() => handleDirectorySelect('output')}
                          >
                            Browse
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Content Display Tab */}
          <TabsContent value="content">
            <Card>
              <CardHeader>
                <CardTitle>Content Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {state.fetchResult ? (
                  <div className="flex flex-col space-y-4">
                    <Tabs defaultValue="markdown" className="w-full">
                      <TabsList>
                        <TabsTrigger value="markdown">Markdown</TabsTrigger>
                        <TabsTrigger value="pdf">PDF</TabsTrigger>
                        {state.fetchResult.video_info && <TabsTrigger value="video-info">Video Info</TabsTrigger>}
                        {state.fetchResult.webpage_info && <TabsTrigger value="webpage-info">Webpage Info</TabsTrigger>}
                      </TabsList>

                      <TabsContent value="markdown">
                        <div className="flex gap-4">
                          <div className="flex-1">
                            <ReactMarkdown 
                              components={{
                                h1: ({node, ...props}) => (
                                  <h1 className="text-2xl font-bold mb-4" {...props} />
                                ),
                                h2: ({node, ...props}) => (
                                  <h2 className="text-xl font-semibold mb-3" {...props} />
                                ),
                                a: ({node, ...props}) => (
                                  <a 
                                    className="text-primary hover:underline" 
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    {...props}
                                  />
                                ),
                                p: ({node, ...props}) => (
                                  <p className="mb-4 leading-relaxed" {...props} />
                                ),
                                ul: ({node, ...props}) => (
                                  <ul className="list-disc list-inside mb-4" {...props} />
                                ),
                                li: ({node, ...props}) => (
                                  <li className="mb-2" {...props} />
                                ),
                              }}
                            >
                              {typeof state.fetchResult.markdown_content === 'object' 
                                ? JSON.stringify(state.fetchResult.markdown_content, null, 2)
                                : state.fetchResult.markdown_content || 'No content fetched yet.'
                              }
                            </ReactMarkdown>
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="pdf">
                        {state.fetchResult?.pdf_path ? (
                          <div className="w-full min-h-[600px] relative bg-white rounded-md shadow">
                            <iframe
                              src={`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`}
                              className="w-full h-full absolute inset-0 rounded-md"
                              title="PDF Viewer"
                              onError={(e) => {
                                console.error("PDF loading error:", e);
                                toast({
                                  variant: "destructive",
                                  title: "Error",
                                  description: "Error loading PDF. Please try downloading instead.",
                                });
                              }}
                            />
                            <div className="absolute top-4 right-4 space-x-2 z-10">
                              <Button
                                onClick={() => window.open(`${BACKEND_URL}/download-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`, '_blank')}
                                variant="secondary"
                                size="sm"
                                className="bg-white/90 hover:bg-white"
                              >
                                Download PDF
                              </Button>
                              <Button
                                onClick={() => window.open(`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`, '_blank')}
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

                      <TabsContent value="video-info">
                        {state.fetchResult?.video_info ? (
                          <div className="space-y-4 p-4 bg-muted rounded-md">
                            <h3 className="text-lg font-semibold">Video Information</h3>
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium">Title</p>
                                <p className="text-sm">{state.fetchResult.video_info.title}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium">Channel</p>
                                <p className="text-sm">{state.fetchResult.video_info.channel}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium">Duration</p>
                                <p className="text-sm">{state.fetchResult.video_info.duration}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium">Upload Date</p>
                                <p className="text-sm">{state.fetchResult.video_info.upload_date}</p>
                              </div>
                            </div>
                            {state.fetchResult.video_info.description && (
                              <div>
                                <p className="text-sm font-medium">Description</p>
                                <p className="text-sm whitespace-pre-line">{state.fetchResult.video_info.description}</p>
                              </div>
                            )}
                            {state.fetchResult.audio_path && (
                              <div>
                                <p className="text-sm font-medium">Audio File</p>
                                <p className="text-sm">{state.fetchResult.audio_path}</p>
                                <Button
                                  onClick={() => window.open(`${BACKEND_URL}/download-audio?path=${encodeURIComponent(state.fetchResult.audio_path)}`, '_blank')}
                                  variant="outline"
                                  size="sm"
                                  className="mt-2"
                                >
                                  Download Audio
                                </Button>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-muted-foreground">
                            <p>No video information available</p>
                          </div>
                        )}
                      </TabsContent>

                      <TabsContent value="webpage-info">
                        {state.fetchResult?.webpage_info ? (
                          <div className="space-y-4 p-4 bg-muted rounded-md">
                            <h3 className="text-lg font-semibold">Webpage Information</h3>
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium">Title</p>
                                <p className="text-sm">{state.fetchResult.webpage_info.title}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium">URL</p>
                                <p className="text-sm break-all">
                                  <a 
                                    href={state.fetchResult.webpage_info.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-primary hover:underline"
                                  >
                                    {state.fetchResult.webpage_info.url}
                                  </a>
                                </p>
                              </div>
                            </div>
                            {state.fetchResult.webpage_info.description && (
                              <div>
                                <p className="text-sm font-medium">Description</p>
                                <p className="text-sm">{state.fetchResult.webpage_info.description}</p>
                              </div>
                            )}
                            {state.fetchResult.webpage_info.word_count && (
                              <div>
                                <p className="text-sm font-medium">Word Count</p>
                                <p className="text-sm">{state.fetchResult.webpage_info.word_count} words</p>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-muted-foreground">
                            <p>No webpage information available</p>
                          </div>
                        )}
                      </TabsContent>
                    </Tabs>

                    {/* File Info Footer */}
                    <div className="mt-4 p-3 bg-muted rounded-md text-sm space-y-2">
                      {state.fetchResult.markdown_path && (
                        <p className="text-muted-foreground">
                          📄 Markdown: {state.fetchResult.markdown_path}
                        </p>
                      )}
                      {state.fetchResult.pdf_path && (
                        <p className="text-muted-foreground">
                          📑 PDF: {state.fetchResult.pdf_path}
                        </p>
                      )}
                      {state.fetchResult.supabase_id && (
                        <p className="text-muted-foreground">
                          🔍 Saved to Supabase: ID {state.fetchResult.supabase_id}
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>Process a YouTube video or fetch a webpage to view content results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Vector Search Tab */}
          <TabsContent value="vector-search">
            <Card>
              <CardHeader>
                <CardTitle>Supabase Vector Search</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col space-y-4">
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="Enter your search query..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                    </div>
                    <Button 
                      onClick={handleVectorSearch} 
                      disabled={searchLoading}
                      className="min-w-[100px]"
                    >
                      {searchLoading ? 'Searching...' : 'Search'}
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

                {searchResults.length > 0 && (
                  <ScrollArea className="h-[500px] w-full rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Source</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Content</TableHead>
                          <TableHead>Similarity</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {searchResults.map((result, index) => (
                          <TableRow key={index}>
                            <TableCell className="font-medium">
                              {result.video_id ? result.video_id : 
                               result.url ? new URL(result.url).hostname : 'Unknown'}
                            </TableCell>
                            <TableCell>
                              {result.video_id ? 'Video' : 
                               result.url ? 'Webpage' : 'Unknown'}
                            </TableCell>
                            <TableCell className="max-w-md truncate">{result.text}</TableCell>
                            <TableCell>{(result.similarity * 100).toFixed(2)}%</TableCell>
                            <TableCell>
                              {result.watch_url && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  asChild
                                >
                                  <a
                                    href={result.watch_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    Watch
                                  </a>
                                </Button>
                              )}
                              {result.url && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  asChild
                                >
                                  <a
                                    href={result.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    Visit
                                  </a>
                                </Button>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Error Display */}
        {state.error && (
          <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
            <p className="font-semibold">Error:</p>
            <p>{typeof state.error === 'string' ? state.error : (typeof state.error === 'object' ? JSON.stringify(state.error) : 'Unknown error')}</p>
          </div>
        )}
      </main>
    </ErrorBoundary>
  );
}