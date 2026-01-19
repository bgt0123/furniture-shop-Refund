"""File storage integration for evidence photos"""

import os
import uuid
from typing import List, Optional
from fastapi import UploadFile


class FileStorageService:
    """Service for handling file uploads and storage for evidence photos"""

    def __init__(self, upload_dir: str = "uploads"):
        """Initialize with upload directory"""
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file and return file path"""
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return file_path

    async def save_multiple_files(self, files: List[UploadFile]) -> List[str]:
        """Save multiple uploaded files"""
        file_paths = []
        for file in files:
            file_path = await self.save_file(file)
            file_paths.append(file_path)
        
        return file_paths

    def get_file_url(self, file_path: str) -> str:
        """Generate URL for accessing stored file"""
        # In production, this would return a proper URL
        # For development, return file path
        return f"/files/{os.path.basename(file_path)}"

    def delete_file(self, file_path: str) -> bool:
        """Delete stored file"""
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False

    def validate_file_type(self, file: UploadFile, allowed_types: List[str]) -> bool:
        """Validate file type"""
        if not file.filename:
            return False
        
        file_extension = file.filename.split('.')[-1].lower()
        return file_extension in allowed_types

    def validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Read file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start
        
        return file_size <= max_size_bytes