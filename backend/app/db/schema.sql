-- Schema for PMOVES-transcribe-and-fetch database

-- Add new tables for the enhanced upserter system

-- Table for storing web page content
CREATE TABLE IF NOT EXISTS webpage_content (
    id BIGSERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT,
    url TEXT,
    content TEXT,
    source_file TEXT,
    upload_date TIMESTAMP,
    content_type TEXT DEFAULT 'webpage',
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing general text content
CREATE TABLE IF NOT EXISTS text_content (
    id BIGSERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT,
    url TEXT,
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    content_type TEXT,
    upload_date TIMESTAMP,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing media (video/audio) metadata
CREATE TABLE IF NOT EXISTS media_content (
    id BIGSERIAL PRIMARY KEY,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT,
    file_path TEXT,
    source_url TEXT,
    duration TEXT,
    content_type TEXT, -- 'video' or 'audio'
    processed BOOLEAN DEFAULT FALSE,
    transcript_id TEXT, -- link to video_transcriptions_full
    metadata JSONB DEFAULT '{}'::jsonb,
    upload_date TIMESTAMP,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add functions to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all content tables
CREATE TRIGGER update_webpage_content_updated_at
BEFORE UPDATE ON webpage_content
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_text_content_updated_at
BEFORE UPDATE ON text_content
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_media_content_updated_at
BEFORE UPDATE ON media_content
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Create search functions for the new content types
CREATE OR REPLACE FUNCTION search_all_content(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
) RETURNS TABLE (
    content_id TEXT,
    title TEXT,
    content TEXT,
    content_type TEXT,
    url TEXT,
    similarity float
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    -- First search video transcriptions
    SELECT 
        vt.video_id::TEXT as content_id,
        'Video Transcript'::TEXT as title,
        vt.content as content,
        'transcript'::TEXT as content_type,
        vt.watch_url as url,
        1 - (vt.embedding <=> query_embedding) as similarity
    FROM 
        video_transcriptions vt
    WHERE 
        1 - (vt.embedding <=> query_embedding) > match_threshold
    
    UNION ALL
    
    -- Search web pages
    SELECT 
        wp.content_id as content_id,
        wp.title as title,
        wp.content as content,
        wp.content_type as content_type,
        wp.url as url,
        1 - (wp.embedding <=> query_embedding) as similarity
    FROM 
        webpage_content wp
    WHERE 
        wp.embedding IS NOT NULL AND
        1 - (wp.embedding <=> query_embedding) > match_threshold
    
    UNION ALL
    
    -- Search text content
    SELECT 
        tc.content_id as content_id,
        tc.title as title,
        tc.content as content,
        tc.content_type as content_type,
        tc.url as url,
        1 - (tc.embedding <=> query_embedding) as similarity
    FROM 
        text_content tc
    WHERE 
        tc.embedding IS NOT NULL AND
        1 - (tc.embedding <=> query_embedding) > match_threshold
    
    UNION ALL
    
    -- Search media content (if it has transcripts)
    SELECT 
        mc.content_id as content_id,
        mc.title as title,
        vtf.full_transcript as content,
        mc.content_type as content_type,
        mc.source_url as url,
        1 - (vtf.embedding <=> query_embedding) as similarity
    FROM 
        media_content mc
    JOIN 
        video_transcriptions_full vtf ON mc.transcript_id = vtf.video_id
    WHERE 
        vtf.embedding IS NOT NULL AND
        1 - (vtf.embedding <=> query_embedding) > match_threshold
    
    ORDER BY 
        similarity DESC
    LIMIT 
        match_count;
END;
$$;

-- Example SQL for crawl_presets table
CREATE TABLE crawl_presets (
    preset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preset_name TEXT NOT NULL UNIQUE,
    description TEXT,
    version INTEGER DEFAULT 1,
    crawl_tool TEXT DEFAULT 'crawl4ai',
    strategy_definition JSONB NOT NULL,
    target_capability TEXT,
    tags JSONB,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Example, adjust if user table is different
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
