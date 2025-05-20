from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgentRegistration(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    status: str
    endpoint: Optional[str] = None
    dependencies: List[str] = []
    version: Optional[str] = None
    tags: List[str] = []
    last_heartbeat: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None

class AgentHeartbeat(BaseModel):
    agent_id: str
    timestamp: datetime

class AgentMetadata(AgentRegistration):
    pass 