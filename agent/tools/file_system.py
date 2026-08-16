"""File System Related Tools: Read_File, Write_File, Edit_File, List_File, Find_File"""

import asyncio
from pathlib import Path
from typing import Any, Dict, Self

from openai._utils import required_args

from agent.tools.base import Tool


class FS_Tool(Tool):
    """
    Base class for File-System related tools
    Include:
        Read_File
        Write_File
        Edit_File
        List_File
        Find_File
    """

    @classmethod
    def create(cls) -> Self:
        return cls()

    def _resolve_path(self, path: str) -> Path:
        return Path(path).expanduser().resolve()


class Read_File(FS_Tool):
    """Tool for Read Files"""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return """
        Read content of a given file
        Each time display 100 lines from offset
        Only support utf-8 text file
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file that want to read",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset from the beginning of the file",
                    },
                },
                "required": ["path"],
            }
        )

    async def execute(
        self, path: str | None = None, offset: int = 1, **kwargs: Any
    ) -> str:
        if not path:
            return "Error: Empty Path"

        fp = self._resolve_path(path)

        if not fp.exists():
            return f"Error: {path} does not exist."
        if not fp.is_file():
            return f"Error: {path} is not a file. "

        try:
            text_content = fp.read_bytes().decode()
        except UnicodeDecodeError:
            return (
                f"Error: Cannot read non-text file {path}, only support utf-8 text file"
            )

        lines = text_content.splitlines()
        total = len(lines)

        if offset < 1:
            offset = 1
        if offset > total:
            return f"Error: offset {offset} is greater than the total lines of the file {total}"

        start = offset - 1
        end = min(start + 100, total)
        result = f"{start} lines above\n"
        numbered = [
            f"{start + i + 1} {content}" for i, content in enumerate(lines[start:end])
        ]
        result += "\n".join(numbered)

        if end >= total:
            result += "\n End of the File"
        else:
            result += f"\n {total - end} lines below"
        return result


class Write_File(FS_Tool):
    """Tool for Write Files"""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Make edit to a file"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        }

    async def execute(
        self, path: str | None = None, content: str | None = None, **kwargs: Any
    ) -> str:
        if not path:
            return "Error: path is required"
        if not content:
            return "Error: content is required"
        resolved_path = self._resolve_path(path)

        if resolved_path.exists():
            return f"Error: file already exists at {resolved_path}, use Edit_File to modify it"
        with open(resolved_path, "w") as f:
            f.write(content)
        return f"File written to {resolved_path}"


class List_Files(FS_Tool):
    """Tool for List Files"""

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files in a directory"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list files from",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list files recursively",
                },
            },
            "required": ["path"],
        }

    async def execute(
        self, path: str | None = None, recursive: bool = False, **kwargs: Any
    ) -> str:
        if not path:
            return "Error: path is empty"

        fp = self._resolve_path(path)

        if not fp.exists():
            return "Error: path does not exist"

        if not fp.is_dir():
            return "Error: path is not a directory"

        if recursive:
            return str(list(fp.glob("**/*")))

        return str(list(fp.iterdir()))


class Find_File(FS_Tool):
    """Tool for Find File within a directory"""

    @property
    def name(self) -> str:
        return "find_file"

    @property
    def description(self) -> str:
        return "Use this tool to find a file by name in a directory. Prefer to use this tool above 'find' bash command"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the file to find",
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search for the file",
                },
            },
            "required": ["name"],
        }

    async def execute(
        self,
        name: str | None = None,
        directory: str | None = None,
        **kwargs: Any,
    ) -> str:
        import os

        if name is None:
            return "Error: name is required"
        if directory is None:
            directory = os.getcwd()

        for root, _, files in os.walk(directory):
            if name in files:
                return os.path.join(root, name)
        return f"Error: file not found within {directory}"
