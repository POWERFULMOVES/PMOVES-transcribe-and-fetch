# Keyword Search Function

| proname        | pg_get_functiondef                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| keyword_search | CREATE OR REPLACE FUNCTION public.keyword_search(query_text text, match_count integer)
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
$function$
 |