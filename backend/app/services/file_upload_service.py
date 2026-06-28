"""
File Upload Service Module
Handles all file upload-related business logic
"""

import os
import uuid
from typing import Optional
from pathlib import Path
from sqlmodel import Session
from backend.app.db.models import UploadedFile


class FileUploadService:
    # Maximum file size: 25MB
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    # Allowed file types
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'other': ['.zip', '.rar', '.tar', '.gz']
    }
    
    @classmethod
    def get_allowed_extensions(cls):
        """Get all allowed file extensions"""
        all_extensions = []
        for category in cls.ALLOWED_EXTENSIONS.values():
            all_extensions.extend(category)
        return all_extensions

    @staticmethod
    def save_uploaded_file(file_data: bytes, original_filename: str, upload_dir: str = "uploads") -> str:
        """
        Save an uploaded file to the server
        Returns the path where the file was saved
        """
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename to prevent conflicts
        file_extension = Path(original_filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        return file_path

    @staticmethod
    def validate_file(original_filename: str, file_size: int) -> bool:
        """
        Validate if a file meets the requirements
        """
        # Check file size
        if file_size > FileUploadService.MAX_FILE_SIZE:
            return False
        
        # Check file extension
        file_extension = Path(original_filename).suffix.lower()
        if file_extension not in FileUploadService.get_allowed_extensions():
            return False
        
        return True

    @staticmethod
    def create_file_record(
        session: Session,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        uploader_id: int,
        message_id: Optional[int] = None,
        dm_id: Optional[int] = None
    ) -> UploadedFile:
        """
        Create a record for an uploaded file in the database
        """
        # Extract just the filename from the path for the filename field
        filename = Path(file_path).name
        
        file_record = UploadedFile(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            uploader_id=uploader_id,
            message_id=message_id,
            dm_id=dm_id
        )
        
        session.add(file_record)
        session.commit()
        session.refresh(file_record)
        
        return file_record

    @staticmethod
    def get_file_by_id(session: Session, file_id: int) -> Optional[UploadedFile]:
        """
        Get a file record by its ID
        """
        return session.get(UploadedFile, file_id)

    @staticmethod
    def delete_file_record(session: Session, file_id: int) -> bool:
        """
        Delete a file record from the database
        NOTE: This does not delete the actual file from disk
        """
        file_record = session.get(UploadedFile, file_id)
        if file_record:
            session.delete(file_record)
            session.commit()
            return True
        return False

    @staticmethod
    def delete_physical_file(file_path: str) -> bool:
        """
        Delete the physical file from disk
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except:
            return False