"""Modules for core memory system: USER.md + MEMORY.md"""

from typing import Any, Dict, Self

from agent.tools.base import Tool
from agent.tools.edit_util import apply_edit_to_content, generate_diff_string
from agent.memory import MemoryStore

class Memory_Tool(Tool):
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    @classmethod
    def create(cls) -> Self:
        return cls(MemoryStore())


class Read_Memory(Memory_Tool):
    """Tool for reading from the memory"""

    def __init__(self, memory_store: MemoryStore):
        super().__init__(memory_store)

    @property
    def name(self) -> str:
        return "read_memory"

    @property
    def description(self) -> str:
        return """
        Read the desired memory content from memory related file
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            type="object",
            properties={
                "file_name": {
                    "type": "string",
                    "description": "The name of the memory file to read from: LITERAL[memory|user]",
                    "enum": ["memory", "user"],
                },
            },
            required=["file_name"],
        )

    async def execute(self, file_name: str | None = None, **kwargs: Any) -> str:
        if not self.memory_store:
            return "Error: Internal Error, MemoryStore not provided"

        if not file_name:
            return "Error: file_name is required"

        return self.memory_store.read_memory(file_name)




class Write_Memory(Memory_Tool):
    """Tool for writing to the memory"""

    @property
    def name(self) -> str:
        return "write_memory"

    @property
    def description(self) -> str:
        return """
        Write content to a core memory file:
        - "memory": MEMORY.md in ~/.dclaw, dynamic notes the agent keeps across sessions. Only use when MEMORY.md does not exist yet; otherwise use the edit_memory tool.
        - "user": USER.md in ~/.dclaw, stable facts about the user. Changes require explicit user confirmation.
        If the length of the content exceeds 10,000 characters, the tool will return an error.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to write to",
                        "enum": ["memory", "user"]
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the memory",
                    },
                },
                "required": ["file_name", "content"],
            }
        )

    async def execute(self, file_name: str | None = None, content: str | None = None, **kwargs: Any) -> str:
        if not self.memory_store:
            return "Error: Existing memory store is None"
        if not file_name:
            return "Error: file_name is required"
        if not content:
            content = ""
        if file_name == "user":
            print(f"{file_name.upper()} WRITE:\n{generate_diff_string(self.memory_store.read_memory(file_name), content)}")
            consent = input("Do you want to save these changes? (y/N): ")
            if consent.lower() != "y":
                return "Edit cancelled by User"
        return self.memory_store.write_memory(file_name, content)


class Edit_Memory(Memory_Tool):
    """Tool for editing the memory"""

    @property
    def name(self) -> str:
        return "edit_memory"

    @property
    def description(self) -> str:
        return """
        Edit the core memory to store facts about the user across sections.
        Editing "user" (USER.md) requires explicit user confirmation.
        Every old_text must match unique, non-overlapping region of the original file.
        Do not include large unchanged regions just to connect distant changes
        If the length of the edited content exceeds 10,000 characters, the tool will return an error.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to edit",
                        "enum": ["memory", "user"],
                    },
                    "old_text": {
                        "type": "string",
                        "description": "The old text to be replaced",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The new text to replace the old test",
                    },
                },
                "required": ["file_name", "old_text", "new_text"],
            }
        )

    async def execute(
        self, file_name: str | None = None, old_text: str | None = None, new_text: str | None = None, **kwargs: Any
    ) -> str:
        if not self.memory_store:
            return "Error: Empty Memory Store. This is an internal error"

        if not file_name:
            return "Error: file_name is required"
        if not old_text:
            return "Error: old_text is required. If you want to replace all the text, use new_text instead"
        if not new_text:
            new_text = ""

        content = self.memory_store.read_memory(file_name)

        updated_content = apply_edit_to_content(content, old_text, new_text)
        if updated_content.startswith("Error:"):
            return updated_content

        if file_name == "user":
            print(f"{file_name.upper()} EDIT:\n{generate_diff_string(content, updated_content)}")
            consent = input("Do you want to save these changes? (y/N): ")
            if consent.lower() != "y":
                return "Edit cancelled by User"
        return self.memory_store.write_memory(file_name, updated_content)
