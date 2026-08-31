"""Context Module building the conversational context for the agent"""

from typing import Any

from prompt import system_prompt
from agent.memory import MemoryStore

class ContextBuilder:
    """ContextBuilder builds the conversational context for the agent."""
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def build_system_prompt(self) -> str:
        parts = []
        parts.append(system_prompt)
        parts.append(self.memory_store.read_memory())
        return "\n""\n".join(parts)

    def build_message(self, history: list[dict[str, Any]], current_msg: str) -> list[dict[str, Any]]:
        message = [
            {
                "role": "system",
                "content": self.build_system_prompt()
            },
            *history
        ]

        message.append({"role": "user", "content": current_msg})

        return message


def create_context_builder(memory_store: MemoryStore | None = None) -> ContextBuilder:
    if memory_store is None:
        memory_store = MemoryStore()
    return ContextBuilder(memory_store)
