"""
Core question processing logic for the TDS Assignment Solver.
AI-powered processor that analyzes and solves TDS assignment questions.
"""

import re
import os
import httpx
import json
from typing import Dict, List, Optional, Tuple, Any

from app.handlers.csv_handler import CSVHandler
from app.handlers.date_handler import DateHandler
from app.handlers.json_handler import JSONHandler
from app.handlers.file_handler import FileHandler
from app.handlers.command_handler import CommandHandler
from app.handlers.json_processor_handler import JSONProcessorHandler
from app.utils.text_utils import extract_pattern
from app.utils.file_utils import extract_from_zip, find_file_by_extension


class QuestionProcessor:
    """
    AI-powered processor for TDS assignment questions. Analyzes the question
    using AI and uses specialized handlers to process specific tasks.
    """

    def __init__(self, ai_proxy_token: Optional[str] = None):
        """
        Initialize the question processor with an AI proxy token.

        Args:
            ai_proxy_token: API token for the AI proxy service
        """
        # Initialize specialized handlers
        self.csv_handler = CSVHandler()
        self.date_handler = DateHandler()
        self.json_handler = JSONHandler()
        self.file_handler = FileHandler()
        self.command_handler = CommandHandler()
        self.json_processor_handler = JSONProcessorHandler()

        # Set up AI
        self.ai_proxy_token = ai_proxy_token or os.environ.get("AIPROXY_TOKEN")
        self.ai_proxy_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

        # Configure request headers
        self.headers = {
            "Authorization": f"Bearer {self.ai_proxy_token}" if self.ai_proxy_token else "",
            "Content-Type": "application/json",
        }

        # Function definition for question analysis
        self.question_analysis_function = {
            "name": "analyze_question",
            "description": "Analyze a TDS (Tools in Data Science) assignment question to determine the best approach to solve it",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_type": {
                        "type": "string",
                        "description": "The type of question (e.g., 'csv_extraction', 'date_calculation', 'json_sorting', 'command_execution', 'json_processing', etc.)"
                    },
                    "actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of actions needed to solve (e.g., ['process_file', 'specialized_calculation', 'execute_command', 'process_json'])"
                    },
                    "direct_answer": {
                        "type": "string",
                        "description": "If you know the exact answer, provide it here, otherwise leave empty"
                    },
                    "calculation_type": {
                        "type": "string",
                        "description": "For specialized calculations, specify the type (e.g., 'count_wednesdays')"
                    },
                    "date_range": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "For date calculations, provide the date range as an array of strings"
                    },
                    "json_data": {
                        "type": "string",
                        "description": "For JSON operations, provide the JSON string"
                    },
                    "file_requirements": {
                        "type": "string",
                        "description": "Description of what to extract from the file"
                    },
                    "column_to_extract": {
                        "type": "string",
                        "description": "For CSV files, the name of the column to extract"
                    },
                    "command_to_execute": {
                        "type": "string",
                        "description": "For command execution questions, the command to run"
                    }
                },
                "required": ["question_type", "actions"],
                "additionalProperties": False
            }
        }

    async def process_question(self, question: str, file_path: Optional[str] = None) -> str:
        """
        Process a question using AI and specialized handlers as needed.

        Args:
            question: The question text
            file_path: Optional path to an uploaded file

        Returns:
            The answer to the question
        """
        # Handle specific patterns directly before AI analysis
        # This helps with cases where the AI might not correctly identify question types

        # Command execution for npx prettier and sha256sum
        if file_path and (
            "npx" in question.lower() and "prettier" in question.lower() and "sha256sum" in question.lower()
        ):
            return await self.command_handler.test_npx_prettier(file_path)

        # Multi-cursor JSON processing
        if file_path and (
            "multi-cursor" in question.lower() and "json" in question.lower() and
            ("jsonhash" in question.lower() or "hash" in question.lower())
        ):
            return await self.json_processor_handler.process_multi_cursor_json(file_path)

        # First, analyze the question with AI to determine approach
        analysis = await self._analyze_question_with_ai(question, file_path)

        # Check if we need to process a file
        if file_path and "process_file" in analysis.get("actions", []):
            file_content = await self._process_file(file_path, analysis)

            # Update the analysis with file content
            if file_content:
                analysis["file_content"] = file_content

        # Process command execution if needed
        if "execute_command" in analysis.get("actions", []):
            return await self.command_handler.process_command_question(question, file_path)

        # Process JSON processing if needed
        if "process_json" in analysis.get("actions", []) and file_path:
            if "multi-cursor" in question.lower() and "jsonhash" in question.lower():
                return await self.json_processor_handler.process_multi_cursor_json(file_path)

        # Process specialized calculations if needed
        if "specialized_calculation" in analysis.get("actions", []):
            calculation_type = analysis.get("calculation_type")

            if calculation_type == "count_wednesdays":
                date_range = analysis.get("date_range")
                if date_range and len(date_range) == 2:
                    return await self.date_handler.count_wednesdays(date_range[0], date_range[1])

            elif calculation_type == "json_sorting":
                json_str = analysis.get("json_data")
                if json_str:
                    return await self.json_handler.sort_json(json_str)

        # If we have a direct answer from analysis, use it
        if "direct_answer" in analysis and analysis["direct_answer"]:
            return analysis["direct_answer"]

        # Otherwise, get final answer from AI with all available information
        return await self._get_final_answer_with_ai(question, analysis)

    async def _analyze_question_with_ai(self, question: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Use AI to analyze the question and determine the best approach using function calling.

        Args:
            question: The question text
            file_path: Optional path to an uploaded file

        Returns:
            Dictionary containing analysis results
        """
        if not self.ai_proxy_token:
            return {
                "error": "AI Proxy token not configured",
                "actions": []
            }

        # Create a prompt for analysis
        prompt = self._create_analysis_prompt(question, file_path)

        try:
            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.ai_proxy_url,
                    headers=self.headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an AI assistant that helps solve questions from the Tools in Data Science course. Your task is to analyze questions and determine the best approach to solve them."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "tools": [
                            {
                                "type": "function",
                                "function": self.question_analysis_function
                            }
                        ],
                        "tool_choice": "auto"
                    },
                    timeout=60.0
                )

            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()

                # Extract the analysis from the response
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]

                    if "tool_calls" in message and len(message["tool_calls"]) > 0:
                        function_call = message["tool_calls"][0]["function"]
                        if "arguments" in function_call:
                            try:
                                analysis = json.loads(function_call["arguments"])
                                return analysis
                            except json.JSONDecodeError:
                                return {"error": "Failed to parse AI response", "actions": []}

                return {"error": "Failed to extract analysis from AI response", "actions": []}
            else:
                return {"error": f"Error from AI service: Status {response.status_code}", "actions": []}

        except Exception as e:
            return {"error": f"Error connecting to AI service: {str(e)}", "actions": []}

    async def _process_file(self, file_path: str, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Process an uploaded file based on analysis.

        Args:
            file_path: Path to the file
            analysis: Question analysis from AI

        Returns:
            File content or extracted data as needed
        """
        # Check file type
        question_type = analysis.get("question_type", "unknown")

        if question_type == "csv_extraction":
            column = analysis.get("column_to_extract", "answer")

            # If it's a ZIP file, extract it first
            if file_path.lower().endswith('.zip'):
                # Extract the ZIP file
                temp_dir = await extract_from_zip(file_path)

                # Find CSV file
                csv_file = await find_file_by_extension(temp_dir, '.csv')

                if csv_file:
                    return await self.csv_handler.extract_from_csv(csv_file, column)

            # If it's directly a CSV file
            elif file_path.lower().endswith('.csv'):
                return await self.csv_handler.extract_from_csv(file_path, column)

        # For other file types, just read the content
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()

                # Truncate if too large
                max_length = 8000
                if len(content) > max_length:
                    return content[:max_length] + "\n...[content truncated]..."
                return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def _get_final_answer_with_ai(self, question: str, analysis: Dict[str, Any]) -> str:
        """
        Get the final answer using AI with all available information.

        Args:
            question: The original question
            analysis: Question analysis including any processed data

        Returns:
            The final answer
        """
        if not self.ai_proxy_token:
            return "AI Proxy token not configured. Please set the AIPROXY_TOKEN environment variable."

        # Create the final prompt with all available information
        prompt = self._create_final_prompt(question, analysis)

        try:
            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.ai_proxy_url,
                    headers=self.headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an AI assistant that helps solve questions from the Tools in Data Science course. Your answers should be concise, accurate, and directly provide the solution without explanation."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0
                    },
                    timeout=60.0
                )

            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()

                # Extract the answer from the response
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"].strip()
                    return self._extract_final_answer(answer)
                else:
                    return "Failed to extract answer from AI response"
            else:
                return f"Error from AI service: Status {response.status_code}, {response.text}"

        except Exception as e:
            return f"Error connecting to AI service: {str(e)}"

    def _create_analysis_prompt(self, question: str, file_path: Optional[str] = None) -> str:
        """
        Create a prompt for the AI to analyze the question.

        Args:
            question: The question text
            file_path: Optional path to an uploaded file

        Returns:
            Analysis prompt
        """
        prompt = """You are an expert data science tool assistant that solves TDS (Tools in Data Science) assignment questions.

Please analyze this question from a TDS graded assignment:

Question: """
        prompt += question + "\n\n"

        if file_path:
            prompt += f"A file was uploaded named: {os.path.basename(file_path)}\n\n"

        prompt += """The question might involve various tasks including:
- Running commands (like npx, sha256sum) and reporting the output
- Extracting data from CSV files
- Counting dates (like Wednesdays between date ranges)
- Sorting JSON data
- Calculating file hashes
- Working with GitHub URLs
- Working with Docker Hub
- Finding information in specific columns
- Converting key-value pairs to JSON objects
- Etc.

Your task is to analyze the question and determine:
1. What type of question this is
2. What actions are needed to solve it
3. What specific calculations or extractions are needed
4. If you already know the exact answer, provide it

Pay special attention to questions involving command execution, like running npx, prettier, or sha256sum.
If the question mentions running a command on a file, identify it as a command_execution type.

Also look for questions about multi-cursor operations, JSON conversions, or anything involving jsonhash.

Be specific and precise in your analysis.
"""

        return prompt

    def _create_final_prompt(self, question: str, analysis: Dict[str, Any]) -> str:
        """
        Create a prompt for the AI to provide the final answer.

        Args:
            question: The original question
            analysis: Question analysis including any processed data

        Returns:
            Final answer prompt
        """
        prompt = """You are an expert at solving TDS assignment questions. I need to solve this question:

"""
        prompt += question + "\n\n"

        # Add file content if available
        if "file_content" in analysis and analysis["file_content"]:
            prompt += "Here is the content of the file:\n\n"
            prompt += analysis["file_content"] + "\n\n"

        # Add error information if present
        if "error" in analysis and analysis["error"]:
            prompt += f"Note: There was an issue during processing: {analysis['error']}\n\n"

        if "question_type" in analysis:
            prompt += f"This appears to be a {analysis['question_type']} question.\n\n"

        if "direct_answer" in analysis and analysis["direct_answer"]:
            prompt += f"Based on the analysis, the answer might be: {analysis['direct_answer']}\n\n"

        prompt += """Please provide ONLY the answer without any explanation. The answer should be directly usable as a submission for the assignment question. 

Do not include phrases like "The answer is" or "Here's the answer". Just provide the exact answer.
"""

        return prompt

    def _extract_final_answer(self, response: str) -> str:
        """
        Extract the final answer from the AI response.

        Args:
            response: The full response from the AI

        Returns:
            The extracted answer
        """
        # Remove any explanations or unnecessary text
        lines = response.strip().split('\n')

        # If the response contains "Answer:" or similar, extract just that part
        for i, line in enumerate(lines):
            if line.lower().startswith(("answer:", "the answer is:", "result:")):
                return line.split(":", 1)[1].strip()

        # If there's a code block, extract it
        if "```" in response:
            code_blocks = []
            in_code_block = False

            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    continue

                if in_code_block:
                    code_blocks.append(line)

            if code_blocks:
                return "\n".join(code_blocks)

        # Default to returning the full response if we can't extract a specific answer
        # But remove any introductory text
        clean_lines = []
        started = False

        for line in lines:
            # Skip introductory text
            if not started and any(phrase in line.lower() for phrase in
                                   ["here's", "to solve", "i'll", "let me", "first", "based on"]):
                continue

            started = True
            clean_lines.append(line)

        if clean_lines:
            return "\n".join(clean_lines)

        # Fall back to the original response
        return response