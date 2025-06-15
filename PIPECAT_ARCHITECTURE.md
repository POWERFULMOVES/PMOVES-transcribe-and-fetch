# PMOVES Pipecat Architecture

## Overview

The PMOVES Pipecat system follows a **core service + agent instances** architecture with full **multimodal capabilities**, **WebRTC integration**, and **Supabase Realtime chat integration** as outlined in the masterplan.

## Architecture Components

### 1. Core Pipecat Service (`pmoves-pipecat`)
**Purpose**: Central communication layer and orchestrator with full multimodal capabilities
- **Port**: 8080 (API), 8081 (WebSocket)
- **Container**: `pmoves-pipecat`
- **Responsibilities**:
  - LiteLLM integration for model serving
  - Agent registry integration with enhanced metadata
  - A2A protocol support for agent-to-agent communication
  - Dynamic agent spawning/orchestration
  - WebSocket communication hub
  - **WebRTC support** via Daily.co integration
  - **Multimodal pipelines** (text, audio, video, images)
  - Example stub in `pmoves-pipecat-agent/multimodal_pipeline.py`
  - **Supabase Realtime integration** for chat
  - **Message routing** via a simple router in `minimal_agent.py`
  - **TTS/STT services** (ElevenLabs, Deepgram)
  - **Advanced Tool-Calling**: The custom `LiteLLMPipecatService` enables robust tool-calling. It leverages LiteLLM's native support for OpenAI-compatible tool calling by passing tool schemas (managed by `ToolSchemaManager`) directly to the LLM via the `tools` parameter in `acompletion` calls. The execution flow is as follows:
    1. The LLM indicates its intent to use a tool in its response.
    2. `LiteLLMPipecatService` detects this tool request (e.g., via `LLMToolCallFrame`).
    3. Streamed tool arguments are accumulated using `ArgumentAccumulatorService`.
    4. The service dispatches to the appropriate registered asynchronous tool handler (via `register_tool_handler` and the `_tool_handlers` dictionary) for modular execution.
    5. The tool's result is then packaged into a "tool" role message and sent back to the LLM in a subsequent `acompletion` call to obtain the final, user-facing response.
    (Note: While LiteLLM provides a callback system, e.g., `CustomLogger`, it is primarily for observability and does not currently offer a direct hook for intercepting and executing tool calls mid-turn, necessitating the described multi-step process.)

### 2. Agent Instances (`pmoves-pipecat-agent`)
**Purpose**: Specialized task execution clients that connect to the Core Pipecat Service. They are not direct Pipecat pipeline participants but rather execute business logic based on commands received.
- **Port**: 8000 (configurable)
- **Container**: `pmoves-pipecat-agent` (example: Supabase agent)
- **Responsibilities**:
  - Connect to the Core Pipecat Service (`pmoves-pipecat`) via WebSocket (as implemented in `pmoves-pipecat-agent/agent.py`). WebRTC connection from agent instance to core is not evident in `agent.py`.
  - House specialized logic for different agent types (e.g., `SupabaseAgent`, `TranscribeAgent`, `MultimodalAgent` in `pmoves-pipecat-agent/agents/`). These specialized classes are not Pipecat `FrameProcessor`s themselves but contain the business logic.
  - Integrate with Supabase Realtime for chat command input and text responses (managed by `PipecatAgentClient` in `agent.py`).
  - Process text-based commands received from the Core Pipecat Service or Supabase Realtime, delegating to the specialized agent logic.
  - Optional OpenTelemetry tracing using `PipelineTask` (see `ENABLE_TRACING`).
  - **Clarification on Frame Handling:** Multimodal Pipecat frame processing (e.g., `AudioFrame`, `ImageFrame`) and the handling of tool-related Pipecat frames (`LLMToolCallFrame`, `FunctionCallResultFrame`, etc.) primarily occur within the Core Pipecat Service (`pmoves-pipecat`), specifically in services like `LiteLLMPipecatService`. The `pmoves-pipecat-agent` instances receive tasks (often derived from these processed frames by the core service) and execute them, returning results typically as text or structured data.
  - **Frame Types**: TextFrame, AudioFrame, VideoFrame, ImageFrame, LLMMessagesFrame
  - **Tool-Related Frames**: Utilizes `LLMToolCallFrame` (LLM requests a tool), `FunctionCallInProgressFrame` (tool execution started), and `FunctionCallResultFrame` (result of tool execution) to manage the tool-calling lifecycle within pipelines.
  - These frames are primarily processed and managed within the Core Pipecat Service (`pmoves-pipecat`). Agent Instances (`pmoves-pipecat-agent`) interact with the outcomes of these processes rather than directly handling these Pipecat frames in their own pipelines.
  - `LLMMessagesFrame`: Carries the history of messages for the LLM.
  - `LLMToolCallFrame`: Indicates the LLM's intent to call a specific tool, including its name and (streamed) arguments.
  - `FunctionCallInProgressFrame`: Signals that a requested tool call is actively being processed.
  - `FunctionCallResultFrame`: Contains the outcome (data or error) of an executed tool call, ready to be sent back to the LLM as part of the multi-step tool execution flow.
  - `ToolsFrame` (Conceptual/Managed by `ToolSchemaManager`): Represents the collection of tool schemas. These are managed by `ToolSchemaManager` and provided directly to LiteLLM's `acompletion` function (in the `tools` parameter), rather than being pushed as a distinct frame through the Pipecat pipeline by the `LiteLLMPipecatService` itself.

## Communication Flow

```mermaid
flowchart TD
    User[User in Chat/WebRTC] --> Supabase[Supabase Realtime]
    User --> WebRTC[Daily.co WebRTC]
    
    Supabase --> Agent[Pipecat Agent Instance]
    WebRTC --> Core[Core Pipecat Service]
    Agent --> Core
    
    Core --> LiteLLM[LiteLLM Proxy]
    Core --> Registry[Agent Registry]
    Core --> TTS[ElevenLabs TTS]
    Core --> STT[Deepgram STT]
    
    LiteLLM --> Models[AI Models]
    
    Agent --> |A2A Protocol| OtherAgent[Other Agent Instances]
    Core --> |Orchestrates| OtherAgent
    
    Core -- Tasks/Data (WebSocket) --> Agent
    Agent -- Results (WebSocket) --> Core
    Agent --> |Chat Response| Supabase
```

## Key Features

### Multimodal Capabilities
- **Text Processing**: LLM integration via LiteLLM proxy
- **Audio Processing**: TTS (ElevenLabs) and STT (Deepgram) services
- **Video Processing**: WebRTC streams via Daily.co
- **Image Processing**: Image frame support in Core Service pipelines
- **Frame Types**: TextFrame, AudioFrame, VideoFrame, ImageFrame, LLMMessagesFrame

### WebRTC Integration
- **Daily.co Transport**: Real-time audio/video communication
- **Room Management**: Dynamic room creation and management
- **Bot Integration**: Agents can join WebRTC calls as participants
- **Multimodal Streams**: Audio, video, and data channels

### Supabase Realtime Chat Integration
- **Real-time Messaging**: Live chat via Supabase Realtime
- **Agent Summoning**: Call agents with `@AgentName` syntax
- **Message Routing**: Automatic routing to appropriate agents
- **Response Handling**: Agents respond with avatars and capabilities
- **Channel Management**: Multiple chat channels supported

### Enhanced Agent Registry Integration
- **Capability Detection**: Dynamic capability detection based on available services
- **Capability Endpoint**: `GET /capabilities` lists capabilities across all agents
- **Provider Capability Query**: `/provider_capabilities` uses LiteLLM to list supported parameters
- **Multimodal Metadata**: Transport types, supported modalities
- **Real-time Status**: Live agent status and health monitoring
- **A2A Protocol**: Agent discovery and inter-agent messaging

### Dynamic Agent Spawning
- **On-demand Creation**: Spawn agents based on requirements
- **Capability-based**: Agents created with specific capabilities
- **Transport Selection**: WebSocket or WebRTC transport
- **Pipeline Configuration**: Custom pipelines per agent type

## Environment Configuration

### Core Service Environment Variables
```bash
# Core service
PIPECAT_SERVICE_PORT=8080
PIPECAT_WEBSOCKET_PORT=8081
LITELLM_PROXY_URL=http://litellm-proxy:4000
AGENT_REGISTRY_URL=http://backend:8000/agents
MAX_AGENTS=10

# Multimodal capabilities
DAILY_API_KEY=your_daily_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key

# Supabase integration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### Agent Instance Environment Variables
```bash
AGENT_TYPE=supabase
AGENT_NAME=SupabaseAgent
CALL_WORD=@SupabaseAgent
CHAT_CHANNEL=main-room
AVATAR_URL=https://example.com/supabase-agent-avatar.png
PIPECAT_SERVICE_URL=http://pipecat:8080
PIPECAT_WS_URL=ws://pipecat:8081
```

## Agent Types and Capabilities

### Supabase Agent
- **Base Capabilities**: text, chat, database, search, upsert
- **Multimodal**: +tts, +stt, +webrtc (if API keys provided)
- **Commands**: `search`, `create table`, `upsert`
- **Integration**: Direct Supabase client access + Realtime chat

### Transcribe Agent
- **Base Capabilities**: text, chat, transcription, media_processing
- **Multimodal**: +tts, +stt, +webrtc, +audio, +video
- **Commands**: `transcribe <url>`, `process audio`, `process video`
- **Integration**: Audio/video processing services

### Multimodal Agent
- **Base Capabilities**: text, chat, vision, image_generation, audio_processing
- **Multimodal**: +tts, +stt, +webrtc, +audio, +video, +image
- **Commands**: `analyze image`, `generate image`, `process audio`
- **Integration**: Vision models, image generation, audio processing

## API Endpoints

### Core Service (`pmoves-pipecat`)
- `GET /health` - Service health with multimodal capability status
- `GET /agents` - List active agents with capabilities
- `POST /agents/spawn` - Spawn new agent instance with config
- `DELETE /agents/{agent_id}` - Stop agent instance
- `GET /models` - List available LiteLLM models
- `POST /chat/send` - Send message to chat channel
- `WS /ws/{agent_id}` - WebSocket for agent communication (supports multimodal frames)
- `GET /a2a/discover` - A2A agent discovery with multimodal info
- `POST /a2a/message/{agent_id}` - A2A messaging with response

### Agent Instance (`pmoves-pipecat-agent`)
- `GET /health` - Agent health, status, and capabilities
- `GET /config` - Agent configuration and settings

## WebSocket Frame Protocol

### Supported Frame Types (Expanded)
The following Pipecat frames are primarily handled and generated within the Core Pipecat Service (`pmoves-pipecat`), particularly by services like `LiteLLMPipecatService`. Agent Instances (`pmoves-pipecat-agent`) typically receive tasks derived from these processed frames via WebSocket.
Pipecat uses a variety of frame types to manage data flow. In addition to basic types like `TextFrame`, `AudioFrame`, `ImageFrame`, and `VideoFrame`, the system heavily relies on specialized frames for LLM interaction and tool-calling:
- `LLMMessagesFrame`: Carries the history of messages for the LLM.
- `LLMToolCallFrame`: Indicates the LLM's intent to call a specific tool, including its name and (streamed) arguments.
- `FunctionCallInProgressFrame`: Signals that a requested tool call is actively being processed.
- `FunctionCallResultFrame`: Contains the outcome (data or error) of an executed tool call, ready to be sent back to the LLM as part of the multi-step tool execution flow.
- `ToolsFrame` (Conceptual/Managed by `ToolSchemaManager`): Represents the collection of tool schemas. These are managed by `ToolSchemaManager` and provided directly to LiteLLM's `acompletion` function (in the `tools` parameter), rather than being pushed as a distinct frame through the Pipecat pipeline by the `LiteLLMPipecatService` itself.

```json
{
  "type": "text",
  "text": "Hello, agent!"
}

{
  "type": "audio",
  "audio": "base64_encoded_audio_data"
}

{
  "type": "image", 
  "image": "base64_encoded_image_data"
}

{
  "type": "video",
  "video": "base64_encoded_video_data"
}
```

### Response Format
```json
{
  "type": "text",
  "agent_id": "supabase_1",
  "data": "Agent response text"
}
```

## Deployment

### Using Docker Compose
```bash
# Build and start core service
docker-compose up pipecat

# Start agent instances
docker-compose up pipecat-agent

# Or start everything
docker-compose up
```

### Health Checks
- Core Service: `http://localhost:8080/health`
- Agent Instance: `http://localhost:8001/health`

### Health Response Example
```json
{
  "status": "healthy",
  "service": "pmoves-pipecat-core",
  "agents_count": 2,
  "max_agents": 10,
  "litellm_available": true,
  "supabase_available": true,
  "realtime_available": true,
  "a2a_available": false,
  "webrtc_available": true,
  "multimodal_capabilities": {
    "tts": true,
    "stt": true,
    "webrtc": true
  }
}
```

## Integration Examples

### Chat Integration
1. User sends message: `@SupabaseAgent search for climate data`
2. Supabase Realtime delivers message to core service
3. Core service routes to SupabaseAgent
4. Agent processes command and searches database
5. Agent responds via Supabase Realtime with results
6. Response appears in chat with agent avatar

### WebRTC Integration
1. User joins Daily.co room
2. Agent spawned with WebRTC transport
3. Agent joins same room as bot participant
4. Real-time audio/video communication
5. Multimodal processing (speech-to-text, text-to-speech)
6. Agent responds with voice and can share screen/video

### A2A Protocol
1. SupabaseAgent needs transcription service
2. Sends A2A message to TranscribeAgent
3. TranscribeAgent processes audio/video
4. Returns transcription via A2A protocol
5. SupabaseAgent stores results in database
6. Collaborative workflow completed

## Next Steps

1. **Complete Pipeline Implementation**
   - Implement full Pipecat pipeline creation
   - Add custom LiteLLM service for Pipecat
   - Enhance frame processing logic

2. **WebRTC Enhancement**
   - Add room management API
   - Implement screen sharing
   - Add video processing capabilities

3. **Agent Registry Enhancement**
   - Add capability-based agent discovery
   - Implement agent health monitoring
   - Add performance metrics

4. **Production Features**
   - Add authentication and authorization
   - Implement rate limiting
   - Add comprehensive logging and monitoring
   - Scale for production workloads 