"""
Voice Chat Schemas
Defines the data structures for voice chat functionality
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VoiceSessionBase(BaseModel):
    user_id: int
    channel_id: int
    session_id: str


class VoiceSessionCreate(VoiceSessionBase):
    pass


class VoiceSessionUpdate(BaseModel):
    disconnected_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class VoiceSessionRead(VoiceSessionBase):
    id: int
    connected_at: datetime
    disconnected_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class VoiceServerBase(BaseModel):
    channel_id: int
    ip_address: str
    port: int
    region: str
    is_available: bool = True


class VoiceServerCreate(VoiceServerBase):
    pass


class VoiceServerUpdate(BaseModel):
    ip_address: Optional[str] = None
    port: Optional[int] = None
    region: Optional[str] = None
    is_available: Optional[bool] = None


class VoiceServerRead(VoiceServerBase):
    id: int

    class Config:
        from_attributes = True


class VoiceConnectRequest(BaseModel):
    channel_id: int
    user_id: int


class VoiceDisconnectRequest(BaseModel):
    session_id: str