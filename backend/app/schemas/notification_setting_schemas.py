"""
Notification Setting Schemas
Defines the data structures for notification settings
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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