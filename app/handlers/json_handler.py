"""
Handler for JSON manipulation questions.
"""

import json
import re
from typing import Dict, List, Any


class JSONHandler:
    """Handler for questions involving JSON data processing."""
    
    async def sort_json(self, json_str: str) -> str:
        """
        Sort a JSON array of objects by the specified fields.

        Args:
            json_str: JSON string to sort

        Returns:
            Sorted JSON string with no whitespace
        """
        try:
            # Clean up the JSON string if needed
            json_str = json_str.strip()

            # Parse the JSON data
            data = json.loads(json_str)

            # Check if the data is a list
            if not isinstance(data, list):
                return f"Error: Expected a JSON array, got {type(data).__name__}"

            # Determine sort keys based on the content
            has_age = any('age' in item for item in data if isinstance(item, dict))
            has_name = any('name' in item for item in data if isinstance(item, dict))

            # Sort by age and name if both exist
            if has_age and has_name:
                sorted_data = sorted(data, key=lambda x: (x.get('age', 0), x.get('name', '')))
            # Sort by age only
            elif has_age:
                sorted_data = sorted(data, key=lambda x: x.get('age', 0))
            # Sort by name only
            elif has_name:
                sorted_data = sorted(data, key=lambda x: x.get('name', ''))
            # Default to no sorting
            else:
                sorted_data = data

            # Convert back to JSON with no whitespace
            return json.dumps(sorted_data, separators=(',', ':'))

        except json.JSONDecodeError as e:
            return f"Error parsing JSON: {str(e)}"
        except Exception as e:
            return f"Error processing JSON: {str(e)}"

    async def extract_json_key(self, json_str: str, key_path: str) -> str:
        """
        Extract a value from JSON using a key path.

        Args:
            json_str: JSON string to process
            key_path: Path to the key (e.g., "data.results[0].name")

        Returns:
            Extracted value as a string
        """
        try:
            # Parse the JSON data
            data = json.loads(json_str)

            # Split the key path
            parts = re.findall(r'(\w+)|\[(\d+)\]', key_path)
            value = data

            # Navigate through the path
            for name, index in parts:
                if name:  # It's a key name
                    value = value.get(name, {})
                elif index:  # It's an array index
                    i = int(index)
                    if isinstance(value, list) and i < len(value):
                        value = value[i]
                    else:
                        return f"Error: Index {i} out of range"

            # Convert the result to a string
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            else:
                return str(value)

        except Exception as e:
            return f"Error extracting from JSON: {str(e)}"