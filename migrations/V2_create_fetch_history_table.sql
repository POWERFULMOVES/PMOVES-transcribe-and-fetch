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