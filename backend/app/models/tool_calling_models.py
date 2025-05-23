from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ToolCallStatus(str, Enum):
    PENDING = "PENDING"
    ACCUMULATING = "ACCUMULATING"
    REASSEMBLING = "REASSEMBLING"
    VALIDATING = "VALIDATING"
    ARGUMENTS_COMPLETE = "ARGUMENTS_COMPLETE"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"

ToolSchema = Dict[str, Any]

class ToolCallState(BaseModel):
    tool_call_id: str
    tool_name: str
    tool_schema: ToolSchema
    accumulated_args: Dict[str, Any] = Field(default_factory=dict)
    partial_arg_buffers: Dict[int, str] = Field(default_factory=dict)
    status: ToolCallStatus = ToolCallStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_details: Optional[str] = None
    expected_chunk_count: Optional[int] = None

class InitiateToolCallRequest(BaseModel):
    tool_name: str
    tool_schema: Optional[ToolSchema] = None
    tool_call_id: Optional[str] = None

class SubmitArgumentChunkRequest(BaseModel):
    tool_call_id: str
    chunk_content: str
    sequence_number: int
    is_last_chunk: bool
