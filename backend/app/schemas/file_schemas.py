"""
File Upload Schemas
Defines the data structures for file uploads
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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