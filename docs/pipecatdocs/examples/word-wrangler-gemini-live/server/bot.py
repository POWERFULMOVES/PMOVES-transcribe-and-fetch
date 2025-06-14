#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
import sys
from typing import Any, Dict
import uuid
import httpx
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecatcloud.agent import DailySessionArguments

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.filters.stt_mute_filter import STTMuteConfig, STTMuteFilter, STTMuteStrategy
from pipecat.processors.frameworks.rtvi import (
    RTVIConfig,
    RTVIObserver,
    RTVIProcessor,
)
from pipecat.services.gemini_multimodal_live.gemini import GeminiMultimodalLiveLLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport

# Add LiteLLM imports
import litellm
from pmoves_pipecat.src.pipecat.services.litellm_service import LiteLLMPipecatService

# Import LLMRegistryService and initialize it
from backend.app.utils.llm_registry_service import LLMRegistryService

load_dotenv(override=True)

# Check if we're in local development mode
LOCAL_RUN = os.getenv("LOCAL_RUN")

logger.add(sys.stderr, level="DEBUG")

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
        "name": "Word Wrangler Agent", # Agent's human-readable name
        "description": "A Pipecat agent for the Word Wrangler game using LiteLLM.", # Description
        "capabilities": ["chat_completion", "text_generation"], # Capabilities (based on LLM)
        "input_schema": {}, # Define input schema if applicable
        "output_schema": {}, # Define output schema if applicable
        "status": "active",
        "endpoint": os.getenv("AGENT_ENDPOINT", "http://localhost:8001"), # Agent's accessible endpoint
        "dependencies": ["llm_registry"], # Dependencies
        "version": "1.0.0", # Agent version
        "tags": ["game", "pipecat", "litellm"], # Tags
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "config": { # Optional: agent-specific configuration
            "personality": os.getenv("DEFAULT_PERSONALITY", "witty"),
            "llm_model_alias": os.getenv("DEFAULT_LLM_MODEL_ALIAS", "my-ollama-gemini"),
        }
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

# --- Define conversation modes with their respective prompt templates ---
game_prompt = """You are the AI host and player for a game of Word Wrangler.\n\nGAME RULES:\n1. The user will be given a word or phrase that they must describe to you\n2. The user CANNOT say any part of the word/phrase directly\n3. You must try to guess the word/phrase based on the user's description\n4. Once you guess correctly, the user will move on to their next word\n5. The user is trying to get through as many words as possible in 60 seconds\n6. The external application will handle timing and keeping score\n\nYOUR ROLE:\n1. Start with this exact brief introduction: "Welcome to Word Wrangler! I'll try to guess the words you describe. Remember, don't say any part of the word itself. Ready? Let's go!"\n2. Listen carefully to the user's descriptions\n3. Make intelligent guesses based on what they say\n4. When you think you know the answer, state it clearly: "Is it [your guess]?"\n5. If you're struggling, ask for more specific clues\n6. Keep the game moving quickly - make guesses promptly\n7. Be enthusiastic and encouraging\n\nIMPORTANT:\n- Keep all responses brief - the game is timed!\n- Make multiple guesses if needed\n- Use your common knowledge to make educated guesses\n- If the user indicates you got it right, just say "Got it!" and prepare for the next word\n- If you've made several wrong guesses, simply ask for "Another clue please?"\n\nStart with the exact introduction specified above, then wait for the user to begin describing their first word."""

# Define personality presets
PERSONALITY_PRESETS = {
    "friendly": "You have a warm, approachable personality. You use conversational language, occasional humor, and express enthusiasm for the topic. Make the user feel comfortable and engaged.",
    "professional": "You have a formal, precise personality. You communicate clearly and directly with a focus on accuracy and relevance. Your tone is respectful and business-like.",
    "enthusiastic": "You have an energetic, passionate personality. You express excitement about the topic and use dynamic language. You're encouraging and positive throughout the conversation.",
    "thoughtful": "You have a reflective, philosophical personality. You speak carefully, considering multiple angles of each point. You ask thought-provoking questions and acknowledge nuance.",
    "witty": "You have a clever, humorous personality. While remaining informative, you inject appropriate wit and playful language. Your goal is to be engaging and entertaining while still being helpful.",
}


async def main(transport: DailyTransport, config: Dict[str, Any]):
    # Use the provided session logger if available, otherwise use the default logger
    logger.debug("Configuration: {}", config)

    # Extract configuration parameters with defaults
    personality = config.get("personality", "witty")

    personality_prompt = PERSONALITY_PRESETS.get(personality, PERSONALITY_PRESETS["friendly"])

    system_instruction = f"""{game_prompt}

{personality_prompt}

Important guidelines:
1. Your responses will be converted to speech, so keep them concise and conversational.
2. Don't use special characters or formatting that wouldn't be natural in speech.
3. Encourage the user to elaborate when appropriate."""

    intro_message = """Start with this exact brief introduction: "Welcome to Word Wrangler! I'll try to guess the words you describe. Remember, don't say any part of the word itself. Ready? Let's go!"""

    # Create the STT mute filter if we have strategies to apply
    stt_mute_filter = STTMuteFilter(
        config=STTMuteConfig(strategies={STTMuteStrategy.MUTE_UNTIL_FIRST_BOT_COMPLETE})
    )

    # Initialize LLMRegistryService (Assuming it's a singleton or can be initialized here)
    llm_registry = LLMRegistryService() # Initialize your registry service
    # In a real application, you might get this from an app context or similar

    # Replace LiteLLMPipecatService initialization to use the registry
    # llm = LiteLLMPipecatService(litellm_router=litellm_router, model_alias="my-litellm-model")
    # Use the preferred model alias from config or default
    preferred_model_alias = config.get("llm_model_alias", "my-ollama-gemini") # Use a default or get from config
    llm = LiteLLMPipecatService(llm_registry_service=llm_registry, preferred_model_alias=preferred_model_alias)

    # Set up the initial context for the conversation
    messages = [
        {
            "role": "user",
            "content": intro_message,
        },
    ]

    # This sets up the LLM context by providing messages and tools
    # Note: LiteLLMPipecatService expects LLMMessagesFrame

    # RTVI events for Pipecat client UI
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
            stt_mute_filter,
            llm, # Use the LiteLLM service
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.debug("Client ready event received")
        await rtvi.set_bot_ready()
        # Kick off the conversation by pushing initial messages as LLMMessagesFrame
        await task.queue_frames([LLMMessagesFrame(messages=messages)])

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        logger.info("First participant joined: {}", participant["id"])
        # Capture the participant's transcription
        await transport.capture_participant_transcription(participant["id"])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        logger.info("Participant left: {}", participant)
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False, force_gc=True)

    await runner.run(task)


async def bot(args: DailySessionArguments):
    """Main bot entry point compatible with the FastAPI route handler.

    Args:
        room_url: The Daily room URL
        token: The Daily room token
        body: The configuration object from the request body
        session_id: The session ID for logging
    """
    from pipecat.audio.filters.krisp_filter import KrispFilter

    logger.info(f"Bot process initialized {args.room_url} {args.token}")

    transport = DailyTransport(
        args.room_url,
        args.token,
        "Word Wrangler Bot",
        DailyParams(
            audio_in_filter=None if LOCAL_RUN else KrispFilter(),
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    try:
        await main(transport, args.body)
        logger.info("Bot process completed")
    except Exception as e:
        logger.exception(f"Error in bot process: {str(e)}")
        raise


# Local development
async def local_daily():
    """Daily transport for local development."""
    from runner import configure

    try:
        async with aiohttp.ClientSession() as session:
            (room_url, token) = await configure(session)
            transport = DailyTransport(
                room_url,
                token,
                bot_name="Bot",
                params=DailyParams(
                    audio_out_enabled=True,
                    vad_analyzer=SileroVADAnalyzer(),
                ),
            )

            test_config = {
                "personality": "witty",
            }

            await main(transport, test_config)
    except Exception as e:
        logger.exception(f"Error in local development mode: {e}")


# Local development entry point
if LOCAL_RUN and __name__ == "__main__":
    try:
        asyncio.run(local_daily())
    except Exception as e:
        logger.exception(f"Failed to run in local mode: {e}")
