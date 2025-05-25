"""
PMOVES Pipecat Agents Package

This package contains specialized agent implementations:
- SupabaseAgent: Database operations and vector search
- TranscribeAgent: Audio/video transcription
- MultimodalAgent: Vision, image generation, and multimodal AI
"""

from .supabase_agent import SupabaseAgent, create_supabase_agent
from .transcribe_agent import TranscribeAgent, create_transcribe_agent
from .multimodal_agent import MultimodalAgent, create_multimodal_agent

__all__ = [
    "SupabaseAgent",
    "TranscribeAgent",
    "MultimodalAgent",
    "create_supabase_agent",
    "create_transcribe_agent",
    "create_multimodal_agent",
]

# Agent factory mapping
AGENT_FACTORIES = {
    "supabase": create_supabase_agent,
    "transcribe": create_transcribe_agent,
    "multimodal": create_multimodal_agent,
}


def create_agent(agent_type: str, config: dict):
    """Factory function to create agents by type"""
    if agent_type not in AGENT_FACTORIES:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return AGENT_FACTORIES[agent_type](config)
