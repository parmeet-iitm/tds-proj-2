"""
Text processing utilities.
"""

import re
from typing import Optional, List, Any


def extract_pattern(text: str, pattern: str, flags: int = 0) -> Optional[str]:
    """
    Extract the first match of a pattern from text.
    
    Args:
        text: Text to search in
        pattern: Regular expression pattern
        flags: Regular expression flags
        
    Returns:
        Matched string or None if not found
    """
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1) if match.groups() else match.group(0)
    return None


def extract_all_patterns(text: str, pattern: str, flags: int = 0) -> List[str]:
    """
    Extract all matches of a pattern from text.
    
    Args:
        text: Text to search in
        pattern: Regular expression pattern
        flags: Regular expression flags
        
    Returns:
        List of matched strings
    """
    matches = re.findall(pattern, text, flags)
    if isinstance(matches[0], tuple) if matches else False:
        # If matches are tuples (groups), flatten them
        return [group for match in matches for group in match if group]
    return matches


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace, etc.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def extract_key_value_pairs(text: str) -> dict:
    """
    Extract key-value pairs from text.
    
    Args:
        text: Text containing key-value pairs
        
    Returns:
        Dictionary of key-value pairs
    """
    pairs = {}
    
    # Look for patterns like "key: value" or "key = value"
    pattern = r'(\w+)\s*[:=]\s*([^,\n]+)'
    matches = re.findall(pattern, text)
    
    for key, value in matches:
        pairs[key.strip()] = value.strip()
    
    return pairs


def extract_date_range(text: str) -> Optional[tuple]:
    """
    Extract a date range from text.
    
    Args:
        text: Text containing a date range
        
    Returns:
        Tuple of (start_date, end_date) or None if not found
    """
    # Try different date formats
    patterns = [
        # YYYY-MM-DD
        r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
        # MM/DD/YYYY
        r'(\d{1,2}/\d{1,2}/\d{4})\s+to\s+(\d{1,2}/\d{1,2}/\d{4})',
        # Month DD, YYYY
        r'([A-Z][a-z]+ \d{1,2}, \d{4})\s+to\s+([A-Z][a-z]+ \d{1,2}, \d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.groups()
    
    return None