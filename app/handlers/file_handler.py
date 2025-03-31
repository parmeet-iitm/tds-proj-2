"""
Handler for file processing questions.
"""

import os
import hashlib
import zipfile
import tempfile
import re
import subprocess
from typing import Optional, List


class FileHandler:
    """Handler for questions involving file operations."""
    
    async def calculate_hash(self, file_path: str) -> str:
        """
        Calculate the SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The SHA-256 hash as a string
        """
        try:
            # Use hashlib to calculate the hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files efficiently
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
        
        except Exception as e:
            return f"Error calculating hash: {str(e)}"
    
    async def extract_archive(self, archive_path: str) -> List[str]:
        """
        Extract an archive and return paths to extracted files.
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            List of paths to extracted files
        """
        try:
            # Create a temporary directory for extraction
            temp_dir = tempfile.mkdtemp()
            
            # Check if it's a ZIP file
            if archive_path.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            
            # Add support for other archive formats as needed
            
            # Return list of extracted files
            extracted_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    extracted_files.append(os.path.join(root, file))
            
            return extracted_files
        
        except Exception as e:
            return [f"Error extracting archive: {str(e)}"]
    
    async def find_text_in_file(self, file_path: str, pattern: str) -> str:
        """
        Search for a pattern in a text file.
        
        Args:
            file_path: Path to the file
            pattern: Regular expression pattern to search for
            
        Returns:
            Matched text or error message
        """
        try:
            # Check if the file is a text file
            if not self._is_text_file(file_path):
                return "Not a text file"
            
            # Read the file and search for the pattern
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                match = re.search(pattern, content)
                if match:
                    return match.group(0)
                else:
                    return "Pattern not found in the file"
        
        except Exception as e:
            return f"Error searching file: {str(e)}"
    
    def _is_text_file(self, file_path: str) -> bool:
        """
        Check if a file is a text file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a text file, False otherwise
        """
        # Check file extension
        text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
        if any(file_path.lower().endswith(ext) for ext in text_extensions):
            return True
        
        # Check content (read a small sample)
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(4096)
                # Files with null bytes are likely binary
                if b'\x00' in sample:
                    return False
                # Try to decode as UTF-8
                try:
                    sample.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except:
            return False