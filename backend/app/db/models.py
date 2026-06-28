# backend/app/db/models.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# --- 連接表 (Join Tables) ---

# 成員與身分組的多對多關聯
class MemberRoleLink(SQLModel, table=True):
    member_id: Optional[int] = Field(default=None, foreign_key="guildmember.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)

# --- 主要模型 ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str
    hashed_password: str
    avatar_url: Optional[str] = None
    is_bot: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 關聯
    owned_guilds: List["Guild"] = Relationship(back_populates="owner")
    memberships: List["GuildMember"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")
    
    # 擁有的機器人
    my_bots: List["Bot"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"foreign_keys": "[Bot.owner_id]"}
    )

class Guild(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    icon: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 關聯
    owner: Optional[User] = Relationship(back_populates="owned_guilds")
    channels: List["Channel"] = Relationship(back_populates="guild", sa_relationship_kwargs={"cascade": "all, delete"})
    categories: List["Category"] = Relationship(back_populates="guild", sa_relationship_kwargs={"cascade": "all, delete"})

    # 伺服器裡的所有成員
    members: List["GuildMember"] = Relationship(back_populates="guild", sa_relationship_kwargs={"cascade": "all, delete"})

    # 伺服器裡的所有身分組
    roles: List["Role"] = Relationship(back_populates="guild", sa_relationship_kwargs={"cascade": "all, delete"})

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    color: str = "#99aab5" # 預設灰色
    position: int = 0 # 排序用，越小越低階
    guild_id: int = Field(foreign_key="guild.id")

    # --- Granular Permissions ---
    # General permissions
    is_admin: bool = Field(default=False)  # Super admin - overrides all other permissions
    can_manage_guild: bool = Field(default=False)
    can_view_audit_log: bool = Field(default=False)

    # Member permissions
    can_kick_members: bool = Field(default=False)
    can_ban_members: bool = Field(default=False)
    can_timeout_members: bool = Field(default=False)
    can_manage_nicknames: bool = Field(default=False)
    can_manage_roles: bool = Field(default=False)

    # Channel permissions
    can_manage_channels: bool = Field(default=False)
    can_create_private_threads: bool = Field(default=False)
    can_create_public_threads: bool = Field(default=False)
    can_send_messages: bool = Field(default=False)
    can_send_tts_messages: bool = Field(default=False)
    can_manage_messages: bool = Field(default=False)
    can_embed_links: bool = Field(default=False)
    can_attach_files: bool = Field(default=False)
    can_mention_everyone: bool = Field(default=False)
    can_view_channel: bool = Field(default=False)
    can_read_message_history: bool = Field(default=False)
    can_use_external_emojis: bool = Field(default=False)
    can_add_reactions: bool = Field(default=False)

    # Voice permissions
    can_connect: bool = Field(default=False)
    can_speak: bool = Field(default=False)
    can_mute_members: bool = Field(default=False)
    can_deafen_members: bool = Field(default=False)
    can_move_members: bool = Field(default=False)
    can_use_voice_activity: bool = Field(default=False)
    can_priority_speaker: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    guild: Optional[Guild] = Relationship(back_populates="roles")
    members: List["GuildMember"] = Relationship(back_populates="roles", link_model=MemberRoleLink)

class GuildMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)  # Add index for faster queries
    guild_id: int = Field(foreign_key="guild.id", index=True)  # Add index for faster queries
    nickname: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # 關聯
    user: Optional[User] = Relationship(back_populates="memberships")
    guild: Optional[Guild] = Relationship(back_populates="members")
    roles: List["Role"] = Relationship(back_populates="members", link_model=MemberRoleLink)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    guild_id: int = Field(foreign_key="guild.id", index=True)
    position: int = Field(default=0)  # Position for ordering categories
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    guild: Optional[Guild] = Relationship(back_populates="categories")
    channels: List["Channel"] = Relationship(back_populates="category")


class Channel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str = Field(default="text")
    guild_id: int = Field(foreign_key="guild.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)  # Optional category association
    position: int = Field(default=0)  # Position within the category
    created_at: datetime = Field(default_factory=datetime.utcnow)

    guild: Optional[Guild] = Relationship(back_populates="channels")
    category: Optional["Category"] = Relationship(back_populates="channels")
    messages: List["Message"] = Relationship(back_populates="channel", sa_relationship_kwargs={"cascade": "all, delete"})

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    user_id: int = Field(foreign_key="user.id", index=True)  # Add index for faster queries
    channel_id: int = Field(foreign_key="channel.id", index=True)  # Add index for faster queries
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index for time-based queries
    replied_to_id: Optional[int] = Field(default=None, foreign_key="message.id", index=True)  # For message threading/replies

    user: Optional[User] = Relationship(back_populates="messages")
    channel: Optional[Channel] = Relationship(back_populates="messages")
    replied_to: Optional["Message"] = Relationship(sa_relationship_kwargs={
        "remote_side": "Message.id"
    })  # Self-referencing relationship for replies
    replies: List["Message"] = Relationship(back_populates="replied_to")  # Replies to this message

class Bot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    token: str = Field(index=True, unique=True)
    bot_user_id: int = Field(foreign_key="user.id")
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="my_bots", sa_relationship_kwargs={"foreign_keys": "[Bot.owner_id]"})


class DirectMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    sender_id: int = Field(foreign_key="user.id", index=True)
    recipient_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_read: bool = Field(default=False)

    # Relationships
    sender: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DirectMessage.sender_id]"})
    recipient: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[DirectMessage.recipient_id]"})


class Reaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    emoji: str = Field(max_length=10)  # Store emoji as string (e.g., "👍", "❤️", etc.)
    user_id: int = Field(foreign_key="user.id", index=True)
    message_id: int = Field(foreign_key="message.id", index=True)  # For channel messages
    dm_id: Optional[int] = Field(default=None, foreign_key="directmessage.id", index=True)  # For direct messages
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship()
    message: Optional[Message] = Relationship()
    direct_message: Optional[DirectMessage] = Relationship()

    class Config:
        arbitrary_types_allowed = True


class UploadedFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)  # Path where file is stored
    file_size: int  # Size in bytes
    mime_type: str = Field(max_length=100)
    uploader_id: int = Field(foreign_key="user.id", index=True)
    message_id: Optional[int] = Field(default=None, foreign_key="message.id", index=True)  # Associated with channel message
    dm_id: Optional[int] = Field(default=None, foreign_key="directmessage.id", index=True)  # Associated with DM
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    uploader: Optional[User] = Relationship()
    message: Optional[Message] = Relationship()
    direct_message: Optional[DirectMessage] = Relationship()


class Timeout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    guild_id: int = Field(foreign_key="guild.id", index=True)
    moderator_id: int = Field(foreign_key="user.id", index=True)  # Who applied the timeout
    reason: str = Field(max_length=500)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: datetime  # When the timeout ends

    # Relationships
    user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Timeout.user_id]"})
    guild: Optional[Guild] = Relationship()
    moderator: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Timeout.moderator_id]"})


class Mute(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    guild_id: int = Field(foreign_key="guild.id", index=True)
    moderator_id: int = Field(foreign_key="user.id", index=True)  # Who applied the mute
    reason: str = Field(max_length=500)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None  # None means indefinite mute

    # Relationships
    user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Mute.user_id]"})
    guild: Optional[Guild] = Relationship()
    moderator: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Mute.moderator_id]"})


class Ban(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    guild_id: int = Field(foreign_key="guild.id", index=True)
    moderator_id: int = Field(foreign_key="user.id", index=True)  # Who applied the ban
    reason: str = Field(max_length=500)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None  # None means permanent ban

    # Relationships
    user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Ban.user_id]"})
    guild: Optional[Guild] = Relationship()
    moderator: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Ban.moderator_id]"})


class PinnedMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id", index=True)
    channel_id: int = Field(foreign_key="channel.id", index=True)
    pinned_by: int = Field(foreign_key="user.id", index=True)
    pinned_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: Optional[Message] = Relationship()
    channel: Optional[Channel] = Relationship()
    user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[PinnedMessage.pinned_by]"})


class StarredMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    starred_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: Optional[Message] = Relationship()
    user: Optional[User] = Relationship()


class NotificationSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)  # Each user has one notification setting
    # Global notification settings
    desktop_notifications: bool = Field(default=True)
    mobile_notifications: bool = Field(default=True)
    email_notifications: bool = Field(default=False)

    # Message notification settings
    notify_on_mentions: bool = Field(default=True)
    notify_on_replies: bool = Field(default=True)
    notify_on_direct_messages: bool = Field(default=True)
    notify_on_friend_activity: bool = Field(default=True)

    # Sound settings
    enable_notification_sound: bool = Field(default=True)
    notification_volume: float = Field(default=1.0)  # 0.0 to 1.0

    # Do not disturb settings
    dnd_enabled: bool = Field(default=False)
    dnd_start_time: Optional[datetime] = None
    dnd_end_time: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship()


class ServerTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=10, unique=True, index=True)  # Unique template code
    name: str = Field(max_length=100)  # Template name
    description: Optional[str] = Field(default=None, max_length=500)  # Template description
    usage_count: int = Field(default=0)  # How many times this template has been used

    # Metadata
    creator_id: int = Field(foreign_key="user.id", index=True)  # User who created the template
    guild_snapshot: str  # JSON string representing the guild structure (channels, roles, etc.)
    icon_url: Optional[str] = None  # Icon for the template
    is_active: bool = Field(default=True)  # Whether the template is active

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    creator: Optional[User] = Relationship()


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(max_length=100)  # The action performed (e.g., "MEMBER_BAN_ADD", "CHANNEL_CREATE", etc.)
    user_id: int = Field(foreign_key="user.id", index=True)  # The user who performed the action
    target_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # The user affected by the action (if applicable)
    guild_id: int = Field(foreign_key="guild.id", index=True)  # The guild where the action occurred
    channel_id: Optional[int] = Field(default=None, foreign_key="channel.id", index=True)  # The channel where the action occurred (if applicable)
    message_id: Optional[int] = Field(default=None, foreign_key="message.id", index=True)  # The message affected (if applicable)
    reason: Optional[str] = Field(default=None, max_length=500)  # Reason for the action (if provided)
    extra_info: Optional[str] = Field(default=None)  # Additional information in JSON format

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[AuditLog.user_id]"})
    target_user: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "[AuditLog.target_user_id]"})
    guild: Optional[Guild] = Relationship()
    channel: Optional[Channel] = Relationship()


class VoiceSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)  # The user participating in the voice session
    channel_id: int = Field(foreign_key="channel.id", index=True)  # The voice channel they're connected to
    session_id: str = Field(max_length=100, unique=True, index=True)  # Unique session identifier
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    disconnected_at: Optional[datetime] = None
    is_active: bool = Field(default=True)  # Whether the session is currently active

    # Relationships
    user: Optional[User] = Relationship()
    channel: Optional[Channel] = Relationship()


class VoiceServer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channel.id", unique=True, index=True)  # The voice channel this server serves
    ip_address: str = Field(max_length=45)  # IPv4 or IPv6 address
    port: int  # Port for voice traffic
    region: str = Field(max_length=50)  # Region identifier (e.g., us-west, eu-central)
    is_available: bool = Field(default=True)  # Whether the voice server is available

    # Relationships
    channel: Optional[Channel] = Relationship()