"""
File Upload Router
Handles all file upload API endpoints
"""

import os
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.schemas import FileUploadResponse
from backend.app.deps import get_current_user
from backend.app.db.models import User, Message, DirectMessage
from backend.app.services.file_upload_service import FileUploadService
from backend.app.exceptions import ResourceNotFoundException


router = APIRouter()


@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    message_id: Optional[int] = Form(None),
    dm_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Upload a file to the server
    """
    # Validate inputs
    if message_id and dm_id:
        raise HTTPException(status_code=400, detail="Only one of message_id or dm_id can be provided")
    
    if not message_id and not dm_id:
        raise HTTPException(status_code=400, detail="Either message_id or dm_id must be provided")
    
    # Check if target exists
    if message_id:
        message = session.get(Message, message_id)
        if not message:
            raise ResourceNotFoundException("Message", message_id)
        # In a full implementation, we'd check if user has permission to upload to this channel
    elif dm_id:
        dm = session.get(DirectMessage, dm_id)
        if not dm:
            raise ResourceNotFoundException("Direct Message", dm_id)
        # Check if user is part of this DM
        if current_user.id not in [dm.sender_id, dm.recipient_id]:
            raise HTTPException(status_code=403, detail="Not authorized to upload to this DM")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file
    if not FileUploadService.validate_file(file.filename, file_size):
        raise HTTPException(
            status_code=400, 
            detail=f"File not allowed. Max size: {FileUploadService.MAX_FILE_SIZE/(1024*1024):.1f}MB. "
                   f"Allowed types: {', '.join(FileUploadService.get_allowed_extensions())}"
        )
    
    # Determine MIME type
    # This is a simplified approach - in production, use python-magic or similar
    ext = os.path.splitext(file.filename)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        mime_type = f"image/{ext[1:]}"  # Remove the dot
    elif ext == '.pdf':
        mime_type = "application/pdf"
    elif ext in ['.txt', '.doc', '.docx']:
        mime_type = "text/plain" if ext == '.txt' else f"application/{ext[1:]}"
    else:
        mime_type = "application/octet-stream"  # Default
    
    # Save file to server
    file_path = FileUploadService.save_uploaded_file(
        file_data=file_content,
        original_filename=file.filename,
        upload_dir="uploads"
    )
    
    # Create database record
    file_record = FileUploadService.create_file_record(
        session=session,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        uploader_id=current_user.id,
        message_id=message_id,
        dm_id=dm_id
    )
    
    return FileUploadResponse(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        file_path=file_record.file_path,
        file_size=file_record.file_size,
        mime_type=file_record.mime_type,
        uploader_id=file_record.uploader_id,
        message_id=file_record.message_id,
        dm_id=file_record.dm_id,
        uploaded_at=file_record.uploaded_at
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
def get_file_info(
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get information about an uploaded file
    """
    file_record = FileUploadService.get_file_by_id(session, file_id)
    if not file_record:
        raise ResourceNotFoundException("File", file_id)
    
    # Check if user has access to this file
    # A user can access a file if:
    # 1. They are the uploader
    # 2. The file is attached to a message in a channel they have access to
    # 3. The file is attached to a DM they are part of
    
    if file_record.uploader_id == current_user.id:
        # User uploaded this file, so they have access
        pass
    elif file_record.message_id:
        # Check if file is attached to a message in a channel
        # In a full implementation, we'd check channel permissions here
        pass
    elif file_record.dm_id:
        # Check if file is attached to a DM
        dm = session.get(DirectMessage, file_record.dm_id)
        if dm and current_user.id not in [dm.sender_id, dm.recipient_id]:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")
    
    return FileUploadResponse(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        file_path=file_record.file_path,
        file_size=file_record.file_size,
        mime_type=file_record.mime_type,
        uploader_id=file_record.uploader_id,
        message_id=file_record.message_id,
        dm_id=file_record.dm_id,
        uploaded_at=file_record.uploaded_at
    )


@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Download an uploaded file
    """
    file_record = FileUploadService.get_file_by_id(session, file_id)
    if not file_record:
        raise ResourceNotFoundException("File", file_id)
    
    # Check if user has access to this file (same logic as get_file_info)
    if file_record.uploader_id != current_user.id:
        if file_record.message_id:
            # In a full implementation, check channel permissions
            pass
        elif file_record.dm_id:
            dm = session.get(DirectMessage, file_record.dm_id)
            if dm and current_user.id not in [dm.sender_id, dm.recipient_id]:
                raise HTTPException(status_code=403, detail="Not authorized to access this file")
    
    # Check if file exists on disk
    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file for download
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_record.file_path,
        media_type=file_record.mime_type,
        filename=file_record.original_filename
    )


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete an uploaded file (only the uploader can delete)
    """
    file_record = FileUploadService.get_file_by_id(session, file_id)
    if not file_record:
        raise ResourceNotFoundException("File", file_id)
    
    # Only the uploader can delete the file
    if file_record.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the uploader can delete this file")
    
    # Delete the database record
    success = FileUploadService.delete_file_record(session, file_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file record")
    
    # Delete the physical file
    FileUploadService.delete_physical_file(file_record.file_path)
    
    return {"status": "file_deleted"}