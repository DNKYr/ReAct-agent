import asyncio
from typing import Any, Self

from typing_extensions import Dict

from agent.tools.base import Tool


class Execute_Bash(Tool):
    @property
    def name(self) -> str:
        return "execute_bash"

    @property
    def description(self) -> str:
        return """
        Execute Bash Command
        Do not use this tool for reading, writing, searching, or any other File System related action.
        Use read_file, write_file, search_file tools instead
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    },
                },
                "required": ["command"],
            }
        )

    @classmethod
    def create(cls) -> Self:
        return cls()

    async def execute(self, command: str | None = None, **kwargs: Any) -> str:
        if not command:
            return "Error: Missing command. Provide command"

        if self._is_dangerous(command):
            return "Error: Dangerous command detected. Do not have access to run dangerous command. Stop and report to the user"

        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            result = stdout.decode()
            if stderr:
                result += stderr.decode()
            return result
        except Exception as e:
            return f"Error: while executing {command}, has {e}"

    def _is_dangerous(self, command: str) -> bool:
        dangerous_commands = [
            "rm",
            "mv",
            "chmod",
            "chown",
            "sudo",
            "wget",
            "curl",
            "ps",
            "kill",
        ]
        return any(cmd in command for cmd in dangerous_commands)
