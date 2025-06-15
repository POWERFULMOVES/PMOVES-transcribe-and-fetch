"""
PMOVES Core Pipecat Service

This is the core communication layer that:
- Integrates with LiteLLM for model serving
- Manages agent registry and discovery
- Handles A2A protocol communication
- Orchestrates dynamic agent spawning
- Provides multimodal communication capabilities (WebRTC, audio, video, images)
- Integrates with Supabase Realtime for chat
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import httpx

# Pipecat imports
try:
    from pipecat.pipeline.pipeline import Pipeline
    from pipecat.pipeline.runner import PipelineRunner
    from pipecat.frames.frames import (
        Frame,
        TextFrame,
        AudioRawFrame as AudioFrame,
        ImageRawFrame as ImageFrame,
        VideoFrame,
        LLMMessagesFrame,
        FunctionCallInProgressFrame,
        FunctionCallResultFrame,
    )
    from pipecat.services.openai import OpenAILLMService
    from pipecat.services.elevenlabs import ElevenLabsTTSService
    from pipecat.services.deepgram import DeepgramSTTService
    from pipecat.transports.services.daily import DailyTransport, DailyParams
    from pipecat.transports.services.websocket import WebsocketTransport
    from pipecat.processors.aggregators.llm_response import LLMResponseAggregator
    from pipecat.processors.aggregators.sentence import SentenceAggregator
    from pipecat.processors.frame_processor import FrameProcessor
    from pipecat.pipeline.frames import FrameDirection

    print("[INFO] Pipecat core imports successful")
except ImportError as e:
    print(f"[WARNING] Pipecat imports failed: {e}")


# Attempt to import LiteLLMPipecatService and related backend services
try:
    from src.pipecat.services.litellm_service import LiteLLMPipecatService
    from backend.app.utils.llm_registry_service import LLMRegistryService
    print("[INFO] LiteLLMPipecatService and LLMRegistryService imported.")
except ImportError as e:
    LiteLLMPipecatService = None
    LLMRegistryService = None
    print(f"[WARNING] Failed to import LiteLLMPipecatService or LLMRegistryService: {e}")


# LiteLLM integration
try:
    import litellm
    # from litellm import completion # completion is not directly used, Router is.
    if not hasattr(litellm, 'Router'):
        print("[WARNING] litellm.Router not available, LiteLLM integration might be limited.")
    print("[INFO] LiteLLM integration components available")
except ImportError:
    litellm = None
    print("[WARNING] LiteLLM not available")

# Supabase and realtime
try:
    from supabase import create_client, Client
    from realtime import AsyncRealtimeClient

    print("[INFO] Supabase integration available")
except ImportError:
    print("[WARNING] Supabase integration not available")

# A2A protocol models (lightweight fallback)
try:
    from .a2a_models import (
        JSONRPCRequest,
        JSONRPCResponse,
        TaskSendRequest,
        TaskGetRequest,
        Task,
        TaskStatus,
        TaskState,
        Message,
        TextPart,
        AgentCard,
        AgentCapabilities,
        AgentSkill,
    )
    a2a_available = True
    print("[INFO] Local A2A models available")
except Exception as e:
    a2a_available = False
    print(f"[WARNING] A2A models not available: {e}")


# Configuration
class PipecatConfig(BaseModel):
    litellm_proxy_url: str = "http://litellm-proxy:4000"
    agent_registry_url: str = "http://backend:8000/agents"
    supabase_url: str = ""
    supabase_key: str = ""
    service_port: int = 8080
    websocket_port: int = 8081
    max_agents: int = 10
    daily_api_key: str = ""
    elevenlabs_api_key: str = ""
    deepgram_api_key: str = ""


# Load configuration
def load_config() -> PipecatConfig:
    return PipecatConfig(
        litellm_proxy_url=os.getenv("LITELLM_PROXY_URL", "http://litellm-proxy:4000"),
        agent_registry_url=os.getenv(
            "AGENT_REGISTRY_URL", "http://backend:8000/agents"
        ),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        service_port=int(os.getenv("PIPECAT_SERVICE_PORT", "8080")),
        websocket_port=int(os.getenv("PIPECAT_WEBSOCKET_PORT", "8081")),
        max_agents=int(os.getenv("MAX_AGENTS", "10")),
        daily_api_key=os.getenv("DAILY_API_KEY", ""),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
    )


config = load_config()


# Agent management with multimodal capabilities
class AgentInstance:
    def __init__(self, agent_id: str, agent_type: str, agent_config: Dict[str, Any], 
                 llm_registry_service: Optional[Any] = None, 
                 litellm_router: Optional[Any] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = agent_config
        self.llm_registry_service = llm_registry_service
        self.litellm_router = litellm_router
        self.pipeline: Optional[Pipeline] = None
        self.runner: Optional[PipelineRunner] = None
        self.transport: Optional[Any] = None
        self.websocket_connections: List[WebSocket] = []
        self.status = "initializing"
        self.capabilities = self._determine_capabilities()
        self.output_queue = asyncio.Queue()

    def _determine_capabilities(self) -> List[str]:
        """Determine agent capabilities based on type and available services"""
        base_capabilities = ["text", "chat"]

        # Add multimodal capabilities based on available API keys
        if config.elevenlabs_api_key:
            base_capabilities.append("tts")
        if config.deepgram_api_key:
            base_capabilities.append("stt")
        if config.daily_api_key:
            base_capabilities.extend(["webrtc", "audio", "video"])

        # Agent-type specific capabilities
        if self.agent_type == "supabase":
            base_capabilities.extend(["database", "search", "upsert"])
        elif self.agent_type == "transcribe":
            base_capabilities.extend(["transcription", "media_processing"])
        elif self.agent_type == "multimodal":
            base_capabilities.extend(["vision", "image_generation", "audio_processing"])

        return base_capabilities

    async def create_pipeline(self) -> Pipeline:
        """Create a multimodal Pipecat pipeline for this agent"""
        try:
            # Create services based on capabilities
            services = []

            # LLM Service (using LiteLLMPipecatService)
            if LiteLLMPipecatService and self.llm_registry_service and self.litellm_router:
                preferred_model_alias = self.config.get("llm_model_alias", "gpt-4o-mini") # Default model
                llm_service = LiteLLMPipecatService(
                    llm_registry_service=self.llm_registry_service,
                    litellm_router=self.litellm_router,
                    preferred_model_alias=preferred_model_alias
                )
                services.append(llm_service)
                print(f"[INFO] LiteLLMPipecatService configured for agent {self.agent_id} with model {preferred_model_alias}")
            elif litellm: # Fallback to OpenAI if custom service or its deps are missing
                print(f"[WARNING] LiteLLMPipecatService not available or not configured for agent {self.agent_id}. Falling back to OpenAILLMService.")
                llm_service = OpenAILLMService(
                    api_key=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY"), # Ensure a default key or handle missing
                    model=self.config.get("llm_model_alias", "gpt-4o-mini") # Use alias or default
                )
                services.append(llm_service)
            else:
                print(f"[ERROR] No LLM service configured for agent {self.agent_id}")


            # TTS Service
            if config.elevenlabs_api_key and "tts" in self.capabilities:
                tts_service = ElevenLabsTTSService(
                    api_key=config.elevenlabs_api_key,
                    voice_id="21m00Tcm4TlvDq8ikWAM",  # Default voice
                )
                services.append(tts_service)

            # STT Service
            if config.deepgram_api_key and "stt" in self.capabilities:
                stt_service = DeepgramSTTService(api_key=config.deepgram_api_key)
                services.append(stt_service)

            # Aggregators
            services.extend([SentenceAggregator(), LLMResponseAggregator()])
            
            # Add custom output processor
            services.append(OutputQueueProcessor(self.output_queue))

            # Create pipeline
            pipeline = Pipeline(services)
            return pipeline

        except Exception as e:
            print(f"[ERROR] Failed to create pipeline for agent {self.agent_id}: {e}")
            return None

    async def create_transport(self, transport_type: str = "websocket") -> Any:
        """Create transport for the agent"""
        try:
            if transport_type == "daily" and config.daily_api_key:
                # WebRTC transport via Daily
                daily_params = DailyParams(
                    api_key=config.daily_api_key,
                    room_url=self.config.get("room_url", ""),
                    token=self.config.get("token", ""),
                )
                transport = DailyTransport(
                    room_url=daily_params.room_url,
                    token=daily_params.token,
                    bot_name=self.config.get("name", self.agent_id),
                )
                return transport
            else:
                # WebSocket transport (default)
                transport = WebsocketTransport()
                return transport

        except Exception as e:
            print(f"[ERROR] Failed to create transport for agent {self.agent_id}: {e}")
            return None

    async def start(self):
        """Start the agent pipeline"""
        try:
            # Create pipeline
            self.pipeline = await self.create_pipeline()
            if not self.pipeline:
                raise Exception("Failed to create pipeline")

            # Create transport
            transport_type = self.config.get("transport", "websocket")
            self.transport = await self.create_transport(transport_type)
            if not self.transport:
                raise Exception("Failed to create transport")

            # Create and start runner
            self.runner = PipelineRunner(self.pipeline, self.transport)
            await self.runner.start()

            self.status = "running"
            print(
                f"[INFO] Agent {self.agent_id} started with capabilities: {self.capabilities}"
            )

        except Exception as e:
            self.status = "error"
            print(f"[ERROR] Failed to start agent {self.agent_id}: {e}")

    async def stop(self):
        """Stop the agent pipeline"""
        try:
            if self.runner:
                await self.runner.stop()

            # Close WebSocket connections
            for ws in self.websocket_connections:
                try:
                    await ws.close()
                except:
                    pass
            self.websocket_connections.clear()

            self.status = "stopped"
            print(f"[INFO] Agent {self.agent_id} stopped")
        except Exception as e:
            print(f"[ERROR] Failed to stop agent {self.agent_id}: {e}")

    async def process_frame(self, frame: Frame) -> Optional[TextFrame]:
        """Process a frame through the agent's pipeline and get a single TextFrame response."""
        if not self.pipeline:
            print(f"[ERROR] Pipeline not available for agent {self.agent_id}")
            return TextFrame(text="Error: Pipeline not available")

        try:
            # Ensure the queue is empty before processing a new frame
            while not self.output_queue.empty():
                self.output_queue.get_nowait()

            # Push the frame into the pipeline for processing.
            # The direction is DOWNSTREAM as it's going from the client into the pipeline.
            await self.pipeline.process_frame(frame, FrameDirection.DOWNSTREAM)

            # Wait for the OutputQueueProcessor to put the result into the queue.
            # This assumes the pipeline produces a single TextFrame as a result.
            processed_frame = await asyncio.wait_for(self.output_queue.get(), timeout=30.0)  # 30s timeout

            if isinstance(processed_frame, TextFrame):
                return processed_frame
            else:
                print(f"[WARNING] Unexpected output frame type for agent {self.agent_id}: {type(processed_frame)}")
                return TextFrame(text=f"Error: Unexpected output type: {type(processed_frame)}")

        except asyncio.TimeoutError:
            print(f"[ERROR] Frame processing timed out for agent {self.agent_id}")
            return TextFrame(text="Error: Processing timed out")
        except Exception as e:
            print(f"[ERROR] Frame processing in pipeline failed for agent {self.agent_id}: {e}")
            return TextFrame(text=f"Error: {str(e)}")


# Custom FrameProcessor to capture output frames
class OutputQueueProcessor(FrameProcessor):
    def __init__(self, queue: asyncio.Queue):
        super().__init__()
        self.queue = queue

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        # Capture TextFrames moving UPSTREAM (i.e., results from the pipeline)
        if isinstance(frame, TextFrame) and direction == FrameDirection.UPSTREAM:
            await self.queue.put(frame)
        
        # Always push the frame so it continues through the pipeline if needed (e.g. to a transport)
        # However, for this specific request-response, we capture and stop it here via the queue.
        # If this processor is the absolute last, pushing is more for standard pipeline completion.
        # If other sinks/transports rely on this, ensure frame continues.
        # For now, we assume this is the primary mechanism for getting the response for process_frame.
        # To prevent frames from going to a transport if this is a direct call,
        # this processor might conditionally not push, or be added only for such calls.
        # For simplicity, let's assume it pushes, and the WebsocketTransport (if active)
        # would also get it but process_frame gets its copy first.
        await self.push_frame(frame, direction)


class PipecatOrchestrator:
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.litellm_client = None # This might be redundant if router is primary interaction point
        self.supabase_client = None
        self.realtime_client = None
        self.chat_channels: Dict[str, Any] = {}
        self.llm_registry_service = None
        self.litellm_router = None

    async def initialize(self):
        """Initialize the orchestrator"""
        # Initialize LLMRegistryService
        if LLMRegistryService:
            try:
                # The base URL for LLMRegistryService should be the backend app's URL
                # Example: "http://backend:8000" if agent_registry_url is "http://backend:8000/agents"
                backend_base_url = config.agent_registry_url.rsplit('/', 1)[0] if '/agents' in config.agent_registry_url else config.agent_registry_url
                self.llm_registry_service = LLMRegistryService(base_url=backend_base_url)
                print(f"[INFO] LLMRegistryService initialized with base_url: {backend_base_url}")
            except Exception as e:
                print(f"[ERROR] Failed to initialize LLMRegistryService: {e}")
        else:
            print("[WARNING] LLMRegistryService not available.")

        # Initialize LiteLLM Router
        if litellm and hasattr(litellm, 'Router'):
            try:
                # Basic model list - ideally fetched from LLMRegistryService or config
                # Ensure this list is compatible with how LiteLLMPipecatService expects to find models via router
                
                model_list_for_router = []
                if self.llm_registry_service:
                    try:
                        # Fetch all available models. Add filters if needed.
                        available_llms = await self.llm_registry_service.get_available_models()
                        for llm in available_llms:
                            # The router's model_name is the alias that LiteLLMPipecatService will use.
                            # LiteLLMPipecatService looks up models in the router using `preferred_model_alias`,
                            # which corresponds to `StandardizedLLM.display_name` (the alias from LiteLLM config).
                            # The router's `litellm_params.model` should be `StandardizedLLM.model_id`
                            # (the actual provider/model_name like "openai/gpt-4o-mini").
                            
                            # Router's model_name should be the alias (StandardizedLLM.display_name)
                            router_model_name = llm.display_name 
                            
                            # litellm_params.model should be the fully qualified ID (StandardizedLLM.model_id)
                            litellm_model_id = llm.model_id

                            model_entry_for_router = {
                                "model_name": router_model_name, # Alias for router matching
                                "litellm_params": {
                                    "model": litellm_model_id, # Actual model for LiteLLM to call
                                    # api_base and api_key can be set here if they are model-specific
                                    # and override the global litellm.api_base or proxy defaults.
                                    # For now, assume global proxy handles this.
                                }
                            }
                            # Add pricing and rate limits if available and if router uses them
                            if llm.pricing:
                                model_entry_for_router["litellm_params"]["rpm"] = llm.pricing.get("rpm") # Example
                                model_entry_for_router["litellm_params"]["tpm"] = llm.pricing.get("tpm") # Example
                            
                            model_list_for_router.append(model_entry_for_router)
                        
                        print(f"[INFO] Fetched {len(model_list_for_router)} models from LLMRegistryService for LiteLLM Router.")
                        if not model_list_for_router:
                            print("[WARNING] LLMRegistryService returned no models. LiteLLM Router might be empty or use defaults.")
                            # Fallback to a minimal default if needed, or let router initialize empty.
                            # For now, we'll let it initialize with what it gets.
                    except Exception as e_fetch_llm:
                        print(f"[ERROR] Failed to fetch models from LLMRegistryService: {e_fetch_llm}. Router may be empty.")
                else:
                    print("[WARNING] LLMRegistryService not available. LiteLLM Router will be initialized with an empty model list or default.")

                # example_model_list = [{
                #     "model_name": "gpt-4o-mini", # This is an alias LiteLLMPipecatService will use
                #     "litellm_params": {          # Params LiteLLM Router uses to call the model
                #         "model": "gpt-4o-mini",  # Actual model identifier for LiteLLM
                #         # "api_base": config.litellm_proxy_url, # Proxy URL for this specific model
                #         # "api_key": os.getenv("OPENAI_API_KEY") # Specific key if needed, else proxy handles
                #     }
                # }]
                # Router can be configured to use the proxy globally or per model.
                # If all models go via the same proxy, setting litellm.api_base might be enough.
                # However, LiteLLMPipecatService is designed to work with a router that has models from potentially multiple sources.
                
                self.litellm_router = litellm.Router(
                    model_list=model_list_for_router if model_list_for_router else [], # Use fetched models or empty list
                    # Fallbacks can be configured here if needed
                    routing_strategy="simple-shuffle", # Or another strategy
                    # set_verbose=True # For debugging router behavior
                )
                # Set the general api_base for litellm to use the proxy for any calls not specifying it.
                litellm.api_base = config.litellm_proxy_url 
                self.litellm_client = litellm # Keep for direct calls if any, or phase out
                print(f"[INFO] LiteLLM Router initialized. Global api_base: {config.litellm_proxy_url}")
            except Exception as e:
                print(f"[ERROR] Failed to initialize LiteLLM Router: {e}")
        else:
            print("[WARNING] LiteLLM Router not available.")

        # Initialize Supabase client
        if config.supabase_url and config.supabase_key:
            try:
                self.supabase_client = create_client(
                    config.supabase_url, config.supabase_key
                )
                print("[INFO] Supabase client initialized")

                # Initialize Realtime client
                await self._setup_realtime()

            except Exception as e:
                print(f"[ERROR] Failed to initialize Supabase client: {e}")

    async def _setup_realtime(self):
        """Setup Supabase Realtime for chat integration"""
        try:
            if not self.supabase_client:
                return

            # Extract Supabase project ID from URL
            supabase_id = config.supabase_url.split("//")[1].split(".")[0]
            realtime_url = f"wss://{supabase_id}.supabase.co/realtime/v1/websocket"

            self.realtime_client = AsyncRealtimeClient(
                realtime_url, config.supabase_key
            )

            # Setup default chat channel
            await self._setup_chat_channel("main-room")

            await self.realtime_client.connect()
            print("[INFO] Supabase Realtime initialized")

        except Exception as e:
            print(f"[ERROR] Failed to setup Realtime: {e}")

    async def _setup_chat_channel(self, channel_name: str):
        """Setup a chat channel for agent communication"""
        try:
            if not self.realtime_client:
                return

            channel = self.realtime_client.channel(f"realtime:public:{channel_name}")

            def on_message(payload):
                msg = payload.get("new", {})
                asyncio.create_task(self._handle_chat_message(msg, channel_name))

            await channel.subscribe()
            channel.on_postgres_changes(
                event="INSERT", schema="public", table="messages", callback=on_message
            )

            self.chat_channels[channel_name] = channel
            print(f"[INFO] Chat channel '{channel_name}' setup complete")

        except Exception as e:
            print(f"[ERROR] Failed to setup chat channel {channel_name}: {e}")

    async def _handle_chat_message(self, message: Dict[str, Any], channel: str):
        """Handle incoming chat messages and route to appropriate agents"""
        try:
            text = message.get("text", "")
            user = message.get("user", "unknown")

            # Check if any agent is being called
            for agent in self.agents.values():
                call_word = agent.config.get("call_word", f"@{agent.agent_id}")
                if call_word in text:
                    print(f"[INFO] Agent {agent.agent_id} called by {user}: {text}")

                    # Create text frame and process through agent
                    text_frame = TextFrame(text=text.replace(call_word, "").strip())
                    response_frame = await agent.process_frame(text_frame)

                    if response_frame:
                        await self._send_chat_response(response_frame, channel, agent)

        except Exception as e:
            print(f"[ERROR] Failed to handle chat message: {e}")

    async def _send_chat_response(
        self, frame: Frame, channel: str, agent: AgentInstance
    ):
        """Send agent response back to chat"""
        try:
            if isinstance(frame, TextFrame):
                # Send text response to Supabase
                response_data = {
                    "text": frame.text,
                    "user": agent.config.get("name", agent.agent_id),
                    "avatar_url": agent.config.get("avatar_url", ""),
                    "agent_id": agent.agent_id,
                    "channel": channel,
                }

                # Insert into messages table
                if self.supabase_client:
                    result = (
                        self.supabase_client.table("messages")
                        .insert(response_data)
                        .execute()
                    )
                    print(f"[INFO] Response sent to chat: {frame.text[:50]}...")

        except Exception as e:
            print(f"[ERROR] Failed to send chat response: {e}")

    async def spawn_agent(self, agent_type: str, agent_config: Dict[str, Any]) -> str:
        """Spawn a new agent instance"""
        if len(self.agents) >= config.max_agents:
            raise HTTPException(status_code=429, detail="Maximum agents reached")

        agent_id = f"{agent_type}_{len(self.agents) + 1}"
        agent = AgentInstance(
            agent_id, 
            agent_type, 
            agent_config,
            llm_registry_service=self.llm_registry_service,
            litellm_router=self.litellm_router
        )

        await agent.start()
        self.agents[agent_id] = agent

        # Register with agent registry
        await self._register_agent(agent)

        return agent_id

    async def stop_agent(self, agent_id: str):
        """Stop and remove an agent instance"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.stop()

            # Deregister from agent registry
            await self._deregister_agent(agent)

            del self.agents[agent_id]

    async def _register_agent(self, agent: AgentInstance):
        """Register agent with the registry"""
        try:
            async with httpx.AsyncClient() as client:
                registration_data = {
                    "agent_id": agent.agent_id,
                    "name": agent.config.get("name", f"Pipecat {agent.agent_type}"),
                    "agent_type": agent.agent_type,
                    "status": agent.status,
                    "endpoint": f"ws://pipecat:{config.websocket_port}/ws/{agent.agent_id}",
                    "capabilities": agent.capabilities,
                    "config": {
                        **agent.config,
                        "multimodal": "webrtc" in agent.capabilities,
                        "realtime_chat": True,
                        "a2a_enabled": a2a_available,
                    },
                    "metadata": {
                        "transport_types": ["websocket", "webrtc"]
                        if "webrtc" in agent.capabilities
                        else ["websocket"],
                        "supported_modalities": [
                            cap
                            for cap in agent.capabilities
                            if cap in ["text", "audio", "video", "image"]
                        ],
                        "chat_integration": True,
                        "created_at": asyncio.get_event_loop().time(),
                    },
                }

                response = await client.post(
                    f"{config.agent_registry_url}", json=registration_data
                )

                if response.status_code == 200:
                    print(f"[INFO] Agent {agent.agent_id} registered with registry")
                else:
                    print(
                        f"[WARNING] Agent registration returned {response.status_code}: {response.text}"
                    )

        except Exception as e:
            print(f"[ERROR] Failed to register agent {agent.agent_id}: {e}")

    async def _deregister_agent(self, agent: AgentInstance):
        """Deregister agent from the registry"""
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{config.agent_registry_url}/{agent.agent_id}")
                print(f"[INFO] Agent {agent.agent_id} deregistered from registry")
        except Exception as e:
            print(f"[ERROR] Failed to deregister agent {agent.agent_id}: {e}")


# Global orchestrator instance
orchestrator = PipecatOrchestrator()

# Simple in-memory task store for A2A RPC
tasks_store: Dict[str, Task] = {}

# FastAPI app
app = FastAPI(title="PMOVES Core Pipecat Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Models
class SpawnAgentRequest(BaseModel):
    agent_type: str
    config: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    agent_id: str
    agent_type: str
    status: str
    capabilities: List[str]
    config: Dict[str, Any]


class ChatMessageRequest(BaseModel):
    channel: str
    text: str
    user: str


# API Endpoints
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "pmoves-pipecat-core",
        "agents_count": len(orchestrator.agents),
        "max_agents": config.max_agents,
        "litellm_router_available": orchestrator.litellm_router is not None,
        "llm_registry_service_available": orchestrator.llm_registry_service is not None,
        "supabase_available": orchestrator.supabase_client is not None,
        "realtime_available": orchestrator.realtime_client is not None,
        "a2a_available": a2a_available,
        "webrtc_available": bool(config.daily_api_key),
        "multimodal_capabilities": {
            "tts": bool(config.elevenlabs_api_key),
            "stt": bool(config.deepgram_api_key),
            "webrtc": bool(config.daily_api_key),
        },
    }


@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    return [
        AgentResponse(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            status=agent.status,
            capabilities=agent.capabilities,
            config=agent.config,
        )
        for agent in orchestrator.agents.values()
    ]


@app.post("/agents/spawn", response_model=AgentResponse)
async def spawn_agent(request: SpawnAgentRequest):
    agent_id = await orchestrator.spawn_agent(request.agent_type, request.config)
    agent = orchestrator.agents[agent_id]

    return AgentResponse(
        agent_id=agent.agent_id,
        agent_type=agent.agent_type,
        status=agent.status,
        capabilities=agent.capabilities,
        config=agent.config,
    )


@app.delete("/agents/{agent_id}")
async def stop_agent(agent_id: str):
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    await orchestrator.stop_agent(agent_id)
    return {"message": f"Agent {agent_id} stopped"}


@app.post("/chat/send")
async def send_chat_message(request: ChatMessageRequest):
    """Send a message to a chat channel"""
    try:
        if orchestrator.supabase_client:
            message_data = {
                "text": request.text,
                "user": request.user,
                "channel": request.channel,
            }

            result = (
                orchestrator.supabase_client.table("messages")
                .insert(message_data)
                .execute()
            )
            return {
                "status": "sent",
                "message_id": result.data[0]["id"] if result.data else None,
            }
        else:
            raise HTTPException(status_code=503, detail="Supabase not available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")


@app.get("/models")
async def list_models():
    """List available models from LiteLLM (via Router or direct proxy call if router not specific)"""
    if orchestrator.litellm_router and orchestrator.litellm_router.get_model_names:
        # This gets model names known to the router instance
        # Note: get_model_names() might not be an async method.
        # Also, this returns aliases, not necessarily full model info.
        # For full info as provided by /models endpoint of proxy, direct call is better.
        # return {"router_models": orchestrator.litellm_router.get_model_names()}
        pass # Fall through to direct proxy call for more complete info for now

    # Fallback or preferred method: query the LiteLLM proxy's /models endpoint
    if not config.litellm_proxy_url:
        raise HTTPException(status_code=503, detail="LiteLLM proxy URL not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # Preferentially use the router's /models endpoint if it has one,
            # or the general proxy /models endpoint.
            # For now, directly query the proxy as before.
            models_url = f"{config.litellm_proxy_url.rstrip('/')}/models"
            response = await client.get(models_url)
            response.raise_for_status() # Raise an exception for bad status codes
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to LiteLLM proxy: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from LiteLLM proxy: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


# WebSocket endpoint for agent communication
@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await websocket.accept()

    if agent_id not in orchestrator.agents:
        await websocket.close(code=4004, reason="Agent not found")
        return

    agent = orchestrator.agents[agent_id]
    agent.websocket_connections.append(websocket)

    try:
        while True:
            # Handle WebSocket communication for the agent
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                frame_type = message.get("type", "text")

                # Create appropriate frame based on type
                if frame_type == "text":
                    frame = TextFrame(text=message.get("text", ""))
                elif frame_type == "audio":
                    frame = AudioFrame(audio=message.get("audio", b""))
                elif frame_type == "image":
                    frame = ImageFrame(image=message.get("image", b""))
                else:
                    frame = TextFrame(text=data)

                # Process through agent pipeline
                response_frame = await agent.process_frame(frame) # Ensure this is awaited

                if response_frame and isinstance(response_frame, TextFrame):
                    response_data = {
                        "type": "text", # We expect TextFrame back
                        "agent_id": agent_id,
                        "data": response_frame.text,
                    }
                    await websocket.send_text(json.dumps(response_data))
                elif response_frame: # Some other frame type, or error frame
                     response_data = {
                        "type": response_frame.__class__.__name__.lower().replace("frame",""),
                        "agent_id": agent_id,
                        "data": response_frame.text if hasattr(response_frame, "text") else "Error: Non-text response or error processing frame",
                     }
                     await websocket.send_text(json.dumps(response_data))
                else: # No response_frame
                    response_data = {
                        "type": "error",
                        "agent_id": agent_id,
                        "data": "Error: No response from agent processing",
                    }
                    await websocket.send_text(json.dumps(response_data))


            except json.JSONDecodeError:
                # Handle plain text if JSON decoding fails
                frame = TextFrame(text=data)
                response_frame = await agent.process_frame(frame) # Ensure this is awaited

                if response_frame and isinstance(response_frame, TextFrame):
                    # For plain text, we can send back a simpler response or wrap it like JSON
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "agent_id": agent_id,
                        "data": response_frame.text
                    }))
                elif response_frame:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "agent_id": agent_id,
                        "data": response_frame.text if hasattr(response_frame, "text") else "Error: Non-text response or error processing frame"
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "agent_id": agent_id,
                        "data": f"Agent {agent_id} processed plain text but no TextFrame response."
                    }))


    except WebSocketDisconnect:
        print(f"[INFO] WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        print(f"[ERROR] WebSocket error for agent {agent_id}: {e}")
    finally:
        if websocket in agent.websocket_connections:
            agent.websocket_connections.remove(websocket)
        await websocket.close()


# A2A Protocol endpoints (if available)
if a2a_available:

    @app.get("/.well-known/agent.json")
    async def well_known_agent() -> Dict[str, Any]:
        """Serve a minimal AgentCard for discovery."""
        card = AgentCard(
            name="PMOVES Pipecat",
            description="Pipecat core service",
            url=f"http://pipecat:{config.service_port}/a2a/rpc",
            version="0.1",
            capabilities=AgentCapabilities(),
            skills=[AgentSkill(id="chat", name="Text chat")],
        )
        return card.model_dump(exclude_none=True)

    @app.post("/a2a/rpc")
    async def a2a_rpc(request: Dict[str, Any]):
        """Handle basic A2A JSON-RPC requests."""
        try:
            rpc = JSONRPCRequest.model_validate(request)
        except Exception as exc:
            return JSONRPCResponse(id=None, error={"code": -32600, "message": str(exc)}).model_dump()

        if rpc.method == "tasks/send":
            send_req = TaskSendRequest.model_validate(request)
            msg: Message = send_req.params.message
            if not msg.parts or msg.parts[0].type != "text":
                return JSONRPCResponse(id=rpc.id, error={"code": -32602, "message": "Only text supported"}).model_dump()

            agent_id = send_req.params.metadata.get("agent_id") if send_req.params.metadata else None
            if not agent_id or agent_id not in orchestrator.agents:
                return JSONRPCResponse(id=rpc.id, error={"code": -32602, "message": "Invalid agent_id"}).model_dump()

            agent = orchestrator.agents[agent_id]
            frame = TextFrame(text=msg.parts[0].text)
            response_frame = await agent.process_frame(frame)
            resp_text = response_frame.text if isinstance(response_frame, TextFrame) else ""

            task = Task(
                id=send_req.params.id,
                status=TaskStatus(
                    state=TaskState.COMPLETED,
                    message=Message(role="agent", parts=[TextPart(text=resp_text)]),
                ),
                metadata=send_req.params.metadata,
            )
            tasks_store[task.id] = task
            return JSONRPCResponse(id=rpc.id, result=task.model_dump()).model_dump()

        elif rpc.method == "tasks/get":
            get_req = TaskGetRequest.model_validate(request)
            task = tasks_store.get(get_req.params.id)
            if not task:
                return JSONRPCResponse(id=rpc.id, error={"code": -32001, "message": "Task not found"}).model_dump()
            return JSONRPCResponse(id=rpc.id, result=task.model_dump()).model_dump()

        else:
            return JSONRPCResponse(id=rpc.id, error={"code": -32601, "message": "Method not found"}).model_dump()


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup"""
    await orchestrator.initialize()
    print(f"[INFO] PMOVES Core Pipecat Service started on port {config.service_port}")
    print(f"[INFO] WebRTC available: {bool(config.daily_api_key)}")
    print(
        f"[INFO] Multimodal capabilities: TTS={bool(config.elevenlabs_api_key)}, STT={bool(config.deepgram_api_key)}"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    # Stop all agents
    for agent_id in list(orchestrator.agents.keys()):
        await orchestrator.stop_agent(agent_id)

    # Disconnect from Realtime
    if orchestrator.realtime_client:
        await orchestrator.realtime_client.disconnect()

    print("[INFO] PMOVES Core Pipecat Service shutdown")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.service_port, reload=False)
