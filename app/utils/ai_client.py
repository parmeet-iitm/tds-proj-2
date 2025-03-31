"""
Client for interacting with AI services.
"""

import json
import httpx
import os
from typing import Dict, List, Optional, Any


class AIClient:
    """
    Client for making requests to AI services.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI client.

        Args:
            api_key: API key for the AI service
        """
        self.api_key = api_key

        # Default to OPENAI_API_KEY environment variable if no key provided
        if not self.api_key:
            self.api_key = os.environ.get("AIPROXY_TOKEN")

        # Define base URL and headers
        self.base_url = "https://api.openai.com/v1/chat/completions"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

        # Default model to use
        self.model = "gpt-3.5-turbo"

    async def call_basic(self, system_prompt: str, user_prompt: str,
                         temperature: float = 0.0) -> str:
        """
        Make a basic call to the AI service.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User query/content
            temperature: Controls randomness (0.0 to 1.0)

        Returns:
            AI response text
        """
        if not self.api_key:
            return "AI service API key not configured"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.base_url,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": temperature
                    },
                    timeout=30.0
                )

                # Check response status
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_info = response.json() if response.content else {"error": "Unknown error"}
                    return f"Error from AI service: {response.status_code}, {error_info}"

        except Exception as e:
            return f"Error connecting to AI service: {str(e)}"

    async def call_with_function(self, system_prompt: str, user_prompt: str,
                                 function_schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a call to the AI service with function calling.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User query/content
            function_schema: Schema of the function to call

        Returns:
            Function call arguments as a dictionary, or None if unsuccessful
        """
        if not self.api_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.base_url,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "functions": [function_schema],
                        "function_call": {"name": function_schema["name"]}
                    },
                    timeout=30.0
                )

                # Check response status
                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]

                    # Extract function call
                    if "function_call" in message:
                        function_call = message["function_call"]
                        if "arguments" in function_call:
                            try:
                                return json.loads(function_call["arguments"])
                            except json.JSONDecodeError:
                                print("Error parsing function arguments")
                                return None

                return None

        except Exception as e:
            print(f"Error in function call: {str(e)}")
            return None