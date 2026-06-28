"""
Direct Messages Router
Handles all direct message API endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import DirectMessageCreate, DirectMessageWithUsers
from backend.app.deps import get_current_user
from backend.app.db.models import User, DirectMessage
from backend.app.services.direct_message_service import DirectMessageService
from backend.app.exceptions import AuthorizationException, ResourceNotFoundException

router = APIRouter()


@router.post("/", response_model=DirectMessageWithUsers)
def send_direct_message(
    dm_in: DirectMessageCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a direct message to another user
    """
    # Verify recipient exists
    recipient = session.get(User, dm_in.recipient_id)
    if not recipient:
        raise ResourceNotFoundException("User", dm_in.recipient_id)
    
    # Prevent sending messages to oneself
    if current_user.id == dm_in.recipient_id:
        raise ValueError("Cannot send direct message to yourself")
    
    # Send the direct message
    dm = DirectMessageService.send_direct_message(
        session=session,
        sender_id=current_user.id,
        recipient_id=dm_in.recipient_id,
        content=dm_in.content
    )
    
    # Return the message with sender and recipient details
    return DirectMessageWithUsers(
        id=dm.id,
        sender_id=dm.sender_id,
        recipient_id=dm.recipient_id,
        content=dm.content,
        created_at=dm.created_at,
        is_read=dm.is_read,
        sender=current_user,
        recipient=recipient
    )


@router.get("/{recipient_id}", response_model=List[DirectMessageWithUsers])
def get_direct_messages_with_user(
    recipient_id: int,
    before: datetime = Query(None, description="Get messages before this timestamp"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return (1-100)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get direct messages between current user and another user
    """
    # Verify recipient exists
    recipient = session.get(User, recipient_id)
    if not recipient:
        raise ResourceNotFoundException("User", recipient_id)
    
    # Get messages between users
    dms = DirectMessageService.get_direct_messages_between_users(
        session=session,
        user1_id=current_user.id,
        user2_id=recipient_id,
        before=before,
        limit=limit
    )
    
    return dms


@router.get("/", response_model=List[User])
def get_direct_message_partners(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all users with whom the current user has had direct conversations
    """
    # Get all direct messages where current user is either sender or recipient
    sent_statement = select(DirectMessage.recipient_id).where(DirectMessage.sender_id == current_user.id)
    received_statement = select(DirectMessage.sender_id).where(DirectMessage.recipient_id == current_user.id)
    
    sent_results = session.exec(sent_statement).all()
    received_results = session.exec(received_statement).all()
    
    # Combine and deduplicate user IDs
    partner_ids = list(set(sent_results + received_results))
    
    # Get user objects for these IDs
    partners = []
    for user_id in partner_ids:
        if user_id != current_user.id:  # Exclude self
            user = session.get(User, user_id)
            if user:
                partners.append(user)
    
    return partners


@router.patch("/{dm_id}/read")
def mark_direct_message_as_read(
    dm_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a direct message as read
    """
    # Verify the message exists and belongs to the current user as recipient
    dm = session.get(DirectMessage, dm_id)
    if not dm:
        raise ResourceNotFoundException("Direct Message", dm_id)
    
    if dm.recipient_id != current_user.id:
        raise AuthorizationException("Cannot mark another user's received message as read")
    
    # Mark as read
    DirectMessageService.mark_as_read(session, dm_id, current_user.id)
    
    return {"status": "marked_as_read"}