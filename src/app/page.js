"use client";

import React, { useEffect, useCallback, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image';

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
import { transcriptionReducer, initialState as transcriptionInitialState, ACTIONS } from './reducers/transcriptionReducer';
import { storage } from './utils/storage';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { permanentMarker, fZeroFont } from './fonts';
import { BACKEND_URL } from '@/lib/constants';

const steps = [
  'Enter YouTube URL',
  'Process Video',
  'Transcribe Audio',
  'Transcription Complete'
];

export default function Home() {
  const [initialState, setInitialState] = useState(null);
  
  // Load state on mount
  useEffect(() => {
    const savedState = storage.get('transcriptionState');
    if (savedState) {
      setInitialState(savedState);
    }
  }, []);

  // Initialize reducer with loaded state
  const [state, dispatch] = useReducer(
    transcriptionReducer,
    {
      ...transcriptionInitialState,
      ...(initialState || {
        statusUpdates: [],
        transcriptionSegments: [],
        activeStep: 0,
        transcribing: false,
        error: null,
        loading: false,
        tabValue: 'status'
      })
    }
  );

  const [elapsedTime, setElapsedTime] = useState(0);
  const [activeTab, setActiveTab] = useState("status");
  const transcriptionBoxRef = useRef(null);
  const paperRef = useRef(null);
  let resizeObserver;
  let rafId;
  const eventSource = useRef(null);
  const statusBoxRef = useRef(null);

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

      const response = await axios.get(`${BACKEND_URL}/fetch-content`, {
        params: {
          url: sanitizedFetchUrl,
          json_response: state.jsonResponse,
          timeout: state.timeout,
          target_selector: state.targetSelector
        }
      });

      if (response.data.markdown_path) {
        try {
          const markdownResponse = await axios.get(`${BACKEND_URL}/fetch-markdown`, {
            params: { path: response.data.markdown_path }
          });

          const content = typeof markdownResponse.data === 'object' 
            ? JSON.stringify(markdownResponse.data, null, 2)
            : markdownResponse.data;

          dispatch({ 
            type: ACTIONS.SET_FETCH_RESULT, 
            payload: {
              markdown_content: content,
              markdown_path: response.data.markdown_path,
              pdf_path: response.data.pdf_path
            }
          });
          dispatch({ 
            type: ACTIONS.ADD_STATUS_UPDATE, 
            payload: 'Content fetched successfully.' 
          });
        } catch (markdownError) {
          console.error("Error fetching Markdown content:", markdownError);
          dispatch({ 
            type: ACTIONS.SET_ERROR, 
            payload: `Error fetching content: ${markdownError.message}` 
          });
        }
      } else {
        dispatch({ 
          type: ACTIONS.SET_ERROR, 
          payload: "No content found in response." 
        });
      }
    } catch (error) {
      console.error("Error fetching content:", error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: `Error: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

// Function to handle video processing
const handleProcessVideo = async () => {
  if (!state.youtubeUrl || !state.obsidianDir) {
    dispatch({
      type: ACTIONS.SET_ERROR,
      payload: "Please fill in all required fields"
    });
    return;
  }

  try {
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.SET_ERROR, payload: null });
    dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
    dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });

    // Make the initial request to start processing
    const response = await axios.post(`${BACKEND_URL}/process-video/`, {
      youtube_video_url: state.youtubeUrl,
      obsidian_dir: state.obsidianDir,
      output_folder: state.outputFolder,
      transcription_model: state.transcriptionModel, // This should be 'groq' or 'faster-whisper'
      use_groq: state.transcriptionModel === 'groq' // Explicitly set based on model selection
    });

    if (response.data && response.data.status === 'started') {
      dispatch({
        type: ACTIONS.ADD_STATUS_UPDATE,
        payload: "Video processing started successfully"
      });
    }

    // Rest of the function...
  } catch (error) {
    // Error handling...
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

  // Update the SSE handling
  useEffect(() => {
    let source = null;
    let retryCount = 0;
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 1000; // 1 second

    const setupSSE = () => {
      if (state.transcribing) {
        try {
          // Close any existing connection
          if (source) {
            source.close();
          }

          // Create new connection with proper error handling
          source = new EventSource(`${BACKEND_URL}/combined-updates`);
          console.log("Setting up SSE connection...");

          // Connection opened
          source.onopen = () => {
            console.log("SSE connection opened");
            retryCount = 0;
            dispatch({
              type: ACTIONS.ADD_STATUS_UPDATE,
              payload: "Connected to transcription service"
            });
          };

          // Handle messages with immediate processing
          source.onmessage = (event) => {
            try {
              // Remove the "data: " prefix and parse immediately
              const data = JSON.parse(event.data.replace(/^data: /, ''));

              // Process update immediately based on type
              switch (data.type) {
                case 'status':
                  requestAnimationFrame(() => {
                    dispatch({
                      type: ACTIONS.ADD_STATUS_UPDATE,
                      payload: data.content
                    });
                  });
                  break;

                case 'transcription_segment':
                  requestAnimationFrame(() => {
                    dispatch({
                      type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT,
                      payload: data.content
                    });
                    // Trigger scroll update immediately
                    if (transcriptionBoxRef.current) {
                      const scrollArea = transcriptionBoxRef.current.querySelector('[data-radix-scroll-area-viewport]');
                      if (scrollArea) {
                        scrollArea.scrollTop = scrollArea.scrollHeight;
                      }
                    }
                  });
                  break;

                case 'transcription_complete':
                  requestAnimationFrame(() => {
                    dispatch({
                      type: ACTIONS.SET_COMPLETED_TRANSCRIPTION,
                      payload: data.content
                    });
                    dispatch({
                      type: ACTIONS.ADD_STATUS_UPDATE,
                      payload: "Transcription completed successfully!"
                    });
                    dispatch({
                      type: ACTIONS.SET_ACTIVE_STEP,
                      payload: steps.length - 1
                    });
                    dispatch({ 
                      type: ACTIONS.SET_TRANSCRIBING, 
                      payload: false 
                    });
                  });
                  break;

                case 'error':
                  console.error('SSE error:', data.content);
                  requestAnimationFrame(() => {
                    dispatch({
                      type: ACTIONS.SET_ERROR,
                      payload: data.content
                    });
                  });
                  break;
              }
            } catch (error) {
              console.error('Error handling SSE message:', error);
            }
          };

          // Enhanced error handling with exponential backoff
          source.onerror = (error) => {
            console.error('SSE connection error:', error);
            
            if (source.readyState === EventSource.CLOSED) {
              if (retryCount < MAX_RETRIES) {
                retryCount++;
                const delay = RETRY_DELAY * Math.pow(2, retryCount - 1);
                console.log(`Retrying connection (${retryCount}/${MAX_RETRIES}) in ${delay}ms...`);
                
                dispatch({
                  type: ACTIONS.ADD_STATUS_UPDATE,
                  payload: `Connection lost. Retrying (${retryCount}/${MAX_RETRIES})...`
                });
                
                setTimeout(() => {
                  setupSSE();
                }, delay);
              } else {
                dispatch({
                  type: ACTIONS.SET_ERROR,
                  payload: "Failed to maintain connection after multiple attempts"
                });
                dispatch({
                  type: ACTIONS.SET_TRANSCRIBING,
                  payload: false
                });
              }
            }
          };

        } catch (error) {
          console.error('Error setting up SSE:', error);
          dispatch({
            type: ACTIONS.SET_ERROR,
            payload: "Failed to connect to transcription service"
          });
        }
      }
    };

    setupSSE();

    // Cleanup function
    return () => {
      if (source) {
        console.log("Cleaning up SSE connection");
        source.close();
        source = null;
      }
    };
  }, [state.transcribing]);

  useEffect(() => {
    const testConnection = async () => {
       try {
          const response = await axios.get(BACKEND_URL);
          console.log("Backend connected:", response.data);
          dispatch({ 
             type: ACTIONS.ADD_STATUS_UPDATE, 
             payload: 'Backend connection established' 
          });
       } catch (error) {
          console.error("Backend connection failed:", error);
          dispatch({ 
             type: ACTIONS.SET_ERROR, 
             payload: `Failed to connect to backend: ${error.message}` 
          });
       }
    };
 
    testConnection();
 }, []);
 
 // Update the timer effect to properly handle transcription state
 useEffect(() => {
    let timer;
    if (state.transcribing) {
       console.log('Starting timer');
       setElapsedTime(0); // Reset timer when starting new transcription
       timer = setInterval(() => {
          setElapsedTime(prev => prev + 1);
       }, 1000);
    } else {
       console.log('Stopping timer');
       if (timer) {
          clearInterval(timer);
       }
    }
    
    return () => {
       if (timer) {
          console.log('Cleaning up timer');
          clearInterval(timer);
       }
    };
 }, [state.transcribing]);
 
 // Update the process video function
 const onProcessVideo = async () => {
    try {
       console.log("Starting video processing...");
       
       // Validate inputs
       if (!validateYoutubeUrl(state.youtubeUrl)) {
          dispatch({ type: ACTIONS.SET_ERROR, payload: 'Please enter a valid YouTube URL' });
          return;
       }
 
       // Reset state
       dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
       dispatch({ type: ACTIONS.SET_ERROR, payload: null });
       setElapsedTime(0);
 
       // Prepare request data
       const requestData = {
          youtube_video_url: state.youtubeUrl,
          obsidian_dir: state.obsidianDir,
          output_folder: state.outputFolder,
          transcription_model: state.transcriptionModel || "faster-whisper",
          use_groq: state.transcriptionModel === 'groq'  // Explicitly set based on model selection
       };
 
       console.log("Request data:", requestData);
 
       dispatch({ type: ACTIONS.SET_LOADING, payload: true });
       dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
       dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 1 });
       dispatch({ 
          type: ACTIONS.ADD_STATUS_UPDATE, 
          payload: 'Starting video processing...' 
       });
 
       console.log("Sending request to backend...");
       const response = await axios.post(`${BACKEND_URL}/process-video/`, requestData);
 
       console.log("Process video response:", response.data);
 
       if (response.data.status === 'started') {
          dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 2 });
          console.log("Video processing started successfully");
       }
 
    } catch (error) {
       console.error("Error processing video:", error);
       const errorMessage = error.response?.data?.detail || error.message;
       dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
       dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
       setElapsedTime(0);
    } finally {
       dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
 };
 
 // Save state changes
 useEffect(() => {
    storage.set('transcriptionState', {
       transcribing: state.transcribing,
       statusUpdates: state.statusUpdates,
       transcriptionSegments: state.transcriptionSegments,
       activeStep: state.activeStep,
       youtubeUrl: state.youtubeUrl,
       elapsedTime: state.elapsedTime
    });
 }, [state]);
 
 // Add a check for ongoing transcription on mount
 useEffect(() => {
    const checkTranscriptionStatus = async () => {
       if (state.transcribing) {
          try {
             // Optionally check with backend if transcription is still running
             dispatch({ 
                type: ACTIONS.ADD_STATUS_UPDATE, 
                payload: 'Reconnecting to previous transcription...' 
             });
          } catch (error) {
             console.error('Error checking transcription status:', error);
             dispatch({ 
                type: ACTIONS.SET_TRANSCRIBING, 
                payload: false 
             });
             storage.remove('transcriptionState');
          }
       }
    };
 
    checkTranscriptionStatus();
 }, []);

 // Auto-scroll status updates to bottom
 useEffect(() => {
    if (statusBoxRef.current && state.statusUpdates.length > 0) {
      const scrollArea = statusBoxRef.current.parentElement;
      if (scrollArea) {
        setTimeout(() => {
          scrollArea.scrollTo({
            top: scrollArea.scrollHeight,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
 }, [state.statusUpdates]);

 // Auto-scroll transcription to bottom
 useEffect(() => {
    if (transcriptionBoxRef.current && state.transcriptionSegments.length > 0) {
      const scrollArea = transcriptionBoxRef.current.parentElement;
      if (scrollArea) {
        setTimeout(() => {
          scrollArea.scrollTo({
            top: scrollArea.scrollHeight,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
 }, [state.transcriptionSegments]);

 // Update the status display component to show model type
 const StatusUpdates = ({ updates, model }) => (
    <div className="space-y-2">
       {updates.map((update, index) => (
          <div key={index} className="text-sm">
             <span className="text-muted-foreground">
                {model === 'groq' ? '🤖 Groq: ' : '🎯 Whisper: '}
             </span>
             {update}
          </div>
       ))}
    </div>
 );
 
 // Add this useEffect for handling transcription updates scroll
 useEffect(() => {
    if (transcriptionBoxRef.current) {
       const scrollArea = transcriptionBoxRef.current.querySelector('[data-radix-scroll-area-viewport]');
       if (scrollArea) {
          scrollArea.scrollTop = scrollArea.scrollHeight;
       }
    }
 }, [state.transcriptionSegments]);
 
 // Add this for status updates scroll
 useEffect(() => {
    if (statusBoxRef.current) {
       const scrollArea = statusBoxRef.current.querySelector('[data-radix-scroll-area-viewport]');
       if (scrollArea) {
          scrollArea.scrollTop = scrollArea.scrollHeight;
       }
    }
 }, [state.statusUpdates]);
 
 return (
    <>
       <main className="container mx-auto mt-8 p-4 max-w-3xl">
          {/* Progress Steps */}
          <Card className="glass-card mb-8">
             <CardContent className="pt-6">
                <div className="flex justify-between items-center relative">
                   {/* Progress Bar */}
                   <div className="absolute top-1/2 left-0 right-0 h-1 bg-muted -translate-y-1/2">
                      <div 
                         className="h-full gradient-progress transition-all duration-300"
                         style={{ 
                            width: `${(state.activeStep / (steps.length - 1)) * 100}%`,
                         }}
                      />
                   </div>
                   
                   {/* Step Circles */}
                   {steps.map((step, index) => (
                      <div key={index} className="flex flex-col items-center relative z-10">
                         <div 
                            className={`
                               rounded-full w-8 h-8 flex items-center justify-center
                               transition-colors duration-300
                               ${state.activeStep >= index || 
                                  (state.transcriptionSegments?.length > 0 && index === steps.length - 1)
                                  ? 'bg-primary text-primary-foreground' 
                                  : 'bg-muted text-muted-foreground'
                               }
                            `}
                         >
                            {index + 1}
                         </div>
                         <span 
                            className={`
                               text-sm mt-2 whitespace-nowrap
                               transition-colors duration-300
                               ${state.activeStep >= index || 
                                  (state.transcriptionSegments?.length > 0 && index === steps.length - 1)
                                  ? 'text-primary' 
                                  : 'text-muted-foreground'
                               }
                            `}
                         >
                            {step}
                         </span>
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
                      onValueChange={(value) => dispatch({ 
                         type: ACTIONS.SET_TRANSCRIPTION_MODEL, 
                         payload: value 
                      })}
                   >
                      <SelectTrigger className="w-full">
                         <SelectValue placeholder="Select transcription model" />
                      </SelectTrigger>
                      <SelectContent>
                         <SelectItem value="faster-whisper">Faster Whisper (large-v3 on GPU)</SelectItem>
                         <SelectItem value="groq">Groq API (distil-whisper-large-v3)</SelectItem>
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
                      className="w-full gradient-button"
                      onClick={onProcessVideo}
                      disabled={state.loading || !state.youtubeUrl}
                   >
                      {state.loading ? 'Processing...' : 'Process Video'}
                   </Button>
                </div>
             </CardContent>
          </Card>
 
          {/* Output Section with Vertical Layout */}
          <div className="mt-8 space-y-4">
            {/* Status Updates Box */}
            <Card>
              <CardHeader>
                <CardTitle>Status Updates</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[250px] w-full rounded-md border p-4">
                  <div ref={statusBoxRef} className="space-y-2">
                    {state.statusUpdates.map((update, index) => (
                      <div key={index} className="text-sm">
                        {update}
                      </div>
                    ))}
                  </div>
                  <ScrollBar />
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Live Transcription Box - Resizable */}
            <Card>
              <CardHeader>
                <CardTitle>Live Transcription</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="resize-y overflow-auto min-h-[250px] h-[400px] max-h-[800px]">
                  <ScrollArea className="h-full w-full rounded-md border p-4">
                    <div ref={transcriptionBoxRef} className="space-y-2">
                      {state.transcriptionSegments.map((segment, index) => (
                        <div key={index} className="text-sm">
                          {segment}
                        </div>
                      ))}
                    </div>
                    <ScrollBar />
                  </ScrollArea>
                </div>
              </CardContent>
            </Card>

            {/* Web Pages Tab Content - Keep as is */}
            <Card className={activeTab === 'webpages' ? '' : 'hidden'}>
              {/* URL Input */}
              <div className="space-y-2">
                <Label>URL to Fetch</Label>
                <Input
                  placeholder="Enter URL to fetch"
                  value={state.fetchUrl}
                  onChange={(e) => dispatch({ type: ACTIONS.SET_FETCH_URL, payload: e.target.value })}
                />
              </div>

              {/* Advanced Options Accordion */}
              <Accordion type="single" collapsible>
                <AccordionItem value="advanced-options">
                  <AccordionTrigger>Advanced Options</AccordionTrigger>
                  <AccordionContent>
                    {/* Target Selector */}
                    <div className="space-y-2 mb-4">
                      <Label>Target Selector</Label>
                      <Input
                        placeholder="CSS Selector (e.g., article, .main-content)"
                        value={state.targetSelector}
                        onChange={(e) => dispatch({ 
                          type: ACTIONS.SET_TARGET_SELECTOR, 
                          payload: e.target.value 
                        })}
                      />
                      <p className="text-sm text-muted-foreground">
                        Specify elements to extract (e.g., article, .main-content)
                      </p>
                    </div>

                    {/* Excluded Selector */}
                    <div className="space-y-2 mb-4">
                      <Label>Exclude Elements</Label>
                      <Input
                        placeholder="Elements to exclude (e.g., nav, footer, .ads)"
                        value={state.excludedSelector}
                        onChange={(e) => dispatch({ 
                          type: ACTIONS.SET_EXCLUDED_SELECTOR, 
                          payload: e.target.value 
                        })}
                      />
                      <p className="text-sm text-muted-foreground">
                        Specify elements to remove (e.g., nav, footer, .ads)
                      </p>
                    </div>

                    {/* Timeout Setting */}
                    <div className="space-y-2 mb-4">
                      <Label>Timeout (seconds)</Label>
                      <Input
                        type="number"
                        min="0"
                        max="300"
                        value={state.timeout}
                        onChange={(e) => dispatch({ 
                          type: ACTIONS.SET_TIMEOUT, 
                          payload: e.target.value 
                        })}
                      />
                    </div>

                    {/* Response Format */}
                    <div className="space-y-2">
                      <Label>Response Format</Label>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <Switch
                            id="json-mode"
                            checked={state.jsonResponse}
                            onCheckedChange={(checked) => dispatch({ 
                              type: ACTIONS.SET_JSON_RESPONSE, 
                              payload: checked 
                            })}
                          />
                          <Label htmlFor="json-mode">JSON Response</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch
                            id="clean-mode"
                            checked={state.cleanFormat}
                            onCheckedChange={(checked) => dispatch({ 
                              type: ACTIONS.SET_CLEAN_FORMAT, 
                              payload: checked 
                            })}
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
                disabled={state.loading}
                className="w-full gradient-button"
              >
                {state.loading ? 'Fetching...' : 'Fetch Content'}
              </Button>

              {/* Results Display */}
              <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                {state.fetchResult ? (
                  <div className="space-y-4">
                    {/* Tabs for switching between Markdown and PDF */}
                    <Tabs defaultValue="markdown" className="w-full">
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="markdown">Markdown View</TabsTrigger>
                        <TabsTrigger value="pdf">PDF View</TabsTrigger>
                      </TabsList>

                      <TabsContent value="markdown">
                        {/* Markdown Content Display */}
                        <div className="prose prose-sm dark:prose-invert max-w-none">
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
                      </TabsContent>

                      <TabsContent value="pdf" className="h-full">
                        {/* PDF Viewer */}
                        {state.fetchResult?.pdf_path ? (
                          <div className="w-full min-h-[600px] relative bg-white rounded-md shadow">
                            <iframe
                              src={`${BACKEND_URL}/view-pdf?path=${encodeURIComponent(state.fetchResult.pdf_path)}`}
                              className="w-full h-full absolute inset-0 rounded-md"
                              title="PDF Viewer"
                              onError={(e) => {
                                console.error("PDF loading error:", e);
                                dispatch({ 
                                  type: ACTIONS.SET_ERROR, 
                                  payload: "Error loading PDF. Please try downloading instead." 
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
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>Enter a URL above and click "Fetch Content" to get started</p>
                  </div>
                )}
                <ScrollBar />
              </ScrollArea>
            </Card>
          </div>

          {/* Error Display */}
          {state.error && (
            <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
              <p className="font-semibold">Error:</p>
              <p>{state.error}</p>
            </div>
          )}
        </main>
      </>
    );
}