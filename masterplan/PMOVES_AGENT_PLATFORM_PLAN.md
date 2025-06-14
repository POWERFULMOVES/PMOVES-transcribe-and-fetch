# PMOVES Agent Platform: Registry, Orchestrator, and Communication Planning

## Overview
This document serves as the planning and coordination hub for the next-generation PMOVES agent platform. It tracks all design, research, and implementation tasks related to:
- Agent Registry (inspired by the LLM registry in LiteLLM)
- Orchestrator (Achon-inspired, dynamic agent creation and workflow management)
- Agent Communication Layer (Pipecat, Supabase Realtime, etc.)
- Documentation and blueprinting
- Task tracking and cross-referencing with relevant repositories and documentation

---

## Key References
- [LiteLLM Registry & agent_llm_plan.md](./agent_llm_plan.md)
- [Achon repo (for orchestrator patterns)](https://github.com/achon/achon) *(replace with actual URL if private/local)*
- [Pipecat repo (for communication layer)](https://github.com/pipecat-ai/pipecat) *(replace with actual URL if private/local)*
- [Supabase Realtime Docs](https://supabase.com/docs/guides/realtime)
- [PMOVES.AI.TEAM Architecture](./PMOVES_AI_TEAM.md)

---

## Agent Registry (inspired by the LLM registry in LiteLLM)

This section details the design and implementation plan for the Agent Registry, a central service for dynamic discovery, registration, and management of all agents.

### Agent Metadata Schema
- **Agent ID:** Unique identifier for each agent.
- **Name:** Human-readable name of the agent.
- **Description:** Brief description of the agent's capabilities and purpose.
- **Capabilities:** JSONB field to store agent capabilities (e.g., text, vision, function calling).
- **Status:** Current operational status of the agent.
- **Endpoint:** URL or connection string for the agent's communication interface.
- **Dependencies:** JSONB field to store any external dependencies or resources the agent needs.
- **Version:** Version number of the agent's software.
- **Tags:** JSONB field to store any additional metadata or tags for the agent.
- **Last Heartbeat:** Timestamp of the last heartbeat signal received from the agent.
- **Config:** JSONB field to store any configuration settings for the agent.

### Registry Service Responsibilities
- **Registration:** Allow agents to register themselves with the registry.
- **Heartbeat:** Receive and process heartbeat signals from agents to verify their health and availability.
- **Retrieval:** Provide metadata about available agents to the orchestrator and UI.
- **Deletion:** Remove agents from the registry when they are no longer available or need to be decommissioned.

### API Endpoint Design
- **POST /agents:** Endpoint for agents to register themselves with the registry.
- **GET /agents:** Endpoint for retrieving metadata about available agents.
- **PUT /agents/{agent_id}/heartbeat:** Endpoint for agents to send heartbeat signals.
- **DELETE /agents/{agent_id}:** Endpoint for removing an agent from the registry.

### Implementation Notes
- **Asynchronous Database Calls:** The registry service will use asynchronous database calls to interact with the PostgreSQL database.
- **Data Integrity:** Constraints and indices will be added to ensure data integrity and efficient querying.
- **Scaling Strategies:** The FastAPI application serving the registry API can be scaled horizontally by running multiple instances behind a load balancer.
- **High Availability and Reliability:** Leverage Supabase's built-in backup and point-in-time recovery features.
- **Migration:** Plan for a migration process to move any data from the prototype storage (if applicable) into the new PostgreSQL database.

### Persistent Storage and Scaling Plan for Agent Registry

To move beyond the initial in-memory or file-based prototype, the Agent Registry requires a robust persistent storage solution and a plan for scaling to handle a growing number of agents and requests.

*   **Database Choice:** Given the project's existing reliance on Supabase and the advantages of PostgreSQL for structured data and potential future-proofing (e.g., PostGIS for location data, `pg_vector` for embedding-related agent metadata), **Supabase (PostgreSQL)** is the recommended choice for the Agent Registry's persistent storage.

*   **Schema Implementation:** The Agent Metadata Schema defined in `docs/masterplan/PMOVES_AGENT_REGISTRY_SCHEMA.md` will be translated into a corresponding PostgreSQL table structure. This will involve creating a table with columns for each metadata field (agent_id, name, description, capabilities (using JSONB), status, endpoint, dependencies (JSONB), version, tags (JSONB), last_heartbeat, config (JSONB)). Constraints and indices will be added to ensure data integrity and efficient querying.

*   **Database Interaction:** The current in-memory/file-based data handling in the registry service will be replaced with asynchronous database calls using a suitable PostgreSQL driver (e.g., `asyncpg` or integrating with a higher-level ORM like SQLAlchemy if already in use elsewhere in the backend). Endpoints for registration, heartbeat, retrieval, and deletion will interact directly with the database.

*   **Scaling Strategies:**
    *   **Registry Service:** The FastAPI application serving the registry API can be scaled horizontally by running multiple instances behind a load balancer. This is a standard approach for handling increased request volume.
    *   **Database:** Supabase provides options for scaling the PostgreSQL database instance as data volume and query load increase. This might involve upgrading the database tier or exploring read replicas for read-heavy workloads.

*   **High Availability and Reliability:**
    *   Leverage Supabase's built-in backup and point-in-time recovery features.
    *   Consider database replication for failover if high availability is critical.
    *   Implement health checks for the registry service instances to allow load balancers to route traffic away from unhealthy instances.

*   **Migration:** Plan for a migration process to move any data from the prototype storage (if applicable) into the new PostgreSQL database.

---

## Supabase UI, Realtime Chat, and Agent Avatars: Integration Plan

This section documents the integration of Supabase UI features, agent avatars, realtime chat, and their orchestration with the PMOVES agent platform. It synthesizes current capabilities and outlines how these components will work together:

### Supabase UI Features
- **Infinite Query:** Already used for efficient paginated data fetching (e.g., video transcriptions, embeddings).
- **Realtime Chat:** Supabase Realtime enables live chat channels. Each agent or user can be a participant.
- **Avatars:** Agents and users can have avatars (image URLs or generated), displayed in chat UIs and agent directories.
- **Auth & Presence:** Supabase UI provides authentication components and user context, supporting presence and avatar assignment.

### Agent-as-Avatar in Realtime Chat
- Orchestrator can spin up agents as chat participants, each with a unique persona and avatar.
- Agents register with the registry and are assigned to chat rooms, subscribing to Supabase Realtime channels.
- Agents can communicate via text, voice, or images (using Pipecat for multimodal responses), appearing as avatars in the chat UI.

### Pipecat Multimodal Communication
- Pipecat powers real-time voice, text, and image communication for agents.
- Agents can listen/respond to chat messages in real time, using Supabase Realtime channels.
- Multimodal responses are rendered in the chat UI using Supabase UI components.

### UI/UX Implementation Notes
- Supabase UI (React) provides ready-to-use components for chat, avatars, buttons, icons, and typography.
- Storybook can be used to explore and prototype UI components.
- Tailwind CSS is used for styling and layout.

### Next Steps (for this integration)
1. Prototype or enhance chat UI with avatars and agent presence using Supabase UI components.
2. Integrate orchestrator logic for dynamic agent spawning and registration in chat rooms.
3. Connect Pipecat for multimodal agent communication in chat.
4. Use Context7 and other MCP tools to further enhance UI and agent features as needed.

---

## Supabase Agent: Search & Upsert Integration Plan (Refined)

The Supabase Agent will combine advanced search, upsert, table management, and backend function orchestration. In addition to previously discussed upsert and management features, the agent will leverage `psearchworking.py` for comprehensive, parameterized, and interactive search.

### Integration with `psearchworking.py`
- **Comprehensive Search:**
  - Supports dot product (vector), keyword, and hybrid search across all major Supabase tables (video transcriptions, document embeddings, full transcripts, web/text/media content).
  - Can stream results into chat, supporting infinite query and live updates.
- **Parameter Management:**
  - Users can adjust search parameters (similarity thresholds, content/summary weights, result percentages, max results) via chat commands.
  - Presets and live parameter updates are supported.
- **Result Analysis:**
  - The agent can trigger LLM-based analysis of search results and return summaries or insights in chat.
- **Result Formatting:**
  - Results are formatted for chat display, including content snippet, source/type, similarity score, timestamps/URLs, and links to full content.

### Sample Command Mapping Table

| Command/Intent                        | Example User Message                                      | Agent Action/Response                                 |
|----------------------------------------|-----------------------------------------------------------|-------------------------------------------------------|
| Search                                | `@SupabaseAgent search for "climate change"`             | Runs `search_all`, streams results in chat            |
| Adjust search parameter                | `@SupabaseAgent set fine-grained similarity threshold to 0.9` | Updates parameter, confirms in chat                  |
| Use preset                            | `@SupabaseAgent use preset broad`                         | Loads preset, confirms in chat                        |
| Show more results                     | `@SupabaseAgent show more results`                        | Streams next batch of results                         |
| Analyze results                       | `@SupabaseAgent analyze results`                          | Runs LLM analysis, returns summary                    |
| Upsert from shared folder              | `@SupabaseAgent upsert new files`                         | Processes and upserts new content, reports status     |
| Table management                      | `@SupabaseAgent create table my_table ...`                | Creates/updates table, confirms in chat               |
| Run backend function                  | `@SupabaseAgent run deduplication on video_transcriptions`| Triggers function, reports status/result              |
| Help                                  | `@SupabaseAgent help`                                     | Lists available commands                              |

These search and parameter management abilities are in addition to upsert, table management, and backend function orchestration previously discussed. The agent will provide a unified, chat-driven interface for all these capabilities.

#### Source Reference Mapping

The following table maps each major Supabase Agent capability to its primary implementation file(s) or module(s) in the codebase:

- **Comprehensive Search (vector, keyword, hybrid, streaming, analysis):**
  - `backend/app/psearchworking.py` (core search logic, parameter management, result formatting, LLM analysis)
- **Upsert from Shared Folder / Content Management:**
  - `backend/app/pmoves_upserter.py` (markdown, HTML, media, video/audio upsert, duplicate checking, Supabase RPC calls)
  - `backend/app/routes/content_upserter.py` (API routes for upsert/content management)
- **Table Management & Backend Function Orchestration:**
  - `backend/app/pmoves_upserter.py` (table creation/alteration, orchestration helpers)
  - `backend/app/main.py` (API endpoints for table management, backend orchestration)
- **Parameter Management (search tuning, presets):**
  - `backend/app/psearchworking.py` (SearchParameters class, preset loading, live updates)
  - `backend/app/config/search_config.py` (parameter presets, validation)
- **Result Streaming & Infinite Query:**
  - `backend/app/psearchworking.py` (search result streaming, batch/pagination logic)
  - Chat UI (infinite query display, not shown here)
- **LLM-based Result Analysis:**
  - `backend/app/psearchworking.py` (analysis functions, OpenAI/Groq integration, registry fallback)

These references ensure that each agent feature is directly traceable to its implementation, supporting maintainability and onboarding.

---

## Pipecat: Architecture, Data Model, and Integration Plan

Pipecat is the core multimodal communication layer for the PMOVES agent platform. This section summarizes its architecture, data model, and how it integrates with the orchestrator, registry, and chat UI.

### Architecture Overview
- **Frames:** Core data structure representing discrete chunks of data (text, audio, image) or control signals (start, stop, error, etc.). Specialized frames for audio, images, text, LLM messages, system/control, metrics, and function calls.
- **FrameProcessors:** Components that operate on frames, transforming or routing them (e.g., LLM completion, TTS, aggregation).
- **Pipelines:** Chains of frame processors, forming the agent's processing logic (e.g., LLM → TTS → Transport).
- **Transports:** Interfaces for input/output, such as WebRTC (Daily), WebSocket, or custom endpoints.

### Example Agent Flow (Frame Lifecycle)
1. User input (e.g., speech) is transcribed and placed in the pipeline as a TranscriptionFrame.
2. Frame processors aggregate, update context, and generate LLM messages.
3. LLM responses are streamed as TextFrames, then converted to audio by TTS processors.
4. Audio frames are sent to the output transport for playback or transmission.
5. Control and system frames manage flow, errors, and task boundaries.

### Example Projects (from pmoves-pipecat/examples)
- **Simple Chatbot:** Basic voice-driven conversational bot (Deepgram, ElevenLabs, OpenAI, Daily).
- **Storytelling Chatbot:** Multimodal, collaborative storytime agent (adds vision, custom UI).
- **Translation Chatbot:** Real-time speech translation and response.
- **Moondream Chatbot:** Adds vision capabilities to GPT-4 (requires GPU).
- **WebSocket Chatbot Server:** Real-time audio streaming and bot interaction via WebSocket.
- **Patient Intake, Phone/Twilio Chatbot, StudyPal, etc.:** Specialized agents for function calling, phone integration, and document conversation.

### Integration with PMOVES Platform
- **Orchestrator:**
  - Spawns and manages Pipecat-based agents as needed (e.g., for chat rooms or tasks).
  - Assigns each agent a unique persona and avatar, and registers it in the agent registry.
  - Connects agents to Supabase Realtime chat channels as participants.
- **Agent Registry:**
  - Stores metadata for each Pipecat agent (capabilities, endpoint, status, etc.).
  - Enables orchestrator and UI to discover and interact with available agents.
- **Chat UI:**
  - Renders agent avatars and messages in real time using Supabase UI components.
  - Receives multimodal responses (text, voice, images) from Pipecat agents via Supabase Realtime.
  - Supports user-to-agent and agent-to-agent communication.
- **Multimodal Communication:**
  - Pipecat agents process and respond to chat messages using pipelines (LLM, TTS, STT, vision, etc.).
  - Responses are sent as frames, which are rendered in the chat UI (text, audio, image, etc.).

#### Detailed Integration Points & Architecture Diagram

**Integration Points:**

- **Orchestrator → Pipecat Agent:**
  - Orchestrator dynamically spawns Pipecat agent instances for each chat room or task.
  - Passes configuration (persona, avatar, capabilities) and registers the agent in the registry.
  - Assigns the agent to a Supabase Realtime channel (chat room).

- **Registry ↔ Orchestrator & UI:**
  - Registry stores and updates metadata for each agent (status, endpoint, capabilities, avatar, etc.).
  - Orchestrator queries registry to discover available agents and their capabilities.
  - Chat UI queries registry to display agent directory, status, and avatars.

- **Chat UI ↔ Supabase Realtime:**
  - Chat UI subscribes to Supabase Realtime channels for live chat updates.
  - Renders messages and avatars for both users and agents.
  - Sends user messages to the channel, which are received by agents.

- **Pipecat Agent ↔ Supabase Realtime:**
  - Pipecat agent subscribes to the same chat channel as the user.
  - Receives user messages, processes them through its pipeline (LLM, TTS, etc.), and sends responses (text, audio, images) back to the channel.
  - Can update its status or avatar in real time.

- **Multimodal Flow:**
  - Text, audio, and image frames are sent as messages or media links in the chat channel.
  - Chat UI renders these using Supabase UI components.

**Architecture Diagram:**

```mermaid
flowchart TD
    User((User))
    ChatUI["Chat UI<br/>(Supabase UI)"]
    Orchestrator["Orchestrator<br/>(Archon-inspired)"]
    Registry["Agent Registry"]
    PipecatAgent["Pipecat Agent<br/>(Multimodal)"]
    Supabase["Supabase Realtime<br/>+ DB"]

    User -- interacts --> ChatUI
    ChatUI -- subscribes/publishes --> Supabase
    ChatUI -- queries --> Registry
    Orchestrator -- spawns/configures --> PipecatAgent
    Orchestrator -- registers/updates --> Registry
    Registry -- provides metadata --> Orchestrator
    Registry -- provides metadata --> ChatUI
    PipecatAgent -- subscribes/publishes --> Supabase
    Supabase -- delivers messages --> PipecatAgent
    Supabase -- delivers messages --> ChatUI
```

This diagram shows the flow of data and control between the user, chat UI, orchestrator, registry, Pipecat agent, and Supabase Realtime. Each component interacts via well-defined interfaces, enabling dynamic, multimodal, and real-time agent communication.

### Production & Scalability Notes
- For production, plan for scalable agent orchestration (worker pools, on-demand instances) and secure transport (SSL for custom UIs).
- Reference Pipecat docs for API and service integration details.

---

## Agent Communication Protocol

To ensure standardized and traceable interactions between agents, a formal communication protocol is defined.

- **Standardized Command Structure:** Agents communicate using a standardized `AgentCommand` structure, transmitted primarily via Pipecat `TextFrame`s. This structure includes a `command_type`, optional `task_id` for correlation, and an `args` dictionary for parameters.
- **Protocol Documentation:** Detailed specification of the `AgentCommand` structure and its usage within Pipecat is available in [./AGENT_COMMAND_PROTOCOL.md](./AGENT_COMMAND_PROTOCOL.md).
- **Multiple Communication Methods:** Leveraging Pipecat's diverse `Transport`s (WebSocket, custom, etc.) and integration capabilities (HTTP via FrameProcessors), agents can be powerful and reachable through various methods, enabling flexibility in deployment and interaction patterns.

---

## Observability Plan

To ensure the reliability, performance, and maintainability of the PMOVES Agent Platform, a comprehensive observability strategy will be implemented across all components (Agent Registry, Orchestrator, Pipecat Agents, and supporting services like the Crawl4AI Docker service and LiteLLM Proxy).

### Key Areas:

*   **Standardized Logging:**
    *   Implement structured logging (e.g., JSON format) in all services and agents.
    *   Define standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    *   Include correlation IDs (e.g., request ID, conversation ID, task ID) in logs to trace requests across components.
    *   Establish a centralized logging collection system (e.g., using filebeat, fluentd, or cloud provider services).

*   **Metrics Collection:**
    *   Identify key metrics for each component:
        *   **Registry:** Agent registration count, heartbeat frequency/latency, query rate, error rate.
        *   **Orchestrator:** Task processing rate, agent spawning/teardown rate, workflow latency, agent selection metrics.
        *   **Agents (Pipecat, etc.):** Message processing rate, pipeline latency, external service call latency (LLM, DB, etc.), error rate.
        *   **Services (Crawl4AI, LiteLLM Proxy):** Request rate, latency, error rate, resource usage (CPU, memory).
    *   Use a standard metrics library/framework (e.g., Prometheus client libraries).
    *   Set up a metrics storage and visualization system (e.g., Prometheus, Grafana).

*   **Distributed Tracing:**
    *   Implement distributed tracing to visualize the flow of requests and tasks across services.
    *   Propagate context (trace IDs, span IDs) between components using standard protocols (e.g., OpenTelemetry).
    *   Integrate tracing into key operations (e.g., a user request hitting the Orchestrator, which calls the Registry, selects an Agent, and the Agent interacts with an LLM).
    *   **Integrate Langfuse** for comprehensive tracing of LLM calls and agent workflows, leveraging its capabilities alongside the existing Grafana/Prometheus/Supabase stack.
    *   **Tracing Context Propagation:** Define and implement mechanisms to pass trace and span IDs between services (Orchestrator to Agent, Agent to LiteLLM, etc.) using headers, message metadata, or function call parameters. This ensures that all related operations fall under a single end-to-end trace in Langfuse.

*   **Health Checks:**
    *   Implement standard `/health` or `/ready` endpoints for REST services (Registry, Orchestrator).
    *   Agents should implement a mechanism to report their health status via heartbeats or a dedicated status endpoint.
    *   Use orchestration tools (like Docker Swarm or Kubernetes) to monitor health endpoints and restart unhealthy instances.

*   **Alerting:**
    *   Configure alerting rules based on critical metrics and error rates (e.g., high error rate for a specific agent, registry downtime, increased LLM latency).
    *   Integrate with a notification system (e.g., Slack, PagerDuty).

### Implementation Steps:
1.  Define a standardized logging format and implement it across core components.
2.  Instrument key code paths for metrics collection.
3.  Implement basic distributed tracing for core workflows.
4.  Add health check endpoints to services and health reporting to agents.
5.  Set up basic dashboards and alerts based on collected data.
6.  Iteratively refine observability based on operational needs.
7.  **Implement Secure Configuration Management:** Transition from environment variables to a secure secrets management solution (e.g., cloud secrets manager, HashiCorp Vault, or a `.env` alternative with encryption/access control) for sensitive information like API keys. This will facilitate easier and more secure integration of new LLM providers via LiteLLM.

---

## Project Goals
- Design a robust, extensible agent registry and discovery system
- Blueprint an orchestrator capable of dynamic agent management and workflow chaining
- Evaluate and prototype a real-time agent communication layer
- Document all schemas, APIs, and protocols for smooth implementation
- Track all tasks, dependencies, and research for transparency and coordination

---

## Current Implementation Status: Significantly Delayed & Partially Blocked

The project's current state significantly lags behind the optimistic claims previously in this document. As detailed in `PROJECT_REVIEW_AND_STATUS.md` and confirmed by codebase inspection, the platform is not complete or production-ready.

**Key Accomplishments to Date (Derived from `PROJECT_REVIEW_AND_STATUS.md` and code review):**

*   **Agent Registry (`pmoves-agent-registry`):**
    *   A standalone FastAPI service for agent registration and heartbeat is implemented and uses Supabase for persistence with a schema generally matching `PLAN.md`.
    *   API endpoints for register, heartbeat, list/get, and delete are present.
    *   *Correction:* Database calls in this service are synchronous, not asynchronous as claimed in `PLAN.md`'s "Implementation Notes" for the registry.
    *   *Note:* A separate set of agent registry routes (`backend/app/routes/agent_registry_routes.py`) also exists within the main backend, interacting with a different Supabase table ("agent_registry") and using a different schema. The purpose and relationship between these two registries are unclear.
*   **Core Agent Infrastructure (Conceptual & Basic Backend):**
    *   `AgentFramework` class (`backend/app/utils/agent_framework.py`) provides helpers for agents to register with an HTTP-based registry (like `pmoves-agent-registry`) and send heartbeats. This framework itself does not implement Pipecat-based communication.
    *   Initial Supabase integration for some agent data persistence.
    *   Basic FastAPI setup for some agent communication endpoints.
*   **Specialized Agent Development (Initial Versions & Concepts):**
    *   `MultimodalAgent`, `SupabaseAgent`, `ResearchAgent`, `CodeExecutionAgent`: Initial versions exist with some foundational capabilities.
    *   `psearchworking.py`: A comprehensive CLI tool for Supabase search (vector, keyword, hybrid) and LLM-based analysis exists. This *could* serve as the backend for `SupabaseAgent` search features, but its direct, active integration as a callable service within a running agent is not confirmed by code review of `psearchworking.py` alone.
    *   Pipecat Core Service (`pmoves-pipecat`): Foundational work including LiteLLM integration and basic tool-calling in `LiteLLMPipecatService` is noted in `STATUS.md`.
*   **Security Foundations (Partially Implemented & Inactive):**
    *   `SecurityMiddleware` (`backend/app/middleware/security_middleware.py`): Code for API key authentication exists but is **explicitly disabled in development mode**. Claims of comprehensive, active security are false. Rate limiting is not implemented in this middleware.
    *   `RestrictedPython` is used for basic code execution sandboxing.
*   **Tooling & Utilities:**
    *   Basic `FileHandler`, `AsyncWebBrowser`.
    *   `VectorDB` integration is conceptual/placeholder.
*   **Configuration Management:**
    *   Pydantic models for some configurations.
    *   `.env` file usage for sensitive settings.

**Current Blockers & Challenges (Primarily from `PROJECT_REVIEW_AND_STATUS.md`, supported by code review):**

1.  **Documentation Access & Interpretation:** Historical issues have caused delays.
2.  **Agent Orchestration & Communication:**
    *   Lack of robust inter-agent communication, task delegation, or workflow management.
    *   The `AgentCommand` protocol defined in `AGENT_COMMAND_PROTOCOL.md` for Pipecat communication is not implemented in `agent_framework.py` and its widespread use in helper agents is unconfirmed and unlikely given the overall status.
3.  **Security Hardening:**
    *   The main API key security middleware is currently disabled.
    *   `CodeExecutionAgent` sandboxing needs significant enhancement.
    *   Comprehensive API authentication/authorization and input validation are not fully implemented or active.
4.  **Task Management & Queuing:** Absence of a centralized task queue.
5.  **Testing & Validation:** Automated testing is largely absent.
6.  **VectorDB/Knowledge Base Integration:** `VectorDB` component remains a placeholder.
7.  **Outdated Planning Documents:** This document (`PMOVES_AGENT_PLATFORM_PLAN.md`) and `ARCHITECTURE.md` require significant updates to reflect the project's true status.
8.  **Agent Registry Ambiguity:** The existence of two separate agent registry implementations needs clarification.

---

## Next Steps & Priorities (Revised)

*   **IMMEDIATE & CRITICAL (Unblocking Task):**
    *   **Priority 1: Resolve Documentation Access.** This is paramount. If `view_text_website` remains unreliable for core library documentation, an alternative strategy *must* be found. This could involve:
        *   Requesting pre-fetched, plain-text versions of key documentation pages to be loaded into the project.
        *   If the issue is with specific sites, try to find alternative documentation sources (e.g., simplified guides, cheat sheets if full docs are too complex for the tool).
        *   **Without this, the project cannot meaningfully proceed on many fronts.**

*   **Once Documentation is Accessible (Core Infrastructure & Refinement):**
    *   **Priority 2: Full SecurityMiddleware Implementation & Integration:**
        *   Implement and test robust API key and/or JWT authentication for all agent endpoints.
        *   Ensure comprehensive input validation using Pydantic for all API request models.
        *   Integrate FastAPI's security utilities correctly.
        *   Review and apply necessary security headers.
    *   **Priority 3: Enhance CodeExecutionAgent Security & Functionality:**
        *   Investigate and implement stricter sandboxing mechanisms (e.g., Docker containers, WebAssembly runtimes, or more advanced `RestrictedPython` configurations if feasible).
        *   Develop clear input/output mechanisms for file handling within the sandboxed environment.
        *   Implement resource limits (CPU, memory, time).
    *   **Priority 4: Refine Individual Agent Capabilities & Error Handling:**
        *   **MultimodalAgent:** Solidify error handling for API calls, improve configuration validation.
        *   **SupabaseAgent:** Ensure DDL operations are truly safe (e.g., by requiring specific confirmations or using a more robust RPC mechanism than a generic "execute_sql_unsafe"). Improve error parsing from Supabase.
        *   **ResearchAgent:** Implement a basic task queue (e.g., using Redis or a Supabase table) for managing search/fetch tasks and their results.
        *   **All Agents (including Pipecat services):** Continue to review and improve error handling, logging, and status reporting based on proper documentation. Solidify tool execution logic within `LiteLLMPipecatService` beyond placeholders.

*   **Future Goals (Post-Blocker Resolution & Core Refinement):**
    *   Develop a robust inter-agent communication protocol (e.g., message bus like Redis pub/sub, or a dedicated orchestration service).
    *   Implement comprehensive automated testing.
    *   Integrate `VectorDB` properly for RAG capabilities and shared knowledge.
    *   Develop a user interface or CLI for managing agents and tasks.
    *   Priority 5: Update `PMOVES_AGENT_PLATFORM_PLAN.md`: Once documentation is unblocked, accurately reflect the project's true status and a detailed, revised roadmap.

---

## Implementation Progress & Iteration Tracker

This section tracks the step-by-step implementation of the Supabase Agent and related platform features. After each iteration, this checklist and plan will be updated to reflect progress and define the next focus area.

### Supabase Agent Fundamentals: Iterative Checklist

- [x] **Catalog existing agent patterns and document adaptation strategy**
- [x] **Update master plan with agent catalog and integration plan**
- [ ] **Scaffold minimal Pipecat agent:**
    - [ ] Connect to Supabase Realtime chat channel
    - [ ] Process incoming messages through a text-only Pipecat pipeline
    - [ ] Send responses to chat with assigned avatar
    - [ ] Register agent with orchestrator/registry
- [ ] **Enhanced Core Service Implementation:**
    - [ ] Full multimodal pipeline creation (TTS, STT, WebRTC, image processing)
    - [ ] Supabase Realtime integration with message routing
    - [ ] Enhanced agent registry with capability detection
    - [ ] A2A protocol support for agent-to-agent communication
    - [ ] Dynamic agent spawning and orchestration
    - [ ] WebSocket and WebRTC transport support
- [ ] **Complete Agent Implementations:**
    - [ ] SupabaseAgent with search/upsert integration
    - [ ] TranscribeAgent with multimodal processing
    - [ ] MultimodalAgent with vision and generation
- [ ] **Production Features:**
    - [ ] Authentication and authorization
    *   [ ] Rate limiting and validation
    *   [ ] Comprehensive monitoring and logging
    *   [ ] Performance optimization
- [ ] **Advanced Features:**
    *   [ ] Agent marketplace and plugin system
    *   [ ] Multi-tenant support
    *   [ ] Enterprise integrations
    *   [ ] Mobile app support

**Current Status: Core Components Partially Implemented, Significant Blockers Remain**
- Foundational work on some core services (like `pmoves-agent-registry`, `psearchworking.py` CLI, parts of `pmoves-pipecat`) and initial versions of specialized agents exist.
- Key platform features such as robust agent orchestration, inter-agent communication (via the defined `AgentCommand` protocol), comprehensive security (API auth is currently disabled), task management, and automated testing are largely incomplete or not yet implemented.
- Critical blockers, including those related to documentation access (historically) and finalising core infrastructure, need to be addressed.
- The platform is not production-ready. Development should focus on addressing blockers and implementing core features and security measures as outlined in the 'Next Steps & Priorities' section.

*This doc will be updated as the project progresses. See individual task breakdowns for detailed status and references.* 