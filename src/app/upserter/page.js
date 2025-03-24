"use client";

import React, { useState, useRef } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ReloadIcon, CheckIcon, Cross2Icon, GlobeIcon, FileTextIcon, VideoIcon, AudioIcon } from '@radix-ui/react-icons';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function UpserterPage() {
  // State for different upload forms
  const [urlValue, setUrlValue] = useState('');
  const [urlMetadata, setUrlMetadata] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [contentType, setContentType] = useState('auto');
  const [overwrite, setOverwrite] = useState(false);
  
  // File upload ref
  const fileInputRef = useRef(null);
  
  // Handle URL submission
  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    setIsUploading(true);
    setError(null);
    setResult(null);
    
    try {
      // Parse metadata JSON if provided
      let metadata = {};
      if (urlMetadata.trim()) {
        try {
          metadata = JSON.parse(urlMetadata);
        } catch (err) {
          setError('Invalid JSON in metadata field');
          setIsUploading(false);
          return;
        }
      }
      
      const response = await fetch('/api/content/upsert/fetch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: urlValue,
          metadata
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Error processing URL');
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };
  
  // Handle file upload
  const handleFileUpload = async (e) => {
    e.preventDefault();
    const files = fileInputRef.current.files;
    
    if (!files || files.length === 0) {
      setError('Please select a file to upload');
      return;
    }
    
    setIsUploading(true);
    setError(null);
    setResult(null);
    
    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    if (contentType !== 'auto') {
      formData.append('content_type', contentType);
    }
    
    // Add metadata if provided
    if (urlMetadata.trim()) {
      try {
        const metadata = JSON.parse(urlMetadata);
        formData.append('metadata_json', JSON.stringify(metadata));
      } catch (err) {
        setError('Invalid JSON in metadata field');
        setIsUploading(false);
        return;
      }
    }
    
    try {
      // Use the transcript endpoint for transcript files with overwrite option
      const endpoint = contentType === 'transcript' 
        ? `/api/content/upsert/transcript?force_overwrite=${overwrite}` 
        : '/api/content/upsert/file';
        
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Error processing file');
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };
  
  // Reset the form
  const handleReset = () => {
    setUrlValue('');
    setUrlMetadata('');
    setContentType('auto');
    setOverwrite(false);
    setError(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">PMOVES Content Upserter</h1>
      <p className="text-gray-600 mb-8">
        Upload and process various types of content: transcripts, web pages, videos, and more.
      </p>
      
      <Tabs defaultValue="url" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="url">Fetch from URL</TabsTrigger>
          <TabsTrigger value="file">Upload File</TabsTrigger>
        </TabsList>
        
        <TabsContent value="url">
          <Card>
            <CardHeader>
              <CardTitle>Fetch Content from URL</CardTitle>
              <CardDescription>
                Enter a URL to fetch and process the content. Works with web pages, YouTube videos, and more.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleUrlSubmit}>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="url">URL</Label>
                  <div className="flex items-center space-x-2">
                    <GlobeIcon className="h-5 w-5 text-gray-400" />
                    <Input 
                      id="url" 
                      placeholder="https://example.com" 
                      value={urlValue}
                      onChange={(e) => setUrlValue(e.target.value)}
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="metadata">Metadata (Optional JSON)</Label>
                  <Textarea 
                    id="metadata" 
                    placeholder='{"title": "Custom Title", "tags": ["example", "test"]}'
                    value={urlMetadata}
                    onChange={(e) => setUrlMetadata(e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button type="button" variant="outline" onClick={handleReset}>Reset</Button>
                <Button type="submit" disabled={isUploading}>
                  {isUploading ? (
                    <>
                      <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                      Fetching...
                    </>
                  ) : (
                    'Fetch and Process'
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
        
        <TabsContent value="file">
          <Card>
            <CardHeader>
              <CardTitle>Upload Content File</CardTitle>
              <CardDescription>
                Upload a file to process. Supports transcripts, videos, audio, and text files.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleFileUpload}>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="file">File</Label>
                  <Input 
                    id="file" 
                    type="file" 
                    ref={fileInputRef}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="content-type">Content Type</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Auto-detect" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto-detect</SelectItem>
                      <SelectItem value="transcript">Transcript</SelectItem>
                      <SelectItem value="webpage">Web Page</SelectItem>
                      <SelectItem value="text">Text</SelectItem>
                      <SelectItem value="video">Video</SelectItem>
                      <SelectItem value="audio">Audio</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {contentType === 'transcript' && (
                  <div className="flex items-center space-x-2">
                    <Switch 
                      id="overwrite" 
                      checked={overwrite}
                      onCheckedChange={setOverwrite}
                    />
                    <Label htmlFor="overwrite">Overwrite existing transcripts</Label>
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="file-metadata">Metadata (Optional JSON)</Label>
                  <Textarea 
                    id="file-metadata" 
                    placeholder='{"title": "Custom Title", "tags": ["example", "test"]}'
                    value={urlMetadata}
                    onChange={(e) => setUrlMetadata(e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button type="button" variant="outline" onClick={handleReset}>Reset</Button>
                <Button type="submit" disabled={isUploading}>
                  {isUploading ? (
                    <>
                      <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    'Upload and Process'
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Results or error display */}
      {error && (
        <Alert variant="destructive" className="mt-8">
          <Cross2Icon className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {result && (
        <Alert className="mt-8 bg-green-50 border-green-200">
          <CheckIcon className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-800">Success</AlertTitle>
          <AlertDescription>
            <div className="mt-2">
              <p><strong>Status:</strong> {result.status}</p>
              <p><strong>Message:</strong> {result.message}</p>
              {result.result && (
                <>
                  <p><strong>Content ID:</strong> {result.result.content_id}</p>
                  <p><strong>Content Type:</strong> {result.result.content_type}</p>
                  {result.result.title && <p><strong>Title:</strong> {result.result.title}</p>}
                </>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
} 