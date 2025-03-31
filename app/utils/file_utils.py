"""
File handling utilities.
"""

import os
import shutil
import tempfile
import zipfile
from fastapi import UploadFile
from typing import Optional, List


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save an uploaded file to a temporary location.

    Args:
        upload_file: FastAPI UploadFile object

    Returns:
        Path to the saved temporary file
    """
    # Create a unique temporary file name
    temp_file = f"temp_{upload_file.filename}"

    # Save the file
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # Return the path to the saved file
    return temp_file


def cleanup_temp_file(file_path: str) -> None:
    """
    Delete a temporary file if it exists.

    Args:
        file_path: Path to the file to be deleted
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting temporary file {file_path}: {str(e)}")


async def get_file_type(file_path: str) -> str:
    """
    Determine the type of file based on extension and content.

    Args:
        file_path: Path to the file

    Returns:
        File type as a string (e.g., "zip", "csv", "text")
    """
    # Check extension first
    ext = os.path.splitext(file_path)[1].lower()

    # Handle common file types
    if ext in ['.zip', '.gz', '.tar']:
        return "archive"
    elif ext in ['.csv']:
        return "csv"
    elif ext in ['.json']:
        return "json"
    elif ext in ['.txt', '.md']:
        return "text"

    # Check content for ambiguous cases
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)

            # Check for ZIP header
            if header.startswith(b'PK\x03\x04'):
                return "archive"

            # Check for CSV-like content (text with commas)
            f.seek(0)
            content = f.read(1024).decode('utf-8', errors='ignore')
            if ',' in content and '\n' in content:
                return "csv"

    except Exception:
        pass

    # Default to "binary" if unable to determine
    return "binary"


async def extract_from_zip(zip_path: str, extract_path: Optional[str] = None) -> str:
    """
    Extract contents from a ZIP file.

    Args:
        zip_path: Path to the ZIP file
        extract_path: Path to extract to (if None, creates a temporary directory)

    Returns:
        Path to the extracted directory
    """
    # Create temporary directory if extract_path is not provided
    if extract_path is None:
        extract_path = tempfile.mkdtemp()

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path


async def find_file_by_extension(directory: str, extension: str) -> Optional[str]:
    """
    Find the first file with a specific extension in a directory (recursive).

    Args:
        directory: Path to search in
        extension: File extension to look for (e.g., '.csv')

    Returns:
        Path to the found file or None if not found
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extension.lower()):
                return os.path.join(root, file)

    return None


async def read_file_content(file_path: str, max_size: int = 1024 * 1024) -> Optional[str]:
    """
    Read the content of a text file with size limitation.

    Args:
        file_path: Path to the file
        max_size: Maximum size to read in bytes

    Returns:
        File content as string or None if file is not readable as text
    """
    try:
        # Check file size first
        file_size = os.path.getsize(file_path)
        size_to_read = min(file_size, max_size)

        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read(size_to_read)
                    if file_size > max_size:
                        content += "\n...[content truncated]..."
                    return content
            except UnicodeDecodeError:
                continue

        # If all encodings fail, read as binary and try to decode
        with open(file_path, 'rb') as f:
            binary_content = f.read(size_to_read)
            try:
                content = binary_content.decode('utf-8', errors='replace')
                if file_size > max_size:
                    content += "\n...[content truncated]..."
                return content
            except:
                return None  # Not a text file

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None


async def list_files_in_directory(directory: str) -> List[str]:
    """
    List all files in a directory and its subdirectories.

    Args:
        directory: Path to the directory

    Returns:
        List of file paths
    """
    file_list = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))

    return file_list