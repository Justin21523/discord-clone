"""
Reactions Router
Handles all reaction API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import ReactionCreate, ReactionWithUser
from backend.app.deps import get_current_user
from backend.app.db.models import User, Message, DirectMessage, Reaction
from backend.app.services.reaction_service import ReactionService
from backend.app.exceptions import ResourceNotFoundException

router = APIRouter()


@router.post("/", response_model=ReactionWithUser)
def add_reaction(
    reaction_in: ReactionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add a reaction to a message or direct message
    """
    # Validate that the target (message or DM) exists
    if reaction_in.message_id:
        # Check if message exists
        message = session.get(Message, reaction_in.message_id)
        if not message:
            raise ResourceNotFoundException("Message", reaction_in.message_id)
    elif reaction_in.dm_id:
        # Check if DM exists
        dm = session.get(DirectMessage, reaction_in.dm_id)
        if not dm:
            raise ResourceNotFoundException("Direct Message", reaction_in.dm_id)
    else:
        raise HTTPException(status_code=400, detail="Either message_id or dm_id must be provided")
    
    # Add the reaction
    reaction = ReactionService.add_reaction(
        session=session,
        user_id=current_user.id,
        emoji=reaction_in.emoji,
        message_id=reaction_in.message_id,
        dm_id=reaction_in.dm_id
    )
    
    # Return the reaction with user info
    return ReactionWithUser(
        id=reaction.id,
        emoji=reaction.emoji,
        user_id=reaction.user_id,
        message_id=reaction.message_id,
        dm_id=reaction.dm_id,
        created_at=reaction.created_at,
        username=current_user.username,
        avatar_url=current_user.avatar_url
    )


@router.delete("/{reaction_id}")
def remove_reaction(
    reaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Remove a reaction (only the user who added it can remove it)
    """
    # Get the reaction
    reaction = session.get(Reaction, reaction_id)
    if not reaction:
        raise ResourceNotFoundException("Reaction", reaction_id)
    
    # Check if the current user owns this reaction
    if reaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove this reaction")
    
    # Remove the reaction
    success = ReactionService.remove_reaction(
        session=session,
        user_id=current_user.id,
        emoji=reaction.emoji,
        message_id=reaction.message_id,
        dm_id=reaction.dm_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    return {"status": "reaction_removed"}


@router.get("/message/{message_id}", response_model=List[ReactionWithUser])
def get_reactions_for_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all reactions for a specific message
    """
    # Verify message exists
    message = session.get(Message, message_id)
    if not message:
        raise ResourceNotFoundException("Message", message_id)
    
    # Check if user has access to the channel this message belongs to
    # (Basic check: user must be able to view the channel)
    # Note: In a full implementation, we'd check channel permissions here
    
    reactions = ReactionService.get_reactions_for_message(
        session=session,
        message_id=message_id
    )
    
    return reactions


@router.get("/dm/{dm_id}", response_model=List[ReactionWithUser])
def get_reactions_for_dm(
    dm_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all reactions for a specific direct message
    """
    # Verify DM exists and current user is involved
    dm = session.get(DirectMessage, dm_id)
    if not dm:
        raise ResourceNotFoundException("Direct Message", dm_id)
    
    # Check if current user is sender or recipient of the DM
    if current_user.id not in [dm.sender_id, dm.recipient_id]:
        raise HTTPException(status_code=403, detail="Not authorized to view reactions for this DM")
    
    reactions = ReactionService.get_reactions_for_dm(
        session=session,
        dm_id=dm_id
    )
    
    return reactions