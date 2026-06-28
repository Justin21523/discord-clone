"""
Moderation Router
Handles all moderation API endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import TimeoutCreate, TimeoutRead, MuteCreate, MuteRead, BanCreate, BanRead
from backend.app.deps import get_current_user
from backend.app.db.models import User, Guild, GuildMember
from backend.app.services.moderation_service import ModerationService
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/timeout", response_model=TimeoutRead)
def apply_timeout(
    timeout_in: TimeoutCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Apply a timeout to a user in a guild
    Requires can_timeout_members permission
    """
    # Verify guild exists
    guild = session.get(Guild, timeout_in.guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", timeout_in.guild_id)
    
    # Check if user has permission to timeout members
    if not PermissionChecker.has_permission(session, current_user.id, timeout_in.guild_id, "can_timeout_members"):
        raise AuthorizationException("You don't have permission to timeout members in this server")
    
    # Verify target user exists
    target_user = session.get(User, timeout_in.user_id)
    if not target_user:
        raise ResourceNotFoundException("User", timeout_in.user_id)
    
    # Check if target user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == timeout_in.user_id)
        .where(GuildMember.guild_id == timeout_in.guild_id)
    ).first()
    
    if not membership:
        raise HTTPException(status_code=400, detail="Target user is not a member of this server")
    
    # Check if target user has higher permissions than the moderator
    target_permissions = PermissionChecker.get_user_permissions(session, timeout_in.user_id, timeout_in.guild_id)
    current_permissions = PermissionChecker.get_user_permissions(session, current_user.id, timeout_in.guild_id)
    
    # If target user is admin and current user is not, deny action
    if target_permissions["is_admin"] and not current_permissions["is_admin"]:
        raise HTTPException(status_code=403, detail="Cannot timeout a user with higher or equal permissions")
    
    # Apply timeout
    timeout = ModerationService.apply_timeout(
        session=session,
        user_id=timeout_in.user_id,
        guild_id=timeout_in.guild_id,
        moderator_id=current_user.id,
        reason=timeout_in.reason,
        duration_minutes=timeout_in.duration_minutes
    )
    
    return TimeoutRead.from_orm(timeout) if hasattr(TimeoutRead, 'from_orm') else TimeoutRead(
        id=timeout.id,
        user_id=timeout.user_id,
        guild_id=timeout.guild_id,
        moderator_id=timeout.moderator_id,
        reason=timeout.reason,
        start_time=timeout.start_time,
        end_time=timeout.end_time
    )


@router.delete("/timeout/{guild_id}/{user_id}")
def remove_timeout(
    guild_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Remove a timeout from a user in a guild
    Requires can_timeout_members permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to timeout members
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_timeout_members"):
        raise AuthorizationException("You don't have permission to manage timeouts in this server")
    
    # Verify target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise ResourceNotFoundException("User", user_id)
    
    # Remove timeout
    success = ModerationService.remove_timeout(
        session=session,
        user_id=user_id,
        guild_id=guild_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User is not timed out in this server")
    
    return {"status": "timeout_removed"}


@router.post("/mute", response_model=MuteRead)
def apply_mute(
    mute_in: MuteCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Apply a mute to a user in a guild
    Requires can_timeout_members permission (mutes are similar to extended timeouts)
    """
    # Verify guild exists
    guild = session.get(Guild, mute_in.guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", mute_in.guild_id)
    
    # Check if user has permission to timeout members (used for muting too)
    if not PermissionChecker.has_permission(session, current_user.id, mute_in.guild_id, "can_timeout_members"):
        raise AuthorizationException("You don't have permission to mute members in this server")
    
    # Verify target user exists
    target_user = session.get(User, mute_in.user_id)
    if not target_user:
        raise ResourceNotFoundException("User", mute_in.user_id)
    
    # Check if target user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == mute_in.user_id)
        .where(GuildMember.guild_id == mute_in.guild_id)
    ).first()
    
    if not membership:
        raise HTTPException(status_code=400, detail="Target user is not a member of this server")
    
    # Check if target user has higher permissions than the moderator
    target_permissions = PermissionChecker.get_user_permissions(session, mute_in.user_id, mute_in.guild_id)
    current_permissions = PermissionChecker.get_user_permissions(session, current_user.id, mute_in.guild_id)
    
    # If target user is admin and current user is not, deny action
    if target_permissions["is_admin"] and not current_permissions["is_admin"]:
        raise HTTPException(status_code=403, detail="Cannot mute a user with higher or equal permissions")
    
    # Apply mute
    mute = ModerationService.apply_mute(
        session=session,
        user_id=mute_in.user_id,
        guild_id=mute_in.guild_id,
        moderator_id=current_user.id,
        reason=mute_in.reason,
        duration_minutes=mute_in.duration_minutes
    )
    
    return MuteRead.from_orm(mute) if hasattr(MuteRead, 'from_orm') else MuteRead(
        id=mute.id,
        user_id=mute.user_id,
        guild_id=mute.guild_id,
        moderator_id=mute.moderator_id,
        reason=mute.reason,
        start_time=mute.start_time,
        end_time=mute.end_time
    )


@router.delete("/mute/{guild_id}/{user_id}")
def remove_mute(
    guild_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Remove a mute from a user in a guild
    Requires can_timeout_members permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to timeout members
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_timeout_members"):
        raise AuthorizationException("You don't have permission to manage mutes in this server")
    
    # Verify target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise ResourceNotFoundException("User", user_id)
    
    # Remove mute
    success = ModerationService.remove_mute(
        session=session,
        user_id=user_id,
        guild_id=guild_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User is not muted in this server")
    
    return {"status": "mute_removed"}


@router.post("/ban", response_model=BanRead)
def apply_ban(
    ban_in: BanCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Apply a ban to a user in a guild
    Requires can_ban_members permission
    """
    # Verify guild exists
    guild = session.get(Guild, ban_in.guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", ban_in.guild_id)
    
    # Check if user has permission to ban members
    if not PermissionChecker.has_permission(session, current_user.id, ban_in.guild_id, "can_ban_members"):
        raise AuthorizationException("You don't have permission to ban members in this server")
    
    # Verify target user exists
    target_user = session.get(User, ban_in.user_id)
    if not target_user:
        raise ResourceNotFoundException("User", ban_in.user_id)
    
    # Check if target user has higher permissions than the moderator
    target_permissions = PermissionChecker.get_user_permissions(session, ban_in.user_id, ban_in.guild_id)
    current_permissions = PermissionChecker.get_user_permissions(session, current_user.id, ban_in.guild_id)
    
    # If target user is admin and current user is not, deny action
    if target_permissions["is_admin"] and not current_permissions["is_admin"]:
        raise HTTPException(status_code=403, detail="Cannot ban a user with higher or equal permissions")
    
    # Apply ban
    ban = ModerationService.apply_ban(
        session=session,
        user_id=ban_in.user_id,
        guild_id=ban_in.guild_id,
        moderator_id=current_user.id,
        reason=ban_in.reason,
        duration_minutes=ban_in.duration_minutes
    )
    
    return BanRead.from_orm(ban) if hasattr(BanRead, 'from_orm') else BanRead(
        id=ban.id,
        user_id=ban.user_id,
        guild_id=ban.guild_id,
        moderator_id=ban.moderator_id,
        reason=ban.reason,
        start_time=ban.start_time,
        end_time=ban.end_time
    )


@router.delete("/ban/{guild_id}/{user_id}")
def remove_ban(
    guild_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Remove a ban from a user in a guild
    Requires can_ban_members permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to ban members
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_ban_members"):
        raise AuthorizationException("You don't have permission to manage bans in this server")
    
    # Verify target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise ResourceNotFoundException("User", user_id)
    
    # Remove ban
    success = ModerationService.remove_ban(
        session=session,
        user_id=user_id,
        guild_id=guild_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User is not banned from this server")
    
    return {"status": "ban_removed"}


@router.get("/{guild_id}/moderation-status/{user_id}")
def get_user_moderation_status(
    guild_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the moderation status of a user in a guild (timeout, mute, ban)
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to view moderation status
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_timeout_members"):
        raise AuthorizationException("You don't have permission to view moderation status in this server")
    
    # Verify target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise ResourceNotFoundException("User", user_id)
    
    # Check moderation status
    is_timed_out = ModerationService.is_timed_out(session, user_id, guild_id)
    is_muted = ModerationService.is_muted(session, user_id, guild_id)
    is_banned = ModerationService.is_banned(session, user_id, guild_id)
    
    return {
        "user_id": user_id,
        "is_timed_out": is_timed_out,
        "is_muted": is_muted,
        "is_banned": is_banned
    }