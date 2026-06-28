"""
Direct Message Service Module
Handles all direct message-related business logic
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, desc
from backend.app.db.models import DirectMessage, User
from backend.app.schemas import DirectMessageWithUsers


class DirectMessageService:
    @staticmethod
    def send_direct_message(
        session: Session, 
        sender_id: int, 
        recipient_id: int, 
        content: str
    ) -> DirectMessage:
        """
        Send a direct message from one user to another
        """
        dm = DirectMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content
        )
        session.add(dm)
        session.commit()
        session.refresh(dm)
        return dm

    @staticmethod
    def get_direct_messages_between_users(
        session: Session,
        user1_id: int,
        user2_id: int,
        before: Optional[datetime] = None,
        limit: int = 50
    ) -> List[DirectMessageWithUsers]:
        """
        Get direct messages between two users
        """
        # Query messages where user1 is sender and user2 is recipient OR user1 is recipient and user2 is sender
        statement = (
            select(DirectMessage, User, User)
            .join(User, DirectMessage.sender_id == User.id, isouter=True)
            .join(User, DirectMessage.recipient_id == User.id, isouter=True)
            .where(
                ((DirectMessage.sender_id == user1_id) & (DirectMessage.recipient_id == user2_id)) |
                ((DirectMessage.sender_id == user2_id) & (DirectMessage.recipient_id == user1_id))
            )
        )
        
        if before:
            statement = statement.where(DirectMessage.created_at < before)
        
        statement = statement.order_by(desc(DirectMessage.created_at)).limit(limit)

        results = session.exec(statement).all()

        # Format results to match DirectMessageWithUsers schema
        dms = []
        for dm, sender, recipient in results:
            dm_with_users = DirectMessageWithUsers(
                id=dm.id,
                sender_id=dm.sender_id,
                recipient_id=dm.recipient_id,
                content=dm.content,
                created_at=dm.created_at,
                is_read=dm.is_read,
                sender=sender,
                recipient=recipient
            )
            dms.append(dm_with_users)

        # Reverse to return in chronological order (oldest first)
        return dms[::-1]

    @staticmethod
    def mark_as_read(session: Session, dm_id: int, user_id: int):
        """
        Mark a direct message as read if the user is the recipient
        """
        dm = session.get(DirectMessage, dm_id)
        if dm and dm.recipient_id == user_id:
            dm.is_read = True
            session.add(dm)
            session.commit()