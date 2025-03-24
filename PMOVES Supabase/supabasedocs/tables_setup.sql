-- Database Schema for PMOVES Supabase

-- Document Embeddings Table
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    text TEXT NOT NULL,
    summary TEXT,
    segment_ids TEXT[],
    watch_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536),
    summary_embedding VECTOR(1536)
);

-- Video Transcriptions Table
CREATE TABLE IF NOT EXISTS video_transcriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    segment_id INTEGER,
    watch_url TEXT,
    start_time TEXT,
    end_time TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    summary TEXT,
    embedding VECTOR(1536),
    summary_embedding VECTOR(1536),
    chunk_id INTEGER,
    full_transcript_id TEXT
);

-- Video Transcriptions Full Table
CREATE TABLE IF NOT EXISTS video_transcriptions_full (
    video_id TEXT PRIMARY KEY,
    full_transcript TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_video_transcriptions_video_id ON video_transcriptions(video_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_video_id ON document_embeddings(video_id);

-- Enable Row Level Security
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcriptions_full ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public access to document_embeddings" ON document_embeddings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_transcriptions" ON video_transcriptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_transcriptions_full" ON video_transcriptions_full FOR ALL USING (true) WITH CHECK (true);

-- Extensions needed for vector operations and UUID generation
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 