# PMOVES.AI Integration

## Service Description
This submodule (`PMOVES-transcribe-and-fetch`) acts as the primary service for extracting context from web URLs (using Jina.ai, Crawl4AI) and handling multi-provider media transcription. 

## Agentic Topology Mapping
- **Tier 4 (Worker)**: Handles `Extract Worker` and `LangExtract` operations.
- **Tier 5 (Media)**: Ingests `PMOVES.YT` (YouTube) URLs, transcodes with FFmpeg, and applies Whisper/Groq/Deepgram for transcription.
- **Tier 6 (Agent Bridge)**: Exposes `TranscribeAgent` and `MultimodalAgent` to the Pipecat orchestration layer.

## Holographic Integration
The output from this service (especially Markdown files and Obsidian-flavored text) is embedded into the **Geometry Bus** via CGP (Consciousness Geometry Protocol). These events are subsequently consumed by `pmoves/services/a2ui-renderer` to visualize the extracted knowledge graphs.

## Model Configuration
It natively supports local and cloud models:
- **Transcription**: OpenAI (Whisper), Groq (Whisper large), Deepgram (Nova-2), Local (Whisper.cpp/Torch).
- **Multimodal extraction**: Support for HuggingFace / Local multimodal layers (including configurations for `ollama/gemma3` and Gemma 4 iterations) for local vision processing.

## Security
- Validates file headers and blocks private IP fetches.
- Requires `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` for history tracking.
