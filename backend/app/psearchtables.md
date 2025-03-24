# Search Display Standards

## Search Process Flow

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

## Table Layout

### Standard Result Fields
- Score (right-aligned, bold)
- Method (with icon, method-specific color)
- Source (with icon, source-specific color)
- Video ID (yellow)
- Content (source-specific color)
- Summary (cyan)
- Metadata (white)
- Start Time (cyan)
- End Time (cyan)
- Segment ID (yellow)
- Watch URL (underlined blue)

### Source-Specific Styling
1. Document Embeddings (📄 Blue)
   - Border: Blue
   - Content: Bright Blue
   - Icon: 📄

2. Video Transcriptions (🎬 Green)
   - Border: Green
   - Content: Bright Green
   - Icon: 🎬

3. Full Transcriptions (📽️ Magenta)
   - Border: Magenta
   - Content: Bright Magenta
   - Icon: 📽️

### Search Method Styling
1. Keyword Search
   - Icon: 🔍
   - Color: Cyan
   - Border: Cyan

2. Dot Product Search
   - Icon: 🎯
   - Color: Blue
   - Border: Blue

3. Advanced Hybrid Search
   - Icon: 🔄
   - Color: Green
   - Border: Green

### Score Coloring
- High (≥ 0.8): Bold Green 🟢
- Medium (≥ 0.6): Bold Yellow 🟡
- Low (< 0.6): Bold Red 🔴
- N/A: Dim ⚪

### Progress Indicators
- Success: ✓ (green)
- Error: ❌ (red)
- Warning: ⚠️ (yellow)
- Info: ℹ️ (cyan)
- Analysis: 🤖 (cyan)
- Statistics: 📊 (cyan)

## Data Map

### Document Embeddings Table
| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| id                | integer          | number               | Unique identifier |
| video_id          | text             | string               | Associated video ID |
| start_time        | text             | string               | Segment start time |
| end_time          | text             | string               | Segment end time |
| text              | text             | string               | Content text |
| summary           | text             | string               | Content summary |
| segment_ids       | text[]           | array                | Related segment IDs |
| watch_url         | text             | string               | Video URL with timestamp |
| created_at        | timestamp        | string               | Creation timestamp |
| embedding         | vector(1536)     | float[]              | Content embedding |
| summary_embedding | vector(1536)     | float[]              | Summary embedding |

### Video Transcriptions Table
| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| id                | uuid             | string               | Unique identifier |
| video_id          | text             | string               | Associated video ID |
| segment_id        | integer          | number               | Segment number |
| watch_url         | text             | string               | Video URL with timestamp |
| start_time        | text             | string               | Segment start time |
| end_time          | text             | string               | Segment end time |
| content           | text             | string               | Segment content |
| created_at        | timestamp        | string               | Creation timestamp |
| metadata          | jsonb            | object               | Additional metadata |
| summary           | text             | string               | Segment summary |
| embedding         | vector(1536)     | float[]              | Content embedding |
| summary_embedding | vector(1536)     | float[]              | Summary embedding |
| chunk_id          | integer          | number               | Associated chunk ID |
| full_transcript_id| text             | string               | Full transcript reference |

### Video Transcriptions Full Table
| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| video_id          | text             | string               | Video identifier |
| full_transcript   | text             | string               | Complete transcript |
| upload_date       | timestamp        | string               | Upload timestamp |
| source_file       | text             | string               | Source file path |

## Search Functions

### Keyword Search
- Function: `keyword_search(query: str, limit: int = 10)`
- Description: Text-based search using database full-text search
- Parameters:
  - query: Search text
  - limit: Maximum results (default: 10)
- Returns: List[SearchResult]

### Dot Product Search
- Function: `dot_product_search(query: str, limit: int = 10, use_summary: bool = False)`
- Description: Semantic search using embedding similarity
- Parameters:
  - query: Search text
  - limit: Maximum results (default: 10)
  - use_summary: Use summary embeddings (default: False)
- Returns: List[SearchResult]

### Advanced Hybrid Search
- Function: `advanced_hybrid_search(query: str, limit: int = 10, content_weight: float = 0.7)`
- Description: Combined semantic and context-aware search
- Parameters:
  - query: Search text
  - limit: Maximum results (default: 10)
  - content_weight: Content vs summary weight (default: 0.7)
- Returns: List[SearchResult]

## Result Types and Formatting

### SearchResult Class

