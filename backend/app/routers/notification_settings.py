"""
Notification Settings Router
Handles all notification setting API endpoints
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.schemas import NotificationSettingRead, NotificationSettingUpdate
from backend.app.deps import get_current_user
from backend.app.db.models import User
from backend.app.services.notification_setting_service import NotificationSettingService

router = APIRouter()


@router.get("/", response_model=NotificationSettingRead)
def get_notification_settings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the current user's notification settings
    """
    settings = NotificationSettingService.get_user_settings(
        session=session,
        user_id=current_user.id
    )
    
    return NotificationSettingRead(
        id=settings.id,
        user_id=settings.user_id,
        desktop_notifications=settings.desktop_notifications,
        mobile_notifications=settings.mobile_notifications,
        email_notifications=settings.email_notifications,
        notify_on_mentions=settings.notify_on_mentions,
        notify_on_replies=settings.notify_on_replies,
        notify_on_direct_messages=settings.notify_on_direct_messages,
        notify_on_friend_activity=settings.notify_on_friend_activity,
        enable_notification_sound=settings.enable_notification_sound,
        notification_volume=settings.notification_volume,
        dnd_enabled=settings.dnd_enabled,
        dnd_start_time=settings.dnd_start_time,
        dnd_end_time=settings.dnd_end_time,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@router.put("/", response_model=NotificationSettingRead)
def update_notification_settings(
    settings_update: NotificationSettingUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update the current user's notification settings
    """
    # Convert Pydantic model to dict, excluding unset values
    update_data = settings_update.dict(exclude_unset=True)
    
    settings = NotificationSettingService.update_user_settings(
        session=session,
        user_id=current_user.id,
        update_data=update_data
    )
    
    return NotificationSettingRead(
        id=settings.id,
        user_id=settings.user_id,
        desktop_notifications=settings.desktop_notifications,
        mobile_notifications=settings.mobile_notifications,
        email_notifications=settings.email_notifications,
        notify_on_mentions=settings.notify_on_mentions,
        notify_on_replies=settings.notify_on_replies,
        notify_on_direct_messages=settings.notify_on_direct_messages,
        notify_on_friend_activity=settings.notify_on_friend_activity,
        enable_notification_sound=settings.enable_notification_sound,
        notification_volume=settings.notification_volume,
        dnd_enabled=settings.dnd_enabled,
        dnd_start_time=settings.dnd_start_time,
        dnd_end_time=settings.dnd_end_time,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )