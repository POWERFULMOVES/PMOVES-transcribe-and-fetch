"use client";

import { useEffect, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import Image from 'next/image';
import useSSE from '@/hooks/useSSE';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { downloadReducer, initialState as downloadInitialState, ACTIONS } from '../reducers/downloadReducer';
import { BACKEND_URL } from '@/lib/constants';
import { useToast } from "@/components/hooks/use-toast"
import { Checkbox } from '@/components/ui/checkbox';
import useAppConfig from '@/hooks/useAppConfig';

export default function Download() {
  const [url, setUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [downloadFolder, setDownloadFolder] = useState('');
  const [state, dispatch] = useReducer(downloadReducer, downloadInitialState);
  const [options, setOptions] = useState({
    download_dir: '',          // Existing
    playlistStart: '1',        // Existing
    extractAudio: false,       // Merged from formatOptions.extract_audio
    audioFormat: 'mp3',        // Merged from formatOptions.audio_format
    audioQuality: '192',       // Merged from formatOptions.audio_quality
    subtitles: false,          // Merged from formatOptions.write_subtitles
    subtitleLanguage: 'en',    // Merged from formatOptions.subtitle_lang
    format: 'best',            // Default for UI video format
    keepVideo: false,          // Default for UI keep video
    downloadPlaylist: false,   // Default for UI download playlist
    playlistEnd: '',           // Default for UI playlist end
    autoSubtitles: false,      // Default for UI auto subtitles
    embedThumbnail: false,     // Default for UI embed thumbnail
    embedMetadata: false,      // Default for UI embed metadata
  });
  const [downloadedFiles, setDownloadedFiles] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const statusBoxRef = useRef(null);
  const { addToast } = useToast();
  const toast = addToast;
  const { config: appConfig, loading: configLoading, error: configError } = useAppConfig();

  // Set initial downloadFolder from config if not set by user
  useEffect(() => {
    if (!configLoading && appConfig) {
      if (!downloadFolder && appConfig.DEFAULT_DOWNLOADS_DIR) {
        setDownloadFolder(appConfig.DEFAULT_DOWNLOADS_DIR);
        setOptions(prev => ({ ...prev, download_dir: appConfig.DEFAULT_DOWNLOADS_DIR }));
      }
    }
  }, [configLoading, appConfig]);

  const handleOptionChange = (key, value) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  // Fetch video info to display thumbnail and title
  const fetchVideoInfo = async () => {
    if (!url.trim()) return;
    
    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      const response = await axios.post(`${BACKEND_URL}/api/video-info`, { url });
      setVideoInfo(response.data);
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    } catch (error) {
      console.error('Error fetching video info:', error);
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.response?.data?.detail || 'Failed to fetch video info' });
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Debounce URL input for video info fetch
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (url.trim().length > 10) {
        fetchVideoInfo();
      }
    }, 800);
    
    return () => clearTimeout(delayDebounce);
  }, [url]);

  // Add useEffect for auto-scrolling status area
  useEffect(() => {
    // Auto-scroll to the bottom when new updates come in
    if (statusBoxRef.current && state.statusUpdates.length > 0) {
      const scrollArea = statusBoxRef.current.querySelector('.scroll-area-viewport');
      if (scrollArea) {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }
    }
  }, [state.statusUpdates]);

  // Use the standardized SSE hook for download status updates
  const {
    connected: sseConnected,
    error: sseError,
    lastMessage: sseLastMessage,
    connect: connectSSE,
    disconnect: disconnectSSE
  } = useSSE('/api/download-status', {
    autoConnect: false, // We'll connect manually when download starts
    withCredentials: true,
    maxRetries: 3,
    reconnectDelay: 1000,
    timeout: 30000,
    onConnect: () => {
      console.log('SSE connection established for downloads');
      toast({
        title: "Connected to download status",
        description: "Ready to receive updates"
      });
    },
    onMessage: (data) => {
      console.log('SSE download update received:', data);
      
      // Show a toast notification for progress updates (but not too frequently)
      if (data.type === 'progress' && (data.progress % 10 === 0 || data.progress === 100)) {
        toast({
          title: "Download in progress",
          description: `Progress: ${data.progress}%`
        });
      }
      
      if (data.type === 'progress') {
        dispatch({ 
          type: ACTIONS.UPDATE_PROGRESS, 
          payload: {
            progress: data.progress,
            speed: data.speed,
            eta: data.eta,
            filename: data.filename,
            total_size: data.total_size
          }
        });
      }
      
      dispatch({
        type: ACTIONS.ADD_STATUS_UPDATE,
        payload: data.type === 'progress' 
          ? { type: data.type, content: `Downloading: ${data.progress}%` }
          : { type: data.type, content: data.message }
      });
      
      if (data.type === 'complete') {
        toast({
          title: "Download complete",
          description: "Your file has been downloaded successfully"
        });
        dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: false });
        disconnectSSE();
      } else if (data.type === 'error') {
        toast({
          variant: "destructive",
          title: "Download failed",
          description: data.message || "An error occurred during download"
        });
        dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: false });
        disconnectSSE();
      }
    },
    onError: (error) => {
      console.error('SSE connection error:', error);
      
      toast({
        variant: "destructive",
        title: "Connection lost",
        description: "Lost connection to the download status feed"
      });
      
      // Add this to the status updates as well
      dispatch({
        type: ACTIONS.ADD_STATUS_UPDATE,
        payload: { 
          type: 'error', 
          content: 'Connection to download status was lost. The download may still be in progress.' 
        }
      });
    },
    onDisconnect: () => {
      console.log('SSE connection closed');
      // Only update downloading state if it was due to an error, not completion
      if (state.downloading) {
        dispatch({ 
          type: ACTIONS.SET_DOWNLOADING, 
          payload: false 
        });
        dispatch({ 
          type: ACTIONS.ADD_STATUS_UPDATE, 
          payload: { type: 'status', content: 'Connection to server lost' }
        });
      }
    }
  });

  // Update the SSE connection setup
  useEffect(() => {
    // Set up SSE if downloading
    if (state.downloading) {
      connectSSE();
    }
    
    // Cleanup on unmount
    return () => {
      disconnectSSE();
    };
  }, [state.downloading, connectSSE, disconnectSSE]); // Only re-run when downloading state changes

  const handleSelectFolder = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/select-directory`);
      if (response.data && response.data.path) {
        setDownloadFolder(response.data.path);
        setOptions(prev => ({ ...prev, download_dir: response.data.path }));
      }
    } catch (error) {
      console.error('Error selecting directory:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to select directory. Please enter path manually.' 
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.RESET_STATUS });
    dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: true });
    
    // Show immediate feedback
    toast({
      title: "Starting download...",
      description: "Preparing your request"
    });
    
    // Add an immediate status update
    dispatch({
      type: ACTIONS.ADD_STATUS_UPDATE,
      payload: { type: 'status', content: `Preparing to download...` }
    });

    try {
      // Include download_dir in options
      const downloadOptions = {
        ...options,
        download_dir: downloadFolder || options.download_dir
      };
      
      const response = await axios.post(`${BACKEND_URL}/api/download`, {
        url: url,
        options: downloadOptions
      });

      if (response.data.status === 'success') {
        // Update the existing toast
        toast({
          title: "Download started",
          description: `${response.data.title}`
        });
        
        dispatch({
          type: ACTIONS.ADD_STATUS_UPDATE,
          payload: {
            type: 'status',
            content: `Download request accepted: ${response.data.title}`
          }
        });
      }
    } catch (error) {
      console.error("Download error:", error);
      toast({
        variant: "destructive",
        title: "Download failed",
        description: error.response?.data?.detail || "Could not start download"
      });
      
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: error.response?.data?.detail || 'Download failed'
      });
      dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: false });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // List of subtitle language options
  const subtitleLanguages = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'ru', label: 'Russian' },
    { value: 'ja', label: 'Japanese' },
    { value: 'ko', label: 'Korean' },
    { value: 'zh-CN', label: 'Chinese (Simplified)' },
    { value: 'zh-TW', label: 'Chinese (Traditional)' },
    { value: 'ar', label: 'Arabic' },
    { value: 'hi', label: 'Hindi' },
    { value: 'auto', label: 'Auto-detect' },
  ];

  // Add useEffect to monitor status updates and load files when complete
  useEffect(() => {
    // Check if we have a status update and it's a 'complete' type
    if (state.statusUpdates.length > 0) {
      const latestUpdate = state.statusUpdates[state.statusUpdates.length - 1];
      if (latestUpdate && 
          (latestUpdate.type === 'complete' || 
          (typeof latestUpdate === 'string' && latestUpdate.includes('Download complete')))) {
        // Load downloaded files after a short delay
        const timer = setTimeout(() => {
          loadDownloadedFiles();
        }, 1000);
        return () => clearTimeout(timer);
      }
    }
  }, [state.statusUpdates]);

  // Use another useEffect to initialize the file list on component mount
  useEffect(() => {
    // Load downloaded files when component mounts
    loadDownloadedFiles();
  }, []);
  
  // Function to load downloaded files
  const loadDownloadedFiles = async () => {
    setFileLoading(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/api/list-downloads`, {
        params: {
          directory: options.download_dir || ''
        }
      });
      if (response.data && response.data.files) {
        setDownloadedFiles(response.data.files);
      } else {
        setDownloadedFiles([]);
      }
    } catch (error) {
      console.error('Error loading files:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load downloaded files",
      });
      setDownloadedFiles([]);
    } finally {
      setFileLoading(false);
    }
  };
  
  // Function to download a file
  const downloadFile = (filename) => {
    const downloadUrl = `${BACKEND_URL}/api/download-file/${encodeURIComponent(filename)}`;
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast({
      title: "Download started",
      description: `Downloading ${filename}`
    });
  };
  
  // Function to open a file in a new tab
  const openFile = (filename, fileType) => {
    const fileUrl = `${BACKEND_URL}/api/download-file/${encodeURIComponent(filename)}`;
    
    // For video and audio files, we might want to use a media player
    if (fileType === 'Video' || fileType === 'Audio') {
      // Open in a new window with a basic media player
      const newWindow = window.open('', '_blank');
      if (newWindow) {
        newWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>Media Player - ${filename}</title>
            <style>
              body { margin: 0; padding: 0; background: #000; height: 100vh; display: flex; align-items: center; justify-content: center; }
              ${fileType === 'Video' ? 'video' : 'audio'} { max-width: 100%; max-height: 100vh; }
            </style>
          </head>
          <body>
            ${fileType === 'Video' 
              ? `<video controls autoplay src="${fileUrl}">Your browser does not support the video tag.</video>`
              : `<audio controls autoplay src="${fileUrl}">Your browser does not support the audio tag.</audio>`
            }
          </body>
          </html>
        `);
        newWindow.document.close();
      } else {
        // Fallback if popup is blocked
        window.open(fileUrl, '_blank');
      }
    } else {
      // For other file types, just open directly
      window.open(fileUrl, '_blank');
    }
    toast({
      title: `Opening ${fileType.toLowerCase()} file`,
      description: filename
    });
  };

  return (
    <div className="container mx-auto p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>YouTube Video Downloader</CardTitle>
          <CardDescription>Download videos, extract audio, or save subtitles</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* URL Input */}
            <div className="space-y-2">
              <Label htmlFor="url">Video URL</Label>
              <div className="flex gap-2">
                <Input
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter YouTube URL"
                  required
                  className="flex-1"
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={fetchVideoInfo}
                  disabled={!url.trim() || state.loading}
                >
                  Check
                </Button>
              </div>
            </div>

            {/* Video Preview */}
            {videoInfo && (
              <Card className="bg-muted/50 border-dashed">
                <CardContent className="p-4">
                  <div className="flex flex-col sm:flex-row gap-4 items-center">
                    {videoInfo.thumbnail && (
                      <div className="relative w-full sm:w-48 aspect-video rounded-md overflow-hidden">
                        <Image
                          src={videoInfo.thumbnail}
                          alt={videoInfo.title || "Video thumbnail"}
                          fill
                          className="object-cover"
                        />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="font-medium line-clamp-2">{videoInfo.title}</h3>
                      {videoInfo.duration && (
                        <p className="text-sm text-muted-foreground mt-1">
                          Duration: {videoInfo.duration}
                        </p>
                      )}
                      {videoInfo.author && (
                        <p className="text-sm text-muted-foreground">
                          Channel: {videoInfo.author}
                        </p>
                      )}
                      {videoInfo.is_playlist && (
                        <Badge variant="secondary" className="mt-2">
                          Playlist ({videoInfo.playlist_count} videos)
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Download Folder Selection */}
            <div className="space-y-2">
              <Label htmlFor="download_dir">Download Folder</Label>
              <div className="flex gap-2">
                <Input
                  id="download_dir"
                  value={downloadFolder}
                  onChange={(e) => setDownloadFolder(e.target.value)}
                  placeholder={appConfig?.DEFAULT_DOWNLOADS_DIR || "Select or enter download folder path"}
                  className="flex-1"
                  disabled={configLoading}
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleSelectFolder}
                >
                  Browse
                </Button>
              </div>
              {downloadFolder && (
                <p className="text-xs text-muted-foreground">
                  Files will be saved to: {downloadFolder}
                </p>
              )}
            </div>

            {/* Optionally, show loading spinner or message if configLoading */}
            {configLoading && <div className="text-center text-muted-foreground">Loading configuration...</div>}
            {configError && <div className="text-center text-red-500">Failed to load config. Using defaults.</div>}

            {/* Download Options */}
            <Accordion type="single" collapsible defaultValue="options">
              <AccordionItem value="options">
                <AccordionTrigger>Download Options</AccordionTrigger>
                <AccordionContent className="space-y-4">
                  {/* Format Selection */}
                  <div className="space-y-2">
                    <Label>Video Format</Label>
                    <Select value={options.format} onValueChange={(value) => handleOptionChange('format', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select quality" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="best">Best Quality</SelectItem>
                        <SelectItem value="1080p">1080p</SelectItem>
                        <SelectItem value="720p">720p</SelectItem>
                        <SelectItem value="480p">480p</SelectItem>
                        <SelectItem value="360p">360p</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Audio Options */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="extractAudio"
                        checked={options.extractAudio}
                        onCheckedChange={(checked) => handleOptionChange('extractAudio', checked)}
                      />
                      <Label htmlFor="extractAudio">Extract Audio</Label>
                    </div>

                    {options.extractAudio && (
                      <div className="pl-6 space-y-4 border-l-2 border-muted">
                        <div className="space-y-2">
                          <Label>Audio Format</Label>
                          <Select value={options.audioFormat} onValueChange={(value) => handleOptionChange('audioFormat', value)}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="mp3">MP3</SelectItem>
                              <SelectItem value="wav">WAV</SelectItem>
                              <SelectItem value="m4a">M4A</SelectItem>
                              <SelectItem value="aac">AAC</SelectItem>
                              <SelectItem value="opus">Opus</SelectItem>
                              <SelectItem value="vorbis">Vorbis</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Audio Quality (kbps)</Label>
                          <Select value={options.audioQuality} onValueChange={(value) => handleOptionChange('audioQuality', value)}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="320">320</SelectItem>
                              <SelectItem value="256">256</SelectItem>
                              <SelectItem value="192">192</SelectItem>
                              <SelectItem value="128">128</SelectItem>
                              <SelectItem value="96">96</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Switch
                            id="keepVideo"
                            checked={options.keepVideo}
                            onCheckedChange={(checked) => handleOptionChange('keepVideo', checked)}
                          />
                          <Label htmlFor="keepVideo">Keep Video File</Label>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Playlist Options */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="downloadPlaylist"
                        checked={options.downloadPlaylist}
                        onCheckedChange={(checked) => handleOptionChange('downloadPlaylist', checked)}
                      />
                      <Label htmlFor="downloadPlaylist">Download Playlist</Label>
                    </div>

                    {options.downloadPlaylist && (
                      <div className="pl-6 space-y-4 border-l-2 border-muted">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="playlistStart">Start From #</Label>
                            <Input
                              id="playlistStart"
                              type="number"
                              min="1"
                              value={options.playlistStart}
                              onChange={(e) => handleOptionChange('playlistStart', e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="playlistEnd">End At # (Optional)</Label>
                            <Input
                              id="playlistEnd"
                              type="number"
                              min={Number(options.playlistStart)}
                              value={options.playlistEnd}
                              onChange={(e) => handleOptionChange('playlistEnd', e.target.value)}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <Separator />

                  {/* Subtitles Options */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="subtitles"
                        checked={options.subtitles}
                        onCheckedChange={(checked) => handleOptionChange('subtitles', checked)}
                      />
                      <Label htmlFor="subtitles">Download Subtitles</Label>
                    </div>

                    {options.subtitles && (
                      <div className="pl-6 space-y-4 border-l-2 border-muted">
                        <div className="space-y-2">
                          <Label>Subtitle Language</Label>
                          <Select 
                            value={options.subtitleLanguage} 
                            onValueChange={(value) => handleOptionChange('subtitleLanguage', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {subtitleLanguages.map(lang => (
                                <SelectItem key={lang.value} value={lang.value}>
                                  {lang.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div className="space-y-2">
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex items-center space-x-2">
                                  <Switch
                                    id="autoSubtitles"
                                    checked={options.autoSubtitles}
                                    onCheckedChange={(checked) => 
                                      handleOptionChange('autoSubtitles', checked)}
                                  />
                                  <Label htmlFor="autoSubtitles">Include Auto-generated</Label>
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Include automatically generated subtitles if available</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </div>
                      </div>
                    )}
                  </div>

                  <Separator />

                  {/* Additional Options */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="embedThumbnail"
                        checked={options.embedThumbnail}
                        onCheckedChange={(checked) => handleOptionChange('embedThumbnail', checked)}
                      />
                      <Label htmlFor="embedThumbnail">Embed Thumbnail</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="embedMetadata"
                        checked={options.embedMetadata}
                        onCheckedChange={(checked) => handleOptionChange('embedMetadata', checked)}
                      />
                      <Label htmlFor="embedMetadata">Embed Metadata</Label>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            {state.error && (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{state.error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit"
              className="w-full bg-gradient-to-r from-green-500 to-purple-500 hover:from-green-600 hover:to-purple-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out transform hover:scale-105"
              disabled={state.downloading || !url || state.loading}
            >
              {state.loading ? (
                <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
                </>
            ) : state.downloading ? "Downloading..." : "Download"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Status Window */}
      <Card>
        <CardHeader>
          <CardTitle>Download Status</CardTitle>
        </CardHeader>
        <CardContent ref={statusBoxRef}>
          <ScrollArea className="h-[200px] w-full rounded-md border p-4">
            {state.statusUpdates.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400">
                No active downloads
              </div>
            ) : (
              <div className="space-y-2">
                {state.statusUpdates.map((update, index) => {
                  if (update.type === 'error') {
                    return (
                      <div key={index} className="text-sm text-red-600 dark:text-red-400">
                        {update.content}
                      </div>
                    );
                  }
                  if (update.type === 'complete') {
                    return (
                      <div key={index} className="text-sm text-green-600 dark:text-green-400 font-medium">
                        ✓ {update.content}
                        <p className="text-xs text-muted-foreground mt-1">
                          Files saved to: {downloadFolder || options.download_dir || 'downloads'}
                        </p>
                      </div>
                    );
                  }
                  return (
                    <div
                      key={index}
                      className="text-sm"
                    >
                      {update.content}
                    </div>
                  );
                })}

                {state.currentProgress && (
                  <div className="space-y-1 mt-4 bg-muted/30 p-3 rounded-md">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{state.currentProgress.filename}</span>
                      <span className="font-bold">{state.currentProgress.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 overflow-hidden">
                      <div
                        className="h-2.5 rounded-full transition-all duration-300"
                        style={{
                          width: `${state.currentProgress.progress}%`,
                          backgroundColor: 'hsl(var(--page-accent))'
                        }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Speed: {state.currentProgress.speed}</span>
                      <span>Size: {state.currentProgress.total_size}</span>
                      <span>ETA: {state.currentProgress.eta}</span>
                    </div>
                    {state.downloading && state.currentProgress.progress < 100 && (
                      <p className="text-center text-xs text-muted-foreground mt-2">
                        Download in progress. Files will be saved to: {downloadFolder || options.download_dir || 'downloads'}
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Downloaded Files Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Downloaded Files</CardTitle>
          <Button 
            variant="outline" 
            size="sm"
            onClick={loadDownloadedFiles}
            disabled={fileLoading}
          >
            {fileLoading ? "Loading..." : "Refresh"}
          </Button>
        </CardHeader>
        <CardContent>
          {downloadedFiles.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filename</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {downloadedFiles.map((file, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{file.name}</TableCell>
                    <TableCell>
                      <Badge variant={
                        file.type === "Video" ? "default" : 
                        file.type === "Audio" ? "secondary" :
                        file.type === "Subtitle" ? "outline" : "destructive"
                      }>
                        {file.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{file.size}</TableCell>
                    <TableCell>{file.modified}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => openFile(file.name, file.type)}
                        >
                          Open
                        </Button>
                        <Button 
                          variant="secondary" 
                          size="sm"
                          onClick={() => downloadFile(file.name)}
                        >
                          Download
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              {fileLoading ? (
                <p>Loading downloaded files...</p>
              ) : (
                <>
                  <p>No downloaded files found</p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="mt-4"
                    onClick={loadDownloadedFiles}
                  >
                    Refresh
                  </Button>
                </>
              )}
            </div>
          )}
        </CardContent>
        {downloadedFiles.length > 0 && (
          <CardFooter className="bg-muted/50 text-xs text-muted-foreground">
            <div>Files saved to: {downloadedFiles[0]?.path?.split('/').slice(0, -1).join('/') || downloadFolder || 'downloads'}</div>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
