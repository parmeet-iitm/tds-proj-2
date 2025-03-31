"""
Handler for CSV extraction questions.
"""

import os
import zipfile
import tempfile
import pandas as pd
import re
from typing import Optional


class CSVHandler:
    """Handler for questions involving CSV file extraction and analysis."""
    
    async def process(self, question: str, file_path: str) -> str:
        """
        Process a CSV-related question.
        
        Args:
            question: The question text
            file_path: Path to the uploaded file
            
        Returns:
            The extracted answer
        """
        # Check if we need to extract a specific column
        column = "answer"  # Default column
        column_match = re.search(r'\"(\w+)\"', question)
        if column_match:
            column = column_match.group(1)
        
        # Process file based on its type
        if file_path.lower().endswith('.zip'):
            return await self.extract_from_zip(file_path, column)
        elif file_path.lower().endswith('.csv'):
            return await self.extract_from_csv(file_path, column)
        else:
            return "Unsupported file format. Please provide a ZIP or CSV file."
    
    async def extract_from_zip(self, zip_path: str, column: str) -> str:
        """
        Extract data from a CSV file inside a ZIP archive.
        
        Args:
            zip_path: Path to the ZIP file
            column: Name of the column to extract
            
        Returns:
            The extracted value or error message
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find CSV files in the extracted contents
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith('.csv'):
                            csv_path = os.path.join(root, file)
                            return await self.extract_from_csv(csv_path, column)
                
                return "No CSV file found in the ZIP archive."
        
        except Exception as e:
            return f"Error extracting from ZIP: {str(e)}"
    
    async def extract_from_csv(self, csv_path: str, column: str) -> str:
        """
        Extract data from a CSV file.
        
        Args:
            csv_path: Path to the CSV file
            column: Name of the column to extract
            
        Returns:
            The extracted value or error message
        """
        try:
            # Try different encodings to handle potential encoding issues
            encodings = ['utf-8', 'latin1', 'cp1252']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                # Last resort: read with error handling
                df = pd.read_csv(csv_path, encoding='utf-8', errors='replace')

            # Check if the requested column exists
            if column in df.columns:
                # Return the first value in the column
                return str(df[column].iloc[0])

            # If the exact column name doesn't exist, try case-insensitive matching
            column_lower = column.lower()
            for col in df.columns:
                if col.lower() == column_lower:
                    return str(df[col].iloc[0])

            # If column doesn't exist, list available columns
            columns = ", ".join(df.columns)
            return f"Column '{column}' not found. Available columns: {columns}"

        except Exception as e:
            return f"Error reading CSV file: {str(e)}"