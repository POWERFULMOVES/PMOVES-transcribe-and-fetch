"""
PMOVES Pipecat Agent Client

This is a lightweight agent client that:
- Connects to the core Pipecat service for orchestration
- Handles specific agent types (Supabase, Transcribe, etc.)
- Communicates via WebSocket with the core service
- Registers itself for discovery and A2A communication
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import websockets
from realtime import AsyncRealtimeClient
from security import SecurityMiddleware, SecurityConfig


# Load configuration from environment variables
def load_config():
    return {
        "agent_type": os.getenv("AGENT_TYPE", "supabase"),
        "agent_name": os.getenv("AGENT_NAME", "SupabaseAgent"),
        "pipecat_service_url": os.getenv("PIPECAT_SERVICE_URL", "http://pipecat:8080"),
        "pipecat_ws_url": os.getenv("PIPECAT_WS_URL", "ws://pipecat:8081"),
        "chat_channel": os.getenv("CHAT_CHANNEL", "main-room"),
        "call_word": os.getenv("CALL_WORD", "@SupabaseAgent"),
        "avatar_url": os.getenv(
            "AVATAR_URL", "https://example.com/supabase-agent-avatar.png"
        ),
        "port": int(os.getenv("PORT", "8000")),
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "supabase_key": os.getenv("SUPABASE_KEY", ""),
    }


config = load_config()


class PipecatAgentClient:
    def __init__(self):
        self.agent_id: Optional[str] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.realtime_client: Optional[AsyncRealtimeClient] = None
        self.status = "initializing"
        self.specialized_agent = None

    async def register_with_core_service(self):
        """Register this agent with the core Pipecat service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config['pipecat_service_url']}/agents/spawn",
                    json={
                        "agent_type": config["agent_type"],
                        "config": {
                            "name": config["agent_name"],
                            "chat_channel": config["chat_channel"],
                            "call_word": config["call_word"],
                            "avatar_url": config["avatar_url"],
                            "capabilities": self.get_capabilities(),
                        },
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    self.agent_id = result["agent_id"]
                    self.status = "registered"
                    print(f"[INFO] Agent registered with ID: {self.agent_id}")
                    return True
                else:
                    print(f"[ERROR] Failed to register agent: {response.text}")
                    return False

        except Exception as e:
            print(f"[ERROR] Registration failed: {e}")
            return False

    async def connect_to_core_service(self):
        """Connect to the core Pipecat service via WebSocket"""
        if not self.agent_id:
            print("[ERROR] Cannot connect without agent ID")
            return False

        try:
            ws_url = f"{config['pipecat_ws_url']}/ws/{self.agent_id}"
            self.websocket = await websockets.connect(ws_url)
            self.status = "connected"
            print(f"[INFO] Connected to core service: {ws_url}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to core service: {e}")
            return False

    async def setup_realtime_chat(self):
        """Setup Supabase Realtime for chat communication"""
        if not config["supabase_url"] or not config["supabase_key"]:
            print(
                "[WARNING] Supabase credentials not provided, skipping realtime setup"
            )
            return

        try:
            supabase_id = config["supabase_url"].split("//")[1].split(".")[0]
            realtime_url = f"wss://{supabase_id}.supabase.co/realtime/v1/websocket"

            self.realtime_client = AsyncRealtimeClient(
                realtime_url, config["supabase_key"]
            )
            channel = self.realtime_client.channel(
                f"realtime:public:{config['chat_channel']}"
            )

            def on_message(payload):
                msg = payload.get("new", {})
                text = msg.get("text", "")
                user = msg.get("user", "unknown")

                if config["call_word"] in text:
                    print(f"[INFO] Called by {user}: {text}")
                    asyncio.create_task(self.handle_chat_message(text, user))

            await channel.subscribe()
            channel.on_postgres_changes(
                event="INSERT", schema="public", table="messages", callback=on_message
            )

            await self.realtime_client.connect()
            print(f"[INFO] Connected to chat channel: {config['chat_channel']}")

        except Exception as e:
            print(f"[ERROR] Failed to setup realtime chat: {e}")

    async def handle_chat_message(self, text: str, user: str):
        """Handle incoming chat messages"""
        command = text.split(config["call_word"], 1)[-1].strip()
        response = await self.process_command(command, user)

        # Send response back to chat
        await self.send_chat_response(response, user)

    async def process_command(self, command: str, user: str) -> str:
        """Process agent-specific commands"""
        if not command:
            return f"Hello {user}! I am {config['agent_name']}. Type '{config['call_word']} help' for commands."

        if command.startswith("help"):
            return self.get_help_text()

        if command.startswith("status"):
            return f"Agent {config['agent_name']} is {self.status}. Type: {config['agent_type']}"

        # Agent-type specific commands
        if config["agent_type"] == "supabase":
            return await self.handle_supabase_command(command, user)
        elif config["agent_type"] == "transcribe":
            return await self.handle_transcribe_command(command, user)
        elif config["agent_type"] == "multimodal":
            return await self.handle_multimodal_command(command, user)
        else:
            return f"Unknown command: {command}"

    async def handle_supabase_command(self, command: str, user: str) -> str:
        """Handle Supabase-specific commands"""
        try:
            if not hasattr(self, "specialized_agent") or not self.specialized_agent:
                return "Supabase agent not initialized"

            if command.startswith("search"):
                query = command[len("search") :].strip()
                if not query:
                    return "Please provide a search query. Usage: search <query>"

                from agents.supabase_agent import VectorSearchQuery

                search_request = VectorSearchQuery(query_text=query)
                result = await self.specialized_agent.vector_search(search_request)

                if result["success"]:
                    count = result["count"]
                    return (
                        f"Found {count} results for '{query}'. Top result: {result['data'][0]['content'][:100]}..."
                        if count > 0
                        else f"No results found for '{query}'"
                    )
                else:
                    return f"Search failed: {result['error']}"

            elif command.startswith("query"):
                # Parse query command: query <table> <operation> [filters]
                parts = command[len("query") :].strip().split()
                if len(parts) < 2:
                    return "Usage: query <table> <operation> [filters]"

                table, operation = parts[0], parts[1]
                from agents.supabase_agent import DatabaseQuery

                query_request = DatabaseQuery(table=table, operation=operation)
                result = await self.specialized_agent.execute_query(query_request)

                if result["success"]:
                    return (
                        f"Query executed successfully. Returned {result['count']} rows."
                    )
                else:
                    return f"Query failed: {result['error']}"

            elif command.startswith("upsert"):
                content = command[len("upsert") :].strip()
                if not content:
                    return "Please provide content to upsert. Usage: upsert <content>"

                result = await self.specialized_agent.upsert_content(
                    {"content": content}
                )
                if result["success"]:
                    return f"Content upserted successfully"
                else:
                    return f"Upsert failed: {result['error']}"

            elif command.startswith("health"):
                status = await self.specialized_agent.get_health_status()
                return f"Supabase Agent Status: {status['status']}, Connection: {status.get('supabase_connection', 'unknown')}"

            return f"Supabase command not recognized: {command}. Available: search, query, upsert, health"

        except Exception as e:
            return f"Error handling Supabase command: {str(e)}"

    async def handle_transcribe_command(self, command: str, user: str) -> str:
        """Handle Transcribe-specific commands"""
        try:
            if not hasattr(self, "specialized_agent") or not self.specialized_agent:
                return "Transcribe agent not initialized"

            if command.startswith("transcribe"):
                url = command[len("transcribe") :].strip()
                if not url:
                    return "Please provide a URL to transcribe. Usage: transcribe <url>"

                from agents.transcribe_agent import TranscriptionRequest

                transcribe_request = TranscriptionRequest(audio_url=url)
                result = await self.specialized_agent.transcribe(transcribe_request)

                if result.success:
                    text_preview = (
                        result.full_text[:200] + "..."
                        if len(result.full_text) > 200
                        else result.full_text
                    )
                    return f"Transcription completed using {result.provider}. Text: {text_preview}"
                else:
                    return f"Transcription failed: {result.error}"

            elif command.startswith("providers"):
                status = await self.specialized_agent.get_health_status()
                available = [k for k, v in status["providers"].items() if v]
                return f"Available transcription providers: {', '.join(available)}"

            elif command.startswith("health"):
                status = await self.specialized_agent.get_health_status()
                return f"Transcribe Agent Status: {status['status']}, Providers: {list(status['providers'].keys())}"

            return f"Transcribe command not recognized: {command}. Available: transcribe, providers, health"

        except Exception as e:
            return f"Error handling transcribe command: {str(e)}"

    async def handle_multimodal_command(self, command: str, user: str) -> str:
        """Handle Multimodal-specific commands"""
        try:
            if not hasattr(self, "specialized_agent") or not self.specialized_agent:
                return "Multimodal agent not initialized"

            if command.startswith("analyze"):
                # Parse analyze command: analyze <image_url> <prompt>
                parts = command[len("analyze") :].strip().split(maxsplit=1)
                if len(parts) < 2:
                    return "Usage: analyze <image_url> <prompt>"

                image_url, prompt = parts[0], parts[1]

                from agents.multimodal_agent import VisionRequest

                vision_request = VisionRequest(image_url=image_url, prompt=prompt)
                result = await self.specialized_agent.analyze_vision(vision_request)

                if result.success:
                    content_preview = (
                        result.generated_content[:300] + "..."
                        if len(result.generated_content) > 300
                        else result.generated_content
                    )
                    return f"Vision analysis completed using {result.provider}. Result: {content_preview}"
                else:
                    return f"Vision analysis failed: {result.error}"

            elif command.startswith("generate"):
                # Parse generate command: generate <prompt>
                prompt = command[len("generate") :].strip()
                if not prompt:
                    return "Usage: generate <prompt>"

                from agents.multimodal_agent import ImageGenerationRequest

                gen_request = ImageGenerationRequest(prompt=prompt)
                result = await self.specialized_agent.generate_image(gen_request)

                if result.success:
                    return f"Image generated successfully using {result.provider}. Saved to: {result.file_path}"
                else:
                    return f"Image generation failed: {result.error}"

            elif command.startswith("screenshot"):
                result = await self.specialized_agent.capture_screen()

                if result.success:
                    return f"Screenshot captured successfully. Saved to: {result.file_path}"
                else:
                    return f"Screenshot failed: {result.error}"

            elif command.startswith("providers"):
                status = await self.specialized_agent.get_health_status()
                vision_providers = [
                    k for k, v in status["vision_providers"].items() if v
                ]
                gen_providers = [
                    k for k, v in status["image_gen_providers"].items() if v
                ]
                return f"Vision providers: {', '.join(vision_providers)}. Image gen providers: {', '.join(gen_providers)}"

            elif command.startswith("health"):
                status = await self.specialized_agent.get_health_status()
                return f"Multimodal Agent Status: {status['status']}, Screen capture: {status.get('screen_capture_enabled', False)}"

            return f"Multimodal command not recognized: {command}. Available: analyze, generate, screenshot, providers, health"

        except Exception as e:
            return f"Error handling multimodal command: {str(e)}"

    async def send_chat_response(self, response: str, user: str):
        """Send response back to chat channel"""
        try:
            if self.realtime_client:
                # Send message to Supabase Realtime channel
                channel = self.realtime_client.channel(
                    f"realtime:public:{config['chat_channel']}"
                )

                message_data = {
                    "text": response,
                    "user": config["agent_name"],
                    "user_type": "agent",
                    "reply_to": user,
                    "timestamp": asyncio.get_event_loop().time(),
                    "agent_type": config["agent_type"],
                }

                await channel.send(
                    "broadcast", {"type": "message", "payload": message_data}
                )
                print(f"[RESPONSE to {user}] {response}")
            else:
                # Fallback to console output if realtime not available
                print(f"[RESPONSE to {user}] {response}")

        except Exception as e:
            print(f"[ERROR] Failed to send chat response: {e}")
            # Fallback to console output
            print(f"[RESPONSE to {user}] {response}")

    def get_capabilities(self) -> list:
        """Get agent capabilities based on type"""
        base_capabilities = ["text", "chat"]

        if config["agent_type"] == "supabase":
            return base_capabilities + ["database", "search", "upsert"]
        elif config["agent_type"] == "transcribe":
            return base_capabilities + ["transcription", "audio", "video"]
        elif config["agent_type"] == "multimodal":
            return base_capabilities + [
                "vision",
                "image_generation",
                "screen_capture",
                "multimodal_analysis",
            ]
        else:
            return base_capabilities

    def get_help_text(self) -> str:
        """Get help text based on agent type"""
        if config["agent_type"] == "supabase":
            return f"""Available commands for {config["agent_name"]}:
- help: Show this help
- status: Show agent status  
- search <query>: Search Supabase database
- create table <definition>: Create a new table
- upsert: Start content upsert process"""

        elif config["agent_type"] == "transcribe":
            return f"""Available commands for {config["agent_name"]}:
- help: Show this help
- status: Show agent status
- transcribe <url>: Transcribe audio/video from URL
- providers: List available transcription providers
- health: Show detailed agent health status"""

        elif config["agent_type"] == "multimodal":
            return f"""Available commands for {config["agent_name"]}:
- help: Show this help
- status: Show agent status
- analyze <image_url> <prompt>: Analyze image with AI vision
- generate <prompt>: Generate image from text prompt
- screenshot: Capture screen screenshot
- providers: List available vision and image generation providers
- health: Show detailed agent health status"""

        else:
            return f"Available commands: help, status"

    async def _initialize_specialized_agent(self):
        """Initialize the specialized agent based on agent type"""
        try:
            from agents import create_agent

            # Prepare configuration for specialized agent
            agent_config = {
                "supabase_url": config.get("supabase_url", ""),
                "supabase_key": config.get("supabase_key", ""),
                "groq_api_key": os.getenv("GROQ_API_KEY"),
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "deepgram_api_key": os.getenv("DEEPGRAM_API_KEY"),
                "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
                "backend_url": os.getenv("BACKEND_URL", "http://pmoves-backend:8000"),
                "litellm_url": os.getenv(
                    "LITELLM_PROXY_URL", "http://litellm-proxy:4000"
                ),
            }

            # Create specialized agent
            self.specialized_agent = create_agent(config["agent_type"], agent_config)

            # Initialize the specialized agent
            if hasattr(self.specialized_agent, "initialize"):
                success = await self.specialized_agent.initialize()
                if success:
                    print(
                        f"[INFO] Specialized {config['agent_type']} agent initialized successfully"
                    )
                else:
                    print(
                        f"[WARNING] Failed to initialize specialized {config['agent_type']} agent"
                    )

        except Exception as e:
            print(f"[ERROR] Failed to initialize specialized agent: {e}")
            self.specialized_agent = None

    async def start(self):
        """Start the agent client"""
        print(f"[INFO] Starting {config['agent_name']} ({config['agent_type']})")

        # Initialize specialized agent
        await self._initialize_specialized_agent()

        # Register with core service
        if not await self.register_with_core_service():
            print("[ERROR] Failed to register with core service")
            return False

        # Connect to core service
        if not await self.connect_to_core_service():
            print("[ERROR] Failed to connect to core service")
            return False

        # Setup realtime chat
        await self.setup_realtime_chat()

        self.status = "running"
        print(
            f"[INFO] {config['agent_name']} is running and listening for '{config['call_word']}'"
        )
        return True

    async def stop(self):
        """Stop the agent client"""
        self.status = "stopping"

        # Cleanup specialized agent
        if self.specialized_agent and hasattr(self.specialized_agent, "cleanup"):
            try:
                await self.specialized_agent.cleanup()
                print(f"[INFO] Specialized agent cleaned up")
            except Exception as e:
                print(f"[WARNING] Error cleaning up specialized agent: {e}")

        if self.websocket:
            await self.websocket.close()

        if self.realtime_client:
            await self.realtime_client.disconnect()

        # Deregister from core service
        if self.agent_id:
            try:
                async with httpx.AsyncClient() as client:
                    await client.delete(
                        f"{config['pipecat_service_url']}/agents/{self.agent_id}"
                    )
                print(f"[INFO] Agent {self.agent_id} deregistered")
            except Exception as e:
                print(f"[ERROR] Failed to deregister: {e}")

        self.status = "stopped"
        print(f"[INFO] {config['agent_name']} stopped")


# Global agent client
agent_client = PipecatAgentClient()

# FastAPI app for health checks and status
app = FastAPI(title=f"PMOVES {config['agent_name']}", version="1.0.0")

# Configure security middleware
security_config = SecurityConfig(
    rate_limit_enabled=True,
    rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
    rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600")),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    auth_enabled=bool(os.getenv("AUTH_ENABLED", "true").lower() == "true"),
    api_keys=os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else [],
    jwt_secret=os.getenv("JWT_SECRET", ""),
    max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
    security_headers_enabled=True,
    security_logging_enabled=True,
    log_requests=True,
)

# Add security middleware
security_middleware = SecurityMiddleware(app, security_config)
app.add_middleware(SecurityMiddleware, config=security_config)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": agent_client.status,
        "agent_type": config["agent_type"],
        "agent_name": config["agent_name"],
        "agent_id": agent_client.agent_id,
        "capabilities": agent_client.get_capabilities(),
    }


@app.get("/config")
def get_config():
    return {
        "agent_type": config["agent_type"],
        "agent_name": config["agent_name"],
        "chat_channel": config["chat_channel"],
        "call_word": config["call_word"],
        "avatar_url": config["avatar_url"],
    }


@app.on_event("startup")
async def startup_event():
    """Start the agent client on startup"""
    # Initialize security middleware
    await security_middleware.initialize()

    # Start the agent client
    await agent_client.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the agent client on shutdown"""
    await agent_client.stop()


if __name__ == "__main__":
    uvicorn.run("agent:app", host="0.0.0.0", port=config["port"], reload=False)
