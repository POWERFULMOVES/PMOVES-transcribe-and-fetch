-- Combined SQL Migration Script for PMOVES Supabase
-- This script combines all versioned migrations (V1 to V5) for database initialization.

-- V1: Adds embedding and PDF path to webpage_content, and integrates webpages into search functions.
-- Ensure required extensions are enabled (idempotent)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- If not already globally enabled
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- If not already globally enabled

-- 1. Alter 'webpage_content' table
ALTER TABLE public.webpage_content
ADD COLUMN IF NOT EXISTS embedding VECTOR(1536) NULL,
ADD COLUMN IF NOT EXISTS pdf_path TEXT NULL;

-- Optional: Index for embedding column on webpage_content.
-- Consider the overall indexing strategy and if direct queries on this column are frequent.
-- CREATE INDEX IF NOT EXISTS idx_webpage_content_embedding ON public.webpage_content USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- 2. Update 'upsert_webpage_content' function
CREATE OR REPLACE FUNCTION public.upsert_webpage_content(
  p_content_id text,
  p_title text,
  p_url text,
  p_content text,
  p_embedding vector(1536), -- New parameter
  p_pdf_path text,         -- New parameter
  p_source_file text DEFAULT NULL
)
RETURNS text -- Returns the content_id of the upserted record
LANGUAGE plpgsql
AS $$
DECLARE
  result record;
  existing_record_content_id text;
BEGIN
  -- Check if a record with the given URL already exists
  SELECT wc.content_id INTO existing_record_content_id
  FROM public.webpage_content wc
  WHERE wc.url = p_url
  LIMIT 1;

  IF existing_record_content_id IS NOT NULL THEN
    -- URL exists, update the existing record
    UPDATE public.webpage_content
    SET
      title = p_title,
      content = p_content,
      embedding = p_embedding,
      pdf_path = p_pdf_path,
      source_file = COALESCE(p_source_file, public.webpage_content.source_file),
      upload_date = CURRENT_TIMESTAMP -- Assuming this also serves as 'updated_at'
    WHERE public.webpage_content.content_id = existing_record_content_id;
    RETURN existing_record_content_id;
  ELSE
    -- URL does not exist, insert a new record
    -- The p_content_id provided should be unique for this new entry
    INSERT INTO public.webpage_content(content_id, title, url, content, embedding, pdf_path, source_file, upload_date, created_at, content_type)
    VALUES (p_content_id, p_title, p_url, p_content, p_embedding, p_pdf_path, p_source_file, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'webpage')
    RETURNING webpage_content.content_id INTO result;
    RETURN result.content_id;
  END IF;
END;
$$;


-- 3. Update 'advanced_hybrid_search' function
CREATE OR REPLACE FUNCTION public.advanced_hybrid_search(
    query_embedding vector(1536),
    match_count integer,
    content_weight double precision,
    summary_weight double precision,
    video_filter text,
    min_similarity double precision
)
 RETURNS TABLE(
    content text,
    source text,
    similarity double precision,
    video_id text,
    segment_id integer,
    watch_url text,
    start_time text,
    end_time text,
    summary text,
    full_transcript text,
    context_before text,
    context_after text
)
 LANGUAGE sql
AS $function$
WITH full_transcripts AS (
    SELECT
        ft.video_id,
        ft.full_transcript
    FROM public.video_transcriptions_full AS ft
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
        LAG(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) as context_before,
        LEAD(t.content) OVER (PARTITION BY t.video_id ORDER BY t.segment_id) as context_after,
        1 AS priority
    FROM public.video_transcriptions AS t
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
    FROM public.document_embeddings AS d
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
        ft_main.full_transcript AS content,
        'video_transcriptions_full' AS source,
        0.5 AS similarity,
        ft_main.video_id,
        NULL::INT AS segment_id,
        NULL::TEXT AS watch_url,
        NULL::TEXT AS start_time,
        NULL::TEXT AS end_time,
        NULL::TEXT AS summary,
        ft_main.full_transcript,
        NULL::TEXT as context_before,
        NULL::TEXT as context_after,
        3 AS priority
    FROM full_transcripts AS ft_main
    WHERE (video_filter IS NULL OR ft_main.video_id = video_filter)

    UNION ALL -- New block for webpage_content

    SELECT
        wpc.content AS content,
        'webpage_content' AS source,
        (1 - (wpc.embedding <=> query_embedding)) * content_weight AS similarity,
        wpc.url AS video_id,
        NULL::INT AS segment_id,
        wpc.url AS watch_url,
        NULL::TEXT AS start_time,
        NULL::TEXT AS end_time,
        wpc.title AS summary,
        wpc.content AS full_transcript,
        NULL::TEXT AS context_before,
        NULL::TEXT AS context_after,
        4 AS priority
    FROM public.webpage_content AS wpc
    WHERE wpc.embedding IS NOT NULL
      AND (1 - (wpc.embedding <=> query_embedding)) >= min_similarity
      AND (video_filter IS NULL)
)
SELECT
    rr.content,
    rr.source,
    rr.similarity,
    rr.video_id,
    rr.segment_id,
    rr.watch_url,
    rr.start_time,
    rr.end_time,
    rr.summary,
    rr.full_transcript,
    rr.context_before,
    rr.context_after
FROM ranked_results AS rr
WHERE rr.content IS NOT NULL
  AND rr.similarity >= min_similarity
ORDER BY rr.priority, rr.similarity DESC NULLS LAST
LIMIT match_count;
$function$;


-- 4. Update 'dot_product_search' function
CREATE OR REPLACE FUNCTION public.dot_product_search(
    query_embedding vector(1536),
    match_count integer,
    content_weight double precision DEFAULT 1.0,
    summary_weight double precision DEFAULT 1.0,
    video_filter text DEFAULT NULL::text
)
 RETURNS TABLE(
    content text,
    source text,
    similarity double precision,
    video_id text,
    segment_id integer,
    watch_url text,
    start_time text,
    end_time text,
    summary text,
    full_transcript text,
    context_before text,
    context_after text
)
 LANGUAGE sql
AS $function$
WITH full_transcripts AS (
    SELECT
        ft.video_id,
        ft.full_transcript
    FROM public.video_transcriptions_full AS ft
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
    FROM public.video_transcriptions AS t
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
    FROM public.document_embeddings AS d
    LEFT JOIN full_transcripts ft ON ft.video_id = d.video_id
    WHERE (d.embedding IS NOT NULL OR d.summary_embedding IS NOT NULL)
      AND (video_filter IS NULL OR d.video_id = video_filter)

    UNION ALL

    -- Search in video_transcriptions_full table
    SELECT
        ft_main.full_transcript AS content,
        'video_transcriptions_full' AS source,
        0.5 AS similarity,
        ft_main.video_id,
        NULL::INT AS segment_id,
        NULL::TEXT AS watch_url,
        'FULL' AS start_time,
        'FULL' AS end_time,
        NULL::TEXT AS summary,
        ft_main.full_transcript,
        NULL::TEXT AS context_before,
        NULL::TEXT AS context_after
    FROM full_transcripts AS ft_main
    WHERE (video_filter IS NULL OR ft_main.video_id = video_filter)

    UNION ALL -- New block for webpage_content

    SELECT
        wpc.content AS content,
        'webpage_content' AS source,
        (1 - (wpc.embedding <=> query_embedding)) * content_weight AS similarity,
        wpc.url AS video_id,
        NULL::INT AS segment_id,
        wpc.url AS watch_url,
        NULL::TEXT AS start_time,
        NULL::TEXT AS end_time,
        wpc.title AS summary,
        wpc.content AS full_transcript,
        NULL::TEXT AS context_before,
        NULL::TEXT AS context_after
    FROM public.webpage_content AS wpc
    WHERE wpc.embedding IS NOT NULL
      AND (video_filter IS NULL)
)
SELECT
    rr.content,
    rr.source,
    rr.similarity,
    rr.video_id,
    rr.segment_id,
    rr.watch_url,
    rr.start_time,
    rr.end_time,
    rr.summary,
    rr.full_transcript,
    rr.context_before,
    rr.context_after
FROM ranked_results AS rr
WHERE rr.content IS NOT NULL
  AND rr.video_id IS NOT NULL
ORDER BY rr.similarity DESC NULLS LAST
LIMIT match_count;
$function$;


-- 5. Update 'keyword_search' function
CREATE OR REPLACE FUNCTION public.keyword_search(
    query_text text,
    match_count integer
)
 RETURNS TABLE(
    content text,
    source text,
    similarity double precision,
    metadata jsonb,
    segment_id integer,
    video_id text,
    watch_url text,
    start_time text,
    end_time text
)
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
  FROM public.video_transcriptions AS t
  WHERE t.content ILIKE '%' || query_text || '%'

  UNION ALL

  -- Search in video_transcriptions_full table
  SELECT
    ft.full_transcript AS content,
    'video_transcriptions_full' AS source,
    word_similarity(ft.full_transcript, query_text)::DOUBLE PRECISION AS similarity,
    NULL::JSONB AS metadata,
    NULL::INT AS segment_id,
    ft.video_id,
    NULL::TEXT AS watch_url,
    NULL::TEXT AS start_time,
    NULL::TEXT AS end_time
  FROM public.video_transcriptions_full AS ft
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
  FROM public.document_embeddings AS de
  WHERE de.text ILIKE '%' || query_text || '%'

  UNION ALL -- New block for webpage_content

  SELECT
    wpc.content,
    'webpage_content' AS source,
    word_similarity(wpc.content, query_text)::DOUBLE PRECISION AS similarity,
    NULL::JSONB AS metadata,
    NULL::INT AS segment_id,
    wpc.url AS video_id,
    wpc.url AS watch_url,
    NULL::TEXT AS start_time,
    NULL::TEXT AS end_time
  FROM public.webpage_content AS wpc
  WHERE (wpc.content ILIKE '%' || query_text || '%' OR wpc.title ILIKE '%' || query_text || '%')

  ORDER BY
    similarity DESC
  LIMIT match_count;
END;
$function$;

-- V2: Creates fetch_history table
CREATE TABLE IF NOT EXISTS fetch_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    url TEXT NOT NULL,
    fetch_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    title TEXT,
    fetching_engine TEXT NOT NULL,
    engine_specific_parameters JSONB,
    output_type TEXT,
    error_message TEXT,
    content_storage_path TEXT,
    raw_content_summary TEXT
);

CREATE INDEX IF NOT EXISTS idx_fetch_history_url ON fetch_history(url);
CREATE INDEX IF NOT EXISTS idx_fetch_history_fetch_date ON fetch_history(fetch_date);
CREATE INDEX IF NOT EXISTS idx_fetch_history_user_id ON fetch_history(user_id);
CREATE INDEX IF NOT EXISTS idx_fetch_history_fetching_engine ON fetch_history(fetching_engine);

-- V3: Adds content_summary to fetch_history
ALTER TABLE fetch_history ADD COLUMN content_summary TEXT NULL;

-- V4: Adds raw_content_path to fetch_history
ALTER TABLE fetch_history ADD COLUMN raw_content_path TEXT NULL;

-- V5: Adds supabase_content_id to fetch_history
ALTER TABLE fetch_history ADD COLUMN supabase_content_id UUID NULL;
