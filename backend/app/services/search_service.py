"""
Search Service Module
Handles all search-related business logic
"""

from typing import List
from datetime import datetime
from sqlmodel import Session, select, func, desc
from backend.app.db.models import Message, User, Channel


class SearchService:
    @staticmethod
    def search_messages(
        session: Session,
        query: str,
        user_id: int = None,
        channel_id: int = None,
        guild_id: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Search for messages based on various criteria
        """
        # Build the query
        statement = select(Message, User, Channel).join(User).join(Channel)
        
        # Add search term condition (search in message content)
        statement = statement.where(func.lower(Message.content).contains(func.lower(query)))
        
        # Add optional filters
        if user_id:
            statement = statement.where(Message.user_id == user_id)
        
        if channel_id:
            statement = statement.where(Message.channel_id == channel_id)
        
        if guild_id:
            statement = statement.where(Channel.guild_id == guild_id)
        
        # Order by most recent first
        statement = statement.order_by(desc(Message.created_at)).offset(offset).limit(limit)
        
        results = session.exec(statement).all()
        
        # Format results
        messages = []
        for message, user, channel in results:
            msg_dict = {
                "id": message.id,
                "content": message.content,
                "user_id": message.user_id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "is_bot": user.is_bot,
                "channel_id": message.channel_id,
                "channel_name": channel.name,
                "created_at": message.created_at,
                "replied_to_id": message.replied_to_id
            }
            messages.append(msg_dict)
        
        return messages

    @staticmethod
    def search_users(
        session: Session,
        query: str,
        guild_id: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Search for users based on username
        """
        statement = select(User)
        
        # Add search term condition (search in username)
        statement = statement.where(func.lower(User.username).contains(func.lower(query)))
        
        # Add optional guild filter
        if guild_id:
            # Need to join with GuildMember to filter by guild
            from backend.app.db.models import GuildMember
            statement = select(User).join(GuildMember).where(
                func.lower(User.username).contains(func.lower(query)) &
                (GuildMember.guild_id == guild_id)
            )
        
        # Order by username
        statement = statement.order_by(User.username).offset(offset).limit(limit)
        
        results = session.exec(statement).all()
        
        # Format results
        users = []
        for user in results:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "is_bot": user.is_bot,
                "created_at": user.created_at
            }
            users.append(user_dict)
        
        return users