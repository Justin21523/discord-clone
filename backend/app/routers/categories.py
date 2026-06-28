"""
Categories Router
Handles all category API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.schemas import CategoryCreate, CategoryRead, ChannelRead
from backend.app.deps import get_current_user
from backend.app.db.models import User, Guild, Category, Channel
from backend.app.services.category_service import CategoryService
from backend.app.utils.permission_checker import PermissionChecker
from backend.app.exceptions import ResourceNotFoundException, AuthorizationException

router = APIRouter()


@router.post("/", response_model=CategoryRead)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new category in a guild
    Requires manage_channels permission
    """
    # Verify guild exists
    guild = session.get(Guild, category_in.guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", category_in.guild_id)
    
    # Check if user has permission to manage channels
    if not PermissionChecker.has_permission(session, current_user.id, category_in.guild_id, "can_manage_channels"):
        raise AuthorizationException("You don't have permission to manage channels in this server")
    
    # Create the category
    category = CategoryService.create_category(
        session=session,
        name=category_in.name,
        guild_id=category_in.guild_id,
        position=category_in.position
    )
    
    return CategoryRead(
        id=category.id,
        name=category.name,
        guild_id=category.guild_id,
        position=category.position,
        created_at=category.created_at
    )


@router.get("/{guild_id}", response_model=List[CategoryRead])
def get_guild_categories(
    guild_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all categories in a guild
    """
    # Verify guild exists and user is a member
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user is a member of the guild
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
        .where(GuildMember.guild_id == guild_id)
    ).first()
    
    if not membership:
        raise AuthorizationException("You are not a member of this server")
    
    # Get categories
    categories = CategoryService.get_categories_by_guild(
        session=session,
        guild_id=guild_id
    )
    
    # Convert to response format
    result = []
    for category in categories:
        result.append(CategoryRead(
            id=category.id,
            name=category.name,
            guild_id=category.guild_id,
            position=category.position,
            created_at=category.created_at
        ))
    
    return result


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_in: CategoryCreate,  # Reusing for updates
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a category
    Requires manage_channels permission
    """
    # Get the category
    category = CategoryService.get_category_by_id(session, category_id)
    if not category:
        raise ResourceNotFoundException("Category", category_id)
    
    # Check if user has permission to manage channels
    if not PermissionChecker.has_permission(session, current_user.id, category.guild_id, "can_manage_channels"):
        raise AuthorizationException("You don't have permission to manage channels in this server")
    
    # Update the category
    updated_category = CategoryService.update_category(
        session=session,
        category_id=category_id,
        name=category_in.name,
        position=category_in.position
    )
    
    if not updated_category:
        raise ResourceNotFoundException("Category", category_id)
    
    return CategoryRead(
        id=updated_category.id,
        name=updated_category.name,
        guild_id=updated_category.guild_id,
        position=updated_category.position,
        created_at=updated_category.created_at
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a category and move its channels to uncategorized
    Requires manage_channels permission
    """
    # Get the category
    category = CategoryService.get_category_by_id(session, category_id)
    if not category:
        raise ResourceNotFoundException("Category", category_id)
    
    # Check if user has permission to manage channels
    if not PermissionChecker.has_permission(session, current_user.id, category.guild_id, "can_manage_channels"):
        raise AuthorizationException("You don't have permission to manage channels in this server")
    
    # Delete the category
    success = CategoryService.delete_category(
        session=session,
        category_id=category_id
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete category")
    
    return {"status": "category_deleted"}


@router.post("/{guild_id}/reorder")
def reorder_categories(
    guild_id: int,
    category_order: List[dict],  # List of dicts with 'id' and 'position' keys
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Reorder categories in a guild
    Requires manage_channels permission
    """
    # Verify guild exists
    guild = session.get(Guild, guild_id)
    if not guild:
        raise ResourceNotFoundException("Guild", guild_id)
    
    # Check if user has permission to manage channels
    if not PermissionChecker.has_permission(session, current_user.id, guild_id, "can_manage_channels"):
        raise AuthorizationException("You don't have permission to manage channels in this server")
    
    # Reorder categories
    CategoryService.reorder_categories(
        session=session,
        guild_id=guild_id,
        category_order=category_order
    )
    
    return {"status": "categories_reordered"}