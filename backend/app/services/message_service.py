"""
Message Service Module
Handles all message-related business logic with proper abstraction
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, desc
from backend.app.db.models import Message, User
from backend.app.schemas import MessageWithUser


class MessageService:
    @staticmethod
    def create_message(session: Session, content: str, user_id: int, channel_id: int, replied_to_id: Optional[int] = None) -> Message:
        """
        Create a new message in the database
        """
        new_message = Message(
            content=content,
            user_id=user_id,
            channel_id=channel_id,
            replied_to_id=replied_to_id
        )
        session.add(new_message)
        session.commit()
        session.refresh(new_message)
        return new_message

    @staticmethod
    def get_messages_by_channel(
        session: Session, 
        channel_id: int, 
        before: Optional[datetime] = None, 
        after: Optional[datetime] = None, 
        limit: int = 50
    ) -> List[MessageWithUser]:
        """
        Retrieve messages for a specific channel with pagination support
        """
        # Join Message and User tables to get user information
        statement = (
            select(Message, User)
            .join(User)
            .where(Message.channel_id == channel_id)
        )
        
        # Add time-based filters for efficient pagination
        if before:
            statement = statement.where(Message.created_at < before)
        if after:
            statement = statement.where(Message.created_at > after)
        
        # Order by creation time (newest first for more intuitive pagination)
        statement = statement.order_by(desc(Message.created_at)).limit(limit)

        results = session.exec(statement).all()

        # Format results to match MessageWithUser schema
        messages = []
        for message, user in results:
            messages.append(MessageWithUser(
                id=message.id,
                content=message.content,
                user_id=message.user_id,
                channel_id=message.channel_id,
                created_at=message.created_at,
                username=user.username,
                avatar_url=user.avatar_url,
                is_bot=user.is_bot
            ))

        # Reverse the list to return in chronological order (oldest first)
        return messages[::-1]