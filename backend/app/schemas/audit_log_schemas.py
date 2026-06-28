"""
Audit Log Schemas
Defines the data structures for audit logs
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogBase(BaseModel):
    action: str
    user_id: int
    target_user_id: Optional[int] = None
    guild_id: int
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    reason: Optional[str] = None
    extra_info: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True