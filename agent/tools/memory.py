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
        Read the desired memory content from memory file
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            type="object",
            properties={
            },
            required=[],
        )

    async def execute(self, **kwargs: Any) -> str:
        if not self.memory_store:
            return "Error: Internal Error, MemoryStore not provided"

        return self.memory_store.read_memory()




class Write_Memory(Memory_Tool):
    """Tool for writing to the memory"""

    @property
    def name(self) -> str:
        return "write_memory"

    @property
    def description(self) -> str:
        return """
        Write to the MEMORY.md in the ~/.dclaw directory
        Store the fact about the user
        Only to use this tool when the MEMORY.md does not already exist.
        If the MEMORY.md already exists, use the edit_memory tool instead.
        If the length of the content exceeds 10,000 characters, the tool will return an error.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to write to the memory",
                    },
                },
                "required": ["content"],
            }
        )

    async def execute(self, content: str | None = None, **kwargs: Any) -> str:
        if not self.memory_store:
            return "Error: Existing memory store is None"
        if not content:
            content = ""
        print(f"Memory WRITE:\n{generate_diff_string(self.memory_store.read_memory(), content)}")
        consent = input("Do you want to save these changes? (y/N): ")
        if consent.lower() != "y":
            return "Edit cancelled by User"
        result = self.memory_store.write_memory(content)
        return result


class Edit_Memory(Memory_Tool):
    """Tool for editing the memory"""

    @property
    def name(self) -> str:
        return "edit_memory"

    @property
    def description(self) -> str:
        return """
        Edit the core memory to stored fact about user across sections
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
                    "old_text": {
                        "type": "string",
                        "description": "The old text to be replaced",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The new text to replace the old test",
                    },
                },
                "required": ["old_text", "new_text"],
            }
        )

    async def execute(
        self, old_text: str | None = None, new_text: str | None = None, **kwargs: Any
    ) -> str:
        if not self.memory_store:
            return "Error: Empty Memory Store. This is an internal error"

        if not old_text:
            return "Error: old_text is required. If you want to replace all the text, use new_text instead"

        if not new_text:
            new_text = ""

        content = self.memory_store.read_memory()

        updated_content = apply_edit_to_content(content, old_text, new_text)
        if updated_content.startswith("Error:"):
            return updated_content

        print(f"Memory EDIT:\n{generate_diff_string(content, updated_content)}")
        consent = input("Do you want to save these changes? (y/N): ")
        if consent.lower() != "y":
            return "Edit cancelled by User"
        return self.memory_store.write_memory(updated_content)
