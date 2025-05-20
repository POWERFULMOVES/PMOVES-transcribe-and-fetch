CREATE TABLE public.llm_call_logs (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    url_crawled text,
    request_timestamp timestamp with time zone,
    llm_call_type text,
    strategy_type text,
    llm_provider text,
    model_name text,
    llm_api_token_provided boolean,
    llm_base_url text,
    instruction_prompt text,
    user_intended_extraction_type text,
    extraction_type_setting text,
    schema_definition_provided boolean,
    chunking_applied boolean,
    chunk_token_threshold_setting integer,
    chunk_overlap_rate_setting real,
    input_content_format text,
    llm_extra_args jsonb,
    llm_call_duration_ms integer,
    call_successful boolean,
    prompt_tokens_total integer,
    completion_tokens_total integer,
    total_tokens_used integer,
    cost numeric,
    number_of_chunks_processed integer,
    llm_response_id text,
    error_type text,
    error_message_detail text,
    extracted_content_preview text,
    input_text_preview text,
    crawl_status_code integer,
    crawl_session_id text,
    CONSTRAINT llm_call_logs_pkey PRIMARY KEY (id)
);

ALTER TABLE public.llm_call_logs ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_llm_call_logs_request_timestamp ON public.llm_call_logs USING btree (request_timestamp);
CREATE INDEX idx_llm_call_logs_llm_call_type ON public.llm_call_logs USING btree (llm_call_type);
CREATE INDEX idx_llm_call_logs_model_name ON public.llm_call_logs USING btree (model_name);
CREATE INDEX idx_llm_call_logs_crawl_session_id ON public.llm_call_logs USING btree (crawl_session_id);

CREATE POLICY "Enable read access for all users" ON public.llm_call_logs FOR SELECT USING (true);
