from typing import Dict, Optional, List
from .schemas import AgentMetadata, AgentRegistration
from datetime import datetime

class AgentStore:
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}

    def register(self, reg: AgentRegistration) -> AgentMetadata:
        agent = AgentMetadata(**reg.dict())
        self._agents[agent.agent_id] = agent
        return agent

    def get(self, agent_id: str) -> Optional[AgentMetadata]:
        return self._agents.get(agent_id)

    def list(self) -> List[AgentMetadata]:
        return list(self._agents.values())

    def heartbeat(self, agent_id: str, timestamp: datetime) -> Optional[AgentMetadata]:
        agent = self._agents.get(agent_id)
        if agent:
            agent.last_heartbeat = timestamp
            agent.status = "active"
        return agent

    def deregister(self, agent_id: str) -> bool:
        return self._agents.pop(agent_id, None) is not None 