-- migrations/V7_create_crawl_presets_table.sql

-- Create the crawl_presets table
CREATE TABLE crawl_presets (
    preset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preset_name TEXT NOT NULL UNIQUE,
    description TEXT,
    version INTEGER DEFAULT 1,
    crawl_tool TEXT DEFAULT 'crawl4ai',
    strategy_definition JSONB NOT NULL,
    target_capability TEXT,
    tags JSONB,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments to the table and columns
COMMENT ON TABLE crawl_presets IS 'Stores reusable crawl configurations (presets) for agents.';
COMMENT ON COLUMN crawl_presets.preset_id IS 'Unique identifier for the crawl preset.';
COMMENT ON COLUMN crawl_presets.preset_name IS 'Human-readable, unique name for the preset (e.g., "deep_dive_news", "quick_product_scrape").';
COMMENT ON COLUMN crawl_presets.description IS 'Brief explanation of what the preset is designed for.';
COMMENT ON COLUMN crawl_presets.version IS 'Version number for the preset to allow for updates.';
COMMENT ON COLUMN crawl_presets.crawl_tool IS 'Specifies the underlying crawl engine this preset is for (e.g., "crawl4ai").';
COMMENT ON COLUMN crawl_presets.strategy_definition IS 'The core JSON structure defining the crawl strategy and its parameters.';
COMMENT ON COLUMN crawl_presets.target_capability IS 'Tag indicating agent capability this preset serves (e.g., "web_research", "data_extraction").';
COMMENT ON COLUMN crawl_presets.tags IS 'JSONB array of strings for categorization and search (e.g., ["news", "finance"]).';
COMMENT ON COLUMN crawl_presets.created_by IS 'Identifier of the user/agent who created the preset. References auth.users(id).';
COMMENT ON COLUMN crawl_presets.created_at IS 'Timestamp of when the preset was created.';
COMMENT ON COLUMN crawl_presets.updated_at IS 'Timestamp of the last update to the preset.';

-- Enable Row Level Security
ALTER TABLE crawl_presets ENABLE ROW LEVEL SECURITY;

-- Allow public read access to all presets
CREATE POLICY "Allow public read access"
ON crawl_presets
FOR SELECT
USING (true);

-- Allow authenticated users to insert new presets
-- The `created_by` field should be automatically populated to auth.uid() by the application logic or a trigger.
-- If using application logic, ensure it's set. If using a trigger, it would be defined here.
-- For now, this policy assumes `created_by` will be correctly set by the inserting application code.
CREATE POLICY "Allow authenticated users to insert presets"
ON crawl_presets
FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Allow users to update their own presets
CREATE POLICY "Allow users to update their own presets"
ON crawl_presets
FOR UPDATE
USING (auth.uid() = created_by)
WITH CHECK (auth.uid() = created_by);

-- Allow users to delete their own presets
CREATE POLICY "Allow users to delete their own presets"
ON crawl_presets
FOR DELETE
USING (auth.uid() = created_by);

-- Optional: Allow service_role full access (if needed for backend operations)
-- CREATE POLICY "Allow service_role full access"
-- ON crawl_presets
-- FOR ALL
-- USING (auth.role() = 'service_role')
-- WITH CHECK (auth.role() = 'service_role');
