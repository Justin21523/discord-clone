"""
Presence Router
Handles all presence-related API endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from backend.app.db.session import get_session
from backend.app.deps import get_current_user
from backend.app.db.models import User, Guild, GuildMember
from backend.app.websockets.presence import presence_manager, PresenceStatus
from backend.app.exceptions import ResourceNotFoundException

router = APIRouter()


@router.get("/{user_id}")
def get_user_presence(
    user_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get presence information for a specific user
    """
    # Verify user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise ResourceNotFoundException("User", user_id)

    # Get presence data
    presence_data = presence_manager.get_presence(user_id)

    return {
        "user_id": user_id,
        "username": target_user.username,
        "status": presence_data["status"],
        "last_seen": presence_data["last_seen"],
        "activity": presence_data["activity"]
    }


@router.get("/guild/{guild_id}")
def get_guild_presences(
    guild_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get presence information for all users in a specific guild
    """
    # Verify guild exists and user has access
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)

    # Check if user is a member of this guild
    membership = session.exec(
        select(GuildMember).where(
            (GuildMember.guild_id == guild_id) &
            (GuildMember.user_id == current_user.id)
        )
    ).first()

    if not membership:
        raise ResourceNotFoundException("Guild", guild_id)  # Or raise permission error

    # Get all members of the guild
    guild_members = session.exec(
        select(GuildMember).where(GuildMember.guild_id == guild_id)
    ).all()

    user_ids = [member.user_id for member in guild_members]

    # Get presence data for all users in the guild
    presences = presence_manager.get_presences_for_guild(guild_id, user_ids)

    # Prepare response with user details
    result = []
    for user_id in user_ids:
        user = session.get(User, user_id)
        if user:
            presence_info = presences.get(user_id, {
                "status": PresenceStatus.OFFLINE.value,
                "last_seen": None,
                "activity": None
            })

            result.append({
                "user_id": user_id,
                "username": user.username,
                "status": presence_info["status"],
                "last_seen": presence_info["last_seen"],
                "activity": presence_info["activity"]
            })

    return result


@router.post("/heartbeat/{user_id}")
def update_user_heartbeat(
    user_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a user's heartbeat (mark as active)
    This endpoint should be called periodically by the client to indicate activity
    """
    # Only the user themselves can update their heartbeat
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own presence")

    # Update heartbeat
    presence_manager.heartbeat(user_id)

    # Get updated presence
    presence_data = presence_manager.get_presence(user_id)

    return {
        "status": presence_data["status"],
        "updated": True
    }


@router.post("/status")
def update_user_status(
    status_data: dict,  # Contains status and activity
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user's presence status
    Expected payload: {"status": "online|idle|dnd|offline", "activity": "optional activity text"}
    """
    status = status_data.get("status")
    activity = status_data.get("activity")
    
    if status not in ["online", "idle", "dnd", "offline"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be one of: online, idle, dnd, offline")
    
    # Update presence status
    presence_manager.set_presence(current_user.id, status, activity)
    
    return {
        "status": "updated",
        "user_id": current_user.id,
        "new_status": status,
        "activity": activity
    }