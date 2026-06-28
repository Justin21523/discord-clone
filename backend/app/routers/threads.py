"""
Thread Router
Handles all message threading and reply API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, desc

from backend.app.db.session import get_session
from backend.app.schemas import MessageWithUser, ThreadedMessageCreate
from backend.app.deps import get_current_user
from backend.app.db.models import User, Message, Channel
from backend.app.services.message_service import MessageService
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/{channel_id}/thread", response_model=MessageWithUser)
def create_threaded_message(
    channel_id: int,
    message_data: ThreadedMessageCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a threaded message/reply in a specific channel
    """
    # Verify channel exists
    channel = session.get(Channel, channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", channel_id)
    
    # If this is a reply to another message, verify that message exists in the same channel
    if message_data.replied_to_id:
        parent_message = session.get(Message, message_data.replied_to_id)
        if not parent_message:
            raise ResourceNotFoundException("Message", message_data.replied_to_id)
        if parent_message.channel_id != channel_id:
            raise AuthorizationException("Cannot reply to a message in a different channel")
    
    # Create the threaded message
    new_message = MessageService.create_message(
        session=session,
        content=message_data.content,
        user_id=current_user.id,
        channel_id=channel_id,
        replied_to_id=message_data.replied_to_id
    )
    
    # Return the message with user info
    return MessageWithUser(
        id=new_message.id,
        content=new_message.content,
        user_id=new_message.user_id,
        channel_id=new_message.channel_id,
        created_at=new_message.created_at,
        replied_to_id=new_message.replied_to_id,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        is_bot=current_user.is_bot
    )


@router.get("/{message_id}/replies", response_model=List[MessageWithUser])
def get_message_replies(
    message_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all replies to a specific message (thread)
    """
    # Verify the parent message exists
    parent_message = session.get(Message, message_id)
    if not parent_message:
        raise ResourceNotFoundException("Message", message_id)
    
    # Verify user has access to the channel
    # In a full implementation, we'd check channel permissions here
    
    # Get all messages that reply to this message
    reply_messages = session.exec(
        select(Message, User)
        .join(User)
        .where(Message.replied_to_id == message_id)
        .order_by(desc(Message.created_at))
    ).all()
    
    # Format results
    replies = []
    for message, user in reply_messages:
        reply = MessageWithUser(
            id=message.id,
            content=message.content,
            user_id=message.user_id,
            channel_id=message.channel_id,
            created_at=message.created_at,
            replied_to_id=message.replied_to_id,
            username=user.username,
            avatar_url=user.avatar_url,
            is_bot=user.is_bot
        )
        replies.append(reply)
    
    # Reverse to return in chronological order (oldest first)
    return replies[::-1]


@router.get("/{channel_id}/threads", response_model=List[MessageWithUser])
def get_thread_starters_in_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all messages in a channel that start threads (messages that are not replies)
    """
    # Verify channel exists
    channel = session.get(Channel, channel_id)
    if not channel:
        raise ResourceNotFoundException("Channel", channel_id)
    
    # Get all messages in the channel that are not replies to other messages
    thread_starters = session.exec(
        select(Message, User)
        .join(User)
        .where((Message.channel_id == channel_id) & (Message.replied_to_id.is_(None)))
        .order_by(desc(Message.created_at))
    ).all()
    
    # Format results
    threads = []
    for message, user in thread_starters:
        thread = MessageWithUser(
            id=message.id,
            content=message.content,
            user_id=message.user_id,
            channel_id=message.channel_id,
            created_at=message.created_at,
            replied_to_id=message.replied_to_id,
            username=user.username,
            avatar_url=user.avatar_url,
            is_bot=user.is_bot
        )
        threads.append(thread)
    
    # Reverse to return in chronological order (oldest first)
    return threads[::-1]