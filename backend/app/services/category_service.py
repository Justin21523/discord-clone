"""
Category Service Module
Handles all category-related business logic
"""

from typing import List
from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import Category, Channel


class CategoryService:
    @staticmethod
    def create_category(
        session: Session,
        name: str,
        guild_id: int,
        position: int = 0
    ) -> Category:
        """
        Create a new category in a guild
        """
        category = Category(
            name=name,
            guild_id=guild_id,
            position=position
        )
        
        session.add(category)
        session.commit()
        session.refresh(category)
        
        return category

    @staticmethod
    def get_category_by_id(
        session: Session,
        category_id: int
    ) -> Category:
        """
        Get a category by its ID
        """
        return session.get(Category, category_id)

    @staticmethod
    def get_categories_by_guild(
        session: Session,
        guild_id: int
    ) -> List[Category]:
        """
        Get all categories in a guild, ordered by position
        """
        categories = session.exec(
            select(Category)
            .where(Category.guild_id == guild_id)
            .order_by(Category.position)
        ).all()
        
        return categories

    @staticmethod
    def update_category(
        session: Session,
        category_id: int,
        name: str = None,
        position: int = None
    ) -> Category:
        """
        Update a category
        """
        category = session.get(Category, category_id)
        if not category:
            return None
        
        if name is not None:
            category.name = name
        if position is not None:
            category.position = position
        
        session.add(category)
        session.commit()
        session.refresh(category)
        
        return category

    @staticmethod
    def delete_category(
        session: Session,
        category_id: int
    ) -> bool:
        """
        Delete a category and move its channels to uncategorized
        """
        category = session.get(Category, category_id)
        if not category:
            return False
        
        # Move all channels in this category to uncategorized (set category_id to None)
        channels = session.exec(
            select(Channel)
            .where(Channel.category_id == category_id)
        ).all()
        
        for channel in channels:
            channel.category_id = None
            session.add(channel)
        
        # Delete the category
        session.delete(category)
        session.commit()
        
        return True

    @staticmethod
    def reorder_categories(
        session: Session,
        guild_id: int,
        category_order: List[dict]  # List of dicts with 'id' and 'position' keys
    ):
        """
        Reorder categories in a guild
        """
        for item in category_order:
            category_id = item['id']
            position = item['position']
            
            category = session.get(Category, category_id)
            if category and category.guild_id == guild_id:
                category.position = position
                session.add(category)
        
        session.commit()