# YouTube Video Transcriber & Content Fetcher

A powerful web application that transcribes YouTube videos using multiple AI models, with support for both local processing via Faster Whisper and cloud processing via Groq API. Built with Next.js frontend and Python FastAPI backend.

## Features

### Transcription Capabilities
- **Dual Processing Options**
  - Local processing using Faster Whisper (large-v3 model)
  - Cloud processing via Groq API for faster results
  - Support for different Whisper model sizes
  - Real-time transcription progress updates

### Output Formats
- **Multiple Export Options**
  - Plain text transcription
  - Timestamped segments with clickable YouTube links
  - CSV export with timestamps and segments
  - Excel export with full formatting and hyperlinks
  - PDF generation with formatted content
  - Markdown files in both plain text and table formats
  - Automatic file naming and organization

### Storage System
- **Flexible Storage Solutions**
  - Local output folder organization
  - Obsidian vault integration
  - Automatic directory structure:
    - `/mp4` - Audio files
    - `/csv` - Timestamped transcriptions
    - `/excel` - Formatted spreadsheets
    - `/md` - Markdown files
    - `/pdf` - PDF exports

### Processing Features
- **Advanced Video Handling**
  - Automatic video information extraction
  - Progress tracking with percentage updates
  - Real-time status notifications
  - Comprehensive error handling and reporting
  - Support for various video formats and qualities

### User Interface
- **Modern Design**
  - Clean, responsive interface using shadcn/ui
  - Dark/light theme support
  - Step-by-step progress tracking
  - Real-time status updates
  - Tab-based navigation
  - Model selection dropdown
  - Directory path configuration

## Prerequisites

- Python 3.10.11 or higher
- Node.js 18.x or higher
- Git
- FFmpeg (for audio processing)
- Groq API key (optional, for cloud processing)

## Installation

### Backend Setup

1. Clone the repository:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.

## Project Structure
