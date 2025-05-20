import os
import asyncio
from fastapi import FastAPI
from threading import Thread
from realtime import AsyncRealtimeClient
from model_registry import get_model_capabilities
from agent_registry import register_agent
import yaml
# Placeholder imports for Pipecat and Supabase Realtime Python SDK
# from pipecat import Pipeline, Frame
# from supabase_py import create_client

try:
    import mcp_tools
except ImportError:
    mcp_tools = None
    print("[WARN] MCP tools not installed. MCP integration will be skipped.")

try:
    import agent2agent_protocol as a2a
except ImportError:
    a2a = None
    print("[WARN] A2A protocol not installed. A2A integration will be skipped.")

# --- Load YAML config ---
def load_config(path=".env.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# --- CONFIG from YAML ---
supabase_cfg = config.get("supabase", {})
litellm_cfg = config.get("litellm", {})
pipecat_cfg = config.get("pipecat", {})

SUPABASE_ID = supabase_cfg.get("id", "your-project-id")
SUPABASE_KEY = supabase_cfg.get("key", "your-anon-or-service-key")
CHAT_CHANNEL = pipecat_cfg.get("chat_channel", "main-room")
CALL_WORD = pipecat_cfg.get("call_word", "@SupabaseAgent")
AVATAR_URL = pipecat_cfg.get("avatar_url", "https://example.com/supabase-agent-avatar.png")
AGENT_NAME = pipecat_cfg.get("agent_name", "SupabaseAgent")
AGENT_ENDPOINT = pipecat_cfg.get("endpoint", "http://localhost:8001")
PIPECAT_MODEL = pipecat_cfg.get("model", "openai/gpt-4o")
LITELLM_PROXY_URL = litellm_cfg.get("proxy_url", "http://litellm-proxy:4000")

# --- Model-Aware Metadata ---
model_capabilities = get_model_capabilities()
agent_metadata = {
    "name": AGENT_NAME,
    "avatar": AVATAR_URL,
    "endpoint": AGENT_ENDPOINT,
    "features": model_capabilities,
    # Add more fields as needed (status, description, etc.)
}

# --- Register Agent ---
registration_result = register_agent(agent_metadata)
print(f"[SupabaseAgent] Registration result: {registration_result}")

# --- MCP Agent Registration Example ---
def register_with_mcp(agent_metadata):
    if not mcp_tools:
        print("[INFO] MCP tools not available, skipping MCP registration.")
        return None
    # Example: Register agent with MCP registry
    try:
        registry = mcp_tools.AgentRegistry()
        result = registry.register_agent(agent_metadata)
        print(f"[MCP] Registered agent: {result}")
        return result
    except Exception as e:
        print(f"[MCP] Registration failed: {e}")
        return None

# --- A2A Message Handler Example ---
def handle_a2a_message(message):
    if not a2a:
        print("[A2A] Protocol not available, skipping A2A message handling.")
        return
    # Example: Parse and respond to A2A message
    try:
        parsed = a2a.parse_message(message)
        print(f"[A2A] Received message: {parsed}")
        # Respond or route as needed
    except Exception as e:
        print(f"[A2A] Error handling message: {e}")

# --- MCP Status Update Stub ---
def update_mcp_status(agent_id, status):
    if not mcp_tools:
        return
    try:
        registry = mcp_tools.AgentRegistry()
        registry.update_status(agent_id, status)
        print(f"[MCP] Updated status for {agent_id} to {status}")
    except Exception as e:
        print(f"[MCP] Status update failed: {e}")

# --- PLACEHOLDER: Connect to Supabase Realtime ---
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# channel = supabase.realtime.subscribe(CHAT_CHANNEL)

print(f"[SupabaseAgent] Listening on channel '{CHAT_CHANNEL}' for call word '{CALL_WORD}'...")

# --- Main message handler ---
def on_message(msg):
    text = msg.get('text', '')
    user = msg.get('user', 'unknown')
    print(f"[SupabaseAgent] Received message from {user}: {text}")
    if CALL_WORD in text:
        command = text.split(CALL_WORD, 1)[-1].strip()
        response = handle_command(command, user)
        # TODO: Send response to Supabase Realtime channel, include AVATAR_URL
        print(f"[SupabaseAgent] Responding: {response}")

# --- Command parser/handler ---
def handle_command(command, user):
    if not command:
        return f"Hello {user}! I am SupabaseAgent. Type '@SupabaseAgent help' for commands."
    if command.startswith('help'):
        return "Available commands: help, echo <text>, (TODO: create table, search, etc.)"
    if command.startswith('echo'):
        return command[len('echo'):].strip()
    # TODO: Add Supabase commands (create table, search, etc.)
    return f"Sorry {user}, I didn't understand that command. Type 'help' for options."

# --- FastAPI app for health check and future endpoints ---
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Supabase Realtime Listener ---
REALTIME_URL = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket"

async def listen_to_realtime():
    client = AsyncRealtimeClient(REALTIME_URL, SUPABASE_KEY)
    channel = client.channel("realtime:public:messages")

    def on_insert(payload):
        msg = payload["new"]
        print(f"[SupabaseAgent] Realtime message: {msg}")
        on_message(msg)  # Call your main handler

    await channel.subscribe()
    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="messages",
        callback=on_insert,
    )
    await client.connect()
    await client.listen()

# --- Run FastAPI and Realtime listener together ---
def start_realtime_listener():
    asyncio.run(listen_to_realtime())

if __name__ == "__main__":
    # Start the Realtime listener in a background thread
    Thread(target=start_realtime_listener, daemon=True).start()
    # Start FastAPI app (for health check and future endpoints)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO:
# - Integrate with real Supabase Realtime SDK for message send/receive
# - Dynamically update agent features/metadata if model/provider changes
# - Add agent discovery/status update logic
# - Implement Supabase command execution (create/search/etc.)
# - Add multimodal (audio/image) support via Pipecat pipeline
# - Add agent-to-agent collaboration 