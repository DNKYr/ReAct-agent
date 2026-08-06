import asyncio
from pathlib import Path
from typing import Any, Dict, Self

from agent.tools.base import Tool


class FS_Tool(Tool):
    """
    Base class for File-System related tools
    Include:
        Read_File
        Write_File
        Search_File
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
