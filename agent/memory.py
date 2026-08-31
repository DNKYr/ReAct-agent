from agent.path_util import MEMORY_MD_PATH
from pathlib import Path

class MemoryStore:
    """
    The memory store manages the agent's memory, including reading, writing, and editing memory files.
    The self.memory_file holds the single truth for the memory.
    The path to the memory file is defined by MEMORY_MD_PATH.
    """

    def __init__(self):
        self.memory_file: Path = MEMORY_MD_PATH


    def _read_from_memory_file(self) -> str:
        return self.memory_file.read_text()

    def _write_to_memory(self, content: str) -> None:
        self.memory_file.write_text(content)

    def read_memory(self) -> str:
        return self.memory_file.read_text()

    def write_memory(self, content: str) -> str:
        # Guard against writing too much content to memory
        if len(content) > 10000:
            return "Error: content too long"
        self._write_to_memory(content)
        return "success"
