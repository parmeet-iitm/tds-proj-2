"""
Handler for JSON processing questions.
"""

import json
import re
import hashlib
import httpx
from typing import Optional, Dict, Any


class JSONProcessorHandler:
    """Handler for questions involving JSON processing and transformation."""

    async def convert_keyvalue_to_json(self, file_path: str) -> str:
        """
        Convert a text file with key=value pairs to a JSON object.

        Args:
            file_path: Path to the text file

        Returns:
            The converted JSON string
        """
        try:
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract key=value pairs
            json_object = {}
            for line in content.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Try to convert value to appropriate data type
                    value = self._convert_value_type(value)
                    json_object[key.strip()] = value

            # Convert to JSON string
            json_string = json.dumps(json_object, separators=(',', ':'))
            return json_string

        except Exception as e:
            return f"Error converting key-value pairs to JSON: {str(e)}"

    def _convert_value_type(self, value: str) -> Any:
        """
        Convert string value to appropriate data type.

        Args:
            value: String value

        Returns:
            Converted value
        """
        # Try to convert to number
        if value.isdigit():
            return int(value)

        try:
            float_val = float(value)
            return float_val
        except ValueError:
            pass

        # Try to convert to boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # Try to convert to array
        if ',' in value:
            # Check if it might be an array
            items = value.split(',')
            if len(items) > 1:
                return [item.strip() for item in items]

        # Default to string
        return value

    async def get_json_hash(self, json_string: str) -> str:
        """
        Calculate hash for a JSON string using the tools-in-data-science.pages.dev/jsonhash service.

        Args:
            json_string: JSON string

        Returns:
            Hash result
        """
        try:
            # First, try to calculate it locally (same algorithm as the website)
            try:
                # This tries to mimic the website's hashing by normalizing JSON first
                json_obj = json.loads(json_string)
                normalized = json.dumps(json_obj, sort_keys=True, separators=(',', ':'))
                hash_value = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
                return hash_value
            except Exception as e:
                print(f"Local hash calculation failed: {str(e)}")

            # If local calculation fails, try to fetch from service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url="https://tools-in-data-science.pages.dev/api/jsonhash",
                    json={"data": json_string},
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("hash", "Error: No hash in response")
                else:
                    return f"Error from hash service: {response.status_code}"

        except Exception as e:
            return f"Error calculating JSON hash: {str(e)}"

    async def process_multi_cursor_json(self, file_path: str) -> str:
        """
        Process a multi-cursor JSON question.

        Args:
            file_path: Path to the text file

        Returns:
            The hash result
        """
        try:
            # Convert key=value pairs to JSON
            json_string = await self.convert_keyvalue_to_json(file_path)

            # Get hash for the JSON
            hash_result = await self.get_json_hash(json_string)

            return hash_result

        except Exception as e:
            return f"Error processing multi-cursor JSON: {str(e)}"