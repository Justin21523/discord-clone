"""
Moderation Schemas
Defines the data structures for moderation actions
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TimeoutCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: int  # How long the timeout should last


class TimeoutRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True


class MuteCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: Optional[int] = None  # None means indefinite


class MuteRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class BanCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: Optional[int] = None  # None means permanent


class BanRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True