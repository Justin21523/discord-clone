"""
Audit Log Service Module
Handles all audit log-related business logic
"""

from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import AuditLog


class AuditLogService:
    @staticmethod
    def create_audit_log(
        session: Session,
        action: str,
        user_id: int,
        guild_id: int,
        target_user_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        reason: str = None,
        extra_info: str = None
    ) -> AuditLog:
        """
        Create a new audit log entry
        """
        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            target_user_id=target_user_id,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
            reason=reason,
            extra_info=extra_info
        )
        
        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)
        
        return audit_log

    @staticmethod
    def get_audit_logs_by_guild(
        session: Session,
        guild_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific guild
        """
        return session.exec(
            select(AuditLog)
            .where(AuditLog.guild_id == guild_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    @staticmethod
    def get_audit_logs_by_user(
        session: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Get audit logs performed by a specific user
        """
        return session.exec(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    @staticmethod
    def get_audit_logs_by_action(
        session: Session,
        action: str,
        guild_id: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific action
        """
        query = select(AuditLog).where(AuditLog.action == action)
        
        if guild_id:
            query = query.where(AuditLog.guild_id == guild_id)
        
        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        
        return session.exec(query).all()

    @staticmethod
    def get_audit_log_by_id(
        session: Session,
        log_id: int
    ) -> AuditLog:
        """
        Get a specific audit log by its ID
        """
        return session.get(AuditLog, log_id)