import os

from openai import OpenAI


class OpenAICompatibleProvider:
    """
    Class for OpenAI-compatible providers.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        model: str = "deepseek-chat",
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def _build_client(self):
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

    def get_client(self):
        if not hasattr(self, "_client"):
            self._build_client()
        return self.client
