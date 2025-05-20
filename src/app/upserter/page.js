"use client";

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ReloadIcon, CheckIcon, Cross2Icon, GlobeIcon } from '@radix-ui/react-icons'; // Removed FileTextIcon, VideoIcon, AudioIcon as Dropzone handles previews
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dropzone, DropzoneContent, DropzoneEmptyState } from '@/components/dropzone';
import { useSupabaseUpload } from '@/hooks/use-supabase-upload';
import { useToast } from "@/components/hooks/use-toast";


export default function UpserterPage() {
  const { toast } = useToast();
  // State for URL upload form
  const [urlValue, setUrlValue] = useState('');
  const [urlMetadata, setUrlMetadata] = useState(''); // For URL tab's generic JSON metadata
  const [isUrlProcessing, setIsUrlProcessing] = useState(false);
  const [urlResult, setUrlResult] = useState(null);
  const [urlError, setUrlError] = useState(null);

  // State for File upload metadata form
  const [fileTitle, setFileTitle] = useState('');
  const [fileDescription, setFileDescription] = useState('');
  const [fileAdditionalMetadataJson, setFileAdditionalMetadataJson] = useState(''); // For File tab's generic JSON metadata
  const [fileContentType, setFileContentType] = useState('auto'); // Kept for metadata
  const [fileOverwrite, setFileOverwrite] = useState(false); // Kept for metadata

  // Supabase Upload Hook
  const supabaseUpload = useSupabaseUpload({
    bucketName: 'pmoves-content', // Replace with your actual bucket name
    path: 'uploads', // Optional: path within the bucket
    allowedMimeTypes: ['image/*', 'video/*', 'audio/*', 'application/pdf', 'text/*'],
    maxFiles: 5,
    maxFileSize: 50 * 1024 * 1024, // 50MB
    onUploadSuccess: async (uploadedFileData, uploadedFile) => { // Made async
      console.log('File uploaded to Supabase:', uploadedFileData, uploadedFile);
      
      const fileInfo = uploadedFileData; // fileInfo is from Supabase upload
      const metadata = { // metadata is from the form
        title: fileTitle,
        description: fileDescription,
        contentType: fileContentType,
        overwrite: fileOverwrite,
        originalFileName: uploadedFile.name, // Added for completeness
        originalFileType: uploadedFile.type,   // Added for completeness
        originalFileSize: uploadedFile.size,   // Added for completeness
        additionalMetadata: {},
      };

      if (fileAdditionalMetadataJson.trim()) {
        try {
          metadata.additionalMetadata = JSON.parse(fileAdditionalMetadataJson);
        } catch (e) {
          console.error("Invalid JSON in additional file metadata:", e);
          toast({
            title: "Invalid Metadata JSON",
            description: "The additional metadata is not valid JSON. File data not sent to backend.",
            variant: "destructive",
          });
          return; // Stop processing if JSON is invalid
        }
      }

      console.log('Attempting to send to backend. FileInfo:', fileInfo, 'Metadata:', metadata);
      
      // Notify user that Supabase upload was successful and backend save is next
      toast({
        title: "Supabase Upload Successful",
        description: `${uploadedFile.name} uploaded to storage. Now saving metadata to backend...`,
        variant: "info", // Changed to info to differentiate from final success
      });

      try {
        const response = await fetch('/api/content/upsert/file', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ fileInfo, metadata }),
        });

        const result = await response.json(); // Attempt to parse JSON response for all cases

        if (!response.ok) {
          const errorMessage = result.message || result.detail || `API Error: ${response.status}`;
          throw new Error(errorMessage);
        }

        toast({
          title: "File and metadata successfully saved!",
          description: result.message || `${fileInfo.path || uploadedFile.name} and its metadata have been saved.`,
          variant: "success",
        });
        console.log('Backend save successful:', result);

      } catch (error) {
        console.error('Error sending data to backend API:', error);
        toast({
          title: "Error saving file metadata",
          description: error.message || "An unexpected error occurred while saving to backend.",
          variant: "destructive",
        });
      }
    },
    onUploadError: (error, file) => {
      console.error('Error uploading file to Supabase:', file.name, error);
      toast({
        title: "Upload Failed",
        description: `Failed to upload ${file.name}: ${error.message}`,
        variant: "destructive",
      });
    },
  });
  
  // Handle URL submission
  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    setIsUrlProcessing(true);
    setUrlError(null);
    setUrlResult(null);
    
    try {
      let metadata = {};
      if (urlMetadata.trim()) {
        try {
          metadata = JSON.parse(urlMetadata);
        } catch (err) {
          setUrlError('Invalid JSON in URL metadata field');
          setIsUrlProcessing(false);
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
      
      setUrlResult(data);
      toast({ title: "URL Fetch Successful", description: data.message, variant: "success" });
    } catch (err) {
      setUrlError(err.message);
      toast({ title: "URL Fetch Error", description: err.message, variant: "destructive" });
    } finally {
      setIsUrlProcessing(false);
    }
  };

  // Reset the forms
  const handleReset = (tab) => {
    if (tab === 'url') {
      setUrlValue('');
      setUrlMetadata('');
      setUrlError(null);
      setUrlResult(null);
    } else if (tab === 'file') {
      supabaseUpload.setFiles([]); // Clear files in dropzone
      supabaseUpload.setErrors([]); // Clear errors in dropzone
      // Note: successes are cleared automatically on new upload by the hook
      setFileTitle('');
      setFileDescription('');
      setFileAdditionalMetadataJson('');
      setFileContentType('auto');
      setFileOverwrite(false);
    }
  };
  
  // Effect to display errors from the hook as alerts, if desired, or use toasts
  useEffect(() => {
    if (supabaseUpload.errors && supabaseUpload.errors.length > 0) {
      const errorMessage = supabaseUpload.errors.map(e => `${e.name ? `${e.name}: ` : ''}${e.message}`).join('; ');
      // console.error("File upload errors:", errorMessage);
      // Using toasts now, but could set a general error state for an Alert display
    }
  }, [supabaseUpload.errors]);

  // Effect to display successes from the hook as alerts, if desired, or use toasts
  useEffect(() => {
    if (supabaseUpload.isSuccess) {
        // console.log("All files uploaded successfully via hook.");
        // Using toasts now
    }
  }, [supabaseUpload.isSuccess]);


  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">PMOVES Content Upserter</h1>
      <p className="text-gray-600 mb-8">
        Upload and process various types of content: transcripts, web pages, videos, and more.
      </p>
      
      <Tabs defaultValue="file" className="w-full"> {/* Default to file tab now */}
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="url">Fetch from URL</TabsTrigger>
          <TabsTrigger value="file">Upload File (New Dropzone)</TabsTrigger>
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
                  <Label htmlFor="url-input">URL</Label> {/* Changed id to avoid conflict */}
                  <div className="flex items-center space-x-2">
                    <GlobeIcon className="h-5 w-5 text-gray-400" />
                    <Input
                      id="url-input"
                      placeholder="https://example.com"
                      value={urlValue}
                      onChange={(e) => setUrlValue(e.target.value)}
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="url-metadata">Metadata (Optional JSON)</Label> {/* Changed id */}
                  <Textarea
                    id="url-metadata"
                    placeholder='{"source": "web", "category": "article"}'
                    value={urlMetadata}
                    onChange={(e) => setUrlMetadata(e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button type="button" variant="outline" onClick={() => handleReset('url')}>Reset</Button>
                <Button type="submit" disabled={isUrlProcessing} className="bg-[hsl(var(--page-accent))] text-[hsl(var(--background))] hover:bg-[hsl(var(--page-accent)/0.9)]">
                  {isUrlProcessing ? (
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
                Drag and drop files or click to select files for upload to Supabase Storage.
              </CardDescription>
            </CardHeader>
            {/* Removed form onSubmit={handleFileUpload} as Dropzone handles upload trigger */}
            <CardContent className="space-y-6"> {/* Increased spacing */}
              <Dropzone {...supabaseUpload} className="border-primary/50 hover:border-primary">
                <DropzoneEmptyState />
                <DropzoneContent />
              </Dropzone>

              {/* Metadata Form */}
              <div className="space-y-4 pt-4 border-t">
                <h3 className="text-lg font-medium">File Metadata</h3>
                <div className="space-y-2">
                  <Label htmlFor="file-title">Title</Label>
                  <Input
                    id="file-title"
                    placeholder="Enter a title for the file(s)"
                    value={fileTitle}
                    onChange={(e) => setFileTitle(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="file-description">Description</Label>
                  <Textarea
                    id="file-description"
                    placeholder="Enter a description for the file(s)"
                    value={fileDescription}
                    onChange={(e) => setFileDescription(e.target.value)}
                    className="min-h-[80px]"
                  />
                </div>
                 <div className="space-y-2">
                  <Label htmlFor="file-content-type">Content Type (for backend processing)</Label>
                  <Select value={fileContentType} onValueChange={setFileContentType}>
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
                
                {fileContentType === 'transcript' && (
                  <div className="flex items-center space-x-2 pt-2">
                    <Switch
                      id="file-overwrite"
                      checked={fileOverwrite}
                      onCheckedChange={setFileOverwrite}
                    />
                    <Label htmlFor="file-overwrite">Overwrite existing transcripts (for backend)</Label>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="file-additional-metadata">Additional Metadata (Optional JSON)</Label>
                  <Textarea
                    id="file-additional-metadata"
                    placeholder='{"custom_key": "custom_value", "project_id": 123}'
                    value={fileAdditionalMetadataJson}
                    onChange={(e) => setFileAdditionalMetadataJson(e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-start"> {/* Changed to justify-start for single button */}
              <Button type="button" variant="outline" onClick={() => handleReset('file')}>Reset File Form</Button>
              {/* The "Upload Files" button is now part of DropzoneContent */}
            </CardFooter>
            {/* Form tag removed */}
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Results or error display for URL Fetching */}
      {urlError && (
        <Alert variant="destructive" className="mt-8">
          <Cross2Icon className="h-4 w-4" />
          <AlertTitle>URL Fetch Error</AlertTitle>
          <AlertDescription>{urlError}</AlertDescription>
        </Alert>
      )}
      
      {urlResult && (
        <Alert className="mt-8 border-[hsl(var(--page-accent))] bg-[hsl(var(--page-accent)/0.1)]">
          <CheckIcon className="h-4 w-4 text-[hsl(var(--page-accent))]" />
          <AlertTitle className="text-[hsl(var(--page-accent))]">URL Fetch Success</AlertTitle>
          <AlertDescription>
            <div className="mt-2">
              <p><strong>Status:</strong> {urlResult.status}</p>
              <p><strong>Message:</strong> {urlResult.message}</p>
              {urlResult.result && (
                <>
                  <p><strong>Content ID:</strong> {urlResult.result.content_id}</p>
                  <p><strong>Content Type:</strong> {urlResult.result.content_type}</p>
                  {urlResult.result.title && <p><strong>Title:</strong> {urlResult.result.title}</p>}
                </>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}
      {/* Note: File upload success/error is handled by toasts via useSupabaseUpload hook callbacks */}
    </div>
  );
}