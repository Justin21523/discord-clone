"""
Reaction Schemas
Defines the data structures for message reactions
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from backend.app.utils.validation_utils import sanitize_input


class ReactionBase(BaseModel):
    emoji: str

    @field_validator('emoji')
    @classmethod
    def validate_emoji(cls, v):
        # Basic validation: emoji should be 1-10 characters
        if len(v) < 1 or len(v) > 10:
            raise ValueError('Emoji must be 1-10 characters')
        # Sanitize input
        return sanitize_input(v)


class ReactionCreate(ReactionBase):
    message_id: Optional[int] = None
    dm_id: Optional[int] = None

    @field_validator('message_id', 'dm_id')
    @classmethod
    def validate_target(cls, v1, v2):
        # Either message_id or dm_id must be provided, but not both
        values = cls.__dict__.get('values', {})
        msg_id = values.get('message_id')
        dm_id = values.get('dm_id')
        
        if not msg_id and not dm_id:
            raise ValueError('Either message_id or dm_id must be provided')
        if msg_id and dm_id:
            raise ValueError('Only one of message_id or dm_id can be provided')
        return v1 or v2


class ReactionRead(ReactionBase):
    id: int
    user_id: int
    message_id: Optional[int] = None
    dm_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionWithUser(ReactionRead):
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True