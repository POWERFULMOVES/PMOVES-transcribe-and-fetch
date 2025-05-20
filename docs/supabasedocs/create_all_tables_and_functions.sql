-- Combined SQL file for PMOVES Supabase - Tables and Functions
-- This file contains all necessary tables, extensions, and functions for the PMOVES backend

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Required for word_similarity function

-- ==========================================
-- DATABASE TABLES
-- ==========================================

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_video_transcriptions_video_id ON video_transcriptions(video_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_video_id ON document_embeddings(video_id);
CREATE INDEX IF NOT EXISTS idx_webpage_content_content_id ON webpage_content(content_id);
CREATE INDEX IF NOT EXISTS idx_text_content_content_id ON text_content(content_id);
CREATE INDEX IF NOT EXISTS idx_media_content_content_id ON media_content(content_id);
CREATE INDEX IF NOT EXISTS idx_webpage_content_url ON webpage_content(url);

-- Enable Row Level Security
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcriptions_full ENABLE ROW LEVEL SECURITY;
ALTER TABLE webpage_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE text_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_content ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public access to document_embeddings" ON document_embeddings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_transcriptions" ON video_transcriptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_transcriptions_full" ON video_transcriptions_full FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to webpage_content" ON webpage_content FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to text_content" ON text_content FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to media_content" ON media_content FOR ALL USING (true) WITH CHECK (true);

-- ==========================================
-- DATABASE FUNCTIONS
-- ==========================================

-- 1. Keyword Search Function
CREATE OR REPLACE FUNCTION public.keyword_search(query_text text, match_count integer)
 RETURNS TABLE(content text, source text, similarity double precision, metadata jsonb, segment_id integer, video_id text, watch_url text, start_time text, end_time text)
 LANGUAGE plpgsql
AS $function$
BEGIN
  RETURN QUERY
  -- Search in video_transcriptions table
  SELECT
    t.content,
    'video_transcriptions' AS source,
    word_similarity(t.content, query_text)::DOUBLE PRECISION AS similarity,
    t.metadata,
    t.segment_id,
    t.video_id,
    t.watch_url,
    t.start_time,
    t.end_time
  FROM video_transcriptions AS t
  WHERE t.content ILIKE '%' || query_text || '%'

  UNION ALL

  -- Search in video_transcriptions_full table
  SELECT
    ft.full_transcript AS content,
    'video_transcriptions_full' AS source,
    word_similarity(ft.full_transcript, query_text)::DOUBLE PRECISION AS similarity,
    NULL::JSONB AS metadata,
    NULL::INT AS segment_id,
    ft.video_id,  -- Return video_id directly
    NULL::TEXT AS watch_url,
    NULL::TEXT AS start_time,
    NULL::TEXT AS end_time
  FROM video_transcriptions_full AS ft
  WHERE ft.full_transcript ILIKE '%' || query_text || '%'

  UNION ALL

  -- Search in document_embeddings table
  SELECT
    de.text AS content,
    'document_embeddings' AS source,
    word_similarity(de.text, query_text)::DOUBLE PRECISION AS similarity,
    NULL::JSONB AS metadata,
    NULL::INT AS segment_id,
    de.video_id,
    de.watch_url,
    de.start_time,
    de.end_time
  FROM document_embeddings AS de
  WHERE de.text ILIKE '%' || query_text || '%'

  ORDER BY
    similarity DESC
  LIMIT match_count;
END;
$function$;

-- 2. Dot Product Search Function
CREATE OR REPLACE FUNCTION public.dot_product_search(query_embedding vector, match_count integer, content_weight double precision DEFAULT 1.0, summary_weight double precision DEFAULT 1.0, video_filter text DEFAULT NULL::text)
 RETURNS TABLE(content text, source text, similarity double precision, video_id text, segment_id integer, watch_url text, start_time text, end_time text, summary text, full_transcript text, context_before text, context_after text)
 LANGUAGE sql
AS $function$
WITH full_transcripts AS (
    SELECT
        video_id,
        full_transcript
    FROM video_transcriptions_full
),
ranked_results AS (
    -- Search in video_transcriptions table (individual segments)
    SELECT
        t.content,
        'video_transcriptions' AS source,
        (1 - (t.embedding <=> query_embedding)) * content_weight AS similarity,
        t.video_id,
        t.segment_id,
        t.watch_url,
        t.start_time,
        t.end_time,
        t.summary,
        ft.full_transcript,
        LAG(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) AS context_before,
        LEAD(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) AS context_after
    FROM video_transcriptions AS t
    LEFT JOIN full_transcripts ft ON ft.video_id = t.video_id
    WHERE t.embedding IS NOT NULL
      AND (video_filter IS NULL OR t.video_id = video_filter)
    
    UNION ALL
    
    -- Search in document_embeddings table
    SELECT
        d.text AS content,
        'document_embeddings' AS source,
        GREATEST(
            (1 - (d.embedding <=> query_embedding)) * content_weight,
            (1 - (d.summary_embedding <=> query_embedding)) * summary_weight
        ) AS similarity,
        d.video_id,
        NULL::INT AS segment_id,
        d.watch_url,
        d.start_time,
        d.end_time,
        d.summary,
        ft.full_transcript,
        NULL::TEXT AS context_before,
        NULL::TEXT AS context_after
    FROM document_embeddings AS d
    LEFT JOIN full_transcripts ft ON ft.video_id = d.video_id
    WHERE (d.embedding IS NOT NULL OR d.summary_embedding IS NOT NULL)
      AND (video_filter IS NULL OR d.video_id = video_filter)
      
    UNION ALL
    
    -- Search in video_transcriptions_full table
    SELECT
        ft.full_transcript AS content,
        'video_transcriptions_full' AS source,
        0.5 AS similarity,  -- Default similarity for full transcripts
        ft.video_id,
        NULL::INT AS segment_id,
        NULL::TEXT AS watch_url,
        'FULL' AS start_time,
        'FULL' AS end_time,
        NULL::TEXT AS summary,
        ft.full_transcript,
        NULL::TEXT AS context_before,
        NULL::TEXT AS context_after
    FROM video_transcriptions_full ft
    WHERE (video_filter IS NULL OR ft.video_id = video_filter)
)
SELECT
    content,
    source,
    similarity,
    video_id,
    segment_id,
    watch_url,
    start_time,
    end_time,
    summary,
    full_transcript,
    context_before,
    context_after
FROM ranked_results
WHERE content IS NOT NULL
  AND video_id IS NOT NULL
ORDER BY similarity DESC NULLS LAST
LIMIT match_count;
$function$;

-- 3. Advanced Hybrid Search Function
CREATE OR REPLACE FUNCTION public.advanced_hybrid_search(query_embedding vector, match_count integer, content_weight double precision, summary_weight double precision, video_filter text, min_similarity double precision)
 RETURNS TABLE(content text, source text, similarity double precision, video_id text, segment_id integer, watch_url text, start_time text, end_time text, summary text, full_transcript text, context_before text, context_after text)
 LANGUAGE sql
AS $function$
WITH full_transcripts AS (
    SELECT
        video_id,
        full_transcript
    FROM video_transcriptions_full
),
ranked_results AS (
    -- Search in video_transcriptions table (individual segments)
    SELECT
        t.content,
        'video_transcriptions' AS source,
        (1 - (t.embedding <=> query_embedding)) * content_weight AS similarity,
        t.video_id,
        t.segment_id,
        t.watch_url,
        t.start_time,
        t.end_time,
        t.summary,
        ft.full_transcript,
        -- Add context from surrounding segments
        LAG(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) as context_before,
        LEAD(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) as context_after,
        1 AS priority
    FROM video_transcriptions AS t
    LEFT JOIN full_transcripts ft ON ft.video_id = t.video_id
    WHERE t.embedding IS NOT NULL
      AND (1 - (t.embedding <=> query_embedding)) >= min_similarity
      AND (video_filter IS NULL OR t.video_id = video_filter)
    
    UNION ALL
    
    -- Search in document_embeddings table
    SELECT
        d.text AS content,
        'document_embeddings' AS source,
        GREATEST(
            (1 - (d.embedding <=> query_embedding)) * content_weight,
            (1 - (d.summary_embedding <=> query_embedding)) * summary_weight
        ) AS similarity,
        d.video_id,
        NULL::INT AS segment_id,
        d.watch_url,
        d.start_time,
        d.end_time,
        d.summary,
        ft.full_transcript,
        NULL::TEXT as context_before,
        NULL::TEXT as context_after,
        2 AS priority
    FROM document_embeddings AS d
    LEFT JOIN full_transcripts ft ON ft.video_id = d.video_id
    WHERE (d.embedding IS NOT NULL OR d.summary_embedding IS NOT NULL)
      AND GREATEST(
          (1 - (d.embedding <=> query_embedding)) * content_weight,
          (1 - (d.summary_embedding <=> query_embedding)) * summary_weight
      ) >= min_similarity
      AND (video_filter IS NULL OR d.video_id = video_filter)
      
    UNION ALL
    
    -- Search in video_transcriptions_full
    SELECT
        ft.full_transcript AS content,
        'video_transcriptions_full' AS source,
        0.5 AS similarity,
        ft.video_id,
        NULL::INT AS segment_id,
        NULL::TEXT AS watch_url,
        NULL::TEXT AS start_time,
        NULL::TEXT AS end_time,
        NULL::TEXT AS summary,
        ft.full_transcript,
        NULL::TEXT as context_before,
        NULL::TEXT as context_after,
        3 AS priority
    FROM full_transcripts AS ft
    WHERE (video_filter IS NULL OR ft.video_id = video_filter)
)
SELECT
    content,
    source,
    similarity,
    video_id,
    segment_id,
    watch_url,
    start_time,
    end_time,
    summary,
    full_transcript,
    context_before,
    context_after
FROM ranked_results
WHERE content IS NOT NULL
  AND video_id IS NOT NULL
  AND similarity >= min_similarity
ORDER BY priority, similarity DESC NULLS LAST
LIMIT match_count;
$function$;

-- ==========================================
-- DUPLICATE CHECKING FUNCTIONS
-- ==========================================

-- Check if webpage content already exists by URL
CREATE OR REPLACE FUNCTION public.check_webpage_duplicate(url_to_check text)
RETURNS TABLE("exists" boolean, content_id text) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    EXISTS(SELECT 1 FROM webpage_content WHERE webpage_content.url = url_to_check) as "exists",
    (SELECT webpage_content.content_id FROM webpage_content WHERE webpage_content.url = url_to_check LIMIT 1) as content_id;
END;
$$;

-- Check if text content already exists by content hash or title
CREATE OR REPLACE FUNCTION public.check_text_duplicate(title_to_check text, content_to_check text)
RETURNS TABLE("exists" boolean, content_id text) 
LANGUAGE plpgsql
AS $$
DECLARE
  content_hash text := md5(content_to_check);
BEGIN
  RETURN QUERY
  WITH existing_content AS (
    SELECT 
      text_content.content_id,
      md5(text_content.content) as hash
    FROM text_content
    WHERE text_content.title = title_to_check
  )
  SELECT 
    EXISTS(SELECT 1 FROM existing_content WHERE existing_content.hash = content_hash) as "exists",
    (SELECT existing_content.content_id FROM existing_content WHERE existing_content.hash = content_hash LIMIT 1) as content_id;
END;
$$;

-- Check if media content already exists by file path or source URL
CREATE OR REPLACE FUNCTION public.check_media_duplicate(file_path_to_check text, source_url_to_check text DEFAULT NULL)
RETURNS TABLE("exists" boolean, content_id text) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    EXISTS(
      SELECT 1 FROM media_content 
      WHERE media_content.file_path = file_path_to_check
      OR (media_content.source_url = source_url_to_check AND source_url_to_check IS NOT NULL)
    ) as "exists",
    (
      SELECT media_content.content_id FROM media_content 
      WHERE media_content.file_path = file_path_to_check
      OR (media_content.source_url = source_url_to_check AND source_url_to_check IS NOT NULL)
      LIMIT 1
    ) as content_id;
END;
$$;

-- Check if video transcription already exists by video_id
CREATE OR REPLACE FUNCTION public.check_video_transcription_duplicate(video_id_to_check text)
RETURNS TABLE("exists" boolean, id uuid) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    EXISTS(SELECT 1 FROM video_transcriptions_full WHERE video_transcriptions_full.video_id = video_id_to_check) as "exists",
    (SELECT video_transcriptions.id FROM video_transcriptions WHERE video_transcriptions.video_id = video_id_to_check LIMIT 1) as id;
END;
$$;

-- Upsert webpage content (insert or update if exists)
CREATE OR REPLACE FUNCTION public.upsert_webpage_content(
  p_content_id text,
  p_title text,
  p_url text,
  p_content text,
  p_source_file text DEFAULT NULL
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  exists_already boolean;
  existing_id text;
  result record;
BEGIN
  -- Check if the content already exists
  SELECT * FROM check_webpage_duplicate(p_url) INTO result;
  exists_already := result."exists";
  existing_id := result.content_id;
  
  IF exists_already THEN
    -- Update existing record
    UPDATE webpage_content
    SET 
      title = p_title,
      content = p_content,
      source_file = COALESCE(p_source_file, webpage_content.source_file),
      upload_date = CURRENT_TIMESTAMP
    WHERE webpage_content.content_id = existing_id;
    
    RETURN existing_id;
  ELSE
    -- Insert new record
    INSERT INTO webpage_content(content_id, title, url, content, source_file)
    VALUES (p_content_id, p_title, p_url, p_content, p_source_file);
    
    RETURN p_content_id;
  END IF;
END;
$$;

-- Upsert text content (insert or update if exists)
CREATE OR REPLACE FUNCTION public.upsert_text_content(
  p_content_id text,
  p_title text,
  p_content text,
  p_url text DEFAULT NULL,
  p_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  exists_already boolean;
  existing_id text;
  result record;
BEGIN
  -- Check if the content already exists
  SELECT * FROM check_text_duplicate(p_title, p_content) INTO result;
  exists_already := result."exists";
  existing_id := result.content_id;
  
  IF exists_already THEN
    -- Update existing record
    UPDATE text_content
    SET 
      content = p_content,
      url = COALESCE(p_url, text_content.url),
      metadata = COALESCE(p_metadata, text_content.metadata),
      upload_date = CURRENT_TIMESTAMP
    WHERE text_content.content_id = existing_id;
    
    RETURN existing_id;
  ELSE
    -- Insert new record
    INSERT INTO text_content(content_id, title, content, url, metadata)
    VALUES (p_content_id, p_title, p_content, p_url, p_metadata);
    
    RETURN p_content_id;
  END IF;
END;
$$;

-- Upsert media content (insert or update if exists)
CREATE OR REPLACE FUNCTION public.upsert_media_content(
  p_content_id text,
  p_title text,
  p_file_path text,
  p_content_type text,
  p_source_url text DEFAULT NULL,
  p_duration text DEFAULT NULL,
  p_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  exists_already boolean;
  existing_id text;
  result record;
BEGIN
  -- Check if the content already exists
  SELECT * FROM check_media_duplicate(p_file_path, p_source_url) INTO result;
  exists_already := result."exists";
  existing_id := result.content_id;
  
  IF exists_already THEN
    -- Update existing record
    UPDATE media_content
    SET 
      title = p_title,
      duration = COALESCE(p_duration, media_content.duration),
      metadata = COALESCE(p_metadata, media_content.metadata),
      upload_date = CURRENT_TIMESTAMP,
      processed = FALSE -- Reset processed flag to trigger reprocessing
    WHERE media_content.content_id = existing_id;
    
    RETURN existing_id;
  ELSE
    -- Insert new record
    INSERT INTO media_content(content_id, title, file_path, content_type, source_url, duration, metadata)
    VALUES (p_content_id, p_title, p_file_path, p_content_type, p_source_url, p_duration, p_metadata);
    
    RETURN p_content_id;
  END IF;
END;
$$; 