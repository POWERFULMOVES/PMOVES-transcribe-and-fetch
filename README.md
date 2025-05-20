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

## ⚡️ GPU Support (PyTorch with CUDA)

By default, `uv sync` will install the CPU-only version of PyTorch.

If you want GPU acceleration, after running `uv sync`, run:

```bash
uv pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

- **If your CUDA version is newer than the latest available PyTorch wheel (e.g., CUDA 12.8), use the closest lower version (e.g., `cu121` for CUDA 12.8).**
- You can check your CUDA version with `nvidia-smi`.
- This step is required because PyTorch CUDA wheels are not available on PyPI and must be installed from the official PyTorch index.

## GPU PyTorch Installation (Windows & WSL/Linux)

After running `uv sync`, run the following script to install the correct GPU-enabled PyTorch wheels:

**On Windows (PowerShell):**
```powershell
.\post_sync.ps1
```

**On WSL/Linux:**
```bash
./post_sync.sh
```

This will ensure you have the CUDA-enabled versions of torch, torchvision, and torchaudio installed for GPU acceleration.

## Prerequisites

- Python 3.12 or higher
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
pip install uv
```

2. Create and activate a virtual environment using uv:

```bash
# Create virtual environment with Python 3.12
uv venv --python=3.12

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install all Python dependencies using uv (from the project root):

```bash
uv sync
```

4. (Optional, but recommended for GPU users) Install CUDA-enabled PyTorch, torchvision, and torchaudio:

**On Windows (PowerShell):**
```powershell
.\post_sync.ps1
```

**On WSL/Linux:**
```bash
./post_sync.sh
```

This will ensure you have the CUDA-enabled versions of torch, torchvision, and torchaudio installed for GPU acceleration.

5. Create a .env file from the example:

```bash
cp backend/.env.example backend/.env
```

6. Edit the .env file with your Groq API key (if needed)

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

⚠️ **Windows Development Note for `crawl4ai` Users**

If you encounter a `NotImplementedError` related to `asyncio` or `playwright` when using features that involve `crawl4ai` (like the Fetch page) on a Windows development environment, it might be due to an incompatibility with Uvicorn's `--reload` flag.

Try running the backend server without the `--reload` flag:
```bash
cd backend
uvicorn app.main:app
```
This primarily affects development. Production deployments (which typically don't use `--reload`) should be fine as long as `asyncio.WindowsProactorEventLoopPolicy()` is set in `backend/app/main.py`.

2. Start the frontend development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

### 6. Running with Docker Compose (Recommended for LLM Features)

For a more robust setup, especially when utilizing features that depend on the centralized LLM management system (like advanced content fetching with `crawl4ai` or direct LLM interactions via `/api/v1/llm/*` endpoints), it is recommended to use Docker Compose. This project uses separate Docker Compose files for the backend application and the LiteLLM proxy.

**Prerequisites for Docker Compose:**
*   Docker and Docker Compose installed.
*   Ensure your `backend/app/.env` file is configured correctly. This file is used by both the backend and the LiteLLM proxy containers.
    *   **Provider API Keys:** (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`) must be in `backend/app/.env` for the LiteLLM proxy to use.
    *   **`LITELLM_PROXY_API_KEY`:** If you secure your LiteLLM proxy with a master key (recommended), set this in `backend/app/.env`. The backend service will also use this key to authenticate with the proxy.
    *   **`LITELLM_PROXY_URL`:** For the backend service, set this to point to the LiteLLM proxy (e.g., `http://litellm-proxy:4000` when running with the provided Docker Compose setup).
    *   Refer to `docs/llm_configuration.md` for detailed instructions on configuring `litellm_proxy_config/config.yaml` and the necessary environment variables.

**Steps:**

1.  **Start the LiteLLM Proxy:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose -f docker-compose.litellm-proxy.yml up -d
    ```
    This will start the LiteLLM proxy, which reads its model configurations from `litellm_proxy_config/config.yaml` and API keys from `backend/app/.env`.

2.  **Start the Backend Application:**
    In a separate terminal (or after the proxy is up), from the project root, run:
    ```bash
    docker-compose -f docker-compose.backend.yml up -d --build
    ```
    This builds and starts the FastAPI backend. It will connect to the LiteLLM proxy using the `LITELLM_PROXY_URL` and `LITELLM_PROXY_API_KEY` from `backend/app/.env`.

3.  **Start the Frontend Development Server (No Change):**
    ```bash
    npm run dev
    # or
    yarn dev
    ```
    The frontend will then connect to the backend service (typically running on `http://localhost:8000` or as configured).

Using this Docker Compose setup ensures that the LiteLLM proxy is available for the backend to manage and route LLM calls effectively.

## Project Structure

```
PMOVES-transcribe-and-fetch/
├── backend/
│   ├── app/
│   │   ├── requirements.txt          # Main project dependencies
│   │   ├── requirements.crawl4ai.txt # crawl4ai specific dependencies
│   │   └── requirements.lock         # Lock file for reproducible builds
│   └── .env
├── frontend/
│   └── ...
├── pyproject.toml                    # Python project metadata
└── README.md
```

## Dependency Management

All dependencies are now managed in `pyproject.toml`.
- To install all main dependencies: `uv sync`
- To install optional crawl4ai dependencies: `uv pip install .[crawl4ai]`

To update dependencies:
```bash
# Update single package
uv pip compile --upgrade-package package_name

# Update all packages
uv pip compile --upgrade

# After any changes, regenerate the lock file
uv pip compile backend/app/requirements.crawl4ai.txt backend/app/requirements.txt --output-file backend/app/requirements.lock

```

## Legacy, Experimental, and Backup Files (for cleanup)

The following files in `backend/app/` are legacy, experimental, or backup versions and are not used in production. They are safe to delete or archive unless you are actively developing or debugging:

- `transcribe1 copy.py`
- `transcribebak.py`
- `gtrans.py`
- `mainloang.py`
- `mainfixed.py`
- `main.py.bak.*` (all variants)
- `main.bak.py`
- `transcribe1.py.bak.*` (all variants)
- `transcribe1.py.backup`
- `psearchworking.py.fixed*`, `psearchworking.py.backup`, `psearchworking.py.original`, `psearchworking.py.new`, `psearchworking_fixed.py`
- `compsearchfix.py`
- `main.py.new`
- `test_embedding_fix.py`, `test_supabase.py`, `test_crawl4ai_isolated.py`, `test_playwright.py`, `test.py` (test/experimental)

**Note:** Only the following are considered production code for core backend services:
- `main.py`
- `transcribe1.py`
- `fetch_content.py`
- `download_manager.py`
- `pmoves_upserter.py`
- `psearchworking.py`
- `audio_processor.py`
- `utils.py`
- `config.py` and `config/`
- `routes/`, `monitoring/`, `db/`

If in doubt, check for imports or usage in `main.py` or the FastAPI app entrypoint.

## Note

A new folder `pmoves-pipecat-agent/` will contain the scaffold for the Pipecat-based SupabaseAgent, supporting chat-based command execution and agent summoning. See that directory for the latest agent communication logic.
