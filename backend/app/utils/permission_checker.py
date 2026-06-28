"""
Permissions Utility Module
Provides functions to check user permissions in guilds and channels
"""

from typing import List, Optional
from sqlmodel import Session, select
from backend.app.db.models import User, Guild, GuildMember, Role, Channel


class PermissionChecker:
    @staticmethod
    def has_permission(
        session: Session,
        user_id: int,
        guild_id: int,
        permission: str  # e.g., "can_manage_channels", "can_kick_members", etc.
    ) -> bool:
        """
        Check if a user has a specific permission in a guild
        """
        # Get the user's roles in this guild
        guild_member = session.exec(
            select(GuildMember)
            .where(GuildMember.user_id == user_id)
            .where(GuildMember.guild_id == guild_id)
        ).first()
        
        if not guild_member:
            return False  # User is not a member of the guild
        
        # Check if user is the guild owner (has all permissions)
        guild = session.get(Guild, guild_id)
        if guild and guild.owner_id == user_id:
            return True
        
        # Get all roles assigned to the user in this guild
        # Note: This assumes a many-to-many relationship between GuildMember and Role
        # In our current model, GuildMember has a roles relationship
        user_roles = guild_member.roles if hasattr(guild_member, 'roles') else []
        
        # Check permissions from highest to lowest priority (by position)
        # Sort roles by position (highest number = highest position)
        sorted_roles = sorted(user_roles, key=lambda r: r.position, reverse=True)
        
        for role in sorted_roles:
            # Admin role has all permissions
            if role.is_admin:
                return True
            
            # Check the specific permission
            if hasattr(role, permission) and getattr(role, permission):
                return True
        
        return False

    @staticmethod
    def has_channel_permission(
        session: Session,
        user_id: int,
        channel_id: int,
        permission: str
    ) -> bool:
        """
        Check if a user has a specific permission in a channel
        This checks both guild-wide permissions and channel-specific permissions
        """
        # First get the channel to find its guild
        channel = session.get(Channel, channel_id)
        if not channel:
            return False
        
        guild_id = channel.guild_id
        
        # Check guild-wide permissions
        if PermissionChecker.has_permission(session, user_id, guild_id, permission):
            return True
        
        # In a full implementation, we would also check channel-specific overwrites here
        # For now, we just check guild permissions
        
        return False

    @staticmethod
    def get_user_permissions(
        session: Session,
        user_id: int,
        guild_id: int
    ) -> dict:
        """
        Get all permissions for a user in a guild
        """
        permissions = {
            # General permissions
            "is_admin": False,
            "can_manage_guild": False,
            "can_view_audit_log": False,
            
            # Member permissions
            "can_kick_members": False,
            "can_ban_members": False,
            "can_timeout_members": False,
            "can_manage_nicknames": False,
            "can_manage_roles": False,
            
            # Channel permissions
            "can_manage_channels": False,
            "can_create_private_threads": False,
            "can_create_public_threads": False,
            "can_send_messages": False,
            "can_send_tts_messages": False,
            "can_manage_messages": False,
            "can_embed_links": False,
            "can_attach_files": False,
            "can_mention_everyone": False,
            "can_view_channel": False,
            "can_read_message_history": False,
            "can_use_external_emojis": False,
            "can_add_reactions": False,
            
            # Voice permissions
            "can_connect": False,
            "can_speak": False,
            "can_mute_members": False,
            "can_deafen_members": False,
            "can_move_members": False,
            "can_use_voice_activity": False,
            "can_priority_speaker": False,
        }
        
        # Get the user's roles in this guild
        guild_member = session.exec(
            select(GuildMember)
            .where(GuildMember.user_id == user_id)
            .where(GuildMember.guild_id == guild_id)
        ).first()
        
        if not guild_member:
            return permissions  # User is not a member of the guild
        
        # Check if user is the guild owner (has all permissions)
        guild = session.get(Guild, guild_id)
        if guild and guild.owner_id == user_id:
            # Grant all permissions to guild owner
            for perm in permissions:
                permissions[perm] = True
            return permissions
        
        # Get all roles assigned to the user in this guild
        user_roles = guild_member.roles if hasattr(guild_member, 'roles') else []
        
        # Combine permissions from all roles (highest position takes precedence for conflicting perms)
        sorted_roles = sorted(user_roles, key=lambda r: r.position, reverse=True)
        
        for role in sorted_roles:
            # If admin role, grant all permissions and return
            if role.is_admin:
                for perm in permissions:
                    permissions[perm] = True
                return permissions
            
            # Otherwise, add permissions from this role if not already set
            for perm_name in permissions:
                if hasattr(role, perm_name):
                    role_perm_value = getattr(role, perm_name)
                    # Only set if not already True (to respect role hierarchy)
                    if not permissions[perm_name]:
                        permissions[perm_name] = role_perm_value
        
        return permissions