import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import httpx

# Configure logging
# Ensure logging is configured only once, ideally at the application entry point.
logger = logging.getLogger(__name__)

# Attempt to import LLMRegistryService related functions
try:
    from .llm_registry_service import initialize_llm_registry, get_llm_registry_service, LLMRegistryService
    llm_service_available = True
except ImportError:
    logger.warning("LLMRegistryService components could not be imported from .llm_registry_service. LLM functionalities will be disabled.")
    llm_service_available = False
    # Define dummy types if not available, so class can still be defined
    class LLMRegistryService: pass


class AgentFramework:
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        status: str, # e.g., "initializing", "active", "inactive"
        registry_url: str,
        heartbeat_interval_seconds: int,
        endpoint: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        llm_registry_url: Optional[str] = None, # URL for the LiteLLM proxy
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.status = status 
        self.endpoint = endpoint
        self.dependencies = dependencies if dependencies is not None else []
        self.version = version
        self.tags = tags if tags is not None else []
        self.config = config

        self.registry_url = registry_url.rstrip('/')
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        
        self.client = httpx.AsyncClient()
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._loop = loop or asyncio.get_event_loop()

        self.llm_registry_url = llm_registry_url
        self._llm_service_instance: Optional[LLMRegistryService] = None

        if llm_service_available and self.llm_registry_url:
            logger.info(f"AgentFramework configured to use LLMRegistryService with proxy URL: {self.llm_registry_url}")
        elif llm_service_available and not self.llm_registry_url:
            logger.info("LLMRegistryService is available but no llm_registry_url provided. LLM features will use default from LLMRegistryService config.")
        else:
            logger.info("LLMRegistryService is not available or not configured. LLM features disabled for this agent.")

        logger.info(f"AgentFramework initialized for agent_id: {self.agent_id}")

    async def start_services(self):
        """Starts services like registration, heartbeats, and initializes LLM Registry if configured."""
        logger.info(f"Agent {self.agent_id} starting services...")
        if await self.register_agent():
            self.start_heartbeat_loop()
        else:
            logger.error(f"Agent {self.agent_id} failed to register. Heartbeat loop not started.")

        if llm_service_available and self.llm_registry_url:
            try:
                await initialize_llm_registry(litellm_proxy_url_override=self.llm_registry_url)
                self._llm_service_instance = get_llm_registry_service()
                logger.info(f"LLMRegistryService initialized successfully for agent {self.agent_id}.")
            except Exception as e:
                logger.error(f"Failed to initialize LLMRegistryService for agent {self.agent_id}: {e}", exc_info=True)
        elif llm_service_available and not self.llm_registry_url: # Use default config from llm_registry_service
             try:
                await initialize_llm_registry() # Initialize with default config
                self._llm_service_instance = get_llm_registry_service()
                logger.info(f"LLMRegistryService initialized successfully with default settings for agent {self.agent_id}.")
             except Exception as e:
                logger.error(f"Failed to initialize LLMRegistryService with default settings for agent {self.agent_id}: {e}", exc_info=True)


    async def register_agent(self) -> bool:
        """Registers the agent with the central registry."""
        registration_payload = {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "status": self.status,
            "endpoint": self.endpoint,
            "dependencies": self.dependencies,
            "version": self.version,
            "tags": self.tags,
            "config": self.config,
            # last_heartbeat is not sent during registration, registry will set it
        }
        register_url = f"{self.registry_url}/register"
        logger.info(f"Attempting to register agent {self.agent_id} at {register_url}")
        try:
            response = await self.client.post(register_url, json=registration_payload, timeout=10.0)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            logger.info(f"Agent {self.agent_id} registered successfully. Response: {response.json()}")
            self.status = "active" # Update status after successful registration
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error registering agent {self.agent_id}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Network error registering agent {self.agent_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error registering agent {self.agent_id}: {e}")
        return False

    async def send_heartbeat(self) -> bool:
        """Sends a heartbeat signal to the registry."""
        heartbeat_payload = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        heartbeat_url = f"{self.registry_url}/heartbeat"
        # logger.debug(f"Sending heartbeat for agent {self.agent_id} to {heartbeat_url}") # Too verbose for INFO
        try:
            response = await self.client.post(heartbeat_url, json=heartbeat_payload, timeout=5.0)
            response.raise_for_status()
            logger.info(f"Heartbeat sent successfully for agent {self.agent_id}.")
            # Update status based on heartbeat success, if needed, or rely on registry
            if self.status != "active":
                self.status = "active" # If it was inactive for some reason and heartbeat is now successful
            return True
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error sending heartbeat for agent {self.agent_id}: {e.response.status_code} - {e.response.text}")
            self.status = "heartbeat_failed" # Indicate a problem
        except httpx.RequestError as e:
            logger.warning(f"Network error sending heartbeat for agent {self.agent_id}: {e}")
            self.status = "heartbeat_failed_network" # Indicate a problem
        except Exception as e:
            logger.error(f"Unexpected error sending heartbeat for agent {self.agent_id}: {e}")
            self.status = "heartbeat_failed_unexpected" # Indicate a problem
        return False

    async def _heartbeat_loop(self):
        """The actual loop that sends heartbeats periodically."""
        logger.info(f"Starting heartbeat loop for agent {self.agent_id} with interval {self.heartbeat_interval_seconds}s.")
        while True:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval_seconds)
            except asyncio.CancelledError:
                logger.info(f"Heartbeat loop for agent {self.agent_id} cancelled.")
                break
            except Exception as e: # Catch-all for unexpected errors within the loop
                logger.error(f"Critical error in heartbeat loop for agent {self.agent_id}: {e}. Restarting loop after delay.")
                await asyncio.sleep(self.heartbeat_interval_seconds) # Wait before retrying loop

    def start_heartbeat_loop(self):
        """Starts the background heartbeat task."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = self._loop.create_task(self._heartbeat_loop())
            logger.info(f"Heartbeat task created for agent {self.agent_id}.")
        else:
            logger.info(f"Heartbeat task for agent {self.agent_id} is already running.")

    async def stop_heartbeat_loop(self):
        """Stops the background heartbeat task."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            logger.info(f"Attempting to cancel heartbeat task for agent {self.agent_id}.")
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                logger.info(f"Heartbeat task for agent {self.agent_id} successfully cancelled.")
            except Exception as e:
                logger.error(f"Error encountered while awaiting cancelled heartbeat task for {self.agent_id}: {e}")
        else:
            logger.info(f"No active heartbeat task to stop for agent {self.agent_id}.")
        
        # Optionally, send a final "deregister" or "inactive" status to the registry
        # This depends on the desired agent lifecycle management
        # For now, we just stop the heartbeats.
        # await self.deregister_agent() # If you implement deregistration

    def get_health(self) -> Dict[str, Any]:
        """Returns the current health status of the agent."""
        return {
            "status": self.status,
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "heartbeat_active": self._heartbeat_task is not None and not self._heartbeat_task.done()
        }

    async def close(self):
        """Gracefully close the httpx client."""
        await self.client.aclose()
        logger.info(f"HTTPX client closed for agent {self.agent_id}.")

# Example of how an agent might use this framework (for testing or illustration)
async def example_usage():
    # This would typically be run within an agent's FastAPI app or service
    agent_config = {
        "agent_id": "test_agent_001",
        "name": "Test Agent",
        "description": "An agent for testing the framework.",
        "capabilities": ["test_capability"],
        "input_schema": {"type": "object", "properties": {"message": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"reply": {"type": "string"}}},
        "status": "initializing", # Initial status
        "endpoint": "http://localhost:8001/invoke", # Agent's own endpoint
        "registry_url": "http://localhost:8008/agents", # PMOVES Agent Registry URL (adjust if different)
        "heartbeat_interval_seconds": 10, # Short interval for testing
    }

    framework = AgentFramework(**agent_config)

    # Simulating application startup
    if await framework.register_agent():
        framework.start_heartbeat_loop()
    else:
        logger.error(f"Agent {framework.agent_id} failed to register. Heartbeat loop not started.")
        await framework.close()
        return

    # Let it run for a bit
    try:
        for i in range(3): # Simulate some time passing
            logger.info(f"Agent {framework.agent_id} health: {framework.get_health()}")
            await asyncio.sleep(agent_config["heartbeat_interval_seconds"])
    finally:
        # Simulating application shutdown
        logger.info(f"Shutting down agent {framework.agent_id}.")
        await framework.stop_heartbeat_loop()
        await framework.close()
        logger.info(f"Agent {framework.agent_id} shutdown complete.")


if __name__ == "__main__":
    # This part is for standalone testing of the framework module.
    # In a real scenario, the AgentFramework would be imported and used by an agent service.
    
    # To run this example, you would need a mock registry service running at http://localhost:8008/agents
    # or change the registry_url to a live one if available.
    
    # For a quick test without a live registry, comment out the actual network calls
    # in register_agent and send_heartbeat, or expect errors.
    
    async def main():
        await example_usage()

    asyncio.run(main())
