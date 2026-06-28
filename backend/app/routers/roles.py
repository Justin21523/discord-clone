"""
Roles and Permissions Router
Handles all role and permission API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import RoleCreate, RoleRead
from backend.app.deps import get_current_user
from backend.app.db.models import User, Guild, Role, GuildMember
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/{guild_id}/roles", response_model=RoleRead)
def create_role(
    guild_id: int,
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new role in a guild
    Requires can_manage_roles permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to manage roles
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_manage_roles"):
        raise AuthorizationException("You don't have permission to manage roles in this server")
    
    # Create the new role
    new_role = Role(
        name=role_in.name,
        color=role_in.color,
        position=role_in.position,
        guild_id=guild_id,
        # Set all permissions from role_in
        is_admin=role_in.is_admin,
        can_manage_guild=role_in.can_manage_guild,
        can_view_audit_log=role_in.can_view_audit_log,
        can_kick_members=role_in.can_kick_members,
        can_ban_members=role_in.can_ban_members,
        can_timeout_members=role_in.can_timeout_members,
        can_manage_nicknames=role_in.can_manage_nicknames,
        can_manage_roles=role_in.can_manage_roles,
        can_manage_channels=role_in.can_manage_channels,
        can_create_private_threads=role_in.can_create_private_threads,
        can_create_public_threads=role_in.can_create_public_threads,
        can_send_messages=role_in.can_send_messages,
        can_send_tts_messages=role_in.can_send_tts_messages,
        can_manage_messages=role_in.can_manage_messages,
        can_embed_links=role_in.can_embed_links,
        can_attach_files=role_in.can_attach_files,
        can_mention_everyone=role_in.can_mention_everyone,
        can_view_channel=role_in.can_view_channel,
        can_read_message_history=role_in.can_read_message_history,
        can_use_external_emojis=role_in.can_use_external_emojis,
        can_add_reactions=role_in.can_add_reactions,
        can_connect=role_in.can_connect,
        can_speak=role_in.can_speak,
        can_mute_members=role_in.can_mute_members,
        can_deafen_members=role_in.can_deafen_members,
        can_move_members=role_in.can_move_members,
        can_use_voice_activity=role_in.can_use_voice_activity,
        can_priority_speaker=role_in.can_priority_speaker
    )
    
    session.add(new_role)
    session.commit()
    session.refresh(new_role)
    
    return new_role


@router.get("/{guild_id}/roles", response_model=List[RoleRead])
def get_guild_roles(
    guild_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all roles in a guild
    """
    # Verify guild exists and user is a member
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
        .where(GuildMember.guild_id == guild_id)
    ).first()
    
    if not membership:
        raise AuthorizationException("You are not a member of this server")
    
    # Get all roles in the guild
    roles = session.exec(
        select(Role)
        .where(Role.guild_id == guild_id)
        .order_by(Role.position.desc())  # Order by position (highest first)
    ).all()
    
    return roles


@router.put("/roles/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    role_in: RoleCreate,  # Reusing RoleCreate for updates
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a role in a guild
    Requires can_manage_roles permission
    """
    # Get the role
    role = session.get(Role, role_id)
    if not role:
        raise ResourceNotFoundException("Role", role_id)
    
    # Check if user has permission to manage roles
    if not PermissionChecker.has_permission(session, current_user.id, role.guild_id, "can_manage_roles"):
        raise AuthorizationException("You don't have permission to manage roles in this server")
    
    # Update the role
    update_data = role_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    
    session.add(role)
    session.commit()
    session.refresh(role)
    
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a role from a guild
    Requires can_manage_roles permission
    """
    # Get the role
    role = session.get(Role, role_id)
    if not role:
        raise ResourceNotFoundException("Role", role_id)
    
    # Check if user has permission to manage roles
    if not PermissionChecker.has_permission(session, current_user.id, role.guild_id, "can_manage_roles"):
        raise AuthorizationException("You don't have permission to manage roles in this server")
    
    # Don't allow deleting the @everyone role (position 0)
    if role.position == 0 and role.name == "@everyone":
        raise AuthorizationException("Cannot delete the @everyone role")
    
    # Remove this role from all members that have it
    # In a full implementation, we would handle this association
    # For now, we'll just delete the role
    
    session.delete(role)
    session.commit()
    
    return {"status": "role_deleted"}


@router.get("/{guild_id}/permissions", response_class=dict)
def get_user_permissions(
    guild_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all permissions for the current user in a guild
    """
    # Verify guild exists and user is a member
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
        .where(GuildMember.guild_id == guild_id)
    ).first()
    
    if not membership:
        raise AuthorizationException("You are not a member of this server")
    
    # Get user permissions
    permissions = PermissionChecker.get_user_permissions(session, current_user.id, guild_id)
    
    return {"permissions": permissions}