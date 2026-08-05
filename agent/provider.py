from typing import Any

from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)

from agent.tools.base import ToolRegistry


class OpenAICompatibleProvider:
    """
    Class for OpenAI-compatible providers.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.default_model = "deepseek-chat"

    def _build_kwargs(
        self,
        messages: list[dict[str, Any]],
        tools: ToolRegistry,
        model: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict[str, Any]:
        model_name = model or self.default_model

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "tools": tools.tools_schema,
            "reasoning_effort": reasoning_effort,
        }
        return kwargs

    def _build_client(self):
        self._client = OpenAI(api_key=self.api_key, base_url=self.api_url)

    def get_client(self):
        if not hasattr(self, "_client"):
            self._build_client()
        return self._client

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: ToolRegistry,
        model: str | None = None,
        reasoning_effort: str | None = None,
    ) -> ChatCompletion:
        if not hasattr(self, "_client"):
            self._build_client()
        kwargs = self._build_kwargs(messages, tools, model, reasoning_effort)
        return self._client.chat.completions.create(**kwargs)


def createOpenAICompatibleProvider(
    api_key: str | None = None, api_url: str | None = None
) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(api_key=api_key, api_url=api_url)
