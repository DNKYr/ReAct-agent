from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Self

from pydantic.dataclasses import dataclass


@dataclass
class ToolCallRequest:
    name: str
    argument: str
    result: str


class Tool(ABC):
    """Base Class for tools"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool Name used in Function Calls"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        ...

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameter"""
        ...

    @classmethod
    @abstractmethod
    def create(cls) -> Self:
        """Create an instance of itself"""
        return cls()

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Run Tools: Return string or else"""
        ...

    def parse_argument(self, argument: str) -> dict[str, Any]:
        import json

        stripped = argument.strip()

        if not stripped:
            return {}

        parsed = json.loads(stripped)
        return {} if parsed is None else parsed

    def to_schema(self) -> Dict[str, Any]:
        """To OpenAI Schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Class for storing list of tools"""

    def __init__(self):
        self.tools: List[Tool] = []

    def add_tools(self, tool: Tool):
        self.tools.append(tool)

    def add_tools_by_name(self, *names: str):
        from agent.tools import resolve_tool
        for name in names:
            self.tools.append(resolve_tool(name).create())

    def search_tools(self, name: str) -> Tool | None:
        for tool in self.tools:
            if name == tool.name:
                return tool
        return None

    @property
    def tools_schema(self) -> List[Dict[str, Any]]:
        """OpenAI schema form for all tools"""
        res = []
        for tool in self.tools:
            res.append(tool.to_schema())
        return res
