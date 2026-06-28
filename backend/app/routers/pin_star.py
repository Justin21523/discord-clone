"""
Pinning and Starring Router
Handles all pinning and starring API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import PinMessageRequest, PinnedMessageRead, StarMessageRequest, StarredMessageRead
from backend.app.deps import get_current_user
from backend.app.db.models import User, Message, Channel, GuildMember
from backend.app.services.pin_star_service import PinStarService
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/pin", response_model=PinnedMessageRead)
def pin_message(
    pin_request: PinMessageRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Pin a message in a channel
    Requires manage_messages permission
    """
    # Verify message exists
    message = session.get(Message, pin_request.message_id)
    if not message:
        raise ResourceNotFoundException("Message", pin_request.message_id)
    
    # Verify channel exists
    channel = session.get(Channel, pin_request.channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", pin_request.channel_id)
    
    # Check if message belongs to the specified channel
    if message.channel_id != pin_request.channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to the specified channel")
    
    # Check if user has permission to manage messages in this channel
    if not PermissionChecker.has_channel_permission(session, current_user.id, pin_request.channel_id, "can_manage_messages"):
        raise AuthorizationException("You don't have permission to pin messages in this channel")
    
    # Pin the message
    pinned_message = PinStarService.pin_message(
        session=session,
        message_id=pin_request.message_id,
        channel_id=pin_request.channel_id,
        user_id=current_user.id
    )
    
    return PinnedMessageRead(
        id=pinned_message.id,
        message_id=pinned_message.message_id,
        channel_id=pinned_message.channel_id,
        pinned_by=pinned_message.pinned_by,
        pinned_at=pinned_message.pinned_at
    )


@router.delete("/pin/{message_id}/{channel_id}")
def unpin_message(
    message_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Unpin a message from a channel
    Requires manage_messages permission
    """
    # Verify message exists
    message = session.get(Message, message_id)
    if not message:
        raise ResourceNotFoundException("Message", message_id)
    
    # Verify channel exists
    channel = session.get(Channel, channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", channel_id)
    
    # Check if user has permission to manage messages in this channel
    if not PermissionChecker.has_channel_permission(session, current_user.id, channel_id, "can_manage_messages"):
        raise AuthorizationException("You don't have permission to unpin messages in this channel")
    
    # Unpin the message
    success = PinStarService.unpin_message(
        session=session,
        message_id=message_id,
        channel_id=channel_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Message is not pinned in this channel")
    
    return {"status": "message_unpinned"}


@router.get("/pinned/{channel_id}", response_model=List[PinnedMessageRead])
def get_pinned_messages(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all pinned messages in a channel
    """
    # Verify channel exists
    channel = session.get(Channel, channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", channel_id)
    
    # Check if user has permission to view this channel
    if not PermissionChecker.has_channel_permission(session, current_user.id, channel_id, "can_view_channel"):
        raise AuthorizationException("You don't have permission to view this channel")
    
    # Get pinned messages
    pinned_messages = PinStarService.get_pinned_messages(
        session=session,
        channel_id=channel_id
    )
    
    # Convert to response format
    result = []
    for pm in pinned_messages:
        result.append(PinnedMessageRead(
            id=pm.id,
            message_id=pm.message_id,
            channel_id=pm.channel_id,
            pinned_by=pm.pinned_by,
            pinned_at=pm.pinned_at
        ))
    
    return result


@router.post("/star", response_model=StarredMessageRead)
def star_message(
    star_request: StarMessageRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Star a message for the current user
    """
    # Verify message exists
    message = session.get(Message, star_request.message_id)
    if not message:
        raise ResourceNotFoundException("Message", star_request.message_id)
    
    # Star the message
    starred_message = PinStarService.star_message(
        session=session,
        message_id=star_request.message_id,
        user_id=current_user.id
    )
    
    return StarredMessageRead(
        id=starred_message.id,
        message_id=starred_message.message_id,
        user_id=starred_message.user_id,
        starred_at=starred_message.starred_at
    )


@router.delete("/star/{message_id}")
def unstar_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Unstar a message for the current user
    """
    # Verify message exists
    message = session.get(Message, message_id)
    if not message:
        raise ResourceNotFoundException("Message", message_id)
    
    # Unstar the message
    success = PinStarService.unstar_message(
        session=session,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Message is not starred by you")
    
    return {"status": "message_unstarred"}


@router.get("/starred", response_model=List[StarredMessageRead])
def get_starred_messages(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all messages starred by the current user
    """
    # Get starred messages
    starred_messages = PinStarService.get_starred_messages(
        session=session,
        user_id=current_user.id
    )
    
    # Convert to response format
    result = []
    for sm in starred_messages:
        result.append(StarredMessageRead(
            id=sm.id,
            message_id=sm.message_id,
            user_id=sm.user_id,
            starred_at=sm.starred_at
        ))
    
    return result