import React from 'react';

// TODO: Consider moving these to a shared utils file
const TRANSCRIPTION_STYLES = {
  groq: {
    icon: '☁️',
    color: 'blue',
    border: 'blue-200',
    content_color: 'blue-700',
    title: 'Groq Cloud Transcription',
    hover: 'hover:bg-blue-50 dark:hover:bg-blue-900/20'
  },
  'faster-whisper': {
    icon: '💻',
    color: 'green',
    border: 'green-200',
    content_color: 'green-700',
    title: 'Local Whisper Transcription',
    hover: 'hover:bg-green-50 dark:hover:bg-green-900/20'
  },
  default: {
    icon: '🎙️',
    color: 'gray',
    border: 'gray-200',
    content_color: 'gray-700',
    title: 'Transcription',
    hover: 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
  }
};

// TODO: Consider moving this to a shared utils file
const formatTimeStamp = (seconds) => {
  if (isNaN(seconds) || seconds < 0) return '00:00.00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 100);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(2, '0')}`;
};

const TranscriptionSegment = ({ segment, index, isLatest, isTranscribing, model }) => {
    const style = TRANSCRIPTION_STYLES[model] || TRANSCRIPTION_STYLES.default;
    const duration = segment.end_time && segment.start_time && !isNaN(segment.end_time) && !isNaN(segment.start_time)
        ? (segment.end_time - segment.start_time).toFixed(2) + 's'
        : '';

    return (
        <div className={
            `group relative rounded-lg p-3 transition-colors ` +
            (style.border === 'blue-200' ? 'border-blue-200 hover:bg-blue-50 dark:hover:bg-blue-900/20 ' : '') +
            (style.border === 'green-200' ? 'border-green-200 hover:bg-green-50 dark:hover:bg-green-900/20 ' : '') +
            (style.border === 'gray-200' ? 'border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800/50 ' : '')
        }>
            {/* Header with timestamp and watch link */}
            <div className="flex justify-between items-center mb-1 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                    <span>{style.icon}</span>
                    <span>
                        {formatTimeStamp(segment.start_time)} - {formatTimeStamp(segment.end_time)}
                        {duration && ` (${duration})`}
                    </span>
                </div>

                {segment.watch_url && (
                    <a
                        href={segment.watch_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`opacity-0 group-hover:opacity-100 transition-opacity text-${style.color}-600 hover:underline flex items-center`}
                        title="Watch segment on YouTube"
                    >
                        <span className="mr-1">Watch</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                )}
            </div>

            {/* Transcription text */}
            <div className={
                `text-sm sm:text-base leading-relaxed ` +
                (style.content_color === 'blue-700' ? 'text-blue-700 dark:text-blue-300 ' : '') +
                (style.content_color === 'green-700' ? 'text-green-700 dark:text-green-300 ' : '') +
                (style.content_color === 'gray-700' ? 'text-gray-700 dark:text-gray-300 ' : '')
            }>
                {segment.speaker && <strong className="mr-1">{segment.speaker}:</strong>}
                {segment.text}
                {isLatest && isTranscribing && (
                    <span className={
                        `inline-block w-1.5 h-4 ml-0.5 animate-pulse-fast align-middle ` +
                        (style.color === 'blue' ? 'bg-blue-500 ' : '') +
                        (style.color === 'green' ? 'bg-green-500 ' : '') +
                        (style.color === 'gray' ? 'bg-gray-500 ' : '')
                    }></span>
                )}
            </div>
        </div>
    );
};

export default TranscriptionSegment;