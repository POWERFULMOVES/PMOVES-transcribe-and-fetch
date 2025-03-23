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
- Git and Git LFS
- FFmpeg (for audio processing)
- Groq API key (optional, for cloud processing)
- uv (for Python package management)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PMOVES-transcribe-and-fetch.git
cd PMOVES-transcribe-and-fetch
```

### 2. Set Up Git LFS

This project uses Git LFS to handle large files. If you don't have Git LFS installed, you can install it by following the instructions at [git-lfs.com](https://git-lfs.com/).

```bash
# Initialize Git LFS
git lfs install

# Pull LFS content
git lfs pull
```

### 3. Backend Setup

1. Install uv for Python package management if you don't have it already:

```bash
# Install uv
pip install uv
```

2. Create and activate a virtual environment using uv:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install Python dependencies:

```bash
uv pip install -r requirements.txt
```

4. Create a .env file from the example:

```bash
cp backend/.env.example backend/.env
```

5. Edit the .env file with your Groq API key (if needed)

### 4. Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
# or
yarn install
```

### 5. Run the Application

1. Start the backend server (in a separate terminal):

```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Project Structure
