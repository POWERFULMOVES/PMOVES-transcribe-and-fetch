# Crawl Presets Plan for PMOVES Agent Platform

## 1. Introduction & Purpose

This document outlines the plan for defining, managing, and utilizing crawl presets within the PMOVES agent platform. The goal is to establish a standardized system for configuring web crawling tasks executed by various agents.

**Benefits:**
-   **Consistency:** Ensures crawls are performed with standardized configurations.
-   **Reusability:** Allows common crawl configurations to be saved and reused across different agents and tasks.
-   **Simplified Agent Configuration:** Abstracts the complexity of detailed crawl settings (e.g., `crawl4ai` parameters) away from individual agent logic or user commands.
-   **User-Friendliness:** Enables users to invoke complex crawl behaviors using simple preset names.

**Alignment:**
This plan integrates with the overall PMOVES agent platform by:
-   Leveraging **Supabase for storage**, similar to the Agent Registry (`masterplan/PMOVES_AGENT_PLATFORM_PLAN.md`).
-   Defining how presets are communicated and used by agents within the **Pipecat architecture** (`PIPECAT_ARCHITECTURE.md`).
-   Providing a mechanism for the **Orchestrator** to assign and manage crawl configurations for agents involved in complex workflows.

## 2. Preset Definition & Schema

Crawl presets will be defined using a JSON structure, closely following the configuration requirements of the underlying crawling tool (e.g., `crawl4ai`).

### 2.1. Core Preset Structure (JSON)

The primary structure for a crawl preset will include:
-   `strategy`: The class name of the crawl strategy (e.g., `"BFSDeepCrawlStrategy"`).
-   `params`: A dictionary of parameters for the chosen strategy, including potential nested configurations for `filter_chain` and `url_scorer`.

*(Refer to `docs/crawl4ai/crawl4ai_custom_context.md` for detailed JSON examples of `crawl4ai` strategy, filter_chain, and url_scorer configurations.)*

The `strategy_definition` should be comprehensive enough to include configurations for extraction strategies (like `LLMExtractionStrategy` including its `LLMConfig`), deep crawling strategies (like `BestFirstCrawlingStrategy` with its `url_scorer` and `filter_chain`), and general `BrowserConfig` / `CrawlerRunConfig` parameters, as detailed in the `fetch_page_enhancement_plan.md` (v1.3) and the examples in Section 6.

### 2.2. Preset Metadata

In addition to the core crawl configuration, each preset will have associated metadata for management and discovery:

-   `preset_id` (UUID, Primary Key): Unique identifier for the preset.
-   `preset_name` (TEXT, UNIQUE): A human-readable, unique name for the preset (e.g., "deep_dive_news_articles", "quick_product_scrape").
-   `description` (TEXT): A brief explanation of what the preset is designed for and its expected outcome.
-   `version` (INTEGER, Default: 1): Version number for the preset to allow for updates and revisions.
-   `crawl_tool` (TEXT, Default: "crawl4ai"): Specifies the underlying crawl engine this preset is for.
-   `strategy_definition` (JSONB): The core JSON structure as described in 2.1 (containing `strategy` and `params`).
-   `target_capability` (TEXT, Optional): A tag indicating what kind of agent capability this preset serves (e.g., "web_research", "data_extraction", "site_monitoring"). This helps in matching presets to suitable agents.
-   `tags` (JSONB, Optional): An array of strings for categorization and search (e.g., `["news", "finance", "deep_crawl"]`).
-   `created_by` (UUID, Optional, Foreign Key to Users table): Identifier of the user/agent who created the preset.
-   `created_at` (TIMESTAMPTZ, Default: NOW()): Timestamp of creation.
-   `updated_at` (TIMESTAMPTZ, Default: NOW()): Timestamp of the last update.

## 3. Storage & Management

### 3.1. Storage Solution

-   **Database:** Supabase (PostgreSQL).
-   **Table Name:** `crawl_presets`.
-   **Schema:** Based on the metadata fields defined in section 2.2.

```sql
-- Example SQL for crawl_presets table
CREATE TABLE crawl_presets (
    preset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preset_name TEXT NOT NULL UNIQUE,
    description TEXT,
    version INTEGER DEFAULT 1,
    crawl_tool TEXT DEFAULT 'crawl4ai',
    strategy_definition JSONB NOT NULL,
    target_capability TEXT,
    tags JSONB,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Example, adjust if user table is different
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies would be applied as per project standards
```

### 3.2. Management API

A set of RESTful API endpoints will be provided for managing crawl presets. These could be part of the main PMOVES backend application.

-   **`POST /api/presets`**: Create a new crawl preset.
    -   Request Body: JSON object containing `preset_name`, `description`, `strategy_definition`, and other optional metadata.
    -   Response: The created preset object with its `preset_id`.
-   **`GET /api/presets`**: List all crawl presets (with pagination and filtering capabilities, e.g., by `tags` or `target_capability`).
    -   Response: Array of preset objects.
-   **`GET /api/presets/{preset_id_or_name}`**: Retrieve a specific crawl preset by its ID or unique name.
    -   Response: Single preset object.
-   **`PUT /api/presets/{preset_id_or_name}`**: Update an existing crawl preset.
    -   Request Body: JSON object with fields to update. May increment `version`.
    -   Response: The updated preset object.
-   **`DELETE /api/presets/{preset_id_or_name}`**: Delete a crawl preset.
    -   Response: Success/failure status.

**Authentication & Authorization:** Access to these endpoints will be secured, aligning with the platform's overall security model (e.g., API keys for agents, JWT for users/UI). Specific roles might be defined for managing presets.

### 3.3. Management UI (Future Consideration)

A user interface, potentially integrated within the existing Supabase-based UI, could be developed to allow users to:
-   View, create, edit, and delete crawl presets.
-   Test presets (trigger a sample crawl).
-   Manage preset versions and tags.

## 4. Preset Utilization by Agents

Agents within the PMOVES platform will utilize these presets to configure and execute crawl tasks.

### 4.1. Discovery & Selection

-   **User Command:** Users can instruct an agent to use a specific preset via a chat command.
    -   Example: `@ResearchAgent crawl <url> using preset 'tech_news_summary'`
-   **Agent Logic:** Agents can be programmed to select appropriate presets based on the task type, context, or their designated `target_capability`.
-   **Orchestrator Assignment:** The Orchestrator, as defined in `masterplan/PMOVES_AGENT_PLATFORM_PLAN.md`, can assign a preset to an agent as part of a defined workflow.
-   **API Query:** Agents can query the `/api/presets` endpoint to find suitable presets based on tags or capabilities.

### 4.2. Passing Presets to Agents

-   **Preset Identifier:** The most common method will be passing the `preset_name` or `preset_id`. The agent is then responsible for fetching the full preset definition from the Management API.
-   **Full Preset JSON:** In some scenarios, the full JSON `strategy_definition` might be passed directly to the agent, especially if the preset is dynamically generated or not yet persisted.

This communication would occur via the Pipecat infrastructure, likely within an `AgentCommand` structure embedded in a Pipecat `TextFrame` or a dedicated custom frame if necessary, aligning with `PIPECAT_ARCHITECTURE.MD` and `AGENT_COMMAND_PROTOCOL.md`.

Example `AgentCommand` snippet:
```json
{
  "command_type": "execute_crawl",
  "task_id": "task_123",
  "args": {
    "url": "https://example.com/new-article",
    "preset_identifier": "tech_news_summary", // or "preset_id": "uuid-..."
    // or "preset_definition": { ... full JSON ... }
    "output_format": "markdown_summary"
  }
}
```

### 4.3. Agent Implementation

Agents designed to perform web crawls (e.g., a `ResearchAgent`, `DataExtractionAgent`, or a generic `CrawlAgent`) will need the following logic:

1.  **Receive Crawl Task:** Via Pipecat message containing the target URL and preset information.
2.  **Fetch Preset Definition:** If a `preset_identifier` is provided, call the `/api/presets/{identifier}` endpoint to get the `strategy_definition` JSON.
3.  **Configure Crawler:**
    *   Parse the `strategy_definition` JSON.
    *   Translate this JSON into the specific configuration object required by the underlying crawl tool (e.g., `crawl4ai`'s `CrawlerRunConfig` and strategy objects). This step mirrors the logic intended for `crawl4ai_docker_fetcher.py`.
    *   This might involve dynamically importing strategy, filter, and scorer classes based on string names in the JSON.
4.  **Execute Crawl:**
    *   Invoke the crawl tool (e.g., make a request to the `Crawl4AI Docker service` if it's a separate microservice, or use a local `crawl4ai` library).
5.  **Process & Return Results:** Handle the crawl output and return it as per the agent's task (e.g., send a summary back to the chat via Pipecat).

## 5. Integration with PMOVES Platform Components

### 5.1. Agent Registry

-   **Capability Indication:** Agents registered in the Agent Registry (`masterplan/PMOVES_AGENT_PLATFORM_PLAN.md`) can list "crawl_preset_execution" or similar as a capability in their metadata.
-   **Default Presets:** An agent's registration metadata could optionally include a list of default or recommended `preset_names` it's optimized for.

### 5.2. Orchestrator

-   **Workflow Definition:** The Orchestrator can use `preset_names` when defining multi-step workflows that involve web crawling. This allows for dynamic and configurable crawl tasks within broader agent processes.
-   **Dynamic Selection:** The Orchestrator could potentially select or even dynamically assemble/modify presets based on the overall workflow state or external triggers.

### 5.3. Communication Layer (Pipecat)

-   Preset identifiers and, if needed, full preset JSON blobs will be part of the standardized agent communication, likely embedded within the `args` of an `AgentCommand` as described in `AGENT_COMMAND_PROTOCOL.md` and transmitted via Pipecat frames (`PIPECAT_ARCHITECTURE.md`).

## 6. Example JSON Preset (for `crawl_presets` table, `strategy_definition` field)

### Example 1: BFS Crawl with Basic Filters

```json
{
  "strategy": "BFSDeepCrawlStrategy",
  "params": {
    "max_depth": 2,
    "include_external": false,
    "max_pages": 50,
    "filter_chain": {
      "filters": [
        {
          "type": "URLPatternFilter",
          "params": {
            "patterns": ["*docs*", "*help*"],
            "case_sensitive": false
          }
        },
        {
          "type": "ContentTypeFilter",
          "params": {
            "allowed_types": ["text/html"]
          }
        }
      ]
    }
  }
}
```
This would be stored in the `strategy_definition` JSONB column for a preset named, for example, `"documentation_site_bfs_crawl"`.

### Example 2: Deep Crawl with `BestFirstCrawlingStrategy`, Keyword Scorer, and URL Pattern Filter

```json
{
  "strategy": "BestFirstCrawlingStrategy",
  "params": {
    "max_depth": 3,
    "max_pages": 100,
    "include_external": true,
    "url_scorer": {
      "type": "KeywordRelevanceScorer",
      "params": {
        "keywords": ["ai", "llm", "development"],
        "weight": 0.75
      }
    },
    "filter_chain": {
      "filters": [
        {
          "type": "URLPatternFilter",
          "params": {
            "patterns": ["*/blog/*", "*/news/*"],
            "case_sensitive": false
          }
        },
        {
          "type": "DomainFilter",
          "params": {
            "allowed_domains": ["example.com", "another.example.org"]
          }
        }
      ]
    }
  }
}
```

### Example 3: Extraction with `LLMExtractionStrategy` and `LLMConfig`

```json
{
  "strategy": "SinglePageFetchStrategy",
  "params": {
    "extraction_strategy": {
      "type": "LLMExtractionStrategy",
      "params": {
        "schema_json": {
          "title": "string",
          "summary": "string",
          "key_topics": ["list", "string"]
        },
        "instruction": "Extract the title, a concise summary, and key topics from the article."
      }
    },
    "llm_config": {
      "provider": "ollama",
      "model": "mistral:latest",
      "base_url": "http://localhost:11434/api",
      "api_token": null
    },
    "browser_config": {
      "user_agent": "MyExtractionBot/1.0",
      "text_mode": true
    },
    "run_config": {
      "page_timeout": 60000,
      "only_text": true
    }
  }
}
```

These examples illustrate how various `crawl4ai` features can be defined within a preset. The `backend/app/crawl4ai_fetcher.py` will be responsible for parsing this `strategy_definition` and configuring the `crawl4ai` library accordingly.

## 7. Future Considerations

-   **Preset Versioning:** More sophisticated version control for presets, allowing rollback or specific version requests.
-   **UI for Preset Sharing/Discovery:** A gallery or community section for sharing and discovering useful presets.
-   **LLM-Assisted Preset Generation:** An agent or UI feature that helps users generate or suggest crawl presets based on natural language descriptions of their goals.
-   **Parameter Validation:** Robust validation of the `strategy_definition` JSON against known schemas for `crawl4ai` or other crawl tools.
-   **Analytics on Preset Usage:** Tracking which presets are used most often, success rates, etc. 