from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class CrawlPresetBase(BaseModel):
    preset_name: str = Field(..., description="Human-readable, unique name for the preset.")
    description: Optional[str] = None
    version: int = 1
    crawl_tool: str = "crawl4ai"
    strategy_definition: Dict[str, Any] = Field(..., description="The core JSON structure defining the crawl strategy and its parameters.")
    target_capability: Optional[str] = None
    tags: Optional[List[str]] = None # Stored as JSONB array in DB, represented as List[str] here
    created_by: Optional[UUID] = Field(None, description="ID of the user creating the preset. To be set by the application based on authenticated user.")


class CrawlPresetCreate(CrawlPresetBase):
    # created_by is now inherited from CrawlPresetBase.
    # If it's mandatory for creation, it should be defined here without Optional.
    # For now, let's assume it can be Optional during creation if systems without auth might create global presets,
    # or it's set by a dependency.
    # Re-evaluating: For user-owned presets, created_by should be mandatory on creation.
    created_by: UUID = Field(..., description="ID of the user creating the preset. Must be provided.")

class CrawlPresetUpdate(BaseModel):
    preset_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[int] = None
    crawl_tool: Optional[str] = None
    strategy_definition: Optional[Dict[str, Any]] = None
    target_capability: Optional[str] = None
    tags: Optional[List[str]] = None
    # updated_at will be set by DB or application logic

class CrawlPresetResponse(CrawlPresetBase):
    preset_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # For Supabase response mapping
