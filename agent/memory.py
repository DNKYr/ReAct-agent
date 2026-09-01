from agent.path_util import MEMORY_MD_PATH, USER_MD_PATH
from agent.path_util import create_memory_file, create_user_file
from pathlib import Path

class MemoryStore:
    """
    The memory store manages the agent's core memory files:
    - MEMORY.md: dynamic notes the agent keeps across sessions
    - USER.md: stable facts related to the user
    """

    def __init__(self):
        self.memory_file: Path = MEMORY_MD_PATH
        self.user_file: Path = USER_MD_PATH


    def _read_from_memory_file(self) -> str:
        if not self.memory_file.exists():
            create_memory_file()
        return self.memory_file.read_text()

    def _write_to_memory(self, content: str) -> None:
        self.memory_file.write_text(content)

    def _read_from_user_file(self) -> str:
        if not self.user_file.exists():
            create_user_file()
        return self.user_file.read_text()

    def _write_to_user(self, content: str) -> None:
        self.user_file.write_text(content)

    def read_memory(self, file_name: str) -> str:
        handler = {
            "memory": self._read_from_memory_file,
            "user": self._read_from_user_file,
        }
        try:
            return handler[file_name]()
        except KeyError:
            return "Error: Invalid file_name"

    def write_memory(self, file_name: str, content: str) -> str:
        # Guard against writing too much content to memory
        if len(content) > 10000:
            return "Error: content too long"
        handler = {
            "memory": self._write_to_memory,
            "user": self._write_to_user,
        }
        try:
            handler[file_name](content)
            return "success"
        except KeyError:
            return "Error: Invalid file_name"
