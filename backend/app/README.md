# Advanced Search System Documentation

## Overview
This system provides a sophisticated multi-modal search capability combining keyword, semantic, and hybrid search approaches.

## Core Components

### 1. Search Methods
- **Keyword Search**: Text-based search using database full-text search
- **Dot Product Search**: Semantic search using embedding similarity
- **Advanced Hybrid Search**: Combined semantic and context-aware search

### 2. Display Flow
1. Combined Search Operation
   - Shows query and initializes search
   - Displays: `📊 Combined Search Operation`

2. Individual Search Execution
   - Shows each search with its icon and results immediately
   - Keyword Search: `🔍 Executing Keyword Search`
   - Dot Product Search: `🎯 Executing Dot Product Search`
   - Advanced Hybrid Search: `🔄 Executing Advanced Hybrid Search`

3. Initial Results Display
   - Shows all results sorted by score
   - Full details for each result
   - Statistics by search method
   - [Pause for review] `👉 Press Enter to continue...`

4. Combined Results Processing
   - Removes duplicates with progress indicator
   - Shows statistics and distribution
   - Displays final combined results

5. Analysis Phase
   - Filtering stage with progress
   - Prioritization with progress
   - Analysis preparation
   - AI analysis from both providers

### 3. Result Types
- Document Embeddings (📄)
- Video Transcriptions (🎬)
- Full Transcriptions (📽️)

### 4. Analysis Providers
- OpenAI (GPT-4)
- Groq (Llama)

## Key Features

### Source-Specific Styling
- Document Embeddings: Blue theme
- Video Transcriptions: Green theme
- Full Transcriptions: Magenta theme

### Search Method Styling
- Keyword Search: Cyan theme
- Dot Product Search: Blue theme
- Advanced Hybrid Search: Green theme

### Score Indicators
- High (≥ 0.8): 🟢 Bold Green
- Medium (≥ 0.6): 🟡 Bold Yellow
- Low (< 0.6): 🔴 Bold Red

