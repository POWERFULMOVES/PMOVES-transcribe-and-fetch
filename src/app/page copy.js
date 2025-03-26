"use client";

import React, { useEffect, useCallback, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ScrollArea,
  ScrollBar,
} from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";

const BACKEND_URL = 'http://127.0.0.1:8000';

const ACTIONS = {
  SET_YOUTUBE_URL: 'SET_YOUTUBE_URL',
  SET_OBSIDIAN_DIR: 'SET_OBSIDIAN_DIR',
  SET_OUTPUT_FOLDER: 'SET_OUTPUT_FOLDER',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_PROCESS_RESULT: 'SET_PROCESS_RESULT',
  SET_TRANSCRIBING: 'SET_TRANSCRIBING',
  ADD_STATUS_UPDATE: 'ADD_STATUS_UPDATE',
  SET_ACTIVE_STEP: 'SET_ACTIVE_STEP',
  RESET_TRANSCRIPTION: 'RESET_TRANSCRIPTION',
  SET_TRANSCRIPTION_MODEL: 'SET_TRANSCRIPTION_MODEL',
  SET_TAB_VALUE: 'SET_TAB_VALUE',
  SET_FETCH_URL: 'SET_FETCH_URL',
  SET_FETCH_RESULT: 'SET_FETCH_RESULT',
  SET_JSON_RESPONSE: 'SET_JSON_RESPONSE',
  SET_TARGET_SELECTOR: 'SET_TARGET_SELECTOR',
  ADD_TRANSCRIPTION_SEGMENT: 'ADD_TRANSCRIPTION_SEGMENT',
  SET_COMPLETED_TRANSCRIPTION: 'SET_COMPLETED_TRANSCRIPTION',
  SET_DEVICE_INFO: 'SET_DEVICE_INFO',
  SET_WHISPER_MODEL_SIZE: 'SET_WHISPER_MODEL_SIZE',
  SET_DRAWER_OPEN: 'SET_DRAWER_OPEN',
  SET_TIMEOUT: 'SET_TIMEOUT'
};

const initialState = {
  youtubeUrl: '',
  obsidianDir: 'J:\\My Drive\\CataclysmstudiosInc\\POWERFULMOVES\\005 - Transcriptions',
  fetchUrl: '',
  statusUpdates: [],
  transcriptionSegments: [],
  completedTranscription: '',
  loading: false,
  transcribing: false,
  tabValue: 0,
  error: null,
  drawerOpen: false,
  activeStep: 0,
  elapsedTime: 0,
  processResult: {},
  outputFolder: 'M:\\PMOVEStransciber\\output',
  jsonResponse: false,
  timeout: null,
  targetSelector: '',
  transcriptionModel: 'faster-whisper',
  whisperModelSize: 'large-v3',
  deviceInfo: null
};

function reducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_YOUTUBE_URL:
      return { ...state, youtubeUrl: action.payload };
    case ACTIONS.SET_OBSIDIAN_DIR:
      return { ...state, obsidianDir: action.payload };
    case ACTIONS.SET_OUTPUT_FOLDER:
      return { ...state, outputFolder: action.payload };
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload };
    case ACTIONS.SET_PROCESS_RESULT:
      return { ...state, processResult: action.payload };
    case ACTIONS.SET_TRANSCRIBING:
      return { ...state, transcribing: action.payload };
    case ACTIONS.ADD_STATUS_UPDATE:
      return { ...state, statusUpdates: [...state.statusUpdates, action.payload] };
    case ACTIONS.SET_ACTIVE_STEP:
      return { ...state, activeStep: action.payload };
    case ACTIONS.RESET_TRANSCRIPTION:
      return { ...state, transcriptionSegments: [], completedTranscription: null };
    case ACTIONS.SET_TRANSCRIPTION_MODEL:
      return { ...state, transcriptionModel: action.payload };
    case ACTIONS.SET_TAB_VALUE:
      return { ...state, tabValue: action.payload };
    case ACTIONS.SET_FETCH_URL:
      return { ...state, fetchUrl: action.payload };
    case ACTIONS.SET_FETCH_RESULT:
      return { ...state, fetchResult: action.payload };
    case ACTIONS.SET_JSON_RESPONSE:
      return { ...state, jsonResponse: action.payload };
    case ACTIONS.SET_TARGET_SELECTOR:
      return { ...state, targetSelector: action.payload };
    case ACTIONS.ADD_TRANSCRIPTION_SEGMENT:
      return {
        ...state,
        transcriptionSegments: [...state.transcriptionSegments, action.payload]
      };
    case ACTIONS.SET_COMPLETED_TRANSCRIPTION:
      return {
        ...state,
        completedTranscription: action.payload
      };
    case ACTIONS.SET_DEVICE_INFO:
      return {
        ...state,
        deviceInfo: action.payload
      };
    case ACTIONS.SET_WHISPER_MODEL_SIZE:
      return {
        ...state,
        whisperModelSize: action.payload
      };
    case ACTIONS.SET_DRAWER_OPEN:
      return {
        ...state,
        drawerOpen: action.payload
      };
    case ACTIONS.SET_TIMEOUT:
      return {
        ...state,
        timeout: action.payload
      };
    default:
      return state;
  }
}

const steps = [
  'Enter YouTube URL',
  'Process Video',
  'Transcribe Audio',
  'Transcription Complete'
];

const validateYoutubeUrl = (url) => {
  const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
  return pattern.test(url);
};

const validateObsidianDir = (dir) => {
  return dir && dir.trim().length > 0;
};

const sanitizeInput = (input) => {
  return input.trim();
};

// Add this function before the Home component
const testBackendConnection = async (dispatch) => {
  try {
    console.log("Attempting to connect to backend...");
    const response = await axios.get(`${BACKEND_URL}/`);
    console.log("Backend connection successful:", response.data);
    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Connected to backend' });
  } catch (error) {
    console.error("Error connecting to backend:", error);
    if (error.response) {
      console.error("Response data:", error.response.data);
      console.error("Response status:", error.response.status);
      console.error("Response headers:", error.response.headers);
    } else if (error.request) {
      console.error("No response received:", error.request);
    } else {
      console.error("Error setting up request:", error.message);
    }
    dispatch({ type: ACTIONS.SET_ERROR, payload: `Failed to connect to backend: ${error.message}` });
  }
};

export default function Home() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [activeTab, setActiveTab] = useState("status");
  const transcriptionBoxRef = useRef(null);
  const paperRef = useRef(null);
  let resizeObserver;
  let rafId;
  const eventSource = useRef(null);

  useEffect(() => {
    const handleResize = () => {
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
      rafId = window.requestAnimationFrame(() => {
        // Add your resize logic here if needed
      });
    };

    if (paperRef.current) {
      resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(paperRef.current);
    }

    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
    };
  }, []);

  // Validation functions
  const validateYoutubeUrl = (url) => {
    const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return regex.test(url);
  };

  const validateObsidianDir = (dir) => {
    return dir && dir.trim().length > 0;
  };

  // Input sanitization function
  const sanitizeInput = (input) => {
    return input.replace(/[<>]/g, "");
  };

  // Function to handle fetching content
  const handleFetchContent = async () => {
    const sanitizedFetchUrl = sanitizeInput(state.fetchUrl);

    if (!sanitizedFetchUrl.trim()) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: "Please enter a URL to fetch content." });
      return;
    }

    try {
      dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Fetching content...' });
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: ACTIONS.SET_ERROR, payload: null });

      console.log("Backend URL:", BACKEND_URL);

      const response = await axios.get(`${BACKEND_URL}/fetch-content`, {
        params: {
          url: sanitizedFetchUrl,
          json_response: true,
          timeout: state.timeout,
          target_selector: state.targetSelector
        }
      });

      console.log("Fetch Result:", response.data);

      if (response.data.markdown_path) {
        try {
          const markdownResponse = await axios.get(`${BACKEND_URL}/fetch-markdown`, {
            params: { path: response.data.markdown_path }
          });
          console.log("Fetched Markdown Content:", markdownResponse.data);

          dispatch({ type: ACTIONS.SET_FETCH_RESULT, payload: markdownResponse.data });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Markdown content fetched successfully.' });
        } catch (markdownError) {
          console.error("Error fetching Markdown content:", markdownError);
          dispatch({ type: ACTIONS.SET_ERROR, payload: `Error fetching Markdown content: ${markdownError.message}` });
        }
      } else {
        console.warn("No markdown_path found in the response.");
        dispatch({ type: ACTIONS.SET_ERROR, payload: "No Markdown path provided in response." });
      }

      dispatch({ type: ACTIONS.SET_TAB_VALUE, payload: 2 });

    } catch (error) {
      console.error("Error fetching content:", error);
      const errorDetail = error.response?.data?.detail || error.message;
      dispatch({ type: ACTIONS.SET_ERROR, payload: `Error fetching content: ${errorDetail}` });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Function to handle video processing
  const handleProcessVideo = async () => {
    if (!validateYoutubeUrl(state.youtubeUrl)) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: "Please enter a valid YouTube URL" });
      return;
    }

    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: ACTIONS.SET_ERROR, payload: null });
      dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
      dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
      
      const response = await axios.post(`${BACKEND_URL}/process-video/`, {
        youtube_video_url: state.youtubeUrl,
        obsidian_dir: state.obsidianDir,
        output_folder: state.outputFolder,
        transcription_model: state.transcriptionModel
      });

      console.log('Process video response:', response.data);
      
      // Set up EventSource for real-time updates
      if (eventSource.current) {
        eventSource.current.close();
      }

      const source = new EventSource(`${BACKEND_URL}/combined-updates/`);
      source.onmessage = handleEventSourceMessage;
      source.onerror = (error) => {
        console.error('EventSource failed:', error);
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Connection to server lost. Please try again.' });
        source.close();
      };
      eventSource.current = source;

    } catch (error) {
      console.error('Error processing video:', error);
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.response?.data?.detail || 'Error processing video' });
      dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Function to handle directory selection
  const handleSelectOutputFolder = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.onchange = (event) => {
      const files = event.target.files;
      if (files.length > 0) {
        const path = files[0].webkitRelativePath.split('/')[0];
        dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: path });
      }
    };
    input.click();
  };

  // Function to format elapsed time
  const formatElapsedTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Auto-scroll effect for transcription
  useEffect(() => {
    if (state.transcriptionSegments.length > 0 && transcriptionBoxRef.current) {
      transcriptionBoxRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [state.transcriptionSegments]);

  // Add the handleEventSourceMessage callback
  const handleEventSourceMessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received SSE message:', data);  // Debug log

      if (data.source === 'status') {
        // Handle status updates
        if (data.type === 'status') {
          dispatch({ type: ACTIONS.SET_STATUS, payload: data.content });
        }
      } else if (data.source === 'transcription') {
        // Handle transcription updates
        if (data.type === 'transcription_segment') {
          dispatch({ 
            type: ACTIONS.ADD_TRANSCRIPTION, 
            payload: data.content 
          });
          // Scroll to bottom of transcription
          const transcriptionElement = document.getElementById('live-transcription');
          if (transcriptionElement) {
            transcriptionElement.scrollTop = transcriptionElement.scrollHeight;
          }
        }
      }
    } catch (error) {
      console.error('Error handling SSE message:', error);
      console.log('Raw event data:', event.data);
    }
  };

  // In your useEffect or component setup
  useEffect(() => {
    if (state.transcribing) {
      const source = new EventSource(`${BACKEND_URL}/combined-updates/`);
      source.onmessage = handleEventSourceMessage;
      source.onerror = (error) => {
        console.error('EventSource failed:', error);
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Connection to server lost' });
        source.close();
      };
      eventSource.current = source;

      return () => {
        if (eventSource.current) {
          eventSource.current.close();
        }
      };
    }
  }, [state.transcribing]);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get(BACKEND_URL);
        console.log("Backend connected:", response.data);
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Connected to backend' });
      } catch (error) {
        console.error("Backend connection failed:", error);
        dispatch({ type: ACTIONS.SET_ERROR, payload: `Failed to connect to backend: ${error.message}` });
      }
    };

    testConnection();
  }, []);

  // Update the timer effect
  useEffect(() => {
    let timer;
    if (state.transcribing) {
      timer = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      setElapsedTime(0); // Reset timer when transcription stops
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [state.transcribing]);

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground p-4 shadow-md">
        <h1 className="text-3xl font-bold text-center">YouTube Transcriber & Content Fetcher</h1>
      </header>

      <main className="container mx-auto mt-8 p-4 max-w-3xl">
        {/* Progress Steps */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div className={`rounded-full w-8 h-8 flex items-center justify-center ${
                    state.activeStep >= index 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted text-muted-foreground'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="text-sm mt-2 text-muted-foreground">{step}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Form */}
        <Card>
          <CardContent className="space-y-4 pt-6">
            {/* Model Selection */}
            <div className="space-y-2">
              <Label>Transcription Model</Label>
              <Select
                value={state.transcriptionModel}
                onValueChange={(value) => dispatch({ type: ACTIONS.SET_TRANSCRIPTION_MODEL, payload: value })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="faster-whisper">Faster Whisper (large-v3 on GPU)</SelectItem>
                  <SelectItem value="groq">Groq API (Cloud - Faster)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* YouTube URL Input */}
            <div className="space-y-2">
              <Label>YouTube Video URL</Label>
              <Input
                type="text"
                placeholder="Enter YouTube Video URL"
                value={state.youtubeUrl}
                onChange={(e) => dispatch({ type: ACTIONS.SET_YOUTUBE_URL, payload: e.target.value })}
              />
            </div>

            {/* Directory Input */}
            <div className="space-y-2">
              <Label>Save Directory</Label>
              <Input
                type="text"
                value={state.obsidianDir}
                onChange={(e) => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: e.target.value })}
              />
            </div>

            {/* Output Folder */}
            <div className="space-y-2">
              <Label>Output Folder</Label>
              <Input
                type="text"
                value={state.outputFolder}
                onChange={(e) => dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: e.target.value })}
              />
            </div>

            {/* Buttons */}
            <div className="space-y-2">
              <Button
                className="w-full"
                variant="outline"
                onClick={handleSelectOutputFolder}
              >
                Select Output Folder
              </Button>

              <Button
                className="w-full"
                onClick={handleProcessVideo}
                disabled={state.loading}
              >
                {state.loading ? 'Processing...' : 'Process Video'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="status" className="w-full mt-8" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="status">Status Updates</TabsTrigger>
            <TabsTrigger value="transcription">Live Transcription</TabsTrigger>
            <TabsTrigger value="webpages">Fetched Web Pages</TabsTrigger>
          </TabsList>

          {/* Status Updates Tab */}
          <TabsContent value="status">
            <Card>
              <CardHeader>
                <CardTitle>Status Updates</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                  {state.statusUpdates.map((message, index) => (
                    <p key={index} className="text-sm text-muted-foreground mb-2">
                      {message}
                    </p>
                  ))}
                  {state.transcribing && (
                    <div className="flex items-center gap-2 mt-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                      <span className="text-sm">Transcribing... {formatElapsedTime(elapsedTime)}</span>
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Transcription Tab */}
          <TabsContent value="transcription">
            <Card>
              <CardHeader>
                <CardTitle>Transcription</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="live" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="live">Live Transcription</TabsTrigger>
                    <TabsTrigger value="completed">Completed Transcription</TabsTrigger>
                  </TabsList>

                  <TabsContent value="live">
                    <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                      <div className="space-y-2">
                        {state.transcriptionSegments.map((segment, index) => (
                          <p key={index} className="text-sm">
                            {segment}
                          </p>
                        ))}
                        <div ref={transcriptionBoxRef} />
                      </div>
                      <ScrollBar />
                    </ScrollArea>
                  </TabsContent>

                  <TabsContent value="completed">
                    <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                      <div className="space-y-2">
                        {state.completedTranscription ? (
                          <ReactMarkdown className="prose prose-sm max-w-none">
                            {state.completedTranscription}
                          </ReactMarkdown>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            Transcription not yet completed.
                          </p>
                        )}
                      </div>
                      <ScrollBar />
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Web Pages Tab */}
          <TabsContent value="webpages">
            <Card>
              <CardHeader>
                <CardTitle>Web Page Content</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* URL and Controls Row */}
                  <div className="space-y-4">
                    <Input
                      placeholder="Enter URL to fetch"
                      value={state.fetchUrl}
                      onChange={(e) => dispatch({ type: ACTIONS.SET_FETCH_URL, payload: e.target.value })}
                    />

                    {/* Target Selector Input */}
                    <Input
                      placeholder="CSS Selector (e.g., article, .main-content)"
                      value={state.targetSelector}
                      onChange={(e) => dispatch({ type: ACTIONS.SET_TARGET_SELECTOR, payload: e.target.value })}
                    />

                    {/* JSON Toggle */}
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="json-mode"
                        checked={state.jsonResponse}
                        onCheckedChange={(checked) => dispatch({ type: ACTIONS.SET_JSON_RESPONSE, payload: checked })}
                      />
                      <Label htmlFor="json-mode">JSON Response</Label>
                    </div>

                    <Button
                      onClick={handleFetchContent}
                      disabled={state.loading}
                      className="w-full bg-destructive hover:bg-destructive/90 text-destructive-foreground"
                    >
                      {state.loading ? 'Fetching...' : 'Fetch Content'}
                    </Button>
                  </div>

                  <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                    {state.fetchResult ? (
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{
                          typeof state.fetchResult === 'string'
                            ? state.fetchResult
                            : state.fetchResult.markdown_content || 'No content fetched yet.'
                        }</ReactMarkdown>
                        {state.fetchResult.markdown_path && (
                          <p className="text-sm text-muted-foreground mt-4">
                            Markdown saved to: {state.fetchResult.markdown_path}
                          </p>
                        )}
                        {state.fetchResult.pdf_path && (
                          <p className="text-sm text-muted-foreground">
                            PDF saved to: {state.fetchResult.pdf_path}
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No content fetched yet.</p>
                    )}
                    <ScrollBar />
                  </ScrollArea>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Error Display */}
        {state.error && (
          <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
            {state.error}
          </div>
        )}
      </main>
    </div>
  );
}
