import React, { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import TranscriptionSegment from './TranscriptionSegment'; // Assuming it's in the same directory

const CompletedTranscriptionView = ({ transcriptionData, model }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState("segmented");

  const segments = useMemo(() => transcriptionData?.segments || [], [transcriptionData]);
  const fullText = transcriptionData?.fullText || "";

  const filteredSegments = useMemo(() => {
    if (!searchTerm) {
      return segments;
    }
    return segments.filter(segment =>
      segment.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (segment.speaker && segment.speaker.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [segments, searchTerm]);

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(fullText)
      .then(() => {
        // Consider adding a toast notification for success
        console.log('Full transcript copied to clipboard');
      })
      .catch(err => {
        // Consider adding a toast notification for error
        console.error('Failed to copy full transcript: ', err);
      });
  };

  if (!transcriptionData || segments.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No completed transcription data available.
      </div>
    );
  }

  return (
    <div className="mt-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} defaultValue="segmented" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-4">
          <TabsTrigger value="segmented">Segmented Transcript</TabsTrigger>
          <TabsTrigger value="full">Full Transcript</TabsTrigger>
          <TabsTrigger value="download">Download Options</TabsTrigger>
        </TabsList>

        <TabsContent value="segmented">
          <div className="mb-4">
            <Input
              type="text"
              placeholder="Search segments (text or speaker)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <ScrollArea className="h-[400px] w-full rounded-md border p-3">
            <div className="space-y-2">
              {filteredSegments.length > 0 ? (
                filteredSegments.map((segment, index) => (
                  <TranscriptionSegment
                    key={segment.id || `completed-seg-${index}`}
                    segment={segment}
                    index={index}
                    model={model || 'default'} // Pass model or a default
                    // isLatest and isTranscribing are not relevant here
                  />
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No segments match your search term.
                </div>
              )}
            </div>
            <ScrollBar orientation="vertical" />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="full">
          <div className="mb-4">
            <Button onClick={handleCopyToClipboard} className="w-full sm:w-auto">
              Copy Full Transcript to Clipboard
            </Button>
          </div>
          <ScrollArea className="h-[400px] w-full rounded-md border p-4 bg-muted/30 dark:bg-muted/10">
            <pre className="whitespace-pre-wrap text-sm">{fullText}</pre>
            <ScrollBar orientation="vertical" />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="download">
          <div className="space-y-3 p-4 border rounded-md">
            <h3 className="text-lg font-semibold mb-3">Download Transcript</h3>
            <Button className="w-full justify-start" variant="outline" onClick={() => alert('Download TXT (Not Implemented)')}>
              Download as TXT (.txt)
            </Button>
            <Button className="w-full justify-start" variant="outline" onClick={() => alert('Download SRT (Not Implemented)')}>
              Download as SRT (.srt)
            </Button>
            <Button className="w-full justify-start" variant="outline" onClick={() => alert('Download VTT (Not Implemented)')}>
              Download as VTT (.vtt)
            </Button>
            <Button className="w-full justify-start" variant="outline" onClick={() => alert('Download JSON (Not Implemented)')}>
              Download as JSON (.json)
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CompletedTranscriptionView;