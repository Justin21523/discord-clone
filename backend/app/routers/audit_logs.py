"""
Audit Logs Router
Handles all audit log API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.schemas import AuditLogRead
from backend.app.deps import get_current_user
from backend.app.db.models import User, Guild, GuildMember
from backend.app.services.audit_log_service import AuditLogService
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.get("/{guild_id}", response_model=List[AuditLogRead])
def get_guild_audit_logs(
    guild_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get audit logs for a specific guild
    Requires view_audit_log permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to view audit logs
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_view_audit_log"):
        raise AuthorizationException("You don't have permission to view audit logs in this server")
    
    # Get audit logs
    audit_logs = AuditLogService.get_audit_logs_by_guild(
        session=session,
        guild_id=guild_id,
        limit=limit,
        offset=offset
    )
    
    # Format response
    result = []
    for log in audit_logs:
        result.append(AuditLogRead(
            id=log.id,
            action=log.action,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            guild_id=log.guild_id,
            channel_id=log.channel_id,
            message_id=log.message_id,
            reason=log.reason,
            extra_info=log.extra_info,
            created_at=log.created_at
        ))
    
    return result


@router.get("/user/{target_user_id}/guild/{guild_id}", response_model=List[AuditLogRead])
def get_user_audit_logs_in_guild(
    target_user_id: int,
    guild_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get audit logs for a specific user in a specific guild
    Requires view_audit_log permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Verify target user exists
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise ResourceNotFoundException("User", target_user_id)
    
    # Check if user has permission to view audit logs
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_view_audit_log"):
        raise AuthorizationException("You don't have permission to view audit logs in this server")
    
    # For now, we'll just get all logs for the guild and filter by target_user_id
    # In a full implementation, we would have a more efficient way to query this
    audit_logs = AuditLogService.get_audit_logs_by_guild(
        session=session,
        guild_id=guild_id,
        limit=limit,
        offset=offset
    )
    
    # Filter logs that affect the target user
    filtered_logs = [log for log in audit_logs if log.target_user_id == target_user_id]
    
    # Format response
    result = []
    for log in filtered_logs:
        result.append(AuditLogRead(
            id=log.id,
            action=log.action,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            guild_id=log.guild_id,
            channel_id=log.channel_id,
            message_id=log.message_id,
            reason=log.reason,
            extra_info=log.extra_info,
            created_at=log.created_at
        ))
    
    return result


@router.get("/action/{action}/guild/{guild_id}", response_model=List[AuditLogRead])
def get_audit_logs_by_action(
    action: str,
    guild_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get audit logs for a specific action in a specific guild
    Requires view_audit_log permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to view audit logs
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_view_audit_log"):
        raise AuthorizationException("You don't have permission to view audit logs in this server")
    
    # Get audit logs for the specific action
    audit_logs = AuditLogService.get_audit_logs_by_action(
        session=session,
        action=action,
        guild_id=guild_id,
        limit=limit,
        offset=offset
    )
    
    # Format response
    result = []
    for log in audit_logs:
        result.append(AuditLogRead(
            id=log.id,
            action=log.action,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            guild_id=log.guild_id,
            channel_id=log.channel_id,
            message_id=log.message_id,
            reason=log.reason,
            extra_info=log.extra_info,
            created_at=log.created_at
        ))
    
    return result