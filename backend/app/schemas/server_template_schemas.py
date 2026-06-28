"""
Server Template Schemas
Defines the data structures for server templates
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ServerTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    guild_snapshot: str  # JSON string representing the guild structure
    icon_url: Optional[str] = None


class ServerTemplateCreate(ServerTemplateBase):
    pass


class ServerTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    guild_snapshot: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None


class ServerTemplateRead(ServerTemplateBase):
    id: int
    code: str
    creator_id: int
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True