"""
Voice Chat Router
Handles all voice chat API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import VoiceSessionRead, VoiceServerRead, VoiceConnectRequest, VoiceDisconnectRequest
from backend.app.deps import get_current_user
from backend.app.db.models import User, Channel, GuildMember
from backend.app.services.voice_chat_service import VoiceChatService
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/connect", response_model=dict)
def connect_to_voice(
    connect_request: VoiceConnectRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Connect a user to a voice channel
    Requires can_connect permission
    """
    # Verify channel exists
    channel = session.get(Channel, connect_request.channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", connect_request.channel_id)
    
    # Check if channel is a voice channel
    if channel.type != "voice":
        raise HTTPException(status_code=400, detail="Channel is not a voice channel")
    
    # Check if user has permission to connect to this voice channel
    if not PermissionChecker.has_channel_permission(session, current_user.id, connect_request.channel_id, "can_connect"):
        raise AuthorizationException("You don't have permission to connect to this voice channel")
    
    # Check if user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
        .where(GuildMember.guild_id == channel.guild_id)
    ).first()
    
    if not membership:
        raise AuthorizationException("You are not a member of this server")
    
    # Create a voice session
    voice_session = VoiceChatService.create_voice_session(
        session=session,
        user_id=current_user.id,
        channel_id=connect_request.channel_id
    )
    
    # Get the voice server for this channel
    voice_server = VoiceChatService.get_voice_server_for_channel(
        session=session,
        channel_id=connect_request.channel_id
    )
    
    # If no voice server is assigned, assign one (in a real implementation, this would be handled differently)
    if not voice_server:
        # For demo purposes, assign a default voice server
        voice_server = VoiceChatService.assign_voice_server_to_channel(
            session=session,
            channel_id=connect_request.channel_id,
            ip_address="127.0.0.1",
            port=8080,
            region="local"
        )
    
    return {
        "session_id": voice_session.session_id,
        "user_id": current_user.id,
        "channel_id": connect_request.channel_id,
        "voice_server": {
            "ip_address": voice_server.ip_address,
            "port": voice_server.port,
            "region": voice_server.region
        },
        "connected_at": voice_session.connected_at
    }


@router.post("/disconnect")
def disconnect_from_voice(
    disconnect_request: VoiceDisconnectRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Disconnect a user from voice chat
    """
    # End the voice session
    success = VoiceChatService.end_voice_session(
        session=session,
        session_id=disconnect_request.session_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice session not found or already ended")
    
    return {"status": "disconnected"}


@router.get("/channel/{channel_id}/participants", response_model=List[dict])
def get_voice_participants(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all users currently in a voice channel
    """
    # Verify channel exists
    channel = session.get(Channel, channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", channel_id)
    
    # Check if user has permission to view this channel
    if not PermissionChecker.has_channel_permission(session, current_user.id, channel_id, "can_view_channel"):
        raise AuthorizationException("You don't have permission to view this channel")
    
    # Get active voice sessions in this channel
    active_sessions = VoiceChatService.get_active_sessions_in_channel(
        session=session,
        channel_id=channel_id
    )
    
    # Get user details for each participant
    participants = []
    for session_obj in active_sessions:
        user = session.get(User, session_obj.user_id)
        if user:
            participants.append({
                "user_id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "connected_at": session_obj.connected_at,
                "session_id": session_obj.session_id
            })
    
    return participants


@router.get("/session/{session_id}", response_model=VoiceSessionRead)
def get_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details about a specific voice session
    """
    voice_session = VoiceChatService.get_voice_session_by_session_id(
        session=session,
        session_id=session_id
    )
    
    if not voice_session:
        raise ResourceNotFoundException("Voice Session", session_id)
    
    # Check if the requesting user is the one in the session or has admin rights
    if voice_session.user_id != current_user.id:
        # Check if user has admin privileges
        has_admin = PermissionChecker.has_permission(
            session, 
            current_user.id, 
            voice_session.channel.guild_id, 
            "is_admin"
        )
        if not has_admin:
            raise AuthorizationException("You don't have permission to view this voice session")
    
    return VoiceSessionRead(
        id=voice_session.id,
        user_id=voice_session.user_id,
        channel_id=voice_session.channel_id,
        session_id=voice_session.session_id,
        connected_at=voice_session.connected_at,
        disconnected_at=voice_session.disconnected_at,
        is_active=voice_session.is_active
    )