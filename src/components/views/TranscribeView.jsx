"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { ProcessingOptionsSelector } from "@/components/processing-options-selector";
import { TranscriptionJobSummary } from "@/components/transcription-job-summary";
import { StatusUpdates } from "@/components/status-updates";
import { TranscriptionSegment } from "@/components/transcription-segment";
import { CompletedTranscriptionView } from "@/components/completed-transcription-view";
import { ACTIONS, validateYoutubeUrl, validateObsidianDir } from "@/app/reducers/transcriptionReducer";
import { useRef, useEffect } from "react";

// Helper for formatted time (could he moved to utils)
const formatElapsedTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export function TranscribeView({ 
    state, 
    dispatch, 
    onProcessVideo, 
    backendStatus, 
    elapsedTime, 
    timerActive, 
    jobStatus, 
    configLoading, 
    appConfig,
    initialStateLoaded 
}) {
    const statusBoxRef = useRef(null);
    const scrollAreaRef = useRef(null);

    // Auto-scroll status updates
    useEffect(() => {
        if (statusBoxRef.current) {
            statusBoxRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
        }
    }, [state.statusUpdates]);

    // Auto-scroll transcription segments
    useEffect(() => {
        if (state.transcribing && scrollAreaRef.current) {
            const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollContainer) {
                scrollContainer.scrollTo({
                    top: scrollContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }
        }
    }, [state.transcriptionSegments, state.transcribing]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
        >
            <Card className="glass-card">
                <CardHeader>
                    <CardTitle>Video Transcription Setup</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 pt-6">
                    {/* Model Selection */}
                    <div className="space-y-2">
                        <Label className="font-semibold">Transcription Processing Option</Label>
                        <ProcessingOptionsSelector
                            selectedOption={state.transcriptionModel}
                            onOptionChange={(value) => dispatch({ type: ACTIONS.SET_TRANSCRIPTION_MODEL, payload: value })}
                        />
                    </div>

                    {/* YouTube URL Input */}
                    <div className="space-y-2">
                        <Label htmlFor="youtube-url" className="font-semibold">YouTube Video URL</Label>
                        <Input
                            id="youtube-url"
                            type="text"
                            placeholder="https://www.youtube.com/watch?v=..."
                            value={state.youtubeUrl}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_YOUTUBE_URL, payload: e.target.value })}
                            className={!validateYoutubeUrl(state.youtubeUrl) && state.youtubeUrl ? 'border-red-500' : ''}
                        />
                        {!validateYoutubeUrl(state.youtubeUrl) && state.youtubeUrl && (
                            <p className="text-xs text-red-600">Please enter a valid YouTube URL.</p>
                        )}
                    </div>

                    {/* Directory Input */}
                    <div className="space-y-2">
                        <Label htmlFor="obsidian-dir" className="font-semibold">Save Directory (Full Path)</Label>
                        <Input
                            id="obsidian-dir"
                            type="text"
                            placeholder={appConfig?.DEFAULT_OBSIDIAN_DIR || "e.g., /path/to/transcripts"}
                            value={state.obsidianDir}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_OBSIDIAN_DIR, payload: e.target.value })}
                            className={!validateObsidianDir(state.obsidianDir) && state.obsidianDir ? 'border-red-500' : ''}
                            disabled={configLoading}
                        />
                        {!validateObsidianDir(state.obsidianDir) && state.obsidianDir && (
                            <p className="text-xs text-red-600">Save directory cannot be empty.</p>
                        )}
                         <p className="text-xs text-muted-foreground">Enter the full path where transcripts should be saved.</p>
                    </div>

                    {/* Output Folder (Optional) */}
                    <div className="space-y-2">
                        <Label htmlFor="output-folder">Output Subfolder (Optional)</Label>
                        <Input
                            id="output-folder"
                            type="text"
                            placeholder={appConfig?.DEFAULT_OUTPUT_FOLDER || "e.g., output"}
                            value={state.outputFolder}
                            onChange={(e) => dispatch({ type: ACTIONS.SET_OUTPUT_FOLDER, payload: e.target.value })}
                            disabled={configLoading}
                        />
                    </div>

                    {/* Process Button */}
                    <Button
                        className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-2 px-4 rounded transition-all hover-lift"
                        onClick={onProcessVideo}
                        disabled={state.loading || !validateYoutubeUrl(state.youtubeUrl) || !validateObsidianDir(state.obsidianDir) || !initialStateLoaded}
                    >
                        {state.loading ? (
                            <>
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Processing...
                            </>
                        ) : 'Process Video'}
                    </Button>
                </CardContent>
            </Card>

            {/* Transcription Job Summary */}
            {state.transcribing && (
                <TranscriptionJobSummary
                    videoTitle={state.videoMetadata?.title || state.youtubeUrl}
                    selectedApiModel={state.transcriptionModel}
                    overallStatus={jobStatus}
                    elapsedTime={formatElapsedTime(elapsedTime)}
                />
            )}

            {/* Output Area (Status + Live Segments) */}
            <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status Updates */}
                <Card className="glass-card">
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <CardTitle>Status Updates</CardTitle>
                            <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                backendStatus === 'connected' ? 'bg-green-500/20 text-green-500' :
                                backendStatus === 'error' ? 'bg-red-500/20 text-red-500' :
                                'bg-yellow-500/20 text-yellow-500'
                            }`}>
                                Backend: {backendStatus.charAt(0).toUpperCase() + backendStatus.slice(1)}
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[300px] w-full rounded-md border border-white/5 bg-black/20 p-3">
                            <div ref={statusBoxRef}>
                                <StatusUpdates updates={state.statusUpdates} model={state.transcriptionModel} />
                            </div>
                            <ScrollBar orientation="vertical" />
                        </ScrollArea>
                    </CardContent>
                </Card>

                {/* Live Transcription */}
                <Card className="glass-card">
                    <CardHeader className="flex flex-row justify-between items-center pb-2">
                        <CardTitle>Live Transcription</CardTitle>
                        <div className="flex items-center space-x-2">
                            {state.transcriptionModel && (
                                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-primary/10 text-primary">
                                    {state.transcriptionModel === "groq" ? "☁️ Cloud" : "💻 Local"}
                                </span>
                            )}
                            {state.transcribing && (
                                <span className={`text-sm text-primary flex items-center ${timerActive ? 'animate-pulse' : ''}`}>
                                    {timerActive && (
                                        <div className="h-2 w-2 rounded-full bg-primary mr-2 animate-ping" />
                                    )}
                                    {formatElapsedTime(elapsedTime)}
                                </span>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea ref={scrollAreaRef} className="h-[300px] w-full rounded-md border border-white/5 bg-black/20 p-3">
                            <div className="space-y-2">
                                {state.transcriptionSegments.length > 0 ? (
                                    state.transcriptionSegments.map((segment, index) => (
                                        <TranscriptionSegment
                                            key={segment.id || `seg-${index}-${Math.random()}`}
                                            segment={segment}
                                            index={index}
                                            isLatest={index === state.transcriptionSegments.length - 1}
                                            isTranscribing={state.transcribing}
                                            model={state.transcriptionModel}
                                        />
                                    ))
                                ) : (
                                    <div className="flex items-center justify-center h-full text-muted-foreground text-sm py-10">
                                        {state.loading || state.transcribing ? "Waiting for transcription data..." : "Transcription output will appear here."}
                                    </div>
                                )}
                            </div>
                            <ScrollBar orientation="vertical" />
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>

            {/* Completed View */}
            {jobStatus === 'Completed' && (
                <CompletedTranscriptionView
                    transcriptionData={state.transcriptionData}
                    model={state.transcriptionModel}
                />
            )}
        </motion.div>
    );
}
