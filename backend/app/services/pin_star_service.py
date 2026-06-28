"""
Pinning and Starring Service Module
Handles all pinning and starring-related business logic
"""

from typing import List
from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import PinnedMessage, StarredMessage, Message, Channel, User


class PinStarService:
    @staticmethod
    def pin_message(
        session: Session,
        message_id: int,
        channel_id: int,
        user_id: int
    ) -> PinnedMessage:
        """
        Pin a message in a channel
        """
        # Verify message exists in the channel
        message = session.get(Message, message_id)
        if not message or message.channel_id != channel_id:
            raise ValueError("Message does not exist in this channel")
        
        # Check if message is already pinned
        existing_pin = session.exec(
            select(PinnedMessage)
            .where(PinnedMessage.message_id == message_id)
            .where(PinnedMessage.channel_id == channel_id)
        ).first()
        
        if existing_pin:
            return existing_pin  # Already pinned
        
        # Create the pin
        pinned_message = PinnedMessage(
            message_id=message_id,
            channel_id=channel_id,
            pinned_by=user_id
        )
        
        session.add(pinned_message)
        session.commit()
        session.refresh(pinned_message)
        
        return pinned_message

    @staticmethod
    def unpin_message(
        session: Session,
        message_id: int,
        channel_id: int
    ) -> bool:
        """
        Unpin a message from a channel
        """
        pinned_message = session.exec(
            select(PinnedMessage)
            .where(PinnedMessage.message_id == message_id)
            .where(PinnedMessage.channel_id == channel_id)
        ).first()
        
        if pinned_message:
            session.delete(pinned_message)
            session.commit()
            return True
        
        return False

    @staticmethod
    def get_pinned_messages(
        session: Session,
        channel_id: int
    ) -> List[PinnedMessage]:
        """
        Get all pinned messages in a channel
        """
        pinned_messages = session.exec(
            select(PinnedMessage)
            .where(PinnedMessage.channel_id == channel_id)
            .order_by(PinnedMessage.pinned_at.desc())
        ).all()
        
        return pinned_messages

    @staticmethod
    def star_message(
        session: Session,
        message_id: int,
        user_id: int
    ) -> StarredMessage:
        """
        Star a message for a user
        """
        # Verify message exists
        message = session.get(Message, message_id)
        if not message:
            raise ValueError("Message does not exist")
        
        # Check if message is already starred by this user
        existing_star = session.exec(
            select(StarredMessage)
            .where(StarredMessage.message_id == message_id)
            .where(StarredMessage.user_id == user_id)
        ).first()
        
        if existing_star:
            return existing_star  # Already starred
        
        # Create the star
        starred_message = StarredMessage(
            message_id=message_id,
            user_id=user_id
        )
        
        session.add(starred_message)
        session.commit()
        session.refresh(starred_message)
        
        return starred_message

    @staticmethod
    def unstar_message(
        session: Session,
        message_id: int,
        user_id: int
    ) -> bool:
        """
        Unstar a message for a user
        """
        starred_message = session.exec(
            select(StarredMessage)
            .where(StarredMessage.message_id == message_id)
            .where(StarredMessage.user_id == user_id)
        ).first()
        
        if starred_message:
            session.delete(starred_message)
            session.commit()
            return True
        
        return False

    @staticmethod
    def get_starred_messages(
        session: Session,
        user_id: int
    ) -> List[StarredMessage]:
        """
        Get all messages starred by a user
        """
        starred_messages = session.exec(
            select(StarredMessage)
            .where(StarredMessage.user_id == user_id)
            .order_by(StarredMessage.starred_at.desc())
        ).all()
        
        return starred_messages

    @staticmethod
    def is_message_pinned(
        session: Session,
        message_id: int,
        channel_id: int
    ) -> bool:
        """
        Check if a message is pinned in a channel
        """
        pinned_message = session.exec(
            select(PinnedMessage)
            .where(PinnedMessage.message_id == message_id)
            .where(PinnedMessage.channel_id == channel_id)
        ).first()
        
        return pinned_message is not None

    @staticmethod
    def is_message_starred(
        session: Session,
        message_id: int,
        user_id: int
    ) -> bool:
        """
        Check if a message is starred by a user
        """
        starred_message = session.exec(
            select(StarredMessage)
            .where(StarredMessage.message_id == message_id)
            .where(StarredMessage.user_id == user_id)
        ).first()
        
        return starred_message is not None