import os
import shutil
import uuid
from typing import Optional
from fastapi import UploadFile
from app.config import settings


class ProjectService:
    def save_source_code(self, file: UploadFile) -> str:
        """
        Saves the uploaded file to the configured UPLOAD_DIR.
        Generates a unique sub-directory to prevent filename collisions.
        Returns the relative path where the file is stored.
        """
        # Ensure upload root directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Create a unique subfolder
        unique_id = uuid.uuid4().hex
        folder_path = os.path.join(settings.UPLOAD_DIR, unique_id)
        os.makedirs(folder_path, exist_ok=True)

        # Save the file
        file_path = os.path.join(folder_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return relative path for database storage
        # Using forward slashes for cross-platform compatibility in path string
        return f"{settings.UPLOAD_DIR}/{unique_id}/{file.filename}"

    def delete_source_code(self, source_code_path: Optional[str]) -> None:
        """
        Deletes the file and its enclosing unique directory from the filesystem if it exists.
        """
        if not source_code_path:
            return

        # Get the directory of the file (since we saved in unique subfolder)
        folder_path = os.path.dirname(source_code_path)
        
        # Verify it is indeed within settings.UPLOAD_DIR to prevent directory traversal deletions
        normalized_upload_dir = os.path.normpath(settings.UPLOAD_DIR)
        normalized_folder_path = os.path.normpath(folder_path)
        
        if normalized_folder_path.startswith(normalized_upload_dir) and os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                # Log or handle file deletion error gracefully
                print(f"[WARNING] Failed to delete directory {folder_path}: {e}")


project_service = ProjectService()
