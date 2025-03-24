# Dot Product Search Function

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
$function$