from fastapi import FastAPI, HTTPException
from typing import List, Optional # Added Optional
from .schemas import AgentRegistration, AgentMetadata, AgentHeartbeat
from .registry import agent_store
from datetime import datetime

app = FastAPI(title="PMOVES Agent Registry Service")

@app.get("/agents", response_model=List[AgentMetadata])
def list_agents(
    capability: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    tag: Optional[str] = None,
):
    return agent_store.list(
        capability=capability,
        status=status,
        name=name,
        tag=tag
    )

@app.get("/agents/{agent_id}", response_model=AgentMetadata)
def get_agent(agent_id: str):
    agent = agent_store.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/agents/register", response_model=AgentMetadata)
def register_agent(reg: AgentRegistration):
    return agent_store.register(reg)

@app.post("/agents/heartbeat", response_model=AgentMetadata)
def agent_heartbeat(hb: AgentHeartbeat):
    agent = agent_store.heartbeat(hb.agent_id, hb.timestamp)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.delete("/agents/{agent_id}")
def deregister_agent(agent_id: str):
    if not agent_store.deregister(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"detail": "Agent deregistered"} 