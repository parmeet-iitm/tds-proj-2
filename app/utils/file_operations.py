"""
File handling utilities for the Assignment Helper API.
"""

import os
import uuid
import shutil
from fastapi import UploadFile
from typing import Optional


async def store_uploaded_file(upload_file: UploadFile) -> str:
    """
    Store an uploaded file with a unique filename.

    Args:
        upload_file: FastAPI UploadFile object

    Returns:
        Path to the stored file
    """
    # Create a unique filename using UUID to avoid collisions
    unique_id = str(uuid.uuid4())
    original_filename = upload_file.filename or "unknown"

    # Extract file extension
    _, file_extension = os.path.splitext(original_filename)

    # Create directory for uploads if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Create full path with unique filename
    temp_file_path = os.path.join("uploads", f"{unique_id}{file_extension}")

    # Save the file
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return temp_file_path


async def remove_temp_file(file_path: str) -> None:
    """
    Safely remove a temporary file.

    Args:
        file_path: Path to the file to be removed
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)

            # If file was in uploads directory and directory is empty, clean it up
            directory = os.path.dirname(file_path)
            if directory == "uploads" and not os.listdir(directory):
                os.rmdir(directory)

    except Exception as e:
        print(f"Error removing temporary file {file_path}: {str(e)}")


async def get_file_info(file_path: str) -> dict:
    """
    Get basic information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        return {
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "extension": os.path.splitext(file_path)[1].lower(),
            "path": file_path
        }
    except Exception as e:
        return {"error": str(e)}