"""
Moderation Service Module
Handles all moderation-related business logic
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from backend.app.db.models import Timeout, Mute, Ban, User, Guild


class ModerationService:
    @staticmethod
    def apply_timeout(
        session: Session,
        user_id: int,
        guild_id: int,
        moderator_id: int,
        reason: str,
        duration_minutes: int
    ) -> Timeout:
        """
        Apply a timeout to a user in a guild
        """
        end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        timeout = Timeout(
            user_id=user_id,
            guild_id=guild_id,
            moderator_id=moderator_id,
            reason=reason,
            end_time=end_time
        )
        
        session.add(timeout)
        session.commit()
        session.refresh(timeout)
        
        return timeout

    @staticmethod
    def remove_timeout(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Remove a timeout from a user in a guild
        """
        # Find active timeout for the user in the guild
        timeout = session.exec(
            select(Timeout)
            .where(Timeout.user_id == user_id)
            .where(Timeout.guild_id == guild_id)
            .where(Timeout.end_time > datetime.utcnow())  # Still active
        ).first()
        
        if timeout:
            session.delete(timeout)
            session.commit()
            return True
        
        return False

    @staticmethod
    def is_timed_out(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Check if a user is currently timed out in a guild
        """
        active_timeout = session.exec(
            select(Timeout)
            .where(Timeout.user_id == user_id)
            .where(Timeout.guild_id == guild_id)
            .where(Timeout.end_time > datetime.utcnow())
        ).first()
        
        return active_timeout is not None

    @staticmethod
    def apply_mute(
        session: Session,
        user_id: int,
        guild_id: int,
        moderator_id: int,
        reason: str,
        duration_minutes: Optional[int] = None
    ) -> Mute:
        """
        Apply a mute to a user in a guild
        """
        end_time = None
        if duration_minutes is not None:
            end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        mute = Mute(
            user_id=user_id,
            guild_id=guild_id,
            moderator_id=moderator_id,
            reason=reason,
            end_time=end_time
        )
        
        session.add(mute)
        session.commit()
        session.refresh(mute)
        
        return mute

    @staticmethod
    def remove_mute(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Remove a mute from a user in a guild
        """
        # Find active mute for the user in the guild
        mute = session.exec(
            select(Mute)
            .where(Mute.user_id == user_id)
            .where(Mute.guild_id == guild_id)
            .where((Mute.end_time.is_(None)) | (Mute.end_time > datetime.utcnow()))  # Active (indefinite or still active)
        ).first()
        
        if mute:
            session.delete(mute)
            session.commit()
            return True
        
        return False

    @staticmethod
    def is_muted(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Check if a user is currently muted in a guild
        """
        active_mute = session.exec(
            select(Mute)
            .where(Mute.user_id == user_id)
            .where(Mute.guild_id == guild_id)
            .where((Mute.end_time.is_(None)) | (Mute.end_time > datetime.utcnow()))
        ).first()
        
        return active_mute is not None

    @staticmethod
    def apply_ban(
        session: Session,
        user_id: int,
        guild_id: int,
        moderator_id: int,
        reason: str,
        duration_minutes: Optional[int] = None
    ) -> Ban:
        """
        Apply a ban to a user in a guild
        """
        end_time = None
        if duration_minutes is not None:
            end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        ban = Ban(
            user_id=user_id,
            guild_id=guild_id,
            moderator_id=moderator_id,
            reason=reason,
            end_time=end_time
        )
        
        session.add(ban)
        session.commit()
        session.refresh(ban)
        
        return ban

    @staticmethod
    def remove_ban(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Remove a ban from a user in a guild
        """
        # Find active ban for the user in the guild
        ban = session.exec(
            select(Ban)
            .where(Ban.user_id == user_id)
            .where(Ban.guild_id == guild_id)
            .where((Ban.end_time.is_(None)) | (Ban.end_time > datetime.utcnow()))  # Active (permanent or still active)
        ).first()
        
        if ban:
            session.delete(ban)
            session.commit()
            return True
        
        return False

    @staticmethod
    def is_banned(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> bool:
        """
        Check if a user is currently banned from a guild
        """
        active_ban = session.exec(
            select(Ban)
            .where(Ban.user_id == user_id)
            .where(Ban.guild_id == guild_id)
            .where((Ban.end_time.is_(None)) | (Ban.end_time > datetime.utcnow()))
        ).first()
        
        return active_ban is not None