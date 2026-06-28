"""
Server Templates Router
Handles all server template API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.schemas import ServerTemplateCreate, ServerTemplateRead, ServerTemplateUpdate
from backend.app.deps import get_current_user
from backend.app.db.models import User
from backend.app.services.server_template_service import ServerTemplateService
from backend.app.exceptions import ResourceNotFoundException

router = APIRouter()


@router.post("/", response_model=ServerTemplateRead)
def create_server_template(
    template_in: ServerTemplateCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new server template
    """
    # Create the template
    template = ServerTemplateService.create_server_template(
        session=session,
        name=template_in.name,
        description=template_in.description,
        creator_id=current_user.id,
        guild_snapshot=template_in.guild_snapshot,
        icon_url=template_in.icon_url
    )
    
    return ServerTemplateRead(
        id=template.id,
        code=template.code,
        name=template.name,
        description=template.description,
        creator_id=template.creator_id,
        guild_snapshot=template.guild_snapshot,
        icon_url=template.icon_url,
        usage_count=template.usage_count,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.get("/{code}", response_model=ServerTemplateRead)
def get_server_template(
    code: str,
    current_user: User = Depends(get_current_user),  # Require authentication to access templates
    session: Session = Depends(get_session)
):
    """
    Get a server template by its code
    """
    template = ServerTemplateService.get_template_by_code(session, code)
    if not template:
        raise ResourceNotFoundException("Server Template", code)
    
    return ServerTemplateRead(
        id=template.id,
        code=template.code,
        name=template.name,
        description=template.description,
        creator_id=template.creator_id,
        guild_snapshot=template.guild_snapshot,
        icon_url=template.icon_url,
        usage_count=template.usage_count,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.get("/", response_model=List[ServerTemplateRead])
def get_server_templates(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all active server templates
    """
    templates = ServerTemplateService.get_all_active_templates(
        session=session,
        limit=limit,
        offset=offset
    )
    
    result = []
    for template in templates:
        result.append(ServerTemplateRead(
            id=template.id,
            code=template.code,
            name=template.name,
            description=template.description,
            creator_id=template.creator_id,
            guild_snapshot=template.guild_snapshot,
            icon_url=template.icon_url,
            usage_count=template.usage_count,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        ))
    
    return result


@router.get("/my-templates", response_model=List[ServerTemplateRead])
def get_my_server_templates(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all server templates created by the current user
    """
    templates = ServerTemplateService.get_templates_by_creator(
        session=session,
        creator_id=current_user.id
    )
    
    result = []
    for template in templates:
        result.append(ServerTemplateRead(
            id=template.id,
            code=template.code,
            name=template.name,
            description=template.description,
            creator_id=template.creator_id,
            guild_snapshot=template.guild_snapshot,
            icon_url=template.icon_url,
            usage_count=template.usage_count,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        ))
    
    return result


@router.put("/{template_id}", response_model=ServerTemplateRead)
def update_server_template(
    template_id: int,
    template_update: ServerTemplateUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a server template (only the creator can update it)
    """
    # Get the template
    template = session.get(ServerTemplate, template_id)
    if not template:
        raise ResourceNotFoundException("Server Template", template_id)
    
    # Check if the current user is the creator
    if template.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update templates you created")
    
    # Convert Pydantic model to dict, excluding unset values
    update_data = template_update.dict(exclude_unset=True)
    
    # Update the template
    updated_template = ServerTemplateService.update_template(
        session=session,
        template_id=template_id,
        update_data=update_data
    )
    
    if not updated_template:
        raise ResourceNotFoundException("Server Template", template_id)
    
    return ServerTemplateRead(
        id=updated_template.id,
        code=updated_template.code,
        name=updated_template.name,
        description=updated_template.description,
        creator_id=updated_template.creator_id,
        guild_snapshot=updated_template.guild_snapshot,
        icon_url=updated_template.icon_url,
        usage_count=updated_template.usage_count,
        is_active=updated_template.is_active,
        created_at=updated_template.created_at,
        updated_at=updated_template.updated_at
    )


@router.delete("/{template_id}")
def delete_server_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a server template (only the creator can delete it)
    """
    # Check if the template exists and belongs to the user
    template = session.get(ServerTemplate, template_id)
    if not template:
        raise ResourceNotFoundException("Server Template", template_id)
    
    if template.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete templates you created")
    
    # Delete the template
    success = ServerTemplateService.delete_template(
        session=session,
        template_id=template_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete template")
    
    return {"status": "template_deleted"}