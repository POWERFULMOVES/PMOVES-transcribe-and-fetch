# PMOVES Agent Catalog

## Overview

This document provides a catalog of proposed agent types to power the PMOVES.AI.TEAM architecture. These agents are designed to be modular, extensible, and scalable, leveraging Pipecat for real-time, multimodal communication and integrating with the Agent Registry for dynamic discovery and management. This catalog serves as a guide for developing new agents and as documentation for the PMOVES Orchestrator (Archon) to understand available agent capabilities and how to dynamically assemble helper teams.

Each agent type is described with its core functionality, the capabilities it exposes to the Agent Registry, and suggested existing examples within the codebase (`pmoves-ottomator-agents/` and `docs/pipecat/examples/foundational/`) that can be adapted for implementation.

## Agent Types

---

### 1. Core Text Chat Agent

*   **Description:** A foundational agent capable of basic text-based conversation via an LLM. Primarily handles text input and output.
*   **Core Capabilities (Registry Mapping):**
    *   `chat_completion`
    *   `text_generation`
*   **Suggested Adaptation Source(s):**
    *   `docs/pipecat/examples/foundational/26d-gemini-multimodal-live-text.py` (Minimal text interaction example)

---

### 2. Multimodal Chat Agent

*   **Description:** An extension of the Core Chat Agent that can process and generate responses across multiple modalities, including text, audio (via ASR/TTS integration), and potentially vision (if the underlying LLM and Pipecat components support it).
*   **Core Capabilities (Registry Mapping):**
    *   `chat_completion`
    *   `text_generation`
    *   `audio_input` (requires ASR)
    *   `audio_output` (requires TTS)
    *   `vision_input` (if capable)
*   **Suggested Adaptation Source(s):**
    *   `docs/pipecat/examples/foundational/26-gemini-multimodal-live.py` (General multimodal example)
    *   `docs/pipecat/examples/word-wrangler-gemini-live/server/bot.py` (Includes ASR/VAD and TTS concepts)

---

### 3. Tool-Calling/Function Agent

*   **Description:** An agent capable of interacting with external tools or executing predefined functions based on LLM output (e.g., using LiteLLM's tool calling feature). Can perform actions like looking up information, interacting with APIs, etc.
*   **Core Capabilities (Registry Mapping):**
    *   `chat_completion`
    *   `text_generation`
    *   `tool_calling`
    *   Specific capabilities based on the tools integrated (e.g., `google_search`, `code_execution`)
*   **Suggested Adaptation Source(s):**
    *   `docs/pipecat/examples/foundational/26b-gemini-multimodal-live-function-calling.py` (Demonstrates function calling)
    *   `pmoves-ottomator-agents/smart-select-multi-tool-agent/` (Example of an agent using multiple tools)

---

### 4. Web Fetcher Agent

*   **Description:** Specializes in fetching content from the web, including advanced crawling, deep navigation, and structured data extraction. Integrates with **crawl4ai (v0.7.x+)** to provide intelligent, adaptive web interaction.
*   **Core Capabilities (Registry Mapping):**
    *   `fetch_web_content`
    *   `crawl_web` (Adaptive, Deep BFS/DFS)
    *   `extract_data`
    *   `extract_data_structured` (JsonCss, Regex, Table)
    *   `extract_data_semantic` (LLM, Cosine Similarity)
    *   `execute_crawl_script` (C4A DSL for multi-step interactions)
*   **Advanced Configuration:**
    *   **Extraction Strategies:** JsonCss (schema-based), LLM (generative), Cosine (semantic clustering), Table (LLM/Heuristic), Regex.
    *   **Agentic Behaviors:** Adaptive Crawling (Coverage/Consistency/Saturation scores), BestFirstCrawling (semantic prioritization).
    *   **Browser Management:** Persistent Contexts, Managed Browsers, CDP Integration.
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/crawl4AI-agent-v2/` (Designed for crawling and extraction)
    *   `pmoves-ottomator-agents/advanced-web-researcher/` (Likely includes web fetching logic)
    *   `backend/app/crawl4ai_docker_fetcher.py` and `backend/app/crawl4ai_fetcher.py` (Backend fetching implementation to draw from)

---

### 5. Search Agent

*   **Description:** Focuses on searching information within connected data sources (e.g., Supabase vector database, indexed documents). Can perform keyword, vector, or hybrid searches.
*   **Core Capabilities (Registry Mapping):**
    *   `search` (general search)
    *   `search_vector` (vector search)
    *   `search_keyword` (keyword search)
    *   `search_hybrid` (hybrid search)
    *   `query_database` (database interaction)
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/mem0-agent/` (Uses Supabase for vector storage and search)
    *   `backend/app/psearchworking.py` (Core backend search logic to integrate)

---

### 6. Summarizer Agent

*   **Description:** Takes large volumes of text content (e.g., fetched documents, transcripts) and generates concise summaries.
*   **Core Capabilities (Registry Mapping):**
    *   `summarize_text`
    *   `analyze_text`
*   **Suggested Adaptation Source(s):**
    *   This capability is often integrated into other agents (like RAG agents) or can be a standalone LLM task. No direct existing standalone example identified, but LLM interaction in any Pipecat example can be adapted.
    *   Refer to LLM service usage in Pipecat examples for text processing patterns.

---

### 7. Content Management/Upsert Agent

*   **Description:** Handles the ingestion and management of content into the platform's knowledge base (e.g., uploading documents, processing fetched content for vector storage).
*   **Core Capabilities (Registry Mapping):**
    *   `upsert_content`
    *   `manage_content`
    *   `process_document`
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/crawl4AI-agent-v2/` (Includes processing/chunking logic relevant to ingestion)
    *   `backend/app/pmoves_upserter.py` (Core backend upsert logic to integrate)

---

### 8. Transcriber Agent

*   **Description:** Processes audio or video content to generate transcripts.
*   **Core Capabilities (Registry Mapping):**
    *   `transcribe_audio`
    *   `transcribe_video`
*   **Suggested Adaptation Source(s):**
    *   Pipecat examples using ASR services (e.g., `docs/pipecat/examples/foundational/26a-gemini-multimodal-live-transcription.py`)

---

### 9. Supabase Agent

*   **Description:** A specialized agent for managing and interacting with the Supabase database. It handles database infrastructure tasks like table creation (potentially via RPCs or migrations), performs data operations (querying, upserting), and can manage user/chat data. Designed to be a scalable, multimodal interface to the database, accessible via CLI, realtime chat (Pipecat, Supabase Realtime), etc.
*   **Core Capabilities (Registry Mapping):**
    *   `manage_database`
    *   `create_table`
    *   `query_data`
    *   `upsert_data`
    *   `manage_schema`
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/pmoves-supabase-agent/` (Core agent implementation)
    *   `migrations/` (Reference for existing database schema and migration patterns)
    *   `backend/app/pmoves_upserter.py` (Relevant upsert/data handling logic)

---

### 10. RLS Agent (Supabase Helper)

*   **Description:** A specialized helper agent for the Supabase Agent focused on generating and applying Supabase Row Level Security (RLS) policies. It interprets policy requirements and translates them into correct SQL `CREATE POLICY` or `ALTER POLICY` statements.
*   **Core Capabilities (Registry Mapping):**
    *   `manage_rls_policies`
    *   `create_rls_policy`
    *   `update_rls_policy`
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/pmoves-supabase-agent/create-rls-policies.md` (Guidelines for RLS policies)

---

### 11. Migration Agent (Supabase Helper)

*   **Description:** A specialized helper agent for the Supabase Agent responsible for generating Supabase database migration files. It takes schema change descriptions and creates timestamped SQL files in the `supabase/migrations/` directory according to naming and style guidelines.
*   **Core Capabilities (Registry Mapping):
    *   `generate_migration`
    *   `apply_migration` (potentially, or orchestrate via Supabase CLI)
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/pmoves-supabase-agent/create-migration.md` (Guidelines for migrations)

---

### 12. Function Creation Agent (Supabase Helper)

*   **Description:** A specialized helper agent for the Supabase Agent focused on generating SQL code for Supabase database functions (RPCs) and potentially applying them. It ensures generated functions follow best practices (e.g., `SECURITY INVOKER`, `search_path`).
*   **Core Capabilities (Registry Mapping):**
    *   `generate_db_function`
    *   `create_db_function`
*   **Suggested Adaptation Source(s):**
    *   `pmoves-ottomator-agents/pmoves-supabase-agent/create-db-functions.md` (Guidelines for database functions)

---

## Integration with Orchestrator and Registry

Each implemented agent based on these types should:

1.  Register itself with the Agent Registry on startup using its unique `agent_id` and providing its metadata (name, description, capabilities, endpoint, etc.), as defined in `docs/masterplan/PMOVES_AGENT_REGISTRY_SCHEMA.md`.
2.  Periodically send heartbeats to the registry to indicate it is active.
3.  Use Pipecat for communication, defining a pipeline that includes transports for input/output (e.g., WebSocket, Daily) and processors for its core logic (LLM service, tool processors, etc.).
4.  Implement handlers for incoming frames/messages relevant to its capabilities.

The PMOVES Orchestrator (Archon) will query the Agent Registry (`GET /agents`) to discover available agents and their capabilities. Based on user requests or workflow requirements, it will select appropriate agents, potentially spawn new instances (if containerized), and orchestrate communication between them via their registered endpoints and the Pipecat communication layer.

---

*This catalog is a living document and will be updated as new agent types are identified and existing agents are refined.* 