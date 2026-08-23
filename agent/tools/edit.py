"""Tools for editing files."""

from typing import Any, Dict

from agent.tools.edit_util import apply_edit_to_content
from agent.tools.file_system import FS_Tool


class Edit_File(FS_Tool):
    """Tool for Edit File"""

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return """
        Edit a single file using exact text replacement. Every old_text must match a unique, non-overlapping region of the original file. Do not include large unchanged regions just to connect distant changes.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to edit",
                    },
                    "old_text": {
                        "type": "string",
                        "description": "The old text to be replaced",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The new text to replace the old text",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            }
        )

    async def execute(
        self,
        path: str | None = None,
        old_text: str | None = None,
        new_text: str | None = None,
        **kwargs: Any,
    ) -> str:
        if not path:
            return "Error: path is required"

        if not old_text:
            return "Error: old_text is required. If want to replace all text, use new_text instead"

        if not new_text:
            new_text = ""

        absolute_path = self._resolve_path(path)
        content = absolute_path.read_text()

        updated_content = apply_edit_to_content(content, old_text, new_text)
        if updated_content.startswith("Error:"):
            return updated_content
        absolute_path.write_text(updated_content)
        return "Success"
