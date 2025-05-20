import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock, Cloud, Server } from 'lucide-react'; // Assuming lucide-react for icons

const TRANSCRIPTION_STYLES = {
  groq: { name: 'Groq Cloud', icon: Cloud, default: true },
  'faster-whisper': { name: 'Local GPU (Faster Whisper)', icon: Server },
};
 
const TranscriptionJobSummary = ({
  videoTitle,
  selectedApiModel, // e.g., 'groq' or 'local'
  overallStatus,
  elapsedTime,
  // estimatedTimeRemaining, // Optional
}) => {
  const modelDetails = TRANSCRIPTION_STYLES[selectedApiModel] || { name: 'Unknown Model', icon: Server };

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-lg">Transcription Job Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {videoTitle && (
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Video Title</p>
            <p className="text-base font-semibold">{videoTitle}</p>
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Processing Model</p>
          <div className="flex items-center text-base font-semibold">
            <modelDetails.icon className="mr-2 h-5 w-5 text-blue-500" />
            {modelDetails.name}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Overall Status</p>
          <p className="text-base font-semibold">{overallStatus || 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Elapsed Time</p>
          <div className="flex items-center text-base font-semibold">
            <Clock className="mr-2 h-5 w-5 text-green-500" />
            {elapsedTime ? `${elapsedTime}s` : '0s'}
          </div>
        </div>
        {/* {estimatedTimeRemaining && (
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Est. Time Remaining</p>
            <p className="text-base font-semibold">{estimatedTimeRemaining}</p>
          </div>
        )} */}
      </CardContent>
    </Card>
  );
};

export default TranscriptionJobSummary;