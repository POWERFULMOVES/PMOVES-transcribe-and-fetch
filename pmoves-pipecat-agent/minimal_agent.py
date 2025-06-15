import os
import uuid
import asyncio
import httpx
from realtime import AsyncRealtimeClient

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.frames.frames import TextFrame, LLMMessagesFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.openai.llm import OpenAILLMService

from .message_router import MessageRouter
from datetime import datetime


class OutputCollector(FrameProcessor):
    """Collects TextFrames from the pipeline."""

    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        if isinstance(frame, TextFrame) and direction == FrameDirection.UPSTREAM:
            await self.queue.put(frame)
        await self.push_frame(frame, direction)


class MinimalPipecatAgent:
    """Minimal text-only Pipecat agent for Supabase Realtime chat."""

    def __init__(self):
        self.config = {
            "supabase_url": os.getenv("SUPABASE_URL", ""),
            "supabase_key": os.getenv("SUPABASE_KEY", ""),
            "chat_channel": os.getenv("CHAT_CHANNEL", "main-room"),
            "call_word": os.getenv("CALL_WORD", "@PipecatAgent"),
            "agent_name": os.getenv("AGENT_NAME", "PipecatAgent"),
            "avatar_url": os.getenv("AVATAR_URL", ""),
            "registry_url": os.getenv("AGENT_REGISTRY_URL", "http://localhost:8000"),
            "openai_key": os.getenv("OPENAI_API_KEY", ""),
            "heartbeat_interval": int(os.getenv("HEARTBEAT_INTERVAL", "30")),
            "enable_tracing": os.getenv("ENABLE_TRACING", "false").lower() == "true",
            "conversation_id": os.getenv("CONVERSATION_ID", ""),
        }
        self.agent_id = str(uuid.uuid4())
        self.realtime = None
        self.channel = None
        self.pipeline = None
        self.runner = None
        self.collector = None
        self.router = MessageRouter(self.config["call_word"])

    async def register_agent(self):
        """Register agent with the orchestrator/registry."""
        caps = ["text"]
        if os.getenv("ELEVENLABS_API_KEY") or os.getenv("CARTESIA_API_KEY"):
            caps.append("tts")
        if os.getenv("DEEPGRAM_API_KEY") or os.getenv("ASSEMBLYAI_API_KEY"):
            caps.append("stt")
        if os.getenv("DAILY_API_KEY"):
            caps.append("webrtc")

        data = {
            "agent_id": self.agent_id,
            "name": self.config["agent_name"],
            "description": "Minimal Pipecat text agent",
            "capabilities": caps,
            "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
            "output_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
            "status": "active",
            "endpoint": None,
            "dependencies": [],
            "version": "0.1.0",
            "tags": ["pipecat", "minimal"],
            "config": {"avatar": self.config["avatar_url"], "chat_channel": self.config["chat_channel"]},
        }
        url = self.config["registry_url"].rstrip("/") + "/agents/register"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=data)
                if res.status_code == 200:
                    print(f"[INFO] Registered agent {self.agent_id}")
                else:
                    print(f"[WARN] Registry response {res.status_code}: {res.text}")
        except Exception as exc:
            print(f"[ERROR] Failed to register agent: {exc}")

    async def build_pipeline(self):
        """Create a simple text-only Pipecat pipeline."""
        llm = OpenAILLMService(api_key=self.config["openai_key"])
        self.collector = OutputCollector()
        self.pipeline = Pipeline([llm, self.collector])
        self.runner = PipelineRunner(handle_sigint=False)

    async def connect_realtime(self):
        """Connect to Supabase Realtime and subscribe to chat channel."""
        if not self.config["supabase_url"] or not self.config["supabase_key"]:
            print("[WARN] Supabase credentials missing; chat disabled")
            return
        supabase_id = self.config["supabase_url"].split("//")[1].split(".")[0]
        realtime_url = f"wss://{supabase_id}.supabase.co/realtime/v1/websocket"
        self.realtime = AsyncRealtimeClient(realtime_url, self.config["supabase_key"])
        self.channel = self.realtime.channel(f"realtime:public:{self.config['chat_channel']}")
        self.channel.on_postgres_changes(event="INSERT", schema="public", table="messages", callback=self._on_message)
        await self.channel.subscribe()
        await self.realtime.connect()
        print(f"[INFO] Connected to chat channel {self.config['chat_channel']}")

    async def _on_message(self, payload):
        msg = payload.get("new", {})
        text = msg.get("text", "")
        user = msg.get("user", "user")
        prompt = self.router.extract_prompt(text)
        if not prompt:
            return
        response = await self.process_text(prompt)
        await self.send_chat_response(response, user)

    async def process_text(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        task = PipelineTask(
            self.pipeline,
            params=PipelineParams(),
            enable_tracing=self.config["enable_tracing"],
            conversation_id=self.config["conversation_id"] or self.agent_id,
            additional_span_attributes={"agent_id": self.agent_id},
        )
        await task.queue_frame(LLMMessagesFrame(messages))
        await self.runner.run(task)
        frame = await self.collector.queue.get()
        return frame.text

    async def send_chat_response(self, response: str, user: str):
        if not self.channel:
            print(f"[RESPONSE to {user}] {response}")
            return
        payload = {
            "text": response,
            "user": self.config["agent_name"],
            "avatar_url": self.config["avatar_url"],
            "reply_to": user,
        }
        await self.channel.send("broadcast", {"type": "message", "payload": payload})
        print(f"[RESPONSE to {user}] {response}")

    async def send_heartbeat(self):
        """Send heartbeat to the agent registry."""
        url = self.config["registry_url"].rstrip("/") + "/agents/heartbeat"
        payload = {"agent_id": self.agent_id, "timestamp": datetime.utcnow().isoformat()}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    print(f"[WARN] Heartbeat failed {res.status_code}: {res.text}")
        except Exception as exc:
            print(f"[ERROR] Heartbeat error: {exc}")

    async def heartbeat_loop(self):
        interval = self.config.get("heartbeat_interval", 30)
        while True:
            await self.send_heartbeat()
            await asyncio.sleep(interval)

    async def run(self):
        await self.register_agent()
        await self.build_pipeline()
        await self.connect_realtime()
        heartbeat = asyncio.create_task(self.heartbeat_loop())
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            heartbeat.cancel()
            if self.realtime:
                await self.realtime.disconnect()


if __name__ == "__main__":
    asyncio.run(MinimalPipecatAgent().run())
