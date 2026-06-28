"""
Notification Setting Service Module
Handles all notification setting-related business logic
"""

from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import NotificationSetting


class NotificationSettingService:
    @staticmethod
    def get_or_create_user_settings(
        session: Session,
        user_id: int
    ) -> NotificationSetting:
        """
        Get a user's notification settings, creating default settings if they don't exist
        """
        # Try to find existing settings
        settings = session.exec(
            select(NotificationSetting)
            .where(NotificationSetting.user_id == user_id)
        ).first()
        
        if settings:
            return settings
        
        # Create default settings
        new_settings = NotificationSetting(
            user_id=user_id,
            desktop_notifications=True,
            mobile_notifications=True,
            email_notifications=False,
            notify_on_mentions=True,
            notify_on_replies=True,
            notify_on_direct_messages=True,
            notify_on_friend_activity=True,
            enable_notification_sound=True,
            notification_volume=1.0,
            dnd_enabled=False
        )
        
        session.add(new_settings)
        session.commit()
        session.refresh(new_settings)
        
        return new_settings

    @staticmethod
    def update_user_settings(
        session: Session,
        user_id: int,
        update_data: dict
    ) -> NotificationSetting:
        """
        Update a user's notification settings
        """
        settings = NotificationSettingService.get_or_create_user_settings(session, user_id)
        
        # Update fields based on provided data
        for field, value in update_data.items():
            if hasattr(settings, field) and value is not None:
                setattr(settings, field, value)
        
        # Update the updated_at timestamp
        settings.updated_at = datetime.utcnow()
        
        session.add(settings)
        session.commit()
        session.refresh(settings)
        
        return settings

    @staticmethod
    def get_user_settings(
        session: Session,
        user_id: int
    ) -> NotificationSetting:
        """
        Get a user's notification settings
        """
        return NotificationSettingService.get_or_create_user_settings(session, user_id)