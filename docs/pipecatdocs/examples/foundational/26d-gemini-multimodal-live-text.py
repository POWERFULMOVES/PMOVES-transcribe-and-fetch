#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import argparse
import os
import asyncio
import uuid
import httpx
from datetime import datetime, timezone

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.gemini_multimodal_live.gemini import (
    GeminiMultimodalLiveLLMService,
    GeminiMultimodalModalities,
    InputParams,
)
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.network.small_webrtc import SmallWebRTCTransport
from pipecat.transports.network.webrtc_connection import SmallWebRTCConnection

load_dotenv(override=True)

# --- Agent Registration and Heartbeat Configuration ---
# In a real system, AGENT_REGISTRY_URL and AGENT_ID might come from environment variables or a config file
AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL", "http://localhost:8000/api") # Default registry URL
AGENT_ID_FILE = ".agent_id"

def get_or_create_agent_id():
    """Gets the agent ID from a file or creates a new one."""
    if os.path.exists(AGENT_ID_FILE):
        with open(AGENT_ID_FILE, "r") as f:
            agent_id = f.read().strip()
            if agent_id:
                logger.info(f"Using existing agent ID: {agent_id}")
                return agent_id
    # Create a new ID if file doesn't exist or is empty
    agent_id = str(uuid.uuid4())
    with open(AGENT_ID_FILE, "w") as f:
        f.write(agent_id)
    logger.info(f"Created new agent ID: {agent_id}")
    return agent_id

AGENT_ID = get_or_create_agent_id()

# --- Agent Registry API Interaction ---
async def register_agent():
    """Registers the agent with the Agent Registry."""
    registry_url = f"{AGENT_REGISTRY_URL}/agents/register"
    agent_metadata = {
        "agent_id": AGENT_ID,
        "name": "Minimal Text Agent", # Agent's human-readable name
        "description": "A minimal Pipecat text agent for testing registration.", # Description
        "capabilities": ["chat_completion", "text_generation"], # Capabilities (based on expected LLM usage)
        "input_schema": {}, # Define input schema if applicable
        "output_schema": {}, # Define output schema if applicable
        "status": "active",
        # Using a placeholder endpoint for this minimal example
        "endpoint": "http://localhost:your-agent-port",
        "dependencies": [], # Dependencies
        "version": "1.0.0", # Agent version
        "tags": ["minimal", "pipecat", "text"], # Tags
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "config": {} # Optional: agent-specific configuration
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(registry_url, json=agent_metadata)
            response.raise_for_status()
            logger.info(f"Agent {AGENT_ID} registered successfully.")
    except httpx.RequestError as e:
        logger.error(f"Error registering agent {AGENT_ID}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during agent registration {AGENT_ID}: {e}")

async def send_heartbeat():
    """Sends a heartbeat to the Agent Registry."""
    registry_url = f"{AGENT_REGISTRY_URL}/agents/heartbeat"
    heartbeat_payload = {
        "agent_id": AGENT_ID,
        "status": "active", # Report current status
        "last_heartbeat": datetime.now(timezone.utc).isoformat()
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(registry_url, json=heartbeat_payload)
            response.raise_for_status()
            # logger.debug(f"Heartbeat sent for agent {AGENT_ID}.") # Log heartbeats less verbosely
    except httpx.RequestError as e:
        logger.error(f"Error sending heartbeat for agent {AGENT_ID}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during heartbeat for agent {AGENT_ID}: {e}")

async def heartbeat_task(interval_seconds: int = 30):
    """Periodically sends heartbeats to the Agent Registry."""
    while True:
        await send_heartbeat()
        await asyncio.sleep(interval_seconds)

SYSTEM_INSTRUCTION = f"""
"You are Gemini Chatbot, a friendly, helpful robot.

Your goal is to demonstrate your capabilities in a succinct way.

Your output will be converted to audio so don't include special characters in your answers.

Respond to what the user said in a creative and helpful way. Keep your responses brief. One or two sentences at most.
"""


async def run_bot(webrtc_connection: SmallWebRTCConnection, _: argparse.Namespace):
    logger.info(f"Starting bot")

    # Register agent on startup
    asyncio.create_task(register_agent())

    # Start the heartbeat task
    heartbeat_interval = int(os.getenv("AGENT_HEARTBEAT_INTERVAL", 30)) # Get interval from env or default
    heartbeat_task_instance = asyncio.create_task(heartbeat_task(heartbeat_interval))

    # Initialize the SmallWebRTCTransport with the connection
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            # set stop_secs to something roughly similar to the internal setting
            # of the Multimodal Live api, just to align events. This doesn't really
            # matter because we can only use the Multimodal Live API's phrase
            # endpointing, for now.
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.5)),
        ),
    )

    llm = GeminiMultimodalLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        transcribe_user_audio=True,
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[{"google_search": {}}, {"code_execution": {}}],
        params=InputParams(modalities=GeminiMultimodalModalities.TEXT),
    )

    # Optionally, you can set the response modalities via a function
    # llm.set_model_modalities(
    #     GeminiMultimodalModalities.TEXT
    # )

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"), voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"
    )

    messages = [
        {
            "role": "user",
            "content": 'Start by saying "Hello, I\'m Gemini".',
        },
    ]

    # Set up conversation context and management
    # The context_aggregator will automatically collect conversation context
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        # Kick off the conversation.
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")

    @transport.event_handler("on_client_closed")
    async def on_client_closed(transport, client):
        logger.info(f"Client closed connection")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)

    # Cancel the heartbeat task when the main task finishes
    heartbeat_task_instance.cancel()
    try:
        await heartbeat_task_instance
    except asyncio.CancelledError:
        logger.info("Heartbeat task cancelled.")


if __name__ == "__main__":
    from run import main

    main()
