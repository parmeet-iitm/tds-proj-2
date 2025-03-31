"""
Utilities for extracting specific content from text.
"""

import re
from typing import Optional, List


class ContentExtractor:
    """
    Utilities for extracting specific content from text responses.
    """

    def extract_answer(self, text: str) -> str:
        """
        Extract a clean answer from AI response text.

        Args:
            text: Full text response from AI

        Returns:
            Cleaned answer text
        """
        # Remove starting phrases like "The answer is" or "Here's the answer:"
        cleaned_text = re.sub(r'^(the answer is|here\'s the answer|answer:|result:|solution:)',
                              '', text, flags=re.IGNORECASE)

        # Remove quotes if the entire text is quoted
        cleaned_text = re.sub(r'^"(.*)"$', r'\1', cleaned_text.strip())

        # Extract code blocks if present
        code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]+?)\s*```', text)
        if code_blocks:
            return code_blocks[0].strip()

        # Remove explanations and justifications
        cleaned_text = self._remove_explanations(cleaned_text)

        return cleaned_text.strip()

    def _remove_explanations(self, text: str) -> str:
        """
        Remove explanatory text and justifications.

        Args:
            text: Text to clean

        Returns:
            Text with explanations removed
        """
        # Split into lines
        lines = text.split('\n')
        cleaned_lines = []

        # Skip lines that look like explanations
        explanation_patterns = [
            r'^\s*explanation\s*:',
            r'^\s*I think',
            r'^\s*Based on',
            r'^\s*According to',
            r'^\s*This is because',
            r'^\s*Let me explain',
            r'^\s*To solve this'
        ]

        in_explanation = False

        for line in lines:
            # Check if line starts an explanation section
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in explanation_patterns):
                in_explanation = True
                continue

            # Skip if in explanation section
            if in_explanation:
                # Check if line might be ending the explanation
                if line.strip() == '' or line.strip().startswith('#') or line.strip().startswith('```'):
                    in_explanation = False
                else:
                    continue

            cleaned_lines.append(line)

        # Join the remaining lines
        return '\n'.join(cleaned_lines)

    def extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text in various formats.

        Args:
            text: Text to extract dates from

        Returns:
            List of extracted dates
        """
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}'  # Month DD, YYYY
        ]

        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))

        return dates

    def extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON from text.

        Args:
            text: Text to extract JSON from

        Returns:
            Extracted JSON string or None if not found
        """
        # Try to find JSON between markers
        json_patterns = [
            r'```(?:json)?\s*(\{[\s\S]*?\})\s*```',  # JSON in code block
            r'(\{[\s\S]*?\})'  # Bare JSON object
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]

        return None