"""
Server Template Service Module
Handles all server template-related business logic
"""

import uuid
import json
from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import ServerTemplate, User, Guild, Channel, Role


class ServerTemplateService:
    @staticmethod
    def create_server_template(
        session: Session,
        name: str,
        description: str,
        creator_id: int,
        guild_snapshot: str,
        icon_url: str = None
    ) -> ServerTemplate:
        """
        Create a new server template
        """
        # Generate a unique code for the template
        code = str(uuid.uuid4())[:8].upper()  # Use first 8 chars of UUID, uppercase
        
        template = ServerTemplate(
            code=code,
            name=name,
            description=description,
            creator_id=creator_id,
            guild_snapshot=guild_snapshot,
            icon_url=icon_url,
            is_active=True
        )
        
        session.add(template)
        session.commit()
        session.refresh(template)
        
        return template

    @staticmethod
    def get_template_by_code(
        session: Session,
        code: str
    ) -> ServerTemplate:
        """
        Get a template by its code
        """
        return session.exec(
            select(ServerTemplate)
            .where(ServerTemplate.code == code)
            .where(ServerTemplate.is_active == True)
        ).first()

    @staticmethod
    def get_templates_by_creator(
        session: Session,
        creator_id: int
    ) -> list[ServerTemplate]:
        """
        Get all templates created by a user
        """
        return session.exec(
            select(ServerTemplate)
            .where(ServerTemplate.creator_id == creator_id)
            .order_by(ServerTemplate.created_at.desc())
        ).all()

    @staticmethod
    def get_all_active_templates(
        session: Session,
        limit: int = 50,
        offset: int = 0
    ) -> list[ServerTemplate]:
        """
        Get all active templates
        """
        return session.exec(
            select(ServerTemplate)
            .where(ServerTemplate.is_active == True)
            .order_by(ServerTemplate.usage_count.desc())  # Order by popularity
            .offset(offset)
            .limit(limit)
        ).all()

    @staticmethod
    def update_template(
        session: Session,
        template_id: int,
        update_data: dict
    ) -> ServerTemplate:
        """
        Update a template
        """
        template = session.get(ServerTemplate, template_id)
        if not template:
            return None
        
        # Update fields based on provided data
        for field, value in update_data.items():
            if hasattr(template, field) and value is not None:
                setattr(template, field, value)
        
        # Update the updated_at timestamp
        template.updated_at = datetime.utcnow()
        
        session.add(template)
        session.commit()
        session.refresh(template)
        
        return template

    @staticmethod
    def increment_usage_count(
        session: Session,
        template_id: int
    ) -> bool:
        """
        Increment the usage count of a template
        """
        template = session.get(ServerTemplate, template_id)
        if not template:
            return False
        
        template.usage_count += 1
        template.updated_at = datetime.utcnow()
        
        session.add(template)
        session.commit()
        
        return True

    @staticmethod
    def delete_template(
        session: Session,
        template_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a template (only the creator can delete it)
        """
        template = session.get(ServerTemplate, template_id)
        if not template or template.creator_id != user_id:
            return False
        
        session.delete(template)
        session.commit()
        
        return True