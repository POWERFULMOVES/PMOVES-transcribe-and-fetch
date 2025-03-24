-- Functions for checking duplicate content before insertion
-- This prevents the same content from being uploaded multiple times

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

-- Update function to upsert webpage content (insert or update if exists)
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