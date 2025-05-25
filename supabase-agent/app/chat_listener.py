import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from supabase import Client

# Fix the import - PostgrestAPIError is typically in postgrest or directly available
try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    try:
        from supabase.lib.exceptions import PostgrestAPIError
    except ImportError:
        # Fallback - create a generic exception class if the specific one isn't available
        class PostgrestAPIError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)


logger = logging.getLogger(__name__)

# --- Conceptual Database Schema ---
# CREATE TABLE public.chat_messages (
#     id SERIAL PRIMARY KEY,
#     user_id TEXT,
#     session_id TEXT,
#     message_text TEXT NOT NULL,
#     "timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL,
#     status TEXT DEFAULT 'new' NOT NULL, -- 'new', 'processing', 'processed', 'failed'
#     created_at TIMESTAMPTZ DEFAULT NOW(),
#     updated_at TIMESTAMPTZ DEFAULT NOW()
# );
#
# CREATE TABLE public.agent_responses (
#     id SERIAL PRIMARY KEY,
#     chat_message_id INTEGER REFERENCES public.chat_messages(id) ON DELETE SET NULL,
#     response_text TEXT NOT NULL,
#     "timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL,
#     created_at TIMESTAMPTZ DEFAULT NOW()
# );
#
# -- Optional: Trigger to update 'updated_at' on chat_messages
# CREATE OR REPLACE FUNCTION trigger_set_timestamp()
# RETURNS TRIGGER AS $$
# BEGIN
#   NEW.updated_at = NOW();
#   RETURN NEW;
# END;
# $$ LANGUAGE plpgsql;
#
# CREATE TRIGGER set_chat_messages_timestamp
# BEFORE UPDATE ON public.chat_messages
# FOR EACH ROW
# EXECUTE PROCEDURE trigger_set_timestamp();
# --- End Conceptual Database Schema ---

# Note on Supabase Realtime:
# For a more efficient system, Supabase Realtime could be used instead of polling.
# This would involve setting up a WebSocket listener for changes on the 'chat_messages' table.
# `supabase-py` v2.x has some Realtime capabilities, but polling is implemented here for simplicity.


class ChatMessageListener:
    def __init__(
        self,
        supabase_client: Client,
        agent_framework_instance,  # Add AgentFramework instance
        input_table_name: str = "chat_messages",
        output_table_name: str = "agent_responses",
        poll_interval_seconds: int = 5,
    ):
        self.supabase_client = supabase_client
        self.agent_framework = agent_framework_instance  # Store AgentFramework
        self.input_table_name = input_table_name
        self.output_table_name = output_table_name
        self.poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._polling_task: Optional[asyncio.Task] = None
        logger.info(
            f"ChatMessageListener initialized for table '{input_table_name}', "
            f"output to '{output_table_name}', polling every {poll_interval_seconds}s."
        )

    async def _process_message_simple(
        self, message_text: str, timestamp: datetime
    ) -> str:
        """Processes message using LLM if available, otherwise echoes."""
        llm_response_text = None
        llm_service = self.agent_framework.get_llm_registry_service()

        if llm_service:
            chat_models = llm_service.get_available_models(
                capability_filter="chat_completion"
            )
            if chat_models:
                # Pick the first available chat model
                # In a real scenario, model selection could be more sophisticated (e.g., based on config, message content)
                selected_model = chat_models[0]
                logger.info(
                    f"Attempting to use LLM '{selected_model.model_id}' for chat response."
                )

                prompt_messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Respond concisely.",
                    },
                    {"role": "user", "content": f"User said: {message_text}"},
                ]
                try:
                    # Example of passing additional kwargs if needed:
                    # completion_kwargs = {"temperature": 0.7, "max_tokens": 150}
                    # llm_response_text = await llm_service.get_chat_completion(
                    #     selected_model.model_id, prompt_messages, **completion_kwargs
                    # )
                    llm_response_text = await llm_service.get_chat_completion(
                        selected_model.model_id, prompt_messages
                    )

                    if llm_response_text:
                        logger.info(
                            f"LLM '{selected_model.model_id}' responded successfully."
                        )
                    else:
                        logger.warning(
                            f"LLM '{selected_model.model_id}' returned no content. Falling back to echo."
                        )
                except Exception as e:
                    logger.error(
                        f"Error during LLM chat completion with '{selected_model.model_id}': {e}",
                        exc_info=True,
                    )
                    llm_response_text = None  # Ensure fallback on error
            else:
                logger.warning(
                    "No chat-capable LLMs found in the registry. Falling back to echo."
                )
        else:
            logger.warning("LLMRegistryService not available. Falling back to echo.")

        if llm_response_text:
            return llm_response_text
        else:
            # Fallback echo response
            return f"Agent (echo): '{message_text}' received at {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}."

    async def _poll_new_messages(self):
        logger.info("Chat message polling loop started.")
        while self._running:
            try:
                # 1. Fetch new messages
                response = (
                    await self.supabase_client.table(self.input_table_name)
                    .select("id, message_text, timestamp, user_id, session_id")
                    .eq("status", "new")
                    .order("timestamp", desc=False)
                    .limit(10)
                    .execute()
                )  # Add limit to avoid processing too many at once

                if response.error:
                    logger.error(
                        f"Error fetching new messages: {response.error.message}"
                    )
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue

                new_messages = response.data
                if not new_messages:
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue

                logger.info(f"Fetched {len(new_messages)} new message(s).")

                for msg in new_messages:
                    message_id = msg["id"]
                    original_message_text = msg["message_text"]
                    original_timestamp_str = msg[
                        "timestamp"
                    ]  # Assuming it's ISO format string

                    try:
                        original_timestamp = datetime.fromisoformat(
                            original_timestamp_str
                        )
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Could not parse timestamp '{original_timestamp_str}' for message {message_id}. Using current time."
                        )
                        original_timestamp = datetime.now(timezone.utc)

                    # 2. Update status to "processing"
                    update_resp = (
                        await self.supabase_client.table(self.input_table_name)
                        .update(
                            {
                                "status": "processing",
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        .eq("id", message_id)
                        .execute()
                    )

                    if update_resp.error:
                        logger.error(
                            f"Error updating message {message_id} to 'processing': {update_resp.error.message}"
                        )
                        continue  # Skip this message, try again next poll

                    # 3. Process the message (simple echo)
                    response_text = await self._process_message_simple(
                        original_message_text, original_timestamp
                    )

                    # 4. Insert response into output_table_name
                    insert_resp_payload = {
                        "chat_message_id": message_id,
                        "response_text": response_text,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    # If output table is the same as input, payload structure would differ (e.g. sender field)
                    # For now, assuming separate agent_responses table.
                    insert_resp = (
                        await self.supabase_client.table(self.output_table_name)
                        .insert(insert_resp_payload)
                        .execute()
                    )

                    if insert_resp.error:
                        logger.error(
                            f"Error inserting agent response for message {message_id}: {insert_resp.error.message}"
                        )
                        # Optionally, revert status of original message to 'new' or set to 'failed_response'
                        await (
                            self.supabase_client.table(self.input_table_name)
                            .update(
                                {
                                    "status": "failed_response_insertion",
                                    "updated_at": datetime.now(
                                        timezone.utc
                                    ).isoformat(),
                                }
                            )
                            .eq("id", message_id)
                            .execute()
                        )
                        continue

                    # 5. Update original message's status to "processed"
                    final_update_resp = (
                        await self.supabase_client.table(self.input_table_name)
                        .update(
                            {
                                "status": "processed",
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        .eq("id", message_id)
                        .execute()
                    )

                    if final_update_resp.error:
                        logger.error(
                            f"Error updating message {message_id} to 'processed': {final_update_resp.error.message}"
                        )
                        # This is less critical as response was already sent.

                    logger.info(
                        f"Successfully processed and responded to message ID {message_id}."
                    )

            except PostgrestAPIError as e:
                logger.error(f"Supabase API error in polling loop: {e.message}")
            except Exception as e:
                logger.error(f"Unexpected error in polling loop: {e}", exc_info=True)

            await asyncio.sleep(self.poll_interval_seconds)
        logger.info("Chat message polling loop stopped.")

    async def start(self):
        if not self._running:
            self._running = True
            self._polling_task = asyncio.create_task(self._poll_new_messages())
            logger.info("ChatMessageListener started.")
        else:
            logger.info("ChatMessageListener is already running.")

    async def stop(self):
        if self._running and self._polling_task:
            self._running = False
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                logger.info("Polling task successfully cancelled.")
            except Exception as e:
                logger.error(
                    f"Error during polling task cancellation: {e}", exc_info=True
                )
            self._polling_task = None
            logger.info("ChatMessageListener stopped.")
        else:
            logger.info("ChatMessageListener is not running or no task to stop.")


# Example usage (for testing, not part of FastAPI app here)
# async def main_test():
#     # Mock Supabase client or configure real one
#     SUPABASE_URL = os.getenv("SUPABASE_URL")
#     SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Service role key for listening/writing
#     if not SUPABASE_URL or not SUPABASE_KEY:
#         print("Supabase URL/Key not found for test.")
#         return
#
#     supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#     listener = ChatMessageListener(supabase_client=supabase)
#     await listener.start()
#     try:
#         while True: # Keep main alive
#             await asyncio.sleep(60)
#     except KeyboardInterrupt:
#         print("Stopping listener...")
#     finally:
#         await listener.stop()

# if __name__ == "__main__":
#     # Configure logging for standalone test
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     # Load env for test (ensure .env is in the right place relative to this file if run directly)
#     # from dotenv import load_dotenv
#     # load_dotenv(dotenv_path='../.env') # Adjust path if needed
#     # import os
#     # from supabase import create_client
#     # asyncio.run(main_test())
