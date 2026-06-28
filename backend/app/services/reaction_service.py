"""
Reaction Service Module
Handles all reaction-related business logic
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import Reaction, User, Message, DirectMessage
from backend.app.schemas import ReactionWithUser


class ReactionService:
    @staticmethod
    def add_reaction(
        session: Session,
        user_id: int,
        emoji: str,
        message_id: Optional[int] = None,
        dm_id: Optional[int] = None
    ) -> Reaction:
        """
        Add a reaction to a message or direct message
        """
        # Check if user already reacted with this emoji to this message/DM
        existing_reaction = session.exec(
            select(Reaction)
            .where(Reaction.user_id == user_id)
            .where(Reaction.emoji == emoji)
            .where(Reaction.message_id == message_id if message_id else Reaction.dm_id == dm_id)
        ).first()
        
        if existing_reaction:
            # If reaction already exists, return it (no duplicate reactions)
            return existing_reaction
        
        reaction = Reaction(
            emoji=emoji,
            user_id=user_id,
            message_id=message_id,
            dm_id=dm_id
        )
        
        session.add(reaction)
        session.commit()
        session.refresh(reaction)
        return reaction

    @staticmethod
    def remove_reaction(
        session: Session,
        user_id: int,
        emoji: str,
        message_id: Optional[int] = None,
        dm_id: Optional[int] = None
    ) -> bool:
        """
        Remove a reaction from a message or direct message
        """
        reaction = session.exec(
            select(Reaction)
            .where(Reaction.user_id == user_id)
            .where(Reaction.emoji == emoji)
            .where(Reaction.message_id == message_id if message_id else Reaction.dm_id == dm_id)
        ).first()
        
        if reaction:
            session.delete(reaction)
            session.commit()
            return True
        return False

    @staticmethod
    def get_reactions_for_message(
        session: Session,
        message_id: int
    ) -> List[ReactionWithUser]:
        """
        Get all reactions for a specific message
        """
        statement = (
            select(Reaction, User)
            .join(User)
            .where(Reaction.message_id == message_id)
            .where(Reaction.dm_id.is_(None))  # Only channel messages, not DMs
        )
        
        results = session.exec(statement).all()

        reactions = []
        for reaction, user in results:
            reaction_with_user = ReactionWithUser(
                id=reaction.id,
                emoji=reaction.emoji,
                user_id=reaction.user_id,
                message_id=reaction.message_id,
                dm_id=reaction.dm_id,
                created_at=reaction.created_at,
                username=user.username,
                avatar_url=user.avatar_url
            )
            reactions.append(reaction_with_user)

        return reactions

    @staticmethod
    def get_reactions_for_dm(
        session: Session,
        dm_id: int
    ) -> List[ReactionWithUser]:
        """
        Get all reactions for a specific direct message
        """
        statement = (
            select(Reaction, User)
            .join(User)
            .where(Reaction.dm_id == dm_id)
            .where(Reaction.message_id.is_(None))  # Only DMs, not channel messages
        )
        
        results = session.exec(statement).all()

        reactions = []
        for reaction, user in results:
            reaction_with_user = ReactionWithUser(
                id=reaction.id,
                emoji=reaction.emoji,
                user_id=reaction.user_id,
                message_id=reaction.message_id,
                dm_id=reaction.dm_id,
                created_at=reaction.created_at,
                username=user.username,
                avatar_url=user.avatar_url
            )
            reactions.append(reaction_with_user)

        return reactions