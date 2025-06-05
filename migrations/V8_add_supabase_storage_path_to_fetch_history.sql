-- migrations/V8_add_supabase_storage_path_to_fetch_history.sql

ALTER TABLE public.fetch_history ADD COLUMN supabase_storage_path TEXT NULL;

COMMENT ON COLUMN public.fetch_history.supabase_storage_path IS 'Path to the content file if stored in Supabase Storage (e.g., in a specific bucket).';
