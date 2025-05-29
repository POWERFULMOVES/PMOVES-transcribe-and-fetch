-- Table for storing LLM Models
CREATE TABLE IF NOT EXISTS llm_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id TEXT UNIQUE NOT NULL, -- e.g., "openai/gpt-3.5-turbo", "ollama/llama2"
    display_name TEXT NOT NULL, -- User-friendly name, e.g., "GPT-3.5 Turbo (OpenAI)"
    provider TEXT NOT NULL, -- e.g., "openai", "ollama", "anthropic", "google"
    family TEXT, -- e.g., "GPT-3.5", "Llama", "Claude 3"
    context_window INTEGER,
    capabilities JSONB DEFAULT '[]'::jsonb, -- Store as array of objects: [{"type": "chat", "details": {}}, {"type": "vision", ...}]
    status TEXT DEFAULT 'active', -- e.g., 'active', 'deprecated', 'beta'
    pricing JSONB, -- Optional: e.g., {"input_cost_per_mtok": 0.50, "output_cost_per_mtok": 1.50, "currency": "USD"}
    rate_limits JSONB, -- Optional: e.g., {"requests_per_minute": 100, "tokens_per_minute": 60000}
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_llm_models_model_id ON llm_models(model_id);
CREATE INDEX IF NOT EXISTS idx_llm_models_provider ON llm_models(provider);
CREATE INDEX IF NOT EXISTS idx_llm_models_family ON llm_models(family);

-- Table for storing Application Configurations
CREATE TABLE IF NOT EXISTS app_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key TEXT UNIQUE NOT NULL, -- e.g., "DEFAULT_SEARCH_PARAMS", "MAX_FETCH_RETRIES"
    config_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_app_configurations_config_key ON app_configurations(config_key);

-- Table for storing Agent Registry
CREATE TABLE IF NOT EXISTS agent_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT UNIQUE NOT NULL, -- A unique identifier for the agent
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL, -- e.g., "data_fetcher", "analyzer", "transcriber"
    endpoints JSONB, -- e.g., {"process": "/api/v1/agents/myagent/process", "status": "/api/v1/agents/myagent/status"}
    capabilities JSONB DEFAULT '[]'::jsonb, -- Similar to llm_models.capabilities
    required_config_keys TEXT[], -- Array of keys from app_configurations needed by this agent
    status TEXT DEFAULT 'disabled', -- e.g., 'active', 'disabled', 'beta', 'maintenance'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_registry_agent_id ON agent_registry(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_registry_type ON agent_registry(type);
CREATE INDEX IF NOT EXISTS idx_agent_registry_status ON agent_registry(status);

-- Triggers for updated_at timestamps
-- Ensure the function exists or create it if not (idempotently)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        CREATE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $func$ language 'plpgsql';
    END IF;
END
$$;

CREATE TRIGGER update_llm_models_updated_at
BEFORE UPDATE ON llm_models
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_app_configurations_updated_at
BEFORE UPDATE ON app_configurations
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_agent_registry_updated_at
BEFORE UPDATE ON agent_registry
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
