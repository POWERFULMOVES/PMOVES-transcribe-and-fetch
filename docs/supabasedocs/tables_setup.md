# Supabase Database Tables Setup

## Document Embeddings Table

| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| id                | integer          | number               |             |
| video_id          | text             | string               |             |
| start_time        | text             | string               |             |
| end_time          | text             | string               |             |
| text              | text             | string               |             |
| summary           | text             | string               |             |
| segment_ids       | text[]           | array                |             |
| watch_url         | text             | string               |             |
| created_at        | timestamp with time zone | string       |             |
| embedding         | public.vector(1536) | string            |             |
| summary_embedding | public.vector(1536) | string            |             |

## Video Transcriptions Table

| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| id                | uuid             | string               |             |
| video_id          | text             | string               |             |
| segment_id        | integer          | number               |             |
| watch_url         | text             | string               |             |
| start_time        | text             | string               |             |
| end_time          | text             | string               |             |
| content           | text             | string               |             |
| created_at        | timestamp with time zone | string       |             |
| metadata          | jsonb            | json                 |             |
| summary           | text             | string               |             |
| embedding         | public.vector(1536) | string            |             |
| summary_embedding | public.vector(1536) | string            |             |
| chunk_id          | integer          | number               |             |
| full_transcript_id| text             | string               |             |

## Video Transcriptions Full Table

| Name              | Format           | Type                 | Description |
|-------------------|------------------|----------------------|-------------|
| video_id          | text             | string               |             |
| full_transcript   | text             | string               |             |
| upload_date       | timestamp with time zone | string       |             |
| source_file       | text             | string               |             |