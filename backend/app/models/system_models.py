from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class AppConfigurationBase(BaseModel):
    config_key: str = Field(..., description="Unique key for the configuration, e.g., 'DEFAULT_SEARCH_PARAMS'.")
    config_value: Dict[str, Any] = Field(..., description="JSONB value for the configuration.")
    description: Optional[str] = None

class AppConfigurationCreate(AppConfigurationBase):
    pass

class AppConfiguration(AppConfigurationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentRegistryBase(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the agent.")
    name: str = Field(..., description="User-friendly name for the agent.")
    description: Optional[str] = None
    type: str = Field(..., description="Type of agent, e.g., 'data_fetcher', 'analyzer'.")
    endpoints: Optional[Dict[str, HttpUrl]] = Field(None, description="Agent's API endpoints, e.g., {'process': 'http://...'}")
    capabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Agent capabilities, similar to LLM capabilities.")
    required_config_keys: Optional[List[str]] = Field(None, description="List of config_key from app_configurations needed by this agent.")
    status: str = Field(default='disabled', description="Agent status, e.g., 'active', 'disabled'.")

class AgentRegistryCreate(AgentRegistryBase):
    pass

class AgentRegistry(AgentRegistryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
