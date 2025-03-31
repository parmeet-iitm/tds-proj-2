"""
Handler for command execution questions.
"""

import os
import re
import subprocess
import tempfile
import shutil
from typing import Optional, Tuple, List


class CommandHandler:
    """Handler for questions involving command execution."""

    # Define allowed commands for security
    ALLOWED_COMMANDS = {
        "npx": {
            "allowed_args": ["-y", "prettier@3.4.2"],
            "allowed_files": [".md", ".js", ".json", ".html", ".css"]
        },
        "sha256sum": {
            "allowed_args": [],
            "allowed_files": ["*"]  # Allow any file for sha256sum
        }
    }

    async def process_command_question(self, question: str, file_path: Optional[str]) -> str:
        """
        Process a question requiring command execution.

        Args:
            question: Question text
            file_path: Path to the uploaded file

        Returns:
            Command output as a string
        """
        if not file_path:
            return "Error: No file was uploaded for command execution."

        # Extract commands from the question
        commands = self._extract_commands(question)
        if not commands:
            return "Error: Could not identify command to execute from question."

        # Create a temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the uploaded file to the temp directory
            file_name = os.path.basename(file_path)
            temp_file_path = os.path.join(temp_dir, file_name)
            shutil.copy(file_path, temp_file_path)

            # Execute the commands
            result = await self._execute_commands(commands, temp_dir, file_name)
            return result

    def _extract_commands(self, question: str) -> List[str]:
        """
        Extract command lines from the question.

        Args:
            question: Question text

        Returns:
            List of command strings
        """
        # Look for common command patterns
        command_patterns = [
            r'run\s+([\w\s\-@\.|\d]+)\.\s+What',
            r'execute\s+([\w\s\-@\.|\d]+)\.\s+What',
            r'command[:\s]+([\w\s\-@\.|\d]+)\.\s+What'
        ]

        for pattern in command_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                command_text = match.group(1).strip()

                # Split piped commands
                if '|' in command_text:
                    return [cmd.strip() for cmd in command_text.split('|')]
                else:
                    return [command_text]

        return []

    async def _execute_commands(self, commands: List[str], working_dir: str, file_name: str) -> str:
        """
        Execute a list of commands in sequence, piping output between them.

        Args:
            commands: List of command strings
            working_dir: Directory to execute commands in
            file_name: Name of the file to operate on

        Returns:
            Final command output
        """
        try:
            result = None

            for cmd_str in commands:
                # Parse the command
                cmd_parts = cmd_str.split()
                command = cmd_parts[0]

                # Replace file placeholder if present
                for i in range(len(cmd_parts)):
                    if cmd_parts[i] == "$FILE" or cmd_parts[i] == "{file}":
                        cmd_parts[i] = file_name

                # Check if the command is allowed
                if command not in self.ALLOWED_COMMANDS:
                    return f"Error: Command '{command}' is not allowed for security reasons."

                # Build the final command based on the allowed list
                allowed_config = self.ALLOWED_COMMANDS[command]
                final_cmd = [command]

                # Add allowed arguments
                for arg in cmd_parts[1:]:
                    if arg == file_name:
                        final_cmd.append(arg)
                    elif arg in allowed_config["allowed_args"] or arg.startswith("--"):
                        final_cmd.append(arg)
                    elif command == "npx" and "@" in arg:  # Special case for npx packages
                        if any(allowed_pkg in arg for allowed_pkg in allowed_config["allowed_args"]):
                            final_cmd.append(arg)
                        else:
                            return f"Error: Package '{arg}' is not allowed for security reasons."

                # Execute the command
                if result is None:
                    # First command in the pipe
                    process = subprocess.run(
                        final_cmd,
                        cwd=working_dir,
                        capture_output=True,
                        text=True
                    )
                    result = process.stdout

                    # Check for errors
                    if process.returncode != 0:
                        return f"Error executing {command}: {process.stderr}"
                else:
                    # Pipe previous result to this command
                    process = subprocess.run(
                        final_cmd,
                        cwd=working_dir,
                        input=result,
                        capture_output=True,
                        text=True
                    )
                    result = process.stdout

                    # Check for errors
                    if process.returncode != 0:
                        return f"Error executing {command}: {process.stderr}"

            return result.strip()

        except Exception as e:
            return f"Error executing commands: {str(e)}"

    async def test_npx_prettier(self, file_path: str) -> str:
        """
        Run npx prettier and sha256sum on a file.

        Args:
            file_path: Path to the file

        Returns:
            Command output as a string
        """
        # Special handler for the npx prettier | sha256sum case
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy the uploaded file
                file_name = os.path.basename(file_path)
                temp_file_path = os.path.join(temp_dir, file_name)
                shutil.copy(file_path, temp_file_path)

                # Run npx prettier
                prettier_process = subprocess.run(
                    ["npx", "-y", "prettier@3.4.2", file_name],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )

                if prettier_process.returncode != 0:
                    return f"Error running prettier: {prettier_process.stderr}"

                # Pipe output to sha256sum
                sha_process = subprocess.run(
                    ["sha256sum"],
                    cwd=temp_dir,
                    input=prettier_process.stdout,
                    capture_output=True,
                    text=True
                )

                if sha_process.returncode != 0:
                    return f"Error running sha256sum: {sha_process.stderr}"

                return sha_process.stdout.strip()

        except Exception as e:
            return f"Error running npx prettier | sha256sum: {str(e)}"