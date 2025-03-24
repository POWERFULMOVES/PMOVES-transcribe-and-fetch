-- SQL to create required tables for PMOVES content upserter

-- Table for storing web page content
CREATE TABLE IF NOT EXISTS webpage_content (
    id SERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    source_file TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    content_type TEXT DEFAULT 'webpage',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing text and markdown content
CREATE TABLE IF NOT EXISTS text_content (
    id SERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    content_type TEXT DEFAULT 'text',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing media file metadata
CREATE TABLE IF NOT EXISTS media_content (
    id SERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    source_url TEXT,
    duration TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    content_type TEXT NOT NULL, -- 'video' or 'audio'
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add enable_row_level_security to video_transcriptions if it doesn't exist
ALTER TABLE IF EXISTS video_transcriptions ENABLE ROW LEVEL SECURITY;

-- Add enable_row_level_security to video_transcriptions_full if it doesn't exist
ALTER TABLE IF EXISTS video_transcriptions_full ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for all tables
CREATE POLICY "Allow public access to webpage_content" ON webpage_content FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to text_content" ON text_content FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to media_content" ON media_content FOR ALL USING (true) WITH CHECK (true); 