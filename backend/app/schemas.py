# backend/app/schemas.py
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from backend.app.utils.validation_utils import validate_username, validate_email, validate_message_content

# 1. 基礎模型 (共用欄位)
class UserBase(BaseModel):
    email: str
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not validate_username(v):
            raise ValueError('Username must be 2-32 characters and contain only letters, numbers, underscores, and hyphens')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

# 2. 註冊時需要的模型 (包含明碼密碼)
class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# 3. 回傳給前端的模型 (不包含密碼！)
class UserRead(UserBase):
    id: int
    is_bot: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        # 告訴 Pydantic 可以從 ORM (SQLModel) 讀取資料
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


# Guild 相關模型

# 1. 基礎欄位
class GuildBase(BaseModel):
    name: str
    icon: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        from backend.app.utils.validation_utils import validate_guild_name
        if not validate_guild_name(v):
            raise ValueError('Server name must be 1-100 characters')
        return v

# 2. 建立時 (前端 -> 後端)
class GuildCreate(GuildBase):
    pass # 只需要 name 和 icon，owner_id 會從 Token 自動抓取

# 3. 讀取時 (後端 -> 前端)
class GuildRead(GuildBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Channel 相關模型
class ChannelBase(BaseModel):
    name: str
    type: str = "text"

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        from backend.app.utils.validation_utils import validate_channel_name
        if not validate_channel_name(v):
            raise ValueError('Channel name must be 1-100 characters and contain only letters, numbers, spaces, hyphens, and underscores')
        return v

class ChannelCreate(ChannelBase):
    pass

class ChannelRead(ChannelBase):
    id: int
    guild_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Message 相關模型
class MessageRead(BaseModel):
    id: int
    content: str
    user_id: int
    channel_id: int
    created_at: datetime
    replied_to_id: Optional[int] = None

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not validate_message_content(v):
            raise ValueError('Message content must be 1-2000 characters and not contain invalid control characters')
        return v

    # 為了方便前端顯示，我們直接把發訊者的名字也帶回去
    # 這需要一點 Pydantic 的技巧，或者我們在 API 層處理
    # 這裡我們先回傳 basic info，前端可以用 user_id 去查，或者後端幫忙 join
    # 簡單起見，我們讓 API 回傳時額外附帶 username

    class Config:
        from_attributes = True

# 專門給前端顯示用的加強版 Schema
class MessageWithUser(MessageRead):
    username: str
    avatar_url: Optional[str] = None
    is_bot: bool = False # 🔥 新增這行

# Schema for creating threaded messages
class ThreadedMessageCreate(BaseModel):
    content: str
    replied_to_id: Optional[int] = None  # ID of the message being replied to

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not validate_message_content(v):
            raise ValueError('Message content must be 1-2000 characters and not contain invalid control characters')
        return v


# --- Moderation Schemas ---
class TimeoutCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: int  # How long the timeout should last


class TimeoutRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True


class MuteCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: Optional[int] = None  # None means indefinite


class MuteRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class BanCreate(BaseModel):
    user_id: int
    guild_id: int
    reason: str
    duration_minutes: Optional[int] = None  # None means permanent


class BanRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


# --- Pinning and Starring Schemas ---
class PinMessageRequest(BaseModel):
    message_id: int
    channel_id: int


class PinnedMessageRead(BaseModel):
    id: int
    message_id: int
    channel_id: int
    pinned_by: int
    pinned_at: datetime

    class Config:
        from_attributes = True


class StarMessageRequest(BaseModel):
    message_id: int


class StarredMessageRead(BaseModel):
    id: int
    message_id: int
    user_id: int
    starred_at: datetime

    class Config:
        from_attributes = True


# --- Notification Setting Schemas ---
class NotificationSettingBase(BaseModel):
    # Global notification settings
    desktop_notifications: bool = True
    mobile_notifications: bool = True
    email_notifications: bool = False

    # Message notification settings
    notify_on_mentions: bool = True
    notify_on_replies: bool = True
    notify_on_direct_messages: bool = True
    notify_on_friend_activity: bool = True

    # Sound settings
    enable_notification_sound: bool = True
    notification_volume: float = 1.0  # 0.0 to 1.0

    # Do not disturb settings
    dnd_enabled: bool = False
    dnd_start_time: Optional[datetime] = None
    dnd_end_time: Optional[datetime] = None


class NotificationSettingCreate(NotificationSettingBase):
    user_id: int


class NotificationSettingUpdate(BaseModel):
    # Global notification settings
    desktop_notifications: Optional[bool] = None
    mobile_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None

    # Message notification settings
    notify_on_mentions: Optional[bool] = None
    notify_on_replies: Optional[bool] = None
    notify_on_direct_messages: Optional[bool] = None
    notify_on_friend_activity: Optional[bool] = None

    # Sound settings
    enable_notification_sound: Optional[bool] = None
    notification_volume: Optional[float] = None  # 0.0 to 1.0

    # Do not disturb settings
    dnd_enabled: Optional[bool] = None
    dnd_start_time: Optional[datetime] = None
    dnd_end_time: Optional[datetime] = None


class NotificationSettingRead(NotificationSettingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Server Template Schemas ---
class ServerTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    guild_snapshot: str  # JSON string representing the guild structure
    icon_url: Optional[str] = None


class ServerTemplateCreate(ServerTemplateBase):
    pass


class ServerTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    guild_snapshot: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None


class ServerTemplateRead(ServerTemplateBase):
    id: int
    code: str
    creator_id: int
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Audit Log Schemas ---
class AuditLogBase(BaseModel):
    action: str
    user_id: int
    target_user_id: Optional[int] = None
    guild_id: int
    channel_id: Optional[int] = None
    message_id: Optional[int] = None
    reason: Optional[str] = None
    extra_info: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Voice Chat Schemas ---
class VoiceSessionBase(BaseModel):
    user_id: int
    channel_id: int
    session_id: str


class VoiceSessionCreate(VoiceSessionBase):
    pass


class VoiceSessionUpdate(BaseModel):
    disconnected_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class VoiceSessionRead(VoiceSessionBase):
    id: int
    connected_at: datetime
    disconnected_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class VoiceServerBase(BaseModel):
    channel_id: int
    ip_address: str
    port: int
    region: str
    is_available: bool = True


class VoiceServerCreate(VoiceServerBase):
    pass


class VoiceServerUpdate(BaseModel):
    ip_address: Optional[str] = None
    port: Optional[int] = None
    region: Optional[str] = None
    is_available: Optional[bool] = None


class VoiceServerRead(VoiceServerBase):
    id: int

    class Config:
        from_attributes = True


class VoiceConnectRequest(BaseModel):
    channel_id: int
    user_id: int


class VoiceDisconnectRequest(BaseModel):
    session_id: str


# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str
    guild_id: int
    position: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Update Channel schemas to include category_id
class ChannelBase(BaseModel):
    name: str
    type: str = "text"
    guild_id: int
    category_id: Optional[int] = None  # Optional category association
    position: int = 0  # Position within the category

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        from backend.app.utils.validation_utils import validate_channel_name
        if not validate_channel_name(v):
            raise ValueError('Channel name must be 1-100 characters and contain only letters, numbers, spaces, hyphens, and underscores')
        return v


class ChannelCreate(ChannelBase):
    pass


class ChannelRead(ChannelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 🔥 新增 Bot 相關模型

class BotCreate(BaseModel):
    name: str

class BotRead(BaseModel):
    id: int
    name: str
    bot_user_id: int
    created_at: datetime
    # 注意：一般讀取時不回傳 Token，除非是剛建立成功時

# 包含 Token 的讀取模型 (只有建立成功時顯示一次)
class BotReadWithToken(BotRead):
    token: str

# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str
    color: str = "#99aab5"
    # General permissions
    is_admin: bool = False
    can_manage_guild: bool = False
    can_view_audit_log: bool = False

    # Member permissions
    can_kick_members: bool = False
    can_ban_members: bool = False
    can_timeout_members: bool = False
    can_manage_nicknames: bool = False
    can_manage_roles: bool = False

    # Channel permissions
    can_manage_channels: bool = False
    can_create_private_threads: bool = False
    can_create_public_threads: bool = False
    can_send_messages: bool = False
    can_send_tts_messages: bool = False
    can_manage_messages: bool = False
    can_embed_links: bool = False
    can_attach_files: bool = False
    can_mention_everyone: bool = False
    can_view_channel: bool = False
    can_read_message_history: bool = False
    can_use_external_emojis: bool = False
    can_add_reactions: bool = False

    # Voice permissions
    can_connect: bool = False
    can_speak: bool = False
    can_mute_members: bool = False
    can_deafen_members: bool = False
    can_move_members: bool = False
    can_use_voice_activity: bool = False
    can_priority_speaker: bool = False

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    guild_id: int
    position: int

    class Config:
        from_attributes = True

# --- Member Schemas ---
# 用於顯示成員列表
class MemberRead(BaseModel):
    id: int
    user_id: int
    guild_id: int
    nickname: Optional[str]
    joined_at: datetime
    user: "UserRead" # 嵌套 User 資訊
    roles: List[RoleRead] = [] # 嵌套 Roles

    class Config:
        from_attributes = True


# Update Guild schemas to include categories
class GuildRead(GuildBase):
    id: int
    owner_id: int
    created_at: datetime
    # Add relationships if needed in the future

    class Config:
        from_attributes = True


# --- Direct Message Schemas ---
class DirectMessageBase(BaseModel):
    recipient_id: int
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not validate_message_content(v):
            raise ValueError('Message content must be 1-2000 characters and not contain invalid control characters')
        return v


class DirectMessageCreate(DirectMessageBase):
    pass


class DirectMessageRead(DirectMessageBase):
    id: int
    sender_id: int
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True


class DirectMessageWithUsers(DirectMessageRead):
    sender: UserRead
    recipient: UserRead

    class Config:
        from_attributes = True


# --- Reaction Schemas ---
class ReactionBase(BaseModel):
    emoji: str

    @field_validator('emoji')
    @classmethod
    def validate_emoji(cls, v):
        # Basic validation: emoji should be 1-10 characters
        if len(v) < 1 or len(v) > 10:
            raise ValueError('Emoji must be 1-10 characters')
        # Sanitize input
        from backend.app.utils.validation_utils import sanitize_input
        return sanitize_input(v)


class ReactionCreate(ReactionBase):
    message_id: Optional[int] = None
    dm_id: Optional[int] = None

    @field_validator('message_id', 'dm_id')
    @classmethod
    def validate_target(cls, values):
        # Either message_id or dm_id must be provided, but not both
        msg_id = values.data.get('message_id')
        dm_id = values.data.get('dm_id')

        if not msg_id and not dm_id:
            raise ValueError('Either message_id or dm_id must be provided')
        if msg_id and dm_id:
            raise ValueError('Only one of message_id or dm_id can be provided')
        return values


class ReactionRead(ReactionBase):
    id: int
    user_id: int
    message_id: Optional[int] = None
    dm_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionWithUser(ReactionRead):
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# --- File Upload Schemas ---
class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploader_id: int
    message_id: Optional[int] = None
    dm_id: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FileAttachment(BaseModel):
    """Schema for attaching files to messages"""
    file_id: int