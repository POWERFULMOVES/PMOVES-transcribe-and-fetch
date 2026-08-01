"use client";

import React, { useEffect, useCallback, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import useSSE from '@/hooks/useSSE';
import useAppConfig from '@/hooks/useAppConfig';

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
  ScrollArea,
  ScrollBar,
} from "@/components/ui/scroll-area";

import { transcriptionReducer, initialState as transcriptionInitialState, ACTIONS } from '@/app/reducers/transcriptionReducer';
import { storage } from '@/app/utils/storage';
import { SSE_CONFIG, BACKEND_URL } from '@/lib/constants';
import { createClient } from '@/lib/supabase';

import ProcessingOptionsSelector from '@/components/transcription/ProcessingOptionsSelector';
import TranscriptionJobSummary from '@/components/transcription/TranscriptionJobSummary';
import CompletedTranscriptionView from '@/components/transcription/CompletedTranscriptionView';
import TranscriptionSegment from '@/components/transcription/TranscriptionSegment';

// --- Helper Functions ---
const formatElapsedTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const scrollToBottom = (elementRef) => {
    if (!elementRef.current) return;
    requestAnimationFrame(() => {
        const scrollContainer = elementRef.current.closest('[data-radix-scroll-area-viewport]') || elementRef.current.parentElement;
        if (scrollContainer) {
            scrollContainer.scrollTo({
                top: scrollContainer.scrollHeight,
                behavior: 'auto'
            });
        }
    });
};

const validateYoutubeUrl = (url) => {
  const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
  return regex.test(url);
};

const validateObsidianDir = (dir) => {
  return dir && dir.trim().length > 0;
};

// Validate transcription segment data
const isValidSegment = (segment) => {
  // console.log('[isValidSegment] Validating segment:', segment);

  if (!segment) return false;

  const segmentData = segment.content && typeof segment.content === 'object' ? segment.content : segment;
  const segmentText = segmentData.text || segmentData.Text || '';
  
  if (!segmentText || typeof segmentText !== 'string' || segmentText.trim() === '') {
    return false; // Strict check for text
  }

  // Ensure segment has the text property
  if (!segment.text) segment.text = segmentText;

  let startTime = segmentData.start_time || segmentData.start || segmentData.startTime || 0;
  let endTime = segmentData.end_time || segmentData.end || segmentData.endTime || 0;

  // Normalization logic for timestamps (simplified for brevity, original logic is robust)
  if (typeof startTime === 'string') startTime = parseFloat(startTime) || 0;
  if (typeof endTime === 'string') endTime = parseFloat(endTime) || 0;

  segment.start_time = startTime;
  segment.end_time = endTime;
  
  if (!segment.id && segmentData.id) segment.id = segmentData.id;

  return true;
};

// Status Updates Component
const StatusUpdates = ({ updates, model }) => {
    const uniqueUpdates = updates
        .filter((update, index, self) => self.indexOf(update) === index)
        .slice(-100);

    return (
        <div className="space-y-2">
            {uniqueUpdates.map((update, index) => (
                <div key={index} className="text-sm flex items-start">
                    <span className={`mr-2 ${model === 'groq' ? "text-blue-600 dark:text-blue-400" : "text-green-600 dark:text-green-400"}`}>
                        {model === 'groq' ? '☁️' : '💻'}
                    </span>
                    <span className="flex-1">
                      {typeof update === 'object' && update !== null ?
                        (update.message ? update.message + (update.details ? ` (${update.details})` : '') : JSON.stringify(update))
                        : update}
                    </span>
                </div>
            ))}
        </div>
    );
};

export default function TranscribePage() {
  const router = useRouter(); // Though not heavily used here, might be useful
  const [initialStateLoaded, setInitialStateLoaded] = useState(false);
  const [persistedState, setPersistedState] = useState(null);
  const [session, setSession] = useState(null);

  // Initialize Supabase session
  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const savedState = storage.get('transcriptionState');
    if (savedState) {
      setPersistedState(savedState);
    }
    setInitialStateLoaded(true);
  }, []);

  const [state, dispatch] = useReducer(
    transcriptionReducer,
    persistedState || transcriptionInitialState
  );
  
  const messageBuffer = useRef([]);
  const bufferTimeoutRef = useRef(null);
  const BATCH_DELAY = 150;
  const initialCheckDoneRef = useRef(false);
  const [timerActive, setTimerActive] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [backendStatus, setBackendStatus] = useState("unknown");
  const statusBoxRef = useRef(null);
  const disconnectTimeoutRef = useRef(null);
  const scrollAreaRef = useRef(null);
  const { config: appConfig, loading: configLoading, error: configError } = useAppConfig();

  // Timer Effect
  useEffect(() => {
    const shouldRunTimer = state.transcribing && state.transcriptionSegments.length > 0;
    if (shouldRunTimer && !timerActive) setTimerActive(true);
    else if (!state.transcribing && timerActive) setTimerActive(false);
    
    if (!state.transcribing) setElapsedTime(0);
  }, [state.transcribing, state.transcriptionSegments.length, timerActive]);

  useEffect(() => {
    let timer;
    if (timerActive) {
      timer = setInterval(() => setElapsedTime(prev => prev + 1), 1000);
    }
    return () => clearInterval(timer);
  }, [timerActive]);

  const steps = [
    'Enter YouTube URL',
    'Process Video',
    'Transcribe Audio',
    'Transcription Complete'
  ];

  const checkBackendHealth = useCallback(async () => {
    setBackendStatus("checking");
    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: "Checking backend connection..." });
    try {
        const endpoints = [{ url: `${BACKEND_URL}/`, name: "root" }, { url: `${BACKEND_URL}/health`, name: "health" }];
        let connected = false;
        const headers = {};
        if (session?.access_token) {
            headers['Authorization'] = `Bearer ${session.access_token}`;
        }
        for (const endpoint of endpoints) {
            try {
                const response = await axios.get(endpoint.url, { headers, timeout: 5000 });
                if (response.status === 200) {
                    setBackendStatus("connected");
                    dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Backend connection successful (${endpoint.name})` });
                    connected = true;
                    break;
                }
            } catch (e) { /* ignore individual failures */ }
        }
        if (!connected) throw new Error("Connection failed");
    } catch (error) {
        setBackendStatus("error");
        dispatch({ type: ACTIONS.SET_ERROR, payload: `Backend connection error: ${error.message}` });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Backend connection failed.'});
    }
  }, [dispatch]);

  useEffect(() => {
      checkBackendHealth();
      return () => {
        const timeoutRef = disconnectTimeoutRef; // Copy ref to ensure valid cleanup
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
      };
  }, [checkBackendHealth]);

  // SSE Setup
  const processBuffer = useCallback(() => {
    if (messageBuffer.current.length > 0) {
      const segmentsToDispatch = [...messageBuffer.current];
      messageBuffer.current = [];
      dispatch({ type: ACTIONS.ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS, payload: segmentsToDispatch });
    }
    bufferTimeoutRef.current = null;
  }, [dispatch]);

  const onMessage = useCallback((data) => {
    try {
      let message;
      if (typeof data === 'string') {
        try { message = JSON.parse(data); } 
        catch (e) { dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Malformed data: ${data.substring(0, 50)}...` }); return; }
      } else { message = data; }

      switch (message.type) {
        case 'status':
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: message.content });
          break;
        case 'transcription_segment':
          if (isValidSegment(message.content)) {
            messageBuffer.current.push(message.content);
            if (bufferTimeoutRef.current === null) {
              bufferTimeoutRef.current = setTimeout(processBuffer, BATCH_DELAY);
            }
          }
          break;
        case 'transcription_complete':
          if (bufferTimeoutRef.current) clearTimeout(bufferTimeoutRef.current);
          processBuffer();
          dispatch({ type: ACTIONS.FINALIZE_TRANSCRIPTION });
          dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 3 });
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
          dispatch({ type: ACTIONS.SET_LOADING, payload: false });
          setTimerActive(false);
          break;
        case 'error':
          if (bufferTimeoutRef.current) clearTimeout(bufferTimeoutRef.current);
          processBuffer();
          dispatch({ type: ACTIONS.SET_ERROR, payload: `Backend Error: ${message.content}` });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Error: ${message.content}` });
          dispatch({ type: ACTIONS.SET_LOADING, payload: false });
          dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
          setTimerActive(false);
          break;
        case 'video_metadata':
          dispatch({ type: ACTIONS.SET_VIDEO_METADATA, payload: message.content });
          dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: `Video: ${message.content.title}` });
          break;
        case 'connection_status':
          if (message.content === 'safe_to_disconnect') {
            if (bufferTimeoutRef.current) clearTimeout(bufferTimeoutRef.current);
            processBuffer();
            dispatch({ type: ACTIONS.SET_SHOULD_DISCONNECT, payload: true });
          }
          break;
        default:
          break;
      }
    } catch (error) {
        console.error("Error in onMessage:", error);
    }
  }, [dispatch, processBuffer]);

  const {
    connected: sseConnected,
    connect: connectSSE,
    disconnect: disconnectSSE
  } = useSSE('/combined-updates', {
    autoConnect: false,
    withCredentials: true,
    maxRetries: SSE_CONFIG.MAX_RETRIES,
    reconnectDelay: SSE_CONFIG.RECONNECT_DELAY,
    onConnect: () => dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Real-time updates connected' }),
    onMessage: (data) => {
      if (window.onMessageOptimized) window.onMessageOptimized(data); // Using the optimization pattern
      else if (data.type === 'status') dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: data.content });
    },
    onDisconnect: (error) => {
       if (error && state.transcribing) {
         dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
         dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Connection lost.' });
       }
    }
  });

  useEffect(() => {
    window.onMessageOptimized = onMessage;
    return () => { window.onMessageOptimized = undefined; };
  }, [onMessage]);

  useEffect(() => {
    if (state.transcribing && !sseConnected) {
        setTimeout(() => { if (state.transcribing) connectSSE(); }, 100);
    }
    return () => { /* Cleanup managed by hook */ };
  }, [state.transcribing, sseConnected, connectSSE]);

  useEffect(() => {
    if (state.shouldDisconnect && sseConnected) {
        disconnectSSE();
        dispatch({ type: ACTIONS.SET_SHOULD_DISCONNECT, payload: false });
    }
  }, [state.shouldDisconnect, sseConnected, disconnectSSE, dispatch]);

  useEffect(() => {
    const checkForActive = async () => {
        try {
            const headers = {};
            if (session?.access_token) {
                headers['Authorization'] = `Bearer ${session.access_token}`;
            }
            const res = await fetch(`${BACKEND_URL}/transcription-status`, { headers });
            const data = await res.json();
            if (data.active) {
                dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
                dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Reconnecting to active job...' });
            }
        } catch (e) {
            console.error("Status check failed", e);
        }
    };
    if (!state.transcribing && initialStateLoaded && !initialCheckDoneRef.current) {
        initialCheckDoneRef.current = true;
        checkForActive();
    }
  }, [initialStateLoaded, state.transcribing, dispatch]);

  // Scroll Auto
  useEffect(() => scrollToBottom(statusBoxRef), [state.statusUpdates]);
  useEffect(() => {
    if (scrollAreaRef.current) {
        const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
        if (viewport) requestAnimationFrame(() => viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'auto' }));
    }
  }, [state.transcriptionSegments]);

  // Persist State
  useEffect(() => {
    if (!initialStateLoaded) return;
    storage.set('transcriptionState', {
        youtubeUrl: state.youtubeUrl,
        obsidianDir: state.obsidianDir,
        outputFolder: state.outputFolder,
        transcriptionModel: state.transcriptionModel
    });
  }, [initialStateLoaded, state.youtubeUrl, state.obsidianDir, state.outputFolder, state.transcriptionModel]);

  // Config Defaults
  useEffect(() => {
    if (initialStateLoaded && !configLoading && appConfig) {
        if (!state.obsidianDir && appConfig.DEFAULT_OBSIDIAN_DIR) dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: appConfig.DEFAULT_OBSIDIAN_DIR });
        if (!state.outputFolder && appConfig.DEFAULT_OUTPUT_FOLDER) dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: appConfig.DEFAULT_OUTPUT_FOLDER });
    }
  }, [initialStateLoaded, configLoading, appConfig, state.obsidianDir, state.outputFolder]);

  // Handler: Process Video
  const onProcessVideo = async () => {
    if (!initialStateLoaded) return;
    if (!validateYoutubeUrl(state.youtubeUrl)) { dispatch({ type: ACTIONS.SET_ERROR, payload: 'Invalid YouTube URL' }); return; }
    if (!validateObsidianDir(state.obsidianDir)) { dispatch({ type: ACTIONS.SET_ERROR, payload: 'Invalid Directory' }); return; }

    try {
        dispatch({ type: ACTIONS.RESET_TRANSCRIPTION });
        messageBuffer.current = [];
        setElapsedTime(0);
        setTimerActive(false);

        const payload = {
            youtube_video_url: state.youtubeUrl,
            obsidian_dir: state.obsidianDir,
            output_folder: state.outputFolder || 'output',
            transcription_model: state.transcriptionModel || "faster-whisper",
            use_groq: state.transcriptionModel === 'groq'
        };

        dispatch({ type: ACTIONS.SET_LOADING, payload: true });
        dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 1 });
        dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Initiating...' });

        const headers = {};
        if (session?.access_token) {
            headers['Authorization'] = `Bearer ${session.access_token}`;
        }

        const response = await axios.post(`${BACKEND_URL}/process-video/`, payload, { headers });
        if (response.data.status === 'started') {
            dispatch({ type: ACTIONS.SET_ACTIVE_STEP, payload: 2 });
            dispatch({ type: ACTIONS.ADD_STATUS_UPDATE, payload: 'Processing started...' });
            dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: true });
        } else {
            throw new Error("Unexpected start status");
        }
    } catch (error) {
        console.error("Process error:", error);
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message || "Failed to start" });
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.SET_TRANSCRIBING, payload: false });
    }
  };

  const MiniSpinner = () => (
    <svg className="animate-spin h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  );

  let jobStatus = 'Idle';
  if (state.error) jobStatus = 'Failed';
  else if (state.transcribing) jobStatus = 'In Progress';
  else if (!state.transcribing && state.activeStep === 3 && state.transcriptionSegments.length > 0) jobStatus = 'Completed';
  else if (!state.transcribing && state.activeStep === 0 && state.transcriptionSegments.length === 0) jobStatus = 'Ready';

  if (!initialStateLoaded) return <div className="flex justify-center items-center h-screen">Loading...</div>;

  return (
      <main className="container mx-auto p-4 max-w-5xl">
         {/* Progress Steps */}
         <Card className="mb-8 shadow-lg backdrop-blur-sm bg-white/80 dark:bg-black/70 border-white/5">
           <CardContent className="pt-6">
             <div className="flex justify-between items-center relative">
               <div className="absolute top-1/2 left-0 right-0 h-1 bg-muted -translate-y-1/2 rounded-full overflow-hidden">
                 <div className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-500 ease-out" 
                      style={{ width: `${(state.activeStep / (steps.length - 1)) * 100}%` }} />
               </div>
               {steps.map((step, index) => (
                   <div key={index} className="flex flex-col items-center relative z-10">
                     <div className={`rounded-full w-8 h-8 flex items-center justify-center border-2 transition-all duration-300 
                         ${state.activeStep >= index ? 'bg-primary text-primary-foreground border-primary' : 'bg-muted text-muted-foreground border-border'}
                         ${state.activeStep === index ? 'ring-2 ring-primary ring-offset-2 dark:ring-offset-background' : ''}`}>
                       {state.activeStep > index ? '✓' : (state.activeStep === index && (state.loading || (index === 2 && state.transcribing)) ? <MiniSpinner /> : index + 1)}
                     </div>
                     <span className={`text-xs sm:text-sm mt-2 font-medium ${state.activeStep >= index ? 'text-primary' : 'text-muted-foreground'}`}>{step}</span>
                   </div>
               ))}
             </div>
           </CardContent>
         </Card>

         <Card className="shadow-md backdrop-blur-sm bg-white/80 dark:bg-black/70 border-white/5 mb-6">
             <CardHeader>
                 <CardTitle className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600">
                     Video Transcription
                 </CardTitle>
             </CardHeader>
             <CardContent className="space-y-6 pt-0">
                 <div className="space-y-4">
                     <div>
                         <Label className="font-semibold mb-2 block">Processing Model</Label>
                         <ProcessingOptionsSelector selectedOption={state.transcriptionModel} onOptionChange={(val) => dispatch({ type: ACTIONS.SET_TRANSCRIPTION_MODEL, payload: val })} />
                     </div>
                     
                     <div className="grid gap-4 md:grid-cols-2">
                         <div className="space-y-2">
                             <Label htmlFor="youtube-url">YouTube URL</Label>
                             <Input id="youtube-url" placeholder="https://youtube.com/watch?v=..." value={state.youtubeUrl} onChange={(e) => dispatch({ type: ACTIONS.SET_YOUTUBE_URL, payload: e.target.value })} 
                                 className={!validateYoutubeUrl(state.youtubeUrl) && state.youtubeUrl ? 'border-red-500' : ''} />
                         </div>
                         <div className="space-y-2">
                             <Label htmlFor="obsidian-dir">Save Directory</Label>
                             <div className="flex gap-2">
                                 <Input
                                     id="obsidian-dir"
                                     placeholder={appConfig?.DEFAULT_OBSIDIAN_DIR || "Full path on disk"}
                                     value={state.obsidianDir}
                                     onChange={(e) => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: e.target.value })}
                                     className={`flex-1 ${!validateObsidianDir(state.obsidianDir) && state.obsidianDir === '' ? 'border-amber-500/50' : ''}`}
                                 />
                                 {appConfig?.DEFAULT_OBSIDIAN_DIR && state.obsidianDir !== appConfig.DEFAULT_OBSIDIAN_DIR && (
                                     <Button
                                         type="button"
                                         variant="outline"
                                         size="sm"
                                         className="shrink-0 text-xs"
                                         onClick={() => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: appConfig.DEFAULT_OBSIDIAN_DIR })}
                                     >
                                         Use Default
                                     </Button>
                                 )}
                             </div>
                             {appConfig?.DEFAULT_OBSIDIAN_DIR && !state.obsidianDir && (
                                 <p className="text-xs text-muted-foreground">
                                     Default: <button
                                         type="button"
                                         className="text-primary hover:underline cursor-pointer"
                                         onClick={() => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: appConfig.DEFAULT_OBSIDIAN_DIR })}
                                     >
                                         {appConfig.DEFAULT_OBSIDIAN_DIR}
                                     </button>
                                 </p>
                             )}
                         </div>
                     </div>

                     <Button className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 shadow-lg shadow-cyan-900/20"
                         onClick={onProcessVideo}
                         disabled={state.loading || !validateYoutubeUrl(state.youtubeUrl) || !validateObsidianDir(state.obsidianDir)}>
                         {state.loading ? 'Processing...' : 'Start Transcription'}
                     </Button>
                 </div>
             </CardContent>
         </Card>

         {state.transcribing && (
             <TranscriptionJobSummary 
                 videoTitle={state.videoMetadata?.title || state.youtubeUrl} 
                 selectedApiModel={state.transcriptionModel} 
                 overallStatus={jobStatus} 
                 elapsedTime={formatElapsedTime(elapsedTime)} 
             />
         )}

         <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
             {/* Status Box */}
             <Card className="shadow-md glass-card h-[400px] flex flex-col">
                 <CardHeader className="py-3 px-4 border-b border-white/5">
                     <div className="flex justify-between items-center">
                         <CardTitle className="text-base">System Status</CardTitle>
                         <span className={`px-2 py-0.5 text-[10px] font-mono rounded-full ${backendStatus === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                             {backendStatus}
                         </span>
                     </div>
                 </CardHeader>
                 <CardContent className="flex-1 p-0 overflow-hidden">
                     <ScrollArea className="h-full w-full p-3">
                         <div ref={statusBoxRef}>
                             <StatusUpdates updates={state.statusUpdates} model={state.transcriptionModel} />
                         </div>
                         <ScrollBar orientation="vertical" />
                     </ScrollArea>
                 </CardContent>
             </Card>

             {/* Live Transcription Box */}
             <Card className="shadow-md glass-card h-[400px] flex flex-col">
                 <CardHeader className="py-3 px-4 border-b border-white/5 flex flex-row justify-between items-center">
                     <CardTitle className="text-base">Live Output</CardTitle>
                     {state.transcribing && (
                        <span className="text-xs font-mono text-cyan-400 animate-pulse">{formatElapsedTime(elapsedTime)}</span>
                     )}
                 </CardHeader>
                 <CardContent className="flex-1 p-0 overflow-hidden">
                     <ScrollArea ref={scrollAreaRef} className="h-full w-full p-3">
                         <div className="space-y-2">
                             {state.transcriptionSegments.length > 0 ? (
                                 state.transcriptionSegments.map((segment, index) => (
                                     <TranscriptionSegment key={segment.id || index} segment={segment} index={index} isLatest={index === state.transcriptionSegments.length - 1} isTranscribing={state.transcribing} model={state.transcriptionModel} />
                                 ))
                             ) : (
                                 <div className="flex items-center justify-center h-full text-muted-foreground text-sm">Waiting for data...</div>
                             )}
                         </div>
                         <ScrollBar orientation="vertical" />
                     </ScrollArea>
                 </CardContent>
             </Card>
         </div>

         {jobStatus === 'Completed' && (
             <div className="mt-8">
                <CompletedTranscriptionView transcriptionData={state.transcriptionData} model={state.transcriptionModel} />
             </div>
         )}
      </main>
  );
}
