from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class TaskState(str, Enum):
    SUBMITTED = 'submitted'
    COMPLETED = 'completed'
    FAILED = 'failed'

class TextPart(BaseModel):
    type: Literal['text'] = 'text'
    text: str

Part = TextPart

class Message(BaseModel):
    role: Literal['user', 'agent']
    parts: List[Part]

class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None

class Task(BaseModel):
    id: str
    status: TaskStatus
    metadata: Optional[Dict[str, Any]] = None

class JSONRPCRequest(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    method: str
    params: Dict[str, Any]

class JSONRPCResponse(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    id: Optional[str] = None
    result: Any | None = None
    error: Optional[Dict[str, Any]] = None

class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False

class AgentSkill(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class AgentCard(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    version: str
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    skills: List[AgentSkill] = Field(default_factory=list)

class TaskSendParams(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    message: Message
    metadata: Optional[Dict[str, Any]] = None

class TaskGetParams(BaseModel):
    id: str

class TaskSendRequest(JSONRPCRequest):
    method: Literal['tasks/send'] = 'tasks/send'
    params: TaskSendParams

class TaskGetRequest(JSONRPCRequest):
    method: Literal['tasks/get'] = 'tasks/get'
    params: TaskGetParams

