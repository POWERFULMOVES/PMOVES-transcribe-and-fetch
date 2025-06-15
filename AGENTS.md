# Development Guidelines

This repository contains multiple services for the PMOVES project. When making changes, keep these notes in mind:

- **Key documentation**
  - `masterplan/PMOVES_AGENT_PLATFORM_PLAN.md` – master plan for the agent platform.
  - `PIPECAT_ARCHITECTURE.md` – overview of Pipecat architecture.
  - `docs/pipecatdocs/` – reference documentation for Pipecat components.
  - `pmoves-pipecat/main.py` – core service implementation used by Pipecat.
  - `pmoves-pipecat-agent/minimal_agent.py` – example agent for Supabase Realtime.
- **Testing**
  - Run `pytest -q` from the repository root after modifying Python code or documentation.
- **Pull Requests**
  - Summaries should mention affected components and any new capabilities.

