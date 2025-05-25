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
        AudioFrame,
        ImageFrame,
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

    print("[INFO] Pipecat core imports successful")
except ImportError as e:
    print(f"[WARNING] Pipecat imports failed: {e}")

# LiteLLM integration
try:
    import litellm
    from litellm import completion

    print("[INFO] LiteLLM integration available")
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

# A2A protocol (conditional import)
try:
    import agent2agent_protocol as a2a

    print("[INFO] A2A protocol available")
except ImportError:
    a2a = None
    print("[INFO] A2A protocol not available, will use fallback")


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
    def __init__(self, agent_id: str, agent_type: str, agent_config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = agent_config
        self.pipeline: Optional[Pipeline] = None
        self.runner: Optional[PipelineRunner] = None
        self.transport: Optional[Any] = None
        self.websocket_connections: List[WebSocket] = []
        self.status = "initializing"
        self.capabilities = self._determine_capabilities()

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

            # LLM Service (via LiteLLM)
            if litellm:
                # This would be a custom LiteLLM service for Pipecat
                # For now, we'll use OpenAI as fallback
                llm_service = OpenAILLMService(
                    api_key=os.getenv("OPENAI_API_KEY", ""), model="gpt-4o"
                )
                services.append(llm_service)

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

    async def process_frame(self, frame: Frame) -> Optional[Frame]:
        """Process a frame through the agent's pipeline"""
        if self.pipeline and self.runner:
            try:
                # This would be implemented based on Pipecat's frame processing
                return frame
            except Exception as e:
                print(f"[ERROR] Frame processing failed for agent {self.agent_id}: {e}")
        return None


class PipecatOrchestrator:
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.litellm_client = None
        self.supabase_client = None
        self.realtime_client = None
        self.chat_channels: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize the orchestrator"""
        # Initialize LiteLLM client
        if litellm:
            try:
                # Configure LiteLLM to use the proxy
                litellm.api_base = config.litellm_proxy_url
                self.litellm_client = litellm
                print(
                    f"[INFO] LiteLLM client initialized with proxy: {config.litellm_proxy_url}"
                )
            except Exception as e:
                print(f"[ERROR] Failed to initialize LiteLLM client: {e}")

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
        agent = AgentInstance(agent_id, agent_type, agent_config)

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
                        "a2a_enabled": a2a is not None,
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
        "litellm_available": orchestrator.litellm_client is not None,
        "supabase_available": orchestrator.supabase_client is not None,
        "realtime_available": orchestrator.realtime_client is not None,
        "a2a_available": a2a is not None,
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
    """List available models from LiteLLM"""
    if not orchestrator.litellm_client:
        raise HTTPException(status_code=503, detail="LiteLLM not available")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.litellm_proxy_url}/models")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {e}")


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
                response_frame = await agent.process_frame(frame)

                if response_frame:
                    response_data = {
                        "type": response_frame.__class__.__name__.lower().replace(
                            "frame", ""
                        ),
                        "agent_id": agent_id,
                        "data": response_frame.text
                        if hasattr(response_frame, "text")
                        else str(response_frame),
                    }
                    await websocket.send_text(json.dumps(response_data))

            except json.JSONDecodeError:
                # Handle plain text
                frame = TextFrame(text=data)
                response_frame = await agent.process_frame(frame)

                if response_frame:
                    await websocket.send_text(f"Agent {agent_id} processed: {data}")

    except WebSocketDisconnect:
        print(f"[INFO] WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        print(f"[ERROR] WebSocket error for agent {agent_id}: {e}")
    finally:
        if websocket in agent.websocket_connections:
            agent.websocket_connections.remove(websocket)
        await websocket.close()


# A2A Protocol endpoints (if available)
if a2a:

    @app.get("/a2a/discover")
    async def a2a_discover():
        """A2A agent discovery endpoint"""
        return {
            "agents": [
                {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "endpoint": f"ws://pipecat:{config.websocket_port}/ws/{agent.agent_id}",
                    "multimodal": "webrtc" in agent.capabilities,
                    "realtime_chat": True,
                }
                for agent in orchestrator.agents.values()
            ]
        }

    @app.post("/a2a/message/{agent_id}")
    async def a2a_message(agent_id: str, message: Dict[str, Any]):
        """A2A message endpoint"""
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = orchestrator.agents[agent_id]

        # Create frame from A2A message
        frame = TextFrame(text=message.get("content", ""))
        response_frame = await agent.process_frame(frame)

        return {
            "status": "message_processed",
            "agent_id": agent_id,
            "response": response_frame.text
            if response_frame and hasattr(response_frame, "text")
            else None,
        }


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
