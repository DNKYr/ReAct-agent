from dataclasses import dataclass
from typing import Any

from openai.types.chat import ChatCompletion

from agent.provider import OpenAICompatibleProvider
from agent.tools.base import ToolRegistry


@dataclass
class AgentSpec:
    """contains single run spec to send to model"""

    messages: list[dict[str, Any]]
    tools: ToolRegistry
    model: str | None = None
    reasoning_effort: str | None = None
    temperature: float | None = None


class AgentRunner:
    """
    Send request to provider, handling tool calls and tool respoonses
    """

    def __init__(self, provider: OpenAICompatibleProvider):
        self.provider = provider

    def load_user_prompt(self, user):
        """load user prompt and put it in message"""
        pass

    def _load_system_prompt(self) -> str:
        """return system_prompt from prompt.py"""
        from prompt import system_prompt

        return system_prompt

    def tool_call():
        """Handling tool calls and return ToolSuccess or ToolFailure"""
        pass

    def _build_context():
        """Build Context from tool call result, system_prompt, and user_prompt"""
        pass

    def send_message(self, spec: AgentSpec) -> ChatCompletion:
        """Send context to provider"""
        return self.provider.chat(
            messages=spec.messages,
            model=spec.model,
            tools=spec.tools,
            reasoning_effort=spec.reasoning_effort,
        )
