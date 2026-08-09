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
            return str(list(fp.rglob("*")))

        return str(list(fp.iterdir()))


class Edit_File(FS_Tool):
    """Tool for Edit File"""

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return """
        This tool is used to edit a file.
        Prerequisite: You have to first run read_file then start your edit.
        Replaces lines start_line through end_line (inclusive) with content.
        Only include the replacement text in content. Lines outside the range are preserved as-is,
        so if content covers logic that also exists outside the range, duplication will occur.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Line number to start editing from",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Line number to end editing at",
                },
            },
            "required": ["path", "content", "start_line", "end_line"],
        }

    async def execute(
        self,
        path: str | None = None,
        content: str | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
        **kwargs: Any,
    ) -> str:
        if not path:
            return "Error: path is required"
        if start_line is None or end_line is None:
            return "Error: start_line and end_line are required"
        if start_line > end_line:
            return "Error: start_line must be less than or equal to end_line"
        if content is None:
            content = ""
        try:
            # Read the file
            with open(path, "r") as f:
                lines = f.readlines()
            if start_line < 1 or end_line > len(lines):
                return "Error: start_line or end_line out of range"
            start0 = start_line - 1
            lines = lines[:start0] + content.splitlines(True) + lines[end_line:]
            return self._write_to_file(path, lines)
        except Exception as e:
            return f"Error: {str(e)}"

    def _write_to_file(self, path: str, content) -> str:
        try:
            with open(path, "w") as f:
                f.writelines(content)
            return "Success"
        except Exception as e:
            return f"Error: {str(e)}"


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
