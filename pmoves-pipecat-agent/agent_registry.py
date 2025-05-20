"""
agent_registry.py

Handles agent registration, updates, and discovery with the orchestrator/registry.
Supports A2A protocol or REST API for interoperability and dynamic agent management.
"""

import requests  # For REST API example; replace with A2A SDK if needed

# TODO: Set orchestrator/registry endpoint (could be discovered dynamically)
REGISTRY_URL = "http://localhost:8001/agents"  # Example REST endpoint


def register_agent(metadata: dict):
    """
    Registers the agent with the orchestrator/registry.
    metadata: dict with keys like name, avatar, endpoint, features, etc.
    Returns the registry response or agent ID.
    """
    # TODO: Use A2A protocol if available, otherwise fallback to REST
    try:
        response = requests.post(REGISTRY_URL, json=metadata)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[AgentRegistry] Registration failed: {e}")
        return None


def update_agent(metadata: dict):
    """
    Updates the agent's metadata in the registry.
    metadata: dict with updated fields.
    """
    # TODO: Use A2A protocol or PATCH/PUT as appropriate
    try:
        response = requests.put(REGISTRY_URL, json=metadata)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[AgentRegistry] Update failed: {e}")
        return None

# TODO: Add agent discovery, status update, and A2A protocol support 