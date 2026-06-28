"""
Search Router
Handles all search API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.deps import get_current_user
from backend.app.db.models import User
from backend.app.services.search_service import SearchService
from backend.app.exceptions import AuthorizationException

router = APIRouter()


@router.get("/messages", response_model=List[dict])
def search_messages(
    query: str = Query(..., min_length=1, max_length=100, description="Search query term"),
    user_id: int = Query(None, description="Filter by user ID"),
    channel_id: int = Query(None, description="Filter by channel ID"),
    guild_id: int = Query(None, description="Filter by guild ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Search for messages across channels the user has access to
    """
    # In a full implementation, we would check if the user has permission to access
    # the specified channels/guilds, but for now we'll just perform the search
    
    # If guild_id is specified, check if user is a member
    if guild_id:
        from sqlmodel import select
        from backend.app.db.models import GuildMember
        membership = session.exec(
            select(GuildMember)
            .where(GuildMember.user_id == current_user.id)
            .where(GuildMember.guild_id == guild_id)
        ).first()
        
        if not membership:
            raise AuthorizationException("You are not a member of this server")
    
    # If channel_id is specified, check if user has access to the channel
    if channel_id:
        from sqlmodel import select
        from backend.app.db.models import Channel, GuildMember
        channel = session.get(Channel, channel_id)
        if channel:
            membership = session.exec(
                select(GuildMember)
                .where(GuildMember.user_id == current_user.id)
                .where(GuildMember.guild_id == channel.guild_id)
            ).first()
            
            if not membership:
                raise AuthorizationException("You don't have access to this channel")
    
    # Perform the search
    results = SearchService.search_messages(
        session=session,
        query=query,
        user_id=user_id,
        channel_id=channel_id,
        guild_id=guild_id,
        limit=limit,
        offset=offset
    )
    
    return results


@router.get("/users", response_model=List[dict])
def search_users(
    query: str = Query(..., min_length=1, max_length=100, description="Search query term"),
    guild_id: int = Query(None, description="Filter by guild ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Search for users by username
    """
    # If guild_id is specified, check if user is a member
    if guild_id:
        from sqlmodel import select
        from backend.app.db.models import GuildMember
        membership = session.exec(
            select(GuildMember)
            .where(GuildMember.user_id == current_user.id)
            .where(GuildMember.guild_id == guild_id)
        ).first()
        
        if not membership:
            raise AuthorizationException("You are not a member of this server")
    
    # Perform the search
    results = SearchService.search_users(
        session=session,
        query=query,
        guild_id=guild_id,
        limit=limit,
        offset=offset
    )
    
    return results