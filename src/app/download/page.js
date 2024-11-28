"use client";

import { useEffect, useRef, useReducer, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { downloadReducer, initialState as downloadInitialState, ACTIONS } from '../reducers/downloadReducer';
import { BACKEND_URL } from '@/lib/constants';

export default function Download() {
  const [url, setUrl] = useState('');
  const [options, setOptions] = useState({
    format: 'best',
    extractAudio: false,
    audioFormat: 'mp3',
    audioQuality: '192',
    downloadPlaylist: false,
    playlistStart: '1',
    playlistEnd: '',
    subtitles: false,
    subtitleLanguage: 'en',
    embedThumbnail: true,
    embedMetadata: true,
    keepVideo: true
  });

  const [state, dispatch] = useReducer(downloadReducer, downloadInitialState);
  const statusBoxRef = useRef(null);

  const handleOptionChange = (key, value) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  // Setup SSE connection for download status
  useEffect(() => {
    let eventSource = null;

    if (state.downloading) {
      eventSource = new EventSource(`${BACKEND_URL}/api/download-status`);
      
      eventSource.onmessage = (event) => {
        try {
          // Remove the "data: " prefix and parse the remaining JSON
          const jsonStr = event.data.replace(/^data: /, '');
          const data = JSON.parse(jsonStr);
          
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
            payload: {
              type: data.type,
              content: data.type === 'progress' 
                ? `Downloading: ${data.progress}%` 
                : data.message
            }
          });
          
          if (data.type === 'complete' || data.type === 'error') {
            dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: false });
            eventSource.close();
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error, event.data);
        }
      };

      eventSource.onerror = () => {
        console.error('SSE connection error');
        dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: false });
        eventSource.close();
      };
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [state.downloading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.RESET_STATUS });
    dispatch({ type: ACTIONS.SET_DOWNLOADING, payload: true });

    try {
      const response = await axios.post(`${BACKEND_URL}/api/download`, {
        url: url,
        options: options
      });

      if (response.data.status === 'success') {
        dispatch({
          type: ACTIONS.ADD_STATUS_UPDATE,
          payload: {
            type: 'status',
            content: `Download request accepted: ${response.data.title}`
          }
        });
      }
    } catch (error) {
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: error.response?.data?.detail || 'Download failed'
      });
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Download Video</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* URL Input */}
            <div className="space-y-2">
              <Label htmlFor="url">Video URL</Label>
              <Input
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter video URL"
                required
              />
            </div>

            {/* Download Options */}
            <Accordion type="single" collapsible>
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
                      <>
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
                      </>
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
                    )}
                  </div>

                  {/* Additional Options */}
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
                      <div className="space-y-2">
                        <Label>Subtitle Language</Label>
                        <Select value={options.subtitleLanguage} onValueChange={(value) => handleOptionChange('subtitleLanguage', value)}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="en">English</SelectItem>
                            <SelectItem value="es">Spanish</SelectItem>
                            <SelectItem value="fr">French</SelectItem>
                            <SelectItem value="de">German</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}

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

            <Button type="submit" disabled={state.downloading || !url}>
              {state.downloading ? "Downloading..." : "Download"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Status Window */}
      <Card>
        <CardHeader>
          <CardTitle>Download Status</CardTitle>
        </CardHeader>
        <CardContent>
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
                  return (
                    <div
                      key={index}
                      className={`text-sm ${
                        update.type === 'complete'
                          ? 'text-green-600 dark:text-green-400'
                          : ''
                      }`}
                    >
                      {update.content}
                    </div>
                  );
                })}

                {state.currentProgress && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{state.currentProgress.filename}</span>
                      <span>{state.currentProgress.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${state.currentProgress.progress}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Speed: {state.currentProgress.speed}</span>
                      <span>ETA: {state.currentProgress.eta}</span>
                      <span>Size: {state.currentProgress.total_size}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
