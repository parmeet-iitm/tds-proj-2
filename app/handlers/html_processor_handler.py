"""
Handler for HTML processing questions.
"""

import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any


class HTMLProcessorHandler:
    """Handler for questions involving HTML processing and CSS selectors."""

    async def process_css_selector_question(self, file_path: str, selector: str, attribute: str = None) -> str:
        """
        Process a question about CSS selectors.

        Args:
            file_path: Path to the HTML file
            selector: CSS selector to use
            attribute: Attribute to extract (optional)

        Returns:
            Result of the query
        """
        try:
            # Extract hidden HTML content from the question or file
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                return "Error: No file provided for HTML processing"

            # Parse the HTML
            return await self._process_html_with_selector(html_content, selector, attribute)

        except Exception as e:
            return f"Error processing HTML: {str(e)}"

    async def _process_html_with_selector(self, html_content: str, selector: str, attribute: str = None) -> str:
        """
        Apply a CSS selector to HTML content and extract information.

        Args:
            html_content: HTML content
            selector: CSS selector to use
            attribute: Attribute to extract (optional)

        Returns:
            Result of the query
        """
        try:
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find elements matching the selector
            elements = soup.select(selector)

            if not elements:
                return f"No elements found matching selector '{selector}'"

            # If an attribute is specified, extract and process it
            if attribute:
                # Special case for data attributes
                if attribute.startswith('data-'):
                    # Check if we need to sum numeric values
                    values = []
                    for element in elements:
                        attr_value = element.get(attribute)
                        if attr_value:
                            try:
                                # Try to convert to number
                                values.append(float(attr_value))
                            except ValueError:
                                values.append(attr_value)

                    # If all values are numeric, sum them
                    if values and all(isinstance(v, (int, float)) for v in values):
                        total = sum(values)
                        # Return as integer if it's a whole number
                        if total.is_integer():
                            return str(int(total))
                        return str(total)
                    else:
                        return ", ".join(str(v) for v in values)
                else:
                    # Extract regular attribute values
                    values = [element.get(attribute, "") for element in elements]
                    return ", ".join(values)
            else:
                # Just return the count if no attribute specified
                return str(len(elements))

        except Exception as e:
            return f"Error processing HTML with selector: {str(e)}"

    def _extract_hidden_html(self, text: str) -> Optional[str]:
        """
        Extract hidden HTML content from text.

        Args:
            text: Text that might contain HTML

        Returns:
            Extracted HTML or None if not found
        """
        # Try to find HTML content between markers
        html_patterns = [
            r'<div[^>]*>([\s\S]*?)</div>',
            r'<html[^>]*>([\s\S]*?)</html>',
            r'<!-- HTML content -->([\s\S]*?)<!--',
            r'```html\s*([\s\S]*?)\s*```'
        ]

        for pattern in html_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the largest match (most likely the complete HTML)
                return max(matches, key=len)

        return None